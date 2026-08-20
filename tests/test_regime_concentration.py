"""loop.evolve.regime_concentration -- quantifies how concentrated the
searchable region's compounded growth is across contiguous sub-windows, backing
the `regime-scan` diagnostic. fitness-decomp (2026-08-20) settled that
aggregate_fitness's cross-scheme instability comes from the mean of the fold
fitnesses, not the consistency penalty -- one dominant window pulling the
average. The open design question is whether a regime-stratified fold scheme is
worth the engine work, which turns on whether that dominant window is isolated
(concentration high) or diffuse (concentration ~even). This helper puts a number
on it, genome-independently (AGENTS.md item 2)."""
import math

import pytest

from loop.evolve import regime_concentration


def test_empty_input_returns_zeros():
    d = regime_concentration([])
    assert d["n_windows"] == 0
    assert d["shares"] == []
    assert d["hhi"] == 0.0
    assert d["top_index"] == -1
    assert d["concentration_ratio"] == 0.0


def test_shares_sum_to_one():
    for rets in ([0.1, -0.2, 0.3], [1.0, 0.5, -0.4, 0.2, -0.1],
                 [0.02] * 7, [-0.3, 0.9]):
        d = regime_concentration(rets)
        assert sum(d["shares"]) == pytest.approx(1.0, abs=1e-12)


def test_perfectly_even_growth_has_ratio_one():
    # equal-magnitude log-returns -> every window carries its even share.
    d = regime_concentration([0.25, 0.25, 0.25, 0.25])
    assert d["concentration_ratio"] == pytest.approx(1.0)
    assert d["hhi"] == pytest.approx(0.25)          # 1/n for n=4
    assert d["even_share"] == pytest.approx(0.25)
    assert d["top_share"] == pytest.approx(0.25)


def test_single_window_is_fully_concentrated():
    d = regime_concentration([0.5])
    assert d["n_windows"] == 1
    assert d["top_index"] == 0
    assert d["top_share"] == pytest.approx(1.0)
    assert d["hhi"] == pytest.approx(1.0)
    assert d["concentration_ratio"] == pytest.approx(1.0)   # top_share * n = 1


def test_dominant_window_raises_concentration():
    # one melt-up dwarfing three quiet windows.
    d = regime_concentration([0.02, 0.02, 1.5, 0.02])
    assert d["top_index"] == 2
    assert d["top_return"] == pytest.approx(1.5)
    assert d["concentration_ratio"] > 1.0
    assert d["top_share"] > d["even_share"]
    assert d["hhi"] > 0.25                                   # above the even 1/4


def test_absolute_value_counts_crashes_as_contributions():
    # a deep crash is as much a dominant single window as a melt-up: the
    # |log-return| share must pick it out, not cancel it against the gains.
    d = regime_concentration([0.05, 0.05, -0.6, 0.05])
    assert d["top_index"] == 2
    assert d["top_return"] == pytest.approx(-0.6)
    assert d["concentration_ratio"] > 1.0


def test_total_return_compounds_windows():
    rets = [0.1, -0.2, 0.3, 0.05]
    d = regime_concentration(rets)
    compounded = 1.0
    for r in rets:
        compounded *= (1.0 + r)
    assert d["total_return"] == pytest.approx(compounded - 1.0, abs=1e-12)
    assert d["total_log_growth"] == pytest.approx(
        sum(math.log(1.0 + r) for r in rets), abs=1e-12)


def test_ratio_matches_top_share_times_n():
    d = regime_concentration([0.5, 0.1, 0.9, -0.2, 0.3])
    assert d["concentration_ratio"] == pytest.approx(
        d["top_share"] * d["n_windows"])
