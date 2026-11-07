"""`loop.engine.benchmark_dual_breadth_trend_short` -- AGENTS.md item 5's
combination of the two genuinely-new (non-regime) confirmation dimensions
measured separately so far: `benchmark_dual_trend_short`'s TEMPORAL filter
(the slow SMA's own trajectory) and `benchmark_breadth_trend_short`'s
CROSS-SECTIONAL filter (fraction of the universe also breaking down this
bar). Both ingredients were individually out-of-sample-checked
(`dual-trend-oos`, `breadth-trend-oos`) before being combined here -- this
tests the combination's mechanics in isolation, not a new parameter search.
Covering is governed by trend-break alone, same ablation discipline every
sibling benchmark in this module uses.
"""
import numpy as np
import pandas as pd
import pytest

from core.market import Replay
from loop.engine import (benchmark_dual_breadth_trend_short,
                         benchmark_breadth_trend_short,
                         benchmark_dual_trend_short,
                         benchmark_trend_break_short)


def _trend_df(prices: list[float], freq: str = "1D") -> pd.DataFrame:
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


def _bull(n: int = 140) -> list[float]:
    return [100.0 * (1.01 ** i) for i in range(n)]


def _bear(n: int = 140) -> list[float]:
    return [100.0 * (0.97 ** i) for i in range(n)]


def _dip_in_uptrend(n: int = 140, dip_at: int = 100, dip_len: int = 8) -> list[float]:
    """Climbs steadily, dips sharply for a short stretch (triggers
    trend-break and can drag breadth down briefly), then resumes climbing --
    the slow SMA itself never actually turns down. This is exactly the
    false-positive shape both dual-trend and breadth-trend were built to
    filter out."""
    prices = [100.0 * (1.01 ** i) for i in range(dip_at)]
    last = prices[-1]
    for j in range(dip_len):
        last *= 0.95
        prices.append(last)
    for i in range(n - dip_at - dip_len):
        last *= 1.01
        prices.append(last)
    return prices


FAST, SLOW, SLOPE_LB = 5, 10, 15


def test_never_shorts_a_sustained_bull_run():
    replay = Replay({"FOO": _trend_df(_bull())})
    r = benchmark_dual_breadth_trend_short(replay, ["FOO"], 0, 139, cash=10_000.0,
                                           fast=FAST, slow=SLOW, slope_lookback=SLOPE_LB,
                                           fee_bps=10.0, slippage_bps=5.0)
    assert r["symbol_bars_short"] == 0
    assert r["trades"] == 0
    assert r["total_return"] == pytest.approx(0.0, abs=1e-9)


def test_shorts_and_profits_when_the_whole_universe_declines_together():
    replay = Replay({"A": _trend_df(_bear()), "B": _trend_df(_bear())})
    r = benchmark_dual_breadth_trend_short(replay, ["A", "B"], 0, 139, cash=10_000.0,
                                           fast=FAST, slow=SLOW, slope_lookback=SLOPE_LB,
                                           breadth_threshold=0.4,
                                           fee_bps=10.0, slippage_bps=5.0)
    assert r["symbol_bars_short"] > 0
    assert r["trades"] >= 1
    assert r["total_return"] > 0


def test_blocks_what_trend_break_alone_would_open_on_a_dip_inside_an_uptrend():
    # A single symbol dips sharply while every other symbol in the universe
    # keeps climbing: plain trend-break opens a short on the dip (its own
    # fast/slow ratio crosses short_enter), but neither the slow-SMA-slope
    # check (the slow SMA is still net rising through a brief dip) nor the
    # breadth check (one symbol dipping among several climbing ones) should
    # pass here -- the combined filter must block it on at least one leg.
    universe = {"DIP": _trend_df(_dip_in_uptrend()),
               "UP1": _trend_df(_bull()), "UP2": _trend_df(_bull()),
               "UP3": _trend_df(_bull())}
    replay = Replay(universe)
    syms = list(universe.keys())
    plain = benchmark_trend_break_short(replay, syms, 0, 139, cash=10_000.0,
                                        fast=FAST, slow=SLOW,
                                        fee_bps=10.0, slippage_bps=5.0)
    combined = benchmark_dual_breadth_trend_short(replay, syms, 0, 139, cash=10_000.0,
                                                  fast=FAST, slow=SLOW, slope_lookback=SLOPE_LB,
                                                  breadth_threshold=0.4,
                                                  fee_bps=10.0, slippage_bps=5.0)
    assert plain["symbol_bars_short"] > 0
    assert combined["symbol_bars_short"] == 0
    assert combined["trades"] == 0


