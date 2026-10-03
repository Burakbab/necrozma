"""`loop.engine.benchmark_trend_break_short` -- the follow-up to
`benchmark_regime_conditional_short`'s 2026-09-27 result (AGENTS.md item 5):
that function's failure was traced to `agents.analyst.Analyst._regime` being
a single, basket-wide, anchor-only on/off switch tuned to gate *long*
entries defensively, not built or validated as a short-timing signal. This
tests the opposite shape -- a per-symbol, price-only trend-breakdown signal
(fast/slow SMA ratio, timed independently per symbol, with hysteresis
between the enter and exit thresholds) -- against synthetic price paths
whose trend is unambiguous by construction.
"""
import numpy as np
import pandas as pd
import pytest

from core.market import Replay
from loop.engine import benchmark_trend_break_short


def _trend_df(prices: list[float], freq: str = "1D") -> pd.DataFrame:
    """Same deterministic-fill convention as the other benchmark test
    files: close path is exactly `prices`, open equals the previous close."""
    n = len(prices)
    closes = np.array(prices, dtype=float)
    opens = np.empty(n)
    opens[0] = closes[0]
    opens[1:] = closes[:-1]
    highs = np.maximum(opens, closes) * 1.001
    lows = np.minimum(opens, closes) * 0.999
    volumes = np.full(n, 1_000.0)
    idx = pd.date_range("2020-01-01", periods=n, freq=freq, tz="UTC")
    return pd.DataFrame({"open": opens, "high": highs, "low": lows,
                         "close": closes, "volume": volumes}, index=idx)


def _bull(n: int = 80) -> list[float]:
    return [100.0 * (1.01 ** i) for i in range(n)]


def _bear(n: int = 80) -> list[float]:
    # Steep enough that SMA(FAST)/SMA(SLOW) - 1 clears the default
    # short_enter=-0.05 threshold once it converges (a mild decline's ratio
    # converges to a shallower constant that never crosses -0.05 at all --
    # checked numerically, not assumed).
    return [100.0 * (0.97 ** i) for i in range(n)]


# Small fast/slow so a ~80-bar synthetic series clears warmup (need =
# slow + 5) well before the window ends, same discipline the
# regime-conditional tests use for their genome's analyst periods.
FAST, SLOW = 5, 10


def test_never_shorts_a_sustained_bull_run():
    replay = Replay({"FOO": _trend_df(_bull())})
    r = benchmark_trend_break_short(replay, ["FOO"], 0, 79, cash=10_000.0,
                                    fast=FAST, slow=SLOW,
                                    fee_bps=10.0, slippage_bps=5.0)
    assert r["symbol_bars_short"] == 0
    assert r["trades"] == 0
    assert r["total_return"] == pytest.approx(0.0, abs=1e-9)


def test_shorts_and_profits_in_a_sustained_decline():
    replay = Replay({"FOO": _trend_df(_bear())})
    r = benchmark_trend_break_short(replay, ["FOO"], 0, 79, cash=10_000.0,
                                    fast=FAST, slow=SLOW,
                                    fee_bps=10.0, slippage_bps=5.0)
    assert r["symbol_bars_short"] > 0
    assert r["trades"] >= 1
    assert r["total_return"] > 0


def test_costs_and_borrow_only_ever_reduce_the_return():
    replay = Replay({"FOO": _trend_df(_bear())})
    zero_cost = benchmark_trend_break_short(replay, ["FOO"], 0, 79, cash=10_000.0,
                                            fast=FAST, slow=SLOW,
                                            fee_bps=0.0, slippage_bps=0.0,
                                            borrow_bps_per_bar=0.0)
    with_fees = benchmark_trend_break_short(replay, ["FOO"], 0, 79, cash=10_000.0,
                                            fast=FAST, slow=SLOW,
                                            fee_bps=10.0, slippage_bps=5.0,
                                            borrow_bps_per_bar=0.0)
    with_borrow = benchmark_trend_break_short(replay, ["FOO"], 0, 79, cash=10_000.0,
                                              fast=FAST, slow=SLOW,
                                              fee_bps=10.0, slippage_bps=5.0,
                                              borrow_bps_per_bar=5.0)
    assert with_fees["total_return"] < zero_cost["total_return"]
    assert with_borrow["total_return"] < with_fees["total_return"]


