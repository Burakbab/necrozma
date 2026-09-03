"""Run protocol step 2 as one command instead of hand-deriving it each session.

AGENTS.md documents a recurring situation: the cloud clone starts detached and
shallow, and a bare `git pull` (or a naive `git status` comparison) reports
local `main` and `origin/main` as having "diverged" or sharing "no common
ancestor". At least six independent scheduled sessions between 2026-09-02 and
2026-09-03 traced this to shallow-fetch staleness, not a real force-push, and
each re-derived the same non-destructive fix by hand: unshallow, check for a
real merge-base, fast-forward if one exists, and only fall back to a
destructive `reset --hard origin/main` if the divergence is genuine (no
merge-base even with full history). This script encodes that sequence once so
a session runs `python3 tools/git_sync.py` instead of re-deriving it -- and,
unlike a hand-run sequence under time pressure, refuses to touch a dirty
working tree before ever reaching the destructive fallback.
"""
from __future__ import annotations

import argparse
import subprocess
import sys


def _run(args: list[str], cwd: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, text=True
    )


def _repo_root(start: str) -> str:
    result = _run(["rev-parse", "--show-toplevel"], start)
    if result.returncode != 0:
        raise RuntimeError(f"not a git repository: {result.stderr.strip()}")
    return result.stdout.strip()


def sync(cwd: str = ".", branch: str = "main") -> dict:
    """Apply the Run protocol step 2 sequence. Returns a status dict for tests/logging."""
    repo = _repo_root(cwd)

    head = _run(["symbolic-ref", "-q", "HEAD"], repo)
    if head.returncode != 0:
        checkout = _run(["checkout", branch], repo)
        if checkout.returncode != 0:
            return {"action": "error", "detail": checkout.stderr.strip()}

    shallow = _run(["rev-parse", "--is-shallow-repository"], repo).stdout.strip()
    if shallow == "true":
        fetch = _run(["fetch", "--unshallow", "origin", branch], repo)
    else:
        fetch = _run(["fetch", "origin", branch], repo)
    if fetch.returncode != 0:
        return {"action": "error", "detail": fetch.stderr.strip()}

    merge_base = _run(["merge-base", branch, f"origin/{branch}"], repo)
    if merge_base.returncode == 0:
        ff = _run(["merge", "--ff-only", f"origin/{branch}"], repo)
        if ff.returncode != 0:
            return {"action": "error", "detail": ff.stderr.strip()}
        return {"action": "fast-forwarded", "detail": ff.stdout.strip()}

    dirty = _run(["status", "--porcelain"], repo).stdout.strip()
    if dirty:
        return {
            "action": "aborted",
            "detail": (
                "no merge-base with origin/%s even after a full fetch (genuine "
                "divergence), but the working tree is dirty -- refusing to "
                "reset --hard and discard uncommitted changes. Resolve by hand."
                % branch
            ),
        }

    reset = _run(["reset", "--hard", f"origin/{branch}"], repo)
    if reset.returncode != 0:
        return {"action": "error", "detail": reset.stderr.strip()}
    return {
        "action": "reset-hard",
        "detail": (
            "no merge-base found even with full history -- origin/%s treated "
            "as authoritative per AGENTS.md's Run protocol step 2. %s"
            % (branch, reset.stdout.strip())
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--branch", default="main")
    parser.add_argument("--cwd", default=".")
    args = parser.parse_args()

    result = sync(cwd=args.cwd, branch=args.branch)
    print(f"git_sync: {result['action']} -- {result['detail']}")
    return 1 if result["action"] in ("error",) else 0


if __name__ == "__main__":
    sys.exit(main())
