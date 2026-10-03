"""`loop.engine.benchmark_combined_short` -- combines the two short-timing
signals measured separately in AGENTS.md item 5: `benchmark_trend_break_short`'s
per-symbol price-only trend breakdown and `benchmark_regime_conditional_short`'s
basket-wide `Analyst._regime` reading. A symbol may only open a short when
BOTH signals agree this bar, and covers the first bar EITHER disagrees.
Tests use synthetic price paths where each signal's own state is unambiguous
by construction, so the AND-gating logic can be checked directly.
"""
import copy

import numpy as np
import pandas as pd
import pytest

from core.genome import SEED_GENOME, Genome
from core.market import Replay
from loop.engine import benchmark_combined_short


def _make_genome(symbols: list[str], anchor: str) -> Genome:
    data = copy.deepcopy(SEED_GENOME)
    data["universe"] = list(symbols)
    data["agents"]["analyst"]["genes"] = {
        "trend_fast": 5, "trend_slow": 10, "rsi_len": 5,
        "vol_short": 5, "vol_long": 10, "breakout_len": 10, "z_len": 10,
        "regime_ma": 10, "regime_anchor": anchor, "volume_len": 10,
    }
    return Genome(data)


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


def _bull(n: int = 150) -> list[float]:
    return [100.0 * (1.01 ** i) for i in range(n)]


def _steep_bear(n: int = 150) -> list[float]:
    # Steep enough that a price-only SMA(5)/SMA(10)-1 trend reading clears
    # the combined function's default short_enter=-0.05 (checked
    # numerically when this signal was first built -- a mild decline's
    # ratio converges to a shallower constant that never crosses -0.05).
    return [100.0 * (0.97 ** i) for i in range(n)]


def _mild_bear(n: int = 150) -> list[float]:
    # Bearish enough to read as "bear" in Analyst._regime (anchor_score < 0
    # or breadth < 0.30 -- an easily-tripped OR), but shallow enough that
    # SMA(5)/SMA(10)-1 never crosses the stricter -5% trend-break threshold.
    return [100.0 * (0.995 ** i) for i in range(n)]


FAST, SLOW = 5, 10


def test_never_shorts_a_sustained_bull_run():
    genome = _make_genome(["FOO"], "FOO")
    replay = Replay({"FOO": _trend_df(_bull())})
    r = benchmark_combined_short(replay, genome, ["FOO"], 40, 149, cash=10_000.0,
                                 fast=FAST, slow=SLOW)
    assert r["symbol_bars_short"] == 0
    assert r["trades"] == 0
    assert r["total_return"] == pytest.approx(0.0, abs=1e-12)


def test_shorts_when_both_signals_agree():
    genome = _make_genome(["FOO"], "FOO")
    replay = Replay({"FOO": _trend_df(_steep_bear())})
    r = benchmark_combined_short(replay, genome, ["FOO"], 40, 149, cash=10_000.0,
                                 fast=FAST, slow=SLOW,
                                 fee_bps=10.0, slippage_bps=5.0)
    assert r["symbol_bars_short"] > 0
    assert r["trades"] >= 1
    assert r["total_return"] > 0


def test_blocked_when_trend_breaks_but_regime_disagrees():
    # ANCHOR stays in a sustained bull run (regime reads "bull", never
    # bear/crisis) while FOO's own price independently breaks down hard
    # enough to clear the price-only trend threshold on its own. The
    # combined signal requires both, so FOO should never be shorted even
    # though the trend-break half of the gate is satisfied.
    genome = _make_genome(["FOO", "ANCHOR"], "ANCHOR")
    replay = Replay({"FOO": _trend_df(_steep_bear()),
                     "ANCHOR": _trend_df(_bull())})
    r = benchmark_combined_short(replay, genome, ["FOO", "ANCHOR"], 40, 149,
                                 cash=10_000.0, fast=FAST, slow=SLOW)
    assert r["symbol_bars_short"] == 0
    assert r["trades"] == 0


def test_blocked_when_regime_bear_but_trend_not_broken():
    # FOO declines just enough to tip Analyst._regime to "bear" (its own
    # anchor) but not enough to clear the stricter -5% price-only
    # trend-break threshold -- the combined signal requires both, so it
    # should stay flat on the trend-break half of the gate.
    genome = _make_genome(["FOO"], "FOO")
    replay = Replay({"FOO": _trend_df(_mild_bear())})
    r = benchmark_combined_short(replay, genome, ["FOO"], 40, 149, cash=10_000.0,
                                 fast=FAST, slow=SLOW, short_enter=-0.05)
    assert r["symbol_bars_short"] == 0
    assert r["trades"] == 0


def test_costs_and_borrow_only_ever_reduce_the_return():
    genome = _make_genome(["FOO"], "FOO")
    replay = Replay({"FOO": _trend_df(_steep_bear())})
    zero_cost = benchmark_combined_short(
        replay, genome, ["FOO"], 40, 149, cash=10_000.0, fast=FAST, slow=SLOW,
        fee_bps=0.0, slippage_bps=0.0, borrow_bps_per_bar=0.0)
    with_fees = benchmark_combined_short(
        replay, genome, ["FOO"], 40, 149, cash=10_000.0, fast=FAST, slow=SLOW,
        fee_bps=10.0, slippage_bps=5.0, borrow_bps_per_bar=0.0)
    with_borrow = benchmark_combined_short(
        replay, genome, ["FOO"], 40, 149, cash=10_000.0, fast=FAST, slow=SLOW,
        fee_bps=10.0, slippage_bps=5.0, borrow_bps_per_bar=5.0)
    assert with_fees["total_return"] < zero_cost["total_return"]
    assert with_borrow["total_return"] < with_fees["total_return"]


def test_empty_when_no_usable_symbols():
    genome = _make_genome(["FOO"], "FOO")
    replay = Replay({"FOO": _trend_df(_steep_bear())})
    assert benchmark_combined_short(replay, genome, ["NOPE"], 40, 149,
                                    cash=10_000.0) == {}


def test_too_short_window_returns_empty():
    genome = _make_genome(["FOO"], "FOO")
    replay = Replay({"FOO": _trend_df(_steep_bear())})
    assert benchmark_combined_short(replay, genome, ["FOO"], 40, 42,
                                    cash=10_000.0) == {}
