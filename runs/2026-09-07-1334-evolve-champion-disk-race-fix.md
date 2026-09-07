# 2026-09-07 ~12:46-13:34 UTC — 3-hourly check: real evolve-vs-`Genome.champion()` disk race found and fixed

## What happened

Freshness checks at the start of this cycle: `review-hard-calls` 0 pending,
items 2/5/6 still blocked with no new owner input, last activity was the
10:31 UTC evolve batch (`updated` timestamp), today's daily bar already
handled at 00:20 UTC. Decided to run another 15-generation `evolve` batch
against the live v3 champion, the same action the last dozen-plus cycles
have taken.

Started the pre-commit `python3 -m pytest -q` baseline and the `evolve 15`
batch as two background processes close together (a mistake — see below).
The evolve batch finished in ~30s (suspiciously fast for 15 real generations)
and printed `champion v1` on every single generation, ending with
`[evolve] champion promoted to v1` — i.e. it silently treated the account's
**original 2026-08-15 seed genome** as the live champion for the entire run,
not the real v3 champion (34 promotions/generations and one v1->v2, one
v2->v3 promotion later). `git diff --stat` on the resulting `live_state.json`
showed a ~614k-line swing. **Not committed** — caught immediately by
checking `genome.version` after the run.

## Root cause

`loop.evolve.EvolutionRun.run()` (and, before this fix, `evotrader_bundle.py`
`main()`'s `evolve` command handler and both `run_from_files.py` evolve
commands) got the genome to evolve from **`core.genome.Genome.champion()`**
— a disk read of the shared, unsandboxed `state/genomes/champion.json` file —
instead of using the genome object already in memory. The live `evolve`
command's own convention was to call `g0.save("champion")` immediately
before constructing the run, relying on nothing else touching that file in
the window between that write and `run()`'s own read. That assumption broke:
this session's own `pytest -q`, run concurrently, exercises
`tests/test_run_from_files_matches_bundle.py`'s `synthetic_universe_4y`
fixture, which legitimately (and normally safely, it backs up and restores
the directory) runs a real `EvolutionRun` against a **fake seed-version
genome** and writes real archive files under the same `state/genomes/`
during the test — including, transiently, `champion.json` itself. My evolve
process's `run()` call happened to land inside that window and read back the
wrong genome — a variant of the exact bug already fixed 2026-09-06 for
`_reconstruct_champion_genome`'s version-1 base (see AGENTS.md's "Current
state" that day), except that fix only touched the read-only reconstruction
helper, not the live promotion path itself, and not `promotion-excess-check`
either (found the same still-present pattern there while auditing every
`Genome.champion()` call site — see below).

**This was a real risk to the live account, not just a wasted batch**: if
any candidate in that confused run had cleared the (also-confused, wrong-
champion) gate, `main()`'s own post-run check — `final = Genome.champion()`
— would have read back whatever `state/genomes/champion.json` held at that
moment and written it into `live_state.json` as a "promotion," potentially
overwriting the real v3 lineage with a fabricated one. It didn't happen this
time only because no candidate cleared the (also wrong) bar in 15
generations.

## Fix

Audited every `Genome.champion()` call site in production code
(`grep -rn "Genome\.champion()"` across real files, not the bundle's
embedded copies) and closed the two still-open ones:

1. **`loop.evolve.EvolutionRun`** now takes an explicit `champion: Genome`
   constructor argument, threaded through in memory for the life of the run.
   `run()` no longer calls `Genome.champion()` at all; it starts from
   `self.champion` and returns the actual final `Genome` object in its result
   dict (`res["final_genome"]`), not just a version int.
2. **`evotrader_bundle.py`'s `main()` `evolve` command** and **both
   `run_from_files.py` evolve commands** (`_cmd_evolve_dry_run`,
   `_cmd_evolve`) now pass `champion=g0` into `EvolutionRun(...)` and read
   `res["final_genome"]` instead of a second `Genome.champion()` disk read at
   the end. Both disk-read points that made the promotion decision
   dependent on shared external state are gone; the decision is now made
   entirely from data already in memory.
