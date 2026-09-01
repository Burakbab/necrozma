# cold_start_ramp grid search is chasing noise -- every "best" point tested so far fails the real gate most days

**3-hourly check, ~15:46-16:47 UTC.** Direct follow-up to the 13:16 UTC
session's own flagged next step (AGENTS.md item 2): "sweep other points from
the 08:08 UTC grid search... through `--recipe consv_trailing_ramp --shift 7`
for a wider-margin point." Built the tooling for it, then ran it, and the
result closes that option off rather than opening a better one.

## What was built

`tools/shadow_4h_x6_seed.py`'s `build_consv_trailing_ramp_seed()` and
`tools/shadow_4h_fold_date_sensitivity.py`'s `build_genome()`/CLI now accept
`ramp_bars`/`ramp_start_scale` overrides (new `--ramp-bars`/`--ramp-scale`
flags; defaults unchanged at 120/0.20, so every prior call site and test
still behaves identically). Previously the fold-date-sensitivity tool could
only check the one hardcoded 120/0.20 point -- this was needed before any
other grid point could be run through the same systematic multi-day check.
5 new hermetic tests, full suite 290/290, committed separately (`5d962bb`)
before running anything, since the tool change is a complete, tested
contribution independent of what it would find.

## Step 1: re-ran the 08:08 UTC sweep at today's data cutoff -- the landscape moved completely

Same `tools/cold_start_ramp_sweep.py`, same seed genome, ~8 hours later
(one extra day's worth of trailing 4h bars). Result: **only 20/37 points
clear `MAX_DD_HARD_FAIL` now, down from 35/37 at 08:08 UTC** -- and the
previous session's own recommended point, **120/0.20, now hard-fails
outright (-44.0% max_dd, `aggregate_fitness` -2.460), a complete flip from
this morning's -34.6% pass**. This isn't a marginal boundary-shift flip like
the 10:27 UTC session found (that was +5.4pp margin flipping to -3.4pp) --
it's the "best" point from a 37-point search failing by 4 points *worse*
than the hard-fail line, on the same seed genome, roughly 8 hours later.

Today's new top point by `aggregate_fitness`: `ramp_bars=150,
start_scale=0.20` (0.472, gate max_dd -34.6%), narrowly ahead of `120/0.30`
(0.471, -34.6%). Full table in `tools/cold_start_ramp_sweep.py`'s own
output (re-run for current numbers -- this table is already stale by the
time anyone reads it, which is rather the point of this note).

## Step 2: checked today's new "best" point across a week with the fold-date-sensitivity tool -- it's worse than 120/0.20 was

`python3 tools/shadow_4h_fold_date_sensitivity.py --recipe
consv_trailing_ramp --ramp-bars 150 --ramp-scale 0.20 --shift 7`: **6 of 7
shifts hard-fail `MAX_DD_HARD_FAIL`**, only today's own as-of date (shift 0)
clears, and even that by a modest +4.6pp margin. The 13:16 UTC session's
120/0.20 check hard-failed 4/7 shifts; this session's top single-day pick
for the *same* seed genome hard-fails *6/7* -- picking the best point from a
fresh point-in-time sweep did not find a more robust point, it found a
point that happens to clear on the one day it was measured and fails almost
everywhere else nearby, same shape as every point checked so far.

## Conclusion: option (a) is closed, option (b) is the only one left standing

The 13:16 UTC note left two untried options: (a) sweep other grid points for
a wider-margin point, or (b) treat this seed genome's fold 1 as structurally
fragile and look for a different lever. This session ran (a) as concretely
as the tooling allows -- a fresh 37-point sweep plus a 7-day robustness check
on its own top pick -- and both steps point the same direction: **there is
no stable point in this two-gene grid**. The point that looks best on any
single day is, by the evidence gathered across three separate sessions now
(08:08 UTC's 120/0.20, 13:16 UTC's 7-day check of it, and this session's
150/0.20), essentially uncorrelated with whether it clears the gate a few
days later. Grid-searching harder within `cold_start_ramp_bars`/
`cold_start_ramp_start_scale` is very unlikely to find a genuinely robust
point -- three different "best of the day" picks have now been tried and
all three fail most nearby days.

**Recommend closing this narrow sub-thread**: do not run another
point-in-time sweep over these two genes expecting a better answer. The
fold-1 cold-start dynamics on this specific seed genome (`consv1 +
trailing_stop -0.06`) are fragile enough that a two-gene position-size ramp
cannot paper over them robustly. Two real next steps, either a bigger lift
than a single 3-hourly session: (1) go back to the pre-ramp genome and try a
structurally different lever on fold 1 specifically (the ramp addresses
*sizing* into a cold start; an untried alternative is changing *what
triggers* new entries in the first N bars after a cold start, e.g. a
stricter consult threshold specifically during the ramp window, not just a
smaller size); or (2) step back further and question whether this whole
`consv1 + trailing_stop` seed genome is the right base to keep patching --
every fix applied to it so far (the ramp, the trailing stop tightening) has
addressed one symptom while the underlying fold-1 drawdown keeps
resurfacing under a different guise.

## What this doesn't change

`live_state.json` untouched throughout (all read-only `Evaluator.evaluate()`/
`dd_corrected_stats()` calls, no `evolve`/`tick`/`save`). Genome still v3
(1d) live. `python3 -m pytest -q` 290/290 (up from 285), no protected file
touched, `tools/edit_bundle_module.py sync --check` confirmed no drift
(these tools aren't part of the bundle). Code change (the ramp-point
override) is real and useful independent of this session's finding --
whichever future session picks up option (1) or (2) above can reuse it.
