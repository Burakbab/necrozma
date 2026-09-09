"""Run a long-running command (e.g. `evolve N`) fully detached, with its
complete output captured from the first byte and its real exit code
retrievable later from a separate process -- no `nohup ... &`, no pairing a
shell `&` with the calling tool's own backgrounding flag.

AGENTS.md's Next-steps item 9 documents this footgun recurring six times in
a week across three different mechanisms (a `nohup ... &` string; a tool-level
`run_in_background: true` combined with a trailing shell `&`; piping a
backgrounded command's stdout through `tail -60` before it ever reached the
log file, permanently losing generations of output). Each was caught with no
real harm, but each re-spent a session's attention rediscovering the same
fix. Item 9's own 2026-09-08 note said if it kept recurring after a doc
fix, "something more mechanical (a wrapper script, a pre-flight check) is
probably warranted" -- it did keep recurring (2026-09-09) after that doc fix,
so this is that wrapper.

Usage, as two separate tool calls (never combine `start` with a shell `&` or
the calling tool's own `run_in_background`):

    python3 tools/background_runner.py start --log runs/evolve.log \\
        --status /tmp/evolve.status -- python3 evotrader_bundle.py evolve 15

    python3 tools/background_runner.py wait --status /tmp/evolve.status --poll 5

`start` launches the command in its own session (detached from this
process's process group, so it survives this process exiting) and returns
almost immediately with the real child PID -- no `nohup`/`&` needed, so there
is nothing to accidentally pair with the calling tool's own backgrounding.
All of the child's stdout/stderr goes directly into `--log` from the first
byte (never piped through anything that could truncate it before capture).
`wait` blocks in this process (safe to run with the calling tool's own
`run_in_background`, since it does not itself spawn or detach anything) until
the child's real exit code appears in `--status`, which `start`'s child
writes itself on completion -- so exit-code retrieval works even though
`wait` runs in a separate process from `start` and is not the child's parent.
"""
from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
import time


def start_background(cmd: list[str], log_path: str, status_path: str, cwd: str = ".") -> dict:
    """Launch cmd detached, capturing all output to log_path and writing its
    real exit code to status_path on completion. Returns immediately."""
    if not cmd:
        raise ValueError("cmd must be non-empty")
    log_path = os.path.abspath(log_path)
    status_path = os.path.abspath(status_path)
    if os.path.exists(status_path):
        os.remove(status_path)

    wrapper = f"{shlex.join(cmd)}; echo $? > {shlex.quote(status_path)}"
    with open(log_path, "wb") as log_fh:
        proc = subprocess.Popen(
            ["/bin/sh", "-c", wrapper],
            cwd=cwd,
            stdout=log_fh,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
    return {"pid": proc.pid, "log_path": log_path, "status_path": status_path}


def is_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def poll_status(status_path: str) -> int | None:
    """Returns the child's real exit code once available, else None."""
    if not os.path.exists(status_path):
        return None
    text = open(status_path).read().strip()
    if not text:
        return None
    return int(text)


def wait_for_exit(status_path: str, poll_interval: float = 2.0, timeout: float | None = None) -> dict:
    """Blocks until status_path carries a real exit code, or timeout elapses."""
    started = time.monotonic()
    while True:
        code = poll_status(status_path)
        if code is not None:
            return {"exited": True, "exit_code": code, "waited_seconds": time.monotonic() - started}
        if timeout is not None and time.monotonic() - started >= timeout:
            return {"exited": False, "exit_code": None, "waited_seconds": time.monotonic() - started}
        time.sleep(poll_interval)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="action", required=True)

    p_start = sub.add_parser("start", help="launch a command fully detached")
    p_start.add_argument("--log", required=True, help="path to capture all stdout/stderr into")
    p_start.add_argument("--status", required=True, help="path the child writes its real exit code to")
    p_start.add_argument("--cwd", default=".")
    p_start.add_argument("cmd", nargs=argparse.REMAINDER, help="-- python3 evotrader_bundle.py evolve 15")

    p_wait = sub.add_parser("wait", help="block until the command started above has exited")
    p_wait.add_argument("--status", required=True)
    p_wait.add_argument("--poll", type=float, default=5.0)
    p_wait.add_argument("--timeout", type=float, default=None)

    args = parser.parse_args(argv)

    if args.action == "start":
        cmd = args.cmd[1:] if args.cmd[:1] == ["--"] else args.cmd
        result = start_background(cmd, args.log, args.status, cwd=args.cwd)
        print(json.dumps(result))
        return 0

    result = wait_for_exit(args.status, poll_interval=args.poll, timeout=args.timeout)
    print(json.dumps(result))
    if not result["exited"]:
        return 2
    return result["exit_code"]


if __name__ == "__main__":
    sys.exit(main())
