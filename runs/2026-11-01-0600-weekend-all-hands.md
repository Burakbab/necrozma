# Weekend all-hands — 2026-11-01 ~06:00-07:xx UTC

## Scope for this session

Markets don't need daily attention on weekends, so this slot went to one
bigger, finished piece of work rather than another routine `evolve` batch
(six separate 3-hourly checks already ran real evolve generations against
the live v3 champion in the last 24h with no promotion — see "Current
state" in AGENTS.md). The highest-value queued item was the "concretely
scoped next step" the 2026-10-31 weekend all-hands explicitly named and left
undone: an out-of-sample check for `benchmark_breadth_trend_short`'s
`breadth_threshold` sweep, the same discipline already applied to
`dual-trend-oos` (2026-10-17) and `regime-combo-oos` (2026-10-24).

## Why this mattered

AGENTS.md item 5 (short selling) has accumulated a long history of
confirmation signals layered onto `benchmark_trend_break_short`: a
basket-wide regime filter (`regime-conditional`, `combined`, `asymmetric`),
a temporal confirmation (`dual-trend`, slow-SMA slope), and most recently a
cross-sectional confirmation (`breadth-trend`, fraction of the universe also
breaking down). Every one of these has, at some point, been tuned by
sweeping a parameter against the live champion's own 4 fold/holdout windows
and reading off an apparent "sweet spot" — and every time that's been
checked out-of-sample so far (`dual-trend-oos`), the sweet spot reversed
completely: the in-sample-best `slope_lookback` (40-50) turned out to be
roughly the worst region out-of-sample, and the true best region (10-20)
was the one the in-sample sweep had rejected.

`breadth-trend`'s own writeup (2026-10-31) swept `breadth_threshold` ∈
{0.2..0.7} against the champion's 4 windows and found: both bull folds get
worse monotonically as the threshold rises; the one real bear window (fold
3) holds up through 0.5 and then **flips sign sharply at 0.6** (a real gain
at every threshold ≤0.5 becomes a real loss at 0.6-0.7); holdout is best at
0.5. The writeup explicitly flagged this as unchecked in-sample mining and
named the exact next step: build a `breadth-trend-oos` sibling to
`dual-trend-oos` before trusting any threshold choice. That's what this
session built and ran.

## What was built

New CLI command `breadth-trend-oos` in `evotrader_bundle.py` (~160 lines,
modeled line-for-line on the existing `dual-trend-oos`/`regime-combo-oos`
commands — same argument conventions `--window-years`/`--borrow-bps-per-bar`,
new `--thresholds` in place of `--lookbacks`/`--short-regimes`). No new
`loop.engine` function was needed: `benchmark_breadth_trend_short` already
exists (shipped 2026-10-31, 10 tests) and takes no genome at all, so this
command just reuses it, `benchmark_trend_break_short`, and
`benchmark_buy_hold` exactly as `short-headroom --trend-break/--breadth-trend`
already call them, against `history-perturb --independent`'s own
fixed-width, non-overlapping, walk-backward-from-now tiling instead of the
champion's own 4 windows.

Verified before running anything for real: `python3 -m pytest -q` 484/484
baseline, `python3 -m py_compile evotrader_bundle.py`,
`tools/edit_bundle_module.py verify` (round-trip clean — `loop/engine.py`
itself was never touched, only `evotrader_bundle.py`'s CLI dispatch, so
there was nothing to drift). Ran both sweeps for real via
`tools/background_runner.py` (two separate `start`+`wait` pairs, run in
parallel since both are read-only and touch no shared state) rather than
foreground (each takes several minutes to load ~27 symbols of up to 12
years of daily history and then replay three benchmark functions per
window per threshold).

## Results

**2.0y tiling** (5 independent windows, all bull markets — same finding
every prior `-oos` check on this universe has made; there is no 2-year
stretch in the available ~2017-2026 history that nets bearish). Mean return
across windows, by threshold:

| | trend-break | th=0.2 | th=0.3 | th=0.4 | th=0.5 | th=0.6 | th=0.7 |
|---|---|---|---|---|---|---|---|
| mean | -5.4% | -6.5% | -3.1% | -4.5% | **+0.6%** | -8.1% | **+5.9%** |

**1.1333y tiling** (the champion's own per-fold width; 9 windows, 2
genuinely bearish — window 2, 2017-10 to 2018-11, buy&hold -38.8%; window
6, 2022-04 to 2023-06, buy&hold -50.9%, the LUNA/FTX era). Mean return
across the 8 valid windows:

| | trend-break | th=0.2 | th=0.3 | th=0.4 | th=0.5 | th=0.6 | th=0.7 |
|---|---|---|---|---|---|---|---|
| mean | -6.5% | -6.9% | -7.2% | -8.3% | **-1.8%** | -8.6% | **-1.9%** |

Both tilings agree on the ranking: **th=0.5 and th=0.7 clearly and
consistently beat both the unfiltered trend-break baseline and every lower
threshold**, on genuinely different calendar stretches than the original
sweep was read off. This is the first parameter choice anywhere in item 5's
`-oos` history to hold up rather than reverse — `dual-trend-oos` found the
opposite outcome for `slope_lookback`. The original writeup's own pick
("0.4-0.5 is the defensible range") was half right: 0.5 generalizes, 0.4
and everything below it does not (both tilings show 0.2-0.4 are no better
than, or measurably worse than, plain trend-break).

**But the captured-edge metric the original "130% captured, the best of any
variant" headline was built on is mostly noise.** Checked directly,
per-window, rather than trusted as a summary average: in the 1.1333y
tiling's two bear windows, per-threshold capture ratios run
[+219.8%, -102.0%] at th=0.2 down to [+130.9%, -103.7%] at th=0.7. **Window
6 — the one genuinely severe crash in either sweep — is a real loss at
every single threshold tested, including the unfiltered trend-break
baseline itself** (-51.9% vs. buy&hold's -50.9%, essentially a total loss
of the available headroom). Every positive-sounding mean captured-edge
number is coming entirely from window 2's own outsized, amplified ratio
(headroom only 38.8%), the exact same thin-headroom amplification effect
`regime-combo-oos`'s own 2026-10-24 writeup already flagged and warned
against trusting. Mean return, not mean captured-edge, is the reliable
statistic here too.

## Reading

Item 5 now has its first threshold choice with genuine out-of-sample
support (breadth_threshold 0.5, and to a lesser extent 0.7) — a real,
if modest, step forward for a line of work that has mostly produced
reversals and non-dominance results until now. But "a real improvement"
here still means smaller average losses across a mostly-bull real crypto
history, not a signal that would have made money in the one severe crash
either sweep actually contains. No variant of any signal tried across this
item's whole history — regime-conditional, trend-break, dual-trend,
breadth-trend, or any combination of them — has ever actually profited in
a real severe crash; every apparent "capture" number that looked otherwise
turned out, once checked per-window, to be driven by a milder window's
amplified ratio. This sharpens, rather than resolves, the still-open,
still owner-gated question of whether to let the Researcher open a short
at all.

## Other housekeeping this session

`AGENTS.md` had grown to 256,959 bytes after the item 5 writeup was added
(within the margin range every prior rotation in this index has used to
trigger one). Archived the oldest remaining full slice — all eight
2026-10-29 3-hourly-check entries, 341 lines — verbatim to new
`AGENTS_ARCHIVE_2026-10-29.md`. Verified via exact line-range removal (the
removed block diffs byte-for-byte identical against the new archive file's
body) and a post-archive `pytest` pass. Cut the live file to 234,448 bytes
before this session's own additions; it now sits at 237,038 bytes after
writing up the weekend result and this archival action.

## Not attempted this session

- No `evolve` batch — six 3-hourly checks already ran real evolve
  generations against v3 in the prior 24h with no promotion; this slot
  went to the queued diagnostic instead, per this session's own
  "fewer, bigger things, finished properly" mandate.
- Did not act on the breadth_threshold=0.5 finding by changing any genome,
  gene range, or wiring anything into the live trading/evolution path.
  `benchmark_breadth_trend_short` still takes no genome and has zero live
  callers — this remains a read-only diagnostic, same as every other
  benchmark in `loop/engine.py`. The still-open, still owner-gated
  question of whether/how to let the Researcher propose short positions is
  unchanged by this session.
- No further out-of-sample check on `regime-combo-oos`'s own result (the
  combined/asymmetric comparison) was revisited — that question was
  already answered 2026-10-24, this session's scope was specifically
  breadth-trend's missing check.

## Verification summary

- `python3 -m pytest -q`: 484/484, both before any edit and after the
  `evotrader_bundle.py` change.
- `tools/edit_bundle_module.py verify` / `sync --check`: both clean.
- `live_state.json`: untouched throughout (no evolve, no tick, no state
  write of any kind this session) — confirmed by inspection, not just
  assumed.
- `evotrader.manifest`: unchanged (`loop/engine.py` was not touched, and
  it is not a `_PROTECTED` file regardless).
- Dashboard: not rebuilt — no state change to reflect, per Run protocol
  step 5's own condition ("if state changed").
