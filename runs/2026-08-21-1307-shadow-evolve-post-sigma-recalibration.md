# Shadow evolve, 8 more generations past live researcher_memory — 2026-08-21 ~13:07 UTC

Scheduled 3-hourly check. Today's daily bar was already handled by the
00:20 UTC daily run (`live_state.json` `updated` at `2026-08-21T00:27:21Z`,
genome version still 3, no double-trade — `tick` not run this session).
`review-hard-calls` checked: 0 pending. The fold-windowing/capping thread
and the `MULTIPLE_TESTING_SIGMA`-adjacent `HOLDOUT_SIGMA` recalibration
(this morning's 09:51 UTC run) are both marked "no immediate follow-up" in
`AGENTS.md`, so this slot went to the one open loose end that recalibration
left: "worth a one-line note the next time a real promotion is evaluated,
on whether the tighter margin changed the outcome". No promotion was
pending to observe, so this run tried to manufacture one via further
blind search in an isolated shadow branch, to see if the new margin would
actually get exercised.

## Setup

Copied `live_state.json` (champion v3, real genome, real accumulated
`researcher_memory`, 182 candidates already tried against v3) to a scratch
directory outside the repo and ran
`EVO_STATE=.../shadow_state.json python3 evotrader_bundle.py evolve 8`
there — same 27-symbol, 1d-bar universe and real Binance data the live
account trades on, same constitution gates (including this morning's new
`HOLDOUT_SIGMA`), but writing only to the scratch copy. **Nothing here
touched the real `live_state.json`** — verified by md5 before and after
(`8b3dc413c9a85fda04bdeb0ad4c63733`, unchanged) and `git status --short`
clean throughout.

## Result: still deep stagnation, and the new HOLDOUT_SIGMA was never exercised

8 generations, ~19 minutes wall time (real backtest per candidate, no
cached shortcuts). Champion held at fitness 1.396 through every
generation; boldness climbed 12→19; cumulative candidates tried against
v3 in this shadow branch rose 182→294 (112 more than the live account has
ever tried). Per-generation best raw fold-aggregate fitness ranged
1.258–1.641 — generation 3's best (1.641) and generation 7's (1.462) both
*numerically beat* champion's 1.396, but neither cleared the
multiple-testing-adjusted acceptance bar (`required_margin()` scales with
`n_candidates`, now 224+ and rising), so **no candidate this run ever
reached the sealed-holdout check at all**.

That's the finding worth recording: the fold-aggregate multiple-testing
gate, not the sealed-holdout gate, is what's rejecting every candidate
right now. This morning's `HOLDOUT_SIGMA` recalibration only changes the
margin `holdout_accepts()` applies *after* a candidate clears the
fold-aggregate gate — it cannot have been exercised by any of this run's
294 candidates, because none of them got that far. The "does the tighter
holdout margin change a real promotion outcome" question from this
morning's entry is still open; it needs a candidate that actually clears
`accepts()` first, and 112 more blind-search draws past the live
account's own history didn't produce one.

## Why this matters

Consistent with `holdout-pressure`'s standing finding (13/13 real
fold-gate-clearing challengers have lost the sealed holdout since v3's
promotion) and every other stagnation-adjacent measurement already in
`AGENTS.md` — but this is the first run to show the *earlier* gate
(fold-aggregate multiple-testing, not sealed-holdout) is the one actually
binding right now, at this candidate count. As `n_candidates` keeps
rising with every generation (live or shadow), `required_margin()` keeps
raising the bar a raw-fitness winner has to clear before it's even
allowed to attempt the holdout check — a mechanical explanation for "why
hasn't the champion moved in a while" that doesn't require any of the
fold-windowing/regime hypotheses already explored and set aside.

Not chased further this run (would need either much deeper boldness/many
more generations, or a fresh researcher_memory reset to lower the
candidate count denominator — the latter would throw away real search
history and wasn't attempted). Nothing here changes anything about
whether the fold-windowing line should stay set aside; it's a
different, independent bottleneck.

**Not applied to the live account.** This 3-hourly slot is explicitly
scoped to shadow/offline work only.

## Verified safe

- No code changed — pure diagnostic use of the existing `evolve` CLI
  against an isolated scratch copy.
- `live_state.json` md5 identical before/after
  (`8b3dc413c9a85fda04bdeb0ad4c63733`).
- `git status --short` clean throughout.
- `constitution verified 8b74865634b1db07` on every invocation (the new
  checksum from this morning's recalibration, unchanged).
- Today's 2026-08-21 bar confirmed already processed by the 00:20 UTC
  daily run before this check started (`tick` not run this session, no
  double-trade).
- `review-hard-calls`: 0 pending.

## Next

Whoever next has a real (live or shadow) candidate that clears the
fold-aggregate gate should note whether the new `HOLDOUT_SIGMA` changes
the outcome vs. what the old value would have said — that's still the
open thread from this morning's recalibration, and this run didn't
produce the candidate needed to close it. Separately worth flagging: the
fold-aggregate gate itself getting mechanically harder to clear as
`n_candidates` grows is a new-ish observation, not previously called out
explicitly in this file's stagnation discussion — not proposing a fix,
just naming the mechanism for whoever looks at this next.
