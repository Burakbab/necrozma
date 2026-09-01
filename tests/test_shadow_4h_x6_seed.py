"""Hermetic tests for tools/shadow_4h_x6_seed.py -- the x6-scaling recipe
itself, no network/market data involved (see AGENTS.md item 2, 2026-08-31
10:02 UTC session, for why this script exists)."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.genome import Genome
from tools.shadow_4h_x6_seed import (
    BAR_HOURS,
    DEFAULT_TRAILING_STOP,
    SCALE,
    X6_ANALYST_GENES,
    X6_RISK_GENES,
    build_consv_trailing_ramp_seed,
    build_consv_trailing_seed,
    build_x6_scaled_seed,
    summarize,
)


def test_x6_scaled_seed_sets_bar_interval():
    g = build_x6_scaled_seed("4h")
    assert g.bar_interval == "4h"


def test_x6_scaled_seed_multiplies_every_period_gene_by_six():
    seed = Genome()
    scaled = build_x6_scaled_seed("4h")
    for gene in X6_ANALYST_GENES:
        assert scaled.gene("analyst", gene) == seed.gene("analyst", gene) * SCALE
    for gene in X6_RISK_GENES:
        assert scaled.risk[gene] == seed.risk[gene] * SCALE


def test_x6_scaled_seed_leaves_non_period_genes_untouched():
    seed = Genome()
    scaled = build_x6_scaled_seed("4h")
    assert scaled.gene("analyst", "regime_anchor") == seed.gene("analyst", "regime_anchor")
    assert scaled.gene("consult_risky", "min_rank_mom") == seed.gene("consult_risky", "min_rank_mom")
    assert scaled.risk["stop_loss"] == seed.risk["stop_loss"]


def test_x6_scaled_seed_is_a_child_not_a_mutation_of_the_seed():
    seed = Genome()
    scaled = build_x6_scaled_seed("4h")
    assert scaled.version == seed.version + 1
    assert seed.bar_interval == "1d"
    assert seed.gene("analyst", "trend_fast") == 10


def test_x6_scaled_seed_default_bar_interval_is_4h():
    g = build_x6_scaled_seed()
    assert g.bar_interval == "4h"


@pytest.mark.parametrize("interval,bars_held,expected_days", [
    ("4h", 6.0, 1.0),
    ("1d", 1.0, 1.0),
    ("1h", 24.0, 1.0),
])
def test_summarize_converts_bars_held_to_days_by_interval(interval, bars_held, expected_days):
    result = {
        "stats": {"avg_bars_held": bars_held, "win_rate": 0.5, "halt_count": 0,
                  "max_dd": -0.1, "sortino": 1.0, "sharpe": 1.0},
        "edge": {"trades_per_year": 100.0},
        "fitness": 0.5,
    }
    summary = summarize(result, interval)
    assert summary["avg_days_held"] == pytest.approx(expected_days)


def test_bar_hours_covers_every_supported_interval():
    assert set(BAR_HOURS) == {"1h", "4h", "1d"}


def test_consv_trailing_seed_applies_consv1_and_trailing_stop_on_top_of_x6():
    x6 = build_x6_scaled_seed("4h")
    seed = build_consv_trailing_seed("4h")
    assert seed.gene("consult_conservative", "rsi_buy_below") == 30.0
    assert seed.gene("consult_conservative", "z_buy_below") == -1.2
    assert seed.risk["trailing_stop"] == DEFAULT_TRAILING_STOP
    # everything x6 already touched is untouched by this extra patch
    for gene in X6_ANALYST_GENES:
        assert seed.gene("analyst", gene) == x6.gene("analyst", gene)
    for gene in X6_RISK_GENES:
        assert seed.risk[gene] == x6.risk[gene]
    assert seed.bar_interval == "4h"


def test_consv_trailing_seed_is_a_child_of_the_x6_seed():
    seed = build_consv_trailing_seed("4h")
    x6 = build_x6_scaled_seed("4h")
    assert seed.version == x6.version + 1


def test_consv_trailing_seed_accepts_a_custom_trailing_stop():
    seed = build_consv_trailing_seed("4h", trailing_stop=-0.08)
    assert seed.risk["trailing_stop"] == -0.08
    # untouched genes still hold at the custom-trailing-stop call site


def test_consv_trailing_ramp_seed_applies_cold_start_ramp_on_top_of_consv_trailing():
    consv_trailing = build_consv_trailing_seed("4h")
    ramped = build_consv_trailing_ramp_seed("4h")
    assert ramped.gene("risk_judge", "cold_start_ramp_bars") == 120
    assert ramped.gene("risk_judge", "cold_start_ramp_start_scale") == 0.20
    # everything consv_trailing already set is untouched by this extra patch
    assert ramped.gene("consult_conservative", "rsi_buy_below") == \
        consv_trailing.gene("consult_conservative", "rsi_buy_below")
    assert ramped.risk["trailing_stop"] == consv_trailing.risk["trailing_stop"]
    assert ramped.bar_interval == "4h"


def test_consv_trailing_ramp_seed_is_a_child_of_consv_trailing_seed():
    ramped = build_consv_trailing_ramp_seed("4h")
    consv_trailing = build_consv_trailing_seed("4h")
    assert ramped.version == consv_trailing.version + 1


def test_consv_trailing_ramp_seed_accepts_ramp_overrides():
    ramped = build_consv_trailing_ramp_seed("4h", ramp_bars=90, ramp_start_scale=0.05)
    assert ramped.gene("risk_judge", "cold_start_ramp_bars") == 90
    assert ramped.gene("risk_judge", "cold_start_ramp_start_scale") == 0.05


def test_consv_trailing_ramp_seed_defaults_match_grid_search_pick():
    ramped = build_consv_trailing_ramp_seed("4h")
    assert ramped.gene("risk_judge", "cold_start_ramp_bars") == 120
    assert ramped.gene("risk_judge", "cold_start_ramp_start_scale") == 0.20


def test_consv_trailing_ramp_seed_conviction_boost_defaults_to_noop():
    ramped = build_consv_trailing_ramp_seed("4h")
    assert ramped.gene("risk_judge", "cold_start_ramp_min_conviction_boost") == 0.0


def test_consv_trailing_ramp_seed_accepts_conviction_boost_override():
    ramped = build_consv_trailing_ramp_seed("4h", ramp_conviction_boost=0.15)
    assert ramped.gene("risk_judge", "cold_start_ramp_min_conviction_boost") == 0.15
    # size-ramp genes stay at their own defaults, independent of this override
    assert ramped.gene("risk_judge", "cold_start_ramp_bars") == 120
    assert ramped.gene("risk_judge", "cold_start_ramp_start_scale") == 0.20
