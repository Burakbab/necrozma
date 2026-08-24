"""Verifies run_from_files.py's supported commands produce byte-identical
output to evotrader_bundle.py for the same command against the same
live_state.json.

This is the safe stepping stone AGENTS.md's item 7 asked for: proof that a
read-only command running against the real core/agents/loop/constitution
files on disk (not the bundle's embedded copy) behaves identically, without
touching live_state.json or attempting the full tick/evolve cutover.

Runs both entrypoints as subprocesses, deliberately not importing either in
this test process -- run_from_files.py imports the real `core`/`constitution`
packages directly, while every other test in this suite goes through
evotrader_bundle.py's meta-path finder (installed via tests/conftest.py); the
two must not be mixed in one interpreter.

`regime` and `fold-dd-blindspot` are also wired up in run_from_files.py but
deliberately have no automated test here: unlike `summary`/`signals`/
`holdout-pressure`, both call core.market.load_universe (directly, or via
loop.evolve.Evaluator/loop.engine.run_backtest), which hits the network on
a cold state/cache (gitignored, not committed) and would make this suite's
runtime and offline-ability depend on market data availability. Verified
manually instead -- `regime` both against 1d and `--interval 4h`,
`fold-dd-blindspot` both with no flags and with `--also-version 2` -- output
byte-identical in every case, live_state.json untouched -- see
runs/2026-08-23-*-run-from-files-diagnostics.md.

`tick-dry-run` (added 2026-08-23, first slice of item 7's actual `tick`
cutover -- see AGENTS.md "Current state") was manually-verified-only against
the real live_state.json at first, for the same reason as `regime`/
`fold-dd-blindspot`: `LiveAccount.tick()` calls
`core.market.load_universe(..., refresh=True)`, which can hit the network.
Unlike those two, though, `tick-dry-run` only ever reached its *skip* branch
manually (every session so far has run after the daily bar was already
traded) -- its non-skip branch, which builds and prints a real would-be
order list, had no automated coverage and no manual verification against
live data either, because that requires a session to start in the narrow
window after a new bar closes and before the 00:20 UTC daily run claims it.

`test_tick_dry_run_*` below closes that gap without waiting for that window
and without hitting the network: it builds a fully synthetic 2-symbol
universe (`ZZTESTAUSDT`/`ZZTESTBUSDT`, names chosen to be obviously fake and
never collide with a real Binance pair or a real cached file), pre-populates
`state/cache/{sym}_1d.pkl` with a synthetic OHLCV series that already spans
`LiveAccount.tick()`'s full 1.5-year `load_universe` window and whose last
bar sits on today's date -- so neither the "need older history" nor the
"need newer bars" branch of `core.market.load()` ever fires, and the only
remaining network call (`live_prices()`'s live-ticker fetch) is wrapped in a
broad try/except that falls back to the synthetic closes either way,
network-reachable or not. A scratch genome (the real seed genome, universe
and `regime_anchor` swapped to the fake symbols) plus a scratch
`live_state.json` (`EVO_STATE` env override, never the real file) drive both
branches deterministically: an empty `journal` forces the non-skip branch
(nothing has ever been "traded" for this scratch account), and a `journal`
pre-seeded with the exact bar `tick()` will compute forces the skip branch.
Both tests assert the scratch state file is byte-identical before and after
(the same invariant the byte-identical-output test above checks for the
read-only commands), and that the real repo's `live_state.json` never
moves -- proving the safety guarantee on the branch that actually matters,
not just the skip path every prior session happened to exercise.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent


@pytest.mark.parametrize("cmd", ["summary", "signals", "holdout-pressure"])
def test_run_from_files_matches_bundle_output(cmd):
    before = (REPO_ROOT / "live_state.json").read_bytes()

    bundle = subprocess.run(
        [sys.executable, "evotrader_bundle.py", cmd],
        cwd=REPO_ROOT, capture_output=True, text=True, check=True,
    )
    real = subprocess.run(
        [sys.executable, "run_from_files.py", cmd],
        cwd=REPO_ROOT, capture_output=True, text=True, check=True,
    )

    assert real.stdout == bundle.stdout
    assert real.returncode == bundle.returncode == 0

    after = (REPO_ROOT / "live_state.json").read_bytes()
    assert after == before, "read-only command must never modify live_state.json"


def test_run_from_files_rejects_unsupported_command():
    result = subprocess.run(
        [sys.executable, "run_from_files.py", "tick"],
        cwd=REPO_ROOT, capture_output=True, text=True,
    )
    assert result.returncode == 1
    assert "unsupported command" in result.stdout


# ---------------------------------------------------------------------------
# tick-dry-run, both branches, against a fully synthetic scratch universe
# ---------------------------------------------------------------------------

_FAKE_SYMBOLS = ["ZZTESTAUSDT", "ZZTESTBUSDT"]
_FAKE_CACHE_DIR = REPO_ROOT / "state" / "cache"
_N_BARS = 600  # ~1.64y > tick()'s 1.5y load_universe window, with margin


@pytest.fixture
def synthetic_universe():
    """Writes state/cache/{sym}_1d.pkl for two fake symbols that already
    cover LiveAccount.tick()'s full 1.5y load window with the last bar on
    today's date, so load_universe() never needs a network fetch (neither
    "need older history" nor "need newer bars" fires). Yields
    (genome_dict, last_two_bar_ids); removes the two cache files afterward
    regardless of test outcome -- never touches any real symbol's cache."""
    _FAKE_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    today = pd.Timestamp.now(tz="UTC").floor("D")
    idx = pd.date_range(end=today, periods=_N_BARS, freq="D", tz="UTC")
    rng = np.random.default_rng(1234)
    paths = []
    for sym in _FAKE_SYMBOLS:
        close = 100 * np.exp(np.cumsum(rng.normal(0, 0.02, _N_BARS)))
        open_ = np.concatenate([[close[0]], close[:-1]])
        high = np.maximum(open_, close) * (1 + rng.uniform(0, 0.01, _N_BARS))
        low = np.minimum(open_, close) * (1 - rng.uniform(0, 0.01, _N_BARS))
        vol = rng.uniform(1000, 5000, _N_BARS)
        df = pd.DataFrame({"open": open_, "high": high, "low": low, "close": close,
                            "volume": vol, "quote_volume": vol * close}, index=idx)
        df.index.name = "ts"
        path = _FAKE_CACHE_DIR / f"{sym}_1d.pkl"
        df.to_pickle(path)
        paths.append(path)

    # matches evotrader_bundle.py's own module-scope import, already resolved
    # via the meta-path finder tests/conftest.py installs at collection time
    from core.genome import SEED_GENOME
    genome = json.loads(json.dumps(SEED_GENOME))
    genome["universe"] = list(_FAKE_SYMBOLS)
    genome["agents"]["analyst"]["genes"]["regime_anchor"] = _FAKE_SYMBOLS[0]

    try:
        yield genome, str(idx[-2]), str(idx[-1])
    finally:
        for p in paths:
            p.unlink(missing_ok=True)


