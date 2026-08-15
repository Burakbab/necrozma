# EvoTrader — Design

**Status:** v0.1 (paper money only)
**Owner:** Burak
**Prime directive:** grow capital, risk-adjusted, without a human in the loop — and get measurably better over time by rewriting its own agent roster.

---

## 0. The core problem this design solves

A system that is allowed to modify itself will, if you let it, learn to **modify its own scorecard** instead of learning to trade. Almost every naive "self-improving agent" fails this way: it overfits the backtest, deletes the agent that says no, and reports a beautiful equity curve that never survives contact with the future.

So the architecture is split into two halves that are **not** symmetric:

| | Mutable | Who can change it |
|---|---|---|
| **Strategy layer** (agents, params, routing, universe) | yes | Superior Judge only, on evidence |
| **Constitution** (broker, evaluator, fitness function, safety gates, this rule) | **no** | Burak only, by hand |

The Researcher is allowed to propose anything about the strategy layer. It is *structurally incapable* of touching the thing that grades it. That asymmetry is the whole reason this can be left running.

---

## 1. Roles

**ANALYST** — the only agent that touches raw market data. Converts a price history window into a `Briefing`: per-symbol features (trend, momentum, volatility, drawdown-from-high, volume shock) plus a market **regime** label. Everyone downstream reasons about the Briefing, never about raw candles. This is deliberate: it means a change to feature engineering is one gene, testable in isolation.

**CONSULTS (3)** — same input, three different temperaments. They are *not* three copies with a risk dial; they read different features and have different opinions about what a good trade is:

- *Risky* — momentum/breakout seeker. Wants to be in the strongest thing. Tolerates drawdown, high conviction, fewer positions.
- *Conservative* — mean-reversion and capital preservation. Wants oversold quality, exits fast, holds cash happily.
- *Moderate* — trend-following with confirmation. Wants agreement between trend and momentum before committing.

Each emits `Intent`s: symbol, direction, conviction ∈ [0,1], horizon, and a **rationale string** — the rationale is not decoration, it's the audit trail the Researcher later mines for patterns.

**RISK JUDGE (minor)** — the first filter. Sees all three proposals *and* the current portfolio. Its job: resolve disagreement, convert conviction into position size, and veto anything that breaks portfolio-level sanity (concentration, correlation, exposure, cash floor). Disagreement is information: unanimous = size up, split = size down, contested = often skip.

**SUPERIOR JUDGE** — final authority, two hats:

- *Trading hat:* hard constraint enforcement and the circuit breaker. Deliberately boring. It should almost never override the Risk Judge; if it does so often, that's a signal the Risk Judge's genes are wrong.
- *Evolution hat:* the **only** writer to the genome. Commits or rejects mutations against the acceptance rules in §4.

**TRADER** — dumb on purpose. Takes approved orders and executes them against the broker with realistic fees/slippage. No discretion. Keeping execution free of judgement means a bad fill is a broker-model bug, not a strategy question.

**RESEARCHER** — reads the ledger + decision log and proposes `Mutation`s to the genome: tweak a parameter, add an agent, delete an agent, rewire routing, change the universe. It may look at the web for *ideas about markets and machine learning*, but per Burak's instruction it does **not** copy human traders' playbooks — the hypothesis space is generated from the system's own data and from general principles, then judged empirically.

**EVALUATOR (minor judge for evolution)** — runs the challenger genome through walk-forward evaluation on data the Researcher's proposal was not derived from, and produces an `EvidencePack`. It never gets an opinion; it reports numbers.

---

## 2. Data contracts

Everything between agents is a frozen dataclass, logged to the decision log. Version them; never pass raw dicts.

```
Briefing   { ts, regime, symbols: {sym -> Features}, portfolio_snapshot }
Intent     { symbol, side, conviction, horizon_bars, rationale, agent, genes_used }
Proposal   { agent, ts, intents[], stance_note }
Verdict    { ts, orders[], vetoes[{intent, reason}], agreement_score, notes }
Order      { symbol, side, quote_amount, limit?, reason_chain[] }
Fill       { order, price, qty, fee, slippage_bps, ts }
Mutation   { kind, target, patch, hypothesis, proposed_by, ts }
EvidencePack { mutation, folds[], champion_stats, challenger_stats, verdict_inputs }
```

**Rule:** every order carries a `reason_chain` back to the intents that caused it. If you can't explain a fill, it shouldn't have happened.

---

## 3. The genome

A single JSON document that fully specifies the strategy layer. Nothing about strategy lives in code as a hardcoded number — code is *mechanism*, genome is *policy*.

Every accepted genome is written immutably to `state/genomes/vN.json`. Lineage is a tree, not a line — a rejected branch is kept, because a mutation that fails today may succeed under a later regime.

---

## 4. Acceptance rules (the part that matters)

A challenger replaces the champion **only if all of these hold**:

