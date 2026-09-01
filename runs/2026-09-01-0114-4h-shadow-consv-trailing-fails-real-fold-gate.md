# 4h shadow: the 22:07 UTC "clears MAX_DD_HARD_FAIL" genome fails the real fold-based gate — cold-start fold artifact, not a data-window difference — 2026-09-01 00:50-01:15 UTC

Direct follow-up to the 2026-08-31 22:07 UTC session's own recommendation: seed a
fresh 4h shadow `EvolutionRun` from its `consv1 + trailing_stop -0.06` genome
(`tools/shadow_4h_x6_seed.py`'s new `build_consv_trailing_seed()`, committed this
session) and check whether it survives fold-aggregate acceptance and the sealed
holdout as a champion in its own right.

## Answer: no — and the reason is a genuine fold-restart artifact, not the
data-window/reproducibility issues this thread has hit before

**The gate a real promotion decision would actually read reports -44.1% max_dd**
(`dd_corrected_stats()`, the exact function `EvolutionRun.generation()` calls
before `accepts()`'s hard-fail check) — still failing `MAX_DD_HARD_FAIL` (40%),
contradicting the 22:07 UTC session's headline "-32.7% max_dd, first variant to
clear the gate outright" for the *same genome*.

Ruled out first: a data-window discrepancy (this thread's most common failure
mode — see the 07:05/10:02 UTC sessions' baseline-mismatch saga). Checked
directly: a continuous, unbroken backtest over the exact same span the fold
gate covers (`[0.0, 0.85]` of the 4-year universe, i.e. excluding the sealed
holdout) reproduces **-32.7% max_dd, matching the full-history number exactly**
— so the 22:07 UTC session's number is real and reproducible, not noise or a
construction bug.

The actual cause: **`Evaluator.evaluate()`'s three walk-forward folds are each
backtested independently from a cold start** (no open positions, full cash,
empty indicator lookback), and the middle fold — `[0.283, 0.567]` of the
4-year span, roughly year 2 of 4 — **hard-fails on its own: -44.1% max_dd,
fitness `-inf`** (sortino a striking 3.12 *within* that fold — a sharp, fast
V-shaped move, not a slow bleed):

| fold window | max_dd | sortino | trades | fold fitness |
|---|---|---|---|---|
| `[0.00, 0.283]` | -30.5% | 0.06 | 351 | -0.152 |
| `[0.283, 0.567]` | **-44.1%** | 3.12 | 636 | **-inf** (rank-floored -5.0) |
| `[0.567, 0.850]` | -26.6% | 0.39 | 491 | 0.199 |

Merged/gate stats take the worst fold's max_dd (-44.1%) — worse than the same
span's own continuous replay (-32.7%). This is the **opposite direction** of
the 2026-08-22 `fold-dd-blindspot` fix `dd_corrected_stats()` was built to
catch (that one worried a *continuous* view could hide a drawdown a *fold-local*
view misses by spanning a boundary invisible to either fold alone). Here a
fold-local cold start is *worse* than the continuous run over the identical
span — plausibly because the continuous run enters that period already
positioned/de-risked from fold 1's trading, cushioning the equity curve in a
way a from-scratch restart can't. `dd_corrected_stats()` correctly takes
`min()` of the two either way, so the gate is not fooled by either direction —
but it means **the 22:07 UTC session's single continuous full-history replay
was never going to reveal this**: cold-start risk at fold boundaries only
shows up once you actually run the fold split the real pipeline uses.

## What this changes for item 2

**The 22:07 UTC session's "first variant to clear the DD gate" claim does not
survive contact with the real promotion pipeline.** Its own full-history
`run_backtest()` metric was accurate and reproducible; the gap is that metric
never runs the fold split at all. Fold-aggregate fitness for this genome as a
would-be champion: **-2.481** (driven almost entirely by the one hard-failed
fold), holdout fitness -0.270 — a genuinely worse profile than the
"-0.001 full-history fitness" headline suggested.

Also ran one real generation of evolution (`EvolutionRun.generation()`, 24
researcher proposals, fixed seed 9001) treating this genome as champion: found
several proposals with much better fold-aggregate fitness (best 0.361,
tightening `max_position_pct`/`exit_trend_below`, and a `conviction_scale`
tweak at 0.360) — real improvement over -2.481 — but **every candidate that
reached the sealed holdout gate failed it** (holdout challenger fitness 0.655
vs. required champion + margin 2.965 after 3 cumulative draws; the champion's
own holdout fitness -0.270 is negative, so a large margin is easy to clear in
absolute terms but the multiple-testing-corrected bar is not). Champion held.

**Recommend for a future session**: this specific genome (x6-scaled seed +
`consv1` + `trailing_stop -0.06`) is a dead end as a promotion candidate — its
apparent drawdown improvement is a full-history-replay artifact that the real
fold gate exposes. Any future attempt to improve on the x6-scaled 4h seed's
drawdown should be checked against the fold-based gate (`Evaluator.evaluate()`
+ `dd_corrected_stats()`), not a single continuous backtest, before being
called a candidate worth promoting — a continuous-only measurement on this
seed family has now twice needed a fold-based check to reveal its real
profile (the 2026-08-22 blind-spot fix being the first). The middle-fold
cold-start failure mode found here (a strategy that's fine once seasoned but
dangerous fresh) is itself a new, fold-length-scale-specific finding that a
future session could chase further (e.g. does a longer warmup or a smaller
initial position size in the first N bars of a fold fix it?) if this seed
family is revisited.

## Method / provenance

Committed this session: `tools/shadow_4h_x6_seed.py`'s `build_consv_trailing_seed()`
(+ 3 new tests, `tests/test_shadow_4h_x6_seed.py`, full suite 255/255) —
reproduces the 22:07 UTC session's exact recipe from one place instead of
re-derived prose, per this thread's established discipline. Everything else
this session was read-only scratch scripts (not committed, per the same
discipline) using `core.market`/`loop.evolve.Evaluator`/`EvolutionRun`
directly: `Evaluator.evaluate()`, `dd_corrected_stats()`, `holdout_check()`,
and one real `EvolutionRun.generation()` call with `seed=9001`. `generation()`
does call `Genome.promote()` internally on any accepted candidate, but none
was accepted this run, and even when it is, that only writes to the
gitignored `state/genomes/` directory — never `live_state.json`. Confirmed
`git status` clean and `live_state.json` md5 unchanged
(`1b5e230bb4e7440ed8fd7778425f8ea9`) throughout, genome still v3 (1d) live.
`python3 -m pytest -q` 255/255 confirmed both before and after this session's
harness commit (the code change itself, not this experiment, is what those
tests cover).
