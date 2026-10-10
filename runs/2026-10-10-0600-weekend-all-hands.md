# Weekend all-hands — 2026-10-10 06:00 UTC

Deep-focus session. Two things this cycle: a quantitative design pass on item
13 (the `HOLDOUT_SIGMA` cumulative-margin calibration question, open since
2026-09-20 and explicitly flagged as "needs the owner's read on risk
appetite, not more evidence-gathering"), and one larger real `evolve` batch
(40 generations, vs. the 3-hourly checks' usual 15) run concurrently in the
background.

## Why item 13, not another routine evolve batch

The last several weeks of 3-hourly checks have been a long, repetitive
sequence of 15-generation `evolve` batches against the live v3 champion,
every one finding nothing (fold-aggregate fitness has sat flat for weeks;
see the chronological "Current state" log in `AGENTS.md`). Item 13 is the
one open question that actually explains *why* — and it's been sitting
unaddressed for three weeks (flagged 2026-09-20, still untouched as of this
morning) despite being named the dominant force keeping v3 in place. The
weekend's extra time budget is better spent making that decision easier for
the owner than running a 41st identical evolve batch that the weekday
sessions already do to exhaustion.

Important ground rule respected: item 13's own text says "do not decide this
via more diagnostics ... this needs the owner's read on risk appetite." This
session does **not** decide it and does **not** touch `constitution/__init__.py`
(one of the two files `constitution.checksum()` hashes — any real change
needs a human re-seal in hand first, same standing rule item 5 hit and
reverted from on 2026-08-30). What follows is read-only analysis to make that
decision easier, not an attempt to make it.

## The quantitative picture

`required_margin(n, sigma=HOLDOUT_SIGMA)` = `HOLDOUT_SIGMA * sqrt(2 * ln(n))`,
`HOLDOUT_SIGMA = 2.0`. Confirmed directly against the live numbers:
`holdout-pressure` right now reports cumulative draws `n = 1198`, margin
`7.530` — matches the formula to 3 decimal places. Three weeks ago
(2026-09-20) it was `n = 523`, margin `7.076`. That's ~34 draws/day, and if
that rate holds under status quo (no reset/cap/decay, the current design):

| when | n (projected) | margin | Δ vs today |
|---|---|---|---|
| today | 1,198 | 7.530 | — |
| +30d | ~2,210 | 7.849 | +0.32 |
| +90d | ~4,236 | 8.174 | +0.64 |
| +6mo | ~7,273 | 8.434 | +0.90 |
| +1yr | ~13,517 | 8.723 | +1.19 |
| +2yr | ~25,836 | 9.015 | +1.49 |

That's the growth the item's own framing already flagged. What hadn't been
quantified yet is **how much any specific bounded alternative would actually
help** — and the answer is less than the framing implied:

| design | margin | margin ÷ best raw holdout edge ever seen (1.095, draw 1183) |
|---|---|---|
| status quo (n=1198) | 7.530 | 6.88x |
| rolling window, last 1000 draws | 7.434 | 6.79x |
| rolling window, last 500 draws | 7.051 | 6.44x |
| rolling window, last 200 draws | 6.510 | 5.95x |
| rolling window, last 100 draws | 6.070 | 5.54x |
| full periodic reset (n=2, the formula's own floor) | 2.355 | 2.15x |

(`1.095` is the largest `challenger_holdout − champion_holdout` of any of the
28 real fold-aggregate winners `holdout-pressure` has on record against v3 —
the best this champion has ever actually been beaten by on the metric that
matters, before the margin is even applied.)

**Reading**: the `sqrt(log n)` correction is a famously slow-growing
function, and that cuts both ways. It means the status-quo design's future
growth is genuinely mild (+1.19 even after a full year at the current draw
rate) — this is not a runaway number heading somewhere catastrophic. But it
also means capping or windowing `n` barely moves today's bar: even an
aggressive last-100-draws window only brings the requirement from 6.9x down
to 5.5x the best edge ever found. Only a full reset to the statistical floor
(`n=2`) gets meaningfully close to parity — and that's the exact move the
constitution's own docstring already argues against by name ("resetting it
is exactly what a mined holdout would look like from the inside").

So the honest update to item 13's framing: **the margin side of this
equation has much less headroom than "9x the best edge" suggested on its
own** — no bounded, principled design short of the explicitly-rejected full
reset gets the ratio below roughly 5.5x. The real reason nothing has cleared
the gate in 1198 cumulative draws is close to "search hasn't found a
genuinely much-better genome yet," not "the gate's bookkeeping is
unreasonable." This doesn't close the question — whether to adopt a bounded
rolling window anyway, purely on the principle that an un-resettable,
indefinitely-growing correction is bad hygiene even if it rarely binds in
practice, is still a real risk-appetite call for the owner, not this session.
It does mean that call should be made knowing a rolling window is a modest
hygiene improvement, not something likely to unlock a promotion by itself.

## Recommendation (not a decision)

1. **Don't touch `constitution/__init__.py` without the owner's sign-off** —
   unchanged from the standing rule.
2. **If/when the owner decides**, the three live options, now with their
   actual effect sizes attached:
   - Status quo: simplest, mildest actual growth rate, consistent with the
     "resetting would look like a mined holdout" argument already in the
     docstring. Costs nothing new; the number nobody likes is already
     disclosed on the dashboard (per the 2026-09-08 drawdown-caveat
     precedent).
   - Rolling window (e.g. last 1000-2000 cumulative draws): bounds worst-case
     growth over years without fully discarding the selection-bias logic.
     Changes almost nothing today (7.434 vs 7.530 at K=1000) — this is a
     "guard against the far future," not a near-term unlock.
   - Full/periodic reset: explicitly warned against by the code it would
     change; not recommended.
3. No code shipped this session. `AGENTS.md`'s item 13 updated with this
   analysis so the next session (or the owner) has the numbers in hand
   rather than re-deriving them.

## Evolve batch (background, concurrent with the above)

Ran a larger-than-usual real `evolve` batch (40 generations, vs. the
3-hourly checks' standard 15) against the live v3 champion via
`tools/background_runner.py`, started before the analysis above and
collected after it, ~35 minutes wall-clock. Result: no promotion. Champion's
fold-aggregate fitness held flat at 1.864 across all 40 generations (988
trades, 40% win, 1% stops, 3 halts, unchanged throughout) — the same reading
the item-13 analysis above would predict: best-of-generation fold-fitness
ranged roughly 1.578-2.538, cumulative candidates tried against v3 rose
57840 → 58393 (`researcher_memory.tested`), stagnation/boldness counter 4180
→ 4219. `holdout-pressure`'s cumulative sealed-holdout draw count moved 1198
→ 1201 (3 new draws this batch, all lost), margin 7.530 → 7.532 — matching
the design-pass projection almost exactly (+30d was projected at +0.32 for
roughly 1000 new draws; 3 draws moving it +0.002 is consistent).

Verified before commit: `python3 -m pytest -q` 465/465 both before (baseline,
right after the item-13 commit) and after `evolve`; top-level key diff of
`live_state.json` (checked directly in Python against `git show
HEAD:live_state.json`, not just eyeballed) showed only
`updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
hard_call_reviews byte-identical); `lineage` length unchanged at 202 (bounded
ring buffer, no new promotion attempt recorded — this is also why
`holdout-pressure`'s "individual sealed-holdout draws" count against the
*current* champion read 26 instead of growing past 28: older generations
rolled off the ring buffer as new ones were added, the cumulative draw
counter itself is unaffected and lives in `researcher_memory`, not
`lineage`); `tools/edit_bundle_module.py verify`/`sync --check` both clean.
Dashboard rebuilt with `EVO_STATE` set (`index.html` shows 58393 challenger
idea(s) tried). Genome still v3 (1d) live, untouched.
