# Sealed-holdout sigma recalibration — 2026-08-21 09:51 UTC (3-hourly check)

## What shipped

A constitution change, argued in `AMENDMENTS.md`. New `constitution.HOLDOUT_SIGMA
= 2.0`. `constitution.required_margin(n_candidates, complexity_delta, sigma=
MULTIPLE_TESTING_SIGMA)` gained an optional `sigma` parameter (default unchanged,
so every existing call site — `accepts()`'s fold-aggregate margin — is
byte-for-byte unaffected). `holdout_accepts()` now calls
`required_margin(n_draws, 0, sigma=HOLDOUT_SIGMA)` instead of falling through to
`MULTIPLE_TESTING_SIGMA`. Docstrings on both functions and the new constant
updated to explain the split. `evotrader_bundle.py`'s `holdout-noise` CLI now
also prints the empirical-sigma-over-`HOLDOUT_SIGMA` ratio alongside the existing
`MULTIPLE_TESTING_SIGMA` ratio, so the calibration is checkable every time the
diagnostic runs, not just this once.

## Why now

This closes the "measure the sigma before trusting the number" question
`holdout_accepts()`'s own docstring has posed since 2026-08-16, and that
`holdout-noise` (shipped 2026-08-20) has been quietly answering for a day and a
half: sealed-holdout fitness noise is real and large. Refined estimates
(converged by ~5000 bootstrap draws, `--n-boot` swept to 50000) across all three
real champions this account has had:

| champion | boot_fitness_std | ratio to old 0.08 |
|---|---|---|
| v1 | ~1.48 | ~18.5x |
| v2 | ~1.21 | ~15.1x |
| v3 (live) | ~2.04 | ~25.5x |

Meanwhile four independent attempts this week to fix the *other* half of the
walk-forward-honesty problem — the fold-aggregate mean term's sensitivity to
one dominant calendar fold (`fold-scheme`'s n_folds sweep, `rolling-folds`,
`regime-folds`'s n_folds/n_subwindows sweep, `fold-cap`'s mean-winsorizing) —
all landed on the same shape: plausible per-champion, not a general fix. Both
this morning's 3-hourly run and today's 09:00 daily-discussion check-in read
that as "stop trying variant #5 on the windowing line, the sharper and
already-quantified next step is this recalibration." This run does that step.

## Design decisions

**Why a separate constant instead of bumping `MULTIPLE_TESTING_SIGMA` itself:**
`MULTIPLE_TESTING_SIGMA` protects a different, better-behaved quantity — the
fold-aggregate fitness, which is already an average over `N_FOLDS` disjoint
windows and has its own dedicated defense (`FOLD_CONSISTENCY_WEIGHT`'s cross-fold
variance penalty). Nothing in `holdout-noise`'s measurement — which resamples a
single sealed-holdout window's realized return path — bears on that quantity's
noise. Conflating the two would either weaken the well-estimated fold-aggregate
margin or leave the holdout margin exactly as under-calibrated as before,
depending on which one implicitly won. A separate `HOLDOUT_SIGMA` lets
`required_margin()`'s existing `sigma` parameter (new, but purely additive —
default preserves every current call site) carry the right noise scale to each
gate.

**Why 2.0, not the mean of the three measurements (~1.58) or the raw v3 number
(~2.04):** This constant is a safety floor, not a point estimate to be right
on average — the whole point of a floor is to hold under the worst case seen so
far, and future champions are unmeasured. Using the max of the three real
readings, rounded to a clean number just below the actual v3 max (2.04 rounds to
2.0, not up), is deliberately slightly conservative relative to the champion
that showed the most noise, and clearly conservative relative to the other two.
A live re-run of `holdout-noise` after making the change (`--n-boot 300` against
the current champion v3) measured empirical sigma at 0.91x `HOLDOUT_SIGMA` —
close to 1x, meaning the new constant isn't drastically over- or under-loose for
the actual live champion today, not just in the earlier full-`n-boot` reading
that motivated the choice.

**What this does *not* claim to fix:** `HOLDOUT_SIGMA`'s own docstring and the
`holdout_accepts()` docstring both carry the caveat that was already on record
before this change: block-bootstrapping one backtest's realized return path
measures order/resampling noise, not the *other* named source of extra noise —
a candidate reaching the sealed holdout only after ranking top-3 on folds that
correlate with it, i.e. arriving pre-selected upward. That effect still isn't
quantified. `HOLDOUT_SIGMA` is a real, measured floor on one of the two known
sources of under-margining, not a claim that the gate is now fully honest.

## Net effect on promotion difficulty

Strictly stricter. At `n_draws=1` the sealed-holdout margin goes from
`required_margin(1, 0)` ≈ 0.094 to `required_margin(1, 0, sigma=2.0)` ≈ 2.35 — a
~25x tighter bar on the very first holdout draw a challenger ever faces, and the
gap only widens as the log-of-cumulative-draws term grows with account age. This
makes future promotions substantially harder to clear, in the same direction as
every prior amendment in this log that touched a statistical constant. It does
not affect `accepts()`'s fold-aggregate gate, drawdown-regression check, or any
hard gate at all.

## Verification

- Full suite: 179 passed (up from 176) — 3 new/updated tests in
  `tests/test_constitution.py` (`test_required_margin_defaults_to_
  multiple_testing_sigma`, `test_required_margin_accepts_a_sigma_override`,
  `test_holdout_accepts_uses_holdout_sigma_not_multiple_testing_sigma`;
  `test_holdout_accepts_margin_scales_with_cumulative_draws` updated to derive
  its edge value from `required_margin(sigma=HOLDOUT_SIGMA)` instead of a
  hand-typed constant that assumed the old sigma).
- `tools/edit_bundle_module.py verify`: round-trip clean after reinserting the
  edited `constitution` module.
- `py_compile` clean on the extracted module before reinsertion.
- `evotrader_bundle.py summary` correctly reported `CONSTITUTION MODIFIED`
  against the old manifest before resealing (proves the checksum mechanism is
  live and working, not silently bypassed), then `constitution verified
  8b74865634b1db07` after `evotrader.manifest` was deliberately updated to the
  new checksum in this commit.
- `live_state.json` md5 identical throughout (`8b3dc413c9a85fda04bdeb0ad4c63733`)
  — this change touches only the checksummed constitution package and one CLI
  diagnostic's print statements, never account state.
- `review-hard-calls`: 0 pending, unaffected by this change.
- Today's 2026-08-21 bar confirmed already processed by the 00:20 UTC daily run
  (`live_state.json`'s `updated` timestamp is `2026-08-21T00:27:21+00:00`,
  genome version still 3) before this check started — `tick` not run this
  session, no double-trade.
- Session started with local `main` detached, no merge-base against a
  force-updated `origin/main` (same recurring container-seed artifact every
  prior run's notes have logged) — reset to `origin/main` per the run protocol,
  no work lost.

## Next

`HOLDOUT_SIGMA` is now live for every future promotion attempt — no immediate
follow-up required, but the next time a real promotion is evaluated it's worth
a one-line check of whether the tighter margin changed the outcome versus what
the old 0.08-based margin would have said (informational only, `holdout_accepts`
already recomputes fresh each time). The two other open threads this file has
been tracking are unaffected and still open: whether the fold-windowing/capping
line has any variant worth trying beyond the four already tested (current read:
no), and whether a longer 4h-shadow run ever breaks the observed stagnation
plateau past generation 10-15.
