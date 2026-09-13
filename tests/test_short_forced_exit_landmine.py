"""Regression tests for the forced-exit sign landmine found 2026-09-13 while
scoping AGENTS.md item 5 Phase 2 (short-selling genome/agent wiring), in
`agents/trader.py` and `loop/engine.py` -- a different file pair from the
`open_positions`-reading landmine already fixed in `agents/judges.py`
earlier the same day (`tests/test_short_position_sign_landmine.py`), so not
covered by that fix.

`Guardian.forced_exits` computed `pnl`/`from_peak` with long-only formulas
(`px / avg_cost - 1`), which read a rising price against an open short as a
*gain* instead of the loss it is (and a falling price as a loss instead of
the gain it is) -- every stop-loss/trailing-stop/take-profit/time-stop check
was backwards for a short. It also always emitted `side="sell"`, which
`PaperBroker.sell()` rejects outright for a short (`pos.qty <= 0` guard) --
so even a correctly-signed check could never actually close the position.
`Trader.execute`'s `sell(...)  if side == "sell" else buy(...)` ternary had
the mirror problem: a `"cover"` order would have fallen into the `buy()`
branch instead of `broker.cover()`. `loop/engine.py`'s circuit-breaker
"flatten the book" path (`Council.tick`) had the same always-"sell" bug.

Fixed 2026-09-13 (this commit): `Guardian.forced_exits` branches on
`pos.is_short` for both the pnl/from_peak formulas (mirrored around
`avg_cost`/`peak_price`, matching `PaperBroker.cover()`'s own `pnl_pct`
convention) and the emitted side (`"cover"` instead of `"sell"`).
`Trader.execute` now dispatches all four `Fill.side` values
(`buy`/`sell`/`short`/`cover`) explicitly instead of a two-way ternary, and
sorts both exit sides (`sell`, `cover`) first. `loop/engine.py`'s flatten
logic is factored into a new pure `_flatten_orders(broker, held)` helper,
also side-aware.

No behavior change for any existing (long-only) caller: `.short()` still
has zero callers in the live trading/evolution path, so `pos.is_short` is
never true there and every code path below still takes the branch it always
took. `live_state.json` untouched; neither `core/portfolio.py` nor
`constitution/__init__.py` (the two checksummed files) touched.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agents.trader import Guardian, Trader
from core.genome import Genome
from core.portfolio import PaperBroker
from core.types import Order
from loop.engine import _flatten_orders


def _shorted_broker(entry_price: float = 100.0, quote_amount: float = 1_000.0) -> PaperBroker:
    b = PaperBroker(cash=10_000.0)
    b.short("t0", "XUSDT", quote_amount, entry_price)
    return b


def _age_position(b: PaperBroker, bars: int, prices_seen: list[float]) -> None:
    """Advance `bars_held`/`peak_price` the same way `PaperBroker.mark()`
    would, without touching cash/nav (irrelevant to these tests)."""
    pos = b.positions["XUSDT"]
    for _ in range(bars):
        pos.bars_held += 1
    for px in prices_seen:
        if pos.qty < 0:
            pos.peak_price = min(pos.peak_price, px)
        else:
            pos.peak_price = max(pos.peak_price, px)


def test_short_price_drop_is_a_profit_not_a_stop_loss():
    # Entry 100, price falls to 70 -- a 30% *gain* for a short. The old
    # long-only formula (`px/avg_cost - 1` = -0.30) would have misread this
    # as a stop-loss-triggering loss.
    b = _shorted_broker(entry_price=100.0)
    _age_position(b, bars=2, prices_seen=[90.0, 70.0])
    g = Genome()
    guardian = Guardian(g)
    orders = guardian.forced_exits(b, {"XUSDT": 70.0})
    stop = g.risk.get("stop_loss", -0.12)
    assert stop < 0  # sanity: a real stop-loss threshold
    assert not any("stop loss" in o.reason_chain[0] for o in orders)


def test_short_price_rise_triggers_stop_loss_with_cover_side():
    # Entry 100, price rises to 116 -- a 16% *loss* for a short (worse than
    # the default -12% stop_loss). Must fire as a stop loss and emit
    # side="cover" (the "sell" PaperBroker.sell() would reject outright).
    b = _shorted_broker(entry_price=100.0)
    _age_position(b, bars=2, prices_seen=[105.0, 116.0])
    g = Genome()
    guardian = Guardian(g)
    orders = guardian.forced_exits(b, {"XUSDT": 116.0})
    assert len(orders) == 1
    o = orders[0]
    assert o.side == "cover"
    assert "stop loss" in o.reason_chain[0]


def test_short_take_profit_fires_on_a_big_price_drop_not_a_rise():
    # Entry 100, price falls to 60 -- a 40% gain, past the default 35%
    # take_profit. The unmirrored formula would have computed pnl = -0.40
    # (a big loss) here, so this would previously have been silent (no
    # branch crosses -0.40 except stop_loss at -0.12, which *would* have
    # fired -- for the wrong reason and the wrong side).
    b = _shorted_broker(entry_price=100.0)
    _age_position(b, bars=2, prices_seen=[80.0, 60.0])
    g = Genome()
    guardian = Guardian(g)
    orders = guardian.forced_exits(b, {"XUSDT": 60.0})
    assert len(orders) == 1
    o = orders[0]
    assert o.side == "cover"
    assert "take profit" in o.reason_chain[0]


def test_short_trailing_stop_uses_the_lowest_price_as_peak():
    # Price falls to a low of 80 (peak for a short, via _update_peak's own
    # min()), then rises back to 95: still an overall profit (pnl > 0) but
    # a real give-back from the low. trailing_stop default is -0.15, and
    # (peak - px)/peak = (80-95)/80 = -0.1875, past it.
    b = _shorted_broker(entry_price=100.0)
    _age_position(b, bars=2, prices_seen=[80.0, 95.0])
    g = Genome()
    guardian = Guardian(g)
    orders = guardian.forced_exits(b, {"XUSDT": 95.0})
    assert len(orders) == 1
    o = orders[0]
    assert o.side == "cover"
    assert "trailing stop" in o.reason_chain[0]


def test_long_forced_exit_behavior_is_unchanged():
    # Same scenario shape as the stop-loss short test, mirrored to a long,
    # to confirm the branch for pos.is_short == False is untouched.
    b = PaperBroker(cash=10_000.0)
    b.buy("t0", "XUSDT", 1_000.0, 100.0)
    pos = b.positions["XUSDT"]
    pos.bars_held = 2
    pos.peak_price = 100.0
    g = Genome()
    guardian = Guardian(g)
    orders = guardian.forced_exits(b, {"XUSDT": 84.0})  # -16% -> past -12% stop
    assert len(orders) == 1
    assert orders[0].side == "sell"
    assert "stop loss" in orders[0].reason_chain[0]


def test_trader_execute_routes_cover_orders_to_broker_cover():
    b = _shorted_broker(entry_price=100.0, quote_amount=1_000.0)
    trader = Trader(b)
    order = Order(symbol="XUSDT", side="cover", fraction=1.0,
                  reason_chain=["guardian: test"], conviction=1.0, agreement=1.0)
    log = trader.execute("t1", [order], {"XUSDT": 90.0})
    assert log[0]["status"] == "filled"
    assert "XUSDT" not in b.positions  # fully covered, position closed
    assert trader.executed == 1
    assert trader.rejected == 0


def test_trader_execute_no_longer_misroutes_cover_into_buy():
    # Before the fix, `sell(...) if side == "sell" else buy(...)` would send
    # a "cover" order into `broker.buy()`, which would try to add to a
    # *long* position on a symbol that's actually short -- buy() itself
    # guards against flip-in-one-call and returns None, so this would have
    # silently rejected the order and left the short open forever.
    b = _shorted_broker(entry_price=100.0, quote_amount=1_000.0)
    cash_before = b.cash
    trader = Trader(b)
    order = Order(symbol="XUSDT", side="cover", fraction=1.0,
                  reason_chain=["guardian: test"], conviction=1.0, agreement=1.0)
    trader.execute("t1", [order], {"XUSDT": 90.0})
    # A real cover changes cash (buys back the short); a misrouted-to-buy
    # no-op would have left cash untouched and the short still open.
    assert b.cash != cash_before
    assert "XUSDT" not in b.positions


def test_flatten_orders_covers_an_open_short_instead_of_selling_it():
    b = _shorted_broker(entry_price=100.0)
    orders = _flatten_orders(b, held=set())
    assert len(orders) == 1
    assert orders[0].side == "cover"
    assert orders[0].symbol == "XUSDT"


def test_flatten_orders_sells_an_open_long_unchanged():
    b = PaperBroker(cash=10_000.0)
    b.buy("t0", "XUSDT", 1_000.0, 100.0)
    orders = _flatten_orders(b, held=set())
    assert len(orders) == 1
    assert orders[0].side == "sell"


def test_flatten_orders_skips_symbols_guardian_already_handled():
    b = _shorted_broker(entry_price=100.0)
    orders = _flatten_orders(b, held={"XUSDT"})
    assert orders == []
