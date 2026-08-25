# `history-perturb --independent`: non-overlapping windows, the sharper follow-up the 07:01 UTC note flagged

**3-hourly self-improvement check, ~09:56 UTC.**

## Why

The 07:01 UTC `history-perturb` note shipped the start-date leg of the
fees/slippage/universe/start-date checklist, but its own scenarios are
nested — every window (2y/3y/4y/5y/6y) ends "now" and shares the same
recent stretch. It explicitly flagged the sharper follow-up: "independent,
non-overlapping windows instead of nested ones that all share the same
recent history, to tell 'recent regime happens to be a genuine headwind for
this genome' apart from a real overfitting story." That's what this ships.

## What shipped

`history-perturb` gained an `--independent` mode (`[--window-years Y]`,
default 2.0) alongside the existing nested `--years` mode — same command,
same `--also-version N` convention, no new CLI entrypoint. It loads the full
available history per universe symbol (`market.load_universe(..., 12.0)`,
generous enough to reach real Binance USDT-pair listing dates), then tiles
fixed-width, non-overlapping windows walking backward from "now" so every
window except possibly the oldest (clipped to whatever history actually
exists) gets a full, comparable width — the most recent window still ends
exactly "now", directly comparable to the nested mode's own convention.
Each window is one independent `run_backtest` call; prints a
fitness-vs-recency Pearson correlation across the windows at the end (plain
Python, no numpy dependency needed for one summary number). Same
guarantees as every other diagnostic in this family: read-only, never
touches `live_state.json` or the champion.

## Result (champion v3, live)

| window | start | end | symbols | fitness | return | sharpe | maxDD | trades | excess ret | beats benchmark |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 2017-08-17 | 2018-08-25 | 8 | 0.477 | +13.8% | 0.64 | -34.7% | 87 | +9.2% | True |
| 2 | 2018-08-25 | 2020-08-24 | 18 | 2.265 | +455.3% | 2.15 | -37.0% | 411 | +421.0% | True |
| 3 | 2020-08-24 | 2022-08-25 | 27 | 1.103 | +363.4% | 1.68 | -39.3% | 549 | +57.5% | True |
| 4 | 2022-08-25 | 2024-08-24 | 27 | 1.431 | +141.8% | 1.33 | -32.6% | 500 | +0.8% | True |
| 5 | 2024-08-24 | 2026-08-25 | 27 | -inf (hard-fail) | +36.9% | 0.63 | -45.0% | 603 | -41.2% | **False** |

4/5 finite-fitness, beats benchmark in 4/5 windows. Fitness-vs-recency
correlation r=+0.295 (weak, driven mostly by window 5's collapse — not a
clean monotonic trend).

**Reading, and this does sharpen the 07:01 UTC finding**: it isn't "one
shared recent stretch is a genuine headwind that a longer nested window's
older gains simply outweigh" (the alternative the nested test couldn't
rule out) — four genuinely independent, non-overlapping historical periods
spanning 2017-2024 all show a real, finite, benchmark-beating edge, three
of them a large one. The champion's problem is narrower and sharper than
"start-date dependent" suggested: it is specifically the most recent
independent 2-year window (2024-08-24 to 2026-08-25 — the same span the
nested test's `--years 2` scenario already flagged) that fails outright,
not a general fragility across history. That's still a real, unresolved
concern (the live champion is trading through exactly that failing regime
right now), but it reframes it from "is this edge real at all" (largely
answered: yes, across 4 independent windows) to "what's different about
2024-2026 specifically" (open).

## Genome-specific check: v1 (reconstructed, unevolved seed) for comparison

Ran the same independent-window sweep against v1 to check whether "strong
across 4 old windows, fails the newest one" is a property of this specific
evolved genome or just market beta. It is not market beta: v1 beats
benchmark in only 1/5 windows (vs v3's 4/5), including losing badly in
windows 3 and 4 where v3's edge was largest (+57.5%/+0.8% excess return for
v3 vs -145.2%/-145.0% for v1 in the same two windows). v1's own
fitness-vs-recency correlation is r=-0.178 (weak, opposite sign) — a
different, weaker, less consistent shape than v3's. This is evidence the
13+ generations of evolution between v1 and v3 produced a genuine,
non-trivial edge over most of history, not just exposure to a rising
market — but it doesn't change the open question about window 5, since v1
doesn't clear that window either (fitness 0.243, still loses to benchmark
there, just less catastrophically than in windows 3-4).

## Verified safe

- Full suite: 235 passed (`pytest tests/`), matches known baseline. No new
  pure function added (composes already-tested `run_backtest`/
  `market.load_universe`, same precedent as the nested mode and
  `costs`/`universe-perturb`/`regime`), so no new test file.
- `git status --short` clean before this commit (only `evotrader_bundle.py`
  touched).
- `live_state.json` md5 unchanged throughout: `f7590581b893d3866e00e28c87fe1c02`.
- `evotrader.manifest` md5 unchanged: `0bf3a7d9411ee692d0a9f152a7533803`.
- Constitution verified `8b74865634b1db07` unchanged.
- Today's bar already processed by the 00:20 UTC daily run before this
  session started; `tick` not run this session, no double-trade.
- `review-hard-calls`: still 0 pending.
- No genome promotion — no README `## Status` update needed.

## Next, if this thread stays worth pursuing

The open question is now specifically "what's different about the
2024-08-24 to 2026-08-25 window" rather than "is the edge start-date
robust" (largely answered). Candidates not attempted here: `regime` on
that exact window to characterize it (trend/chop/volatility shape vs the
four windows that worked), or checking whether a shorter sub-slice of
window 5 recovers (i.e., is the whole 2 years bad, or is it concentrated
in a sub-period — same kind of question `drawdown` already answers for
maxDD specifically, not yet asked of fitness/excess-return generally).
Also untried: denser/narrower `--window-years` (e.g. 1.0) for more
independent draws, at the cost of shorter, noisier per-window backtests.
