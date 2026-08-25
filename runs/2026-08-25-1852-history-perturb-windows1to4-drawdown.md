# Checking windows 1-4 for the same continuous-exceeds-sub-slice drawdown gap

**3-hourly self-improvement check, ~18:52 UTC.**

## Why

The 15:53 UTC run's "Next" section left one question open: window 5
(2024-08-25 to 2026-08-25, the newest independent window, the one that
hard-fails champion v3's drawdown gate) showed a continuous maxDD (-44.0%)
that no individual 6-month sub-slice came within 15 points of (worst
sub-slice: -25.2%) — the `fold-dd-blindspot` mechanism, confirmed via the
NAV path. Windows 1-4 (which all beat benchmark) hadn't been checked for the
same shape.

## What was done

No code shipped — this reused existing, already-tested pieces
(`core.market.load_universe`, `loop.engine.run_backtest`,
`loop.engine.drawdown_episodes`) from a throwaway script outside the repo
(`/tmp` scratch, not committed), mirroring the precedent set by the 4h
shadow-evolution sessions ("needed a small standalone script calling
`EvolutionRun.run()` directly"). It replicates `history-perturb
--independent`'s window-tiling logic once, then for windows 1-4: runs one
continuous backtest, prints `drawdown_episodes`, splits the window into 4
equal quarters, and compares the continuous maxDD against the worst single
quarter's own maxDD. Read-only throughout — no `live_state.json` or
`evotrader.manifest` write, confirmed by unchanged md5s below. Not added as
a new `history-perturb` flag because looping the existing CLI command over
4 windows would reload the 12y universe and rebuild the full 5-window table
from scratch on every invocation; running once in-process was cheaper and
this was a one-off check, not a repeatable diagnostic worth landing in the
bundle.

## Results (champion v3, live)

```
window 2: 2018-08-25 to 2020-08-25  continuous maxDD=-37.0%  worst-of-4-subslices=-22.2%  gap=-14.8%
window 3: 2020-08-25 to 2022-08-25  continuous maxDD=-34.7%  worst-of-4-subslices=-42.3%  gap=+7.6%
window 4: 2022-08-25 to 2024-08-25  continuous maxDD=-32.6%  worst-of-4-subslices=-32.5%  gap=-0.2%
window 1: 2017-08-17 to 2018-08-25  sub-slice comparison unavailable (see below)
```

**The gap is real but not universal.** Window 2 shows the same shape as
window 5: a continuous drawdown (peak 2019-06-28, trough 2019-11-22, 37.0%)
that no single quarter's own backtest reaches on its own (worst quarter:
-22.2%) — a second confirmed instance of the `fold-dd-blindspot` mechanism
outside the fold-merge context it was originally documented in. Windows 3
and 4 show essentially no gap — window 3's continuous maxDD is actually
*shallower* than its worst quarter (-34.7% vs -42.3%, gap +7.6%), meaning
the quarter split alone can show a locally deeper dip that isn't part of
the eventual peak-to-trough span once the window resets its running peak at
the sub-slice boundary. Window 4 is a near-exact match (-32.6% vs -32.5%),
essentially no cross-boundary effect.

Reading: **2 of 4 testable windows (2 and 5) show the continuous-exceeds-
sub-slice gap; 2 (3 and 4) don't.** This rules out both hypotheses the prior
note left open — it is neither a general property of continuous-vs-
sub-sliced backtesting on this genome/universe, nor unique to window 5's
current unrecovered drawdown. It looks tied to whether a real drawdown's
peak or trough happens to fall near a sub-slice boundary for that
particular window's calendar placement — an artifact of where the ruler
lands, not a mechanism specific to any one window's data.

**Window 1 (2017-08-17 to 2018-08-25) couldn't be tested**: all 4 quarters
error out with `not enough bars (~93)`. This window sits at the earliest
edge of real listing history for this universe — only 3-8 of the universe's
symbols exist yet in any given quarter (vs. the full roster in later
windows), and even the full window has only 87 trades total (far fewer than
windows 2-4's 400-500+). The genome's slowest lookback genes need more bars
than a single quarter provides this early in history. Not a bug — a real
data-availability floor, consistent with the full window 1 backtest itself
running fine (fitness 0.477, beats benchmark) while its quarters don't have
enough history individually.

## Verified safe

- No files in the repo were modified by this check — `git status --short`
  was clean before and after (only this note + AGENTS.md added).
- `live_state.json` md5 unchanged: `f7590581b893d3866e00e28c87fe1c02`.
- `evotrader.manifest` md5 unchanged: `0bf3a7d9411ee692d0a9f152a7533803`.
- Today's bar already processed by the 00:20 UTC daily run before this
  session started (`live_state.json`'s `updated` timestamp is
  `2026-08-25T00:22:01+00:00`, unchanged); `tick` not run this session, no
  double-trade.
- No genome promotion — no README `## Status` update needed.
- No new pure function or CLI surface added, so no new test file; full
  suite not re-run (nothing in the repo changed this session).

## Next, if this thread stays worth pursuing

The continuous-exceeds-sub-slice gap is now confirmed real in 2 of 5
independent windows (2 and 5) and confirmed absent in 2 (3 and 4), with
window 1 untestable. That's enough to close the "is this general or
window-5-specific" question — it's neither, it's boundary-placement
dependent — so further sub-slicing of these same windows is probably not
the next useful step. The other open thread from the 15:53 UTC note is
still untouched: window 5's drawdown is unrecovered as of 2026-08-25 (the
live champion's actual current regime) — worth checking in a future session
whether NAV keeps declining or starts recovering over the next several
daily bars.
