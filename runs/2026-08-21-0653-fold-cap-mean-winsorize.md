# fold-cap: winsorizing the outlier fold's mean-term pull — mixed, not a fix

2026-08-21 (3-hourly check)

## Why

AGENTS.md's Current state (2026-08-21-0351 entry) flagged the remaining
untried option in the fold-instability thread: `fitness-decomp` (2026-08-20)
traced `aggregate_fitness`'s swing across fold schemes to the *mean* term of
the fold fitnesses, not the `FOLD_CONSISTENCY_WEIGHT * std` penalty term. The
`regime-folds` `--n-subwindows`/`--n-folds` sweep (2026-08-21-0351) then
showed that *isolating* the dominant fold into its own group (the
regime-stratified approach) is double-edged — it helps at low fold counts but
isolating a weak fold the same way costs more than the good isolate gains as
fold count rises, with no principled correct operating point. That run's own
conclusion: "shift attention entirely to a fix that caps/down-weights a single
outlier fold's pull on the mean term ... rather than any windowing/isolation
scheme." This is that fix, measured as a diagnostic first, not applied.

## What was built

New pure function `loop.evolve.capped_fitness_decomposition(fold_fits, cap_z=1.0)`:
winsorizes each fold fitness to a ceiling of `mean(fold_fits) + cap_z *
std(fold_fits)` (values below the ceiling untouched; nothing capped from
below, since the concern is one fold pulling the mean *up*, not down) before
taking the mean, and reports both the plain and capped aggregate side by
side. The `FOLD_CONSISTENCY_WEIGHT * std` penalty term is deliberately left
computed from the *original*, uncapped `fold_fits` — that penalty already
exists to punish cross-fold spread, so capping it too would double-count the
same concern the mean-capping is meant to isolate on its own. Tested:
`tests/test_capped_fitness_decomposition.py`, 9 new tests (penalty-term
invariance under capping, dominant-outlier gets capped, no-outlier is a
no-op, zero-spread/single-fold degenerate cases match `fitness_decomposition`
exactly, monotonicity in `cap_z`, never caps from below, empty-input branch).
Full suite 176 passed, up from 167.

New read-only CLI `fold-cap [--cap-z Z] [--also-version N]`: reuses the exact
same 5 fold schemes `fitness-decomp` already evaluates (disjoint `n_folds`
3/5, rolling overlap 0.5/0.7/0.85 via the existing `rolling_folds`), runs one
backtest per window per scheme (same cost class as `fitness-decomp`/
`fold-scheme` — capping is a pure post-hoc transform of `fold_fitness`, so
each scheme's backtest is run once and reused across the whole `cap_z`
sweep), and reports how the `aggregate_fitness` range across those 5 schemes
changes as `cap_z` sweeps a default grid `[0.5, 1.0, 1.5, 2.0]`. Never
touches `live_state.json`, `N_FOLDS`, or the sealed holdout.

## Result

Against champion v3 (live), capping makes the cross-scheme range **wider at
every tested `cap_z`**, never tighter:

```
 cap_z  capped range  vs baseline
  0.50         0.977       +0.320  (wider)
  1.00         0.835       +0.178  (wider)
  1.50         0.659       +0.002  (wider)
  2.00         0.657       +0.000  (same)
```
(uncapped baseline range: 0.657)

Against v1 (the seed, reconstructed), it's the opposite — capping **tightens**
the range at the two more aggressive settings:

```
 cap_z  capped range  vs baseline
  0.50         0.446       -0.217  (tighter)
  1.00         0.493       -0.170  (tighter)
  1.50         0.663       +0.000  (same)
  2.00         0.663       +0.000  (same)
```
(uncapped baseline range: 0.663)

## Reading

