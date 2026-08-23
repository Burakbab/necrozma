# Fresh unscaled seed, 1d bars, 16 generations — 2026-08-23 ~22:16 UTC

Scheduled 3-hourly check. Today's daily bar was already handled by the 00:20
UTC run (`live_state.json` `updated` unchanged since then, md5
`af16ffdc22a57c5d63a83003216a8f99` throughout this session) — nothing new to
trade this cycle. `review-hard-calls` still 0 pending. Used the slot on the
"Measured 2026-08-16" section's open call to prefer evidence-producing work
("convergence across independent seeds") — this specific check (a genuinely
fresh, unscaled seed at the live 1d cadence) had never been run before; every
prior seed-convergence test in AGENTS.md's item 2 was at 4h bars, several of
them pre-scaled.

## Setup

Same isolation discipline as every prior shadow run, simplified further:
`EVO_STATE=shadow_state.json` pointed at a scratch directory outside the
repo with **no existing state file at all** — `LiveAccount.load()` on a
missing path returns an empty account, which falls back to
`Genome.champion()`, which (with no `state/genomes/` on disk in this fresh
container) returns the plain hand-written `SEED_GENOME` (v1) and persists it
under the scratch cwd's own `state/genomes/`. No copying of the real
`live_state.json` was needed or done. Ran
`python3 evotrader_bundle.py evolve 1` then `evolve 15` (16 generations
total, real 27-symbol 1d Binance data, `n_blind=14` default) against this
fresh seed. **Nothing here touched the real repo's `live_state.json` or
`state/`** — confirmed both by construction (`GENOME_DIR`/`STATE_PATH`
resolve under the bundle's own working-directory-relative extraction, which
landed entirely inside the scratch dir this run — verified no
`state/genomes/` exists under the real repo afterward) and by md5 (unchanged
throughout).

Caveat worth naming: `evolve` pulls the last 4 years of data ending *today*,
not the same window the real v1→v2→v3 lineage was originally evolved
against weeks ago — so the seed's raw fitness number here (`-0.022`) isn't
directly comparable to the real lineage's first recorded entry (`0.576` for
v1 in `live_state.json`'s lineage) purely because the window shifted, not
because the genome differs. This doesn't affect the finding below, which is
about the seed's own fold-vs-holdout divergence *within this run's own
window*, not a cross-window comparison.

## Result: zero promotions in 16 generations — and a mechanistic reason, not just a data point

Every prior fresh/scaled-seed convergence test in AGENTS.md (all at 4h bars)
found a first promotion within 1-2 generations via blind search alone. This
run found **none** in 16, despite 235 cumulative unique proposals tried and
several candidates reaching a fold-aggregate fitness far above the seed's
own (best-per-generation fitness values: 0.22, 0.44, 0.36, 0.14, 0.28, 0.61,
0.15, 0.24, 0.18, 0.15, 0.14, 0.76, 0.58, 0.55, 0.66, 0.89 — generation 16's
best alone is 40x the seed's `-0.022`).

The reason isn't the fold-aggregate gate (`accepts()`) — 10 of the 16
generations' best candidate *did* clear it. It's the sealed holdout. The
seed genome's own holdout fitness, on the newest 15% slice of the current
4-year window, is **-2.566** — dramatically worse than its `-0.022`
fold-aggregate number, a much sharper fold/holdout divergence baked into the
seed than any real champion has ever shown (v3's own holdout draw, by
contrast, was measured strongly positive in the 2026-08-18 unscaled-4h-seed
run). Combined with `holdout_accepts()`'s multiple-testing margin
(`HOLDOUT_SIGMA=2.0`, growing as `2.0 * sqrt(2*ln(n_draws))` — by design,
not a bug, see `constitution/__init__.py`), every one of the 17 candidates
that reached the holdout gate failed:

| draw# | fold fitness | challenger holdout | champion holdout | margin | needed > |
|---|---|---|---|---|---|
| 1  | 0.218 | -2.515 | -2.566 | 2.355 | -0.211 |
| 2  | 0.183 | -0.356 | -2.566 | 2.355 | -0.211 |
| 3  | 0.360 | -2.495 | -2.566 | 2.965 |  0.399 |
| 4  | 0.266 | -2.716 | -2.566 | 3.330 |  0.764 |
| 5  | 0.210 | -2.253 | -2.566 | 3.588 |  1.022 |
| 6  | 0.612 | -1.160 | -2.566 | 3.786 |  1.220 |
| 7  | 0.244 | -1.275 | -2.566 | 3.946 |  1.380 |
| 8  | 0.756 | -0.786 | -2.566 | 4.079 |  1.513 |
| 9  | 0.302 |  0.290 | -2.566 | 4.193 |  1.627 |
| 10 | 0.579 | -2.034 | -2.566 | 4.292 |  1.726 |
| 11 | 0.385 | -1.181 | -2.566 | 4.380 |  1.814 |
| 12 | 0.551 | -0.741 | -2.566 | 4.459 |  1.893 |
| 13 | 0.293 | -1.149 | -2.566 | 4.530 |  1.964 |
| 14 | 0.664 | -1.478 | -2.566 | 4.595 |  2.029 |
| 15 | 0.427 | -1.883 | -2.566 | 4.655 |  2.089 |
| 16 | 0.885 | -0.261 | -2.566 | 4.710 |  2.144 |
| 17 | 0.817 | -0.074 | -2.566 | 4.761 |  2.195 |

Draw #2, in generation 1, came closest ever attempted (challenger -0.356 vs.
needed > -0.211, a miss of only 0.145) — and every draw after it missed by
more, not less, both because no later challenger's holdout score trended
better (they bounce between -2.7 and +0.29 with no visible improvement
across 16 generations) and because the required margin keeps climbing
regardless. By draw 17 the bar is +2.195 against a champion sitting at
-2.566 — a gap of 4.76 points that fold-aggregate-improving mutations
plainly are not closing.

**Reading**: this sharpens rather than repeats the 2026-08-18 finding ("a
champion that draws a lucky holdout score becomes hard to unseat"). That
entry was about a *good* champion's holdout draw protecting it. This is the
mirror case — a genuinely *bad* seed's own holdout draw traps it too, for
the same structural reason (cumulative margin inflation), independent of
whether the champion's starting score was lucky or unlucky. Merely running
more generations cannot fix this: every fold-aggregate-clearing proposal
burns another holdout draw and pushes the bar higher, so the trap deepens
monotonically rather than resolving. Answers this session's framing of the
"convergence across independent seeds" open item for the *live* 1d cadence
specifically (previously only tested at 4h, where pre-scaling and/or a less
severe seed fold/holdout gap let searches through quickly): blind search
from a genuinely fresh 1d seed is not guaranteed to converge to anything at
all within a realistic generation budget, and this run is a concrete
existence proof, not a hypothetical.

Not chased further this session: whether the seed's holdout weakness is
data-window-specific (a different 4-year pull might show a smaller
fold/holdout gap) or a durable property of the hand-written `SEED_GENOME`
itself. That's the natural next question if this thread continues — e.g.
does `holdout-noise`'s block-bootstrap sigma on the seed specifically match
`HOLDOUT_SIGMA`, or is the seed's -2.566 an unusually deep outlier draw in
its own right.

## Verified safe

`git status` clean throughout and after; real `live_state.json` md5 unchanged
(`af16ffdc22a57c5d63a83003216a8f99`); no `state/` directory created under the
real repo path (confirmed by listing); `review-hard-calls` still reports 0
pending; no genome promotion anywhere real (no README Status change needed).
No push notification sent — a shadow/offline research finding with zero
effect on live trading behavior.
