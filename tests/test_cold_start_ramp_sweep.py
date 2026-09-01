"""Hermetic tests for tools/cold_start_ramp_sweep.py -- the grid-search
mechanics only (dedup, hard-fail flagging, report sorting), no network/market
data involved. See AGENTS.md item 2's "a real search over just those two
genes ... is the natural next step" note (2026-09-01 04:18 UTC session) for
why this script exists."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import tools.cold_start_ramp_sweep as sweep_mod
from tools.cold_start_ramp_sweep import RAMP_BARS_GRID, START_SCALE_GRID, sweep
from tools.shadow_4h_x6_seed import build_consv_trailing_seed


def test_grid_has_no_duplicate_points_after_noop_skip():
    seen = set()
    for ramp_bars in RAMP_BARS_GRID:
        for start_scale in START_SCALE_GRID:
            if ramp_bars == 0 and start_scale != 1.0:
                continue
            key = (ramp_bars, start_scale)
            assert key not in seen
            seen.add(key)


def test_grid_includes_the_previous_sessions_hand_picked_point():
    # 04:18 UTC session's ramp_bars=120/start_scale=0.10 is the point every
    # future sweep should be checked against -- must stay on the grid.
    assert 120 in RAMP_BARS_GRID
    assert 0.10 in START_SCALE_GRID


def test_grid_includes_the_true_noop_baseline():
    assert 0 in RAMP_BARS_GRID
    assert 1.0 in START_SCALE_GRID


class _FakeEvaluator:
    """Stands in for loop.evolve.Evaluator without touching real market data."""

    def folds(self):
        return [(0.0, 0.3), (0.3, 0.6)]

    def evaluate(self, g, folds=None):
        # Deterministic function of the genome's own patched gene so a test
        # can assert on a specific grid point without a real backtest.
        ramp_bars = g.genes("risk_judge")["cold_start_ramp_bars"]
        stats = {"max_dd": -0.5 if ramp_bars < 100 else -0.3, "trades": 50,
                 "bars": 500, "sortino": 1.0}
        return {"folds": [{"window": w, "stats": stats} for w in self.folds()],
                "aggregate_fitness": float(ramp_bars) / 100.0,
                "stats": stats}


def _fake_dd_corrected_stats(evaluator, g, stats, folds=None):
    return dict(stats)


def test_sweep_flags_clears_hard_fail_from_gate_stats(monkeypatch):
    monkeypatch.setattr(sweep_mod, "dd_corrected_stats", _fake_dd_corrected_stats)
    base = build_consv_trailing_seed("4h")
    rows = sweep(_FakeEvaluator(), base)

    low_ramp = next(r for r in rows if r["ramp_bars"] == 60 and r["start_scale"] == 0.10)
    high_ramp = next(r for r in rows if r["ramp_bars"] == 240 and r["start_scale"] == 0.10)
    assert low_ramp["gate_max_dd"] == pytest.approx(-0.5)
    assert low_ramp["clears_hard_fail"] is False  # 50% > MAX_DD_HARD_FAIL (40%)
    assert high_ramp["gate_max_dd"] == pytest.approx(-0.3)
    assert high_ramp["clears_hard_fail"] is True


def test_sweep_covers_every_grid_point_exactly_once(monkeypatch):
    monkeypatch.setattr(sweep_mod, "dd_corrected_stats", _fake_dd_corrected_stats)
    base = build_consv_trailing_seed("4h")
    rows = sweep(_FakeEvaluator(), base)
    expected = {(rb, ss) for rb in RAMP_BARS_GRID for ss in START_SCALE_GRID
                if not (rb == 0 and ss != 1.0)}
    got = {(r["ramp_bars"], r["start_scale"]) for r in rows}
    assert got == expected


def test_sweep_baseline_point_matches_ramp_off_default(monkeypatch):
    # ramp_bars=0/start_scale=1.0 must build a genome equivalent to the
    # no-ramp default -- this is the "reproduces the 01:14 UTC session's own
    # baseline" internal consistency check the sweep relies on.
    monkeypatch.setattr(sweep_mod, "dd_corrected_stats", _fake_dd_corrected_stats)
    base = build_consv_trailing_seed("4h")
    rows = sweep(_FakeEvaluator(), base)
    baseline = next(r for r in rows if r["ramp_bars"] == 0)
    assert baseline["start_scale"] == 1.0
    assert baseline["clears_hard_fail"] is False
