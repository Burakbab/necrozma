"""Grid search over `cold_start_ramp_bars` / `cold_start_ramp_start_scale`
on top of the 22:07 UTC session's `consv1 + trailing_stop` 4h-shadow genome
-- the follow-up AGENTS.md item 2 flagged after the 04:18 UTC session shipped
the two genes but hand-picked 120/0.10 from a small, unrecorded sweep ("a
real search over just those two genes ... is the natural next step").

Evaluates every grid point with the exact real functions
`EvolutionRun.generation()` calls before `accepts()`'s hard-fail check
(`Evaluator.evaluate()` + `dd_corrected_stats()`), not a continuous-replay
proxy -- same discipline the 04:18 UTC session used by hand for the single
120/0.10 point this sweeps around.

Not wired into any scheduled command, the bundle, or run_from_files.py.
Read-only: builds genomes and runs `Evaluator.evaluate()` (walk-forward
`run_backtest` calls) plus one continuous-replay call per point, never
touches `live_state.json`, never calls `evolve`/`tick`/`save`.

Usage:
    python3 tools/cold_start_ramp_sweep.py [--years 4.0] [--refresh]
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
from tools.shadow_4h_x6_seed import build_consv_trailing_seed  # noqa: E402

# The grid this sweep covers. Centered on the 04:18 UTC session's hand-picked
# 120/0.10 point, with (0, 1.0) included as the exact no-op baseline (the
# genome the 01:14 UTC session found hard-failing) so the sweep reproduces
# that session's own baseline number as an internal consistency check.
RAMP_BARS_GRID = (0, 60, 90, 120, 150, 180, 240)
START_SCALE_GRID = (1.0, 0.30, 0.20, 0.10, 0.05, 0.0)


def sweep(evaluator: Evaluator, base) -> list[dict[str, Any]]:
    folds = evaluator.folds()
    rows = []
    for ramp_bars in RAMP_BARS_GRID:
        for start_scale in START_SCALE_GRID:
            if ramp_bars == 0 and start_scale != 1.0:
                continue  # ramp_bars=0 is a no-op regardless of scale -- skip duplicates
            g = base.child(
                [("agents.risk_judge.genes.cold_start_ramp_bars", ramp_bars),
                 ("agents.risk_judge.genes.cold_start_ramp_start_scale", start_scale)],
                note=f"cold_start_ramp sweep point {ramp_bars}/{start_scale}")
            ev = evaluator.evaluate(g, folds=folds)
            gate_stats = dd_corrected_stats(evaluator, g, ev["stats"], folds=folds)
            gate_fitness = fitness(gate_stats)
            fold_dds = [f["stats"]["max_dd"] if "stats" in f else None for f in ev["folds"]]
            rows.append({
                "ramp_bars": ramp_bars,
                "start_scale": start_scale,
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
    print(f"{'ramp_bars':>10} {'scale':>6} {'agg_fit':>9} {'gate_dd':>9} "
          f"{'clears':>7} {'trades':>7} {'sortino':>8}  fold_max_dds")
    for r in sorted(rows, key=lambda r: (-r["clears_hard_fail"], -r["aggregate_fitness"])):
        dds = "/".join(f"{d:.1%}" if d is not None else "err" for d in r["fold_max_dds"])
        print(f"{r['ramp_bars']:>10d} {r['start_scale']:>6.2f} "
              f"{r['aggregate_fitness']:>9.3f} {r['gate_max_dd']:>9.1%} "
              f"{str(r['clears_hard_fail']):>7} {r['trades']:>7} "
              f"{r['sortino']:>8.2f}  {dds}")
    clearing = [r for r in rows if r["clears_hard_fail"]]
    if clearing:
        best = max(clearing, key=lambda r: r["aggregate_fitness"])
        print(f"\nBest among {len(clearing)}/{len(rows)} points clearing MAX_DD_HARD_FAIL: "
              f"ramp_bars={best['ramp_bars']} start_scale={best['start_scale']} "
              f"aggregate_fitness={best['aggregate_fitness']:.3f}")
    else:
        print("\nNo grid point clears MAX_DD_HARD_FAIL.")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--bar-interval", default="4h")
    ap.add_argument("--years", type=float, default=4.0)
    ap.add_argument("--refresh", action="store_true", help="force a clean re-fetch")
    ap.add_argument("--trailing-stop", type=float, default=-0.06)
    args = ap.parse_args()

    base = build_consv_trailing_seed(args.bar_interval, args.trailing_stop)
    data = load_universe(base.universe, interval=base.bar_interval,
                         years=args.years, refresh=args.refresh)
    evaluator = Evaluator(data)
    rows = sweep(evaluator, base)
    print_report(rows)


if __name__ == "__main__":
    main()
