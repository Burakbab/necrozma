# 4h shadow evolution, n_blind=6 — 2026-08-16 ~14:04 UTC

Follow-up to `runs/2026-08-16-1300-real-test-suite.md`, same 3-hourly cycle:
that note flagged this run as still on generation 1 when it was written.
It has since finished. Same isolation discipline as every prior 4h shadow
run: whole scratch dir isolated (no `live_state.json` anywhere in it, so
`Genome.champion()` falls back to the hand-scaled seed built for this run,
not the real 1d champion), verified `v1 (4h bars)` in the log header before
trusting it, nothing here touches this repo.

## What this run answers

The open item from AGENTS.md item 2: prior 4h shadow runs used the CLI's
hardcoded `n_blind=14` (calibrated for 1d backtest cost) and took
25-27 minutes per generation, too slow for a 3-hourly slot to run more than
~2 generations. This run bypassed the bundled CLI (`evolve` hardcodes
`n_blind=14`) with a small standalone script calling `EvolutionRun.run()`
directly at `n_blind=6`, 6 generations, from a fresh x6-scaled seed (same
scaling as the 2026-08-16-0000 and -0600 runs: `trend_fast/slow`, `rsi_len`,
`vol_short/long`, `breakout_len`, `z_len`, `regime_ma`, `volume_len`,
`max_bars_held`, `min_bars_held` all x6).

Total wall time: ~72 minutes (157s data pull + ~70 min for 6 generations,
~10-12 min/generation vs. the prior run's 25-27 min/generation at
`n_blind=14`). Confirms the fix: `n_blind=6` is workable for a 3-hourly slot
if the whole 6-generation run is kicked off early and checked on rather
than run in the foreground.

## Result: one promotion, then stagnation — same shape as every prior 4h run

Generation 1: scaled seed v1 (fitness **-4.231**, 0/3 folds beating
benchmark, excess return **-50.9%** vs benchmark) → **v2**, patch
`agents.risk_judge.genes.correlation_penalty: 0.0 -> 0.75`, fitness
**-4.231 -> 0.839**. Sealed holdout passed (challenger -2.302 vs champion
-2.429, margin 0.094, 1 cumulative draw) with real edge: holdout excess
return +9.2% (+11.8% annualized), drawdown 12.2 points better than
benchmark, `beat_benchmark: true`. Generations 2-6 all held — best
candidate each generation (0.839 tied, 0.747, 0.716, 0.514, 0.690) never
cleared champion v2's bar, boldness climbing 0→3 as usual under stagnation.
Full detail in `result.json` inside the scratch dir (not committed —
ephemeral `/tmp`, gone with this container).

## Why this doesn't reopen the "correlation_penalty is resolved-negative" item

AGENTS.md's item 3 says all five widened-grid `correlation_penalty` values
(0.1/0.25/0.5/0.75/0.9) — **0.75 included** — lost outright against three
separate real 1d champions (v2, v3, v4-shadow). This run's `0.75` won
instantly here. Surface reading: contradiction. Actual reading, once you
look at *what* it beat: every prior 4h shadow run (2026-08-16-0000's two
runs, 2026-08-16-0600's corrected run, both cited in AGENTS.md item 2) found
its own generation-1 promotion off the x6-scaled seed, each via a
*different, unrelated* gene — `consult_moderate.min_rank_mom` +
`risk_judge.max_positions` in one, `breakout_len` + `max_position_pct` in
another. The scaled seed is genuinely broken (0/3 folds beating benchmark,
-50.9% excess return) and evolution's very first generation reliably finds
*something* that fixes it, because almost any change that reduces
concentration/turnover looks great against a catastrophic baseline.
`correlation_penalty` shrinks concurrent correlated positions, which is a
plausible mechanism for taming an overtrading scaled seed specifically —
but so were the unrelated genes the other three runs found. This is the
same "quick fix, then stagnation" pattern for a fourth time, not evidence
that correlation-awareness specifically generalizes. It does NOT invalidate
the 1d finding (which tested `correlation_penalty` against *competent*
champions, where an edge has to show up net of an already-reasonable
policy, not net of a broken one) and it should not be read as "try
`correlation_penalty` again at 1d" — the 1d line is still fairly called
resolved-negative at the five grid values tried.

## Updated picture for item 2 (4h bars)

Four independent x6-scaled-seed generation-1 draws now (this run + the three
in AGENTS.md item 2), each finding a different gate-passing, holdout-passing
fix, each stagnating within 1-5 further generations. The pattern is
consistent enough to stop treating any single one of these fitness numbers
(0.47, 0.81, 0.84 here) as meaningfully different — they're draws from the
same "fix the broken scaled seed, then plateau" distribution, not a
convergent search finding one true 4h policy. What's still not tried:
seeding a 4h search from something other than an x6-scaled 1d seed (e.g. a
genuinely fresh blind search with no scaling prior), or running long enough
past the first plateau (10+ generations at this now-workable `n_blind=6`)
to see if a *second* plateau is reachable. Neither attempted this cycle —
time budget.

Nothing here touched `live_state.json`, promoted anything live, or changed
`researcher_memory`. Purely a shadow/offline data point per the standing
2026-08-15 decision to keep live cadence daily.
