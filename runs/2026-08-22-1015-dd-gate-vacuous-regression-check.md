# 3-hourly self-improvement check — 2026-08-22 10:15 UTC

## State check

- Cloud clone started detached again; `git checkout main && git reset --hard
  origin/main` per the run protocol, nothing lost.
- `live_state.json`: genome v3, `updated` timestamp `2026-08-22T00:21:18+00:00`
  — today's daily bar already processed by the 00:20 UTC run. `tick` not run
  this session, no double-trade risk. `constitution verified
  8b74865634b1db07` unchanged throughout. `review-hard-calls`: 0 pending.
- `git log` shows the most recent commit (`bf289a2`, this morning's
  09:00 UTC daily discussion) flagged the still-open question from the
  weekend all-hands fix — whether champion v3 should be demoted now that its
  true (dd-corrected) drawdown is known to exceed `MAX_DD_HARD_FAIL` — as a
  decision needing explicit owner sign-off. That run note had no "Push
  notification" section at all (unlike the two prior sessions this week that
  surfaced this same thread, which both explicitly logged sending one), so a
  push notification summarizing the open decision was sent this session,
  since it looked like a real gap rather than a deliberate skip.

## What this session did

Per the weekend all-hands run's own "Next" note — "whoever next evaluates a
real promotion candidate should note in the run record whether the corrected
gate actually changed a promotion outcome it wouldn't have under the old
fold-merged-only check" — ran more shadow evolution against an isolated
scratch copy of `live_state.json` (`EVO_STATE=<scratch copy>`, same
discipline as every prior shadow-evolve session; real file's md5 unchanged
throughout, `3f71d6ab111ecd646eda9e0e595a9970`) and checked the new
dd-corrected gate's actual behavior on real candidates, not just synthetic
ones.

**10 generations run** (3 then 7, continuing the same scratch copy/researcher
memory): champion held throughout, no promotion shadow or otherwise. Best
fold-aggregate fitness seen: 1.787 (generation 5), still short of the
multiple-testing-adjusted margin at that candidate count.

**Built a small one-off script** (not committed — diagnostic-only, composes
already-tested `Evaluator.evaluate`/`dd_corrected_stats`/`constitution.accepts`,
no new pure function) that, for every one of the top-3 fold-ranked candidates
each generation actually ran through `accepts()` (30 candidates total across
the 10 generations), recomputes what the OLD fold-merged-only gate would
have decided next to what the NEW dd-corrected gate actually decided.

**Result — the first concrete, real-candidate evidence on this question:**

- 0 of 30 candidates showed the *intended* tightening effect (OLD would
  accept the fold-aggregate check, NEW rejects it) in this sample. Every
  candidate whose dd-corrected max_dd crossed 40% had *already* failed the
  OLD gate too, for an unrelated reason (margin or its own uncorrected
  max_dd already over 40%) — so in this specific 30-candidate sample, the
  hard-fail tightening never yet flipped an accept/reject/next-stage
  decision on its own. Consistent with, not proof against, the finding —
  a bigger or more adversarial sample could still find one.

