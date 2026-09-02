"""Combines the two diagnostics the 2026-09-01/09-02 cold-start-ramp thread
built separately, to answer the specific question the 2026-09-02 01:12 UTC
run note left open: does today's one-off finding -- that `consv_trailing`'s
fold-1 hard-fail flips to clearing under the two-sided `dd_trust_continuous_stats`
view (-43.8% one-sided vs -32.7% two-sided) -- hold up across nearby run
dates, or was *that itself* a single lucky/unlucky snapshot the way the
08:08 UTC ramp-genes sweep's "best point" turned out to be (10:27/13:16 UTC)?

`shadow_4h_fold_date_sensitivity.py` already walks a genome across
`--shift` trailing "as-of" dates and reports the one-sided `dd_corrected_stats`
gate verdict at each. `shadow_4h_trust_continuous_check.py` already applies
the two-sided `dd_trust_continuous_stats` correction, but only at a single
snapshot in time. Neither tool alone can answer "does the flip hold across
several days" -- this one runs both corrections at every shift of the same
walk, so a flip that only shows up on one lucky day looks different from one
that holds consistently.

Not wired into any scheduled command, the bundle, or run_from_files.py.
Read-only: reuses `shadow_4h_fold_date_sensitivity.build_genome`/
`slice_window` and `loop.evolve`'s `Evaluator.evaluate`/`dd_corrected_stats`/
`dd_trust_continuous_stats`, all pure replay functions -- never touches
`live_state.json`, never calls `evolve`/`tick`/`save`.

Usage:
    python3 tools/shadow_4h_fold_date_sensitivity_trust_check.py
        [--recipe consv_trailing] [--trailing-stop -0.06] [--shift 7] [--years 4.0]
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
from loop.evolve import Evaluator, dd_corrected_stats, dd_trust_continuous_stats  # noqa: E402
from tools.shadow_4h_fold_date_sensitivity import (  # noqa: E402
    RECIPES,
    build_genome,
    slice_window,
)


def summarize_flips(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Pure summary over per-shift rows (each with `one_sided_hard_fail`/
    `two_sided_hard_fail: bool`). Splits shifts into the three cases that
    matter for judging whether a one-off flip is a stable finding: flips
    (one-sided fails, two-sided clears -- overstatement), both fail (real
    risk, confirmed independent of fold rebasing), and neither fails."""
    n = len(rows)
    n_flip = sum(1 for r in rows if r["one_sided_hard_fail"] and not r["two_sided_hard_fail"])
    n_both_fail = sum(1 for r in rows if r["one_sided_hard_fail"] and r["two_sided_hard_fail"])
    n_neither = sum(1 for r in rows
                    if not r["one_sided_hard_fail"] and not r["two_sided_hard_fail"])
    return {"n_shifts": n, "n_flip": n_flip, "n_both_fail": n_both_fail, "n_neither": n_neither}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--recipe", choices=tuple(RECIPES), default="consv_trailing")
    ap.add_argument("--bar-interval", default="4h")
    ap.add_argument("--trailing-stop", type=float, default=-0.06)
    ap.add_argument("--shift", type=int, default=7,
                    help="how many days back to walk 'now', 0-indexed (default 7)")
    ap.add_argument("--years", type=float, default=4.0)
    ap.add_argument("--refresh", action="store_true", help="force a clean re-fetch")
    args = ap.parse_args()

    genome = build_genome(args.recipe, args.bar_interval, args.trailing_stop)
    print(f"[shadow_4h_fold_date_sensitivity_trust_check] recipe={args.recipe} "
          f"bar_interval={args.bar_interval} trailing_stop={args.trailing_stop} "
          f"shift={args.shift}")

    buffer_years = args.years + (args.shift / 365.25) + 0.1
    raw = market.load_universe(genome.universe, genome.bar_interval, buffer_years,
                               refresh=args.refresh)
    if not raw:
        print("no market data")
        sys.exit(1)

    width = pd.Timedelta(days=args.years * 365.25)
    now_ts = pd.Timestamp(int(time.time() * 1000), unit="ms", tz="UTC")

    print(f"\nFOLD-DATE SENSITIVITY, ONE-SIDED VS TWO-SIDED -- shadow {args.recipe} "
          f"({args.bar_interval}, n_folds={N_FOLDS}, holdout_frac={HOLDOUT_FRAC:.2f}, "
          f"trailing {args.years}y window, 'now' walked back 0-{args.shift - 1} days)")
    print("=" * 118)
    print(f"  {'shift':>6s} {'as-of':>12s} {'one-sided max_dd':>18s}  "
          f"{'two-sided max_dd':>18s}  one_fail  two_fail  flip?")

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

        one_sided = dd_corrected_stats(evaluator, genome, res["stats"])
        one_dd = one_sided.get("max_dd", 0.0)
        one_fail = abs(one_dd) > MAX_DD_HARD_FAIL

        two_sided = dd_trust_continuous_stats(evaluator, genome, res["stats"])
        two_dd = two_sided.get("max_dd", 0.0)
        two_fail = abs(two_dd) > MAX_DD_HARD_FAIL

        flip = one_fail and not two_fail
        rows.append({"shift": shift, "one_sided_max_dd": one_dd,
                     "one_sided_hard_fail": one_fail, "two_sided_max_dd": two_dd,
                     "two_sided_hard_fail": two_fail})
        print(f"  {shift:>6d} {str(as_of.date()):>12s} {one_dd:>+17.1%}  "
              f"{two_dd:>+17.1%}  {'YES' if one_fail else 'no ':>8s}  "
              f"{'YES' if two_fail else 'no ':>8s}  {'<-- FLIP' if flip else ''}",
              flush=True)

    summary = summarize_flips(rows)
    print(f"\n  -> {summary['n_flip']}/{summary['n_shifts']} shifts flip (one-sided "
          "hard-fails, two-sided clears -- fold-rebasing overstatement)")
    print(f"  -> {summary['n_both_fail']}/{summary['n_shifts']} shifts fail under both "
          "views (real risk, not an artifact)")
    print(f"  -> {summary['n_neither']}/{summary['n_shifts']} shifts clear under both views")
    if summary["n_shifts"] and summary["n_flip"] == summary["n_shifts"] - summary["n_neither"]:
        print("-> every one-sided hard-fail in this walk flips under the two-sided view: "
              "consistent with a fold-rebasing overstatement, not a one-off snapshot.")
    elif summary["n_both_fail"]:
        print("-> at least one shift still hard-fails under both views: the "
              "2026-09-02 01:12 UTC single-day flip does not hold up across "
              "nearby run dates -- some real risk remains even under the "
              "two-sided correction.")
    print(f"\n[shadow_4h_fold_date_sensitivity_trust_check] done in "
          f"{time.time() - t0:.0f}s. live_state.json untouched.")


if __name__ == "__main__":
    main()
