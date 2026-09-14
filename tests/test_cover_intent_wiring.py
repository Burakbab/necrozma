"""Tests for the "cover" intent shape (AGENTS.md item 5 Phase 2), the
concretely-scoped next step flagged by `tests/test_short_position_sign_landmine.py`
and the 2026-09-13 ~09:47-10:20 UTC session: the three consults could not
*propose* closing a short, only "sell" a long.

Three pieces, each tested here:

1. **Consults** (`agents/consults.py`): each consult's long-only exit check
   now has a mirror for an open short, reusing the same genes symmetrically
   (e.g. an RSI-too-high long exit mirrors to an RSI-too-low short exit) and
   emitting `side="cover"` instead of `side="sell"`.
2. **RiskJudge.rule** (`agents/judges.py`): the exits-first loop used to
   bucket every non-"buy" intent as a "sell" and gate it on `is_long`
   (a "cover" intent would have landed there and been silently dropped,
   since a short's weight is never positive). It now buckets "cover"
   separately and gates it on `is_short`, emitting `Order(side="cover")`.
3. **SuperiorJudge.review** (`agents/judges.py`): "exits are never blocked,
   ever" only ever collected `side == "sell"` orders into `kept` -- a
   genuine landmine found while wiring this up: a "cover" order coming out
   of `RiskJudge.rule` would have been silently dropped here (not vetoed,
   just absent from the returned `Verdict.orders`), because it satisfies
   neither the `sells` nor the `buys` filter. Fixed to collect both exit
   sides.

No behavior change for any existing (long-only) live caller: `.short()`
still has zero callers in the live trading/evolution path, so
`b.open_positions` is never actually negative there and every new
is_short/"cover" branch below is unreachable in production today -- same
invariant every prior slice of this item preserved. See AGENTS.md item 5
and `runs/2026-09-14-*-cover-intent-wiring.md`.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agents.consults import ConservativeConsult, ModerateConsult, RiskyConsult
from agents.judges import RiskJudge, SuperiorJudge
from core.genome import Genome
from core.portfolio import PaperBroker
from core.types import Briefing, Features, Intent, Order, Proposal, Verdict


def _short_weight(quote_amount: float = 1_000.0, entry_price: float = 100.0,
                   mark_price: float = 100.0, symbol: str = "XUSDT") -> float:
    b = PaperBroker(cash=10_000.0)
    b.short("t0", symbol, quote_amount, entry_price)
    return b.position_weight(symbol, {symbol: mark_price})


def _features(**overrides) -> Features:
    base = dict(symbol="XUSDT", price=100.0, ret_1=0.0, ret_5=0.0, ret_20=0.0,
                trend=0.0, slope=0.0, rsi=50.0, vol=0.5, vol_ratio=1.0,
                dd_from_high=0.0, dist_ma=0.0, zscore=0.0, volume_shock=1.0,
                breakout=0.0, rank_mom=0.5)
    base.update(overrides)
    return Features(**base)


def _briefing(features: dict[str, Features], open_positions: dict[str, float]) -> Briefing:
    return Briefing(ts="t0", regime="bull", regime_score=0.5, breadth=0.8,
                     features=features, equity=10_000.0, cash_pct=0.9,
                     open_positions=open_positions)


# ---- 1. Consults propose "cover", not "sell", for an open short ----------

def test_risky_consult_covers_on_mirrored_condition():
    w = _short_weight()
    g = Genome()
    consult = RiskyConsult(g)
    # Long exit: rsi > exit_rsi(88) or trend < exit_trend_below(-0.03).
    # Mirror: rsi < 12 or trend > 0.03.
    feat = _features(rsi=5.0)
    proposal = consult.consider(_briefing({"XUSDT": feat}, {"XUSDT": w}))
    assert len(proposal.intents) == 1
    assert proposal.intents[0].side == "cover"


def test_moderate_consult_covers_on_mirrored_condition():
    w = _short_weight()
    g = Genome()
    consult = ModerateConsult(g)
    # Long exit: trend < exit_trend_below(0.0) or rsi > exit_rsi(80).
    # Mirror: trend > 0.0 or rsi < 20.
    feat = _features(trend=0.05)
    proposal = consult.consider(_briefing({"XUSDT": feat}, {"XUSDT": w}))
    assert len(proposal.intents) == 1
    assert proposal.intents[0].side == "cover"


def test_consults_still_sell_not_cover_for_an_open_long():
    # Regression: the new is_short branch must not change long behavior.
    g = Genome()
    feat = _features(rsi=95.0)
    for cls in (RiskyConsult, ModerateConsult, ConservativeConsult):
        proposal = cls(g).consider(_briefing({"XUSDT": feat}, {"XUSDT": 0.1}))
        assert len(proposal.intents) == 1
        assert proposal.intents[0].side == "sell"


def test_consults_propose_nothing_for_a_short_when_mirror_condition_not_met():
    w = _short_weight()
    g = Genome()
    feat = _features()  # rsi 50, trend 0 -- neither exit nor its mirror fires
    for cls in (RiskyConsult, ModerateConsult, ConservativeConsult):
        proposal = cls(g).consider(_briefing({"XUSDT": feat}, {"XUSDT": w}))
        assert proposal.intents == ()


# ---- 2. RiskJudge.rule routes "cover" intents against a real short -------

def test_risk_judge_turns_a_cover_intent_into_a_cover_order_for_a_real_short():
    w = _short_weight()
    g = Genome()
    judge = RiskJudge(g)
    proposals = [
        Proposal(agent=a, ts="t0", stance="s",
                 intents=(Intent(agent=a, symbol="XUSDT", side="cover",
                                 conviction=0.9, horizon=0, rationale="test"),))
        for a in ("consult_risky", "consult_moderate", "consult_conservative")
    ]
    verdict = judge.rule(_briefing({}, {"XUSDT": w}), proposals, n_consults=3)
    cover_orders = [o for o in verdict.orders if o.side == "cover"]
    assert len(cover_orders) == 1
    assert cover_orders[0].symbol == "XUSDT"
    assert cover_orders[0].fraction > 0


def test_risk_judge_ignores_a_cover_intent_when_the_symbol_is_not_actually_short():
    # A "cover" intent against a flat or long symbol must not manufacture an
    # order -- mirrors the existing is_long gate that a "sell" intent against
    # a flat/short symbol already gets.
    g = Genome()
    judge = RiskJudge(g)
    proposals = [
        Proposal(agent="consult_risky", ts="t0", stance="s",
                 intents=(Intent(agent="consult_risky", symbol="XUSDT", side="cover",
                                 conviction=0.9, horizon=0, rationale="test"),))
    ]
    verdict = judge.rule(_briefing({}, {"XUSDT": 0.1}), proposals, n_consults=3)
    assert verdict.orders == []


def test_risk_judge_vetoes_a_same_bar_buy_against_a_pending_cover():
    w = _short_weight()
    g = Genome()
    judge = RiskJudge(g)
    proposals = [
        Proposal(agent="consult_risky", ts="t0", stance="s", intents=(
            Intent(agent="consult_risky", symbol="XUSDT", side="cover",
                   conviction=0.9, horizon=0, rationale="cover"),)),
        Proposal(agent="consult_moderate", ts="t0", stance="s", intents=(
            Intent(agent="consult_moderate", symbol="XUSDT", side="buy",
                   conviction=0.9, horizon=10, rationale="buy"),)),
    ]
    verdict = judge.rule(_briefing({}, {"XUSDT": w}), proposals, n_consults=3)
    buy_orders = [o for o in verdict.orders if o.side == "buy"]
    assert buy_orders == []
    assert any(v.symbol == "XUSDT" and v.side == "buy" for v in verdict.vetoes)


# ---- 3. SuperiorJudge.review no longer drops "cover" orders --------------

def test_superior_judge_keeps_a_cover_order_instead_of_silently_dropping_it():
    g = Genome()
    order = Order(symbol="XUSDT", side="cover", fraction=1.0,
                   reason_chain=["test"], conviction=0.9, agreement=1.0)
    verdict = Verdict(ts="t0", orders=[order], vetoes=[], agreement_score=1.0)
    w = _short_weight()
    out = SuperiorJudge(g).review(_briefing({}, {"XUSDT": w}), verdict, halted=False)
    # The landmine this test guards against: `kept` used to only ever collect
    # `side == "sell"` orders as "exits are never blocked" -- a "cover" order
    # satisfied neither that filter nor the `buys` one, so it vanished from
    # the returned Verdict entirely instead of being vetoed or kept.
    assert len(out.orders) == 1
    assert out.orders[0].side == "cover"
    assert out.vetoes == []


def test_superior_judge_keeps_a_cover_order_even_when_halted():
    # Exits are never blocked, ever -- including by the circuit breaker.
    g = Genome()
    order = Order(symbol="XUSDT", side="cover", fraction=1.0,
                   reason_chain=["test"], conviction=0.9, agreement=1.0)
    verdict = Verdict(ts="t0", orders=[order], vetoes=[], agreement_score=1.0)
    w = _short_weight()
    out = SuperiorJudge(g).review(_briefing({}, {"XUSDT": w}), verdict, halted=True)
    assert len(out.orders) == 1
    assert out.orders[0].side == "cover"
