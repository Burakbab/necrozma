# 3-hourly self-improvement check — 2026-08-22 16:29 UTC

## State check

- Cloud clone started detached with local `main` pointing at an old,
  unrelated pre-restart commit (`fa43c4b`, not an ancestor of `origin/main`'s
  tip) — the same recurring container-seed artifact prior sessions have
  logged. `git checkout main && git reset --hard origin/main` per the run
  protocol, nothing lost.
- `live_state.json`: genome v3, `updated` timestamp `2026-08-22T00:21:18+00:00`
  — today's daily bar already processed by the 00:20 UTC run, current time
  ~15:46-16:29 UTC, no new bar since. `tick` not run this session, no
  double-trade risk. `constitution verified 8b74865634b1db07` unchanged
  throughout. `review-hard-calls`: 0 pending.

## What this session did

A third round of the explicit "Next" ask carried by the 10:15 and 13:22 UTC
sessions today: keep tracking, generation after generation, whether the
dd-corrected gate's "vacuous-regression-check" pattern (champion v3's own
dd-corrected max_dd already exceeds `MAX_DD_HARD_FAIL`, so
`fitness(champion) == -inf`, which permanently disables the
merged-fitness-regression check and loosens the drawdown-regression-tolerance
check for as long as v3 remains champion — see
`runs/2026-08-22-1015-dd-gate-vacuous-regression-check.md`) keeps consuming
extra sealed-holdout draws.

Same isolation discipline as every prior shadow-evolve session: fresh scratch
copy of `live_state.json` (`/tmp/necrozma_scratch/live_state_scratch.json`),
real champion v3 and its actual accumulated `researcher_memory` (182
candidates already tried, `holdout_draws=13`), real file never touched
(`live_state.json` md5 identical before/after, `3f71d6ab111ecd646eda9e0e595a9970`).
Wrote a small diagnostic-only script (not committed — composes already-tested
`Evaluator.evaluate`/`dd_corrected_stats`/`constitution.accepts`, no new pure
function, same precedent as the two prior sessions' scripts) that reimplements
`EvolutionRun.generation()`'s own top-3 loop verbatim for the real (NEW,
dd-corrected) path, and, before each `accepts()` call, also computes what the
OLD (raw fold-merged, uncorrected) gate would have decided on the same
candidate, logging both plus the reason string each path gave.

First attempt was cut short by an internal 590s safety timeout at generation
5 (no data lost otherwise, but not saved — the script wrote its JSON log only
at the end); fixed to checkpoint after every generation and re-ran fresh
(the scratch copy and real file were both still untouched, confirmed by md5,
so nothing needed to be redone beyond restarting the run — the killed
partial run's early candidates are a separate, non-overlapping random draw
from the same researcher and are not counted in the totals below, since
their data was never persisted).

**20 generations run to completion** (vs. 10 and 18 in the two prior
sessions today). Champion held throughout, no promotion shadow or otherwise.
**60 top-3 candidates reached the gate**, for a combined 144-candidate sample
across all three of today's sessions:

- **4 of 60 candidates flipped accept/reject between OLD and NEW** — the
  highest single-session flip count either metric has shown yet:
  - **3 of 60 (generations 3, 8, 17): OLD rejects, NEW accepts — the
    vacuous-accept bug.** All three show the exact mechanism from the 10:15
    session: `f_champ == -inf` (dd-corrected champion max_dd -46.5%, over
    `MAX_DD_HARD_FAIL`) makes the merged-fitness-regression check vacuously
    true (gen 3, 17: OLD rejected on `"merged fitness regressed"`, an
    impossible check once no finite value is `< -inf`), and separately the
    drawdown-regression-tolerance check is measured against the same
    much-worse champion baseline (gen 8: OLD rejected on `"drawdown
    regression: 39.5% vs champion 34.1%"`, using the honest but far tighter
    old-style 34.1% baseline; NEW instead compares to -46.5%, so 39.5% passes
    tolerance easily). All three reached the sealed holdout on the strength
    of this vacuous pass (holdout draws climbed to 27 across the session).
  - **1 of 60 (generation 15): OLD accepts, NEW rejects — the intended
    tightening, and the first time in 144 candidates across all three
    sessions today that this direction actually changed an outcome, not just
    a secondary check that never became load-bearing.** OLD's raw fold-merged
    max_dd for this candidate was 31.8% (would have cleared every check); the
    dd-corrected number was 41.3%, over the hard-fail line, so NEW rejected
    it outright with `"challenger failed a hard gate ... drawdown > 40%"`
    before the champion-relative checks were even reached. This is the
    corrected gate doing exactly the weekend all-hands fix's job — catching a
    real drawdown the fold-merged number missed — and for the first time
    across the three sessions, it was the actual reason a candidate got
    rejected instead of a moot side observation next to an independent
    fold-aggregate-margin rejection.
