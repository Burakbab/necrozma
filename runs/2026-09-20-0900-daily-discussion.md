# Daily discussion — 2026-09-20 09:00 UTC

## Session start

Container started detached from `refs/heads/main` with the working tree
clean and already matching `origin/main`'s history (no divergence). `git
checkout main && git pull origin main` fast-forwarded 23 commits
(`aaee4c8..906aa44`), nothing lost. Read-only check-in — no code or trading
state touched this session.

## What changed since yesterday's daily discussion (2026-09-19 09:00 UTC)

Read `AGENTS.md`'s "Owner decisions pending" and "Current state" sections
plus the intervening run notes. Since yesterday:

- **Tick 37 daily trading** (~00:20 UTC 09-20): handled at the dedicated
  daily slot; no tick-triggered `evolve` (`37 % 7 = 2`). See
  `runs/2026-09-20-0020-daily-trading.md`.
- **Seven more scheduled `evolve` batches** against the live v3 (1d)
  champion, all no promotion. Cumulative candidates tried against v3 rose
  24399 → 25025; stagnation/boldness counter 1755 → 1801. Champion's
  fold-aggregate fitness held flat throughout, never cleared by a wide
  enough margin. `holdout-pressure` margin kept drifting up slowly
  (7.071 → 7.075+), same already-disclosed situation.
- **`boldness-scan`, a new read-only diagnostic, shipped and run twice
  independently, converging on the same answer.** The weekend all-hands
  session (~06:05-07:30 UTC) built it to test whether capping the
  stagnation-driven boldness counter (currently unbounded, saturates past
  ~82 into full-genome random redraws) helps find better candidates. It
  found something more specific instead: a real shadow candidate that beat
  the champion's raw sealed-holdout fitness by +0.761 still failed the
  holdout gate, because `required_margin()` at 523 cumulative draws sits at
  7.076 — a challenger needs roughly **9x** the holdout edge any real
  candidate has produced so far before v3 can be replaced through the
  normal search path. Cross-checked against 27 real fold-aggregate winners
  that have reached the holdout and lost every time (margin 7.043→7.075
  across draws 493-522) — this is not a shadow-only artifact. A second,
  independent 3-hourly session (~06:46-07:37 UTC, same commit, unaware of
  the first run until push-time collision) re-ran the same diagnostic at 20
  generations/arm instead of 15 and got the same qualitative result: capping
  boldness shows no clear advantage over the unbounded/production behavior.
  Two draws, same read: **the bottleneck is the ever-rising holdout margin,
  not the boldness/search mechanism.** Full detail in
  `runs/2026-09-20-0600-weekend-all-hands.md` and
  `runs/2026-09-20-0737-boldness-scan-first-result.md`.
- `review-hard-calls` still 0 pending. Genome still v3, constitution
  manifest `726dfa4bac85891a` unchanged throughout.

## Does anything need the owner's decision?

**One item is worth raising, and it's new today, not a re-ask.** The
weekend all-hands write-up ends with a question it explicitly labels "the
owner's call" but which has not yet been added to the numbered "Owner
decisions pending" list above — it currently only exists as a sentence
inside a "Current state" log entry, which is where things go to be
forgotten once this file next rotates. Restating it plainly here so it
doesn't get lost:

`HOLDOUT_SIGMA` was set once, back on 2026-08-21, calibrated against the
sealed-holdout noise measured at that time. The multiple-testing correction
it feeds into is cumulative and never resets on a promotion — every
candidate ever tried against the current champion counts toward the bar,
forever, for as long as that champion stays undefeated. Two independent
diagnostic runs this weekend confirmed this is now the actual, dominant
force keeping v3 in place: not weak search, not boldness saturating, but a
holdout bar that has climbed to ~9x the best raw edge any real candidate
has produced in 27 tries. Nothing about the search process getting
better would change this — the margin's size depends only on cumulative
draw count, not on candidate quality. Left to run indefinitely, the bar
keeps rising and any future champion will face this same, worse problem
after enough evolve cycles.

This is not a bug and not something a scheduled session should decide
alone: whether `HOLDOUT_SIGMA`'s never-resetting cumulative design is the
intended, permanently-conservative behavior (accept it, keep disclosing the
drawdown-gate situation as already agreed on 2026-09-08), or whether it
warrants a design pass on a decay/reset mechanism (e.g., resetting the
draw count on some cadence, or scoping it per some rolling window instead
of the champion's entire undefeated lifetime) is a real risk-appetite call
about how conservative the promotion bar should be allowed to become over
time — exactly the kind of constitution-adjacent question this file's
protocol reserves for the owner, not a thing to quietly decide via more
diagnostics. Recommend a future session (or the owner directly) add this
as a proper numbered item under "Owner decisions pending" the next time
that section is touched, rather than leaving it buried in the 2026-09-20
weekend all-hands log entry.

The two previously-standing items are unchanged, not re-escalating, just
noting no movement:

- Item 6 (equities/FX data source) — still open, `.env.example` still
  stages unused Alpaca credentials with zero references in code, still
  waiting on a human to confirm Alpaca or name an alternative.
- Item 5's short-open question (whether/how a consult may *open* a short,
  distinct from the shipped cover/close path) — still genuinely unscoped,
  nothing new this cycle.

## Next

No action taken this session beyond this note (read-only check-in, as
intended for this slot). Scheduled sessions continue live tick handling,
real `evolve` against the live champion, and diagnostics as usual. The
`HOLDOUT_SIGMA` calibration question above is now flagged in two places
(this note and the 2026-09-20 weekend all-hands "Current state" entry);
it stays open until the owner weighs in, same as items 5 and 6.
