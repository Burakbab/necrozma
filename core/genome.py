"""The genome — everything the system is allowed to change about itself.

Code is mechanism. Genome is policy. There should be no strategy number
hardcoded anywhere in agents/ — if a constant matters, it belongs here, where
the Researcher can propose changing it and the Superior Judge can veto.
"""
from __future__ import annotations

import copy
import json
import os
import time
from datetime import datetime, timezone
from typing import Any

GENOME_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                          "state", "genomes")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


SEED_GENOME: dict[str, Any] = {
    "version": 1,
    "parent": None,
    "created": None,
    "note": "seed roster — hand-written starting point, expected to be replaced by evolution",
    # Which OHLCV bar size this genome trades and is scored on. "1h" | "4h" | "1d".
    # Gene periods below (trend_fast/slow, rsi_len, breakout_len, regime_ma,
    # max_bars_held, ...) are expressed in *bars*, not wall-clock time, so
    # switching this without re-tuning them changes what those numbers mean.
    "bar_interval": "1d",
    # 27 liquid USDT pairs with 4+ years of history. Breadth is not cosmetic:
    # a fitness estimate over 12 symbols is too noisy to tell a real edge from
    # luck, so the acceptance gates reject everything and nothing can ever be
    # learned. More symbols -> more trades -> a tighter estimate -> the gates
    # become passable by genuine improvements instead of only by noise.
    # PAXG (gold) is deliberately included as a non-crypto-correlated asset.
    "universe": ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT",
                 "ADAUSDT", "DOGEUSDT", "LINKUSDT", "AVAXUSDT", "LTCUSDT",
                 "DOTUSDT", "TRXUSDT", "ZECUSDT", "UNIUSDT", "NEARUSDT",
                 "INJUSDT", "FETUSDT", "AAVEUSDT", "XLMUSDT", "SHIBUSDT",
                 "BCHUSDT", "CRVUSDT", "FILUSDT", "ATOMUSDT", "ICPUSDT",
                 "HBARUSDT", "PAXGUSDT"],
    "agents": {
        "analyst": {
            "enabled": True,
            "genes": {
                "trend_fast": 10, "trend_slow": 50,
                "rsi_len": 14,
                "vol_short": 10, "vol_long": 40,
                "breakout_len": 20, "z_len": 30,
                "regime_ma": 50, "regime_anchor": "BTCUSDT",
                "volume_len": 20,
            },
        },
        "consult_risky": {
            "enabled": True, "weight": 1.0,
            "genes": {
                "min_breakout": -0.02,   # within 2% of the N-bar high
                "min_rank_mom": 0.70,    # top 30% of the universe by momentum
                "min_slope": 0.0,
                "rsi_max": 82.0,         # even a momentum chaser has a limit
                "min_vol_ratio": 0.0,
                "conviction_scale": 1.20,
                "exit_rsi": 88.0,
                "exit_trend_below": -0.03,
            },
        },
        "consult_moderate": {
            "enabled": True, "weight": 1.0,
            "genes": {
                "min_trend": 0.005,
                "min_slope": 0.0,
                "rsi_lo": 45.0, "rsi_hi": 72.0,
                "min_rank_mom": 0.50,
                "max_vol": 1.60,
                "conviction_scale": 1.0,
                "exit_trend_below": 0.0,
                "exit_rsi": 80.0,
            },
        },
        "consult_conservative": {
            "enabled": True, "weight": 1.0,
            "genes": {
                "rsi_buy_below": 38.0,
                "z_buy_below": -0.8,
                "require_uptrend": True,     # only buy dips inside an uptrend
                "min_trend": -0.01,
                "max_vol": 1.10,
                "max_dd_from_high": -0.35,   # don't catch a falling knife
                "conviction_scale": 0.80,
                "take_profit": 0.12,
                "exit_rsi": 68.0,
            },
        },
        "risk_judge": {
            "enabled": True,
            "genes": {
                "base_size_pct": 0.12,
                "unanimous_bonus": 1.60,
                "two_agree_bonus": 1.20,
                "lone_voice_scale": 0.60,
                "min_conviction": 0.30,
                "max_positions": 6,
                "max_position_pct": 0.25,
                "cash_floor_pct": 0.05,
                "regime_scale": {"bull": 1.0, "chop": 0.6, "bear": 0.25, "crisis": 0.0},
                "sell_conviction_threshold": 0.35,
                "scale_in_allowed": True,
                # Scales new buy size up linearly over the first
                # `cold_start_ramp_bars` calls to RiskJudge.rule() (i.e. bars
                # since this genome started trading from a cold start), from
                # `cold_start_ramp_start_scale`x to 1.0x. Defaults are a true
                # no-op (0 bars = never fires) -- see AGENTS.md item 2,
                # 2026-09-01 session, for the cold-start-fold finding this
                # exists to address: a from-scratch restart (a fresh
                # walk-forward fold, or a genuinely new live account) can size
                # into a downturn at full risk with none of the de-risking a
                # seasoned position would already have, which the 22:07 UTC/
                # 01:14 UTC sessions found makes an otherwise-fine genome fail
                # the fold-based drawdown gate that a continuous replay never
                # reveals.
                "cold_start_ramp_bars": 0,
                "cold_start_ramp_start_scale": 1.0,
                # Structurally different lever than the size ramp above: adds
                # to `min_conviction` (not just shrinks the order) during the
                # same cold-start window, tapering linearly back to 0 extra
                # by `cold_start_ramp_bars`. A weak-conviction entry gets
                # vetoed outright instead of sized down -- see AGENTS.md item
                # 2, 2026-09-01 16:47 UTC entry, for why the size-only ramp
                # (three independent grid points) wasn't enough on its own.
                # Default 0.0 is a true no-op.
                "cold_start_ramp_min_conviction_boost": 0.0,
            },
        },
        "superior_judge": {
            "enabled": True,
            "genes": {
                "hard_max_position_pct": 0.35,
                "hard_cash_floor_pct": 0.02,
                "hard_max_positions": 8,
                "block_buys_in_crisis": True,
                "max_new_positions_per_bar": 3,
            },
        },
    },
    "risk": {
        "stop_loss": -0.12,
        "trailing_stop": -0.15,
        "take_profit": 0.35,
        "max_bars_held": 60,
        "min_bars_held": 1,
    },
    "routing": {
        "consults": ["consult_risky", "consult_moderate", "consult_conservative"],
        "minor_judges": ["risk_judge"],
        "final": "superior_judge",
    },
    "broker": {"fee_bps": 10.0, "slippage_bps": 5.0, "start_cash": 10_000.0},
}


