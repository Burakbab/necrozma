# Fold-scheme sensitivity diagnostic (2026-08-18, 3-hourly check)

New read-only CLI command `evotrader_bundle.py fold-scheme`. Same guarantees
as `anatomy`/`consults`/`costs`/`regime`/`hard-calls`: full-history replay,
never touches `live_state.json` or the constitution's `N_FOLDS` constant.

## Why

AGENTS.md's item 2 (regime diagnostic, 2026-08-17) found fold 2 of the fixed
3-fold walk-forward split is a permanent +200%+ melt-up window, and left an
open question for whoever next touches the fold scheme: is
`FOLD_CONSISTENCY_WEIGHT`'s cross-fold variance penalty enough when one of
three fixed folds is a structural outlier, or does that call for a
rolling/regime-stratified fold scheme? This is a first, cheap answer to that
question — not a redesign, a measurement.

## What it does

Re-evaluates the live champion's own genome under alternative fold counts
using the exact same `loop.evolve.Evaluator` class the real `evolve` loop
uses — `Evaluator` already took `n_folds` as a constructor parameter, so no
engine or constitution code changed, only a new CLI branch. The sealed
holdout is untouched regardless of `n_folds` (`evaluate()` never looks past
`search_end`). Reports per-fold fitness, buy-and-hold return, excess return,
and `beat_benchmark`, plus the "outlier gap" (largest single fold's b&h
return minus the mean of the rest) at each fold count.

## Result, against real champion v3

```
n_folds=3 (current constitution default)
  fold 1  fitness   1.025  b&h return    +8.7%  excess   +19.1%  beat benchmark
  fold 2  fitness   4.377  b&h return  +220.1%  excess   +89.9%  beat benchmark
  fold 3  fitness    -inf  b&h return    -7.3%  excess   +15.8%  beat benchmark
  aggregate_fitness =  -1.224   3/3 folds beat benchmark
  outlier gap +219.4%

n_folds=5
  aggregate_fitness =   1.633   5/5 folds beat benchmark
  outlier gap +53.8%

n_folds=8
  fold 1  slice too short (95 bars)
  aggregate_fitness =  -0.500   2/8 folds beat benchmark
  outlier gap +52.0%
```

Two findings:

1. **The outlier gap shrinks sharply and monotonically as fold count rises**
   (+219.4% → +53.8% → +52.0%) — direct, quantified confirmation that fold 2's
   dominance is an artefact of there being only 3 folds, not something
   `FOLD_CONSISTENCY_WEIGHT` can see past at the current split. A rolling or
   more-numerous fold scheme would materially reduce how much one calendar
   window can dictate the fold-aggregate score by itself.

2. **`aggregate_fitness` itself does *not* move monotonically or safely with
   fold count** — it swings from -1.224 (n=3) to +1.633 (n=5) back down to
   -0.500 (n=8), and at n=8 the smallest fold (95 bars) is close enough to the
   `run_backtest` 120-bar minimum that fold 1 fails outright ("slice too
   short"). This is not evidence that 5 or 8 folds is "more correct" — it's
   evidence that naively raising `N_FOLDS` on the current fixed 85/15 split
   trades one instability (one outlier fold dominating) for another (smaller
   folds hitting the hard-gate floor, `MIN_TRADES`/`MIN_BARS`/maxDD, more
   often, which is exactly what happened to fold 3 at n=3 — its `fitness` is
   `-inf` here despite a positive 15.8% excess return, because whatever hard
   gate tripped isn't visible from the b&h/excess numbers alone). A
   regime-stratified scheme (folds defined by market regime, not equal
   calendar slices) would sidestep the small-fold problem while still
   diluting the outlier — worth more than raising `N_FOLDS` alone, but bigger
   scope, not attempted this run.

## Caveat

The -1.224 aggregate_fitness reported here at n_folds=3 does **not** match
champion v3's recorded promotion-time fold-aggregate fitness of 1.389 from
`AGENTS.md`. This is expected, not a bug: `market.load_universe(..., 4.0)`
loads the newest 4 years ending *today* (2026-08-18), a different sliding
window than whatever the search saw at promotion time on 2026-08-16 — the
same caveat every full-history diagnostic here carries (`costs`, `anatomy`,
`consults`). This diagnostic is only valid for *relative* comparison across
fold counts on the same data snapshot, which is what it's for.

## Verified safe

- Purely additive: only a new CLI `elif` branch in `evotrader_bundle.py`'s
  `main()` (not inside the embedded `_SRC` bundle strings — `main()` lives
  outside them), calling an existing, already-tested class
  (`loop.evolve.Evaluator`) with a different constructor argument it already
  accepted. No constitution file touched, `N_FOLDS` constant unchanged.
- `live_state.json` md5 identical before/after
  (`c4289723973ee8ace977f7abaf0003a8`).
- `evotrader.manifest` / `constitution verified dfae6a697f51fb49` unchanged.
- Full test suite: 72 passed (unchanged from before this run — no new tests
  added, since this is print-only CLI glue over an already-tested class, the
  same bar the existing `regime`/`costs`/`anatomy`/`consults` diagnostics are
  held to; they have no dedicated test files either).

## Next

If a fold-scheme redesign is ever undertaken, this suggests the target isn't
"more equal-sized folds" (that just relocates the instability) but a
regime-stratified or rolling scheme that keeps folds above the hard-gate
minimum bar count while still preventing one calendar window from being
weighted like a third of the whole search. Not attempted — this run only
measured the existing shape, per the same discipline as `regime` before it.
