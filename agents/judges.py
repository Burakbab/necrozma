"""THE JUDGES.

RiskJudge (minor) — reads the three proposals *and* the portfolio, resolves
disagreement into position sizes, and vetoes anything that breaks portfolio
sanity. Its core insight: consensus is information. When three agents that
think differently all want the same thing, that's a stronger signal than any
one of them shouting.

SuperiorJudge — final authority. Deliberately boring in the trading loop: hard
limits and the circuit breaker only. Its real power is in the evolution loop,
where it is the sole writer to the genome.
"""
from __future__ import annotations

from collections import defaultdict

from core.genome import Genome
from core.types import Briefing, Order, Proposal, Verdict, Veto


class RiskJudge:
    name = "risk_judge"

    def __init__(self, genome: Genome):
        self.g = genome
        self.genes = genome.genes("risk_judge")
        self._bars_seen = 0  # calls to rule() since this instance was built

    def rule(self, b: Briefing, proposals: list[Proposal], n_consults: int) -> Verdict:
        g = self.genes
        bar_i = self._bars_seen
        self._bars_seen += 1
        ramp_bars = int(g.get("cold_start_ramp_bars", 0))
        ramp_scale = 1.0
        conviction_boost = 0.0
        if ramp_bars > 0 and bar_i < ramp_bars:
            start_scale = float(g.get("cold_start_ramp_start_scale", 1.0))
            ramp_scale = start_scale + (1.0 - start_scale) * (bar_i / ramp_bars)
            max_boost = float(g.get("cold_start_ramp_min_conviction_boost", 0.0))
            if max_boost > 0:
                conviction_boost = max_boost * (1.0 - bar_i / ramp_bars)
        vol_cap = float(g.get("cold_start_ramp_vol_cap", 0.0))
        vol_cap_active = ramp_bars > 0 and bar_i < ramp_bars and vol_cap > 0
        vetoes: list[Veto] = []
        orders: list[Order] = []

        buys: dict[str, list] = defaultdict(list)
        sells: dict[str, list] = defaultdict(list)
        for p in proposals:
            for it in p.intents:
                (buys if it.side == "buy" else sells)[it.symbol].append(it)

        # ---- exits first. Always. Freeing risk before adding it is the whole
        # difference between a portfolio and a collection of hopes.
        for sym, intents in sells.items():
            if b.open_positions.get(sym, 0.0) <= 0:
                continue
            conv = max(i.conviction for i in intents)
            share = len(intents) / max(n_consults, 1)
            score = conv * (0.5 + 0.5 * share)
            if score >= g.get("sell_conviction_threshold", 0.35):
                frac = 1.0 if share >= 0.67 else 0.5
                orders.append(Order(
                    symbol=sym, side="sell", fraction=frac,
                    reason_chain=[f"{i.agent}: {i.rationale}" for i in intents],
                    conviction=conv, agreement=share))
            else:
                vetoes.append(Veto(sym, "sell", self.name,
                                   f"exit conviction {score:.2f} below threshold"))

        selling = {o.symbol for o in orders if o.side == "sell"}
        regime_scale = float(g.get("regime_scale", {}).get(b.regime, 0.5))

        if regime_scale <= 0.0 and buys:
            for sym in buys:
                vetoes.append(Veto(sym, "buy", self.name,
                                   f"regime '{b.regime}' — no new risk"))
            return Verdict(b.ts, orders, vetoes, 0.0,
                           f"regime {b.regime}: entries closed", self.name)

        # ---- entries, best-scored first
        open_count = sum(1 for w in b.open_positions.values() if w > 0)
        cash_avail = b.equity * max(0.0, b.cash_pct - g.get("cash_floor_pct", 0.05))

        scored = []
        for sym, intents in buys.items():
            if sym in selling:
                vetoes.append(Veto(sym, "buy", self.name, "same-bar exit takes precedence"))
                continue
            share = len(intents) / max(n_consults, 1)
            conv = sum(i.conviction for i in intents) / len(intents)
            if share >= 0.99:
                mult = g.get("unanimous_bonus", 1.6)
            elif share >= 0.66:
                mult = g.get("two_agree_bonus", 1.2)
            else:
                mult = g.get("lone_voice_scale", 0.6)
            scored.append((conv * mult, sym, intents, share, conv))
        scored.sort(reverse=True, key=lambda x: x[0])

        max_pos = int(g.get("max_positions", 6))
        for score, sym, intents, share, conv in scored:
            if conv < g.get("min_conviction", 0.30) + conviction_boost:
                vetoes.append(Veto(sym, "buy", self.name,
                                   f"conviction {conv:.2f} below floor"))
                continue
            held_w = b.open_positions.get(sym, 0.0)
            if held_w > 0 and not g.get("scale_in_allowed", True):
                vetoes.append(Veto(sym, "buy", self.name, "already held; scale-in disabled"))
                continue
            if held_w <= 0 and open_count >= max_pos:
                vetoes.append(Veto(sym, "buy", self.name,
                                   f"position slots full ({open_count}/{max_pos})"))
                continue

            target = float(g.get("base_size_pct", 0.12)) * score * regime_scale
            target = min(target, float(g.get("max_position_pct", 0.25)) - held_w)
            # Room/slot accounting (cash_avail, open_count) is always figured
            # against the full un-ramped amount -- the ramp holds capital
            # back, it doesn't free that capital up for extra lower-priority
            # positions to fill the same bar (which would just redistribute
            # the same total exposure across more, smaller positions instead
            # of actually reducing it during the cold-start window).
            full_amount = min(target * b.equity, cash_avail)
            amount = full_amount * ramp_scale
            if vol_cap_active:
                feat = b.features.get(sym)
                if feat is not None and feat.vol > vol_cap:
                    amount *= vol_cap / feat.vol
            if amount <= 0 or target <= 0:
                vetoes.append(Veto(sym, "buy", self.name, "no room: size cap or cash floor"))
                continue

            orders.append(Order(
                symbol=sym, side="buy", quote_amount=amount,
                reason_chain=[f"{i.agent}: {i.rationale}" for i in intents],
                conviction=conv, agreement=share))
            cash_avail -= full_amount
            if held_w <= 0:
                open_count += 1

        agreement = (sum(o.agreement for o in orders) / len(orders)) if orders else 0.0
        return Verdict(b.ts, orders, vetoes, agreement,
                       f"regime {b.regime} (scale {regime_scale:.2f}), "
                       f"breadth {b.breadth:.0%}", self.name)


