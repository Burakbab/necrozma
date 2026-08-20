# 2026-08-20 18:55 UTC — regime-scan: is the fold-2 melt-up concentrated enough to warrant regime-stratified folds?

3-hourly self-improvement check. No new bar: the last closed daily bar
(2026-08-19) was already processed by the 00:20 UTC daily run (tick 6);
`tick` re-checked and reports "already traded". No trade this session.

## What shipped

Two things this cycle.

**1. Ran the flagged one-liner `fitness-decomp --also-version 2` (third champion).**
It confirms the finding across all three real champions: the *mean* of the fold
fitnesses swings more than the FOLD_CONSISTENCY_WEIGHT penalty term across the
five fold schemes. v2 (reconstructed): aggregate range 2.543, of which the mean
term ranges 2.173 and the penalty term only 0.370 — an even more pronounced mean
dominance than v3's (mean 1.500 vs penalty 0.610) or v1's (0.609 vs 0.183). So
"the mean term, not the penalty term, drives the aggregate instability" is now a
3-of-3 property, not a v3 quirk. Diagnostic-only, no code changed for this half,
`live_state.json` md5 unchanged.

**2. Shipped `regime-scan`** — the missing measurement before anyone commits to
the regime-stratified fold-scheme engine work every fold diagnostic since
2026-08-17 keeps pointing at. New pure helper
`loop.evolve.regime_concentration(window_returns)` +read-only CLI
`regime-scan [--n-windows K] [--interval X]`. Genome-independent (buy-and-hold
only, no backtest/council), so `--also-version` would change nothing and isn't
offered. Same read-only / never-touch-`live_state` guarantees as `regime`. 8 new
tests (`tests/test_regime_concentration.py`), full suite 151 passed (up from 143).

### The measurement it answers

fitness-decomp settled *that* the aggregate swings because of the mean term (one
dominant window pulling the fold average). The open design question is whether a
regime-stratified scheme (spread that window across folds) is worth the engine
work for non-contiguous folds `run_backtest` can't replay — and that turns on one
unmeasured number: is the melt-up **isolated** to a tight stretch (stratification
helps) or **diffuse** (it won't)? `regime_concentration` measures it from
per-window buy-and-hold log-returns: shares `p_i = |log(1+r_i)| / sum|log(1+r_j)|`,
`hhi = sum p_i^2`, `concentration_ratio = top_share * n` (1.0 = even, >1 =
concentrated).

### Result: concentrated, and scale-robust

Concentration ratio holds at ~2.5–2.75x its even share at **every** resolution:

| resolution | richest window | its share of |log-growth| | ratio |
|-----------:|:---------------|--------------------------:|------:|
| n=3 (fold resolution) | fold 2, +257% b&h | 91.8% | 2.75x |
| n=6 | +152% window | 42.9% | 2.57x |
| n=12 | +102% window | 20.4% | 2.45x |

The raw *share* falls as windows get finer (finer bins split the bull runs), but
the *ratio over even share* stays ~2.5x — the concentration is real, not a
coarse-binning artefact. At the resolution evolution actually uses (n=3), one of
three folds carries **92%** of the region's compounded growth. That is the fold-2
melt-up, quantified.

### Sharper mechanism the n=12 scan exposes

Fold 2 isn't one indivisible melt-up event — it's **two separated bull runs
colliding in one calendar fold**: w5 (2023-10→2024-01, +92.5%) and w8
(2024-08→2024-11, +102.1%), with w7 (−19.1%) between them. Under the fixed 3-fold
split both land in fold 2. This is exactly the case regime-stratification is
built for: put w5's bull run in one fold and w8's in another and the +200% fold-2
outlier stops existing, without inventing or dropping any data. So the engine
work for non-contiguous folds looks **warranted** — the melt-up is separable, not
a single atomic window you'd have to keep whole.

## Verification / safety

- `constitution verified dfae6a697f51fb49` unchanged — not touched. `loop.evolve`
  is not checksummed (constitution + core.portfolio only), edited via
  `tools/edit_bundle_module.py` (round-trip `verify` clean before and after),
  `py_compile` clean.
- `live_state.json` md5 `cca58deb976cef403c5010f2e2b9528b` identical throughout
  (before fitness-decomp, after regime-scan at n=3/6/12). `evotrader.manifest`
  md5 `6a4434574ff424f74ff300ebdb50d194` identical. No trade, no promotion, no
  constitution amendment → no AMENDMENTS.md row, no README Status change needed.
- Full suite 151 passed. New helper is pure and identity-checked
  (total_return compounds the windows exactly; ratio = top_share * n).
- Session started detached, two stale seed-import commits behind a force-updated
  `origin/main`; reset to `origin/main` per protocol (only diff was the
  local-only `docs/` folder, no work lost).

## Next

- The regime-stratified fold scheme itself is now motivated *and* measured: at
  fold resolution one fold holds 92% of growth (ratio 2.75x), and the n=12 scan
  shows the melt-up is two separable bull runs, so splitting them across folds is
  a concrete, data-preserving fix. Building it is still real work and a
  **constitution change** (it changes how a challenger is scored — `Evaluator`
  would need to accept a fold as a *set* of windows, and `run_backtest` would
  need to replay a non-contiguous union of bars; N_FOLDS / FOLD_CONSISTENCY_WEIGHT
  live in the checksummed constitution). That needs a design pass and an
  `AMENDMENTS.md` row, not a tail-end addition — flagged, not started.
- A regime *definition* independent of the window under test is now in hand:
  `regime-scan`'s per-window buy-and-hold return is exactly the genome-independent
  label a stratifier would group on (bull / flat / bear).
- Cheap follow-up not run: `regime-scan --interval 4h` to check whether the 4h
  bars show the same ~2.5x concentration (the shadow-evolution track would want to
  know before any 4h fold-scheme redesign).
