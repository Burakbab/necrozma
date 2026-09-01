"""Hermetic tests for tools/shadow_4h_fold_date_sensitivity.py -- the pure
slicing, gate-margin, recipe-selection and summary helpers only. No network,
market data, or real Evaluator/backtest involved."""
import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.shadow_4h_fold_date_sensitivity import (
    build_genome,
    gate_margin,
    slice_window,
    summarize_shifts,
)


def _frame(start: str, n: int, freq: str = "4h") -> pd.DataFrame:
    idx = pd.date_range(start, periods=n, freq=freq, tz="UTC")
    return pd.DataFrame({"close": range(n)}, index=idx)


def test_slice_window_keeps_only_bars_inside_trailing_width():
    raw = {"BTCUSDT": _frame("2020-01-01", 200, "1D")}
    as_of = pd.Timestamp("2020-06-01", tz="UTC")
    width = pd.Timedelta(days=30)
    sliced = slice_window(raw, as_of, width)
    df = sliced["BTCUSDT"]
    assert df.index.min() >= as_of - width
    assert df.index.max() <= as_of
    assert len(df) < 200


def test_slice_window_drops_symbol_left_empty_by_the_slice():
    raw = {"BTCUSDT": _frame("2020-01-01", 200, "1D"),
          "ETHUSDT": _frame("2025-01-01", 50, "1D")}
    as_of = pd.Timestamp("2020-06-01", tz="UTC")
    width = pd.Timedelta(days=30)
    sliced = slice_window(raw, as_of, width)
    assert "BTCUSDT" in sliced
    assert "ETHUSDT" not in sliced


def test_gate_margin_positive_when_clearing():
    # -0.30 max_dd vs 0.40 hard-fail cutoff -> clears by 10 points
    assert gate_margin(-0.30) == pytest.approx(0.10)


def test_gate_margin_negative_when_hard_failing():
    # -0.434 max_dd vs 0.40 cutoff -> fails by 3.4 points, matching the
    # 2026-09-01 10:27 UTC run note's real boundary-flip number
    assert gate_margin(-0.434) == pytest.approx(-0.034)


def test_gate_margin_uses_magnitude_of_signed_max_dd():
    assert gate_margin(-0.20) == gate_margin(0.20)


def test_build_genome_x6_ignores_trailing_stop_arg():
    g = build_genome("x6", "4h", -0.99)
    assert g.bar_interval == "4h"
    assert g.risk["trailing_stop"] != -0.99


def test_build_genome_consv_trailing_applies_trailing_stop():
    g = build_genome("consv_trailing", "4h", -0.12)
    assert g.risk["trailing_stop"] == -0.12


def test_build_genome_consv_trailing_ramp_has_ramp_genes():
    g = build_genome("consv_trailing_ramp", "4h", -0.06)
    assert g.gene("risk_judge", "cold_start_ramp_bars") == 120
    assert g.gene("risk_judge", "cold_start_ramp_start_scale") == 0.20


def test_summarize_shifts_counts_hard_fails_and_margins():
    rows = [
        {"aggregate_fitness": 0.5, "gate_max_dd": -0.30, "hard_fail": False},
        {"aggregate_fitness": 0.2, "gate_max_dd": -0.434, "hard_fail": True},
        {"aggregate_fitness": 0.8, "gate_max_dd": -0.346, "hard_fail": False},
    ]
    summary = summarize_shifts(rows)
    assert summary["n_shifts"] == 3
    assert summary["n_hard_fail"] == 1
    assert summary["n_clearing"] == 2
    assert summary["min_margin"] == pytest.approx(-0.034)
    assert summary["max_margin"] == pytest.approx(0.10)
    assert summary["aggregate_fitness_range"] == (0.5, 0.8)


def test_summarize_shifts_handles_all_hard_fail():
    rows = [{"aggregate_fitness": float("-inf"), "gate_max_dd": -0.50, "hard_fail": True}]
    summary = summarize_shifts(rows)
    assert summary["n_hard_fail"] == 1
    assert summary["aggregate_fitness_range"] is None


def test_summarize_shifts_handles_empty():
    summary = summarize_shifts([])
    assert summary["n_shifts"] == 0
    assert summary["min_margin"] is None
    assert summary["aggregate_fitness_range"] is None
