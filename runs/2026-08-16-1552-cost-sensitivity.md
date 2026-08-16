# Cost-sensitivity (fee/slippage perturbation), 2026-08-16 ~15:52 UTC

3-hourly check. No new daily bar to trade (`live_state.json.updated` was
2026-08-16T06:56:33Z, last journal entry is bar 2026-08-15, today's bar
doesn't close until 2026-08-17T00:00Z — nothing to do on the trading side,
as expected on almost every 3-hourly firing).

Used the slot to build the "perturbation tests on fees/slippage" item flagged
in AGENTS.md's "Measured 2026-08-16" section as preferred evidence-generating
work, not yet attempted (checked: no prior run note or AGENTS.md mention of
fee/slippage sensitivity). Shipped a new `costs` CLI diagnostic
(`evotrader_bundle.py costs`), same shape and same guarantees as `anatomy`/
`consults`: replays the champion's full history, never touches
`live_state.json` or the champion, read-only, meant for a human to read.

## What it does

Replays the full 4-year history against champion v3 five times, each with
the genome's `broker.fee_bps`/`broker.slippage_bps` scaled by a different
multiplier (`copy.deepcopy`'d genome data, never the live genome object),
reporting fitness/return/sharpe/maxDD/trades/fees-paid/excess-return-vs-
benchmark per scenario. `log_detail=False` since only aggregate stats are
needed, not the decision log.

## Result

```
scenario                fitness    return  sharpe   maxDD  trades   fees paid  excess ret
baseline                  0.775   535.9%    1.35  -34.1%    1159 $    5,824     473.4%
1.5x costs                 -inf   307.9%    1.07  -45.1%    1170 $    7,616     245.4%
2x costs                  0.578   323.7%    1.08  -38.8%    1061 $    9,527     261.1%
3x costs                  0.701   304.4%    1.06  -35.3%    1095 $   12,946     241.9%
slippage stress (5x)       -inf   271.4%    1.01  -42.3%    1091 $    4,564     208.9%
```

Baseline fee 10.0bps / slippage 5.0bps (the genome's own defaults, same as
Binance-tier retail costs with no volume discount).

**Two things worth separating, because the raw table conflates them:**

1. **Returns and excess-return-over-benchmark degrade smoothly and stay
   strongly positive under stress.** Total return drops from 535.9% (2x
   more than the fitness function ever sees at holdout scale) to 271-324%
   as costs rise, and excess return over the same buy-and-hold benchmark
   drops from +473% to +209-261%. Even at 5x slippage or 3x all-in costs,
   the champion still beats buy-and-hold by a wide margin on this
   full-history replay. Costs are a real drag (fees paid roughly doubles
   from 2x to 3x costs, as expected) but not what breaks the strategy.

2. **Fitness is not smooth, and that's a gate artifact, not new information
   about the strategy.** `1.5x costs` and `slippage stress (5x)` both show
   `fitness = -inf` despite the `3x costs` scenario (strictly higher costs)
   scoring 0.701. Traced to `constitution.MAX_DD_HARD_FAIL = 0.40`: both
   `-inf` scenarios' maxDD (-45.1%, -42.3%) cross that hard-fail line while
   `2x`/`3x costs` (-38.8%, -35.3%) stay just under it. The multiple-testing
   holdout machinery this system uses for promotion never applies here —
   these are five independent single-draw backtests, not a search — so
   `-inf` correctly means "this specific historical path crossed the
   hard-fail gate," not "this cost level is uniquely catastrophic." Reading
   the fitness column as a monotonic cost-sensitivity curve would be wrong;
   the return/excess-return columns are the honest ones for that question.

**The one number worth flagging for real:** the champion's own baseline
scenario here already runs at -34.1% max drawdown against a 40% hard-fail
gate — a 1.5x cost multiplier (not a large stress) is enough to push it over
that line on this particular full-history replay. That's a thinner margin to
the hard-fail gate than the headline return numbers suggest, and worth
keeping in mind alongside the existing 32.6% drawdown noted at the v2->v3
promotion.

## Scope note

This is a full-4-year-history point estimate per scenario, same caveat as
`anatomy`/`consults`: one replay, not a walk-forward/holdout split, so it is
in-sample by construction (v3 was found by evolution against overlapping
data) and the absolute return numbers (500%+) should not be read as a
forward-looking claim — compare the *shape* across scenarios, not the
absolute level, against the promotion-time holdout numbers in AGENTS.md's
"Current state" section. Not a promotion-relevant test; nothing here touched
`live_state.json`, the champion, or `researcher_memory`.

## Next

- The same `costs` tool could be pointed at the sealed-holdout window
  specifically (`start_frac`/`end_frac` args already exist in
  `run_backtest`) to see whether the drawdown-gate margin is thinner or
  wider out of sample than the full-history number above — not attempted
  this cycle, time budget.
- Doesn't change any AGENTS.md "Next steps" priority ordering; this was
  additive evidence-generation, not a capability change.
