# A shadow fold-date-sensitivity tool, and the systematic answer: the ramp genome fails the real gate more often than it passes

**3-hourly check, ~12:48-13:16 UTC.** Today's daily bar was already handled
by the 00:20 UTC run (`live_state.json` `updated` 00:22:17 UTC) — no trading
this cycle.

Direct follow-up to the 10:27 UTC session's own flagged next step (AGENTS.md
item 2): *"before trusting any single point-in-time clears/fails
MAX_DD_HARD_FAIL measurement on this genome family again, ... build a shadow
equivalent of the existing fold-date-sensitivity CLI command ... so this can
be checked systematically instead of by two accidental same-day snapshots
landing on opposite sides."*

## What was built

`tools/shadow_4h_fold_date_sensitivity.py`: the bundled `fold-date-sensitivity`
command's mechanism (`Evaluator(data, n_folds=N_FOLDS).evaluate(genome)` at
several "as-of" dates, each with its own trailing 4-year window), generalized
to take a shadow genome builder (`--recipe x6|consv_trailing|consv_trailing_ramp`,
reusing `tools/shadow_4h_x6_seed.py`'s builders) instead of only the live 1d
champion. Adds one thing the bundled command doesn't need: at every shift it
also runs `dd_corrected_stats()` — the exact correction
`EvolutionRun.generation()` applies before `accepts()`'s hard-fail check reads
`max_dd` — and reports whether that genome would actually clear
`MAX_DD_HARD_FAIL` as champion that day, not just its `aggregate_fitness`.
11 new hermetic tests for the pure helpers (window slicing, gate-margin,
recipe selection, shift summary) — no network. Full suite 285/285 (up from
274). Committed before running it. Not wired into any scheduled command, the
bundle, or `run_from_files.py`; read-only with respect to the live account.

## Result: the 120/0.20 ramp genome hard-fails the real gate on 4 of 7 days

Ran `--recipe consv_trailing_ramp --shift 7` (one week of "as-of" dates,
trailing 4y window each, ~707s total — about 100s/shift, so a full sweep
fits comfortably inside a 3-hourly slot):

```
   shift        as-of window start  aggregate_fitness   gate max_dd  hard_fail
       0   2026-09-01   2022-09-01             -2.460       -44.0%        YES
       1   2026-08-31   2022-08-31              0.308       -34.4%        no
       2   2026-08-30   2022-08-30              0.377       -34.9%        no
       3   2026-08-29   2022-08-29              0.099       -42.9%        YES
       4   2026-08-28   2022-08-28              0.161       -35.5%        no
       5   2026-08-27   2022-08-27             -2.456       -43.4%        YES
       6   2026-08-26   2022-08-26             -2.451       -43.4%        YES
```

**4/7 shifts hard-fail `MAX_DD_HARD_FAIL` outright.** Of the 3 that clear, the
best margin is +5.6 points (aggregate_fitness range among clearing shifts:
[0.161, 0.377]) — well inside the swing a single bar's fold-boundary shift can
cause, exactly as the 10:27 UTC session suspected but hadn't measured
systematically. This settles the open question that session left as (a) build
this tool or (b) treat "<10 points of margin" as not a real pass: the answer
turns out to be starker than either framing — this isn't a genome sitting
just above a fragile line, it's a genome that's on the wrong side of the line
more often than not across the last week of possible run dates. The 08:08 UTC
grid search's "120/0.20 beats 120/0.10" finding is likely still true as a
*relative* comparison (both points are being evaluated against the same
fold-boundary noise), but "120/0.20 clears `MAX_DD_HARD_FAIL`" should not be
read as an established fact about this genome — it's closer to a coin flip
across nearby as-of dates.

## What this means for item 2

**Recommend against treating `cold_start_ramp_bars=120,
cold_start_ramp_start_scale=0.20` (or the 120/0.10 predecessor — untested
here, but built from the same fragile fold 1) as a settled fix for the
01:14 UTC session's cold-start-fold dead end.** The ramp mechanism itself is
real and correctly wired (still a genuine no-op at defaults, still tested,
still moves fold 1's max_dd in the right direction on average) — but at this
specific point in gene-space the fix is not reliably clearing the gate it
was built to clear. Two honest next steps, neither attempted this session:
(a) sweep `--recipe consv_trailing_ramp` at other grid points from the
08:08 UTC search (e.g. a larger `ramp_bars` or `start_scale`) through this
same 7-shift tool to see if a more conservative point on the ramp buys a
wider margin, or (b) accept that this seed genome (`consv1 + trailing_stop
-0.06`) has a structurally fragile fold 1 that no cold-start ramp alone
reliably fixes, and look for a different lever. The tool now exists to check
either path in ~12 minutes instead of by accident.

`live_state.json` untouched (md5 `1b5e230bb4e7440ed8fd7778425f8ea9`,
unchanged), constitution checksum unchanged, no protected file touched,
`tools/edit_bundle_module.py sync --check` not needed (no `core/`/`agents/`/
`loop/`/`constitution/` module edited). Genome still v3 (1d) live, untouched.
