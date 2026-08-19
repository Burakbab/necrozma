"""loop.engine.holding_mask -- reconstructs which symbols the account
actually held, per bar, purely from run_backtest's own closed_trades and
open_positions records. Exists to answer the follow-up AGENTS.md item 3 left
open: whether portfolio-realized correlation (what the champion actually held
*together*) tells a different story than raw universe-wide correlation.
Read-only, pure function: no genome, broker, or replay object involved."""
import numpy as np

from loop.engine import holding_mask


def test_closed_trade_marks_half_open_interval():
    closed = [{"symbol": "A", "entry_ts": "t0", "exit_ts": "t3"}]
    ts_index = {"t0": 0, "t1": 1, "t2": 2, "t3": 3, "t4": 4}
    mask = holding_mask(closed, [], ts_index, 5)
    # held for bars 0,1,2 -- NOT bar 3, the bar the closing fill lands on
    assert mask["A"].tolist() == [True, True, True, False, False]


def test_open_position_held_through_end_of_window():
    openp = [{"symbol": "B", "opened_ts": "t2"}]
    ts_index = {"t0": 0, "t1": 1, "t2": 2, "t3": 3, "t4": 4}
    mask = holding_mask([], openp, ts_index, 5)
    assert mask["B"].tolist() == [False, False, True, True, True]


def test_overlapping_positions_both_marked_true_in_overlap():
    closed = [{"symbol": "A", "entry_ts": "t0", "exit_ts": "t4"}]
    openp = [{"symbol": "B", "opened_ts": "t2"}]
    ts_index = {"t0": 0, "t1": 1, "t2": 2, "t3": 3, "t4": 4}
    mask = holding_mask(closed, openp, ts_index, 5)
    held_count = mask["A"].astype(int) + mask["B"].astype(int)
    # both held together on bars 2,3 only
    assert held_count.tolist() == [1, 1, 2, 2, 1]


def test_repeat_trades_same_symbol_union_correctly():
    closed = [
        {"symbol": "A", "entry_ts": "t0", "exit_ts": "t1"},
        {"symbol": "A", "entry_ts": "t3", "exit_ts": "t4"},
    ]
    ts_index = {"t0": 0, "t1": 1, "t2": 2, "t3": 3, "t4": 4}
    mask = holding_mask(closed, [], ts_index, 5)
    assert mask["A"].tolist() == [True, False, False, True, False]


def test_unknown_timestamp_skipped_not_raised():
    closed = [{"symbol": "A", "entry_ts": "missing", "exit_ts": "t2"}]
    ts_index = {"t0": 0, "t1": 1, "t2": 2}
    mask = holding_mask(closed, [], ts_index, 3)
    assert "A" not in mask


def test_missing_exit_ts_skipped_not_raised():
    closed = [{"symbol": "A", "entry_ts": "t0", "exit_ts": "missing"}]
    ts_index = {"t0": 0, "t1": 1, "t2": 2}
    mask = holding_mask(closed, [], ts_index, 3)
    assert "A" not in mask


def test_symbol_none_skipped_not_raised():
    closed = [{"symbol": None, "entry_ts": "t0", "exit_ts": "t2"}]
    ts_index = {"t0": 0, "t1": 1, "t2": 2}
    mask = holding_mask(closed, [], ts_index, 3)
    assert mask == {}


def test_no_symbols_ever_held_returns_empty_dict():
    mask = holding_mask([], [], {"t0": 0}, 3)
    assert mask == {}


def test_disjoint_positions_never_co_held():
    closed = [
        {"symbol": "A", "entry_ts": "t0", "exit_ts": "t2"},
        {"symbol": "B", "entry_ts": "t2", "exit_ts": "t4"},
    ]
    ts_index = {"t0": 0, "t1": 1, "t2": 2, "t3": 3, "t4": 4}
    mask = holding_mask(closed, [], ts_index, 5)
    held_count = mask["A"].astype(int) + mask["B"].astype(int)
    assert np.max(held_count) == 1


def test_returned_arrays_are_length_n_bool():
    closed = [{"symbol": "A", "entry_ts": "t0", "exit_ts": "t2"}]
    ts_index = {"t0": 0, "t1": 1, "t2": 2}
    mask = holding_mask(closed, [], ts_index, 3)
    assert mask["A"].dtype == np.bool_
    assert len(mask["A"]) == 3
