# Hard-call trigger narrowing: "solo bar" requirement

3-hourly self-improvement check. Continues AGENTS.md item 4's open thread:
after the 2026-08-17 05:53-ish "highest-conviction" narrowing measured
*worse* (38.6% → 52.0%, `runs/2026-08-17-1553-hard-call-trigger-narrowing.md`),
that note left three untried candidates. Tried candidate (ii): "requiring
zero corroborating signal anywhere that bar", i.e. distinguish "the whole
council went quiet except one loud voice" from "one of several independent
picks that bar happened to be lone-voice".

## Change

`agents.judges.flag_hard_call`'s low-agreement trigger now requires the
lone-voice buy to be the bar's **only** order at all — no other buy, no
sell — not merely the bar's highest-conviction buy (which the prior
narrowing tried and which backfired because lone-voice and
highest-conviction-that-bar are strongly correlated: most bars with any buy
have exactly one). Signature unchanged
(`flag_hard_call(orders, just_halted, overrides_this_bar,
low_agreement_threshold=0.4)`). Purely additive/narrowing, same guarantees
as before: computed strictly after `Trader.execute()`, cannot change what
gets traded.

Tests (`tests/test_hard_calls.py`, 51 passed up from 50): replaced the two
conviction-leader-specific tests with three — a solo lone-voice buy still
flags, a lone-voice buy next to *another buy* doesn't flag (unchanged
behavior from before), and new: a lone-voice buy next to an unrelated
**sell** doesn't flag either (this is the case the old conviction-only logic
missed entirely, since it only ever looked at `buys`).

## Result

Re-ran `evotrader_bundle.py hard-calls` against the real champion v3,
full-history replay (1,386 logged bars):

| version | flag rate | low_agreement_buy | notes |
|---|---|---|---|
| original (bar-aggregate `agreement_score`) | 38.6% | 455 | 2026-08-17 measurement |
| highest-conviction narrowing | 52.0% | 643 | backfired |
| **solo-bar narrowing (this run)** | **24.4%** | **253** | real reduction |

`circuit_breaker` (4) and `superior_override` (85) unchanged, as expected —
this narrowing only touches the low-agreement trigger. 24.4% is a genuine
improvement over both prior versions — the first narrowing attempt that
actually reduced the rate instead of raising it — but it is still well
above the ≈6.4% floor that dropping `low_agreement_buy` entirely would give
(candidate (iii) from the prior run's list), so this alone doesn't settle
the (a)-vs-(b) architecture question from AGENTS.md item 4 yet: a
review-after-the-fact pass in (b) still can't comfortably cover roughly a
quarter of all bars.

Verified live path unaffected: `constitution verified dfae6a697f51fb49`,
`summary` NAV/`live_state.json` md5 identical before and after (this
diagnostic never writes state, but checked directly anyway since this was
a code change, not just a report run).

## Next

Candidate (i) from the prior run's list — size relative to the rest of the
*portfolio*, not just conviction within the bar — hasn't been tried yet and
composes with this change (both are independent narrowing axes on the same
trigger). If a future run tries it and the combined rate still doesn't
clear a workable threshold, candidate (iii) — drop `low_agreement_buy`
outright, keep only `circuit_breaker` + `superior_override` (~6.4%, already
known-workable) — is still the fallback the prior note flagged it as.
