# 4h shadow evolution meets the dd-corrected gate, plus a first 4h holdout-noise number — 2026-08-30 21:52-23:05 UTC

Picked up item 2's still-open 4h-shadow thread (last touched 2026-08-19/20)
and the `holdout-noise` command's own flagged-but-never-measured question:
"4h's holdout window has ~6.3x more bars than 1d's for the same wall-clock
slice ... if anything this should be a *smaller* effect here ... worth
keeping in mind." Same isolation discipline as every prior 4h-shadow
session: fresh scratch dir (`/tmp/.../4h-holdout-noise/`) containing only a
copy of `evotrader_bundle.py` + `evotrader.manifest`, no `live_state.json`
anywhere near it, so `Genome.champion()` falls back to a hand-built seed
instead of touching this repo's state. Standalone script
(`run_4h_holdout_noise.py`, not committed — ephemeral, gone with the
container) called `EvolutionRun.generation()` directly in a loop from an
x6-scaled seed (same scaling as every prior 4h-shadow run: `trend_fast/slow`,
`rsi_len`, `vol_short/long`, `breakout_len`, `z_len`, `regime_ma`,
`volume_len`, `max_bars_held`, `min_bars_held`, all x6, `bar_interval` ->
`"4h"`), 8 generations at `n_blind=6`. Verified after: real repo `git status`
clean, `live_state.json` md5 unchanged (`81922c6011c986449f635dbf43553d0e`),
`python3 -m pytest -q` 243/243, genome still v3 (1d). 27 symbols x 4 years of
4h bars, ~373s load, ~70 min for 8 generations.

## Finding 1: the dd-corrected gate now blocks what used to be a clean gen-1 fix

Every prior x6-scaled-seed 4h run (2026-08-16 through -19) found its own
generation-1 promotion — a quick fix that took the catastrophic scaled seed
(fitness around -4.2 to -4.5) to positive fold-aggregate fitness within one
generation, every time. **This run is the first one to find none at all,
across all 8 generations** — the seed's fitness stayed pinned at -4.200 the
entire run.

The reason is visible directly in `result.json`'s per-generation records, not
a guess: every generation's *top-ranked* candidate by fold-aggregate fitness
looked like exactly the same kind of quick fix these runs always find
(-0.131, 0.330, 0.352, 0.459, 0.338, 0.381 — all comfortably above the tiny
multiple-testing margin against a -4.200 champion). None of them promoted.
Two rejection reasons split the failures roughly evenly:

- **"challenger failed a hard gate (too few trades, too short, or drawdown
  > 40%)"** — 6 of the ~15 top-3 candidates checked across the 8
  generations, despite each one's *fold-aggregate* fitness clearing the
  champion by a wide margin. This is `dd_corrected_stats()` — the
  continuous-replay max_dd computation `fold-dd-blindspot` (2026-08-22) and
  `succession-audit` added specifically because a fold-merged max_dd is
  structurally blind to drawdowns spanning a fold boundary — catching a real
  drawdown these candidates' fold-merged numbers never saw.
- **"failed sealed holdout"** — the rest, the same fold-vs-holdout pattern
  every prior 4h-shadow run and the live 1d account have already established.

**Why this wasn't seen before**: `dd_corrected_stats()` wasn't wired into
`generation()`'s actual acceptance loop until the 2026-08-21/22 weekend
all-hands (see AGENTS.md item 2, `fold-dd-blindspot`/`succession-audit`
entries) — *after* every prior 4h-shadow run in this account's history
(all dated 2026-08-16 through -20, and the -20 rolling-folds/fitness-decomp
work didn't re-run a fresh evolution). This looks like the first 4h shadow
evolution run since that fix landed, and it changes the qualitative shape of
the whole thread: the reliable "quick fix in generation 1" pattern that
every previous session treated as a given was measured *before* the gate
that would have caught it got wired in. Whether the x6-scaled seed can still
find a dd-corrected-gate-clearing fix at all is now the open question, not
"how many generations until the second plateau" — 8 generations of one draw
isn't enough to answer that (a different random seed, or the researcher's
`boldness` mechanism given more room past generation 8, might still find one;
not attempted further this session on a time-budget call after the ~70 min
evolution phase already spent).

## Finding 2: first real number on the 4h holdout-noise question, with a caveat

Block-bootstrapped (same methodology as `evotrader_bundle.py holdout-noise`
— `loop.engine.bootstrap_fitness_distribution`, `n_boot=2000`,
`block_size=10`) the sealed-holdout return path of the only genome this run
produced: the never-promoted x6-scaled seed itself (fitness -4.200 on the
search folds; on the sealed holdout alone, -0.583 — not as catastrophic,
consistent with the fold/holdout regime mismatch this thread has documented
before).

| | 1d (real champions, 2026-08-20/21 measurement) | 4h (this seed) |
|---|---|---|
| boot_fitness_std | v1 ~1.48, v2 ~1.21, v3 ~2.04 | **1.461** |
| std / `HOLDOUT_SIGMA` (2.0) | 0.74x-1.02x | **0.73x** |
| std / `MULTIPLE_TESTING_SIGMA` (0.08) | ~15-25x | **18.26x** |
| holdout bar count | ~219 (equivalent wall-clock slice) | **1315** (~6x) |

The flagged hypothesis — more holdout bars should mean less relative noise —
is *directionally* supported (0.73x sits at the low end of the 1d range, and
the bar count really is ~6x as expected), but it lands almost exactly inside
the existing 1d range rather than meaningfully below it, so this is weak
support at best, not confirmation. **Real caveat, stated plainly**: the 1d
numbers were measured on three genuinely promoted, live champions;
this 4h number is measured on a genome that never cleared the search gate at
all (Finding 1 above) — not an apples-to-apples comparison. A genuinely
4h-competitive genome's holdout noise is still unmeasured; that's the
sharper version of this question a future session would need to answer, and
it requires first finding a genome that promotes at all under the
now-wired-in dd-corrected gate (Finding 1's open question).

## What's next for item 2

Two concrete, connected follow-ups, neither attempted here on the time
budget:

1. A longer or differently-seeded x6-scaled 4h run to see whether *any*
   genome can clear the dd-corrected gate post-2026-08-22 — the prerequisite
   for a real 4h holdout-noise measurement and for the thread's older
   "does a second plateau exist" question, both of which implicitly assumed
   the old gen-1-promotes-easily shape that this run shows no longer holds.
2. If several fresh 4h runs all show the same "top candidate looks good on
   fold-aggregate, fails on dd-corrected replay" shape, that would be a
   4h-specific instance worth a mechanistic look — same kind of question
   `fold-dd-blindspot` originally answered for the 1d live champion, not yet
   asked of the 4h track's overtrading-prone scaled seed specifically.

Nothing here touched `live_state.json`, promoted anything live, or changed
`researcher_memory` — purely shadow/offline compute per the standing rule
for this item.
