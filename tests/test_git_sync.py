"""tools/git_sync.py -- exercises the fast-forward and reset-hard branches
against real local git repositories (file:// remotes, no network), since the
whole point of the script is git plumbing that doesn't mean much mocked out."""
import subprocess

import pytest

from tools.git_sync import sync


def _git(args, cwd):
    result = subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, text=True
    )
    assert result.returncode == 0, f"git {args} failed: {result.stderr}"
    return result.stdout


def _init_repo(path):
    path.mkdir(parents=True, exist_ok=True)
    _git(["init", "-q", "-b", "main"], path)
    _git(["config", "user.email", "test@example.com"], path)
    _git(["config", "user.name", "Test"], path)
    return path


def _commit(path, name, content="x"):
    (path / name).write_text(content)
    _git(["add", name], path)
    _git(["commit", "-q", "-m", name], path)


def _rewrite_history_orphan(repo, name, content):
    """Replace repo's `main` with a disjoint orphan history -- a genuine
    force-push rewrite, sharing no merge-base with anyone who already has the
    old `main`. A `reset --hard`/new-commit on the same lineage still shares
    the original root commit, which isn't what a real force-push looks like."""
    _git(["checkout", "--orphan", "__rewrite__", "-q"], repo)
    _git(["rm", "-rf", "-q", "."], repo)
    (repo / name).write_text(content)
    _git(["add", name], repo)
    _git(["commit", "-q", "-m", name], repo)
    _git(["branch", "-D", "main"], repo)
    _git(["branch", "-m", "main"], repo)


def _clone(origin, dest):
    subprocess.run(
        ["git", "clone", "-q", str(origin), str(dest)],
        capture_output=True, text=True, check=True,
    )
    _git(["config", "user.email", "test@example.com"], dest)
    _git(["config", "user.name", "Test"], dest)
    return dest


def test_clone_already_up_to_date_is_a_clean_fast_forward(tmp_path):
    origin = _init_repo(tmp_path / "origin")
    _commit(origin, "a")
    clone = _clone(origin, tmp_path / "clone")

    result = sync(cwd=str(clone))

    assert result["action"] == "fast-forwarded"
    assert _git(["rev-parse", "HEAD"], clone) == _git(["rev-parse", "HEAD"], origin)


def test_clone_behind_origin_fast_forwards_without_losing_anything(tmp_path):
    origin = _init_repo(tmp_path / "origin")
    _commit(origin, "a")
    clone = _clone(origin, tmp_path / "clone")
    _commit(origin, "b")  # origin moves ahead after the clone

    result = sync(cwd=str(clone))

    assert result["action"] == "fast-forwarded"
    assert _git(["rev-parse", "HEAD"], clone) == _git(["rev-parse", "HEAD"], origin)


def test_detached_head_checks_out_branch_first(tmp_path):
    origin = _init_repo(tmp_path / "origin")
    _commit(origin, "a")
    clone = _clone(origin, tmp_path / "clone")
    _git(["checkout", "-q", "--detach", "HEAD"], clone)
    _commit(origin, "b")

    result = sync(cwd=str(clone))

    assert result["action"] == "fast-forwarded"
    assert _git(["symbolic-ref", "-q", "HEAD"], clone).strip() == "refs/heads/main"


def test_genuine_divergence_with_clean_tree_resets_to_origin(tmp_path):
    origin = _init_repo(tmp_path / "origin")
    _commit(origin, "a")
    clone = _clone(origin, tmp_path / "clone")
    _rewrite_history_orphan(origin, "c", "rewritten history")
    # Give the clone a local commit of its own too, on the old lineage.
    _commit(clone, "b", "local-only")

    result = sync(cwd=str(clone))

    assert result["action"] == "reset-hard"
    assert _git(["rev-parse", "HEAD"], clone) == _git(["rev-parse", "HEAD"], origin)


def test_genuine_divergence_with_dirty_tree_refuses_to_clobber_it(tmp_path):
    origin = _init_repo(tmp_path / "origin")
    _commit(origin, "a")
    clone = _clone(origin, tmp_path / "clone")
    _rewrite_history_orphan(origin, "c", "rewritten history")
    _commit(clone, "b", "local-only")
    (clone / "uncommitted.txt").write_text("do not delete me")

    before_head = _git(["rev-parse", "HEAD"], clone)
    result = sync(cwd=str(clone))

    assert result["action"] == "aborted"
    assert (clone / "uncommitted.txt").exists()
    assert _git(["rev-parse", "HEAD"], clone) == before_head


def test_shallow_clone_behind_origin_unshallows_and_fast_forwards(tmp_path):
    origin = _init_repo(tmp_path / "origin")
    for i in range(5):
        _commit(origin, f"a{i}")
    clone_path = tmp_path / "clone"
    subprocess.run(
        ["git", "clone", "-q", "--depth", "1", f"file://{origin}", str(clone_path)],
        capture_output=True, text=True, check=True,
    )
    _git(["config", "user.email", "test@example.com"], clone_path)
    _git(["config", "user.name", "Test"], clone_path)
    assert _git(["rev-parse", "--is-shallow-repository"], clone_path).strip() == "true"
    _commit(origin, "b")  # origin moves ahead of the shallow clone's single commit

    result = sync(cwd=str(clone_path))

    assert result["action"] == "fast-forwarded"
    assert _git(["rev-parse", "--is-shallow-repository"], clone_path).strip() == "false"
    assert _git(["rev-parse", "HEAD"], clone_path) == _git(["rev-parse", "HEAD"], origin)


def test_not_a_git_repository_raises(tmp_path):
    plain_dir = tmp_path / "not-a-repo"
    plain_dir.mkdir()
    with pytest.raises(RuntimeError):
        sync(cwd=str(plain_dir))
