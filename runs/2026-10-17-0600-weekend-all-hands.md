# Weekend all-hands — 2026-10-17 ~06:00-07:15 UTC

## Scope

Weekend session, deep focus rather than day-to-day trading. Synced the
repo (49 commits behind, clean fast-forward, no divergence), re-installed
deps, and reviewed `AGENTS.md`'s "Current state" / "Next steps" plus
recent `runs/` to see what the weekday 3-hourly checks have been doing:
mostly real `evolve` batches against the live v3 champion (no promotion,
stagnation counter now past 5000) and routine freshness checks. Nothing
new queued beyond the existing open items, so this session picked up the
most concretely-actionable loose end in item 5 (short selling): the
2026-10-11 `dual-trend` `slope_lookback` sweep's own writeup had flagged
itself as potentially in-sample-mined and explicitly called for an
out-of-sample check before trusting its "40-50 sweet spot" conclusion.
That check had never been run. This session built it and ran it.

## Why this item, not another evolve batch or item 13

Item 13 (holdout-sigma design) already has a full quantified design pass
(2026-10-10) sitting on the owner's desk — nothing left to measure there
without the owner's risk-appetite call. Item 6 (equities/FX) needs a human
to pick a data source first. Running yet another 15-generation `evolve`
batch is exactly what the 3-hourly checks already do around the clock with
no promotion for weeks — a weekend session with more time budget is better
spent closing an open methodological question than adding one more
identical batch to an already-long streak. The dual-trend out-of-sample
validation was concretely scoped, had a clear pass/fail shape, and was
flagged by name as the next step in the most recently active research
thread (item 5), so it was the highest-value use of this slot.

## What was built

New CLI command `evotrader_bundle.py dual-trend-oos` (plain code in
`main()`'s dispatch, not inside the `_SRC` dict that mirrors into
`core/`/`agents/`/`loop/`/`constitution/` — so no `tools/edit_bundle_module.py
sync` was needed; this is CLI glue only, not library code). It re-runs the
2026-10-11 `slope_lookback` sweep (`10, 20, 30, 40, 50, 60, 80`) using the
already-shipped, already-tested `loop.engine.benchmark_trend_break_short`
and `loop.engine.benchmark_dual_trend_short` unchanged, but against
`history-perturb --independent`'s own window construction: fixed-width,
non-overlapping tiles walking backward from "now" over the full ~2017-2026
history per symbol, instead of the champion's own 4 fold/holdout windows
the original sweep was read directly off. `--window-years` controls tile
width (default 2.0, matching `history-perturb --independent`'s own
default), `--lookbacks` overrides the sweep list, `--borrow-bps-per-bar`
matches `short-headroom`'s own flag. Reports a per-window row (buy&hold,
plain trend-break baseline, one column per `slope_lookback`), a mean-return
summary row, and a captured-edge summary restricted to windows where
buy&hold actually lost money (the only windows a short has a positive
theoretical edge to capture).

No new `loop.engine` function, no genome change, no new test file —
nothing here is a pure function that didn't already exist and already have
its own tests; this is argument-parsing and print-formatting glue around
two already-tested benchmarks, consistent with how every other
`short-headroom` variant's CLI dispatch section is (not individually
unit-tested; the underlying `loop.engine.benchmark_*` functions are).
`python3 -m pytest -q` ran 474/474 both before and after this edit, as
expected for a change that touches no library code.

## What was measured

Ran the new command twice, both in the background via
`tools/background_runner.py` (per the standing AGENTS.md item 9 rule —
these runs are a few minutes each, same cost class as `history-perturb
--independent`: one real benchmark replay per window per `slope_lookback`
value, times two signals).

**Run 1 — default 2.0y tiling.** 5 independent windows spanning
2017-08-17 to 2026-10-17. All five were bull markets by buy&hold:
+18.5%, +37.3%, +249.8%, +164.9%, +104.8%. Not one bear window at this
tile width in this universe's real history — the captured-edge metric was
undefined everywhere (`no bear window in this sweep`, printed for all
seven `slope_lookback` values). The only readable signal was mean return
across windows: `lb=20` did best at -3.1% (vs. plain trend-break's
-11.5%); `lb=40`/`50` — the claimed sweet spot — came in at -5.9%/-5.6%,
worse than `lb=20`.

