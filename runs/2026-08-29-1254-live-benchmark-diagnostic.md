# live-benchmark diagnostic — 2026-08-29 12:54 UTC (3-hourly check)

## Why

Today's earlier three sessions (06:00 weekend all-hands, 06:59
promotion-excess-check, 10:17 candidate-excess-shadow-check) all measured the
raw-fitness-vs-excess-return question by replaying **backtests** — real
champions or real shadow-search candidates re-run against history. None of
them looked at the one number that isn't a replay at all: what the live paper
account's own real, already-executed fills actually returned since inception,
next to an equal-weight buy-and-hold of the same universe over the identical
real calendar window.

The dashboard's "Honest caveats" panel has asserted, as static hand-written
prose since it was written, that "it has lost less than the market did over
the same stretch" — nothing in the codebase actually computed that
comparison from real data. This session built the diagnostic that does.

## What shipped

New read-only CLI command `python3 evotrader_bundle.py live-benchmark`,
added to `evotrader_bundle.py`'s own CLI dispatch (not a `_SRC` module —
same precedent as `succession-audit`/`promotion-excess-check`). It:

- Reads `acct.broker.nav_history` (already on disk, no new data needed for
  the live side).
- Fetches the current champion's universe via `core.market.load_universe`
  (the same call every other diagnostic makes) and finds the two bar indices
  in `Replay` matching the account's first and last recorded nav dates.
- Calls the already-tested `loop.engine.benchmark_buy_hold` over that exact
  window with the account's real `start_cash`.
- Prints live vs. benchmark return/sharpe/maxDD, the excess, and two
  caveats: (1) whether the real journal shows more than one genome version
  traded during the window (it does here — see below), and (2) sample size
  / fee asymmetry (benchmark has no ongoing fees to charge; the live number
  is already net of every real fee/slippage cost paid).

Composes only already-tested primitives (`market.load_universe`, `Replay`,
`benchmark_buy_hold`) — no new pure function, no engine or constitution
change. Never touches `live_state.json`: verified `md5sum` unchanged before
and after. `tools/edit_bundle_module.py sync --check` clean (new code lives
in the bundle's own CLI section, exactly where `succession-audit` and
`promotion-excess-check` live). Full suite: `python3 -m pytest -q`.

## Real numbers, first run

```
LIVE ACCOUNT vs. EQUAL-WEIGHT BUY-AND-HOLD, 2026-08-14 to 2026-08-28 (14 1d bar(s))
                            return   sharpe    maxDD
  live paper account      +12.27%     6.12    -3.0%
  buy & hold (universe)   +20.15%     6.38    -5.7%
  excess (live - b&h)      -7.88%
```

The live account **trails** buy-and-hold by 7.9pp over its real 14-bar life
so far — the first real (not backtested, not shadow-searched) data point on
the exact question today's earlier sessions have been chasing via replay.
Directionally consistent with the weekend all-hands' mechanistic finding
(sealed-holdout fitness dominated by absolute return, weak/negative
correlation with excess return for 2 of 3 real champions) and with today's
10:17 UTC finding (disagreement between the two criteria is real, if a
near-tie so far) — but this is the account's own actual money-on-the-table
number, not a replay of either.

**Real caveat, not a footnote**: the account traded under genome v1 (day 1),
v2 (day 2), then v3 (days 3–15, 86.7% of the window) — two promotions
happened mid-window. This is not a clean single-genome test; it's the
account's genuine realized history including the transition costs and
early mistakes of the evolution process itself, which is arguably the more
honest number for "how has this system actually done" but the wrong number
to cite as "how has champion v3 done." The diagnostic prints this caveat
automatically whenever more than one version appears in the real journal.

Also only 14 daily bars — far too short to be a verdict either way, and it
will keep growing for free every day the account keeps trading; re-running
`live-benchmark` costs one market-data fetch and is worth doing periodically
alongside the daily-discussion check-in, the same way `holdout-pressure`
and `succession-audit` already are.

## What this does NOT do

Purely descriptive — like every other diagnostic in this file, it feeds no
gate, changes no acceptance rule, and does not touch the still-open
"should the selection metric be redefined around excess return" question,
which stays the owner-level design decision flagged in the 09:00 UTC daily
discussion and the 10:17 UTC entry before it.

## Next

Worth a periodic re-run (weekly-ish) as the live account's real history
grows — the excess-return gap should either persist, narrow, or flip as more
real bars accumulate, and that's a genuinely different signal from anything
a backtest or shadow search can produce. Not wired into the dashboard this
session (would require a network fetch on every dashboard rebuild, which
happens far more often than this is worth computing fresh) — a cheap
follow-up if this stays valuable: cache the last `live-benchmark` result
somewhere the dashboard build can read without its own market fetch.
