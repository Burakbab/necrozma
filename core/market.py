"""Market data layer.

Single responsibility: give the rest of the system clean OHLCV bars, and make
lookahead bias structurally impossible during replay.

Source: Binance public market-data mirror (data-api.binance.vision).
Free, no API key, 24/7, ~490 USDT pairs, history back to 2017.

Nothing above this module knows what an exchange or an asset class is. Adding
equities later means adding a fetcher here, not touching a single agent.
"""
from __future__ import annotations

import json
import os
import time
import urllib.request
import urllib.error
from dataclasses import dataclass
from typing import Iterator, Sequence

import numpy as np
import pandas as pd

BASE = "https://data-api.binance.vision/api/v3"
CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "state", "cache")

_MS = {"1h": 3_600_000, "4h": 14_400_000, "1d": 86_400_000}

# Bars-per-year for each supported interval, used to annualise stats
# (Sharpe/Sortino/turnover/CAGR) correctly regardless of which bar size a
# genome trades on. Keyed the same as _MS so the two can never drift apart.
BARS_PER_YEAR = {"1h": 24 * 365.25, "4h": 6 * 365.25, "1d": 365.25}


def _get(url: str, retries: int = 4) -> object:
    last = None
    for i in range(retries):
        try:
            with urllib.request.urlopen(url, timeout=25) as r:
                return json.loads(r.read().decode())
        except Exception as e:  # noqa: BLE001 - network is allowed to be flaky
            last = e
            time.sleep(1.5 * (i + 1))
    raise RuntimeError(f"fetch failed: {url}: {last}")


def fetch_klines(symbol: str, interval: str = "1d", start_ms: int | None = None,
                 end_ms: int | None = None) -> pd.DataFrame:
    """Page through Binance klines. Returns a UTC-indexed OHLCV frame.

    A short page (`len(batch) < 1000`) used to be treated as unconditional proof
    the range was exhausted. It isn't: a transient partial response from the
    API mid-range looks identical to a real end-of-history page, and the old
    code broke out of the loop either way -- silently returning a truncated
    frame with no error, no warning, nothing that would ever show up short of
    someone diffing bar counts against a full recount. `load_universe`'s own
    2026-08-22 3-hourly check found exactly this: a champion's full-history
    backtest reporting -46.5% maxDD (crossing its own MAX_DD_HARD_FAIL gate)
    when several independent sessions the same week had reported -34.1% on the
    same historical window -- and this session's own fetch, unlike whatever
    produced the -34.1% reads, came back with zero missing calendar bars across
    all 27 symbols (verified against Binance's public mirror directly). A short
    page that stops well before `end_ms` now gets a few bounded retries before
    the loop accepts it as real; genuinely reaching `end_ms` (or getting a
    truly empty batch) still exits immediately, so a real end-of-history page
    costs nothing extra.
    """
    step = _MS[interval]
    if end_ms is None:
        end_ms = int(time.time() * 1000)
    if start_ms is None:
        start_ms = end_ms - step * 1500
    rows: list[list] = []
    cursor = start_ms
    short_retries = 0
    while cursor < end_ms:
        url = f"{BASE}/klines?symbol={symbol}&interval={interval}&startTime={cursor}&limit=1000"
        batch = _get(url)
        if not batch:
            break
        rows.extend(batch)
        nxt = batch[-1][0] + step
        if nxt <= cursor:
            break
        cursor = nxt
        if len(batch) < 1000:
            if cursor + step <= end_ms and short_retries < 3:
                # Short page, but we're not actually at the requested end --
                # likely a transient partial response. Retry this cursor
                # position instead of accepting it as end-of-history.
                short_retries += 1
                time.sleep(1.5 * short_retries)
                continue
            break
        short_retries = 0
        time.sleep(0.12)  # be a good citizen

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows, columns=[
        "open_time", "open", "high", "low", "close", "volume", "close_time",
        "quote_volume", "trades", "taker_base", "taker_quote", "ignore"])
    df = df[df.open_time < end_ms]
    df["ts"] = pd.to_datetime(df.open_time, unit="ms", utc=True)
    for c in ("open", "high", "low", "close", "volume", "quote_volume"):
        df[c] = df[c].astype(float)
    df = df[["ts", "open", "high", "low", "close", "volume", "quote_volume"]]
    df = df.drop_duplicates("ts").set_index("ts").sort_index()
    return df


