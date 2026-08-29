# Candidate-level fitness-vs-excess-return check — 15-generation shadow search

2026-08-29, ~09:45-10:20 UTC (3-hourly check)

## Why

The 06:00 UTC weekend all-hands mechanistically identified that sealed-holdout
fitness is dominated by a challenger's own absolute return, not by
excess-over-benchmark (Pearson(fitness, own return) 0.96-0.99, Pearson(fitness,
excess_return) weak or negative for 2 of 3 real champions). The 06:59 UTC
`promotion-excess-check` then checked that against real history: on a
same-basis replay, raw fitness and excess return never actually disagreed on
either of the account's two real promotions (v1->v2, v2->v3) — reassuring,
but only two data points, and both are cases where a promotion *did* happen.
Today's 09:00 UTC daily discussion flagged the evidence base as "still thin"
and explicitly left open whether disagreement shows up among the much larger
population of candidates the search actually generates and rejects, not just
the rare ones that get promoted.

This session ran that check: real search against the live champion, every
candidate's raw-fitness verdict compared against its excess-return verdict at
both the fold-aggregate and sealed-holdout stage, not just the promoted ones.

## What

Standalone script (`candidate_excess_shadow.py`), not committed — same
sandbox-only discipline as every prior shadow-evolve session (2026-08-16
4h-shadow runs, 2026-08-28 guardian-weighted-shadow-evolve): this composes
fresh backtests via real search, unlike the cheap lineage-reading diagnostics
(`holdout-pressure`, `promotion-excess-check`) that get committed as CLI
subcommands, so it stays a sandbox script per that same precedent.

15 generations, `n_blind=14` (CLI default), seeded from the live champion v3
and its real `researcher_memory` (224 already-tested proposals, stagnation
15, cumulative holdout_draws 22 — the real bar, not an artificially reset
one, same choice the guardian-weighted session made). Composes only
already-tested functions exactly as `EvolutionRun.generation()` does
(`Researcher.propose`, `diagnose`, `Evaluator.evaluate`, `Evaluator.
holdout_check`, `dd_corrected_stats`, `constitution.accepts`/
`holdout_accepts`) — no new pure function, no engine/constitution change.

One deliberate methodological difference from `generation()`: every
fold-aggregate candidate this generation (not just the top-3 gate-tested
ones) has its `edge.excess_return` compared against the champion's, and every
candidate that reaches the sealed holdout (whether it ultimately passes or
not) has its holdout-stage excess return compared too — `generation()` itself
only ever persists edge data for an *accepted* candidate, so this required
composing the same calls directly rather than calling `generation()` and
reading its return value.

**Safer than the guardian-weighted precedent, not just as safe**: that session
used `EvolutionRun` directly, which touches gitignored `state/genomes/`/
`state/lineage.jsonl` on disk. This script never calls `Genome.save()`,
`.promote()`, or `EvolutionRun.run()` at all — the entire 15-generation loop
carries the current shadow-champion `Genome` object in memory (reassigning a
local variable on a shadow promotion, never writing a file), so it touches
*nothing* on disk, not even a gitignored path. `live_state.json` is opened
read-only once (plain `json.load`, no `LiveAccount.load`/`.save()` anywhere
in the script).

## Result

Champion held at v3 through all 15 generations (no shadow promotion) — same
qualitative shape every non-4h shadow-evolve session against this champion
has found. ~80s/generation on 1d bars, matching the guardian-weighted
session's timing, ~21 min total, well inside a 3-hourly slot.

**Fold-aggregate stage: 210 candidates compared, 139 disagreements (66.2%).**
Raw fitness and excess return disagree on which side (challenger vs
champion) wins far more often than not. Read this next to the weekend
entry's mechanism, not as a standalone number: this generation's replay uses
*today's* fold window, where the champion's own fold-aggregate fitness is
deeply negative (-1.695, a materially less favorable window than the
promotion-time one) — with the champion that far underwater on raw fitness,
almost any candidate with unremarkable absolute performance looks like a
fitness winner, while excess return (a comparison against the same
benchmark, much more compressed across genomes on one fixed window per the
weekend entry's finding) moves far less. High disagreement at this stage is
consistent with, and further evidence for, the weekend entry's mechanism —
it does not independently establish a new one. (Per-candidate disagreement
*direction* — which side each metric favored — wasn't captured, only the
disagree/agree count; a natural follow-up if this number gets revisited.)

**Sealed-holdout stage: 45 candidates compared (every candidate that cleared
the fold-aggregate gate this run), 4 disagreements (8.9%).** This is the
sharper number — the first time this account has seen the two criteria
actually disagree on *any* candidate at the gate that matters for a real
promotion, versus 0/2 on the two real historical promotions. All 4 cases
share the same shape: the challenger's raw holdout fitness clearly beat the
champion's (0.503 baseline vs 0.521-1.070), but its holdout excess return
was marginally *below* the champion's own 23.12% (22.02%-23.03%, all within
~0.1-1.1 percentage points) — fitness says challenger wins, excess return
says it's a near-tie leaning champion. None of the 4 were actually promoted
(`holdout_accepts()`'s multiple-testing margin rejected all of them on raw
fitness terms alone, same "raw beat, margin rejected" pattern the
2026-08-28 `holdout-margin-audit` thread already quantified) — so this
doesn't change any real decision, but it is a real, measured instance of
the two criteria disagreeing on a candidate that reached the gate a real
promotion is decided at, which the 06:59 UTC check never found because it
only had two actual promotions to look at.

## What this settles, and doesn't

Sharpens, not settles, the weekend entry's open question. It shows
disagreement between the two criteria is not a hypothetical at the gate
that matters (unlike the reassuring 0/2 on real promotions) — but every
disagreement found here was a near-tie on excess return specifically
(differences under 1.1pp), not a case where a genuinely excess-return-losing
candidate would have out-scored the champion on fitness by a wide margin.
Whether that near-tie pattern holds up over more generations/champions, or
whether a more lopsided disagreement exists somewhere in the space, is not
answered by one 15-generation run. The larger question — whether the
selection metric itself should be redefined — remains exactly where the
weekend entry and today's daily discussion left it: an owner-level design
decision, not attempted here.

## Verified safe

- No file written anywhere by the shadow script: `git status --short` clean
  throughout, no `state/` directory exists after the run (checked directly —
  it was never created, unlike the guardian-weighted session which did write
  gitignored files there).
- `md5sum live_state.json evotrader.manifest` unchanged throughout:
  `bf360fc7f86f6bae2bc46bb6f6dc6026` / `0bf3a7d9411ee692d0a9f152a7533803`.
- `python3 -m pytest -q` — 240/240 passed (no repo code touched this
  session, only a sandbox-only script outside the repo).
- Today's bar (00:20 UTC) was already processed before this session started
  (`runs/2026-08-29-0020-daily-trading.md` exists); no `tick` run, no
  double-trade risk. No `evolve` run against the real state either — only
  the sandboxed shadow script, which never calls `acct.save()` or
  `Genome.save()`.

## Next

- If this line of inquiry continues: capture per-candidate disagreement
  *direction* at the fold stage (not just the count) to see whether it's
  systematically one-sided (as the weekend entry's mechanism would predict)
  or genuinely mixed.
- A run replayed against a *favorable* fold window (where the champion's own
  fold-aggregate fitness isn't deeply negative from calendar drift) would
  isolate how much of the 66.2% fold-stage number is the window-drift
  artifact named above versus a more fundamental property.
- Still not attempted, still the owner's call: redefining the selection
  metric itself.
