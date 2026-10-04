"""`loop.engine.benchmark_asymmetric_short` -- the variant
`benchmark_combined_short`'s own 2026-10-03 writeup flagged as the next
thing to try: gate OPENING a short on both signals agreeing (same entry
rule as `benchmark_combined_short`), but let the per-symbol trend-break
signal ALONE govern COVERING, instead of covering the moment either signal
disagrees. `benchmark_combined_short` was found to inherit the regime
classifier's documented exit-side whipsaw (an ordinary pullback-recovery
reads "bear" then flips back out), forcing premature covers out of
positions the trend-break signal alone would have held through a real
decline. Tests use synthetic price paths where each signal's own state is
unambiguous by construction, so the asymmetric cover logic can be checked
directly against `benchmark_combined_short`'s own AND/OR behavior.
"""
import copy

import numpy as np
import pandas as pd
import pytest

from core.genome import SEED_GENOME, Genome
from core.market import Replay
from loop.engine import benchmark_asymmetric_short, benchmark_combined_short


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
    return [100.0 * (0.97 ** i) for i in range(n)]


def _mild_bear(n: int = 150) -> list[float]:
    return [100.0 * (0.995 ** i) for i in range(n)]


def _bear_then_recover_past_high(n: int = 150) -> list[float]:
    # 50 bars of the same steep decline as `_steep_bear`, then a strong
    # recovery that overshoots back past the starting level and flattens
    # out -- designed so Analyst._regime (on this series as its own
    # anchor) reads "bear" during the decline and genuinely leaves
    # bear/crisis (not just dips briefly) once the recovery is underway
    # and settles, rather than a price-only trend ever actually recovering.
    out = []
    p = 100.0
    for _ in range(50):
        p *= 0.97
        out.append(p)
    for _ in range(40):
        p *= 1.05
        out.append(p)
    while len(out) < n:
        p *= 1.0005
        out.append(p)
    return out


FAST, SLOW = 5, 10


def test_never_shorts_a_sustained_bull_run():
    genome = _make_genome(["FOO"], "FOO")
    replay = Replay({"FOO": _trend_df(_bull())})
    r = benchmark_asymmetric_short(replay, genome, ["FOO"], 40, 149, cash=10_000.0,
                                   fast=FAST, slow=SLOW)
    assert r["symbol_bars_short"] == 0
    assert r["trades"] == 0
    assert r["total_return"] == pytest.approx(0.0, abs=1e-12)


def test_shorts_when_both_signals_agree():
    genome = _make_genome(["FOO"], "FOO")
    replay = Replay({"FOO": _trend_df(_steep_bear())})
    r = benchmark_asymmetric_short(replay, genome, ["FOO"], 40, 149, cash=10_000.0,
                                   fast=FAST, slow=SLOW,
                                   fee_bps=10.0, slippage_bps=5.0)
    assert r["symbol_bars_short"] > 0
    assert r["trades"] >= 1
    assert r["total_return"] > 0


def test_blocked_when_trend_breaks_but_regime_disagrees():
    # Same entry gate as benchmark_combined_short -- both signals still
    # need to agree to open. ANCHOR stays in a sustained bull run so the
    # regime never reads bear/crisis even though FOO's own price-only
    # trend clears the break threshold on its own.
    genome = _make_genome(["FOO", "ANCHOR"], "ANCHOR")
    replay = Replay({"FOO": _trend_df(_steep_bear()),
                     "ANCHOR": _trend_df(_bull())})
    r = benchmark_asymmetric_short(replay, genome, ["FOO", "ANCHOR"], 40, 149,
                                   cash=10_000.0, fast=FAST, slow=SLOW)
    assert r["symbol_bars_short"] == 0
    assert r["trades"] == 0


def test_blocked_when_regime_bear_but_trend_not_broken():
    genome = _make_genome(["FOO"], "FOO")
    replay = Replay({"FOO": _trend_df(_mild_bear())})
    r = benchmark_asymmetric_short(replay, genome, ["FOO"], 40, 149, cash=10_000.0,
                                   fast=FAST, slow=SLOW, short_enter=-0.05)
    assert r["symbol_bars_short"] == 0
    assert r["trades"] == 0


