# Portfolio-realized correlation — 2026-08-19 00:52 UTC (3-hourly check)

Routine 3-hourly self-improvement session. Ran unattended.

## Step 2 check (daily bar)

`live_state.json`'s `updated` timestamp was 2026-08-19T00:21:55Z and
`runs/2026-08-19-0020-daily-trading.md` (tick 5, bar 2026-08-18) already
covers today's daily bar, 31 minutes before this session started. Confirmed
`tick` would report `already traded` (not re-run, per protocol — no reason to
touch live state just to re-verify an already-documented result). Nothing to
trade this cycle, as expected for a 3-hourly firing right after the dedicated
daily 00:20 UTC run.

## What this session built

AGENTS.md's "Next steps" item 3 (cross-asset correlation awareness for the
Risk Judge) had one explicit open follow-up from the 2026-08-18 21:46 run:
`correlation-universe` measured *raw universe-wide* pairwise correlation and
found it high and broadly uniform (+0.52 to +0.64 across folds/holdout) —
weak evidence against the "build a fuller cross-universe factor model"
option, but explicitly caveated as not conclusive because it measures the
whole universe's structure, not the *portfolio-realized* correlation of
symbols the champion actually holds together.

This session built that follow-up: `correlation-universe --realized`.

### What changed

- **`loop.engine.holding_mask(closed_trades, open_positions, ts_index, n)`**
  — new pure function. Reconstructs a per-symbol boolean per-bar mask of
  when the account actually held each symbol, purely from
  `run_backtest`'s own returned `closed_trades` (entry_ts/exit_ts) and a new
  `open_positions` field (symbols still open at the end of the replay
  window — did not exist on `run_backtest`'s return dict before this run,
  added as a purely additive third field alongside the existing
  `closed_trades`/`decision_log`). Half-open interval convention `[entry_i,
  exit_i)`, matching `core.portfolio`'s own fill-to-fill semantics (a
  position is open from the bar it fills on, not including the bar the
  closing fill lands on). Unknown timestamps or a `None` symbol are silently
  skipped rather than raising, same fail-toward-nothing-to-report
  convention `pairwise_correlation_stats` already uses.
- **`correlation-universe --realized`** — new CLI flag on the existing
  command. Runs one real full-history backtest (`run_backtest(g0, data)`,
  same cost class as `anatomy`/`consults`/`costs` — a few minutes, heavier
  than the base command's ~80s), builds the held-set mask, and for each
  fold/holdout window finds bars with >= 2 symbols simultaneously held,
  samples up to `--samples` of them, and runs each sampled bar's held subset
  through the *same* `pairwise_correlation_stats` function the base command
  uses — so the two tables are directly comparable (same lookback, same
  threshold, same fold/holdout split).
- **Tests**: `tests/test_holding_mask.py`, 10 new tests — half-open interval
  correctness, open-position-held-to-end, overlap counting across two
  symbols, repeated trades on the same symbol, unknown/missing timestamps
  skipped not raised, `None` symbol skipped, empty input, disjoint positions
  never co-held, and array dtype/length sanity. Full suite: **104 passed, up
  from 94**.

### Result (real 27-symbol universe, champion v3, full history)

```
UNIVERSE (base command, unchanged from 2026-08-18 21:46 run)
  fold 1   mean corr +0.630   [+0.55, +0.79]
  fold 2   mean corr +0.509   [+0.32, +0.69]
  fold 3   mean corr +0.616   [+0.54, +0.70]
  holdout  mean corr +0.572   [+0.41, +0.82]

HELD-ONLY (new --realized flag)
  fold 1   bars>=2held 325   mean corr +0.523   [+0.25, +0.82]
  fold 2   bars>=2held 394   mean corr +0.470   [+0.17, +0.70]
  fold 3   bars>=2held 394   mean corr +0.427   [+0.21, +0.70]
  holdout  bars>=2held 185   mean corr +0.437   [+0.25, +0.59]

  fold 1     held-only +0.523 vs universe-wide +0.630 (lower by 0.108)
  fold 2     held-only +0.470 vs universe-wide +0.509 (lower by 0.039)
  fold 3     held-only +0.427 vs universe-wide +0.616 (lower by 0.189)
  holdout    held-only +0.437 vs universe-wide +0.572 (lower by 0.135)
```

Held-only correlation is lower than universe-wide correlation in **every**
window, by 0.04 to 0.19. The champion holds up to 6 positions out of a
27-symbol universe with `correlation_penalty` at its default no-op `0.0` —
no correlation awareness is active in the live mechanism at all — and its
entry/exit rules (RSI, trend, breakout, z-score thresholds across the three
consults) already land on a less-correlated subset than a random draw from
the universe would produce, in every window measured.

### Reading this against item 3's open decision

The 2026-08-18 21:46 run's universe-wide result already leaned toward "drop
the `correlation_penalty` line" over "build the fuller cross-universe factor
model", but was explicitly caveated: raw universe structure isn't the same
question as what the champion actually holds together. This run answers that
caveat directly, and the answer points the same direction, not the opposite
one — there is no hidden concentration problem in the champion's actual
trading history for a correlation-aware sizing rule to have caught. Combined
with the fixed-value grid's clean loss against three independent champions
(2026-08-16) and the universe-wide read, this is now three independent
negative results for the "build/tune this gene" side of the decision.

Still not fully closed. This measures one champion's one set of entry/exit
rules — a genome that concentrated harder (more positions in one sector, say)
could plausibly show a different held-set correlation picture even in the
same universe. The honest next check, if item 3 is ever revisited with intent
to actually decide, is running `--realized` against a differently-tuned
genome (e.g. `--also-version N` style, or a shadow evolution run), not
re-measuring the same champion again.

### Verified safe

- `loop.engine` is not in the checksummed set (`constitution` + `core.portfolio`
  only) — purely additive, no constitution change.
- `live_state.json` md5 identical before and after:
  `09c35b692da1d694c5a3cace5d488f40`.
- `git status` clean of anything but the intended diff (new test file,
  `evotrader_bundle.py`, `AGENTS.md`).
- `constitution verified dfae6a697f51fb49` printed at the start of the
  `--realized` run, unchanged throughout.
- Confirmed no double-trade risk before starting: today's daily bar was
  already handled by the 00:20 UTC run; this session never called `tick`.
- Full test suite: 104 passed (up from 94), no regressions.
