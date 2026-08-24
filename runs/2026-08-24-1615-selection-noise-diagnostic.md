# Selection noise: a first number on the "harder, unquantified question" — 2026-08-24 ~16:15 UTC

Scheduled 3-hourly check. Today's daily bar was already handled by the 00:20
UTC run (`live_state.json` `updated` 2026-08-24T00:22:01+00:00, genome
version still 3, md5 `0b628cf88674a6de938b4a806f33cf70` unchanged throughout
this session) — nothing new to trade this cycle. `review-hard-calls` still 0
pending.

Picked up the open question the 2026-08-21 `holdout-sigma-recalibration` run
explicitly left unchased (see AGENTS.md item 2, that entry's closing note):
"`HOLDOUT_SIGMA` measures realized-return-path resampling noise only, not the
added noise from a candidate arriving pre-selected by correlated folds — a
harder, unquantified question, not picked up this run." Every fold-scheme/
windowing/capping variant tried since then was independently declared
exhausted (2026-08-21 `fold-cap-mean-winsorize`); this is a different
question from that whole line — not "does windowing fix the aggregate," but
"is the fold-aggregate winner's sealed-holdout score itself optimistically
biased relative to a candidate that wasn't selected."

## Method

One-off script (same precedent as `runs/2026-08-24-0049-seed-holdout-noise-diagnostic.md`
— not a new CLI command, this doesn't need to be permanent yet). Imported
`core.live.LiveAccount` (read-only `.load()`), `core.market`,
`loop.evolve.Evaluator`, `agents.researcher.Researcher`/`diagnose`,
`loop.engine.run_backtest` directly from the real unflattened packages —
exactly the objects `EvolutionRun.generation()` itself composes, just driven
by hand so a random non-winning candidate could be pulled from the same
batch for comparison (`generation()` only ever evaluates the sealed holdout
for its top-3 fold-ranked candidates, never a deliberately-average one).

Six independent draws against real live champion v3 and real market data.
Each draw: run `Researcher.propose(champion, diag, n_blind=10, exclude=...)`,
evaluate every proposal's fold-aggregate fitness via `Evaluator.evaluate`
(identical to `generation()`'s own scoring step), take the fold-aggregate
winner (what a real promotion decision would carry to the holdout gate) and
one candidate chosen uniformly at random from the rest of the same batch,
then run **both** through `Evaluator.holdout_check` — something
`generation()` never does for a non-finalist. Compare each candidate's own
(fold fitness − holdout fitness) gap: if selection adds optimism bias beyond
ordinary resampling noise, the winner's gap should run systematically larger
than the random pick's.

**Caught and fixed a real methodology bug before trusting any number.** First
attempt (`exclude=set()` fresh every draw) gave the *identical* winner
(fold=1.556, holdout=−1.251) in all 6 draws — `Researcher.propose`'s
`from_diagnosis()`/`structural()` proposals are deterministic given a fixed
champion+diagnosis (only `perturb()` is seeded), so with no exclusion the
same non-random candidate wins every time regardless of draw index; only the
random comparison candidate was ever actually independent. Fixed by
accumulating `exclude` across draws — mirroring `EvolutionRun.tested`'s real
cumulative-per-champion behavior — so each draw searches genuinely fresh
ground. Rerun confirmed the fix: winners varied per draw (fold fitness 1.556,
1.252, 1.202, 1.302, 1.426, 1.202).

## Result: directionally consistent, not yet significant at n=6

| draw | n candidates | winner fold | winner holdout | winner gap | random fold | random holdout | random gap |
|---|---|---|---|---|---|---|---|
| 0 | 21 | 1.556 | −1.251 | +2.806 | −1.360 | −0.156 | −1.203 |
| 1 | 10 | 1.252 | −0.286 | +1.538 | 0.112 | −2.662 | +2.774 |
| 2 | 10 | 1.202 | −0.950 | +2.151 | 1.177 | −0.084 | +1.261 |
| 3 | 10 | 1.302 | −1.398 | +2.701 | 0.055 | −1.141 | +1.196 |
| 4 | 10 | 1.426 | −1.735 | +3.161 | 1.011 | 0.089 | +0.921 |
| 5 | 10 | 1.202 | 0.528 | +0.673 | 0.391 | −0.603 | +0.993 |

Winner gap: mean **+2.172**, std 0.928, n=6. Random gap: mean **+0.990**, std
1.274, n=6. The fold-selected winner's fold-to-holdout drop is larger than
the randomly-picked contender's in 4 of 6 draws (all but draws 1 and 5), and
larger on average by +1.18. A paired comparison on the 6 per-draw
differences gives t≈1.55 — directionally consistent with a winner's-curse
style selection effect, but not significant at this sample size (would need
roughly t≈2.57 at 5 df for a conventional 95% read). `champ_fit` (v3's own
fold-aggregate fitness against the full search region) was 1.245 in every
draw, as expected — same champion, same data, no randomness in that
computation.

**Reading**: this is the first real number on the selection-noise question,
not a settled answer. It points the same direction `HOLDOUT_SIGMA`'s own
docstring worried about — a fold-selected candidate's holdout score looks
worse, on average, than a candidate that merely happened to exist in the same
batch — but 6 draws is a small sample against std ≈0.9-1.3 gaps, and this
used one fixed champion (v3) and one fixed n_blind (10). Not attempted here:
more draws to sharpen the significance, a second champion (v1/v2, one-line
`--also-version`-style change if this becomes a permanent diagnostic), or
translating a confirmed effect into an actual `HOLDOUT_SIGMA`-style
correction (that would be a constitution change needing its own
`AMENDMENTS.md` argument, well beyond what a first measurement earns).

## Verified safe

- `git status --short` clean before and after (script lives in the session
  scratchpad, not the repo; only `state/cache/` — gitignored — was touched by
  the real market-data pulls and backtests).
- `live_state.json` md5 unchanged throughout (`0b628cf88674a6de938b4a806f33cf70`).
- Full test suite: 235 passed (no code changed this session, ran as a
  baseline sanity check).
- `review-hard-calls` still 0 pending. No genome promotion anywhere real, so
  no README Status staleness.
- Total diagnostic compute: ~9 minutes wall time for the corrected 6-draw
  run (plus ~2 min for the first, bugged attempt) — well inside this
  session's budget, cheaper than most 4h-shadow-evolution generations from
  earlier in this project's history.

No push notification sent — a read-only research finding (directionally
suggestive, not conclusive) with zero effect on live trading behavior, same
threshold every prior diagnostic-only 3-hourly session in this history has
used.
