# Shadow evolve against live champion v3 — 2026-08-16 ~10:00 UTC

Scheduled 3-hourly check. Today's daily bar was already handled by the 00:20
UTC daily run and the weekend all-hands' v2→v3 promotion at 06:56 UTC
(`live_state.json` `updated` unchanged since then) — nothing new to trade
this cycle. Used the slot on Next-steps item 3 (correlation-penalty grid)
and, incidentally, found a second real shadow promotion.

## Setup

Same pattern as the `0059` and prior shadow runs: copied `live_state.json`
(champion v3, real accumulated `researcher_memory`) into a scratch directory
outside the repo and ran `EVO_STATE=shadow_state.json python3
evotrader_bundle.py evolve 8` there — real 27-symbol 1d Binance data, real
constitution gates, writing only to the scratch copy. **Nothing here touched
the real `live_state.json`.**

## Result: a real v3→v4 shadow promotion, correlation grid still loses

**Generation 2** found a gate-passing promotion by blind search:

- **v3 → v4**: `consult_risky.min_breakout` −0.02→0.01, `consult_risky.conviction_scale`
  0.7356→0.8713, `consult_moderate.rsi_lo` 25.0→34.0452,
  `consult_conservative.min_trend` −0.01→−0.0075, `risk_judge.max_positions`
  6→2, `consult_moderate.exit_trend_below` 0→−0.0104.
  Selection fitness 1.389→1.761, merged fitness 1.591→2.300, max_dd 29.1%
  (within tolerance on v3's own dd). Sealed holdout: champion −1.172,
  challenger **+0.740**, passed (11 cumulative draws, margin 0.175).
  Holdout edge vs benchmark: excess return +42.5%, excess Sharpe +1.68,
  drawdown 24.7 points better than buy-and-hold, **beat_benchmark: true**,
  3/3 folds beating benchmark on the selection side too.

Generations 3–8 (against the new v4 champion, `n_tested_cumulative` 29→98)
found nothing that beat it — best candidates 2.08, 1.73, 1.86, 2.01, 2.03,
1.58 vs champion's rising 1.761 + widening multiple-testing margin.

**Not applied to the live account** — same scoping as every previous shadow
run in this slot: promoting a champion is out of scope for the 3-hourly
check. Flagging for the daily/weekend run same as `0059` did for v2→shadow-v4:
this specific combination may or may not be what the live account's own
blind search stumbles onto next, so it's worth a deliberate look rather than
assuming convergence.

### Correlation-penalty grid: now tried against three separate champions, never wins

All five widened-grid values (`0.1`, `0.25`, `0.5`, `0.75`, `0.9`) fired as
fresh structural proposals against the v4 champion in generations 3–8 of
this run (`researcher_memory.tested` confirms all 5 present) — none placed
in the top-4 of any generation, let alone won. Combined with prior sessions:

| value | tried against | outcome |
|---|---|---|
| 0.25, 0.5, 0.75 | v2 | lost outright (best 0.59) |
| 0.1, 0.9 | v3 (in a prior run) | lost outright (best 1.57 vs champion higher) |
| 0.1, 0.25, 0.5, 0.75, 0.9 | v4 (this run) | none in top-4 of any of 6 generations |

Every value in the widened grid has now lost against v2, v3, and v4. This is
reasonably strong evidence the single-fixed-value mechanism (`correlation_penalty`
shrinking new entries vs. currently-held symbols only) doesn't help at any of
the five magnitudes tried, on this universe, under real search+holdout
conditions — not just the earlier v0.5-against-v2 result. Per the open item
in `AGENTS.md`: the honest move now is either to drop this line, or build
the fuller cross-universe pairwise factor-model version (bigger, separate
structural step, still not attempted).

Total runtime: ~13 minutes (data cached from earlier ticks; 8 generations,
`n_blind=14` each, 1d bars).
