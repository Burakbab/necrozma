"""Short selling (Phase 1): PaperBroker.short()/.cover(), borrow accrual.

Re-implemented 2026-09-08 per the design/trace in
runs/2026-08-30-0951-short-selling-design-pass.md and
runs/2026-08-30-1301-short-selling-phase1-blocked-by-seal.md — the code was
built once (2026-08-30), then reverted because shipping it trips
CONSTITUTION MODIFIED without a human re-seal in hand first. That sign-off
now exists, so this reapplies the same design (signed-qty convention, the
cross-side guards, borrow accrual in mark()) against the current file.
"""
from __future__ import annotations

from core.portfolio import PaperBroker, Position


def _broker(**kw) -> PaperBroker:
    defaults = dict(cash=10_000.0, fee_bps=10.0, slippage_bps=5.0, min_order=25.0)
    defaults.update(kw)
    return PaperBroker(**defaults)


# -- short -> cover, profit and loss ----------------------------------------

def test_short_then_cover_profits_on_a_price_drop():
    b = _broker()
    cash_before = b.cash
    b.short("t0", "XUSDT", 1_000.0, 100.0)
    assert b.positions["XUSDT"].qty < 0
    assert b.cash > cash_before  # opening a short receives cash

    f = b.cover("t1", "XUSDT", 1.0, 80.0)
    assert f is not None
    trade = b.closed[-1]
    assert trade.pnl > 0  # price fell after shorting: profit
    assert "XUSDT" not in b.positions  # fully covered, position closed


def test_short_then_cover_loses_on_a_price_rise():
    b = _broker()
    b.short("t0", "XUSDT", 1_000.0, 100.0)
    b.cover("t1", "XUSDT", 1.0, 120.0)
    trade = b.closed[-1]
    assert trade.pnl < 0  # price rose after shorting: loss


def test_partial_cover_leaves_a_smaller_short_open():
    b = _broker()
    b.short("t0", "XUSDT", 1_000.0, 100.0)
    full_qty = abs(b.positions["XUSDT"].qty)

    b.cover("t1", "XUSDT", 0.4, 90.0)
    pos = b.positions["XUSDT"]
    assert pos.is_short
    assert abs(pos.qty) == full_qty * 0.6
    assert len(b.closed) == 1


# -- equity falls as price rises against a short -----------------------------

def test_equity_falls_as_price_rises_against_a_short():
    b = _broker()
    b.short("t0", "XUSDT", 1_000.0, 100.0)
    eq_at_entry = b.equity({"XUSDT": 100.0})
    eq_after_rise = b.equity({"XUSDT": 150.0})
    eq_after_drop = b.equity({"XUSDT": 50.0})
    assert eq_after_rise < eq_at_entry < eq_after_drop


# -- cross-side guards --------------------------------------------------------

def test_short_refuses_when_already_long():
    b = _broker()
    b.buy("t0", "XUSDT", 1_000.0, 100.0)
    f = b.short("t1", "XUSDT", 500.0, 100.0)
    assert f is None
    assert b.positions["XUSDT"].qty > 0  # untouched


def test_buy_refuses_when_already_short():
    b = _broker()
    b.short("t0", "XUSDT", 1_000.0, 100.0)
    f = b.buy("t1", "XUSDT", 500.0, 100.0)
    assert f is None
    assert b.positions["XUSDT"].qty < 0  # untouched


def test_sell_refuses_on_a_short_position():
    b = _broker()
    b.short("t0", "XUSDT", 1_000.0, 100.0)
    f = b.sell("t1", "XUSDT", 1.0, 100.0)
    assert f is None
    assert b.positions["XUSDT"].is_short


def test_cover_refuses_on_a_long_position():
    b = _broker()
    b.buy("t0", "XUSDT", 1_000.0, 100.0)
    f = b.cover("t1", "XUSDT", 1.0, 100.0)
    assert f is None
    assert b.positions["XUSDT"].qty > 0


# -- no-leverage cash cap ------------------------------------------------------

def test_short_notional_capped_by_available_cash():
    b = _broker(cash=1_000.0)
    f = b.short("t0", "XUSDT", 5_000.0, 100.0)
    assert f is not None
    # target notional was capped at self.cash *before* the short was opened
    assert f.qty * f.price <= 1_000.0 * 1.0001  # small tolerance for eff price


# -- borrow accrual ------------------------------------------------------------

