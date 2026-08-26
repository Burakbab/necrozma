# Traced the boundary-shift path-dependence mechanism: it's day-1 cash allocation, not a black box

**3-hourly self-improvement check, ~06:55 UTC.**

## Why

Picked up the sharpest concrete next step from the 03:53 UTC entry: "trace
what actually differs between two adjacent boundary-shift runs' first few
trades ... to find the path-dependence mechanism directly instead of
treating it as a black box." Today's bar (2026-08-26) was already traded by
the dedicated 00:20 UTC daily run before this session started — confirmed
via `live_state.json`'s `updated: 2026-08-26T00:22:17+00:00` and the
`runs/2026-08-26-0020-daily-trading.md` note; nothing new to trade this
session.

## What happened

Wrote a scratch script reproducing window 3's shift 2 vs shift 3 (the pair
the 03:53 UTC entry called out: +357.2% vs -148.2% excess return one day
apart) with `run_backtest(..., log_detail=True)` so both runs carry a full
`closed_trades` list and `decision_log`. Diffed the two trade sequences and
the day-1 decisions directly.

**Finding**: the very first closed trade already differs. Shift 2 and shift
3 both enter BTCUSDT on 2020-11-03 at the identical price (14030.5418 — the
entry bar itself is unaffected by the 1-day boundary shift since it's ~12
bars into the replay), but with a **different position size** (qty 0.001641
vs 0.002163) and a **different exit** (2020-11-05 vs 2020-11-04, different
`consult_conservative`/`consult_moderate` exit rationale). Tracing further
back: **day 1's fills are a different set of symbols entirely** — shift 2
fills `['BNBUSDT', 'LINKUSDT', 'XLMUSDT']`, shift 3 fills `['BCHUSDT',
'BNBUSDT', 'LTCUSDT']`. Two of three symbols don't even match.

**Mechanism**: shifting the window's start date by one day changes every
asset's rolling-indicator values (MA spread, RSI, momentum rank, breakout %)
on what becomes "day 1" of the replay, because those indicators are computed
over lookback windows anchored to the replay's own start, not calendar time.
That's expected and mundane on its own — but `risk_judge`'s cash allocation
on day 1 is a **greedy, order-sensitive, hard-capped** process (visible in
the `decision_log`: most proposals get vetoed with `"no room: size cap or
cash floor"` even on day 1, cash going from $10,000 to ~35% within one bar).
Whichever symbols happen to cross the entry threshold and get evaluated
first on day 1 claim the available cash; a 1-day shift changes that set
outright, not just its ranking. Once day 1's capital is split across a
different set of positions, bar 2 onward compounds the divergence through
500+ trades and ~2 years — by the end, total return separates by 500+
percentage points from what is nominally "the same" 2-year window.

This confirms the 03:53 UTC entry's cascading-first-bar-decision hypothesis
directly, with a real trade-level trace instead of inference from aggregate
stats.

## Shipped

New `--trace-diff S1,S2` flag on `history-perturb --boundary-shift`
(`evotrader_bundle.py`, inside the existing `boundary_shift_n` block —
CLI-only code in `main()`, not part of the unflattened `_SRC` modules, so no
bundle-sync step needed). Given two shift indices already covered by
`--boundary-shift N`, re-runs those two specific shifts with
`log_detail=True` (the rest of the sweep stays `log_detail=False`, same
cost as before) and prints: the first structurally-divergent closed trade
between the two shifts, and whether day-1's fills are the same symbol set.
Same guarantees as every other `history-perturb` flag: requires
`--independent --boundary-shift`, read-only, never touches
`live_state.json` or the champion, no new pure function so no new test file
(consistent with how `--sub-slice`/`--drawdown` were added — this whole
diagnostic family isn't unit-tested with fixtures since it needs real market
data; verified instead by running it and checking the full suite still
passes).

Verified against the real numbers from the 03:53 UTC entry's window-3
table:

```
python3 evotrader_bundle.py history-perturb --independent --boundary-shift 4 \
  --sub-slice-window 3 --trace-diff 2,3
```

reproduces `1.174 fitness / 663.9% return / -34.7% maxDD` for shift 2 and
`-inf fitness / 146.8% return / -47.7% maxDD` for shift 3 exactly, then
prints the trade/fills trace above.

## Reading

This closes the "still not chased" mechanism gap flagged in both prior
boundary-shift entries (00:59 and 03:53 UTC). It reframes what "path
dependence" means here concretely: it isn't noise in the return-generating
process itself, it's that a hard-capped, order-sensitive first-bar
allocation is a discrete, high-leverage decision point — small input
changes (which day is "day 1") flip which assets receive capital, not just
by how much. That's a fragility of the greedy allocation scheme under
`risk_judge`'s size caps / cash floor, not of the strategy's signals per se.
Doesn't by itself argue for a specific fix (e.g. smoothing day-1 entries,
staggering the warmup, or accepting this as an inherent property of any
capital-constrained multi-asset entry process) — that's a separate design
question, not attempted here. Folds into the already-open v3
demotion/rollback question (raised to the owner 2026-08-22) as the
mechanistic explanation underneath the boundary-noise finding, not a new
open item on its own.

## Verified safe

- Full suite: 235 passed (`pytest tests/`, 138.71s) after the change —
  same count as the 03:53 UTC entry's baseline (235), no regressions, no
  new tests needed for this CLI-only addition.
- `python3 -c "import ast; ast.parse(...)"` on `evotrader_bundle.py` before
  running anything, confirming the edit is syntactically clean.
- `git status --short` shows only `evotrader_bundle.py` modified.
- `live_state.json` md5 unchanged (`1441d25f45fb4a927f993cbc8c505a5b`)
  before and after — this session never calls `acct.save()`.
- `evotrader.manifest` / constitution unaffected — the edit is inside
  `main()`'s CLI dispatcher, not the `constitution/` package, and every
  invocation printed `constitution verified 8b74865634b1db07`, unchanged.
- Today's bar already processed by the 00:20 UTC daily run before this
  session started (`tick` not run this session, no double-trade).
- No genome promotion — no README `## Status` update needed.

## Next, if this thread stays worth pursuing

- Whether the same day-1-allocation mechanism explains window 5's
  boundary-noise the same way, or whether window 5 (the one currently in a
  real drawdown) shows something additionally regime-specific — not
  checked this session, only window 3 was traced.
- Whether a fix belongs at the allocation layer (e.g. size day-1 entries
  proportionally instead of first-come-first-served) is real design work,
  untried, and would need its own reasoning about whether it's worth a
  constitution change or genome-level gene.
