"""RESEARCHER — proposes changes to the roster.

Two sources of hypotheses, deliberately mixed:

1. **Diagnosis-driven.** Read the ledger, find where money actually leaked,
   propose a change aimed at that leak. High prior of being right, low
   novelty — it can only fix problems that have already cost money.

2. **Blind perturbation.** Random moves in gene space. Low hit rate, but it is
   the only source of ideas nobody thought of. Every genuinely surprising
   improvement in this system will come from here.

Per Burk's instruction, the hypothesis space is generated from the system's own
data and from general principles — not by copying human traders. Most humans
lose money; imitating them imports their losses along with their style.

The Researcher has no authority. It writes proposals. The Evaluator measures
them and the Superior Judge decides. It cannot touch the constitution, the
broker, or the fitness function.
"""
from __future__ import annotations

import random
from collections import defaultdict
from typing import Any

from core.genome import Genome
from core.types import Mutation

# The mutable surface. Anything not listed here cannot be changed by evolution
# — an allowlist, not a denylist, so a new gene is inert until someone
# deliberately opens it up.
GENE_SPACE: dict[str, tuple[float, float, str]] = {
    "risk.stop_loss": (-0.45, -0.04, "float"),
    "risk.trailing_stop": (-0.45, -0.05, "float"),
    "risk.take_profit": (0.06, 1.50, "float"),
    "risk.max_bars_held": (5, 250, "int"),

    "agents.consult_risky.genes.min_breakout": (-0.15, 0.01, "float"),
    "agents.consult_risky.genes.min_rank_mom": (0.30, 0.95, "float"),
    "agents.consult_risky.genes.rsi_max": (55.0, 95.0, "float"),
    "agents.consult_risky.genes.exit_rsi": (60.0, 99.0, "float"),
    "agents.consult_risky.genes.exit_trend_below": (-0.25, 0.02, "float"),
    "agents.consult_risky.genes.conviction_scale": (0.3, 2.0, "float"),

    "agents.consult_moderate.genes.min_trend": (-0.03, 0.08, "float"),
    "agents.consult_moderate.genes.rsi_lo": (25.0, 60.0, "float"),
    "agents.consult_moderate.genes.rsi_hi": (60.0, 92.0, "float"),
    "agents.consult_moderate.genes.min_rank_mom": (0.20, 0.90, "float"),
    "agents.consult_moderate.genes.max_vol": (0.5, 3.5, "float"),
    "agents.consult_moderate.genes.exit_trend_below": (-0.25, 0.03, "float"),
    "agents.consult_moderate.genes.exit_rsi": (60.0, 99.0, "float"),
    "agents.consult_moderate.genes.conviction_scale": (0.3, 2.0, "float"),

    "agents.consult_conservative.genes.rsi_buy_below": (15.0, 50.0, "float"),
    "agents.consult_conservative.genes.z_buy_below": (-3.0, 0.2, "float"),
    "agents.consult_conservative.genes.max_vol": (0.4, 3.0, "float"),
    "agents.consult_conservative.genes.max_dd_from_high": (-0.75, -0.05, "float"),
    "agents.consult_conservative.genes.exit_rsi": (50.0, 95.0, "float"),
    "agents.consult_conservative.genes.conviction_scale": (0.3, 2.0, "float"),
    "agents.consult_conservative.genes.min_trend": (-0.15, 0.05, "float"),

    "agents.risk_judge.genes.base_size_pct": (0.03, 0.35, "float"),
    "agents.risk_judge.genes.unanimous_bonus": (1.0, 3.0, "float"),
    "agents.risk_judge.genes.two_agree_bonus": (0.6, 2.2, "float"),
    "agents.risk_judge.genes.lone_voice_scale": (0.0, 1.5, "float"),
    "agents.risk_judge.genes.min_conviction": (0.05, 0.75, "float"),
    "agents.risk_judge.genes.max_positions": (2, 10, "int"),
    "agents.risk_judge.genes.max_position_pct": (0.05, 0.34, "float"),
    "agents.risk_judge.genes.cash_floor_pct": (0.0, 0.5, "float"),
    "agents.risk_judge.genes.sell_conviction_threshold": (0.1, 0.9, "float"),
    "agents.risk_judge.genes.cold_start_ramp_bars": (0, 300, "int"),
    "agents.risk_judge.genes.cold_start_ramp_start_scale": (0.0, 1.0, "float"),
    "agents.risk_judge.genes.cold_start_ramp_min_conviction_boost": (0.0, 0.5, "float"),
    "agents.risk_judge.genes.cold_start_ramp_vol_cap": (0.0, 3.0, "float"),

    "agents.analyst.genes.trend_fast": (3, 30, "int"),
    "agents.analyst.genes.trend_slow": (25, 150, "int"),
    "agents.analyst.genes.rsi_len": (5, 40, "int"),
    "agents.analyst.genes.breakout_len": (5, 90, "int"),
    "agents.analyst.genes.regime_ma": (20, 200, "int"),

    "agents.superior_judge.genes.max_new_positions_per_bar": (1, 6, "int"),
}

