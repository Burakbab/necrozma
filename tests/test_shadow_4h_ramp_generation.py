"""Hermetic tests for tools/shadow_4h_ramp_generation.py -- the pure
gene-touch detection and reporting helpers only, no network/market data or
real EvolutionRun involved."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.shadow_4h_ramp_generation import print_top, touches_ramp_genes


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
