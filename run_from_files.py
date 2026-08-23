"""Read-only CLI entrypoint that runs against the real core/agents/loop/
constitution files on disk instead of evotrader_bundle.py's embedded copy.

Item 7 in AGENTS.md ("unflatten evotrader_bundle.py into real files") flags
the full cutover -- every live command (tick/summary/evolve/...) running
against the real files instead of the bundle -- as its own bigger, riskier
session, not something to attempt in one 3-hourly slot. This is a smaller,
safe stepping stone toward it: only the two commands that never write to
live_state.json (`summary`, `signals`) are wired up here, verified
byte-for-byte identical to evotrader_bundle.py's own output for the same
commands against the same state file (see
tests/test_run_from_files_matches_bundle.py).

`tick`/`evolve`/anything that calls acct.save() is deliberately NOT
included here -- wiring those up, and deciding whether to ever point a
scheduled run at this file instead of the bundle, remains the separate,
riskier session AGENTS.md already flagged. This file must never be added to
a scheduled run's command list until that decision is made.

Unlike evotrader_bundle.py's main(), this does not touch
`constitution.EMBEDDED_SOURCES` -- that dict stays empty, so
`constitution.checksum()` takes its file-based branch and hashes the real
`constitution/__init__.py` and `core/portfolio.py` on disk instead.
"""
from __future__ import annotations

import json
import os
import sys

from constitution import verify
from core.live import LiveAccount

SUPPORTED_COMMANDS = ("summary", "signals")


def main() -> None:
    cmd = sys.argv[1] if len(sys.argv) > 1 else "summary"
    if cmd not in SUPPORTED_COMMANDS:
        print(
            f"[run_from_files] unsupported command {cmd!r} -- only "
            f"{SUPPORTED_COMMANDS} are wired up against the real files "
            "(see module docstring); use evotrader_bundle.py for anything else"
        )
        sys.exit(1)

    state_path = os.environ.get("EVO_STATE", "live_state.json")
    ok, msg = verify(os.environ.get("EVO_MANIFEST", "evotrader.manifest"))
    print(f"[constitution] {msg}")
    if not ok:
        sys.exit(1)

    acct = LiveAccount.load(state_path)
    if cmd == "signals":
        print(acct.signals())
    elif cmd == "summary":
        print(json.dumps(acct.summary(), indent=2, default=str))


if __name__ == "__main__":
    main()
