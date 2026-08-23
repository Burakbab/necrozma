# 2026-08-23 09:46 UTC — 3-hourly self-improvement check: run_from_files.py

## Context

Pulled clean (origin/main was 8 commits ahead — bundler-sync-tool,
weekend-all-hands push, consult-role-test, shadow-evolve rounds 4/5, daily
trading, daily discussion). `live_state.json`'s `updated` timestamp
(2026-08-23T00:22:00+00:00) and `runs/2026-08-23-0020-daily-trading.md`
confirm today's daily bar was already handled by the 00:20 UTC scheduled run.
`review-hard-calls` reports 0 pending. No `tick` run this session — no
double-trade risk.

## What was built

AGENTS.md's "Next steps" item 7 (unflatten `evotrader_bundle.py`) has, as of
this morning, real `core`/`agents`/`loop`/`constitution` packages on disk
(weekend all-hands) and a bundler to regenerate the bundle from them
(0648 bundle-sync-tool session). The one piece both of those sessions left
open, explicitly flagged three times running now as "bigger, riskier,
separate session": no CLI entrypoint actually runs the live commands against
the real files instead of the bundle.

That full cutover (wiring up `tick`/`evolve`, deciding whether a scheduled
run should ever point at the real files) is still too big and risky for one
3-hourly slot — a bug in a state-mutating command could double-trade or
corrupt `live_state.json`. But a safe, useful slice of it fits: the two
commands that never call `acct.save()` — `summary` and `signals` — are pure
reads. Wiring those up against the real files first, and proving them
byte-identical to the bundle's output, is a genuine step forward with none of
the downside risk.

New `run_from_files.py` at the repo root:
- Imports `constitution` and `core.live.LiveAccount` directly — ordinary
  Python imports, no meta-path finder involved (that only gets installed by
  importing `evotrader_bundle`, which this file deliberately never does; the
  real `core/`/`agents/`/`loop/`/`constitution/` directories resolve via
  normal package import).
- Calls `verify()` the same way `evotrader_bundle.main()` does, but does
  *not* populate `constitution.EMBEDDED_SOURCES` — so `constitution.
  checksum()` takes its dormant file-based branch (hashing the real
  `constitution/__init__.py` + `core/portfolio.py` on disk) instead of the
  bundle-mode branch. Confirmed this reproduces `evotrader.manifest`'s
  `8b74865634b1db07` exactly, same as the weekend all-hands session first
  found when it exercised this branch.
- Supports only `summary`/`signals`; any other command (`tick`, `evolve`,
  etc.) prints an explanatory message and exits 1 rather than silently doing
  something unverified.

## Verification

Manual, against the real live `live_state.json`:
```
python3 run_from_files.py summary   # byte-identical to evotrader_bundle.py summary
python3 run_from_files.py signals   # byte-identical to evotrader_bundle.py signals
python3 run_from_files.py bogus     # exit 1, explanatory message, no state touched
```
Eyeballed both outputs line-for-line against the bundle's own output — identical.

New `tests/test_run_from_files_matches_bundle.py` (3 tests, suite 219 → 222):
runs both entrypoints as subprocesses (never imported in the same
interpreter as the bundle-importing test suite, to avoid the real on-disk
packages and the bundle's meta-path finder fighting over the same module
names), asserts `summary`/`signals` stdout is byte-identical between the two
entrypoints, asserts `live_state.json` is provably unmodified by either
read-only command (hash-compared before/after), and asserts the unsupported-
command rejection path.

Full suite: `python3 -m pytest -q` → 222 passed.

Safety checks:
- `py_compile` clean on `run_from_files.py` and the new test file.
- `tools/edit_bundle_module.py verify` — round-trip clean.
- `tools/edit_bundle_module.py sync --check` — no drift.
- `git status` — pure addition, two new untracked files, zero existing lines
  touched.
- `live_state.json` md5 unchanged: `af16ffdc22a57c5d63a83003216a8f99`.
- `evotrader.manifest` md5 unchanged: `0bf3a7d9411ee692d0a9f152a7533803`.
- `evotrader_bundle.py` md5 unchanged: `3835305b96044055bc17d43358e2bfba`.
- `constitution verified 8b74865634b1db07` on every invocation.
- `review-hard-calls`: 0 pending.
- No genome promotion — no README `## Status` change needed.

## What this is not

Not the cutover. `evotrader_bundle.py` remains the live path; nothing about
what a scheduled run executes changed. `run_from_files.py` is not referenced
by any scheduled task, cron, or run protocol step. `tick`/`evolve` are not
wired up here — that's still explicitly the separate, riskier session
AGENTS.md's item 7 has flagged repeatedly.

## Next

Whoever picks up item 7 next has two remaining pieces, in rough order of
size: (1) wire `tick`/`evolve` up against the real files the same way, which
needs real care since a bug could double-trade or corrupt `live_state.json`
— probably wants its own scratch-isolated verification pass the way the
shadow-evolve sessions use, before ever running it against the real state
file; (2) decide, separately, whether/when a scheduled run should ever
actually point at the real files instead of the bundle at all — that's a
human call given the standing "keep the bundle working as a fallback until
confident" instruction in item 7's own text, not something to flip
unilaterally in a 3-hourly session.

No push notification sent — infrastructure/maintainability work with zero
effect on live trading behavior, same reasoning as every prior item-7
session today.
