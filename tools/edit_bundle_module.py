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

`verify` extracts and reinserts every module unmodified and asserts the
resulting bundle text is byte-identical to the original — run this before
trusting the tool on a real edit, and after every reinsert.
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
    print(__doc__)
    return 1


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv[1:]))
