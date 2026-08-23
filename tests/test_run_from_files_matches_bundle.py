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
cutover -- see AGENTS.md "Current state") has the same network dependency
(`LiveAccount.tick()` calls `core.market.load_universe(..., refresh=True)`)
and so gets the same treatment: no automated test here, verified manually
instead against the real live_state.json -- output's bar/tick number match
`evotrader_bundle.py tick`'s own skip-path message exactly, and
live_state.json's md5 is identical before and after both commands. Unlike
`regime`/`fold-dd-blindspot`, `tick-dry-run`'s stdout is deliberately NOT
byte-identical to the bundle's `tick` (it prefixes every line with
`[tick-dry-run]` and adds an explicit "will NOT call acct.save()" banner,
specifically so its output can never be mistaken for a real trade
confirmation) -- the parity that matters here is the decision itself (same
bar, same tick number, same skip-or-trade outcome), not the exact text.
"""
import os
import subprocess
import sys
from pathlib import Path

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
