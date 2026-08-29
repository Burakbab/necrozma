# 3-hourly check, 2026-08-29 ~00:56 UTC — `history-perturb --champion-only`

## What this is

The 2026-08-28 21:53 UTC "champion anchor drift" Current-state entry found the
same, unchanged live champion v3 scoring three different sealed-holdout
fitness values across its reign (-1.172, -0.881, 0.763 on the holdout scale),
purely from `evolve()`'s `HOLDOUT_FRAC` split recomputing as the
4y-ending-"now" history grows by one bar a day. That entry flagged a concrete,
scoped follow-up: "a `--champion-only` mode on `history-perturb`/
`holdout-noise` that re-scores one fixed genome at several as-of dates, to
turn this session's one-off 3-point observation into a real calibrated
number." This session built that.

## What shipped

New `history-perturb --champion-only N [--as-of-step-days D]` mode (default
`D=14`). Unlike every other `history-perturb` mode (`--independent`,
`--boundary-shift`, etc.), which tile *fixed-width* windows, this replicates
the sealed holdout's own definition: "the newest `HOLDOUT_FRAC` of however
much history exists." For `N` as-of dates `D` days apart walking back from
"now," it loads history generously (12y, same as `--independent`), truncates
every symbol's frame to `index <= as_of`, and runs
`run_backtest(genome, data, 1 - HOLDOUT_FRAC, 1.0)` on the truncated data —
exactly the split `Evaluator.holdout_check()` computes inside `evolve()`,
just at controlled points instead of whatever real `evolve()` calls happened
to log. Reports the fitness range/spread/mean/std across as-of dates next to
`MULTIPLE_TESTING_SIGMA`/`HOLDOUT_SIGMA`, mirroring the comparison
`holdout-noise` already makes for resampling noise — this measures the noise
source that diagnostic's own docstring says it can't see ("one fixed price
path; it can't see window drift"). Mutually exclusive with `--independent`
(different window scheme, checked and rejected with a clear message).
Supports `--also-version N` like every other mode. No new pure function, no
constitution or engine change — this is CLI-only, same as `--independent`/
`--boundary-shift` before it, so (per that precedent) not mirrored in
`run_from_files.py` (which only mirrors commands already ported there per
item 7's notes; `history-perturb`/`holdout-noise` never were).

Verified: `python3 -m pytest -q` — 240/240 passed (no regressions, no new
tests needed since no new pure function was added). `md5sum live_state.json
evotrader.manifest` unchanged (`bf360fc7f86f6bae2bc46bb6f6dc6026` /
`0bf3a7d9411ee692d0a9f152a7533803`) across every manual run of the new
command, including with `--also-version`. `tools/edit_bundle_module.py sync
--check` clean (this command lives entirely in the bundle's own CLI dispatch,
not in any `_SRC`-managed module, so there is nothing to sync). Today's bar
(00:20 UTC) was already processed before this session started (confirmed via
`live_state.json`'s `updated` timestamp and `runs/2026-08-29-0020-daily-trading.md`
existing) — no `tick` run.

## Finding: a real, denser calibration of the champion-anchor-drift number

`--champion-only 10 --as-of-step-days 21` against live champion v3 (10 as-of
points spanning ~189 days back from today):

```
   as-of   as-of date   bars  holdout start  fitness    return  sharpe   maxDD  trades  excess ret beat bench
       0   2026-08-29    494     2025-04-22    1.167    41.2%    0.84  -29.3%     373      -9.4%      False
       1   2026-08-08    491     2025-04-04     -inf   -13.8%   -0.11  -47.3%     387     -20.1%      False
       2   2026-07-18    488     2025-03-17     -inf    -8.9%    0.02  -46.4%     389     -23.8%      False
       3   2026-06-27    485     2025-02-27     -inf   -12.3%   -0.07  -44.5%     422      -4.5%      False
       4   2026-06-06    482     2025-02-09   -0.102    -0.7%    0.18  -37.9%     403      10.3%       True
       5   2026-05-16    479     2025-01-22   -0.824   -27.1%   -0.48  -30.4%     380     -13.1%      False
       6   2026-04-25    476     2025-01-04   -0.408   -15.8%   -0.17  -28.8%     400      18.1%       True
       7   2026-04-04    472     2024-12-18    0.319     6.5%    0.32  -28.2%     411      42.0%       True
       8   2026-03-14    469     2024-11-30    0.259    10.6%    0.40  -34.8%     400      52.6%       True
       9   2026-02-21    466     2024-11-12    0.632    30.5%    0.70  -37.7%     384      37.0%       True
```

7/10 finite (3 hit the maxDD>40% hard gate outright), range [-0.824, 1.167],
**spread 1.991, mean 0.149, empirical std 0.613**. That std is **7.66x
`MULTIPLE_TESTING_SIGMA` (0.08)** — confirming the fold-aggregate margin has
essentially no defense against this noise source, consistent with the
2026-08-28 finding — but only **0.31x `HOLDOUT_SIGMA` (2.0)**, i.e. the
sealed-holdout margin as currently calibrated comfortably covers this
specific as-of-drift noise on its own.

**Important caveat, not resolved here**: `HOLDOUT_SIGMA` was calibrated
2026-08-21 from `holdout-noise`'s block-bootstrap *resampling* noise on one
fixed price path (v3 measured ~2.04 there). This session's as-of-drift std
(0.613) is a **different, independent noise source** — the same underlying
price path, but the window itself sliding — not a component `holdout-noise`
could see (its own docstring says so) and not obviously already included in
the 2.04 figure. Whether the two should be combined (e.g. added in
quadrature, since they plausibly represent independent perturbations) or are
already correlated enough that 2.04 implicitly covers both is an open
statistical question, not answered by this run. If they *are* independent
and should combine, `sqrt(2.04^2 + 0.613^2) ≈ 2.13` — a modest ~4% increase
over the current `HOLDOUT_SIGMA`, not the kind of gap that would flip a real
promotion decision on its own, but worth someone checking the math before
concluding it's negligible.

## What this does and doesn't change

Read-only, confirms and sharpens rather than resolves the still-open,
constitution-amendment-level design question from 2026-08-28: whether to (a)
periodically refresh the champion's own holdout score, or (b) move to an
absolute/percentile holdout bar instead of the additive margin. This session
gives that question a denser, controlled number instead of 3 uncontrolled
real data points, but the decision itself is unchanged and still deserves
more scrutiny than a 3-hourly session.

## Next steps

- Someone should check whether as-of-drift noise (this session) and
  resampling noise (`holdout-noise`, 2026-08-21) are independent enough to
  combine, and if so, whether `HOLDOUT_SIGMA` should be recalibrated —
  before proposing any change, since it's a constitution amendment either
  way.
- `--champion-only` could be run with a longer span / different
  `--as-of-step-days` to see if the spread grows, shrinks, or plateaus with
  more history — not attempted here (10 points/189 days was chosen as a
  first calibration run, not because it's known to be enough).
