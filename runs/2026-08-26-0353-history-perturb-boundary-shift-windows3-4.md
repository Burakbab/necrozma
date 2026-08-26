# `history-perturb --boundary-shift` on windows 3 and 4: the noise is general, not a window-5 special case

**3-hourly self-improvement check, ~03:53 UTC.**

## Why

Picked up the sharpest open follow-up from the 2026-08-26 00:59 UTC entry:
"(a) run `--boundary-shift` on windows 3/4 too, to see if they're similarly
noisy or if window 5 is unusual in how close its verdict sits to the flip
point." Today's bar (2026-08-26) was already traded by the dedicated 00:20
UTC daily run before this session started — nothing new to do on the
trading side; full suite (235 passed) run first to confirm baseline.

## What happened

No code changes — same `--boundary-shift N [--sub-slice-window I]` flag
shipped 2026-08-26 00:59 UTC, just pointed at windows 3 and 4 instead of 5.
Read-only, one real `run_backtest` per shift, `live_state.json` and the
champion untouched.

## Result (champion v3, live, N=15 each)

| window | dates (shift 0) | beats benchmark | excess ret range | hard-fails (maxDD>40%) |
|---|---|---|---|---|
| 3 | 2020-08-25 to 2022-08-26 | 10/15 | [-162.7%, +366.2%] | 2/15 (-47.7%) |
| 4 | 2022-08-26 to 2024-08-25 | 10/15 | [-48.9%, +142.5%] | 0/15 (stays ≤34.1%) |
| 5 (00:59 UTC entry, for comparison) | 2024-08-25 to 2026-08-26 | 6/15 | [-44.4%, +57.3%] | 14/15 (-35% to -57%) |

Full tables in the CLI output, not re-pasted here. Window 3's swing is the
widest of the three by excess-return range (a ~530-point spread — two
shifts landed near-identical maxDD to shift 0 but with wildly different
trade sequences, e.g. shift 2's +357.2% vs shift 3's -148.2% one day later),
and it also hard-fails on 2 of 15 shifts even though shift 0 itself clears
comfortably (+45.3% excess, `beat_benchmark: True`). Window 4 never
hard-fails at any shift (maxDD tops out at -34.1%) but still flips
`beat_benchmark` on more than half its shifts.

## Reading

This answers the 00:59 UTC entry's open question directly: **window 5 is
not unusual in being boundary-noisy — all three windows checked so far show
the same order-of-magnitude sensitivity in `beat_benchmark`/excess-return
to a 0-14 day shift in where a 2-year window starts.** What *is* different
about window 5 is the hard-fail rate: 14/15 shifts breach the >40% max-dd
gate in window 5, vs. 2/15 in window 3 and 0/15 in window 4. That lines up
with the 00:59 UTC entry's framing — the max-dd/hard-fail signal is the
more genuine, regime-driven half of "window 5 is bad," while the
beat-benchmark verdict is largely boundary-placement noise, and that same
split now looks like a general property of this backtest, not specific to
window 5's current regime. Practical upshot for the open v3
demotion/rollback question (raised to the owner 2026-08-22): any single
`--independent` run's per-window `beat_benchmark` column should be read as
one noisy draw from a wide distribution, for any window, not just the one
currently in a drawdown — the drawdown *depth* is the more trustworthy
signal when arguing about a specific window's regime.

**Mechanism still not chased.** The 00:59 UTC entry's hypothesis (an early
regime-detection/entry decision in the first few bars cascades into a
materially different trade sequence over 500+ trades) is now supported by
three independent windows showing the same shape, but still not verified by
tracing actual trade divergence between two adjacent shifts. That remains
the sharpest concrete next step if this thread continues.

## Verified safe

- Full suite: 235 passed (`pytest tests/`, 129.54s), matches known baseline.
  No code changes this session — existing diagnostic run twice, no new test
  file needed.
- `git status --short` clean before and after (no diff to commit — see
  below).
- `live_state.json` untouched, still reflects tick 12 from the 00:20 UTC
  daily run (`updated: 2026-08-26T00:22:17+00:00`, md5 unchanged from the
  00:59 UTC entry's own check).
- `evotrader.manifest` md5 unchanged (constitution verified
  `8b74865634b1db07` on every invocation, printed above).
- Today's bar already processed by the 00:20 UTC daily run before this
  session started (`tick` not run this session, no double-trade).
- No genome promotion — no README `## Status` update needed.

## Next, if this thread stays worth pursuing

- Trace what actually differs between two adjacent boundary-shift runs'
  first few trades (e.g. window 3's shift 2 vs shift 3, +357.2% vs -148.2%
  one day apart) to find the path-dependence mechanism directly instead of
  treating it as a black box — the sharpest remaining item across all three
  boundary-shift sessions so far.
- The per-trade `anatomy` post-mortem restricted to window 5 (open since
  2026-08-25 21:55 UTC) is still on the table, now with the caveat
  reinforced twice over: window 5's specific trade list is one noisy draw
  among many, useful for tracing mechanism, not for characterizing "the"
  window-5 regime.
- Otherwise, fold this into the already-open v3 demotion/rollback question
  (raised to the owner 2026-08-22) as a further data point narrowing what
  "window 5 fails" actually means (real drawdown depth, noisy benchmark
  verdict, and now: not even unique to window 5).
