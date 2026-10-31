"""`loop.engine.benchmark_breadth_trend_short` -- AGENTS.md item 5's second
attempt at "a genuinely new signal to pair with trend-break, not another way
of wiring the existing regime classifier to it" (the 2026-10-24
`regime-combo-oos` writeup's own framing of what the next session on this
item should try). `benchmark_dual_trend_short` tried a TEMPORAL confirmation
(the slow SMA's own trajectory over time) and its sweet spot didn't survive
an out-of-sample check (`dual-trend-oos`, 2026-10-17). This tests a
CROSS-SECTIONAL confirmation instead: BREADTH, the fraction of the universe
whose own trend already reads a breakdown this bar -- a purely price-only,
non-regime measure of whether a decline is broad-based or idiosyncratic.
Covering is governed by trend-break alone (same ablation discipline
`benchmark_dual_trend_short`/`benchmark_asymmetric_short` both used), so
these tests isolate the entry filter's own effect.
"""
import numpy as np
import pandas as pd
import pytest

from core.market import Replay
from loop.engine import benchmark_breadth_trend_short, benchmark_trend_break_short


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


def _bull(n: int = 100) -> list[float]:
    return [100.0 * (1.01 ** i) for i in range(n)]


def _bear(n: int = 100) -> list[float]:
    return [100.0 * (0.97 ** i) for i in range(n)]


FAST, SLOW = 5, 10


def test_never_shorts_a_sustained_bull_run():
    replay = Replay({"FOO": _trend_df(_bull())})
    r = benchmark_breadth_trend_short(replay, ["FOO"], 0, 99, cash=10_000.0,
                                      fast=FAST, slow=SLOW,
                                      fee_bps=10.0, slippage_bps=5.0)
    assert r["symbol_bars_short"] == 0
    assert r["trades"] == 0
    assert r["total_return"] == pytest.approx(0.0, abs=1e-9)


def test_shorts_and_profits_when_the_whole_universe_declines():
    # Every symbol breaking down together -> breadth is 1.0 every bar, so
    # this must behave exactly like plain trend-break for each symbol.
    replay = Replay({"A": _trend_df(_bear()), "B": _trend_df(_bear())})
    r = benchmark_breadth_trend_short(replay, ["A", "B"], 0, 99, cash=10_000.0,
                                      fast=FAST, slow=SLOW,
                                      fee_bps=10.0, slippage_bps=5.0)
    assert r["symbol_bars_short"] > 0
    assert r["trades"] >= 1
    assert r["total_return"] > 0


def test_breadth_filter_blocks_an_idiosyncratic_decline_in_a_broadly_bullish_universe():
    # One symbol breaks down while three others keep climbing: breadth is
    # 1/4 = 0.25 every bar DOWN's own trend qualifies. At the default
    # breadth_threshold (0.4), that is below the bar, so breadth-trend must
    # refuse to open a short on DOWN at all -- even though DOWN's own
    # trend-break condition fires on its own (plain trend-break opens it).
    universe = {"DOWN": _trend_df(_bear()),
               "UP1": _trend_df(_bull()), "UP2": _trend_df(_bull()),
               "UP3": _trend_df(_bull())}
    replay = Replay(universe)
    syms = list(universe.keys())
    plain = benchmark_trend_break_short(replay, syms, 0, 99, cash=10_000.0,
                                        fast=FAST, slow=SLOW,
                                        fee_bps=10.0, slippage_bps=5.0)
    breadth = benchmark_breadth_trend_short(replay, syms, 0, 99, cash=10_000.0,
                                            fast=FAST, slow=SLOW,
                                            breadth_threshold=0.4,
                                            fee_bps=10.0, slippage_bps=5.0)
    assert plain["symbol_bars_short"] > 0
    assert breadth["symbol_bars_short"] == 0
    assert breadth["trades"] == 0


