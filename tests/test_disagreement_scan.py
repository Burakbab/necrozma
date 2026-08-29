"""loop.evolve.disagreement_scan -- formalises the fitness-vs-excess-return
disagreement check four separate throwaway shadow scripts ran by hand on
2026-08-29 (see AGENTS.md "Current state" 06:00/10:17/16:28/19:12 entries)
into one reusable, tested function. Fully hermetic: fakes `run_backtest` and
`Researcher.propose`/`.key` so no market data or real search is needed."""
from dataclasses import dataclass

import pytest

from core.genome import Genome
from core.types import Mutation
from loop.evolve import Evaluator, disagreement_scan


HOLDOUT_WINDOW = Evaluator(data={}).holdout  # (0.85, 1.0) at default HOLDOUT_FRAC


def _stats(sortino):
    return {"sortino": sortino, "trades": 50, "bars": 200, "max_dd": -0.1,
            "turnover_annual": 1.0, "win_rate": 0.5, "total_return": 0.1,
            "halt_count": 0}


@dataclass
class _FakeResearcher:
    """Returns a fixed mutation batch once, then nothing -- enough to drive
    exactly one real `disagreement_scan` generation deterministically."""
    batches: list

    def __post_init__(self):
        self._calls = 0

    def propose(self, g, diag, n_blind=14, exclude=(), boldness=0.0):
        if self._calls >= len(self.batches):
            return []
        batch = self.batches[self._calls]
        self._calls += 1
        return batch

    @staticmethod
    def key(m):
        return (m.kind, m.target, tuple(sorted(m.patch.items())))


def _make_backtest(table):
    """table: {(note, "fold"|"holdout"): (sortino, excess_return)}"""
    def fake_backtest(g, data, a, b, log_detail=False):
        if log_detail:
            return {"closed_trades": [], "stats": {}}
        note = g.data.get("note", "")
        stage = "holdout" if (round(a, 6), round(b, 6)) == HOLDOUT_WINDOW else "fold"
        sortino, excess = table[(note, stage)]
        return {"stats": _stats(sortino), "fitness": sortino,
                "benchmark": {}, "edge": {"excess_return": excess,
                                          "beat_benchmark": excess > 0}}
    return fake_backtest


def _champion(note="champion"):
    g = Genome()
    g.data["note"] = note
    return g


def test_fold_and_holdout_disagreement_tallied_and_never_persists(monkeypatch):
    import loop.evolve as evolve

    champ = _champion()
    mutations = [
        Mutation(kind="tune", target="x", patch={"a": 1}, hypothesis="risky"),
        Mutation(kind="tune", target="x", patch={"a": 2}, hypothesis="conservative"),
        Mutation(kind="tune", target="x", patch={"a": 3}, hypothesis="agree"),
    ]
    researcher = _FakeResearcher(batches=[mutations])

    table = {
        ("champion", "fold"): (1.0, 0.05),
        ("champion", "holdout"): (0.5, 0.05),
        # fold stage: fitness says better, excess says worse -> "risky"
        ("risky", "fold"): (1.5, 0.01),
        # fold stage: fitness says worse, excess says better -> "conservative"
        # (fails the fold accept() gate outright, so it never reaches holdout)
        ("conservative", "fold"): (0.9, 0.10),
        # fold stage: both say better -> "agree"; clears the fold gate
        ("agree", "fold"): (1.5, 0.10),
        # holdout stage for "risky" (clears fold gate, fails holdout_accepts):
        # fitness says worse, excess says better -> "conservative"
        ("risky", "holdout"): (0.3, 0.10),
        # holdout stage for "agree": clears the (huge, HOLDOUT_SIGMA-scaled)
        # margin outright -> promotes; both metrics say better -> "agree"
        ("agree", "holdout"): (3.5, 0.10),
    }
    monkeypatch.setattr(evolve, "run_backtest", _make_backtest(table))
    # Never persist anything to disk, no matter what the scan does internally.
    monkeypatch.setattr(Genome, "promote",
                        lambda self: (_ for _ in ()).throw(
                            AssertionError("disagreement_scan must never promote")))
    monkeypatch.setattr(Genome, "save",
                        lambda self, tag=None: (_ for _ in ()).throw(
                            AssertionError("disagreement_scan must never save")))

    ev = Evaluator(data={"X": []})
    result = disagreement_scan(champ, ev, researcher, generations=1, n_blind=14)

    assert result["fold_stage"] == {
        "n": 3, "disagreements": 2, "disagreement_rate": pytest.approx(2 / 3),
        "risky": 1, "conservative": 1,
    }
    assert result["holdout_stage"] == {
        "n": 2, "disagreements": 1, "disagreement_rate": pytest.approx(0.5),
        "risky": 0, "conservative": 1,
    }
    assert result["shadow_promotions"] == 1
    assert result["final_champion_version"] == champ.version + 1
    assert result["final_holdout_draws"] == 2
    assert result["generations_run"] == 1


def test_no_proposals_yields_empty_tallies_and_bumps_stagnation(monkeypatch):
    import loop.evolve as evolve

    monkeypatch.setattr(evolve, "run_backtest",
                        lambda g, data, a, b, log_detail=False:
                        {"closed_trades": [], "stats": _stats(1.0),
                         "fitness": 1.0, "benchmark": {},
                         "edge": {"excess_return": 0.05, "beat_benchmark": True}})
    researcher = _FakeResearcher(batches=[[]])
    ev = Evaluator(data={"X": []})
    result = disagreement_scan(_champion(), ev, researcher, generations=1)

    assert result["fold_stage"] == {"n": 0, "disagreements": 0,
                                    "disagreement_rate": None, "risky": 0,
                                    "conservative": 0}
    assert result["holdout_stage"] == result["fold_stage"]
    assert result["shadow_promotions"] == 0
    assert result["final_stagnation"] == 1


def test_zero_generations_is_a_no_op(monkeypatch):
    import loop.evolve as evolve

    def boom(*a, **k):
        raise AssertionError("must not backtest with zero generations")
    monkeypatch.setattr(evolve, "run_backtest", boom)
    researcher = _FakeResearcher(batches=[])
    ev = Evaluator(data={"X": []})
    result = disagreement_scan(_champion(), ev, researcher, generations=0)

    assert result["fold_stage"]["n"] == 0
    assert result["holdout_stage"]["n"] == 0
    assert result["shadow_promotions"] == 0
    assert result["final_champion_version"] == _champion().version