def test_per_symbol_independence_mixed_basket():
    # One symbol trends up throughout (never shorted), the other trends down
    # throughout (shorted) -- each symbol's own signal is timed off its own
    # price path, not the basket average.
    replay = Replay({"UP": _trend_df(_bull()), "DOWN": _trend_df(_bear())})
    r = benchmark_trend_break_short(replay, ["UP", "DOWN"], 0, 79, cash=10_000.0,
                                    fast=FAST, slow=SLOW,
                                    fee_bps=10.0, slippage_bps=5.0)
    # Exactly one symbol (DOWN) ever opens a short: one open fill plus one
    # forced close at window end, never a flip back to short afterward.
    assert r["trades"] >= 1
    assert r["flips"] <= 2


def test_hysteresis_requires_recovering_past_exit_not_just_enter():
    # A decline that breaches short_enter, then only partially recovers to
    # a level still below short_exit, should stay short rather than cover
    # and immediately re-enter -- fewer flips than a single-threshold
    # (short_enter == short_exit) version of the same price path.
    down = [100.0 * (0.985 ** i) for i in range(30)]
    partial_up = [down[-1] * (1.003 ** i) for i in range(1, 20)]
    down_again = [partial_up[-1] * (0.985 ** i) for i in range(1, 31)]
    prices = down + partial_up + down_again
    replay = Replay({"FOO": _trend_df(prices)})
    n = len(prices)
    hysteresis = benchmark_trend_break_short(
        replay, ["FOO"], 0, n - 1, cash=10_000.0, fast=FAST, slow=SLOW,
        short_enter=-0.05, short_exit=-0.02, fee_bps=10.0, slippage_bps=5.0)
    single_threshold = benchmark_trend_break_short(
        replay, ["FOO"], 0, n - 1, cash=10_000.0, fast=FAST, slow=SLOW,
        short_enter=-0.05, short_exit=-0.05, fee_bps=10.0, slippage_bps=5.0)
    assert hysteresis["flips"] <= single_threshold["flips"]


def test_empty_when_no_usable_symbols():
    replay = Replay({"FOO": _trend_df(_bear())})
    assert benchmark_trend_break_short(replay, ["NOPE"], 0, 79, cash=10_000.0) == {}


def test_too_short_window_returns_empty():
    replay = Replay({"FOO": _trend_df(_bear())})
    assert benchmark_trend_break_short(replay, ["FOO"], 0, 2, cash=10_000.0) == {}


def test_single_symbol_bars_short_never_exceeds_bars_total():
    # With exactly one symbol in the universe, at most one position can
    # ever be open, so symbol_bars_short (a (symbol, bar)-pair count) is
    # bounded by bars_total in this specific case.
    replay = Replay({"FOO": _trend_df(_bear())})
    r = benchmark_trend_break_short(replay, ["FOO"], 0, 79, cash=10_000.0,
                                    fast=FAST, slow=SLOW,
                                    fee_bps=10.0, slippage_bps=5.0)
    assert 0 <= r["symbol_bars_short"] <= r["bars_total"]
    assert r["avg_concurrent_short"] == pytest.approx(
        r["symbol_bars_short"] / r["bars_total"])


def test_multi_symbol_bars_short_can_exceed_bars_total():
    # Independent per-symbol timing means several symbols can be short on
    # the same bar at once -- symbol_bars_short is a sum over (symbol, bar)
    # pairs, not a bar count, so with enough simultaneously-shorted symbols
    # it legitimately exceeds bars_total. avg_concurrent_short > 1 is the
    # readable way to see the same fact.
    replay = Replay({"A": _trend_df(_bear()), "B": _trend_df(_bear()),
                     "C": _trend_df(_bear())})
    r = benchmark_trend_break_short(replay, ["A", "B", "C"], 0, 79, cash=10_000.0,
                                    fast=FAST, slow=SLOW,
                                    fee_bps=10.0, slippage_bps=5.0)
    assert r["symbol_bars_short"] > r["bars_total"]
    assert r["avg_concurrent_short"] > 1.0
