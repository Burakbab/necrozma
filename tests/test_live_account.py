"""LiveAccount.tick's idempotency guard: an unattended daily job firing twice
(retry, manual re-run, clock wobble) must never double-trade the same bar.
Entirely hermetic -- core.market.load_universe is monkeypatched to synthetic
data, and the genome is passed in explicitly so the constructor never falls
back to Genome.champion() (which would touch disk under the real cwd)."""
import pytest

import core.market as market
from core.genome import Genome
from core.live import LiveAccount
from core.market import Replay

from tests.helpers import synthetic_ohlcv

SYMBOLS = ["FOO", "BAR"]


def _synthetic_data(n=120):
    return {s: synthetic_ohlcv(n, seed=i) for i, s in enumerate(SYMBOLS)}


def _account(monkeypatch, data):
    monkeypatch.setattr(market, "load_universe", lambda *a, **k: data)
    genome = Genome().child([("universe", SYMBOLS)])
    return LiveAccount({"genome": genome.data})


def _expected_bar_id(data):
    replay = Replay(data)
    i = len(replay) - 2
    return str(replay.index[i])


def test_tick_trades_a_fresh_bar(monkeypatch):
    data = _synthetic_data()
    acct = _account(monkeypatch, data)
    entry = acct.tick(use_live_price=False, refresh=False)

    assert "skipped" not in entry
    assert "error" not in entry
    assert entry["bar"] == _expected_bar_id(data)
    assert entry["tick"] == 1
    assert len(acct.journal) == 1
    assert acct.journal[-1] is entry


def test_tick_refuses_to_double_trade_the_same_bar(monkeypatch):
    data = _synthetic_data()
    acct = _account(monkeypatch, data)
    bar_id = _expected_bar_id(data)

    # simulate a previous, already-recorded trade on this exact bar
    acct.journal.append({"bar": bar_id, "tick": 1, "nav_after": 10_000.0})
    acct.ticks = 1

    result = acct.tick(use_live_price=False, refresh=False)

    assert "skipped" in result
    assert result["bar"] == bar_id
    assert result["tick"] == 1  # unchanged -- no new tick was recorded
    assert len(acct.journal) == 1  # nothing appended


def test_force_bypasses_the_idempotency_guard(monkeypatch):
    data = _synthetic_data()
    acct = _account(monkeypatch, data)
    bar_id = _expected_bar_id(data)
    acct.journal.append({"bar": bar_id, "tick": 1, "nav_after": 10_000.0})
    acct.ticks = 1

    result = acct.tick(use_live_price=False, refresh=False, force=True)

    assert "skipped" not in result
    assert len(acct.journal) == 2
    assert acct.journal[-1]["bar"] == bar_id


def test_idempotency_guard_only_looks_at_the_most_recent_journal_entry(monkeypatch):
    """The guard compares against journal[-1] only, by design -- not a scan
    of the whole journal. Document that explicitly so a future "fix" that
    changes this doesn't do so by accident."""
    data = _synthetic_data()
    acct = _account(monkeypatch, data)
    bar_id = _expected_bar_id(data)

    # this bar was traded once, long ago, but is no longer the last entry
    acct.journal.append({"bar": bar_id, "tick": 1, "nav_after": 10_000.0})
    acct.journal.append({"bar": "some-other-bar", "tick": 2, "nav_after": 10_050.0})
    acct.ticks = 2

    result = acct.tick(use_live_price=False, refresh=False)
    assert "skipped" not in result
    assert len(acct.journal) == 3


def _flagged_journal_entry(tick, bar="2020-01-01T00:00:00+00:00"):
    return {"tick": tick, "bar": bar,
           "decision": {"hard_call": {"is_hard_call": True,
                                      "reasons": ["circuit breaker tripped this bar"]}}}


def test_loading_state_without_hard_call_reviews_field_defaults_to_empty():
    """State saved before this field existed must still load cleanly --
    same backward-compatibility guarantee as every other durable field."""
    acct = LiveAccount({"genome": Genome().data})
    assert acct.hard_call_reviews == []


def test_add_hard_call_review_records_a_verdict():
    acct = LiveAccount({"genome": Genome().data})
    acct.journal.append(_flagged_journal_entry(tick=5))

    record = acct.add_hard_call_review(5, verdict="proceed", notes="looks fine")

    assert record["tick"] == 5
    assert record["bar"] == "2020-01-01T00:00:00+00:00"
    assert record["verdict"] == "proceed"
    assert record["notes"] == "looks fine"
    assert record["reasons"] == ["circuit breaker tripped this bar"]
    assert acct.hard_call_reviews == [record]


def test_add_hard_call_review_rejects_unknown_tick():
    acct = LiveAccount({"genome": Genome().data})
    with pytest.raises(ValueError):
        acct.add_hard_call_review(99, verdict="proceed")


def test_add_hard_call_review_rejects_a_tick_that_was_not_flagged():
    acct = LiveAccount({"genome": Genome().data})
    acct.journal.append({"tick": 1, "bar": "2020-01-01",
                         "decision": {"hard_call": {"is_hard_call": False, "reasons": []}}})
    with pytest.raises(ValueError):
        acct.add_hard_call_review(1, verdict="proceed")


def test_hard_call_reviews_round_trip_through_save_and_load(tmp_path):
    acct = LiveAccount({"genome": Genome().data})
    acct.journal.append(_flagged_journal_entry(tick=1))
    acct.add_hard_call_review(1, verdict="proceed", notes="ok")

    path = str(tmp_path / "state.json")
    acct.save(path)
    reloaded = LiveAccount.load(path)

    assert reloaded.hard_call_reviews == acct.hard_call_reviews
