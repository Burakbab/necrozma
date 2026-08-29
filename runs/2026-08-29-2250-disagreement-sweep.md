# disagreement-sweep: the keep_frac sweep, as a real tool this time

2026-08-29, ~22:00-22:50 UTC (3-hourly check)

## Why

Four separate throwaway shadow scripts today (06:00, 10:17, 16:28, 19:12 UTC
entries in AGENTS.md) measured how often raw `ranking_fitness` and
excess-over-benchmark return disagree about which of champion/challenger is
better. The 19:12 UTC session's own "Next" flagged the obvious follow-up: "a
`keep_frac` sweep ... would show whether the disagreement rate scales
smoothly with how favorable the window is, or whether today's result is
itself noisy." Rather than write a fifth one-off sandbox script, this
session formalised the mirrored-`generation()` gating logic those scripts
already used by hand into a tested, reusable function and CLI command.

## What

New `loop.evolve.disagreement_scan(champion, evaluator, researcher,
generations, n_blind, initial_tested, initial_stagnation,
initial_holdout_draws)` — mirrors `EvolutionRun.generation()`'s exact
proposal/gating pipeline (`Researcher.propose`, `Evaluator.evaluate`,
`dd_corrected_stats`, `constitution.accepts`, `Evaluator.holdout_check`,
`constitution.holdout_accepts`, same cumulative-tested-set and
stagnation/boldness bookkeeping) but never calls
`Genome.save()`/`.promote()`/`EvolutionRun._record()` — an in-generation
"would-promote" only swaps the champion in memory for the rest of the scan.
Classifies every candidate's fold-stage verdict, and (for candidates that
clear the fold gate) holdout-stage verdict, as `"agree"` / `"risky"` (raw
fitness favors the challenger, excess return doesn't) / `"conservative"`
(the reverse) — the same terms the 16:28/19:12 UTC run notes already used by
hand. Tested hermetically (`tests/test_disagreement_scan.py`, 3 new tests,
full suite 243 passed up from 240): fold/holdout tallying and direction
classification, the no-proposals stagnation path, the zero-generations
no-op, and an explicit assertion that `Genome.promote`/`Genome.save` are
never called even when a shadow promotion occurs mid-scan.

New CLI `disagreement-sweep [--keep-fracs 1.0,0.90,...] [--generations 15]
[--n-blind 14] [--fresh]` truncates each symbol's loaded history to its
first `keep_frac` of bars (same trick the 19:12 UTC session used by hand)
and runs `disagreement_scan` at each point, seeded from the live champion's
real `researcher_memory` by default (`--fresh` starts blind instead). Smoke
tested first at `keep_frac=1.0, --generations 1` against real data: fold
fitness -1.695 matched the 16:28/10:17 UTC sessions' own reading of today's
window exactly. Then ran the real thing: `--keep-fracs 0.95,0.85
--generations 15` (the default `n_blind=14`), each point seeded from the
same real `researcher_memory` snapshot (224 tested proposals, stagnation 15,
holdout_draws 22 — independent draws, not chained across keep_fracs, same
convention every prior session in this thread used).

## Result

Combining today's five keep_frac points (four from this and earlier
sessions' shadow work, one new tool run each for 0.95/0.85):

| keep_frac | champ fold-fit | fold n | fold dis% | risky | cons | ho n | ho dis% |
|---|---|---|---|---|---|---|---|
| 1.00 (10:17 UTC) | -1.695 | 210 | 66.2% | — | — | 45 | 8.9% |
| 1.00 (16:28 UTC, different seed) | -1.695 | 210 | 63.3% | 118 (88.7%) | 15 (11.3%) | 40 | 15.0% |
| 0.95 (this session) | 0.949 | 210 | 21.0% | 27 | 17 | 25 | 0.0% |
| 0.90 (19:12 UTC) | 1.398 | 210 | 8.6% | 14 (77.8%) | 4 (22.2%) | 4 | 0.0% |
| 0.85 (this session) | 1.263 | 211 | 20.4% | 35 (81.4%) | 8 (18.6%) | 24 | 4.2% |

**The disagreement rate does not scale smoothly with `keep_frac` itself —
it tracks the champion's own fold-aggregate fitness on that window instead,
and against *that* variable the relationship is a clean monotonic
decrease.** Sorted by champion fold-fitness (not by keep_frac): -1.695 ->
66.2%, 0.949 -> 21.0%, 1.263 -> 20.4%, 1.398 -> 8.6%. keep_frac 0.90 happens
to land on an unusually favorable window (champion fold-fit 1.398, the
highest of the five points, higher than the less-truncated 0.95's 0.949) —
that is why the 19:12 UTC session's single 0.90 data point looked like part
of a smooth keep_frac trend when it was really one favorable draw. 0.95 and
0.85 bracket it at 21.0%/20.4% — nearly identical to each other despite a
10-point difference in truncation, and both well above 0.90's 8.6% — which
only makes sense once champion dominance, not truncation depth, is treated
as the driver. The risky-direction skew (raw fitness overstating relative to
excess return more often than the reverse) persists at every point
regardless: 61-89% risky across all five samples that have a direction
breakdown recorded, never in the "conservative" majority.

Holdout-stage (the gate a real promotion is decided at) tells the same
story more starkly: 8.9%/15.0% disagreement on the two windows where the
champion is deeply underwater (-1.695), falling to 0.0-4.2% on all three
windows where it dominates (0.949/1.263/1.398). The one holdout-stage
disagreement at 0.85 (1/24, risky direction) is consistent with, not a
break from, that pattern — a small nonzero rate on an otherwise-strong
window, not evidence the effect reverses.

## What this settles, and doesn't

Sharpens the 19:12 UTC session's own reading rather than replacing it: that
session called the collapse from 63.3%/66.2% to 8.6% "substantially an
as-of-drift artifact... not a fixed flaw in raw fitness" but treated it as
roughly keep_frac-driven. This sweep shows the actual driver is one level
down — champion fold-fitness on the window under test, which correlates
with but is not identical to keep_frac (0.90 is an outlier-favorable window,
not a representative point on a smooth curve). Practically: the disagreement
rate is highest exactly when the champion is already struggling on raw
fitness terms, which is also when a promotion decision matters least in the
sense that the champion is likely to be replaced on raw-fitness grounds
alone regardless of what excess return says — this argues, again, for
patience rather than urgency on the still-open "should the selection metric
be redefined around excess return" question, which remains explicitly the
owner's call, not attempted here.

Five points, two random seeds, one champion (v3) — not a dense sweep, not
tried against a different champion (still blocked on reconstructed old
champions lacking their own real `researcher_memory`), and "champion
fold-fitness predicts disagreement rate" is a pattern from 5 data points,
not a proven law.

## Verified safe

- `md5sum live_state.json` unchanged throughout today's entire thread:
  `bf360fc7f86f6bae2bc46bb6f6dc6026`.
- `disagreement_scan`'s own contract (never calls
  `Genome.save()`/`.promote()`/`EvolutionRun._record()`) verified by an
  explicit test that monkeypatches both to raise if called.
- `python3 -m pytest -q`: 243/243 (up from 240; +3 new tests).
- `tools/edit_bundle_module.py sync --check`: clean (the CLI dispatch lives
  in the bundle's own `main()`, same precedent as
  `promotion-excess-check`/`live-benchmark`; `disagreement_scan` itself
  lives in `loop/evolve.py`, synced into the bundle's `_SRC` normally).
- Today's bar (00:20 UTC) was already processed before this session started;
  no `tick` run, no double-trade risk. No `evolve` run against real state.

## Next

- A denser sweep (e.g. every 0.02-0.05 step) would confirm "champion
  fold-fitness predicts disagreement rate" as a smooth relationship rather
  than 5 points that happen to be consistent with one.
- Still blocked, still worth unblocking eventually: running this against a
  reconstructed old champion (v1/v2) would need synthesizing a
  `researcher_memory` for it, since only the live champion has real
  accumulated search history.
- Still not attempted, still the owner's call: redefining the selection
  metric itself.
