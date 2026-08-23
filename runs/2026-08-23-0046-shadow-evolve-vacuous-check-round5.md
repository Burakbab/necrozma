# 3-hourly self-improvement check — 2026-08-23 00:46 UTC

## State check

- `git pull` clean, local `main` reached a detached-HEAD state at session start
  (2 commits ahead with no branch pointer — the recurring container-seed
  artifact prior sessions have logged, not real divergent work); `git
  checkout main && git pull` fast-forwarded cleanly to `origin/main`'s tip, no
  work lost.
- `pip3 install -r requirements.txt -q` (bare cloud sandbox).
- `live_state.json`: genome v3, `updated` timestamp `2026-08-23T00:22:00+00:00`
  — today's daily bar already processed by the 00:20 UTC run, current time
  ~00:46-01:32 UTC, no new bar since. `tick` not run this session, no
  double-trade risk. `constitution verified 8b74865634b1db07` unchanged
  throughout. `review-hard-calls`: 0 pending.

## What this session did

A fifth round of the explicit "Next" ask carried by the 10:15, 13:22, 16:29
and 22:40 UTC sessions on 2026-08-22: keep tracking, generation after
generation, whether the dd-corrected gate's "vacuous-regression-check"
pattern (champion v3's own dd-corrected max_dd already exceeds
`MAX_DD_HARD_FAIL`, so `fitness(champion) == -inf`, which permanently
disables the merged-fitness-regression check and loosens the
drawdown-regression-tolerance check for as long as v3 remains champion — see
`runs/2026-08-22-1015-dd-gate-vacuous-regression-check.md`) keeps consuming
extra sealed-holdout draws.

Same isolation discipline as every prior shadow-evolve session: fresh scratch
dir (`/tmp/necrozma_scratch/round5`, `cwd` changed before any bundled module
import so `GENOME_DIR`/`LINEAGE_PATH` resolve under the scratch tree —
asserted at runtime, not just described), real champion v3 and its actual
accumulated `researcher_memory` seeded the same way the `evolve` CLI itself
does (from `acct.researcher_memory`: 182 tested proposals, stagnation 12,
holdout_draws 13 at session start), real file never touched (`live_state.json`
md5 identical before/after, `af16ffdc22a57c5d63a83003216a8f99`). Wrote a small
diagnostic-only script (`vacuous_check_round5.py`, not committed — composes
already-tested `Evaluator.evaluate`/`dd_corrected_stats`/`constitution.accepts`,
no new pure function, same precedent as every prior round's script) that
reimplements `EvolutionRun.generation()`'s own top-3 loop verbatim for the
real (NEW, dd-corrected) path — including actually advancing the shadow
champion on a real promotion, which never triggered — and, before each
`accepts()` call, also computes what the OLD (raw fold-merged, uncorrected)
gate would have decided on the same candidate, checkpointing to JSON after
every generation. Smoke-tested at 1 generation first (95s, correct output,
real file md5 unchanged) before committing to the full run.

**25 generations run to completion in ~40 minutes** (background process,
watched via `Monitor`), each generation taking a consistent ~93-99s — faster
per-generation than prior rounds' ~142-166s, likely because this session's
`researcher_memory` seed (182 already-tested proposals) was larger than
earlier rounds' fresher seeds, so `Researcher.propose` had less new ground to
cover per call. Champion held all 25 generations, no promotion shadow or
otherwise. **75 top-3 candidates reached the gate** (25 generations × up to 3
ranked candidates each), 32 of which cleared the fold-aggregate gate and
reached the sealed holdout (`holdout_draws` climbed 13 → 45 in this scratch
lineage) — all 32 correctly rejected there, consistent with
`holdout-pressure`'s standing finding.

**One vacuous-accept flip this round** (generation 3, OLD rejects, NEW
accepts), zero intended-tightening flips. The flip's own numbers are a clean
textbook case of the mechanism: champion's merged max_dd is -38.8% (OLD path,
finite fitness) vs -46.5% dd-corrected (NEW path, `fitness(champion) ==
-inf`) — OLD correctly rejects on "merged fitness regressed: 1.315 vs
champion 1.330" (a real, finite comparison), while NEW's merged-fitness-
regression check is vacuously satisfied (`1.307 >= -inf`) so the candidate
sails through on selection-fitness margin and drawdown-tolerance alone. It
reached the sealed holdout and was correctly rejected there — no incorrect
promotion resulted, same as every prior round.

