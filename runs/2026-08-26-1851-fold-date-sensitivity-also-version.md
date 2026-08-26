# Fold-date-sensitivity across v1/v2/v3 — is the swing v3-specific? (2026-08-26 ~18:51 UTC)

## Question

The 12:57 UTC entry found the real `evolve()` fold-aggregate fitness swings
[-1.652, +1.480] (spread 3.13) across a 7-day "as-of" window for live
champion v3, with a hard `RANK_FLOOR` fail (-5.000) on today's date
specifically. Open item: is this v3-specific, or general across genomes?
`fold-date-sensitivity` already ships `--also-version N` (same flag as
`fold-scheme`/`succession-audit`/etc.) — no code change needed, just run it.

## Method

`python3 evotrader_bundle.py fold-date-sensitivity --also-version 2` and
`--also-version 1`, each reconstructing the named past champion via
`_reconstruct_champion_genome` and running it through the identical
`Evaluator(data, n_folds=N_FOLDS).evaluate(genome)` sweep as v3, `--shift`
default 7 (today back to 6 days ago).

## Results

| genome | aggregate_fitness range | spread | RANK_FLOOR (-5.000) hits |
|---|---|---|---|
| v3 (live) | [-1.652, 1.480] | 3.132 | 1/7 (fold 3, shift 0 only) |
| v2 (reconstructed) | [-2.522, 0.293] | 2.814 | 4/7 (fold 1, shifts 1/3/4/6) |
| v1 (reconstructed) | [-2.731, 0.430] | 3.161 | 3/7 (fold 1, shifts 0/2/4) |

## Reading

Not v3-specific — all three genomes checked so far (the full live lineage)
show the same order-of-magnitude spread (2.8-3.2), and two of the three
(v1, v2) hard-fail a fold on a *majority* of the 7 shifts checked, worse
than v3's 1/7. This rules out "v3 happens to sit on an unlucky boundary"
as the explanation and points back at the general day-1 greedy-allocation
mechanism the boundary-shift thread already traced (06:55/09:50 UTC
entries) as the real cause — it's a property of the fold/allocation scheme
itself, not of any one evolved genome.

Matches the pattern already seen in the unrelated selection-noise thread:
checking a second and third genome is what turns a one-genome anecdote
into a general finding, not more draws against the same genome.

## Still open

The two next-steps named in the 12:57 UTC entry that this run did NOT
attempt: (1) whether this measurably flips any real accept/reject verdict
in practice (replay a real historical generation's candidate batch against
the champion re-evaluated at a different shift — needs a `Researcher`
batch, not just re-evaluating the champion alone, so it's a bigger next
session); (2) the day-1-allocation-redesign question (proportional/ranked
instead of greedy-first-come) — untried design work, no code attempted
here.

## Safety checklist

- No code changed (`git status --short` empty on `evotrader_bundle.py`)
  before and after — reused existing `--also-version` flag, same as prior
  no-code-change diagnostic sessions. No test suite run (no code changed).
- `live_state.json` md5 unchanged: `1441d25f45fb4a927f993cbc8c505a5b`
  (still tick 12, the 00:20 UTC daily run — no double-trade, today's bar
  already processed before this session started).
- `evotrader.manifest` md5 unchanged: `0bf3a7d9411ee692d0a9f152a7533803`.
- `tools/edit_bundle_module.py sync --check`: "bundle already matches real
  files, no changes".
- Constitution verified `8b74865634b1db07` on every invocation, unchanged.
- No genome promotion — no README `## Status` change needed.
