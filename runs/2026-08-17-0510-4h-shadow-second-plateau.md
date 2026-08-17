# 4h shadow evolution, 10 generations past the first plateau — 2026-08-17 ~03:48-05:07 UTC

Follow-up to the open item in AGENTS.md's item 2 ("4h bars"): four prior
x6-scaled-seed shadow runs (2026-08-16 00:00, 06:00, 14:04, and the
correlation-check run) each found a quick generation-1 fix for the broken
scaled seed, then plateaued within 1-6 further generations — nobody had yet
run long enough past a first plateau to see whether a *second* one is
reachable. This run does: 10 generations at `n_blind=6` (bypassing the
bundled CLI's hardcoded `n_blind=14`, same standalone-script approach as the
2026-08-16-1404 run), from a fresh x6-scaled seed. Same isolation discipline
as every prior 4h shadow run: whole scratch dir isolated, no `live_state.json`
anywhere in it, so `Genome.champion()` falls back to the hand-scaled seed
built for this run only — verified `bar_interval=4h` in the setup log before
trusting anything. Nothing here touched this repo's `live_state.json`,
`researcher_memory`, or the real champion.

Total wall time: 4937s (~82 min) — 428s to fetch 27 symbols x 4 years of 4h
bars (no cache, `refresh=True`), then 10 generations.

## Result: two promotions, not one — the second plateau exists

**Generation 1** (as expected from every prior run): scaled seed v1
(fitness **-2.369**) → **v2** via `agents.risk_judge.genes.correlation_penalty`
0.0 → **0.1**, fitness -2.369 → 0.618. Sealed holdout passed (challenger
-2.242 vs champion -2.392, 2 cumulative draws), holdout edge: excess return
+10.0%, `beat_benchmark: true`. Note the magnitude: the 2026-08-16-1404 run's
generation-1 fix was also `correlation_penalty`, but at **0.75**, not 0.1.
Two different magnitudes of the same gene both "fixed" two different
x6-scaled seeds on their first try — read this the same way that run's note
did: `correlation_penalty` isn't specially validated at either value, almost
any change that shrinks concentration looks great against a catastrophically
overtrading baseline (0/3 folds beating benchmark before the fix). Does not
reopen the 1d `correlation_penalty` finding (resolved-negative at five grid
values against three competent champions) — this is still testing against a
broken one.

**Generations 2-8: seven generations of stagnation**, boldness climbing
0→7 as the researcher widened its net each round without clearing the bar
(best candidate each generation: fitness 0.794, 0.392, 0.307, -2.321, 0.343,
0.339, -2.280, vs. champion's 0.618 + rising multiple-testing margin — 52
candidates cumulatively tried against v2 by generation 8). Same shape as
every prior run's stagnation phase, just longer because this run kept going
instead of stopping at generation 2-6 like the others did on a time budget.

**Generation 9: second promotion.** **v2 → v3**, fitness 0.618 → **1.010**,
via a genuinely combined 5-gene blind-search patch (not a one-line tune):
`consult_conservative.z_buy_below` -0.8→0.2, `consult_conservative.min_trend`
-0.01→0.0197, `consult_moderate.min_trend` 0.005→0.0435,
`risk_judge.max_positions` 6→3, `risk_judge.cash_floor_pct` 0.05→0.40.
Sealed holdout passed convincingly: challenger **0.008** vs champion
**-2.242** (3 cumulative holdout draws, margin 0.119) — holdout edge: excess
return **+35.3%** (+50.8% annualized), excess Sharpe **+1.29**,
`beat_benchmark: true`. This is real evidence a second, structurally
different fix exists past the first plateau, not noise: it took 7
generations of failed attempts and boldness 7 (much wider mutation batches)
to find, and it passed the same honest holdout gate as everything else here.

**Generation 10: held, and the holdout gate visibly did its job.** Best
candidate (`consult_moderate.conviction_scale` +
`superior_judge.max_new_positions_per_bar`) scored fold-aggregate fitness
**1.364** — comfortably clearing v3's 1.010 plus the multiple-testing margin,
i.e. it would have been accepted on fold stats alone — but **failed the
sealed holdout**: challenger -0.021 vs champion 0.008 + margin 0.144 (5th
cumulative holdout draw). Rejected correctly. Worth citing on its own the
next time someone asks "does the holdout gate actually catch anything, or is
it just there" — this is a clean, real instance of it overruling a
fold-winning candidate right after a fresh promotion.

## Answering the open question directly

AGENTS.md item 2 asked whether "10+ generations past the first plateau at
the now-workable `n_blind=6`" reaches a second plateau. **Yes** — one real
promotion found at generation 9, after 7 generations of stagnation, via a
combined multi-gene patch the researcher only reaches at higher boldness.
This is one data point, not a law: still not attempted is whether a *third*
plateau exists past generation 10, or whether the same shape holds from a
genuinely fresh (non-x6-scaled) seed. Both remain open.

Nothing here touched `live_state.json`, promoted anything live, or changed
`researcher_memory`. Purely a shadow/offline data point per the standing
2026-08-15 decision to keep live cadence daily. Scratch dir and
`result.json` are ephemeral (`/tmp`), gone with this container.
