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

Beyond `summary`/`signals`, this also wires up four of the diagnostic
commands AGENTS.md's own command table already documents as never touching
live_state.json or the champion: `holdout-pressure` and `holdout-margin-audit`
(both read acct.lineage only, no market data or backtest -- the cheapest
diagnostics in the bundle), `regime` (one market load, equal-weight
buy-and-hold per fold/holdout window, no genome or Council involved), and
`fold-dd-blindspot` (one Evaluator.evaluate() call plus two continuous
run_backtest replays per genome -- same cost class as `regime`, ~1-2
minutes). All four are transcribed here verbatim from their
evotrader_bundle.py implementation, not reimplemented -- see
tools/edit_bundle_module.py for the module-level equivalent of that
discipline. The remaining diagnostics (`anatomy`, `consults`, `costs`,
`succession-audit`, ...) are heavier (a full backtest or more, sometimes
several) and not attempted in this pass.

`tick-dry-run` is the first piece of the actual `tick`/`evolve` cutover
AGENTS.md item 7 has flagged as the riskier remainder across five prior
sessions -- but scoped to stay exactly as safe as everything else here: it
calls the real `LiveAccount.tick()` (the same method the bundle's `tick`
command calls) to exercise the full decision pipeline -- market data,
Council, both judges, hard-call flagging -- against the real files, and
prints the resulting decision, but it NEVER calls `acct.save()`. Whatever
`tick()` mutates (self.journal, self.broker, self.ticks) lives only in this
process's own `acct` object and is discarded when the process exits;
`live_state.json` on disk is never opened for writing. This is not a
special dry-run code path inside `tick()` itself -- `LiveAccount.tick()`
has no such mode and this file adds none -- the guarantee is entirely
"the only line that writes state is never called", verified by
`tests/test_run_from_files_matches_bundle.py`'s dry-run test asserting the
state file's content is byte-identical before and after. On any bar
already traded (the common case -- the daily 00:20 UTC run normally beats
every later 3-hourly check to it) `tick()`'s own idempotency guard returns
its `skipped` dict before mutating `self.journal` or `self.broker` at all,
so this is doubly inert on a day's second-or-later invocation, same as
calling the bundle's own `tick` command a second time is already safe by
design. `--force` is intentionally NOT wired here (unlike the bundle's
`tick`): forcing a repeat decision on an already-traded bar is an explored
question for a human, not something a 3-hourly script should ever need,
and leaving it out removes any temptation to add it under time pressure.

