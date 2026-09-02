"""Hermetic tests for tools/consv1_threshold_sweep.py -- the grid-search
mechanics only (grid coverage, hard-fail flagging, report sorting), no
network/market data involved. See AGENTS.md item 2's 2026-09-02 ~09:47-10:10
UTC session note (SCALE ruled out, "consv1 consult-tightening thresholds ...
not yet checked in isolation" flagged as the remaining untried slice) for why
this script exists."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import tools.consv1_threshold_sweep as sweep_mod
from tools.consv1_threshold_sweep import RSI_BUY_BELOW_GRID, Z_BUY_BELOW_GRID, sweep
from tools.shadow_4h_x6_seed import build_x6_scaled_seed


def test_grid_includes_the_untightened_noop_baseline():
    # core/genome.py's own defaults -- the point that should reproduce the
    # bare x6 seed's already-measured hard-fail as a sanity check.
    assert 38.0 in RSI_BUY_BELOW_GRID
    assert -0.8 in Z_BUY_BELOW_GRID


def test_grid_includes_the_previous_sessions_tightened_point():
    # 2026-08-31 22:07 UTC session's consv1 point, here without the
    # trailing_stop tightening it was always previously stacked with.
    assert 30.0 in RSI_BUY_BELOW_GRID
    assert -1.2 in Z_BUY_BELOW_GRID


def test_grid_has_no_duplicate_points():
    seen = set()
    for rsi in RSI_BUY_BELOW_GRID:
        for z in Z_BUY_BELOW_GRID:
            key = (rsi, z)
            assert key not in seen
            seen.add(key)


class _FakeEvaluator:
    """Stands in for loop.evolve.Evaluator without touching real market data."""

    def folds(self):
        return [(0.0, 0.3), (0.3, 0.6)]

    def evaluate(self, g, folds=None):
        # Deterministic function of the genome's own patched genes so a test
        # can assert on a specific grid point without a real backtest.
        rsi = g.genes("consult_conservative")["rsi_buy_below"]
        stats = {"max_dd": -0.5 if rsi >= 38.0 else -0.3, "trades": 50,
                 "bars": 500, "sortino": 1.0}
        return {"folds": [{"window": w, "stats": stats} for w in self.folds()],
                "aggregate_fitness": (38.0 - rsi) / 10.0,
                "stats": stats}


def _fake_dd_corrected_stats(evaluator, g, stats, folds=None):
    return dict(stats)


def test_sweep_flags_clears_hard_fail_from_gate_stats(monkeypatch):
    monkeypatch.setattr(sweep_mod, "dd_corrected_stats", _fake_dd_corrected_stats)
    base = build_x6_scaled_seed("4h")
    rows = sweep(_FakeEvaluator(), base)

    baseline = next(r for r in rows if r["rsi_buy_below"] == 38.0 and r["z_buy_below"] == -0.8)
    tightened = next(r for r in rows if r["rsi_buy_below"] == 22.0 and r["z_buy_below"] == -1.6)
    assert baseline["gate_max_dd"] == pytest.approx(-0.5)
    assert baseline["clears_hard_fail"] is False  # 50% > MAX_DD_HARD_FAIL (40%)
    assert tightened["gate_max_dd"] == pytest.approx(-0.3)
    assert tightened["clears_hard_fail"] is True


def test_sweep_covers_every_grid_point_exactly_once(monkeypatch):
    monkeypatch.setattr(sweep_mod, "dd_corrected_stats", _fake_dd_corrected_stats)
    base = build_x6_scaled_seed("4h")
    rows = sweep(_FakeEvaluator(), base)
    expected = {(rsi, z) for rsi in RSI_BUY_BELOW_GRID for z in Z_BUY_BELOW_GRID}
    got = {(r["rsi_buy_below"], r["z_buy_below"]) for r in rows}
    assert got == expected


def test_sweep_leaves_trailing_stop_at_the_untightened_default(monkeypatch):
    # The whole point of this sweep is isolating consv1 from trailing_stop --
    # every grid point's genome must keep the seed's default trailing_stop.
    monkeypatch.setattr(sweep_mod, "dd_corrected_stats", _fake_dd_corrected_stats)
    base = build_x6_scaled_seed("4h")
    captured = []
    real_child = base.__class__.child

    def _spy_child(self, patches, note=""):
        captured.append(patches)
        return real_child(self, patches, note=note)

    monkeypatch.setattr(base.__class__, "child", _spy_child)
    sweep(_FakeEvaluator(), base)
    for patches in captured:
        keys = {k for k, _ in patches}
        assert "risk.trailing_stop" not in keys
        assert "agents.risk_judge.genes.cold_start_ramp_bars" not in keys
