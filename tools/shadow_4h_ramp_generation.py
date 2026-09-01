"""Run real `EvolutionRun.generation()` calls against the cold-start-ramp
4h-shadow champion (`tools.shadow_4h_x6_seed.build_consv_trailing_ramp_seed()`,
now 120 bars / 0.20x after the 2026-09-01 08:08 UTC grid search) -- the
"natural next check" that same run note flagged and left undone: the 04:18
UTC session already ran one `generation()` against the prior 120/0.10 point
(seed 9001, 34 blind proposals, champion held) but never re-ran it against
the refined 120/0.20 point, and that session's own script only captured the
generation summary, not `record["top"]`'s per-candidate patch list -- so
whether any proposal actually touched either new `cold_start_ramp_bars`/
`cold_start_ramp_start_scale` gene went unrecorded. This script prints
`record["top"]` every generation so that stays visible, and flags any
proposal (in or out of the top 8) whose patch touches either gene.

Not wired into any scheduled command, the bundle, or run_from_files.py.
Read-only with respect to the live account: `EvolutionRun.generation()` never
touches `live_state.json` -- it only appends to the gitignored
`state/lineage.jsonl` scratch log. Never calls `evolve`/`tick`/`save`.

Usage:
    python3 tools/shadow_4h_ramp_generation.py [--generations 3] [--n-blind 6]
                                               [--seed 9002] [--years 4.0]
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.market import load_universe  # noqa: E402
from loop.evolve import EvolutionRun  # noqa: E402
from tools.shadow_4h_x6_seed import build_consv_trailing_ramp_seed  # noqa: E402

RAMP_GENES = ("cold_start_ramp_bars", "cold_start_ramp_start_scale")


def touches_ramp_genes(patch: dict) -> list[str]:
    return [k for k in patch if any(k.endswith(g) for g in RAMP_GENES)]


def print_top(record: dict) -> None:
    top = record.get("top", [])
    if not top:
        print("    (no candidates reached the top-8 cut -- researcher exhausted)")
        return
    for i, cand in enumerate(top):
        fit = cand["fitness"]
        fit_s = f"{fit:.3f}" if fit is not None else "nonfinite"
        touched = touches_ramp_genes(cand["patch"])
        flag = f"  <-- touches {touched}" if touched else ""
        print(f"    #{i + 1} fitness={fit_s} kind={cand['kind']} "
              f"target={cand['target']} patch={cand['patch']}{flag}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--bar-interval", default="4h")
    ap.add_argument("--years", type=float, default=4.0)
    ap.add_argument("--refresh", action="store_true", help="force a clean re-fetch")
    ap.add_argument("--trailing-stop", type=float, default=-0.06)
    ap.add_argument("--seed", type=int, default=9002,
                    help="Researcher RNG seed -- 9002, distinct from the 04:18 "
                         "UTC session's 9001, so this is a fresh draw rather "
                         "than a rerun of the same proposal sequence")
    ap.add_argument("--generations", type=int, default=3)
    ap.add_argument("--n-blind", type=int, default=6,
                    help="calibrated for 4h cost by the 2026-08-16 1404 UTC "
                         "session -- do not use the bundled CLI's 1d-tuned "
                         "default of 14 here")
    args = ap.parse_args()

    champion = build_consv_trailing_ramp_seed(args.bar_interval, args.trailing_stop)
    print(f"[shadow_4h_ramp_generation] champion: cold_start_ramp "
          f"{champion.gene('risk_judge', 'cold_start_ramp_bars')}/"
          f"{champion.gene('risk_judge', 'cold_start_ramp_start_scale')} on consv1 + "
          f"trailing_stop {args.trailing_stop}, {args.bar_interval} bars")

    data = load_universe(champion.universe, interval=champion.bar_interval,
                         years=args.years, refresh=args.refresh)
    run = EvolutionRun(data, seed=args.seed, verbose=True)

    any_ramp_touch = False
    t0 = time.time()
    for i in range(args.generations):
        print(f"\n--- generation {i + 1}/{args.generations} "
              f"({time.time() - t0:.0f}s elapsed)")
        champion, record = run.generation(champion, n_blind=args.n_blind)
        print_top(record)
        if any(touches_ramp_genes(c["patch"]) for c in record.get("top", [])):
            any_ramp_touch = True
        if "accepted" in record:
            print(f"    *** ACCEPTED: champion is now v{champion.version} ***")

    print(f"\n[shadow_4h_ramp_generation] done in {time.time() - t0:.0f}s. "
          f"Final champion version: v{champion.version}. Any top-8 candidate "
          f"touched a cold_start_ramp gene: {any_ramp_touch}.")
    print("live_state.json untouched -- this script never calls save()/promote() "
          "against the live account.")


if __name__ == "__main__":
    main()
