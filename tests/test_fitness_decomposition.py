"""loop.evolve.fitness_decomposition -- splits Evaluator's aggregate_fitness
into its mean term and its FOLD_CONSISTENCY_WEIGHT * std consistency-penalty
term, backing the `fitness-decomp` diagnostic. fold-scheme and rolling-folds
both showed the fold windowing swings aggregate_fitness; this makes the split
between the two terms measurable so the swing's driver can be identified rather
than asserted (AGENTS.md item 2, rolling-folds 2026-08-20)."""
import numpy as np
import pytest

from constitution import FOLD_CONSISTENCY_WEIGHT
from loop.evolve import Evaluator, fitness_decomposition


def test_reconstructs_evaluator_formula_exactly():
    # mean - FOLD_CONSISTENCY_WEIGHT*std is the identity Evaluator.evaluate uses.
    for fits in ([1.0, 2.0, 3.0], [0.5, -0.5], [1.4082, -0.5, 2.003, 0.9],
                 [-5.0, -5.0, -5.0]):
        d = fitness_decomposition(fits)
        expected = float(np.mean(fits) - FOLD_CONSISTENCY_WEIGHT * np.std(fits))
        assert d["aggregate_fitness"] == pytest.approx(expected, abs=1e-12)
        assert d["mean_term"] - d["penalty_term"] == pytest.approx(
            d["aggregate_fitness"], abs=1e-12)


def test_terms_have_expected_signs_and_values():
    d = fitness_decomposition([1.0, 2.0, 3.0])
    assert d["mean_term"] == pytest.approx(2.0)
    assert d["std"] == pytest.approx(float(np.std([1.0, 2.0, 3.0])))
    assert d["penalty_term"] == pytest.approx(FOLD_CONSISTENCY_WEIGHT * d["std"])
    assert d["penalty_term"] >= 0.0
    assert d["n_folds"] == 3


def test_zero_spread_has_zero_penalty():
    d = fitness_decomposition([1.5, 1.5, 1.5, 1.5])
    assert d["std"] == pytest.approx(0.0)
    assert d["penalty_term"] == pytest.approx(0.0)
    assert d["aggregate_fitness"] == pytest.approx(1.5)


def test_single_fold_has_no_penalty():
    d = fitness_decomposition([0.7])
    assert d["std"] == pytest.approx(0.0)
    assert d["penalty_term"] == pytest.approx(0.0)
    assert d["aggregate_fitness"] == pytest.approx(0.7)
    assert d["n_folds"] == 1


def test_empty_matches_evaluate_empty_branch():
    d = fitness_decomposition([])
    assert d["aggregate_fitness"] == float("-inf")
    assert d["mean_term"] == 0.0
    assert d["penalty_term"] == 0.0
    assert d["n_folds"] == 0


def test_penalty_grows_with_spread_at_fixed_mean():
    tight = fitness_decomposition([1.0, 1.0, 1.0])
    wide = fitness_decomposition([-1.0, 1.0, 3.0])  # same mean 1.0, larger std
    assert tight["mean_term"] == pytest.approx(wide["mean_term"])
    assert wide["penalty_term"] > tight["penalty_term"]
    assert wide["aggregate_fitness"] < tight["aggregate_fitness"]


def test_matches_evaluator_evaluate_on_synthetic_data(monkeypatch):
    # End-to-end: decomposing an evaluate() result's fold_fitness must equal
    # that same evaluate() call's own aggregate_fitness, on a real Evaluator.
    import loop.evolve as evolve

    fake_fits = iter([0.8, -0.2, 1.5])

    def fake_backtest(g, data, a, b, log_detail=False):
        f = next(fake_fits)
        return {"stats": {"sortino": f, "trades": 99, "bars": 999, "max_dd": 0.1,
                          "turnover_annual": 1.0},
                "fitness": f, "benchmark": {}, "edge": {}}

    monkeypatch.setattr(evolve, "run_backtest", fake_backtest)
    ev = Evaluator(data={"X": []}, n_folds=3)
    res = ev.evaluate(object())
    d = fitness_decomposition(res["fold_fitness"])
    assert d["aggregate_fitness"] == pytest.approx(res["aggregate_fitness"], abs=1e-12)
