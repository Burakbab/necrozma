# The real evolve() fold-aggregate fitness is date-sensitive too, not just the diagnostic

**3-hourly self-improvement check, ~12:57 UTC.**

## Why

Today's bar (2026-08-26) was already traded by the dedicated 00:20 UTC daily
run before this session started (`live_state.json` `updated`
`2026-08-26T00:22:17+00:00`) — nothing to do on the trading side. Picked up
the framing question the 09:50 UTC entry raised and flagged as able to
"resolve the whole thread without further diagnostics": the day-1
greedy-cash-allocation boundary-shift artifact traced across windows 3 and 5
lives entirely inside `history-perturb`'s own hand-rolled
`run_backtest(genome, data, 0.0, 1.0)` sweep — never the real
`loop.evolve.Evaluator` fold scheme `evolve` actually uses for promotion
decisions. But `evolve`'s own `market.load_universe(g0.universe,
g0.bar_interval, 4.0)` call always loads a trailing 4-year window ending
"now" — so every real `evolve` invocation implicitly redraws its own fold
boundaries by however many days have passed since the last invocation. That
means the question isn't hypothetical: it's checkable directly against the
real machinery.

## What happened

Shipped `fold-date-sensitivity [--shift N] [--also-version N]` (same
file/precedent as `fold-scheme`: CLI-only code in `main()`, not part of the
unflattened `_SRC` modules, no new pure function so no new test file).
Re-evaluates a champion under the exact same `Evaluator(data,
n_folds=N_FOLDS).evaluate(genome)` call `evolve` makes internally, at
`--shift` (default 7) different "as-of" dates walking back from today, each
with its own trailing 4-year window computed the same way `load_universe`
computes it live. Read-only: never touches `live_state.json` or the
champion.

```
python3 evotrader_bundle.py fold-date-sensitivity --shift 7
```

## Result

```
FOLD-DATE SENSITIVITY -- v3 (live) (n_folds=3, holdout_frac=0.15, trailing 4y window, 'now' walked back 0-6 days)
   shift        as-of window start  aggregate_fitness  fold fitnesses
       0   2026-08-26   2022-08-26             -1.652  [0.054, 3.759, -5.000]
       1   2026-08-25   2022-08-25              0.843  [0.028, 4.027, 0.374]
       2   2026-08-24   2022-08-24              1.245  [-0.013, 4.002, 1.486]
       3   2026-08-23   2022-08-23              0.919  [0.043, 3.277, 0.878]
       4   2026-08-22   2022-08-22              1.126  [-0.201, 4.529, 1.141]
       5   2026-08-21   2022-08-21              1.396  [1.063, 4.436, 0.512]
       6   2026-08-20   2022-08-20              1.480  [1.212, 4.390, 0.586]

  -> 7/7 finite, aggregate_fitness range [-1.652, 1.480] (spread 3.132) across a 7-day 'as-of' window
