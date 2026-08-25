# `history-perturb --drawdown`: locating window 5's -44.0% drawdown exactly

**3-hourly self-improvement check, ~15:53 UTC.**

## Why

The 12:55 UTC `history-perturb --sub-slice` run found champion v3's newest
independent window (window 5, 2024-08-25 to 2026-08-25) hard-failing on
maxDD (-44.0%) even though no individual 6-month sub-slice of that same
window came within 15 points of the 40% gate (worst was -25.2%). It read
this as the same *shape* as the already-documented `fold-dd-blindspot`
mechanism — a continuous drawdown spanning a window boundary, invisible to
any one independently-reset sub-slice's own local max_dd — but couldn't
confirm it mechanistically, because nothing exposed `run_backtest`'s
internal NAV path for a direct look. Its "Next" section named two
follow-ups: locate the drawdown precisely (finer sub-slice or the NAV path),
or check whether windows 1-4 show the same gap.

Checked first, before writing new code: `run_backtest` already returns
`nav_history` (a full `(timestamp, nav)` list — see `core/portfolio.py`'s
`PaperBroker.nav_history`) in its result dict, and `loop.engine` already has
a tested pure function, `drawdown_episodes`, that turns a `nav_history` into
ranked peak/trough/recovery episodes (it's what the existing `drawdown`
command already uses over the full 4-year history or the sealed holdout).
The "not exposed" line in the prior run's note was wrong — no engine change
needed, just wiring the already-existing pieces into `history-perturb`.

## What shipped

`history-perturb --independent` gained `--drawdown [--sub-slice-window I]`
(requires `--independent`, same convention as `--sub-slice`): runs one
continuous `run_backtest` over window `I` (default: the most recent/last
window) and prints `drawdown_episodes(nav_history, top_n=5)` for it —
depth, peak date, trough date, bars, recovery date (or "not recovered") —
next to the window's own reported `max_dd` for a match/mismatch sanity
check. No new pure function (reuses `drawdown_episodes` and `run_backtest`
exactly as the existing `drawdown` command does), so no new test file, same
precedent as `--sub-slice`.

## Result (champion v3, live; window 5, 2024-08-25 to 2026-08-25)

```
DRAWDOWN EPISODES within window 5 (2024-08-25 to 2026-08-25)
reported max_dd (stats, whole window): -44.0%
deepest episode reproduces it: -44.0% (match)
   depth  peak date    trough date   bars  recovery
 -44.0%  2025-11-08   2026-08-11     276  not recovered
 -25.9%  2024-12-13   2025-03-30     107  2025-06-10
 -14.6%  2025-06-10   2025-06-22      12  2025-07-17
 -12.6%  2025-07-27   2025-08-02       6  2025-09-18
 -11.2%  2024-12-08   2024-12-10       2  2024-12-13
```

The deepest episode reproduces the reported max_dd exactly. Peak
**2025-11-08**, trough **2026-08-11**, 276 bars, **not yet recovered** as of
the newest bar in this replay. This is a real, single, unbroken decline —
not several smaller ones merged by coincidence — and it straddles exactly
the boundary the 12:55 UTC sub-slice run's shape argument predicted: the
peak (2025-11-08) falls inside sub-window 3 (2025-08-25 to 2026-02-23,
which that run measured as fitness-negative but still *beating* benchmark),
and the trough (2026-08-11) falls inside sub-window 4 (2026-02-23 to
2026-08-25, fitness-negative and *losing* to benchmark). Neither sub-window
alone can see this drawdown's full -44.0% depth because each backtest resets
its own running peak at its own start — textbook `fold-dd-blindspot`
mechanism, now confirmed directly via the NAV path rather than inferred from
shape.

The four shallower episodes are all recovered and none come close to the
40% gate individually, consistent with the sub-slice run's finding that no
6-month piece reaches it on its own.

## Verified safe

- Full suite: 235 passed (`pytest tests/`, 156.34s), matches known baseline.
  No new pure function (composes already-tested `run_backtest` and
  `drawdown_episodes`), so no new test file, same precedent as every other
  perturbation diagnostic in this family.
- `git status --short` clean before this commit (only `evotrader_bundle.py`
  and `AGENTS.md` touched).
- `live_state.json` md5 unchanged: `f7590581b893d3866e00e28c87fe1c02`.
- `evotrader.manifest` md5 unchanged: `0bf3a7d9411ee692d0a9f152a7533803`.
- Constitution verified `8b74865634b1db07` unchanged (printed at every
  command invocation).
- Today's bar already processed by the 00:20 UTC daily run before this
  session started (`live_state.json`'s `updated` timestamp is
  `2026-08-25T00:22:01+00:00`); `tick` not run this session, no
  double-trade.
- `review-hard-calls`: still 0 pending (unchanged from prior session).
- No genome promotion — no README `## Status` update needed.

## Next, if this thread stays worth pursuing

1. Run `--drawdown` against windows 1-4 (which all beat benchmark) to check
   whether the same continuous-exceeds-any-sub-slice gap shows up there too,
   or whether it's specific to window 5's regime — the open half of the
   12:55 UTC run's "Next" section.
2. The drawdown is **unrecovered as of today** (2026-08-25) — this describes
   the live champion's actual current regime, not just a historical
   backtest artifact. Worth a glance in a future session whether the NAV
   path keeps declining or starts recovering over the next several daily
   bars, since "not recovered" here means "still in it, right now," not
   "the data ran out."
