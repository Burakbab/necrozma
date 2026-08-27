# `history-perturb --independent --anatomy`: the window-5 per-trade post-mortem

**3-hourly self-improvement check, ~09:56 UTC.**

## Why

Today's bar (2026-08-27) was already traded by the dedicated 00:20 UTC daily
run before this session started (`live_state.json` `updated`
`2026-08-27T00:21:49+00:00`, tick 13) — nothing to do on the trading side.
The 06:48 UTC entry closed the lineage-age holdout-margin question and left
two items open from the 2026-08-26 09:50 UTC boundary-shift entry: a
window-5 per-trade `anatomy` post-mortem, and a day-1-allocation redesign
(untried design work). Also noted, before starting either: this session's
local `git` clone had diverged from `origin/main` (detached-HEAD checkout
landed on a stale `main` ref from a previous session, 50 commits behind and
sideways of current `origin/main`) — per `AGENTS.md`'s own run protocol,
`origin/main` is authoritative on divergence; resolved with `git reset --hard
origin/main` before reading anything else, no force-push, no local work lost
(there was none — the stale branch was pure history, not uncommitted
changes).

Picked the anatomy post-mortem: every other window-5 diagnostic in this
thread (`--sub-slice`, `--drawdown`, `--boundary-shift`) reports aggregate
stats or drawdown episodes, never which trades or mechanisms actually drove
the loss. The stress-test half of the fold-date-sensitivity thread was
explicitly discouraged from another identical-method batch by the 04:05 UTC
entry, so this thread's remaining open item was the better use of the slot.

## What shipped

New `--anatomy [--sub-slice-window I]` flag on `history-perturb
--independent`. Reuses the already-tested `trade_anatomy` (`loop.engine`,
same function the plain `anatomy` command calls) and the same
`run_backtest(..., log_detail=True)` call every other flag in this family
already makes — just scoped to one independent window instead of the full
`[0,1]` history. No engine or constitution change, no new pure function, CLI-
only code in `main()` (same file, same precedent noted by the
`--trace-diff`/`--boundary-shift` entries — not part of the unflattened
`_SRC` modules, so `tools/edit_bundle_module.py sync --check` stays a true
no-op). Target window selection reuses the existing `--sub-slice-window`
flag, same convention as `--drawdown`/`--sub-slice` (defaults to the most
recent window).

## Result — window 5 (2024-08-26 to 2026-08-27, 483 closed trades)

```
483 closed trades | win rate 32.3% | profit factor 0.97
expectancy per trade $-2 | total $-800
strategy -6.1% vs buy-and-hold +70.2% -> excess -76.3%

BY ENTRY AGENT
  consult_conservative     $-2  n=4    win 75%
  consult_risky           $769  n=319  win 34%
  consult_moderate      $1,016  n=252  win 33%

BY EXIT MECHANISM
  consult_moderate      $-2,760  n=126  win 33%
  circuit_breaker       $-2,463  n=17   win 12%
  consult_risky         $-1,615  n=144  win 15%
  consult_conservative   $1,078  n=20   win 90%
  guardian               $4,960  n=176  win 41%

BY MARKET REGIME
  bear   $-2,623  n=335  win 30%
  chop     $-593  n=79   win 32%
  bull    $2,416  n=69   win 46%

BY HOLDING PERIOD
  6-20 bars  $-3,734  n=280  win 31%
  1 bar         $530  n=53   win 28%
  2-5 bars    $2,404  n=150  win 36%

Worst symbols: XLMUSDT $-1,771, ICPUSDT $-1,549, FILUSDT $-1,382,
               ATOMUSDT $-1,317, FETUSDT $-1,269
```

**Reading, different shape from the full-history 2026-08-16 finding.** The
2026-08-16 "Measured" note found `consult_conservative` a bad *entry* signal
(38% win, -$8,159) system-wide, and the 2026-08-23 `consult-role-test`
diagnostic found that already search-corrected for live champion v3 (it
rarely fires as an entry any more). Window 5 confirms that specifically:
`consult_conservative` contributes only 4 entries here (barely used), and
its role-asymmetry pattern is intact as an *exit* signal (+$1,078, 90% win,
the best win rate of any category in this table) — old finding, still true,
not the story in this window.

