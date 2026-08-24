# Selection noise, batch 2: more draws weaken the signal, not strengthen it — 2026-08-24 ~18:57 UTC

Scheduled 3-hourly check. Today's daily bar was already handled by the 00:20
UTC run (`live_state.json` `updated` 2026-08-24T00:22:01+00:00, genome version
still 3, md5 `0b628cf88674a6de938b4a806f33cf70` unchanged before, during, and
after this session) — nothing new to trade this cycle. `review-hard-calls`
still 0 pending.

Picked up the explicit loose end the 16:15 UTC `selection-noise-diagnostic`
run left open: "more draws to sharpen the significance" on the winner's-curse
question (does a fold-aggregate winner's sealed-holdout score run
systematically worse than a candidate that merely existed in the same batch).
That run got t≈1.55 at n=6, directionally consistent with a selection-noise
effect but short of conventional significance, and named "more draws" as the
natural next step over a second champion or a constitution change (both
bigger asks than a first replication deserves).

## Method

Same method exactly, transcribed fresh (script lived in the previous
session's scratchpad, not the repo, so not reusable directly) — see
`runs/2026-08-24-1615-selection-noise-diagnostic.md`'s "Method" section for
the full description. 6 more independent draws against the same real
champion v3 and real market data, `n_blind=10`, `exclude` accumulated across
draws (the methodology fix the first session had to make already baked in
this time). Each draw: fold-aggregate-winner vs. one uniformly-random
non-winning candidate from the same batch, both run through
`Evaluator.holdout_check` (not just the winner, which is all a real
`generation()` call would ever do).

## Result: batch 2 alone reverses the direction; combined 12-draw sample is *weaker* than batch 1 alone

| draw | n | winner fold | winner holdout | winner gap | random fold | random holdout | random gap |
|---|---|---|---|---|---|---|---|
| 0 | 21 | 1.556 | −1.268 | +2.824 | 1.125 | −2.081 | +3.206 |
| 1 | 10 | 1.246 | −0.210 | +1.456 | −2.517 | −1.159 | −1.358 |
| 2 | 10 | 1.470 | −0.140 | +1.611 | 0.800 | −1.609 | +2.409 |
| 3 | 10 | 1.412 | −0.006 | +1.418 | 1.084 | −2.034 | +3.117 |
| 4 | 10 | 1.245 | −0.201 | +1.447 | 0.564 | −0.843 | +1.408 |
| 5 | 10 | 1.181 | −0.140 | +1.321 | 0.997 | −1.129 | +2.126 |

Batch 2 winner gap: mean **+1.679**, std 0.568, n=6. Batch 2 random gap: mean
**+1.818**, std 1.692, n=6. This time the *random* pick's fold-to-holdout
drop is larger on average than the fold-selected winner's — the opposite of
batch 1's direction and of the winner's-curse hypothesis. Paired t on batch 2
alone: −0.218 (not significant, wrong sign).

Combining both batches (n=12, the only honest way to use "more draws" —
independent draws from the same method against the same champion, not a
different question): winner gap mean 1.926 (std 0.778), random gap mean 1.404
(std 1.492), paired diff mean +0.521, **paired t ≈ 1.02 at df=11** — weaker
than batch 1's t≈1.55 alone, not stronger. Doubling the sample size moved the
result further from significance, not closer.

**Reading**: this is a real negative update, not a null result to shrug off.
If the winner's-curse effect were real and batch 1's n=6 had simply been too
small to detect it cleanly, more draws should have *tightened* the estimate
around a positive mean and pushed t up. Instead batch 2's random-gap variance
came in much higher (std 1.692 vs batch 1's 1.274) driven by one outlier draw
(draw 1's random gap −1.358, the only negative gap either batch has produced),
and batch 2's own winner-vs-random comparison went the other way. The most
defensible read after 12 draws: **there isn't yet good evidence of a
winner's-curse selection effect distinct from ordinary per-candidate holdout
noise** — batch 1's t≈1.55 looks more like a favorable draw from a
noisy small-sample distribution than the leading edge of a real, sharpenable
signal. This doesn't rule out a real effect existing at a magnitude too small
to see in 12 draws, but it removes the "just needs more data" framing batch 1
left open — the next unit of evidence here has diminishing, not increasing,
value at this per-draw cost (~10 min/6-draw batch). Not translating this into
any `HOLDOUT_SIGMA`-style correction — the evidence doesn't support one, and
even a confirmed effect would need its own `AMENDMENTS.md` argument this
finding doesn't earn.

Leaving this question here unless a future session has a specific reason to
revisit it (e.g. a cheap way to run an order of magnitude more draws, or
testing a second champion) — further identical-method batches are unlikely to
resolve it either way given batch 2's own variance blowup.

## Verified safe

- `git status --short` clean before and after (script lived in the session
  scratchpad, not the repo; only `state/cache/`, gitignored, touched by real
  market-data pulls and backtests).
- `live_state.json` md5 unchanged throughout (`0b628cf88674a6de938b4a806f33cf70`).
- Full test suite: 235 passed (no code changed this session, baseline sanity
  check).
- `review-hard-calls` still 0 pending. No genome promotion anywhere real, so
  no README Status staleness.
- Total diagnostic compute: ~10 minutes wall time for the 6-draw batch, plus
  ~2.5 minutes for the full test suite baseline.

No push notification — a read-only research finding (this time a negative
one) with zero effect on live trading behavior, same threshold every prior
diagnostic-only 3-hourly session in this history has used.
