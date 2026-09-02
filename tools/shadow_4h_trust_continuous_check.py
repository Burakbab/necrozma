"""Applies the existing, already-tested `dd_trust_continuous_stats()` two-sided
drawdown correction (built 2026-08-22 for the bundled `succession-audit`
command, to audit past *1d* champions) to the 4h-shadow cold-start-ramp genome
family for the first time -- the "step back and reconsider" option (2b) the
2026-09-01 21:59 UTC run note left as item 2's only untried path, after every
lever tried against fold 1's cold start (size ramp, conviction floor, vol cap)
either failed to help or made the real gate's drawdown worse.

None of those sessions questioned whether fold 1's own reported drawdown was
trustworthy in the first place. `dd_corrected_stats()` (what `accepts()`
actually gates a real promotion on) is one-sided: it takes min(fold-merged,
continuous), which can only ever make max_dd *more* negative, correcting for
a drawdown that spans a fold boundary invisible to the fold-local number. But
`loop.evolve`'s own `dd_trust_continuous_stats()` docstring names the
opposite, still-open direction: fold-merged can also *overstate* true risk
when a fold's own local peak rebases to a fresh, lower value right at its
boundary, turning a decline that would be a modest fraction of the real
long-accumulated peak into a much larger fraction of the reset one -- exactly
what a fold starting cold (broker reset to flat cash, `RiskJudge` reset to
its own bar-zero) mechanically does at every fold edge. Every 4h-shadow
session since 2026-08-31 has been treating fold 1's from-cold-start max_dd as
ground truth and hand-tuning genes to survive it; this checks whether that
number is trustworthy at all, using code that already exists and is already
tested (`succession-audit` exercises `dd_trust_continuous_stats()` against
past 1d champions) -- no new mechanism, no engine or constitution change.

Not wired into any scheduled command, the bundle, or run_from_files.py.
Read-only: builds genomes in memory and calls `Evaluator.evaluate()`/
`dd_corrected_stats()`/`dd_trust_continuous_stats()`, all pure replay
functions -- never touches `live_state.json`, never calls
`evolve`/`tick`/`save`.

Usage:
    python3 tools/shadow_4h_trust_continuous_check.py [--recipes x6,consv_trailing,consv_trailing_ramp]
        [--years 4.0] [--refresh]
"""
from __future__ import annotations

import argparse
import math
import sys
import time
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from constitution import MAX_DD_HARD_FAIL, N_FOLDS, fitness as fitness_fn  # noqa: E402
from core import market  # noqa: E402
from core.genome import Genome  # noqa: E402
from loop.evolve import Evaluator, dd_corrected_stats, dd_trust_continuous_stats  # noqa: E402
from tools.shadow_4h_x6_seed import (  # noqa: E402
    build_consv_trailing_ramp_seed,
    build_consv_trailing_seed,
    build_x6_scaled_seed,
)

RECIPES = {
    "x6": lambda: build_x6_scaled_seed("4h"),
    "consv_trailing": lambda: build_consv_trailing_seed("4h"),
    "consv_trailing_ramp": lambda: build_consv_trailing_ramp_seed("4h"),
}


def audit_genome(evaluator: Evaluator, g: Genome) -> dict[str, Any]:
    """One genome's row: fold-agg fitness plus both drawdown-correction
    policies' verdicts, and the per-fold local max_dd list so a divergence
    between the two policies can be traced to a specific fold. Pure function
    over an already-built `Evaluator` -- no I/O, unit-testable with a fake
    evaluator/genome pair."""
    res = evaluator.evaluate(g, log_detail=False)
    fold_dd = [f["stats"].get("max_dd") for f in res["folds"] if "stats" in f]

    corrected = dd_corrected_stats(evaluator, g, res["stats"])
    corrected_dd = corrected.get("max_dd", 0.0)
    corrected_fit = fitness_fn(corrected)
    corrected_fail = abs(corrected_dd) > MAX_DD_HARD_FAIL

    trust_cont = dd_trust_continuous_stats(evaluator, g, res["stats"])
    trust_dd = trust_cont.get("max_dd", 0.0)
    trust_fit = fitness_fn(trust_cont)
    trust_fail = abs(trust_dd) > MAX_DD_HARD_FAIL

    return {
        "aggregate_fitness": res["aggregate_fitness"],
        "fold_max_dd": fold_dd,
        "dd_corrected_max_dd": corrected_dd,
        "dd_corrected_fitness": corrected_fit,
        "dd_corrected_hard_fail": corrected_fail,
        "trust_continuous_max_dd": trust_dd,
        "trust_continuous_fitness": trust_fit,
        "trust_continuous_hard_fail": trust_fail,
        "verdict_flips": corrected_fail and not trust_fail,
    }


