"""loop.evolve.regime_stratified_groups -- greedy longest-processing-time
balance of sub-window indices into n_folds groups by |log(1+r)| weight,
backing the `regime-folds` diagnostic (AGENTS.md item 2). Genome-independent:
only the buy-and-hold return per sub-window feeds the grouping."""
import math

import pytest

from loop.evolve import regime_stratified_groups


def _weighted_returns(weights):
    """Inverse of the function's own |log(1+r)| weight, so a test can specify
    exact target weights instead of reasoning through log-return arithmetic."""
    return [math.expm1(w) for w in weights]


def test_rejects_non_positive_n_folds():
    with pytest.raises(ValueError):
        regime_stratified_groups([0.1, 0.2], n_folds=0)
    with pytest.raises(ValueError):
        regime_stratified_groups([0.1, 0.2], n_folds=-1)


def test_empty_returns_gives_n_folds_empty_groups():
    groups = regime_stratified_groups([], n_folds=3)
    assert groups == [[], [], []]


def test_more_folds_than_windows_leaves_extras_empty():
    groups = regime_stratified_groups([0.1, 0.2], n_folds=4)
    assert len(groups) == 4
    non_empty = [g for g in groups if g]
    assert len(non_empty) == 2
    covered = sorted(i for g in groups for i in g)
    assert covered == [0, 1]


def test_every_index_covered_exactly_once():
    returns = [0.5, -0.3, 0.1, 0.05, -0.6, 0.02, 0.4, -0.02]
    groups = regime_stratified_groups(returns, n_folds=3)
    covered = sorted(i for g in groups for i in g)
    assert covered == list(range(len(returns)))


def test_lpt_balances_a_known_case():
    # Classic LPT trace: weights 5,4,3,2,1,1 (here at indices 5,4,3,2,0,1)
    # split into 2 bins should balance to 8/8, not pile onto one bin.
    weights = [1, 1, 2, 3, 4, 5]
    returns = _weighted_returns(weights)
    groups = regime_stratified_groups(returns, n_folds=2)
    assert sorted(groups[0]) == [0, 2, 5]
    assert sorted(groups[1]) == [1, 3, 4]


def test_single_dominant_window_isolated_from_a_split_remainder():
    # One heavyweight window plus several lighter, distinguishable ones: LPT
    # should not let the heavyweight's fold pick up any of the others while a
    # fold with a strictly lower running total is available.
    weights = [10.0, 1.0, 0.9, 0.8, 0.7, 0.6]
    returns = _weighted_returns(weights)
    groups = regime_stratified_groups(returns, n_folds=3)
    owner = next(g for g in groups if 0 in g)
    assert owner == [0]


def test_deterministic_across_repeated_calls():
    returns = [0.3, -0.1, 0.2, 0.05, -0.4, 0.15]
    first = regime_stratified_groups(returns, n_folds=3)
    second = regime_stratified_groups(returns, n_folds=3)
    assert first == second


def test_single_fold_collects_every_window():
    returns = [0.3, -0.1, 0.2, 0.05]
    groups = regime_stratified_groups(returns, n_folds=1)
    assert len(groups) == 1
    assert sorted(groups[0]) == [0, 1, 2, 3]


def test_zero_return_windows_still_all_get_placed():
    groups = regime_stratified_groups([0.0, 0.0, 0.0, 0.0], n_folds=2)
    covered = sorted(i for g in groups for i in g)
    assert covered == [0, 1, 2, 3]
