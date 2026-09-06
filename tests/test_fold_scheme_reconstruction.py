"""evotrader_bundle._reconstruct_champion_genome -- rebuilds a historical
champion genome purely from live_state.json's own recorded `lineage` (every
accepted promotion's patch), since there is no persisted genome archive to
load from directly (`state/genomes/` is gitignored, rebuildable-cache-only).
Backs the `fold-scheme --also-version N` diagnostic flag, which checks
whether a fold-scheme finding is a property of one genome or replicates
across independently-arrived-at champions."""
import json
import os

import pytest

import core.genome as genome_module
from core.genome import Genome, SEED_GENOME
from evotrader_bundle import _reconstruct_champion_genome


@pytest.fixture
def isolated_cwd(tmp_path, monkeypatch):
    """Genome.champion()/.child() write under GENOME_DIR, computed once at
    module-import time from the process's cwd at that moment -- see
    tests/test_genome.py's identically-named fixture for why
    monkeypatch.chdir alone would not be enough here."""
    isolated = tmp_path / "state" / "genomes"
    monkeypatch.setattr(genome_module, "GENOME_DIR", str(isolated))
    return tmp_path


def _accepted(new_version, patch):
    return {"accepted": {"new_version": new_version, "patch": patch}}


def test_version_1_is_the_seed_and_needs_no_lineage(isolated_cwd):
    g = _reconstruct_champion_genome(1, lineage=[])
    assert g.version == 1
    assert g.data == Genome.champion().data


def test_version_1_ignores_a_stale_champion_json_cache(isolated_cwd):
    """The bug found 2026-09-06: `evolve` unconditionally overwrites
    state/genomes/champion.json with the *live* champion at the start of
    every run, to diff before/after for a promotion. Any reconstruction
    diagnostic run afterward in the same container used to read that same
    file as its "version 1 seed" via `Genome.champion()`, silently
    reconstructing every version from the live champion's genes instead of
    the real seed. Simulates that pollution directly: a champion.json
    already sitting on disk with unrelated (fake-v3-shaped) genes must not
    change what version 1 reconstructs to."""
    genome_dir = os.path.join(str(isolated_cwd), "state", "genomes")
    os.makedirs(genome_dir, exist_ok=True)
    polluted = json.loads(json.dumps(SEED_GENOME))
    polluted["version"] = 3
    polluted["agents"]["consult_moderate"]["genes"]["rsi_lo"] = 999.0
    with open(os.path.join(genome_dir, "champion.json"), "w") as f:
        json.dump(polluted, f)

    g = _reconstruct_champion_genome(1, lineage=[])

    assert g.version == 1
    assert g.gene("consult_moderate", "rsi_lo") == SEED_GENOME["agents"]["consult_moderate"]["genes"]["rsi_lo"]
    assert g.data["agents"] == SEED_GENOME["agents"]


def test_reconstructed_v3_ignores_a_stale_champion_json_cache(isolated_cwd):
    """Same pollution, but chained through real accepted patches -- the
    scenario that actually broke `succession-audit`'s v1/v2/v3 rows on
    2026-09-06 (all three came out identical because they all silently
    based off the polluted live-champion cache)."""
    genome_dir = os.path.join(str(isolated_cwd), "state", "genomes")
    os.makedirs(genome_dir, exist_ok=True)
    polluted = json.loads(json.dumps(SEED_GENOME))
    polluted["version"] = 3
    polluted["risk"]["stop_loss"] = -0.9999
    with open(os.path.join(genome_dir, "champion.json"), "w") as f:
        json.dump(polluted, f)

    lineage = [
        _accepted(2, {"agents.consult_moderate.genes.rsi_lo": 35.1764}),
        _accepted(3, {"agents.consult_moderate.genes.rsi_lo": 25.0,
                      "risk.max_bars_held": 15}),
    ]
    g3 = _reconstruct_champion_genome(3, lineage)

    assert g3.version == 3
    assert g3.risk["stop_loss"] == SEED_GENOME["risk"]["stop_loss"]


def test_reconstructs_single_accepted_patch(isolated_cwd):
    lineage = [_accepted(2, {"risk.stop_loss": -0.3})]
    g = _reconstruct_champion_genome(2, lineage)
    assert g.version == 2
    assert g.risk["stop_loss"] == -0.3


def test_reconstructs_chained_patches_in_order(isolated_cwd):
    lineage = [
        _accepted(2, {"agents.consult_moderate.genes.rsi_lo": 35.1764}),
        _accepted(3, {"agents.consult_moderate.genes.rsi_lo": 25.0,
                      "risk.max_bars_held": 15}),
    ]
    g3 = _reconstruct_champion_genome(3, lineage)
    assert g3.version == 3
    assert g3.gene("consult_moderate", "rsi_lo") == 25.0
    assert g3.risk["max_bars_held"] == 15

    # intermediate version is reachable too, with the gene at its own value
    g2 = _reconstruct_champion_genome(2, lineage)
    assert g2.version == 2
    assert g2.gene("consult_moderate", "rsi_lo") == 35.1764


def test_ignores_non_accepted_lineage_entries(isolated_cwd):
    lineage = [
        {"champion_version": 1, "n_candidates": 5},  # a generation with no promotion
        _accepted(2, {"risk.stop_loss": -0.3}),
    ]
    g = _reconstruct_champion_genome(2, lineage)
    assert g.risk["stop_loss"] == -0.3


def test_unrecorded_version_raises(isolated_cwd):
    lineage = [_accepted(2, {"risk.stop_loss": -0.3})]
    with pytest.raises(ValueError, match="version 99"):
        _reconstruct_champion_genome(99, lineage)


def test_reconstructed_v3_matches_real_live_lineage_bit_exact(isolated_cwd):
    """The real-world check this diagnostic depends on: replaying the
    actual accepted patches recorded for the live v1->v2->v3 promotions
    must reproduce the exact same genes the live account is trading with
    today. If this ever drifts, `fold-scheme --also-version N`'s numbers
    for the reconstructed champion would be silently wrong."""
    import json
    import os

    live_state_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "live_state.json",
    )
    with open(live_state_path) as f:
        state = json.load(f)
    lineage = state["lineage"]
    live_genes = state["genome"]

    g3 = _reconstruct_champion_genome(3, lineage)
    assert g3.version == live_genes["version"]
    assert g3.risk == live_genes["risk"]
    for agent, spec in live_genes["agents"].items():
        for key, value in spec["genes"].items():
            assert g3.gene(agent, key) == value, f"{agent}.{key} mismatch"
