"""loop.engine.pairwise_correlation_stats -- full-universe pairwise return
correlation, summarised. Exists to gather evidence for the open decision in
AGENTS.md item 3 (drop the fixed-value correlation_penalty gene, or build a
fuller cross-universe factor-model version): the live mechanism
(agents.judges.RiskJudge._correlation_scale) only ever compares a buy
candidate against symbols already *held*, never the rest of the universe.
Read-only: takes already-built return arrays, never a genome or replay."""
import numpy as np

from loop.engine import pairwise_correlation_stats


def test_fewer_than_three_symbols_errors():
    rets = {"A": np.random.default_rng(0).normal(size=40),
            "B": np.random.default_rng(1).normal(size=40)}
    res = pairwise_correlation_stats(rets)
    assert "error" in res
    assert res["n_symbols"] == 2


def test_identical_series_are_perfectly_correlated():
    base = np.random.default_rng(0).normal(size=40)
    rets = {"A": base, "B": base.copy(), "C": base.copy()}
    res = pairwise_correlation_stats(rets)
    assert res["n_pairs"] == 3
    assert res["mean_corr"] > 0.999
    assert res["min_corr"] > 0.999
    assert res["frac_above_threshold"] == 1.0


def test_negated_series_are_perfectly_anti_correlated():
    base = np.random.default_rng(0).normal(size=40)
    rets = {"A": base, "B": -base, "C": base.copy()}
    res = pairwise_correlation_stats(rets)
    # A-B and B-C are -1, A-C is +1
    assert res["min_corr"] < -0.999
    assert res["max_corr"] > 0.999
    assert res["frac_above_threshold"] < 1.0


def test_independent_noise_is_near_zero_on_average():
    rng = np.random.default_rng(42)
    rets = {s: rng.normal(size=500) for s in ("A", "B", "C", "D", "E")}
    res = pairwise_correlation_stats(rets)
    assert res["n_pairs"] == 10
    assert abs(res["mean_corr"]) < 0.15


def test_zero_variance_symbol_is_dropped_not_raised():
    base = np.random.default_rng(0).normal(size=40)
    rets = {"A": base, "B": base.copy(), "FLAT": np.zeros(40)}
    res = pairwise_correlation_stats(rets)
    # only the A-B pair is valid; FLAT contributes no pairs
    assert res["n_pairs"] == 1
    assert res["n_symbols"] == 3


def test_too_short_series_dropped_not_raised():
    base = np.random.default_rng(0).normal(size=40)
    rets = {"A": base, "B": base.copy(), "SHORT": np.array([0.01, 0.02])}
    res = pairwise_correlation_stats(rets)
    assert res["n_pairs"] == 1


def test_nan_series_dropped_not_raised():
    base = np.random.default_rng(0).normal(size=40)
    with_nan = base.copy()
    with_nan[5] = float("nan")
    rets = {"A": base, "B": base.copy(), "NANY": with_nan}
    res = pairwise_correlation_stats(rets)
    assert res["n_pairs"] == 1


def test_threshold_changes_frac_above_but_not_correlations():
    base = np.random.default_rng(0).normal(size=40)
    rets = {"A": base, "B": -base, "C": base.copy()}
    loose = pairwise_correlation_stats(rets, threshold=-1.0)
    strict = pairwise_correlation_stats(rets, threshold=0.99)
    assert loose["frac_above_threshold"] == 1.0
    assert strict["frac_above_threshold"] < 1.0
    assert loose["mean_corr"] == strict["mean_corr"]


def test_all_degenerate_symbols_errors():
    rets = {"A": np.zeros(40), "B": np.zeros(40), "C": np.zeros(40)}
    res = pairwise_correlation_stats(rets)
    assert "error" in res
    assert res["n_pairs"] == 0
