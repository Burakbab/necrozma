"""`loop.engine.benchmark_dual_trend_short` -- AGENTS.md item 5's next step
after `benchmark_combined_short`/`benchmark_asymmetric_short` both found the
basket-wide regime classifier to be the weak link in every combination tried
with `benchmark_trend_break_short` (2026-10-03/04 writeups): its `bear` leg
fires almost as often as individual symbols' own trend-break during ordinary
pullbacks inside a still-intact bull market, so it barely filters false
positives on the entry side and whipsaws on the exit side. This tests a
genuinely different confirmation dimension instead -- TIMEFRAME agreement,
not basket-wide regime agreement: require the slow SMA's own trajectory over
`slope_lookback` bars to be flat-or-declining (the medium-term trend itself
turning down), not just a momentary fast/slow dip, before opening a short.
Covering is governed by trend-break alone (same ablation discipline
`benchmark_asymmetric_short` used), so these tests isolate the entry filter.
"""
import numpy as np
import pandas as pd
import pytest

from core.market import Replay
from loop.engine import benchmark_dual_trend_short, benchmark_trend_break_short


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
    # Steep enough that SMA(FAST)/SMA(SLOW) - 1 clears the default
    # short_enter=-0.05 threshold once it converges, and steep enough that
    # the slow SMA itself is declining well before the window ends.
    return [100.0 * (0.97 ** i) for i in range(n)]


# Small fast/slow/slope_lookback so a ~100-bar synthetic series clears
# warmup (need = slow + slope_lookback + 5) well before the window ends.
FAST, SLOW, LOOKBACK = 5, 10, 10

# Wider separation between the fast period and the slow/lookback pair for
# the slope-filter test below: the slope check needs a slow SMA genuinely
# dominated by bars outside a brief dip, which a 10-bar slow/lookback can't
# guarantee against a dip sharp enough to also trip the fast/slow trigger.
SLOPE_FAST, SLOPE_SLOW, SLOPE_LOOKBACK = 3, 30, 20


def test_never_shorts_a_sustained_bull_run():
    replay = Replay({"FOO": _trend_df(_bull())})
    r = benchmark_dual_trend_short(replay, ["FOO"], 0, 99, cash=10_000.0,
                                   fast=FAST, slow=SLOW, slope_lookback=LOOKBACK,
                                   fee_bps=10.0, slippage_bps=5.0)
    assert r["symbol_bars_short"] == 0
    assert r["trades"] == 0
    assert r["total_return"] == pytest.approx(0.0, abs=1e-9)


def test_shorts_and_profits_in_a_sustained_decline():
    replay = Replay({"FOO": _trend_df(_bear())})
    r = benchmark_dual_trend_short(replay, ["FOO"], 0, 99, cash=10_000.0,
                                   fast=FAST, slow=SLOW, slope_lookback=LOOKBACK,
                                   fee_bps=10.0, slippage_bps=5.0)
    assert r["symbol_bars_short"] > 0
    assert r["trades"] >= 1
    assert r["total_return"] > 0


def test_slope_filter_blocks_a_dip_inside_a_still_rising_slow_sma():
    # A brief, sharp dip stitched into an otherwise-rising path: the fast
    # (3-bar) /slow (30-bar) ratio clears short_enter at the dip (plain
    # trend-break would open a short here, reacting quickly via the short
    # fast window), but the slow SMA's own value over the 20-bar lookback
    # stays higher than it was throughout -- dominated by the ~27 unaffected
    # bars in its 30-bar window, the medium-term trend never actually turned
    # down. Dual-trend should refuse to open; plain trend-break (no slope
    # filter, same fast/slow pair) should open at least once. Numerically
    # verified: trend first exceeds short_exit again (and the signal would
    # have covered) before slow_slope ever turns non-positive, so dual never
    # opens at all in this construction, not just "less often".
    up = [100.0 * (1.015 ** i) for i in range(80)]
    dip = [up[-1] * (0.85 ** i) for i in range(1, 4)]
    recover = [dip[-1] * (1.015 ** i) for i in range(1, 60)]
    prices = up + dip + recover
    replay = Replay({"FOO": _trend_df(prices)})
    n = len(prices)
    dual = benchmark_dual_trend_short(
        replay, ["FOO"], 0, n - 1, cash=10_000.0,
        fast=SLOPE_FAST, slow=SLOPE_SLOW, slope_lookback=SLOPE_LOOKBACK,
        fee_bps=10.0, slippage_bps=5.0)
    plain = benchmark_trend_break_short(
        replay, ["FOO"], 0, n - 1, cash=10_000.0,
        fast=SLOPE_FAST, slow=SLOPE_SLOW,
        fee_bps=10.0, slippage_bps=5.0)
    assert plain["symbol_bars_short"] > 0
    assert dual["symbol_bars_short"] == 0
    assert dual["trades"] == 0


