"""THE CONSTITUTION — locked.

Everything in this package defines how the system is *graded*. The Researcher
may propose any change to the strategy layer; it may not propose a change to
anything in here. The Superior Judge verifies the checksum of this package at
startup and refuses to run if it moved without a human editing MANIFEST.

Why this exists: a self-modifying system whose reward function is inside its
own mutable surface will always find it cheaper to edit the scoreboard than to
learn the game. Locking the scoreboard is what makes the rest safe to leave
running unattended.

Only Burk edits this file, by hand.
"""
from __future__ import annotations

import hashlib
import math
import os
from typing import Any

# ---------------------------------------------------------------------------
# Fitness
# ---------------------------------------------------------------------------

MIN_TRADES = 30
MIN_BARS = 90
MAX_DD_HARD_FAIL = 0.40
DD_FREE_ALLOWANCE = 0.20
DD_PENALTY_WEIGHT = 2.0
TURNOVER_FREE = 50.0
TURNOVER_PENALTY_WEIGHT = 0.5

# Acceptance gates
DD_REGRESSION_TOLERANCE = 1.15     # challenger maxDD may be at most 15% worse
COMPLEXITY_COST_PER_UNIT = 0.05    # fitness margin required per unit of added complexity
MULTIPLE_TESTING_SIGMA = 0.08      # noise scale of a fold-aggregate fitness estimate
HOLDOUT_SIGMA = 2.0                # noise scale of a single sealed-holdout fitness estimate.
                                   # Calibrated 2026-08-21 from `holdout-noise`'s block-bootstrap
                                   # measurement of the real sealed-holdout return path across all
                                   # three real champions this account has had (boot_fitness_std in
                                   # fitness units: v1 ~1.48, v2 ~1.21, v3 ~2.04). Set at the highest
                                   # observed, not an average -- this is a safety floor and future
                                   # champions are unmeasured. holdout_accepts()'s own docstring
                                   # already argued a single holdout window is noisier than a
                                   # fold-aggregate; this is that argument with a number attached,
                                   # not a guess. Still likely an underestimate: it measures
                                   # realized-path resampling noise only, not the extra noise from
                                   # candidates arriving pre-selected by folds that correlate with
                                   # the holdout window. See AMENDMENTS.md.
CIRCUIT_BREAKER_DD = 0.25
CIRCUIT_BREAKER_COOLDOWN = 20      # bars frozen after a trip
CIRCUIT_BREAKER_FLATTEN = True     # liquidate on trip, don't hold bags through a crash

# Evolution search hygiene
HOLDOUT_FRAC = 0.15                # newest slice of history, never touched during search
N_FOLDS = 3                        # walk-forward folds used to judge a challenger
FOLD_CONSISTENCY_WEIGHT = 0.35     # penalty on cross-fold variance: a strategy that
                                   # works in one fold and dies in another is not a strategy


def fitness(stats: dict[str, Any]) -> float:
    """The single number the whole evolution loop optimises.

    Deliberately NOT total return. Return alone rewards leverage, luck and
    catastrophic risk-taking; over a long enough run those all end at zero.
    """
    if stats.get("error"):
        return float("-inf")
    if stats.get("trades", 0) < MIN_TRADES:
        return float("-inf")
    if stats.get("bars", 0) < MIN_BARS:
        return float("-inf")
    max_dd = abs(stats.get("max_dd", 0.0))
    if max_dd > MAX_DD_HARD_FAIL:
        return float("-inf")

    base = stats.get("sortino", 0.0)
    if not math.isfinite(base):
        base = 0.0
    dd_pen = DD_PENALTY_WEIGHT * max(0.0, max_dd - DD_FREE_ALLOWANCE)
    turn = stats.get("turnover_annual", 0.0)
    turn_pen = TURNOVER_PENALTY_WEIGHT * max(0.0, (turn - TURNOVER_FREE) / TURNOVER_FREE)
    return float(base - dd_pen - turn_pen)


RANK_FLOOR = -5.0


