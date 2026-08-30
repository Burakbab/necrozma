# Does lone_voice_scale > two_agree_bonus contribute to the risky-direction skew? (real-champion follow-up)

2026-08-30, ~07:45-09:15 UTC (3-hourly check)

## Why

The 05:18 UTC session's own "Next" section flagged the natural follow-up to
its hand-clamped-genome test: "hold fold-fitness constant (compare against a
second real champion, e.g. v1/v2 reconstructed, rather than a hand-built
counterfactual that also moves fitness)". This session attempts it.

Checked first whether the real lineage even offers the comparison: v1 and v2
both have `lone_voice_scale=0.6 < two_agree_bonus=1.2`; only v3 (live) has
`lone_voice_scale=1.4791 > two_agree_bonus=1.2`. So the three real champions
this account has ever had split 2-vs-1 on the inequality the 00:46 UTC
hard-call review flagged — a genuine natural experiment, not a constructed
one.

## What

Same `loop.evolve.disagreement_scan` machinery as every prior session in this
thread, same discipline (never calls `Genome.save()`/`.promote()`, nothing
written to `live_state.json`, scratch scripts lived outside the repo,
deleted after use). Ran it against all three real champions
(`_reconstruct_champion_genome` for v1/v2, the live genome directly for v3),
each with its own fresh `Evaluator` on today's real 27-symbol/4-year window,
same `Researcher(seed=4242)`, `generations=15, n_blind=14`, blank
`researcher_memory` for all three (fair comparison — none of them get the
real champion's accumulated memory). Run in two background batches (v1+v3,
then v2) after an earlier attempt was killed by an over-tight 55-minute
`timeout` wrapper combined with output lost to a `| tail` pipe — no data
lost from the repo's perspective (nothing was persisted either way), just
wall-clock spent restarting cleanly with direct file redirection instead.

## Result

| ver | lone | two | lone>two | champ fold-fit | fold n | fold dis% | risky | cons | risky share | ho n | ho dis% | risky | cons |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| v1 | 0.6000 | 1.2 | False | -0.151 | 231 | 26.8% | 36 | 26 | **58.1%** | 24 | 0.0% | 0 | 0 |
| v2 | 0.6000 | 1.2 | False | +0.112 | 231 | 16.9% | 11 | 28 | **28.2%** | 8 | 12.5% | 0 | 1 |
| v3 (live) | 1.4791 | 1.2 | True | -1.669 | 221 | 44.8% | 90 | 9 | **90.9%** | 44 | 2.3% | 1 | 0 |

Two things, not one — same shape as the 05:18 UTC clamp test's own write-up:

1. **The swing is much bigger this time, and in the predicted direction.**
   v1's 58.1% risky share and v2's 28.2% are both well below the 61-89%
   range every other point in this thread (including the 05:18 UTC clamp
   test's 86.1%/90.9%) has shown. v2 is the **first data point in this
   entire thread where the conservative direction is the majority**
   (71.8%) — a genuinely new result, not a replication of anything seen
   before. Read in isolation, this looks like much stronger evidence *for*
   the flagged hypothesis than the clamp test found.

2. **But it's more confounded, not less — the real lineage doesn't give a
   clean "hold fold-fitness constant" comparison.** Sorted by fold-fitness
   instead of by the gene inequality, the same three points line up exactly
   as monotonically as sorted by the gene: v2 (fit +0.112, risky 28.2%) →
   v1 (fit -0.151, risky 58.1%) → v3 (fit -1.669, risky 90.9%). Fitness and
   `lone_voice_scale > two_agree_bonus` happen to covary in the same
   direction across every real champion this account has ever promoted —
   the worst-fitness-on-today's-window champion (v3) is also the only one
   with the inequality flagged. Three uncontrolled real points cannot
   separate "the gene pairing drives the skew" from "worse fold-fitness
   drives the skew" (the keep_frac sweep's own established pattern) when
   the two explanations never disagree in the available data. The 05:18 UTC
   session's stated goal — hold fold-fitness roughly fixed while varying
   only the gene pairing — is not something the real lineage can supply;
   only a genuinely designed counterfactual (re-tune some other gene to
   restore fold-fitness after changing this pairing) could do that, and
   that's real design work, not a reconstruction.

One incidental resolution of the 05:18 UTC session's own flagged loose end:
that session found the clamped genome's disagreement *rate* moved opposite
to fold-fitness (the one case in the whole thread breaking the keep_frac
sweep's monotonic fitness-predicts-disagreement pattern) and guessed this
might be because it varied the genome instead of the calendar window. Here,
varying the genome via three *real* evolved champions instead of one
hand-clamped gene, the pattern holds again: disagreement rate 16.9% (v2) →
26.8% (v1) → 44.8% (v3) tracks fitness monotonically, same direction as
every calendar-window point. Best read: the 05:18 UTC anomaly looks like an
artifact specific to clamping a single gene in isolation (which also
produced an unusually large, potentially out-of-distribution fold-fitness
swing, -1.669→-2.637, more than either real-champion gap here), not a
general property of genome-only perturbations.

## What this settles, and doesn't

The narrow "is `lone_voice_scale > two_agree_bonus` a contributor to the
disagreement thread's risky-direction skew" question has now had three
independent looks (05:18 UTC hand-clamp, this session's real-champion
comparison, and the underlying keep_frac-sweep/fitness-decomposition work
that established the fold-fitness confound in the first place) and all
three land on the same structural problem: this account's own history never
offers a case where the gene pairing and fold-fitness quality point in
different directions, so the question is not answerable from data this
project has generated, real or shadow, without a deliberately constructed
counterfactual that this session did not build. Recommend treating this
specific narrow side-question as **exhausted for now**, same standing as
the fold-scheme windowing chain's own four-mechanism exhaustion finding
(2026-08-21) — not wrong to revisit, but not worth another data point
without a genuinely controlled construction. Does not touch, and was never
meant to touch, the broader "should the selection metric be redefined
around excess return" question, which stays closed per the 06:00 UTC
weekend all-hands write-up unless one of its three named triggers fires.

## Verified safe

- `git status --short` (repo): clean before and after — scratch scripts
  lived in the session scratchpad, not the repo.
- `md5sum live_state.json`: unchanged, `81922c6011c986449f635dbf43553d0e`,
  matching every prior entry in this thread today — `disagreement_scan`'s
  own contract (never calls `Genome.save()`/`.promote()`/
  `EvolutionRun._record()`).
- No `tick`/`evolve` run against real state; today's bar (00:20 UTC, tick
  16) was already processed and reviewed before this session started.
- No code changed this session, so no test-suite/bundle-sync delta —
  `python3 -m pytest -q` confirmed 243/243 at session start.

## Next

- If this line is ever picked back up, it needs a genuinely constructed
  counterfactual that holds fold-fitness roughly fixed while only the gene
  pairing changes (e.g. re-tune one or two other genes after the clamp to
  bring fitness back near the real champion's own value) — not another
  real-champion or clamp-only comparison, both of which this thread has now
  tried and both landed on the same confound.
