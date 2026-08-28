"""loop.evolve.summarize_holdout_pressure -- separates "nothing beat the
fold-aggregate gate" from "something did and the sealed holdout rejected it
anyway" in EvolutionRun's own recorded lineage, without any new evolve run.
Exists because AGENTS.md's 2026-08-18 4h-shadow work named the second
pattern (a lucky holdout draw entrenching a champion against genuinely
fold-superior challengers) as "worth watching for on the live 1d account
too" -- this is the tool that watches for it, reading lineage already in
live_state.json."""
from constitution import holdout_accepts
from loop.evolve import raw_holdout_beats, summarize_holdout_pressure


def _rejection(why, fold_fitness):
    return {"target": "some.gene", "why": why, "fold_fitness": fold_fitness}


def test_no_generations_for_this_champion_is_empty():
    summary = summarize_holdout_pressure([{"champion_version": 4}], champion_version=3)
    assert summary["n_generations"] == 0
    assert summary["holdout_draws"] == []


def test_no_new_proposals_generation_counted_separately():
    lineage = [{"champion_version": 3, "n_candidates": 0}]
    summary = summarize_holdout_pressure(lineage, champion_version=3)
    assert summary["n_generations"] == 1
    assert summary["no_proposal_generations"] == 1
    assert summary["fold_blocked_generations"] == 0
    assert summary["holdout_draws"] == []


def test_fold_gate_blocked_generation_has_no_holdout_draws():
    """Rejections whose `why` is a fold-aggregate-margin failure, not a
    sealed-holdout failure, must not be mistaken for a holdout draw."""
    lineage = [{
        "champion_version": 3,
        "n_candidates": 5,
        "rejections": [_rejection(
            "selection fitness 1.200 did not clear champion 1.389 + "
            "required margin 0.233", 1.2)],
    }]
    summary = summarize_holdout_pressure(lineage, champion_version=3)
    assert summary["fold_blocked_generations"] == 1
    assert summary["holdout_draws"] == []


def test_holdout_rejection_is_parsed_from_the_real_message_format():
    """Build the rejection `why` string with the actual constitution
    function, not a hand-typed guess at its format -- if `holdout_accepts`'s
    wording ever changes, this test breaks loudly instead of the parser
    silently under-counting real draws."""
    ok, why = holdout_accepts(champion_holdout=-1.1717268013730777,
                              challenger_holdout=-1.708, n_draws=8)
    assert ok is False
    lineage = [{
        "champion_version": 3,
        "n_candidates": 5,
        "rejections": [_rejection(why, 1.856)],
    }]
    summary = summarize_holdout_pressure(lineage, champion_version=3)
    assert summary["fold_blocked_generations"] == 0
    assert len(summary["holdout_draws"]) == 1
    d = summary["holdout_draws"][0]
    assert d["fold_fitness"] == 1.856
    assert d["holdout_challenger"] == -1.708
    assert d["holdout_champion"] == -1.1717268013730777 or round(d["holdout_champion"], 3) == -1.172
    assert d["cumulative_draws"] == 8


def test_multiple_holdout_draws_in_one_generation_are_all_counted():
    """`generation()` checks up to 3 top candidates and holdout-tests every
    one that clears the fold-aggregate gate -- a generation can carry more
    than one real holdout draw, and all of them must show up, not just the
    last."""
    _, why1 = holdout_accepts(-1.172, -2.296, n_draws=2)
    _, why2 = holdout_accepts(-1.172, -1.173, n_draws=3)
    _, why3 = holdout_accepts(-1.172, -1.172, n_draws=4)
    lineage = [{
        "champion_version": 3,
        "n_candidates": 14,
        "rejections": [_rejection(why1, 1.711),
                       _rejection(why2, 1.698),
                       _rejection(why3, 1.683)],
    }]
    summary = summarize_holdout_pressure(lineage, champion_version=3)
    assert len(summary["holdout_draws"]) == 3
    assert [d["cumulative_draws"] for d in summary["holdout_draws"]] == [2, 3, 4]
    assert summary["fold_blocked_generations"] == 0


def test_accepted_generation_is_not_double_counted_as_fold_blocked():
    lineage = [{
        "champion_version": 3,
        "n_candidates": 5,
        "accepted": {"new_version": 4},
        "rejections": [_rejection("selection fitness 0.5 did not clear "
                                  "champion 1.389 + required margin 0.2", 0.5)],
    }]
    summary = summarize_holdout_pressure(lineage, champion_version=3)
    assert summary["accepted_generations"] == 1
    assert summary["fold_blocked_generations"] == 0
    assert summary["holdout_draws"] == []