class SuperiorJudge:
    """Final authority. In the trading loop it should rarely intervene — if it
    overrides the Risk Judge often, that is itself evidence the Risk Judge's
    genes are miscalibrated, and the Researcher is told about it."""

    name = "superior_judge"

    def __init__(self, genome: Genome):
        self.g = genome
        self.genes = genome.genes("superior_judge")
        self.override_count = 0
        self.overrides: list[str] = []

    def review(self, b: Briefing, v: Verdict, halted: bool) -> Verdict:
        g = self.genes
        kept: list[Order] = []
        vetoes = list(v.vetoes)

        sells = [o for o in v.orders if o.side == "sell"]
        buys = [o for o in v.orders if o.side == "buy"]
        kept.extend(sells)  # exits are never blocked. Ever.

        if halted:
            for o in buys:
                vetoes.append(Veto(o.symbol, "buy", self.name, "circuit breaker active"))
                self._log(f"{b.ts} blocked {o.symbol}: circuit breaker")
            return Verdict(v.ts, kept, vetoes, v.agreement_score,
                           v.notes + " | HALTED", self.name)

        if b.regime == "crisis" and g.get("block_buys_in_crisis", True):
            for o in buys:
                vetoes.append(Veto(o.symbol, "buy", self.name, "crisis regime: capital preservation"))
                self._log(f"{b.ts} blocked {o.symbol}: crisis regime")
            return Verdict(v.ts, kept, vetoes, v.agreement_score,
                           v.notes + " | crisis lockdown", self.name)

        open_count = sum(1 for w in b.open_positions.values() if w > 0)
        new_positions = 0
        max_new = int(g.get("max_new_positions_per_bar", 3))
        hard_max_pos = int(g.get("hard_max_positions", 8))
        hard_cap = float(g.get("hard_max_position_pct", 0.35))
        hard_floor = float(g.get("hard_cash_floor_pct", 0.02))
        spend_budget = b.equity * max(0.0, b.cash_pct - hard_floor)

        for o in buys:
            held = b.open_positions.get(o.symbol, 0.0)
            if held <= 0:
                if open_count + new_positions >= hard_max_pos:
                    vetoes.append(Veto(o.symbol, "buy", self.name, "hard position-count limit"))
                    self._log(f"{b.ts} blocked {o.symbol}: hard position limit")
                    continue
                if new_positions >= max_new:
                    vetoes.append(Veto(o.symbol, "buy", self.name, "new-position rate limit"))
                    self._log(f"{b.ts} blocked {o.symbol}: rate limit")
                    continue
            room = (hard_cap - held) * b.equity
            amt = min(o.quote_amount, room, spend_budget)
            if amt <= 0:
                vetoes.append(Veto(o.symbol, "buy", self.name, "hard concentration limit"))
                self._log(f"{b.ts} blocked {o.symbol}: concentration")
                continue
            if amt < o.quote_amount * 0.999:
                self._log(f"{b.ts} trimmed {o.symbol}: {o.quote_amount:.0f} -> {amt:.0f}")
            o.quote_amount = amt
            o.reason_chain.append(f"{self.name}: approved (cap-checked)")
            kept.append(o)
            spend_budget -= amt
            if held <= 0:
                new_positions += 1

        return Verdict(v.ts, kept, vetoes, v.agreement_score, v.notes, self.name)

    def _log(self, msg: str) -> None:
        self.override_count += 1
        if len(self.overrides) < 500:
            self.overrides.append(msg)


