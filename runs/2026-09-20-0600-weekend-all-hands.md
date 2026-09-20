# Weekend all-hands — 2026-09-20 (~06:05-07:30 UTC)

## Scope

Sync (git checkout main + pull, `pip3 install -r requirements.txt`), read
AGENTS.md in full plus recent `runs/`, then picked the highest-value item
for a deep-focus weekend slot per the "Next steps" priority list. Items 2
(4h bars) and 3 (correlation-aware sizing) are closed/parked, item 6
(equities/FX) and the "open a short" half of item 5 both explicitly wait on
an owner decision, item 4 (LLM-backed consults / hard-call review) is
working as designed with nothing queued. That left the recurring pattern in
every recent 3-hourly check itself as the open question worth a real look:
champion v3 has now gone **1801 generations and 25,025 cumulative
candidates without a promotion**, and the sealed-holdout margin keeps
creeping up (7.075 at last check). Nobody had stopped to ask *why*, in
mechanism terms, rather than just re-running another 15-generation batch
and reporting "no promotion" again.

## What was built

`agents.researcher.Researcher.perturb`'s own docstring already works out
the arithmetic: `jump_p` (chance a mutated gene gets a fresh uniform
redraw across its whole range) saturates at 0.75 by boldness ~4.6, and
`genes_per` (how many of `GENE_SPACE`'s 43 genes one proposal touches at
once) saturates at *all 43 genes* by boldness ~82. `boldness` is fed
directly from the champion's stagnation counter
(`boldness=float(self.stagnation)` in `EvolutionRun.generation()`), and the
live champion's stagnation is 1801 — meaning every non-exploitative blind
proposal against the live champion has, for roughly the last 1719
generations, been a full-genome, mostly-uniform-random redraw of all 43
genes at once. That's been a hypothesis anyone could read off the code;
nobody had actually measured whether it matters.

New `loop.evolve.boldness_scan` (tested: `tests/test_boldness_scan.py`, 4
tests, full suite 426/426) runs the identical seeded shadow search twice
from the identical starting point (same champion, same real
`researcher_memory`) — once with boldness left unbounded (mirrors
production exactly) and once capped at `--cap` — and reports how often
each arm's best candidate clears the fold-aggregate `accepts()` gate and
the sealed holdout. A fresh `Researcher(seed)` is built for each arm so
both draw from the identical RNG stream at the point they diverge; the only
input difference is the boldness value fed into `propose` each generation.
Never calls `Genome.save()`/`.promote()`/`EvolutionRun._record()` — same
read-only contract as the existing `disagreement_scan`. New CLI command
`boldness-scan` (`--generations`, `--cap`, `--seed`, `--n-blind`,
`--fresh`). Bundle synced via `tools/edit_bundle_module.py sync`, verified
byte-consistent; `live_state.json` and the constitution manifest untouched
throughout. Shipped and pushed as its own commit before running it for
real, per the "only commit finished, working things" rule.

## What it found, running for real against the live champion

`boldness-scan --generations 15 --cap 20 --seed 7`, seeded from the real
`researcher_memory` (tested=25025, stagnation=1801, holdout_draws=522):

| | best-of-gen fold-fitness range | fold-gate clears | holdout clears |
|---|---|---|---|
| **uncapped** (mirrors production) | 1.618 – **4.199** | 2 / 15 | 0 |
| **capped at boldness=20** | 1.338 – 2.251 | 3 / 15 | 0 |

Neither arm promoted — consistent with every recent 3-hourly check's own
experience. The capped arm cleared the fold-gate slightly *more* often (3
vs 2) despite the uncapped arm reaching a far higher peak fitness (4.199 vs
2.251), but 15 generations against one seed is far too small a sample to
call that a real effect either way; it would need many more generations or
several seeds to say anything with confidence.

**The more informative result was in *why* the uncapped arm's 4.199
outlier still failed.** Reproduced generation 5 directly against the real
`EvolutionRun` pipeline (same seed, same `initial_champion_version` so
`tested`/`stagnation` aren't spuriously reset — a bug in the first
reproduction attempt, caught and fixed before trusting the result) to get
the actual rejection reason `boldness_scan`'s summary doesn't carry:

