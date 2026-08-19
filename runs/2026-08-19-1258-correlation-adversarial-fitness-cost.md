# Adversarial-concentration genome: does its measured concentration cost fitness/drawdown?

3-hourly check. Follow-up to `runs/2026-08-19-0951-correlation-adversarial-genome.md`,
which built `_adversarial_concentration_genome` and measured that it concentrates
held-set correlation toward universe-wide in fold 3/holdout, but explicitly left
open whether that concentration costs anything as a trading candidate — it had
only ever been evaluated for correlation structure, never run through `stats()`/
`fitness()`. This closes that gap.

## What changed

`correlation-universe --realized` already runs one full-history `run_backtest()`
per genome (needed to reconstruct `holding_mask`) — `result['stats']`,
`result['fitness']`, and `result['edge']` were already sitting in the return
value, just never printed. Added one print block per genome, right after the
existing backtest call, no new backtest run, no new function:

```
full-history: return +580.6%  sortino +2.15  maxDD -34.1%  trades 1165  fitness +0.744  vs b&h +507.6% (beats benchmark)
```

Purely additive CLI output. `py_compile` clean, full suite still 104 passed (no
new tests needed — this only prints already-computed, already-tested values from
`run_backtest`, same bar the `--realized`/`--also-version`/`--adversarial` glue
itself was held to).

## Result

Ran `correlation-universe --realized --adversarial` (full history, live v3 vs
the adversarial-concentration genome from the 09:51 run):

| genome | return | sortino | maxDD | trades | fitness | vs b&h |
|---|---|---|---|---|---|---|
| v3 (live) | +580.6% | +2.15 | **-34.1%** | 1165 | **+0.744** | +507.6% (beats) |
| adversarial-concentration | +163.3% | +0.94 | **-52.6%** | 2339 | **-inf** | +90.3% (beats) |

The adversarial genome's `fitness = -inf` because `-52.6%` maxDD crosses the
constitution's `MAX_DD_HARD_FAIL` (40%) — the same hard-fail gate the
2026-08-16 cost-sensitivity run flagged v3 crossing at a 1.5x cost multiplier.
Sortino roughly halves (2.15 → 0.94) and trade count doubles (1165 → 2339, the
loosened entry gates trading far more often for a worse per-trade outcome). It
still nominally "beats benchmark" on raw return (this genome's buy-and-hold
comparison basket also crashed harder over the same held-symbol set — `vs b&h`
is a relative number, not a pass), but it would fail the hard drawdown gate
outright and never reach a holdout check in real search.

## Reading this against item 3

This is the piece the 09:51 run explicitly left open, and it changes the
interpretation more than it changes the recommendation. Previously: "ordinary
fitness-driven selectivity happens to keep held sets less correlated as an
incidental byproduct." Now: it isn't incidental — the same genome that
concentrates exposure (loosened selectivity, no correlation awareness) also
blows through the drawdown hard-fail gate and gets a fitness of `-inf`. The
`MAX_DD_HARD_FAIL`/`MIN_TRADES` gates plus ordinary Sortino-shaped fitness
already select against exactly the kind of unselective, concentrated trading a
`correlation_penalty`-style mechanism would also police — not as a
correlation-aware mechanism, but because concentrated exposure and poor risk
control tend to travel together in this system's actual candidate space. This
strengthens the case that `correlation_penalty`/`correlation_lookback`/
`_correlation_scale` are dead weight given the gates already in place, not
just unused so far.

Caveat: this is still one adversarial construction (blanket-loosened
selectivity), not a genome that concentrates exposure *without* also failing
other gates — e.g. a genome with tight selectivity per-symbol but no
diversification requirement, which might concentrate without necessarily
trading more or drawing down harder. Not constructed or tested this run.

## Verified safe

- Purely additive: new print statements only, no new function, no constitution
  or `core.portfolio`/`agents.judges` change (neither checksummed set touched).
- `py_compile evotrader_bundle.py` clean.
- Full suite: 104 passed (unchanged from before this run).
- `live_state.json` md5 identical before/after: `09c35b692da1d694c5a3cace5d488f40`.
- `git status --short` clean of anything but the `evotrader_bundle.py` diff.
- `constitution verified dfae6a697f51fb49` printed and unchanged throughout.
- Today's 2026-08-18 bar (tick 5) confirmed already processed by the 00:20 UTC
  daily run before this check started (`live_state.json`'s `updated` timestamp
  `2026-08-19T00:21:55+00:00` predates this session; `tick` not run this
  session, no double-trade risk).

## Next

Item 3's open question is now down to a narrower one: whether a genome that
concentrates exposure *without* also failing the drawdown/trade-count gates is
constructible — if fitness-driven selection reliably catches concentration as
a side effect of catching bad risk control generally, "drop the line" gets
stronger; if a gate-passing-but-concentrated genome can be built, that would
be the first real case *for* keeping `correlation_penalty` active. Also still
open from the 09:51 run: a sector/theme-targeted adversarial genome instead of
blanket-loosened selectivity, which might concentrate harder while staying
inside the hard gates.
