"""Read-only CLI entrypoint that runs against the real core/agents/loop/
constitution files on disk instead of evotrader_bundle.py's embedded copy.

Item 7 in AGENTS.md ("unflatten evotrader_bundle.py into real files") flags
the full cutover -- every live command (tick/summary/evolve/...) running
against the real files instead of the bundle -- as its own bigger, riskier
session, not something to attempt in one 3-hourly slot. This is a smaller,
safe stepping stone toward it: only commands that never write to
live_state.json are wired up here, verified byte-for-byte identical to
evotrader_bundle.py's own output for the same commands against the same
state file (see tests/test_run_from_files_matches_bundle.py).

`tick`/`evolve`/anything that calls acct.save() is deliberately NOT
included here -- wiring those up, and deciding whether to ever point a
scheduled run at this file instead of the bundle, remains the separate,
riskier session AGENTS.md already flagged. This file must never be added to
a scheduled run's command list until that decision is made.

Unlike evotrader_bundle.py's main(), this does not touch
`constitution.EMBEDDED_SOURCES` -- that dict stays empty, so
`constitution.checksum()` takes its file-based branch and hashes the real
`constitution/__init__.py` and `core/portfolio.py` on disk instead.

Beyond `summary`/`signals`, this also wires up three of the diagnostic
commands AGENTS.md's own command table already documents as never touching
live_state.json or the champion: `holdout-pressure` (reads acct.lineage
only, no market data or backtest -- the cheapest diagnostic in the bundle),
`regime` (one market load, equal-weight buy-and-hold per fold/holdout
window, no genome or Council involved), and `fold-dd-blindspot` (one
Evaluator.evaluate() call plus two continuous run_backtest replays per
genome -- same cost class as `regime`, ~1-2 minutes). All three are
transcribed here verbatim from their evotrader_bundle.py implementation,
not reimplemented -- see tools/edit_bundle_module.py for the module-level
equivalent of that discipline. The remaining diagnostics (`anatomy`,
`consults`, `costs`, `succession-audit`, ...) are heavier (a full backtest
or more, sometimes several) and not attempted in this pass.
"""
from __future__ import annotations

import json
import os
import sys

from constitution import verify
from core.live import LiveAccount

SUPPORTED_COMMANDS = ("summary", "signals", "holdout-pressure", "regime",
                      "fold-dd-blindspot")


def _reconstruct_champion_genome(version, lineage):
    """Rebuild a historical champion genome purely from live_state.json's own
    recorded `lineage` (every accepted promotion's patch), by replaying
    accepted patches from the seed forward. Transcribed verbatim from
    evotrader_bundle.py's own helper of the same name (not part of any
    _SRC module -- it's plain CLI-script code, so it has to be duplicated
    here rather than imported). Used by `fold-dd-blindspot --also-version N`.
    Raises ValueError if `version` was never an accepted promotion recorded
    in lineage (version 1, the seed, always succeeds and needs no patches)."""
    from core.genome import Genome

    patches_by_version = {}
    for e in lineage:
        acc = e.get("accepted")
        if acc:
            patches_by_version[acc["new_version"]] = acc["patch"]

    g = Genome.champion()
    versions = {1: g}
    for v in sorted(patches_by_version):
        g = g.child(list(patches_by_version[v].items()), note=f"reconstructed-v{v}")
        versions[v] = g

    if version not in versions:
        raise ValueError(
            f"genome version {version} has no accepted promotion recorded in "
            f"lineage (known versions: {sorted(versions)})"
        )
    return versions[version]


