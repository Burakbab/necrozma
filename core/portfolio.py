"""Paper broker + portfolio accounting.

This file lives under the *constitution* in spirit: the Researcher may never
propose changes to it. If the thing that measures money can be edited by the
thing being measured, every number downstream is fiction.

Conventions:
  - Long-only for v0.1 (shorting comes later, with borrow costs modelled).
  - Decision at close of bar i  ->  fill at open of bar i+1.
  - Fees and slippage always charged. A backtest without costs is a daydream.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field, asdict
from typing import Any

import numpy as np


@dataclass
class Fill:
    ts: str
    symbol: str
    side: str            # "buy" | "sell"
    qty: float
    price: float         # effective price incl. slippage
    ref_price: float     # unslipped reference
    fee: float
    reason: str


@dataclass
class Position:
    symbol: str
    qty: float = 0.0
    avg_cost: float = 0.0
    opened_ts: str | None = None
    peak_price: float = 0.0     # for trailing stops
    bars_held: int = 0
    entry_agents: tuple[str, ...] = ()   # who talked us into this

    @property
    def is_open(self) -> bool:
        return self.qty > 1e-12


@dataclass
class ClosedTrade:
    symbol: str
    qty: float
    entry_price: float
    exit_price: float
    entry_ts: str
    exit_ts: str
    pnl: float
    pnl_pct: float
    bars_held: int
    exit_reason: str
    entry_agents: tuple[str, ...] = ()


class PaperBroker:
    """Imaginary money, real accounting."""

    def __init__(self, cash: float = 10_000.0, fee_bps: float = 10.0,
                 slippage_bps: float = 5.0, min_order: float = 25.0):
        self.start_cash = cash
        self.cash = cash
        self.fee_bps = fee_bps
        self.slippage_bps = slippage_bps
        self.min_order = min_order
        self.positions: dict[str, Position] = {}
        self.fills: list[Fill] = []
        self.closed: list[ClosedTrade] = []
        self.nav_history: list[tuple[str, float]] = []
        self.peak_nav = cash
        self.halted = False
        self.just_halted = False
        self.halt_bars_left = 0
        self.halt_count = 0
        self.halt_reason = ""

    # -- valuation ---------------------------------------------------------
    def equity(self, prices: dict[str, float]) -> float:
        v = self.cash
        for sym, p in self.positions.items():
            if p.is_open:
                px = prices.get(sym)
                if px is not None and not math.isnan(px):
                    v += p.qty * px
        return v

    def exposure(self, prices: dict[str, float]) -> float:
        eq = self.equity(prices)
        if eq <= 0:
            return 0.0
        invested = eq - self.cash
        return invested / eq

    def position_weight(self, symbol: str, prices: dict[str, float]) -> float:
        eq = self.equity(prices)
        p = self.positions.get(symbol)
        if not p or not p.is_open or eq <= 0:
            return 0.0
        px = prices.get(symbol, 0.0)
        return (p.qty * px) / eq

    # -- execution ---------------------------------------------------------
    def buy(self, ts: str, symbol: str, quote_amount: float, price: float,
            reason: str = "", agents: tuple[str, ...] = ()) -> Fill | None:
        if self.halted or price is None or price <= 0:
            return None
        quote_amount = min(quote_amount, self.cash)
        if quote_amount < self.min_order:
            return None
        eff = price * (1 + self.slippage_bps / 10_000)
        fee = quote_amount * self.fee_bps / 10_000
        qty = (quote_amount - fee) / eff
        if qty <= 0:
            return None

        pos = self.positions.setdefault(symbol, Position(symbol))
        new_qty = pos.qty + qty
        pos.avg_cost = (pos.avg_cost * pos.qty + eff * qty) / new_qty if new_qty > 0 else eff
        pos.qty = new_qty
        if pos.opened_ts is None:
            pos.opened_ts = ts
            pos.bars_held = 0
            pos.entry_agents = tuple(agents)
        elif agents:
            pos.entry_agents = tuple(sorted(set(pos.entry_agents) | set(agents)))
        pos.peak_price = max(pos.peak_price, price)
        self.cash -= quote_amount

        f = Fill(ts, symbol, "buy", qty, eff, price, fee, reason)
        self.fills.append(f)
        return f

    def sell(self, ts: str, symbol: str, fraction: float, price: float,
             reason: str = "") -> Fill | None:
        pos = self.positions.get(symbol)
        if not pos or not pos.is_open or price is None or price <= 0:
            return None
        fraction = max(0.0, min(1.0, fraction))
        qty = pos.qty * fraction
        if qty <= 0:
            return None
        eff = price * (1 - self.slippage_bps / 10_000)
        gross = qty * eff
        fee = gross * self.fee_bps / 10_000
        proceeds = gross - fee
        if gross < self.min_order and fraction < 1.0:
            return None  # don't trade dust

        pnl = (eff - pos.avg_cost) * qty - fee
        self.cash += proceeds
        entry_ts = pos.opened_ts or ts
        entry_px = pos.avg_cost
        bars = pos.bars_held
        pos.qty -= qty

        self.closed.append(ClosedTrade(
            symbol=symbol, qty=qty, entry_price=entry_px, exit_price=eff,
            entry_ts=entry_ts, exit_ts=ts, pnl=pnl,
            pnl_pct=(eff / entry_px - 1) if entry_px > 0 else 0.0,
            bars_held=bars, exit_reason=reason, entry_agents=pos.entry_agents))

        if not pos.is_open:
            self.positions.pop(symbol, None)

        f = Fill(ts, symbol, "sell", qty, eff, price, fee, reason)
        self.fills.append(f)
        return f

    # -- bookkeeping -------------------------------------------------------
    def mark(self, ts: str, prices: dict[str, float], dd_halt: float = 0.25,
             cooldown: int = 20) -> float:
        """Mark to market, age positions, run the circuit breaker.

        The breaker is a cooldown, not a death sentence. An earlier version
        latched permanently, which meant a single bad month turned the rest of
        the backtest into a flat line — measuring how fast the system died
        rather than how well it traded. On trip: flatten, freeze for `cooldown`
        bars, re-baseline the peak, resume.
        """
        for sym, pos in self.positions.items():
            if pos.is_open:
                pos.bars_held += 1
                px = prices.get(sym)
                if px:
                    pos.peak_price = max(pos.peak_price, px)
        nav = self.equity(prices)
        self.nav_history.append((ts, nav))
        self.just_halted = False

        if self.halted:
            self.halt_bars_left -= 1
            if self.halt_bars_left <= 0:
                self.halted = False
                self.peak_nav = nav          # fresh baseline; don't re-trip instantly
                self.halt_reason = ""
            return nav

        self.peak_nav = max(self.peak_nav, nav)
        if self.peak_nav > 0 and (nav / self.peak_nav - 1) < -abs(dd_halt):
            self.halted = True
            self.just_halted = True
            self.halt_bars_left = cooldown
            self.halt_count += 1
            self.halt_reason = (f"circuit breaker: drawdown {nav / self.peak_nav - 1:.1%} "
                                f"< -{dd_halt:.0%} (freeze {cooldown} bars)")
        return nav

    # -- results -----------------------------------------------------------
    def nav_series(self) -> np.ndarray:
        return np.array([v for _, v in self.nav_history], dtype=float)

    def stats(self, bars_per_year: float = 365.0) -> dict[str, Any]:
        nav = self.nav_series()
        if len(nav) < 3:
            return {"error": "insufficient history", "trades": len(self.closed)}
        rets = np.diff(nav) / np.maximum(nav[:-1], 1e-9)
        total = nav[-1] / nav[0] - 1
        yrs = max(len(nav) / bars_per_year, 1e-6)
        cagr = (nav[-1] / nav[0]) ** (1 / yrs) - 1 if nav[0] > 0 else 0.0
        vol = float(np.std(rets, ddof=1)) * math.sqrt(bars_per_year) if len(rets) > 2 else 0.0
        downside = rets[rets < 0]
        dd_dev = float(np.std(downside, ddof=1)) * math.sqrt(bars_per_year) if len(downside) > 2 else 0.0
        sharpe = float(np.mean(rets)) * bars_per_year / vol if vol > 1e-9 else 0.0
        sortino = float(np.mean(rets)) * bars_per_year / dd_dev if dd_dev > 1e-9 else 0.0
        peaks = np.maximum.accumulate(nav)
        max_dd = float(np.min(nav / np.maximum(peaks, 1e-9) - 1))
        wins = [t for t in self.closed if t.pnl > 0]
        gross_win = sum(t.pnl for t in wins)
        gross_loss = -sum(t.pnl for t in self.closed if t.pnl <= 0)
        turnover = sum(f.qty * f.price for f in self.fills) / max(nav[0], 1e-9) / yrs
        return {
            "start_nav": float(nav[0]), "end_nav": float(nav[-1]),
            "total_return": float(total), "cagr": float(cagr),
            "vol": vol, "sharpe": sharpe, "sortino": sortino,
            "max_dd": max_dd, "bars": len(nav),
            "trades": len(self.closed),
            "win_rate": len(wins) / len(self.closed) if self.closed else 0.0,
            "profit_factor": gross_win / gross_loss if gross_loss > 1e-9 else (
                float("inf") if gross_win > 0 else 0.0),
            "avg_trade_pct": float(np.mean([t.pnl_pct for t in self.closed])) if self.closed else 0.0,
            "avg_bars_held": float(np.mean([t.bars_held for t in self.closed])) if self.closed else 0.0,
            "turnover_annual": float(turnover),
            "fees_paid": float(sum(f.fee for f in self.fills)),
            "halted": self.halted, "halt_reason": self.halt_reason,
            "halt_count": self.halt_count,
        }

    # -- persistence (the live account must survive an ephemeral container) --
    def to_state(self) -> dict[str, Any]:
        return {
            "start_cash": self.start_cash, "cash": self.cash,
            "fee_bps": self.fee_bps, "slippage_bps": self.slippage_bps,
            "min_order": self.min_order,
            "positions": {s: asdict(p) for s, p in self.positions.items() if p.is_open},
            "fills": [asdict(f) for f in self.fills],
            "closed": [asdict(t) for t in self.closed],
            "nav_history": self.nav_history,
            "peak_nav": self.peak_nav, "halted": self.halted,
            "halt_bars_left": self.halt_bars_left, "halt_count": self.halt_count,
            "halt_reason": self.halt_reason,
        }

    @classmethod
    def from_state(cls, st: dict[str, Any]) -> "PaperBroker":
        b = cls(cash=st.get("start_cash", 10_000.0), fee_bps=st.get("fee_bps", 10.0),
                slippage_bps=st.get("slippage_bps", 5.0), min_order=st.get("min_order", 25.0))
        b.cash = st.get("cash", b.cash)
        b.positions = {s: Position(**{**p, "entry_agents": tuple(p.get("entry_agents", ()))})
                       for s, p in st.get("positions", {}).items()}
        b.fills = [Fill(**f) for f in st.get("fills", [])]
        b.closed = [ClosedTrade(**{**t, "entry_agents": tuple(t.get("entry_agents", ()))})
                    for t in st.get("closed", [])]
        b.nav_history = [tuple(x) for x in st.get("nav_history", [])]
        b.peak_nav = st.get("peak_nav", b.start_cash)
        b.halted = st.get("halted", False)
        b.halt_bars_left = st.get("halt_bars_left", 0)
        b.halt_count = st.get("halt_count", 0)
        b.halt_reason = st.get("halt_reason", "")
        return b

    def to_dict(self) -> dict[str, Any]:
        return {
            "stats": self.stats(),
            "nav_history": self.nav_history,
            "fills": [asdict(f) for f in self.fills],
            "closed": [asdict(t) for t in self.closed],
            "open_positions": {s: asdict(p) for s, p in self.positions.items() if p.is_open},
        }