def test_combined_is_never_more_permissive_than_either_filter_alone():
    # On a universe where breadth clears the bar (whole universe bearish)
    # but not every symbol's slow SMA has actually turned down in a way
    # dual-trend would require, the combined short count must not exceed
    # what dual-trend alone opens, and must not exceed what breadth-trend
    # alone opens -- it is an AND of two filters, so it can only be more
    # restrictive than either one.
    universe = {"A": _trend_df(_bear()), "B": _trend_df(_bear()),
               "C": _trend_df(_bear())}
    replay = Replay(universe)
    syms = list(universe.keys())
    dual = benchmark_dual_trend_short(replay, syms, 0, 139, cash=10_000.0,
                                      fast=FAST, slow=SLOW, slope_lookback=SLOPE_LB,
                                      fee_bps=10.0, slippage_bps=5.0)
    breadth = benchmark_breadth_trend_short(replay, syms, 0, 139, cash=10_000.0,
                                            fast=FAST, slow=SLOW, breadth_threshold=0.4,
                                            fee_bps=10.0, slippage_bps=5.0)
    combined = benchmark_dual_breadth_trend_short(replay, syms, 0, 139, cash=10_000.0,
                                                  fast=FAST, slow=SLOW, slope_lookback=SLOPE_LB,
                                                  breadth_threshold=0.4,
                                                  fee_bps=10.0, slippage_bps=5.0)
    assert combined["symbol_bars_short"] <= dual["symbol_bars_short"]
    assert combined["symbol_bars_short"] <= breadth["symbol_bars_short"]


def test_raising_breadth_threshold_only_ever_reduces_shorting():
    universe = {"DOWN": _trend_df(_bear()),
               "UP1": _trend_df(_bull()), "UP2": _trend_df(_bull()),
               "UP3": _trend_df(_bull())}
    replay = Replay(universe)
    syms = list(universe.keys())
    loose = benchmark_dual_breadth_trend_short(replay, syms, 0, 139, cash=10_000.0,
                                               fast=FAST, slow=SLOW, slope_lookback=SLOPE_LB,
                                               breadth_threshold=0.1,
                                               fee_bps=10.0, slippage_bps=5.0)
    strict = benchmark_dual_breadth_trend_short(replay, syms, 0, 139, cash=10_000.0,
                                                fast=FAST, slow=SLOW, slope_lookback=SLOPE_LB,
                                                breadth_threshold=0.9,
                                                fee_bps=10.0, slippage_bps=5.0)
    assert strict["symbol_bars_short"] <= loose["symbol_bars_short"]


def test_costs_and_borrow_only_ever_reduce_the_return():
    replay = Replay({"A": _trend_df(_bear()), "B": _trend_df(_bear())})
    syms = ["A", "B"]
    common = dict(fast=FAST, slow=SLOW, slope_lookback=SLOPE_LB, breadth_threshold=0.4)
    zero_cost = benchmark_dual_breadth_trend_short(replay, syms, 0, 139, cash=10_000.0,
                                                   fee_bps=0.0, slippage_bps=0.0,
                                                   borrow_bps_per_bar=0.0, **common)
    with_fees = benchmark_dual_breadth_trend_short(replay, syms, 0, 139, cash=10_000.0,
                                                    fee_bps=10.0, slippage_bps=5.0,
                                                    borrow_bps_per_bar=0.0, **common)
    with_borrow = benchmark_dual_breadth_trend_short(replay, syms, 0, 139, cash=10_000.0,
                                                      fee_bps=10.0, slippage_bps=5.0,
                                                      borrow_bps_per_bar=5.0, **common)
    assert with_fees["total_return"] < zero_cost["total_return"]
    assert with_borrow["total_return"] < with_fees["total_return"]


def test_empty_when_no_usable_symbols():
    replay = Replay({"FOO": _trend_df(_bear())})
    assert benchmark_dual_breadth_trend_short(replay, ["NOPE"], 0, 139, cash=10_000.0) == {}


def test_too_short_window_returns_empty():
    replay = Replay({"FOO": _trend_df(_bear())})
    assert benchmark_dual_breadth_trend_short(replay, ["FOO"], 0, 2, cash=10_000.0) == {}


def test_bars_short_bookkeeping_consistent_with_siblings():
    replay = Replay({"A": _trend_df(_bear()), "B": _trend_df(_bear()),
                     "C": _trend_df(_bear())})
    r = benchmark_dual_breadth_trend_short(replay, ["A", "B", "C"], 0, 139, cash=10_000.0,
                                           fast=FAST, slow=SLOW, slope_lookback=SLOPE_LB,
                                           breadth_threshold=0.4,
                                           fee_bps=10.0, slippage_bps=5.0)
    assert 0 <= r["symbol_bars_short"]
    assert r["avg_concurrent_short"] == pytest.approx(
        r["symbol_bars_short"] / r["bars_total"])
