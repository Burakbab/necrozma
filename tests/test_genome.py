import os

import pytest

import core.genome as genome_module
from core.genome import Genome


@pytest.fixture
def isolated_cwd(tmp_path, monkeypatch):
    """Genome.save/load/champion/promote write under GENOME_DIR, which is
    computed ONCE at module-import time from the process's cwd at that
    moment -- not the test's cwd. `monkeypatch.chdir` alone does nothing
    here (the module is already imported by the time any test runs); the
    module-level constant itself has to be patched, or these tests would
    silently write into the real repo's state/genomes/."""
    isolated = tmp_path / "state" / "genomes"
    monkeypatch.setattr(genome_module, "GENOME_DIR", str(isolated))
    return tmp_path


def test_seed_genome_defaults():
    g = Genome()
    assert g.version == 1
    assert g.bar_interval == "1d"
    assert g.data["parent"] is None
    assert g.enabled("consult_risky")


def test_child_bumps_version_and_does_not_mutate_parent():
    g = Genome()
    child = g.child([("risk.stop_loss", -0.2)], note="tighten stop")
    assert child.version == g.version + 1
    assert child.data["parent"] == g.version
    assert child.risk["stop_loss"] == -0.2
    # parent untouched
    assert g.risk["stop_loss"] == -0.12
    assert child.data["note"] == "tighten stop"


def test_child_applies_nested_dotted_path():
    g = Genome()
    child = g.child([("agents.risk_judge.genes.max_position_pct", 0.5)])
    assert child.gene("risk_judge", "max_position_pct") == 0.5
    # sibling genes under the same agent are untouched
    assert child.gene("risk_judge", "base_size_pct") == g.gene("risk_judge", "base_size_pct")


def test_complexity_counts_enabled_agents_and_genes():
    g = Genome()
    baseline = g.complexity()
    disabled = g.child([("agents.consult_risky.enabled", False)])
    # disabling an agent removes 1 (the agent itself) + its gene count
    risky_genes = len(g.genes("consult_risky"))
    assert disabled.complexity() == baseline - (1 + risky_genes)


def test_save_load_roundtrip(isolated_cwd):
    g = Genome().child([("risk.take_profit", 0.5)])
    path = g.save("mytag")
    assert os.path.exists(path)
    loaded = Genome.load("mytag")
    assert loaded.data == g.data


def test_load_by_version_int(isolated_cwd):
    g = Genome()
    g.save(f"v{g.version}")
    loaded = Genome.load(g.version)
    assert loaded.version == g.version


def test_champion_creates_seed_on_first_call(isolated_cwd):
    g = Genome.champion()
    assert g.version == 1
    assert g.bar_interval == "1d"
    assert os.path.exists(os.path.join(isolated_cwd, "state", "genomes", "champion.json"))
    assert os.path.exists(os.path.join(isolated_cwd, "state", "genomes", "v1.json"))


def test_champion_is_stable_across_calls(isolated_cwd):
    first = Genome.champion()
    second = Genome.champion()
    assert first.data == second.data


def test_promote_updates_champion(isolated_cwd):
    g0 = Genome.champion()
    child = g0.child([("risk.stop_loss", -0.3)], note="promoted candidate")
    child.promote()
    reloaded = Genome.champion()
    assert reloaded.version == child.version
    assert reloaded.risk["stop_loss"] == -0.3
    # the old version file is still there, immutable
    old = Genome.load(g0.version)
    assert old.risk["stop_loss"] == g0.risk["stop_loss"]
