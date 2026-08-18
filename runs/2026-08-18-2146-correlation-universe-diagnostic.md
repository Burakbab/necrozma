# 3-hourly check — 2026-08-18 21:46 UTC — cross-universe correlation diagnostic

## Git state on entry

Container came up in detached HEAD with local `main` on a completely
unrelated 2-commit history (no shared ancestor with `origin/main` at all —
`git merge-base` returned nothing), unlike the usual "diverged, shared
history" case other 3-hourly notes describe. Resolved per protocol:
`git checkout main && git reset --hard origin/main`. Confirmed the reset
landed on the real project (`AGENTS.md`, `runs/` present) before doing
anything else.

## Daily bar

Already handled. `live_state.json` `updated: 2026-08-18T00:21:43+00:00`
matches `runs/2026-08-18-0020-daily-trading.md` (tick 4). Cross-checked
against today's own `runs/2026-08-18-2030-daily-evaluation.md`, which
already confirmed the mechanism ran cleanly. No tick attempted this cycle.

## What was built

A read-only diagnostic for the open decision AGENTS.md item 3 flagged after
the `correlation_penalty` grid (5 values, 3 champions) lost every time:
"either drop the single-fixed-value line, or move to the cross-universe
pairwise factor-model version if this is still worth pursuing
structurally." Nothing had actually measured the universe's own
correlation structure — the live mechanism
(`agents.judges.RiskJudge._correlation_scale`) only ever compares a new buy
candidate against symbols already *held*, never the rest of the universe.
That gap is exactly what a fuller factor-model version would need
justifying first.

- `loop.engine.pairwise_correlation_stats(rets: dict[str, np.ndarray],
  threshold: float = 0.5) -> dict`: a pure function, every pairwise Pearson
  correlation across a set of return series, summarised (mean, median, min,
  max, fraction above a threshold, pair/symbol counts). Degenerate inputs
  (near-zero variance, too-short series, NaNs, fewer than 3 usable symbols)
  are dropped rather than raised — same "fail toward nothing to report"
  convention `agents.judges._pairwise_corr` already uses for the live
  mechanism.
- New CLI `evotrader_bundle.py correlation-universe [--interval I]
  [--lookback N] [--samples N] [--threshold X]`: for each walk-forward fold
  and the sealed holdout (same split `regime`/`fold-scheme` use), samples
  `--samples` points (default 8) spaced through the window, computes the
  full pairwise correlation matrix of `--lookback`-bar (default 30,
  matching the `correlation_lookback` gene's own default) raw returns
  across every universe symbol at each sample point, and reports the
  mean/range per window plus a fold-vs-holdout comparison. Genome-
  independent — raw price correlation, not any consult or genome signal —
  same guarantee class as `regime`.

## Result against the real champion (v3), full history

```
UNIVERSE PAIRWISE CORRELATION BY FOLD/HOLDOUT — 1d bars, 27 symbols (threshold +0.50)
====================================================================================================
  window     start        end          samples  mean corr               range  frac >= thr
  fold 1     2022-10-18   2023-10-06         8     +0.636      [+0.55, +0.79]       78.0%
  fold 2     2023-10-06   2024-11-23         8     +0.515      [+0.35, +0.71]       58.2%
  fold 3     2024-11-23   2026-01-11         8     +0.625      [+0.53, +0.71]       73.9%
  holdout    2026-01-11   2026-08-18         8     +0.577      [+0.41, +0.81]       63.9%

  mean fold correlation +0.592 vs holdout +0.577 (holdout lower by 0.015)
```

Wall clock: ~80s (one `load_universe` call, no backtest, no Council — same
cost class as `regime`).

## Reading it

Two things stand out, both pointing the same direction:

1. **Correlation is high everywhere.** Every window's mean is above +0.5,
   and 58-78% of pairs individually clear the +0.5 threshold. This is a
   crypto universe correlated to a common beta most of the time, not a
   basket with a few tight clusters and a lot of genuine diversification
   sitting elsewhere in the 27 symbols.
2. **The sealed holdout isn't a correlation outlier.** The original
   crisis-contagion hypothesis behind item 3 (diversification collapsing
   exactly when it's needed, i.e. correlation spiking specifically in the
   holdout's crash window) doesn't show up here — holdout mean (+0.577) is
   *lower* than the fold mean (+0.592), and the gap (0.015) is smaller than
   the spread of individual samples within any one window (e.g. fold 2's
   range is [+0.35, +0.71], a 0.36 spread). Whatever regime-dependence
   exists is swamped by within-window sample noise at this granularity.

Put together: the wider universe wasn't hiding a differently-structured
correlation opportunity that a held-vs-candidate check would miss and a
fuller factor model would catch. It's uniformly high, which is closer to
"nothing to exploit with cleverer pairwise machinery" than to "there's a
cluster the current mechanism blind to." That's evidence toward the "drop
the line" side of item 3's fork, not the "build bigger" side — though not
proof; see caveats below.

## Caveats — why this isn't a final answer

- **Raw universe correlation, not portfolio-realized correlation.** This
  measures correlation across all 27 symbols equally. It says nothing about
  the correlation structure of what the champion's Risk Judge actually ends
  up holding together on a given bar (typically 4-8 positions out of 27,
  chosen by other genes entirely). If the champion's own selection process
  happens to concentrate in the more-correlated half of the universe more
  than a random symbol would, held-vs-candidate is already seeing a biased,
  worse-than-average sample — this diagnostic can't tell.
- **8 samples/window is coarse.** The within-window range (e.g. fold 2's
  [+0.35, +0.71]) shows real time-variation this sampling doesn't resolve
  finely — a genuine correlation spike lasting a handful of bars around a
  specific crash event could exist and simply not land on a sample point.
- **30-bar lookback is one choice.** Matches the gene's own default, chosen
  for comparability, not validated as the "right" window for measuring
  regime-dependent correlation.

## Why this is safe

- Purely additive: `loop.engine` is not in the constitution's checksummed
  set (`constitution` + `core.portfolio` only) — verified live,
  `constitution verified dfae6a697f51fb49` unchanged before/after.
- Bundle mechanics: same `ast.parse` -> locate `_SRC['loop.engine'] = ...`
  literal -> `ast.literal_eval` -> edit as ordinary Python -> `repr()` ->
  splice-back-at-same-span approach documented in
  `runs/2026-08-17-0050-hard-call-flagging.md`, verified by round-tripping
  the literal back through `ast.literal_eval` and confirming the new
  function name appears, then `py_compile`.
- Tested: `tests/test_universe_correlation.py`, 9 new tests (identical
  series -> corr ~1, negated series -> corr ~-1, independent noise -> corr
  near 0, degenerate/zero-variance/too-short/NaN series dropped not raised,
  fewer-than-3-symbols and all-degenerate both error cleanly, threshold
  changes the count but not the underlying correlations). Full suite: **94
  passed, up from 85**.
- Verified against the real `live_state.json`: `summary` and `tick` both
  ran clean (`tick` correctly reported "bar 2026-08-17 already traded (tick
  4) — nothing to do", no double-trade), `constitution verified
  dfae6a697f51fb49` throughout, `md5sum live_state.json` identical
  before/after (`c4289723973ee8ace977f7abaf0003a8`), `git status` showed
  only the intended diagnostic changes.

## AGENTS.md updated

New "Current state" entry, the `correlation-universe` command added to both
command-reference lists (with a paragraph explaining cost/behavior next to
`fold-scheme`'s), and item 3 of "Next steps" gained a new "Resolved"
sub-entry pointing at this result and its caveats.
