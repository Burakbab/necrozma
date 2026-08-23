"""THE THREE CONSULTS.

Not one strategy with a risk dial in three positions — three genuinely
different theories of where money comes from. That matters: if they were
correlated, their agreement would carry no information, and the Risk Judge's
whole job (reading disagreement) would be noise.

  risky        -> "buy what is already winning"      (momentum / breakout)
  conservative -> "buy what is temporarily hated"    (mean reversion)
  moderate     -> "buy confirmed trends, patiently"  (trend + confirmation)

Each emits Intents with a rationale. The rationale is not decoration — it is
the raw material the Researcher mines to work out which reasoning actually pays.
"""
from __future__ import annotations

from core.genome import Genome
from core.types import Briefing, Intent, Proposal


class BaseConsult:
    name = "consult"
    stance = ""

    def __init__(self, genome: Genome, name: str | None = None):
        self.g = genome
        if name:
            self.name = name
        self.genes = genome.genes(self.name)

    def scale(self, x: float) -> float:
        return max(0.0, min(1.0, x * float(self.genes.get("conviction_scale", 1.0))))

    def consider(self, b: Briefing) -> Proposal:
        raise NotImplementedError

    def _wrap(self, b: Briefing, intents: list[Intent]) -> Proposal:
        return Proposal(agent=self.name, ts=b.ts, stance=self.stance,
                        intents=tuple(intents))


class RiskyConsult(BaseConsult):
    name = "consult_risky"
    stance = "strength begets strength — own the leaders, cut fast when they stop leading"

    def consider(self, b: Briefing) -> Proposal:
        g = self.genes
        out: list[Intent] = []
        for sym, f in b.features.items():
            held = b.open_positions.get(sym, 0.0) > 0

            if held and (f.rsi > g.get("exit_rsi", 88) or f.trend < g.get("exit_trend_below", -0.03)):
                out.append(Intent(self.name, sym, "sell", 0.8, 0, (
                    f"leadership lost: rsi {f.rsi:.0f}, trend {f.trend:+.1%}"), dict(g)))
                continue

            if (f.breakout >= g.get("min_breakout", -0.02)
                    and f.rank_mom >= g.get("min_rank_mom", 0.7)
                    and f.slope >= g.get("min_slope", 0.0)
                    and f.rsi <= g.get("rsi_max", 82)
                    and f.vol_ratio >= g.get("min_vol_ratio", 0.0)):
                conv = self.scale(0.45 + 0.35 * f.rank_mom + 6 * max(0.0, f.breakout))
                out.append(Intent(self.name, sym, "buy", conv, 15, (
                    f"at/near range high (breakout {f.breakout:+.1%}), "
                    f"momentum rank {f.rank_mom:.2f}, slope {f.slope:+.2%}"), dict(g)))
        return self._wrap(b, out)


class ConservativeConsult(BaseConsult):
    name = "consult_conservative"
    stance = "buy fear inside strength, sell relief — and hold cash without shame"

    def consider(self, b: Briefing) -> Proposal:
        g = self.genes
        out: list[Intent] = []
        for sym, f in b.features.items():
            held = b.open_positions.get(sym, 0.0) > 0

            if held and f.rsi > g.get("exit_rsi", 68):
                out.append(Intent(self.name, sym, "sell", 0.7, 0,
                                  f"mean reversion complete: rsi {f.rsi:.0f}", dict(g)))
                continue

            if f.vol > g.get("max_vol", 1.10):
                continue
            if f.dd_from_high < g.get("max_dd_from_high", -0.35):
                continue  # falling knife
            if g.get("require_uptrend", True) and f.trend < g.get("min_trend", -0.01):
                continue

            if f.rsi <= g.get("rsi_buy_below", 38) and f.zscore <= g.get("z_buy_below", -0.8):
                depth = min(1.0, (g.get("rsi_buy_below", 38) - f.rsi) / 20.0)
                conv = self.scale(0.35 + 0.45 * depth)
                out.append(Intent(self.name, sym, "buy", conv, 10, (
                    f"oversold inside an uptrend: rsi {f.rsi:.0f}, z {f.zscore:+.2f}, "
                    f"trend {f.trend:+.1%}"), dict(g)))
        return self._wrap(b, out)


class ModerateConsult(BaseConsult):
    name = "consult_moderate"
    stance = "trend plus confirmation; no heroics, no bag-holding"

    def consider(self, b: Briefing) -> Proposal:
        g = self.genes
        out: list[Intent] = []
        for sym, f in b.features.items():
            held = b.open_positions.get(sym, 0.0) > 0

            if held and (f.trend < g.get("exit_trend_below", 0.0) or f.rsi > g.get("exit_rsi", 80)):
                out.append(Intent(self.name, sym, "sell", 0.65, 0, (
                    f"trend broke: trend {f.trend:+.1%}, rsi {f.rsi:.0f}"), dict(g)))
                continue

            if f.vol > g.get("max_vol", 1.6):
                continue

            if (f.trend >= g.get("min_trend", 0.005)
                    and f.slope >= g.get("min_slope", 0.0)
                    and g.get("rsi_lo", 45) <= f.rsi <= g.get("rsi_hi", 72)
                    and f.rank_mom >= g.get("min_rank_mom", 0.5)):
                conv = self.scale(0.40 + 0.30 * f.rank_mom + min(0.25, 8 * max(0.0, f.trend)))
                out.append(Intent(self.name, sym, "buy", conv, 20, (
                    f"confirmed trend: ma-spread {f.trend:+.1%}, slope {f.slope:+.2%}, "
                    f"rsi {f.rsi:.0f} in band"), dict(g)))
        return self._wrap(b, out)


REGISTRY = {
    "consult_risky": RiskyConsult,
    "consult_moderate": ModerateConsult,
    "consult_conservative": ConservativeConsult,
}


def build_consults(genome: Genome) -> list[BaseConsult]:
    out = []
    for name in genome.consults:
        cls = REGISTRY.get(name)
        if cls:
            out.append(cls(genome))
    return out
