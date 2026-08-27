# 2026-08-27 15:49 UTC — 3-hourly check: window-4 anatomy, third independent confirmation

## Context

The 12:54 UTC entry today ran `history-perturb --independent --anatomy` on
window 3 (2020-08-27 to 2022-08-27, net winner) and found the same
exit-mechanism split as window 5's earlier post-mortem (discretionary
consult exits lose, mechanical guardian/consult_conservative exits win),
while the holding-period claim from window 5 didn't replicate. It named
window 4 as the next window to check, to see whether the exit-mechanism
split is 3-for-3.

## What ran

Housekeeping first: `git checkout main` landed in the same stale-branch
state the 09:56 UTC entry hit and fixed (local `main` 50 commits behind
`origin/main`, from an earlier session's clone) — resolved the same way,
`git reset --hard origin/main`, no force-push, no local work lost (working
tree was clean). `pip3 install -r requirements.txt`. Then confirmed today's
bar was already handled (`live_state.json` `updated`
`2026-08-27T00:21:49+00:00`, tick 13, unchanged all day) before running:

```
python3 evotrader_bundle.py history-perturb --independent --anatomy --sub-slice-window 4
```

No new code — `--anatomy [--sub-slice-window I]` already existed from the
09:56 UTC entry. Read-only, no state/genome/constitution touched: `git
status` clean throughout, `live_state.json` md5
`1add861014e44aa69e814491cbd22e00` and `evotrader.manifest` md5
`0bf3a7d9411ee692d0a9f152a7533803` both unchanged before and after the run.

## Result — window 4 (2022-08-27 to 2024-08-27, 497 closed trades)

Window 4 is a mixed case: +129.6% absolute return but -5.5% excess vs a
+135.2% benchmark (`beat_bench: false`) — net loser relative to
buy-and-hold, unlike window 3, but for a different reason than window 5
(window 4 still made money in absolute terms; window 5 lost outright).

- BY EXIT MECHANISM: `circuit_breaker` -$3,668/15 (7% win), `consult_risky`
  -$2,322/107 (32% win), `consult_moderate` -$2,173/159 (40% win) all lose;
  `consult_conservative` +$1,733/22 (95% win) and `guardian` +$20,784/194
  (52% win) both profit. **Same ranking as windows 3 and 5 — this is now a
  third independent confirmation** of discretionary consult exits
  underperforming mechanical exits, across a bull-dominated net winner
  (window 3), a bear-dominated net loser (window 5), and now a mixed
  absolute-winner/relative-loser (window 4).
- BY HOLDING PERIOD: 6-20 bars is the *most* profitable bucket here
  (+$10,649/302), matching window 3's positive reading and contradicting
  window 5's "6-20 bars is the sole negative bucket" finding. This is the
  second window against one confirming window 5 — the holding-period claim
  stays dropped, now on firmer footing.
- BY REGIME: `chop` is the only negative bucket (-$2,306/82, 26% win);
  `bear` (+$4,669/293, 49% win) and `bull` (+$11,991/122, 46% win) both
  profit here, unlike window 5 where `bear` was the loser. Regime
  attribution doesn't have a consistent sign across windows — reads as
  window-specific, not a general property.

## Reading

The exit-mechanism finding — `consult_moderate`/`consult_risky`/
`circuit_breaker` exits underperform `guardian`/`consult_conservative`
exits — now holds in 3/3 independent 2-year windows checked (3, 4, 5),
across three different net-outcome shapes (net winner, mixed, net loser)
and three different regime compositions. This is the strongest evidence yet
that it's a structural property of the current genome's exit logic, not a
regime artifact or a fluke of any one window. The holding-period and
regime-sign claims both fail to replicate consistently and should stay
dropped as leads.

What's still untried: an actual gene/threshold change tightening
`consult_moderate`/`consult_risky`'s own exit conditions toward
`guardian`'s mechanical stop/take-profit/time-stop logic. This diagnostic
shows correlation between exit agent and P&L, not that changing the exit
gene would help fold-aggregate fitness net of what it costs elsewhere —
these same consults' *entries* are separately flat-to-positive in every
window checked so far, so any change has to preserve that. That's real
code plus a real `evolve` run (shadow, not touching live), not another
read-only diagnostic — a bigger scope than this session, but the
diagnostic groundwork (3/3 replication across regime types) is now solid
enough to justify attempting it.

## Next

- Windows 1 and 2 remain unchecked if a fourth/fifth confirmation is
  wanted, but with 3/3 already agreeing across three different outcome
  shapes, the marginal value of a fourth read-only pass is lower than
  attempting the actual gene-change sketch below.
- **Recommended next step for a session with more time budget**: sketch a
  shadow `evolve` run (or a hand-authored genome variant, tested via
  `run_backtest` directly) that tightens `consult_moderate.max_bars_held`-
  style exit thresholds or routes more consult exits through
  `guardian`-like mechanical rules, then check fold-aggregate fitness
  against the unmodified champion on the same folds this diagnostic used.
  Must not touch `live_state.json` — shadow/offline only until proven.
- Day-1-allocation-redesign question (flagged 2026-08-26 09:50 UTC) is
  still open and untouched.

No code, state, or constitution changed this session. No genome
promotion, no README/dashboard update needed.
