# 2026-08-27 12:54 UTC — 3-hourly check: window-3 anatomy, checking window-5 exit-mechanism pattern

## Context

The 09:56 UTC entry today ran `history-perturb --independent --anatomy` on
window 5 (2024-08-26 to 2026-08-27, net -6.1% vs benchmark) and found the
loss concentrated in discretionary exits (`consult_moderate`, `circuit_breaker`,
`consult_risky`) while mechanical exits (`guardian`, `consult_conservative`)
were strongly profitable, and 6-20 bar holds were the only negative
holding-period bucket. It flagged this as "one window, not yet a pattern" and
named window 3 as the next regime-mixed window to check.

## What ran

Housekeeping first: `git pull`/state checks from the top of the protocol
found nothing new (today's bar already processed at 00:21:49 UTC by the
00:20 daily run; `live_state.json` still tick 13). Then:

```
python3 evotrader_bundle.py history-perturb --independent --anatomy --sub-slice-window 3
```

Read-only, no state/genome/constitution touched (confirmed after: `git status`
clean, `live_state.json` md5 `1add861014e44aa69e814491cbd22e00` and
`evotrader.manifest` md5 `0bf3a7d9411ee692d0a9f152a7533803` both unchanged
from before the run).

(Note: `history-perturb --help` is not a real flag — the CLI has no argparse
help handler and silently falls through to the default nested-years mode
instead of erroring. Ran once by mistake this session, harmless — same
read-only guarantees, just not the intended command. Worth a one-line fix
some day but not chased now.)

## Result

Window 3 (2020-08-27 to 2022-08-27, 554 trades) is net **profitable**:
+527.2% return vs +303.8% benchmark, excess +223.4%, fitness 1.160 — unlike
window 5's net loss. But the same *exit-mechanism* split shows up:

- BY EXIT MECHANISM: `consult_moderate` -$15,026/132 (27% win),
  `consult_risky` -$4,956/192 (24% win), `circuit_breaker` -$4,561/5 (0% win)
  all lose money; `consult_conservative` +$4,031/15 (53% win) and `guardian`
  +$77,883/210 (50% win) both profit. Same ranking as window 5 (discretionary
  consult exits lose, mechanical/guardian exits win) — **this part
  replicates**.
- BY HOLDING PERIOD: 6-20 bars is the *second-most profitable* bucket here
  (+$29,557/320), not the sole negative one like in window 5. 2-5 bars is
  also positive (+$28,498/179); only 1-bar holds lose slightly (-$683/55).
  **This part does not replicate** — window 5's "6-20 bar holds are
  structurally negative" finding was specific to that window being a net
  loser overall, not a general holding-period defect.
- BY REGIME: `bear` has the most trades (393) and is net negative
  (-$10,072), same qualitative shape as window 5's bear bucket, but here
  `bull` trades (only 133 of 554) are so profitable (+$78,575, 62% win) they
  swamp it — window 3 is not bear-heavy in P&L terms the way window 5 was,
  despite bear dominating trade count in both.

## Reading

The exit-mechanism ranking (discretionary consult exits underperform,
guardian/conservative-exit outperform) now has two independent confirmations
(window 3 bull-dominated-net-winner, window 5 bear-dominated-net-loser) and
looks like a real, regime-independent property of the current genome's exit
logic, not a fluke of one losing window. The holding-period claim does not
generalize — drop it as a lead. A live gene change (tightening
`consult_moderate`/`consult_risky`'s own exit thresholds toward guardian's
mechanical stops) is still untried and still just a hypothesis at this point,
not sketched as code — the anatomy diagnostic shows correlation between exit
agent and P&L, not that changing the exit gene would improve fold-aggregate
fitness net of what it would give up elsewhere (e.g. these same consults'
entries are separately reported as flat-to-positive, so any change has to
preserve that).

## Next

- If this thread continues: pick a third window (1, 2, or 4) to see whether
  the exit-mechanism split is 3-for-3 or window-3-and-5-specific for some
  other reason (e.g. both are "the two windows checked so far", not proof of
  universality).
- Sketching an actual gene/threshold change for `consult_moderate`/
  `consult_risky` exits is the natural next step if the pattern holds up
  further, but that's real code + a real `evolve` run, not another read-only
  diagnostic — scope for a future session with more time budget.
- Day-1-allocation-redesign question (flagged 2026-08-26 09:50 UTC) is still
  open and untouched.

No code, state, or constitution changed this session. No genome promotion,
no README/dashboard update needed.
