"""Shadow equivalent of `evotrader_bundle.py fold-date-sensitivity`, generalized
from the live 1d champion to a 4h-shadow genome builder -- the "natural next
step" the 2026-09-01 10:27 UTC run note flagged and left undone after finding
that the 08:08 UTC grid search's `cold_start_ramp_bars=120,
cold_start_ramp_start_scale=0.20` recommendation flipped from clearing
`MAX_DD_HARD_FAIL` (-34.6% max_dd) to hard-failing it (-43.4%) on the exact
same genome, just because the data snapshot had one extra trailing 4h bar --
a fold-boundary-shift artifact, not a market move or a bug. That note's own
words: "before trusting any single point-in-time clears/fails
MAX_DD_HARD_FAIL measurement on this genome family again, ... build a shadow
equivalent of the existing fold-date-sensitivity CLI command ... so this can
be checked systematically instead of by two accidental same-day snapshots
landing on opposite sides."

Same mechanism as the bundled `fold-date-sensitivity` command: re-evaluates a
genome under the exact `Evaluator(data, n_folds=N_FOLDS).evaluate(genome)`
call `EvolutionRun.generation()` makes internally, at several different
"as-of" dates (today, and up to `--shift`-1 days before), each with its own
trailing 4-year window built the same way `market.load_universe` builds it
live. Adds one thing the bundled command does not need (the live champion is
always the champion; a shadow genome under test is not): at every shift, it
also computes `dd_corrected_stats()` on the fold-merged stats -- the exact
correction `EvolutionRun.generation()` applies before `accepts()`'s hard-fail
check reads `max_dd` -- and reports whether that specific genome would clear
`MAX_DD_HARD_FAIL` as champion that day, not just what its aggregate_fitness
happened to be.

Not wired into any scheduled command, the bundle, or run_from_files.py.
Read-only with respect to the live account: builds a `Genome` in memory and
calls `Evaluator.evaluate()`/`continuous_max_dd()`, both pure replay
functions -- never touches `live_state.json`, never calls
`evolve`/`tick`/`save`.

Usage:
    python3 tools/shadow_4h_fold_date_sensitivity.py [--recipe consv_trailing_ramp]
        [--bar-interval 4h] [--trailing-stop -0.06] [--shift 7] [--years 4.0]
"""
from __future__ import annotations

import argparse
import math
import sys
import time
from pathlib import Path
from typing import Any

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from constitution import HOLDOUT_FRAC, MAX_DD_HARD_FAIL, N_FOLDS  # noqa: E402
from core import market  # noqa: E402
from core.genome import Genome  # noqa: E402
from loop.evolve import Evaluator, dd_corrected_stats  # noqa: E402
from tools.shadow_4h_x6_seed import (  # noqa: E402
    build_consv_trailing_ramp_seed,
    build_consv_trailing_seed,
    build_x6_scaled_seed,
)

RECIPES = {
    "x6": build_x6_scaled_seed,
    "consv_trailing": build_consv_trailing_seed,
    "consv_trailing_ramp": build_consv_trailing_ramp_seed,
}


def build_genome(recipe: str, bar_interval: str, trailing_stop: float,
                  ramp_bars: int | None = None,
                  ramp_start_scale: float | None = None) -> Genome:
    builder = RECIPES[recipe]
    if recipe == "x6":
        return builder(bar_interval)
    if recipe == "consv_trailing_ramp":
        kwargs: dict[str, Any] = {}
        if ramp_bars is not None:
            kwargs["ramp_bars"] = ramp_bars
        if ramp_start_scale is not None:
            kwargs["ramp_start_scale"] = ramp_start_scale
        return builder(bar_interval, trailing_stop, **kwargs)
    return builder(bar_interval, trailing_stop)


def slice_window(raw: dict[str, pd.DataFrame], as_of: pd.Timestamp,
                  width: pd.Timedelta) -> dict[str, pd.DataFrame]:
    """Trailing `width` window ending at `as_of`, dropping any symbol left
    empty by the slice. Pulled out as a pure function (same slicing the
    bundled `fold-date-sensitivity` command does inline) so it is
    unit-testable against synthetic frames without a real market fetch."""
    start = as_of - width
    data = {s: df[(df.index >= start) & (df.index <= as_of)] for s, df in raw.items()}
    return {s: df for s, df in data.items() if len(df) > 0}


def gate_margin(corrected_max_dd: float) -> float:
    """Signed distance from the real gate's hard-fail cutoff: positive means
    it clears with that many points of margin, negative means it hard-fails
    by that much. `MAX_DD_HARD_FAIL` is a magnitude (0.40); `max_dd` in stats
    dicts is signed negative, hence the abs()."""
    return MAX_DD_HARD_FAIL - abs(corrected_max_dd)


