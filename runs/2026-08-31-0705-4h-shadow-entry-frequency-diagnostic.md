# 4h shadow: the drawdown isn't from faster flips or a per-bar position cap — it's entry frequency, and a new confound (max_new_positions_per_bar) is ruled out — 2026-08-31 06:47-07:05 UTC

Direct follow-up to the 04:07 UTC session's sharpened open question for item 2: is the
x6-scaled 4h seed genuinely too aggressive, or is there still an un-scaled mechanical
confound? That session ruled out `run_backtest`'s `warmup` default and
`constitution.CIRCUIT_BREAKER_COOLDOWN`. This session took a different angle: instead of
testing more harness constants, characterized *how* the x6-scaled seed's drawdown
happens (trade frequency, holding period, win rate) via direct `run_backtest()` calls —
no evolution needed — and found one previously-unexamined un-scaled genome gene, tested
it, and ruled it out too.

## Method

Read-only, no `evolve`/`tick`/`save`. Imported `core.genome`, `core.market`,
`loop.engine` directly from the real repo files (same discipline `run_from_files.py`
already uses — pure functions, no state mutation) rather than the bundle, since no CLI
entrypoint was needed. Never opened the real `live_state.json`; the live champion v3's
genome was exported once to a standalone JSON file via a read-only `json.dump` and
loaded from there. Fetched fresh 4h and 1d data (27 symbols x 4y, Binance) into the
real repo's `state/cache/` (shared, reusable cache — not `live_state.json`). Three
single-shot `run_backtest()` calls (full history, no walk-forward, no search):

1. **v3 (live champion) at 1d** — the real genome, real bar size, as a control.
2. **x6-scaled 4h seed** — same recipe as every prior 4h-shadow session (period genes
   x6, `max_bars_held`/`min_bars_held` x6).
3. **Raw unscaled 4h seed** — bar_interval flipped to 4h, every gene left at its 1d
   value (same construction as the 2026-08-17 0820 UTC session's unscaled-seed run).

## Result 1: trade frequency, not holding-period, is what's inflated

| | trades/yr | avg days held | win rate | halts | max_dd | sortino |
|---|---|---|---|---|---|---|
| v3 (1d, live) | 277 | 9.09 | 35.7% | 6 | -46.5% | 1.04 |
| seed, x6-scaled (4h) | 1278 (4.6x) | 10.71 | 67.7% | 7 | -66.1% | -0.29 |
| seed, unscaled (4h) | 2114 (7.6x) | 4.37 | 49.8% | 9 | -77.1% | -0.84 |

(v3's own full-history continuous max_dd of -46.5% matches the 2026-08-30 18:51 UTC
succession-audit's recorded number closely — confirms this methodology reproduces known
numbers before trusting the new ones.)

The x6-scaled seed's `avg_days_held` (10.71) is not shorter than v3's (9.09) — if
anything slightly longer. That rules out "positions get flipped in and out faster" as
the overtrading mechanism. What's actually inflated 4.6x is the *rate of new entries*:
far more distinct trades get opened per unit calendar time across the 27-symbol
universe, each one a normal-length hold, not a rash of quick round-trips. The unscaled
seed shows the opposite shape (much shorter holds, 4.37 days) and is worse on every
metric — consistent with, and now quantifying, the 2026-08-17 0820 UTC session's
qualitative finding that manual period-scaling is a real improvement over no scaling
at all, just not sufficient on its own.

Also notable and not previously measured: the x6-scaled seed's win rate (67.7%) is
*higher* than v3's own (35.7%), yet its Sortino is negative and its drawdown far worse
— a lot of small wins offset by large, insufficiently-controlled losses, not a
signal-quality problem per se.

## Result 2: a new candidate confound, tested and ruled out

`superior_judge.max_new_positions_per_bar` (seed value 3) caps new position opens
*per bar*, not per day. At 4h (6 bars/day) that's a ceiling of 18 new positions/day
versus the 1d-intended 3/day — a 6x looser cap that no prior 4h-shadow session's
scaling recipe touched (only the analyst's period genes and `max_bars_held`/
`min_bars_held` were ever scaled). Mechanically distinct from the 04:07 UTC session's
two harness-level constants (this one lives in the genome itself, and is a rate cap,
not a lookback period), so worth checking in isolation before folding it into "genuinely
too aggressive."

Same isolated-variable-swap method as the 04:07 UTC warmup/cooldown check: x6-scaled
seed with `max_new_positions_per_bar` at its seed value (3) vs. tightened to 1 (the
closest integer approximation of "~3/day" at 4h), 4h data, otherwise identical genome.

| variant | trades/yr | avg days held | halts | max_dd | sortino |
|---|---|---|---|---|---|
| cap=3 (baseline) | 1278 | 10.71 | 7 | -66.1% | -0.29 |
| cap=1 | 1306 | 10.34 | 8 | -65.7% | -0.11 |

Trade count barely moved (actually rose slightly) and max_dd improved by 0.4 points —
noise, not a fix, same as the warmup/cooldown result. Reads as: the per-bar cap rarely
actually binds in practice (rarely are there >1 fillable high-conviction buy signal in
a single 4h bar), so it isn't where the extra trade volume comes from. **Ruled out** as
a meaningful driver.

## What this changes for item 2

Sharpens, doesn't reopen, the open question. Two harness constants (04:07 UTC) and now
one genome rate-cap gene are ruled out as the source of the x6-scaled seed's
catastrophic drawdown. The entry-frequency finding above points at a different, more
promising place to look: the *threshold* genes that gate individual entries/exits
(`consult_risky`/`consult_moderate`/`consult_conservative`'s RSI bands, z-score bands,
`min_trend`/`min_breakout`/`min_rank_mom` minimums) were never touched by any x6-scaling
recipe or any prior hand-tuning attempt — only period-length genes and the two
bars-held genes were ever scaled. If 4h bars are simply noisier per-bar than daily
closes (which average out a lot of intrabar movement), the same RSI/z-score/trend
thresholds tuned against 1d noise would fire far more often against 4h noise without
any of the *period* genes needing to change — exactly the entry-frequency-not-hold-time
shape measured above. **This is now the sharpest, most concretely scoped candidate for
"genuinely hand-retuned, not just scaled"**: not re-guessing every period again, but
specifically widening/tightening the consult threshold genes (independent of period
scaling) and re-measuring trade frequency the same way this session did, before
committing to a full evolution run on a new starting point.

Nothing here touched `live_state.json`, promoted anything live, or changed
`researcher_memory` — purely shadow/offline compute (fresh `state/cache/` entries only,
not gitignored's problem to solve). `git status` clean, `live_state.json` md5 unchanged
throughout, genome still v3 (1d), `python3 -m pytest -q` 243/243 confirmed at session
start.
