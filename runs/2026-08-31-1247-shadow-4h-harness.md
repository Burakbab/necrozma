# 4h shadow: reusable x6-scaled-seed harness shipped, reproduces the 10:02 UTC baseline exactly — 2026-08-31 12:47-12:59 UTC

Direct follow-up to the 10:02 UTC session's flagged methodological gap: two sessions in
a row (07:05 UTC, 10:02 UTC) hand-built the same documented "x6-scaled seed" recipe for
4h-shadow work in an uncommitted scratch script, and their baselines for what should be
the identical genome didn't match (1278 vs. 392.7 trades/yr) with no way to diff the two
scripts after the fact. The 10:02 UTC session recommended committing a small, never-
scheduled, reusable harness for this specific recipe so future runs are diffable.

## What shipped

`tools/shadow_4h_x6_seed.py` — read-only, no `evolve`/`tick`/`save`, never touches
`live_state.json`, not wired into any scheduled command, the bundle, or
`run_from_files.py`:

- `build_x6_scaled_seed(bar_interval="4h")` builds the genome via `Genome.child()`
  (the same provenance-tracked mechanism evolution itself uses, not ad hoc dict
  mutation): sets `bar_interval` and multiplies the nine period-length `analyst`
  genes (`trend_fast`, `trend_slow`, `rsi_len`, `vol_short`, `vol_long`,
  `breakout_len`, `z_len`, `regime_ma`, `volume_len`) plus the two `risk` genes
  (`max_bars_held`, `min_bars_held`) by 6 — exactly the recipe every 4h-shadow
  session since 2026-08-16 has described in prose.
- `summarize()`/`print_report()` reproduce the same metrics table every prior
  4h-shadow run note has hand-assembled (trades/yr, avg days held, win rate,
  halts, max_dd, sortino, sharpe, fitness).
- A CLI (`--bar-interval`, `--years`, `--refresh`, `--warmup`) that fetches the
  live champion's 27-symbol universe at the target interval and runs one
  single-shot full-history `run_backtest()`.

`tests/test_shadow_4h_x6_seed.py` — 9 new hermetic tests, no network/market data:
scaling math is correct per-gene, non-period genes are left untouched, the result
is a `Genome.child()` (versioned, provenance-tracked) not a seed mutation, default
`bar_interval` is `"4h"`, and `summarize()`'s bars-held-to-days conversion is
correct for all three supported intervals. Full suite: 252/252 (243 prior + 9 new).

## Live verification

Ran the harness for real against a warm 4h/4y cache (27 symbols, fetched once,
`state/cache/*.pkl`, gitignored):

| trades/yr | avg days held | win rate | halts | max_dd | sortino | sharpe | fitness |
|---|---|---|---|---|---|---|---|
| 392.7 | 15.54 | 49.4% | 6 | -44.3% | 0.94 | 0.77 | -inf |

This **exactly reproduces the 10:02 UTC session's own baseline** on every reported
metric. `fitness` correctly reports `-inf`: max_dd (44.3%) exceeds
`constitution.MAX_DD_HARD_FAIL` (40%), a hard-gate fail per `constitution.fitness()` —
expected given every prior session's numbers for this seed, not a harness bug.

## What this does and doesn't settle

Exact reproduction of the more recent session's baseline is the strongest evidence
yet that the 07:05-vs-10:02 UTC gap (1278 vs. 392.7 trades/yr) was a genuine
construction difference in the 07:05 session's script, not environment noise,
non-determinism, or a subtle harness bug in either session — but since that script
was never committed, the exact line that diverged still cannot be identified after
the fact. That specific mystery stays open and is now unrecoverable; what changes
going forward is that it can't recur silently, since every future 4h-shadow session
using this recipe now has one committed, diffable construction to run against
instead of a fresh hand-rolled script each time.

## Next steps

Use this harness, not a new scratch script, for the next variant test on the
x6-scaled seed. The 07:05 UTC session's standing suggestion — testing
`correlation_penalty` on the x6-scaled seed independent of period scaling, since
consult-threshold tightening (10:02 UTC) was ruled out as a free-lunch drawdown
fix — is the natural next step and was not attempted this session (time spent on
the harness itself plus its live verification).

Nothing here touched `live_state.json`, promoted anything, or changed
`researcher_memory` — purely a new committed tool plus its tests and a read-only
live smoke-test. `git status` clean before this commit, `live_state.json` md5
unchanged (`37a1b00bee3f7cb1ad2f4adde0ab9ed0`), genome still v3 (1d),
`python3 -m pytest -q` 252/252 (243 prior + 9 new).
