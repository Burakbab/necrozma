"""THE EVOLUTION LOOP.

    Researcher proposes  ->  Evaluator walk-forwards  ->  Superior Judge commits

The Evaluator is the honest broker. It never gets an opinion; it produces
numbers on data the proposal was not derived from. The Superior Judge applies
the constitution's acceptance rules and is the only thing that can write a new
champion genome.

Three anti-self-delusion measures live here:

  * **Walk-forward folds.** A challenger is scored on several disjoint future
    slices, not one. Aggregate fitness is penalised for variance across folds:
    a strategy that works in one fold and dies in the next isn't a strategy,
    it's a coincidence that hasn't been caught yet.

  * **Sealed holdout.** The newest slice of history is untouched during search
    and used only for the final confirmation. Anything that only looks good
    until it meets the holdout gets rejected there.

  * **Multiple-testing penalty.** Testing 40 mutations and crowning the best
    one is how you manufacture a champion out of noise. The required margin
    scales with how many candidates were tried.
"""
from __future__ import annotations

import json
import math
import os
import re
import time
from dataclasses import asdict
from typing import Any

import numpy as np

from agents.researcher import Researcher, diagnose
from constitution import (FOLD_CONSISTENCY_WEIGHT, HOLDOUT_FRAC, N_FOLDS,
                          RANK_FLOOR, accepts, fitness, holdout_accepts,
                          ranking_fitness)
from core.genome import Genome
from core.types import Mutation
from loop.engine import run_backtest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LINEAGE_PATH = os.path.join(ROOT, "state", "lineage.jsonl")


def rolling_folds(search_end: float, base_n_folds: int = N_FOLDS,
                   overlap: float = 0.5) -> list[tuple[float, float]]:
    """Overlapping, fixed-width windows spanning the searchable region.

    `fold-scheme` (raising n_folds on the fixed disjoint split) shrinks every
    window as the count grows, and at n_folds=8 one window came within 25 bars
    of run_backtest's hard minimum and another failed a hard gate outright --
    see AGENTS.md's fold-scheme entries. This is the other way to get more
    reads of the same span: keep window width fixed at whatever
    Evaluator.folds() already uses for `base_n_folds`, and slide that
    fixed-size window across the region instead of subdividing it, so no
    window ever shrinks below its base_n_folds size. The windows overlap and
    are therefore not independent draws -- this is a smoothing diagnostic on
    how much a single dominant window (e.g. the permanent fold-2 melt-up) can
    still swing aggregate_fitness, not a replacement evaluation scheme.

    overlap=0.0 reproduces Evaluator.folds()'s own disjoint edges at
    n_folds=base_n_folds (same count, same windows); overlap approaching 1.0
    produces many nearly-identical windows one bar apart.
    """
    if not (0.0 <= overlap < 1.0):
        raise ValueError("overlap must be in [0, 1)")
    if base_n_folds < 1:
        raise ValueError("base_n_folds must be >= 1")
    width = search_end / base_n_folds
    stride = width * (1.0 - overlap)
    if stride <= 0.0:
        raise ValueError("stride must be positive")
    windows = []
    start = 0.0
    while start + width <= search_end + 1e-9:
        windows.append((start, min(start + width, search_end)))
        start += stride
    return windows


def fitness_decomposition(fold_fits: list[float]) -> dict[str, float]:
    """Split aggregate_fitness into its mean and consistency-penalty terms.

    Evaluator.evaluate scores a genome as
    ``mean(fold_fits) - FOLD_CONSISTENCY_WEIGHT * std(fold_fits)``. fold-scheme
    and rolling-folds both showed that changing the fold windowing swings that
    single aggregate number, but the aggregate alone can't say *why*: a swing
    could come from the mean term (the outlier fold pulling the average) or
    from the penalty term (the cross-fold spread the FOLD_CONSISTENCY_WEIGHT
    std penalty reads). The rolling-folds run hypothesised the penalty term is
    the culprit -- adding more overlapping windows adds variance to std at
    least as fast as it dilutes the outlier's share of the mean. This returns
    both terms separately so that hypothesis is measurable, not asserted.

    ``mean_term - penalty_term`` reconstructs aggregate_fitness exactly (same
    np.mean/np.std this uses), so the decomposition is an identity, not an
    approximation. Empty input returns -inf aggregate with zero terms, matching
    Evaluator.evaluate's own empty-folds branch.
    """
    if not fold_fits:
        return {"mean_term": 0.0, "std": 0.0, "penalty_term": 0.0,
                "aggregate_fitness": float("-inf"), "n_folds": 0}
    arr = np.asarray(fold_fits, dtype=float)
    mean_term = float(np.mean(arr))
    std = float(np.std(arr))
    penalty_term = float(FOLD_CONSISTENCY_WEIGHT * std)
    return {"mean_term": mean_term, "std": std, "penalty_term": penalty_term,
            "aggregate_fitness": mean_term - penalty_term,
            "n_folds": int(arr.size)}


