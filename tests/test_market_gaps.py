"""core.market.find_gaps -- catches silent truncation in fetched OHLCV data.

2026-08-22 3-hourly check: a champion's full-history backtest reported -46.5%
maxDD (crossing its own MAX_DD_HARD_FAIL gate) in a session whose fetch was
verified gap-free, when several independent sessions the same week had
reported -34.1% on what should be the same immutable historical window.
`fetch_klines`'s old short-page handling treated any batch under 1000 rows as
proof the range was exhausted, which is also what a transient partial
response looks like -- silently truncating the frame with no error. This is
the pure diff powering the now-loud `load_universe` warning, and the retry
this prompted in `fetch_klines` itself."""
import pandas as pd

from core.market import find_gaps


def _index(*day_offsets: int) -> pd.DatetimeIndex:
    base = pd.Timestamp("2024-01-01", tz="UTC")
    return pd.DatetimeIndex([base + pd.Timedelta(days=d) for d in day_offsets])


def test_no_gaps_in_contiguous_daily_index():
    df = pd.DataFrame({"close": [1.0, 2.0, 3.0, 4.0]}, index=_index(0, 1, 2, 3))
    assert find_gaps(df, "1d") == []


def test_single_missing_day_detected():
    df = pd.DataFrame({"close": [1.0, 2.0, 3.0]}, index=_index(0, 1, 3))
    gaps = find_gaps(df, "1d")
    assert gaps == [pd.Timestamp("2024-01-01", tz="UTC") + pd.Timedelta(days=2)]


def test_multi_day_block_missing_detected():
    df = pd.DataFrame({"close": [1.0, 2.0]}, index=_index(0, 10))
    gaps = find_gaps(df, "1d")
    assert len(gaps) == 9
    assert gaps[0] == pd.Timestamp("2024-01-01", tz="UTC") + pd.Timedelta(days=1)
    assert gaps[-1] == pd.Timestamp("2024-01-01", tz="UTC") + pd.Timedelta(days=9)


def test_empty_and_single_row_frames_are_trivially_gap_free():
    assert find_gaps(pd.DataFrame({"close": []}), "1d") == []
    assert find_gaps(pd.DataFrame({"close": [1.0]}, index=_index(0)), "1d") == []


def test_hourly_interval_uses_hourly_step():
    base = pd.Timestamp("2024-01-01", tz="UTC")
    idx = pd.DatetimeIndex([base, base + pd.Timedelta(hours=1), base + pd.Timedelta(hours=3)])
    df = pd.DataFrame({"close": [1.0, 2.0, 3.0]}, index=idx)
    gaps = find_gaps(df, "1h")
    assert gaps == [base + pd.Timedelta(hours=2)]
