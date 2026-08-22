# 3-hourly self-improvement check — 2026-08-22 13:22 UTC

## State check

- Cloud clone started detached again with local `main` 2 commits behind an
  old force-updated `origin/main` tip (the same recurring container-seed
  artifact prior sessions have logged) — `git checkout main && git reset
  --hard origin/main` per the run protocol, nothing lost.
- `live_state.json`: genome v3, `updated` timestamp `2026-08-22T00:21:18+00:00`
  — today's daily bar already processed by the 00:20 UTC run. `tick` not run
  this session, no double-trade risk. `constitution verified
  8b74865634b1db07` unchanged throughout. `review-hard-calls`: 0 pending.
- No push notification sent this session — the open v3 demotion question was
  already surfaced by the last two sessions (09:00 and 10:15 UTC today) and
  nothing here changes its practical severity or urgency (see "Reading"
  below).

## What this session did

Continued the explicit "Next" ask from the 10:15 UTC session: keep tracking,
generation after generation, whether the dd-corrected gate's
"vacuous-regression-check" pattern (champion v3's own dd-corrected max_dd
already exceeds `MAX_DD_HARD_FAIL`, so `fitness(champion) == -inf`, which
permanently disables the merged-fitness-regression check and loosens the
drawdown-regression-tolerance check for as long as v3 remains champion —
see `runs/2026-08-22-1015-dd-gate-vacuous-regression-check.md`) keeps
consuming extra sealed-holdout draws.

Same isolation discipline as every prior shadow-evolve session: fresh scratch
copy of `live_state.json` (`EVO_STATE=<scratch copy>`), real champion v3 and
its actual accumulated `researcher_memory` (182 candidates already tried,
holdout_draws=13), real file never touched (`live_state.json` md5 identical
before/after, `3f71d6ab111ecd646eda9e0e595a9970`). Wrote a small
diagnostic-only script (not committed — composes already-tested
`Evaluator.evaluate`/`dd_corrected_stats`/`constitution.accepts`, no new
pure function, same precedent as the 10:15 session's script) that
reimplements `EvolutionRun.generation()`'s own top-3 loop verbatim for the
real (NEW, dd-corrected) path — so the shadow run's actual promotion
decisions are identical to what `evolve` would produce — and, before each
`accepts()` call, also computes what the OLD (raw fold-merged, uncorrected)
gate would have decided on the same candidate, logging both.

**18 generations run** (vs. the 10:15 session's 10): champion held
throughout, no promotion shadow or otherwise. Best fold-aggregate fitness
seen: 1.886 (generation 16), still short of the multiple-testing-adjusted
margin at that candidate count (434 cumulative by generation 18).

**54 top-3 candidates reached the gate** (vs. the previous session's 30, for
a combined 84-candidate sample across the two sessions):

- **0 of 54 showed either kind of accept/reject flip** — no
  OLD-accepts/NEW-rejects (the intended tightening actually changing an
  outcome) and, unlike the 10:15 session (2/30), **no
  OLD-rejects/NEW-accepts** (the vacuous-regression-check bug actually
  changing an outcome) either. Combined across both sessions: 2/84 candidates
  showed the vacuous-accept pattern, both from the earlier session
  (generations 9-10 there), zero from this session's 18 generations
  (generations 1-18 here, a fresh, non-overlapping candidate batch). One
  session finding it and the next not finding it in a larger sample is
  evidence the pattern is real but occasional, not something that fires
  every generation — tempers, without resolving, the "if it does so
  consistently" escalation condition the 10:15 note set.

- **A second, previously-undocumented effect found in this session's larger
  sample: 2 of 54 candidates (generations 5 and 17) hard-failed under NEW
  (dd-corrected max_dd 41.7%/41.3%, over `MAX_DD_HARD_FAIL`) while their raw,
  uncorrected max_dd was still under 40% (39.0%/32.5%)** — so OLD would never
  have hard-failed them on drawdown at all. In both cases the outcome did not
  flip (OLD still rejected both, but via the fold-aggregate margin check
  instead, since neither cleared it anyway), so this is not a third
  concerning mechanism, it's the corrected hard-fail check doing exactly what
  the weekend all-hands fix intended — catching a challenger whose *true*
  drawdown crosses the safety threshold even though its fold-merged number
  understated it. Worth naming because it is the first time in either
  session's samples that the "intended tightening" direction (NEW rejects
  something OLD's number alone wouldn't have flagged) showed up at all, even
  though the margin check already caught both candidates independently so it
  never became the deciding factor.

- **8 of 54 candidates cleared the fold-aggregate gate under both OLD and NEW
  identically** (all agreed, no flip) and reached the sealed holdout — all 8
  were correctly rejected there, consistent with `holdout-pressure`'s
  standing finding that real post-promotion challengers against v3
  overwhelmingly lose the sealed holdout. Champion's own dd-corrected max_dd
  was the same `-46.48%` in every one of the 54 comparisons (it doesn't
  change candidate to candidate — only the challenger's does), confirming
  the `f_champ == -inf` condition that disables the merged-fitness-regression
  check was live and available to fire on all 8 of these, and (per the 0
  flips found) still didn't change any outcome this round.

## Reading

Sharpens the picture from the 10:15 session rather than reversing it. The
vacuous-regression-check mechanism is confirmed real (it fired twice in the
prior session) but this session's larger, non-overlapping 54-candidate
sample found zero further occurrences — 2/84 total, not a
every-generation phenomenon. Combined with the newly-observed
raw-passes/corrected-fails cases (2/54, correctly caught by margin anyway),
the overall picture across 84 real shadow candidates is: the dd-corrected
gate has not yet been the sole cause of any actual accept/reject outcome
difference in either direction that would have changed which candidates
reach the scarce sealed-holdout check — the fold-aggregate margin check is
doing most of the rejecting either way at today's candidate count (434+),
consistent with `margin-curve`'s finding that the fold-aggregate margin is
nearly saturated. Still does not resolve the underlying open question (does
champion v3's true, dd-corrected 46.5% drawdown warrant demotion) — that
remains explicitly the owner's call, unchanged by this session's evidence.
Not urgent enough to escalate further today: no push notification sent, per
the same reasoning the 10:15 session used for its own incremental finding.

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
  session started (`updated` timestamp unchanged from session start);
  `tick` not run this session. `review-hard-calls`: 0 pending.
- No genome promotion (champion held v3 throughout, real and shadow) — no
  README `## Status` change needed.

## Next

- The vacuous-regression-check pattern is now measured at 2/84 real shadow
  candidates across two independent sessions, not a per-generation certainty.
  Whoever next runs shadow or real evolution against v3 should keep adding to
  this sample rather than treating either session's count as final — the
  question that matters for prioritizing the demotion/rollback design pass
  is the cumulative rate, not any single session's draw.
- The demotion/rollback design question itself is unchanged and still not
  attempted (explicitly out of scope for a 3-hour slot per the weekend
  all-hands note) — still the owner's call per the standing "no
  rollback mechanism exists yet" note.
