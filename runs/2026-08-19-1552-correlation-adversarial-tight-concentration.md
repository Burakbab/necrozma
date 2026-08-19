# Correlation-universe: a second adversarial genome, selectivity untouched

3-hourly self-improvement check, 2026-08-19 ~15:47 UTC.

## Context

AGENTS.md item 3's correlation question has been narrowed repeatedly today.
The 09:51 run's `_adversarial_concentration_genome` was the first construction
whose held-set correlation approached universe-wide, but it did so by loosening
every consult's entry gate to near pass-through. The 12:58 run then showed that
genome also crosses `MAX_DD_HARD_FAIL` (maxDD -52.6%, fitness -inf) — so the
open question left standing was: does concentration *require* losing
selectivity to show up, or can a genome concentrate while keeping entry gates
exactly as tight as the champion's own tuning? That's the one case that would
argue for keeping `correlation_penalty` as a real safety valve rather than
dead weight.

## What was built

`_adversarial_concentration_genome_tight(base)` in `evotrader_bundle.py`
(next to the existing `_adversarial_concentration_genome`): patches only
`agents.risk_judge.genes.max_positions` (6→3), `max_position_pct` (0.25→0.9),
`cash_floor_pct` (0.3503→0.05), `correlation_penalty` (explicit 0.0, same as
every real champion), and the matching `agents.superior_judge.genes`
ceilings (`hard_max_positions` 8→3, `hard_max_position_pct` 0.35→0.9,
`hard_cash_floor_pct` 0.02→0.02 unchanged). **No consult gene is touched at
all** — every entry filter (RSI bands, trend/breakout/momentum thresholds,
volatility caps) stays exactly as v3's own evolution tuned it. The only lever
pulled is "fewer, much larger simultaneous positions" — forcing concentration
through position-count/sizing limits alone, not through indiscriminate entry.

Wired into `correlation-universe --realized` as a new `--adversarial-tight`
flag, same machinery as `--also-version`/`--adversarial`.

One false start caught before the real run: `max_positions=2` compiles and
runs fine but produces **zero** held-only correlation rows in every window
("need >=3 held symbols") — `pairwise_correlation_stats` requires at least 3
simultaneously-held symbols to report anything, and a 2-slot cap can never
reach 3. Bumped to `max_positions=3` (still a real concentration forcing
function vs. the champion's 6 slots) before the measurement became meaningful.
Left as a docstring note so the next person doesn't repeat it.

## Result

Full-history real backtest, `adversarial-concentration-tight` vs champion v3:

| | v3 (live) | adversarial-tight |
|---|---|---|
| return | +606.2% | +214.5% |
| sortino | +2.18 | +1.12 |
| maxDD | -34.1% | **-57.5%** |
| trades | 1165 | 560 |
| fitness | +0.780 | **-inf** |

Held-only mean correlation by window (v3 vs adversarial-tight vs universe-wide):

| window | v3 held-only | tight held-only | universe-wide |
|---|---|---|---|
| fold 1 | +0.523 | +0.536 | +0.630 |
| fold 2 | +0.470 | **+0.561** | +0.509 |
| fold 3 | +0.427 | +0.527 | +0.616 |
| holdout | +0.437 | +0.514 | +0.578 |

Two things worth separating:

1. **This is the first genome, of any construction tried, whose held-set
   correlation exceeds universe-wide in a real window** (fold 2: +0.561 vs
   +0.509) — not just "approaches" it, as the loosened-gates adversarial
   genome did. Concentration *is* achievable while leaving selectivity fully
   intact; it just takes forcing it through position-count/sizing, not gate
   loosening.
2. **It still fails the same hard-fail gate the loosened-gates genome
   failed, and worse** (-57.5% vs -52.6%). Selectivity being untouched didn't
   protect it — three much-larger, much-less-diversified bets drawdown harder
   than the champion's six moderate ones, independent of entry quality.

## Reading against item 3

This closes the narrower open question from a second, independent angle: not
just "a genome that loosens selectivity to concentrate also blows the
drawdown gate" (09:51/12:58 runs), but "a genome that keeps selectivity fully
intact and concentrates *only* through fewer/larger positions also blows the
drawdown gate, and does so more severely." Two structurally different ways of
reaching concentration, same outcome. This is the strongest evidence yet that
`MAX_DD_HARD_FAIL`/Sortino-shaped fitness already select against concentrated
trading in this system's actual candidate space as a side effect — not a
property of one adversarial recipe. The honest remaining gap: both
constructions here are hand-built single genomes, never run through real
search/evolution, so "no real *searched* candidate would ever ship
concentrated" is still inferred, not demonstrated by a real promotion
attempt.

## Verification

- Purely additive: one new function + one new CLI flag, no existing code path
  changed.
- `py_compile evotrader_bundle.py` clean.
- Full suite: 104 passed (unchanged — no new tests, same bar the existing
  `_adversarial_concentration_genome`/`--adversarial` diagnostic was held to:
  print-only CLI glue over already-tested functions).
- `live_state.json` md5 identical before/after: `09c35b692da1d694c5a3cace5d488f40`.
- `evotrader.manifest` md5 identical: `6a4434574ff424f74ff300ebdb50d194`.
- `git status --short` clean of anything but the `evotrader_bundle.py` diff.
- `constitution verified dfae6a697f51fb49` unchanged throughout.
- Today's 2026-08-18 bar (tick 5) confirmed already processed by the 00:20
  UTC daily run before this check started — `tick` still correctly reports
  "already traded", no double-trade.

## Next

- The remaining honest gap named above: run this tight-concentration
  construction (or something like it) through real `evolve` search rather
  than hand-building it, to check whether search itself would ever wander
  toward this region before the drawdown gate kills it — not attempted this
  run (bigger scope, a real search cycle rather than one hand-built genome).
- Item 3's decision (drop `correlation_penalty`/`correlation_lookback`/
  `_correlation_scale` vs. keep as an unused safety valve) now has its
  strongest evidence base yet: 4 real champions + 2 independent adversarial
  constructions, all consistent. If this item is ever revisited to actually
  act, this is enough to decide on rather than another read.
