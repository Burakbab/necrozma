"""GUARDIAN + TRADER.

Guardian runs *before* the council every bar and issues mandatory exits: stop
loss, trailing stop, take profit, max holding period. These are not opinions
and no judge can veto them. Consults are optimists by construction; something
in the system has to be unconditionally willing to sell.

Trader has no discretion at all. It takes approved orders and puts them
through the broker at the next open. Keeping judgement out of execution means
a bad fill is a broker-model bug, never a strategy question.
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
                out.append(Order(symbol=sym, side="sell", fraction=1.0,
                                 reason_chain=[f"{self.name}: {reason}"],
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
        # sells first — they fund the buys
        for o in sorted(orders, key=lambda x: 0 if x.side == "sell" else 1):
            px = fill_prices.get(o.symbol)
            if px is None:
                self.rejected += 1
                log.append({"symbol": o.symbol, "side": o.side, "status": "no_price"})
                continue
            reason = " | ".join(o.reason_chain[-2:])
            agents = tuple(sorted({r.split(":")[0].strip() for r in o.reason_chain
                                   if ":" in r and r.split(":")[0].strip().startswith("consult")}))
            f = (self.broker.sell(ts, o.symbol, o.fraction, px, reason) if o.side == "sell"
                 else self.broker.buy(ts, o.symbol, o.quote_amount, px, reason, agents))
            if f is None:
                self.rejected += 1
                log.append({"symbol": o.symbol, "side": o.side, "status": "rejected"})
            else:
                self.executed += 1
                log.append({"symbol": o.symbol, "side": o.side, "status": "filled",
                            "qty": f.qty, "price": f.price, "reason": reason})
        return log
