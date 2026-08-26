# `history-perturb --boundary-shift`: window 5's "hard-fail" verdict is largely boundary-placement noise

**3-hourly self-improvement check, ~00:59 UTC.**

## Why

Today's bar (2026-08-25) was already traded by the dedicated 00:20 UTC daily
run before this session started — nothing to do on the trading side. Picked
up the open thread from the 2026-08-25 21:55 UTC entry ("what's different
about 2024-2026" — ruled out coarse regime shape). The plan was a per-trade
`anatomy`-style post-mortem restricted to window 5. Building that turned up
something sharper than the post-mortem itself.

## What happened

A throwaway script re-ran `history-perturb --independent` (unchanged code,
just one day later than the 2026-08-25 09:56 UTC run) to get window 5's data
for the anatomy cut. Window 5's verdict had flipped: **excess return -41.2%
(hard-fail) on 2026-08-25 → +3.7% (beats benchmark) on 2026-08-26**, from a
single day's shift in where "now" lands (every window boundary walks back
one day when tiling from "now"). Window 4 flipped the other way (+0.8% →
-11.4%). That is too large a swing for one calendar day of real returns —
it points at backtest path-dependence: a different first bar in the window
cascades into a different two-year trade sequence, not a one-day price move.

## What shipped

New `--boundary-shift N [--sub-slice-window I]` flag on `history-perturb
--independent` (see `evotrader_bundle.py`, same file/precedent as
`--sub-slice`/`--drawdown` — requires `--independent`, reuses its
already-loaded `raw`/`windows`, one real `run_backtest` per shift, read-only,
no new pure function). Walks window `I`'s end date back `0..N-1` days (same
width) and reports fitness/return/maxDD/trades/excess-return/beat-benchmark
at each shift, plus a summary line.

## Result (champion v3, live, window 5, N=15)

| shift | end | maxDD | excess ret | beat bench |
|---:|---|---:|---:|---|
| 0 | 2026-08-26 | -44.0% | +3.7% | True |
| 1 | 2026-08-25 | -45.0% | -44.4% | False |
| 2 | 2026-08-24 | -44.7% | -27.4% | False |
| 3 | 2026-08-23 | -46.8% | -33.7% | False |
| 4 | 2026-08-22 | -46.8% | -26.7% | False |
| 5 | 2026-08-21 | -46.9% | -8.8% | False |
| 6 | 2026-08-20 | -46.9% | -11.2% | False |
| 7 | 2026-08-19 | -45.1% | +5.5% | True |
| 8 | 2026-08-18 | -35.3% | +49.0% | True |
| 9 | 2026-08-17 | -44.0% | +55.5% | True |
| 10 | 2026-08-16 | -41.5% | +57.3% | True |
| 11 | 2026-08-15 | -46.8% | -12.5% | False |
| 12 | 2026-08-14 | -44.8% | +7.4% | True |
| 13 | 2026-08-13 | -46.9% | -15.7% | False |
| 14 | 2026-08-12 | -57.4% | -43.6% | False |

Full table reproduced in the CLI output; not re-pasted in full here. **Two
different signals, two different robustness levels:**

1. **The >40% max-dd hard-fail gate is comparatively robust**: 14/15 shifts
   breach it (all in the -35% to -57% range except shift 8's -35.3%, which
   is also the one shift with finite fitness). Whatever regime the champion
   is trading through right now really does put it into a deep drawdown
   fairly independent of the exact boundary day — this part of "window 5 is
   bad" holds up.
2. **The beat-benchmark / excess-return verdict does not.** 6/15 shifts beat
   benchmark, 9/15 don't, and the excess return ranges from -44.4% to
   +57.3% — a ~100-point spread from walking the same window back two
   weeks. Characterizing window 5 as "the champion fails to beat benchmark
   in its current regime," as the 2026-08-24/25 session sequence did
   (`-independent`, `--sub-slice`, `--drawdown`, the regime-characterization
   entry), picked one particular noisy draw and treated it as a stable
   property. It isn't one.

## Reading

This reframes, but doesn't erase, the last two days of window-5
investigation. The trend/chop/volatility/correlation regime-shape work
(2026-08-25 21:55 UTC) and the drawdown-episode location (2026-08-25 15:53
UTC, peak 2025-11-08 to trough 2026-08-11) are about the drawdown itself,
which this run's finding says is the more robust half — that work still
stands. What's now in question is any claim built on "window 5 fails to
beat benchmark" as if that were a settled, single number — it was one
sample from a distribution with a huge spread. The already-open v3
demotion/rollback question (raised to the owner 2026-08-22) should weigh
this: the drawdown depth is real and robust, but the "loses to a lazy
buy-and-hold basket in its own recent history" framing specifically is not
as solid as it read.

**Mechanism not chased further here**: *why* is a 2-year backtest this
sensitive to a 1-14 day shift in start date? Plausible candidate: an early
regime-detection or entry decision in the first few bars of the window
sets up a materially different initial position, which compounds
differently over 625+ trades. Not verified — would need per-trade
divergence tracing between two adjacent-shift runs, not attempted this
session.

## Verified safe

- Full suite: 235 passed (`pytest tests/`, 150.53s), matches known baseline.
  No new pure function (composes already-tested `run_backtest`), same
  precedent as `--sub-slice`/`--drawdown` — no new test file.
- `tools/edit_bundle_module.py sync --check`: no drift (this CLI-dispatch
  code isn't part of the unflattened `_SRC` modules).
- `git status --short` clean before this commit except `evotrader_bundle.py`.
- `live_state.json` untouched by this session (not in the diff) — still
  reflects tick 12 from the 00:20 UTC daily run.
- `evotrader.manifest` md5 unchanged: `0bf3a7d9411ee692d0a9f152a7533803`.
- Constitution verified `8b74865634b1db07` unchanged (printed on every CLI
  invocation this session).
- Today's bar already processed by the 00:20 UTC daily run before this
  session started (`tick` not run this session, no double-trade).
- No genome promotion — no README `## Status` update needed.

## Next, if this thread stays worth pursuing

The per-trade `anatomy` post-mortem restricted to window 5 that this session
originally set out to do is still open — worth doing, but now with the
caveat that "window 5" as a single 2-year span ending exactly "now" is one
noisy draw, so its trade list shouldn't be over-read either. Sharper
follow-ups: (a) run `--boundary-shift` on windows 3/4 too, to see if they're
similarly noisy or if window 5 is unusual in how close its verdict sits to
the flip point; (b) trace what actually differs between two adjacent-shift
runs' first few trades to find the mechanism directly instead of treating it
as a black box.
