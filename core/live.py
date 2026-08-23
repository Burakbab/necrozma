"""LIVE PAPER TRADING — real prices, imaginary money, one bar at a time.

The backtest and the live run share the same Council code path. That is the
whole point: when the live account diverges from what the backtest said it
would do, that's a bug worth chasing, not a mystery.

Convention: run shortly after 00:00 UTC. The decision is made on the last
*closed* daily bar; the fill is the live price at the moment of execution,
which is a few minutes into the new bar — the closest live analogue of the
backtest's "fill at next open".

State lives in a single JSON blob so it can be parked in the Claude project
and survive this container being reclaimed.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any

from agents.trader import Trader
from core import market
from core.genome import Genome
from core.market import Replay, ReplayWindow
from core.portfolio import PaperBroker

STATE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                         "state", "live")
STATE_PATH = os.path.join(STATE_DIR, "account.json")
JOURNAL_PATH = os.path.join(STATE_DIR, "journal.jsonl")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def live_prices(symbols: list[str]) -> dict[str, float]:
    """Current mid prices straight off the exchange."""
    out: dict[str, float] = {}
    try:
        data = market._get(f"{market.BASE}/ticker/price")
        book = {t["symbol"]: float(t["price"]) for t in data}  # type: ignore[union-attr]
        for s in symbols:
            if s in book:
                out[s] = book[s]
    except Exception:  # noqa: BLE001 - fall back to last close below
        pass
    return out


class LiveAccount:
    def __init__(self, state: dict[str, Any] | None = None):
        self.state = state or {}
        self.genome = (Genome(self.state["genome"]) if self.state.get("genome")
                       else Genome.champion())
        self.broker = (PaperBroker.from_state(self.state["broker"])
                       if self.state.get("broker") else
                       PaperBroker(cash=float(self.genome.data["broker"]["start_cash"]),
                                   fee_bps=float(self.genome.data["broker"]["fee_bps"]),
                                   slippage_bps=float(self.genome.data["broker"]["slippage_bps"])))
        self.journal: list[dict] = self.state.get("journal", [])
        # evolution history rides along in the same durable blob — otherwise a
        # promotion's reasoning is lost the moment the container is reclaimed
        self.lineage: list[dict] = self.state.get("lineage", [])
        self.started = self.state.get("started") or _now()
        self.ticks = int(self.state.get("ticks", 0))
        self.researcher_memory: dict = self.state.get("researcher_memory", {})
        # verdicts written back onto flagged (agents.judges.flag_hard_call)
        # journal entries by a later scheduled session reasoning about them --
        # AGENTS.md item 4 design (b), "review after the fact" rather than
        # gating execution. Defaults to empty so loading any state saved
        # before this field existed round-trips unchanged.
        self.hard_call_reviews: list[dict] = self.state.get("hard_call_reviews", [])

    # -- io ----------------------------------------------------------------
    @classmethod
    def load(cls, path: str = STATE_PATH) -> "LiveAccount":
        if os.path.exists(path):
            with open(path) as f:
                return cls(json.load(f))
        return cls()

    def save(self, path: str = STATE_PATH) -> str:
        # dirname("live_state.json") is "" — makedirs("") raises. A bare
        # filename is exactly what the scheduled run uses, so this crashed
        # *after* the trade was booked and before the state was written.
        d = os.path.dirname(path)
        if d:
            os.makedirs(d, exist_ok=True)
        blob = {
            "started": self.started, "ticks": self.ticks, "updated": _now(),
            "genome": self.genome.data,
            "broker": self.broker.to_state(),
            "journal": self.journal[-400:],
            "lineage": self.lineage[-200:],
            "researcher_memory": self.researcher_memory,
            "hard_call_reviews": self.hard_call_reviews,
        }
        with open(path, "w") as f:
            json.dump(blob, f, indent=2, default=str)
        return path

    def add_hard_call_review(self, tick: int, verdict: str, notes: str = "") -> dict[str, Any]:
        """Record a reasoned verdict on a flagged bar.

        Never gates execution -- the tick this reviews already ran, same-pass,
        long before this is ever called; this only appends a durable note a
        later scheduled session (or a human) can read. Raises on a `tick`
        that either doesn't exist in the journal or was never actually
        flagged, so a typo can't quietly manufacture a review for a bar that
        was never a hard call.
        """
        entry = next((e for e in self.journal if e.get("tick") == tick), None)
        if entry is None:
            raise ValueError(f"no journal entry for tick {tick}")
        hc = (entry.get("decision") or {}).get("hard_call") or {}
        if not hc.get("is_hard_call"):
            raise ValueError(f"tick {tick} was not flagged as a hard call")
        record = {
            "tick": tick, "bar": entry.get("bar"), "reviewed_at": _now(),
            "verdict": verdict, "notes": notes, "reasons": hc.get("reasons", []),
        }
        self.hard_call_reviews.append(record)
        return record

    # -- the tick ----------------------------------------------------------
    def tick(self, use_live_price: bool = True, refresh: bool = True,
             force: bool = False) -> dict[str, Any]:
        from loop.engine import Council  # local import: avoids a cycle

        uni = self.genome.universe
        interval = self.genome.bar_interval
        data = market.load_universe(uni, interval, years=1.5, refresh=refresh)
        if not data:
            return {"error": "no market data"}

        replay = Replay(data)
        n = len(replay)
        if n < 80:
            return {"error": f"not enough history ({n} bars)"}

        # last fully closed daily bar. Today's forming bar is index n-1, so the
        # last closed one is n-2. Never decide on a bar that isn't finished.
        i = n - 2
        bar_id = str(replay.index[i])

        # Idempotency: an unattended daily job can fire twice (retry, manual
        # re-run, clock wobble). Trading the same bar twice would double the
        # position and corrupt the track record, so refuse politely.
        if self.journal and self.journal[-1].get("bar") == bar_id and not force:
            return {"skipped": f"bar {bar_id[:10]} already traded (tick {self.ticks})",
                    "tick": self.ticks, "bar": bar_id,
                    "nav_after": round(self.broker.equity(
                        {s: replay.close_at(s, i) for s in replay.data
                         if replay.close_at(s, i)}), 2)}

        window = ReplayWindow(replay.data, i, replay.index[i], replay.arrays)
        closes = {s: replay.close_at(s, i) for s in replay.data}
        closes = {s: p for s, p in closes.items() if p}

        fills = live_prices(uni) if use_live_price else {}
        for s, p in closes.items():
            fills.setdefault(s, p)

        council = Council(self.genome, self.broker)
        before_nav = self.broker.equity(closes)
        before_cash = self.broker.cash
        council.tick(window, closes, fills, log_detail=True)
        after_nav = self.broker.equity(fills if fills else closes)

        self.ticks += 1
        entry = {
            "ts": _now(),
            "bar": str(replay.index[i]),
            "tick": self.ticks,
            "nav_before": round(before_nav, 2),
            "nav_after": round(after_nav, 2),
            "cash": round(self.broker.cash, 2),
            "cash_before": round(before_cash, 2),
            "positions": {s: round(p.qty * fills.get(s, closes.get(s, 0)), 2)
                          for s, p in self.broker.positions.items() if p.is_open},
            "genome_version": self.genome.version,
            "halted": self.broker.halted,
            "decision": council.decision_log[-1] if council.decision_log else None,
        }
        self.journal.append(entry)
        return entry

    # -- reporting ---------------------------------------------------------
    def signals(self) -> str:
        """Today's decision, in plain language.

        This is the no-credentials path. Nothing here ever needs a brokerage
        account, an API key, a tax ID, or KYC: prices come from a public
        endpoint and the portfolio is tracked in this file. If real money is
        ever involved, the system says what it would do and a human places the
        order wherever they already have an account — the ledger stays
        authoritative either way, because the ledger was never the broker's.
        """
        if not self.journal:
            return "No decision recorded yet — run a tick first."
        e = self.journal[-1]
        d = e.get("decision") or {}
        nav = e.get("nav_after", 0.0)
        ret = (nav / self.broker.start_cash - 1) if self.broker.start_cash else 0.0

        lines = [
            f"Project Necrozma — decision for bar {str(e.get('bar', ''))[:10]}  (tick {e.get('tick')})",
            f"Account: ${nav:,.2f}  ({ret:+.2%} since {str(self.started)[:10]})  "
            f"cash ${e.get('cash', 0):,.2f}",
            f"Market read: {d.get('regime', '?')}, breadth {d.get('breadth', 0):.0%}",
            "",
        ]

        forced = d.get("forced_exits") or []
        orders = d.get("orders") or []
        if not forced and not orders:
            lines.append("  ACTION: none. Hold the current book.")
        for f in forced:
            lines.append(f"  SELL ALL  {f['symbol']:<10s}  (mandatory) — {f['why']}")
        for o in orders:
            if o["side"] == "sell":
                pct = int(o.get("fraction", 1.0) * 100)
                lines.append(f"  SELL {pct:>3d}%  {o['symbol']:<10s}")
            else:
                lines.append(f"  BUY  ${o.get('amount', 0):>8,.0f}  {o['symbol']:<10s}"
                             f"  (agreement {o.get('agreement', 0):.0%})")
            for r in o.get("why", [])[:3]:
                lines.append(f"           └─ {r}")

        book = e.get("positions") or {}
        lines.append("")
        lines.append("Book after this decision:")
        if book:
            for s, v in sorted(book.items(), key=lambda kv: -kv[1]):
                lines.append(f"  {s:<10s} ${v:>9,.0f}   {v / max(nav, 1):>5.1%}")
        else:
            lines.append("  all cash")
        return "\n".join(lines)

    def summary(self) -> dict[str, Any]:
        bpy = market.BARS_PER_YEAR.get(self.genome.bar_interval, 365.25)
        st = self.broker.stats(bars_per_year=bpy)
        return {
            "started": self.started, "ticks": self.ticks,
            "genome_version": self.genome.version,
            "nav": self.broker.nav_history[-1][1] if self.broker.nav_history else self.broker.cash,
            "cash": self.broker.cash,
            "open_positions": {s: {"qty": p.qty, "avg_cost": p.avg_cost,
                                   "bars_held": p.bars_held,
                                   "entry_agents": list(p.entry_agents)}
                               for s, p in self.broker.positions.items() if p.is_open},
            "stats": st,
            "halted": self.broker.halted, "halt_reason": self.broker.halt_reason,
        }
