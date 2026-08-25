# Characterizing window 5: trend/chop, volatility, and correlation don't explain the hard-fail

**3-hourly self-improvement check, ~21:55 UTC.**

Today's daily bar was already handled by the 00:20 UTC run (`live_state.json`
`updated` 2026-08-25T00:22:01+00:00, genome version still 3, md5
`f7590581b893d3866e00e28c87fe1c02` unchanged throughout this session) —
nothing new to trade this cycle. `review-hard-calls` still 0 pending.

## Why

The 09:56 UTC `history-perturb --independent` run found champion v3 beats
benchmark in 4 of 5 genuinely independent, non-overlapping 2-year windows
(2017-2024) but hard-fails the newest one (2024-08-25 to 2026-08-25, window
5 — the live champion's actual current regime). Its own "Next" section named
the open question precisely: "what's different about the 2024-08-24 to
2026-08-25 window", and flagged `regime`-style characterization
(trend/chop/volatility shape vs the four windows that worked) as the
untried next step. The 18:52 UTC session answered a different open question
from the same thread (the continuous-exceeds-sub-slice drawdown gap, found
in 2/4 testable windows) but left this one untouched. This session takes it.

## What was done

No code shipped — three throwaway `/tmp` scripts (not committed), same
precedent as the 18:52 UTC session's window 1-4 check and the 4h
shadow-evolution sessions. Each replicates `history-perturb --independent`'s
exact window-tiling logic (`window_years=2.0`, tiling backward from "now"
over a 12y `load_universe` load) and then, per window, computes one
genome-independent regime metric using already-tested pure functions:

1. **Trend/chop**: per-symbol efficiency ratio (`|log(close[-1]/close[0])| /
   sum(|daily log returns|)` — 1.0 is a straight-line trend, near 0 is a
   round trip / chop) and annualized realized volatility, averaged across
   the universe.
2. **Benchmark shape**: `loop.engine.benchmark_buy_hold` over each window
   (same function `regime`/`regime-scan` already use), to see whether
   window 5 is a crash, a chop, or another melt-up in raw market terms.
3. **Cross-asset correlation**: `loop.engine.pairwise_correlation_stats`
   (same function `correlation-universe` already uses) over each window's
   full daily-return set.

All three reuse existing, already-tested functions with no modification —
nothing new to unit test, consistent with the precedent set by every other
one-off shape-characterization check in this thread.

## Result (champion v3's universe, all 5 independent windows)

| window | span | mean efficiency ratio | mean ann. vol | b&h return | b&h sharpe | b&h maxDD | mean pairwise corr |
|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | 2017-08-17 to 2018-08-25 | 0.120 | 117.2% | +28.9% | 0.75 | -70.2% | 0.755 |
| 2 | 2018-08-25 to 2020-08-25 | 0.027 | 109.4% | +21.5% | 0.55 | -72.9% | 0.663 |
| 3 | 2020-08-25 to 2022-08-25 | 0.035 | 131.8% | +289.2% | 1.18 | -84.2% | 0.522 |
| 4 | 2022-08-25 to 2024-08-25 | 0.036 | 78.7% | +154.1% | 1.03 | -57.0% | 0.548 |
| 5 | 2024-08-25 to 2026-08-25 | 0.036 | 84.6% | +79.5% | 0.77 | -61.0% | 0.584 |

(Windows 3-5 all use the full 27-symbol universe; windows 1-2 have fewer
symbols listed that early, same data-availability floor the 18:52 UTC note
already documented.)

## Reading: none of these three genome-independent regime metrics distinguish window 5

Champion v3 beats benchmark in windows 3 and 4 but hard-fails in window 5.
By every metric measured here, **window 5 sits inside the range of windows
3-4, not outside it**:

- **Efficiency ratio**: 0.036 — essentially identical to window 3 (0.035)
  and window 4 (0.036). Not choppier or trendier than the windows the
  champion clears.
- **Volatility**: 84.6% annualized — between window 4's 78.7% and window
  3's 131.8%, not an outlier in either direction.
- **Benchmark shape**: window 5's buy-and-hold return is +79.5%, sharpe
  0.77 — a genuine bull/melt-up-shaped window (like 3 and 4, just a smaller
  one), not a crash or a directionless chop. This directly rules out "window
  5 is a bear market" as the explanation.
- **Correlation**: 0.584 mean pairwise — actually the *highest* of windows
  3-5, but only modestly (0.522/0.548/0.584), not a step change into a
  qualitatively different "crisis contagion" regime the way window 1's 0.755
  is.

**This is a real negative result, not a null one.** It rules out the
straightforward "window 5 is a different kind of market" hypothesis the
09:56 UTC note's own framing invited — by trend, volatility, raw benchmark
shape, and cross-asset correlation, window 5 looks like a smaller sibling of
windows 3-4, which the champion beats comfortably (+57.5%/+0.8% excess
return there vs -41.2% in window 5). Whatever makes the champion fail
specifically in window 5 is not visible in any of these genome-independent,
market-only characterizations — it has to be something about how the
champion's own genome/mechanism responds to this specific window's bar
sequence, not a coarse regime label. This sharpens, not closes, the open
question from 09:56 UTC.

## Verified safe

- No files in the repo were modified by the check itself — `git status
  --short` was clean before this commit except this note + `AGENTS.md`.
- `live_state.json` md5 unchanged: `f7590581b893d3866e00e28c87fe1c02`.
- `evotrader.manifest` md5 unchanged: `0bf3a7d9411ee692d0a9f152a7533803`.
- Today's bar already processed by the 00:20 UTC daily run before this
  session started; `tick` not run this session, no double-trade.
- No genome promotion — no README `## Status` update needed.
- No new pure function or CLI surface added, so no new test file; full
  suite not re-run (nothing in the repo changed this session).

## Next, if this thread stays worth pursuing

The coarse regime-shape hypotheses (trend/chop, volatility, benchmark
direction, correlation) are now ruled out. Sharper candidates not attempted
here: (a) `anatomy`-style per-trade post-mortem restricted to window 5 only,
to see which specific consult/gate is misfiring in this window the way the
2026-08-16 "Measured" section did for the full history; (b) compare window
5's own trade count/turnover against windows 3-4 — the champion's genome
was tuned on the older folds, so a mechanical mismatch (e.g. lookback genes
sized for a different volatility clustering pattern) is still plausible even
though raw volatility levels match; (c) accept this as one more data point
that the champion's edge is not fully regime-general and fold it into the
already-open v3 demotion/rollback question (raised to the owner 2026-08-22,
reaffirmed since) rather than continuing to search for a
market-shape explanation that three separate metrics have now failed to
provide.

No push notification — a read-only research finding (a negative one, ruling
out three hypotheses) with zero effect on live trading behavior, same
threshold every prior diagnostic-only 3-hourly session in this history has
used. The standing v3 demotion/rollback question itself is unchanged by
this — already raised to the owner 2026-08-22, reaffirmed since, no new
facts here that change that status.
