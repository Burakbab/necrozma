"""`loop.engine.benchmark_regime_conditional_short` -- the follow-up to
`short-headroom`'s first result (AGENTS.md item 5, 2026-09-26): a permanent
equal-weight short lost badly in 3 of the champion's 4 real windows (all
bull) and only helped in the one real bear window. This tests the
regime-*conditional* version -- short only open on bars where the real,
causal `agents.analyst.Analyst._regime` classifier (the same one
`RiskJudge.rule`'s `regime_scale` gene already gates *long* entries by)
reads `bear`/`crisis` -- against a small, hand-built genome and synthetic
price paths whose regime is unambiguous by construction.
"""
import copy

import numpy as np
import pandas as pd
import pytest

from core.genome import SEED_GENOME, Genome
from core.market import Replay
from loop.engine import benchmark_regime_conditional_short


def _make_genome(symbols: list[str], anchor: str) -> Genome:
    """A genome whose analyst gene periods are small enough that a ~150-bar
    synthetic series clears warmup well before any test's `start` index, and
    whose universe/regime_anchor point at the caller's own synthetic
    symbols -- everything else (risk/broker/consult genes) is irrelevant to
    this function (it never touches RiskJudge/SuperiorJudge/Trader) and is
    left at the seed default.
    """
    data = copy.deepcopy(SEED_GENOME)
    data["universe"] = list(symbols)
    data["agents"]["analyst"]["genes"] = {
        "trend_fast": 5, "trend_slow": 10, "rsi_len": 5,
        "vol_short": 5, "vol_long": 10, "breakout_len": 10, "z_len": 10,
        "regime_ma": 10, "regime_anchor": anchor, "volume_len": 10,
    }
    return Genome(data)


def _trend_df(prices: list[float], freq: str = "1D") -> pd.DataFrame:
    """Same deterministic-fill convention as `test_short_headroom_benchmark`'s
    helper: close path is exactly `prices`, open equals the previous close."""
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


def _bull(n: int = 150) -> list[float]:
    return [100.0 * (1.01 ** i) for i in range(n)]


def _bear(n: int = 150) -> list[float]:
    return [100.0 * (0.99 ** i) for i in range(n)]


def _bull_then_bear(n_bull: int = 75, n_bear: int = 75) -> list[float]:
    up = [100.0 * (1.01 ** i) for i in range(n_bull)]
    down = [up[-1] * (0.99 ** i) for i in range(1, n_bear + 1)]
    return up + down


def test_never_shorts_a_sustained_bull_run():
    prices = _bull()
    genome = _make_genome(["FOO"], "FOO")
    replay = Replay({"FOO": _trend_df(prices)})
    res = benchmark_regime_conditional_short(replay, genome, ["FOO"], 40, 149,
                                              cash=10_000.0)
    assert res["bars_short"] == 0
    assert res["flips"] == 0
    assert res["trades"] == 0
    assert res["total_return"] == pytest.approx(0.0, abs=1e-12)


def test_shorts_through_a_sustained_decline():
    prices = _bear()
    genome = _make_genome(["FOO"], "FOO")
    replay = Replay({"FOO": _trend_df(prices)})
    res = benchmark_regime_conditional_short(replay, genome, ["FOO"], 40, 149,
                                              cash=10_000.0,
                                              fee_bps=10.0, slippage_bps=5.0)
    assert res["bars_short"] > 0
    assert res["trades"] >= 1
    assert res["total_return"] > 0  # a short profits from a real decline


def test_conditional_short_is_flat_less_often_in_a_mixed_window():
    # Bull first half, bear second half -- the conditional short should stay
    # flat through the bull segment (unlike a permanent short, which would
    # be short the whole window) and only engage once the decline starts.
    prices = _bull_then_bear()
    genome = _make_genome(["FOO"], "FOO")
    replay = Replay({"FOO": _trend_df(prices)})
    res = benchmark_regime_conditional_short(replay, genome, ["FOO"], 40, 149,
                                              cash=10_000.0)
    assert 0 < res["bars_short"] < res["bars_total"]
    assert res["flips"] >= 1


def test_costs_and_borrow_only_ever_reduce_the_return():
    prices = _bear()
    genome = _make_genome(["FOO"], "FOO")
    replay = Replay({"FOO": _trend_df(prices)})
    zero_cost = benchmark_regime_conditional_short(
        replay, genome, ["FOO"], 40, 149, cash=10_000.0,
        fee_bps=0.0, slippage_bps=0.0, borrow_bps_per_bar=0.0)
    with_fees = benchmark_regime_conditional_short(
        replay, genome, ["FOO"], 40, 149, cash=10_000.0,
        fee_bps=10.0, slippage_bps=5.0, borrow_bps_per_bar=0.0)
    with_borrow = benchmark_regime_conditional_short(
        replay, genome, ["FOO"], 40, 149, cash=10_000.0,
        fee_bps=10.0, slippage_bps=5.0, borrow_bps_per_bar=5.0)
    assert with_fees["total_return"] < zero_cost["total_return"]
    assert with_borrow["total_return"] < with_fees["total_return"]


def test_equal_weight_two_symbols_both_traded_in_a_shared_decline():
    foo_prices = _bear()
    bar_prices = [90.0 * (0.99 ** i) for i in range(150)]
    genome = _make_genome(["FOO", "BAR"], "FOO")
    replay = Replay({"FOO": _trend_df(foo_prices), "BAR": _trend_df(bar_prices)})
    res = benchmark_regime_conditional_short(replay, genome, ["FOO", "BAR"], 40, 149,
                                              cash=10_000.0)
    assert res["bars_short"] > 0
    assert res["trades"] >= 2  # both symbols opened (and closed) at least once


def test_empty_when_no_usable_symbols():
    genome = _make_genome(["FOO"], "FOO")
    replay = Replay({"FOO": _trend_df(_bear())})
    assert benchmark_regime_conditional_short(replay, genome, ["NOPE"], 40, 149,
                                              cash=10_000.0) == {}


def test_too_short_window_returns_empty():
    genome = _make_genome(["FOO"], "FOO")
    replay = Replay({"FOO": _trend_df(_bear())})
    assert benchmark_regime_conditional_short(replay, genome, ["FOO"], 40, 42,
                                              cash=10_000.0) == {}
