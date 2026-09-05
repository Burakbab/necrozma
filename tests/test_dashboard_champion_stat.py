from evotrader_dashboard import _genome_sub


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
