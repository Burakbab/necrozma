import math
import os

import pytest

import constitution as c


def _stats(**overrides):
    base = {"trades": 40, "bars": 200, "max_dd": -0.10, "sortino": 1.0,
            "turnover_annual": 20.0}
    base.update(overrides)
    return base


def test_fitness_rejects_error():
    assert c.fitness({"error": "no market data"}) == float("-inf")


def test_fitness_rejects_too_few_trades():
    assert c.fitness(_stats(trades=c.MIN_TRADES - 1)) == float("-inf")


def test_fitness_rejects_too_few_bars():
    assert c.fitness(_stats(bars=c.MIN_BARS - 1)) == float("-inf")


def test_fitness_rejects_drawdown_over_hard_fail():
    assert c.fitness(_stats(max_dd=-(c.MAX_DD_HARD_FAIL + 0.01))) == float("-inf")


def test_fitness_penalises_drawdown_beyond_free_allowance():
    small_dd = c.fitness(_stats(max_dd=-0.05))
    big_dd = c.fitness(_stats(max_dd=-0.35))
    assert big_dd < small_dd


def test_fitness_penalises_turnover_beyond_free_threshold():
    low_turn = c.fitness(_stats(turnover_annual=10.0))
    high_turn = c.fitness(_stats(turnover_annual=500.0))
    assert high_turn < low_turn


def test_ranking_fitness_floors_instead_of_minus_inf():
    assert c.fitness(_stats(trades=0)) == float("-inf")
    assert c.ranking_fitness(_stats(trades=0)) == c.RANK_FLOOR


def test_ranking_fitness_never_below_floor_even_if_worse_than_floor():
    # a pathological sortino more negative than RANK_FLOOR must still clip
    assert c.ranking_fitness(_stats(sortino=-50.0)) == c.RANK_FLOOR


def test_required_margin_grows_with_more_candidates():
    m1 = c.required_margin(1, 0)
    m50 = c.required_margin(50, 0)
    m500 = c.required_margin(500, 0)
    assert m1 < m50 < m500


def test_required_margin_grows_with_complexity():
    plain = c.required_margin(10, 0)
    complex_ = c.required_margin(10, 4)
    assert complex_ > plain
    assert complex_ - plain == pytest.approx(c.COMPLEXITY_COST_PER_UNIT * 4)


def test_accepts_rejects_challenger_hard_gate_failure():
    champ = _stats()
    chal = _stats(trades=1)  # fails MIN_TRADES -> fitness -inf
    ok, why = c.accepts(champ, chal, n_candidates=1)
    assert not ok
    assert "hard gate" in why


def test_accepts_rejects_when_margin_not_cleared():
    champ = _stats(sortino=1.0)
    chal = _stats(sortino=1.001)  # trivially better, not enough to clear the margin
    ok, why = c.accepts(champ, chal, n_candidates=100)
    assert not ok
    assert "required margin" in why


def test_accepts_rejects_merged_regression_even_if_selection_score_clears():
    champ = _stats(sortino=1.0)
    chal = _stats(sortino=0.5)  # worse merged fitness
    # selection scores lie and say the challenger is much better
    ok, why = c.accepts(champ, chal, n_candidates=1,
                         champion_score=0.0, challenger_score=10.0)
    assert not ok
    assert "merged fitness regressed" in why


def test_accepts_rejects_drawdown_regression():
    champ = _stats(max_dd=-0.10, sortino=1.0)
    chal = _stats(max_dd=-0.30, sortino=5.0)  # way better sortino, way worse dd
    ok, why = c.accepts(champ, chal, n_candidates=1,
                         champion_score=0.0, challenger_score=10.0)
    assert not ok
    assert "drawdown regression" in why


def test_accepts_true_when_everything_clears():
    champ = _stats(sortino=1.0, max_dd=-0.10)
    chal = _stats(sortino=5.0, max_dd=-0.10)
    ok, why = c.accepts(champ, chal, n_candidates=1,
                         champion_score=0.0, challenger_score=10.0)
    assert ok


def test_holdout_accepts_rejects_nonfinite_challenger():
    ok, why = c.holdout_accepts(1.0, float("-inf"))
    assert not ok


def test_holdout_accepts_true_when_champion_has_no_finite_score():
    ok, why = c.holdout_accepts(float("-inf"), 0.5)
    assert ok
    assert "no finite holdout fitness to beat" in why


def test_holdout_accepts_margin_scales_with_cumulative_draws():
    # a fixed edge that clears the margin at 1 draw may not clear it after
    # many cumulative draws against the same holdout
    edge = c.required_margin(1, 0, sigma=c.HOLDOUT_SIGMA) + 0.01
    ok_early, _ = c.holdout_accepts(0.0, edge, n_draws=1)
    ok_late, _ = c.holdout_accepts(0.0, edge, n_draws=100)
    assert ok_early
    assert not ok_late


def test_required_margin_defaults_to_multiple_testing_sigma():
    assert c.required_margin(10, 0) == pytest.approx(
        c.MULTIPLE_TESTING_SIGMA * math.sqrt(2.0 * math.log(10)))


def test_required_margin_accepts_a_sigma_override():
    default = c.required_margin(10, 0)
    overridden = c.required_margin(10, 0, sigma=c.HOLDOUT_SIGMA)
    assert overridden == pytest.approx(
        c.HOLDOUT_SIGMA * math.sqrt(2.0 * math.log(10)))
    assert overridden > default  # HOLDOUT_SIGMA > MULTIPLE_TESTING_SIGMA


def test_holdout_accepts_uses_holdout_sigma_not_multiple_testing_sigma():
    # an edge that would clear the fold-aggregate margin (MULTIPLE_TESTING_SIGMA)
    # must not automatically clear the sealed-holdout margin (HOLDOUT_SIGMA),
    # since the two are now different constants.
    fold_margin = c.required_margin(20, 0)  # uses MULTIPLE_TESTING_SIGMA
    holdout_margin = c.required_margin(20, 0, sigma=c.HOLDOUT_SIGMA)
    assert holdout_margin > fold_margin
    edge_between = fold_margin + 0.01
    assert edge_between < holdout_margin
    ok, why = c.holdout_accepts(0.0, edge_between, n_draws=20)
    assert not ok
    assert f"margin {holdout_margin:.3f}" in why


def test_checksum_seals_on_first_call_and_detects_tamper(tmp_path):
    manifest = str(tmp_path / "MANIFEST")
    c.EMBEDDED_SOURCES.clear()
    c.EMBEDDED_SOURCES.update({"constitution": "abc", "core.portfolio": "def"})
    try:
        ok, msg = c.verify(manifest)
        assert ok
        assert "sealed" in msg
        assert os.path.exists(manifest)

        # unchanged -> still verifies
        ok2, msg2 = c.verify(manifest)
        assert ok2
        assert "verified" in msg2

        # tamper with either embedded source -> must be caught
        c.EMBEDDED_SOURCES["constitution"] = "abc-tampered"
        ok3, msg3 = c.verify(manifest)
        assert not ok3
        assert "CONSTITUTION MODIFIED" in msg3
    finally:
        c.EMBEDDED_SOURCES.clear()
