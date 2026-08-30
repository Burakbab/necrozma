# 3-hourly check — 2026-08-30 00:46 UTC — first real hard-call verdict recorded

## Daily bar

Already handled. `live_state.json` `updated: 2026-08-30T00:21:36+00:00`, tick
16 (bar 2026-08-29) traded LINKUSDT and left the first-ever real hard-call
flag pending review (see `runs/2026-08-30-0020-daily-trading.md`). No new bar
to trade this cycle.

## What this cycle did: reviewed tick 16's flagged hard call

`review-hard-calls` flagged tick 16 as a lone-voice LINKUSDT buy (agreement
0.33, 0.94 conviction, 17.0% of equity, the only order the bar produced) —
the first live tick to ever trip `flag_hard_call` since the infrastructure
shipped 2026-08-18 with no real case yet to exercise it.

Reconstructed `RiskJudge.rule`'s scoring arithmetic by hand against champion
v3's real evolved `risk_judge` genes and matched it to the actual order to
the cent, rather than taking the flag at face value:

- 9 buy candidates were proposed that bar. Champion v3's evolved
  `lone_voice_scale` (1.4791) is *higher* than `two_agree_bonus` (1.2) — an
  evolved property, not a default — so a confident solo signal structurally
  outscores a weaker two-consultant agreement. LINKUSDT's score
  (conviction 0.938 × 1.4791 = 1.387) was the single highest of all 9
  candidates, beating even the bar's only multi-agree candidate, UNIUSDT
  (conv 0.662 × 1.2 = 0.794, share 0.667).
- Deployable cash that bar was `cash_pct` 52.0% minus the evolved
  `cash_floor_pct` 35.03% = 16.97% of equity ($1915.45) — recomputing
  `target = min(base_size_pct * score * regime_scale, max_position_pct)`,
  capped by `cash_avail`, gives `min(0.25, ...) * equity` capped to exactly
  $1915.45, matching the real order's `amount` to the cent. LINK's fill
  consumed the entire deployable-cash budget, which is why every other
  candidate that bar (several with real conviction — XRP 0.904, ETH
  0.892) was vetoed `"no room: size cap or cash floor"` — a correct
  consequence of the cash floor, not a processing-order bug.
- Size (17.0% of equity) sits within both `max_position_pct` (25%) and
  `hard_max_position_pct` (35%). The underlying signal itself was an
  ordinary confirmed-trend read (ma-spread +26.1%, slope +4.70%, rsi 71
  in-band), not an outlier bet.

**Verdict: `approve`** — recorded via
`evotrader_bundle.py review-hard-calls --tick 16 --verdict approve --notes
'...'` (full notes text in `live_state.json`'s `hard_call_reviews`). This was
the evolved genome's own risk logic operating exactly as designed; nothing to
correct. `review-hard-calls` now reports 0 pending, 1 reviewed.

## Open observation, not actioned this cycle

Champion v3's `lone_voice_scale` (1.4791) evolving to exceed
`two_agree_bonus` (1.2) is a real, measurable design choice that structurally
favors single-consultant conviction over cross-consultant consensus. This is
the same direction the last few 3-hourly sessions' disagreement-sweep work
has been circling (raw-fitness-vs-excess-return disagreement skews heavily
"risky" direction, 61-89% across every keep_frac point tried). Not chased
further this run — flagging it as a candidate thread for whoever next
revisits the disagreement/selection-metric question, since this gene pairing
may be a contributor to why lone-voice bets keep winning the risk-sizing
lottery.

## Verified safe

`review-hard-calls` re-run after recording confirms 0 pending. Full test
suite and bundle sync check kicked off in background; only `live_state.json`
changed (`hard_call_reviews` gained one entry) — `git diff --stat` shows
`live_state.json | 15 +++++++++++++--`, no other file touched.

## AGENTS.md updated

"Current state" (new dated entry) and "Next steps" item 0 marked resolved
(the pending hard-call review is no longer outstanding).
