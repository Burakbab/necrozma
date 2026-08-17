# Regime diagnostic: chasing the fold/holdout fitness split — 2026-08-17 09:46-09:56 UTC

3-hourly self-improvement check. `live_state.json`'s `updated` was
`2026-08-17T00:26:31Z`, matching the `2026-08-17-0020-daily-trading.md` note
for today's already-handled daily bar — no new bar to trade this cycle.

Follow-up to the open item at the end of
`runs/2026-08-17-0820-4h-shadow-unscaled-seed.md`: every accepted promotion
in that run had **negative** fold-aggregate fitness (search folds, oldest
85% of the 4-year window) while its **sealed holdout** fitness (newest 15%)
was strongly positive and rising — the opposite of the usual overfitting
shape. That note flagged "chase the fold/holdout split anomaly directly —
slice the 4h data into the same three search folds plus holdout and look at
what regime each actually contains" as the next step, rather than continuing
to infer it from fitness numbers alone.

## What was built

New read-only CLI diagnostic, `evotrader_bundle.py regime [--interval
1h|4h|1d]` (committed separately, see the "Add regime diagnostic" commit).
It slices the champion's universe into the same walk-forward windows
`Evaluator.folds()`/`HOLDOUT_FRAC` use (3 search folds over the oldest 85%,
holdout over the newest 15%) and reports equal-weight buy-and-hold
return/sharpe/maxDD per window — no genome, no council, no backtest replay,
just `benchmark_buy_hold()` over each slice. Same guarantees as
`anatomy`/`consults`/`costs`: never touches `live_state.json` or the
champion. Verified first against the live 1d champion (sensible output,
matches the known "-36.8% holdout return" finding already in AGENTS.md),
then run against `--interval 4h` for this investigation. Full test suite
still green (45/45) after adding it.

## Result: 1d and 4h see essentially the same calendar regimes

| window | 1d return / sharpe / maxDD | 4h return / sharpe / maxDD |
|---|---|---|
| fold 1 (2022-08/10 → 2023-10-05) | +6.8% / 0.42 / -34.7% | +8.6% / 0.42 / -36.0% |
| fold 2 (2023-10-05 → 2024-11-22) | +197.8% / 1.78 / -52.1% | +204.5% / 1.74 / -55.8% |
| fold 3 (2024-11-22 → 2026-01-10) | -3.9% / 0.31 / -56.7% | +2.1% / 0.41 / -59.5% |
| holdout (2026-01-10 → 2026-08-17) | -36.8% / -1.19 / -42.1% | -36.3% / -1.24 / -42.8% |

Unsurprising in hindsight — the fold/holdout boundaries are fixed fractions
of the same underlying calendar history for the same 27-symbol universe, so
resampling to 4h bars doesn't change what happened in the market, only how
finely it's diced. This rules out the naive version of the "regime
mismatch" theory from the 08:20 note: **the holdout is not a secretly easier
bull market that a lucky genome coasted through.** It is the single worst
window of the four by raw buy-and-hold terms — down -36%, Sharpe -1.2 to
-1.24, a real bear leg — while fold 2 is a spectacular +200%+ bull run.

## The actual mechanism: fitness is relative, and the folds/holdout pull in opposite directions

This flips the anomaly from confusing to expected. `edge_vs_benchmark()` and
the Sortino-shaped `fitness()` measure performance **relative to buy-and-hold
of the same universe**, not absolute return. The unscaled-seed genomes that
generation's fixes produced were built defensively out of necessity
(`consult_moderate` disabled entirely, `correlation_penalty` near-max at 0.9,
chop-regime sizing halved) — three separate risk-reducing patches, because
the raw unscaled seed was catastrophically overtrading at 4h.

- **Fold 2 is a +204% melt-up.** Any genome trading defensively (smaller
  size, fewer entries, correlation vetoes) will *structurally* underperform
  a passive basket riding a broad bull run that hard — it cannot keep up
  without taking exactly the risk it was just forced to shed. That alone is
  enough to drag fold-aggregate fitness deeply negative, independent of
  whether the strategy is "good."
- **The holdout is a -36% bear leg.** A defensive genome holding cash,
  vetoing correlated entries and sizing down in chop is exactly the profile
  that loses *less* than a passive basket in a real drawdown — which is
  precisely what `beat_benchmark: true` at rising holdout fitness (0.815 →
  1.704 → 2.486 across v2→v3→v4) is reporting. Losing less than -36% is a
  low bar, but it is a genuine edge over doing nothing in that window.

So the split isn't a data-window mismatch or a search artifact — it's the
predictable signature of a defensive-by-necessity genome scored against two
windows with opposite character (one euphoric, one bearish). A strategy
tuned to survive can look bad in the first and good in the second at the
same time, for the same underlying reason. Generation 4's rejected
candidate (better fold-aggregate, -0.171, but failed the holdout at -0.768)
fits this too: whatever made it fold-competitive in a way v4 wasn't
plausibly cost it some of that defensiveness, which the holdout then
punished — consistent with, not contradicting, this read.

## Answering the open question

Not "is the holdout an easier regime" (no — it's the hardest of the four by
raw buy-and-hold return) but "is the split explained by regime": yes, just
not the direction assumed. Fold 2's outlier bull run structurally
disadvantages any risk-reduced genome on relative-return fitness, and the
holdout's bear leg structurally advantages the same genome the same way.
Nothing here says the unscaled-seed v4 genome is *good* — its raw
fold-aggregate fitness never went positive, meaning it still didn't
beat-benchmark in 2 of the 3 folds even accounting for this effect — but it
does explain why holdout fitness kept rising while fold fitness stayed flat,
without needing a "lucky window" story.

One thing this diagnostic does not resolve, and a natural next step for
whoever picks up item 2 or 3 in AGENTS.md: is `FOLD_CONSISTENCY_WEIGHT`
(which already penalises cross-fold variance) doing enough when one of three
folds is a +200% outlier bull run baked permanently into the fixed 85/15
split? A rolling or regime-stratified fold scheme would answer that; not
attempted here, this run only characterised the existing fixed windows.

Nothing here touched `live_state.json`, `researcher_memory`, or the real
champion. `state/cache/*.pkl` (both 1d and 4h, now cached from this run) is
gitignored and ephemeral.
