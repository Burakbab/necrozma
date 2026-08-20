"""loop.evolve.rolling_folds -- overlapping, fixed-width windows spanning the
searchable region, backing the `rolling-folds` diagnostic. Unlike raising
Evaluator's n_folds (which shrinks every window as the count grows -- see
fold-scheme's n=8 near-MIN_BARS finding, AGENTS.md item 2), this keeps window
width fixed and slides it, so more (correlated) reads of the same span never
shrink a single window below its base_n_folds size."""
import pytest

from loop.evolve import Evaluator, rolling_folds


def test_zero_overlap_matches_evaluator_folds_exactly():
    search_end = 0.85
    n = 3
    ev = Evaluator(data={}, n_folds=n)
    assert rolling_folds(search_end, n, overlap=0.0) == ev.folds()


def test_windows_are_fixed_width():
    windows = rolling_folds(0.85, base_n_folds=4, overlap=0.5)
    widths = [b - a for a, b in windows]
    expected = 0.85 / 4
    assert all(w == pytest.approx(expected) for w in widths)


def test_higher_overlap_produces_more_windows():
    counts = {
        overlap: len(rolling_folds(0.85, base_n_folds=3, overlap=overlap))
        for overlap in (0.0, 0.5, 0.75)
    }
    assert counts[0.0] < counts[0.5] < counts[0.75]


def test_windows_never_extend_past_search_end():
    for overlap in (0.0, 0.3, 0.6, 0.9):
        windows = rolling_folds(0.85, base_n_folds=5, overlap=overlap)
        assert windows, f"overlap={overlap} produced no windows"
        assert all(b <= 0.85 + 1e-9 for _, b in windows)
        assert all(a >= 0.0 for a, _ in windows)


def test_windows_span_the_full_region_start_to_near_end():
    windows = rolling_folds(0.85, base_n_folds=3, overlap=0.5)
    assert windows[0][0] == 0.0
    width = 0.85 / 3
    assert windows[-1][1] == pytest.approx(0.85) or \
        windows[-1][1] >= 0.85 - width


def test_windows_are_chronological_and_ordered():
    windows = rolling_folds(0.85, base_n_folds=4, overlap=0.6)
    starts = [a for a, _ in windows]
    assert starts == sorted(starts)
    assert len(starts) == len(set(starts))


def test_rejects_invalid_overlap():
    with pytest.raises(ValueError):
        rolling_folds(0.85, 3, overlap=1.0)
    with pytest.raises(ValueError):
        rolling_folds(0.85, 3, overlap=-0.1)


def test_rejects_non_positive_base_n_folds():
    with pytest.raises(ValueError):
        rolling_folds(0.85, base_n_folds=0)


def test_single_fold_with_zero_overlap_spans_whole_region():
    windows = rolling_folds(0.85, base_n_folds=1, overlap=0.0)
    assert windows == [(0.0, 0.85)]