The window-5 story is different: **entries are not the problem here** — all
three consults' own entry attribution is flat-to-positive (`consult_risky`
+$769, `consult_moderate` +$1,016, `consult_conservative` ~$0). The loss is
concentrated in **exits**: `consult_moderate`'s own exit signal is the single
largest loss category (-$2,760, 126 trades, 33% win — a discretionary exit
that underperforms just holding), `circuit_breaker` is second (-$2,463 over
only 17 trades — a 12% win rate and -$145 average, the worst per-trade
number of any category), and `consult_risky`'s exit is third (-$1,615, 15%
win). Meanwhile the two *mechanical* exit paths are strongly profitable:
`guardian` (stop-loss/take-profit/time-stop) is the single best category on
the whole table (+$4,960, 41% win, the most trades of any category), and
`consult_conservative`'s exit as already noted. Read together: in this
window, letting a rule-based exit run is working; the two consults'
own discretionary exit calls are actively losing money relative to what a
mechanical exit would have done, and the circuit breaker (already known
system-wide as a small net negative, -$1,820/14 trades from the 2026-08-16
measurement) is a much larger and more decisive drag here (-$2,463/17
trades) — consistent with a genuinely harder regime, not a fixed defect,
since 335/483 trades (69%) are tagged `bear` and that bucket alone accounts
for -$2,623, more than the whole window's net loss.

**Holding period cuts across both**: the 6-20 bar bucket is the only
structurally negative one (-$3,734, 280 trades, 58% of all trades) while
quick trades (1 bar, +$530) and short holds (2-5 bars, +$2,404) are both
positive. Combined with the exit-mechanism read, this points at the same
underlying shape from two angles: trades that get *held* long enough for a
consult's own discretionary exit judgment to fire (rather than a fast
mechanical stop/target) are where the loss concentrates.

**Not chased further this session, flagged for whoever picks this up
next**: this is one window (483 trades, one specific 2-year draw, already
flagged noisy by the 2026-08-26 00:59 UTC boundary-shift entry — a
1-day shift in "now" previously flipped this same window from hard-fail to
beat-benchmark). Before treating "consult_moderate/consult_risky exits
underperform guardian/circuit_breaker-adjacent mechanical exits in a bear
regime" as a real, actionable pattern rather than one noisy draw's post-hoc
story, it should be checked against at least one other window this
mechanism could plausibly appear in (window 3, also regime-mixed per the
2026-08-25 21:55 UTC characterization) — not attempted here, this session
only ran the flag once on the target window it was built for. If it
replicates, the natural next question is whether tightening
`consult_moderate`/`consult_risky`'s own exit thresholds (or leaning harder
on `guardian`'s mechanical exits) is worth proposing as an actual gene
change — genuinely untried, no code sketched.

## Verification

- `py_compile evotrader_bundle.py` clean.
- `tools/edit_bundle_module.py sync --check`: "bundle already matches real
  files, no changes" (confirms the edit is CLI-only, no `_SRC` drift).
- Full suite: 235 passed (125.68s), matches baseline, no new pure function
  so no new test file (same precedent as every other flag in this family).
- `git diff --stat`: only `evotrader_bundle.py` touched.
- `live_state.json` md5 `1add861014e44aa69e814491cbd22e00` unchanged (still
  tick 13, `updated` `2026-08-27T00:21:49+00:00` from the 00:20 UTC daily
  run — no double-trade).
- `evotrader.manifest` md5 `0bf3a7d9411ee692d0a9f152a7533803` unchanged,
  constitution verified `8b74865634b1db07` unchanged.
- No genome promotion — no README `## Status` change needed, no dashboard
  rebuild needed (state didn't change).
