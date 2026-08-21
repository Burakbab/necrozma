"""loop.evolve.Evaluator.evaluate_grouped -- scores a fold built from several
independently-backtested sub-windows (merged the same way Evaluator._merge
already combines folds for the acceptance gates), instead of one contiguous
slice per fold. Backs the `regime-folds` diagnostic: the first real test of
the regime-stratified fold idea that needs no run_backtest or constitution
change (AGENTS.md item 2, 2026-08-21)."""
import numpy as np
import pytest

from constitution import FOLD_CONSISTENCY_WEIGHT, ranking_fitness
from loop.evolve import Evaluator

STATS_BY_WINDOW = {
    (0.0, 0.2): {"trades": 40, "bars": 200, "sortino": 1.0, "sharpe": 1.0,
                 "max_dd": -0.10, "turnover_annual": 2.0, "win_rate": 0.5,
                 "total_return": 0.10, "halt_count": 0},
    (0.2, 0.4): {"trades": 50, "bars": 200, "sortino": 2.0, "sharpe": 1.2,
                 "max_dd": -0.20, "turnover_annual": 3.0, "win_rate": 0.6,
                 "total_return": 0.20, "halt_count": 1},
    (0.4, 0.6): {"trades": 60, "bars": 200, "sortino": -1.0, "sharpe": 0.5,
                 "max_dd": -0.50, "turnover_annual": 1.0, "win_rate": 0.4,
                 "total_return": -0.05, "halt_count": 2},
    (0.6, 0.8): {"trades": 70, "bars": 200, "sortino": 0.5, "sharpe": 0.7,
                 "max_dd": -0.30, "turnover_annual": 2.5, "win_rate": 0.45,
                 "total_return": 0.05, "halt_count": 0},
}
SUB_WINDOWS = [(0.0, 0.2), (0.2, 0.4), (0.4, 0.6), (0.6, 0.8)]


def _fake_backtest(g, data, a, b, log_detail=False):
    st = STATS_BY_WINDOW[(a, b)]
    return {"stats": st, "fitness": ranking_fitness(st), "benchmark": {}, "edge": {}}


def _fake_backtest_all_error(g, data, a, b, log_detail=False):
    return {"error": "slice too short (10 bars)"}


def test_matches_manual_merge_and_ranking_fitness(monkeypatch):
    import loop.evolve as evolve
    monkeypatch.setattr(evolve, "run_backtest", _fake_backtest)
    ev = Evaluator(data={}, n_folds=2)
    groups = [[0, 1], [2, 3]]

    res = ev.evaluate_grouped(object(), SUB_WINDOWS, groups)

    expected_fold0 = Evaluator._merge([{"stats": STATS_BY_WINDOW[(0.0, 0.2)]},
                                       {"stats": STATS_BY_WINDOW[(0.2, 0.4)]}])
    expected_fold1 = Evaluator._merge([{"stats": STATS_BY_WINDOW[(0.4, 0.6)]},
                                       {"stats": STATS_BY_WINDOW[(0.6, 0.8)]}])
    assert res["folds"][0]["stats"] == expected_fold0
    assert res["folds"][1]["stats"] == expected_fold1
    assert res["fold_fitness"][0] == pytest.approx(ranking_fitness(expected_fold0))
    assert res["fold_fitness"][1] == pytest.approx(ranking_fitness(expected_fold1))


def test_aggregate_uses_the_same_formula_as_evaluate(monkeypatch):
    import loop.evolve as evolve
    monkeypatch.setattr(evolve, "run_backtest", _fake_backtest)
    ev = Evaluator(data={}, n_folds=2)
    groups = [[0, 1], [2, 3]]

    res = ev.evaluate_grouped(object(), SUB_WINDOWS, groups)

    expected_agg = float(np.mean(res["fold_fitness"]) -
                         FOLD_CONSISTENCY_WEIGHT * np.std(res["fold_fitness"]))
    assert res["aggregate_fitness"] == pytest.approx(expected_agg, abs=1e-12)


def test_single_sub_window_folds_reduce_to_that_windows_own_fitness(monkeypatch):
    import loop.evolve as evolve
    monkeypatch.setattr(evolve, "run_backtest", _fake_backtest)
    ev = Evaluator(data={}, n_folds=4)
    groups = [[0], [1], [2], [3]]

    res = ev.evaluate_grouped(object(), SUB_WINDOWS, groups)

    for i, (a, b) in enumerate(SUB_WINDOWS):
        assert res["fold_fitness"][i] == pytest.approx(
            ranking_fitness(STATS_BY_WINDOW[(a, b)]))


def test_all_sub_windows_erroring_floors_that_fold(monkeypatch):
    import loop.evolve as evolve
    from constitution import RANK_FLOOR
    monkeypatch.setattr(evolve, "run_backtest", _fake_backtest_all_error)
    ev = Evaluator(data={}, n_folds=1)

    res = ev.evaluate_grouped(object(), SUB_WINDOWS, [[0, 1]])

    assert res["fold_fitness"] == [RANK_FLOOR]
    assert "error" in res["folds"][0]


def test_empty_group_floors_that_fold(monkeypatch):
    import loop.evolve as evolve
    from constitution import RANK_FLOOR
    monkeypatch.setattr(evolve, "run_backtest", _fake_backtest)
    ev = Evaluator(data={}, n_folds=2)

    res = ev.evaluate_grouped(object(), SUB_WINDOWS, [[0, 1], []])

    assert res["fold_fitness"][1] == RANK_FLOOR
    assert "error" in res["folds"][1]


def test_partial_errors_within_a_group_merge_only_the_valid_sub_windows(monkeypatch):
    import loop.evolve as evolve

    def one_window_errors(g, data, a, b, log_detail=False):
        if (a, b) == (0.2, 0.4):
            return {"error": "slice too short"}
        return _fake_backtest(g, data, a, b, log_detail)

    monkeypatch.setattr(evolve, "run_backtest", one_window_errors)
    ev = Evaluator(data={}, n_folds=1)

    res = ev.evaluate_grouped(object(), SUB_WINDOWS, [[0, 1]])

    expected = Evaluator._merge([{"stats": STATS_BY_WINDOW[(0.0, 0.2)]}])
    assert res["folds"][0]["stats"] == expected
    assert res["folds"][0]["n_sub_windows"] == 2
    assert res["folds"][0]["n_sub_windows_ok"] == 1


def test_empty_groups_list_gives_negative_infinite_aggregate(monkeypatch):
    import loop.evolve as evolve
    monkeypatch.setattr(evolve, "run_backtest", _fake_backtest)
    ev = Evaluator(data={}, n_folds=0)

    res = ev.evaluate_grouped(object(), SUB_WINDOWS, [])

    assert res["fold_fitness"] == []
    assert res["aggregate_fitness"] == float("-inf")