def format_row(name: str, audit: dict[str, Any]) -> str:
    fold_dd_str = ", ".join(
        "n/a" if v is None else f"{v:.1%}" for v in audit["fold_max_dd"])
    agg = audit["aggregate_fitness"]
    agg_str = f"{agg:.3f}" if math.isfinite(agg) else "-inf"
    flip = "  <-- gate verdict flips (real risk, not an overstatement)" \
        if audit["verdict_flips"] else ""
    return (
        f"{name}\n"
        f"  fold-agg fitness: {agg_str}   per-fold max_dd: [{fold_dd_str}]\n"
        f"  dd_corrected (current gate):   max_dd {audit['dd_corrected_max_dd']:+.1%}  "
        f"fitness {audit['dd_corrected_fitness']:.3f}  "
        f"hard_fail={'YES' if audit['dd_corrected_hard_fail'] else 'no'}\n"
        f"  trust_continuous (two-sided):  max_dd {audit['trust_continuous_max_dd']:+.1%}  "
        f"fitness {audit['trust_continuous_fitness']:.3f}  "
        f"hard_fail={'YES' if audit['trust_continuous_hard_fail'] else 'no'}"
        f"{flip}"
    )


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--recipes", default="x6,consv_trailing,consv_trailing_ramp",
                    help="comma-separated subset of: " + ",".join(RECIPES))
    ap.add_argument("--years", type=float, default=4.0)
    ap.add_argument("--refresh", action="store_true", help="force a clean re-fetch")
    args = ap.parse_args()

    names = [n.strip() for n in args.recipes.split(",") if n.strip()]
    unknown = [n for n in names if n not in RECIPES]
    if unknown:
        print(f"unknown recipe(s): {unknown}, choose from {list(RECIPES)}")
        sys.exit(1)

    genomes = {n: RECIPES[n]() for n in names}
    universe = next(iter(genomes.values())).universe
    bar_interval = next(iter(genomes.values())).bar_interval
    print(f"[shadow_4h_trust_continuous_check] recipes={names} "
          f"bar_interval={bar_interval} n_folds={N_FOLDS} years={args.years}")

    data = market.load_universe(universe, bar_interval, args.years, refresh=args.refresh)
    if not data:
        print("no market data")
        sys.exit(1)
    print(f"[shadow_4h_trust_continuous_check] {len(data)} symbols loaded", flush=True)

    evaluator = Evaluator(data, n_folds=N_FOLDS)
    t0 = time.time()
    print()
    any_flip = False
    for name, g in genomes.items():
        audit = audit_genome(evaluator, g)
        print(format_row(name, audit))
        print()
        any_flip = any_flip or audit["verdict_flips"]

    print(f"[shadow_4h_trust_continuous_check] done in {time.time() - t0:.0f}s. "
          "live_state.json untouched.")
    if any_flip:
        print("-> at least one recipe's hard-fail verdict is one-sided-only: the "
              "two-sided trust_continuous view would let it through. That fold's "
              "reported drawdown is at least partly a fold-rebasing overstatement, "
              "not pure real risk -- reread its per-fold max_dd list before hand-"
              "tuning any more cold-start genes against it.")
    else:
        print("-> every recipe that hard-fails under the current gate also "
              "hard-fails under the two-sided trust_continuous view: the "
              "drawdown is real, confirmed independently of fold rebasing, not "
              "a measurement artifact. The cold-start-ramp genes were fighting "
              "a real risk, not a mismeasured one.")


if __name__ == "__main__":
    main()