- **The remaining 56/60 showed no flip**: most agreed reject under both
  paths (fold-aggregate margin still doing the bulk of the rejecting at
  today's candidate count, consistent with `margin-curve`'s near-saturation
  finding), a handful agreed accept and reached the sealed holdout, all
  correctly rejected there (consistent with `holdout-pressure`'s standing
  finding).

## Reading

This sharpens the picture in the opposite direction from the 13:22 session's
tempering read. Combined across all three of today's sessions: **5/144 real
shadow candidates (≈3.5%) have shown the vacuous-accept flip** (2 from 10:15,
0 from 13:22, 3 from this session) — a session-to-session count of 2, 0, 3,
not a monotonically fading or vanishing rate. Three independent 10-20
generation samples in one day landing at 2, 0, and 3 occurrences reads as
real, non-trivial background noise from this mechanism rather than either "it
only fired once" or "it fires every generation" — the true rate is
plausibly in the low-single-digit percent and this session's higher draw is
within that range, not an outlier requiring a new explanation. Separately,
this is also the first session where the *intended* tightening direction
actually changed a decision, which is worth noting on its own: the
weekend-all-hands fix is doing real work in both directions now, not just the
unintended one.

Neither flip type has yet produced an incorrect promotion — all candidates
that reached the sealed holdout via either path, correctly or vacuously, were
rejected there. But every vacuous pass still burns one of the scarce,
never-reset sealed-holdout draws (`holdout_draws` is now 27 in this scratch
branch, up from 13 real / 20 in the 13:22 session's branch — these are
independent scratch lineages, not additive with the real counter). This
doesn't resolve or reprioritize the still-unstarted demotion/rollback design
question — that remains explicitly the owner's call — but the combined
5/144 rate across three sessions is a firmer number to cite than any single
session's count was.

No push notification sent this session: the underlying mechanism and its
practical severity/urgency were already communicated in full by the 10:15
session, and this round's contribution is a sharper cumulative rate plus one
new (favorable) data point about the intended-tightening direction working —
useful evidence, not a new risk requiring the owner's attention right now.

## Verification

- No code changed this session — pure diagnostic script, not committed
  (throwaway, lives only in the scratch dir `/tmp/necrozma_scratch`).
- `live_state.json` md5 identical throughout (`3f71d6ab111ecd646eda9e0e595a9970`).
- `evotrader.manifest` untouched (`0bf3a7d9411ee692d0a9f152a7533803`),
  `constitution verified 8b74865634b1db07` unchanged on every invocation.
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

- Combined rate across three sessions today is now 5/144 (≈3.5%)
  vacuous-accept flips and 1/144 intended-tightening flips. Whoever next runs
  shadow or real evolution against v3 should keep adding to this cumulative
  sample — the per-session count (2, 0, 3) is noisy enough that more draws
  still meaningfully sharpen the rate estimate, not just confirm it.
- The demotion/rollback design question itself is unchanged and still not
  attempted (explicitly out of scope for a 3-hour slot per the weekend
  all-hands note) — still the owner's call per the standing "no rollback
  mechanism exists yet" note.
