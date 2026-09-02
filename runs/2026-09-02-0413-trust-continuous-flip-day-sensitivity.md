# 2026-09-02 ~03:47-04:13 UTC (3-hourly check): the 01:12 UTC flip doesn't hold across nearby days

## Context

Daily bar already handled at 00:20 UTC (`runs/2026-09-02-0020-daily-trading.md`,
`live_state.json` `updated` timestamp matches) -- nothing to trade this cycle.
Used the slot to follow up on the 01:12 UTC entry's own explicit next step:

> the concrete next step is checking whether today's flip holds across the
> `--shift`-day walk `fold-date-sensitivity` already does, before treating it
> as settled.

The 01:12 UTC session found that `consv_trailing`'s pre-ramp fold-1 hard-fail
(the finding that started the whole cold-start-ramp gene thread three days
ago) flips under the two-sided `dd_trust_continuous_stats` view: -43.8%
one-sided (hard-fail) vs -32.7% two-sided (clears). That was a single
snapshot in time, and this exact genome family has a documented history of
single-snapshot findings not holding up (the 08:08 UTC ramp-genes sweep's
"best point" flipped by 10:27 UTC the same day; three independent "best
point" picks each later failed most nearby days -- 16:47 UTC).

## What was built

New `tools/shadow_4h_fold_date_sensitivity_trust_check.py` (7 new tests in
`tests/test_shadow_4h_fold_date_sensitivity_trust_check.py`, full suite
322/322) -- combines the two diagnostics that existed separately:
`shadow_4h_fold_date_sensitivity.py`'s multi-day "as-of" walk and
`shadow_4h_trust_continuous_check.py`'s two-sided `dd_trust_continuous_stats`
correction. At every shift it now reports both the one-sided (real gate) and
two-sided (diagnostic-only) `max_dd` and whether the shift is a "flip"
(one-sided fails, two-sided clears), "both fail" (real risk, confirmed
independent of fold rebasing), or "neither fails". Pure composition, reuses
`build_genome`/`slice_window` from the existing tool and
`dd_corrected_stats`/`dd_trust_continuous_stats` from `loop.evolve` --
no engine, constitution, or gene change. Read-only: never touches
`live_state.json`, never calls `evolve`/`tick`/`save`.
`tools/edit_bundle_module.py sync --check` confirmed no drift (new
`tools/`/`tests/` files only).

## Result: the flip is itself day-sensitive, not settled

Ran `consv_trailing` (the recipe that flipped) across the same 7-day walk
`fold-date-sensitivity` already uses:

```
shift  as-of        one-sided   two-sided   one_fail  two_fail
0      2026-09-02    -43.8%      -32.7%       YES      no    <-- FLIP
1      2026-09-01    -35.3%      -32.7%       no       no
2      2026-08-31    -35.5%      -32.7%       no       no
3      2026-08-30    -38.0%      -32.7%       no       no
4      2026-08-29    -46.8%      -42.9%       YES      YES   (real risk both ways)
5      2026-08-28    -34.6%      -32.7%       no       no
6      2026-08-27    -44.7%      -32.7%       YES      no    <-- FLIP
```

(exact tool output: 2/7 flip, 1/7 fail under both views, 4/7 clear under
both.) **Shift 4 (2026-08-29) hard-fails under both the one-sided and the
two-sided view (-46.8%/-42.9%)** -- on that day the drawdown is real risk,
not a fold-rebasing artifact. Shifts 0 and 6 flip the same way 01:12 UTC's
snapshot did; shifts 1, 2, 3, 5 don't even hard-fail one-sided in the first
place (consistent with the boundary fragility this genome family already has
documented, independent of the two-sided question).

**Conclusion: the 01:12 UTC finding does not generalize.** It correctly
described that one day's snapshot, but "the fold-1 drawdown is partly an
artifact" is not a stable property of this genome across nearby run dates --
one of seven days shows real risk under both corrections. This is the same
"best-point/best-snapshot doesn't hold nearby" pattern this thread has now
found three separate times (grid-point instability 16:47 UTC, boundary
generation-vs-sweep flip 10:27 UTC, and now this). **Recommend against
treating `dd_trust_continuous_stats` as settling the fold-1 question one way
or the other for this genome family** -- it doesn't consistently show
overstatement, and doesn't consistently show real risk either; it varies by
day the same way the raw one-sided number does.

## What this does and doesn't change

Does not touch the still-open "Next steps" item 2 options: (2a) non-conviction
structural levers are closed (conviction floor, vol cap both tried and
failed/backfired); (2b) stepping back from this seed genome and reconsidering
the base recipe is still the only untried option, and this entry doesn't
change that -- it only closes off treating the fold-rebasing-artifact angle as
a shortcut around (2b). `dd_trust_continuous_stats()` stays diagnostic-only,
not wired into `accepts()` -- same explicit owner-decision framing as before.
No engine or constitution change. `live_state.json` untouched, no protected
file touched. Genome still v3 (1d) live, untouched.
