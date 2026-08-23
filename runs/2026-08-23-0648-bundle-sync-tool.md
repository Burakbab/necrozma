# 2026-08-23 06:48 UTC — 3-hourly check: bundler half of item 7's unflatten

## Daily bar

`live_state.json` `updated: 2026-08-23T00:22:00+00:00`, genome version 3,
matches the 00:20 UTC daily run already recorded in
`runs/2026-08-23-0020-daily-trading.md`. No new bar to process this cycle —
`tick` not run. `review-hard-calls` checked: 0 pending.

## What shipped

The weekend all-hands session (2026-08-23 06:00 UTC) did the safe half of
AGENTS.md item 7 (real `core/`/`agents/`/`loop/`/`constitution/` files,
byte-identical to `evotrader_bundle.py`'s embedded `_SRC` dict) and left two
gaps as explicitly bigger, separate work: no bundler to regenerate the
bundle *from* the real files, and no CLI entrypoint running live commands
against the real files. This session closes the first gap.

New `sync` command on the existing `tools/edit_bundle_module.py` (already
the sanctioned way to touch bundle internals):

```
python3 tools/edit_bundle_module.py sync           # regenerate _SRC from real files, write bundle
python3 tools/edit_bundle_module.py sync --check    # report drift, exit 1, don't write
```

`sync_from_files(bundle_text, root)` walks every `_SRC` module (via the same
`_PKGS`-driven module→path mapping the drift-guard test already used),
reads the corresponding real file, and replaces that module's `_SRC` entry
with its content — the reverse direction of `extract`. The `_pkgs`/
`_module_to_path` helpers that used to live only inside
`tests/test_unflattened_files_match_bundle.py` are now `pkgs`/
`module_to_path` on `tools/edit_bundle_module.py` itself (parameterized by
`root` instead of a module-level `REPO_ROOT` global, so they're usable
against a scratch tree in tests, not just the real repo) — the test file
now imports them instead of keeping its own copy, no behavior change there.

New `tests/test_bundle_sync_from_files.py` (10 tests, suite 209 → 219):
synthetic-tree unit tests for `pkgs`/`module_to_path`/`sync_from_files`
(package vs. plain-module path mapping, drift pulls new content in,
already-in-sync is a true no-op, missing real file raises
`FileNotFoundError` naming the module) via `tmp_path`, never touching the
real repo, plus one real-repo test confirming `sync_from_files` against the
actual `evotrader_bundle.py` and actual package tree is a no-op today (i.e.
the two copies genuinely haven't drifted since the weekend session).

## Verification against real data, not just the synthetic tests

- `sync --check` against the real repo: "bundle already matches real files,
  no changes", exit 0.
- `sync` (write mode) against the real repo: same md5 before/after
  (`3835305b96044055bc17d43358e2bfba`) — confirmed no-op, not just claimed.
- Drift-detection sanity check: appended a comment line to `core/types.py`,
  re-ran `sync --check` — got `DRIFT: bundle does not match real files`,
  exit 1, confirming the check path isn't vacuously always-pass. Restored
  `core/types.py` from a backup immediately after; `git status --porcelain`
  confirms the working tree is clean on that file post-restore.
- `tools/edit_bundle_module.py verify` (the pre-existing round-trip check):
  still clean.
- `py_compile` clean on the two edited files, the new test file, and
  `evotrader_bundle.py` itself.
- Full suite: 219 passed (up from 209 — the 10 new sync tests; no existing
  test changed behavior).
- `evotrader_bundle.py` untouched: `git status` shows no change to it, and
  its md5 (checked during the write-mode no-op test above) matches the
  weekend session's recorded `3835305b96044055bc17d43358e2bfba`.
- `live_state.json` md5 unchanged (`af16ffdc22a57c5d63a83003216a8f99`),
  `evotrader.manifest` md5 unchanged (`0bf3a7d9411ee692d0a9f152a7533803`),
  `constitution verified 8b74865634b1db07` on every invocation.
- No genome promotion — no README `## Status` update needed.

## What's still open

Item 7's remaining, explicitly-bigger gap: no CLI entrypoint runs the live
commands (`tick`/`summary`/`evolve`/...) against the real `core`/`agents`/
`loop`/`constitution` packages instead of the bundle. That's the actual
cutover and needs its own dedicated, careful session — this one only makes
the two trees mechanically re-syncable, it doesn't change which one is
live. `evotrader_bundle.py` remains what every scheduled command executes.

No push notification sent — infrastructure/maintainability work with zero
effect on live trading behavior, not a safety finding or a promotion.