def ranking_fitness(stats: dict[str, Any]) -> float:
    """Fitness with a finite floor, for *ranking* candidates during search.

    `fitness()` returns -inf for anything that fails a hard gate, which is the
    correct verdict but destroys the gradient: if every candidate scores -inf
    the search is blind. Ranking uses a floor so search can still climb toward
    the gates; acceptance still uses the real `fitness()`, so a floored score
    can never buy a promotion.
    """
    f = fitness(stats)
    return RANK_FLOOR if f == float("-inf") else max(f, RANK_FLOOR)


def required_margin(n_candidates: int, complexity_delta: int,
                    sigma: float = MULTIPLE_TESTING_SIGMA) -> float:
    """How much better a challenger must be before we believe it.

    Test k noisy candidates and pick the winner, and it beats the truth by
    roughly sigma * sqrt(2 * ln k) on luck alone. That is the shape of the
    penalty — NOT linear in k.

    (v0.1 had this linear at 0.02/candidate, which set the bar at 0.46 for a
    24-candidate generation and made promotion arithmetically impossible on a
    Sortino-scaled metric. That was a mis-specification, not a safety property.
    The sqrt-log form is the standard correction for the expected maximum of k
    noisy estimates. The real defences against crowning noise — the cross-fold
    consistency penalty and the sealed holdout — are unchanged.)

    `sigma` defaults to `MULTIPLE_TESTING_SIGMA`, the fold-aggregate noise
    scale — that is the right constant for `accepts()`, which mines the
    fold-aggregate metric. `holdout_accepts()` passes `HOLDOUT_SIGMA` instead:
    a single sealed-holdout score is a noisier estimate than a fold-aggregate
    (fewer effective independent windows averaged), so the same k-candidate
    correction needs a larger sigma to mean the same thing.
    """
    mt = sigma * math.sqrt(2.0 * math.log(max(n_candidates, 2)))
    cx = COMPLEXITY_COST_PER_UNIT * max(0, complexity_delta)
    return mt + cx


def accepts(champion: dict[str, Any], challenger: dict[str, Any],
            n_candidates: int = 1, complexity_delta: int = 0,
            champion_score: float | None = None,
            challenger_score: float | None = None) -> tuple[bool, str]:
    """The acceptance rule. Returns (accept?, human-readable reason).

    `champion_score` / `challenger_score` are the **selection metric** — the
    fold-aggregate fitness that actually ranked the candidates. The margin is
    applied there, because that is where selection bias enters. `champion` and
    `challenger` are the merged fold stats, used for the hard gates and the
    drawdown-regression check.

    (Earlier this applied the multiple-testing margin to the merged stats,
    which rank nothing, while the fold-aggregate that does the ranking got no
    protection at all. Backwards on both counts: the metric being mined for a
    winner is the one that needs the correction. Falling back to the merged
    fitness when no score is supplied keeps the old call sites honest.)
    """
    f_champ = fitness(champion)
    f_chal = fitness(challenger)

    if f_chal == float("-inf"):
        return False, "challenger failed a hard gate (too few trades, too short, or drawdown > 40%)"

    s_champ = f_champ if champion_score is None else champion_score
    s_chal = f_chal if challenger_score is None else challenger_score

    margin = required_margin(n_candidates, complexity_delta)
    if s_chal <= s_champ + margin:
        return False, (f"selection fitness {s_chal:.3f} did not clear champion "
                       f"{s_champ:.3f} + required margin {margin:.3f}")

    # A challenger must not be worse on the merged record either — clearing the
    # selection metric while quietly degrading the aggregate is not progress.
    if f_chal < f_champ:
        return False, (f"merged fitness regressed: {f_chal:.3f} vs champion {f_champ:.3f}")

    dd_champ = abs(champion.get("max_dd", 0.0)) or 1e-9
    dd_chal = abs(challenger.get("max_dd", 0.0))
    if dd_chal > dd_champ * DD_REGRESSION_TOLERANCE:
        return False, (f"drawdown regression: {dd_chal:.1%} vs champion {dd_champ:.1%} "
                       f"(tolerance x{DD_REGRESSION_TOLERANCE})")

    return True, (f"selection fitness {s_chal:.3f} > {s_champ:.3f} + {margin:.3f}, "
                  f"merged {f_chal:.3f} >= {f_champ:.3f}, "
                  f"drawdown {dd_chal:.1%} within tolerance")