def capped_fitness_decomposition(fold_fits: list[float], cap_z: float = 1.0) -> dict[str, Any]:
    """Winsorize the mean term against a single dominant fold, leaving the
    consistency-penalty term untouched, and report both the plain and capped
    aggregate side by side.

    fitness-decomp (2026-08-20) settled that aggregate_fitness's swing across
    fold schemes rides the *mean* term (one outlier fold), not the
    FOLD_CONSISTENCY_WEIGHT * std penalty term, in all three real champions.
    regime-folds' n_subwindows/n_folds sweep (2026-08-21) then showed that
    *isolating* the outlier into its own fold is double-edged -- it helps at
    low fold counts but isolating a weak fold the same way costs more than it
    gains at higher counts. That leaves the fix AGENTS.md's Current state
    flagged as the sharper remaining option: cap the outlier's pull on the
    mean term directly, rather than reshuffling which folds exist at all.

    This winsorizes each fold fitness to a ceiling of ``mean(fold_fits) +
    cap_z * std(fold_fits)`` (a standard symmetric-from-above outlier cap --
    values below the ceiling are untouched, nothing is capped from below,
    since the concern here is one fold pulling the mean *up*, not down) before
    taking the mean. The ceiling and which folds get capped are computed from
    the *original* fold_fits, so this is deterministic and not iterative. The
    consistency-penalty term is deliberately computed from the ORIGINAL
    (uncapped) fold_fits, not the capped ones: that penalty already exists to
    punish cross-fold spread, so capping it too would double-count the same
    concern the mean-capping is meant to isolate -- this diagnostic asks
    whether capping the mean term ALONE stabilizes the aggregate, not whether
    capping everything does.

    Degenerate cases: a single fold or zero-spread fold set has std=0, so the
    ceiling equals the mean and nothing gets capped -- ``capped_mean_term ==
    mean_term`` exactly, matching fitness_decomposition's own single-fold/
    zero-spread behavior. Empty input returns the same -inf/zero shape
    fitness_decomposition uses for its empty branch.
    """
    if not fold_fits:
        return {"mean_term": 0.0, "capped_mean_term": 0.0, "std": 0.0,
                "penalty_term": 0.0, "aggregate_fitness": float("-inf"),
                "capped_aggregate_fitness": float("-inf"),
                "n_folds": 0, "n_capped": 0, "cap_z": float(cap_z)}
    arr = np.asarray(fold_fits, dtype=float)
    mean_term = float(np.mean(arr))
    std = float(np.std(arr))
    penalty_term = float(FOLD_CONSISTENCY_WEIGHT * std)
    ceiling = mean_term + cap_z * std
    capped = np.minimum(arr, ceiling)
    n_capped = int(np.sum(arr > ceiling + 1e-12))
    capped_mean_term = float(np.mean(capped))
    return {"mean_term": mean_term, "capped_mean_term": capped_mean_term,
            "std": std, "penalty_term": penalty_term,
            "aggregate_fitness": mean_term - penalty_term,
            "capped_aggregate_fitness": capped_mean_term - penalty_term,
            "n_folds": int(arr.size), "n_capped": n_capped,
            "cap_z": float(cap_z)}


def regime_concentration(window_returns: list[float]) -> dict[str, Any]:
    """Quantify how concentrated the searchable region's compounded growth is
    across contiguous sub-windows -- genome-independent.

    fitness-decomp (2026-08-20) settled that aggregate_fitness's instability
    across fold schemes is driven by the *mean* of the fold fitnesses, not the
    FOLD_CONSISTENCY_WEIGHT penalty term, in all three real champions. The mean
    moves because one window -- fold 2 in the fixed 3-fold split, a permanent
    +200% melt-up per the `regime` diagnostic -- dominates the average. Every
    run since lands on the same untried fix: a regime-stratified fold scheme
    that spreads that melt-up across folds so no single fold is a permanent
    outlier. But that fix needs engine work `run_backtest` can't do yet
    (folds would become non-contiguous unions of bars), so before committing
    to it, one number has gone unmeasured: is the melt-up ISOLATED to a tight
    calendar stretch (stratification would help) or DIFFUSE across the region
    (it wouldn't, and the effort should go to MULTIPLE_TESTING_SIGMA instead)?
    This measures exactly that.

    Each contiguous window's contribution to the region's total compounded
    growth is its log-return ``log(1 + r)``; those sum across the region to its
    total log-growth (compounding is additive in logs). Concentration is
    reported over the ABSOLUTE log-returns, so a deep crash counts as a large
    contribution rather than cancelling a melt-up out -- both are exactly the
    kind of dominant single window that swings the fold mean. Shares are
    ``p_i = |L_i| / sum_j |L_j|``; ``hhi = sum p_i^2`` runs from ``1/n``
    (perfectly even) to ``1`` (all in one window); ``top_share`` is the single
    largest with the window index that carries it; ``concentration_ratio =
    top_share * n`` is how many times its even share the richest window holds
    (1.0 = even, >1 = concentrated). Empty input returns zeros.
    """
    n = len(window_returns)
    if n == 0:
        return {"n_windows": 0, "shares": [], "hhi": 0.0, "top_index": -1,
                "top_share": 0.0, "top_return": 0.0, "even_share": 0.0,
                "concentration_ratio": 0.0, "total_log_growth": 0.0,
                "total_return": 0.0}
    logs = [math.log(max(1.0 + r, 1e-12)) for r in window_returns]
    abs_logs = [abs(x) for x in logs]
    total_abs = sum(abs_logs)
    if total_abs <= 0.0:
        shares = [1.0 / n] * n
    else:
        shares = [x / total_abs for x in abs_logs]
    hhi = float(sum(s * s for s in shares))
    top_index = max(range(n), key=lambda i: shares[i])
    top_share = float(shares[top_index])
    even_share = 1.0 / n
    total_log = float(sum(logs))
    return {"n_windows": n, "shares": shares, "hhi": hhi,
            "top_index": int(top_index), "top_share": top_share,
            "top_return": float(window_returns[top_index]),
            "even_share": even_share,
            "concentration_ratio": top_share / even_share,
            "total_log_growth": total_log,
            "total_return": float(math.exp(total_log) - 1.0)}


