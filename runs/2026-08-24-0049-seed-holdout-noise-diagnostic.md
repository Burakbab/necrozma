# Seed genome's sealed-holdout noise, quantified — 2026-08-24 ~00:49 UTC

Scheduled 3-hourly check. Today's daily bar was already handled by the 00:20
UTC run (`live_state.json` `updated` 2026-08-24T00:22:01+00:00, genome version
still 3, md5 unchanged throughout this session) — nothing new to trade this
cycle. `review-hard-calls` still 0 pending. Picked up the open question the
previous session (`runs/2026-08-23-2216-fresh-seed-1d-shadow-evolution.md`)
explicitly left unchased: is the fresh `SEED_GENOME`'s badly-negative
sealed-holdout fitness an unusually deep outlier draw, or an ordinary sample
from its own noise?

## Setup

One-off script (not a new CLI command — this question doesn't need to be a
permanent diagnostic yet, unlike `holdout-noise`, which only takes a real
champion from `live_state.json`'s lineage via `acct.genome`/`--also-version`).
Imported `core.genome.SEED_GENOME`/`Genome`, `core.market`,
`loop.engine.run_backtest`/`bootstrap_fitness_distribution` directly from the
real unflattened packages (proven byte-identical to the bundle's own `_SRC`
entries) — no `LiveAccount`, no `state/genomes/`, no path anywhere near
`live_state.json`. One real backtest of the seed over the sealed holdout
window (newest 15% of a fresh 4-year pull, same caveat as the prior session:
the window has shifted one more day, so the seed's holdout fitness here
(-1.194) is not the same number as before (-2.566) purely because of the date
shift), then `bootstrap_fitness_distribution` block-bootstraps that one
observed return path 2000 times per RNG seed. Only wrote to `state/cache/`
(gitignored, shared market-data cache — same as every other diagnostic run
from repo root).

## Result: an ordinary draw, not an outlier

| RNG seed | bootstrap fitness std | z-score of real fitness |
|---|---|---|
| 0 | 1.771 | -0.07 |
| 1 | 1.847 | -0.13 |
| 2 | 1.783 | -0.10 |
| 3 | 1.816 | -0.09 |

The seed's real observed holdout fitness sits within 0.13 sigma of its own
bootstrap distribution's mean at every RNG seed tried — about as ordinary a
draw as a distribution can produce. The bootstrap sigma itself (~1.77-1.85)
is squarely in the same range `holdout-noise`'s docstring already recorded for
the three real champions (v1 ~1.48, v2 ~1.21, v3 ~2.04), not an outlier level
of noise either.

**Reading**: this closes the specific question the prior session left open.
The seed's poor sealed-holdout score is not a fluke of *which* order the
holdout's returns happened to arrive in (that's what the bootstrap
distribution measures) — it's a genuine property of the seed's actual
return path on this data window: the seed genome really does perform badly
over this specific holdout slice, and no amount of re-drawing the bar order
would typically produce a much better or much worse number. Combined with the
prior session's finding (blind search from this seed never got any candidate
past `holdout_accepts()`'s climbing multiple-testing margin in 16
generations), the full picture is: a genuinely bad seed on a genuinely bad
window, correctly and consistently rejected — not evidence of a holdout-gate
bug, a resampling artifact, or a fixable seed-selection mistake, just the
gates doing their job on a bad starting point. Not chased further: whether a
*different* 4-year data pull (a different holdout window entirely) would show
the seed in a better light — that's a question about `SEED_GENOME`'s
robustness across market regimes generally, bigger than this session's scope,
and only loosely connected to the noise-vs-signal question this run answered.

## Verified safe

`git status --short` clean before and after (only `state/cache/`, gitignored,
touched); `live_state.json` md5 unchanged throughout; full test suite still
223 passed (no code changed this session, ran as a baseline sanity check
before writing this note); `review-hard-calls` still 0 pending; no genome
promotion anywhere real (no README Status change needed). No push
notification sent — a read-only research finding with zero effect on live
trading behavior.