- **2 of 30 candidates (generations 9 and 10) showed the opposite:
  OLD rejects, NEW accepts** — and this is not a bug in the diagnostic
  script, it is `constitution.accepts()` working exactly as written, given
  a fact about the current champion the previous sessions did not spell
  out this precisely. `accepts()` (`constitution.py`) computes
  `f_champ = fitness(champion_stats)` and rejects a challenger outright if
  `f_chal < f_champ` ("merged fitness regressed"). Champion v3's own
  dd-corrected `max_dd` is -46.5%, which is itself over `MAX_DD_HARD_FAIL`
  (0.40) — so `fitness()`'s own hard-fail branch makes `f_champ == -inf`
  for as long as v3 remains champion under the corrected accounting. No
  finite challenger fitness is ever `< -inf`, so **the
  merged-fitness-regression check is not just weakened, it is permanently
  disabled while v3 is champion** — every challenger that clears the
  fold-aggregate selection margin sails through this check automatically,
  regardless of whether its own merged fitness is actually any good. The
  weekend all-hands note called this "harmless to the mechanics that
  matter... becomes vacuously true" in the abstract; this session confirms
  it fires for real, twice, inside an actual generation loop, not just as
  a traced-through hypothetical.

  A second, related effect on the same root cause: the drawdown-regression
  check (`dd_chal > dd_champ * DD_REGRESSION_TOLERANCE`) also uses the
  champion's own (now much worse) corrected `max_dd` as its baseline —
  1.15x-46.5% ≈ 53.5% tolerance instead of 1.15x-34.1% ≈ 39.2% under the old
  baseline. So a challenger with real drawdown in the high 30s-to-40s%,
  which would have failed the *old* drawdown-regression check outright, now
  passes it too, for the same underlying reason.

  **Consequence observed directly, not hypothetical:** both generation-9
  and generation-10 top candidates (fold fitness 1.523 and 1.415) cleared
  `accepts()` via this now-vacuous path and reached the sealed holdout gate
  — consuming real, cumulative holdout draws (20th and 21st against this
  scratch copy's holdout draw count) that a healthy champion's intact
  regression check would likely have blocked earlier. Both were correctly
  rejected at the holdout (`-2.421` and `-0.606` vs champion `-0.166` +
  margin), so **no incorrect promotion resulted** — but `HOLDOUT_SIGMA`'s
  own design is that the cumulative draw count never resets and permanently
  raises the bar for every future candidate (`margin-curve`,
  2026-08-21: the holdout margin is nowhere near saturated at today's draw
  counts, so extra draws visibly move it). Two draws is a small sample, but
  it means the fold-aggregate gate is currently admitting more candidates
  to the scarce holdout check than it would under a healthy champion, not
  fewer — the opposite of what "tightening the drawdown gate" was supposed
  to do to overall promotion difficulty, even though no individual
  challenger evaluation is dishonest.

## Reading

This does not reverse anything about the fold-dd-blindspot fix itself — the
per-challenger hard-fail and drawdown-regression checks are still strictly
more honest than before, and nothing here shows a bad genome being let
through as a *promotion* (the sealed holdout still caught both cases). But
it sharpens the still-open demotion question flagged this morning and in
the weekend all-hands note: while champion v3 remains champion, the
fold-aggregate acceptance gate is running with one of its two
champion-relative safety checks (merged-fitness-regression) permanently
disabled and the other (drawdown-regression-tolerance) meaningfully
loosened — both consequences of the champion's own corrected number already
having failed the hard-fail bar. That is one more concrete, mechanistic
reason (not just "the number looks bad") that this is a real question about
whether v3 should keep serving as the baseline other candidates are
measured against, not just a paper-loss/PR-optics question. Not acted on
this session — still the owner's call, per the standing rule that
promotion/demotion policy is a risk-appetite decision, not an engineering
default.

## Verification

- No code changed this session — pure diagnostic script, not committed
  (throwaway, lives only in the scratch dir).
- `live_state.json` md5 identical throughout (`3f71d6ab111ecd646eda9e0e595a9970`).
- `evotrader.manifest` untouched, `constitution verified 8b74865634b1db07`
  unchanged on every invocation.
- `git status --short` clean before this commit (only `AGENTS.md` +
  this run note change).
- Scratch copy of `live_state.json` and its `state/lineage.jsonl` growth
  are gitignored / scratch-only, not committed.
- Today's 2026-08-22 daily bar confirmed already processed before this
  session started; `tick` not run this session.

## Push notification

Sent this session: a summary of the still-open v3 demotion decision (see
"State check" above — the prior daily-discussion run appears to have
written the escalation into `AGENTS.md`/its own run note but not actually
pushed a notification, unlike the two earlier sessions this week that
covered the same thread). Not sent a second time for this session's own
finding (the vacuous-regression-check mechanism) — it sharpens the existing
open question with a mechanism, but doesn't change the practical
severity/urgency already communicated, and no incorrect promotion occurred.
Consistent with the weekend all-hands session's own reasoning for not
re-notifying on an incremental finding.

## Next

- Whoever next runs shadow or real evolution against v3 should keep
  tracking whether this "vacuous regression check" pattern keeps consuming
  extra holdout draws — if it does so consistently generation after
  generation, that's an argument for prioritizing the demotion/rollback
  design pass sooner rather than treating it as low-urgency.
- If/when the owner's demotion decision lands and a healthy champion is
  back in place (its own corrected max_dd within 40%), this specific
  vacuous-check mechanism resolves itself automatically — no code fix is
  needed for the mechanism itself, only for whether v3 should keep being
  champion in the meantime.