def regime_stratified_groups(window_returns: list[float], n_folds: int) -> list[list[int]]:
    """Assign sub-window indices to `n_folds` groups by greedy longest-
    processing-time (LPT) balancing on each window's |log(1+r)| weight -- the
    same weight `regime_concentration` shares its `concentration_ratio` from.

    regime-scan (2026-08-20) measured the searchable region's compounded
    growth as concentrated ~2.5x its even share in one or two sub-windows, and
    fitness-decomp (2026-08-20) showed that concentration reaching
    aggregate_fitness's mean term (not the consistency penalty) is what makes
    it swing across fold schemes -- the fixed 3-fold calendar split just
    happens to trap the whole melt-up in one fold. This groups finer
    sub-windows into folds so no fold hoards a disproportionate share of the
    region's growth instead. AGENTS.md's item 2 assumed this needed
    `run_backtest` to replay a non-contiguous union of bars; it doesn't --
    `Evaluator.evaluate_grouped` scores a group by backtesting each of its
    sub-windows independently (state resets at each boundary, same as at
    every existing fold boundary) and merging the results, so this function
    only needs to produce the *grouping*, which is genome-independent.

    LPT: sort sub-windows by descending weight (ties broken by ascending
    index, for determinism), then repeatedly assign the next-heaviest
    sub-window to whichever fold currently holds the least total weight
    (ties broken by lowest fold index). This is the standard heuristic for
    balancing a fixed number of bins by load and is optimal-ish for makespan,
    not just plausible.

    `n_folds` must be >= 1. More folds than sub-windows leaves the extra
    folds empty (their fitness floors at RANK_FLOOR at evaluation time, same
    as `evaluate()`'s own empty-folds branch). Empty `window_returns` returns
    `n_folds` empty groups.
    """
    if n_folds < 1:
        raise ValueError("n_folds must be >= 1")
    groups: list[list[int]] = [[] for _ in range(n_folds)]
    n = len(window_returns)
    if n == 0:
        return groups
    weights = [abs(math.log(max(1.0 + r, 1e-12))) for r in window_returns]
    order = sorted(range(n), key=lambda i: (-weights[i], i))
    totals = [0.0] * n_folds
    for i in order:
        j = min(range(n_folds), key=lambda k: (totals[k], k))
        groups[j].append(i)
        totals[j] += weights[i]
    return groups


