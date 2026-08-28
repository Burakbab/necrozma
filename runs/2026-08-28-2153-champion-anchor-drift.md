# Champion anchor drift — the fold/holdout comparison baseline isn't fixed either

## Scope

3-hourly check, ~21:53 UTC. Read-only analysis of `live_state.json`'s own
recorded lineage using already-tested library functions
(`loop.evolve.summarize_holdout_pressure`, `constitution.required_margin`).
No backtest run, no market data touched, no code changed,
`live_state.json`/`evotrader.manifest` untouched throughout (verified by
md5sum before/after). Builds directly on today's `guardian-gene-test`,
`guardian-weighted shadow evolve`, and `holdout-margin-audit` sessions (see
"Current state" entries at 09:45/13:00/16:32/18:46 UTC) — same open question
(why does champion v3 keep holding against genuinely fold-superior,
sometimes even holdout-beating, challengers), but this looks at a piece of
the mechanism none of those four sessions checked: is the number a
challenger has to beat actually fixed?

## What was checked

Every prior entry on this topic describes the sealed-holdout comparison as
"the champion's own single noisy holdout draw" or "one historical draw" —
i.e. a fixed number, set once, that `required_margin()`'s growing correction
is added to. That framing comes from `holdout_accepts()`'s docstring ("The
holdout is not re-drawn between runs"). But the *champion's* side of the
comparison is not read from anywhere frozen — `EvolutionRun.generation()`
calls `self.evaluator.holdout_check(champion)` fresh, every generation,
re-backtesting the unchanged champion genome over whatever the current
sealed-holdout window happens to be (the docstring's own words: "a history
that grows by one bar a day"). So the anchor a challenger has to beat is
recomputed on every `evolve()` invocation, not stored once at promotion.

Pulled every real recorded draw against live champion v3 via
`summarize_holdout_pressure(state["lineage"], 3)` (the same function
`holdout-pressure`/`holdout-margin-audit` use) and grouped consecutive draws
by `holdout_champion` value:

| starts at cumulative draw | champion holdout fitness | champion fold-aggregate fitness |
|---|---|---|
| 2 | -1.172 | 1.389 |
| 11 | -0.881 | 1.396 |
| 14 | 0.763 | -1.612 |

Three distinct values for the *same, unchanged* v3 genome, recorded across
its own real reign — not three genomes, not three different search windows
chosen deliberately, just the same fixed genome scored again each time
`evolve()` ran, on whatever the calendar-shifted 4-year window looked like
that day. Max swing between consecutive re-scores: **1.644** on the holdout
fitness scale, **~3.01** on the fold-aggregate fitness scale (1.396 →
-1.612) — both far larger than the typical distance between rejected
challengers and the champion (the -0.9 to +0.6 range the 13:00 UTC session
found across every hand-picked Guardian variant).

## Why this matters

`MULTIPLE_TESTING_SIGMA` (0.08, guards `accepts()`'s fold-aggregate gate)
and `HOLDOUT_SIGMA` (2.0, guards `holdout_accepts()`) were both calibrated
against a *different* noise source: `holdout-noise`'s block-bootstrap
resampling of one fixed realized price path (see "Current state"
2026-08-20/21). That measures "how much would this same score wobble if the
same historical bars were resampled" — it does not, and cannot, measure "how
much does the champion's own recomputed score move as the search/holdout
windows themselves slide forward by one bar a day." This session's numbers
put a first real value on that second source, and at least on this one
champion's reign so far, it is **not small**:

- The fold-aggregate gate's margin at realistic `n_tested_cumulative` counts
  is small (`required_margin(n, 0)` with the default `sigma=0.08`: roughly
  0.1-0.3 for n in the tens-to-hundreds range this account has actually
  seen) — two orders of magnitude smaller than the ~3.0-unit day-to-day
  swing just measured in `champion_fold_fitness` above. If that swing is
  representative rather than a one-off, the fold gate's multiple-testing
  correction is being computed to a precision the anchor itself doesn't
  hold to.
- The holdout gate's margin (`HOLDOUT_SIGMA=2.0`, ~5.0-5.7 at current draw
  counts) is large enough to absorb a 1.6-unit anchor swing on its own — so
  this doesn't change today's headline conclusion (no plausible challenger
  magnitude clears ~5.6 either way). But it does mean the "champion's one
  historical draw" framing in every prior entry on this topic, including
  today's, is not quite accurate: there is no single historical draw being
  defended, there is a moving target being re-measured, and `HOLDOUT_SIGMA`
  was never asked to cover its own movement.

## What this does and doesn't change

Does not change the standing recommendation: this is still a
constitution-amendment-level question (`AMENDMENTS.md` row required),
deserving more scrutiny than a 3-hourly session, not attempted here.

Does sharpen the two directions the 18:46 UTC entry named:

- **(a) "periodically refresh the champion's own holdout score"** is not a
  new mechanism to add — it is *already happening*, silently, every time
  `evolve()` runs, as an unintended side effect of the sliding window. What's
  missing is not the refresh, it's (i) measuring how much noise that refresh
  itself injects (this session's 1.6-3.0-unit swings are a first data point,
  not a calibrated estimate — three plateaus from one champion's reign), and
  (ii) deciding whether `n_draws`/`n_tested_cumulative` should reset, decay,
  or stay fully cumulative when the thing they're being compared against is
  itself moving. The docstring's existing objection to resetting the counter
  ("exactly what a mined holdout would look like from the inside") is about
  the *count*, and still holds; it says nothing about the *anchor* also
  silently moving underneath that count.
- **(b) an absolute/percentile bar** would sidestep the anchor-drift question
  entirely (no champion re-score to drift), which this session's finding is
  a small point in favor of, on top of whatever the 18:46 UTC entry's own
  reasoning already covered.

## Next

Whoever runs the actual design session on `required_margin()`/
`holdout_accepts()` should treat "how much does the champion's own
recomputed fold/holdout score move purely from calendar drift, independent
of any real performance change" as a third input alongside `HOLDOUT_SIGMA`
and `MULTIPLE_TESTING_SIGMA` — right now it has exactly one small,
uncontrolled data point (this session), not a measurement. A `--champion-only`
mode on the existing `history-perturb`/`holdout-noise` machinery (re-score
the same fixed champion genome at several different "as-of" dates without
touching any candidate) would turn this from an anecdote into a real number,
the same way `holdout-noise` did for resampling noise — flagged here as a
concrete, scoped follow-up diagnostic, not attempted this session.

## Verified safe

`live_state.json` and `evotrader.manifest` md5 unchanged throughout
(`0fa0731311baab0508f959f79a01214e` / `0bf3a7d9411ee692d0a9f152a7533803`);
no backtest run, no `evolve`/`tick` call made; only read `live_state.json`
and imported already-tested pure functions. Today's bar (00:20 UTC) was
already processed before this session started — no `tick` run, no
double-trade risk.
