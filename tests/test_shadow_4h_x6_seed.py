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
    SCALE,
    X6_ANALYST_GENES,
    X6_RISK_GENES,
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