`evolve-dry-run` (added 2026-08-24) is the second and final piece of that
cutover: it runs the real self-improvement search (`loop.evolve.
EvolutionRun`, the same class the bundle's `evolve` command drives) against
the real files, generation by generation, exactly as `evolve` does --
including resuming `acct.researcher_memory` so the multiple-testing bar
keeps rising across invocations the same way -- but it NEVER calls
`acct.save()`, no matter whether a candidate would have been promoted.
`EvolutionRun` itself still writes to `state/genomes/` (via `Genome.save`/
`.promote()`) and appends to `state/lineage.jsonl` -- both gitignored,
rebuildable local cache per `.gitignore`'s own comment, not the durable
state this guarantee is about. `live_state.json` is never opened for
writing on any code path here, same discipline as `tick-dry-run`. Unlike
`evolve`, this command also accepts an optional `--seed N` (the bundle's
`evolve` always passes `seed=None` for genuine randomness on every live
run) so a caller -- namely this file's own test suite -- can make a run
reproducible without waiting on real market conditions.

`tick`/`evolve` (added 2026-08-24, after both dry-run twins above were
tested) are the actual cutover: the same bodies as evotrader_bundle.py's
own `tick`/`evolve` commands, transcribed verbatim, including the real
`acct.save(state_path)` calls. This is the point item 7 has been building
toward across many prior sessions -- proof, not assertion, that the real
files produce identical decisions to the bundle came first (byte-identical
output tests for every read-only command, byte-identical *state* tests for
both dry-run twins on both their skip and non-skip branches), and only
then did the saving versions get added. `tick` supports `--force` (unlike
`tick-dry-run`, which deliberately omits it -- see that docstring) because
this command is meant to be a genuine drop-in replacement for the bundle's
own `tick`, not a narrower safety-scoped variant of it. `evolve` keeps the
same test-only `--seed N` escape hatch `evolve-dry-run` added, for the same
reason. `tests/test_run_from_files_matches_bundle.py`'s `test_tick_*`
tests prove byte-for-byte state-file parity against the bundle's own real
`tick` on identical starting scratch state (both branches); `evolve`'s
parity is checked against its own `evolve-dry-run` twin instead (same seed,
same starting state, same decision), since the bundle's `evolve` has no
`--seed` flag to pin down for a subprocess-level comparison the way `tick`
does.

Adding these two commands here does NOT change what powers live trading:
no scheduled run has been pointed at this file, `evotrader_bundle.py`
remains what every scheduled `tick`/`evolve`/`summary` command actually
runs, and that stays true until a separate, deliberate decision says
otherwise -- this file makes the real-files path *capable* of the real
cutover, it does not flip it. Running `tick`/`evolve` here against the
real `live_state.json` has exactly the same effect as running the
bundle's own `tick`/`evolve` against it (proven, not assumed, by the
tests above) -- there is no more safety margin in calling the bundle
today than in calling this file, which is exactly the point: the
remaining reason to prefer the bundle for scheduled runs is now habit and
caution, not an unverified risk.
"""
from __future__ import annotations

import json
import os
import sys

from constitution import verify
from core.live import LiveAccount

SUPPORTED_COMMANDS = ("summary", "signals", "holdout-pressure",
                      "holdout-margin-audit", "regime",
                      "fold-dd-blindspot", "tick-dry-run", "evolve-dry-run",
                      "tick", "evolve")


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


def _cmd_holdout_margin_audit(acct) -> None:
    from loop.evolve import raw_holdout_beats, summarize_holdout_pressure
    versions = sorted(set(e.get("champion_version") for e in acct.lineage
                          if e.get("champion_version") is not None))
    print()
    print("HOLDOUT MARGIN AUDIT — raw beats vs. margin-adjusted rejections, "
          "by champion reign")
    print("=" * 72)
    any_draws = False
    for v in versions:
        summary = summarize_holdout_pressure(acct.lineage, v)
        draws = summary["holdout_draws"]
        if not draws:
            print(f"  champion v{v}: 0 sealed-holdout draws recorded (nothing "
                  f"reached holdout, or it was promoted away before anything did)")
            continue
        any_draws = True
        audit = raw_holdout_beats(draws)
        print(f"  champion v{v}: {audit['n_draws']} sealed-holdout draws, "
              f"{audit['n_raw_beats']} beat the champion's raw holdout score "
              f"and were still rejected on margin")
        if audit["first_flip_index"] is not None:
            d = draws[audit["first_flip_index"]]
            print(f"    first raw beat: draw #{audit['first_flip_index'] + 1} "
                  f"(cumulative draw {d['cumulative_draws']}), holdout "
                  f"{d['holdout_challenger']:.3f} vs champion "
                  f"{d['holdout_champion']:.3f} (needed +{d['margin']:.3f} margin)")
        for i, (d, flipped) in enumerate(zip(draws, audit["flips"])):
            mark = " <- raw beat" if flipped else ""
            print(f"    {'n/a' if d['fold_fitness'] is None else format(d['fold_fitness'], '7.3f')} "
                  f"fold-fit  holdout {d['holdout_challenger']:>7.3f}  "
                  f"champ {d['holdout_champion']:>7.3f}  "
                  f"margin {d['margin']:>6.3f}{mark}")
    print()
    if any_draws:
        print("  Reading it: every row already failed `holdout_accepts()` today, so "
              "none of\n  this changed a real decision. 'raw beat' rows are where the "
              "rejection came\n  entirely from the additive margin, not from the "
              "challenger actually being\n  worse -- only the FIRST raw beat in a "
              "reign is a valid counterfactual\n  ('would this have promoted under a "
              "zero-margin rule'); later raw beats in\n  the same reign were tested "
              "against a champion a real promotion would have\n  already replaced, so "
              "they are shown for completeness, not summed into a\n  missed-promotion "
              "count. This does not recommend removing the margin --\n  `required_margin()` "
              "exists because the best of many noisy draws beats an\n  equal champion "
              "by luck alone often enough on its own; it quantifies how\n  much of the "
              "historical rejection record is margin, not sign, using real\n  recorded "
              "lineage instead of a new search.")
    else:
        print("  No champion reign in this account's real lineage has ever had a "
              "fold-aggregate\n  winner reach the sealed holdout yet.")


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


def _cmd_tick_dry_run(acct) -> None:
    """Run the real decision pipeline (LiveAccount.tick) against the real
    files and print what it decided, but never persist anything -- see the
    module docstring for the exact safety argument. `acct.save()` is not
    called anywhere in this function, on any code path."""
    print("[tick-dry-run] DRY RUN -- deciding against the real files, "
          "will NOT call acct.save() no matter what happens below", flush=True)
    entry = acct.tick(force=False)
    if "error" in entry:
        print(f"[tick-dry-run] error: {entry['error']}")
        sys.exit(1)
    if "skipped" in entry:
        print(f"[tick-dry-run] {entry['skipped']} -- nothing to do "
              "(state file was never opened for writing)")
        return
    print("[tick-dry-run] a real decision was computed for an UNTRADED bar "
          "-- this would be a live trade under `evotrader_bundle.py tick`, "
          "but nothing here was saved:")
    print(json.dumps({k: v for k, v in entry.items() if k != "decision"}, indent=2))
    d = entry.get("decision") or {}
    for f in (d.get("fills") or []):
        print(f"  {f['status']:8s} {f['side']:4s} {f['symbol']:10s} {f.get('reason', '')[:110]}")
    if not d.get("fills"):
        print("  no trades this bar")
    print("[tick-dry-run] state file untouched -- re-run "
          "`evotrader_bundle.py tick` (or this bar's normal scheduled run) "
          "to actually book this decision")


def _cmd_evolve_dry_run(acct) -> None:
    """Run the real self-improvement loop (loop.evolve.EvolutionRun) against
    the real files -- transcribed verbatim from evotrader_bundle.py's own
    `evolve` command body -- but never call acct.save(), on any code path,
    win or lose. See the module docstring for the exact safety argument."""
    from core import market
    from core.genome import Genome
    from loop.evolve import EvolutionRun

    n = 3
    if len(sys.argv) > 2 and not sys.argv[2].startswith("--"):
        n = int(sys.argv[2])
    seed = None
    if "--seed" in sys.argv:
        seed = int(sys.argv[sys.argv.index("--seed") + 1])

    print("[evolve-dry-run] DRY RUN -- searching against the real files, "
          "will NOT call acct.save() no matter what happens below", flush=True)
    g0 = acct.genome
    g0.save("champion")
    data = market.load_universe(g0.universe, g0.bar_interval, 4.0)
    if not data:
        print("no market data")
        sys.exit(1)
    print(f"[evolve-dry-run] {len(data)} symbols, champion v{g0.version} "
          f"({g0.bar_interval} bars), {n} generations")

    # Same researcher-memory resume as the bundle's `evolve` -- see its own
    # comment for why this matters (the multiple-testing bar must keep
    # rising across invocations, not reset to n=1 every time).
    mem = acct.researcher_memory or {}
    if mem.get("champion_version") == g0.version:
        init_tested = {tuple(tuple(pair) for pair in item) for item in mem.get("tested", [])}
        init_stagnation = int(mem.get("stagnation", 0))
    else:
        init_tested, init_stagnation = set(), 0
    init_holdout_draws = int(mem.get("holdout_draws", 0))

    run = EvolutionRun(data, seed=seed, initial_tested=init_tested,
                       initial_stagnation=init_stagnation,
                       initial_champion_version=g0.version,
                       initial_holdout_draws=init_holdout_draws)
    run.run(generations=n, n_blind=14)
    final = Genome.champion()
    if final.version != g0.version:
        print(f"[evolve-dry-run] would have promoted champion v{g0.version} -> "
              f"v{final.version} -- NOT saved, live_state.json untouched")
    else:
        print("[evolve-dry-run] champion would have held -- NOT saved, "
              "live_state.json untouched")


def _cmd_tick(acct, state_path) -> None:
    """The actual `tick` cutover -- transcribed verbatim from
    evotrader_bundle.py's own `tick` command body, including the real
    acct.save(state_path) call. See the module docstring for the parity
    argument."""
    entry = acct.tick(force="--force" in sys.argv)
    if "error" in entry:
        print(f"[live] error: {entry['error']}")
        sys.exit(1)
    if "skipped" in entry:
        print(f"[live] {entry['skipped']} — nothing to do")
        return
    acct.save(state_path)
    print(json.dumps({k: v for k, v in entry.items() if k != "decision"}, indent=2))
    d = entry.get("decision") or {}
    for f in (d.get("fills") or []):
        print(f"  {f['status']:8s} {f['side']:4s} {f['symbol']:10s} {f.get('reason', '')[:110]}")
    if not (d.get("fills")):
        print("  no trades this bar")


def _cmd_evolve(acct, state_path) -> None:
    """The actual `evolve` cutover -- transcribed verbatim from
    evotrader_bundle.py's own `evolve` command body, including the real
    acct.save(state_path) calls on both the promote and hold paths. Adds
    the same test-only `--seed N` escape hatch `evolve-dry-run` has (the
    bundle's own `evolve` always passes seed=None); see the module
    docstring for why."""
    from core import market
    from core.genome import Genome
    from loop.evolve import EvolutionRun

    n = 3
    if len(sys.argv) > 2 and not sys.argv[2].startswith("--"):
        n = int(sys.argv[2])
    seed = None
    if "--seed" in sys.argv:
        seed = int(sys.argv[sys.argv.index("--seed") + 1])

    g0 = acct.genome
    g0.save("champion")
    data = market.load_universe(g0.universe, g0.bar_interval, 4.0)
    print(f"[evolve] {len(data)} symbols, champion v{g0.version} "
          f"({g0.bar_interval} bars), {n} generations")

    mem = acct.researcher_memory or {}
    if mem.get("champion_version") == g0.version:
        init_tested = {tuple(tuple(pair) for pair in item) for item in mem.get("tested", [])}
        init_stagnation = int(mem.get("stagnation", 0))
    else:
        init_tested, init_stagnation = set(), 0
    init_holdout_draws = int(mem.get("holdout_draws", 0))

    run = EvolutionRun(data, seed=seed, initial_tested=init_tested,
                       initial_stagnation=init_stagnation,
                       initial_champion_version=g0.version,
                       initial_holdout_draws=init_holdout_draws)
    res = run.run(generations=n, n_blind=14)
    acct.lineage.extend(res.get("generations", []))
    acct.researcher_memory = {
        "champion_version": run.tested_version,
        "tested": [[list(pair) for pair in k] for k in run.tested],
        "stagnation": run.stagnation,
        "holdout_draws": run.holdout_draws,
    }
    final = Genome.champion()
    if final.version != g0.version:
        acct.genome = final
        acct.save(state_path)
        print(f"[evolve] champion promoted to v{final.version}")
    else:
        acct.save(state_path)
        print("[evolve] champion held")


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
    elif cmd == "holdout-margin-audit":
        _cmd_holdout_margin_audit(acct)
    elif cmd == "regime":
        _cmd_regime(acct)
    elif cmd == "fold-dd-blindspot":
        _cmd_fold_dd_blindspot(acct)
    elif cmd == "tick-dry-run":
        _cmd_tick_dry_run(acct)
    elif cmd == "evolve-dry-run":
        _cmd_evolve_dry_run(acct)
    elif cmd == "tick":
        _cmd_tick(acct, state_path)
    elif cmd == "evolve":
        _cmd_evolve(acct, state_path)


if __name__ == "__main__":
    main()
