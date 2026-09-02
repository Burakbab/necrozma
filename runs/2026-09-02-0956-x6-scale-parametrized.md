# 2026-09-02 ~09:47-onward UTC: parametrize the x6-scaling recipe's SCALE constant

## Context

3-hourly self-improvement check. `live_state.json`'s `updated` was
`2026-09-02T00:22:38+00:00` and `runs/2026-09-02-0020-daily-trading.md`
already covers today's daily bar -- nothing new to trade this cycle, as
expected for a 3-hourly firing.

AGENTS.md item 2 (4h-bar shadow evolution) is at option (2b): a fresh
Researcher-driven search on the unpatched `x6` seed (2026-09-02 ~06:56 UTC)
hits the same fold-1 cold-start drawdown wall as every hand-picked patch
since 2026-08-31. That entry's own pointer names two untried sub-options:
(i) more generations/seeds of the same unconstrained search, or (ii)
reconsider the *base recipe itself* -- the x6 bar-scaling approach, or the
`consv1` consult-tightening choice -- rather than searching on top of either.
The entry explicitly recommends (ii) as "the more promising untried half ...
not running more generations of the same search," so this cycle picks up
(ii)'s most literal reading first: is fold 1's cold-start drawdown a property
of the 4h-bar switch itself, or specific to the `SCALE=6` constant every
session since 2026-08-16 has hand-built as a fixed choice?

## What changed

`tools/shadow_4h_x6_seed.py`'s `SCALE = 6` module constant was never
threaded as a parameter -- `build_x6_scaled_seed()`,
`build_consv_trailing_seed()`, and `build_consv_trailing_ramp_seed()` all
hard-multiplied by the module constant. Added a `scale: int = SCALE` keyword
argument to all three builders (default unchanged, so every existing caller
and run note's numbers still mean `scale=6`), plus a `--scale` CLI flag on
both `tools/shadow_4h_x6_seed.py` and `tools/shadow_4h_fold_date_sensitivity.py`
(threaded through that file's `build_genome()` dispatcher too, as an
`Optional[int]` so existing positional/keyword callers are unaffected).

This is infrastructure only -- no behavior change at the default scale. It
exists so a fold-date-sensitivity run can compare `scale=4`/`scale=6`/`scale=8`
against the real fold-based gate and see whether the SCALE=6 choice itself is
implicated in fold 1's repeated near-40%+ drawdown, or whether the drawdown
persists at other bar-scaling ratios too (which would argue the problem is
inherent to trading 4h bars with a 27-symbol multi-position system from cold
start, not a tunable side-effect of the specific x6 multiplier).

8 new tests (4 in `tests/test_shadow_4h_x6_seed.py` covering the default-vs-
explicit-scale-6 equivalence and custom scale on all three builders; 4 in
`tests/test_shadow_4h_fold_date_sensitivity.py` covering `build_genome()`'s
new `scale` kwarg across all three recipes), full suite **332/332** (up from
324). `tools/edit_bundle_module.py sync --check` confirmed no drift (neither
shadow tool is bundled). `live_state.json` untouched, no protected file
touched. Genome still v3 (1d) live, untouched.

## Empirical check: result

Ran `shadow_4h_fold_date_sensitivity.py --recipe x6 --shift 1 --scale {4,6,8}`
against real 4h Binance data (bare `x6` recipe -- no `consv1`/trailing-stop/
ramp genes, so this isolates the scaling multiplier itself, same as every
other bare-seed measurement in this thread):

| scale | gate max_dd | hard_fail | gate margin | fold fitnesses |
|-------|------------:|:---------:|-------------:|-----------------|
| 4     | -56.5%      | YES       | -16.5%       | [-0.314, -5.000, -5.000] |
| 6     | -44.3%      | YES       | -4.3%        | [0.092, 2.560, -0.271] |
| 8     | -48.0%      | YES       | -8.0%        | [-5.000, -5.000, 0.198] |

**All three scales hard-fail `MAX_DD_HARD_FAIL` on the real fold-based gate.
`SCALE=6` is not the cause of fold 1's cold-start drawdown -- it is, if
anything, the least-bad of the three points tried** (smallest margin of
failure, and the only one where more than one fold clears at all). Scale 4
and scale 8 both fail by a wider margin and have two of three folds bottom
out at the fitness floor (-5.000, `dd_corrected_stats()`'s "check failed
completely" sentinel), which scale 6 avoids.

**Reading:** this answers the literal first half of option (2b)(ii) --
adjusting the x6 bar-scaling multiplier is not a route around fold 1's
cold-start drawdown; every scale tested drowns the same way, and the
multiplier this thread already settled on (6) happens to be the best of the
three, not an arbitrary unexamined pick that got lucky/unlucky. Combined
with the 2026-09-02 ~06:56 UTC finding (unconstrained Researcher search on
the unpatched seed also can't route around it), this narrows what's left of
item 2's "reconsider the base recipe" idea to the other named half: the
`consv1` consult-tightening choice (`rsi_buy_below`/`z_buy_below`), not yet
checked the same way (e.g. does varying those two thresholds, independent of
whatever else is layered on top, change fold 1's behavior on its own,
holding scale=6 fixed?). Not run this cycle -- flagged as the next untried
slice under (2b) in AGENTS.md item 2.

One shift, one seed, bare `x6` only (not `consv_trailing`/
`consv_trailing_ramp`) -- not exhaustive, but consistent with every other
finding in this thread: the fold-1 cold-start drawdown looks structural to
trading 4h bars with this 27-symbol multi-position system from a cold
broker start, not an artifact of any single hand-picked constant tried so
far (SCALE, ramp bars/scale, conviction boost, vol cap all checked and none
alone fixes it -- only the `consv1 + trailing_stop + ramp` stack together
does, per the 2026-08-31/09-01 findings).

`live_state.json` untouched throughout. No protected file touched. Genome
still v3 (1d) live, untouched.
