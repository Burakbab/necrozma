# 2026-08-20 03:48 UTC — 3-hourly check: built the bundle-editing tool the last session flagged as needed

## Context

Today's daily bar (2026-08-20) was already processed by the 00:20 UTC run
before this session started (`live_state.json`'s `updated` timestamp is
`2026-08-20T00:21:36+00:00`, and `runs/2026-08-20-0020-daily-trading.md`
already exists) — no `tick` run this session, no double-trade risk.

Item 3 (cross-asset correlation) closed for good in the 00:55 UTC run just
before this one. Item 4 (LLM-backed hard-call review) has nothing to act on —
checked `review-hard-calls`, still zero flagged bars, zero reviewed. Item 2's
open question (does a much-longer 4h shadow run ever break the 9-generation
stagnation wall) is explicitly flagged in AGENTS.md as a judgment call with
falling marginal value, not a clear best use of a slot right now.

The 00:55 UTC correlation-removal run note left a concrete, small, unclaimed
piece of infrastructure debt: its "Editing mechanism note for future
sessions" says the extract/reinsert approach used to edit
`evotrader_bundle.py`'s giant single-line `_SRC[...]` module strings "lived
in `/tmp`, gone with the container, so the next session that needs to touch
bundle internals will want to rebuild the same two-function tool rather than
hand-edit the giant lines." That's exactly the kind of thing worth doing once
and committing, rather than re-inventing every time a future session needs to
touch bundle internals — and it ties into item 7's stated risk (the
2026-08-15 migration's nbsp whitespace corruption, caught by the checksum and
py_compile, not by review).

## What shipped

New `tools/edit_bundle_module.py` (plus `tools/__init__.py` so it's
importable from tests): pulls a named module's source out of
`evotrader_bundle.py`'s `_SRC['dotted.name'] = '...'` line via
`ast.literal_eval`, writes it to a real `.py` file for normal editing, and
folds an edited file back in via `repr()`, replacing only that one line.
Four primitives (`get_module_source`, `set_module_source`, `list_modules`,
plus disk-touching `extract`/`reinsert` wrappers) and a small CLI
(`list`/`extract`/`reinsert`/`verify`).

`verify` extracts and reinserts every module in the real bundle, unmodified,
and asserts the result is byte-identical to the original — this is the
"round-trip verified byte-identical on an unmodified extract before trusting
it on real edits" step the 00:55 run described doing ad hoc, now a permanent,
reusable check.

New `tests/test_edit_bundle_module.py` (7 tests): synthetic-bundle tests for
`get_module_source`/`set_module_source`/`list_modules` (missing-module
`KeyError`, unmodified round-trip, editing one module doesn't touch others),
plus one test that runs the real round-trip-verification check against the
actual current `evotrader_bundle.py` (`>=15` modules found, every one
round-trips byte-identical) — the regression this tool exists to prevent,
checked on every `pytest` run, not just manually.

## Verification

- Manual full workflow test on a scratch copy in `/tmp` (not this repo):
  extracted `core.types`, appended a line, reinserted, confirmed the new
  line landed in the right place in the `_SRC` dict entry and
  `python3 -m py_compile` stayed clean on the edited scratch copy.
- `python3 tools/edit_bundle_module.py verify` on the real repo: round-trip
  verified, bundle unchanged.
- Full suite: 111 passed (up from 104 — 7 new tests, no existing test
  touched).
- `py_compile` clean on `evotrader_bundle.py`, `tools/edit_bundle_module.py`,
  and the new test file.
- `live_state.json` md5 identical before/after
  (`cca58deb976cef403c5010f2e2b9528b`, same value the 00:55 UTC run
  recorded).
- `evotrader.manifest` md5 identical (`6a4434574ff424f74ff300ebdb50d194`).
- `git status --short` clean of anything but the two new files
  (`tools/edit_bundle_module.py`, `tools/__init__.py`,
  `tests/test_edit_bundle_module.py`) plus this run note.
- `python3 evotrader_bundle.py summary` still reports `constitution verified
  dfae6a697f51fb49` and the expected account state (genome v3, 6 ticks).

## Caveat / one bug caught before committing

First draft of the test suite hand-wrote one sample module's source as a
Python string literal using double quotes for the escaping style, then
asserted `set_module_source` round-tripped it byte-identical — that's not a
meaningful test, since `repr()` (what `set_module_source` actually uses) has
its own canonical quoting rules and won't reproduce an arbitrary hand-chosen
quote style. Fixed by building the synthetic sample's `_SRC[...]` lines with
`repr()` itself, so the assertion is against the tool's own canonical output
form, the same form the real bundle is already written in.

## Next

Not used for a real edit this session — this was building the tool ahead of
need, per the 00:55 UTC run's flag, not applying it to any specific change.
The next session that needs to touch `evotrader_bundle.py` internals (e.g.
any future item-3-style removal, or item 7's eventual unflatten) should use
this instead of hand-editing the `_SRC` lines or rebuilding an ad hoc
version in `/tmp`.
