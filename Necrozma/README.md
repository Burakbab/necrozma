# Necrozma

A self-evolving trading system. Paper money only, for now.

The prime directive: grow capital on a risk-adjusted basis without a human in the
loop, and get measurably better over time by rewriting its own agent roster.

## The one idea that matters

A system allowed to modify itself will, given the chance, learn to modify its own
scorecard rather than learn to trade. So the architecture is split into two halves
that are deliberately **not** symmetric:

| | Mutable | Who can change it |
|---|---|---|
| **Strategy layer** (agents, params, routing, universe) | yes | Superior Judge only, on evidence |
| **Constitution** (broker, evaluator, fitness function, safety gates) | **no** | Burak only, by hand |

The Researcher may propose anything about the strategy layer. It is structurally
incapable of touching the thing that grades it. That asymmetry is what makes the
system safe to leave running.

`constitution.py` is checksummed at every startup against `evotrader.manifest`.
If the fitness function or the gate logic moved, the run refuses to start.

## Org chart

```
market data ──► ANALYST ──► Briefing
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
        RISKY CONSULT   MODERATE CONSULT  CONSERVATIVE CONSULT
              └───────────────┼───────────────┘
                              ▼
                     RISK JUDGE (minor)      aggregate, size, veto
                              ▼
                     SUPERIOR JUDGE          hard limits, circuit breaker
                              ▼
                     TRADER ──► PAPER BROKER ──► ledger

── evolution track ──────────────────────────────────────────────
   RESEARCHER ──Mutation──► EVALUATOR ──Evidence──► SUPERIOR JUDGE
   (proposes)               (walk-forward)          (commit / reject)
```

The three consults are not one strategy with a risk dial in three positions —
they are three different theories of where money comes from (momentum, mean
reversion, confirmed trend). If they were correlated, their agreement would carry
no information and the Risk Judge's whole job would be reading noise.

## Layout

```
constitution.py        fitness, acceptance gates, integrity check — LOCKED
core/
  types.py             frozen dataclass message contracts between agents
  market.py            Binance public data, replay with no lookahead
  portfolio.py         paper broker + accounting — LOCKED
  genome.py            the mutable policy document
  live.py              live paper trading, durable state
agents/
  analyst.py           the only agent that touches raw candles
  consults.py          risky / moderate / conservative
  judges.py            RiskJudge (minor) + SuperiorJudge (final)
  trader.py            Guardian forced exits + dumb executor
  researcher.py        proposes mutations; has no authority
loop/
  engine.py            the decision cycle + backtest
  evolve.py            walk-forward folds, sealed holdout, promotion
```

## Running

```
python evotrader_bundle.py tick        # one live paper tick, real prices
python evotrader_bundle.py summary     # account status, no trading
python evotrader_bundle.py evolve 5    # 5 generations of self-improvement
```

## Status

v0.1 — deterministic genome-driven agents, real historical data, paper broker,
full decision log. See `docs/design.md` for the acceptance rules, the amendment
log, and the roadmap.

Real money is gated behind six months of positive walk-forward, a live paper run
that matches its own backtest within tolerance, and explicit sign-off. The system
cannot promote itself.
