# 2026-08-22 03:56 UTC — 3-hourly check: the maxDD gate has a real fold-boundary blind spot

## Context

The previous 3-hourly check (`runs/2026-08-22-0100-maxdd-jump-and-fetch-truncation-bug.md`)
found and fixed a real silent-truncation bug in `core.market.fetch_klines`, but
explicitly left the actual mystery unresolved: why did this session's
`universe-perturb` baseline read -46.5% maxDD (crossing `MAX_DD_HARD_FAIL`) when
every session the week before had consistently reported -34.1% for what should be
the same computation. Its "Next" line asked for exactly one thing: re-run the
full single-symbol census fresh under the now gap-checked fetch path before
trusting either number, and only then resume a `MAX_DD_HARD_FAIL` design pass.

## Step 1 — reproduce clean

Fresh census, standalone script (`load_universe` once, `run_backtest` per
single-symbol drop, same primitives `universe-perturb`'s CLI uses):

- Baseline (27 symbols): fitness `-inf`, maxDD **-46.5%**, trades 1071, return
  228.4% — identical to the 01:00 session's number.
- 15/27 single-symbol drops now hard-fail `MAX_DD_HARD_FAIL` alone (up from
  14/27 on 2026-08-21): ETH, BNB, SOL, ADA, DOGE, AVAX, DOT, TRX, ZEC, INJ,
  AAVE, XLM, SHIB, CRV, FIL. CRVUSDT is newly added to the failing set vs the
  2026-08-21 census.
- No `[market] WARNING` gap lines from the new `find_gaps` check anywhere in
  this run's output.

Clean reproduction under a verified-gapless fetch path is exactly the branch the
previous entry flagged as "materially more urgent than 'cliff nearby'" — the
silent-truncation fix does not explain the -34.1%-vs-46.5% discrepancy.

## Step 2 — find the actual mechanism instead of stopping at "confirmed, unexplained"

Champion v3 was promoted through `loop.evolve.Evaluator`, which never runs one
continuous backtest over the full history — it backtests 3 disjoint calendar
folds independently and merges their stats. Read `Evaluator._merge`:

```python
"max_dd": float(np.min([x.get("max_dd", 0) for x in s])),
```

That is the worst of the three folds' own **independently computed local**
peak-to-troughs — each fold's NAV/position tracking starts fresh at that fold's
own boundary. A true continuous drawdown that starts near the end of one fold
and bottoms out early in the next fold is invisible to *either* fold's own
local max_dd, and therefore invisible to the merged number `accepts()` and
`fitness()` actually gate on.

Verified directly with a small standalone script (`Evaluator(data).evaluate(g0)`
next to one continuous `run_backtest(g0, data, 0.0, 1.0)`):

```
fold 1 [0.000, 0.283]: max_dd -26.9%  fitness -0.201
fold 2 [0.283, 0.567]: max_dd -34.1%  fitness  4.529
fold 3 [0.567, 0.850]: max_dd -26.9%  fitness  1.141
merged (gate-visible) max_dd = -34.1%
```

-34.1% is exactly the number every 2026-08-21 session reported — it's not stale
or wrong, it's a genuinely different metric (worst-of-3-local-folds) than what
`universe-perturb`/`drawdown`/`anatomy` compute (one unbroken full-history
replay). The two numbers were never supposed to agree.

## New diagnostic: `fold-dd-blindspot [--also-version N]`

Read-only CLI in the plain-script section of `evotrader_bundle.py` (pure
addition, no `_SRC[...]` module touched). For each champion: prints each fold's
own local max_dd, the gate-visible merged max_dd, one continuous replay over the
identical `[0, search_end]` span, and one continuous replay over the full
`[0, 1]` history (matching `universe-perturb`/`drawdown`/`anatomy`'s own
number). Composes only already-tested `Evaluator.evaluate`/`run_backtest` — no
engine or constitution change, same precedent as `fold-scheme`/`margin-curve`/
`regime` (no new pure function, no new test file).

```
MAXDD GATE BLIND SPOT -- v3 (live)
  fold 1 [0.000, 0.283]: own local max_dd  -26.9%
  fold 2 [0.283, 0.567]: own local max_dd  -34.1%
  fold 3 [0.567, 0.850]: own local max_dd  -26.9%
  gate-visible max_dd (worst of the folds above, what accepts() checks):  -34.1%
  true continuous max_dd, same [0, 0.850] search span, one unbroken replay:  -46.5%  (gap -12.4%)
  true continuous max_dd, full [0, 1] history incl. holdout:  -46.5% (OVER MAX_DD_HARD_FAIL, gate never sees it)

MAXDD GATE BLIND SPOT -- v1 (reconstructed)
  fold 1 [0.000, 0.283]: own local max_dd  -30.2%
  fold 2 [0.283, 0.567]: own local max_dd  -44.4%
  fold 3 [0.567, 0.850]: own local max_dd  -21.6%
  gate-visible max_dd (worst of the folds above, what accepts() checks):  -44.4%
  true continuous max_dd, same [0, 0.850] search span, one unbroken replay:  -45.3%  (gap -0.9%)
  true continuous max_dd, full [0, 1] history incl. holdout:  -54.4% (OVER MAX_DD_HARD_FAIL, gate never sees it)
```

The -12.4pp gap for v3 is the exact jump the 01:00 session flagged as a mystery.
It lives entirely inside the search span (the full-[0,1] number is unchanged at
-46.5%), not in the holdout slice. v1's blind spot is small inside the search
span (0.9pp) but much larger once the holdout slice is folded in (-54.4% true
vs -44.4% gate-visible) — matching the independent -54.3% reading the
2026-08-21 `universe-perturb` session found for v1's unperturbed full-history
baseline. The blind spot's size is genome/window-specific, not a fixed offset.

## Verification

- `py_compile evotrader_bundle.py` clean.
- `python3 tools/edit_bundle_module.py verify` — round-trip clean.
- Full test suite: 184 passed (unchanged — no new pure function needed).
- `live_state.json` md5 identical throughout: `3f71d6ab111ecd646eda9e0e595a9970`.
- `evotrader.manifest` md5 identical: `0bf3a7d9411ee692d0a9f152a7533803`.
- `constitution verified 8b74865634b1db07` unchanged on every invocation.
- `git diff --stat`: `evotrader_bundle.py | 72 +++...` — pure addition, zero
  `_SRC[...]` lines touched (confirmed by grepping the diff).
- Today's 2026-08-22 bar already confirmed processed by the 00:20 UTC daily run
  before this check started (`live_state.json` `updated` timestamp
  `2026-08-22T00:21:18+00:00`); `tick` not run this session, no double-trade.
- `review-hard-calls`: not re-checked this session (no new candidate activity);
  no genome promotion, no README `## Status` change needed.

## Reading

This is not a data bug and the silent-truncation fix from the previous session,
while still a real and worthwhile fix, does not explain this discrepancy. The
actual finding is structural: `MAX_DD_HARD_FAIL` is supposed to be a hard safety
gate against catastrophic drawdown, but the number it actually checks
(worst-of-3-independent-folds' local max_dd) cannot see a drawdown that spans a
fold boundary, by construction. Champion v3's true full-history drawdown
(-46.5%) already exceeds the 40% threshold that gate is supposed to enforce,
and the acceptance process that promoted v3 structurally could not have caught
that, because it never runs one continuous backtest across fold boundaries.

## Not attempted this run

Fixing this is a genuine constitution change — recomputing the merged max_dd
from a continuous replay (or some other reconstruction) changes what
`accepts()`/`fitness()` actually gate on, and needs its own design pass (there
isn't an obviously-correct way to reconstruct a "true" merged drawdown that
doesn't undermine the walk-forward folds' independence — that needs real
thought, not a quick patch) plus an `AMENDMENTS.md` row. Deliberately not
started this run; flagged as the clear next priority in AGENTS.md's Next steps.

## Push notification

Sent given the severity: this closes out the previous session's open safety
question ("is this a bug or a real gate failure") with a definitive answer —
real gate failure, not a bug — and the live champion's true drawdown already
exceeds its own supposed hard-fail threshold by a mechanism nothing before this
session had identified.
