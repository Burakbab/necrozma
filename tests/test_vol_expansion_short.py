"""`loop.engine.benchmark_vol_expansion_short` -- AGENTS.md item 5's third
genuinely new confirmation dimension for `benchmark_trend_break_short`'s
entry, alongside `benchmark_dual_trend_short`'s TEMPORAL and
`benchmark_breadth_trend_short`'s CROSS-SECTIONAL dimensions. This one asks
about the CHARACTER of the move: is the pullback accompanied by a real
expansion in realized volatility (short-term return stdev well above
long-term), the signature of a genuine breakdown, or is it a quiet drift
that happens to clear the trend-break threshold? Covering is governed by
trend-break alone (same ablation discipline every sibling in this module
uses), so these tests isolate the entry filter.
"""
import numpy as np
import pandas as pd
import pytest

from core.market import Replay
from loop.engine import (benchmark_vol_expansion_short, benchmark_trend_break_short,
                         _realized_vol_ratio)


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


def _bear_calm(n: int = 100) -> list[float]:
    # Smooth, low-volatility decline: trend-break fires, but realized vol
    # stays essentially flat -- no expansion to confirm against.
    return [100.0 * (0.97 ** i) for i in range(n)]


def _bear_volatile(n: int = 100, seed: int = 7) -> list[float]:
    # Same ~3%/bar average decline, but with added noise in the back half
    # of the series so short-term realized vol is well above long-term by
    # the time the series ends -- a real volatility-expansion event, not
    # just a steady drift.
    rng = np.random.default_rng(seed)
    out = [100.0]
    for i in range(1, n):
        drift = -0.03
        noise = rng.normal(0.0, 0.0005) if i < n - 25 else rng.normal(0.0, 0.05)
        out.append(out[-1] * (1.0 + drift + noise))
    return out


FAST, SLOW, VS, VL = 5, 10, 5, 20


def test_never_shorts_a_sustained_bull_run():
    replay = Replay({"FOO": _trend_df(_bull())})
    r = benchmark_vol_expansion_short(replay, ["FOO"], 0, 99, cash=10_000.0,
                                      fast=FAST, slow=SLOW, vol_short=VS, vol_long=VL,
                                      fee_bps=10.0, slippage_bps=5.0)
    assert r["symbol_bars_short"] == 0
    assert r["trades"] == 0
    assert r["total_return"] == pytest.approx(0.0, abs=1e-9)


def test_calm_decline_can_be_filtered_out_by_a_high_threshold():
    # A smooth, low-noise decline has a vol_ratio close to 1.0 throughout
    # (short-term and long-term realized vol are roughly equal when the
    # whole path is one steady drift) -- a high enough threshold should
    # block it even though plain trend-break fires freely.
    replay = Replay({"FOO": _trend_df(_bear_calm())})
    plain = benchmark_trend_break_short(replay, ["FOO"], 0, 99, cash=10_000.0,
                                        fast=FAST, slow=SLOW,
                                        fee_bps=10.0, slippage_bps=5.0)
    gated = benchmark_vol_expansion_short(replay, ["FOO"], 0, 99, cash=10_000.0,
                                          fast=FAST, slow=SLOW, vol_short=VS, vol_long=VL,
                                          vol_ratio_threshold=5.0,
                                          fee_bps=10.0, slippage_bps=5.0)
    assert plain["symbol_bars_short"] > 0
    assert gated["symbol_bars_short"] == 0
    assert gated["trades"] == 0


def test_shorts_a_genuinely_volatile_decline():
    replay = Replay({"FOO": _trend_df(_bear_volatile())})
    r = benchmark_vol_expansion_short(replay, ["FOO"], 0, 99, cash=10_000.0,
                                      fast=FAST, slow=SLOW, vol_short=VS, vol_long=VL,
                                      vol_ratio_threshold=1.3,
                                      fee_bps=10.0, slippage_bps=5.0)
    assert r["symbol_bars_short"] > 0
    assert r["trades"] >= 1