class Evaluator:
    """Minor judge for the evolution track. Reports numbers, never opinions."""

    name = "evaluator"

    def __init__(self, data: dict, n_folds: int = N_FOLDS,
                 holdout_frac: float = HOLDOUT_FRAC):
        self.data = data
        self.n_folds = n_folds
        self.search_end = 1.0 - holdout_frac      # search may never look past here
        self.holdout = (self.search_end, 1.0)

    def folds(self) -> list[tuple[float, float]]:
        """Disjoint, chronological slices of the searchable region."""
        edges = np.linspace(0.0, self.search_end, self.n_folds + 1)
        return [(float(edges[i]), float(edges[i + 1])) for i in range(self.n_folds)]

    def evaluate(self, g: Genome, folds: list[tuple[float, float]] | None = None,
                 log_detail: bool = False) -> dict[str, Any]:
        folds = folds or self.folds()
        per_fold, fits = [], []
        for a, b in folds:
            r = run_backtest(g, self.data, a, b, log_detail=log_detail)
            if "error" in r:
                per_fold.append({"window": [a, b], "error": r["error"]})
                fits.append(RANK_FLOOR)
                continue
            per_fold.append({"window": [a, b], "stats": r["stats"],
                             "fitness": r["fitness"],
                             "rank_fitness": ranking_fitness(r["stats"]),
                             "benchmark": r.get("benchmark", {}),
                             "edge": r.get("edge", {})})
            fits.append(ranking_fitness(r["stats"]))

        if not fits:
            agg = float("-inf")
        else:
            # mean minus cross-fold spread: consistency is part of the score,
            # not a footnote. One great fold and one disaster is not an edge.
            agg = float(np.mean(fits) - FOLD_CONSISTENCY_WEIGHT * np.std(fits))

        # aggregate stats across folds, for the acceptance gates
        merged = self._merge([f for f in per_fold if "stats" in f])
        return {"folds": per_fold, "fold_fitness": fits,
                "aggregate_fitness": agg, "stats": merged,
                "edge": self._merge_edge([f for f in per_fold if f.get("edge")])}

    def evaluate_grouped(self, g: Genome, sub_windows: list[tuple[float, float]],
                          groups: list[list[int]],
                          log_detail: bool = False) -> dict[str, Any]:
        """Evaluate a genome under folds built from `regime_stratified_groups`
        instead of one contiguous slice per fold. Backs the `regime-folds`
        diagnostic -- the first real test of the regime-stratified fold idea
        that doesn't need an engine or constitution change (see that
        function's docstring for why).

        Each sub-window in a group gets its own independent `run_backtest`
        call -- no non-contiguous replay, genome state (positions, indicator
        lookback windows) simply resets at every sub-window boundary within a
        fold, exactly as it already does at every boundary between today's
        three calendar folds. A group's sub-window results are combined with
        the same trade-weighted `_merge` this class already uses to combine
        folds for the acceptance gates, then scored with the same
        `ranking_fitness` used per-fold in `evaluate()`. The final
        `aggregate_fitness` uses the identical `mean - FOLD_CONSISTENCY_WEIGHT
        * std` formula across folds, so its number is directly comparable to
        `evaluate()`'s own `aggregate_fitness` at the same fold count -- this
        is an approximation of a genuinely non-contiguous single replay (which
        would need `run_backtest` itself to change), not that replay, but it
        needs nothing checksummed to measure whether balancing regime
        concentration across folds stabilizes the aggregate.
        """
        per_fold, fits = [], []
        for group in groups:
            sub_results = []
            for idx in group:
                a, b = sub_windows[idx]
                r = run_backtest(g, self.data, a, b, log_detail=log_detail)
                if "error" not in r:
                    sub_results.append(r)
            windows = [sub_windows[i] for i in group]
            if not sub_results:
                per_fold.append({"sub_windows": windows,
                                 "error": "no valid sub-windows"})
                fits.append(RANK_FLOOR)
                continue
            merged = self._merge([{"stats": r["stats"]} for r in sub_results])
            fit = ranking_fitness(merged)
            per_fold.append({"sub_windows": windows, "stats": merged,
                             "fitness": fit, "n_sub_windows": len(group),
                             "n_sub_windows_ok": len(sub_results)})
            fits.append(fit)

        if not fits:
            agg = float("-inf")
        else:
            agg = float(np.mean(fits) - FOLD_CONSISTENCY_WEIGHT * np.std(fits))
        return {"folds": per_fold, "fold_fitness": fits, "aggregate_fitness": agg}

    @staticmethod
    def _merge_edge(folds: list[dict]) -> dict[str, Any]:
        """Mean edge across folds, plus how many of them actually beat the
        benchmark. Three folds averaging positive because one was spectacular
        is a different claim from three folds that each cleared the bar."""
        if not folds:
            return {}
        e = [f["edge"] for f in folds]
        beat = sum(1 for x in e if x.get("beat_benchmark"))
        return {
            "excess_return": float(np.mean([x.get("excess_return", 0.0) for x in e])),
            "excess_return_annual": float(np.mean(
                [x.get("excess_return_annual", 0.0) for x in e])),
            "excess_sharpe": float(np.mean([x.get("excess_sharpe", 0.0) for x in e])),
            "drawdown_delta": float(np.mean([x.get("drawdown_delta", 0.0) for x in e])),
            "trades_per_year": float(np.mean([x.get("trades_per_year", 0.0) for x in e])),
            "folds_beating_benchmark": f"{beat}/{len(e)}",
        }

    @staticmethod
    def _merge(folds: list[dict]) -> dict[str, Any]:
        if not folds:
            return {"error": "no folds"}
        s = [f["stats"] for f in folds]
        return {
            "trades": sum(x.get("trades", 0) for x in s),
            "bars": sum(x.get("bars", 0) for x in s),
            "sortino": float(np.mean([x.get("sortino", 0) for x in s])),
            "sharpe": float(np.mean([x.get("sharpe", 0) for x in s])),
            "max_dd": float(np.min([x.get("max_dd", 0) for x in s])),
            "turnover_annual": float(np.mean([x.get("turnover_annual", 0) for x in s])),
            "win_rate": float(np.mean([x.get("win_rate", 0) for x in s])),
            "total_return": float(np.mean([x.get("total_return", 0) for x in s])),
            "halt_count": sum(x.get("halt_count", 0) for x in s),
        }

    def holdout_check(self, g: Genome) -> dict[str, Any]:
        r = run_backtest(g, self.data, *self.holdout, log_detail=False)
        if "error" in r:
            return {"error": r["error"]}
        return {"stats": r["stats"], "fitness": r["fitness"],
                "benchmark": r.get("benchmark", {}), "edge": r.get("edge", {})}

    def continuous_max_dd(self, g: Genome,
                           folds: list[tuple[float, float]] | None = None) -> float | None:
        """One unbroken backtest over the full span `folds` covers, for closing
        the blind spot `fold-dd-blindspot` found (2026-08-22, see AGENTS.md
        item 2 and AMENDMENTS.md): `_merge`'s max_dd is the worst of each
        fold's own INDEPENDENTLY backtested local peak-to-trough -- state
        (positions, indicator lookback) resets at every fold boundary, so a
        true drawdown that starts near the end of one fold and bottoms out in
        the next is invisible to every individual fold's own local number,
        and therefore invisible to the merged number `accepts()`/`fitness()`
        gate on. This runs the identical genome over `[folds[0][0],
        folds[-1][1]]` with no boundary resets, i.e. what actually would have
        happened. Not used as the everyday scoring path -- see `evaluate()`'s
        own docstring for why the fold-local numbers stay the search/ranking
        signal -- callers that need the closed gate call this explicitly (see
        `EvolutionRun.generation()`, the one place a real promotion decision
        gets made). Returns None (not 0.0) if there is nothing to backtest or
        the backtest errors, so a caller never mistakes "unknown" for "no
        drawdown".
        """
        folds = folds or self.folds()
        if not folds:
            return None
        r = run_backtest(g, self.data, folds[0][0], folds[-1][1], log_detail=False)
        if "error" in r:
            return None
        return float(r["stats"].get("max_dd", 0.0))


