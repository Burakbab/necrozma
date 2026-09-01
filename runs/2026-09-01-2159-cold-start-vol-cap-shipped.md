# 2026-09-01 ~21:46-22:00 UTC — volatility-scaled cold-start position cap shipped

3-hourly self-improvement session. `live_state.json` untouched (`updated`
still `2026-09-01T00:22:17+00:00`; today's daily bar was already handled by
the 00:20 UTC run, and the 20:30 UTC daily-evaluation session confirmed tick
18 ran cleanly — nothing to trade this cycle).

## What this session did

The 19:21 UTC session closed off the cold-start conviction-floor lever
(swept 0.0-0.40, byte-identical results at every value — fold 1's failing
trades are already unanimous, high-conviction entries, so a conviction
filter has no marginal band to catch) and narrowed "Next steps" item 2 to
two options: (2a) a non-conviction structural lever, e.g. a
volatility-scaled position cap, or (2b) step back from patching this
`consv1 + trailing_stop -0.06` seed genome further.

This session built (2a).

### Built: `risk_judge.cold_start_ramp_vol_cap`

New gene (default `0.0`, true no-op), wired into `agents/judges.py`'s
`RiskJudge.rule()` alongside the existing size ramp and conviction boost:
during the same `cold_start_ramp_bars` window, a buy's size is capped by the
traded symbol's own `Features.vol` (annualised realised vol) — a symbol
whose vol exceeds the cap gets its buy shrunk by `cap / vol`, composing
multiplicatively with the existing size ramp. No new data plumbing needed:
`Features.vol` is already computed by the Analyst every bar for every
symbol, unlike the removed correlation-penalty gene which needed a new
`rets_by_symbol` field on `Briefing`.

Checked first whether this axis is even meaningfully different from what's
already in the codebase: `ConservativeConsult` and `ModerateConsult` already
veto high-vol symbols outright (`max_vol` 1.10 / 1.60 respectively), but
`RiskyConsult` (momentum/breakout) has no vol filter at all — a volatile
breakout can reach the Risk Judge at full conviction today. So a cold-start
vol cap below ~1.10 can bind specifically on `RiskyConsult`-driven entries
in a way nothing else in the system currently does, unlike the conviction
boost which found no band to act on.

Registered in `agents.researcher.GENE_SPACE` (`(0.0, 3.0, "float")`) for
real search. Threaded through both shadow tools:
`tools/shadow_4h_x6_seed.py`'s `build_consv_trailing_ramp_seed()` gained a
`ramp_vol_cap` kwarg / `--ramp-vol-cap` CLI flag, and
`tools/shadow_4h_fold_date_sensitivity.py` gained a matching
`--ramp-vol-cap` override, mirroring exactly how `ramp_conviction_boost` was
threaded through both tools in the prior session.

12 new tests: 10 in `tests/test_cold_start_ramp.py` (no-op default,
shrinks a volatile symbol's order by the expected `cap/vol` factor, leaves
a calm symbol untouched, fails safe when the symbol has no `Features` entry
at all, only active inside the ramp window — not before or after, composes
multiplicatively with the size ramp, and does not fire if
`cold_start_ramp_bars` itself is 0 even with a cap set), 1 each in the two
shadow-tool test files (override + default-noop). Full suite **309/309**
(up from 303). `tools/edit_bundle_module.py sync` run and confirmed no
drift (caught real drift first — the initial edits only touched the real
`.py` files, and the embedded bundle test suite failed 8 tests including my
own new ones with wrong numbers, because `tests/conftest.py` imports
`evotrader_bundle` and its custom meta-path finder serves the *embedded*,
stale copy of `core.genome`/`agents.judges`/`agents.researcher` to every
test unless the bundle is re-synced first — a good reminder of exactly the
failure mode `tools/edit_bundle_module.py` exists to prevent).

`live_state.json` untouched, no protected file touched, genome still v3
(1d) live, untouched.

### Not finished this session: the empirical check against fold 1

Started the same check the 19:21 UTC session used for the conviction-boost
gene (`shadow_4h_fold_date_sensitivity.py --recipe consv_trailing_ramp
--ramp-vol-cap <value> --shift 7`) but it was still running (network-bound
market-data fetch, not stuck — low CPU time, process alive) when this
session's time budget ran out. **This entry ships tested, no-op-by-default
infrastructure only — it is not yet a verdict on whether the lever actually
helps fold 1's drawdown.** Same posture the conviction-boost gene shipped
under in the prior session (committed before its own empirical result was
in hand).

## Recommendation for the next session

Run the fold-1 check this session didn't finish:
`shadow_4h_fold_date_sensitivity.py --recipe consv_trailing_ramp
--ramp-vol-cap <value> --shift 7` at a few candidate values, something in
the 0.3-0.8 range (below `consult_conservative`'s own 1.10 `max_vol` veto,
so the cap can actually bind on `RiskyConsult`-driven buys that have no vol
filter of their own — a cap above ~1.10-1.60 would rarely trigger since
most surviving candidates are already below that from the consults' own
vetoes). If it measurably improves fold 1's hard-fail rate on the real
gate, that's real progress on item 2. If it's another byte-identical no-op
like the conviction boost, that closes option (2a) too and leaves only
(2b) — stepping back from this seed genome — as the live option, per the
19:21 UTC entry.
