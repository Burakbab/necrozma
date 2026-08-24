"""Evaluator.continuous_max_dd / dd_corrected_stats -- closes the
fold-boundary max_dd blind spot `fold-dd-blindspot` found (2026-08-22, see
AGENTS.md item 2 and AMENDMENTS.md): `Evaluator._merge`'s max_dd is the worst
of each fold's own INDEPENDENTLY backtested local peak-to-trough, so a true
drawdown that starts near the end of one fold and bottoms out in the next is
invisible to every fold's own local number and therefore to the merged
number `constitution.accepts()`/`fitness()` gate on. These two functions run
one additional, unbroken backtest over the fold-covered span and fold its
max_dd into the gate stats -- see `EvolutionRun.generation()` for where the
correction is actually applied to a promotion decision."""
import pytest

from loop.evolve import Evaluator, dd_corrected_stats, dd_trust_continuous_stats


def test_continuous_max_dd_calls_backtest_over_full_fold_span(monkeypatch):
    import loop.evolve as evolve

    seen = []

    def fake_backtest(g, data, a, b, log_detail=False):
        seen.append((a, b))
        return {"stats": {"max_dd": -0.30}}

    monkeypatch.setattr(evolve, "run_backtest", fake_backtest)
    ev = Evaluator(data={}, n_folds=3)  # folds() -> [(0, .283), (.283, .567), (.567, .85)]
    result = ev.continuous_max_dd(object())
    assert result == pytest.approx(-0.30)
    assert seen == [(0.0, ev.search_end)]


def test_continuous_max_dd_respects_explicit_folds(monkeypatch):
    import loop.evolve as evolve

    seen = []

    def fake_backtest(g, data, a, b, log_detail=False):
        seen.append((a, b))
        return {"stats": {"max_dd": -0.12}}

    monkeypatch.setattr(evolve, "run_backtest", fake_backtest)
    ev = Evaluator(data={}, n_folds=3)
    windows = [(0.1, 0.3), (0.3, 0.5), (0.5, 0.9)]
    result = ev.continuous_max_dd(object(), folds=windows)
    assert seen == [(0.1, 0.9)]
    assert result == pytest.approx(-0.12)


def test_continuous_max_dd_returns_none_on_backtest_error(monkeypatch):
    import loop.evolve as evolve

    monkeypatch.setattr(evolve, "run_backtest",
                        lambda g, data, a, b, log_detail=False: {"error": "boom"})
    ev = Evaluator(data={}, n_folds=3)
    assert ev.continuous_max_dd(object()) is None


def test_continuous_max_dd_returns_none_on_empty_folds():
    ev = Evaluator(data={}, n_folds=3)
    assert ev.continuous_max_dd(object(), folds=[]) is None


def test_dd_corrected_stats_takes_the_worse_of_the_two(monkeypatch):
    # The whole point: a genome whose fold-merged max_dd looks fine but whose
    # true continuous replay is worse must come back with the worse number,
    # not the fold-merged one -- that is the exact blind spot found in v3
    # (gate-visible -34.1% vs true continuous -46.5%).
    import loop.evolve as evolve

    monkeypatch.setattr(evolve, "run_backtest",
                        lambda g, data, a, b, log_detail=False: {"stats": {"max_dd": -0.465}})
    ev = Evaluator(data={}, n_folds=3)
    stats = {"max_dd": -0.341, "trades": 100, "bars": 900}
    corrected = dd_corrected_stats(ev, object(), stats)
    assert corrected["max_dd"] == pytest.approx(-0.465)
    # original input dict is untouched
    assert stats["max_dd"] == pytest.approx(-0.341)


def test_dd_corrected_stats_never_loosens_the_gate(monkeypatch):
    # If the continuous replay happens to read BETTER than the fold-merged
    # worst, the gate must keep the stricter (more negative) fold number --
    # this fix only ever tightens, never loosens, same standing rule as
    # every prior AMENDMENTS.md row.
    import loop.evolve as evolve

    monkeypatch.setattr(evolve, "run_backtest",
                        lambda g, data, a, b, log_detail=False: {"stats": {"max_dd": -0.10}})
    ev = Evaluator(data={}, n_folds=3)
    stats = {"max_dd": -0.341, "trades": 100, "bars": 900}
    corrected = dd_corrected_stats(ev, object(), stats)
    assert corrected["max_dd"] == pytest.approx(-0.341)