def test_borrow_accrues_against_cash_for_an_open_short():
    b = _broker(borrow_bps_per_bar=10.0)
    b.short("t0", "XUSDT", 1_000.0, 100.0)
    cash_after_open = b.cash
    b.mark("t1", {"XUSDT": 100.0})
    assert b.cash < cash_after_open  # borrow cost charged this bar


def test_no_borrow_charge_when_rate_is_zero():
    b = _broker(borrow_bps_per_bar=0.0)
    b.short("t0", "XUSDT", 1_000.0, 100.0)
    cash_after_open = b.cash
    b.mark("t1", {"XUSDT": 100.0})
    assert b.cash == cash_after_open


def test_borrow_never_charged_against_a_long_position():
    b = _broker(borrow_bps_per_bar=10.0)
    b.buy("t0", "XUSDT", 1_000.0, 100.0)
    cash_after_open = b.cash
    b.mark("t1", {"XUSDT": 100.0})
    assert b.cash == cash_after_open  # only price move, no borrow on a long


# -- circuit breaker still works with an open short ---------------------------

def test_circuit_breaker_trips_on_a_losing_short():
    b = _broker()
    b.short("t0", "XUSDT", 5_000.0, 100.0)
    # price rallies hard against the short -> equity drawdown -> breaker trips
    nav = b.mark("t1", {"XUSDT": 100.0})
    assert not b.halted
    nav = b.mark("t2", {"XUSDT": 200.0}, dd_halt=0.10)
    assert b.halted
    assert b.halt_reason


# -- peak_price direction ------------------------------------------------------

def test_peak_price_tracks_the_low_for_a_short():
    b = _broker()
    b.short("t0", "XUSDT", 1_000.0, 100.0)
    assert b.positions["XUSDT"].peak_price == 100.0
    b.mark("t1", {"XUSDT": 90.0})
    assert b.positions["XUSDT"].peak_price == 90.0
    b.mark("t2", {"XUSDT": 95.0})
    assert b.positions["XUSDT"].peak_price == 90.0  # rally doesn't raise it back


def test_peak_price_tracks_the_high_for_a_long_unchanged_behavior():
    b = _broker()
    b.buy("t0", "XUSDT", 1_000.0, 100.0)
    assert b.positions["XUSDT"].peak_price == 100.0
    b.mark("t1", {"XUSDT": 110.0})
    assert b.positions["XUSDT"].peak_price == 110.0
    b.mark("t2", {"XUSDT": 105.0})
    assert b.positions["XUSDT"].peak_price == 110.0  # pullback doesn't lower it


# -- state round trip -----------------------------------------------------------

def test_short_position_state_round_trip():
    b = _broker(borrow_bps_per_bar=5.0)
    b.short("t0", "XUSDT", 1_000.0, 100.0)
    b.mark("t1", {"XUSDT": 95.0})
    st = b.to_state()
    b2 = PaperBroker.from_state(st)
    assert b2.borrow_bps_per_bar == 5.0
    assert b2.positions["XUSDT"].qty == b.positions["XUSDT"].qty
    assert b2.positions["XUSDT"].is_short
    assert b2.cash == b.cash


def test_pre_phase1_state_loads_with_zero_borrow_rate():
    # a saved state from before this change has no borrow_bps_per_bar key
    st = {"start_cash": 10_000.0, "cash": 10_000.0, "fee_bps": 10.0,
          "slippage_bps": 5.0, "min_order": 25.0, "positions": {}, "fills": [],
          "closed": [], "nav_history": [], "peak_nav": 10_000.0,
          "halted": False, "halt_bars_left": 0, "halt_count": 0, "halt_reason": ""}
    b = PaperBroker.from_state(st)
    assert b.borrow_bps_per_bar == 0.0


# -- regression: existing long-only behavior is byte-identical ----------------

def test_buy_sell_mark_unchanged_for_a_caller_that_never_shorts():
    b = _broker()
    b.buy("t0", "XUSDT", 1_000.0, 100.0, reason="entry", agents=("consult_a",))
    b.mark("t1", {"XUSDT": 105.0})
    fill = b.sell("t2", "XUSDT", 1.0, 110.0, reason="exit")

    assert fill is not None
    assert fill.side == "sell"
    trade = b.closed[-1]
    # same formulas as before this change: eff = 110*(1-5/10000), fee on gross
    eff = 110.0 * (1 - 5.0 / 10_000)
    qty = trade.qty
    gross = qty * eff
    fee = gross * 10.0 / 10_000
    expected_pnl = (eff - 100.0 * (1 + 5.0 / 10_000)) * qty - fee
    assert abs(trade.pnl - expected_pnl) < 1e-9
    assert "XUSDT" not in b.positions