def summarize_shifts(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Pure summary over a list of per-shift result dicts (each with at least
    `hard_fail: bool` and `aggregate_fitness: float`, `gate_max_dd: float`).
    No network or replay involved -- the reporting half of this tool, kept
    separate from the replay loop so it's unit-testable directly."""
    n = len(rows)
    n_hard_fail = sum(1 for r in rows if r["hard_fail"])
    clearing = [r for r in rows if not r["hard_fail"]]
    margins = [gate_margin(r["gate_max_dd"]) for r in rows
               if math.isfinite(r["gate_max_dd"])]
    finite_aggs = [r["aggregate_fitness"] for r in clearing
                  if math.isfinite(r["aggregate_fitness"])]
    return {
        "n_shifts": n,
        "n_hard_fail": n_hard_fail,
        "n_clearing": n - n_hard_fail,
        "min_margin": min(margins) if margins else None,
        "max_margin": max(margins) if margins else None,
        "aggregate_fitness_range": (
            (min(finite_aggs), max(finite_aggs)) if finite_aggs else None),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--recipe", choices=tuple(RECIPES), default="consv_trailing_ramp")
    ap.add_argument("--bar-interval", default="4h")
    ap.add_argument("--trailing-stop", type=float, default=-0.06)
    ap.add_argument("--shift", type=int, default=7,
                    help="how many days back to walk 'now', 0-indexed (default 7, "
                         "same default as the bundled fold-date-sensitivity command)")
    ap.add_argument("--years", type=float, default=4.0)
    ap.add_argument("--refresh", action="store_true", help="force a clean re-fetch")
    ap.add_argument("--ramp-bars", type=int, default=None,
                    help="override cold_start_ramp_bars (consv_trailing_ramp recipe only, "
                         "default: builder's own default, currently 120)")
    ap.add_argument("--ramp-scale", type=float, default=None,
                    help="override cold_start_ramp_start_scale (consv_trailing_ramp recipe "
                         "only, default: builder's own default, currently 0.20)")
    args = ap.parse_args()

    genome = build_genome(args.recipe, args.bar_interval, args.trailing_stop,
                          args.ramp_bars, args.ramp_scale)
    ramp_note = ""
    if args.recipe == "consv_trailing_ramp":
        ramp_note = (f" ramp_bars={genome.gene('risk_judge', 'cold_start_ramp_bars')} "
                     f"ramp_scale={genome.gene('risk_judge', 'cold_start_ramp_start_scale')}")
    print(f"[shadow_4h_fold_date_sensitivity] recipe={args.recipe} "
          f"bar_interval={args.bar_interval} trailing_stop={args.trailing_stop} "
          f"shift={args.shift}{ramp_note}")

    buffer_years = args.years + (args.shift / 365.25) + 0.1
    raw = market.load_universe(genome.universe, genome.bar_interval, buffer_years,
                               refresh=args.refresh)
    if not raw:
        print("no market data")
        sys.exit(1)

    width = pd.Timedelta(days=args.years * 365.25)
    now_ts = pd.Timestamp(int(time.time() * 1000), unit="ms", tz="UTC")

    print(f"\nFOLD-DATE SENSITIVITY -- shadow {args.recipe} ({args.bar_interval}, "
          f"n_folds={N_FOLDS}, holdout_frac={HOLDOUT_FRAC:.2f}, trailing "
          f"{args.years}y window, 'now' walked back 0-{args.shift - 1} days)")
    print("=" * 108)
    print(f"  {'shift':>6s} {'as-of':>12s} {'window start':>12s} "
          f"{'aggregate_fitness':>18s}  {'gate max_dd':>12s}  hard_fail  fold fitnesses")

    rows: list[dict[str, Any]] = []
    t0 = time.time()
    for shift in range(args.shift):
        as_of = now_ts - pd.Timedelta(days=shift)
        data = slice_window(raw, as_of, width)
        if not data:
            print(f"  {shift:>6d}  no market data")
            continue
        evaluator = Evaluator(data, n_folds=N_FOLDS)
        res = evaluator.evaluate(genome, log_detail=False)
        agg = res["aggregate_fitness"]
        fits = res["fold_fitness"]
        corrected = dd_corrected_stats(evaluator, genome, res["stats"])
        gate_max_dd = corrected.get("max_dd", 0.0)
        hard_fail = abs(gate_max_dd) > MAX_DD_HARD_FAIL
        rows.append({"shift": shift, "aggregate_fitness": agg,
                     "gate_max_dd": gate_max_dd, "hard_fail": hard_fail})
        agg_str = f"{agg:>18.3f}" if math.isfinite(agg) else f"{'-inf':>18s}"
        fits_str = ", ".join(f"{f:.3f}" if math.isfinite(f) else "-inf" for f in fits)
        print(f"  {shift:>6d} {str(as_of.date()):>12s} {str((as_of - width).date()):>12s} "
              f"{agg_str}  {gate_max_dd:>+11.1%}  "
              f"{'YES' if hard_fail else 'no ':>9s}  [{fits_str}]", flush=True)

    summary = summarize_shifts(rows)
    print(f"\n  -> {summary['n_hard_fail']}/{summary['n_shifts']} shifts hard-fail "
          f"MAX_DD_HARD_FAIL on the real gate (dd_corrected_stats)")
    if summary["min_margin"] is not None:
        print(f"  -> gate margin range across shifts: "
              f"[{summary['min_margin']:+.1%}, {summary['max_margin']:+.1%}] "
              "(negative = hard-fails by that much)")
    if summary["aggregate_fitness_range"] is not None:
        lo, hi = summary["aggregate_fitness_range"]
        print(f"  -> aggregate_fitness range among clearing shifts: "
              f"[{lo:.3f}, {hi:.3f}]")
    print(f"\n[shadow_4h_fold_date_sensitivity] done in {time.time() - t0:.0f}s. "
          "live_state.json untouched.")


if __name__ == "__main__":
    main()