## Reading

Combined across all five sessions on this thread (four on 2026-08-22, this
one on 2026-08-23): **6/279 real shadow candidates (≈2.15%) have now shown
the vacuous-accept flip** (session counts 2, 0, 3, 0, 1) and **1/279 (≈0.36%)
the intended-tightening flip** (all from the 16:29 session). This round's
single occurrence pulls the previous combined figure (5/204 ≈ 2.5%) down
slightly rather than up — consistent with the standing read: a real,
non-trivial, but genuinely noisy background rate, not a fires-every-
generation certainty and not a one-off. Six sessions' worth of session counts
(2, 0, 3, 0, 1) still don't resolve to a stable per-session rate; 279
candidates is a larger sample than any single prior session cited but still
small for a rare-event rate this variable session-to-session.

No incorrect promotion resulted this session, same as every prior round —
the one candidate that reached the sealed holdout via the vacuous NEW-accept
path was correctly rejected there.

No push notification sent — this session adds one more data point that
narrows rather than changes the already-fully-communicated mechanism and
severity from the 2026-08-22 10:15 session; no new risk, no incorrect
promotion, no code change.

## Verification

- No code changed this session — pure diagnostic script, not committed
  (throwaway, lives only in the scratch dir `/tmp/necrozma_scratch`).
- `live_state.json` md5 identical throughout (`af16ffdc22a57c5d63a83003216a8f99`).
- `evotrader.manifest` untouched, `constitution verified 8b74865634b1db07`
  unchanged on every invocation.
- `git status --short` clean before this commit (only `AGENTS.md` + this run
  note change).
- Scratch dir and its intermediate state are scratch-only, not committed.
- Today's 2026-08-23 daily bar confirmed already processed before this
  session started (`updated` timestamp unchanged from session start); `tick`
  not run this session. `review-hard-calls`: 0 pending, checked again after
  the shadow run.
- No genome promotion (champion held v3 throughout, real and shadow) — no
  README `## Status` change needed.

## Next

- Combined rate across five sessions is now 6/279 (≈2.15%) vacuous-accept
  flips and 1/279 (≈0.36%) intended-tightening flips. Per-session counts
  (2, 0, 3, 0, 1) are still noisy enough that this is not a number to treat
  as final — whoever next runs shadow or real evolution against v3 should
  keep adding to the cumulative sample and cite 6/279 (not round 4's 5/204)
  as the current figure.
- The demotion/rollback design question itself is unchanged and still not
  attempted (explicitly out of scope for a 3-hour slot per the weekend
  all-hands note) — still the owner's call per the standing "no rollback
  mechanism exists yet" note. `succession-audit`'s 2026-08-22 18:54 finding
  (no real champion currently clears the dd-corrected drawdown gate, v2 for a
  different reason than v1/v3) remains the fact base to start from if that
  design pass opens.
- Given this thread now spans five sessions and 279 candidates without the
  rate settling to something worth anchoring on, and given each round costs
  ~40-90 minutes for a marginal data point, whoever next picks this up should
  weigh another round of the same measurement against picking up a different
  open item (AGENTS.md's "Next steps" 4h-bar third-plateau question, or item
  7's unflatten work) — this is a judgment call, not a rule, since the rate's
  practical severity (no incorrect promotion in 279 candidates across 5
  independent sessions) hasn't changed.
