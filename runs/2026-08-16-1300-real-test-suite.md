# Real test suite committed — 2026-08-16 ~13:00 UTC

Scheduled 3-hourly check. Today's daily bar was already handled by the 00:20
UTC run (tick 2, bar 2026-08-15) — `live_state.json`'s `updated` timestamp
(06:56:33) reflects the weekend all-hands' v3 promotion, not a new trade, and
no new daily bar has closed since. Nothing to trade this cycle.

Used the rest of the slot on the flagged top-priority gap from AGENTS.md's
"Current state": there was never a committed test suite in this repo —
`git log --all` had no test file, ever — so the old "29 tests pass" claim was
unverifiable and CI only smoke-tested compile + live command paths.

## What shipped

`tests/` — 36 `pytest` tests, entirely hermetic (no network, never touches
`live_state.json` or the repo's `state/`):

- `test_genome.py` (9) — `Genome` child/save/load/champion/promote roundtrip,
  immutability of parents, complexity accounting.
- `test_constitution.py` (18) — `fitness()`'s hard gates and drawdown/turnover
  penalties, `ranking_fitness()`'s floor, `required_margin()`'s growth with
  candidate count and complexity, `accepts()`'s full gate order (hard
  failure → margin → merged-fitness regression → drawdown regression →
  accept), `holdout_accepts()` including that the cumulative-draws margin can
  flip an otherwise-passing edge to a reject, and checksum seal/tamper
  detection.
- `test_lookahead.py` (4) — the one that matters most. A direct unit test on
  `core.market.Replay`/`ReplayWindow` proving the window at bar `i` is
  physically the same array slice whether or not bars after `i` are poisoned
  1000x, plus that fills happen at bar `i+1`'s open, never bar `i`'s close.
  Then an end-to-end test: run the same genome through `run_backtest` twice,
  identical except every bar strictly after the backtest's `end_frac` cutoff
  is multiplied 37x (prices) and zeroed (volume) in one copy — asserts
  `stats`, `nav_history`, `closed_trades`, `decision_log`, and `fitness` are
  bit-for-bit identical. A companion control test proves the comparison is
  actually sensitive (mutating a bar *inside* the window changes the result),
  so the invariance test can't be silently vacuous.
- `test_live_account.py` (5) — `LiveAccount.tick`'s same-bar idempotency
  guard: a fresh bar trades, a repeated bar returns `"skipped"` and appends
  nothing, `force=True` bypasses it, and it explicitly only compares against
  `journal[-1]` (documented as by-design, not a full-journal scan).

`.github/workflows/ci.yml` gained a `test` job running `pytest tests/ -q`,
ahead of the existing `smoke-test` job (kept as-is). `requirements.txt`
gained `pytest`.

## A mistake caught before committing

First draft of `test_genome.py` used `monkeypatch.chdir(tmp_path)` to
isolate `Genome.save/load/champion` from the real repo. That doesn't work:
`core.genome.GENOME_DIR` (like `core.live.STATE_PATH`, `core.market.CACHE_DIR`,
`loop.evolve.LINEAGE_PATH`) is computed **once**, at module-import time, from
whatever the process cwd was at that moment — not re-evaluated per test.
Since `conftest.py` imports the bundle once at collection time from the repo
root, `GENOME_DIR` was permanently `<repo root>/state/genomes` for the whole
pytest session regardless of any later `chdir`. Running the suite once with
that bug actually wrote real files into this repo's `state/`
(`champion.json`, `v1.json`, `v2.json`, `mytag.json`) before the test
assertions (which checked the wrong, tmp_path-based path) caught the
mismatch and failed loudly. Deleted the polluted `state/` dir — it's
gitignored and was never staged — and fixed the fixture to monkeypatch
`core.genome.GENOME_DIR` directly instead of relying on `chdir`. Worth
knowing for anyone adding tests here later: this bundle's cwd-derived module
paths need direct monkeypatching, not `chdir`.

## Also attempted this cycle, inconclusive

Kicked off an isolated scratch 4h-bar shadow evolution (AGENTS.md item 2's
open item: calibrate `n_blind` down from the 1d default of 14, which the
2026-08-16-0600 weekend all-hands found made each 4h generation take
25-27 minutes) with `n_blind=6`, 6 generations, from a fresh x6-scaled seed
— same setup discipline as prior runs (whole scratch dir isolated, verified
`Genome.champion() -> v1 (4h bars)` before trusting it, never touched this
repo). Still running generation 1 (21 candidates on walk-forward folds) when
this note was written — didn't finish inside this slot. No result to report;
nothing was promoted or written anywhere in the repo. Left running in the
background scratch dir; if a future session finds it (it won't — it's a
`/tmp` scratch path scoped to this container) or wants to repeat it, the
setup is: hand-scale `trend_fast/slow`, `rsi_len`, `vol_short/long`,
`breakout_len`, `z_len`, `regime_ma`, `volume_len`, `max_bars_held`,
`min_bars_held` by 6x, set `bar_interval="4h"`, save as `champion`, then run
`EvolutionRun.run(generations=N, n_blind=6)` directly (the bundled CLI's
`evolve` command hardcodes `n_blind=14`, so this needs a small standalone
script, not the CLI).