def test_only_generations_for_the_requested_champion_version_are_included():
    lineage = [
        {"champion_version": 2, "n_candidates": 3,
         "rejections": [_rejection("selection fitness 0.1 did not clear "
                                   "champion 0.5 + required margin 0.1", 0.1)]},
        {"champion_version": 3, "n_candidates": 0},
    ]
    summary = summarize_holdout_pressure(lineage, champion_version=3)
    assert summary["n_generations"] == 1
    assert summary["no_proposal_generations"] == 1


def test_real_champion_v3_lineage_shows_the_entrenchment_pattern():
    """Regression check against the actual shape found in live_state.json on
    2026-08-18: 9 real generations searched against champion v3, several
    fold-aggregate winners reached the sealed holdout, and every single one
    lost. Hand-built from the real recorded rejection strings (not loaded
    from the live file -- tests stay hermetic) so this keeps meaning
    something if the parser regexp is ever touched."""
    def gen(champion_fitness, n_candidates, rejections, accepted=None):
        e = {"champion_version": 3, "champion_fitness": champion_fitness,
             "n_candidates": n_candidates, "rejections": rejections}
        if accepted:
            e["accepted"] = accepted
        return e

    _, r1 = holdout_accepts(-1.1717268013730777, -2.296, n_draws=2)
    _, r2 = holdout_accepts(-1.1717268013730777, -1.173, n_draws=3)
    _, r3 = holdout_accepts(-1.1717268013730777, -1.1717268013730777, n_draws=4)
    lineage = [
        gen(1.3893142310355746, 28, [_rejection(r1, 1.711), _rejection(r2, 1.698),
                                     _rejection(r3, 1.683)]),
        gen(1.3893142310355746, 14, [_rejection(
            "selection fitness 1.560 did not clear champion 1.389 + "
            "required margin 0.233", 1.56)]),
    ]
    summary = summarize_holdout_pressure(lineage, champion_version=3)
    assert summary["n_generations"] == 2
    assert summary["fold_blocked_generations"] == 1
    assert len(summary["holdout_draws"]) == 3
    assert all(d["holdout_challenger"] <= d["holdout_champion"] + d["margin"]
              for d in summary["holdout_draws"])


def test_raw_holdout_beats_empty_draws_is_empty():
    result = raw_holdout_beats([])
    assert result == {"n_draws": 0, "n_raw_beats": 0, "first_flip_index": None,
                       "flips": []}


def test_raw_holdout_beats_finds_a_raw_beat_that_still_lost_on_margin():
    """Real shape from live_state.json's v3 lineage: a challenger's raw
    sealed-holdout score beat the champion's outright, but not by
    `required_margin()`'s additive amount, so `holdout_accepts` still
    rejected it -- `raw_holdout_beats` must surface that as a raw beat."""
    _, why = holdout_accepts(champion_holdout=0.763, challenger_holdout=1.636,
                              n_draws=15)
    assert why.startswith("failed sealed holdout")  # rejected on margin, not sign
    lineage = [{"champion_version": 3, "n_candidates": 14,
                "rejections": [_rejection(why, 1.0205)]}]
    draws = summarize_holdout_pressure(lineage, champion_version=3)["holdout_draws"]
    result = raw_holdout_beats(draws)
    assert result == {"n_draws": 1, "n_raw_beats": 1, "first_flip_index": 0,
                       "flips": [True]}


def test_raw_holdout_beats_no_flip_when_challenger_never_beats_champion_raw():
    _, why = holdout_accepts(champion_holdout=-1.172, challenger_holdout=-2.296,
                              n_draws=2)
    lineage = [{"champion_version": 3, "n_candidates": 14,
                "rejections": [_rejection(why, 1.7106)]}]
    draws = summarize_holdout_pressure(lineage, champion_version=3)["holdout_draws"]
    result = raw_holdout_beats(draws)
    assert result == {"n_draws": 1, "n_raw_beats": 0, "first_flip_index": None,
                       "flips": [False]}


def test_raw_holdout_beats_first_flip_index_ignores_later_draws():
    """Later draws in the same reign were evaluated against the champion
    that a real promotion at the first flip would have replaced -- they are
    not independent counterfactuals, so `first_flip_index` must point at the
    earliest one and not be recomputed from a later, larger raw beat."""
    _, why_no_beat = holdout_accepts(0.763, -1.172, n_draws=14)
    _, why_first_flip = holdout_accepts(0.763, 1.636, n_draws=15)
    _, why_second_flip = holdout_accepts(0.763, 1.613, n_draws=21)
    lineage = [{"champion_version": 3, "n_candidates": 14, "rejections": [
        _rejection(why_no_beat, 1.0),
        _rejection(why_first_flip, 1.02),
        _rejection(why_second_flip, 0.8),
    ]}]
    draws = summarize_holdout_pressure(lineage, champion_version=3)["holdout_draws"]
    result = raw_holdout_beats(draws)
    assert result["n_draws"] == 3
    assert result["n_raw_beats"] == 2
    assert result["first_flip_index"] == 1
    assert result["flips"] == [False, True, True]