def test_holds_through_a_regime_flip_combined_would_have_covered_on():
    # The actual point of this function: FOO declines steeply and NEVER
    # recovers for the whole window (its own SMA(5)/SMA(10)-1 trend stays
    # below short_exit=-0.02 throughout, by construction), while ANCHOR
    # (the regime's own anchor symbol) crashes then recovers hard enough
    # that Analyst._regime genuinely leaves bear/crisis partway through.
    # benchmark_combined_short covers the instant the regime leaves
    # bear/crisis even though FOO's own trend never recovered;
    # benchmark_asymmetric_short should stay short through that flip and
    # only ever cover on FOO's own trend (never, in this construction, so
    # it rides the position all the way to the window's forced close).
    genome = _make_genome(["FOO", "ANCHOR"], "ANCHOR")
    replay = Replay({"FOO": _trend_df(_steep_bear()),
                     "ANCHOR": _trend_df(_bear_then_recover_past_high())})
    combined = benchmark_combined_short(
        replay, genome, ["FOO", "ANCHOR"], 40, 149, cash=10_000.0,
        fast=FAST, slow=SLOW, fee_bps=10.0, slippage_bps=5.0)
    asym = benchmark_asymmetric_short(
        replay, genome, ["FOO", "ANCHOR"], 40, 149, cash=10_000.0,
        fast=FAST, slow=SLOW, fee_bps=10.0, slippage_bps=5.0)
    assert combined and asym
    # Asymmetric rides the still-broken trend through the regime flip, so
    # it accumulates far more bars held short and a materially larger
    # realized return on a FOO price path that keeps declining throughout.
    assert asym["symbol_bars_short"] > combined["symbol_bars_short"]
    assert asym["total_return"] > combined["total_return"]
    # Both still open the position in the first place -- this isn't a
    # "never covers" bug, just a different (trend-only) cover rule: the
    # asymmetric run flips at most once more than the combined run's own
    # extra regime-driven re-entry/cover pair, never dramatically more.
    assert asym["flips"] <= combined["flips"] + 1


def test_costs_and_borrow_only_ever_reduce_the_return():
    genome = _make_genome(["FOO"], "FOO")
    replay = Replay({"FOO": _trend_df(_steep_bear())})
    zero_cost = benchmark_asymmetric_short(
        replay, genome, ["FOO"], 40, 149, cash=10_000.0, fast=FAST, slow=SLOW,
        fee_bps=0.0, slippage_bps=0.0, borrow_bps_per_bar=0.0)
    with_fees = benchmark_asymmetric_short(
        replay, genome, ["FOO"], 40, 149, cash=10_000.0, fast=FAST, slow=SLOW,
        fee_bps=10.0, slippage_bps=5.0, borrow_bps_per_bar=0.0)
    with_borrow = benchmark_asymmetric_short(
        replay, genome, ["FOO"], 40, 149, cash=10_000.0, fast=FAST, slow=SLOW,
        fee_bps=10.0, slippage_bps=5.0, borrow_bps_per_bar=5.0)
    assert with_fees["total_return"] < zero_cost["total_return"]
    assert with_borrow["total_return"] < with_fees["total_return"]


def test_empty_when_no_usable_symbols():
    genome = _make_genome(["FOO"], "FOO")
    replay = Replay({"FOO": _trend_df(_steep_bear())})
    assert benchmark_asymmetric_short(replay, genome, ["NOPE"], 40, 149,
                                      cash=10_000.0) == {}


def test_too_short_window_returns_empty():
    genome = _make_genome(["FOO"], "FOO")
    replay = Replay({"FOO": _trend_df(_steep_bear())})
    assert benchmark_asymmetric_short(replay, genome, ["FOO"], 40, 42,
                                      cash=10_000.0) == {}
