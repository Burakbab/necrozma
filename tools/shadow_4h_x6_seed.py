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
    args = ap.parse_args()

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
