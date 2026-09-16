# 3-hourly self-improvement check — 2026-09-16 ~00:48-01:04 UTC

## Scope

Item 12 (`AGENTS.md`), flagged 2026-09-15 ~21:47-22:20 UTC: `live_state.json`
was on a ~4.8MB/day growth trajectory, on track to hit GitHub's hard 100MB
per-file push limit around 2026-09-24/25 — about 9 days out. Root cause
already identified by the flagging session: `researcher_memory["tested"]`
persists the *full* gene patch for every candidate ever tried against the
unbeaten live v3 champion (17,710 entries, no cap, only resets on a real
promotion), because `agents/researcher.py`'s `Researcher.key()` used the
patch itself as a proposal's identity instead of a hash.

No live trading this cycle — checked before starting: `live_state.json`
`updated` `2026-09-16T00:22:28+00:00`, matching `runs/2026-09-16-0020-daily-trading.md`
(tick 33, 00:20 UTC daily run). Current time ~00:48 UTC, well before the
next daily bar close. This is the concretely-scoped, urgent next step
`AGENTS.md` item 12 named — highest-value item this cycle, and small enough
to land in one sitting.

**Also fixed this cycle, unrelated to item 12**: the container's local `main`
branch pointer was stale (pointed at commit `71ae680`, ~50 commits behind
`origin/main`'s actual tip `c348774`) from before the repo's history was
rewritten upstream at some point. Working tree was clean and detached HEAD
was already sitting on `origin/main`'s real tip, so this was a pure branch-
pointer staleness, not local work at risk — `git reset --hard origin/main`
brought the branch ref back in line with no content change.

## What changed

`Researcher.key()` (`agents/researcher.py`) now returns a 16-hex-char sha256
hash of the sorted `(gene_path, str(value))` patch tuple instead of the
tuple itself. Added `Researcher.patch_key()` (the hashing primitive, split
out so it can be called on a raw tuple without a `Mutation` object) and
`Researcher.migrate_tested_entry()`, which normalizes one
`researcher_memory["tested"]` entry to the current hash identity whether
it's already a hash (new format) or a full persisted patch (old format,
JSON's `list[list[str]]` rendering of the pre-fix tuple-of-tuples) — a
one-time, one-way, read-time conversion, exactly the migration story
`AGENTS.md` item 12 scoped as "simplest."

Updated every site that reconstructs the `tested` set from
`researcher_memory` (not just counts its length, which needed no change):

- `evotrader_bundle.py`'s `evolve` command (the live path) — reads via
  `Researcher.migrate_tested_entry`, writes back `list(run.tested)` (now a
  set of hashes, not `[[list(pair) for pair in k] for k in run.tested]`).
- `evotrader_bundle.py`'s `disagreement-sweep` command — read-only, seeds
  from live `researcher_memory` but never writes; same migration-aware read.
- `run_from_files.py`'s `_cmd_evolve` and `_cmd_evolve_dry_run` — mirrors of
  the two bundle sites above (the "not yet wired into any scheduled run" real
  files cutover), updated identically to keep
  `tests/test_run_from_files_matches_bundle.py` meaningful.

`loop/evolve.py` needed no change — `EvolutionRun.tested` is a plain opaque
`set`, agnostic to whether its members are tuples or hash strings.

`tools/edit_bundle_module.py sync` regenerated the bundle's embedded
`_SRC['agents.researcher']` from the edited real file; `verify` and
`sync --check` both clean afterward.

New test file `tests/test_researcher_memory_hash.py` (7 tests): hash
stability and determinism, dict-order independence, `migrate_tested_entry`
is the identity on already-migrated (string) entries, migrating an
old-format entry lands on the *same* hash a fresh `key()` call on the
identical patch produces today (the actual correctness property — gets this
wrong and the migration silently forgets every pre-fix candidate, letting
the Researcher re-test them for free), a mixed old/new list migrates to
exactly one hash per distinct patch with no spurious loss or duplication,
and a synthetic 38-gene/2000-candidate set (matching item 12's own
description of a typical blind-perturbation patch) confirms the hash-based
list is more than 20x smaller than the old full-patch one.

## Applied the migration to the real `live_state.json`

Added `tools/migrate_tested_memory.py`: loads the account via
`core.live.LiveAccount`, replaces `researcher_memory["tested"]` with the
migrated hash set, and — before saving — refuses to write if the migration
changed the candidate count (would mean a same-patch hash collision or a
bug) or if any top-level key besides `researcher_memory`/`updated` changed.
Not required for correctness (the next real `evolve` invocation would
migrate-on-read and persist only hashes automatically, since every read site
above now does that) — run anyway to relieve the size pressure immediately
rather than waiting out however many more 3-hourly cycles until the next
evolve batch.

Result: `researcher_memory["tested"]` 17,710 entries before and after
(membership unchanged, confirmed by the script's own count check), JSON
size of that field 29,143,659 → 354,200 bytes (**82.3x smaller**).
`live_state.json` itself: **57.2MB → 7.2MB**. Direct top-level key diff
against the pre-migration file: only `researcher_memory` and `updated`
changed; `genome`, `broker`, `journal`, `lineage`, `hard_call_reviews`,
`started`, `ticks` byte-identical (checked directly, not just via the
script's own guard).

## Verification before commit

- `python3 -m pytest -q`: 422/422 (415 baseline + 7 new), run twice — once
  right after the code changes (before touching `live_state.json`), once
  again after the migration script ran against it.
- `python3 evotrader_bundle.py summary` and `... holdout-pressure`: both run
  clean against the migrated file — constitution verified `726dfa4bac85891a`,
  genome still v3, NAV/positions/holdout-pressure counts all sane (200
  generations, 114 real holdout draws, unchanged from before the migration).
- `tools/edit_bundle_module.py verify` / `sync --check`: both clean.
- Dashboard rebuilt (`index.html`) — diff is only the `updated` timestamp and
  a randomized SVG gradient element id, no data change.
- Constitution untouched (`evotrader.manifest` `726dfa4bac85891a` unchanged;
  neither `constitution/` nor `core/portfolio.py` touched).

Genome still v3 (1d) live, unchanged. No trading this cycle.

## Not done / left for a future session

`AGENTS.md` item 12 asked for "a regression test asserting
`researcher_memory["tested"]` shrinks by roughly the expected factor on a
save/load round-trip against a synthetic large `tested` set" — covered by
`test_hash_based_tested_list_is_much_smaller_than_full_patch_list` above,
plus the direct 82.3x measurement against the real account. Considering item
12 closed: root cause fixed at every read/write site, real migration applied
and verified byte-for-byte, tests added and passing, `live_state.json` no
longer on a collision course with GitHub's push limit (7.2MB now vs. the
57.2MB that triggered the warning, and future growth is bounded by candidate
*count* rather than *patch size* — 200 generations/17,710 candidates cost
~354KB instead of ~29MB).