3. **`promotion-excess-check`** (in `evotrader_bundle.py`, not part of any
   `_SRC` module) still had `genome_cache = {1: Genome.champion()}` —
   exactly the pattern the 2026-08-16/2026-09-06 fix history already flagged
   and fixed in `_reconstruct_champion_genome` — changed to
   `Genome()` (hardcoded seed, no disk I/O), matching every other
   reconstruction call site. This is a read-only diagnostic (never touches
   `live_state.json`), so this half of the fix is a correctness fix for that
   command's own output, not a live-account safety fix — but it was silently
   wrong under the exact same "ran after an `evolve` call in the same
   container" condition documented in AGENTS.md's 2026-09-06 entry, and had
   evidently not actually been fixed despite being covered by that entry's
   language.
4. `g0.save("champion")` at the top of each evolve command is kept — it was
   never the unsafe half of the pattern, and other tooling / manual
   inspection may still find it useful as a point-in-time archive.

`tools/edit_bundle_module.py sync` re-generated the bundle's embedded
`_SRC['loop.evolve']` from the real `loop/evolve.py`; `verify` and
`sync --check` both confirmed a clean round-trip. `evotrader_bundle.py`'s
own `main()`/`promotion-excess-check` code (plain script code, not part of
any `_SRC` module) was edited directly.

## Verification

- Full suite: `python3 -m pytest -q` **366/366**, unchanged pass count (this
  is a pure refactor of how a genome is passed around, not new coverage —
  no new test added this cycle; the existing `test_run_from_files_matches_bundle.py`
  evolve/evolve-dry-run tests already exercise these exact code paths
  end-to-end via subprocess and passed).
- Re-ran the three most relevant files in isolation after the fix:
  `test_run_from_files_matches_bundle.py` + `test_genome.py` +
  `test_fold_scheme_reconstruction.py`, **30/30 passed**.
- `tools/edit_bundle_module.py verify` clean, `sync --check` clean,
  `py_compile` on all three touched files clean.
- `live_state.json` **never modified** by this cycle's work — `git status`
  before commit shows only the three source files
  (`evotrader_bundle.py`, `loop/evolve.py`, `run_from_files.py`) changed.
  The corrupted state from the race was caught before any commit and
  discarded with `git checkout -- live_state.json` (restored the real v3
  state byte-for-byte, confirmed via `git show HEAD:live_state.json`).
- `python3 evotrader_bundle.py summary` after the fix: constitution
  `8b74865634b1db07` unchanged, genome version 3, ticks 24 — live account
  exactly as it was before this cycle started. No live trading this cycle
  (today's bar already handled at 00:20 UTC).
- Not one of the two checksummed files (`constitution`, `core.portfolio`),
  so no manifest re-seal needed.

## Process note for future sessions

**Never run `pytest -q` and a real `evolve`/`evolve-dry-run` invocation
concurrently in the same container**, even though nothing in AGENTS.md
previously said not to. `tests/test_run_from_files_matches_bundle.py`
deliberately (and, in isolation, safely) exercises the real evolution loop
against `state/genomes/` — the same shared, non-test-isolated directory a
live `evolve` run's `Genome.champion()`/`.save("champion")` calls used to
depend on. Running the two at the same time is exactly the race this cycle
hit. This fix removes the live path's dependency on that shared file
entirely, so the specific failure mode here cannot recur even if the two are
run concurrently again — but there is no similar guarantee for whatever the
next thing that touches `state/genomes/` turns out to be, so keep them
sequential regardless. This cycle ran pytest and evolve sequentially after
the fix, specifically to avoid re-triggering anything not yet caught by
this find.

No 15-generation evolve batch actually landed this cycle (the corrupted one
was discarded, and the remaining time went to root-causing and fixing this
instead) — cumulative candidates tried against v3 remain unchanged at 4551
from the 10:31 UTC batch. Next cycle should resume normal evolve batches
against the real v3 champion, now safe from this specific race.
