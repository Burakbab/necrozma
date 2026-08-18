"""agents.judges.flag_hard_call -- deterministic triage for which decision-log
bars are worth a slower second look. Purely additive: it is computed AFTER
the Trader has already executed fills, so it can never change what a tick
does, only what gets logged about it. This is the "flag hard calls" half of
the LLM-backed-consult item in AGENTS.md; the other half (acting on a flag)
is not built yet."""
from agents.judges import (flag_hard_call, pending_hard_call_reviews,
                          summarize_hard_calls)
from core.genome import Genome
from core.types import Order
from loop.engine import run_backtest

from tests.helpers import synthetic_ohlcv

SYMBOLS = ["FOO", "BAR", "BAZ"]


def _buy(symbol="FOO", agreement=0.33, conviction=0.5):
    return Order(symbol=symbol, side="buy", quote_amount=100.0,
                agreement=agreement, conviction=conviction)


def _sell(symbol="FOO"):
    return Order(symbol=symbol, side="sell", fraction=1.0)


def test_quiet_bar_is_not_a_hard_call():
    flag = flag_hard_call(orders=[_buy(agreement=0.9)],
                          just_halted=False, overrides_this_bar=0)
    assert flag == {"is_hard_call": False, "reasons": []}


def test_circuit_breaker_trip_is_always_a_hard_call():
    flag = flag_hard_call(orders=[], just_halted=True, overrides_this_bar=0)
    assert flag["is_hard_call"] is True
    assert "circuit breaker" in flag["reasons"][0]


def test_superior_override_is_a_hard_call():
    flag = flag_hard_call(orders=[_buy(agreement=0.9)], just_halted=False,
                          overrides_this_bar=1)
    assert flag["is_hard_call"] is True
    assert any("superior_judge intervened" in r for r in flag["reasons"])


def test_solo_lone_voice_buy_is_a_hard_call():
    """A lone-voice buy that is the *only* order the bar produced -- the
    whole council went quiet except this one weak-consensus bet -- is the
    narrowed trigger as of 2026-08-17 (see the module docstring for why the
    prior "also the conviction leader" narrowing measured worse, not
    better)."""
    flag = flag_hard_call(orders=[_buy(agreement=0.1)], just_halted=False,
                          overrides_this_bar=0)
    assert flag["is_hard_call"] is True
    assert any("lone-voice buy" in r and "only order" in r for r in flag["reasons"])


def test_lone_voice_buy_is_not_a_hard_call_when_another_buy_accompanies_it():
    """A lone-voice buy sitting alongside another buy that bar is "one of
    several independent picks happened to be lone-voice", not "the whole
    council is quiet except one loud voice" -- not a hard call, regardless of
    which one has the higher conviction."""
    lone = _buy(symbol="FOO", agreement=0.1, conviction=0.9)
    other = _buy(symbol="BAR", agreement=1.0, conviction=0.3)
    flag = flag_hard_call(orders=[lone, other], just_halted=False, overrides_this_bar=0)
    assert flag == {"is_hard_call": False, "reasons": []}


def test_lone_voice_buy_is_not_a_hard_call_when_a_sell_accompanies_it():
    """The stricter 2026-08-17 narrowing looks at *all* orders that bar, not
    just other buys -- a lone-voice buy next to an unrelated exit is still a
    bar with more than one signal firing, not a quiet bar with a single weak
    bet."""
    lone = _buy(symbol="FOO", agreement=0.1)
    exit_ = _sell(symbol="BAR")
    flag = flag_hard_call(orders=[lone, exit_], just_halted=False, overrides_this_bar=0)
    assert flag == {"is_hard_call": False, "reasons": []}


def test_low_agreement_without_any_buy_is_not_a_hard_call():
    """The threshold only matters when it's actually gating money moving --
    a sell-only bar with weak agreement isn't a disagreement worth escalating,
    it's just an exit."""
    flag = flag_hard_call(orders=[_sell()], just_halted=False, overrides_this_bar=0)
    assert flag == {"is_hard_call": False, "reasons": []}


def test_reasons_accumulate_for_multiple_triggers():
    flag = flag_hard_call(orders=[_buy(agreement=0.1)], just_halted=True,
                          overrides_this_bar=3)
    assert flag["is_hard_call"] is True
    assert len(flag["reasons"]) == 3


def test_agreement_threshold_is_configurable():
    flag = flag_hard_call(orders=[_buy(agreement=0.5)], just_halted=False,
                          overrides_this_bar=0, low_agreement_threshold=0.6)
    assert flag["is_hard_call"] is True


def test_size_gate_off_by_default_ignores_a_small_solo_buy():
    """min_size_pct defaults to 0.0 -- a solo lone-voice buy still flags
    regardless of how small it is, same as before this axis existed."""
    small = _buy(agreement=0.1)
    small.quote_amount = 1.0  # 0.01% of a $10k nav
    flag = flag_hard_call(orders=[small], just_halted=False,
                          overrides_this_bar=0, nav=10_000.0)
    assert flag["is_hard_call"] is True


def test_size_gate_flags_a_solo_buy_that_commits_enough_equity():
    big = _buy(agreement=0.1)
    big.quote_amount = 1_500.0  # 15% of a $10k nav
    flag = flag_hard_call(orders=[big], just_halted=False, overrides_this_bar=0,
                          nav=10_000.0, min_size_pct=0.10)
    assert flag["is_hard_call"] is True
    assert any("lone-voice buy" in r and "of equity" in r for r in flag["reasons"])


