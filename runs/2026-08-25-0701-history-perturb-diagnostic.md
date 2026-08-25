# `history-perturb`: the start-date leg of the fees/slippage/universe/start-date perturbation checklist

**3-hourly self-improvement check, ~07:00 UTC.**

## Why

The 2026-08-16 "Measured — read before proposing more genes" note named
"perturbation tests on fees/slippage/universe/start-date" as the preferred
kind of evidence over new capability. `costs` (2026-08-16) covers
fees/slippage. `universe-perturb` (2026-08-21) covers universe composition.
Start-date had never been tested — and it's a different question from the
fold-windowing/holdout-margin thread (which tests different ways of slicing
a *fixed* 4-year window and was set aside as exhausted on 2026-08-21): this
asks whether the champion's edge over benchmark holds if the backtest had
started from a genuinely different calendar date.

## What shipped

New read-only CLI `evotrader_bundle.py history-perturb [--years
Y1,Y2,...] [--also-version N]`. Same guarantees as `costs`/
`universe-perturb`: one real `run_backtest` per scenario, never touches
`live_state.json` or the champion. Default scenario list: 2/3/4/5/6 years
of lookback, all ending "now".

## A real bug caught before shipping

The first draft passed `years` straight through to
`core.market.load_universe(..., years)`. That's wrong:
`core.market.load()`'s docstring says "the cache only ever grows" — it
fetches more history if the cache doesn't cover the requested `years`, but
it **never trims** the returned frame down to that window. So once the
on-disk cache holds 4 years (which it does after almost any other
diagnostic runs), asking for `years=2` or `years=3` silently returns the
same 4-year frame as `years=4`.

Confirmed directly with a throwaway script:

```
>>> market.load('BTCUSDT', '1d', 2.0)   # after cache already held 4y
n=1461 start=2022-08-26 end=2026-08-25
>>> market.load('BTCUSDT', '1d', 4.0)
n=1461 start=2022-08-26 end=2026-08-25   # identical
>>> market.load('BTCUSDT', '1d', 6.0)
n=2192 start=2020-08-25 end=2026-08-25   # only this one actually changed
```

A first version of this diagnostic ran with this bug and printed three rows
that all shared the same `window start` field — the tell that gave it away
(the value only reflects `replay`'s slice-after-warmup index, not the raw
loaded range, so it silently repeated across "different" scenarios instead
of erroring).

**Fix**: load once at `max(years_list)` (extending the cache if needed),
then explicitly truncate each symbol's frame to `[now - years, now]` before
each backtest — independent of whatever the shared on-disk cache holds.
This is a property of the diagnostic script, not a fix to
`core.market.load()` itself; that function's cache-only-grows contract is
correct and deliberate for its actual callers (`tick`, `evolve`, every
other diagnostic), which always want "at least N years," not "exactly N
years."

## Result (champion v3, live)

| years back | window start | fitness | return | sharpe | maxDD | trades | excess return | beats benchmark |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 2.0 | 2024-10-24 | -inf (hard-fail) | +37.6% | 0.64 | -45.0% | 603 | -40.6% | **False** |
| 4.0 | 2022-10-25 | -inf (hard-fail) | +190.6% | 0.87 | -46.5% | 1087 | +78.7% | True |
| 6.0 | 2020-10-24 | -3.161 | +3701.6% | 1.52 | -39.3% | 1946 | +3065.1% | True |

(All three currently hard-fail or score deeply negative on the dd-corrected
`MAX_DD_HARD_FAIL` gate the way live champion v3 already does post the
2026-08-22 fix — see AGENTS.md's "Current state" for that background. The
finding here is about the *relative* shape across windows, not about
whether v3 would pass `accepts()` today, which is already a known,
separately-tracked condition.)

**Reading**: over just the most recent 2 years, the champion actually loses
to a passive buy-and-hold basket. Over 4 and 6 years it wins, and wins by a
large and growing margin. That's the opposite of "recent data looks better"
— the edge is concentrated in the older part of the window, not the recent
part, which cuts against the naive "the champion overfit to a recent bull
run" worry, but doesn't answer why 2y alone looks bad. First measurement,
not a settled read: n=3, and all three windows are nested (they share the
same recent 2 years), so this can't yet distinguish "genuinely start-date
robust" from "one shared recent stretch is a genuine headwind that a longer
window's older gains simply outweigh."

## Verified safe

- Full suite: 235 passed (`pytest tests/`), matches known baseline, no new
  pure function added so no new test file (same precedent as
  `costs`/`universe-perturb`/`regime`).
- `git status --short` clean before this commit.
- `live_state.json` md5 unchanged throughout: `f7590581b893d3866e00e28c87fe1c02`.
- `evotrader.manifest` md5 unchanged: `0bf3a7d9411ee692d0a9f152a7533803`.
- Constitution verified `8b74865634b1db07` unchanged.
- Today's bar already processed by the 00:20 UTC daily run before this
  session started; `tick` not run this session, no double-trade.
- `review-hard-calls`: still 0 pending.
- No genome promotion — no README `## Status` update needed.

## Next, if this thread stays worth pursuing

More/denser `--years` points, or — sharper — independent, non-overlapping
windows instead of nested ones that all share the same recent history, to
tell "recent regime happens to be a genuine headwind for this genome" apart
from a real overfitting story. Not attempted this session (time-boxed to
shipping a working, verified diagnostic plus one real finding).
