# Shadow evolution at 4h bars — 2026-08-16 ~00:00 UTC

Scheduled 3-hourly check. Nothing to trade this cycle (next daily bar closed
right at the end of this run, handled separately by the 00:20 UTC daily job —
this note doesn't touch `live_state.json`). Used the cycle on Next-steps item
2: "run a fresh evolution from the seed genome at 4h granularity as a
shadow/offline exercise ... to get real comparative data before ever switching
the live cadence."

Both runs below were done entirely outside this repo (a scratch copy of the
bundle, its own `state/genomes` + `state/lineage.jsonl` + `state/cache`) and
never read or wrote this repo's `live_state.json`. No `evolve` CLI invocation
against the live account happened this cycle.

## Setup

27-symbol universe, 4 years of real 4h Binance klines (236,682 bars total,
~6.3x the ~37,700 a 4-year 1d pull gives). 2 generations, `n_blind=10` each,
same walk-forward/holdout/multiple-testing gates the live evolution loop uses.

## Run 1 — seed genome, bar-count genes untouched

The hand-written seed genome as-is, just with `bar_interval` set to `"4h"`.
Every period gene (`trend_fast`, `trend_slow`, `rsi_len`, `vol_short/long`,
`breakout_len`, `z_len`, `regime_ma`, `volume_len`, `risk.max_bars_held`,
`risk.min_bars_held`) is expressed in bars, so at 4h these mean 6x less
wall-clock time than they did at 1d (e.g. `trend_slow=50` bars ≈ 8.3 days
instead of 50 days).

Result: **catastrophic, not just suboptimal.**

| | value |
|---|---|
| fitness | **−4.46** |
| total_return | −22.3% |
| max_dd | −64.1% |
| turnover_annual | 160.0 (vs. ~38 for the same seed at 1d) |
| halt_count | 9–10 (circuit breaker constantly tripping) |
| win_rate | 49.7% |

2 generations, 34 cumulative candidates tried (mix of blind search and the
existing structural proposals, including `correlation_penalty: 0.0 → 0.5`).
**Every single one failed a hard gate** (drawdown > 40% or too few/short
trades) — none could even be scored on real fitness, so the acceptance rule
never got a finite candidate to compare against the champion. The champion
held at v1 for both generations because there was nothing to promote it to,
not because v1 was defensible.

Reading: this is exactly the failure mode flagged when the plan was sketched
— reusing bar-count gene values verbatim at a 6x-denser bar size makes the
system trade far too fast (way more entries/exits per unit wall-clock time),
which multiplies turnover and fees and trips the circuit breaker repeatedly.
Two generations of mutation search couldn't dig out of that hole because
almost every mutation still inherits the same fundamentally-too-fast periods.

## Run 2 — seed genome, bar-count genes hand-scaled ×6

Same seed, same universe, same cached 4h data. This time every bar-count gene
listed above was multiplied by 6 first (`trend_fast` 10→60, `trend_slow`
50→300, `rsi_len` 14→84, `breakout_len` 20→120, `regime_ma` 50→300,
`max_bars_held` 60→360, `min_bars_held` 1→6, etc.) so each period covers
roughly the same wall-clock window it did at 1d bars.

Result: **workable, and evolution found a real improvement in generation 1.**

| | v1 (scaled seed) | v2 (accepted) |
|---|---|---|
| fitness | −2.42 | **0.81** |
| trades | 1,191 | 364 |
| total_return | 51.0% | 18.3% |
| sortino | 1.05 | 0.99 |
| max_dd | −43.3% | **−18.6%** |
| turnover_annual | 54.2 | 16.1 |
| halt_count | 5 | **0** |

Gen 1's accepted mutation: `consult_moderate.min_rank_mom` 0.5→0.5352,
`risk_judge.max_positions` 6→2 (selection fitness 0.812 > champion −2.416 +
required margin 0.197; merged fitness did not regress; sealed holdout passed:
challenger −1.961 vs champion −2.358; drawdown 18.6% within the regression
tolerance). Gen 2 found nothing that cleared the bar against the new v2
champion — best candidate (fitness 1.179, dropping `consult_conservative`)
failed the sealed holdout (−1.971 vs champion's −1.961) and was correctly
rejected.

Note the scaled v1's own drawdown (−43.3%) is still over the constitution's
40% hard-fail line in isolation — it only survived because it wasn't itself a
*challenger* being gated, it's the champion the challengers are compared
against. The accepted v2 fixes this (−18.6%) as a side effect of shrinking
`max_positions`, not because anything explicitly targeted the seed's
drawdown.

## What this means for the roadmap decision

Comparable, not conclusive: v2's fold-aggregate fitness (0.81, scaled 4h,
2 generations) sits in the same neighbourhood as the live daily champion v2's
0.889 (13+ generations, much more search time), and this scaled-4h line was
never checked against the live champion directly — different bar size,
different universe window handling, not an apples-to-apples promotion
candidate.

The concrete finding is narrower and more useful than a fitness number: **you
cannot switch the live cadence to 4h and keep the current genome's gene
values.** The unscaled seed doesn't just underperform at 4h, it fails every
acceptance gate outright. Hand-scaling bar-count genes by 6x turns "broken"
into "evolvable" — that's real signal that the "reset to seed, let evolution
retune from scratch" path from the original plan sketch is the right one (not
hand-scaling as the final answer, but as a viable *starting point* for a
longer search), rather than ever expecting a 1d-tuned genome to transfer
as-is.

Not done, deliberately left for whenever this gets picked up for a real
decision: more generations (2 is barely past first contact), a direct
walk-forward comparison against live champion v2 on the same holdout, and
folding the correlation-awareness gene into the 4h search (it was proposed by
the Researcher in both runs here but never got to be evaluated on a finite
fitness because of the hard-gate failures in run 1, and lost to other
candidates in run 2).

Total compute: ~44 minutes (7 min data pull, once — cached for run 2 — plus
~31 min + ~37 min for the two evolution runs). Nothing written to
`live_state.json`; nothing promoted live.
