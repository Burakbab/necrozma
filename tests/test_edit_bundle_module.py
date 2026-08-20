"""tools/edit_bundle_module.py -- round-trips a module's source out of
evotrader_bundle.py's embedded _SRC dict and back in, for editing bundle
internals without hand-touching its giant escaped-string lines. Exercises the
same get/set primitives the CLI's extract/reinsert wrap, entirely in memory
(never touches the real evotrader_bundle.py on disk)."""
import pytest

from tools.edit_bundle_module import get_module_source, list_modules, set_module_source


# Built with repr() rather than hand-written quoting, so its literal style
# matches what set_module_source itself produces (Python's repr() picks
# single- vs double-quoting based on the string's own content) -- a
# byte-identical round-trip assertion only makes sense against a canonical
# form.
_SOURCE_A = "x = 1\ny = 2\n"
_SOURCE_A_B = 'has "quotes" and a newline\n'
SAMPLE_BUNDLE = (
    "_SRC = {}\n"
    "_SRC['a'] = " + repr(_SOURCE_A) + "\n"
    "_SRC['a.b'] = " + repr(_SOURCE_A_B) + "\n"
    "OTHER = 'not a module line'\n"
)


def test_list_modules_finds_every_src_key_in_order():
    assert list_modules(SAMPLE_BUNDLE) == ["a", "a.b"]


def test_get_module_source_decodes_the_literal():
    assert get_module_source(SAMPLE_BUNDLE, "a") == "x = 1\ny = 2\n"
    assert get_module_source(SAMPLE_BUNDLE, "a.b") == 'has "quotes" and a newline\n'


def test_get_module_source_missing_module_raises():
    with pytest.raises(KeyError):
        get_module_source(SAMPLE_BUNDLE, "nope")


def test_set_module_source_unmodified_round_trips_byte_identical():
    for module in list_modules(SAMPLE_BUNDLE):
        source = get_module_source(SAMPLE_BUNDLE, module)
        assert set_module_source(SAMPLE_BUNDLE, module, source) == SAMPLE_BUNDLE


def test_set_module_source_only_touches_the_target_line():
    edited = set_module_source(SAMPLE_BUNDLE, "a", "new source\n")
    assert get_module_source(edited, "a") == "new source\n"
    assert get_module_source(edited, "a.b") == get_module_source(SAMPLE_BUNDLE, "a.b")
    assert edited.count("\n") == SAMPLE_BUNDLE.count("\n")


def test_set_module_source_missing_module_raises():
    with pytest.raises(KeyError):
        set_module_source(SAMPLE_BUNDLE, "nope", "x")


def test_real_bundle_every_module_round_trips_byte_identical():
    """The actual regression this tool exists for: verify against the real,
    current evotrader_bundle.py, not just the synthetic sample above."""
    from pathlib import Path

    import tools.edit_bundle_module as m

    bundle_text = m.BUNDLE_PATH.read_text()
    modules = list_modules(bundle_text)
    assert len(modules) >= 15  # sanity: the bundle has this many modules today
    for module in modules:
        source = get_module_source(bundle_text, module)
        assert set_module_source(bundle_text, module, source) == bundle_text