REGIME_KEYS = ["bull", "chop", "bear", "crisis"]


def _get_path(d: dict, path: str) -> Any:
    node: Any = d
    for p in path.split("."):
        if not isinstance(node, dict) or p not in node:
            return None
        node = node[p]
    return node


def _clamp(v, lo, hi, kind):
    v = max(lo, min(hi, v))
    return int(round(v)) if kind == "int" else round(float(v), 4)


def diagnose(result: dict[str, Any]) -> dict[str, Any]:
    """Where did the money actually go? This is the Researcher's evidence base."""
    trades = result.get("closed_trades", [])
    stats = result.get("stats", {})
    pnl_by_exit: dict[str, float] = defaultdict(float)
    n_by_exit: dict[str, int] = defaultdict(int)
    pnl_by_entry: dict[str, float] = defaultdict(float)
    n_by_entry: dict[str, int] = defaultdict(int)

    for t in trades:
        who = str(t.get("exit_reason", "")).split(":")[0].strip()[:30] or "unknown"
        pnl_by_exit[who] += t.get("pnl", 0.0)
        n_by_exit[who] += 1
        for a in (t.get("entry_agents") or ["unattributed"]):
            pnl_by_entry[a] += t.get("pnl", 0.0)
            n_by_entry[a] += 1

    stop_trades = [t for t in trades if "stop loss" in str(t.get("exit_reason", ""))]
    tp_trades = [t for t in trades if "take profit" in str(t.get("exit_reason", ""))]
    time_trades = [t for t in trades if "time stop" in str(t.get("exit_reason", ""))]

    return {
        "pnl_by_exit": dict(pnl_by_exit), "n_by_exit": dict(n_by_exit),
        "pnl_by_entry": dict(pnl_by_entry), "n_by_entry": dict(n_by_entry),
        "stop_share": len(stop_trades) / len(trades) if trades else 0.0,
        "stop_pnl": sum(t["pnl"] for t in stop_trades),
        "tp_share": len(tp_trades) / len(trades) if trades else 0.0,
        "time_share": len(time_trades) / len(trades) if trades else 0.0,
        "avg_bars_held": stats.get("avg_bars_held", 0.0),
        "trades": len(trades),
        "win_rate": stats.get("win_rate", 0.0),
        "turnover": stats.get("turnover_annual", 0.0),
        "halt_count": stats.get("halt_count", 0),
        "superior_overrides": result.get("superior_overrides", 0),
    }