Same shape this whole investigation keeps landing on: a mechanism that reads
as a plausible general fix for one champion (v1: tighter, cleanly monotonic
in `cap_z`) does the opposite for another (v3: wider, also monotonic but in
the other direction) — not a tie-breaking coin flip, a systematic disagreement
between the two real champions checked. Mechanism for why v3 gets *wider*
under capping, not narrower: the schemes that produce v3's highest aggregate
(`disjoint n_folds=5` at +2.053, `rolling overlap=0.7` at +1.954) are exactly
the schemes where the dominant fold's fitness is being winsorized down the
hardest, while the schemes already near the bottom of the range
(`disjoint n_folds=3` at +1.396) have less spread among their own folds and so
get capped less — capping doesn't compress the range toward the middle, it
pulls down whichever scheme happens to have the fattest single outlier
*within that scheme*, and for v3 that happens anti-correlated with which
scheme was already high, widening rather than narrowing the spread across
schemes. For v1 the correlation runs the other way, so the same mechanism
narrows it. This is evidence the "cap the mean term" idea is exactly as
double-edged as the regime-folds isolation idea it was proposed as an
alternative to — it is not a parameter-free fix waiting for the right `cap_z`;
the direction of the effect depends on which scheme currently holds the
per-scheme outlier, which is champion-specific and not something `cap_z`
alone controls.

Combined with `fold-scheme`'s own n_folds sweep (non-monotonic, champion-
dependent), `rolling-folds` (widens more than it narrows), and `regime-folds`
(double-edged at higher fold/subwindow counts): **four independent windowing/
capping mechanisms have now all shown the same champion-dependent,
non-generalizing shape.** None of them is a clean fix. This is a stronger
basis than any single one of them for treating "reshape the fold scheme" as a
dead end for stabilizing `aggregate_fitness`, and for redirecting future
effort at this problem toward the other half of the picture `holdout-noise`
already measured: the sealed-holdout margin's `MULTIPLE_TESTING_SIGMA`
constant is 14-25x too small across all three real champions (see the
2026-08-20 holdout-noise entries), which is a separate, already-quantified,
already-actionable finding that doesn't depend on getting fold windowing
right first.

## Verified safe

- `loop.evolve` isn't checksummed (only `constitution`/`core.portfolio` are).
- `tools/edit_bundle_module.py verify` round-trip clean before and after the
  edit.
- `py_compile` clean.
- Full suite 176 passed (up from 167), no existing test touched.
- `live_state.json` md5 identical throughout: `8b3dc413c9a85fda04bdeb0ad4c63733`.
- `evotrader.manifest` md5 identical throughout: `6a4434574ff424f74ff300ebdb50d194`.
- `constitution verified dfae6a697f51fb49` unchanged on every invocation
  (nothing touched here is checksummed; no `AMENDMENTS.md` row needed).
- `git status --short` clean of anything but `evotrader_bundle.py` (the new
  CLI command + help line) and the new test file.
- Today's 2026-08-21 daily bar confirmed already processed by the 00:20 UTC
  daily run (`runs/2026-08-21-0020-daily-trading.md`, `live_state.json`
  `updated: 2026-08-21T00:27:21+00:00`) before this check started — `tick`
  not run this session, no double-trade.
- `review-hard-calls` checked: 0 pending (item 4's infrastructure is still
  waiting on its first real flagged bar).

## Next

The fold-windowing/capping line has now had four independent, consistent-
shape negative results (this run, `fold-scheme`, `rolling-folds`,
`regime-folds`). Recommend treating it as exhausted for now rather than
trying a fifth variant (e.g. capping from below too, or a different ceiling
formula) — the champion-dependent sign flip suggests no single-parameter
windowing/capping scheme will generalize across champions, so further
variants are likely to keep reproducing the same shape rather than finding
the fix. The `MULTIPLE_TESTING_SIGMA` recalibration flagged since
2026-08-20's `holdout-noise` work is the sharper, already-quantified next
step on the walk-forward-honesty thread — it's a constitution change
(checksummed, needs an `AMENDMENTS.md` row) and deserves its own design pass,
not a tail-end addition to a diagnostic session. Outside that thread, item 4
(LLM-backed consults) is fully built and just waiting for its first real
`is_hard_call: true` live bar — nothing to do there until one fires. Items 5
(short selling) and 6 (equities/FX) remain the larger unstarted roadmap work.