def dd_corrected_stats(evaluator: "Evaluator", g: Genome, stats: dict[str, Any],
                        folds: list[tuple[float, float]] | None = None) -> dict[str, Any]:
    """A copy of `stats` with `max_dd` replaced by the worse (more negative)
    of its own value and `evaluator.continuous_max_dd(g, folds)` -- the
    fold-dd-blindspot fix (2026-08-22, AGENTS.md item 2 / AMENDMENTS.md)
    applied at the one place a real promotion decision reads `max_dd`:
    `constitution.accepts()`'s hard-fail and drawdown-regression checks.

    Never loosens the gate: if the continuous replay can't run (empty folds,
    a backtest error) `stats` comes back unchanged, same as before this fix
    existed. `stats` itself is never mutated -- callers that also use the
    original (e.g. for logging/diagnosis) keep the fold-local number.
    """
    corrected = dict(stats)
    cont = evaluator.continuous_max_dd(g, folds)
    if cont is not None:
        corrected["max_dd"] = min(corrected.get("max_dd", 0.0), cont)
    return corrected


def dd_trust_continuous_stats(evaluator: "Evaluator", g: Genome, stats: dict[str, Any],
                               folds: list[tuple[float, float]] | None = None) -> dict[str, Any]:
    """Diagnostic-only sibling of `dd_corrected_stats()` -- NOT wired into
    `accepts()`/`EvolutionRun.generation()`, and never will be without a
    deliberate decision to change the live gate's policy. Exists only so a
    read-only diagnostic (`succession-audit`) can show what the gate's
    verdict would look like under a different, two-sided correction policy,
    for comparison against the current one-sided one.

    `dd_corrected_stats()` takes `min(fold-merged, continuous)`, which can
    only ever tighten the gate: correct for the original `fold-dd-blindspot`
    direction (fold-merged UNDERSTATING true risk, since each fold's local
    peak-to-trough resets at its boundary and misses a drawdown that spans
    two folds), but blind to the opposite direction the 2026-08-22
    `succession-audit` diagnostic found in champion v2 -- fold-merged can
    also OVERSTATE true risk, when a fold rebases to a fresh, lower local
    peak and a decline that would be a modest fraction of the real
    long-accumulated peak becomes a much larger fraction of that reset
    peak. `min()` has no way to recover a truer, better continuous number
    from an overstated fold-local one.

    This function instead always trusts `continuous_max_dd()` -- the one
    unbroken replay, "what actually would have happened" -- when it's
    available, replacing `max_dd` outright rather than taking the worse of
    the two. That is a genuine loosening in the overstatement case, which is
    exactly why it stays a diagnostic-only comparison point and not a
    replacement for the conservative gate: whether the gate should ever
    actually loosen is a real design decision (see AGENTS.md item 2's
    still-open succession/demotion thread), not something a read-only
    report should decide by quietly using a different function.
    """
    corrected = dict(stats)
    cont = evaluator.continuous_max_dd(g, folds)
    if cont is not None:
        corrected["max_dd"] = cont
    return corrected


