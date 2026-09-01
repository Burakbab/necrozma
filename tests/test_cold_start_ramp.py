"""Tests for RiskJudge's cold_start_ramp_bars/cold_start_ramp_start_scale
genes (agents/judges.py) -- added 2026-09-01 to address the fold-restart
cold-start drawdown artifact found in
runs/2026-09-01-0114-4h-shadow-consv-trailing-fails-real-fold-gate.md (see
AGENTS.md item 2). Defaults (0 bars, scale 1.0) must be a true no-op."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agents.judges import RiskJudge
from core.genome import Genome
from core.types import Briefing, Intent, Proposal


def _briefing(**overrides) -> Briefing:
    defaults = dict(ts="2020-01-01", regime="bull", regime_score=0.5, breadth=0.8,
                    features={}, equity=10_000.0, cash_pct=1.0, open_positions={})
    defaults.update(overrides)
    return Briefing(**defaults)


def _unanimous_buy_proposals(symbol: str = "BTCUSDT", conviction: float = 0.9) -> list[Proposal]:
    agents = ["consult_risky", "consult_moderate", "consult_conservative"]
    return [
        Proposal(agent=a, ts="2020-01-01", stance="bullish",
                 intents=(Intent(agent=a, symbol=symbol, side="buy",
                                 conviction=conviction, horizon=10,
                                 rationale="test"),))
        for a in agents
    ]


def test_default_genome_has_no_ramp():
    g = Genome()
    assert g.genes("risk_judge")["cold_start_ramp_bars"] == 0
    assert g.genes("risk_judge")["cold_start_ramp_start_scale"] == 1.0
    assert g.genes("risk_judge")["cold_start_ramp_min_conviction_boost"] == 0.0


def test_zero_ramp_bars_is_a_true_noop():
    g = Genome()
    judge = RiskJudge(g)
    proposals = _unanimous_buy_proposals()
    b = _briefing()
    v1 = judge.rule(b, proposals, n_consults=3)
    v2 = judge.rule(b, proposals, n_consults=3)
    assert v1.orders and v2.orders
    # same inputs, same bar -> same size every call when ramp is off, no
    # matter how many bars this RiskJudge instance has already seen
    assert v1.orders[0].quote_amount == v2.orders[0].quote_amount


def test_ramp_scales_first_order_down_from_start_scale():
    g = Genome().child([
        ("agents.risk_judge.genes.cold_start_ramp_bars", 10),
        ("agents.risk_judge.genes.cold_start_ramp_start_scale", 0.2),
    ])
    unramped = RiskJudge(Genome())
    ramped = RiskJudge(g)
    proposals = _unanimous_buy_proposals()
    b = _briefing()

    base_amount = unramped.rule(b, proposals, n_consults=3).orders[0].quote_amount
    first_bar_amount = ramped.rule(b, proposals, n_consults=3).orders[0].quote_amount

    assert first_bar_amount == pytest.approx(base_amount * 0.2)


def test_ramp_reaches_full_size_at_ramp_bars_and_stays_there():
    ramp_bars = 5
    g = Genome().child([
        ("agents.risk_judge.genes.cold_start_ramp_bars", ramp_bars),
        ("agents.risk_judge.genes.cold_start_ramp_start_scale", 0.0),
    ])
    judge = RiskJudge(g)
    baseline = RiskJudge(Genome())
    proposals = _unanimous_buy_proposals()
    b = _briefing()

    base_amount = baseline.rule(b, proposals, n_consults=3).orders[0].quote_amount

    amounts = []
    for _ in range(ramp_bars + 3):
        v = judge.rule(b, proposals, n_consults=3)
        amounts.append(v.orders[0].quote_amount if v.orders else 0.0)

    # bar 0 fully suppressed (start_scale 0.0)
    assert amounts[0] == 0.0
    # monotonically non-decreasing while ramping
    assert all(a <= b_ for a, b_ in zip(amounts[:ramp_bars], amounts[1:ramp_bars + 1]))
    # once past ramp_bars, full size, matching the unramped judge exactly
    for a in amounts[ramp_bars:]:
        assert a == pytest.approx(base_amount)


def test_ramp_counter_is_per_instance_not_global():
    g = Genome().child([
        ("agents.risk_judge.genes.cold_start_ramp_bars", 3),
        ("agents.risk_judge.genes.cold_start_ramp_start_scale", 0.0),
    ])
    proposals = _unanimous_buy_proposals()
    b = _briefing()

    j1 = RiskJudge(g)
    for _ in range(3):
        j1.rule(b, proposals, n_consults=3)
    j2 = RiskJudge(g)  # a fresh judge (new fold / new backtest) starts cold again
    v = j2.rule(b, proposals, n_consults=3)
    # start_scale 0.0 fully suppresses bar 0's size -> RiskJudge vetoes it
    # outright (amount <= 0), same "no room" path a zero cash_avail would hit
    assert v.orders == []
    assert any(veto.reason == "no room: size cap or cash floor" for veto in v.vetoes)


def test_conviction_boost_is_a_true_noop_at_default():
    # marginal conviction, just above the default 0.30 floor
    g = Genome().child([
        ("agents.risk_judge.genes.cold_start_ramp_bars", 10),
        ("agents.risk_judge.genes.cold_start_ramp_start_scale", 0.5),
    ])
    judge = RiskJudge(g)
    proposals = _unanimous_buy_proposals(conviction=0.32)
    b = _briefing()
    v = judge.rule(b, proposals, n_consults=3)
    assert v.orders  # boost defaults to 0.0 -> min_conviction floor unchanged


def test_conviction_boost_vetoes_marginal_entry_at_cold_start():
    g = Genome().child([
        ("agents.risk_judge.genes.cold_start_ramp_bars", 10),
        ("agents.risk_judge.genes.cold_start_ramp_start_scale", 1.0),
        ("agents.risk_judge.genes.cold_start_ramp_min_conviction_boost", 0.10),
    ])
    judge = RiskJudge(g)
    # conviction 0.32 clears the base 0.30 floor but not 0.30 + 0.10 boost
    proposals = _unanimous_buy_proposals(conviction=0.32)
    b = _briefing()
    v = judge.rule(b, proposals, n_consults=3)
    assert v.orders == []
    assert any(veto.reason.startswith("conviction") for veto in v.vetoes)


def test_conviction_boost_tapers_to_zero_by_ramp_bars():
    ramp_bars = 4
    g = Genome().child([
        ("agents.risk_judge.genes.cold_start_ramp_bars", ramp_bars),
        ("agents.risk_judge.genes.cold_start_ramp_start_scale", 1.0),
        ("agents.risk_judge.genes.cold_start_ramp_min_conviction_boost", 0.10),
    ])
    judge = RiskJudge(g)
    proposals = _unanimous_buy_proposals(conviction=0.32)
    b = _briefing()

    vetoed = []
    for _ in range(ramp_bars + 2):
        v = judge.rule(b, proposals, n_consults=3)
        vetoed.append(v.orders == [])

    # bar 0: full boost (0.30 + 0.10 = 0.40) vetoes the 0.32-conviction entry
    assert vetoed[0] is True
    # once past ramp_bars, boost is fully tapered off -> entry clears again
    assert all(v is False for v in vetoed[ramp_bars:])


def test_conviction_boost_leaves_sizing_ramp_unaffected():
    # the two levers are independent: a conviction boost alone (start_scale
    # left at 1.0) must not change order size for entries that do clear it
    g = Genome().child([
        ("agents.risk_judge.genes.cold_start_ramp_bars", 5),
        ("agents.risk_judge.genes.cold_start_ramp_start_scale", 1.0),
        ("agents.risk_judge.genes.cold_start_ramp_min_conviction_boost", 0.05),
    ])
    judge = RiskJudge(g)
    baseline = RiskJudge(Genome())
    proposals = _unanimous_buy_proposals(conviction=0.9)  # well clear of any boost
    b = _briefing()

    base_amount = baseline.rule(b, proposals, n_consults=3).orders[0].quote_amount
    boosted_amount = judge.rule(b, proposals, n_consults=3).orders[0].quote_amount
    assert boosted_amount == pytest.approx(base_amount)
