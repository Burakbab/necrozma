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

### Tested (same session, after the commit above): the vol cap doesn't help fold 1 either — and at magnitudes that actually bind, it makes the drawdown worse

The baseline `--shift 1` check (cap=0.0, matching the committed gene's
no-op default) confirmed the expected starting point: `gate max_dd` -34.6%,
`aggregate_fitness` 0.395, fold fitnesses `[-0.040, 2.260, 0.075]` — same
as every prior session's number for this exact point.

First surprise: the 0.3-0.8 cap range this note originally recommended
(picked by analogy to `consult_conservative`'s 1.10 `max_vol` veto) turned
out to be the wrong scale entirely. A direct instrumentation of
`RiskJudge.rule()` against fold 1's own first-120-bars window (scratch
script, not committed) found the *actual* realised-vol distribution of buy
candidates there is 0.033-0.342 (mean 0.188, p90 0.301) — every value in
the originally-recommended range is above the observed maximum, so a cap
there is a guaranteed no-op on this fold regardless of magnitude. Confirmed
directly: cap=0.5 through the real gate reproduces cap=0.0's numbers to 3
decimal places (`gate max_dd` -34.6%, `aggregate_fitness` 0.395 both
runs) — same shape of finding as the conviction-boost gene, but for a
different underlying reason (wrong assumed scale, not "no marginal band").

Swept caps actually inside the observed range instead
(`fold1_vol_cap_sweep.py`, scratch, one continuous fold-1 backtest per
point, not the full walk-forward gate):

| `vol_cap` | fold-1 max_dd | sortino | trades | fitness |
|---:|---:|---:|---:|---:|
| 0.30 (barely inside range) | -34.8% | 2.371 | 558 | 1.272 (~cap=0.0, negligible bite) |
| 0.20 | -34.8% | 2.27 | 556 | 1.224 |
| 0.15 | **-43.5%** | 2.37 | 618 | **-inf (hard-fails)** |
| 0.10 | **-43.8%** | 2.60 | 639 | **-inf (hard-fails)** |
| 0.05 (near-universal shrink) | -35.7% | 2.54 | 543 | 1.437 |

Confirmed on the real gate too (`--shift 1`, `dd_corrected_stats`, not just
the single-fold continuous number above): cap=0.20 gate max_dd -35.4%
(worse than baseline -34.6%, fold-1 fitness 2.260→1.867, aggregate_fitness
0.395→0.332); cap=0.05 gate max_dd -36.0% (also worse, aggregate_fitness
0.395→0.370). **No cap value tested — from 0.05 to 0.5 — ever improves
fold 1's drawdown on either the continuous or the real fold-based gate. At
magnitudes too high to bind it's a no-op (as expected); at magnitudes that
actually shrink real orders (0.05-0.20) the drawdown gets measurably
*worse*, not better**, and at 0.10-0.15 specifically it swings the fold
from passing to hard-failing outright. Not root-caused this session (a
plausible mechanism: shrinking early positions changes portfolio equity's
trajectory, which feeds back into every later bar's `target = base_size_pct
* score * regime_scale` sizing and which symbols later get a slot, so the
actual trade sequence downstream of bar 0-120 isn't just "the same trades,
smaller" — it can genuinely different trades in a 27-symbol, multi-position
system, not obviously for the better).

## Recommendation for the next session

**Option (2a) — a volatility-scaled position cap — is now closed for this
`consv1 + trailing_stop -0.06` seed genome, same as the conviction-boost
option before it, but for a different reason: this lever does bite, and
when it does, it makes fold 1's drawdown worse rather than better, not just
neutral.** The gene stays in the genome (real, tested, no-op-by-default,
GENE_SPACE-registered — a different seed genome or a real `Researcher`
search may still find a magnitude/genome combination where it helps; this
session only tested one genome's one fold). Do not keep hand-tuning
`cold_start_ramp_vol_cap` against this specific genome expecting a
different sign — three magnitudes inside the fold's actual vol range have
now each made things worse, not just failed to help.

**This closes out both halves of the 19:21 UTC entry's option (2a) fork.**
The only next-steps item 2 option left un-tried is **(2b): step back from
patching this `consv1 + trailing_stop -0.06` seed genome further and
reconsider the base recipe** — every lever tried against fold 1's cold
start so far (size ramp alone: boundary-fragile per the 13:16/16:47 UTC
sessions; conviction floor: no marginal band; vol cap: backfires when it
bites) has failed to produce a genome that reliably clears the real gate
across nearby dates. That is a bigger, multi-session task, not a single
3-hourly slice.