class EvolutionRun:
    def __init__(self, data: dict, seed: int | None = 7, verbose: bool = True,
                 initial_tested: set | None = None, initial_stagnation: int = 0,
                 initial_champion_version: int | None = None,
                 initial_holdout_draws: int = 0):
        self.data = data
        self.evaluator = Evaluator(data)
        self.researcher = Researcher(seed)
        self.verbose = verbose
        self.log: list[dict] = []
        # Proposals already ruled out against the current champion, and how
        # long that champion has stood. Both reset the moment it is beaten.
        #
        # Seeded from live_state.json's researcher_memory (keyed by champion
        # version) when the caller has it -- otherwise every fresh `evolve` CLI
        # invocation forgets what it already rejected against an unbeaten
        # champion and re-spends backtests re-discovering the same near-miss
        # candidates generation after generation, invocation after invocation.
        self.tested: set = set(initial_tested or ())
        self.tested_version: int | None = initial_champion_version
        self.stagnation = int(initial_stagnation)
        # Draws against the sealed holdout, counted for the life of the
        # lineage. Deliberately NOT reset when the champion changes: the
        # holdout is the same slice of history before and after a
        # promotion, so a promotion does not restore its innocence.
        self.holdout_draws = int(initial_holdout_draws)

    def _say(self, msg: str) -> None:
        if self.verbose:
            print(msg, flush=True)

    def generation(self, champion: Genome, n_blind: int = 14) -> tuple[Genome, dict]:
        t0 = time.time()

        # 1. what does the champion actually do, and where does it leak?
        diag_run = run_backtest(champion, self.data, 0.0, self.evaluator.search_end,
                                log_detail=True)
        diag = diagnose(diag_run)
        champ_eval = self.evaluator.evaluate(champion)
        champ_fit = champ_eval["aggregate_fitness"]
        self._say(f"  champion v{champion.version}: fitness {champ_fit:.3f}  "
                  f"({diag['trades']} trades, win {diag['win_rate']:.0%}, "
                  f"stops {diag['stop_share']:.0%}, halts {diag['halt_count']})")

        if self.tested_version != champion.version:
            self.tested = set()
            self.tested_version = champion.version
            self.stagnation = 0

        # 2. propose — skipping anything already rejected against this champion
        mutations = self.researcher.propose(
            champion, diag, n_blind=n_blind, exclude=self.tested,
            boldness=float(self.stagnation))
        for m in mutations:
            self.tested.add(self.researcher.key(m))
        # Multiple testing is CUMULATIVE against a fixed champion: every
        # candidate ever tried against it is another draw from the same urn.
        # Counting only this generation's batch would understate the bias and
        # let a long unbeaten search crown noise.
        n_tested = len(self.tested)
        self._say(f"  researcher: {len(mutations)} new proposals "
                  f"({n_tested} tried against v{champion.version}, "
                  f"boldness {self.stagnation})")
        if not mutations:
            self.stagnation += 1
            self._say("  researcher exhausted its ideas this round")
            self._record({"champion_version": champion.version,
                          "champion_fitness": champ_fit, "n_candidates": 0,
                          "note": "no new proposals"})
            return champion, {"champion_version": champion.version, "n_candidates": 0}

        # 3. evaluate every one on walk-forward folds
        results = []
        for m in mutations:
            child = champion.child(list(m.patch.items()), note=m.hypothesis)
            ev = self.evaluator.evaluate(child)
            results.append((ev["aggregate_fitness"], m, child, ev))
        results.sort(key=lambda x: (-np.inf if not np.isfinite(x[0]) else -x[0]))

        # 4. the Superior Judge rules on the best candidate
        gen_record = {
            "champion_version": champion.version,
            "champion_fitness": champ_fit,
            "champion_stats": champ_eval["stats"],
            "champion_edge": champ_eval.get("edge", {}),
            "diagnosis": diag,
            "n_candidates": len(mutations),
            "n_tested_cumulative": n_tested,
            "holdout_draws_before": self.holdout_draws,
            "stagnation": self.stagnation,
            "top": [{"fitness": (None if not np.isfinite(f) else round(f, 4)),
                     "kind": m.kind, "target": m.target,
                     "hypothesis": m.hypothesis, "patch": m.patch}
                    for f, m, _, _ in results[:8]],
            "seconds": 0.0,
        }

        # Close the fold-boundary max_dd blind spot (fold-dd-blindspot,
        # 2026-08-22, see AGENTS.md item 2 and AMENDMENTS.md) right where a
        # real promotion decision gets made: accepts()'s hard-fail and
        # drawdown-regression checks read whichever max_dd sits in these
        # stats dicts. Only generations that reach this loop with at least
        # one finite candidate pay for the champion's continuous-replay
        # backtest, cached across the loop since the champion doesn't change
        # between candidates; each challenger pays for its own, but only the
        # up-to-3 candidates ranked highest ever reach this gate at all.
        champ_gate_stats = None
        for fit, m, child, ev in results[:3]:
            if not np.isfinite(fit):
                continue
            if champ_gate_stats is None:
                champ_gate_stats = dd_corrected_stats(self.evaluator, champion, champ_eval["stats"])
            chal_gate_stats = dd_corrected_stats(self.evaluator, child, ev["stats"])

            ok, why = accepts(champ_gate_stats, chal_gate_stats,
                              n_candidates=n_tested,
                              complexity_delta=max(0, m.complexity_delta),
                              champion_score=champ_fit,
                              challenger_score=fit)
            if not ok:
                gen_record.setdefault("rejections", []).append(
                    {"target": m.target, "why": why, "fold_fitness": round(fit, 4)})
                continue

            # 5. sealed holdout — the last honest test
            ho_champ = self.evaluator.holdout_check(champion)
            ho_chal = self.evaluator.holdout_check(child)
            # Every challenger that reaches this gate is one more draw
            # against the same bars. Count it before judging it.
            self.holdout_draws += 1
            if ho_chal.get("error"):
                ho_ok = False
                ho_why = f"challenger produced no holdout result: {ho_chal['error']}"
            else:
                ho_ok, ho_why = holdout_accepts(
                    ho_champ.get("fitness", float("-inf")),
                    ho_chal.get("fitness", float("-inf")),
                    n_draws=self.holdout_draws)
            gen_record["holdout"] = {"champion": ho_champ.get("fitness"),
                                     "challenger": ho_chal.get("fitness"),
                                     "draws": self.holdout_draws,
                                     "passed": bool(ho_ok), "why": ho_why}
            if not ho_ok:
                gen_record.setdefault("rejections", []).append({
                    "target": m.target, "why": ho_why,
                    "fold_fitness": round(fit, 4)})
                continue

            child.promote()
            gen_record["accepted"] = {
                "new_version": child.version, "kind": m.kind, "target": m.target,
                "edge": ev.get("edge", {}), "holdout_edge": ho_chal.get("edge", {}),
                "hypothesis": m.hypothesis, "patch": m.patch,
                "fitness": round(fit, 4), "was": round(champ_fit, 4), "why": why}
            gen_record["seconds"] = round(time.time() - t0, 1)
            self._say(f"  ACCEPTED v{child.version}: {m.hypothesis}")
            self._say(f"    fitness {champ_fit:.3f} -> {fit:.3f} | {why}")
            self._record(gen_record)
            return child, gen_record

        gen_record["seconds"] = round(time.time() - t0, 1)
        self.stagnation += 1
        self._say(f"  no proposal cleared the bar (best {results[0][0]:.3f} "
                  f"vs champion {champ_fit:.3f}) — champion holds")
        self._record(gen_record)
        return champion, gen_record

    def run(self, generations: int = 5, n_blind: int = 14) -> dict[str, Any]:
        g = Genome.champion()
        history = []
        for i in range(generations):
            self._say(f"\n--- generation {i + 1}/{generations}")
            g, rec = self.generation(g, n_blind=n_blind)
            history.append(rec)
        return {"final_version": g.version, "generations": history}

    @staticmethod
    def _record(rec: dict) -> None:
        os.makedirs(os.path.dirname(LINEAGE_PATH), exist_ok=True)
        with open(LINEAGE_PATH, "a") as f:
            f.write(json.dumps(rec, default=str) + "\n")


_HOLDOUT_REJECTION_RE = re.compile(
    r"failed sealed holdout: (?P<challenger>-?\d+\.\d+) did not clear champion "
    r"(?P<champion>-?\d+\.\d+) \+ margin (?P<margin>\d+\.\d+) "
    r"\((?P<draws>\d+) cumulative draws")


