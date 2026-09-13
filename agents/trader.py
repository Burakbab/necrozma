"""GUARDIAN + TRADER.

Guardian runs *before* the council every bar and issues mandatory exits: stop
loss, trailing stop, take profit, max holding period. These are not opinions
and no judge can veto them. Consults are optimists by construction; something
in the system has to be unconditionally willing to sell.

Trader has no discretion at all. It takes approved orders and puts them
through the broker at the next open. Keeping judgement out of execution means
a bad fill is a broker-model bug, never a strategy question.

Both are sign-aware for a short position (`Position.qty < 0`, per
`core/portfolio.py`'s Phase 1 convention) as of 2026-09-13: `forced_exits`'s
`pnl`/`from_peak` formulas were written long-only and, unmirrored, read a
rising price against an open short as a *gain* instead of the loss it is
(and vice versa) -- wrong sign on every stop/trailing-stop/take-profit
check. It also always emitted `side="sell"`, which `PaperBroker.sell()`
rejects outright for a short (`pos.qty <= 0` guard). `Trader.execute`'s
sell-or-buy ternary had the mirror problem: a `"cover"` order would have
fallen into the `buy()` branch. Found while scoping AGENTS.md item 5 Phase
2 (the `agents/judges.py` open_positions sign-landmine fixed earlier
2026-09-13 didn't cover this file). No behavior change for any existing
caller: `.short()` still has zero callers in the live trading/evolution
path, so `Position.qty` is never negative there and every branch below
still takes the long-only path it always did.
"""
from __future__ import annotations

from core.genome import Genome
from core.portfolio import PaperBroker
from core.types import Order, Verdict


class Guardian:
    name = "guardian"

    def __init__(self, genome: Genome):
        self.r = genome.risk

    def forced_exits(self, broker: PaperBroker, prices: dict[str, float]) -> list[Order]:
        out: list[Order] = []
        stop = float(self.r.get("stop_loss", -0.12))
        trail = float(self.r.get("trailing_stop", -0.15))
        tp = float(self.r.get("take_profit", 0.35))
        max_bars = int(self.r.get("max_bars_held", 60))
        min_bars = int(self.r.get("min_bars_held", 1))

        for sym, pos in list(broker.positions.items()):
            if not pos.is_open:
                continue
            px = prices.get(sym)
            if not px or pos.avg_cost <= 0:
                continue
            if pos.bars_held < min_bars:
                continue
            # A short profits when price falls, and its peak (set by
            # `_update_peak` to the *lowest* price seen) is its best point --
            # both formulas mirror the long ones around that.
            if pos.is_short:
                pnl = (pos.avg_cost - px) / pos.avg_cost
                from_peak = (pos.peak_price - px) / pos.peak_price if pos.peak_price > 0 else 0.0
            else:
                pnl = px / pos.avg_cost - 1
                from_peak = (px / pos.peak_price - 1) if pos.peak_price > 0 else 0.0

            reason = None
            if pnl <= stop:
                reason = f"stop loss hit ({pnl:+.1%})"
            elif from_peak <= trail and pnl > 0:
                reason = f"trailing stop ({from_peak:+.1%} off peak, locking {pnl:+.1%})"
            elif pnl >= tp:
                reason = f"take profit ({pnl:+.1%})"
            elif pos.bars_held >= max_bars:
                reason = f"time stop ({pos.bars_held} bars, {pnl:+.1%})"

            if reason:
                out.append(Order(symbol=sym, side=("cover" if pos.is_short else "sell"),
                                 fraction=1.0, reason_chain=[f"{self.name}: {reason}"],
                                 conviction=1.0, agreement=1.0))
        return out


class Trader:
    name = "trader"

    def __init__(self, broker: PaperBroker):
        self.broker = broker
        self.executed = 0
        self.rejected = 0

    def execute(self, ts: str, orders: list[Order],
                fill_prices: dict[str, float]) -> list[dict]:
        log: list[dict] = []
        exit_sides = ("sell", "cover")
        # exits first — they fund the entries
        for o in sorted(orders, key=lambda x: 0 if x.side in exit_sides else 1):
            px = fill_prices.get(o.symbol)
            if px is None:
                self.rejected += 1
                log.append({"symbol": o.symbol, "side": o.side, "status": "no_price"})
                continue
            reason = " | ".join(o.reason_chain[-2:])
            agents = tuple(sorted({r.split(":")[0].strip() for r in o.reason_chain
                                   if ":" in r and r.split(":")[0].strip().startswith("consult")}))
            if o.side == "sell":
                f = self.broker.sell(ts, o.symbol, o.fraction, px, reason)
            elif o.side == "cover":
                f = self.broker.cover(ts, o.symbol, o.fraction, px, reason)
            elif o.side == "buy":
                f = self.broker.buy(ts, o.symbol, o.quote_amount, px, reason, agents)
            elif o.side == "short":
                f = self.broker.short(ts, o.symbol, o.quote_amount, px, reason, agents)
            else:
                f = None
            if f is None:
                self.rejected += 1
                log.append({"symbol": o.symbol, "side": o.side, "status": "rejected"})
            else:
                self.executed += 1
                log.append({"symbol": o.symbol, "side": o.side, "status": "filled",
                            "qty": f.qty, "price": f.price, "reason": reason})
        return log