def flag_hard_call(orders: list[Order], just_halted: bool, overrides_this_bar: int,
                   low_agreement_threshold: float = 0.4,
                   nav: float | None = None,
                   min_size_pct: float = 0.0) -> dict[str, Any]:
    """Cheap, deterministic triage for which bars deserve a slower second look.

    This is not a verdict and it changes nothing the Trader executes -- it only
    labels bars where the machinery disagreed with itself (Superior Judge
    overrode the Risk Judge), acted on thin consensus in its single biggest bet
    (a lone-voice buy that is also the bar's highest-conviction order), or did
    something drastic (the circuit breaker just tripped). That label is the
    "flag hard calls" half of the LLM-backed-consult plan in AGENTS.md item 4:
    pick out which bars are worth spending a slower, reasoned opinion on,
    before any such opinion exists to spend. The other half -- actually
    consulting on a flagged bar and feeding a verdict back in -- is not built
    yet; this only marks the candidates.

    The low-agreement trigger was measured (2026-08-17,
    `evotrader_bundle.py hard-calls`) against a bar-level aggregate
    (`agreement_score`, the mean across every order that bar) and found to
    fire on 38.6% of bars -- almost entirely "exactly one of three consults
    proposed *a* buy that bar", a pattern the Risk Judge already prices in via
    `lone_voice_scale`, not a rare event. A first narrowing read each order's
    own `agreement` field instead and only flagged a lone-voice buy when it
    was *also* the bar's single highest-conviction buy order -- but that
    measured *worse* (52.0%, `runs/2026-08-17-1553-hard-call-trigger-narrowing.md`):
    lone-voice and highest-conviction-that-bar turn out to be strongly
    correlated here, not independent, because most bars with any buy at all
    have exactly one. A second narrowing required the lone-voice buy be the
    *only* order the bar produced at all -- no other buy, no sell -- and that
    worked (24.4%, `runs/2026-08-17-1850-hard-call-solo-bar-narrowing.md`):
    "the whole council went quiet except one loud voice" vs. "one of several
    independent picks that bar happened to be lone-voice".

    This version adds a third, independent axis on top of the solo-bar
    requirement rather than replacing it: `min_size_pct` gates on how much of
    the account's equity the lone-voice buy actually commits. A solo bar with
    a token-sized position is a different claim from a solo bar betting a
    real fraction of the book on one weak-consensus signal -- only the latter
    is the kind of decision worth a slower second look. When `min_size_pct`
    is 0.0 (the default) this axis is off and behavior is identical to the
    solo-bar-only version; a caller opts in by passing both `nav` (the bar's
    portfolio equity, already computed by `Council.tick` before this is
    called) and a positive `min_size_pct`. Measured against the real live
    champion (2026-08-17, `evotrader_bundle.py hard-calls`): of the 253 solo
    lone-voice bars on a full-history replay, position sizes ranged from a
    fraction of a percent of equity up to 24.8%, with no natural break -- a
    continuous spread, not two clusters. `min_size_pct=0.10` is the wired
    default because it cuts this trigger's own contribution from 18.3% of all
    bars to 3.5% (253 -> 48 bars) while still catching every solo bet that
    actually risks a meaningful slice of the account, bringing the combined
    flag rate to ~9.6% of bars -- close to the circuit_breaker +
    superior_override-only floor (~6.1%) instead of nearly 4x it.
    """
    reasons: list[str] = []
    if just_halted:
        reasons.append("circuit breaker tripped this bar")
    if overrides_this_bar > 0:
        reasons.append(f"superior_judge intervened on {overrides_this_bar} order(s)")
    buys = [o for o in orders if o.side == "buy"]
    if buys and len(orders) == 1:
        leader = buys[0]
        if leader.agreement < low_agreement_threshold:
            size_pct = (leader.quote_amount / nav) if nav else 0.0
            if min_size_pct <= 0.0 or size_pct >= min_size_pct:
                detail = f", {size_pct:.1%} of equity" if min_size_pct > 0.0 else ""
                reasons.append(
                    f"lone-voice buy on {leader.symbol} (agreement {leader.agreement:.2f}) "
                    f"is the only order the bar produced ({leader.conviction:.2f} conviction"
                    f"{detail})")
    return {"is_hard_call": bool(reasons), "reasons": reasons}


