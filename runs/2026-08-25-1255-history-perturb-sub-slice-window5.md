# `history-perturb --sub-slice`: characterizing window 5's failure

**3-hourly self-improvement check, ~12:55 UTC.**

## Why

The 09:56 UTC `history-perturb --independent` run found champion v3 hard-failing
specifically the newest independent 2-year window (window 5, ~2024-08 to
~2026-08) while beating benchmark in the other four (three by a wide margin).
That run's own "Next" section named two untried follow-ups: `regime` on that
exact span, or a sub-slice check on whether the failure is spread evenly
across the whole 2 years or concentrated in a sub-period. This does the
sub-slice check — more directly informative than `regime` alone, since it
measures the genome's own fitness/excess-return per sub-period, not just the
market's shape.

## What shipped

`history-perturb` gained `--sub-slice N [--sub-slice-window I]`, usable only
together with `--independent` (reuses its already-loaded full history and
computed non-overlapping window list — no new data loading). Splits window
`I` (1-indexed, defaults to the most recent/last window — the one under
investigation) into `N` equal contiguous sub-windows and runs one real
`run_backtest` per sub-window. Same guarantees as every diagnostic in this
family: read-only, never touches `live_state.json` or the champion.

## Result (champion v3, live; window 5, split into 4 six-month sub-windows)

Re-ran `--independent` first (window boundaries shift a few hours' worth of
days between sessions since every window ends "now" — window 4 flipped from
beat_bench `True`/+0.8% at 09:56 UTC to `False`/-8.0% now, a boundary-noise
effect, not a new finding). Window 5 still hard-fails (-inf, maxDD -44.0%),
consistent with the 09:56 UTC result.

| sub | start | end | fitness | return | sharpe | maxDD | trades | excess ret | beats benchmark |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | 2024-08-25 | 2025-02-23 | 4.080 | +55.0% | 2.68 | -21.9% | 103 | -5.8% | False |
| 2 | 2025-02-23 | 2025-08-25 | 1.501 | +10.5% | 0.89 | -16.7% | 77 | -23.7% | False |
| 3 | 2025-08-25 | 2026-02-23 | -1.200 | -9.1% | -0.82 | -24.3% | 143 | +33.2% | True |
| 4 | 2026-02-23 | 2026-08-25 | -1.109 | -8.5% | -0.62 | -25.2% | 100 | -16.3% | False |

4/4 finite-fitness, beats benchmark in only 1/4 sub-windows.

**Reading**: the failure is not spread evenly — it's a clean front/back
split. The first half (sub 1-2) is fitness-positive, sub 1 dramatically so
(4.080, the best fitness of *any* window or sub-window measured in this
whole thread, though it still trails a stronger benchmark melt-up). The
second half (sub 3-4) is fitness-negative on both absolute and (mostly)
relative terms. More importantly: **no individual 6-month sub-window comes
close to the 40% hard-fail drawdown threshold** (worst is sub 4's -25.2%),
yet the full continuous 2-year window's own max_dd is -44.0% — over the
gate. That gap is the same *shape* as the already-documented
`fold-dd-blindspot` mechanism (a true continuous drawdown spanning a window
boundary is invisible to any one independently-reset backtest's local
max_dd) — here surfaced by a single continuous run exceeding what any of its
own sub-slices show locally, rather than by merging independent folds. Not
proven mechanistically identical (would need the actual NAV path, not
attempted here), but the pattern fits: cumulative growth peaks around the
sub1/sub2 boundary (+55%, then +10.5% more) and a real decline runs through
sub3/sub4 — a continuous peak-to-trough draw that likely straddles the
sub-window split, so no single sub-window's own reset-at-zero max_dd catches
the full depth.

This reframes the open question again: it's not "window 5 is uniformly
bad," it's "there's a real drawdown starting sometime around
early-to-mid-2025 that a full continuous replay measures at -44% but that no
6-month slice, viewed independently, reaches — worth locating precisely
(a finer sub-slice, or a direct NAV/drawdown timeseries plot) if this thread
continues."

## Verified safe

- Full suite: 235 passed (`pytest tests/`, 135.67s), matches known baseline.
  No new pure function added (composes already-tested `run_backtest` and the
  already-loaded `--independent` window list), so no new test file — same
  precedent as every other perturbation diagnostic in this family.
- `git status --short` clean before this commit (only `evotrader_bundle.py`
  touched).
- `live_state.json` md5 unchanged throughout: `f7590581b893d3866e00e28c87fe1c02`.
- `evotrader.manifest` md5 unchanged: `0bf3a7d9411ee692d0a9f152a7533803`.
- Constitution verified `8b74865634b1db07` unchanged (printed at every
  command invocation).
- Today's bar already processed by the 00:20 UTC daily run before this
  session started (`live_state.json`'s `updated` timestamp is
  `2026-08-25T00:22:01+00:00`); `tick` not run this session, no
  double-trade.
- `review-hard-calls`: still 0 pending (unchanged from prior session).
- No genome promotion — no README `## Status` update needed.

## Next, if this thread stays worth pursuing

Locate the continuous drawdown more precisely — either a direct NAV/drawdown
timeseries over window 5 (would need a small extension to expose
`run_backtest`'s internal equity curve, not currently returned), or a finer
`--sub-slice` (e.g. 8 sub-windows of ~3 months) to narrow down which
boundary the true peak-to-trough straddles. Also untried: whether this same
"continuous exceeds any sub-slice" gap shows up in windows 1-4 too (they all
pass, so it's less urgent, but would confirm or rule out that this is a
generic property of continuous vs. sub-sliced backtesting rather than
something specific to window 5).
