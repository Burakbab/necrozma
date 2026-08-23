"""Extract/reinsert a single module's source from evotrader_bundle.py's embedded
_SRC dict, for editing the bundle without hand-touching its giant escaped-string
lines.

evotrader_bundle.py stores each virtual module as one line: `_SRC['dotted.name']
= '<entire module source as a Python string literal>'`. Editing those lines
directly with string-match tools is impractical and risky (a 2026-08-15
migration was corrupted by whitespace transcription errors caught only by the
constitution checksum and py_compile, not by review). This tool round-trips a
module out to a real .py file, lets you edit it normally, then folds it back in.

Usage:
    python3 tools/edit_bundle_module.py list
    python3 tools/edit_bundle_module.py extract <module.name> <out_path>
    python3 tools/edit_bundle_module.py reinsert <module.name> <in_path>
    python3 tools/edit_bundle_module.py verify
    python3 tools/edit_bundle_module.py sync [--check]

`verify` extracts and reinserts every module unmodified and asserts the
resulting bundle text is byte-identical to the original — run this before
trusting the tool on a real edit, and after every reinsert.

`sync` is the bundler: it regenerates every `_SRC[...]` entry in
evotrader_bundle.py from the real, normally-importable `core/`, `agents/`,
`loop/`, `constitution/` package tree (added 2026-08-23, see AGENTS.md item
7), the reverse direction of `extract`. The real files are the source of
truth for `sync`; run it after editing a real file directly instead of going
through `extract`/`reinsert`, so the bundle (still the live path every
scheduled command executes) picks up the change. `--check` reports drift
without writing and exits 1 if any module differs — safe to run in CI or a
pre-commit check. Does not touch `live_state.json` or `evotrader.manifest`.
"""
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

BUNDLE_PATH = Path(__file__).resolve().parent.parent / "evotrader_bundle.py"


def _module_line_prefix(module: str) -> str:
    return f"_SRC[{module!r}] = "


def list_modules(bundle_text: str) -> list[str]:
    return re.findall(r"^_SRC\['([^']+)'\] = ", bundle_text, re.M)


def get_module_source(bundle_text: str, module: str) -> str:
    prefix = _module_line_prefix(module)
    for line in bundle_text.split("\n"):
        if line.startswith(prefix):
            return ast.literal_eval(line[len(prefix):])
    raise KeyError(f"no _SRC entry for module {module!r}")


def set_module_source(bundle_text: str, module: str, source: str) -> str:
    prefix = _module_line_prefix(module)
    lines = bundle_text.split("\n")
    for i, line in enumerate(lines):
        if line.startswith(prefix):
            lines[i] = prefix + repr(source)
            return "\n".join(lines)
    raise KeyError(f"no _SRC entry for module {module!r}")


def extract(module: str, out_path: str) -> None:
    bundle_text = BUNDLE_PATH.read_text()
    source = get_module_source(bundle_text, module)
    Path(out_path).write_text(source)


def reinsert(module: str, in_path: str) -> None:
    bundle_text = BUNDLE_PATH.read_text()
    new_source = Path(in_path).read_text()
    BUNDLE_PATH.write_text(set_module_source(bundle_text, module, new_source))


def verify_roundtrip() -> bool:
    bundle_text = BUNDLE_PATH.read_text()
    for module in list_modules(bundle_text):
        source = get_module_source(bundle_text, module)
        roundtripped = set_module_source(bundle_text, module, source)
        if roundtripped != bundle_text:
            raise AssertionError(f"round-trip mismatch for module {module!r}")
    return True


def pkgs(bundle_text: str) -> list[str]:
    """The bundle's own `_PKGS` constant: dotted names that are packages
    (get `__init__.py`) rather than plain modules (get `<name>.py`)."""
    match = re.search(r"^_PKGS = (\[[^\]]*\])", bundle_text, re.M)
    if not match:
        raise AssertionError("evotrader_bundle.py's _PKGS constant moved or was renamed")
    return eval(match.group(1))  # noqa: S307 -- trusted local repo file, a literal list


def module_to_path(module: str, pkg_list: list[str], root: Path) -> Path:
    """Map a dotted `_SRC` module name to the real file it corresponds to
    under the unflattened `core/`/`agents/`/`loop/`/`constitution/` tree
    (`root` is normally the repo root, `BUNDLE_PATH.parent`)."""
    parts = module.split(".")
    if module in pkg_list:
        return root.joinpath(*parts, "__init__.py")
    return root.joinpath(*parts[:-1], parts[-1] + ".py")


def sync_from_files(bundle_text: str, root: Path) -> str:
    """Return `bundle_text` with every `_SRC[module]` entry replaced by the
    current content of its corresponding real file under `root`. The real
    files are treated as the source of truth here — this is the reverse
    direction of `extract`, i.e. the bundler `_SRC` generation step
    AGENTS.md item 7 still needs before the two trees can't silently drift.
    Raises FileNotFoundError if a module's real file is missing."""
    pkg_list = pkgs(bundle_text)
    text = bundle_text
    for module in list_modules(bundle_text):
        path = module_to_path(module, pkg_list, root)
        if not path.exists():
            raise FileNotFoundError(f"no real file {path} for embedded module {module!r}")
        text = set_module_source(text, module, path.read_text())
    return text


def _main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 1
    cmd, rest = argv[0], argv[1:]
    if cmd == "list":
        for module in list_modules(BUNDLE_PATH.read_text()):
            print(module)
        return 0
    if cmd == "extract":
        module, out_path = rest
        extract(module, out_path)
        print(f"wrote {out_path}")
        return 0
    if cmd == "reinsert":
        module, in_path = rest
        reinsert(module, in_path)
        print(f"reinserted {module} into {BUNDLE_PATH}")
        return 0
    if cmd == "verify":
        verify_roundtrip()
        print("round-trip verified: bundle unchanged")
        return 0
    if cmd == "sync":
        check = "--check" in rest
        bundle_text = BUNDLE_PATH.read_text()
        synced = sync_from_files(bundle_text, BUNDLE_PATH.parent)
        if synced == bundle_text:
            print("bundle already matches real files, no changes")
            return 0
        if check:
            print("DRIFT: bundle does not match real files (run without --check to apply)")
            return 1
        BUNDLE_PATH.write_text(synced)
        print(f"synced {BUNDLE_PATH} from real files")
        return 0
    print(__doc__)
    return 1


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv[1:]))
