"""Documents an open landmine for AGENTS.md item 5 Phase 2 (short-selling
genome/agent wiring), found 2026-09-13 (weekend all-hands) while scoping that
work: `PaperBroker.position_weight()` (Phase 1, shipped 2026-09-08) already
returns a *negative* weight for an open short (`qty * price / equity`, and
`qty < 0` for a short by the signed-qty convention `core/portfolio.py`
documents). That negative weight flows unmodified into
`Briefing.open_positions` (`loop/engine.py`'s `weights = {s:
b.position_weight(s, prices) ...}` -> `agents/analyst.py`'s `brief()`), where
every current reader assumes a positive value means "held" and a
non-positive one means "flat" -- true today only because nothing has ever
called `.short()` in the live trading/evolution path.

This is not hypothetical: the three consults' `held = ... > 0` exit checks,
`RiskJudge.rule`'s slot-counting and `held_w`-based sizing headroom, and
`SuperiorJudge.review`'s hard-cap `room = (hard_cap - held) * equity` line
would all misread a short position once one exists. The `SuperiorJudge` case
is the sharpest: a *negative* `held` makes `room` *larger* than
`hard_cap * equity`, i.e. the hard safety cap gets silently loosened for a
symbol that already carries directional (short) risk -- the opposite of what
a hard-limit gate is for.

These tests pin today's actual (buggy-once-shorts-are-wired) behavior with a
synthetic negative-weight `Briefing`, built directly from `PaperBroker.short()`
+ `position_weight()` so the sign isn't hand-waved. They exist so whoever
next attempts item 5 Phase 2 (routing "short"/"cover" intents through
RiskJudge/SuperiorJudge) has a concrete, failing-once-fixed checklist instead
of rediscovering this from scratch -- see AGENTS.md item 5 and
`runs/2026-09-13-0600-weekend-all-hands.md`. No behavior changes here: every
assertion describes the current code as-is, and neither `core/portfolio.py`
nor `constitution/__init__.py` (the two checksummed files) is touched.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agents.judges import RiskJudge, SuperiorJudge
from core.genome import Genome
from core.portfolio import PaperBroker
from core.types import Briefing, Features, Intent, Order, Proposal, Verdict


def _short_weight(quote_amount: float = 1_000.0, entry_price: float = 100.0,
                   mark_price: float = 100.0) -> float:
    """The real, signed weight `position_weight()` reports for an open short,
    computed via the actual Phase 1 broker mechanics -- not hand-typed."""
    b = PaperBroker(cash=10_000.0)
    b.short("t0", "XUSDT", quote_amount, entry_price)
    return b.position_weight("XUSDT", {"XUSDT": mark_price})


def _features(symbol: str = "XUSDT") -> Features:
    return Features(symbol=symbol, price=100.0, ret_1=0.0, ret_5=0.0, ret_20=0.0,
                    trend=0.0, slope=0.0, rsi=50.0, vol=0.5, vol_ratio=1.0,
                    dd_from_high=0.0, dist_ma=0.0, zscore=0.0, volume_shock=1.0,
                    breakout=0.0, rank_mom=0.5)


def test_position_weight_is_negative_for_an_open_short():
    # Establishes the premise every other test in this file relies on.
    w = _short_weight()
    assert w < 0.0


def test_risk_judge_undercounts_a_shorted_symbol_as_an_open_slot():
    w = _short_weight()
    g = Genome()
    judge = RiskJudge(g)
    b = Briefing(ts="t0", regime="bull", regime_score=0.5, breadth=0.8,
                 features={}, equity=10_000.0, cash_pct=0.9,
                 open_positions={"XUSDT": w})
    # An open short occupies real risk, but `open_count` (agents/judges.py's
    # RiskJudge.rule, `sum(1 for w in b.open_positions.values() if w > 0)`)
    # counts it as zero positions used -- a shorted symbol is invisible to
    # the max_positions slot limit.
    open_count = sum(1 for wt in b.open_positions.values() if wt > 0)
    assert open_count == 0
    assert len(b.open_positions) == 1


def test_risk_judge_gives_extra_buy_headroom_to_a_shorted_symbol():
    w = _short_weight()
    # base_size_pct raised so `target` actually reaches the
    # `max_position_pct - held_w` cap being tested -- at the default
    # base_size_pct the uncapped target is already well under
    # max_position_pct and this comparison would pass for the wrong reason
    # (both sides simply uncapped and identical).
    g = Genome().child([("agents.risk_judge.genes.base_size_pct", 1.0)])
    proposals = [
        Proposal(agent=a, ts="t0", stance="bullish",
                 intents=(Intent(agent=a, symbol="XUSDT", side="buy",
                                 conviction=0.9, horizon=10, rationale="test"),))
        for a in ("consult_risky", "consult_moderate", "consult_conservative")
    ]
    flat = Briefing(ts="t0", regime="bull", regime_score=0.5, breadth=0.8,
                     features={}, equity=10_000.0, cash_pct=0.9, open_positions={})
    shorted = Briefing(ts="t0", regime="bull", regime_score=0.5, breadth=0.8,
                        features={}, equity=10_000.0, cash_pct=0.9,
                        open_positions={"XUSDT": w})
    flat_amount = RiskJudge(g).rule(flat, proposals, n_consults=3).orders[0].quote_amount
    shorted_amount = RiskJudge(g).rule(shorted, proposals, n_consults=3).orders[0].quote_amount
    # `target = min(target, max_position_pct - held_w)` (agents/judges.py):
    # a negative `held_w` raises this cap instead of leaving it alone, so the
    # proposed buy on top of an existing short gets *more* room than the same
    # buy against a flat position, not less.
    assert shorted_amount > flat_amount


def _buy_verdict(amount: float = 10_000.0) -> Verdict:
    # Order is a mutable dataclass and SuperiorJudge.review() mutates
    # `o.quote_amount` in place -- build a fresh Order/Verdict per call so
    # two `review()` calls in the same test don't see each other's trimmed
    # amount.
    order = Order(symbol="XUSDT", side="buy", quote_amount=amount,
                   reason_chain=["test"], conviction=0.9, agreement=1.0)
    return Verdict(ts="t0", orders=[order], vetoes=[], agreement_score=1.0)


def test_superior_judge_hard_cap_loosens_for_a_shorted_symbol():
    w = _short_weight()
    g = Genome()

    flat = Briefing(ts="t0", regime="bull", regime_score=0.5, breadth=0.8,
                     features={}, equity=10_000.0, cash_pct=0.9, open_positions={})
    shorted = Briefing(ts="t0", regime="bull", regime_score=0.5, breadth=0.8,
                        features={}, equity=10_000.0, cash_pct=0.9,
                        open_positions={"XUSDT": w})

    hard_cap = g.genes("superior_judge").get("hard_max_position_pct", 0.35)
    flat_out = SuperiorJudge(g).review(flat, _buy_verdict(), halted=False)
    shorted_out = SuperiorJudge(g).review(shorted, _buy_verdict(), halted=False)

    flat_room = flat_out.orders[0].quote_amount
    shorted_room = shorted_out.orders[0].quote_amount
    # Intended invariant: the hard cap never lets a symbol's buy exceed
    # `hard_cap * equity` regardless of what else is going on with it. That
    # holds when flat...
    assert flat_room <= hard_cap * flat.equity + 1e-6
    # ...but the same symbol carrying an open short gets a *larger* allowance
    # than the hard cap intends, because `room = (hard_cap - held) * equity`
    # adds back the magnitude of the (negative) short weight instead of
    # treating it as exposure already spent.
    assert shorted_room > hard_cap * shorted.equity
    assert shorted_room > flat_room


def test_consult_exit_check_treats_an_open_short_as_flat():
    from agents.consults import ConservativeConsult
    from core.types import Briefing as B

    w = _short_weight()
    g = Genome()
    consult = ConservativeConsult(g)
    feat = _features()
    # Set rsi above this consult's exit_rsi so a *held long* would trigger
    # its "mean reversion complete" exit intent.
    feat = Features(**{**feat.__dict__, "rsi": 90.0})
    briefing = B(ts="t0", regime="bull", regime_score=0.5, breadth=0.8,
                 features={"XUSDT": feat}, equity=10_000.0, cash_pct=0.9,
                 open_positions={"XUSDT": w})
    proposal = consult.consider(briefing)
    # `held = b.open_positions.get(sym, 0.0) > 0` reads the open short as not
    # held, so the exit branch never fires for it -- a real short position
    # this consult should be able to reason about closing is invisible to it.
    assert proposal.intents == ()
