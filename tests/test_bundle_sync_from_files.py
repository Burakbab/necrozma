"""tools/edit_bundle_module.py's `sync` command -- regenerates evotrader_bundle.py's
_SRC dict from the real core/agents/loop/constitution files, the reverse
direction of `extract`. Exercises `pkgs`/`module_to_path`/`sync_from_files`
against an isolated tmp_path tree (never touches the real evotrader_bundle.py
or real package files), plus one check against the real repo confirming the
two trees are actually in sync today.
"""
import pytest

from tools.edit_bundle_module import (
    get_module_source,
    list_modules,
    module_to_path,
    pkgs,
    sync_from_files,
)

SAMPLE_BUNDLE = (
    "_PKGS = ['pkg']\n"
    "_SRC = {}\n"
    "_SRC['pkg'] = " + repr("old pkg init\n") + "\n"
    "_SRC['pkg.mod'] = " + repr("old mod source\n") + "\n"
    "OTHER = 'not a module line'\n"
)


def _write_real_files(root, pkg_init="new pkg init\n", mod_source="new mod source\n"):
    (root / "pkg").mkdir(parents=True, exist_ok=True)
    (root / "pkg" / "__init__.py").write_text(pkg_init)
    (root / "pkg" / "mod.py").write_text(mod_source)


def test_pkgs_reads_the_pkgs_constant():
    assert pkgs(SAMPLE_BUNDLE) == ["pkg"]


def test_pkgs_missing_constant_raises():
    with pytest.raises(AssertionError):
        pkgs("_SRC = {}\n")


def test_module_to_path_package_gets_init(tmp_path):
    assert module_to_path("pkg", ["pkg"], tmp_path) == tmp_path / "pkg" / "__init__.py"


def test_module_to_path_plain_module_gets_dotted_file(tmp_path):
    assert module_to_path("pkg.mod", ["pkg"], tmp_path) == tmp_path / "pkg" / "mod.py"


def test_sync_from_files_pulls_real_file_content_into_src(tmp_path):
    _write_real_files(tmp_path)
    synced = sync_from_files(SAMPLE_BUNDLE, tmp_path)
    assert get_module_source(synced, "pkg") == "new pkg init\n"
    assert get_module_source(synced, "pkg.mod") == "new mod source\n"
    # Non-module lines (_PKGS, OTHER) are untouched.
    assert "_PKGS = ['pkg']" in synced
    assert "OTHER = 'not a module line'" in synced


def test_sync_from_files_already_in_sync_is_a_true_no_op(tmp_path):
    _write_real_files(tmp_path, pkg_init="old pkg init\n", mod_source="old mod source\n")
    assert sync_from_files(SAMPLE_BUNDLE, tmp_path) == SAMPLE_BUNDLE


def test_sync_from_files_missing_real_file_raises(tmp_path):
    # Only write the package dir, not mod.py.
    (tmp_path / "pkg").mkdir()
    (tmp_path / "pkg" / "__init__.py").write_text("x\n")
    with pytest.raises(FileNotFoundError):
        sync_from_files(SAMPLE_BUNDLE, tmp_path)


def test_real_repo_bundle_and_files_are_currently_in_sync():
    """Not a synthetic case: confirms sync_from_files is a no-op against the
    actual evotrader_bundle.py and the actual core/agents/loop/constitution
    tree, i.e. the two copies test_unflattened_files_match_bundle.py guards
    haven't drifted. Read-only -- never writes BUNDLE_PATH."""
    import tools.edit_bundle_module as m

    bundle_text = m.BUNDLE_PATH.read_text()
    root = m.BUNDLE_PATH.parent
    assert sync_from_files(bundle_text, root) == bundle_text


def test_sync_from_files_unknown_module_missing_file_message_names_it(tmp_path):
    (tmp_path / "pkg").mkdir()
    (tmp_path / "pkg" / "__init__.py").write_text("x\n")
    with pytest.raises(FileNotFoundError, match="pkg.mod"):
        sync_from_files(SAMPLE_BUNDLE, tmp_path)


def test_sync_from_files_covers_every_real_bundle_module_via_cli_path():
    """Sanity: list_modules on the real bundle still returns >=15 entries and
    every one resolves through module_to_path without raising, matching the
    floor test_edit_bundle_module.py/test_unflattened_files_match_bundle.py use."""
    import tools.edit_bundle_module as m

    bundle_text = m.BUNDLE_PATH.read_text()
    pkg_list = pkgs(bundle_text)
    modules = list_modules(bundle_text)
    assert len(modules) >= 15
    for module in modules:
        path = module_to_path(module, pkg_list, m.BUNDLE_PATH.parent)
        assert path.exists()
