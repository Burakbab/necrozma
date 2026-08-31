# 4h shadow: two harness-scaling confounds tested and ruled out — 2026-08-31 03:52-04:06 UTC

Direct follow-up to the 2026-08-31 02:43 UTC run note's sharpened open question for
item 2: is the x6-scaled 4h seed genome itself structurally too aggressive for the
dd-corrected gate to ever clear, or would a genuinely retuned (not just scaled)
starting point behave differently? Before spending a bigger session on hand-retuning
or a long blind search, this session checked a cheaper alternative explanation first:
every 4h-shadow run since 2026-08-16 has hand-scaled the seed genome's *period genes*
(`trend_fast/slow`, `vol_short/long`, `breakout_len`, `z_len`, `regime_ma`,
`volume_len`, `max_bars_held`, `min_bars_held`) by x6, but two bar-count constants
that live *outside* the genome were never touched by that recipe:

- `run_backtest()`'s `warmup` parameter (default 60 bars). At 1d this safely exceeds
  every seed-genome period gene (max 50), so every fold starts fully primed. At 4h,
  several x6-scaled genes (`trend_slow`/`regime_ma`=300, `z_len`=180,
  `breakout_len`/`volume_len`=120) exceed the still-60 warmup — meaning the first
  ~240 bars (~40 days) of every fold/holdout/continuous-replay slice could be
  running on incompletely-primed indicators.
- `constitution.CIRCUIT_BREAKER_COOLDOWN` (20 bars). At 1d that's a 20-day freeze
  after a drawdown trip; at 4h it's only ~3.3 days — a much shorter freeze than the
  genome's own tuning implicitly assumes, plausibly letting the book re-enter risk
  before a crash has resolved and re-trip repeatedly.

Both are plausible mechanical explanations for the seed's elevated trade count,
halt count, and catastrophic drawdown that would have nothing to do with the
genome's actual risk-taking — i.e. a methodology artifact in every prior 4h-shadow
run, not evidence about the seed itself.

## Method

Same isolation discipline as every prior 4h-shadow session: fresh scratch dir
containing only a copy of `evotrader_bundle.py` + `evotrader.manifest`, no
`live_state.json` nearby. Fetched a fresh 27-symbol x 4-year 4h dataset (Binance,
~7min). Built the same x6-scaled seed genome construction used since 2026-08-16.
Two standalone scripts (`warmup_experiment.py`, `cooldown_experiment.py`, not
committed — ephemeral), each calling `run_backtest`/`Evaluator` directly (bypassing
`EvolutionRun`, since no evolution was needed to test these two variables) with
only one parameter changed at a time:

1. **Warmup**: 60 (the implicit value every prior shadow script used) vs. 360
   (60×6, matching the same x6 logic already applied to the genome's own periods).
2. **Circuit-breaker cooldown**: 20 (real constitution value) vs. 120 (20×6),
   patched only in this throwaway process's `loop.engine` module — the real,
   checksummed `constitution/__init__.py` was never touched.

Baseline reproduced the 2026-08-30/31 sessions' recorded numbers closely enough to
trust the setup: fitness -4.296, 4468 trades (vs. their 4413 — small diff plausibly
from the slightly later `years=4.0` fetch window), halts 6 (vs. 5), max_dd -0.542/-0.568
fold-merged/continuous.

## Result: neither confound matters — the seed is genuinely this bad on its own terms

| variant | trades | halts | fold max_dd | continuous max_dd | fold-agg fitness |
|---|---|---|---|---|---|
| warmup=60 (baseline) | 4468 | 6 | -0.542 | -0.568 | -4.296 |
| warmup=360 (x6) | 4449 | 7 | -0.542 | -0.534 | -4.306 |
| cooldown=20 (baseline) | 4468 | 6 | -0.542 | -0.568 | -4.296 |
| cooldown=120 (x6) | 4225 | 6 | -0.517 | -0.517 | -4.317 |

Every metric moves by noise-scale amounts (a few percent of trades, ±0.02-0.05 on
max_dd, ±0.02 on fitness) — nowhere close to closing a ~13-17 point drawdown gap to
`MAX_DD_HARD_FAIL` (0.40) from a continuous max_dd of -0.52 to -0.57. Both variants
still hard-fail the dd-corrected gate outright.

## What this changes for item 2

Rules out the "harness never finished adapting to 4h" explanation for this specific
seed's pathology — it is not an indicator warm-up or circuit-breaker-freeze artifact.
Sharpens the 2026-08-31 02:43 UTC note's open question by eliminating one branch:
this is evidence *for* "the x6-scaled seed itself is structurally too aggressive"
and *against* "it's a scaling-recipe artifact in the eval harness," at least along
these two specific dimensions. Does not rule out other un-scaled bar-count
constants this session didn't check (`constitution.MIN_BARS`=90, `run_backtest`'s
hard 120-bar minimum-slice-length checks) — those gate *validity*, not risk-taking,
so they're a weaker candidate explanation for a 50%+ drawdown and were not tested
here on a time-budget call. The remaining open question is unchanged in kind but now
better supported: a genuinely hand-retuned (not just scaled) 4h starting point is the
next real test of hypothesis 2, not another same-construction run or another
un-scaled-constant check.

Nothing here touched `live_state.json`, promoted anything live, or changed
`researcher_memory` — purely shadow/offline compute. Real repo `git status` clean,
`live_state.json` md5 unchanged throughout, genome still v3 (1d), `python3 -m
pytest -q` 243/243 confirmed at session start.
