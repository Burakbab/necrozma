"""Message contracts between agents.

Frozen dataclasses, not dicts. If two agents disagree about a field name, that
should be an error at write-time, not a silent None three layers downstream.
Every one of these gets written to the decision log.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any


@dataclass(frozen=True)
class Features:
    """What the Analyst extracts per symbol. The *only* view of the market that
    any downstream agent gets."""
    symbol: str
    price: float
    ret_1: float          # last-bar return
    ret_5: float
    ret_20: float
    trend: float          # (fast MA / slow MA) - 1
    slope: float          # normalised slope of the fast MA
    rsi: float            # 0..100
    vol: float            # annualised realised vol
    vol_ratio: float      # short vol / long vol; >1 = vol expanding
    dd_from_high: float   # <= 0
    dist_ma: float        # (price / slow MA) - 1
    zscore: float         # price z-score vs slow window
    volume_shock: float   # volume vs its own average
    breakout: float       # (price / N-bar high) - 1 ; >= 0 means new high
    rank_mom: float       # cross-sectional momentum rank 0..1

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Briefing:
    ts: str
    regime: str                     # "bull" | "bear" | "chop" | "crisis"
    regime_score: float             # -1..1
    breadth: float                  # fraction of universe in uptrend
    features: dict[str, Features]
    equity: float
    cash_pct: float
    open_positions: dict[str, float]  # symbol -> weight


@dataclass(frozen=True)
class Intent:
    agent: str
    symbol: str
    side: str                 # "buy" | "sell" | "hold"
    conviction: float         # 0..1
    horizon: int              # bars
    rationale: str
    genes_used: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Proposal:
    agent: str
    ts: str
    stance: str               # one-line temperament note
    intents: tuple[Intent, ...]


@dataclass(frozen=True)
class Veto:
    symbol: str
    side: str
    by: str
    reason: str


@dataclass
class Order:
    symbol: str
    side: str                 # "buy" | "sell"
    quote_amount: float = 0.0   # for buys
    fraction: float = 0.0       # for sells
    reason_chain: list[str] = field(default_factory=list)
    conviction: float = 0.0
    agreement: float = 0.0


@dataclass
class Verdict:
    ts: str
    orders: list[Order]
    vetoes: list[Veto]
    agreement_score: float
    notes: str = ""
    by: str = "risk_judge"


@dataclass
class Mutation:
    kind: str                 # "tune" | "add_agent" | "remove_agent" | "reweight" | "universe"
    target: str
    patch: dict[str, Any]
    hypothesis: str
    proposed_by: str = "researcher"
    ts: str = ""
    complexity_delta: int = 0
