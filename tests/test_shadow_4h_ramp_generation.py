"""Hermetic tests for tools/shadow_4h_ramp_generation.py -- the pure
gene-touch detection and reporting helpers, plus the --recipe CLI wiring
added 2026-09-02 for AGENTS.md item 2's option (2b). No network/market data or
real EvolutionRun involved anywhere in this file."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import tools.shadow_4h_ramp_generation as ramp_gen  # noqa: E402
from tools.shadow_4h_ramp_generation import print_top, touches_ramp_genes  # noqa: E402


def test_touches_ramp_genes_detects_bars_gene():
    patch = {"agents.risk_judge.genes.cold_start_ramp_bars": 90}
    assert touches_ramp_genes(patch) == ["agents.risk_judge.genes.cold_start_ramp_bars"]


def test_touches_ramp_genes_detects_start_scale_gene():
    patch = {"agents.risk_judge.genes.cold_start_ramp_start_scale": 0.5}
    assert touches_ramp_genes(patch) == [
        "agents.risk_judge.genes.cold_start_ramp_start_scale"]


def test_touches_ramp_genes_ignores_unrelated_patch():
    patch = {"risk.trailing_stop": -0.05, "agents.analyst.genes.rsi_len": 20}
    assert touches_ramp_genes(patch) == []


def test_touches_ramp_genes_handles_multiple_genes_in_one_patch():
    patch = {
        "agents.risk_judge.genes.cold_start_ramp_bars": 90,
        "agents.risk_judge.genes.cold_start_ramp_start_scale": 0.3,
        "risk.trailing_stop": -0.05,
    }
    touched = touches_ramp_genes(patch)
    assert len(touched) == 2
    assert "agents.risk_judge.genes.cold_start_ramp_bars" in touched
    assert "agents.risk_judge.genes.cold_start_ramp_start_scale" in touched


def test_print_top_handles_empty_top_without_error(capsys):
    print_top({"top": []})
    out = capsys.readouterr().out
    assert "researcher exhausted" in out


def test_print_top_prints_each_candidate_and_flags_ramp_touch(capsys):
    record = {"top": [
        {"fitness": 0.5, "kind": "blind", "target": "risk.trailing_stop",
         "patch": {"risk.trailing_stop": -0.05}},
        {"fitness": None, "kind": "blind", "target": "risk_judge",
         "patch": {"agents.risk_judge.genes.cold_start_ramp_bars": 90}},
    ]}
    print_top(record)
    out = capsys.readouterr().out
    assert "#1 fitness=0.500" in out
    assert "#2 fitness=nonfinite" in out
    assert "touches ['agents.risk_judge.genes.cold_start_ramp_bars']" in out


class _StubEvolutionRun:
    """Stands in for loop.evolve.EvolutionRun -- records its constructor args,
    never touches real market data or runs a real generation."""
    instances: list["_StubEvolutionRun"] = []

    def __init__(self, data, seed, verbose):
        self.data = data
        self.seed = seed
        self.verbose = verbose
        _StubEvolutionRun.instances.append(self)

    def generation(self, champion, n_blind):
        raise AssertionError("generation() should not be called when --generations 0")


def _run_main_with_recipe(monkeypatch, capsys, recipe: str):
    _StubEvolutionRun.instances = []
    monkeypatch.setattr(ramp_gen, "load_universe", lambda *a, **k: {"BTCUSDT": object()})
    monkeypatch.setattr(ramp_gen, "EvolutionRun", _StubEvolutionRun)
    monkeypatch.setattr(sys, "argv",
                        ["shadow_4h_ramp_generation.py", "--recipe", recipe,
                         "--generations", "0"])
    ramp_gen.main()
    return capsys.readouterr().out


def test_main_accepts_x6_recipe_with_no_hand_picked_patches(monkeypatch, capsys):
    out = _run_main_with_recipe(monkeypatch, capsys, "x6")
    assert "recipe=x6" in out
    assert "champion: 4h bars" in out
    assert "trailing_stop" not in out.split("\n")[0]
    assert len(_StubEvolutionRun.instances) == 1


def test_main_default_recipe_still_reports_ramp_genes(monkeypatch, capsys):
    out = _run_main_with_recipe(monkeypatch, capsys, "consv_trailing_ramp")
    assert "recipe=consv_trailing_ramp" in out
    assert "cold_start_ramp 120/0.2" in out
    assert "trailing_stop -0.06" in out
