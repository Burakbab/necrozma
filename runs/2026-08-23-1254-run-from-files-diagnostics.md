# 2026-08-23 12:54 UTC — 3-hourly check: run_from_files.py gains two more read-only commands

## Context

`run_from_files.py` (added earlier today, 09:46 UTC) runs `summary`/`signals`
against the real `core`/`agents`/`loop`/`constitution` files instead of
`evotrader_bundle.py`'s embedded copy — item 7's "safe first slice" of the
still-open live-command cutover. That entrypoint deliberately only wired up
the two commands that never call `acct.save()`. This session extends the
same safe pattern to two more commands AGENTS.md's own command table already
documents as read-only diagnostics that "never touch `live_state.json` or the
champion": `holdout-pressure` and `regime`.

Not attempted: `tick`/`evolve`, or the remaining heavier diagnostics
(`anatomy`, `consults`, `costs`, `regime-scan`, `correlation-universe`, ...,
each a full backtest or more) — still out of scope for a single slot, same
reasoning as every prior item-7 session today.

## What changed

`run_from_files.py`: `SUPPORTED_COMMANDS` now `("summary", "signals",
"holdout-pressure", "regime")`. Both new commands' bodies are transcribed
verbatim from `evotrader_bundle.py`'s own `elif cmd == "holdout-pressure"`
and `elif cmd == "regime"` blocks (lines 894-940 and 455-511 respectively) —
not reimplemented, same "transcribe, don't rewrite" discipline the module's
own docstring already commits to for `summary`/`signals`.

- `holdout-pressure`: reads `acct.lineage` only — no market data, no
  backtest, the cheapest diagnostic in the whole command table per its own
  bundle docstring. Fully safe to add to the automated test suite: no
  network dependency, no meaningful runtime cost.
- `regime`: one `core.market.load_universe` call (network fetch on a cold
  `state/cache`, which is gitignored and not committed) plus equal-weight
  buy-and-hold per fold/holdout window — no genome, no Council, no
  backtest. `--interval` passthrough preserved (reads `sys.argv` directly,
  same convention the bundle uses).

`tests/test_run_from_files_matches_bundle.py`: `holdout-pressure` added to
the existing `summary`/`signals` parametrized byte-identical-output test
(fast, no network — suite went 222 → 223 passed). `regime` deliberately has
**no** automated test: unlike the other three commands, it depends on
network market-data availability, which would make the whole suite's
runtime and offline-ability depend on Binance being reachable and undo
the "full suite runs in seconds, no network" property every prior session
has relied on. Verified manually instead (see below) and the reasoning is
documented in the test file's own docstring so nobody wonders why regime
has no test next to it.

## Verification

- `python3 evotrader_bundle.py holdout-pressure` vs
  `python3 run_from_files.py holdout-pressure`: byte-identical stdout,
  `live_state.json` md5 unchanged throughout (`af16ffdc22a57c5d63a83003216a8f99`).
- `python3 evotrader_bundle.py regime` vs `python3 run_from_files.py regime`
  (default `1d` interval, the live champion's own bar size): byte-identical
  stdout, `live_state.json` md5 unchanged. Bundle run took ~67s (cold-ish
  cache), `run_from_files.py` run 0.6s (warm cache from the bundle run just
  before it) — same data, same output, timing difference is cache state,
  not a behavior difference.
- `python3 evotrader_bundle.py regime --interval 4h` vs
  `python3 run_from_files.py regime --interval 4h`: byte-identical stdout,
  `live_state.json` md5 unchanged. Ran in the background for several
  minutes (cold `state/cache` for `4h` data over the network) while the
  rest of this session's work continued; confirms `--interval` passthrough
  works identically on both entrypoints, not just the default `1d` case.
- `py_compile` clean on `run_from_files.py`.
- Full suite: 223 passed (up from 222).
- `tools/edit_bundle_module.py verify` round-trip clean.
- `tools/edit_bundle_module.py sync --check`: no drift.
- `live_state.json` md5 unchanged throughout this entire session
  (`af16ffdc22a57c5d63a83003216a8f99`), `evotrader.manifest` unchanged
  (`0bf3a7d9411ee692d0a9f152a7533803`), `evotrader_bundle.py` unchanged
  (`3835305b96044055bc17d43358e2bfba`), `constitution verified
  8b74865634b1db07` on every invocation.
- Today's 2026-08-23 bar already processed by the 00:20 UTC daily run
  before this session started (`tick` not run this session, no
  double-trade). `review-hard-calls`: 0 pending. No genome promotion, no
  README Status change needed.

No push notification sent — infrastructure/maintainability work with zero
effect on live trading behavior, same reasoning as every prior item-7
session today.

## Next

Item 7's remaining piece is unchanged by this session: no CLI entrypoint
runs `tick`/`evolve` (the state-mutating commands) against the real files,
and no scheduled run has been pointed at `run_from_files.py` instead of the
bundle — both still a separate, bigger, riskier session. If anyone wants to
keep extending `run_from_files.py`'s read-only surface further, the next
cheapest candidates by the bundle's own documented cost class are
`fold-scheme`/`rolling-folds`/`fitness-decomp`/`fold-dd-blindspot`/
`succession-audit` (one backtest per fold, same class as `regime` but a bit
heavier) — all still deliberately out of the automated test suite for the
same network/runtime reason `regime` is.
