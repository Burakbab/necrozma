# Correlation-universe --realized, second genome (v1 seed) — 2026-08-19 03:50 UTC

## Why

The 2026-08-19 00:52 UTC run's own "Next" line named the honest next step
before treating AGENTS.md item 3's drop-vs-build decision as settled: check
whether a genuinely different genome (not just a different
`correlation_penalty` value on the same champion) changes the held-set
correlation picture. Two prior reads (universe-wide, and v3's own
portfolio-realized) both leaned toward "drop the line", but both were one
champion's one set of entry/exit rules.

## What changed

`evotrader_bundle.py correlation-universe --realized` gained an
`--also-version N` flag, reusing `_reconstruct_champion_genome` (already
built and bit-exact-verified for `fold-scheme --also-version N`). It runs
one additional full-history backtest against the reconstructed genome,
computes its own held-set correlation via the existing `holding_mask` +
`pairwise_correlation_stats`, and prints a cross-genome comparison table.
No new pure functions — this is CLI glue over already-tested code, same bar
`fold-scheme --also-version` was held to (no new tests needed).

## Result

Ran `--also-version 1` (the seed genome, no patches — the most different
real genome this account has had from v3, predating even the existence of
the `correlation_penalty` gene's tuning history). v1's held-only correlation
is *also* lower than universe-wide in every window, same shape as v3:

| window | v3 held-only | v1 held-only | universe-wide |
|---|---|---|---|
| fold 1 | +0.523 | +0.443 | +0.630 |
| fold 2 | +0.470 | +0.409 | +0.509 |
| fold 3 | +0.427 | +0.407 | +0.616 |
| holdout | +0.437 | +0.452 | +0.572 |

Both champions' actual position selection lands on a less-correlated subset
than the universe average, in every window, despite the seed and v3 having
13+ generations of unrelated parametric differences between them (entry/exit
thresholds, sizing, stop-loss/trailing-stop, regime gating — none of it
correlation-aware, since `correlation_penalty` sits at the default `0.0` in
both). v1's held-only numbers run slightly lower than v3's in three of four
windows (holdout is the exception, v1 slightly higher) — a difference in
degree, not in direction.

## Reading

Three independent measurements now agree: universe-wide structure, v3's
portfolio-realized structure, and now v1's portfolio-realized structure. All
three point the same way — there is no concentration problem visible for a
correlation-aware sizing rule to have caught, and it is not an artefact of
one champion's specific tuning. This is the check the prior run's "Next"
line asked for, not another read of the same genome. Still not v2 (the
account's only other real champion) — could be added the same way in one
line if a fourth data point is ever wanted, but three consistent
measurements across two genuinely different genomes plus the raw universe
read is a reasonable place to treat "drop `correlation_penalty`,
`correlation_lookback`, and `_correlation_scale`" as the supported
conclusion, if this item is ever revisited to actually make the change (not
done this run — this is still diagnostic-only, no code path deletes
anything).

## Verified safe

- Purely additive: only the `correlation-universe --realized` CLI branch
  changed, gated behind a new optional flag; default behavior (no
  `--also-version`) is unchanged.
- Full test suite: 104 passed (unchanged from before this run — no new
  tests, matching the `fold-scheme --also-version` precedent of CLI glue
  over already-tested functions).
- `live_state.json` md5 identical before/after
  (`09c35b692da1d694c5a3cace5d488f40`).
- `git status` clean of anything but the `evotrader_bundle.py` diff.
- `constitution verified dfae6a697f51fb49` unchanged throughout (`loop.engine`
  and `_reconstruct_champion_genome` are not in the checksummed set).
- `tick` still correctly reports `already traded` (checked before touching
  anything — today's 2026-08-18 bar was already processed by the 00:20 UTC
  daily run, tick 5; no double-trade).

## Next

If item 3 is ever revisited with a decision to actually make, this closes
the open "different genome" gap the 2026-08-19 00:52 UTC run flagged — three
consistent independent reads now support "drop the line" over "build the
fuller cross-universe factor model". The remaining honest caveat: all
measurements so far are still real-champion genomes only (v1, v3), not a
genome deliberately designed to concentrate (e.g. one that clusters entries
in a correlated sector) — that would be a different, adversarial-style
check, not another pass over the same two accidental data points.
