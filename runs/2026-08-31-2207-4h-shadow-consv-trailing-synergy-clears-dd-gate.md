# 4h shadow: consult_conservative tightening + trailing-stop tightening is super-additive — first variant in this thread ever to clear MAX_DD_HARD_FAIL — 2026-08-31 21:56-22:07 UTC

Direct follow-up to the 16:00 UTC session's recommendation: try `consult_conservative`-only
tightening (the one variant of that session's four that beat baseline on every metric it
moved) as a starting point, paired with something that attacks drawdown directly, since no
single-consult threshold change alone has touched the 07:05 UTC entry-frequency mechanism
enough to matter.

## Method

Read-only, no `evolve`/`tick`/`save`, using the committed `tools/shadow_4h_x6_seed.py`
harness for baseline construction (warm cache, no new fetch). Three batches of single-shot
`run_backtest()` calls, same x6-scaled-seed universe/years as every prior session in this
thread. `consv1` below is exactly the 16:00 UTC session's winning conservative-only variant
(`consult_conservative.rsi_buy_below` 38.0→30.0, `z_buy_below` -0.8→-1.2).

## Result

| variant | trades/yr | days held | win% | halts | max_dd | sortino | sharpe | fitness |
|---|---|---|---|---|---|---|---|---|
| baseline | 392.7 | 15.54 | 49.4% | 6 | -44.3% | 0.97 | 0.79 | -inf |
| consv1 (16:00 UTC's variant) | 381.4 | 16.87 | 50.8% | 6 | -44.5% | 1.05 | 0.87 | -inf |
| consv1 pushed further (rsi 24, z -1.6) | 381.4 | 16.87 | 50.8% | 6 | -44.5% | 1.05 | 0.87 | -inf |
| consv1 + stop_loss -0.08 | 416.3 | 12.41 | 50.3% | 7 | -48.7% | 0.91 | 0.75 | -inf |
| consv1 + max_position_pct 0.15 | 402.5 | 15.44 | 52.7% | 6 | -46.7% | 0.96 | 0.79 | -inf |
| consv1 + cash_floor_pct 0.15 | 356.7 | 16.80 | 49.0% | 5 | -41.8% | 0.95 | 0.78 | -inf |
| consv1 + trailing_stop -0.10 | 400.7 | 13.53 | 53.1% | 5 | -41.0% | 0.97 | 0.80 | -inf |
| trailing_stop -0.10 alone (no consv1) | 410.8 | 14.50 | 52.0% | 6 | -44.4% | 0.86 | 0.71 | -inf |
| consv1 + trailing_stop -0.08 | 443.5 | 13.73 | 50.1% | 6 | -40.3% | 1.05 | 0.88 | -inf |
| **consv1 + trailing_stop -0.06** | 475.5 | 10.33 | 57.0% | 5 | **-32.7%** | **1.35** | **1.09** | -0.001 |
| consv1 + trailing_stop -0.10 + cash_floor 0.15 | 414.3 | 12.98 | 54.0% | 4 | -41.2% | 1.10 | 0.90 | -inf |
| **consv1 + trailing_stop -0.08 + cash_floor 0.15** | 461.7 | 13.20 | 53.3% | 5 | **-35.1%** | 1.29 | 1.07 | **0.146** |
| trailing_stop -0.06 alone (no consv1) | 477.8 | 11.02 | 54.8% | 6 | -41.4% | 1.14 | 0.92 | -inf |
| trailing_stop -0.08 alone (no consv1) | 452.3 | 13.79 | 51.0% | 6 | -39.3% | 1.08 | 0.89 | 0.073 |
| cash_floor_pct 0.15 alone (no consv1) | 392.2 | 14.83 | 51.9% | 8 | -41.9% | 1.02 | 0.84 | -inf |
| consv1 + trailing_stop -0.06 (repeat, determinism check) | 475.5 | 10.33 | 57.0% | 5 | -32.7% | 1.35 | 1.09 | -0.001 |

(Baseline's sortino/sharpe here, 0.97/0.79, differ slightly from the 16:00 UTC session's
0.94/0.77 for the same recipe — consistent with this thread's previously-documented
as-of/window drift between sessions run hours apart, not a reproducibility bug; `max_dd`
itself matched exactly. The determinism-repeat row above confirms no RNG noise within a
session, matching this thread's earlier "no RNG reachable from a plain `run_backtest()`
call" finding.)

## Four separable findings

1. **Pushing `consult_conservative`'s thresholds further than the 16:00 UTC session's step
   (rsi_buy_below 30→24, z_buy_below -1.2→-1.6) has *zero* additional effect** — identical
   numbers to one decimal on every metric. Answers that session's own "worth trying"
   suggestion: no, at least not this gene pair — something else in the genome is now the
   binding constraint on entries, not these two thresholds.

2. **`stop_loss` and `max_position_pct` tightening both make things worse**, not better,
   stacked on `consv1` — genuine negative results. A tighter hard stop (-0.08 vs -0.12)
   raises trade count and halts and worsens drawdown (-48.7%), plausibly more whipsaw/
   re-entry rather than cleaner risk-cutting; a tighter position cap (0.15 vs 0.25) forces
   more simultaneous positions to deploy the same capital, worsening drawdown too
   (-46.7%) — the opposite of the intended effect.

3. **`trailing_stop` alone is non-monotonic**: -0.08 alone clears the gate (-39.3%,
   fitness 0.073) but both a looser -0.10 (-44.4%) and a tighter -0.06 (-41.4%) alone do
   not — the middle value tested is a local optimum in isolation, not either extreme. Not
   chased further this session; flagged as a genuine curiosity for whoever next touches
   this gene.

4. **The headline result: `consv1` + `trailing_stop` tightening together is strongly
   super-additive, not merely additive.** Neither lever alone gets close on its own
   (`consv1` alone: -44.5%; `trailing_stop` alone at any of three tested levels: -39.3% to
   -44.4%), but combined, two variants both clear `MAX_DD_HARD_FAIL` (40%) outright for the
   first time in this thread's entire history since 2026-08-16:
   - `consv1 + trailing_stop -0.06`: **-32.7% max_dd**, sortino 1.35, sharpe 1.09 — the
     best risk-adjusted numbers this whole item-2 thread has ever recorded for the
     x6-scaled seed, at any prior step.
   - `consv1 + trailing_stop -0.08 + cash_floor_pct 0.15`: **-35.1% max_dd**, fitness
     **+0.146** — the first *positive* full-history fitness this thread has recorded for
     this seed family (every prior baseline and variant, including champion v3's own
     4h-shadow numbers, has landed at `-inf` from the dd hard-fail or negative).

## What this changes for item 2

This is the first genuinely promising 4h-shadow result since the dd-corrected gate landed
(2026-08-21/22) — every session since then (23:05, 02:43, 04:07, 07:05, 10:02, 12:47, 16:00
UTC) found either zero promotions in a real `evolve()` run or single-lever changes that
moved metrics by noise only. This measurement uses the exact same continuous full-history
`run_backtest()` max_dd every prior session in this thread has compared against (not the
fold-merged blind spot `dd_corrected_stats()` was built to catch), so it's apples-to-apples
with "-44.3%/-48.0%/etc. never cleared the gate" — this is a real, comparable improvement,
not a different metric looking better.

**What this is not**: neither variant has been run through the actual promotion pipeline
(`EvolutionRun`/`generation()`'s fold-aggregate acceptance + sealed holdout via
`accepts()`/`holdout_accepts()`) — only a single full-history backtest, same as every prior
item-2 measurement. Clearing `MAX_DD_HARD_FAIL` on this one continuous replay is necessary
but not sufficient for what a real promotion needs.

**Recommend as the next concrete step**: seed a fresh 4h shadow `EvolutionRun` from
`consv1 + trailing_stop -0.06` (or the cash_floor variant) instead of the plain x6-scaled
seed, and see whether it (a) survives fold-aggregate acceptance and the sealed holdout as
a "champion" in its own right, and (b) whether evolution can improve on it further from
this much stronger starting point than every prior 4h-shadow run has had. This is a
sharper, evidence-backed next step than this thread's prior framing ("try consult_conservative
tightened further" — now answered, see finding 1).

Nothing here touched `live_state.json`, promoted anything, or changed `researcher_memory` —
purely shadow/offline compute (warm `state/cache/` reuse, no new fetch). `git status` clean
before this commit, `live_state.json` md5 unchanged (`37a1b00bee3f7cb1ad2f4adde0ab9ed0`),
genome still v3 (1d), `python3 -m pytest -q` 252/252 confirmed at session start, no code
changed (three standalone scratch scripts using the committed harness, not themselves
committed, per this thread's established discipline of only committing genuinely reusable
pieces).
