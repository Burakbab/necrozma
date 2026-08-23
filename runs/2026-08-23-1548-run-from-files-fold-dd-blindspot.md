# run_from_files.py: fold-dd-blindspot diagnostic — 2026-08-23 15:48 UTC

3-hourly check. Prior scheduled session ended ~12:54 UTC; this one picked up
where it left off on AGENTS.md item 7's still-open remaining piece.

## Setup

- `git pull` landed the container in detached HEAD (cloud clone quirk); reset
  local `main` to `origin/main` (same commit, no divergence — just not on a
  branch yet). `pip3 install -r requirements.txt -q` for numpy/pandas.
- Checked `live_state.json`'s `updated` (`2026-08-23T00:22:00+00:00`) against
  `runs/2026-08-23-0020-daily-trading.md`: today's bar already processed by
  the 00:20 UTC daily run. `tick` not run this session. `review-hard-calls`:
  0 pending.

## What shipped

`run_from_files.py` grows a third read-only diagnostic: `fold-dd-blindspot`
(the command that explains the "-34.1% vs -46.5% maxDD" gate blind spot the
2026-08-22 weekend all-hands session fixed at the constitution level). Body
transcribed verbatim from `evotrader_bundle.py`'s own `elif cmd ==
"fold-dd-blindspot"` block — same discipline as `holdout-pressure`/`regime`
before it.

This one also needed `_reconstruct_champion_genome` for `--also-version N`
support. That helper lives in `evotrader_bundle.py` as plain CLI-script code
(defined at module level, not inside any of the 15 `_SRC` entries), so it
isn't importable from the real files the way `Evaluator`/`run_backtest` are —
duplicated verbatim into `run_from_files.py` instead. If `succession-audit`
(the other diagnostic using this helper) gets added here in a future
session, the duplication is already in place.

## Verification

- `python3 evotrader_bundle.py fold-dd-blindspot` vs `python3
  run_from_files.py fold-dd-blindspot`: byte-identical stdout.
- Same comparison with `--also-version 2`: byte-identical stdout.
- `live_state.json` md5 unchanged throughout both manual runs
  (`af16ffdc22a57c5d63a83003216a8f99`).
- No automated test added, same reasoning as `regime`: this command calls
  `core.market.load_universe` (via `Evaluator.evaluate`/`run_backtest`),
  which needs network access on a cold `state/cache` (gitignored) — adding
  it to the automated suite would make the suite's runtime and
  offline-ability depend on Binance being reachable. `tests/
  test_run_from_files_matches_bundle.py`'s docstring updated to name both
  `regime` and `fold-dd-blindspot` as manually-verified-only.
- `py_compile run_from_files.py`: clean.
- Full suite: 223 passed (unchanged count — no new pure function or test,
  matching `regime`'s precedent exactly).
- `tools/edit_bundle_module.py verify`: round-trip clean.
- `tools/edit_bundle_module.py sync --check`: no drift.
- `evotrader_bundle.py` md5 unchanged (`3835305b96044055bc17d43358e2bfba`).
- `evotrader.manifest` md5 unchanged (`0bf3a7d9411ee692d0a9f152a7533803`).
- `constitution verified 8b74865634b1db07` on every invocation.
- No genome promotion this session — no README `## Status` update needed.

## Next

`succession-audit` is the next candidate by cost class (same
`_reconstruct_champion_genome` helper already in place here, just a heavier
per-champion loop — 3 champions today, ~2 minutes). But today alone has now
seen four sessions grow this read-only surface (entrypoint, then two more
diagnostics, now this one) without moving the actual cutover
(`tick`/`evolve` against the real files) forward at all. Whoever picks up
item 7 next should weigh continuing this pattern against either attempting
a genuinely scoped piece of the real cutover, or picking up a different open
item (the 4h-bar third-plateau question, the vacuous-regression-check
thread, or item 4's "first real hard-call flag" trigger) instead.

No push notification sent — infrastructure/maintainability work with zero
effect on live trading behavior, same reasoning as every prior item-7
session today.
