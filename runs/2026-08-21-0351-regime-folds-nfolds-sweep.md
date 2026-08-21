# regime-folds: sweeping --n-subwindows / --n-folds

Follow-up to `runs/2026-08-21-0056-regime-folds-and-holdout-pressure.md`, which
shipped `regime-folds` and left AGENTS.md item 2 with an explicit next step:
"sweep `--n-subwindows`/`--n-folds`, and settle whether isolating vs. forcing
the dominant window to share a fold is the right objective." This run does
that sweep. No code changed — existing CLI flags, purely read-only diagnostic.

## Setup

`tick` re-checked first: `live_state.json`'s `updated` is
`2026-08-21T00:27:21+00:00`, and `runs/2026-08-21-0020-daily-trading.md`
already recorded today's bar processed (tick 7, no trade, non-promoting
`evolve 3`). `tick` not re-run this session, no double-trade risk.

## Sweep 1: n_folds fixed effect at constant n_subwindows=6

| n_folds | baseline aggregate | stratified aggregate | delta |
|---|---|---|---|
| 3 | 1.396 | 2.119 | **+0.723** |
| 4 | 2.037 | 2.163 | **+0.126** |
| 5 | 2.053 | 1.804 | **−0.249** |

A clean monotonic trend against champion v3 (live): the stratification
benefit shrinks as fold count rises and flips negative by n_folds=5. Looking
at the fold-fitness lists explains why. At n_folds=3 and 4, the single
dominant sub-window (w3, +156.8% b&h) is isolated alone in its own fold and
scores very high (5.696) while every other fold still merges several
sub-windows together, staying moderate. At n_folds=5, LPT balance starts
isolating *other* sub-windows too — specifically w5 (−27.9% b&h) ends up
alone in fold 3, which the calendar baseline would have merged with
offsetting windows, and it drops to fold fitness **−0.544** on its own. The
cross-fold consistency penalty (`FOLD_CONSISTENCY_WEIGHT * std(fold_fits)`)
reacts to spreading a strong isolate (+5.7) against a weak isolate (−0.5)
more than it reacts to the calendar baseline's narrower fold-fitness range —
so the benefit from isolating the good outlier gets eaten by the cost of
also isolating a bad one.

## Sweep 2: n_subwindows fixed effect at constant n_folds=3

| n_subwindows | baseline aggregate | stratified aggregate | delta |
|---|---|---|---|
| 4 | 1.396 | 2.110 | +0.714 |
| 6 | 1.396 | 2.119 | +0.723 |
| 8 | 1.396 | 1.806 | +0.410 |

Less clean than the n_folds sweep, but the same shape: still positive at
every resolution tried, peaks around 4-6 sub-windows, weakens at 8 (finer
sub-windows fragment the dominant window's isolation — w3's +156.8% at
n=6 splits into w4/w5 at n=8, no single sub-window carries the same
concentrated weight alone anymore).

## Sweep 3: does the n_folds=5 reversal generalize across champions?

Ran `--n-subwindows 6 --n-folds 5 --also-version N` against the other two
real champions:

| champion | baseline aggregate | stratified aggregate | delta |
|---|---|---|---|
| v3 (live) | 2.053 | 1.804 | −0.249 |
| v1 | 0.033 | −0.127 | −0.160 |
| v2 | 0.020 | 0.055 | +0.035 (near zero) |

Two of three champions lower at n_folds=5, the third is a wash — a much more
consistent "stratification stops helping past a low fold count" story than
the mixed n_folds=3 reading from the previous run (v3 +0.723, v1 +0.057, v2
−0.065, no clear pattern by champion). The champion-level variation at
n_folds=3 looks like it was partly a fold-count artefact, not fully a
per-genome property.

## Reading against the open design question

The previous run's open question was whether *isolating* the dominant window
(what LPT balance actually does — nothing else is heavy enough to make
pairing with it the balanced choice) is the right objective, versus something
that actually *splits/dilutes* it. This sweep sharpens that: isolating the
dominant window only helps net aggregate_fitness while the fold count stays
low enough that isolation is selective (just the one outlier). Raise fold
count and the same LPT mechanism starts isolating *unfavorable* sub-windows
too, and the aggregate-fitness cost of that outweighs the benefit — because
the consistency penalty punishes a wide spread of isolated-fold fitnesses
more than it punishes the calendar baseline's narrower, already-merged
range. This is evidence *against* "isolating is the fix" as a general
recipe, and sharpens the case (already raised by `fitness-decomp`) that a
fix needs to target the mean term's outlier sensitivity directly — e.g.
capping/down-weighting one exceptional fold's contribution to the mean,
rather than any windowing scheme that relies on LPT-style isolation, which
this sweep shows is a double-edged mechanism, not a one-directional
improvement.

## Verified safe

Purely read-only diagnostic runs, no code touched. `git status --short`
clean throughout (no diff). `live_state.json` md5 identical before and
after (`8b3dc413c9a85fda04bdeb0ad4c63733`), `evotrader.manifest` md5
identical (`6a4434574ff424f74ff300ebdb50d194`), constitution verified
`dfae6a697f51fb49` unchanged on every invocation. Today's 2026-08-21 bar
(the last closed daily bar, dated 2026-08-20 in the tick record) confirmed
already processed by the 00:20 UTC daily run before this check started —
`tick` not run this session, no double-trade risk.

## Next

The n_folds=5 reversal is the sharpest finding so far against "regime
stratification via sub-window isolation" as a general fix. Two directions
open: (a) try `--n-folds 3` with more sub-windows to see if the positive
effect is robust when isolation stays selective (a partial answer already
in Sweep 2 — n=8 weakens it even at n_folds=3), or (b) shift design attention
to a fix that targets `Evaluator`'s mean term directly (e.g. capping any
single fold's contribution before averaging, or a genuinely different
aggregation than plain mean-minus-std-penalty) rather than any windowing
scheme, since this sweep shows windowing-only fixes are sensitive to a
parameter (fold count) with no principled "correct" value yet identified.
Either is real design work, bigger than a single 3-hourly slot to build and
argue through `AMENDMENTS.md` (this stays a diagnostic; no constitution
change made).
