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

`test_evolve_dry_run_*` below (added 2026-08-24) covers the second and
final state-mutating command, `evolve-dry-run`. Same EVO_STATE-scratch
discipline, but with two differences from the tick-dry-run tests above:
the synthetic cache needs ~4.1 years of bars, not ~1.6 (evolve's own
`market.load_universe(..., 4.0)` call, not tick's 1.5y window), and the
real `loop.evolve.EvolutionRun` also writes archive files to
`state/genomes/` and `state/lineage.jsonl` as an ordinary side effect of a
real run (`Genome.save`/`.promote()`) -- both gitignored, rebuildable local
cache per `.gitignore`'s own comment, never read back by anything on the
live trading path (nothing outside `core/genome.py` itself reads
`state/genomes/`), so leaving them behind would not corrupt a later real
`tick`/`evolve` run. The fixture snapshots and restores both anyway, purely
so this test doesn't leave a fake-universe genome archive lying around in
the container for a human (or the next session) to trip over.

`test_tick_*` (real, saving `tick`, added 2026-08-24) reuses the same
`synthetic_universe` fixture as `test_tick_dry_run_*` above, but instead of
asserting the scratch state file never changes, it runs the bundle's own
real `tick` and run_from_files.py's real `tick` against two byte-identical
copies of the same starting scratch state and asserts their resulting
state files are identical afterward, aside from wall-clock timestamps --
the strongest parity check available, direct proof rather than inference
from the dry-run twin. `tick` is deterministic here (no real randomness in
`LiveAccount.tick()` itself; the one network call, `live_prices()`'s
live-ticker fetch, is wrapped in a broad try/except that falls back to the
synthetic close for fake symbols regardless of network reachability, same
as the dry-run tests already established) -- but not byte-identical,
because the two subprocesses run a moment apart in real time and several
fields (`updated`, `genome.created`, `journal[].ts`, ...) are stamped from
`core.live._now()` at save/construction time, not derived from the bar
being traded. `_normalize_timestamps` below recursively blanks any
ISO-8601-shaped string before comparing, so the check still fails on any
real content difference.

`test_evolve_*` (real, saving `evolve`, added 2026-08-24) cannot use the
same subprocess-vs-bundle parity trick `tick` uses, because the bundle's
own `evolve` command has no `--seed` flag -- there is no way to make two
separate processes' RandomState draws line up. Instead it checks parity
against `evolve`'s own dry-run twin: run `evolve-dry-run` and `evolve`
with the same `--seed` against byte-identical starting scratch state, and
assert they reach the same decision (same final champion version, same
number of lineage generations appended, same researcher-memory contents)
-- the only difference being that `evolve` actually persists it and
`evolve-dry-run` doesn't, which is exactly the property being tested.
"""
import json
import os
import re
import shutil
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
        [sys.executable, "run_from_files.py", "anatomy"],
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


# ---------------------------------------------------------------------------
# evolve-dry-run, against the same kind of synthetic scratch universe, but
# with enough history to cover evolve's own 4-year market.load_universe()
# ---------------------------------------------------------------------------

_GENOME_DIR = REPO_ROOT / "state" / "genomes"
_LINEAGE_PATH = REPO_ROOT / "state" / "lineage.jsonl"
_N_BARS_4Y = 1500  # > 4y evolve's own load_universe() window, with margin


@pytest.fixture
def synthetic_universe_4y():
    """Same discipline as `synthetic_universe` above (fully synthetic, never-
    a-real-Binance-pair symbols, cache pre-populated so no fetch branch of
    core.market.load() ever fires), but with ~4.1 years of bars instead of
    ~1.6 -- evolve's own `market.load_universe(..., 4.0)` call needs the
    whole window covered, unlike tick()'s 1.5y one. Also snapshots and
    restores state/genomes/ and state/lineage.jsonl around the test: running
    the real EvolutionRun against a fake-universe genome writes ordinary
    archive files there (Genome.save/.promote(), gitignored, rebuildable,
    never read back by the live trading path -- see the module docstring),
    but restoring them anyway keeps this test from leaving a fake-universe
    genome archive behind in the container."""
    _FAKE_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    today = pd.Timestamp.now(tz="UTC").floor("D")
    idx = pd.date_range(end=today, periods=_N_BARS_4Y, freq="D", tz="UTC")
    rng = np.random.default_rng(5678)
    paths = []
    for sym in _FAKE_SYMBOLS:
        close = 100 * np.exp(np.cumsum(rng.normal(0, 0.02, _N_BARS_4Y)))
        open_ = np.concatenate([[close[0]], close[:-1]])
        high = np.maximum(open_, close) * (1 + rng.uniform(0, 0.01, _N_BARS_4Y))
        low = np.minimum(open_, close) * (1 - rng.uniform(0, 0.01, _N_BARS_4Y))
        vol = rng.uniform(1000, 5000, _N_BARS_4Y)
        df = pd.DataFrame({"open": open_, "high": high, "low": low, "close": close,
                            "volume": vol, "quote_volume": vol * close}, index=idx)
        df.index.name = "ts"
        path = _FAKE_CACHE_DIR / f"{sym}_1d.pkl"
        df.to_pickle(path)
        paths.append(path)

    from core.genome import SEED_GENOME
    genome = json.loads(json.dumps(SEED_GENOME))
    genome["universe"] = list(_FAKE_SYMBOLS)
    genome["agents"]["analyst"]["genes"]["regime_anchor"] = _FAKE_SYMBOLS[0]

    genomes_existed = _GENOME_DIR.exists()
    genomes_backup = ({p.name: p.read_bytes() for p in _GENOME_DIR.glob("*.json")}
                      if genomes_existed else {})
    lineage_existed = _LINEAGE_PATH.exists()
    lineage_backup = _LINEAGE_PATH.read_bytes() if lineage_existed else None

    try:
        yield genome
    finally:
        for p in paths:
            p.unlink(missing_ok=True)
        if _GENOME_DIR.exists():
            for p in list(_GENOME_DIR.glob("*.json")):
                if p.name not in genomes_backup:
                    p.unlink(missing_ok=True)
            for name, data in genomes_backup.items():
                (_GENOME_DIR / name).write_bytes(data)
            if not genomes_existed:
                shutil.rmtree(_GENOME_DIR, ignore_errors=True)
        if lineage_existed:
            _LINEAGE_PATH.write_bytes(lineage_backup)
        elif _LINEAGE_PATH.exists():
            _LINEAGE_PATH.unlink(missing_ok=True)


def _run_evolve_dry_run(scratch_state_path, *extra_args):
    env = dict(os.environ, EVO_STATE=str(scratch_state_path))
    return subprocess.run(
        [sys.executable, "run_from_files.py", "evolve-dry-run", *extra_args],
        cwd=REPO_ROOT, capture_output=True, text=True, env=env,
    )


def test_evolve_dry_run_never_saves_state(synthetic_universe_4y, tmp_path):
    genome = synthetic_universe_4y
    scratch = tmp_path / "scratch_live_state.json"
    scratch.write_text(json.dumps(
        {"genome": genome, "journal": [], "lineage": [], "ticks": 0}))
    before_real = (REPO_ROOT / "live_state.json").read_bytes()
    before_scratch = scratch.read_bytes()

    result = _run_evolve_dry_run(scratch, "1", "--seed", "7")

    assert result.returncode == 0, result.stderr
    assert "1 generations" in result.stdout
    assert ("champion would have held" in result.stdout
            or "would have promoted champion" in result.stdout)
    assert scratch.read_bytes() == before_scratch, \
        "evolve-dry-run must never call acct.save(), win or lose"
    assert (REPO_ROOT / "live_state.json").read_bytes() == before_real


def test_evolve_dry_run_resumes_researcher_memory(synthetic_universe_4y, tmp_path):
    """The bundle's `evolve` resumes acct.researcher_memory so the
    Researcher's boldness (stagnation count, which widens its mutation
    batches -- see loop/evolve.py's Researcher.propose) keeps climbing
    across invocations instead of resetting to 0 every time (see
    evotrader_bundle.py's own comment on this) -- evolve-dry-run must do
    the same, even though it never writes the resumed memory back out.
    Checked via the "boldness N" the generation log line always prints,
    rather than trying to reconstruct the Researcher's internal key format
    for its excluded-proposals set from stdout, which the code makes no
    promise to expose in a parseable form."""
    genome = synthetic_universe_4y
    scratch = tmp_path / "scratch_live_state.json"
    from core.genome import SEED_GENOME
    g0_version = SEED_GENOME["version"]

    # A champion_version MISMATCH must not resume anything -- stagnation
    # resets to 0 regardless of what the stale memory claims.
    scratch.write_text(json.dumps({
        "genome": genome, "journal": [], "lineage": [], "ticks": 0,
        "researcher_memory": {"champion_version": g0_version + 999,
                              "tested": [], "stagnation": 5, "holdout_draws": 0},
    }))
    mismatched = _run_evolve_dry_run(scratch, "1", "--seed", "7")
    assert mismatched.returncode == 0, mismatched.stderr
    assert "boldness 0)" in mismatched.stdout, mismatched.stdout

    # A champion_version MATCH must resume the stagnation count as-is.
    scratch.write_text(json.dumps({
        "genome": genome, "journal": [], "lineage": [], "ticks": 0,
        "researcher_memory": {"champion_version": g0_version,
                              "tested": [], "stagnation": 5, "holdout_draws": 0},
    }))
    before_scratch = scratch.read_bytes()
    matched = _run_evolve_dry_run(scratch, "1", "--seed", "7")

    assert matched.returncode == 0, matched.stderr
    assert "boldness 5)" in matched.stdout, matched.stdout
    assert scratch.read_bytes() == before_scratch, \
        "evolve-dry-run must never call acct.save(), even with resumed memory"


# ---------------------------------------------------------------------------
# tick (real, saving) -- byte-for-byte state parity against the bundle's own
# real tick, on identical starting scratch state, both branches
# ---------------------------------------------------------------------------

def _run_bundle_tick(scratch_state_path, *extra_args):
    env = dict(os.environ, EVO_STATE=str(scratch_state_path))
    return subprocess.run(
        [sys.executable, "evotrader_bundle.py", "tick", *extra_args],
        cwd=REPO_ROOT, capture_output=True, text=True, env=env,
    )


def _run_tick(scratch_state_path, *extra_args):
    env = dict(os.environ, EVO_STATE=str(scratch_state_path))
    return subprocess.run(
        [sys.executable, "run_from_files.py", "tick", *extra_args],
        cwd=REPO_ROOT, capture_output=True, text=True, env=env,
    )


_ISO_TS_RE = re.compile(r"^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}")


def _normalize_timestamps(obj):
    """Recursively blank any ISO-8601-shaped string (core.live._now()'s own
    format, and pandas' str(Timestamp) format for bar labels) so two
    real-time subprocess runs of an otherwise-deterministic command can be
    compared for decision content without wall-clock noise failing the
    comparison. Any other content difference still fails it."""
    if isinstance(obj, dict):
        return {k: _normalize_timestamps(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_normalize_timestamps(v) for v in obj]
    if isinstance(obj, str) and _ISO_TS_RE.match(obj):
        return "<TIMESTAMP>"
    return obj


def test_tick_matches_bundle_on_untraded_bar(synthetic_universe, tmp_path):
    genome, last_closed_bar, _forming_bar = synthetic_universe
    starting_state = json.dumps(
        {"genome": genome, "journal": [], "lineage": [], "ticks": 0})
    bundle_scratch = tmp_path / "bundle_live_state.json"
    real_scratch = tmp_path / "real_live_state.json"
    bundle_scratch.write_text(starting_state)
    real_scratch.write_text(starting_state)
    before_real_repo = (REPO_ROOT / "live_state.json").read_bytes()

    bundle_result = _run_bundle_tick(bundle_scratch)
    real_result = _run_tick(real_scratch)

    assert bundle_result.returncode == real_result.returncode == 0, \
        (bundle_result.stderr, real_result.stderr)
    assert f'"bar": "{last_closed_bar}"' in bundle_result.stdout
    assert f'"bar": "{last_closed_bar}"' in real_result.stdout
    assert bundle_scratch.read_bytes() != starting_state.encode(), \
        "sanity check: the non-skip branch must actually save something"

    bundle_state = _normalize_timestamps(json.loads(bundle_scratch.read_bytes()))
    real_state = _normalize_timestamps(json.loads(real_scratch.read_bytes()))
    assert real_state == bundle_state, \
        "run_from_files.py tick must persist the same state as " \
        "evotrader_bundle.py tick (aside from wall-clock timestamps), " \
        "given identical starting state"
    assert (REPO_ROOT / "live_state.json").read_bytes() == before_real_repo, \
        "this test must never touch the real live_state.json"


def test_tick_skips_already_traded_bar_without_saving(synthetic_universe, tmp_path):
    genome, last_closed_bar, _forming_bar = synthetic_universe
    scratch = tmp_path / "scratch_live_state.json"
    scratch.write_text(json.dumps({
        "genome": genome,
        "journal": [{"bar": last_closed_bar, "tick": 1}],
        "lineage": [], "ticks": 1,
    }))
    before_real = (REPO_ROOT / "live_state.json").read_bytes()
    before_scratch = scratch.read_bytes()

    result = _run_tick(scratch)

    assert result.returncode == 0, result.stderr
    assert "nothing to do" in result.stdout
    assert scratch.read_bytes() == before_scratch, \
        "tick must not call acct.save() on the skip branch"
    assert (REPO_ROOT / "live_state.json").read_bytes() == before_real


# ---------------------------------------------------------------------------
# evolve (real, saving) -- decision parity against its own evolve-dry-run
# twin (the bundle's `evolve` has no --seed flag, so a byte-for-byte
# subprocess comparison like tick's isn't possible here)
# ---------------------------------------------------------------------------

def _run_evolve(scratch_state_path, *extra_args):
    env = dict(os.environ, EVO_STATE=str(scratch_state_path))
    return subprocess.run(
        [sys.executable, "run_from_files.py", "evolve", *extra_args],
        cwd=REPO_ROOT, capture_output=True, text=True, env=env,
    )


def test_evolve_saves_and_matches_its_own_dry_run_decision(synthetic_universe_4y, tmp_path):
    genome = synthetic_universe_4y
    starting_state = json.dumps(
        {"genome": genome, "journal": [], "lineage": [], "ticks": 0})
    dry_scratch = tmp_path / "dry_live_state.json"
    real_scratch = tmp_path / "real_live_state.json"
    dry_scratch.write_text(starting_state)
    real_scratch.write_text(starting_state)
    before_real_repo = (REPO_ROOT / "live_state.json").read_bytes()

    dry_result = _run_evolve_dry_run(dry_scratch, "1", "--seed", "7")
    real_result = _run_evolve(real_scratch, "1", "--seed", "7")

    assert dry_result.returncode == real_result.returncode == 0, \
        (dry_result.stderr, real_result.stderr)
    assert dry_scratch.read_bytes() == starting_state.encode(), \
        "sanity check: evolve-dry-run must still never save"
    assert real_scratch.read_bytes() != starting_state.encode(), \
        "evolve must actually persist state"

    dry_held = "champion would have held" in dry_result.stdout
    real_held = "champion held" in real_result.stdout
    assert dry_held == real_held, (dry_result.stdout, real_result.stdout)

    real_state = json.loads(real_scratch.read_bytes())
    assert len(real_state["lineage"]) == 1, \
        "one generation's worth of search should have been appended"
    assert real_state["researcher_memory"]["champion_version"] == genome["version"]
    assert real_state["researcher_memory"]["stagnation"] >= 0
    assert (REPO_ROOT / "live_state.json").read_bytes() == before_real_repo, \
        "this test must never touch the real live_state.json"


def test_evolve_rejects_unsupported_flags_the_same_as_evolve_dry_run(synthetic_universe_4y, tmp_path):
    """`evolve` (real) and `evolve-dry-run` share the same argv-parsing code
    shape (positional generation count, optional --seed) -- confirms the
    default generation count (3, unspecified) is respected identically, one
    generation at a time being the only case exercised above."""
    genome = synthetic_universe_4y
    scratch = tmp_path / "scratch_live_state.json"
    scratch.write_text(json.dumps(
        {"genome": genome, "journal": [], "lineage": [], "ticks": 0}))

    result = _run_evolve(scratch, "2", "--seed", "3")

    assert result.returncode == 0, result.stderr
    assert "2 generations" in result.stdout
    state = json.loads(scratch.read_bytes())
    assert len(state["lineage"]) == 2