def test_costs_and_borrow_only_ever_reduce_the_return():
    replay = Replay({"FOO": _trend_df(_bear())})
    zero_cost = benchmark_dual_trend_short(replay, ["FOO"], 0, 99, cash=10_000.0,
                                           fast=FAST, slow=SLOW, slope_lookback=LOOKBACK,
                                           fee_bps=0.0, slippage_bps=0.0,
                                           borrow_bps_per_bar=0.0)
    with_fees = benchmark_dual_trend_short(replay, ["FOO"], 0, 99, cash=10_000.0,
                                           fast=FAST, slow=SLOW, slope_lookback=LOOKBACK,
                                           fee_bps=10.0, slippage_bps=5.0,
                                           borrow_bps_per_bar=0.0)
    with_borrow = benchmark_dual_trend_short(replay, ["FOO"], 0, 99, cash=10_000.0,
                                             fast=FAST, slow=SLOW, slope_lookback=LOOKBACK,
                                             fee_bps=10.0, slippage_bps=5.0,
                                             borrow_bps_per_bar=5.0)
    assert with_fees["total_return"] < zero_cost["total_return"]
    assert with_borrow["total_return"] < with_fees["total_return"]


def test_per_symbol_independence_mixed_basket():
    replay = Replay({"UP": _trend_df(_bull()), "DOWN": _trend_df(_bear())})
    r = benchmark_dual_trend_short(replay, ["UP", "DOWN"], 0, 99, cash=10_000.0,
                                   fast=FAST, slow=SLOW, slope_lookback=LOOKBACK,
                                   fee_bps=10.0, slippage_bps=5.0)
    assert r["trades"] >= 1
    assert r["flips"] <= 2


def test_empty_when_no_usable_symbols():
    replay = Replay({"FOO": _trend_df(_bear())})
    assert benchmark_dual_trend_short(replay, ["NOPE"], 0, 99, cash=10_000.0) == {}


def test_too_short_window_returns_empty():
    replay = Replay({"FOO": _trend_df(_bear())})
    assert benchmark_dual_trend_short(replay, ["FOO"], 0, 2, cash=10_000.0) == {}


def test_single_symbol_bars_short_never_exceeds_bars_total():
    replay = Replay({"FOO": _trend_df(_bear())})
    r = benchmark_dual_trend_short(replay, ["FOO"], 0, 99, cash=10_000.0,
                                   fast=FAST, slow=SLOW, slope_lookback=LOOKBACK,
                                   fee_bps=10.0, slippage_bps=5.0)
    assert 0 <= r["symbol_bars_short"] <= r["bars_total"]
    assert r["avg_concurrent_short"] == pytest.approx(
        r["symbol_bars_short"] / r["bars_total"])


def test_multi_symbol_bars_short_can_exceed_bars_total():
    replay = Replay({"A": _trend_df(_bear()), "B": _trend_df(_bear()),
                     "C": _trend_df(_bear())})
    r = benchmark_dual_trend_short(replay, ["A", "B", "C"], 0, 99, cash=10_000.0,
                                   fast=FAST, slow=SLOW, slope_lookback=LOOKBACK,
                                   fee_bps=10.0, slippage_bps=5.0)
    assert r["symbol_bars_short"] > r["bars_total"]
    assert r["avg_concurrent_short"] > 1.0
