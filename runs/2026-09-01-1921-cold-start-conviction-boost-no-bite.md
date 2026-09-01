# 2026-09-01 19:21 UTC — cold-start conviction-floor lever built and tested: no bite on this genome

3-hourly self-improvement session. `live_state.json` untouched (`updated`
still `2026-09-01T00:22:17+00:00`, today's daily bar already handled by the
00:20 UTC run — nothing to trade this cycle).

## What this session did

The 16:47 UTC session closed off "sweep other `cold_start_ramp_bars`/
`cold_start_ramp_start_scale` grid points" as a dead end: three independent
best-of-day picks for that two-gene size-only ramp each fail most nearby
days on the real fold-based gate. It left two next steps, both bigger than
one session: (1) a structurally different lever on fold 1 — e.g. a stricter
entry threshold during the cold-start window, not just smaller position
size — or (2) step back from patching this `consv1 + trailing_stop -0.06`
seed genome further.

This session built and tried (1).

### Built: `risk_judge.cold_start_ramp_min_conviction_boost`

New gene (default `0.0`, true no-op), wired into `agents/judges.py`'s
`RiskJudge.rule()` alongside the existing size ramp: during the same
`cold_start_ramp_bars` window, adds to `min_conviction` (tapering linearly
back to 0 by `cold_start_ramp_bars`, same shape as the size ramp's own
taper) so a marginal-conviction buy gets vetoed outright instead of just
sized down. Registered in `agents.researcher.GENE_SPACE`
(`(0.0, 0.5, "float")`) for real search, threaded through
`tools/shadow_4h_x6_seed.py`'s `build_consv_trailing_ramp_seed()` (new
`ramp_conviction_boost` kwarg) and `tools/shadow_4h_fold_date_sensitivity.py`
(new `--ramp-conviction-boost` flag). 9 new tests (5 in
`tests/test_cold_start_ramp.py` covering the veto/taper/independence-from-
sizing semantics directly on `RiskJudge`, 2 each in the two shadow-tool test
files). Full suite 303/303, `tools/edit_bundle_module.py sync --check`
clean. **Committed and pushed separately before this note**
(`ba1d2e4`) — the gene itself is safe, tested infrastructure regardless of
what the rest of this note finds.

### Tested: zero measurable effect on fold 1, even at 8x the tried-and-failed default

Ran `shadow_4h_fold_date_sensitivity.py --recipe consv_trailing_ramp --shift 7`
against the 120/0.20 ramp point plus the new boost, at three values:

| `ramp_conviction_boost` | hard-fails / 7 shifts | shift-0 gate max_dd |
|---:|---:|---:|
| 0.0 (baseline, same cutoff) | 6/7 | -34.6% |
| 0.15 | 6/7 | -34.6% |
| 0.40 (near GENE_SPACE max of 0.5) | 6/7 | -34.6% |

All three runs are **byte-identical** across every one of the 7 shifts
(same `aggregate_fitness`, same `gate max_dd` to the decimal, same
per-fold fitness triples). Not a near-miss — the boost has literally no
effect on this genome's backtest at any tested magnitude.

(Side note, not this session's focus: the 6/7 hard-fail rate itself, at
today's ~19:00 UTC data cutoff, is worse than the 13:16 UTC session's 4/7
for the unboosted 120/0.20 point — consistent with the 16:47 UTC entry's
finding that the whole genome family's pass rate has been sliding across
the day, not something this session's boost caused.)

**Why**: instrumented `RiskJudge.rule()` directly (scratch script, not
committed) against fold 1's own backtest window (`start_frac=0.2833,
end_frac=0.5667` — the fold the 01:14 UTC session identified as the
hard-failing one). Of 672 buy candidates considered during the first 120
bars (the ramp window), the conviction distribution is sharply bimodal:
most (mean 0.873) are unanimous three-consult-agreement trades at
0.80-0.96 conviction, comfortably clear of any boosted floor up to 0.5.
The only candidates below 0.70 raw conviction were either (a) already
below the *un-boosted* base `min_conviction` floor of 0.30 (4 `PAXGUSDT`
candidates at bars 81-84, conviction 0.28-0.30 — vetoed with or without
the new gene) or (b) above whatever boosted threshold applied at their
specific bar (the taper drops the boost fast: by bar 30 an 0.40 boost is
already down to ~0.20 added). Diffing the actual filled-order list
(symbol, conviction, quote_amount, bar index) between `boost=0.0` and
`boost=0.4` for the identical fold-1 backtest: **identical order sequence,
every field.** There is no marginal-conviction band this lever could
filter in this genome's actual signal distribution — the fold-1 drawdown
comes from adverse price action on already-high-conviction, unanimous
trades, not from noisy low-conviction entries slipping through.

## Recommendation for the next session

**Do not tune `cold_start_ramp_min_conviction_boost` on this specific
genome expecting a different answer — it's been swept 0 to 80% of its
GENE_SPACE range with a provably identical result each time, for a
mechanistic reason (the signal distribution has no marginal band), not a
magnitude-tuning problem.** The gene stays in the genome (it's a real,
tested, no-op-by-default lever — a different seed genome or a real
`Researcher` search combining it with other genes might still find use for
it), but hand-tuning it further against *this* `consv1 + trailing_stop`
seed's fold 1 is a dead end, same conclusion as the closed size-ramp grid
search.

This leaves next-steps item 2's option (1) tried and empirically closed for
this genome (a conviction-based entry filter doesn't touch the failure
mode), narrowing to two live options: **(2a)** a non-conviction structural
lever — e.g. a volatility-scaled position cap, or restricting which
symbols/regimes can open new cold-start positions at all (the failing
trades are unanimous-agreement and high-conviction; the lever needs to key
on something other than agent conviction) — or **(2b)**, as the 16:47 UTC
entry already flagged, step back from patching this seed genome further
and reconsider the base `consv1 + trailing_stop -0.06` recipe itself.
Neither is a single-session task.
