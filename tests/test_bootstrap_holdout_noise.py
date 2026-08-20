"""loop.engine.{block_bootstrap_resample, stats_from_returns,
bootstrap_fitness_distribution} -- answers constitution.holdout_accepts()'s
own open question ("Measure the sigma before trusting the number") by
block-bootstrapping a real backtest's observed return path to see how much a
single sealed-holdout fitness score could plausibly move from return-order
noise alone. Read-only: takes an already-computed nav_history, never runs a
genome, broker, or replay."""
import numpy as np
import pytest

from constitution import MULTIPLE_TESTING_SIGMA
from core.portfolio import PaperBroker
from loop.engine import (block_bootstrap_resample, bootstrap_fitness_distribution,
                         stats_from_returns)


def _nav_from_returns(rets, start=10_000.0):
    nav = start * np.cumprod(1.0 + np.concatenate([[0.0], rets]))
    return [(str(i), float(v)) for i, v in enumerate(nav)]


# -- block_bootstrap_resample ------------------------------------------------

def test_resample_length_matches_request():
    rng = np.random.default_rng(0)
    rets = np.linspace(-0.01, 0.01, 37)
    out = block_bootstrap_resample(rets, 100, block_size=7, rng=rng)
    assert len(out) == 100


def test_resample_values_are_a_subset_of_the_original():
    rng = np.random.default_rng(0)
    rets = np.array([0.001, -0.002, 0.003, -0.004, 0.005])
    out = block_bootstrap_resample(rets, 50, block_size=2, rng=rng)
    assert set(np.round(out, 12)).issubset(set(np.round(rets, 12)))


def test_resample_deterministic_given_same_seed():
    rets = np.linspace(-0.02, 0.02, 41)
    out_a = block_bootstrap_resample(rets, 41, 5, np.random.default_rng(7))
    out_b = block_bootstrap_resample(rets, 41, 5, np.random.default_rng(7))
    assert np.array_equal(out_a, out_b)


def test_resample_different_seeds_usually_differ():
    rets = np.linspace(-0.02, 0.02, 41)
    out_a = block_bootstrap_resample(rets, 41, 5, np.random.default_rng(1))
    out_b = block_bootstrap_resample(rets, 41, 5, np.random.default_rng(2))
    assert not np.array_equal(out_a, out_b)


def test_resample_empty_input_returns_empty():
    rng = np.random.default_rng(0)
    out = block_bootstrap_resample(np.array([]), 10, block_size=3, rng=rng)
    assert len(out) == 0


def test_resample_block_size_larger_than_series_is_clamped_not_fatal():
    rng = np.random.default_rng(0)
    rets = np.array([0.01, -0.01, 0.02])
    out = block_bootstrap_resample(rets, 20, block_size=999, rng=rng)
    assert len(out) == 20
    assert set(np.round(out, 12)).issubset(set(np.round(rets, 12)))


def test_resample_constant_series_is_reproduced_exactly():
    rng = np.random.default_rng(0)
    rets = np.full(30, 0.0015)
    out = block_bootstrap_resample(rets, 30, block_size=6, rng=rng)
    assert np.allclose(out, 0.0015)


# -- stats_from_returns -------------------------------------------------------

def test_stats_from_returns_matches_paperbroker_stats_on_the_same_path():
    rng = np.random.default_rng(3)
    rets = rng.normal(0.0008, 0.02, size=150)
    nav_history = _nav_from_returns(rets)
    broker = PaperBroker(cash=10_000.0)
    broker.nav_history = nav_history
    broker_stats = broker.stats(bars_per_year=365.25)

    mine = stats_from_returns(rets, trades=broker_stats["trades"],
                              turnover_annual=0.0, bars_per_year=365.25)
    for key in ("total_return", "cagr", "vol", "sharpe", "sortino", "max_dd", "bars"):
        assert mine[key] == pytest.approx(broker_stats[key], rel=1e-9, abs=1e-12)


def test_stats_from_returns_too_short_reports_error():
    out = stats_from_returns(np.array([]), trades=0, turnover_annual=0.0,
                             bars_per_year=365.25)
    assert "error" in out


def test_stats_from_returns_passes_through_trades_and_turnover_unchanged():
    rets = np.linspace(-0.01, 0.01, 100)
    out = stats_from_returns(rets, trades=57, turnover_annual=12.5, bars_per_year=365.25)
    assert out["trades"] == 57
    assert out["turnover_annual"] == 12.5