class Genome:
    def __init__(self, data: dict[str, Any] | None = None):
        self.data: dict[str, Any] = copy.deepcopy(data or SEED_GENOME)
        if self.data.get("created") is None:
            self.data["created"] = _now()

    # -- access ------------------------------------------------------------
    def genes(self, agent: str) -> dict[str, Any]:
        return self.data["agents"].get(agent, {}).get("genes", {})

    def enabled(self, agent: str) -> bool:
        return bool(self.data["agents"].get(agent, {}).get("enabled", False))

    def gene(self, agent: str, key: str, default: Any = None) -> Any:
        return self.genes(agent).get(key, default)

    @property
    def universe(self) -> list[str]:
        return list(self.data["universe"])

    @property
    def bar_interval(self) -> str:
        """"1h" | "4h" | "1d" — defaults to "1d" for genomes saved before this
        field existed, so old lineage/champion files keep loading unchanged."""
        return str(self.data.get("bar_interval", "1d"))

    @property
    def risk(self) -> dict[str, Any]:
        return self.data["risk"]

    @property
    def version(self) -> int:
        return int(self.data["version"])

    @property
    def consults(self) -> list[str]:
        return [a for a in self.data["routing"]["consults"] if self.enabled(a)]

    def complexity(self) -> int:
        """Crude but honest: number of live agents + number of live genes.
        Used by the acceptance rule to charge rent on added machinery."""
        n = 0
        for name, spec in self.data["agents"].items():
            if spec.get("enabled"):
                n += 1 + len(spec.get("genes", {}))
        return n

    # -- mutation ----------------------------------------------------------
    def child(self, patches: list[tuple[str, Any]], note: str = "") -> "Genome":
        """Return a new genome with dotted-path patches applied. Never mutates
        self — lineage must stay immutable or the audit trail is worthless."""
        d = copy.deepcopy(self.data)
        for path, value in patches:
            node = d
            parts = path.split(".")
            for p in parts[:-1]:
                node = node.setdefault(p, {})
            node[parts[-1]] = value
        d["parent"] = self.data.get("version")
        d["version"] = int(self.data.get("version", 0)) + 1
        d["created"] = _now()
        d["note"] = note
        return Genome(d)

    # -- persistence -------------------------------------------------------
    def save(self, tag: str | None = None) -> str:
        os.makedirs(GENOME_DIR, exist_ok=True)
        name = tag or f"v{self.version}"
        path = os.path.join(GENOME_DIR, f"{name}.json")
        with open(path, "w") as f:
            json.dump(self.data, f, indent=2)
        return path

    @classmethod
    def load(cls, path_or_version: str | int) -> "Genome":
        if isinstance(path_or_version, int):
            path = os.path.join(GENOME_DIR, f"v{path_or_version}.json")
        elif os.path.exists(path_or_version):
            path = path_or_version
        else:
            path = os.path.join(GENOME_DIR, f"{path_or_version}.json")
        with open(path) as f:
            return cls(json.load(f))

    @classmethod
    def champion(cls) -> "Genome":
        p = os.path.join(GENOME_DIR, "champion.json")
        if os.path.exists(p):
            return cls.load(p)
        g = cls()
        g.save("champion")
        g.save("v1")
        return g

    def promote(self) -> None:
        self.save(f"v{self.version}")
        self.save("champion")
