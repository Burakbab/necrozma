# 4h shadow, second independent seed: still zero promotions post-dd-corrected-gate — 2026-08-31 00:49-02:39 UTC

Direct follow-up to the 2026-08-30 23:05 UTC run note's "What's next for item 2",
follow-up 1: "a longer or differently-seeded x6-scaled 4h run to see whether *any*
genome can clear the dd-corrected gate post-2026-08-22." That session found zero
promotions across 8 generations at the default `Researcher(seed=7)` — every prior
4h-shadow session (2026-08-16 through -19) had used that same default seed, so it
was an open question whether the finding was seed-specific.

Same isolation discipline as every prior 4h-shadow session: fresh scratch dir
containing only copies of `evotrader_bundle.py` + `evotrader.manifest`, no
`live_state.json` anywhere near it (`Genome.champion()` falls back to the
hand-built seed). Same x6-scaled seed recipe (`trend_fast/slow`, `rsi_len`
untouched — wasn't in the original scale list, kept — `vol_short/long`,
`breakout_len`, `z_len`, `regime_ma`, `volume_len`, `max_bars_held`,
`min_bars_held`, all x6, `bar_interval` -> `"4h"`). The one deliberate change:
`EvolutionRun(data, seed=9001)` instead of the default `seed=7`. 14 generations
(vs. the prior session's 8, time budget allowed more this cycle), `n_blind=6`.
Standalone script (`run_4h_diffseed.py`, not committed — ephemeral). Verified
after: real repo `git status` clean, `live_state.json` unchanged (matches
committed version, no diff), genome still v3 (1d) untouched. `python3 -m
pytest -q` re-run this session (see below).

## Result: zero promotions again, same qualitative shape

Champion (the x6-scaled seed) never moved: fitness pinned at **-4.296** the
entire 14 generations (4413 trades, win 69%, stops 5%, halts 5 on the search
folds; sealed-holdout fitness -1.787). Every generation's top-3 fold-aggregate
candidates were checked against the dd-corrected gate and, when that passed,
the sealed holdout — same two-stage funnel as the 23:05 UTC run. 42 rejections
total (3 per generation x 14):

- **31/42 (74%) failed the dd-corrected hard gate** (too few trades, too
  short, or continuous-replay drawdown > 40%) — a much higher share than the
  23:05 UTC run's 6/15 (40%).
- **11/42 (26%) failed the sealed holdout** — lower share than the 23:05 UTC
  run's 9/15 (60%).

So the two seeds land on the *same outcome* (zero promotions) via a
*different mechanism split* — seed=7's candidates more often cleared the hard
gate and died at holdout; seed=9001's candidates more often died at the hard
gate itself. Read together this is stronger evidence than either run alone:
the "post-fix, this x6-scaled seed can't clear the promotion funnel" finding
isn't an artifact of one `Researcher` seed's particular proposal sequence —
it replicates with an unrelated seed and looks like two different failure
modes of the same underlying problem (the scaled seed's search-fold behavior
and its sealed-holdout behavior are both fragile, not just one of the two).

One data point worth flagging: generation 5 found a candidate at fold-fitness
**1.310** (a real, large improvement over the champion's -4.296) that still
failed holdout — challenger holdout fitness -0.976 against a required bar of
champion (-1.787) + multiple-testing margin (2.965 at 3 cumulative holdout
draws) = 1.178. This is the sharpest single illustration in either 4h-shadow
run of the fold/holdout regime mismatch this whole thread has documented on
the live 1d path: a fold-aggregate result that looks like a clean win can
still be nowhere close at the sealed holdout once the multiple-testing margin
is counted honestly.

## What this changes for item 2

The open question from the 23:05 UTC note — "whether *any* genome can still
clear the dd-corrected gate at all" — now has two independent negative data
points instead of one. Recommend treating "the x6-scaled seed, as currently
constructed, cannot clear the post-fix promotion funnel in a handful of
generations regardless of Researcher seed" as reasonably well-supported, and
sharpening the open question rather than re-running more seeds of the same
seed genome: is the x6-scaled seed itself structurally too aggressive
(4413 trades over the search window, halts 5, a champion fitness of -4.296
never seen on any real live 1d champion) for this gate to ever clear from,
or would a *retuned* (not just scaled) 4h starting point behave differently?
That's a different, larger experiment (hand-tuning or a longer blind search
from an already-workable point) than "run the same scaled seed again with a
new seed" — not attempted here on a time-budget call after ~110 minutes of
evolution.

The apples-to-apples 4h holdout-noise measurement flagged by the 23:05 UTC
note (a genuinely 4h-competitive genome's holdout noise, vs. this run's and
that one's never-promoted seeds) is still unmeasured and still blocked on the
same prerequisite: finding a genome that promotes at all under this gate.

Nothing here touched `live_state.json`, promoted anything live, or changed
`researcher_memory` — purely shadow/offline compute per the standing rule for
this item.
