"""agents.judges.flag_hard_call -- deterministic triage for which decision-log
bars are worth a slower second look. Purely additive: it is computed AFTER
the Trader has already executed fills, so it can never change what a tick
does, only what gets logged about it. This is the "flag hard calls" half of
the LLM-backed-consult item in AGENTS.md; the other half (acting on a flag)
is not built yet."""
from agents.judges import flag_hard_call
from core.genome import Genome
from core.types import Order
from loop.engine import run_backtest

from tests.helpers import synthetic_ohlcv

SYMBOLS = ["FOO", "BAR", "BAZ"]


def _buy(symbol="FOO"):
    return Order(symbol=symbol, side="buy", quote_amount=100.0)


def _sell(symbol="FOO"):
    return Order(symbol=symbol, side="sell", fraction=1.0)


def test_quiet_bar_is_not_a_hard_call():
    flag = flag_hard_call(agreement_score=0.9, orders=[_buy()],
                          just_halted=False, overrides_this_bar=0)
    assert flag == {"is_hard_call": False, "reasons": []}


def test_circuit_breaker_trip_is_always_a_hard_call():
    flag = flag_hard_call(agreement_score=0.9, orders=[], just_halted=True,
                          overrides_this_bar=0)
    assert flag["is_hard_call"] is True
    assert "circuit breaker" in flag["reasons"][0]


def test_superior_override_is_a_hard_call():
    flag = flag_hard_call(agreement_score=0.9, orders=[_buy()], just_halted=False,
                          overrides_this_bar=1)
    assert flag["is_hard_call"] is True
    assert any("superior_judge intervened" in r for r in flag["reasons"])


def test_low_agreement_behind_a_live_buy_is_a_hard_call():
    flag = flag_hard_call(agreement_score=0.1, orders=[_buy()], just_halted=False,
                          overrides_this_bar=0)
    assert flag["is_hard_call"] is True
    assert any("low consult agreement" in r for r in flag["reasons"])


def test_low_agreement_without_any_buy_is_not_a_hard_call():
    """The threshold only matters when it's actually gating money moving --
    a sell-only bar with weak agreement isn't a disagreement worth escalating,
    it's just an exit."""
    flag = flag_hard_call(agreement_score=0.1, orders=[_sell()], just_halted=False,
                          overrides_this_bar=0)
    assert flag == {"is_hard_call": False, "reasons": []}


def test_reasons_accumulate_for_multiple_triggers():
    flag = flag_hard_call(agreement_score=0.1, orders=[_buy()], just_halted=True,
                          overrides_this_bar=3)
    assert flag["is_hard_call"] is True
    assert len(flag["reasons"]) == 3


def test_agreement_threshold_is_configurable():
    flag = flag_hard_call(agreement_score=0.5, orders=[_buy()], just_halted=False,
                          overrides_this_bar=0, low_agreement_threshold=0.6)
    assert flag["is_hard_call"] is True


def _genome():
    return Genome().child([("universe", SYMBOLS)])


def test_every_logged_bar_carries_a_hard_call_flag():
    """End-to-end wiring check: run_backtest's decision_log entries all carry
    a well-shaped hard_call field, without asserting on which specific bars
    got flagged (that depends on genome tuning, not on this plumbing)."""
    data = {s: synthetic_ohlcv(240, seed=i) for i, s in enumerate(SYMBOLS)}
    result = run_backtest(_genome(), data, log_detail=True)
    assert "error" not in result
    log = result["decision_log"]
    assert log, "expected at least one logged bar from a 240-bar synthetic run"
    for entry in log:
        assert "hard_call" in entry
        flag = entry["hard_call"]
        assert set(flag) == {"is_hard_call", "reasons"}
        assert isinstance(flag["is_hard_call"], bool)
        assert isinstance(flag["reasons"], list)
        assert flag["is_hard_call"] == bool(flag["reasons"])


def test_hard_call_computation_cannot_affect_execution():
    """hard_call is computed strictly after the Trader has already executed
    fills for the bar -- running with log_detail off (skipping the flag
    entirely) must produce byte-identical trading outcomes."""
    data = {s: synthetic_ohlcv(240, seed=i) for i, s in enumerate(SYMBOLS)}
    with_log = run_backtest(_genome(), data, log_detail=True)
    without_log = run_backtest(_genome(), data, log_detail=False)
    assert with_log["stats"] == without_log["stats"]
    assert with_log["closed_trades"] == without_log["closed_trades"]
