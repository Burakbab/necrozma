import json

import evotrader_dashboard as dashboard
from evotrader_dashboard import _genome_sub, build


def test_genome_sub_shows_tested_count_for_current_champion():
    live = {"researcher_memory": {"champion_version": 3, "tested": list(range(924))}}
    champ = {"version": 3}
    sub = _genome_sub(live, champ, lineage=[1, 2, 3])
    assert "3 generation(s) run" in sub
    assert "924 challenger idea(s) tried" in sub


def test_genome_sub_omits_tested_count_for_stale_memory():
    # researcher_memory persists per-champion and resets on promotion, so a
    # champion_version mismatch (just-promoted, memory not seeded yet) must
    # not surface a stale count.
    live = {"researcher_memory": {"champion_version": 2, "tested": list(range(50))}}
    champ = {"version": 3}
    sub = _genome_sub(live, champ, lineage=[1])
    assert sub == "1 generation(s) run"


def test_genome_sub_handles_missing_researcher_memory():
    sub = _genome_sub(live={}, champ={"version": 1}, lineage=[])
    assert sub == "0 generation(s) run"


def test_genome_sub_omits_suffix_when_tested_list_empty():
    live = {"researcher_memory": {"champion_version": 1, "tested": []}}
    sub = _genome_sub(live, champ={"version": 1}, lineage=[])
    assert sub == "0 generation(s) run"


def test_build_prefers_live_state_genome_over_stale_champion_cache(tmp_path, monkeypatch):
    # state/genomes/champion.json is a gitignored per-container cache that can
    # lag behind live_state.json (the documented source of truth) until evolve
    # next overwrites it. It once briefly published a wrong genome version on
    # the public dashboard (AGENTS.md Next steps item 10) because build()
    # preferred it over live_state.json. Regression test for the fix.
    live_path = tmp_path / "live.json"
    champ_path = tmp_path / "champion.json"
    out_path = tmp_path / "index.html"

    live_path.write_text(json.dumps({
        "genome": {"version": 3},
        "broker": {
            "nav_history": [], "start_cash": 10_000, "cash": 10_000,
            "closed": [], "positions": {},
        },
        "journal": [], "ticks": 0, "started": "2026-01-01", "lineage": [],
    }))
    champ_path.write_text(json.dumps({"version": 1}))  # stale disk cache

    monkeypatch.setattr(dashboard, "P_LIVE", str(live_path))
    monkeypatch.setattr(dashboard, "P_CHAMP", str(champ_path))
    monkeypatch.setattr(dashboard, "P_LIN", str(tmp_path / "lineage.jsonl"))
    monkeypatch.setattr(dashboard, "P_BT", str(tmp_path / "backtest.json"))

    build(out_path=str(out_path))
    rendered = out_path.read_text()
    assert ">v3<" in rendered
    assert ">v1<" not in rendered
