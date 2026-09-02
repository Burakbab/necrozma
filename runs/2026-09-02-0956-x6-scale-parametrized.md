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

## Empirical check (in progress / result below)

Kicked off `shadow_4h_fold_date_sensitivity.py --recipe x6 --shift 1
--scale {4,6,8}` against real 4h Binance data (fresh cache in this cloud
sandbox, so the scale=6 baseline run alone needs to fetch all 27 universe
symbols from scratch -- slow, still running when this note was first
written). Result to follow in this same file once all three scales have run,
or in a follow-up run note if a later session picks this back up first.
