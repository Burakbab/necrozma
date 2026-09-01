# Real grid search over cold_start_ramp_bars/start_scale — finds a strictly better point, and a non-monotonic landscape

**3-hourly check, ~06:47-08:08 UTC.** Direct follow-up to the 04:18 UTC
session's own flagged next step (AGENTS.md item 2): the two new
`risk_judge` genes (`cold_start_ramp_bars`/`cold_start_ramp_start_scale`)
were shipped with a hand-picked 120/0.10 from "a small sweep" that was never
recorded, and the run note explicitly suggested "a real search over just
those two genes... might find a materially better point."

## What was built

`tools/cold_start_ramp_sweep.py`: a grid search over both genes on top of
`build_consv_trailing_seed()` (the `consv1 + trailing_stop -0.06` 4h-shadow
genome), scored with the exact real functions `EvolutionRun.generation()`
calls before `accepts()`'s hard-fail check — `Evaluator.evaluate()` (the real
3-fold walk-forward split) plus `dd_corrected_stats()` (the fold-vs-continuous
worse-of max_dd fix) — not a continuous-replay proxy. Grid: `ramp_bars in
{0, 60, 90, 120, 150, 180, 240}` x `start_scale in {1.0, 0.30, 0.20, 0.10,
0.05, 0.0}`, with the `ramp_bars=0` no-op collapsed to one point (37 total,
skipping duplicate no-ops). 6 new hermetic tests
(`tests/test_cold_start_ramp_sweep.py`) cover the grid dedup and hard-fail
flagging logic with a stubbed evaluator — no network, no real backtest.
Committed separately (`f7aa62b`) before the sweep itself finished, since the
tool and its tests are a complete, tested contribution independent of what
the sweep would find.

## Result: 37-point sweep, ~65 min wall clock (real 4h Binance data, 4 years, 8 symbols)

35/37 points clear `MAX_DD_HARD_FAIL`; full table in the tool's own output
(not reproduced here — re-run `python3 tools/cold_start_ramp_sweep.py` for
the live numbers). Headline findings:

**1. The hand-picked 120/0.10 point is beaten outright by 120/0.20** — same
`ramp_bars`, one notch less aggressive on `start_scale`:

| | gate max_dd | aggregate_fitness | gate fitness | holdout fitness | beats benchmark |
|---|---|---|---|---|---|
| baseline (no ramp) | -35.3% | 0.400 | 0.695 | -0.265 | True |
| 120/0.10 (04:18 UTC pick) | -34.6% | 0.368 | 0.732 | -0.290 | True |
| **120/0.20 (sweep best)** | **-34.6%** | **0.454** | **0.791** | -0.287 | True |

Same drawdown-gate outcome, strictly higher fold-aggregate fitness (the
actual selection metric `generation()` ranks candidates by) and gate fitness,
holdout essentially a wash. Verified with a separate direct script
(`Evaluator.evaluate()` + `dd_corrected_stats()` + `evaluator.holdout_check()`
on all three genomes back to back, same data). **Updated
`tools/shadow_4h_x6_seed.py`'s `COLD_START_RAMP_PATCH`/
`build_consv_trailing_ramp_seed()` to 120/0.20**, since this builder exists
specifically so future sessions don't re-derive a stale hand pick — updated
its one dependent test (`test_consv_trailing_ramp_seed_applies_cold_start_ramp_on_top_of_consv_trailing`)
to match.

**2. The landscape is not smooth — two grid points hard-fail outright next to
points that clear comfortably.** `ramp_bars=60, start_scale=0.05` and
`ramp_bars=240, start_scale=0.10` both land at roughly -43% to -44% max_dd
(hard-fail) while every neighboring grid point in each direction clears at
~-34% to -35%. This isn't a boundary effect (both failing points sit in the
interior of the grid, not at an edge) and isn't obviously explained by
`ramp_bars` or `start_scale` alone — no simple monotonic story fits both. Not
investigated further this session (would need per-bar fold-2 trade logs to
diagnose, a bigger dig than this sweep's scope). **Flagging this for whoever
next runs a real `Researcher`-driven search over these two genes**: the
fold-2 cold-start dynamics this ramp interacts with are genuinely jagged in
this two-gene space, not a smooth bowl a hill-climb can safely assume —
mutation-based search should expect occasional sharp failures near otherwise-
good points, not treat one nearby failure as ruling out the whole
neighborhood.

**3. A reproducibility note, not fully resolved.** This session's own
`aggregate_fitness` for the exact 120/0.10 genome (0.368, reproduced twice —
once via a standalone timing script, once via the sweep itself) does not
match the 04:18 UTC run note's reported 0.467 for what should be the
identical genome and data (that note's `gate max_dd` of -34.6% *does* match
exactly, only `aggregate_fitness` disagrees). Not chased down this session —
flagging in the same spirit as the 2026-08-31 07:05-vs-10:02 UTC baseline
mismatch (AGENTS.md item 2): treat any single hand-run `aggregate_fitness`
number from a prior run note with some caution, and prefer numbers from a
committed, re-runnable script (this sweep, or `shadow_4h_x6_seed.py`) over
one transcribed into prose. The three-way comparison in the table above (all
measured together, in one script, this session) is internally consistent
regardless of which absolute number is "right."

## What this doesn't yet establish

Not run through a full `EvolutionRun.generation()` as champion (the 04:18 UTC
session already did that for 120/0.10 and found it stable against 34 blind
proposals — a fresh `generation()` run against the new 120/0.20 point would
be the natural next check, not attempted here). Still no established prior
champion for this seed lineage to compare against for a real promotion
decision. The sweep only covers this one seed genome
(`consv1 + trailing_stop -0.06`) — whether the same 120/0.20 point holds for
other trailing-stop values on the same seed, or for a genuinely different
seed, is untested.

`live_state.json` untouched throughout, `python3 -m pytest -q` 268/268
(the 6 sweep tests were already counted in this session's earlier commit;
this run only updated two existing test/genome values, not test count), no
protected file touched, `tools/edit_bundle_module.py sync --check` confirmed
no drift. Genome still v3 (1d) live, untouched.
