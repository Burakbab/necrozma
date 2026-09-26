"""`loop.engine.benchmark_sell_short` -- the AGENTS.md item 5 "how much
upside is theoretically on the table from shorting" diagnostic.

Core claims under test: at zero cost, an equal-weight short's total_return
is exactly the negative of the equal-weight true fill-to-fill long return
(entry = `replay.next_open(s, start)`, exit = `replay.close_at(s, end-1)` --
NOT `benchmark_buy_hold`'s own reported number, which values its starting
position at the close of the entry bar instead of the fill price used to
size it, a one-bar reference-point difference that's negligible over a real
multi-bar window but visible in a short synthetic one with an exaggerated
per-bar move -- see `benchmark_sell_short`'s docstring), and real costs
(fee/slippage/borrow) only ever pull that number down, never up.
"""
import numpy as np
import pandas as pd
import pytest

from core.market import Replay
from loop.engine import benchmark_sell_short


def _trend_df(prices: list[float], freq: str = "1D") -> pd.DataFrame:
    """A deterministic OHLCV frame whose close path is exactly `prices` and
    whose open equals the previous bar's close (matching `synthetic_ohlcv`'s
    convention) -- gives exact, hand-checkable entry/exit fills instead of a
    random walk."""
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


def _declining():
    # 30 bars, steady 1%/bar decline.
    return _trend_df([100.0 * (0.99 ** i) for i in range(30)])


def _rising():
    return _trend_df([100.0 * (1.01 ** i) for i in range(30)])


def _true_fill_to_fill_return(prices: list[float], start: int, end: int) -> float:
    """The TRUE long return a real fill would experience: entry at the open
    of bar `start + 1` (== close of bar `start`, by `_trend_df`'s
    convention), exit at the close of bar `end - 1`."""
    entry = prices[start]
    exitp = prices[end - 1]
    return exitp / entry - 1


def test_zero_cost_short_mirrors_negative_true_long_return_declining():
    prices = [100.0 * (0.99 ** i) for i in range(30)]
    replay = Replay({"FOO": _trend_df(prices)})
    short = benchmark_sell_short(replay, ["FOO"], 0, 29, cash=10_000.0,
                                 fee_bps=0.0, slippage_bps=0.0, borrow_bps_per_bar=0.0)
    expected = -_true_fill_to_fill_return(prices, 0, 29)
    assert short["total_return"] == pytest.approx(expected, rel=1e-9, abs=1e-12)


def test_zero_cost_short_mirrors_negative_true_long_return_rising():
    prices = [100.0 * (1.01 ** i) for i in range(30)]
    replay = Replay({"FOO": _trend_df(prices)})
    short = benchmark_sell_short(replay, ["FOO"], 0, 29, cash=10_000.0,
                                 fee_bps=0.0, slippage_bps=0.0, borrow_bps_per_bar=0.0)
    expected = -_true_fill_to_fill_return(prices, 0, 29)
    assert short["total_return"] == pytest.approx(expected, rel=1e-9, abs=1e-12)


def test_short_profits_in_a_decline():
    replay = Replay({"FOO": _declining()})
    short = benchmark_sell_short(replay, ["FOO"], 0, 29, cash=10_000.0,
                                 fee_bps=10.0, slippage_bps=5.0, borrow_bps_per_bar=0.0)
    assert short["total_return"] > 0
    assert short["trades"] == 1


def test_short_loses_in_a_rally():
    replay = Replay({"FOO": _rising()})
    short = benchmark_sell_short(replay, ["FOO"], 0, 29, cash=10_000.0,
                                 fee_bps=10.0, slippage_bps=5.0, borrow_bps_per_bar=0.0)
    assert short["total_return"] < 0


def test_costs_and_borrow_only_ever_reduce_the_return():
    replay = Replay({"FOO": _declining()})
    zero_cost = benchmark_sell_short(replay, ["FOO"], 0, 29, cash=10_000.0,
                                     fee_bps=0.0, slippage_bps=0.0, borrow_bps_per_bar=0.0)
    with_fees = benchmark_sell_short(replay, ["FOO"], 0, 29, cash=10_000.0,
                                     fee_bps=10.0, slippage_bps=5.0, borrow_bps_per_bar=0.0)
    with_borrow = benchmark_sell_short(replay, ["FOO"], 0, 29, cash=10_000.0,
                                       fee_bps=10.0, slippage_bps=5.0, borrow_bps_per_bar=5.0)
    assert with_fees["total_return"] < zero_cost["total_return"]
    assert with_borrow["total_return"] < with_fees["total_return"]


def test_equal_weight_two_symbols_matches_average_of_individual_returns():
    # Two different price paths -- the equal-weight short's total_return
    # should be exactly the average of each symbol's own zero-cost short
    # return (no cross-terms: each symbol's notional and PnL are additive
    # in cash, per `PaperBroker`'s accounting).
    foo_prices = [100.0 * (0.99 ** i) for i in range(30)]
    bar_prices = [100.0 / (0.99 ** i) for i in range(30)]
    replay = Replay({"FOO": _trend_df(foo_prices), "BAR": _trend_df(bar_prices)})
    short = benchmark_sell_short(replay, ["FOO", "BAR"], 0, 29, cash=10_000.0,
                                 fee_bps=0.0, slippage_bps=0.0, borrow_bps_per_bar=0.0)
    assert short["trades"] == 2
    expected = np.mean([-_true_fill_to_fill_return(foo_prices, 0, 29),
                        -_true_fill_to_fill_return(bar_prices, 0, 29)])
    assert short["total_return"] == pytest.approx(expected, rel=1e-9, abs=1e-12)


def test_empty_when_no_usable_symbols():
    replay = Replay({"FOO": _declining()})
    assert benchmark_sell_short(replay, ["NOPE"], 0, 29, cash=10_000.0) == {}


def test_too_short_window_returns_empty():
    replay = Replay({"FOO": _declining()})
    assert benchmark_sell_short(replay, ["FOO"], 0, 2, cash=10_000.0) == {}