def test_dd_corrected_stats_falls_back_to_original_on_backtest_error(monkeypatch):
    import loop.evolve as evolve

    monkeypatch.setattr(evolve, "run_backtest",
                        lambda g, data, a, b, log_detail=False: {"error": "boom"})
    ev = Evaluator(data={}, n_folds=3)
    stats = {"max_dd": -0.341, "trades": 100, "bars": 900}
    corrected = dd_corrected_stats(ev, object(), stats)
    assert corrected["max_dd"] == pytest.approx(-0.341)


def test_dd_corrected_stats_preserves_other_fields():
    ev = Evaluator(data={}, n_folds=3)
    stats = {"max_dd": -0.341, "trades": 100, "bars": 900, "sortino": 1.2}
    corrected = dd_corrected_stats(ev, object(), stats, folds=[])
    assert corrected["trades"] == 100
    assert corrected["sortino"] == pytest.approx(1.2)


# dd_trust_continuous_stats -- diagnostic-only sibling, NOT wired into
# accepts()/EvolutionRun.generation() (see succession-audit's 2026-08-22
# finding: fold-merged max_dd can also OVERSTATE true risk via fold
# rebasing, a direction dd_corrected_stats()'s min() can't recover from).

def test_dd_trust_continuous_stats_replaces_worse_fold_local_number(monkeypatch):
    # v2's own case: fold-merged (-40.1%) is WORSE than the true continuous
    # replay (-38.1%), an overstatement from fold-2 rebasing to a fresh local
    # peak. Unlike dd_corrected_stats() (which would keep -40.1%, the worse
    # of the two), this function always trusts the continuous number.
    import loop.evolve as evolve

    monkeypatch.setattr(evolve, "run_backtest",
                        lambda g, data, a, b, log_detail=False: {"stats": {"max_dd": -0.381}})
    ev = Evaluator(data={}, n_folds=3)
    stats = {"max_dd": -0.401, "trades": 100, "bars": 900}
    corrected = dd_trust_continuous_stats(ev, object(), stats)
    assert corrected["max_dd"] == pytest.approx(-0.381)
    assert stats["max_dd"] == pytest.approx(-0.401)


def test_dd_trust_continuous_stats_also_replaces_better_fold_local_number(monkeypatch):
    # The original fold-dd-blindspot direction: continuous is WORSE than
    # fold-merged. Same outcome as dd_corrected_stats() here (both trust the
    # worse continuous number), just by always-replace rather than min().
    import loop.evolve as evolve

    monkeypatch.setattr(evolve, "run_backtest",
                        lambda g, data, a, b, log_detail=False: {"stats": {"max_dd": -0.465}})
    ev = Evaluator(data={}, n_folds=3)
    stats = {"max_dd": -0.341, "trades": 100, "bars": 900}
    corrected = dd_trust_continuous_stats(ev, object(), stats)
    assert corrected["max_dd"] == pytest.approx(-0.465)


def test_dd_trust_continuous_stats_falls_back_to_original_on_backtest_error(monkeypatch):
    import loop.evolve as evolve

    monkeypatch.setattr(evolve, "run_backtest",
                        lambda g, data, a, b, log_detail=False: {"error": "boom"})
    ev = Evaluator(data={}, n_folds=3)
    stats = {"max_dd": -0.341, "trades": 100, "bars": 900}
    corrected = dd_trust_continuous_stats(ev, object(), stats)
    assert corrected["max_dd"] == pytest.approx(-0.341)


def test_dd_trust_continuous_stats_preserves_other_fields():
    ev = Evaluator(data={}, n_folds=3)
    stats = {"max_dd": -0.341, "trades": 100, "bars": 900, "sortino": 1.2}
    corrected = dd_trust_continuous_stats(ev, object(), stats, folds=[])
    assert corrected["trades"] == 100
    assert corrected["sortino"] == pytest.approx(1.2)