def _cmd_holdout_pressure(acct) -> None:
    from loop.evolve import summarize_holdout_pressure
    g0 = acct.genome
    summary = summarize_holdout_pressure(acct.lineage, g0.version)
    draws = summary["holdout_draws"]
    print()
    print(f"HOLDOUT PRESSURE — champion v{g0.version}")
    print("=" * 72)
    print(f"  {summary['n_generations']} generation(s) of real search run against "
          f"this champion since its promotion")
    print(f"    {summary['no_proposal_generations']:>3d} no new proposals")
    print(f"    {summary['fold_blocked_generations']:>3d} fold-aggregate gate blocked "
          f"(nothing that generation reached the sealed holdout)")
    print(f"    {summary['accepted_generations']:>3d} accepted (would have promoted "
          f"this champion away)")
    print(f"    {len(draws):>3d} individual sealed-holdout draws across the rest "
          f"— every one lost" if draws else "    0 sealed-holdout draws")
    if draws:
        print()
        print("  fold-aggregate winners the sealed holdout rejected (one row per "
              "real draw):")
        print(f"    {'fold fit':>9s} {'champ fold':>11s} {'holdout':>9s} "
              f"{'champ holdout':>14s} {'margin':>7s} {'draws':>6s}")
        for d in draws:
            ff = d["fold_fitness"]
            print(f"    {'n/a' if ff is None else format(ff, '9.3f')} "
                  f"{d['champion_fold_fitness']:>11.3f} "
                  f"{d['holdout_challenger']:>9.3f} "
                  f"{d['holdout_champion']:>14.3f} "
                  f"{d['margin']:>7.3f} {d['cumulative_draws']:>6d}")
        print()
        print("  Reading it: every row cleared the fold-aggregate bar (a genuine "
              "improvement on\n  search data) and still lost on one noisy sealed-"
              "holdout draw -- the more of these\n  accumulate, the likelier this "
              "champion is entrenched by holdout luck rather than\n  by being "
              "the best genome the search has actually found.")


def _cmd_regime(acct) -> None:
    from constitution import HOLDOUT_FRAC, N_FOLDS
    from core import market
    from core.market import Replay
    from loop.engine import benchmark_buy_hold
    interval = None
    if "--interval" in sys.argv:
        interval = sys.argv[sys.argv.index("--interval") + 1]
    g0 = acct.genome
    interval = interval or g0.bar_interval
    data = market.load_universe(g0.universe, interval, 4.0)
    if not data:
        print("no market data")
        sys.exit(1)
    replay = Replay({s: df for s, df in data.items() if s in g0.universe})
    n = len(replay)
    search_end = 1.0 - HOLDOUT_FRAC
    edges = [i / N_FOLDS * search_end for i in range(N_FOLDS + 1)]
    windows = [(f"fold {i + 1}", edges[i], edges[i + 1]) for i in range(N_FOLDS)]
    windows.append(("holdout", search_end, 1.0))
    bcfg = g0.data.get("broker", {})
    cash = float(bcfg.get("start_cash", 10_000.0))
    bpy = market.BARS_PER_YEAR.get(interval, 365.25)
    print(f"[regime] {len(data)} symbols, {interval} bars, {n} total bars", flush=True)
    print()
    print(f"REGIME BY FOLD/HOLDOUT — {interval} bars, {len(data)} symbols, "
          f"equal-weight buy-and-hold")
    print("=" * 92)
    print(f"  {'window':<10s} {'start':<12s} {'end':<12s} {'bars':>6s} "
          f"{'return':>9s} {'sharpe':>7s} {'maxDD':>7s}")
    for label, a, b in windows:
        start = max(60, int(n * a))
        end = min(n - 1, int(n * b))
        if end - start < 5:
            print(f"  {label:<10s} window too short ({end - start} bars)")
            continue
        bench = benchmark_buy_hold(replay, g0.universe, start, end, cash,
                                   bars_per_year=bpy)
        if not bench:
            print(f"  {label:<10s} no benchmark data")
            continue
        print(f"  {label:<10s} {str(replay.index[start])[:10]:<12s} "
              f"{str(replay.index[end])[:10]:<12s} {end - start:>6d} "
              f"{bench['total_return']:>+8.1%} {bench['sharpe']:>7.2f} "
              f"{bench['max_dd']:>7.1%}")


