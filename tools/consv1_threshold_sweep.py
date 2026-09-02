"""Grid search over `consult_conservative`'s `rsi_buy_below`/`z_buy_below`
thresholds ("consv1") on top of the *bare* x6-scaled seed -- default
`risk.trailing_stop` (-0.15), no ramp genes -- against the real fold-based
promotion gate.

AGENTS.md item 2's 2026-09-02 ~09:47-10:10 UTC session ruled out the SCALE
constant as fold 1's cause (scale 4/6/8 all hard-fail) and named the
remaining untried half of "reconsider the base recipe": the `consv1`
consult-tightening thresholds themselves, which every session since
2026-08-31 has only ever measured stacked with a tightened `trailing_stop`
(and, later, cold-start-ramp genes) -- never in isolation, so it has never
been possible to tell how much of the `consv1 + trailing_stop` synergy the
22:07 UTC session found is `consv1` doing real work vs. `trailing_stop`
carrying it.

Evaluates every grid point with the exact real functions
`EvolutionRun.generation()` calls before `accepts()`'s hard-fail check
(`Evaluator.evaluate()` + `dd_corrected_stats()`), same discipline as
`tools/cold_start_ramp_sweep.py`.

Not wired into any scheduled command, the bundle, or run_from_files.py.
Read-only: builds genomes and runs `Evaluator.evaluate()` (walk-forward
`run_backtest` calls) plus one continuous-replay call per point, never
touches `live_state.json`, never calls `evolve`/`tick`/`save`.

Usage:
    python3 tools/consv1_threshold_sweep.py [--years 4.0] [--refresh] [--scale 6]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from constitution import fitness  # noqa: E402
from core.market import load_universe  # noqa: E402
from loop.evolve import Evaluator, dd_corrected_stats  # noqa: E402
from tools.shadow_4h_x6_seed import SCALE, build_x6_scaled_seed  # noqa: E402

# core/genome.py's untightened defaults are the no-op point in each grid
# (rsi_buy_below=38.0, z_buy_below=-0.8); the 2026-08-31 22:07 UTC session's
# tightened point (30.0, -1.2) is included so this sweep's (30.0, -1.2) row
# is directly comparable to that session's number -- the only difference
# here is no `trailing_stop` tightening on top of it. The third point on
# each axis goes further than that session ever tried, in case a more
# aggressive threshold (untried because trailing_stop was always assumed to
# be doing the heavy lifting) clears the gate on its own.
RSI_BUY_BELOW_GRID = (38.0, 30.0, 22.0)
Z_BUY_BELOW_GRID = (-0.8, -1.2, -1.6)


def sweep(evaluator: Evaluator, base) -> list[dict[str, Any]]:
    folds = evaluator.folds()
    rows = []
    for rsi_buy_below in RSI_BUY_BELOW_GRID:
        for z_buy_below in Z_BUY_BELOW_GRID:
            g = base.child(
                [("agents.consult_conservative.genes.rsi_buy_below", rsi_buy_below),
                 ("agents.consult_conservative.genes.z_buy_below", z_buy_below)],
                note=f"consv1-only sweep point rsi={rsi_buy_below}/z={z_buy_below} "
                     f"(no trailing_stop tightening, no ramp)")
            ev = evaluator.evaluate(g, folds=folds)
            gate_stats = dd_corrected_stats(evaluator, g, ev["stats"], folds=folds)
            gate_fitness = fitness(gate_stats)
            fold_dds = [f["stats"]["max_dd"] if "stats" in f else None for f in ev["folds"]]
            rows.append({
                "rsi_buy_below": rsi_buy_below,
                "z_buy_below": z_buy_below,
                "aggregate_fitness": ev["aggregate_fitness"],
                "gate_max_dd": gate_stats["max_dd"],
                "gate_fitness": gate_fitness,
                "clears_hard_fail": gate_fitness != float("-inf"),
                "fold_max_dds": fold_dds,
                "trades": gate_stats.get("trades"),
                "sortino": gate_stats.get("sortino"),
            })
    return rows


def print_report(rows: list[dict[str, Any]]) -> None:
    print(f"{'rsi_buy_below':>13} {'z_buy_below':>11} {'agg_fit':>9} {'gate_dd':>9} "
          f"{'clears':>7} {'trades':>7} {'sortino':>8}  fold_max_dds")
    for r in sorted(rows, key=lambda r: (-r["clears_hard_fail"], -r["aggregate_fitness"])):
        dds = "/".join(f"{d:.1%}" if d is not None else "err" for d in r["fold_max_dds"])
        print(f"{r['rsi_buy_below']:>13.1f} {r['z_buy_below']:>11.1f} "
              f"{r['aggregate_fitness']:>9.3f} {r['gate_max_dd']:>9.1%} "
              f"{str(r['clears_hard_fail']):>7} {r['trades']:>7} "
              f"{r['sortino']:>8.2f}  {dds}")
    clearing = [r for r in rows if r["clears_hard_fail"]]
    if clearing:
        best = max(clearing, key=lambda r: r["aggregate_fitness"])
        print(f"\nBest among {len(clearing)}/{len(rows)} points clearing MAX_DD_HARD_FAIL: "
              f"rsi_buy_below={best['rsi_buy_below']} z_buy_below={best['z_buy_below']} "
              f"aggregate_fitness={best['aggregate_fitness']:.3f}")
    else:
        print("\nNo grid point clears MAX_DD_HARD_FAIL.")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--bar-interval", default="4h")
    ap.add_argument("--years", type=float, default=4.0)
    ap.add_argument("--refresh", action="store_true", help="force a clean re-fetch")
    ap.add_argument("--scale", type=int, default=SCALE,
                    help="period-length gene multiplier passed to build_x6_scaled_seed "
                         "(default 6, holds the settled SCALE choice fixed per "
                         "AGENTS.md item 2, option (2b)(ii))")
    args = ap.parse_args()

    base = build_x6_scaled_seed(args.bar_interval, scale=args.scale)
    data = load_universe(base.universe, interval=base.bar_interval,
                         years=args.years, refresh=args.refresh)
    evaluator = Evaluator(data)
    rows = sweep(evaluator, base)
    print_report(rows)


if __name__ == "__main__":
    main()
