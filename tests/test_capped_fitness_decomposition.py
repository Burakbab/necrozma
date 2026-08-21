"""loop.evolve.capped_fitness_decomposition -- winsorizes the mean term of
aggregate_fitness against a single dominant fold, leaving the
FOLD_CONSISTENCY_WEIGHT * std consistency-penalty term untouched, backing the
`fold-cap` diagnostic. fitness-decomp (2026-08-20) traced aggregate_fitness's
across-scheme swing to the mean term, not the penalty term; regime-folds'
n_folds sweep (2026-08-21) showed isolating the outlier fold is double-edged.
This measures the untried remaining option: capping the outlier's pull on the
mean directly (AGENTS.md item 2, Current state 2026-08-21)."""
import numpy as np
import pytest

from constitution import FOLD_CONSISTENCY_WEIGHT
from loop.evolve import capped_fitness_decomposition, fitness_decomposition


def test_penalty_term_matches_fitness_decomposition_exactly():
    # The penalty term is deliberately untouched by capping -- it must equal
    # the plain fitness_decomposition's penalty term on the same input.
    for fits in ([1.0, 2.0, 3.0], [0.5, -0.5], [1.4082, -0.5, 2.003, 0.9],
                 [10.0, 0.1, 0.2]):
        plain = fitness_decomposition(fits)
        capped = capped_fitness_decomposition(fits)
        assert capped["penalty_term"] == pytest.approx(plain["penalty_term"], abs=1e-12)
        assert capped["mean_term"] == pytest.approx(plain["mean_term"], abs=1e-12)
        assert capped["aggregate_fitness"] == pytest.approx(
            plain["aggregate_fitness"], abs=1e-12)


def test_dominant_outlier_fold_gets_capped():
    # One fold far above the rest: the ceiling is mean + cap_z*std, so that
    # fold's contribution to capped_mean_term must be strictly less than its
    # raw value, and capped_mean_term must be strictly less than mean_term.
    fits = [0.1, 0.2, 5.0]
    d = capped_fitness_decomposition(fits, cap_z=1.0)
    assert d["n_capped"] == 1
    assert d["capped_mean_term"] < d["mean_term"]
    assert d["capped_aggregate_fitness"] < d["aggregate_fitness"]
    ceiling = d["mean_term"] + 1.0 * d["std"]
    expected_capped_mean = float(np.mean([0.1, 0.2, min(5.0, ceiling)]))
    assert d["capped_mean_term"] == pytest.approx(expected_capped_mean)


def test_no_outlier_nothing_capped():
    # Loose enough a ceiling (cap_z=2.5) that no fold in a small, tightly
    # clustered set exceeds it -- capping should be a no-op.
    fits = [0.98, 1.0, 1.02]
    d = capped_fitness_decomposition(fits, cap_z=2.5)
    assert d["n_capped"] == 0
    assert d["capped_mean_term"] == pytest.approx(d["mean_term"], abs=1e-12)
    assert d["capped_aggregate_fitness"] == pytest.approx(d["aggregate_fitness"], abs=1e-12)


def test_zero_spread_is_a_no_op():
    d = capped_fitness_decomposition([1.5, 1.5, 1.5, 1.5], cap_z=0.5)
    assert d["std"] == pytest.approx(0.0)
    assert d["n_capped"] == 0
    assert d["capped_mean_term"] == pytest.approx(1.5)
    assert d["capped_aggregate_fitness"] == pytest.approx(1.5)


def test_single_fold_is_a_no_op():
    d = capped_fitness_decomposition([0.7])
    assert d["n_folds"] == 1
    assert d["n_capped"] == 0
    assert d["capped_mean_term"] == pytest.approx(0.7)
    assert d["capped_aggregate_fitness"] == pytest.approx(0.7)


def test_empty_matches_fitness_decomposition_empty_branch():
    plain = fitness_decomposition([])
    capped = capped_fitness_decomposition([])
    assert capped["aggregate_fitness"] == plain["aggregate_fitness"] == float("-inf")
    assert capped["capped_aggregate_fitness"] == float("-inf")
    assert capped["mean_term"] == capped["capped_mean_term"] == 0.0
    assert capped["n_folds"] == 0
    assert capped["n_capped"] == 0


def test_smaller_cap_z_never_caps_less():
    # A tighter ceiling (smaller cap_z) can only catch the same or more
    # folds as a looser one, never fewer -- monotonic in cap_z.
    fits = [0.1, 0.3, 0.5, 4.0]
    tight = capped_fitness_decomposition(fits, cap_z=0.25)
    loose = capped_fitness_decomposition(fits, cap_z=2.0)
    assert tight["n_capped"] >= loose["n_capped"]
    assert tight["capped_mean_term"] <= loose["capped_mean_term"]


def test_never_caps_from_below():
    # A single deep-loss fold should be left untouched by a ceiling-only cap.
    fits = [-5.0, 0.1, 0.2]
    d = capped_fitness_decomposition(fits, cap_z=1.0)
    assert d["n_capped"] == 0
    assert d["capped_mean_term"] == pytest.approx(d["mean_term"], abs=1e-12)


def test_returns_cap_z_used():
    d = capped_fitness_decomposition([1.0, 2.0, 3.0], cap_z=1.5)
    assert d["cap_z"] == pytest.approx(1.5)
