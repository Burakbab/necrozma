# Universe-perturbation diagnostic — 2026-08-21 19:02 UTC (3-hourly check)

## Why

AGENTS.md's 2026-08-16 "read before proposing more genes" note named
"perturbation tests on fees/slippage/universe/start-date" and "convergence
across independent seeds" as the preferred kind of evidence to produce, over
adding capability. `costs` already covers fees/slippage. Nothing had ever
covered universe composition — a gap, and a genuinely untried angle rather
than a fifth variant on the fold-windowing/holdout-margin thread the last six
3-hourly runs today have been working (that thread's own last two entries
independently recommended treating it as exhausted for now).

The seed genome's own comments make two testable claims about the universe
that had never actually been tested: "more symbols -> more trades -> a
tighter estimate" and PAXG is "deliberately included as a non-crypto-
correlated asset." Universe composition is also confirmed (`grep` over
`agents.researcher`'s `GENE_SPACE`) to be a structural constant, never a
Researcher-mutable gene — identical across all three real champions this
account has ever had, so a finding here is a property of the system's design,
not of any one evolved genome.

## What shipped

New read-only CLI `universe-perturb [--drop-frac F] [--n-trials N] [--seed S]
[--drop SYM1,SYM2,...] [--holdout] [--also-version N]` in the plain-script
CLI section of `evotrader_bundle.py` (no `_SRC` module touched, nothing
checksummed). Same guarantees as `costs`: one real `run_backtest` call per
scenario against the champion's own genome/broker config, `data` loaded once
for the full universe and subsetted per scenario (`run_backtest` already
intersects `data.keys()` with `genome.universe`, so no engine change needed),
benchmark buy-and-hold is recomputed per scenario over the same subset
(`benchmark_buy_hold(replay, genome.universe, ...)` already keys off the
genome passed in) — so every "excess_return"/"beat_benchmark" comparison
stays fair against the same universe it was run on, not the full 27-symbol
benchmark. Never touches `live_state.json` or the champion.