def summarize_holdout_pressure(lineage: list[dict], champion_version: int) -> dict[str, Any]:
    """Read-only summary of `EvolutionRun.generation()`'s own lineage records,
    scoped to whichever generations ran while `champion_version` was reigning.

    Separates two failure modes that both just look like "champion held": a
    generation where nothing even cleared the fold-aggregate gate
    (`fold_blocked_generations`), versus one where a real fold-aggregate
    winner reached the sealed holdout and was rejected only there -- the
    entrenchment pattern the 2026-08-18 4h-shadow work first named ("a lucky
    holdout draw at promotion time can entrench a champion against
    genuinely-better-on-search-folds challengers"). Answers whether the
    *live* champion shows the pattern using lineage already recorded in
    `live_state.json` -- no new `evolve` run required.

    `generation()` checks up to 3 top-ranked candidates per generation and
    holdout-tests every one that clears the fold-aggregate gate (not just the
    single best), but only the *last* one checked survives into
    `gen_record["holdout"]` -- the rest are visible only as rejection
    entries, each carrying its own `fold_fitness` alongside a `why` string in
    `holdout_accepts()`'s fixed format. Parsing that format (instead of
    reading `gen_record["holdout"]` alone) is what recovers every individual
    holdout draw, not just one representative per generation -- verified by
    `tests/test_holdout_pressure.py` constructing rejection entries from the
    real `constitution.holdout_accepts()` output, so a template change there
    would break the parser loudly rather than silently under-counting draws.
    """
    gens = [e for e in lineage if e.get("champion_version") == champion_version]
    draws = []
    no_proposal_generations = fold_blocked_generations = accepted_generations = 0
    for e in gens:
        if not e.get("n_candidates"):
            no_proposal_generations += 1
            continue
        if e.get("accepted"):
            accepted_generations += 1
            continue
        saw_holdout = False
        for r in e.get("rejections", []):
            m = _HOLDOUT_REJECTION_RE.search(r.get("why", ""))
            if not m:
                continue
            saw_holdout = True
            draws.append({
                "fold_fitness": r.get("fold_fitness"),
                "champion_fold_fitness": e.get("champion_fitness"),
                "holdout_challenger": float(m["challenger"]),
                "holdout_champion": float(m["champion"]),
                "margin": float(m["margin"]),
                "cumulative_draws": int(m["draws"]),
            })
        if not saw_holdout:
            fold_blocked_generations += 1
    return {
        "champion_version": champion_version,
        "n_generations": len(gens),
        "no_proposal_generations": no_proposal_generations,
        "fold_blocked_generations": fold_blocked_generations,
        "accepted_generations": accepted_generations,
        "holdout_draws": draws,
    }


def raw_holdout_beats(holdout_draws: list[dict]) -> dict[str, Any]:
    """How many of `summarize_holdout_pressure`'s recorded rejections were
    only margin failures -- the challenger's raw sealed-holdout score already
    exceeded the champion's, just not by `required_margin()`'s additive
    amount.

    Exists to put a real, historical number on the entrenchment tension the
    2026-08-28 guardian-weighted shadow-evolve session quantified on 361
    freshly-generated shadow candidates (23% beat the champion's raw holdout
    score and were still rejected): this answers the same question using
    `live_state.json`'s own recorded lineage against the real v3 champion,
    no new search required. `holdout_draws` is `summarize_holdout_pressure`'s
    own `"holdout_draws"` list for one champion reign, in the chronological
    (append) order `EvolutionRun` recorded them.

    This is a lower-bound diagnostic, not a proposed replacement rule: a
    "raw beat" ignores multiple-testing risk entirely (`required_margin`
    exists precisely because the best of many noisy draws beats an equal
    champion by luck alone often enough to manufacture a lineage out of
    noise), so treat `n_raw_beats` as "how much of the rejection was the
    margin, not the sign" rather than "how many of these should have been
    promoted."

    `first_flip_index` only marks the first draw a naive zero-margin rule
    would have accepted -- every later draw in the same list was evaluated
    against the *actual* (unpromoted) champion, so once a real promotion had
    happened the champion, the fold ranking, and every subsequent draw would
    differ. Draws after the first flip are not independent counterfactuals;
    they are included in `flips` for completeness but should not be summed
    into a "this many promotions were missed" count.
    """
    flips = [d["holdout_challenger"] > d["holdout_champion"] for d in holdout_draws]
    first_flip_index = next((i for i, f in enumerate(flips) if f), None)
    return {
        "n_draws": len(holdout_draws),
        "n_raw_beats": sum(flips),
        "first_flip_index": first_flip_index,
        "flips": flips,
    }


