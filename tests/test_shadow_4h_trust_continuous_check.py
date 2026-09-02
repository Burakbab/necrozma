"""Hermetic tests for tools/shadow_4h_trust_continuous_check.py -- the pure
`audit_genome`/`format_row` logic and the unknown-recipe CLI guard, using the
same monkeypatched-`run_backtest` pattern as tests/test_continuous_max_dd.py.
No network or real market data involved."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from loop.evolve import Evaluator  # noqa: E402
from tools.shadow_4h_trust_continuous_check import (  # noqa: E402
    audit_genome,
    format_row,
    main,
)


def _fold_and_continuous(monkeypatch, fold_dd: float, continuous_dd: float):
    """Every per-fold `run_backtest` call returns `fold_dd`; the one call
    covering the whole fold span (continuous_max_dd's own signature: window
    == (folds[0][0], folds[-1][1])) returns `continuous_dd` instead."""
    import loop.evolve as evolve

    ev = Evaluator(data={}, n_folds=3)
    full_span = (0.0, ev.search_end)

    def fake_backtest(g, data, a, b, log_detail=False):
        if (a, b) == full_span:
            return {"stats": {"max_dd": continuous_dd}}
        return {"stats": {"max_dd": fold_dd, "sortino": 1.0, "trades": 10},
                "fitness": 1.0, "benchmark": {}, "edge": {}}

    monkeypatch.setattr(evolve, "run_backtest", fake_backtest)
    return ev


def test_audit_genome_flips_when_fold_local_overstates_risk(monkeypatch):
    # Fold-local hard-fails (-45%) but the continuous replay is fine (-20%):
    # the current one-sided gate (min of the two) hard-fails, the two-sided
    # trust_continuous view does not -- exactly the "fold rebasing
    # overstatement" case dd_trust_continuous_stats() exists for.
    ev = _fold_and_continuous(monkeypatch, fold_dd=-0.45, continuous_dd=-0.20)
    audit = audit_genome(ev, object())
    assert audit["dd_corrected_hard_fail"] is True
    assert audit["dd_corrected_max_dd"] == pytest.approx(-0.45)
    assert audit["trust_continuous_hard_fail"] is False
    assert audit["trust_continuous_max_dd"] == pytest.approx(-0.20)
    assert audit["verdict_flips"] is True


def test_audit_genome_does_not_flip_when_risk_is_real(monkeypatch):
    # Both views agree the drawdown is bad: not a measurement artifact.
    ev = _fold_and_continuous(monkeypatch, fold_dd=-0.45, continuous_dd=-0.48)
    audit = audit_genome(ev, object())
    assert audit["dd_corrected_hard_fail"] is True
    assert audit["trust_continuous_hard_fail"] is True
    assert audit["verdict_flips"] is False


def test_audit_genome_no_flip_when_neither_hard_fails(monkeypatch):
    ev = _fold_and_continuous(monkeypatch, fold_dd=-0.10, continuous_dd=-0.12)
    audit = audit_genome(ev, object())
    assert audit["dd_corrected_hard_fail"] is False
    assert audit["trust_continuous_hard_fail"] is False
    assert audit["verdict_flips"] is False


def test_audit_genome_reports_per_fold_max_dd(monkeypatch):
    ev = _fold_and_continuous(monkeypatch, fold_dd=-0.30, continuous_dd=-0.30)
    audit = audit_genome(ev, object())
    assert audit["fold_max_dd"] == [pytest.approx(-0.30)] * 3


def test_format_row_flags_a_flip():
    audit = {"aggregate_fitness": 0.5, "fold_max_dd": [-0.45, -0.1, -0.1],
             "dd_corrected_max_dd": -0.45, "dd_corrected_fitness": -1.0,
             "dd_corrected_hard_fail": True,
             "trust_continuous_max_dd": -0.20, "trust_continuous_fitness": 1.0,
             "trust_continuous_hard_fail": False, "verdict_flips": True}
    out = format_row("consv_trailing_ramp", audit)
    assert "consv_trailing_ramp" in out
    assert "gate verdict flips" in out


def test_format_row_no_flip_marker_when_verdicts_agree():
    audit = {"aggregate_fitness": -1.0, "fold_max_dd": [-0.45, -0.1, -0.1],
             "dd_corrected_max_dd": -0.45, "dd_corrected_fitness": -1.0,
             "dd_corrected_hard_fail": True,
             "trust_continuous_max_dd": -0.48, "trust_continuous_fitness": -1.2,
             "trust_continuous_hard_fail": True, "verdict_flips": False}
    out = format_row("x6", audit)
    assert "gate verdict flips" not in out


def test_main_rejects_unknown_recipe(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["prog", "--recipes", "not_a_real_recipe"])
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 1
    assert "unknown recipe" in capsys.readouterr().out