```

If `evolve` were run today (shift 0), the live champion's own re-evaluation
against its real fold scheme would show fold 3 hard-failing outright
(`-5.000` = `RANK_FLOOR`, the floor `evaluate()` applies to an `-inf`
fitness) — one day earlier or later and fold 3 is solidly positive
(0.028–1.212). `aggregate_fitness` itself swings from -1.652 to +1.480, a
3.1-point spread, purely from which calendar day the evaluation ran on.

Checked and ruled out one confound before trusting this: `load_universe`
called "now" mid-day returns today's still-forming daily bar as the last
row (volume ~7.4k vs ~25-30k on the two prior closed days — verified
directly). Re-ran shift 0 with that forming bar explicitly dropped before
evaluation — identical result to five decimal places (`agg=
-1.652085716126818` both ways). The hard-fail is not a partial-candle
artifact; it is the same day-1 boundary mechanism the 06:55/09:50 UTC
entries traced (a one-day shift changes every asset's rolling-indicator
values at each fold's start, and `risk_judge`'s greedy hard-capped cash
allocation lets whichever symbols cross the entry threshold first claim the
funding), now confirmed against the real `Evaluator` fold scheme instead of
the diagnostic's own independent-window replay.

## Reading

Answers the framing question directly, and not the way "backtest-evaluation
artifact, not a live-trading risk" would have hoped: **this has real
live-trading relevance.** The live account's own order execution never
re-draws its "day 1" — that part of the original framing still holds — but
`evolve`'s promotion-gating fold-aggregate fitness is recomputed fresh
against a trailing-4y-ending-now window on every real invocation, and this
result shows that number can swing by 3+ fitness points and cross the hard
drawdown-fail gate outright depending on which day the call happens to run.
Concretely: the champion's own re-evaluation would have hard-failed one of
its three search folds today specifically, while looking comfortably
positive on six of the last seven days. This is not about promotion
correctness in the way the sealed-holdout/multiple-testing machinery
guards against (a challenger beating the champion by luck) — it's a new,
distinct source of noise in the champion's *own* fold-aggregate signal, and
by extension in `accepts()`'s champion-relative regression checks, which
compare a challenger against whatever the champion's fold-aggregate happens
to read on the day `evolve` is called.

## Verified safe

- Full suite 235 passed (133.12s, matches baseline, no new test file per the
  no-new-pure-function precedent — same as `fold-scheme`/`history-perturb`).
- `tools/edit_bundle_module.py sync --check` reports no drift (this
  CLI-dispatch code isn't part of the unflattened `_SRC` modules).
- `git status --short` shows only `evotrader_bundle.py` modified.
- `live_state.json` untouched: md5 `1441d25f45fb4a927f993cbc8c505a5b`
  (unchanged from the 09:50 UTC entry), still reflects tick 12 from the
  00:20 UTC daily run.
- `evotrader.manifest` md5 unchanged: `0bf3a7d9411ee692d0a9f152a7533803`.
- Constitution verified `8b74865634b1db07` unchanged.
- Today's bar already processed before this session started (no double-trade).
- No genome promotion — no README `## Status` update needed.

## Confirmed mechanism: `accepts()`'s champion baseline is freshly recomputed, not read from storage

Checked directly rather than left as a guess: `loop.evolve.EvolutionRun.
generation()` (lines 542-543) computes `champ_fit =
self.evaluator.evaluate(champion)["aggregate_fitness"]` **fresh, every
single `generation()` call**, on `self.data` — the same trailing-4y-ending-
"now" data this diagnostic reproduces. That `champ_fit` is passed straight
into `accepts()` as `champion_score` (line 621), which is exactly the
number the required-margin comparison (`s_chal <= s_champ + margin`) is
measured against. It is *not* read from `live_state.json`'s stored
promotion-time fitness. So the swing this session measured isn't a
side-channel curiosity — it directly moves the bar every real challenger
must clear on whatever day `evolve` happens to run: a day when the
champion's own re-evaluation craters (like today) lowers the bar for a
mediocre challenger to look like it "beat" the champion; a day when the
champion's re-evaluation is unusually strong raises the bar and could sink
a genuinely-improved challenger's fold-aggregate comparison. (The
sealed-holdout gate downstream still has its own independent check, so this
is not necessarily enough on its own to let a bad challenger all the way to
promotion — but it is a real, previously-uncharacterized source of noise in
which challengers even reach that gate.)

## Next, if this thread stays worth pursuing

The open items from the 09:50 UTC entry (window-5 `anatomy` post-mortem;
whether a day-1 allocation redesign — proportional/ranked instead of
greedy-first-come — is worth attempting) are still open. Sharper now:
whether this date-sensitivity measurably changes which challengers clear
`accepts()` in practice — e.g. replaying a real historical `evolve`
generation's candidate batch against the champion re-evaluated at a
different `--shift` value and checking whether the accept/reject verdict on
any borderline candidate flips — not attempted this session, would need its
own session. `fold-date-sensitivity --also-version N` (same flag convention
as `fold-scheme`) is a one-line follow-up to see whether this swing is
v3-specific or general across champions — not run yet, would need its own
session given the ~30-60s-per-shift cost already spent this session's time
budget on `--shift 7`.