- The candidate (a full-genome redraw touching all 37 mutable genes at
  boldness 1805) scored fold-aggregate fitness **4.199** against the
  champion's 1.728 — comfortably clearing the fold-stage margin (0.360 at
  ~25,039 cumulative candidates).
- At the sealed holdout it scored **3.070 against the champion's 2.309** —
  a genuine raw beat, +0.761.
- It was still rejected: `failed sealed holdout: 3.070 did not clear
  champion 2.309 + margin 7.076 (523 cumulative draws against this
  holdout)`.

Cross-checked against the real (non-shadow) lineage via `holdout-pressure`:
27 real fold-aggregate winners have reached the sealed holdout against v3
and lost every time, margin climbing 7.043 → 7.075 across draws 493-522.
One of those real rows (fold-fitness 4.940, draw 502) is an even bigger
outlier than this session's shadow find — so extreme fold-fitness spikes
reaching holdout and failing there is already a known, tracked pattern in
production, not something this session discovered from scratch.

## The actual conclusion, stated plainly

The session went in expecting to find that unbounded boldness had
degenerated blind search into wasted, low-value full-genome randomization,
and that capping it would be the fix worth proposing. The data don't
support that as the dominant story. The mechanism does produce those wide,
mostly-random full-genome proposals, and it can produce a genuinely
better-on-both-fold-and-raw-holdout candidate (this session's reproduced
example proves that isn't just theoretical) — but **the sealed-holdout
margin has grown, by design, to a size (7.076 after 523 cumulative draws)
that a raw edge of 0.761 is nowhere near clearing, and no plausible search
strategy change fixes that**: the margin scales as
`HOLDOUT_SIGMA * sqrt(2 * ln(n_draws))`, so it keeps rising (slowly,
~0.001/draw at this range) regardless of whether the candidates reaching it
come from a wide random search or a narrow local one. Capping boldness
might modestly change *how often* something reaches the holdout gate at
all (the 3-vs-2 fold-gate-clear difference hints at this, weakly), but it
would not change what it takes to actually clear the holdout once there.

This is the multiple-testing correction working as designed — deliberately
making an unbeaten champion's bar rise the longer it stands, specifically
to prevent a mined holdout draw from manufacturing a promotion out of
noise (see AGENTS.md's "Two flaws" section). It is not a bug. But it does
mean, stated as a number for the first time rather than "margin still
rising slowly, nothing new": at 523 cumulative draws, a challenger needs a
raw sealed-holdout fitness edge of roughly **9x** what this session's best
real example produced (7.076 needed vs 0.761 delivered) before champion v3
can ever be replaced through the normal search path. Promotions from here
are going to be rare by construction, not because search has stopped
finding real improvements.

## What's next, deliberately not attempted this session

Two different, larger questions this surfaces but doesn't answer, each
needing its own dedicated look rather than a tail-end addition here:

1. **Does capping boldness change the fold-gate-clear rate in a real,
   statistically meaningful way?** This session's single 15-generation,
   single-seed comparison (3 vs 2) is suggestive, not conclusive. A real
   answer needs either many more generations or several different seeds
   averaged — `boldness-scan` already has the `--seed` flag to do this,
   just not run enough times yet.
2. **Is `HOLDOUT_SIGMA` (and therefore the holdout margin's absolute size)
   still well-calibrated at 500+ cumulative draws?** `holdout-noise`
   measured it once (2026-08-20, ~24-25x for v3) as a bootstrap estimate of
   realized-path noise, but its own docstring already flags that a
   candidate arrives at this gate pre-selected upward (only top-3
   fold-aggregate winners ever reach it), which `HOLDOUT_SIGMA` doesn't
   capture. Whether the margin's design should ever be revisited is a
   constitution-adjacent policy question, not an engineering one — same
   category as item 2's `MULTIPLE_TESTING_SIGMA` open thread — and stays
   the owner's call, not something to change unilaterally off one
   session's shadow run.

No code path touching the live champion, `live_state.json`, or the
constitution changed. `boldness-scan` is now a permanent, reusable
diagnostic for whoever picks either question up next.
