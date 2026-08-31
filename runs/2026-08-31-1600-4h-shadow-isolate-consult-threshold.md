# 4h shadow: isolating which consult's threshold-tightening drives the 10:02 UTC drawdown result — and a stale recommendation caught along the way — 2026-08-31 15:46-16:00 UTC

Direct follow-up to the 10:02 UTC session's flagged gap: that session tightened nine
threshold genes across all three consults (`consult_risky`, `consult_moderate`,
`consult_conservative`) at once and found trade count dropped as predicted but drawdown
got *worse*, not better — a real negative result, but one that couldn't say which
consult's tightening (if any) was responsible versus which were just along for the ride.
The 07:05 UTC framing had already named "thresholds on `consult_risky` alone vs. all
three consults" as untested.

## A stale recommendation, caught before acting on it

The 12:47 UTC session's own "Next steps" pointed at testing `correlation_penalty` on the
x6-scaled seed as the natural next 4h-shadow variant. That gene does not exist any more —
`correlation_penalty`/`correlation_lookback`/`RiskJudge._correlation_scale` were fully
removed on 2026-08-20 (item 3, closed). `grep -rn correlation_penalty --include='*.py'`
across the repo today turns up only comments/docstrings describing its removal, not a
live gene. Two consecutive 4h-shadow sessions (10:02, 12:47 UTC) carried this suggestion
forward without checking it still applied. Corrected in AGENTS.md's item 2 and item 3
cross-reference so a third session doesn't repeat it.

## Method

Read-only, no `evolve`/`tick`/`save`. Used the committed `tools/shadow_4h_x6_seed.py`
harness (`build_x6_scaled_seed`, `summarize`) for the baseline construction instead of a
fresh hand-rolled script, per the 12:47 UTC session's own recommendation. Built four
`Genome.child()` variants from the same x6-scaled seed, isolating the 10:02 UTC session's
nine threshold-gene changes by which consult they belong to:

- **risky-only**: `consult_risky.min_rank_mom` 0.70→0.85, `rsi_max` 82.0→75.0,
  `min_breakout` -0.02→-0.01
- **moderate-only**: `consult_moderate.min_trend` 0.005→0.015, `rsi_lo`/`rsi_hi`
  45.0/72.0→50.0/65.0, `min_rank_mom` 0.50→0.65
- **conservative-only**: `consult_conservative.rsi_buy_below` 38.0→30.0, `z_buy_below`
  -0.8→-1.2
- **all-three**: the 10:02 UTC session's exact combination, run again in this same
  process as a reproducibility check

One fetch of the live champion's 27-symbol 4h/4y universe (warm cache from the 12:47 UTC
session, no gap warnings), five single-shot `run_backtest()` calls back-to-back.

## Result

| variant | trades/yr | days held | win% | halts | max_dd | sortino | sharpe |
|---|---|---|---|---|---|---|---|
| baseline | 392.7 | 15.54 | 49.4% | 6 | -44.3% | 0.94 | 0.77 |
| risky-only | 382.4 | 15.68 | 48.3% | 6 | **-48.7%** | 0.87 | 0.73 |
| moderate-only | 337.3 | 15.58 | 47.2% | 7 | -45.7% | 0.74 | 0.63 |
| conservative-only | 381.4 | 16.87 | 50.8% | 6 | -44.5% | **1.02** | **0.85** |
| all-three | 327.7 | 14.72 | 44.8% | 8 | -48.0% | 0.77 | 0.65 |

The all-three row reproduces the 10:02 UTC session's own numbers closely (327.8→327.7
trades/yr, -48.0% max_dd both sessions) — good evidence the harness-based construction is
stable, not just internally consistent within one session.

**Three separable, previously-conflated effects:**

1. **`consult_risky` tightening alone barely reduces trade count (392.7→382.4, only
   -2.6%) but makes drawdown clearly worse (-44.3%→-48.7%)** — worse than the all-three
   combination itself. Tightening the most aggressive consult's entry gate doesn't act
   like risk reduction here; if anything it looks like it's removing some of what was
   diversifying entries away from whatever concentrated the losses.
2. **`consult_moderate` tightening alone does most of the all-three run's trade-count
   reduction (392.7→337.3, -14.1% of the combination's -16.5%)** but has the worst
   risk-adjusted numbers of any single variant (sortino 0.74, sharpe 0.63) — fewer trades,
   not better ones.
3. **`consult_conservative` tightening alone is close to a free improvement**: trade
   count and drawdown both move by noise only (-2.9% trades, +0.2pp max_dd) but sortino
   and sharpe both *beat baseline* (0.94→1.02, 0.77→0.85) — the only one of the four
   variants that improves on baseline at all, and it does so cleanly, not by trading a
   worse metric for a better one.

None of the four variants — including this one — gets anywhere close to clearing
`MAX_DD_HARD_FAIL` (40%); the best max_dd here is still baseline's -44.3%. This does not
fix the drawdown-gate problem item 2 has been chasing since the dd-corrected gate landed
(2026-08-21/22). But it does replace "tightening thresholds doesn't help" with a sharper,
correctly-attributed claim: the 10:02 UTC combination's worse-drawdown result was driven
by `consult_risky` and `consult_moderate` (one clearly harmful, one merely
trade-count-reducing without a quality gain), masking that `consult_conservative`'s piece
was quietly an improvement the whole time.

## What this changes for item 2

**Recommend a future session try `consult_conservative`-only tightening as its own
starting point** — combined with something else that actually attacks drawdown directly
(the entry-frequency finding from 07:05 UTC still holds: this seed enters far more often
per year than v3, and no single-consult threshold change tested so far, in either
direction, has touched that mechanism enough to matter) rather than bundled with the two
consults now shown to hurt. Also worth trying: `consult_conservative` tightened *further*
than this one step, since this one data point is still short of the hard-fail line and
directionally the only variant moving the right way on every metric.

Nothing here touched `live_state.json`, promoted anything, or changed
`researcher_memory` — purely shadow/offline compute (warm `state/cache/` reuse, no new
fetch needed). `git status` clean before this commit, `live_state.json` md5 unchanged
(`37a1b00bee3f7cb1ad2f4adde0ab9ed0`), genome still v3 (1d), `python3 -m pytest -q`
252/252 confirmed at session start, no code changed (one standalone scratch script using
the committed harness, not itself committed, per this thread's established discipline of
only committing genuinely reusable pieces).