**Run 2 — 1.1333y tiling** (`4.0 * (1 - HOLDOUT_FRAC) / N_FOLDS`, i.e. the
champion's own actual per-fold width, computed directly from
`constitution.HOLDOUT_FRAC`/`N_FOLDS`). 9 windows (the first too short to
backtest, 36 bars). Two were genuinely bearish by buy&hold: window 3
(2018-11-10 to 2019-12-29, -30.2%) and window 6 (2022-04-05 to 2023-05-24,
-53.3%). Captured-edge by `slope_lookback`, averaged over those two bear
windows:

| slope_lookback | captured |
|---|---|
| 10 | **+11.9%** |
| 20 | -20.6% |
| 30 | -26.6% |
| 40 | -6.8% |
| 50 | -8.3% |
| 60 | -19.8% |
| 80 | -38.5% |

Only `lb=10` is positive, and even that is driven entirely by window 3
(+58.6% captured there) while window 6 — the deeper of the two real bear
markets — was a net **loss** at `lb=10` (-34.9% captured). `lb=40`/`50`,
the value the 2026-10-11 in-sample sweep called a sweet spot, are both
negative here: the signal loses money, after real costs, during the
actual bear markets it exists to profit from. Mean return across all 8
valid windows (bull and bear combined) tells the same story: `lb=10` is
the real out-of-sample best performer (-4.1%, vs. plain trend-break's
-8.3%), not `lb=40-50` (-9.6%/-7.7%).

## Reading

Both independent-window runs agree on the direction, even though they
disagree on the exact number: the true out-of-sample-favored region is
**short** lookbacks (10-20), roughly the opposite end of the sweep from
where the in-sample table pointed (40-50). Neither width turned up any
`slope_lookback` value with a reliably positive captured-edge across more
than one real bear window at a time — `lb=10`'s own +11.9% average is a
single-window result wearing an average's clothing (one big win, one real
loss). This is exactly the failure mode the 2026-10-11 writeup warned
about in its own words: "picking 40-50 ... from this table would be
exactly the kind of in-sample parameter mining this whole repo's
fold/holdout discipline exists to catch, not a free pass around it." The
free pass was never taken at the time — the shipped function's default
(`slope_lookback=20`) was deliberately left unchanged rather than reset to
either sweep's favorite — and this session's result is the retroactive
confirmation that leaving it alone was the right call: the in-sample
number doesn't hold up against data it was never tuned on.

This does not reopen or resolve the still-open, still owner-gated
question of whether the Researcher should ever be allowed to open a short
position — if anything, it raises the bar slightly, since the one concrete
parameter-tuning result this item's long combination-search history had
produced (combined → asymmetric → dual-trend → this sweep) turns out not
to generalize. No code path reachable from live trading was touched:
`RiskJudge`/`SuperiorJudge`/`Analyst` are untouched, `.short()` still has
zero live callers, and `live_state.json` was verified byte-identical
(direct diff against a pre-session copy) before and after both diagnostic
runs.

## Verification before commit

- `python3 -m pytest -q`: 474/474, both before (baseline) and after the
  `evotrader_bundle.py` edit.
- `live_state.json`: byte-identical throughout (direct `diff` against a
  copy taken at session start), confirming both `dual-trend-oos` runs
  never wrote state.
- `py_compile` clean on `evotrader_bundle.py` after the edit.
- `AGENTS.md` size after this session's edits: 238,765 bytes — comfortably
  under the 256KB single-read threshold, no archival rotation needed this
  cycle.
- No constitution file touched, no `evotrader.manifest` reseal needed.
- Dashboard not rebuilt: `live_state.json` did not change this session, so
  `index.html` has nothing new to reflect.

## What's next

- The out-of-sample question for item 5's dual-trend signal is now
  answered — don't re-run this exact check again without a reason (a new
  genome, a materially different window scheme, or a proposed fix to the
  signal itself).
- If anyone revisits item 5's "let the Researcher open a short" design
  question, this result is directly relevant evidence against treating
  `dual-trend` at `slope_lookback` 40-50 as a validated starting point —
  the honest state of that sub-thread is "no slope_lookback value tested
  so far survives out-of-sample validation," not "40-50 works, needs
  wiring."
- Items 6 and 13 remain owner decisions, unchanged by this session.
