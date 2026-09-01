"""Reusable (never scheduled) scratch harness for the 4h-shadow "x6-scaled
seed" recipe that every 4h-shadow session since 2026-08-16 has hand-built ad
hoc in an uncommitted scratch script (see AGENTS.md item 2's history).

The 2026-08-31 10:02 UTC session found its own baseline for this exact
recipe (392.7 trades/yr, -44.3% max_dd) didn't reproduce the 07:05 UTC
session's baseline (1278 trades/yr, -66.1% max_dd) for what should be the
identical genome, and had no committed script from either session to diff
against. This module is the fix: one place the recipe is defined, so a
future session's baseline is diffable against a prior one instead of
reconstructed from a run note's prose description each time.

Not wired into any scheduled command, the bundle, or run_from_files.py.
Read-only: builds a genome and runs `loop.engine.run_backtest` once, never
touches `live_state.json`, never calls `evolve`/`tick`/`save`.

Usage:
    python3 tools/shadow_4h_x6_seed.py [--years 4.0] [--refresh] [--warmup 60]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.genome import Genome  # noqa: E402
from core.market import BARS_PER_YEAR, load_universe  # noqa: E402
from loop.engine import run_backtest  # noqa: E402

# The period-length genes the x6-scaling recipe multiplies -- everything
# expressed in *bars* rather than wall-clock time, so switching bar_interval
# without scaling these changes what they mean (see core/genome.py's own
# comment on SEED_GENOME["bar_interval"]).
X6_ANALYST_GENES = ("trend_fast", "trend_slow", "rsi_len", "vol_short", "vol_long",
                    "breakout_len", "z_len", "regime_ma", "volume_len")
X6_RISK_GENES = ("max_bars_held", "min_bars_held")
SCALE = 6

BAR_HOURS = {"1h": 1, "4h": 4, "1d": 24}


def build_x6_scaled_seed(bar_interval: str = "4h") -> Genome:
    """The seed genome, switched to `bar_interval` with every period-length
    gene multiplied by SCALE. Matches the recipe documented in AGENTS.md item
    2 (2026-08-16 onward) exactly -- deliberately NOT re-tuned, just rescaled,
    so the drawdown/overtrading behavior measured here is attributable to the
    bar-size switch alone, not to any other change."""
    seed = Genome()
    patches: list[tuple[str, Any]] = [("bar_interval", bar_interval)]
    for gene in X6_ANALYST_GENES:
        patches.append((f"agents.analyst.genes.{gene}", seed.gene("analyst", gene) * SCALE))
    for gene in X6_RISK_GENES:
        patches.append((f"risk.{gene}", seed.risk[gene] * SCALE))
    return seed.child(patches, note=f"x6-scaled seed for {bar_interval} shadow evolution")


# The 2026-08-31 22:07 UTC session's headline finding on top of the x6-scaled
# seed: consult_conservative tightening (rsi_buy_below 38->30, z_buy_below
# -0.8->-1.2, "consv1") stacked with a tightened trailing stop is strongly
# super-additive on max_dd -- neither lever alone clears MAX_DD_HARD_FAIL on
# this seed, but combined they do (see AGENTS.md item 2 and
# runs/2026-08-31-2207-4h-shadow-consv-trailing-synergy-clears-dd-gate.md for
# the full sweep). -0.06 is that session's best risk-adjusted variant.
CONSV1_PATCH: list[tuple[str, Any]] = [
    ("agents.consult_conservative.genes.rsi_buy_below", 30.0),
    ("agents.consult_conservative.genes.z_buy_below", -1.2),
]
DEFAULT_TRAILING_STOP = -0.06


def build_consv_trailing_seed(bar_interval: str = "4h",
                              trailing_stop: float = DEFAULT_TRAILING_STOP) -> Genome:
    """`build_x6_scaled_seed()` plus the 22:07 UTC session's `consv1 +
    trailing_stop` combination -- the first variant in this whole 4h-shadow
    thread (since 2026-08-16) to clear `MAX_DD_HARD_FAIL` on a single
    full-history backtest. That measurement was never run through the real
    promotion pipeline (fold-aggregate acceptance + sealed holdout); this
    builder exists so a future session can seed a fresh `EvolutionRun` from
    it instead of re-deriving the patch from the run note's prose."""
    base = build_x6_scaled_seed(bar_interval)
    patches = list(CONSV1_PATCH) + [("risk.trailing_stop", trailing_stop)]
    return base.child(patches, note=f"consv1 + trailing_stop {trailing_stop} on x6-scaled "
                                    f"{bar_interval} seed (2026-08-31 22:07 UTC finding)")


# The 2026-09-01 01:14 UTC session found the 22:07 UTC session's genome above
# fails the REAL fold-based promotion gate (-44.1% max_dd on fold
# [0.283, 0.567]'s own from-cold-start replay, vs. the -32.7% a single
# continuous full-history backtest reports) -- a genuine cold-start artifact,
# not a data-window bug: the fold restarts the broker from empty/full-cash,
# and a fresh restart sizes into that fold's downturn at full risk with none
# of the de-risking a seasoned position would already have. The same
# session's own run note flagged "does a smaller initial position size in the
# first N bars of a fold fix it?" as the natural follow-up. It does: the new
# `risk_judge.cold_start_ramp_bars`/`cold_start_ramp_start_scale` genes
# (shipped 2026-09-01 04:18 UTC, see AGENTS.md item 2) at 120 bars / 0.10x
# take that same fold from -44.1% (still hard-failing) to -34.6% (clears
# MAX_DD_HARD_FAIL). A same-session follow-up grid-searched both genes
# (`tools/cold_start_ramp_sweep.py`, 37 points) and found 120 bars / 0.20x
# strictly better on the identical real gate: same -34.6% gate max_dd,
# aggregate_fitness 0.454 vs 120/0.10's 0.368, holdout still beats benchmark
# either way -- this is now the recommended point, not the original hand
# pick. Verified via the real gene (Genome.child() patch, not a monkeypatch)
# against real 4h Binance data.
COLD_START_RAMP_PATCH: list[tuple[str, Any]] = [
    ("agents.risk_judge.genes.cold_start_ramp_bars", 120),
    ("agents.risk_judge.genes.cold_start_ramp_start_scale", 0.20),
]


def build_consv_trailing_ramp_seed(bar_interval: str = "4h",
                                   trailing_stop: float = DEFAULT_TRAILING_STOP) -> Genome:
    """`build_consv_trailing_seed()` plus the 2026-09-01 cold-start-ramp fix
    that clears `MAX_DD_HARD_FAIL` on the real fold-based gate (see
    `COLD_START_RAMP_PATCH`'s docstring) -- this thread's first genome to
    clear that gate on the gate itself, not just a continuous replay. Exists
    so a future session seeding a fresh `EvolutionRun` from it reproduces the
    exact recipe instead of re-deriving it from a run note."""
    base = build_consv_trailing_seed(bar_interval, trailing_stop)
    return base.child(COLD_START_RAMP_PATCH,
                      note="cold_start_ramp 120/0.20 on consv1 + trailing_stop "
                           f"{trailing_stop} (2026-09-01 fold-gate fix, "
                           "grid-search-refined)")


def summarize(result: dict[str, Any], bar_interval: str) -> dict[str, Any]:
    """The subset of `run_backtest`'s output every 4h-shadow run note has
    reported, in one place instead of re-picked-apart by hand each session."""
    stats = result["stats"]
    hours_per_bar = BAR_HOURS.get(bar_interval, 24)
    return {
        "trades_per_year": result["edge"]["trades_per_year"],
        "avg_days_held": stats["avg_bars_held"] * hours_per_bar / 24.0,
        "win_rate": stats["win_rate"],
        "halt_count": stats["halt_count"],
        "max_dd": stats["max_dd"],
        "sortino": stats["sortino"],
        "sharpe": stats["sharpe"],
        "fitness": result["fitness"],
    }


def print_report(summary: dict[str, Any]) -> None:
    print(f"{'trades/yr':>12} {'avg days held':>14} {'win rate':>9} {'halts':>6} "
          f"{'max_dd':>8} {'sortino':>8} {'sharpe':>8} {'fitness':>8}")
    print(f"{summary['trades_per_year']:>12.1f} {summary['avg_days_held']:>14.2f} "
          f"{summary['win_rate']:>9.1%} {summary['halt_count']:>6d} "
          f"{summary['max_dd']:>8.1%} {summary['sortino']:>8.2f} "
          f"{summary['sharpe']:>8.2f} {summary['fitness']:>8.3f}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--bar-interval", default="4h")
    ap.add_argument("--years", type=float, default=4.0)
    ap.add_argument("--refresh", action="store_true", help="force a clean re-fetch")
    ap.add_argument("--warmup", type=int, default=60)
    ap.add_argument("--recipe", choices=("x6", "consv_trailing", "consv_trailing_ramp"),
                    default="x6",
                    help="x6: plain x6-scaled seed. consv_trailing: x6-scaled seed "
                         "plus the 22:07 UTC session's consv1 + trailing_stop patch. "
                         "consv_trailing_ramp: consv_trailing plus the 2026-09-01 "
                         "cold-start-ramp fix that clears MAX_DD_HARD_FAIL on the "
                         "real fold-based gate.")
    args = ap.parse_args()

    if args.recipe == "consv_trailing_ramp":
        genome = build_consv_trailing_ramp_seed(args.bar_interval)
    elif args.recipe == "consv_trailing":
        genome = build_consv_trailing_seed(args.bar_interval)
    else:
        genome = build_x6_scaled_seed(args.bar_interval)
    data = load_universe(genome.universe, interval=genome.bar_interval,
                         years=args.years, refresh=args.refresh)
    result = run_backtest(genome, data, start_frac=0.0, end_frac=1.0,
                          log_detail=False, warmup=args.warmup)
    if "error" in result:
        print(f"[shadow_4h_x6_seed] {result['error']}")
        return
    print_report(summarize(result, args.bar_interval))


if __name__ == "__main__":
    main()
