# Daily discussion / check-in — 2026-08-31 09:00 UTC

Scheduled daily discussion, separate from the 00:20 UTC trading run and the
3-hourly evolution/maintenance cycles. No code or state changes this run —
pure read and reflect, per this routine's task.

## State check

- Cloud clone started in detached HEAD at `50c8bff` (tip of `origin/main`
  before this session's own pull). `git checkout main && git pull origin
  main` fast-forwarded 14 commits from yesterday's sessions (four run notes
  on 2026-08-30 plus the demotion-rollback design pass, then four more from
  overnight 4h-shadow work into 2026-08-31 and today's daily trading run).
- `git status --short` clean. `md5sum live_state.json` =
  `37a1b00bee3f7cb1ad2f4adde0ab9ed0` — changed since yesterday's snapshot,
  consistent with the 00:20 UTC run trading tick 17 (bought LINKUSDT,
  XRPUSDT). README `## Status` still describes v3, consistent with no
  promotion since 2026-08-16.
- Read `AGENTS.md` Current state / Next steps and every run note since the
  2026-08-30 09:00 discussion: `1851` (v3 demotion/rollback design pass —
  see below), `2305` and the three 2026-08-31 4h-shadow sessions (`0243`,
  `0407`, `0705`) continuing the entry-frequency investigation for item 2,
  and `0020` (today's daily trading, tick 17, clean run, `review-hard-calls`
  0 pending). Also read the 13:01 UTC short-selling note, from just before
  yesterday's discussion window but not yet surfaced in a daily check-in.

## Reflection

Two threads moved since yesterday.

**The v3 demotion/rollback question — open and reaffirmed daily since
2026-08-22 — now has a design pass and a recommendation**, the same
treatment the fitness-vs-excess-return question got on 2026-08-30 06:00 UTC.
`succession-audit` re-run fresh confirms the standing facts (v3 hard-fails
the corrected drawdown gate at -46.5% continuous maxDD; v1 also hard-fails;
v2 clears drawdown narrowly but is worse on every return measure) and adds
one new data point: v3's full-history excess return over buy-and-hold is
+68.2%, the only positive number of the three, while v1 and v2 are both
deeply negative. Recommendation is status quo (option C: treat
`MAX_DD_HARD_FAIL` as prospective on new candidates, not retroactive on a
sitting champion) with three named, checkable revisit triggers — a real
challenger clearing `accepts()`/`holdout_accepts()` against v3, a future
`succession-audit` candidate that beats v3 on both drawdown *and* excess
return, or the live account's real drawdown approaching
`CIRCUIT_BREAKER_DD` (0.25). None has fired. This closes the same kind of
gap the fitness-vs-excess-return question closed the day before — an item
that sat as "the owner's call, unstarted" for over a week now has an argued
position and concrete triggers instead.

**Short selling Phase 1 was implemented, tested (16/16 new tests passing),
and then fully reverted** — not because the design was wrong, but because
`core/portfolio.py` is one of the two files `constitution.checksum()`
literally seals. Editing it and syncing it into the live bundle trips
`CONSTITUTION MODIFIED`, and the Run protocol's own rule is to stop there,
not re-seal it. The session correctly reverted in full
(`git checkout -- core/portfolio.py evotrader_bundle.py`, deleted the new
test file) rather than leave the seal broken or re-seal it unilaterally.
This is new since yesterday's discussion and hasn't been surfaced in a
check-in yet.

## Does anything here need the owner?

- **Short selling Phase 1 needs a human to review the `core/portfolio.py`
  diff and re-seal `evotrader.manifest` before any further work on this
  item can land.** This is a real gate, not a formality — no CLI path
  re-seals a mismatched manifest, by design. The design itself (signed-`qty`
  `Position`, `short()`/`cover()` mirroring `buy()`/`sell()`, per-bar borrow
  accrual in `mark()`) held up under a real implementation attempt and is
  ready to be reapplied once that sign-off exists; nothing is lost by
  waiting, since the code was reverted rather than left half-landed. No
  action needed from the owner today unless they want to unblock this item
  now — flagging it because it's the first genuine "needs a human, not just
  more search" item since the fitness-vs-excess-return and demotion/rollback
  questions were both closed with recommendations rather than left open.
- **The v3 demotion/rollback design question is now closed with a
  recommendation (status quo, three named triggers)** as of yesterday's
  18:51 UTC design pass — see above. Not a new ask; flagging the closure
  for continuity, same as yesterday's note did for the fitness-vs-
  excess-return thread the day it closed.
- Live account is 17 daily ticks old, nowhere near the 6-month real-money
  threshold. `hard_call_reviews` still has just the one entry (tick 16),
  reviewed same-day back on 2026-08-30. No `AMENDMENTS.md` row missing for
  anything that actually shipped (short selling never shipped, so none is
  owed yet).

**One item worth the owner's awareness: short selling Phase 1 is designed,
tested, and waiting on a manifest re-seal, not on more engineering.**
Everything else is either closed with a recommendation (demotion/rollback,
as of yesterday) or unchanged background work (4h-shadow entry-frequency
diagnostics, still narrowing toward a specific set of threshold genes to
hand-retune, no decision pending there).