def test_costs_and_borrow_only_ever_reduce_the_return():
    replay = Replay({"FOO": _trend_df(_bear_volatile())})
    zero_cost = benchmark_vol_expansion_short(replay, ["FOO"], 0, 99, cash=10_000.0,
                                              fast=FAST, slow=SLOW, vol_short=VS, vol_long=VL,
                                              vol_ratio_threshold=1.3,
                                              fee_bps=0.0, slippage_bps=0.0,
                                              borrow_bps_per_bar=0.0)
    with_fees = benchmark_vol_expansion_short(replay, ["FOO"], 0, 99, cash=10_000.0,
                                              fast=FAST, slow=SLOW, vol_short=VS, vol_long=VL,
                                              vol_ratio_threshold=1.3,
                                              fee_bps=10.0, slippage_bps=5.0,
                                              borrow_bps_per_bar=0.0)
    with_borrow = benchmark_vol_expansion_short(replay, ["FOO"], 0, 99, cash=10_000.0,
                                                fast=FAST, slow=SLOW, vol_short=VS, vol_long=VL,
                                                vol_ratio_threshold=1.3,
                                                fee_bps=10.0, slippage_bps=5.0,
                                                borrow_bps_per_bar=5.0)
    assert with_fees["total_return"] < zero_cost["total_return"]
    assert with_borrow["total_return"] < with_fees["total_return"]


def test_per_symbol_independence_mixed_basket():
    replay = Replay({"UP": _trend_df(_bull()), "DOWN": _trend_df(_bear_volatile())})
    r = benchmark_vol_expansion_short(replay, ["UP", "DOWN"], 0, 99, cash=10_000.0,
                                      fast=FAST, slow=SLOW, vol_short=VS, vol_long=VL,
                                      vol_ratio_threshold=1.3,
                                      fee_bps=10.0, slippage_bps=5.0)
    assert r["trades"] >= 1


def test_empty_when_no_usable_symbols():
    replay = Replay({"FOO": _trend_df(_bear_volatile())})
    assert benchmark_vol_expansion_short(replay, ["NOPE"], 0, 99, cash=10_000.0) == {}


def test_too_short_window_returns_empty():
    replay = Replay({"FOO": _trend_df(_bear_volatile())})
    assert benchmark_vol_expansion_short(replay, ["FOO"], 0, 2, cash=10_000.0) == {}


def test_single_symbol_bars_short_never_exceeds_bars_total():
    replay = Replay({"FOO": _trend_df(_bear_volatile())})
    r = benchmark_vol_expansion_short(replay, ["FOO"], 0, 99, cash=10_000.0,
                                      fast=FAST, slow=SLOW, vol_short=VS, vol_long=VL,
                                      vol_ratio_threshold=1.3,
                                      fee_bps=10.0, slippage_bps=5.0)
    assert 0 <= r["symbol_bars_short"] <= r["bars_total"]
    assert r["avg_concurrent_short"] == pytest.approx(
        r["symbol_bars_short"] / r["bars_total"])


def test_multi_symbol_bars_short_can_exceed_bars_total():
    replay = Replay({"A": _trend_df(_bear_volatile(seed=1)),
                     "B": _trend_df(_bear_volatile(seed=2)),
                     "C": _trend_df(_bear_volatile(seed=3))})
    r = benchmark_vol_expansion_short(replay, ["A", "B", "C"], 0, 99, cash=10_000.0,
                                      fast=FAST, slow=SLOW, vol_short=VS, vol_long=VL,
                                      vol_ratio_threshold=1.3,
                                      fee_bps=10.0, slippage_bps=5.0)
    assert r["symbol_bars_short"] > r["bars_total"]
    assert r["avg_concurrent_short"] > 1.0


def test_realized_vol_ratio_direct():
    # A flat-then-noisy series: short-term window (last VS bars) has much
    # higher realized return stdev than the long-term window.
    calm = np.full(30, 100.0)
    rng = np.random.default_rng(0)
    noisy_tail = 100.0 * np.cumprod(1.0 + rng.normal(0.0, 0.05, 10))
    c = np.concatenate([calm, noisy_tail])
    ratio = _realized_vol_ratio(c, n_short=5, n_long=30)
    assert ratio > 1.0


def test_realized_vol_ratio_nan_when_too_short():
    assert np.isnan(_realized_vol_ratio(np.array([100.0, 101.0, 99.0]),
                                        n_short=5, n_long=30))


def test_realized_vol_ratio_nan_when_short_not_shorter_than_long():
    c = np.full(50, 100.0) + np.arange(50) * 0.1
    assert np.isnan(_realized_vol_ratio(c, n_short=30, n_long=30))
