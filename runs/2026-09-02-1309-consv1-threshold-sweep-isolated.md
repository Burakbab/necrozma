# 2026-09-02 ~12:47-13:09 UTC: consv1 thresholds swept in isolation from trailing_stop

## Context

3-hourly self-improvement check. `live_state.json`'s `updated` was
`2026-09-02T00:22:38+00:00` and `runs/2026-09-02-0020-daily-trading.md`
already covers today's daily bar -- nothing new to trade this cycle.

AGENTS.md item 2 is at option (2b), "reconsider the base recipe itself."
The 09:47-10:10 UTC session ruled out the `SCALE` constant as fold 1's
cause (scale 4/6/8 all hard-fail the real gate) and named the remaining
untried half: the `consv1` consult-tightening thresholds
(`rsi_buy_below`/`z_buy_below`), which every session since 2026-08-31 has
only ever measured *stacked with* a tightened `trailing_stop` (and later
cold-start-ramp genes) -- never checked on their own against the real
fold-based gate, holding `scale=6` fixed.

## What changed

New `tools/consv1_threshold_sweep.py` -- grid search over `rsi_buy_below`
(38.0/30.0/22.0) x `z_buy_below` (-0.8/-1.2/-1.6) on top of the *bare*
`build_x6_scaled_seed()` (default `risk.trailing_stop=-0.15`, no ramp
genes), evaluated with the exact real functions
`EvolutionRun.generation()` calls before `accepts()`'s hard-fail check
(`Evaluator.evaluate()` + `dd_corrected_stats()`), same discipline as
`tools/cold_start_ramp_sweep.py`. The grid's (38.0, -0.8) point is the
untightened no-op baseline (should reproduce the already-known bare `x6`
number as a sanity check); (30.0, -1.2) is the 2026-08-31 22:07 UTC
session's tightened point, here for the first time *without* the
`trailing_stop` tightening it was always previously paired with.

6 new tests (`tests/test_consv1_threshold_sweep.py`): grid coverage/no-dup
checks, a hermetic fake-evaluator test of the hard-fail flagging logic, and
a spy-on-`.child()` test asserting every sweep genome leaves
`risk.trailing_stop` and the cold-start-ramp genes untouched -- the whole
point of the sweep is isolating `consv1` from those other levers. Full
suite **338/338** (up from 332). `tools/edit_bundle_module.py sync --check`
clean (neither this tool nor its test is bundled). `live_state.json`
untouched, no protected file touched. Genome still v3 (1d) live, untouched.

## Empirical check: result

Ran the sweep against real 4h Binance data (4 years, 11-symbol universe,
`scale=6` fixed):

| rsi_buy_below | z_buy_below | agg_fitness | gate max_dd | hard_fail | trades | sortino |
|--------------:|------------:|------------:|------------:|:---------:|-------:|--------:|
| 38.0 (no-op)  | -0.8 (no-op) | -2.450     | -44.3%      | YES       | 1170   | 1.05    |
| 38.0          | -1.2        | -2.450      | -44.3%      | YES       | 1163   | 1.05    |
| 38.0          | -1.6        | -2.500      | -42.6%      | YES       | 1141   | 0.97    |
| 30.0          | -0.8        | -2.565      | -43.9%      | YES       | 1082   | 0.89    |
| 30.0          | -1.2        | -2.565      | -43.9%      | YES       | 1082   | 0.89    |
| 30.0          | -1.6        | -2.565      | -43.9%      | YES       | 1082   | 0.89    |
| 22.0          | -0.8        | -2.565      | -43.9%      | YES       | 1082   | 0.89    |
| 22.0          | -1.2        | -2.565      | -43.9%      | YES       | 1082   | 0.89    |
| 22.0          | -1.6        | -2.565      | -43.9%      | YES       | 1082   | 0.89    |

**All 9 grid points hard-fail `MAX_DD_HARD_FAIL` -- `consv1` alone, without
`trailing_stop`, does not clear fold 1's gate at any threshold tried, and
does not even meaningfully move the gate `max_dd` (range -42.6% to -44.3%
across the whole grid, vs. the -44.3% untightened baseline).** Two
sub-findings worth keeping:

1. **`rsi_buy_below` dominates `z_buy_below` once tight enough.** Every
   `rsi_buy_below <= 30.0` row is bit-for-bit identical regardless of
   `z_buy_below` (-2.565 fitness, -43.9% gate max_dd, 1082 trades, 0.89
   sortino, same three fold max_dds) -- once the RSI leg is doing enough
   vetoing on its own, tightening the z-score leg further has zero
   additional effect on which bars get bought. Only at the untightened
   `rsi_buy_below=38.0` does `z_buy_below` still move anything (1170 ->
   1141 trades, -44.3% -> -42.6% gate max_dd from -0.8 to -1.6).
2. **Tightening `consv1` alone makes `aggregate_fitness` slightly worse,
   not better** (-2.450 at baseline -> -2.565 at any `rsi_buy_below<=30`
   point) -- fewer trades (1170 -> 1082) without a compensating drawdown
   improvement large enough to help fitness, unlike the trailing-stop-paired
   version.

**Reading:** this settles item 2's last-named untried slice under (2b).
The 2026-08-31 22:07 UTC "consv1 + trailing_stop is strongly super-additive"
finding is now more precisely attributable: `trailing_stop` is the lever
carrying that synergy, not `consv1` -- `consv1` alone (any threshold tried)
barely moves the real gate's `max_dd` at all and cannot clear it without
`trailing_stop` doing the actual work. Combined with the 09:47-10:10 UTC
`SCALE` result and the 06:46-07:15 UTC unconstrained-search result, **all
three named single-lever alternatives under "reconsider the base recipe"
(bar-scaling multiplier, unconstrained search, consult-tightening alone)
have now been checked and none routes around fold 1 on its own** -- only
the full `consv1 + trailing_stop + ramp` stack does, consistent with every
finding in this thread since 2026-08-31. **Recommend closing out option
(2b) as exhausted for single-lever alternatives**; the remaining open
choice under item 2 is whether to accept the full stack as the fold-1 fix
and move toward a real (non-shadow) promotion attempt for this genome
family, or treat 4h-bar shadow evolution as not yet worth promoting and
redirect effort elsewhere (e.g. the parked short-selling Phase 1 item, or
item 4's LLM-backed consults work). Not decided here -- flagged for the
next session/owner call.

One 4-year window, one universe snapshot, bare `consv1`-only recipe (no
ramp) -- not exhaustive, but the "rsi dominates" and "fitness slightly
worse, not better" patterns are internally consistent (verified via the
real gene path, `Genome.child()` patches, against real 4h Binance data, not
a monkeypatch or proxy). `live_state.json` untouched throughout. No
protected file touched. Genome still v3 (1d) live, untouched.
