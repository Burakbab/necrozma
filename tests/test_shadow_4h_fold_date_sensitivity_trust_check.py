"""Hermetic tests for tools/shadow_4h_fold_date_sensitivity_trust_check.py --
the pure `summarize_flips` helper, plus one end-to-end `main()` run against a
monkeypatched `run_backtest` (same pattern as
tests/test_shadow_4h_trust_continuous_check.py). No network or real market
data involved."""
import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core import market  # noqa: E402
from loop.evolve import Evaluator  # noqa: E402
from tools.shadow_4h_fold_date_sensitivity_trust_check import (  # noqa: E402
    main,
    summarize_flips,
)


def test_summarize_flips_counts_flip_shifts():
    rows = [
        {"one_sided_hard_fail": True, "two_sided_hard_fail": False},
        {"one_sided_hard_fail": True, "two_sided_hard_fail": False},
        {"one_sided_hard_fail": False, "two_sided_hard_fail": False},
    ]
    summary = summarize_flips(rows)
    assert summary["n_shifts"] == 3
    assert summary["n_flip"] == 2
    assert summary["n_both_fail"] == 0
    assert summary["n_neither"] == 1


def test_summarize_flips_counts_both_fail_shifts():
    rows = [
        {"one_sided_hard_fail": True, "two_sided_hard_fail": True},
        {"one_sided_hard_fail": True, "two_sided_hard_fail": False},
    ]
    summary = summarize_flips(rows)
    assert summary["n_both_fail"] == 1
    assert summary["n_flip"] == 1
    assert summary["n_neither"] == 0


def test_summarize_flips_handles_empty():
    summary = summarize_flips([])
    assert summary == {"n_shifts": 0, "n_flip": 0, "n_both_fail": 0, "n_neither": 0}


def _frame(n: int, freq: str = "4h") -> pd.DataFrame:
    """`n` bars of `freq` ending now, so a `--shift`-day walk from "now" always
    lands inside the frame regardless of when the test runs."""
    idx = pd.date_range(end=pd.Timestamp.now(tz="UTC"), periods=n, freq=freq)
    return pd.DataFrame({"close": range(n)}, index=idx)


def test_main_reports_flip_when_fold_local_overstates_risk(monkeypatch, capsys):
    # Fold-local (-45%) hard-fails the one-sided gate, but the continuous
    # replay (-20%) is fine -- the trust_continuous_check flip case, exactly
    # what the 2026-09-02 01:12 UTC run note found for consv_trailing.
    import loop.evolve as evolve

    monkeypatch.setattr(market, "load_universe",
                        lambda universe, bar_interval, years, refresh=False:
                            {"BTCUSDT": _frame(4000)})

    def fake_backtest(g, data, a, b, log_detail=False):
        ev = Evaluator(data={}, n_folds=3)
        if (a, b) == (0.0, ev.search_end):
            return {"stats": {"max_dd": -0.20}}
        return {"stats": {"max_dd": -0.45, "sortino": 1.0, "trades": 10},
                "fitness": 1.0, "benchmark": {}, "edge": {}}

    monkeypatch.setattr(evolve, "run_backtest", fake_backtest)
    monkeypatch.setattr(sys, "argv",
                        ["shadow_4h_fold_date_sensitivity_trust_check.py",
                         "--recipe", "consv_trailing", "--shift", "1"])

    main()
    out = capsys.readouterr().out
    assert "1/1 shifts flip" in out
    assert "0/1 shifts fail under both views" in out
    assert "live_state.json untouched" in out


def test_main_reports_no_flip_when_both_sides_fail(monkeypatch, capsys):
    import loop.evolve as evolve

    monkeypatch.setattr(market, "load_universe",
                        lambda universe, bar_interval, years, refresh=False:
                            {"BTCUSDT": _frame(4000)})

    def fake_backtest(g, data, a, b, log_detail=False):
        return {"stats": {"max_dd": -0.45, "sortino": 1.0, "trades": 10},
                "fitness": 1.0, "benchmark": {}, "edge": {}}

    monkeypatch.setattr(evolve, "run_backtest", fake_backtest)
    monkeypatch.setattr(sys, "argv",
                        ["shadow_4h_fold_date_sensitivity_trust_check.py",
                         "--recipe", "consv_trailing", "--shift", "1"])

    main()
    out = capsys.readouterr().out
    assert "0/1 shifts flip" in out
    assert "1/1 shifts fail under both views" in out
    assert "does not hold up across" in out


def test_main_no_market_data_exits(monkeypatch, capsys):
    monkeypatch.setattr(market, "load_universe",
                        lambda universe, bar_interval, years, refresh=False: {})
    monkeypatch.setattr(sys, "argv",
                        ["shadow_4h_fold_date_sensitivity_trust_check.py",
                         "--shift", "1"])
    with pytest.raises(SystemExit):
        main()
    assert "no market data" in capsys.readouterr().out
