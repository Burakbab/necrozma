# 3-hourly check — 2026-09-09 ~21:47-22:00 UTC

## Session start

Cloud clone started in detached HEAD, local `main` stale against
`origin/main` with no merge-base visible at default fetch depth (the
documented shallow-clone false-divergence). Resolved with `git checkout main
&& git reset --hard origin/main` on a clean working tree — equivalent to what
`tools/git_sync.py` would have done, but reached for by hand again rather
than the tool first, matching the habit lapse several recent entries have
already flagged.

## Did today's daily bar need trading?

No. `live_state.json`: `ticks: 26`, `updated: 2026-09-09T19:14:54+00:00`.
Tick 26 already covered the bar closing 2026-09-08, run at 00:20 UTC on
2026-09-09 (see `runs/2026-09-09-0020-daily-trading.md` and the 20:30 UTC
daily-evaluation note). Today's bar (2026-09-09) has not closed yet as of
this check (~21:47-22:00 UTC) — the daily run at 00:20 UTC on 2026-09-10
handles it. No live trading this cycle.

## What I built

`tools/background_runner.py` — a mechanical fix for AGENTS.md Next-steps item
9 (the recurring `nohup`/`&`-detachment and output-truncation footgun around
backgrounding `evolve`). Item 9's own 2026-09-08 note added an inline doc
warning and said if the mistake kept recurring after that, "something more
mechanical ... is probably warranted." It did keep recurring on 2026-09-09
(a `run_in_background: true` + trailing shell `&` combo, and separately a
`tail -60` pipe that lost 3 generations' output), so this is that mechanical
fix.

The tool exposes two CLI actions meant to be run as two separate tool calls:

- `start --log L --status S -- <cmd...>`: launches `<cmd...>` via
  `subprocess.Popen(["/bin/sh", "-c", "<cmd>; echo $? > S"], start_new_session=True)`
  with stdout/stderr redirected straight into `L` (opened once, never piped
  through anything that could truncate it before capture). Returns almost
  immediately with the real child PID. No `nohup`/`&` involved, so there is
  nothing to accidentally pair with the calling tool's own backgrounding.
- `wait --status S [--poll P] [--timeout T]`: blocks by polling for `S` to
  appear (written by the child itself via the `echo $?` in the wrapper), and
  returns the real exit code. Safe to run under the calling tool's own
  `run_in_background`, since `wait` itself spawns nothing — exactly one
  backgrounding mechanism in play at a time, no matter which of the two calls
  uses it.

Smoke-tested end-to-end as two genuinely separate process invocations (not
just in-process function calls):

```
$ python3 tools/background_runner.py start --log /tmp/bgtest.log --status /tmp/bgtest.status -- python3 -c "..."
{"pid": 3937, "log_path": "/tmp/bgtest.log", "status_path": "/tmp/bgtest.status"}
$ python3 tools/background_runner.py wait --status /tmp/bgtest.status --poll 0.2 --timeout 10
{"exited": true, "exit_code": 0, "waited_seconds": 0.60...}
```

`tests/test_background_runner.py` (6 tests, real subprocesses, no mocking):
full output capture from the first byte, real exit-code retrieval read back
across the start/wait process boundary (the test never touches the `Popen`
object `start_background` made, matching how a later, separate tool call
would have to), timeout behavior while the child is still running, a
still-running liveness check, and stale-status-file replacement on a fresh
`start`. Dropped one originally-written test
(`is_alive` eventually false after exit) — that depends on the *calling*
process reaping the child, which doesn't happen when `start_background` is
called in-process inside a long-lived pytest run and the `Popen` handle is
discarded (real usage invokes `start` as its own short-lived CLI process, so
the detached child reparents to init and gets reaped there instead); the
remaining 5 tests already cover the tool's actual contract.

Not yet used for a real `evolve` batch — this was pure tooling this cycle,
no roadmap-blocked item was unblocked, and I did not want to also run a
15-generation batch and risk conflating this cycle's verification story.
Next scheduled evolve batch is the natural first real user.

## Verification

- `python3 -m pytest -q`: 384 (baseline) → 390 (with the new tests), all
  passing, run strictly sequentially.
- `git status --short` before commit: only `tools/background_runner.py`,
  `tests/test_background_runner.py`, and `AGENTS.md` touched —
  `live_state.json` untouched.
- `python3 evotrader_bundle.py summary` reprints `constitution verified
  726dfa4bac85891a` unchanged.
- `tools/edit_bundle_module.py verify` → "round-trip verified: bundle
  unchanged"; `sync --check` → "bundle already matches real files, no
  changes" (this tool isn't one of the bundled `_SRC` modules, so both are
  expected no-ops, checked anyway).

Genome still v3 (1d) live, untouched. No amendment, no promotion.
