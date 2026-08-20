# 2026-08-20 12:54 UTC — 3-hourly check: rolling-fold diagnostic + holdout-noise convergence check

## Housekeeping

Cloud clone started detached with a stale local `main` two commits behind
(`fa43c4b`/`a4f81e0`, superseded Aug 15-16 initial-import commits, same shape
as the last two runs' notes on this) — reset to `origin/main` per the run
protocol. `pip3 install -r requirements.txt -q` clean. Today's 2026-08-19 bar
(the last closed daily bar as of the 00:20 UTC run) confirmed already
processed before this session touched anything (`live_state.json` `updated`
timestamp `2026-08-20T00:21:36Z`, `tick` correctly reports "already traded");
no double-trade. `review-hard-calls` still reports zero pending — no live bar
has flagged `is_hard_call` yet, so item 4's "first real review" step is still
not actionable.

## 1. Holdout-noise convergence check (cheap, no code change)

The 2026-08-20-0654/0948 runs measured the sealed-holdout bootstrap sigma at
`n_boot=1000` for all three real champions (v3 ~23.8-26x
`MULTIPLE_TESTING_SIGMA`, v1 ~18.9x, v2 ~14.3x) and flagged "a much higher
`--n-boot` to check the estimate has converged" as the one remaining cheap
option. Ran it: `--n-boot` swept 1000/5000/20000/50000 x 3 seeds each against
v3, plus one `--n-boot 20000` pass each against `--also-version 1` and
`--also-version 2`.

Result: converges cleanly. At `n_boot=1000` the empirical-sigma-ratio spread
across seeds is ~25.1-26.1x (±0.5x); by `n_boot=5000` it tightens to
25.4-25.7x; by 20000-50000 it's stable at 25.4-25.6x (±0.1x). Refined point
estimates: **v3 ≈ 25.5x, v1 ≈ 18.5x, v2 ≈ 15.1x** `MULTIPLE_TESTING_SIGMA` —
consistent with (slightly higher than) the `n_boot=1000` reads, same relative
ordering across champions. This closes the "has it converged" question
cleanly: yes, by ~5000 draws, and the ~24-26x order-of-magnitude finding was
never an artifact of too few bootstrap resamples. No further cheap data
points remain on the noise-magnitude question — diagnostic only, no code
changed, no commit for this half.

## 2. New diagnostic: `rolling-folds` (code shipped)

AGENTS.md's item 2 "Next" line has said since 2026-08-18 that a
regime-stratified/rolling fold scheme is the untried alternative to just
raising `N_FOLDS` (which the existing `fold-scheme` diagnostic showed shrinks
every window as count rises — at `n_folds=8` one window came within 25 bars
of `run_backtest`'s hard 120-bar minimum and another failed a hard gate
outright). Built the rolling half of that as a new read-only diagnostic,
same guarantee class as `fold-scheme`/`regime`/`correlation-universe`.

New `loop.evolve.rolling_folds(search_end, base_n_folds, overlap)`: a pure
function returning overlapping, **fixed-width** windows spanning the
searchable region — width is pinned to whatever `Evaluator.folds()` already
uses at `base_n_folds`, and that fixed-size window slides across the region
by `(1 - overlap) * width` per step, so more (correlated) reads of the same
span never shrink any individual window below its `base_n_folds` size.
`overlap=0.0` reproduces `Evaluator.folds()`'s own disjoint edges exactly
(verified by test). Wired into `Evaluator.evaluate(g, folds=...)`, which
already accepted a custom fold list — no change to `Evaluator` or the
constitution needed. New CLI `rolling-folds [--overlap F] [--base-n-folds N]
[--also-version N]`, mirroring `fold-scheme`'s structure and same-run
disjoint-vs-rolling comparison. `tests/test_rolling_folds.py`, 9 new tests
(zero-overlap-matches-disjoint-exactly, fixed width, monotonic window count
vs overlap, in-bounds, chronological ordering, invalid-input rejection) —
full suite 136 passed, up from 127.

**First result, against live champion v3** (default `overlap=0.5`,
`base_n_folds=3`, same 3-way calendar split `fold-scheme`'s baseline uses):
5 overlapping windows, `aggregate_fitness` 1.399 vs the disjoint baseline's
1.480 (−0.080) — close, and the outlier gap (largest single window's b&h
return vs mean of the rest) shrinks modestly, +252.4% → +222.9%, because the
127-bar melt-up episode (`drawdown`'s fold 2, unchanged across every prior
diagnostic in this file) is still fully contained inside one window at this
overlap. Swept `--overlap 0.7` (7 windows) and `--overlap 0.85` (14 windows):
`aggregate_fitness` does **not** converge or stabilize as overlap rises —
0.306 (0.85) vs 2.003 (0.7) vs 1.399 (0.5) vs 1.480 (baseline), a wider swing
than the existing `fold-scheme` n_folds sweep already showed (−1.224 →
+1.633 → −0.500 across n=3/5/8). The outlier gap does shrink monotonically
with overlap (252.4% → 222.9% → 152.9% → 152.7%, flattening past 0.7), but
`aggregate_fitness` swinging harder than the gap it's supposed to be
insulating against says the instability isn't purely "one big fold
dominates" — `FOLD_CONSISTENCY_WEIGHT`'s cross-fold std penalty is itself
sensitive to how many (correlated) windows get fed into it, and adding more
overlapping reads adds noise to that penalty term at least as fast as it
dilutes the outlier. Cross-checked against `--also-version 1`: the outlier
gap is identical to v3's at every overlap (genome-independent by
construction, same as `fold-scheme`'s finding), `aggregate_fitness` ranks
v1 < v3 as everywhere else, and the rolling-vs-disjoint delta is negative for
both champions at `overlap=0.5` (v3 −0.080, v1 −0.306) — not yet enough
points to say whether that sign is systematic or coincidence.

**Reading against the open "Next" item:** rolling windows are not a
free win. Naive fixed-width sliding does mute the raw outlier-gap number, but
it does **not** produce a more stable `aggregate_fitness` than the existing
disjoint-fold-count sweep — if anything, moderate-to-high overlap swings it
harder. This is real, if negative, evidence: whoever next attempts the
"regime-stratified/rolling redesign" this file has flagged since 2026-08-18
should not assume "add overlap" alone solves the non-monotonicity: either
`FOLD_CONSISTENCY_WEIGHT` needs to change alongside the windowing (fewer,
less-correlated windows might need a different variance weight than more,
more-correlated ones), or the fix needs to be genuinely regime-stratified
(grouping by market character, not just calendar position) rather than a
denser calendar slide. Not attempted this run — regime-stratification is a
separate, larger question (would need to define "regime" independent of the
window itself, e.g. via `regime`'s own buy-and-hold sharpe/return
characterization) and deserves its own session, per the same
"don't start something you can't land" scoping this note is itself following.

**Verified safe:** purely additive (`loop.evolve` isn't in the checksummed
set — `constitution` + `core.portfolio` only), `tools/edit_bundle_module.py
verify` round-trip clean before editing, `py_compile` clean, full suite 136
passed (up from 127, 9 new), `live_state.json` md5 identical throughout
(`cca58deb976cef403c5010f2e2b9528b`), `evotrader.manifest` md5 identical
(`6a4434574ff424f74ff300ebdb50d194`), `constitution verified
dfae6a697f51fb49` unchanged, `git status --short` clean of anything but the
`evotrader_bundle.py` diff and the new test file before this run's own
commit, `tick` re-checked after all diagnostic runs and still correctly
reports "already traded" (no double-trade).

## Next

- The regime-stratification half of item 2's rolling/regime-stratified idea
  is still untried — this run only did the rolling-window half, and found it
  isn't sufficient by itself.
- `rolling-folds --also-version 2` would complete the three-champion sweep
  this diagnostic hasn't run yet (one line, same pattern as every
  `--also-version` follow-up in this file).
- Item 4 (hard-call review) still has nothing to review — first real
  `is_hard_call: true` live bar is still pending.
- The `MULTIPLE_TESTING_SIGMA` recalibration decision (now with a converged
  ~25.5x/18.5x/15.1x per-champion point estimate) is still an unstarted
  constitution change, and this run's finding sharpens why it "reads best
  combined with the fold-scheme work" rather than done in isolation: the
  fold-scheme instability itself doesn't have an obvious fix yet either.
