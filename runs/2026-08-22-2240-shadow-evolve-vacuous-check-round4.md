# 3-hourly self-improvement check — 2026-08-22 22:40 UTC

## State check

- `git pull` clean, local `main` already at `origin/main`'s tip — no detached-HEAD
  container-seed artifact this session (unlike several prior sessions today).
- `live_state.json`: genome v3, `updated` timestamp `2026-08-22T00:21:18+00:00`
  — today's daily bar already processed by the 00:20 UTC run, current time
  ~21:46-22:40 UTC, no new bar since. `tick` not run this session, no
  double-trade risk. `constitution verified 8b74865634b1db07` unchanged
  throughout. `review-hard-calls`: 0 pending.

## What this session did

A fourth round of the explicit "Next" ask carried by the 10:15, 13:22 and
16:29 UTC sessions today: keep tracking, generation after generation, whether
the dd-corrected gate's "vacuous-regression-check" pattern (champion v3's own
dd-corrected max_dd already exceeds `MAX_DD_HARD_FAIL`, so
`fitness(champion) == -inf`, which permanently disables the
merged-fitness-regression check and loosens the drawdown-regression-tolerance
check for as long as v3 remains champion — see
`runs/2026-08-22-1015-dd-gate-vacuous-regression-check.md`) keeps consuming
extra sealed-holdout draws.

Same isolation discipline as every prior shadow-evolve session today: fresh
scratch copy of `live_state.json` (`/tmp/necrozma_scratch/live_state_scratch.json`),
real champion v3 and its actual accumulated `researcher_memory` seeded the
same way the `evolve` CLI itself does (from `acct.researcher_memory`), real
file never touched (`live_state.json` md5 identical before/after,
`3f71d6ab111ecd646eda9e0e595a9970`). Wrote a small diagnostic-only script
(`/tmp/necrozma_scratch/vacuous_check_round4.py`, not committed — composes
already-tested `Evaluator.evaluate`/`dd_corrected_stats`/`constitution.accepts`,
no new pure function, same precedent as the three prior sessions' scripts)
that reimplements `EvolutionRun.generation()`'s own top-3 loop verbatim for
the real (NEW, dd-corrected) path — including actually advancing the shadow
champion on a real promotion, which never triggered — and, before each
`accepts()` call, also computes what the OLD (raw fold-merged, uncorrected)
gate would have decided on the same candidate, logging both plus the reason
string each path gave, checkpointing to JSON after every generation (the
prior session's lesson about not losing a killed run's data).

**20 generations run to completion in ~49 minutes** (background process,
watched via periodic progress checks), each generation taking a consistent
~142-166s. Champion held all 20 generations, no promotion shadow or
otherwise. **60 top-3 candidates reached the gate** (20 generations × up to 3
ranked candidates each), 13 of which cleared the fold-aggregate gate and
reached the sealed holdout (`holdout_draws` climbed 13 → 28 in this scratch
lineage) — all 13 correctly rejected there, consistent with
`holdout-pressure`'s standing finding.

**Zero flips of either kind this round** — no vacuous-accept (OLD rejects,
NEW accepts) and no intended-tightening (OLD accepts, NEW rejects) among all
60 candidates checked.

## Reading

Combined across all four of today's sessions: **5/204 real shadow candidates
(≈2.5%) have shown the vacuous-accept flip** (2 from 10:15, 0 from 13:22, 3
from 16:29, 0 from this session — session counts 2, 0, 3, 0) and **1/204
(≈0.5%) have shown the intended-tightening flip** (all from 16:29). Adding a
second zero-flip session to the sample (13:22 was the first) pulls the
combined vacuous-accept rate back down from the 16:29 session's 5/144 (≈3.5%)
toward roughly half that — this reads as the same "real, non-trivial, but
genuinely noisy background rate" conclusion the 16:29 session reached, not a
reversal of it: two sessions found the pattern (2, 3 occurrences) and two
found nothing (0, 0), and 204 candidates is still a small sample for a
rare-event rate this variable session-to-session. The right read stays what
the 16:29 entry already said — cite 5/204 (not 5/144) as the current combined
figure, and note it moved with one more zero-flip draw the same way it can
move again either direction with the next one.

No incorrect promotion resulted this session, same as every prior round —
all candidates that reached the sealed holdout via either accept path (this
session, only the honest NEW path — no vacuous pass occurred) were correctly
rejected there.

No push notification sent — this session adds a data point that narrows
rather than changes the already-fully-communicated mechanism and severity
from the 10:15 session; no new risk, no incorrect promotion, no code change.

## Verification

- No code changed this session — pure diagnostic script, not committed
  (throwaway, lives only in the scratch dir `/tmp/necrozma_scratch`).
- `live_state.json` md5 identical throughout (`3f71d6ab111ecd646eda9e0e595a9970`).
- `evotrader.manifest` untouched, `constitution verified 8b74865634b1db07`
  unchanged on every invocation.
- `git status --short` clean before this commit (only `AGENTS.md` + this run
  note change).
- Scratch copy of `live_state.json` and its intermediate state are scratch-
  only, not committed.
- Today's 2026-08-22 daily bar confirmed already processed before this
  session started (`updated` timestamp unchanged from session start); `tick`
  not run this session. `review-hard-calls`: 0 pending, checked again after
  the shadow run.
- No genome promotion (champion held v3 throughout, real and shadow) — no
  README `## Status` change needed.

## Next

- Combined rate across four sessions today is now 5/204 (≈2.5%)
  vacuous-accept flips and 1/204 (≈0.5%) intended-tightening flips. The
  per-session counts (2, 0, 3, 0) are noisy enough that this is still not a
  number to treat as final — whoever next runs shadow or real evolution
  against v3 should keep adding to the cumulative sample rather than
  anchoring on today's total, and should cite 5/204 (not 16:29's 5/144) as
  the current figure.
- The demotion/rollback design question itself is unchanged and still not
  attempted (explicitly out of scope for a 3-hour slot per the weekend
  all-hands note) — still the owner's call per the standing "no rollback
  mechanism exists yet" note. `succession-audit`'s 18:54 finding (no real
  champion currently clears the dd-corrected drawdown gate, v2 for a
  different reason than v1/v3) remains the fact base to start from if that
  design pass opens.
