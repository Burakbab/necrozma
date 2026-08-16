"""Shared synthetic-data builders for hermetic tests. No network, no disk."""
import numpy as np
import pandas as pd


def synthetic_ohlcv(n: int, seed: int, start_price: float = 100.0,
                     freq: str = "1D") -> pd.DataFrame:
    """A deterministic, self-consistent OHLCV frame: geometric random walk
    closes, open = previous close, high/low bracket open and close, volume
    a positive random series. Enough movement to actually trigger signals
    (flat data would make a lookahead test pass trivially, by never trading)."""
    rng = np.random.default_rng(seed)
    rets = rng.normal(loc=0.0005, scale=0.03, size=n)
    closes = start_price * np.exp(np.cumsum(rets))
    opens = np.empty(n)
    opens[0] = start_price
    opens[1:] = closes[:-1]
    highs = np.maximum(opens, closes) * (1 + rng.uniform(0.0, 0.01, size=n))
    lows = np.minimum(opens, closes) * (1 - rng.uniform(0.0, 0.01, size=n))
    volumes = rng.uniform(1_000, 10_000, size=n)
    idx = pd.date_range("2020-01-01", periods=n, freq=freq, tz="UTC")
    return pd.DataFrame({"open": opens, "high": highs, "low": lows,
                         "close": closes, "volume": volumes}, index=idx)