def disagreement_scan(champion: Genome, evaluator: "Evaluator", researcher: "Researcher",
                       generations: int = 15, n_blind: int = 14,
                       initial_tested: set | None = None,
                       initial_stagnation: int = 0,
                       initial_holdout_draws: int = 0) -> dict[str, Any]:
    """Research-only instrumented replay of `EvolutionRun.generation()`'s exact
    proposal/gating pipeline, measuring how often raw `ranking_fitness` and
    excess-over-benchmark return disagree about which of champion/challenger
    is better -- at both the fold-aggregate stage (every candidate proposed
    each generation) and the sealed-holdout stage (only candidates that clear
    the fold-aggregate acceptance gate, the rarer and more consequential
    disagreement since it's the gate a real promotion is decided at).

    Formalises what four separate one-off throwaway shadow scripts measured
    by hand on 2026-08-29 (see AGENTS.md "Current state" 06:00, 10:17, 16:28,
    19:12 entries -- each classified "risky" (raw fitness favors the
    challenger, excess return doesn't) vs "conservative" (the reverse) by the
    same reasoning coded here) into one reusable, tested function instead of
    a fifth throwaway script.

    Mirrors `generation()`'s own calls exactly (`Researcher.propose`,
    `Evaluator.evaluate`, `dd_corrected_stats`, `constitution.accepts`,
    `Evaluator.holdout_check`, `constitution.holdout_accepts`, the same
    cumulative-tested-set and stagnation/boldness bookkeeping) but never
    calls `Genome.save()`/`.promote()`/`EvolutionRun._record()` -- an
    in-generation "would-promote" only swaps `champion` for a later
    generation's own diagnosis and proposals, exactly like the shadow
    scripts' own documented discipline of never persisting anything to disk.
    The caller decides what data the champion is scored against (a
    truncated/sandboxed `Evaluator` for a shadow calendar window, or the live
    one for the real thing) and whether `researcher`/`initial_tested`/
    `initial_stagnation`/`initial_holdout_draws` carry a champion's real
    `researcher_memory` or start blind.
    """
    tested: set = set(initial_tested or ())
    tested_version = champion.version
    stagnation = int(initial_stagnation)
    holdout_draws = int(initial_holdout_draws)
    fold_directions: list[str] = []
    holdout_directions: list[str] = []
    shadow_promotions = 0

    def _direction(champ_val: float, chal_val: float,
                    champ_excess: float | None, chal_excess: float | None) -> str | None:
        if champ_excess is None or chal_excess is None:
            return None
        fitness_favors_chal = chal_val > champ_val
        excess_favors_chal = chal_excess > champ_excess
        if fitness_favors_chal == excess_favors_chal:
            return "agree"
        return "risky" if fitness_favors_chal else "conservative"

    for _ in range(generations):
        diag_run = run_backtest(champion, evaluator.data, 0.0, evaluator.search_end,
                                log_detail=True)
        diag = diagnose(diag_run)
        champ_eval = evaluator.evaluate(champion)
        champ_fit = champ_eval["aggregate_fitness"]
        champ_excess = (champ_eval.get("edge") or {}).get("excess_return")

        if tested_version != champion.version:
            tested = set()
            tested_version = champion.version
            stagnation = 0

        mutations = researcher.propose(champion, diag, n_blind=n_blind,
                                        exclude=tested, boldness=float(stagnation))
        for m in mutations:
            tested.add(researcher.key(m))
        if not mutations:
            stagnation += 1
            continue
        n_tested = len(tested)

        results = []
        for m in mutations:
            child = champion.child(list(m.patch.items()), note=m.hypothesis)
            ev = evaluator.evaluate(child)
            results.append((ev["aggregate_fitness"], m, child, ev))
        results.sort(key=lambda x: (-np.inf if not np.isfinite(x[0]) else -x[0]))

        for fit, m, child, ev in results:
            if not np.isfinite(fit):
                continue
            chal_excess = (ev.get("edge") or {}).get("excess_return")
            direction = _direction(champ_fit, fit, champ_excess, chal_excess)
            if direction is not None:
                fold_directions.append(direction)

        champ_gate_stats = None
        promoted_this_gen = False
        for fit, m, child, ev in results[:3]:
            if not np.isfinite(fit):
                continue
            if champ_gate_stats is None:
                champ_gate_stats = dd_corrected_stats(evaluator, champion, champ_eval["stats"])
            chal_gate_stats = dd_corrected_stats(evaluator, child, ev["stats"])

            ok, _why = accepts(champ_gate_stats, chal_gate_stats, n_candidates=n_tested,
                               complexity_delta=max(0, m.complexity_delta),
                               champion_score=champ_fit, challenger_score=fit)
            if not ok:
                continue

            ho_champ = evaluator.holdout_check(champion)
            ho_chal = evaluator.holdout_check(child)
            holdout_draws += 1
            if ho_chal.get("error") or ho_champ.get("error"):
                continue
            ho_champ_fit = ho_champ.get("fitness", float("-inf"))
            ho_chal_fit = ho_chal.get("fitness", float("-inf"))
            ho_champ_excess = (ho_champ.get("edge") or {}).get("excess_return")
            ho_chal_excess = (ho_chal.get("edge") or {}).get("excess_return")
            direction = _direction(ho_champ_fit, ho_chal_fit, ho_champ_excess, ho_chal_excess)
            if direction is not None:
                holdout_directions.append(direction)

            ho_ok, _ho_why = holdout_accepts(ho_champ_fit, ho_chal_fit, n_draws=holdout_draws)
            if not ho_ok:
                continue

            champion = child   # in-memory only -- never .promote()'d, never saved
            shadow_promotions += 1
            promoted_this_gen = True
            break

        if not promoted_this_gen:
            stagnation += 1

    def _tally(directions: list[str]) -> dict[str, Any]:
        n = len(directions)
        disagreements = [d for d in directions if d != "agree"]
        risky = sum(1 for d in disagreements if d == "risky")
        conservative = sum(1 for d in disagreements if d == "conservative")
        return {
            "n": n,
            "disagreements": len(disagreements),
            "disagreement_rate": (len(disagreements) / n) if n else None,
            "risky": risky,
            "conservative": conservative,
        }

    return {
        "fold_stage": _tally(fold_directions),
        "holdout_stage": _tally(holdout_directions),
        "generations_run": generations,
        "final_champion_version": champion.version,
        "shadow_promotions": shadow_promotions,
        "final_stagnation": stagnation,
        "final_holdout_draws": holdout_draws,
    }