def _run_tick_dry_run(scratch_state_path):
    env = dict(os.environ, EVO_STATE=str(scratch_state_path))
    return subprocess.run(
        [sys.executable, "run_from_files.py", "tick-dry-run"],
        cwd=REPO_ROOT, capture_output=True, text=True, env=env,
    )


def test_tick_dry_run_computes_real_decision_for_untraded_bar(synthetic_universe, tmp_path):
    genome, last_closed_bar, _forming_bar = synthetic_universe
    scratch = tmp_path / "scratch_live_state.json"
    scratch.write_text(json.dumps(
        {"genome": genome, "journal": [], "lineage": [], "ticks": 0}))
    before_real = (REPO_ROOT / "live_state.json").read_bytes()
    before_scratch = scratch.read_bytes()

    result = _run_tick_dry_run(scratch)

    assert result.returncode == 0, result.stderr
    assert "a real decision was computed for an UNTRADED bar" in result.stdout
    assert "skipped" not in result.stdout
    assert f'"bar": "{last_closed_bar}"' in result.stdout
    assert '"tick": 1' in result.stdout
    assert scratch.read_bytes() == before_scratch, \
        "tick-dry-run must never call acct.save(), even on the non-skip branch"
    assert (REPO_ROOT / "live_state.json").read_bytes() == before_real


def test_tick_dry_run_skips_already_traded_bar(synthetic_universe, tmp_path):
    genome, last_closed_bar, _forming_bar = synthetic_universe
    scratch = tmp_path / "scratch_live_state.json"
    scratch.write_text(json.dumps({
        "genome": genome,
        "journal": [{"bar": last_closed_bar, "tick": 1}],
        "lineage": [], "ticks": 1,
    }))
    before_real = (REPO_ROOT / "live_state.json").read_bytes()
    before_scratch = scratch.read_bytes()

    result = _run_tick_dry_run(scratch)

    assert result.returncode == 0, result.stderr
    assert "already traded" in result.stdout
    assert "a real decision was computed" not in result.stdout
    assert scratch.read_bytes() == before_scratch
    assert (REPO_ROOT / "live_state.json").read_bytes() == before_real
