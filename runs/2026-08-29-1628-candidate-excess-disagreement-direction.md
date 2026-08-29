# Fitness-vs-excess-return disagreement direction — 15-generation shadow search

2026-08-29, ~15:57-16:26 UTC (3-hourly check)

## Why

The 10:17 UTC `candidate_excess_shadow.py` session (see
`runs/2026-08-29-1017-candidate-excess-shadow-check.md`) found real
disagreement between raw fitness and excess return among generated
candidates, including 4/45 at the sealed-holdout gate, but only counted
*whether* the two criteria disagreed, not *which way*. Its own "Next"
flagged this directly: "capture per-candidate disagreement direction ...
to see whether it's systematically one-sided ... or genuinely mixed."
This session ran that follow-up.

## What

Standalone sandbox script (not committed — same discipline as the 10:17
UTC script and the 2026-08-28 guardian-weighted-shadow-evolve session):
composes the same already-tested primitives `Researcher.propose`,
`Evaluator.evaluate`/`holdout_check`, `dd_corrected_stats`,
`constitution.accepts`/`holdout_accepts` directly, mirroring
`EvolutionRun.generation()`'s exact gating (up to 3 fold-ranked candidates
per generation reach the accepts() gate; only those that pass reach the
sealed holdout) so the same-champion accepted/rejected verdicts line up
with what a real `evolve` run would have decided. New instrumentation:
for every candidate at both stages, record `(challenger - champion)` for
both raw fitness and excess return, then classify into four buckets —
both favor challenger, both favor champion, "risky" (fitness favors
challenger while excess return favors champion — the direction that
matters, since search ranks and promotes on fitness), and "conservative
miss" (fitness favors champion while excess return favors the
challenger).

15 generations, `n_blind=14`, seeded from the live champion v3's real
`researcher_memory` (224 tested proposals, stagnation 15, holdout_draws
22 — the real, not reset, bar), same seeding the 10:17 UTC session used.
Touches nothing on disk: the shadow champion genome lives only in a
local variable (reassigned on a shadow promotion, never saved), no
`Genome.save()`/`.promote()`-to-disk/`EvolutionRun.run()` call anywhere,
`live_state.json` opened read-only once. Champion held at v3 through all
15 generations — no shadow promotion, same qualitative shape as every
other non-4h shadow-evolve session against this champion.

## Result

**The disagreement is not genuinely mixed — it is heavily one-sided
toward the "risky" direction, at both stages.**

Fold-aggregate stage, 210 candidates: 133 disagreements (63.3%, close to
the 10:17 UTC session's 66.2% on a different random seed — consistent).
Of those 133: **118 (88.7%) are the risky direction** (raw fitness
ranks the challenger above the champion while excess return ranks it
below), only 15 (11.3%) are the conservative-miss direction.

Sealed-holdout stage — the gate a real promotion is decided at — 40
candidates reached it (every candidate that cleared the fold-aggregate
`accepts()` gate this run): 6 disagreements (15.0%, in the same range as
the 10:17 UTC session's 8.9%). Of those 6: **5 (83.3%) are the risky
direction**, 1 (16.7%) is conservative-miss. This matches the 10:17 UTC
session's own qualitative description of its 4 holdout-stage
disagreements ("challenger's raw holdout fitness clearly beat the
champion's ... while its holdout excess return was marginally below the
champion's") — that session just hadn't tabulated direction as a
number yet.

## What this settles, and doesn't

Answers the 10:17 UTC session's open question: at both stages the
skew is large and consistent (88.7% / 83.3% risky, not a coin flip),
not "genuinely mixed." Read together with that session's other finding
(every holdout-stage disagreement so far has been a *near-tie* on excess
return, 0.1-1.1pp) the fuller picture is: raw fitness's blind spot is
real, systematic, and points in a consistent direction (it can rank a
challenger above the champion on a near-tie-or-worse relative-to-benchmark
basis), but every real instance found so far is a near-miss, not a
lopsided flip that would have driven a bad promotion. Both are one
15-generation sample against one champion, at whatever fold/holdout
calendar window happened to be current when the sessions ran (today's
fold window has the champion deeply underwater on raw fitness per the
06:00 UTC weekend all-hands' as-of-drift finding) — neither the 88.7%/
83.3% skew nor the near-tie magnitude is validated across champions or
calendar windows yet.

Still, and explicitly, the owner-level design decision the weekend
all-hands and the 09:00 UTC daily discussion already flagged
("should the selection metric be redefined around excess return")
remains untouched by this — this sharpens the evidence base for that
decision, it does not make it.

## Verified safe

- No file written anywhere by the shadow script: `git status --short`
  clean before, during (checked mid-run), and after.
- `md5sum live_state.json` unchanged throughout:
  `bf360fc7f86f6bae2bc46bb6f6dc6026`.
- Sandbox script deleted after extracting results (`git status --short`
  shows nothing untracked) — not committed, per the same precedent as
  every other real-search shadow script this project has run.
- Today's bar (00:20 UTC) was already processed before this session
  started (`runs/2026-08-29-0020-daily-trading.md` exists); no `tick`
  run, no double-trade risk. No `evolve` run against real state either.
- Full test suite unaffected (no repo code changed this session, only a
  since-deleted sandbox script outside the tested surface).

## Next

- If this line of inquiry continues further: a run against a
  *favorable* fold window (champion's own fold-aggregate fitness not
  deeply negative from calendar drift) to check whether the 63.3%
  fold-stage disagreement rate and its 88.7% risky-direction skew are
  themselves as-of-drift artifacts, or hold up on a friendlier window.
- Repeating this against a different champion version (once one exists)
  would separate "property of v3 specifically" from "property of the
  raw-fitness-vs-excess-return relationship in general."
- Still not attempted, still the owner's call: redefining the selection
  metric itself.