def find_gaps(df: pd.DataFrame, interval: str) -> list[pd.Timestamp]:
    """Which expected bar timestamps are missing from `df`'s index, if any.

    Pure and cheap: a fixed-step calendar grid from the first to the last
    timestamp actually present, diffed against what's there. Exists to catch
    exactly the class of bug `fetch_klines`'s short-page handling above
    guards against going forward, and any pre-existing `state/cache/*.pkl`
    left over from before that fix (or any other future silent-truncation
    bug in a data source this doesn't control) -- this only looks at the
    shape of the data actually returned, it never trusts the fetch path.
    Returns `[]` for an empty or single-row frame (nothing to diff).
    """
    if len(df) < 2:
        return []
    step = pd.Timedelta(milliseconds=_MS[interval])
    expected = pd.date_range(df.index[0], df.index[-1], freq=step, tz="UTC")
    return list(expected.difference(df.index))


def load(symbol: str, interval: str = "1d", years: float = 4.0,
         refresh: bool = False) -> pd.DataFrame:
    """Cached loader — the cache only ever grows.

    This used to overwrite the cache with whatever window the caller asked for,
    which meant a live tick wanting 1.5 years silently truncated the 4 years the
    backtest folds depend on. Now: keep the union, fetch only the missing ends.
    """
    os.makedirs(CACHE_DIR, exist_ok=True)
    path = os.path.join(CACHE_DIR, f"{symbol}_{interval}.pkl")
    step = _MS[interval]
    end = int(time.time() * 1000)
    want_start = end - int(years * 365.25 * 86_400_000)

    cached = pd.DataFrame()
    if os.path.exists(path):
        try:
            cached = pd.read_pickle(path)
        except Exception:  # noqa: BLE001 - corrupt cache -> refetch
            cached = pd.DataFrame()

    if cached.empty:
        df = fetch_klines(symbol, interval, want_start, end)
        if not df.empty:
            df.to_pickle(path)
        return df

    have_start = int(cached.index[0].timestamp() * 1000)
    have_end = int(cached.index[-1].timestamp() * 1000)
    pieces = [cached]

    if want_start < have_start - step:                      # need older history
        older = fetch_klines(symbol, interval, want_start, have_start)
        if not older.empty:
            pieces.insert(0, older)
    if refresh and end > have_end + step:                    # need newer bars
        newer = fetch_klines(symbol, interval, have_end + step, end)
        if not newer.empty:
            pieces.append(newer)

    df = (pd.concat(pieces) if len(pieces) > 1 else cached)
    df = df[~df.index.duplicated(keep="last")].sort_index()
    if len(pieces) > 1:
        df.to_pickle(path)
    return df


def load_universe(symbols: Sequence[str], interval: str = "1d",
                  years: float = 4.0, refresh: bool = False) -> dict[str, pd.DataFrame]:
    out: dict[str, pd.DataFrame] = {}
    for s in symbols:
        df = load(s, interval, years, refresh)
        if len(df) > 200:
            gaps = find_gaps(df, interval)
            if gaps:
                print(f"[market] WARNING: {s} ({interval}) is missing {len(gaps)} "
                      f"expected bar(s) between {df.index[0]} and {df.index[-1]} -- "
                      f"first few: {[str(g) for g in gaps[:5]]}. Any backtest using "
                      f"this data may be silently wrong (misaligned dates across "
                      f"symbols, understated drawdown, etc). Delete "
                      f"state/cache/{s}_{interval}.pkl and re-run to force a clean "
                      f"refetch.")
            out[s] = df
    return out


# ---------------------------------------------------------------------------
# Replay
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Bar:
    ts: pd.Timestamp
    open: float
    high: float
    low: float
    close: float
    volume: float