def _cmd_fold_dd_blindspot(acct) -> None:
    from loop.evolve import Evaluator
    from loop.engine import run_backtest
    from core import market
    from constitution import MAX_DD_HARD_FAIL
    g0 = acct.genome
    genomes = [(f"v{g0.version} (live)", g0)]
    if "--also-version" in sys.argv:
        also_version = int(sys.argv[sys.argv.index("--also-version") + 1])
        try:
            g_other = _reconstruct_champion_genome(also_version, acct.lineage)
        except ValueError as e:
            print(f"[fold-dd-blindspot] {e}")
            sys.exit(1)
        genomes.append((f"v{also_version} (reconstructed)", g_other))
    data = market.load_universe(g0.universe, g0.bar_interval, 4.0)
    if not data:
        print("no market data")
        sys.exit(1)
    print(f"[fold-dd-blindspot] replaying {len(data)} symbols against "
          f"{' and '.join(label for label, _ in genomes)} ...", flush=True)
    print()
    for label, genome in genomes:
        ev = Evaluator(data)
        res = ev.evaluate(genome, log_detail=False)
        print(f"MAXDD GATE BLIND SPOT -- {label}")
        print("=" * 96)
        for i, f in enumerate(res["folds"]):
            if "error" in f:
                print(f"  fold {i + 1}: {f['error']}")
                continue
            print(f"  fold {i + 1} [{f['window'][0]:.3f}, {f['window'][1]:.3f}]: "
                  f"own local max_dd {f['stats'].get('max_dd', 0):>7.1%}")
        gate_dd = res["stats"].get("max_dd", 0.0)
        print(f"  gate-visible max_dd (worst of the folds above, what accepts() "
              f"checks): {gate_dd:>7.1%}")
        search_end = ev.search_end
        true_search = run_backtest(genome, data, 0.0, search_end, log_detail=False)
        true_search_dd = true_search["stats"].get("max_dd", 0.0) if not true_search.get("error") else None
        if true_search_dd is not None:
            print(f"  true continuous max_dd, same [0, {search_end:.3f}] search span, "
                  f"one unbroken replay: {true_search_dd:>7.1%}  "
                  f"(gap {true_search_dd - gate_dd:+.1%} vs gate-visible)")
        true_full = run_backtest(genome, data, 0.0, 1.0, log_detail=False)
        true_full_dd = true_full["stats"].get("max_dd", 0.0) if not true_full.get("error") else None
        if true_full_dd is not None:
            over = " (OVER MAX_DD_HARD_FAIL, gate never sees it)" if abs(true_full_dd) > MAX_DD_HARD_FAIL else ""
            print(f"  true continuous max_dd, full [0, 1] history incl. holdout "
                  f"(what universe-perturb/drawdown/anatomy report): "
                  f"{true_full_dd:>7.1%}{over}")
        print()


def main() -> None:
    cmd = sys.argv[1] if len(sys.argv) > 1 else "summary"
    if cmd not in SUPPORTED_COMMANDS:
        print(
            f"[run_from_files] unsupported command {cmd!r} -- only "
            f"{SUPPORTED_COMMANDS} are wired up against the real files "
            "(see module docstring); use evotrader_bundle.py for anything else"
        )
        sys.exit(1)

    state_path = os.environ.get("EVO_STATE", "live_state.json")
    ok, msg = verify(os.environ.get("EVO_MANIFEST", "evotrader.manifest"))
    print(f"[constitution] {msg}")
    if not ok:
        sys.exit(1)

    acct = LiveAccount.load(state_path)
    if cmd == "signals":
        print(acct.signals())
    elif cmd == "summary":
        print(json.dumps(acct.summary(), indent=2, default=str))
    elif cmd == "holdout-pressure":
        _cmd_holdout_pressure(acct)
    elif cmd == "regime":
        _cmd_regime(acct)
    elif cmd == "fold-dd-blindspot":
        _cmd_fold_dd_blindspot(acct)


if __name__ == "__main__":
    main()
