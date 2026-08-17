# Hard-call trigger narrowing attempt — 2026-08-17 3-hourly check

## Context

`AGENTS.md` item 4 ("LLM-backed consults") flagged a sharper next step after
the 12:54 run measured the as-shipped `flag_hard_call` firing on 38.6% of
logged bars, almost entirely via the `low_agreement_buy` trigger — which is
mechanically "exactly one of three consults proposed this buy" (agreement
discretizes to 0/0.33/0.67/1.0 with 3 consults), a pattern `lone_voice_scale`
already prices in, not a rare disagreement. The suggested next step: "narrow
the trigger set first (drop low-agreement-buy entirely, or replace it with
something that isn't a simple share-of-3 threshold — e.g. only fire when a
lone-voice buy is *also* the highest-conviction/largest order that bar) and
re-run `hard-calls` to see what rate that leaves."

This run implemented the "replace it" option and measured the result.

## What changed

`agents.judges.flag_hard_call` previously took a bar-level aggregate
`agreement_score` (the mean `agreement` across every order in the bar,
buys and sells together) and flagged any bar with a live buy where that
average fell below 0.4. Two problems with that: it's a bar-wide average, not
a property of the buy itself, and every `Order` already carries its own
`agreement` field (the consult-share that produced it) — the aggregate was
throwing that away.

New signature: `flag_hard_call(orders, just_halted, overrides_this_bar,
low_agreement_threshold=0.4)` — `agreement_score` is gone. The low-agreement
trigger now reads each buy order's own `agreement`, finds the bar's
highest-conviction buy, and fires only if *that* order is also lone-voice
(`agreement < threshold`). `summarize_hard_calls`'s category matching updated
to the new reason-string prefix (`"lone-voice buy"` instead of `"low consult
agreement"`); the call site in `loop.engine.Council.tick` updated to the new
signature. `tests/test_hard_calls.py` updated: all `flag_hard_call` calls
adapted to the new signature, one test renamed/rewritten
(`test_lone_voice_highest_conviction_buy_is_a_hard_call`) plus a new test
(`test_lone_voice_buy_is_not_a_hard_call_when_not_the_conviction_leader`)
asserting the actual narrowing behavior: a lone-voice buy sitting next to a
stronger, better-agreed buy the same bar should *not* flag. Full suite:
50 passed (up from 49).

Purely additive to what already shipped 2026-08-17 — same guarantees as
before: computed strictly after `Trader.execute()`, cannot change what gets
traded. Verified live path unaffected: `evotrader_bundle.py summary`
still reports `constitution verified dfae6a697f51fb49` and the same NAV/
positions as before this change; `live_state.json` untouched (git status
confirms — only `evotrader_bundle.py` and the test file changed).

## Result: the narrowing did not narrow anything — the rate went UP

Re-ran `evotrader_bundle.py hard-calls` against the real champion v3,
full-history replay (1,386 logged bars, same replay as the 12:54 run):

| | old (bar-aggregate share-of-3) | new (per-order, highest-conviction) |
|---|---|---|
| `low_agreement_buy` | 455 (32.8%) | 643 (46.4%) |
| total flagged | 535/1386 (38.6%) | 721/1386 (52.0%) |
| `circuit_breaker` | 4 | 4 (unchanged, different trigger) |
| `superior_override` | 85 | 85 (unchanged, different trigger) |

The rate got *worse*, not better. Diagnosed why with a one-off script
grouping decision-log bars by how many buy orders they contain:

| buy orders that bar | # bars | # flagged as lone-voice+leader |
|---|---|---|
| 0 | 488 | — |
| 1 | 448 | 327 (73%) |
| 2 | 273 | 201 (74%) |
| 3 | 140 | 117 (84%) |
| 4 | 42 | 34 (81%) |
| 5 | 9 | 8 (89%) |

The mechanism: "lone-voice" and "highest-conviction buy that bar" are not
independent axes in this system — they're strongly *correlated*, not
orthogonal. When a bar has exactly one buy order, that order is trivially
both the lone voice and the leader (no second order to be beaten by), which
is ~73% of any-single-buy bars already. And even in multi-buy bars, the
top-conviction buy is still lone-voice most of the time (74-89% across 2-5
buy orders) — a single confident consult's pick often outranks weaker
unanimous/two-agree proposals on raw conviction. The old bar-aggregate
version diluted this by averaging in sell orders' (typically higher)
agreement, which accidentally suppressed some of these bars below the 0.4
cutoff; reading the buy's own agreement directly removes that dilution and
exposes more of them.

**This is a real, useful negative result, not a wasted change.** It answers
the roadmap's open question directly: "highest-conviction/largest order that
bar" is not a discriminating filter here, because it's nearly synonymous
with "the only buy that bar" in a system where only one consult typically
proposes any single symbol. A future narrowing attempt needs an axis that
is *not* correlated with lone-voice status to actually shrink the set —
candidates worth trying next: position size relative to the rest of the
portfolio (not just conviction, which is an input to size but not the same
number), requiring the bar to have *zero* corroborating signal from any
other symbol too (not just this symbol), or accepting that low-agreement-buy
doesn't decompose cleanly and dropping it outright — leaving
`circuit_breaker` + `superior_override` ≈ 89/1386 (6.4%), the same
human/LLM-reviewable rate already measured in the 12:54 run, as the
practical trigger set for whichever of design (a)/(b) gets picked next.

## Not attempted this run

Did not implement "apply consult verdict" (the harder half of item 4) —
still blocked on the same (a)-vs-(b) architecture decision from the 12:54
run note, now with two narrowing attempts' worth of evidence behind it
instead of one. Did not try the size-relative-to-portfolio or
zero-corroboration-anywhere variants suggested above — next session's move
if this line is still worth pursuing.
