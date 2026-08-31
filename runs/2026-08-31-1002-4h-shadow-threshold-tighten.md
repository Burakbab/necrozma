# 4h shadow: tightening consult thresholds cuts trade count but doesn't fix drawdown — and the baseline itself didn't reproduce the 07:05 UTC session's numbers — 2026-08-31 09:46-10:02 UTC

Direct follow-up to the 07:05 UTC session's sharpened recommendation for item 2: with
period-length genes and the two bars-held genes already ruled out (04:07, 07:05 UTC) and
`max_new_positions_per_bar` ruled out (07:05 UTC), the next candidate mechanism was the
*threshold* genes that gate individual entries/exits — RSI bands, z-score bands,
`min_trend`/`min_breakout`/`min_rank_mom` minimums across all three consults — never
touched by any x6-scaling recipe or prior hand-tuning attempt.

## Method

Read-only, no `evolve`/`tick`/`save`, same discipline as every prior 4h-shadow session:
imported `core.genome`, `core.market`, `loop.engine` directly from the real repo files,
never opened `live_state.json`, fresh `state/cache/` entries only (this container starts
with an empty cache every session — confirmed no pre-existing `.pkl` files before the
fetch). Built the same x6-scaled seed recipe every prior session has used (`trend_fast/
slow`, `rsi_len`, `vol_short/long`, `breakout_len`, `z_len`, `regime_ma`, `volume_len`,
`max_bars_held`, `min_bars_held` all x6), then a second genome from it with nine consult
threshold genes tightened (independent of any period gene):

| gene | seed | tightened |
|---|---|---|
| `consult_risky.min_rank_mom` | 0.70 | 0.85 (top 15% not top 30%) |
| `consult_risky.rsi_max` | 82.0 | 75.0 |
| `consult_risky.min_breakout` | -0.02 | -0.01 (closer to N-bar high) |
| `consult_moderate.min_trend` | 0.005 | 0.015 |
| `consult_moderate.rsi_lo` / `rsi_hi` | 45.0 / 72.0 | 50.0 / 65.0 (narrower band) |
| `consult_moderate.min_rank_mom` | 0.50 | 0.65 |
| `consult_conservative.rsi_buy_below` | 38.0 | 30.0 (deeper dip required) |
| `consult_conservative.z_buy_below` | -0.8 | -1.2 (rarer trigger) |

Fetched fresh 4h data for the 27-symbol universe (4y, Binance) — 8766 bars per symbol,
exactly the requested window, no gap warnings. Two single-shot `run_backtest()` calls
(full history, no walk-forward), back-to-back in the same process on the same data.

## Result: tightening works as a frequency lever, not a drawdown fix

| | trades/yr | avg days held | win rate | halts | max_dd | sortino | sharpe |
|---|---|---|---|---|---|---|---|
| baseline (x6-scaled seed) | 392.7 | 15.54 | 49.4% | 6 | -44.3% | 0.94 | 0.77 |
| tightened thresholds | 327.8 | 14.72 | 44.8% | 8 | -48.0% | 0.76 | 0.65 |

Trade frequency did drop (392.7 → 327.8/yr, -16.5%) as the noise hypothesis predicted.
But drawdown got *worse*, not better (-44.3% → -48.0%), halt count rose (6 → 8), and both
risk-adjusted metrics fell (sortino 0.94 → 0.76, sharpe 0.77 → 0.65). Fewer, more
selective entries did not translate into a shallower drawdown here — if anything the
portfolio got slightly more concentrated risk per trade without the volume of entries
to diversify across, worse on every dimension except raw count. **This is a genuine
negative result for "the consult thresholds are where the 4h noise problem lives"** —
narrowing them is not, on its own, the fix item 2's framing hoped for.

## An unresolved discrepancy, flagged rather than papered over

This session's baseline numbers do not reproduce the 07:05 UTC session's baseline for
what should be the identical x6-scaled seed: 392.7 vs. 1278 trades/yr, 15.54 vs. 10.71
avg days held, -44.3% vs. -66.1% max_dd, sortino +0.94 vs. -0.29. Checked and ruled out
as explanations:

- **Gene construction mismatch** — the full scaled genome was dumped and checked
  gene-by-gene against the documented x6 recipe (this file's "Next steps" item 2
  history); every value matches.
- **Data gaps/quality** — 8766 bars/symbol, exactly 4.0 years at 6 bars/day, no gap
  warning from `load_universe`.
- **`run_backtest`'s `warmup` default** — re-ran the same baseline at `warmup=60` (the
  default) and `warmup=360` (x6-scaled, matching the period genes): trades/yr 392.7 vs.
  405.7, max_dd -44.30% vs. -44.31% — moves by noise only, doesn't explain a 3x gap.

No RNG is in the `run_backtest`/Council path (`agents/researcher.py`'s `random.Random`
is evolution-proposal-only, `loop/engine.py`'s `np.random.default_rng` is the
bootstrap-resampling diagnostic only — neither is reachable from a plain
`run_backtest()` call), so this isn't a seed-dependent non-determinism. The two numbers
in *this* session's own table are trustworthy relative to each other (same script, same
process, same data, back-to-back) — that comparison is what the table above reports on.
But neither this session nor the 07:05 UTC one had its scratch script committed (per
this thread's standing "no code changed, standalone scratch script" discipline), so a
line-by-line diff against the earlier run isn't possible after the fact. **Flagging
this as a new, sharper methodological open question**: before trusting any single
4h-shadow baseline number in isolation again, a future session should either (a) commit
a small reusable (but never scheduled) scratch harness for this specific "build x6-seed,
run full-history backtest" recipe so results are diffable and reproducible run-to-run,
or (b) re-run this exact recipe twice in the same session to confirm it's stable before
comparing across sessions at all.

## What this changes for item 2

Threshold-gene tightening is tested and, on this one specific set of nine gene changes,
does not fix the drawdown problem — it's a real trade-off (fewer trades, worse
risk-adjusted numbers), not a free lunch. Doesn't rule out threshold genes entirely
(only one direction and one specific combination was tried; a different combination,
e.g. loosening exits rather than tightening entries, or thresholds on `consult_risky`
alone vs. all three consults, is untested), but removes "just tighten everything" as
the easy next guess. Combined with the reproducibility flag above, recommends the next
session either (a) re-establish a solid, reproducible baseline number before testing
more variants, or (b) pick a different mechanism entirely — the entry-frequency finding
(07:05 UTC) still holds regardless of the absolute trade-count number, so testing
correlation-aware entry gating (`correlation_penalty`, already a known-relevant gene
from the very first 4h promotions) independent of period scaling is a reasonable
next candidate.

Nothing here touched `live_state.json`, promoted anything live, or changed
`researcher_memory` — purely shadow/offline compute (fresh `state/cache/` entries only).
`git status` clean, `live_state.json` md5 unchanged (`37a1b00bee3f7cb1ad2f4adde0ab9ed0`),
genome still v3 (1d), `python3 -m pytest -q` 243/243 confirmed at session start, no code
changed (three standalone scratch scripts, not committed).