1. **Minimum evidence.** ≥ 30 closed trades and ≥ 90 days of simulated time in the evaluation window. Below that, results are noise.
2. **Out-of-sample only.** Fitness is computed on walk-forward folds. The Researcher's proposal may be *derived* from in-sample data; it is *judged* only on the next unseen fold.
3. **Sealed holdout.** The most recent slice of history is never used for anything until the Superior Judge's final check. Any genome that touched it during search is disqualified.
4. **No regression.** `fitness(challenger) > fitness(champion)` on every fold's aggregate, AND `maxDD(challenger) ≤ maxDD(champion) × 1.15`. A win bought with more risk is not a win.
5. **Multiple-testing penalty.** If *k* mutations were tested this generation, the required margin scales with *k*. Test 100 things and one will look great by luck; the bar rises to account for it.
6. **Complexity cost.** Adding an agent or a gene must clear a margin proportional to the complexity added. Simplicity is the default; deletion is free.
7. **Regime coverage.** The challenger must not lose money in any single regime bucket the champion was profitable in. No trading a bull-only strategy into a bear.

**Fitness** (locked in the constitution):

```
annualised Sortino on out-of-sample equity
  − 2.0 × max(0, maxDD − 0.20)         # drawdown above 20% hurts, hard
  − 0.5 × max(0, (turnover − 50) / 50) # churn is a cost, not a virtue
  hard-fail if maxDD > 0.40 or trades < 30
```

**Benchmarks tracked always, and reported honestly:** buy-and-hold equal-weight universe, buy-and-hold BTC, and cash. A strategy that underperforms buy-and-hold on risk-adjusted terms is flagged in every report even if it is beating its own ancestors. Improving relative to your own past self is not the same as being good.

---

## 5. Safety

- **Circuit breaker.** Peak-to-trough drawdown > 25% → the Superior Judge halts new entries and forces the roster into review. Not a suggestion; enforced in the broker.
- **Immutable constitution.** `constitution.py` is checksummed at every startup. If the fitness function, evaluator, or gate logic changed, the run refuses to start. This is the anti-cheat.
- **Paper first.** Real money is gated behind: 6 months of positive walk-forward, a live paper run that matches its own backtest within tolerance, and explicit sign-off from Burak. The system cannot promote itself.
- **Full audit.** Every tick writes the complete decision chain to the ledger. Any trade in history can be replayed and explained.

---

## 6. Why crypto first

The sandbox is Binance's public data API: free, no key, 24/7, ~490 USDT pairs, history to 2017, 1h and 1d candles. A 24/7 market means the evolution loop is never waiting for an exchange to open, and there's enough cross-sectional breadth for the consults to actually disagree. Equities and FX can be added later behind the same `MarketData` interface — nothing above the data layer knows what an asset class is.

---

## 6b. Amendment log

The constitution is locked against the Researcher, not against Burak. Every change to it is recorded here so that "we loosened a gate" can never happen quietly.

| date | change | why |
|---|---|---|
| 2026-08-15 | Circuit breaker became a 20-bar cooldown + forced flatten, instead of latching permanently | The latching version turned 62% of a backtest into a flat line, so fitness was measuring how fast the system died rather than how well it traded. |
| 2026-08-15 | Multiple-testing margin: linear `0.02k` → `σ·sqrt(2 ln k)` with σ=0.08 | The linear form put the bar at 0.46 for a 24-candidate generation, which is arithmetically unreachable on a Sortino-scaled metric — a mis-specification, not a safety property. sqrt-log is the standard correction for the expected maximum of k noisy estimates. The cross-fold consistency penalty and sealed holdout were left untouched. |
| 2026-08-15 | Added `ranking_fitness()` with a finite floor | `fitness()` returns −∞ on a hard gate failure, which is the right verdict but leaves search with no gradient when every candidate fails. Ranking uses a floor; **acceptance still uses the real `fitness()`**, so a floored score can never buy a promotion. |

A note on the second row, because it is the dangerous kind of change: lowering a bar because your system can't clear it is exactly the failure this design exists to prevent. The defence is that the replacement is the textbook correction rather than a tuned-down number, the two independent gates were not touched, and the change is written down here where it can be argued with.

## 6c. Why breadth, not a softer bar

The first universe was 12 symbols. With that little cross-section, the standard error on a fold's Sortino is larger than any improvement worth having, so the acceptance gates correctly rejected everything — the system could not learn, and the honest reading was "this data cannot distinguish these strategies."

The fix was more evidence, not a lower bar: 27 liquid pairs with 4+ years of history (plus PAXG, deliberately, as something that doesn't move with crypto). Champion fold-fitness went from −0.56 to +0.58 on the same code. When a gate blocks everything, the first question is whether the measurement is too noisy, not whether the gate is too strict.

## 7. Roadmap

- **v0.1** ← *here.* Deterministic genome-driven agents, real historical data, paper broker, one full backtest, decision log.
- **v0.2** Evolution loop live: Researcher proposes, Evaluator walk-forwards, Superior Judge commits. Multi-generation run.
- **v0.3** LLM-backed agents behind the same interface — reasoning consults for the hard calls, deterministic ones for the cheap calls.
- **v0.4** Continuous paper trading on live prices, scheduled, with a persistent dashboard.
- **v1.0** Real-money proposal presented to Burak with the full evidence pack. His decision, not the system's.