def test_lowering_the_breadth_threshold_lets_the_same_idiosyncratic_decline_through():
    # Same universe as above (breadth caps at 0.25), but with the
    # threshold lowered below that ceiling the short should now open.
    universe = {"DOWN": _trend_df(_bear()),
               "UP1": _trend_df(_bull()), "UP2": _trend_df(_bull()),
               "UP3": _trend_df(_bull())}
    replay = Replay(universe)
    syms = list(universe.keys())
    r = benchmark_breadth_trend_short(replay, syms, 0, 99, cash=10_000.0,
                                      fast=FAST, slow=SLOW,
                                      breadth_threshold=0.1,
                                      fee_bps=10.0, slippage_bps=5.0)
    assert r["symbol_bars_short"] > 0
    assert r["trades"] >= 1


def test_majority_decline_clears_the_default_threshold():
    # Three of four symbols decline together (breadth 0.75 >= 0.4): all
    # three should open, same as plain trend-break would for each of them.
    universe = {"D1": _trend_df(_bear()), "D2": _trend_df(_bear()),
               "D3": _trend_df(_bear()), "UP": _trend_df(_bull())}
    replay = Replay(universe)
    syms = list(universe.keys())
    r = benchmark_breadth_trend_short(replay, syms, 0, 99, cash=10_000.0,
                                      fast=FAST, slow=SLOW,
                                      breadth_threshold=0.4,
                                      fee_bps=10.0, slippage_bps=5.0)
    assert r["symbol_bars_short"] > 0
    assert r["trades"] >= 3


def test_costs_and_borrow_only_ever_reduce_the_return():
    replay = Replay({"A": _trend_df(_bear()), "B": _trend_df(_bear())})
    syms = ["A", "B"]
    zero_cost = benchmark_breadth_trend_short(replay, syms, 0, 99, cash=10_000.0,
                                              fast=FAST, slow=SLOW,
                                              fee_bps=0.0, slippage_bps=0.0,
                                              borrow_bps_per_bar=0.0)
    with_fees = benchmark_breadth_trend_short(replay, syms, 0, 99, cash=10_000.0,
                                              fast=FAST, slow=SLOW,
                                              fee_bps=10.0, slippage_bps=5.0,
                                              borrow_bps_per_bar=0.0)
    with_borrow = benchmark_breadth_trend_short(replay, syms, 0, 99, cash=10_000.0,
                                                 fast=FAST, slow=SLOW,
                                                 fee_bps=10.0, slippage_bps=5.0,
                                                 borrow_bps_per_bar=5.0)
    assert with_fees["total_return"] < zero_cost["total_return"]
    assert with_borrow["total_return"] < with_fees["total_return"]


def test_empty_when_no_usable_symbols():
    replay = Replay({"FOO": _trend_df(_bear())})
    assert benchmark_breadth_trend_short(replay, ["NOPE"], 0, 99, cash=10_000.0) == {}


def test_too_short_window_returns_empty():
    replay = Replay({"FOO": _trend_df(_bear())})
    assert benchmark_breadth_trend_short(replay, ["FOO"], 0, 2, cash=10_000.0) == {}


def test_single_symbol_bars_short_never_exceeds_bars_total():
    replay = Replay({"FOO": _trend_df(_bear())})
    r = benchmark_breadth_trend_short(replay, ["FOO"], 0, 99, cash=10_000.0,
                                      fast=FAST, slow=SLOW,
                                      fee_bps=10.0, slippage_bps=5.0)
    assert 0 <= r["symbol_bars_short"] <= r["bars_total"]
    assert r["avg_concurrent_short"] == pytest.approx(
        r["symbol_bars_short"] / r["bars_total"])


def test_multi_symbol_bars_short_can_exceed_bars_total():
    replay = Replay({"A": _trend_df(_bear()), "B": _trend_df(_bear()),
                     "C": _trend_df(_bear())})
    r = benchmark_breadth_trend_short(replay, ["A", "B", "C"], 0, 99, cash=10_000.0,
                                      fast=FAST, slow=SLOW,
                                      fee_bps=10.0, slippage_bps=5.0)
    assert r["symbol_bars_short"] > r["bars_total"]
    assert r["avg_concurrent_short"] > 1.0
