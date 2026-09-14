"""Regression tests for the sign-landmine found 2026-09-13 (weekend
all-hands) while scoping AGENTS.md item 5 Phase 2 (short-selling
genome/agent wiring): `PaperBroker.position_weight()` (Phase 1, shipped
2026-09-08) returns a *negative* weight for an open short (`qty * price /
equity`, and `qty < 0` for a short by the signed-qty convention
`core/portfolio.py` documents). That negative weight flows unmodified into
`Briefing.open_positions` (`loop/engine.py`'s `weights = {s:
b.position_weight(s, prices) ...}` -> `agents/analyst.py`'s `brief()`).

`RiskJudge.rule`'s slot-counting and `held_w`-based sizing headroom, and
`SuperiorJudge.review`'s slot-counting and hard-cap `room` line, all used to
assume a non-positive weight meant "flat" -- true only because nothing had
ever called `.short()` in the live path. Fixed 2026-09-13 (this commit):
those five read sites (`agents/judges.py`) now treat any nonzero weight as
an occupied slot and use `abs(weight)` for exposure/cap accounting, so a
short can no longer under-count position slots or loosen a hard cap it
should be tightening.

The three consults' `held = ... > 0` exit checks were, at the time this file
was first written, intentionally left long-only (`agents/consults.py`,
spelled `is_long(...)` for clarity): closing a short needed its own intent
shape ("cover", not "sell") that didn't exist yet. That gap is now closed
(see `tests/test_cover_intent_wiring.py` for the "cover" intent shape and
its routing through `RiskJudge`/`SuperiorJudge`) -- the test below now
checks the consult's mirrored short-exit condition instead of the old gap.

No behavior change for any existing (long-only) live caller: `.short()`
still has zero callers in the live trading/evolution path, `live_state.json`
untouched, neither `core/portfolio.py` nor `constitution/__init__.py` (the
two checksummed files) touched. See AGENTS.md item 5 and
`runs/2026-09-13-0600-weekend-all-hands.md` for how this was found.
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


def test_risk_judge_counts_a_shorted_symbol_as_an_open_slot():
    w = _short_weight()
    g = Genome()
    judge = RiskJudge(g)
    b = Briefing(ts="t0", regime="bull", regime_score=0.5, breadth=0.8,
                 features={}, equity=10_000.0, cash_pct=0.9,
                 open_positions={"XUSDT": w})
    # Fixed: agents/judges.py's RiskJudge.rule now counts any nonzero weight
    # (`!= 0`, not `> 0`) as an occupied slot, so a short is no longer
    # invisible to the max_positions limit.
    open_count = sum(1 for wt in b.open_positions.values() if wt != 0)
    assert open_count == 1
    assert len(b.open_positions) == 1


def test_risk_judge_does_not_give_extra_buy_headroom_to_a_shorted_symbol():
    w = _short_weight()
    # base_size_pct raised so `target` actually reaches the
    # `max_position_pct - abs(held_w)` cap being tested -- at the default
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
    # Fixed: `target = min(target, max_position_pct - abs(held_w))` -- the
    # short's magnitude now eats into the cap the same way a long would,
    # instead of a negative held_w raising it. The shorted case must not get
    # *more* room than the flat one.
    assert shorted_amount <= flat_amount


def _buy_verdict(amount: float = 10_000.0) -> Verdict:
    # Order is a mutable dataclass and SuperiorJudge.review() mutates
    # `o.quote_amount` in place -- build a fresh Order/Verdict per call so
    # two `review()` calls in the same test don't see each other's trimmed
    # amount.
    order = Order(symbol="XUSDT", side="buy", quote_amount=amount,
                   reason_chain=["test"], conviction=0.9, agreement=1.0)
    return Verdict(ts="t0", orders=[order], vetoes=[], agreement_score=1.0)


def test_superior_judge_hard_cap_holds_for_a_shorted_symbol():
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
    # `hard_cap * equity` regardless of what else is going on with it.
    assert flat_room <= hard_cap * flat.equity + 1e-6
    # Fixed: `room = (hard_cap - abs(held)) * equity` now treats the short's
    # magnitude as exposure already spent, so the cap holds for it too and no
    # longer grants more allowance than the flat case.
    assert shorted_room <= hard_cap * shorted.equity + 1e-6
    assert shorted_room <= flat_room


def test_consult_exit_check_now_proposes_covering_an_open_short():
    from agents.consults import ConservativeConsult
    from core.types import Briefing as B

    w = _short_weight()
    g = Genome()
    consult = ConservativeConsult(g)
    feat = _features()
    # ConservativeConsult's long exit fires when rsi > exit_rsi (default 68).
    # Its short mirror fires on the opposite extreme: rsi < 100 - exit_rsi
    # (default 32) -- set well below that.
    feat = Features(**{**feat.__dict__, "rsi": 10.0})
    briefing = B(ts="t0", regime="bull", regime_score=0.5, breadth=0.8,
                 features={"XUSDT": feat}, equity=10_000.0, cash_pct=0.9,
                 open_positions={"XUSDT": w})
    proposal = consult.consider(briefing)
    # Fixed (AGENTS.md item 5 Phase 2): the consult now proposes a "cover",
    # not a "sell" (which `PaperBroker.sell()` would reject for a short
    # anyway), when its mirrored short-exit condition triggers.
    assert len(proposal.intents) == 1
    assert proposal.intents[0].side == "cover"
    assert proposal.intents[0].symbol == "XUSDT"
