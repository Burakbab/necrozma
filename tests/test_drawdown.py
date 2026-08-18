"""loop.engine.drawdown_episodes -- breaks a nav_history series into
peak-to-trough-to-recovery episodes. Exists to answer a concrete open item
from AGENTS.md's costs/holdout diagnostic: `stats()['max_dd']` is one
number, it doesn't say *when* the drawdown happened or whether it was one
bad stretch or several. Read-only: never touches live_state.json, doesn't
run a backtest itself, just walks a nav series."""
import numpy as np

from loop.engine import drawdown_episodes


def test_too_short_series_returns_empty():
    assert drawdown_episodes([("d0", 100.0), ("d1", 101.0)]) == []


def test_monotonic_rise_has_no_drawdown_episodes():
    nav = [(f"d{i}", 100.0 + i) for i in range(10)]
    assert drawdown_episodes(nav) == []


def test_single_episode_peak_trough_recovery():
    nav = [("d0", 100), ("d1", 120), ("d2", 90), ("d3", 130)]
    episodes = drawdown_episodes(nav)
    assert len(episodes) == 1
    e = episodes[0]
    assert e["peak_ts"] == "d1" and e["peak_nav"] == 120.0
    assert e["trough_ts"] == "d2" and e["trough_nav"] == 90.0
    assert e["recovery_ts"] == "d3"
    assert abs(e["dd_pct"] - (90.0 / 120.0 - 1)) < 1e-9
    assert e["peak_to_trough_bars"] == 1


def test_unrecovered_episode_at_series_end_has_no_recovery():
    nav = [("d0", 100), ("d1", 150), ("d2", 80)]
    episodes = drawdown_episodes(nav)
    assert len(episodes) == 1
    assert episodes[0]["recovery_ts"] is None
    assert episodes[0]["trough_ts"] == "d2"


def test_episodes_sorted_deepest_first_and_top_n_limits():
    nav = [("d0", 100), ("d1", 110), ("d2", 95),   # -13.6%
          ("d3", 120), ("d4", 60),                 # -50.0%
          ("d5", 130), ("d6", 100)]                 # -23.1%, unrecovered
    episodes = drawdown_episodes(nav, top_n=2)
    assert len(episodes) == 2
    assert episodes[0]["dd_pct"] < episodes[1]["dd_pct"]
    assert episodes[0]["peak_ts"] == "d3" and episodes[0]["trough_ts"] == "d4"


def test_deepest_episode_reproduces_stats_style_max_dd():
    # Same running-peak definition PaperBroker.stats() uses for max_dd:
    # min(nav / running_peak - 1). drawdown_episodes()'s deepest episode
    # must match it exactly, not approximately -- a scheduled session reads
    # this diagnostic next to `stats()`'s own max_dd and treats a mismatch
    # as a bug, per the CLI's own "match"/"MISMATCH" sanity print.
    rng = np.random.default_rng(7)
    values = 100 * np.cumprod(1 + rng.normal(0, 0.02, size=200))
    nav = [(f"d{i}", float(v)) for i, v in enumerate(values)]

    peaks = np.maximum.accumulate(values)
    expected_max_dd = float(np.min(values / peaks - 1))

    episodes = drawdown_episodes(nav, top_n=1)
    assert episodes, "random-walk series should have at least one drawdown"
    assert abs(episodes[0]["dd_pct"] - expected_max_dd) < 1e-9


def test_multiple_episodes_do_not_overlap_and_recover_before_next_peak():
    nav = [("d0", 100), ("d1", 90), ("d2", 100), ("d3", 80), ("d4", 100)]
    episodes = drawdown_episodes(nav, top_n=10)
    assert len(episodes) == 2
    peaks = {e["peak_ts"] for e in episodes}
    troughs = {e["trough_ts"] for e in episodes}
    assert peaks == {"d0", "d2"}
    assert troughs == {"d1", "d3"}
