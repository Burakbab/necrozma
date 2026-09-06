# Researcher boldness saturation fix — 2026-09-06 06:47-07:xx UTC (3-hourly check)

## Why this cycle didn't run a seventh plain `evolve` batch

Six straight 3-hourly cycles (2026-09-05 12:46, 15:47, 18:46, 2026-09-06
00:46, 03:47 UTC) ran plain `evolve` against the live v3 (1d) champion and
found nothing new each time: fitness flat at 1.215, every new candidate lost.
Rather than run a seventh identical batch on no new information, this cycle
asked *why* the search keeps landing in the same place instead of just
running it again.

## The finding

`agents/researcher.py`'s `Researcher.perturb(g, n, n_genes=2, boldness)`:

```python
jump_p = min(0.75, 0.2 + 0.12 * boldness)
spread = 1.0 + 0.35 * boldness
genes_per = min(len(paths), n_genes + int(boldness // 2))
```

Both `jump_p` and `genes_per` are capped, and both saturate at boldness
values far below where real stagnation counters actually reach:

| boldness | jump_p | spread | genes_per / 44 |
|---|---|---|---|
| 0 | 0.20 | 1.00 | 2 |
| 4 | 0.68 | 2.40 | 4 |
| 5 | 0.75 (capped) | 2.75 | 4 |
| 20 | 0.75 | 8.00 | 12 |
| 50 | 0.75 | 18.50 | 27 |
| **92** | 0.75 | ~33.2 | **44 (capped, all genes)** |
| **134 (live value)** | 0.75 | 47.90 | 44 |

The live champion's stagnation/boldness counter is already **134** (see the
03:47 UTC entry). It crossed `genes_per`'s saturation point (~92) roughly 40+
generations ago. Past that point, every single blind-search candidate
mutates *all 44 genes at once*, and each gene independently has a 75% chance
of an outright uniform redraw across its entire allowed range. The remaining
25% "local jitter" branch also scales its own spread by the same unbounded
`boldness` (47.9x at the live value), so it isn't meaningfully more local
either — verified directly:

```
$ python3 -c "... Researcher(seed=42).perturb(g, n=14, boldness=134.0) ..."
genes touched per proposal: [2, 2, 1, 44, 43, 44, 44, 44, 44, 40, 42, 43, 43, 44]
```
(that's the *fixed* version already reserving a local slice — before the
fix, all 14 would read close to 44.)

The docstring's own stated intent — "widen search under stagnation, don't
abandon it, the local hill has been climbed" — has in practice become "only
ever fully randomize the entire genome" for a large and growing share of
this account's evolution history, with nothing measuring or flagging the
saturation point directly until now.

## The fix

`perturb` now reserves `max(1, n // 4)` of every batch's candidates to
always run at boldness 0 (narrow, ≤2-gene, small jitter — the same
behavior every proposal used to get at the very start of a champion's
life), regardless of how high the real `boldness` argument climbs. The
remaining candidates keep the existing graduated-widening behavior
unchanged. Net effect: long stagnation now adds wide exploration *on top
of* continued local exploitation, instead of silently replacing it.

At `boldness=0` (every evolve run's actual starting point, and the state
every past promotion was found from) the change is a no-op — the
local-slice branch only activates when `boldness > 0` — verified both by
code inspection and by the existing
`test_propose_non_blind_proposals_are_seed_independent_only_perturb_varies`
test passing unmodified.

## What this is not

- Not a constitution change. `agents/researcher.py` is not one of the two
  files `constitution.checksum()` hashes (only `constitution` and
  `core.portfolio` are) — no re-seal needed, verified
  (`constitution.verify()` still reports `8b74865634b1db07`).
- Not a change to acceptance gates. This only changes which candidates get
  *proposed* to the fold/holdout gates — it cannot make a bad promotion
  more likely, it can only make finding a genuinely better candidate
  somewhat more likely by keeping local exploitation alive.
- Not a live-state change. `live_state.json` was never opened for writing
  this cycle (md5 identical before/after); no `evolve`/`tick` was run.

## Verification

- Edited the real `agents/researcher.py` (source of truth per item 7),
  re-synced the bundle with `tools/edit_bundle_module.py sync` (the actual
  live path every scheduled command executes) — `sync --check` and `verify`
  both confirm bundle and real files match.
- New `tests/test_researcher_perturb_boldness.py` (3 tests): boldness=0
  unaffected, a high-boldness (134) batch still contains both narrow
  (≤2-gene) and wide (full-genome) candidates, local-slice sizing scales
  sanely with batch size.
- Full suite: 358/358 (was 355, +3).
- `live_state.json` md5 unchanged, constitution checksum unchanged, genome
  still v3 (1d) live and untouched, no protected file touched.
- No live trading this cycle — tick 23 already handled at 00:20 UTC
  (confirmed via `live_state.json`'s `updated` timestamp and
  `runs/2026-09-06-0020-daily-trading.md` before starting).

## Next

The next `evolve` batch against the live v3 champion is the first to
actually exercise this fix. Worth noting in that batch's run note whether
the reserved local slice finds anything the fully-saturated wide search
couldn't in the last 40+ generations — though a single batch either way
won't be conclusive on its own; this is a mechanism fix justified on its
own logic (restoring a design intent that had silently broken), not a
guaranteed fitness improvement.