class Researcher:
    name = "researcher"

    def __init__(self, seed: int | None = None):
        self.rng = random.Random(seed)

    # -- 1. diagnosis-driven ----------------------------------------------
    def from_diagnosis(self, g: Genome, d: dict[str, Any]) -> list[Mutation]:
        out: list[Mutation] = []

        # Stops that fire often AND lose money are usually sitting inside the
        # asset's normal noise band, not outside it.
        if d["stop_share"] > 0.15 and d["stop_pnl"] < 0:
            cur = g.risk.get("stop_loss", -0.12)
            out.append(Mutation(
                kind="tune", target="risk.stop_loss",
                patch={"risk.stop_loss": _clamp(cur * 1.6, *GENE_SPACE["risk.stop_loss"][:2],
                                                GENE_SPACE["risk.stop_loss"][2])},
                hypothesis=(f"{d['stop_share']:.0%} of exits are stop-losses and they lost "
                            f"{d['stop_pnl']:.0f} — the stop is inside daily noise; widen it")))

        # Time stops firing a lot means the holding period is fighting the
        # signal's natural horizon.
        if d["time_share"] > 0.25:
            cur = g.risk.get("max_bars_held", 60)
            out.append(Mutation(
                kind="tune", target="risk.max_bars_held",
                patch={"risk.max_bars_held": _clamp(cur * 2, 5, 250, "int")},
                hypothesis=f"{d['time_share']:.0%} of exits are time stops — horizon too short"))

        # An entry agent that is reliably net-negative over enough trades is
        # not adding a view, it's adding losses.
        for agent, pnl in d["pnl_by_entry"].items():
            n = d["n_by_entry"].get(agent, 0)
            if agent.startswith("consult") and n >= 25 and pnl < 0:
                cur = g.gene(agent, "conviction_scale", 1.0)
                out.append(Mutation(
                    kind="reweight", target=f"agents.{agent}.genes.conviction_scale",
                    patch={f"agents.{agent}.genes.conviction_scale": _clamp(cur * 0.6, 0.3, 2.0, "float")},
                    hypothesis=f"{agent} entries lost {pnl:.0f} over {n} trades — turn it down"))
                out.append(Mutation(
                    kind="remove_agent", target=agent,
                    patch={f"agents.{agent}.enabled": False},
                    hypothesis=f"{agent} entries lost {pnl:.0f} over {n} trades — try removing it",
                    complexity_delta=-1 - len(g.genes(agent))))

        # The Superior Judge should be a rubber stamp. If it's constantly
        # overriding, the Risk Judge is sizing beyond the hard limits.
        if d["superior_overrides"] > max(30, d["trades"] * 0.4):
            cur = g.gene("risk_judge", "base_size_pct", 0.12)
            out.append(Mutation(
                kind="tune", target="agents.risk_judge.genes.base_size_pct",
                patch={"agents.risk_judge.genes.base_size_pct": _clamp(cur * 0.7, 0.03, 0.35, "float")},
                hypothesis=(f"superior judge intervened {d['superior_overrides']} times — "
                            "the risk judge is sizing past the hard caps")))

        # Repeated circuit-breaker trips = too much risk on at once.
        if d["halt_count"] >= 2:
            cur = g.gene("risk_judge", "max_position_pct", 0.25)
            out.append(Mutation(
                kind="tune", target="agents.risk_judge.genes.max_position_pct",
                patch={"agents.risk_judge.genes.max_position_pct": _clamp(cur * 0.7, 0.05, 0.34, "float")},
                hypothesis=f"circuit breaker tripped {d['halt_count']}x — concentration too high"))

        # Very low trade count starves the evidence gate.
        if d["trades"] < 40:
            cur = g.gene("risk_judge", "min_conviction", 0.30)
            out.append(Mutation(
                kind="tune", target="agents.risk_judge.genes.min_conviction",
                patch={"agents.risk_judge.genes.min_conviction": _clamp(cur * 0.7, 0.05, 0.75, "float")},
                hypothesis=f"only {d['trades']} trades — too selective to measure"))

        return out

    # -- 2. blind search ---------------------------------------------------
    def perturb(self, g: Genome, n: int = 12, n_genes: int = 2,
                boldness: float = 0.0) -> list[Mutation]:
        """`boldness` rises with how long the champion has gone unbeaten.

        A search that keeps failing in the same neighbourhood should widen its
        steps, not keep re-sampling the same basin — the local hill has been
        climbed, and what's left is either further away or isn't there.
        """
        out: list[Mutation] = []
        paths = list(GENE_SPACE)
        jump_p = min(0.75, 0.2 + 0.12 * boldness)
        spread = 1.0 + 0.35 * boldness
        genes_per = min(len(paths), n_genes + int(boldness // 2))
        for _ in range(n):
            picks = self.rng.sample(paths, k=min(genes_per, len(paths)))
            patch: dict[str, Any] = {}
            desc = []
            for path in picks:
                lo, hi, kind = GENE_SPACE[path]
                cur = _get_path(g.data, path)
                if cur is None:
                    continue
                # log-ish multiplicative jitter, plus an occasional big jump so
                # search isn't trapped in the basin around the seed
                if self.rng.random() < jump_p:
                    nv = self.rng.uniform(lo, hi)
                else:
                    nv = (cur * self.rng.uniform(1 - 0.4 * spread, 1 + 0.6 * spread)
                          + self.rng.gauss(0, abs(hi - lo) * 0.05 * spread))
                nv = _clamp(nv, lo, hi, kind)
                if nv == cur:
                    continue
                patch[path] = nv
                desc.append(f"{path.split('.')[-1]} {cur}->{nv}")
            if patch:
                out.append(Mutation(kind="tune", target="+".join(sorted(patch)),
                                    patch=patch,
                                    hypothesis="blind search: " + ", ".join(desc)))
        return out

    # -- 3. structural -----------------------------------------------------
    def structural(self, g: Genome) -> list[Mutation]:
        out: list[Mutation] = []
        for agent in ("consult_risky", "consult_moderate", "consult_conservative"):
            if g.enabled(agent):
                out.append(Mutation(
                    kind="remove_agent", target=agent,
                    patch={f"agents.{agent}.enabled": False},
                    hypothesis=f"is {agent} carrying its weight, or just adding noise?",
                    complexity_delta=-1 - len(g.genes(agent))))
            else:
                out.append(Mutation(
                    kind="add_agent", target=agent,
                    patch={f"agents.{agent}.enabled": True},
                    hypothesis=f"conditions may have changed — try {agent} again",
                    complexity_delta=1 + len(g.genes(agent))))

        # regime scaling is where most of the risk control actually lives
        cur = dict(g.gene("risk_judge", "regime_scale", {}))
        for k in REGIME_KEYS:
            if k not in cur:
                continue
            for mult in (0.5, 1.5):
                nv = round(min(1.5, max(0.0, cur[k] * mult)), 3)
                if nv != cur[k]:
                    out.append(Mutation(
                        kind="tune", target=f"regime_scale.{k}",
                        patch={f"agents.risk_judge.genes.regime_scale.{k}": nv},
                        hypothesis=f"size {'up' if mult > 1 else 'down'} in '{k}' regime: {cur[k]} -> {nv}"))

        return out

    @staticmethod
    def key(m: Mutation) -> tuple:
        """Identity of a proposal — the patch itself, not its prose."""
        return tuple((k, str(v)) for k, v in sorted(m.patch.items(), key=lambda kv: kv[0]))

    def propose(self, g: Genome, diagnostics: dict[str, Any], n_blind: int = 14,
                exclude: set | None = None, boldness: float = 0.0) -> list[Mutation]:
        """`exclude` is the set of proposal keys already ruled out against this
        champion. Without it the diagnosis-driven and structural proposals are
        deterministic given the champion, so an unbeaten champion gets the
        identical losing candidate re-tested every single generation — four
        generations of this project burned twelve backtests re-rejecting one
        idea before the memory was added."""
        exclude = exclude or set()
        props = self.from_diagnosis(g, diagnostics)
        props += self.structural(g)
        props += self.perturb(g, n=n_blind, boldness=boldness)

        seen, uniq = set(), []
        for m in props:
            k = self.key(m)
            if k in seen or k in exclude:
                continue
            seen.add(k)
            uniq.append(m)
        return uniq
