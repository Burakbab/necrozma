"""loop.evolve.boldness_scan -- controlled A/B replay isolating whether
Researcher.perturb's unbounded `boldness` argument (vs. capped) changes how
often a shadow search's best candidate clears the fold-aggregate accept()
gate and the sealed holdout. Fully hermetic: fakes `run_backtest` so no
market data or real search is needed."""
from dataclasses import dataclass

import pytest

from core.genome import Genome
from loop.evolve import Evaluator, boldness_scan


HOLDOUT_WINDOW = Evaluator(data={}).holdout  # (0.85, 1.0) at default HOLDOUT_FRAC


def _stats(sortino):
    return {"sortino": sortino, "trades": 50, "bars": 200, "max_dd": -0.1,
            "turnover_annual": 1.0, "win_rate": 0.5, "total_return": 0.1,
            "halt_count": 0}


def _make_backtest(champion_version):
    """Every genome scores a flat fold/holdout sortino keyed only by whether
    it's the champion (by version) or a challenger -- children always score
    strictly better on both fold and holdout, so any run that proposes at
    least one finite candidate promotes deterministically. This isolates the
    thing under test (how many candidates each arm proposes, and how many
    reach a promotion) from backtest-outcome noise."""
    def fake_backtest(g, data, a, b, log_detail=False):
        if log_detail:
            return {"closed_trades": [], "stats": {}}
        is_champion = g.version == champion_version[0]
        sortino = 1.0 if is_champion else 5.0
        return {"stats": _stats(sortino), "fitness": sortino,
                "benchmark": {}, "edge": {"excess_return": 0.0, "beat_benchmark": True}}
    return fake_backtest


def test_uncapped_and_capped_are_identical_when_cap_is_none(monkeypatch):
    import loop.evolve as evolve

    champ = Genome()
    champion_version = [champ.version]
    monkeypatch.setattr(evolve, "run_backtest", _make_backtest(champion_version))
    monkeypatch.setattr(Genome, "promote", lambda self: None)
    monkeypatch.setattr(Genome, "save", lambda self, tag=None: None)

    ev = Evaluator(data={"X": []})
    result = boldness_scan(champ, ev, generations=3, n_blind=6, boldness_cap=None, seed=11)

    assert result["uncapped"] == result["capped"]


def test_capped_arm_never_exceeds_the_cap(monkeypatch):
    import loop.evolve as evolve

    champ = Genome()
    champion_version = [champ.version]

    def fake_backtest(g, data, a, b, log_detail=False):
        if log_detail:
            return {"closed_trades": [], "stats": {}}
        # Every challenger loses -- forces stagnation to climb every
        # generation in both arms, so boldness has room to grow past the cap.
        is_champion = g.version == champion_version[0]
        sortino = 1.0 if is_champion else 0.5
        return {"stats": _stats(sortino), "fitness": sortino,
                "benchmark": {}, "edge": {"excess_return": 0.0, "beat_benchmark": False}}

    monkeypatch.setattr(evolve, "run_backtest", fake_backtest)
    monkeypatch.setattr(Genome, "promote",
                        lambda self: (_ for _ in ()).throw(
                            AssertionError("no candidate should clear the gate here")))
    monkeypatch.setattr(Genome, "save",
                        lambda self, tag=None: (_ for _ in ()).throw(
                            AssertionError("boldness_scan must never save")))

    ev = Evaluator(data={"X": []})
    result = boldness_scan(champ, ev, generations=8, n_blind=6, boldness_cap=2.0, seed=3,
                           initial_stagnation=0)

    uncapped_boldness = result["uncapped"]["effective_boldness_per_gen"]
    capped_boldness = result["capped"]["effective_boldness_per_gen"]
    assert all(b <= 2.0 for b in capped_boldness)
    # With 8 generations of pure stagnation the uncapped arm's boldness
    # should actually climb past the cap -- otherwise this test isn't
    # exercising the thing it claims to.
    assert max(uncapped_boldness) > 2.0
    assert result["uncapped"]["shadow_promotions"] == 0
    assert result["capped"]["shadow_promotions"] == 0
    assert result["uncapped"]["final_stagnation"] == 8
    assert result["capped"]["final_stagnation"] == 8


def test_a_clearly_better_challenger_promotes_and_stops_both_arms_stagnating(monkeypatch):
    import loop.evolve as evolve

    champ = Genome()
    champion_version = [champ.version]
    monkeypatch.setattr(evolve, "run_backtest", _make_backtest(champion_version))
    monkeypatch.setattr(Genome, "promote", lambda self: None)
    monkeypatch.setattr(Genome, "save",
                        lambda self, tag=None: (_ for _ in ()).throw(
                            AssertionError("boldness_scan must never save")))

    ev = Evaluator(data={"X": []})
    result = boldness_scan(champ, ev, generations=1, n_blind=6, boldness_cap=5.0, seed=42)

    for arm in ("uncapped", "capped"):
        r = result[arm]
        assert r["shadow_promotions"] == 1
        assert r["holdout_gate_clears"] == 1
        assert r["fold_gate_clears"] >= 1
        assert r["final_champion_version"] != champ.version
        assert r["final_stagnation"] == 0


def test_zero_generations_is_a_no_op(monkeypatch):
    import loop.evolve as evolve

    def boom(*a, **k):
        raise AssertionError("must not backtest with zero generations")
    monkeypatch.setattr(evolve, "run_backtest", boom)

    ev = Evaluator(data={"X": []})
    result = boldness_scan(Genome(), ev, generations=0, boldness_cap=5.0)

    for arm in ("uncapped", "capped"):
        assert result[arm]["best_fold_fitness_per_gen"] == []
        assert result[arm]["shadow_promotions"] == 0