# -- bootstrap_fitness_distribution -------------------------------------------

def _realistic_returns(rng, n=250):
    # Enough bars/trades to clear MIN_BARS/MIN_TRADES so fitness isn't just -inf.
    return rng.normal(0.0012, 0.018, size=n)


def test_bootstrap_reports_expected_fields():
    rng = np.random.default_rng(5)
    nav_history = _nav_from_returns(_realistic_returns(rng))
    out = bootstrap_fitness_distribution(nav_history, trades=40, turnover_annual=15.0,
                                         bars_per_year=365.25, n_boot=100,
                                         block_size=10, seed=0)
    expected_keys = {"n_boot", "block_size", "bars", "real_fitness", "real_sortino",
                     "real_max_dd", "real_total_return", "boot_fitness_mean",
                     "boot_fitness_std", "boot_fitness_p05", "boot_fitness_p95",
                     "frac_hard_fail", "sortino_std", "total_return_std",
                     "max_dd_p05", "max_dd_p95"}
    assert expected_keys.issubset(out.keys())
    assert out["n_boot"] == 100
    assert out["boot_fitness_std"] >= 0.0


def test_bootstrap_deterministic_given_same_seed():
    rng = np.random.default_rng(9)
    nav_history = _nav_from_returns(_realistic_returns(rng))
    out_a = bootstrap_fitness_distribution(nav_history, 40, 15.0, 365.25,
                                           n_boot=50, block_size=10, seed=3)
    out_b = bootstrap_fitness_distribution(nav_history, 40, 15.0, 365.25,
                                           n_boot=50, block_size=10, seed=3)
    assert out_a == out_b


def test_bootstrap_constant_returns_have_zero_sigma():
    # Every block-resample of a constant series reproduces the exact same
    # path regardless of which blocks get picked -- the empirical sigma
    # should be (numerically) zero, a clean sanity check on the mechanism
    # itself before trusting it on real noisy data.
    nav_history = _nav_from_returns(np.full(200, 0.0015))
    out = bootstrap_fitness_distribution(nav_history, trades=40, turnover_annual=10.0,
                                         bars_per_year=365.25, n_boot=50,
                                         block_size=15, seed=0)
    assert out["boot_fitness_std"] == pytest.approx(0.0, abs=1e-9)
    assert out["sortino_std"] == pytest.approx(0.0, abs=1e-9)
    assert out["frac_hard_fail"] == 0.0


def test_bootstrap_insufficient_nav_history_reports_error():
    out = bootstrap_fitness_distribution([("d0", 100.0), ("d1", 101.0)], trades=0,
                                         turnover_annual=0.0, bars_per_year=365.25)
    assert "error" in out


def test_bootstrap_real_fitness_matches_direct_stats_from_returns_call():
    rng = np.random.default_rng(11)
    rets = _realistic_returns(rng)
    nav_history = _nav_from_returns(rets)
    out = bootstrap_fitness_distribution(nav_history, trades=45, turnover_annual=20.0,
                                         bars_per_year=365.25, n_boot=10, seed=0)
    from constitution import fitness
    direct = fitness(stats_from_returns(rets, 45, 20.0, 365.25))
    assert out["real_fitness"] == pytest.approx(direct, rel=1e-9)


def test_bootstrap_std_is_a_meaningful_fraction_of_multiple_testing_sigma():
    # Not a tight assertion on the exact number (it depends on the realized
    # path), just a guard against a wiring bug that would silently produce
    # std == 0 or NaN on genuinely noisy, non-degenerate input.
    rng = np.random.default_rng(21)
    nav_history = _nav_from_returns(_realistic_returns(rng, n=400))
    out = bootstrap_fitness_distribution(nav_history, trades=60, turnover_annual=25.0,
                                         bars_per_year=365.25, n_boot=300,
                                         block_size=15, seed=0)
    assert np.isfinite(out["boot_fitness_std"])
    assert out["boot_fitness_std"] > 0.0
    assert out["sortino_std"] > 0.0
    # Sanity: the empirical sigma should be within a couple orders of
    # magnitude of MULTIPLE_TESTING_SIGMA, not some wildly different unit.
    assert 0.001 < out["boot_fitness_std"] < MULTIPLE_TESTING_SIGMA * 50