def summarize_hard_calls(decision_log: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate `flag_hard_call` output across a decision log (a live
    journal's per-tick decisions, or a backtest's `decision_log`) into counts
    a human can read in one screen: how often it fires, and on which of the
    three triggers. Read-only — takes an already-built log, never a genome or
    live state, so it cannot touch anything by construction.

    This exists to answer "does this actually flag any real bars?" without
    waiting on one live tick at a time: a full-history backtest already runs
    every bar through the same `flag_hard_call` call a live tick would, so it
    gives the same answer many bars at once.
    """
    n = len(decision_log)
    flagged = [d for d in decision_log if d.get("hard_call", {}).get("is_hard_call")]
    by_category = {"circuit_breaker": 0, "superior_override": 0, "low_agreement_buy": 0}
    for d in flagged:
        for r in d["hard_call"]["reasons"]:
            if r.startswith("circuit breaker"):
                by_category["circuit_breaker"] += 1
            elif r.startswith("superior_judge"):
                by_category["superior_override"] += 1
            elif r.startswith("lone-voice buy"):
                by_category["low_agreement_buy"] += 1
    return {
        "n_bars": n,
        "n_flagged": len(flagged),
        "flag_rate": (len(flagged) / n) if n else 0.0,
        "by_category": by_category,
        "flagged": [{"ts": d.get("ts"), "reasons": d["hard_call"]["reasons"]}
                    for d in flagged],
    }


def pending_hard_call_reviews(journal: list[dict[str, Any]],
                              reviews: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Which flagged live ticks still have no recorded review.

    This is the first piece of the "review after the fact" half of AGENTS.md
    item 4's design (b): flag_hard_call already marks candidate bars
    (additive, computed after execution); this is a pure set difference
    between `LiveAccount.journal` (what actually happened) and
    `LiveAccount.hard_call_reviews` (verdicts a later scheduled session wrote
    back after reasoning about a flagged bar) -- matched by `tick`, the
    journal's own stable id. Design (b) over (a) because the measured flag
    rate (~9.6% as of 2026-08-17, `evotrader_bundle.py hard-calls`) is low
    enough that a scheduled session can plausibly look at every flagged bar
    without it becoming the normal path, and because a live daily tick only
    produces at most one candidate a day -- (a)'s stop-before-execution
    split isn't needed to keep up with that rate.

    Read-only: takes two already-built lists, never state itself, so it
    cannot write anything by construction. Nothing yet calls this outside
    the `review-hard-calls` CLI command -- no live journal entry has ever
    actually flagged (`is_hard_call: true`) as of this writing, so this is
    infrastructure ahead of its first real case, not a response to one.
    """
    reviewed_ticks = {r["tick"] for r in reviews}
    pending = []
    for entry in journal:
        hc = (entry.get("decision") or {}).get("hard_call") or {}
        if hc.get("is_hard_call") and entry.get("tick") not in reviewed_ticks:
            pending.append({
                "tick": entry.get("tick"),
                "bar": entry.get("bar"),
                "reasons": hc.get("reasons", []),
            })
    return pending
