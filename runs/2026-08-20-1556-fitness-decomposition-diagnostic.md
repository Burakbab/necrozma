# 2026-08-20 15:56 UTC — fitness-decomp diagnostic: which term drives the aggregate_fitness swing

3-hourly self-improvement check. No new daily bar to trade (live_state.json
`updated` 2026-08-20T00:21:36Z, genome v3, handled by the 00:20 UTC daily run —
`runs/2026-08-20-0020-daily-trading.md`; `tick` not run this session). Spent the
slot on item 2's fold-scheme redesign question.

## What shipped

New read-only diagnostic `evotrader_bundle.py fitness-decomp [--also-version N]`,
backed by a new pure function `loop.evolve.fitness_decomposition(fold_fits)`.

`Evaluator.evaluate` scores a genome as
`mean(fold_fits) - FOLD_CONSISTENCY_WEIGHT * std(fold_fits)`. `fold-scheme` and
`rolling-folds` both showed that changing the fold windowing swings that single
aggregate number, but the aggregate is one value — it can't say whether the
swing rides the **mean term** (the +200% fold-2 melt-up pulling the average) or
the **consistency-penalty term** (`FOLD_CONSISTENCY_WEIGHT * cross-fold std`).
The 2026-08-20 rolling-folds run *inferred* the penalty term was the culprit:
"adding more overlapping reads adds variance to that penalty term at least as
fast as it dilutes the outlier's share of the mean." `fitness_decomposition`
splits aggregate_fitness into `mean_term` and `penalty_term` so that inference
becomes measurable. `mean_term - penalty_term` reconstructs aggregate_fitness
exactly (same `np.mean`/`np.std` — an identity, not an approximation), unit-
tested against `Evaluator`'s own formula.

The CLI evaluates the live champion (and any `--also-version N`) under five
schemes — disjoint at `n_folds` 3/5 and rolling at overlap 0.5/0.7/0.85 — and
prints the mean/penalty split per scheme plus the across-scheme range of each
term.

## Finding: the mean term drives the swing, not the penalty term

Against champion **v3 (live)**:

| scheme | #w | mean | std | penalty | aggregate |
|---|---|---|---|---|---|
| disjoint n_folds=3 | 3 | 2.063 | 1.666 | −0.583 | 1.480 |
| disjoint n_folds=5 | 5 | 2.734 | 0.938 | −0.328 | 2.406 |
| rolling overlap=0.5 | 5 | 1.865 | 1.332 | −0.466 | 1.399 |
| rolling overlap=0.7 | 7 | 2.322 | 0.910 | −0.319 | 2.003 |
| rolling overlap=0.85 | 14 | 1.234 | 2.652 | −0.928 | 0.306 |

Range across schemes: aggregate **2.100**, of which the **mean term ranges
1.500** and the penalty term only **0.610**.

Cross-checked against **v1 (reconstructed)**: same qualitative pattern —
aggregate range 0.426, mean term range **0.609**, penalty term range **0.183**.
Both champions: the mean term varies more than twice as much as the penalty
term across these schemes.

## Reading — refines (partly corrects) the rolling-folds inference

The rolling-folds run guessed the FOLD_CONSISTENCY_WEIGHT penalty term was the
main source of aggregate instability. Direct measurement says otherwise: both
terms swing, but the **mean of the fold fitnesses** has the larger range in both
champions. The aggregate is unstable mostly because *which windows capture the
permanent fold-2 melt-up* moves the average, not because the cross-fold std
penalty is over-reacting to how many correlated windows feed it.

The extreme `overlap=0.85` case is where both terms move the aggregate-lowering
way at once (mean drops to 1.234 **and** penalty rises to −0.928, cratering the
aggregate to 0.306) — so overlap does amplify the penalty term, consistent with
the prior run's observation that naive overlap made things *worse*. But the raw
driver across the whole scheme set is the mean term.

This sharpens item 2's redesign direction: retuning `FOLD_CONSISTENCY_WEIGHT`
alone would not stabilize the aggregate, because the dominant instability isn't
in the penalty term it controls — it's in the mean being dominated by one
outlier window. That points more firmly at **genuine regime-stratification** (so
no single window is a permanent +200% outlier in the first place) over a penalty-
weight tweak or a denser calendar slide. Regime-stratification remains the real,
unstarted design work (needs a regime definition independent of the window under
test — candidate: `regime`'s own per-window buy-and-hold characterization).

## Verified safe

- `loop.evolve` is not checksummed (`constitution` + `core.portfolio` only).
  `tools/edit_bundle_module.py verify` round-trip clean before the edit;
  reinserted via the same tool, `py_compile` clean.
- Full suite **143 passed** (up from 136) — 7 new tests in
  `tests/test_fitness_decomposition.py` (formula identity, sign/value checks,
  zero-spread and single-fold no-penalty cases, empty→−inf branch, penalty
  grows with spread at fixed mean, and an end-to-end match against a real
  `Evaluator.evaluate` on synthetic backtest data).
- `live_state.json` md5 identical throughout (`cca58deb976cef403c5010f2e2b9528b`),
  `evotrader.manifest` md5 identical (`6a4434574ff424f74ff300ebdb50d194`),
  `constitution verified dfae6a697f51fb49` unchanged. No promotion (no genome
  version change → no README `## Status` update needed), no constitution change
  (no `AMENDMENTS.md` row needed).
- Diagnostic is read-only: one backtest per window per scheme (same cost class
  as `fold-scheme`/`rolling-folds`), never touches state or the champion.
- Session started on a detached HEAD two stale seed-import commits behind a
  force-updated `origin/main`; reset to `origin/main` per the run protocol's
  "origin/main is authoritative" rule (no work lost — the divergent local
  commits were the already-superseded Aug 15 initial-import commits).

## Next

- `fitness-decomp --also-version 2` is a one-line follow-up not yet run (third
  real champion, same cross-genome discipline as every other sweep in this
  file).
- The regime-stratified fold scheme itself is still unstarted design work, now
  with sharper motivation: the instability to design around is the mean term's
  sensitivity to the outlier window, not the consistency-penalty term.
