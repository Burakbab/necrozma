# Fold-scheme sensitivity: a third champion (v1, the seed)

3-hourly self-improvement check. No code changed — this is a read-only run
of the existing `evotrader_bundle.py fold-scheme --also-version N`
diagnostic (shipped 2026-08-18, see `runs/2026-08-18-1256-fold-scheme-champion-replication.md`)
against a third champion, closing the open question that run's "Next" line
left: *"whether a third champion looks like v2's shape, v3's shape, or a
third one."*

## Why v1

`fold-scheme --also-version N` reconstructs any past champion from
`live_state.json`'s own recorded `lineage`, and `_reconstruct_champion_genome`
already documents that version 1 (the seed genome — no accepted patches
needed) always succeeds. v1 is the only remaining champion in this account's
history that hadn't been fold-scheme-swept yet (v2 checked 12:56 UTC today,
v3 checked 09:52 UTC today).

## Command

```
python3 evotrader_bundle.py fold-scheme --also-version 1
```

## Result

Outlier gap (buy-and-hold-only, genome-independent by construction, as
expected): identical to the decimal across all three champions at every
fold count — +219.4% (n=3), +53.8% (n=5), +52.0% (n=8). Confirms nothing
new; this column can never distinguish genomes.

`aggregate_fitness` (genome-dependent — the column that actually tests
generalization of the earlier finding):

| n_folds | v1 (seed) | v2 | v3 (live) |
|---|---|---|---|
| 3 | -2.577 | 0.581 | -1.224 |
| 5 | 0.244 | 0.196 | 1.633 |
| 8 | -0.938 | -0.836 | -0.500 |

v1's shape is **non-monotonic** (down → up → down), the same qualitative
swing v3 showed, not v2's monotonic decrease. So the 12:56 UTC run's
conclusion — "the non-monotonic swing is v3-specific, not a general
fold-scheme property" — was drawn from only one non-monotonic data point
against one monotonic one. With v1 added, **2 of 3 champions swing
non-monotonically, 1 decreases monotonically.** That flips the working
read: non-monotonic behavior is not a v3-specific oddity, it looks like the
more common shape across this account's own champion history, though n=3
genomes is still too small to call it a law either way, and v1's absolute
fitness values are unusually negative throughout (0/3, 1/5, 1/8 folds beat
benchmark — the seed genome was never good, which may itself be
correlated with which shape a genome shows; not teased apart here).

## Verified safe

- No code changed this run — pure re-invocation of existing, already-tested
  CLI glue.
- `git status --short` clean before and after.
- `live_state.json` md5 unchanged (`c4289723973ee8ace977f7abaf0003a8`).
- `constitution verified dfae6a697f51fb49`.
- Full test suite: 78 passed (same as before running the diagnostic).

## Next

The open fold-scheme question from 2026-08-18's earlier runs stands, now
with a slightly different framing: if a regime-stratified/rolling fold
scheme redesign is ever undertaken (constitution change, needs its own
design pass and an `AMENDMENTS.md` row), don't assume non-monotonicity is
a v3 quirk to route around — on this evidence it's at least as likely to be
a property of the fixed 3-fold calendar split itself, showing up on most
genomes tried against it. `--also-version N` has now swept all three real
champions this account has ever had (1, 2, 3); the next genuinely new data
point only arrives when a fourth champion is promoted.