def holdout_accepts(champion_holdout: float, challenger_holdout: float,
                    n_draws: int = 1) -> tuple[bool, str]:
    """The sealed-holdout gate.

    The holdout is not re-drawn between runs. It is the newest HOLDOUT_FRAC of
    a history that grows by one bar a day, so a system evolving for months
    interrogates substantially the same bars every time it promotes. Every
    candidate ever compared against it is another draw from one urn, and the
    best of N draws beats an equal champion by luck alone often enough to
    manufacture a lineage out of noise.

    So the correction that guards the selection metric guards this one too. It
    applies to the *cumulative* number of draws, which — unlike the
    per-champion proposal set — is never reset by a promotion. Resetting it is
    exactly what a mined holdout would look like from the inside: a clean gate
    passed over and over, each time from a fresh count of one.

    This margin uses `HOLDOUT_SIGMA`, not `MULTIPLE_TESTING_SIGMA` — a single
    holdout window is a noisier estimate than a fold-aggregate, so the same
    k-draw correction needs a larger sigma to protect against the same amount
    of luck. Until 2026-08-21 this used `MULTIPLE_TESTING_SIGMA` as a
    knowingly-too-small placeholder (this docstring said so: "measure the
    sigma before trusting the number"); `holdout-noise`'s block bootstrap has
    now measured it (see `HOLDOUT_SIGMA`'s definition and AMENDMENTS.md), and
    `HOLDOUT_SIGMA` is that measurement, not a guess. It is still likely a
    floor rather than the true value: a candidate only reaches this gate
    after ranking top-3 on folds that correlate with it, so it arrives
    pre-selected upward, and `HOLDOUT_SIGMA` doesn't capture that second
    effect, only realized-path resampling noise.
    """
    if not math.isfinite(challenger_holdout):
        return False, "challenger produced no finite holdout fitness"
    if not math.isfinite(champion_holdout):
        return True, "champion has no finite holdout fitness to beat"
    margin = required_margin(n_draws, 0, sigma=HOLDOUT_SIGMA)
    if challenger_holdout <= champion_holdout + margin:
        return False, (f"failed sealed holdout: {challenger_holdout:.3f} did not clear "
                       f"champion {champion_holdout:.3f} + margin {margin:.3f} "
                       f"({n_draws} cumulative draws against this holdout)")
    return True, (f"holdout {challenger_holdout:.3f} > champion {champion_holdout:.3f} "
                  f"+ margin {margin:.3f} ({n_draws} cumulative draws)")


# ---------------------------------------------------------------------------
# Integrity
# ---------------------------------------------------------------------------

_HERE = os.path.dirname(os.path.abspath(__file__))
_PROTECTED = ["__init__.py", os.path.join("..", "core", "portfolio.py")]

# When running as a single-file bundle there are no source files on disk, so
# the runner hands over the embedded source text instead. Same guarantee: we
# still hash the exact bytes that are about to be executed.
EMBEDDED_SOURCES: dict[str, str] = {}


def checksum() -> str:
    h = hashlib.sha256()
    if EMBEDDED_SOURCES:
        for key in ("constitution", "core.portfolio"):
            h.update(EMBEDDED_SOURCES.get(key, "").encode())
        return h.hexdigest()[:16]
    for rel in _PROTECTED:
        p = os.path.normpath(os.path.join(_HERE, rel))
        with open(p, "rb") as f:
            h.update(f.read())
    return h.hexdigest()[:16]


def verify(manifest_path: str | None = None) -> tuple[bool, str]:
    """Fail loud if the scoreboard moved."""
    manifest_path = manifest_path or os.path.join(_HERE, "MANIFEST")
    cur = checksum()
    if not os.path.exists(manifest_path):
        with open(manifest_path, "w") as f:
            f.write(cur + "\n")
        return True, f"constitution sealed at {cur}"
    with open(manifest_path) as f:
        recorded = f.read().strip()
    if recorded != cur:
        return False, (f"CONSTITUTION MODIFIED: expected {recorded}, found {cur}. "
                       "A human must review and re-seal before any run.")
    return True, f"constitution verified {cur}"