def test_size_gate_does_not_flag_a_solo_buy_that_is_too_small():
    small = _buy(agreement=0.1)
    small.quote_amount = 500.0  # 5% of a $10k nav
    flag = flag_hard_call(orders=[small], just_halted=False, overrides_this_bar=0,
                          nav=10_000.0, min_size_pct=0.10)
    assert flag == {"is_hard_call": False, "reasons": []}


def test_size_gate_without_nav_fails_safe_and_does_not_flag():
    """If a caller opts into the size gate (min_size_pct > 0) but can't supply
    nav, there is no way to compute the fraction -- treat that as "gate not
    satisfied", not "gate skipped"."""
    big = _buy(agreement=0.1)
    big.quote_amount = 5_000.0
    flag = flag_hard_call(orders=[big], just_halted=False, overrides_this_bar=0,
                          min_size_pct=0.10)
    assert flag == {"is_hard_call": False, "reasons": []}


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


def _entry(hard_call=None):
    """A minimal decision-log-shaped dict -- summarize_hard_calls only ever
    reads the "ts" and "hard_call" keys, so tests don't need a real bar."""
    return {"ts": "2020-01-01", "hard_call": hard_call or {"is_hard_call": False,
                                                            "reasons": []}}


def test_summarize_empty_log():
    s = summarize_hard_calls([])
    assert s == {"n_bars": 0, "n_flagged": 0, "flag_rate": 0.0,
                 "by_category": {"circuit_breaker": 0, "superior_override": 0,
                                  "low_agreement_buy": 0},
                 "flagged": []}


def test_summarize_counts_and_rate():
    log = [
        _entry(),
        _entry({"is_hard_call": True, "reasons": ["circuit breaker tripped this bar"]}),
        _entry({"is_hard_call": True,
                "reasons": ["superior_judge intervened on 2 order(s)",
                           "lone-voice buy on FOO (agreement 0.20) is the "
                           "only order the bar produced (0.30 conviction)"]}),
    ]
    s = summarize_hard_calls(log)
    assert s["n_bars"] == 3
    assert s["n_flagged"] == 2
    assert s["flag_rate"] == 2 / 3
    assert s["by_category"] == {"circuit_breaker": 1, "superior_override": 1,
                                "low_agreement_buy": 1}
    assert [f["ts"] for f in s["flagged"]] == ["2020-01-01", "2020-01-01"]


def test_summarize_tolerates_entries_missing_the_field():
    """The live journal's earliest ticks predate the hard_call field entirely
    -- summarize_hard_calls must treat a missing key as "not flagged", not
    raise, so the CLI can run it over the whole journal unconditionally."""
    log = [{"ts": "2020-01-01"}, _entry()]
    s = summarize_hard_calls(log)
    assert s["n_bars"] == 2
    assert s["n_flagged"] == 0


def test_summarize_on_real_backtest_log_is_well_shaped():
    """End-to-end: feed a real run_backtest decision_log through and check
    the aggregate is internally consistent, without asserting on which bars
    got flagged (that depends on genome tuning)."""
    data = {s: synthetic_ohlcv(240, seed=i) for i, s in enumerate(SYMBOLS)}
    result = run_backtest(_genome(), data, log_detail=True)
    s = summarize_hard_calls(result["decision_log"])
    assert s["n_bars"] == len(result["decision_log"])
    assert s["n_flagged"] == len(s["flagged"])
    assert sum(s["by_category"].values()) >= s["n_flagged"]


def _journal_entry(tick, hard_call=None, bar="2020-01-01"):
    """A minimal journal-entry-shaped dict -- pending_hard_call_reviews only
    ever reads "tick", "bar" and decision.hard_call."""
    return {"tick": tick, "bar": bar,
           "decision": {"hard_call": hard_call or {"is_hard_call": False,
                                                    "reasons": []}}}


def test_pending_reviews_empty_when_nothing_flagged():
    journal = [_journal_entry(1), _journal_entry(2)]
    assert pending_hard_call_reviews(journal, reviews=[]) == []


def test_pending_reviews_lists_flagged_ticks_with_no_review():
    flagged = {"is_hard_call": True, "reasons": ["circuit breaker tripped this bar"]}
    journal = [_journal_entry(1), _journal_entry(2, flagged), _journal_entry(3, flagged)]
    pending = pending_hard_call_reviews(journal, reviews=[])
    assert [p["tick"] for p in pending] == [2, 3]
    assert pending[0]["bar"] == "2020-01-01"
    assert pending[0]["reasons"] == flagged["reasons"]


def test_pending_reviews_excludes_already_reviewed_ticks():
    flagged = {"is_hard_call": True, "reasons": ["circuit breaker tripped this bar"]}
    journal = [_journal_entry(2, flagged), _journal_entry(3, flagged)]
    reviews = [{"tick": 2, "verdict": "proceed"}]
    pending = pending_hard_call_reviews(journal, reviews)
    assert [p["tick"] for p in pending] == [3]


def test_pending_reviews_tolerates_entries_missing_the_decision_or_hard_call_key():
    """Ticks from before hard_call shipped, or a tick whose council.tick call
    somehow logged no decision at all, must not raise."""
    journal = [{"tick": 1}, {"tick": 2, "decision": {}}]
    assert pending_hard_call_reviews(journal, reviews=[]) == []
