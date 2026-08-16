"""Anti-lookahead-bias tests.

If any of these fail, every backtest/fitness number the evolution loop has
ever produced is suspect -- see AGENTS.md's "Current state" note on why a
committed suite matters more than most other roadmap items. Two levels:

1. Unit-level, directly against `core.market.Replay`/`ReplayWindow` -- the
   actual slicing mechanism that is supposed to make seeing the future
   structurally impossible.
2. End-to-end, through `loop.engine.run_backtest` -- poison bars strictly
   after the window a backtest is scored on and confirm the result (stats,
   trades, decision log) is bit-for-bit identical to an unpoisoned run.
"""
import copy

from core.genome import Genome
from core.market import Replay
from loop.engine import run_backtest

from tests.helpers import synthetic_ohlcv


def test_replay_window_never_sees_future_closes():
    df = synthetic_ohlcv(50, seed=1)
    replay = Replay({"FOO": df})
    i = 20

    window = None
    for idx, w in replay.walk(0, 49):
        if idx == i:
            window = w
            break
    assert window is not None

    seen = window.closes("FOO", n=300)
    expected = df["close"].to_numpy()[: i + 1]
    assert (seen == expected).all()
    assert len(seen) == i + 1  # nothing beyond index i, ever

    # poisoning everything after i must not change what the window at i sees
    poisoned = df.copy()
    poisoned.iloc[i + 1:] = poisoned.iloc[i + 1:] * 1000.0
    replay2 = Replay({"FOO": poisoned})
    window2 = None
    for idx, w in replay2.walk(0, 49):
        if idx == i:
            window2 = w
            break
    assert (window2.closes("FOO", n=300) == expected).all()
    assert window2.last_close("FOO") == window.last_close("FOO")
    assert (window2.history("FOO", n=300)["close"].to_numpy() == expected).all()


def test_replay_fills_at_next_bar_open_not_current_close():
    df = synthetic_ohlcv(50, seed=2)
    df = df.copy()
    marker = 987654.0
    df.loc[df.index[21], "open"] = marker  # the bar *after* i=20
    replay = Replay({"FOO": df})

    fill_price = replay.next_open("FOO", 20)
    assert fill_price == marker
    assert fill_price != replay.close_at("FOO", 20)


def _restricted_genome(symbols):
    return Genome().child([("universe", list(symbols))])


def _run(genome, data, end_frac):
    return run_backtest(genome, data, start_frac=0.0, end_frac=end_frac, log_detail=True)


def test_backtest_result_is_invariant_to_poisoning_bars_after_the_window():
    n = 400
    symbols = ["FOO", "BAR", "BAZ"]
    baseline = {s: synthetic_ohlcv(n, seed=100 + i, start_price=50.0 * (i + 1))
               for i, s in enumerate(symbols)}
    genome = _restricted_genome(symbols)

    end_frac = 0.65
    end = min(n - 1, int(n * end_frac))
    assert end < n - 1, "test needs real room after the window to poison"

    poisoned = copy.deepcopy(baseline)
    for s, df in poisoned.items():
        future = df.index[end + 1:]
        assert len(future) > 0
        df.loc[future, ["open", "high", "low", "close"]] *= 37.0
        df.loc[future, "volume"] *= 0.0  # also try a degenerate value, not just a spike

    base_result = _run(genome, baseline, end_frac)
    poison_result = _run(genome, poisoned, end_frac)

    assert "error" not in base_result, base_result.get("error")
    assert "error" not in poison_result, poison_result.get("error")

    assert base_result["stats"] == poison_result["stats"]
    assert base_result["nav_history"] == poison_result["nav_history"]
    assert base_result["closed_trades"] == poison_result["closed_trades"]
    assert base_result["decision_log"] == poison_result["decision_log"]
    assert base_result["fitness"] == poison_result["fitness"]


def test_backtest_result_changes_when_a_bar_inside_the_window_changes():
    """Sanity check for the test above: prove the comparison is sensitive at
    all, so an accidental no-op poison (e.g. poisoning past the end of the
    array) can't silently pass the invariance test above for the wrong
    reason."""
    n = 400
    symbols = ["FOO", "BAR"]
    baseline = {s: synthetic_ohlcv(n, seed=200 + i, start_price=80.0)
               for i, s in enumerate(symbols)}
    genome = _restricted_genome(symbols)
    end_frac = 0.65

    mutated = copy.deepcopy(baseline)
    mid = n // 3  # well inside the [start, end) window
    for s, df in mutated.items():
        df.loc[df.index[mid], ["open", "high", "low", "close"]] *= 5.0

    base_result = _run(genome, baseline, end_frac)
    mutated_result = _run(genome, mutated, end_frac)
    assert base_result["stats"] != mutated_result["stats"]
