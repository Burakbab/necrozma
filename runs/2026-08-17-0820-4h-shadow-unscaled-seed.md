# 4h shadow evolution from a genuinely unscaled seed — 2026-08-17 07:00-08:13 UTC

Follow-up to the open item in AGENTS.md item 2, sharper wording from the
2026-08-17-0510 run: "whether the same shape holds from a genuinely fresh
(non-x6-scaled) seed." Every prior 4h shadow run (2026-08-16 00:00, 06:00,
14:04, the correlation-check run, and the 2026-08-17 second-plateau run)
hand-scaled the seed's bar-count genes (`trend_slow`, `regime_ma`,
`max_bars_held`, ...) x6 before evolving, because the raw seed was known to
be catastrophically broken at 4h. Nobody had let evolution work on the
*unscaled* seed itself. This run does that: same seed genome as always,
`bar_interval` flipped to `"4h"`, every period gene left at its 1d value.

Same isolation discipline as every prior 4h shadow run: fresh scratch dir,
only `evotrader_bundle.py` + `evotrader.manifest` copied in, no
`live_state.json` anywhere in it, so `Genome.champion()` falls back to the
hand-built unscaled seed and `core.market`'s cache/`core.genome`'s
`GENOME_DIR` (both cwd-derived at import time) never touch this repo's
`state/` or the real champion. Verified `bar_interval=4h` in the setup log
before trusting anything. One process hiccup worth recording: a first
attempt was killed by an over-eager internal 600s timeout with zero output
flushed (Python buffers stdout to a pipe by default); the retry used
`python3 -u` and ran fully detached. The killed attempt's partial
`state/genomes/` and cache were wiped before the real run started — nothing
from it leaked into the numbers below.

10 generations at `n_blind=6` (the by-now-standard workable rate for this
bar size, bypassing the bundled CLI's hardcoded `n_blind=14`), one
continuous script, no cache (`refresh=True`). Total wall time 4360s (~73
min) plus 404s to fetch 27 symbols x 4 years of 4h bars = ~80 min.

## Result: the unscaled seed does NOT show the same shape

Every prior x6-scaled run: catastrophic seed (fitness roughly -2 to -4.5) ->
**one** quick fix in generation 1 -> workable/positive fitness (0.6-0.8+)
within a single generation, then plateau (sometimes a second promotion much
later, per the 2026-08-17-0510 run). The unscaled seed instead needed
**three** separate generations to claw partway back, and never crossed into
positive fold-aggregate fitness at all across all 10 generations:

| gen | accepted | patch | fold-aggregate fitness |
|---|---|---|---|
| 1 | v1 -> v2 | `consult_moderate.enabled` True -> **False** (disable it as an entry source entirely — "entries lost -4648 over 6199 trades") | -4.515 -> -1.748 |
| 2 | v2 -> v3 | `risk_judge.correlation_penalty` 0.0 -> **0.9** (near-maximal cross-asset correlation veto) | -1.748 -> -0.905 |
| 3 | v3 -> v4 | `risk_judge.regime_scale.chop` 0.6 -> **0.3** (halve sizing in chop) | -0.905 -> -0.445 |
| 4-10 | — held at v4 | 53 candidates cumulatively tried, boldness climbed 0->6, best any generation got was -0.171 (gen 4) | stuck at -0.445 |

Three qualitatively different fixes (disable an entire consult, near-max
cross-asset correlation veto, halve chop-regime sizing) were each necessary
but not sufficient — each one only partially closed the gap, unlike the
x6-scaled runs where a single gene change was enough. Trade count fell each
time (7394 -> 6061 -> 4970 -> 4710) but even the final v4 is still
overtrading relative to what a properly period-scaled genome produces at 4h
(compare: the 2026-08-16-1404 run's post-fix champion had far fewer trades
at similar bar count). v4's fold-aggregate fitness (-0.445) never got
anywhere near positive, let alone the 0.6-1.0+ range every x6-scaled run's
first fix reached in one step.

## A sharper anomaly: search folds and the sealed holdout tell opposite stories

This is the part worth flagging loudest. Every accepted promotion's
**fold-aggregate fitness stayed negative** (search folds cover the oldest
85% of the 4-year window, 0/3 folds beat benchmark at every step) while the
**sealed holdout fitness was strongly positive and rising** at every single
draw:

| version | fold-aggregate fitness | holdout fitness | holdout beat benchmark |
|---|---|---|---|
| v1 (implicit, pre-promotion) | -4.515 | -1.792 | — |
| v2 | -1.748 | **0.815** | yes |
| v3 | -0.905 | **1.704** | yes |
| v4 | -0.445 | **2.486** | yes |
| gen 4's best (rejected) | -0.171 | -0.768 | failed the holdout gate — correctly rejected |

Read this carefully: the champion that search kept selecting was *never*
good on the data it was searched against, only on the newest 15% slice it
never saw. That is the opposite of the usual overfitting worry (great in
search, falls apart on holdout) — here the holdout is inexplicably far
kinder to this genome than the folds it was tuned on. The most likely
explanation is a regime mismatch: 4h bars' newest 15% (roughly the last
~5-6 months of the 4-year window) may simply be a much more favorable
market segment for a still-overtrading, still-negative-search-fitness
policy than the earlier ~3.5 years it was scored against — not evidence the
policy generalises, evidence the two windows are unlike each other for this
genome. Generation 4's rejection is the control case that shows the gate
still works: a candidate that scored *better* on fold-aggregate (-0.171 vs
v4's -0.445) still failed the holdout outright (-0.768), so this isn't the
holdout gate being rubber-stamped — it swings hard in both directions for
this seed. Not chased further this run; flagging it since nothing in the
prior x6-scaled runs showed this pattern this starkly (their fold and
holdout fitness moved together, both crossing from negative to positive on
the same promotion).

## Answering the open question directly

**No, a genuinely unscaled fresh 4h seed does not show the same shape as
the x6-scaled seed.** It needs more generations to find any fix at all
(3 vs 1), never reaches positive fold-aggregate fitness in 10 generations
(vs. 0.6-0.8+ in one generation for every x6-scaled run), and the promotions
it does find lean on a fold/holdout split that behaves unlike anything seen
in scaled runs. This is consistent with — and now has real evidence behind
— the original 2026-08-16 finding that "a 1d-tuned genome cannot be ported
to 4h as-is": evolution alone, given enough generations, *can* claw an
unscaled seed partway out of catastrophic territory, but manual pre-scaling
before evolving gets to a categorically better place (positive fitness,
fewer trades, aligned fold/holdout behaviour) in a fraction of the
generations. Pre-scaling isn't just a head start, it changes what shape of
outcome is reachable at all in a workable generation budget.

Open next: is 10 generations just not enough for the unscaled seed to reach
what the scaled seed finds in 1-2, or is -0.445 fold-aggregate a genuine
plateau for this starting point? Also open: chase the fold/holdout split
anomaly directly — slice the 4h data into the same three search folds plus
holdout and look at what regime each actually contains, rather than
inferring it from fitness numbers alone.

Nothing here touched `live_state.json`, `researcher_memory`, or the real
champion (still v3, 1d bars, unchanged). Scratch dir, cache, and
`result.json` are ephemeral (`/tmp`), gone with this container.
