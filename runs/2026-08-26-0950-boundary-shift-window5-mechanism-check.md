# Boundary-shift day-1 allocation mechanism confirmed on window 5 too

**3-hourly self-improvement check, ~09:50 UTC.**

## Why

Today's bar (2026-08-26) was already traded by the dedicated 00:20 UTC daily
run before this session started — nothing to do on the trading side
(`live_state.json` `updated` timestamp `2026-08-26T00:22:17+00:00`, matches
the 00:20 UTC daily run; `runs/2026-08-26-0020-daily-trading.md` and the
09:00 UTC daily discussion both confirm no anomalies). Picked up the sharpest
open item from the 06:55 UTC entry: that session traced window 3's boundary-
shift path-dependence to a greedy, hard-capped day-1 cash allocation in
`risk_judge`, but explicitly left open "whether the same day-1-allocation
mechanism explains window 5's noise... not checked this session, only
window 3 was traced."

## What happened

No code changes — reused the existing `--trace-diff` flag shipped 06:55 UTC
(same file/precedent as `--sub-slice`/`--drawdown`/`--boundary-shift`
themselves) pointed at window 5 instead of window 3:

```
python3 evotrader_bundle.py history-perturb --independent \
  --sub-slice-window 5 --boundary-shift 15 --trace-diff 0,1
```

Chose shifts 0 vs 1 because they're the sharpest one-day divergence on
record for window 5 (from the 00:59 UTC entry's sweep: excess return +3.7%
→ -44.4%, `beat_benchmark` True → False, from walking the window end back a
single day).

## Result

```
TRADE-DIVERGENCE TRACE: shift 0 (625 trades) vs shift 1 (603 trades)
first divergent trade index: 0
  shift 0: DOGEUSDT entry=2024-10-25 exit=2024-11-06 qty=18967.038022 px=0.1317 pnl=1223.18
  shift 1: LINKUSDT entry=2024-10-24 exit=2024-11-03 qty=64.318228 px=11.6258 pnl=-57.37
day-1 fills (DIFFERENT set): shift 0 ['DOGEUSDT', 'SOLUSDT', 'ZECUSDT'] vs shift 1 ['ETHUSDT', 'LINKUSDT', 'LTCUSDT']
```

Same mechanism as window 3, and if anything sharper here: window 3's two
shifts shared one symbol (`BNBUSDT`) in their day-1 fill set; window 5's two
shifts share **zero** — a completely disjoint set of first-day buys. The
very first trade in the whole 625/603-trade sequence already diverges, which
is consistent with the 06:55 UTC entry's account of *why*: `risk_judge`'s
day-1 cash allocation is greedy and hard-capped, so a one-day shift in where
the window starts changes every asset's rolling-indicator values on the new
"day 1," and whichever symbols cross the entry threshold first under the
tighter cap claim the available cash outright — a different symbol ranking
on day 1 produces a different funded set, not just a different order.

## Reading

Answers the open question directly: the day-1-greedy-allocation mechanism is
not window-3-specific. It's the general explanation for the boundary-shift
noise across every window checked so far (3, 4, 5), same as the
beat-benchmark/excess-return instability itself has now been shown general
(00:59 and 03:53 UTC entries). This closes out the "is it general" half of
the thread the 06:55 UTC entry opened. What's still genuinely untried is any
fix — proportional or ranked day-1 sizing instead of greedy-first-come, or
smoothing the entry-threshold ranking near the window boundary — and whether
such a change would be worth making given it only affects backtest/evaluation
path-dependence, not live trading (the live account only ever sees one real
"day 1," the actual first trade after account creation, not a swept
ensemble).

The per-trade `anatomy` post-mortem restricted to window 5, open since the
00:59 UTC entry, is still open and now doubly caveated: not just "window 5
is one noisy draw" but "day 1 of whichever draw you pick is itself an
artifact of exactly where the boundary lands," so a single post-mortem's
specific trade list would need that context to avoid being over-read.

## Verified safe

- No code changes this session (`git status --short` empty before this
  commit except the new run note) — reused the existing `--trace-diff` flag,
  no new pure function, so no test suite run needed (matches the
  no-code-change precedent of prior sessions in this family).
- `live_state.json` untouched: md5 `1441d25f45fb4a927f993cbc8c505a5b`, still
  reflects tick 12 from the 00:20 UTC daily run.
- `evotrader.manifest` md5 unchanged: `0bf3a7d9411ee692d0a9f152a7533803`.
- Constitution verified `8b74865634b1db07` unchanged (printed on the CLI
  invocation this session).
- Today's bar already processed by the 00:20 UTC daily run before this
  session started (`tick` not run this session, no double-trade).
- No genome promotion — no README `## Status` update needed.

## Next, if this thread stays worth pursuing

The mechanism is now confirmed general across windows 3 and 5 (2/2 checked).
Remaining open items, unchanged in kind from the 06:55 UTC entry: (a) the
window-5 per-trade `anatomy` post-mortem, now with the day-1-artifact caveat
layered on top of the noisy-draw caveat; (b) whether a day-1 allocation
redesign (proportional/ranked instead of greedy-first-come) is worth
attempting — untried design work, not a diagnostic; (c) whether this
mechanism has any live-trading relevance at all, since the live account
never re-draws its own "day 1" the way these swept backtest windows do —
worth stating explicitly next time this thread is picked up, since it's the
kind of framing question that could resolve the whole thread as "backtest-
evaluation artifact, not a live-trading risk" without further diagnostics.
