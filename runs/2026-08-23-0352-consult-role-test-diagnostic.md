# Consult role-test diagnostic (3-hourly check)

Picked up the standing "Measured 2026-08-16" finding that has sat unactioned
since it was written: `anatomy`'s `by_entry_agent`/`by_exit_reason` breakdown
found `consult_conservative` was **-$8,159 as an entry signal (38% win)** but
**+$25,706 as an exit signal (89% win)** against whichever champion was live
that day — a bad buyer and an excellent seller. Nobody had tested the direct
implication: what happens if its buy intents are suppressed but its sell rule
is left exactly as evolution tuned it?

## What was built

New read-only CLI `evotrader_bundle.py consult-role-test [--also-version N]`
(`evotrader_bundle.py`, plain-script CLI section, zero `_SRC[...]` lines
touched). Runs one full-history (`[0, 1]`) `run_backtest` of a genome as-is,
then monkeypatches `ConservativeConsult.consider` for the duration of a
second `run_backtest` call so its buy intents are filtered out of the
`Proposal` it returns (its "mean reversion complete" sell rule is untouched),
restores the original method in a `finally` before the command returns.
Never persists anything, adds no gene, no mutation-range change, no
constitution touch. Composes only already-tested `run_backtest`/
`benchmark_buy_hold`/`fitness`/`_reconstruct_champion_genome`, same
"diagnostic only" precedent as every other CLI command in this file.

## Result: genome-dependent, not a fixed law

| genome | fitness (baseline → exit-only) | return | maxDD | trades |
|---|---|---|---|---|
| v1 (seed) | -inf → -inf | -11.8% → **-34.4%** (worse) | -54.3% → **-65.2%** (worse) | 1599 → 1544 |
| v2 | 0.183 → **0.584** (better) | +37.9% → **+76.8%** | -38.1% → **-29.9%** | 1612 → 1624 |
| v3 (live) | -inf → -inf | +125.4% → +125.6% (~flat) | -46.5% → -46.5% (~flat) | 1069 → 1065 |

v1: suppressing conservative's entries makes an already-failing genome worse
— it was net-additive there despite the 08-16 finding's framing, at least in
aggregate (the 08-16 anatomy breakdown was per-trade P&L attribution, not a
counterfactual replay; a bad-average-trade signal can still net-positive by
occupying capital that would otherwise sit idle or chase worse setups — this
result doesn't contradict that finding, it tests a different question).

v2: suppressing them is a large, clean improvement on every axis — fitness
more than triples, drawdown improves 8.2pp, and (surprisingly) trade count
goes *up* slightly rather than down, meaning other consults/positions
absorbed the freed cash/slots rather than the book just trading less. This
is the closest real evidence yet that the 08-16 finding pointed at something
real, at least for that genome.

v3 (the live champion, most tuned): the effect is essentially gone — 4
fewer trades out of 1069, fitness/maxDD/return all unchanged to the
precision reported. Reading: v3's own evolution history has already tuned
`consult_conservative`'s entry gate (`rsi_buy_below`, `z_buy_below`,
`min_trend`, `max_dd_from_high`) tight enough that it rarely fires as an
entry signal at all any more — the bad-buyer problem the 08-16 finding
flagged looks like it was mostly search-corrected already by the time v3
existed, not by design (nothing in the genome models "conservative should
be exit-only"), just as a side effect of 13+ generations of unrelated
parameter tuning after that finding was written.

## Verified safe

`py_compile` clean, `tools/edit_bundle_module.py verify` round-trip clean,
`git diff --stat` confirms a pure addition (84 insertions, 0 deletions,
zero `_SRC[...]` lines touched), full suite still 192 passed (unchanged —
no new pure function, just a CLI command composing existing ones),
`live_state.json` md5 identical throughout (`af16ffdc22a57c5d63a83003216a8f99`),
`evotrader.manifest` md5 unchanged (`0bf3a7d9411ee692d0a9f152a7533803`),
`constitution verified 8b74865634b1db07` unchanged on every invocation,
today's 2026-08-23 bar confirmed already processed by the 00:20 UTC daily
run before this session started (`updated` timestamp
`2026-08-23T00:22:00+00:00`, `tick` not run this session, no double-trade),
`review-hard-calls` checked (0 pending), no genome promotion (no README
Status change needed).

## Next

v3's near-zero delta means this isn't an actionable finding for the *live*
champion right now — building a real `entry_enabled`/exit-only gene and
running it through the real search would very likely just find what
tuning already found by other means. Not recommended as a next step on its
own. What *would* be worth doing, cheaply, next time evolution runs for real
against v3: watch whether any accepted future patch ever re-widens
`consult_conservative`'s entry gate (loosens `rsi_buy_below`/`z_buy_below`/
`max_dd_from_high`) — if it does, re-running `consult-role-test` at that
point is a one-line check for whether the bad-buyer problem has come back.
No push notification sent — this is exploratory evidence, not a safety
finding or an incorrect promotion.