Default scenario set: baseline (full universe), "drop PAXG only" (the
targeted test of the seed comment's claim), then `--n-trials` (default 6)
random drops of `--drop-frac` (default 20%, ~5 of 27 symbols) with a fixed
seed for reproducibility. `--drop` overrides with one explicit comma-list
scenario. Prints maxDD/trades per scenario (not just fitness) specifically so
a `-inf` result is interpretable instead of an opaque "hard fail" — and it
mattered immediately, see below. No new pure function added anywhere
(`loop.evolve`/`core`/`constitution` untouched) — composes only already-
tested `run_backtest`/`Genome`/`edge_vs_benchmark`, same as `costs`/`regime`/
`margin-curve`, so no new test file, consistent with that precedent. Full
suite still 179 passed.

## Result

**Full history, champion v3 (live):** baseline (27 symbols) fitness 0.876,
maxDD -34.1%. Dropping PAXG alone costs -0.236 fitness (0.640) — a real,
non-trivial cost, the opposite of "dead weight" (unlike `correlation_penalty`,
item 3, which measured as a genuine no-op before removal). 6 random 5-symbol
drops (seed 0): fitness ranged 0.640-0.830 among the 5 that stayed finite,
but **2 of 6 hit the MAX_DD_HARD_FAIL gate outright** (-inf fitness) — not
because the strategy stopped working (both hard-fail scenarios still beat
benchmark, excess_return +51.2% and +119.1%) but because maxDD crossed 40%
(43.7%, 44.2%) against baseline's own 34.1%. The champion's drawdown margin
to its own hard-fail gate is thin enough that losing a random ~fifth of the
universe — no adversarial selection, no signal degradation implied by the
still-positive excess returns — can flip a scenario from "fine, beats
benchmark" straight to a hard rejection purely through the drawdown channel.
This is a new, mechanistic, and slightly uncomfortable finding: fitness
under `universe-perturb` is not a smooth function of universe composition
near this champion's current operating point, it has a cliff.

**Sealed holdout, v3:** no hard-fails in this smaller window (maxDD stayed
under 36% in all 7 scenarios), but fitness still swings hard: baseline
-0.478, range -2.583 to -0.432 across the 7 scenarios — a swing of 2.15 vs a
baseline of -0.478. Same qualitative story as the fold-windowing thread's
repeated finding (aggregate fitness is far more sensitive to *which* bars/
symbols are in scope than to the strategy's own genes) but from a completely
different axis (universe, not calendar folds) — independent corroboration,
not a restatement.

**Cross-checked against v1 (reconstructed, `--also-version 1`), full
history:** a genuinely new and separate finding, not part of this
diagnostic's original question. v1's own full-history baseline (all 27
symbols, no perturbation) **hard-fails outright** — maxDD -54.3%, fitness
-inf. This does NOT mean v1 should never have been promoted: v1 was accepted
under the fold-aggregate + sealed-holdout process (disjoint windows, `_merge`
across folds), which is a different metric from this diagnostic's one
continuous 4-year single-replay backtest — the same mean-term/single-outlier-
fold sensitivity this file's fold-scheme/regime-folds/fold-cap entries have
already measured extensively means a champion can pass the walk-forward gates
while still looking bad end-to-end in one unbroken replay. Still worth
flagging plainly since it was previously unmeasured: nobody had run a full
single-continuous backtest of the reconstructed v1 before (`fold-scheme`/
`holdout-noise`/`rolling-folds`'s `--also-version 1` all evaluate v1 through
folds or the holdout slice only, never the full continuous span). v1's
perturbed scenarios (dropping PAXG or a random fifth) mostly reduced the
drawdown below baseline's own 54.3% (5 of 7 land under 40%, back to finite
fitness) — one more data point for the same cliff-not-smooth-function
finding, this time showing the cliff can cut the other way (perturbation
*rescuing* a baseline hard-fail, not just causing one).

## Verified safe

- `py_compile` clean, full suite 179 passed (unchanged from before this run).
- `live_state.json` md5 identical throughout (`8b3dc413c9a85fda04bdeb0ad4c63733`).
- `evotrader.manifest` md5 identical throughout (`0bf3a7d9411ee692d0a9f152a7533803`).
- `constitution verified 8b74865634b1db07` unchanged on every invocation.
- `git diff` confirms zero `_SRC[...]` lines touched — pure addition to the
  plain-script CLI dispatch section, same pattern as `margin-curve`.
- Today's 2026-08-21 bar confirmed already processed by the 00:20 UTC daily
  run before this check started (`live_state.json`'s `updated` timestamp
  `2026-08-21T00:27:21+00:00`, current time ~19:02 UTC, `tick` not run this
  session, no double-trade).
- `review-hard-calls` checked: 0 pending.
- No genome promotion this run (no README `## Status` change needed).

## Next

- The drawdown-cliff finding is the sharper of the two results here and
  reads as a genuine, previously-unmeasured risk in the champion's current
  operating point — not immediately actionable (this diagnostic only
  characterizes the cliff, it doesn't propose a fix), but worth carrying
  forward as evidence the next time anyone discusses `MAX_DD_HARD_FAIL`'s own
  margin the way `holdout-noise`/`margin-curve` did for the multiple-testing
  margins. A natural (not yet attempted) follow-up: sweep `--drop-frac` down
  from 20% to see how close to the full 27-symbol universe the cliff sits, or
  up to see how much of the universe can be lost before *most* trials
  hard-fail rather than a minority.
- `--n-trials`/`--seed` sweep for a denser read of the cliff's exact location
  not attempted this run (6 trials was enough to find the cliff exists, not
  enough to map its edge precisely).
- The v1 full-continuous-history hard-fail is flagged, not chased further —
  it corroborates rather than reopens the already-settled fold-vs-single-
  replay sensitivity question this file's fold-scheme/regime-folds/fold-cap
  entries cover in depth.
- `--holdout` random-drop sensitivity (2.15 fitness spread on a -0.478
  baseline) is consistent with, not a departure from, everything the
  fold-windowing thread already found about how noisy small out-of-sample
  windows are — no new action implied beyond what `HOLDOUT_SIGMA` already
  accounts for.
