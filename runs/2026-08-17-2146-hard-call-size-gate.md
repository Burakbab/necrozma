# Hard-call size gate — 2026-08-17 21:46 UTC (3-hourly self-improvement check)

## Context

`AGENTS.md` item 4 (LLM-backed consults, "flag hard calls" half) had one
remaining untried narrowing candidate after two prior 3-hourly runs today:

- 38.6% (original low-agreement trigger)
- 52.0% (candidate: highest-conviction-that-bar — backfired,
  `runs/2026-08-17-1553-hard-call-trigger-narrowing.md`)
- 24.4% (candidate (ii): solo bar — worked,
  `runs/2026-08-17-1850-hard-call-solo-bar-narrowing.md`)
- candidate (i), not yet tried: size relative to portfolio equity, composed
  on top of the solo-bar requirement rather than replacing it.

## What changed

`agents.judges.flag_hard_call` gained two new optional parameters:

```
flag_hard_call(orders, just_halted, overrides_this_bar,
               low_agreement_threshold=0.4,
               nav=None, min_size_pct=0.0)
```

- `min_size_pct=0.0` (the default) reproduces the exact solo-bar-only
  behavior from the 18:50 run — purely additive, no existing caller's
  behavior changes unless it opts in.
- When `min_size_pct > 0`, a solo lone-voice buy only flags if
  `leader.quote_amount / nav >= min_size_pct` — i.e. the bet has to commit a
  real fraction of the account, not just be the bar's only order.
- If `min_size_pct > 0` but no `nav` is supplied, the gate fails safe (does
  **not** flag) rather than guessing — there's no way to compute the
  fraction without it.

`loop.engine.Council.tick`'s existing `flag_hard_call(...)` call now passes
`nav=nav, min_size_pct=0.10` — `nav` was already computed earlier in that
scope (used for `broker.mark`/the briefing), nothing new to thread through.

## Why 0.10

Ran the real live champion (v3) through a single full-history backtest
(`run_backtest(..., log_detail=True)`, the same call `hard-calls` makes),
then post-processed the existing decision log's solo lone-voice bars against
a grid of `min_size_pct` values without re-running the backtest per
threshold (each entry's logged `orders[].amount` and `nav` are enough to
recompute the fraction). Of 253 solo lone-voice bars, sizes ranged
continuously from 0.004% to 24.8% of equity, no natural break/cluster:

| `min_size_pct` | solo-lone-voice bars kept | approx. combined rate |
|---|---|---|
| 0.00 (off) | 253 (18.3%) | 24.4% |
| 0.03 | 80 (5.8%) | 11.9% |
| 0.05 | 70 (5.1%) | 11.2% |
| 0.08 | 58 (4.2%) | 10.3% |
| **0.10** | **48 (3.5%)** | **9.6%** |

0.10 was chosen as the value that cuts this trigger's own contribution
roughly 5x (18.3% → 3.5%) while still catching every bet that risks a real
slice of the account (double-digit percent of equity) — not a value tuned
to hit a specific target rate after the fact.

## Verification

- `tests/test_hard_calls.py`: 55 passed, up from 51. New cases: size gate
  off by default still flags a token-sized solo buy (backward compat), a
  big-enough solo buy (15% of nav, threshold 10%) flags with the size
  detail in the reason string, a too-small solo buy (5% of nav) does not
  flag, and no-`nav`-supplied-with-`min_size_pct`-set fails safe.
- Full suite: 55/55 passed.
- Live path unaffected: `evotrader_bundle.py summary` still reports
  `constitution verified dfae6a697f51fb49`; `live_state.json` md5 identical
  before and after (`30cea2ae0995aa3a73bb1c78bf9a75d9`).
- `evotrader_bundle.py hard-calls` against the real champion v3 reproduced
  the offline projection exactly: **133/1386 logged bars flagged (9.6%)**
  — `circuit_breaker` 4, `superior_override` 85, `low_agreement_buy` 48.
  Sample reasons now carry the size detail, e.g. "lone-voice buy on
  FILUSDT (agreement 0.33) is the only order the bar produced (0.88
  conviction, 12.1% of equity)".
- Live journal: still 0 flagged (all 3 real ticks predate the field, as
  before this change — nothing new to compare against yet).

## What this does and doesn't mean

This only changes what counts as a "hard call" for logging purposes — same
purely-additive guarantee as every prior step on this item (computed after
`Trader.execute()` has already filled the bar; `test_hard_call_computation_cannot_affect_execution`
still passes, confirming `log_detail` on/off produce byte-identical trading
outcomes). It does not build the "act on a flag" half of item 4.

9.6% is close enough to the ≈6.1% `circuit_breaker`+`superior_override`-only
floor that further narrowing has diminishing returns. The honest next step
on this item is the (a)-vs-(b) architecture decision AGENTS.md already
named (pause-mid-tick-and-resume vs. review-after-the-fact) — not another
narrowing pass.

## Also this run

- Session started with local `main` detached and diverged from a rewritten
  `origin/main` (same pattern the 20:30 daily-evaluation run flagged as a
  recurring one-off) — resolved with `git checkout main` +
  `git reset --hard origin/main`, no unique local commits lost.
- Confirmed via `live_state.json`'s `updated` timestamp (`2026-08-17T00:26:31Z`)
  and `runs/2026-08-17-0020-daily-trading.md` that today's daily bar was
  already handled by the 00:20 UTC scheduled run — did not run `tick` this
  cycle.
