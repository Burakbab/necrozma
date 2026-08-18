# Fold-scheme sensitivity: does it replicate across champions?

3-hourly self-improvement check. Today's daily bar was already handled by
the 00:20 UTC run (tick 4, bar 2026-08-17) — confirmed via `live_state.json`'s
`updated` timestamp and `runs/2026-08-18-0020-daily-trading.md` before
touching anything else; no `tick` needed this cycle.

## What this answers

The 09:52 UTC `fold-scheme` diagnostic (see `runs/2026-08-18-0952-fold-scheme-sensitivity.md`)
left an explicit next step: its finding (fold 2's outlier dominance over
`aggregate_fitness` shrinks as `n_folds` rises, but `aggregate_fitness`
itself swings non-monotonically) was measured on one champion, one data
snapshot, and "should not be done without first checking whether the
pattern replicates on other champions."

This checks that, using a genuinely independent second champion: v2, the
account's *first* real self-promotion (2026-08-15), reconstructed exactly
from `live_state.json`'s own recorded `lineage` (every accepted promotion's
patch, replayed from the seed genome forward — there's no persisted genome
archive to load from directly, `state/genomes/` is gitignored and
rebuildable-cache-only).

## New capability, tested

`evotrader_bundle._reconstruct_champion_genome(version, lineage)`: walks
`lineage`'s accepted-promotion patches from the seed (`Genome.champion()`)
forward, applying each in order, and returns the genome at the requested
version. Verified bit-exact against the *real* live champion's genes before
trusting it for anything: `tests/test_fold_scheme_reconstruction.py`
includes a test that replays the actual `live_state.json` lineage and
asserts every gene of the reconstructed v3 matches `live_state.json`'s
`genome` field exactly (6 tests total, full suite 78 passed up from 72).

Wired into the CLI as `fold-scheme --also-version N`: runs the same
`n_folds` sweep (3/5/8) against both the live champion and the reconstructed
version `N`, then prints a cross-champion comparison. Purely additive —
`fold-scheme` with no flag reproduces the exact same output as before
(verified: same numbers as the 09:52 run, `live_state.json` md5 identical
before/after both the flagged and unflagged invocations).

## Result — and a correction to how to read it

```
CROSS-CHAMPION COMPARISON
  outlier gap by scheme:
    n_folds=3: v3 (live): +219.4%  v2 (reconstructed): +219.4%
    n_folds=5: v3 (live): +53.8%   v2 (reconstructed): +53.8%
    n_folds=8: v3 (live): +52.0%   v2 (reconstructed): +52.0%

  aggregate_fitness by scheme:
    n_folds=3: v3 (live): -1.224  v2 (reconstructed): 0.581
    n_folds=5: v3 (live): 1.633   v2 (reconstructed): 0.196
    n_folds=8: v3 (live): -0.500  v2 (reconstructed): -0.836
```

The outlier gap is **identical to the decimal** across both champions at
every fold count. This isn't a coincidence and it isn't really a
"replication" finding — the outlier gap is computed purely from
buy-and-hold return per fold (`bench.get("total_return")`), which by
construction never depends on the genome under test. Any genome would show
the same gap at the same `n_folds` on the same data snapshot. The 09:52
run's phrasing ("this is one champion, one data snapshot") slightly
overstated what needed checking on this specific number — it was always
guaranteed to replicate, and re-running it added confirmation but not new
information.

`aggregate_fitness`, by contrast, **is** genome-dependent, and it's the
column that actually tests the replication question — and here the two
champions diverge in shape, not just magnitude: v3's aggregate_fitness
swings non-monotonically across fold counts (-1.224 → +1.633 → -0.500)
while v2's decreases monotonically (0.581 → 0.196 → -0.836). Two data
points isn't enough to call a law, but it does mean the 09:52 run's
"aggregate_fitness swings non-monotonically with fold count" finding does
**not** generalize as a fixed shape — it's specific to v3's own genome
interacting with the fold windows, not a property of the fold scheme alone
that every champion would show the same way.

## What this changes going forward

- Next time a fold-scheme (or similar cross-fold-sensitivity) question comes
  up, `--also-version N` is available to check a specific historical
  champion without hand-reconstructing genomes again.
- The regime-stratified/rolling fold scheme redesign flagged as the likely
  right direction (still a constitution change, still needs its own design
  pass) should be evaluated per-genome if it's ever built, not assumed to
  behave the same way across champions — this run is a second, weaker data
  point for that caution, not a reason to change what gets built.

## Verification

- `python3 -m pytest tests/` — 78 passed (was 72), all new tests in
  `tests/test_fold_scheme_reconstruction.py`.
- `live_state.json` md5 identical before/after every command run this
  cycle (`summary`, `signals`, `tick`, `fold-scheme`, `fold-scheme
  --also-version 2`, `fold-scheme --also-version 99` (deliberate failure
  case)).
- `tick` correctly refused to re-trade bar 2026-08-17 ("already traded").
- `constitution verified dfae6a697f51fb49` unchanged throughout — this
  touches only CLI glue in `main()`, not the checksummed `constitution/`
  package.
- `git status` clean except the intended diff (`evotrader_bundle.py`,
  new test file); `state/` (genome archive + market cache side effects
  of running these commands) confirmed gitignored, not staged.
