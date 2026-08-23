# 2026-08-23 18:45 UTC — 3-hourly check: `run_from_files.py` gets a `tick-dry-run` command

## What happened

Today's daily bar (2026-08-22, decided at 00:22 UTC) was already processed
before this session started — `live_state.json`'s `updated` timestamp
(`2026-08-23T00:22:00+00:00`) and the run note at
`runs/2026-08-23-0020-daily-trading.md` confirm it. No real `tick` run this
session.

Used the rest of the slot on AGENTS.md item 7 (unflatten `evotrader_bundle.py`
into real files). Five prior sessions today grew `run_from_files.py`'s
read-only surface (`summary`/`signals` entrypoint, then `holdout-pressure`,
`regime`, `fold-dd-blindspot`) without ever touching the actual point of the
item: `tick`/`evolve` against the real files. AGENTS.md's own notes flagged
that continuing to widen the read-only surface was reaching diminishing
returns and floated a scoped next step: "a `signals`-style dry-run of
`tick`'s decision logic that stops short of `acct.save()`". That's what this
session built.

## `tick-dry-run`

New command in `run_from_files.py`. Calls the real `LiveAccount.tick()` —
the exact method `evotrader_bundle.py tick` calls, doing real market data
load, real `Council` deliberation, both judges, hard-call flagging — but
**never calls `acct.save()`**. There's no dry-run branch inside `tick()`
itself; the safety guarantee is entirely "the one line that writes to disk
is never reached in this file", which is narrower and more load-bearing
than the previous five commands' guarantee ("nothing in the call graph
writes to disk at all").

Verified against the live account:

```
$ python3 run_from_files.py tick-dry-run
[constitution] constitution verified 8b74865634b1db07
[tick-dry-run] DRY RUN -- deciding against the real files, will NOT call acct.save() no matter what happens below
[tick-dry-run] bar 2026-08-22 already traded (tick 9) -- nothing to do (state file was never opened for writing)

$ python3 evotrader_bundle.py tick
[constitution] constitution verified 8b74865634b1db07
[live] bar 2026-08-22 already traded (tick 9) — nothing to do
```

Same bar, same tick number, same skip outcome. `live_state.json` md5
(`af16ffdc22a57c5d63a83003216a8f99`) identical before and after both
invocations. Both hit `tick()`'s own idempotency guard, which returns before
mutating `self.journal`/`self.broker` at all — doubly inert on a bar that's
already traded, exactly like calling the bundle's `tick` a second time
already is.

Stdout is deliberately **not** byte-identical to the bundle's `tick` — every
line is prefixed `[tick-dry-run]` and there's an explicit "will NOT call
acct.save()" banner, so the output can never be mistaken for a real trade
confirmation. The parity that matters is the decision (bar, tick number,
skip-or-trade outcome), not the exact text, so no automated byte-diff test
was appropriate here anyway.

`--force` is deliberately not wired up in this command (the bundle's `tick`
has it). Forcing a repeat decision on an already-traded bar is a question
for a human to ask for explicitly, not something worth making one flag away
on a 3-hourly schedule.

## Why no automated test

Same reasoning as `regime`/`fold-dd-blindspot`: `LiveAccount.tick()` calls
`core.market.load_universe(..., refresh=True)`, which hits the network on a
cold `state/cache` (gitignored). Adding it to the automated suite would make
the suite's runtime and offline-safety depend on Binance being reachable.
Verified manually instead (above). `tests/test_run_from_files_matches_bundle.py`'s
docstring extended to document both the network dependency and the
deliberate stdout divergence from the bundle.

## What's still open

- `tick-dry-run`'s non-skip branch (an actual new decision on an untraded
  bar) has never been exercised against live data — every run today hit the
  skip path, because the daily run always beats a 3-hourly check to a fresh
  bar in practice. Whoever next has a slot that starts before the 00:20 UTC
  daily run has processed a new bar could exercise it as an extra safety
  check ahead of the real `tick`.
- The actual cutover — a *saving* `tick`/`evolve` against the real files,
  and the decision to ever point a scheduled run at `run_from_files.py`
  instead of the bundle — remains separate, bigger, and riskier. Not
  attempted here. `evotrader_bundle.py` is still what every scheduled
  command actually executes.

## Verification checklist

- `py_compile` clean on `run_from_files.py`
- full test suite: 223 passed (unchanged — no new automated test, by design)
- `tools/edit_bundle_module.py verify` round-trip clean
- `tools/edit_bundle_module.py sync --check` reports no drift
- `live_state.json` md5 unchanged throughout: `af16ffdc22a57c5d63a83003216a8f99`
- `evotrader.manifest` md5 unchanged: `0bf3a7d9411ee692d0a9f152a7533803`
- `evotrader_bundle.py` md5 unchanged: `3835305b96044055bc17d43358e2bfba`
- `constitution verified 8b74865634b1db07` on every invocation
- today's bar already processed by the 00:20 UTC daily run before this
  session started; no real `tick` run this session (two idempotent skip-path
  dry runs only)
- `review-hard-calls`: 0 pending
- no genome promotion — no README `## Status` change needed
