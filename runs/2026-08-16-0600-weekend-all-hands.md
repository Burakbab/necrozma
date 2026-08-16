# Weekend all-hands — 2026-08-16 ~06:00 UTC

Scheduled weekend session (Saturdays/Sundays, deeper focus than the 3-hourly
check). No trade was due this cycle — the 00:20 UTC daily run already handled
today's bar. Spent the full slot on Next-steps items 2 and 3a: get more
generations of real search against the live champion, and settle the "is v2
measurably behind" question one way or the other instead of leaving it as an
open flag for a future session to pick up.

## Headline: the live account self-promoted v2 -> v3, fitness 0.682 -> 1.389

Two real `evotrader_bundle.py evolve` invocations ran against the actual
`live_state.json` this session (not a shadow copy):

**Round 1** — `evolve 8`. No promotion. Cumulative candidates tested against
v2 rose from 138 to 252; best per-generation fold-aggregate fitness ranged
0.49-0.78, short of the ~0.95 bar the multiple-testing margin now demands at
that cumulative count. Committed anyway (`c58d747`) — the researcher-memory
update (which candidates are excluded from re-testing) is real progress even
without a promotion, and losing it would mean generation 1 of the next run
re-discovers the same 252 dead ends.

**Round 2** — `evolve 15`, continuing from the same point. Generation 6
found a real one: fold-aggregate fitness 0.682 -> 1.389, merged fitness
0.805 -> 1.591 (no regression), drawdown 32.6% (within the 15% regression
tolerance on v2's ~30% baseline), and it **beat the sealed holdout and
buy-and-hold both** — holdout excess return +21.7%, excess Sharpe +0.44,
drawdown 16.0 points better than benchmark in that window. 9 more
generations after that found nothing further (best candidate 1.98 against
a champion now sitting at 1.389). Committed as `35afb01`.

The accepted patch touches 13 genes across almost every agent — this was not
a one-line tune:

| gene | v2 | v3 |
|---|---|---|
| `risk.stop_loss` | −0.12 | −0.3364 |
| `risk.trailing_stop` | −0.15 | −0.1993 |
| `risk.max_bars_held` | 60 | 15 |
| `consult_risky.min_rank_mom` | 0.7 | 0.3 |
| `analyst.rsi_len` | 14 | 31 |
| `analyst.regime_ma` | 50 | 49 |
| `consult_moderate.rsi_lo` | 35.18 | 25.0 |
| `consult_conservative.z_buy_below` | −0.8 | −0.5876 |
| `consult_conservative.max_dd_from_high` | −0.35 | −0.2638 |
| `consult_conservative.exit_rsi` | 68.0 | 77.1724 |
| `risk_judge.lone_voice_scale` | 0.6 | 1.4791 |
| `risk_judge.cash_floor_pct` | 0.05 | 0.3503 |
| `risk_judge.base_size_pct` | 0.12 | 0.2392 |

Read this the way `AGENTS.md`'s "Measured 2026-08-16" section asks: this is a
gate-passing, holdout-confirmed improvement over v2, not proof the policy
beats doing nothing overall — `edge_vs_benchmark()` is reported, not
optimised, and buy-and-hold still needs checking on the full replay before
this gets called more than "less wrong than v2." The genome swap is
forward-looking only — it changes what the account decides on the next tick,
it does not touch the open positions or trade history booked under v2.

Dashboard rebuilt for v3 and pushed (`0e6bc21`).

### Why this matters beyond one promotion

`AGENTS.md` flagged on 2026-08-16 that a shadow run using this same
champion, same data, same accumulated researcher-memory had independently
found a real v2->v3->v4 improvement (fitness up to 2.461) that was
deliberately never applied live, and asked whether "the daily run's own
`evolve` may or may not stumble onto this same combination." Round 2 answers
that directly: yes, given enough generations (15, this time), honest search
against the real account does find a comparable-magnitude improvement on its
own — a different specific gene combination, similar magnitude jump
(1.39x vs the shadow's 3.6x), same overall story of "v2 was a weak
plateau." No hand-tuned patch was spliced in from the shadow run; this is
the account's own search, its own holdout draw, its own audit trail.

## Item 2 (4h bars): two more shadow data points, one of them a mistake worth logging

### A mistake, caught and logged rather than hidden

While setting up an isolated scratch copy for a 4h-bar shadow run, the
initial `cp -r` of the repo into scratch carried over the *real*
`live_state.json` (champion v2, 1d bars). The scaled 4h seed genome was
written to `state/genomes/champion.json` in that scratch dir, but
`evotrader_bundle.py`'s `LiveAccount.load()` reads the genome straight out of
`live_state.json` when that file exists and only falls back to
`Genome.champion()` (which would have picked up the 4h seed) when it
doesn't — so this run silently evolved the real 1d champion a third time
instead of a 4h genome. Caught by checking the log header
(`champion v2 (1d bars)`, not the expected `v1 (4h bars)`) before trusting
the result.

That accidental run is not worthless — it is a *third* independent, honestly
randomized blind-search draw against the exact same real v2 starting point
(same 1d data, same pre-session researcher-memory), isolated in scratch so
it never touched the real account. It found its own two-step promotion:
v2 -> v3 (fitness 0.682 -> 1.072, patch centred on `exit_rsi`/`max_vol`/
`min_breakout`/`base_size_pct`/`cash_floor_pct`) -> v4 (1.072 -> 1.818,
`rsi_len` 14->23, `take_profit` 0.35->0.2897), both holdout-confirmed in
that isolated copy. Three independent draws now (the 00:59 UTC shadow run,
this one, and the real round 2 above) have each found a real, gate-passing,
holdout-passing improvement over v2 somewhere in the 1.4x-3.6x fitness
range, via three different specific gene combinations. That consistency is
the useful signal — v2 was a genuine local plateau, not a hard ceiling, and
this is now confirmed four separate ways counting the live promotion. This
scratch run and its artifacts were not committed anywhere; the fix (moving
the mislabeled attempt aside, rebuilding scratch cleanly, verifying the log
header says `v1 (4h bars)` before backgrounding) is recorded here so the
next session doesn't repeat it. `evolve` invoked with `EVO_STATE` pointed
at a scratch path still needs its *whole* directory to be scratch, including
`live_state.json` itself, not just the state it's told to write to.

### The corrected 4h run: still evolvable, still slow

Fixed setup, re-verified (`champion v1 (4h bars)` in the log header, genome
version 1, note confirming the x6-scaled bar-count genes), then
`EVO_STATE=... evolve 8` from the clean scratch dir. Generation 1 (27
proposals, `n_blind=14` default) found a promotion in one shot: fitness
−2.374 -> 0.469 (`breakout_len` 120->46, `max_position_pct` 0.25->0.34,
drawdown 40.0%, right at the hard-fail line but passing as a *champion*
comparison point, not gated the way a challenger would be). Generation 2
found nothing better (best candidate 0.666 vs champion 0.469) and held.

Stopped partway into generation 3 and killed the process — at this
`n_blind` and bar count, each generation was taking ~25-27 minutes (a 4h
backtest fold now walks ~6.3x as many bars as 1d), so the requested 8
generations would have run 3+ hours, well past what this slot should spend
on one open question. `n_blind=10` (used in the earlier successful 4h run)
or fewer generations per invocation is the right default for future 4h
shadow work — 14 blind proposals per generation is calibrated for 1d
backtest cost, not 4h.

Combined with the earlier 2026-08-16-0000 run (hand-scaled seed reaching
fitness 0.81 in 2 generations, then also finding nothing further) and
today's 2 generations (fitness 0.47, weaker magnitude but the same
qualitative shape: catastrophic unscaled seed -> workable after x6 scaling
-> a first-generation promotion -> quick stagnation), the pattern holds
across three separate scaled-seed 4h runs now: **x6-scaling the bar-count
genes reliably turns "every candidate fails a hard gate" into "evolvable and
improvable," but the specific fitness reached in 1-2 generations varies by
random draw** (0.47 here, 0.81 in the first run) the same way 1d search
varies. Not yet resolved: whether continued 4h search converges toward the
live 1d champion's neighbourhood or a genuinely different regime — that
needs a run with a much smaller `n_blind` (5-8) or fewer generations
prioritised over more proposals per generation, given the per-generation
cost at this bar size.

## Time budget

~1h45m total. ~18 min real `evolve 8` (round 1), ~31 min real `evolve 15`
(round 2, found the v3 promotion), ~13 min mislabeled 4h attempt (actually
1d, cheap because 1d data was already cached), ~56 min corrected 4h attempt
(2 generations before being stopped on time). Two commits carry real state
changes (round 1's researcher-memory update, round 2's v3 promotion) plus
the dashboard rebuild; the two 4h shadow runs and the mislabeled run stayed
entirely in `/tmp` scratch and touched nothing in the repo.

## Decisions made this session

1. **Applied**: v2 -> v3 promotion, found by the live account's own honest
   search. No shadow-run patch was hand-copied into `live_state.json` —
   that would have laundered a result found under one set of gate draws
   into an account that hadn't actually spent them, which is exactly the
   kind of validation-mining the sealed-holdout multiple-testing margin
   exists to catch (see `AMENDMENTS.md`'s 2026-08-16 entry). Letting the
   real account run its own search for real, even though it took two
   invocations and ~50 minutes, keeps the promotion honest.
2. **Not applied**: the shadow-found v4 candidates from either the 00:59 UTC
   run or this session's mislabeled attempt. Both are real, holdout-passing
   results, but in an isolated copy with its own holdout-draw count — using
   them would require deciding how to honestly merge that draw history into
   the live account's `researcher_memory`, which is more surgery than this
   session had grounds to justify given the real account found its own
   promotion anyway.
3. **Stopped early**: the corrected 4h run, on a time-budget call, not a
   result call — logged as an open item with a concrete fix (`n_blind`
   too high for this bar size) rather than left to silently time out.
