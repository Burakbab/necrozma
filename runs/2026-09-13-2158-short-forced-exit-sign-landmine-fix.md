# Short forced-exit sign landmine fix — 2026-09-13 ~21:47-21:58 UTC

**No live trading this cycle**: tick 30 already handled at 00:20 UTC
(`live_state.json` `updated` `2026-09-13T19:11:27+00:00`, from the prior
~18:47-19:11 UTC evolve batch — confirmed before starting; today's daily bar
was already processed, nothing new to trade). Repo started 27 commits
behind `origin/main` in detached HEAD; `git checkout main && git pull origin
main` fast-forwarded cleanly, no divergence.

## What was found

Continuing AGENTS.md item 5 Phase 2 (short-selling agent wiring) past the
`agents/judges.py` open_positions sign-landmine fixed earlier today
(~09:47-10:20 UTC, commit `cb0d5c7`), a **different, previously-uncaught
landmine in the same family** turned up in `agents/trader.py` and
`loop/engine.py` — neither file was in that morning fix's five-call-site
audit, since that audit was scoped to `open_positions` readers, and these
two bugs live in the forced-exit path instead.

1. **`Guardian.forced_exits`** (`agents/trader.py`) computed `pnl`/
   `from_peak` with long-only formulas (`px / avg_cost - 1`). For a short
   position (`Position.qty < 0`), this reads a rising price (a real loss)
   as a gain, and a falling price (a real gain) as a loss — every
   stop-loss/trailing-stop/take-profit check would fire on the wrong
   condition, or fail to fire on the real one. It also always emitted
   `side="sell"`, which `PaperBroker.sell()` rejects outright for a short
   (`pos.qty <= 0` guard) — so even if the pnl sign had been right by
   accident, the resulting order could never actually close the position.
2. **`Trader.execute`**'s `sell(...) if side == "sell" else buy(...)`
   ternary had the mirror problem: a `"cover"` order (the correct side for
   closing a short) would have fallen into the `buy()` branch instead of
   `broker.cover()`.
3. **`loop/engine.py`**'s circuit-breaker "flatten the book" path
   (`Council.tick`) had the same always-`"sell"` bug for any open short at
   the moment a breaker trip most needs the book actually flattened.

## Fix

- `Guardian.forced_exits` now branches on `pos.is_short`: `pnl = (avg_cost -
  px) / avg_cost` and `from_peak = (peak_price - px) / peak_price` for a
  short (mirrored around `avg_cost`/`peak_price`, matching
  `PaperBroker.cover()`'s own `pnl_pct` convention — `peak_price` is already
  the *lowest* price seen for a short, via `_update_peak`'s own `min()`),
  and emits `side="cover"` instead of `"sell"`.
- `Trader.execute` now dispatches all four `Fill.side` values
  (`buy`/`sell`/`short`/`cover`) explicitly instead of a two-way ternary,
  and the exits-first sort now covers both exit sides (`sell`, `cover`).
- `loop/engine.py`'s inline flatten loop is factored into a new pure
  `_flatten_orders(broker, held) -> list[Order]` helper (same side-aware
  logic), called from `Council.tick`.

New `tests/test_short_forced_exit_landmine.py` (10 tests, built on real
`PaperBroker.short()`/`.cover()` mechanics, not hand-typed pnl numbers):
short price drop is *not* misread as a stop-loss, short price rise *does*
correctly trigger a stop-loss with `side="cover"`, take-profit and trailing
stop both fire on the mirrored condition, a matching long-side test
confirms the untouched branch is unchanged, `Trader.execute` correctly
routes a `"cover"` order to `broker.cover()` (and no longer silently
no-ops it into `buy()`), and `_flatten_orders` covers a short / sells a
long / skips symbols Guardian already handled. Verified each new test
actually depends on the fix: reverted the code via `git stash` while the
new test file stayed on disk — `_flatten_orders` import itself fails
against the pre-fix `loop/engine.py`, confirming the tests aren't
vacuously true.

**No behavior change for any existing caller**: `.short()` still has zero
callers in the live trading/evolution path, so `pos.is_short` is never true
along any real backtest or live tick today — every branch above still takes
exactly the long-only path it always took. `live_state.json` untouched
throughout (`updated` unchanged at `2026-09-13T19:11:27+00:00`). Neither
`core/portfolio.py` nor `constitution/__init__.py` (the two checksummed
files) touched — constitution verified `726dfa4bac85891a` unchanged before
and after. `tools/edit_bundle_module.py sync` run after editing
`agents/trader.py`/`loop/engine.py` directly (the documented step, and the
same one a prior session's run note flagged as easy to forget — confirmed
`sync --check`/`verify` both clean afterward). Full suite: 406/406 (396
baseline + 10 new).

## Still open

The three consults still cannot *propose* closing a short (`held =
is_long(...)` in `agents/consults.py`, unchanged, deliberately — see this
morning's fix). This session's fix means that *if* a short position ever
existed, the mandatory Guardian-level stop-loss/trailing-stop/take-profit/
time-stop safety net and the circuit-breaker flatten-the-book path would
now behave correctly instead of misfiring or silently failing to close it
— but nothing in the live path opens a short yet (`.short()` still has zero
callers), so a consult-level "cover" intent (the discretionary exit, not
the mandatory safety net) is still the concretely-scoped next step for
whoever continues Phase 2 wiring, per AGENTS.md item 5.