class ReplayWindow:
    """A read-only view of history *up to and including* bar index i.

    Agents receive one of these and physically cannot see the future: the
    underlying arrays are sliced before they're handed over. This is the single
    most important anti-bug measure in the whole project — lookahead bias is
    the reason most backtests are fiction.
    """

    __slots__ = ("_data", "_arr", "_i", "ts")

    def __init__(self, data: dict[str, pd.DataFrame], i: int, ts: pd.Timestamp,
                 arrays: dict[str, dict[str, np.ndarray]] | None = None):
        self._data = data
        # Pre-extracted numpy columns. Slicing pandas 12 symbols x 400 bars per
        # backtest was ~85% of evolution runtime; slicing numpy views is free,
        # and evolution throughput is the budget that decides how much this
        # system can learn per hour.
        self._arr = arrays or {}
        self._i = i
        self.ts = ts

    def _col(self, symbol: str, col: str, n: int) -> np.ndarray:
        a = self._arr.get(symbol, {}).get(col)
        if a is None:
            df = self._data.get(symbol)
            if df is None or col not in df:
                return np.empty(0)
            a = df[col].to_numpy(dtype=float)
        lo = max(0, self._i + 1 - n)
        return a[lo:self._i + 1]

    def history(self, symbol: str, n: int = 300) -> pd.DataFrame:
        df = self._data.get(symbol)
        if df is None:
            return pd.DataFrame()
        lo = max(0, self._i + 1 - n)
        return df.iloc[lo:self._i + 1]

    def closes(self, symbol: str, n: int = 300) -> np.ndarray:
        return self._col(symbol, "close", n)

    def volumes(self, symbol: str, n: int = 300) -> np.ndarray:
        return self._col(symbol, "volume", n)

    def last_close(self, symbol: str) -> float | None:
        df = self._data.get(symbol)
        if df is None or self._i >= len(df):
            return None
        v = df["close"].iat[self._i]
        return None if pd.isna(v) else float(v)

    def symbols(self) -> list[str]:
        return list(self._data.keys())


class Replay:
    """Aligns a multi-symbol universe onto one timeline and walks it forward.

    Execution convention: a decision made on the close of bar i is filled on
    the *open* of bar i+1. No exceptions. That one rule kills an entire class
    of accidentally-profitable backtests.
    """

    def __init__(self, data: dict[str, pd.DataFrame]):
        idx = None
        for df in data.values():
            idx = df.index if idx is None else idx.union(df.index)
        self.index: pd.DatetimeIndex = idx if idx is not None else pd.DatetimeIndex([])
        # reindex every symbol onto the shared timeline; missing bars stay NaN
        self.data = {s: df.reindex(self.index) for s, df in data.items()}
        # extract once, slice many
        self.arrays: dict[str, dict[str, np.ndarray]] = {
            s: {c: df[c].to_numpy(dtype=float) for c in ("open", "high", "low", "close", "volume")
                if c in df}
            for s, df in self.data.items()}

    def __len__(self) -> int:
        return len(self.index)

    def next_open(self, symbol: str, i: int) -> float | None:
        """Fill price for a decision taken at bar i."""
        a = self.arrays.get(symbol, {}).get("open")
        if a is None or i + 1 >= len(a):
            return None
        v = a[i + 1]
        return None if np.isnan(v) else float(v)

    def close_at(self, symbol: str, i: int) -> float | None:
        a = self.arrays.get(symbol, {}).get("close")
        if a is None or i >= len(a):
            return None
        v = a[i]
        return None if np.isnan(v) else float(v)

    def walk(self, start: int = 0, end: int | None = None) -> Iterator[tuple[int, ReplayWindow]]:
        end = len(self.index) - 1 if end is None else min(end, len(self.index) - 1)
        for i in range(start, end):
            yield i, ReplayWindow(self.data, i, self.index[i], self.arrays)


def top_symbols_by_volume(n: int = 20, quote: str = "USDT",
                          exclude_stables: bool = True) -> list[str]:
    """Pick a liquid universe from live 24h stats. Deliberately not curated by
    hand — the genome decides the universe, and it should be able to change it."""
    stables = {"USDC", "TUSD", "BUSD", "FDUSD", "DAI", "USDP", "EUR", "TRY", "BRL",
               "AEUR", "USD1", "XUSD", "USDE"}
    data = _get(f"{BASE}/ticker/24hr")
    rows = []
    for t in data:  # type: ignore[union-attr]
        s = t["symbol"]
        if not s.endswith(quote):
            continue
        base = s[: -len(quote)]
        if exclude_stables and (base in stables or base.startswith("USD")):
            continue
        if any(base.endswith(k) for k in ("UPUSDT", "DOWNUSDT", "UP", "DOWN", "BULL", "BEAR")):
            continue
        try:
            rows.append((s, float(t["quoteVolume"])))
        except (KeyError, ValueError):
            continue
    rows.sort(key=lambda x: -x[1])
    return [s for s, _ in rows[:n]]
