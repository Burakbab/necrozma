"""Guards the new real-file package tree (core/, agents/, loop/,
constitution/) against drifting from evotrader_bundle.py's embedded _SRC
dict.

Item 7 in AGENTS.md's Next steps ("unflatten evotrader_bundle.py into real
files") is done in the sense that a real, byte-identical copy of every
embedded module now exists on disk as normal importable packages -- but the
bundle stays the live path (this file never imports evotrader_bundle as the
runtime; conftest.py's own bundle import continues to serve every other test
file via its meta-path finder, which always wins the name lookup once
installed, so the real files on disk are otherwise inert to the existing
suite). This test is the tripwire: if anyone edits one copy without the
other, this fails immediately instead of the two silently drifting apart
until someone actually attempts the cutover.

Deliberately does not touch evotrader_bundle.py, live_state.json, or
evotrader.manifest -- read-only comparison only.
"""
import re
from pathlib import Path

import pytest

import tools.edit_bundle_module as m
from tools.edit_bundle_module import get_module_source, list_modules

REPO_ROOT = m.BUNDLE_PATH.parent


def _pkgs(bundle_text: str) -> list[str]:
    match = re.search(r"^_PKGS = (\[[^\]]*\])", bundle_text, re.M)
    assert match, "evotrader_bundle.py's _PKGS constant moved or was renamed"
    return eval(match.group(1))  # noqa: S307 -- trusted local repo file, a literal list


def _module_to_path(module: str, pkgs: list[str]) -> Path:
    parts = module.split(".")
    if module in pkgs:
        return REPO_ROOT.joinpath(*parts, "__init__.py")
    return REPO_ROOT.joinpath(*parts[:-1], parts[-1] + ".py")


def _bundle_modules():
    bundle_text = m.BUNDLE_PATH.read_text()
    pkgs = _pkgs(bundle_text)
    modules = list_modules(bundle_text)
    assert len(modules) >= 15  # sanity, same floor test_edit_bundle_module.py uses
    return bundle_text, pkgs, modules


@pytest.mark.parametrize("module", list_modules(m.BUNDLE_PATH.read_text()))
def test_real_file_matches_embedded_source(module):
    bundle_text, pkgs, _ = _bundle_modules()
    path = _module_to_path(module, pkgs)
    assert path.exists(), f"expected real file {path} for embedded module {module!r}"
    on_disk = path.read_text()
    embedded = get_module_source(bundle_text, module)
    assert on_disk == embedded, (
        f"{path} has drifted from _SRC[{module!r}] in evotrader_bundle.py -- "
        "re-extract with tools/edit_bundle_module.py or hand-sync the two copies"
    )


def test_no_extra_or_missing_real_package_files():
    """Every embedded module has exactly one real file, and there are no
    stray .py files under the four package dirs that don't correspond to a
    real embedded module (which would mean the two trees have diverged in
    shape, not just content)."""
    bundle_text, pkgs, modules = _bundle_modules()
    expected = {str(_module_to_path(mod, pkgs)) for mod in modules}
    actual = set()
    for pkg in pkgs:
        for path in (REPO_ROOT / pkg).rglob("*.py"):
            actual.add(str(path))
    assert actual == expected
