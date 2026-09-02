# Equities/FX design pass (item 6)

3-hourly check, ~15:46-16:05 UTC. No code shipped this session. `live_state.json`
untouched, no protected file touched. Genome still v3 (1d) live, untouched.

## Why this item, not item 2

Item 2 (4h shadow evolution / fold-1 cold-start drawdown) hit an explicit
decision fork this morning (~12:47-13:09 UTC): all single-lever alternatives
to the `consv1 + trailing_stop + ramp` stack are now exhausted, and what's
left is an owner call (accept the full stack and attempt a real, non-shadow
promotion, or park the thread) — not something a single 3-hourly session
should decide unilaterally, and not something landable in one session either
way. The two redirect options the 12:47 UTC entry names are both currently
no-ops: `review-hard-calls` reports 0 pending (item 4), and short selling
Phase 1 is blocked without a human sign-off + constitution re-seal in hand
(item 5, 2026-08-30 13:01 UTC entry). Item 6 ("Equities/FX behind the same
`MarketData` interface") has never had a design pass and was the next
concretely-scoped item with real open work.

## What's actually there today

Item 6's own wording implies a `MarketData` interface already exists to plug
into. It doesn't, formally:

- `core/market.py` (336 lines) has no `MarketData` class, ABC, or Protocol.
  The "interface" is really the free-function surface: `fetch_klines()`
  (`:48`), `load()` (`:133`), `load_universe()` (`:180`), `Bar`/
  `ReplayWindow`/`Replay` (`:203-311`), `top_symbols_by_volume()` (`:314`).
  The module docstring (`:1-11`) already stakes the claim — "Nothing above
  this module knows what an exchange or an asset class is. Adding equities
  later means adding a fetcher here, not touching a single agent." — but
  it's untested: no second fetcher has ever been written, and the ad-hoc
  import pattern below means it isn't quite true yet either.
- There is no single dependency-injection point. `core.market` is imported
  directly in ~20+ places: `core/live.py:23,42`, `loop/engine.py:26,479`,
  `agents/analyst.py:15`, `run_from_files.py` (5 sites), `tools/*.py` (6
  files), plus one `from core import market` per function inside
  `evotrader_bundle.py`'s flattened mirror (30+ sites, per the bundle's own
  per-function-import convention). This is a materially different shape
  than item 5's `PaperBroker` precedent: there's no one class with a small
  method surface to extend. Swapping in a second data source touches every
  call site that assumes Binance/24-7/`"XXXUSDT"`, not just one module.
- **Crypto-specific assumptions found, with the sites that encode them:**
  - *Live price feed is a second, separate crypto-only path*: `core/live.py`
    live-fill pricing hits Binance's `ticker/price` endpoint directly
    (`live_prices()`, `core/live.py:38-49`), bypassing even `core.market`'s
    historical-bar surface.
  - *No market-hours/session/holiday gate exists anywhere.* `core/live.py`'s
    module docstring says "run shortly after 00:00 UTC" and the tick always
    decides on the last closed bar (`i = n - 2`, `core/live.py:145`) — crypto
    never closes, so nothing has ever needed to check whether "today" is a
    trading day. Equities/FX would need this added from scratch, not
    relaxed from something that over-constrains today.
  - *Calendar-grid assumption in the data-integrity check.*
    `find_gaps(df, interval)` (`core/market.py:114-130`) builds a fixed-step
    `pd.date_range` from first to last timestamp and diffs it against what's
    present. For crypto (24/7) this is exactly right. For equities/FX it
    would flag every weekend and holiday as a "gap" — a false-positive data
    integrity failure, not a real one. `Replay`'s reindex-to-union-index step
    (`core/market.py:277-283`) and `BARS_PER_YEAR` (`core/market.py:33`,
    used to annualise Sharpe/Sortino/CAGR) carry the same continuous-calendar
    assumption.
  - *Symbol format is load-bearing, not cosmetic.* `"BTCUSDT"`-style
    base+quote concatenation appears in `core/genome.py:40-45` (default
    `universe`), `agents/analyst.py:127` (`regime_anchor` default
    `"BTCUSDT"`), and `top_symbols_by_volume()`
    (`core/market.py:314-336`, hardcoded USDT-quote + stablecoin-exclusion
    filtering).
  - *Genome schema has no asset-class/quote-currency/session-calendar knob.*
    `bar_interval` (`"1h"/"4h"/"1d"` only, `core/genome.py:29-33`) and
    `universe` are the only market-shape fields that exist.
- **`.env.example` already stages Alpaca paper-trading credentials**
  (`APCA_API_BASE_URL`, `APCA_API_KEY_ID`, `APCA_API_SECRET_KEY`,
  `.env.example:3-6`) — but a repo-wide `grep -i "APCA|ALPACA"` finds zero
  other references anywhere in code, tests, or `AGENTS.md`. Flagging this
  explicitly rather than acting on it: it reads as a forgotten or
  anticipatory placeholder from before this item existed, not partial
  implementation. Worth a human confirming intent (was Alpaca ever actually
  planned as the equities data source?) rather than a session guessing.

## Why no code this session

`core/portfolio.py` and `constitution/__init__.py` are the only two files
`constitution.checksum()` hashes (`_PROTECTED`,
`constitution/__init__.py:226`) — neither is touched by anything above, so
this item doesn't carry item 5's specific "accidentally broke the seal"
trap. But the honest small-and-isolated slice available today (e.g. a
session-aware `find_gaps` variant, or a new `asset_class` genome field) would
have no real consumer yet: there is still no second fetcher, no decision on
Alpaca vs. another source, and no design for how `core/live.py`'s tick
cadence would gate on a trading calendar. Shipping that scaffolding now would
be exactly the kind of speculative, untested-against-real-use abstraction
this codebase's own conventions (and every prior design-pass item, e.g.
item 5) argue against — a genome field or fetcher stub with zero real
callers is dead weight, not progress, until there's an actual second data
source to wire it to.

## Concretely scoped next step

Before any code: a human decision on what "equities/FX" should actually mean
here — a real broker/data account (the staged Alpaca keys suggest one was
once considered) or a free historical-only mirror analogous to
`data-api.binance.vision`. Once that's picked, Phase 1 (mirroring item 5's
shape) is:
1. A new fetcher in `core/market.py` returning the same UTC-indexed OHLCV
   `DataFrame` shape `load()` does today, tested against synthetic
   business-day-only data in isolation — zero change to any existing
   crypto call site.
2. A session-calendar-aware variant of `find_gaps` (additive optional param,
   default preserves today's continuous-calendar behavior byte-for-byte),
   tested against both a crypto-shaped fixture (no behavior change) and a
   weekday-only fixture (correctly reports zero gaps for weekend absences).
3. Stop there. Wiring a real trading-hours gate into `core/live.py`'s tick
   cadence, a genome `asset_class`/quote-currency field, and updating
   `top_symbols_by_volume()`'s USDT-only filtering are all separate,
   bigger, riskier follow-on sessions — same "don't do it all in one
   sitting" discipline item 5 and item 7 both used.

## Verification this session

No code changed. `python3 -m pytest -q` run as a pre-existing-baseline check
before starting: 338/338 passed (0:02:40). No file outside `runs/` and
`AGENTS.md` touched.
