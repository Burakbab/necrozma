# AGENTS.md archive: 2026-09-29

Archived verbatim from AGENTS.md's "Current state" log on 2026-10-04
(weekend all-hands) to keep the live file under its 256KB single-read
limit. Nothing reworded, nothing lost — see AGENTS.md itself for
everything from 2026-09-30 onward, and AGENTS_ARCHIVE_2026-09-28.md for
anything older.

- **Run 2026-09-29 (3-hourly check, ~21:45-22:17 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 40182 → 40389 (per
  `researcher_memory.tested`), stagnation/boldness counter 2899 → 2913.** No
  live trading this cycle (tick 46 already handled at the dedicated 00:20
  UTC daily slot, and the prior 3-hourly check's own evolve batch already
  ran at ~19:15 UTC — confirmed via `live_state.json`'s `updated` timestamp
  at session start, `2026-09-29T19:15:26+00:00`, matching
  `runs/2026-09-29-1918-evolve-batch-v3.md`, and the 20:30 UTC daily
  evaluation, `runs/2026-09-29-2030-daily-evaluation.md`, already-recorded/
  read-only). Freshness checks before running: `review-hard-calls` still 0
  pending (4 reviewed, unchanged), items 6/13 still owner decisions,
  `AGENTS.md` size 247,651 bytes — comfortably under the 256KB threshold —
  so, with nothing else queued, used the slot for one more real
  15-generation batch via `tools/background_runner.py` (`start` + separate
  `wait`), exit code 0, no truncation, ~32 minutes. Champion's
  fold-aggregate fitness held flat at 1.053 across all 15 generations (975
  trades, 37% win, 1% stops, 4 halts, unchanged throughout). Best-of-generation
  fold-fitness ranged 1.423-2.208, never clearing the promotion-margin bar.
  See `runs/2026-09-29-2217-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 441/441 both before (baseline) and after `evolve`;
  top-level key diff of `live_state.json` (checked directly in Python
  against `git show HEAD:live_state.json`, not just eyeballed) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  `holdout-pressure` re-checked (read-only, no state change) — margin rose
  slightly (7.388, was 7.379) at draw 918, same slow-rise pattern already
  tracked under item 13, nothing new; dashboard rebuilt with `EVO_STATE` set
  (`index.html` shows 40389 challenger ideas tried). Genome still v3 (1d)
  live, untouched. Container arrived detached HEAD 44 commits behind
  `origin/main`; `git checkout main` plus `tools/git_sync.py` fast-forwarded
  cleanly, nothing lost.

- **Run 2026-09-29 (3-hourly check, ~18:47-19:13 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 39975 → 40182 (per
  `researcher_memory.tested`), stagnation/boldness counter 2884 → 2898.** No
  live trading this cycle (tick 46 already handled at the dedicated 00:20
  UTC daily slot, and the prior 3-hourly check's own evolve batch already
  ran at ~15:47-16:18 UTC — confirmed via `live_state.json`'s `updated`
  timestamp at session start, `2026-09-29T16:17:30+00:00`, matching
  `runs/2026-09-29-1618-evolve-batch-v3.md`). Freshness checks before
  running: `review-hard-calls` still 0 pending (4 reviewed, unchanged),
  items 6/13 still owner decisions, `AGENTS.md` size 245,341 bytes —
  comfortably under the 256KB threshold — so, with nothing else queued,
  used the slot for one more real 15-generation batch via
  `tools/background_runner.py` (`start` + separate `wait`), exit code 0, no
  truncation, ~26 minutes. Champion's fold-aggregate fitness held flat at
  1.053 across all 15 generations (975 trades, 37% win, 1% stops, 4 halts,
  unchanged throughout). Best-of-generation fold-fitness ranged 1.416-1.848,
  never clearing the promotion-margin bar. See
  `runs/2026-09-29-1918-evolve-batch-v3.md`. Verified before commit: `python3
  -m pytest -q` 441/441 both before (baseline) and after `evolve`; top-level
  key diff of `live_state.json` (checked directly in Python against `git
  show HEAD:live_state.json`, not just eyeballed) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  `holdout-pressure` re-checked (read-only, no state change) — margin rose
  slightly (7.375, was 7.362) at draw 896, same slow-rise pattern already
  tracked under item 13, nothing new; dashboard rebuilt with `EVO_STATE` set
  (`index.html` shows 40182 challenger ideas tried). Genome still v3 (1d)
  live, untouched. Container arrived detached HEAD 44 commits behind
  `origin/main`; `git checkout main` plus `tools/git_sync.py` fast-forwarded
  cleanly, nothing lost.

- **Run 2026-09-29 (3-hourly check, ~15:47-16:18 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 39767 → 39975 (per
  `researcher_memory.tested`), stagnation/boldness counter 2869 → 2883.** No
  live trading this cycle (tick 46 already handled at the dedicated 00:20
  UTC daily slot, and the prior 3-hourly check's own evolve batch already
  ran at ~12:47-13:18 UTC — confirmed via `live_state.json`'s `updated`
  timestamp at session start, `2026-09-29T13:18:14+00:00`, matching
  `runs/2026-09-29-1315-evolve-batch-v3.md`). Freshness checks before
  running: `review-hard-calls` still 0 pending (4 reviewed, unchanged),
  items 6/13 still owner decisions, `AGENTS.md` size 243,031 bytes —
  comfortably under the 256KB threshold — so, with nothing else queued,
  used the slot for one more real 15-generation batch via
  `tools/background_runner.py` (`start` + separate `wait`), exit code 0, no
  truncation, ~31 minutes. Champion's fold-aggregate fitness held flat at
  1.053 across all 15 generations (975 trades, 37% win, 1% stops, 4 halts,
  unchanged throughout). Best-of-generation fold-fitness ranged 1.278-1.843,
  never clearing the promotion-margin bar. See
  `runs/2026-09-29-1618-evolve-batch-v3.md`. Verified before commit: `python3
  -m pytest -q` 441/441 both before (baseline) and after `evolve`; top-level
  key diff of `live_state.json` (checked directly in Python against `git
  show HEAD:live_state.json`, not just eyeballed) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  `holdout-pressure` re-checked (read-only, no state change) — margin rose
  slightly (7.362, was 7.352) at draw 876, same slow-rise pattern already
  tracked under item 13, nothing new; dashboard rebuilt with `EVO_STATE` set
  (`index.html` shows 39975 challenger ideas tried). Genome still v3 (1d)
  live, untouched. Container arrived detached HEAD 43 commits behind
  `origin/main`; `git checkout main` plus `tools/git_sync.py` fast-forwarded
  cleanly, nothing lost.

- **Run 2026-09-29 (3-hourly check, ~12:47-13:xx UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 39562 → 39767 (per
  `researcher_memory.tested`), stagnation/boldness counter 2854 → 2869.** No
  live trading this cycle (tick 46 already handled at the dedicated 00:20
  UTC daily slot, and the prior 3-hourly check's own evolve batch already
  ran at ~10:19 UTC — confirmed via `live_state.json`'s `updated` timestamp
  at session start, `2026-09-29T10:19:08+00:00`, matching
  `runs/2026-09-29-1021-evolve-batch-v3.md`). Freshness checks before
  running: `review-hard-calls` still 0 pending (4 reviewed, unchanged),
  items 6/13 still owner decisions, `AGENTS.md` size 240,735 bytes —
  comfortably under the 256KB threshold — so, with nothing else queued,
  used the slot for one more real 15-generation batch via
  `tools/background_runner.py` (`start` + separate `wait`), exit code 0, no
  truncation, ~15 minutes. Champion's fold-aggregate fitness held flat at
  1.053 across all 15 generations (975 trades, 37% win, 1% stops, 4 halts,
  unchanged throughout). Best-of-generation fold-fitness ranged 1.233-2.356,
  never clearing the promotion-margin bar. See
  `runs/2026-09-29-1315-evolve-batch-v3.md`. Verified before commit: `python3
  -m pytest -q` 441/441 both before (baseline) and after `evolve`; top-level
  key diff of `live_state.json` (checked directly in Python against a
  pre-batch snapshot, not just eyeballed) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  `holdout-pressure` re-checked (read-only, no state change) — margin rose
  slightly (7.352, was 7.344) at draw 859, same slow-rise pattern already
  tracked under item 13, nothing new; dashboard rebuilt with `EVO_STATE` set
  (`index.html` shows 39767 challenger ideas tried). Genome still v3 (1d)
  live, untouched. Container arrived detached HEAD at `origin/main`'s tip
  (`47b5df6`); `git checkout main` plus `tools/git_sync.py` fast-forwarded
  cleanly, nothing lost.

- **Run 2026-09-29 (3-hourly check, ~09:47-10:21 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 39355 → 39562 (per
  `researcher_memory.tested`), stagnation/boldness counter 2839 → 2853.** No
  live trading this cycle (tick 46 already handled at the dedicated 00:20
  UTC daily slot, and the prior 3-hourly check's own evolve batch already
  ran at ~07:31 UTC — confirmed via `live_state.json`'s `updated` timestamp
  at session start, `2026-09-29T07:31:12+00:00`, matching
  `runs/2026-09-29-0731-evolve-batch-v3.md` and the 09:00 UTC daily
  discussion note, `runs/2026-09-29-0900-daily-discussion.md`, both
  already-recorded/read-only). Freshness checks before running:
  `review-hard-calls` still 0 pending (4 reviewed, unchanged), items 6/13
  still owner decisions, `AGENTS.md` size 238,184 bytes — comfortably under
  the 256KB threshold (already rotated by the prior batch) — so, with
  nothing else queued, used the slot for one more real 15-generation batch
  via `tools/background_runner.py` (`start` + separate `wait`), exit code
  0, no truncation, ~30 minutes. Champion's fold-aggregate fitness held
  flat at 1.053 across all 15 generations (975 trades, 37% win, 1% stops,
  4 halts, unchanged throughout). Best-of-generation fold-fitness ranged
  1.412-2.448, never clearing the promotion-margin bar. See
  `runs/2026-09-29-1021-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 441/441 both before (baseline) and after `evolve`;
  top-level key diff of `live_state.json` (checked directly in Python
  against a pre-batch snapshot, not just eyeballed) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  `holdout-pressure` re-checked (read-only, no state change) — margin rose
  slightly (7.344, was 7.332) at draw 847, same slow-rise pattern already
  tracked under item 13, nothing new; dashboard rebuilt with `EVO_STATE` set
  (`index.html` shows 39562 challenger ideas tried). Genome still v3 (1d)
  live, untouched. Container arrived detached HEAD several commits behind
  `origin/main` (`fdc3373` → `6ce65ed`, ~20 commits from other scheduled
  sessions across 2026-09-27/28/29); `git checkout main` plus
  `tools/git_sync.py` fast-forwarded cleanly, nothing lost.

- **Run 2026-09-29 (3-hourly check, ~06:47-07:35 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 39147 → 39355 (per
  `researcher_memory.tested`), stagnation/boldness counter 2823 → 2838.** No
  live trading this cycle (tick 46 already handled at the dedicated 00:20
  UTC daily slot, and the prior 3-hourly check's own evolve batch already
  ran at ~04:24 UTC — confirmed via `live_state.json`'s `updated` timestamp
  at session start, `2026-09-29T04:19:55+00:00`, matching
  `runs/2026-09-29-0424-evolve-batch-v3.md`). Freshness checks before
  running: `review-hard-calls` still 0 pending (4 reviewed, unchanged),
  items 6/13 still owner decisions, `AGENTS.md` size 256,060 bytes — under
  the 256KB threshold (~6.1KB margin, tighter than usual, worth rotating
  soon but not done this cycle) — so, with nothing else queued, used the
  slot for one more real 15-generation batch via `tools/background_runner.py`
  (`start` + separate `wait`), exit code 0, no truncation, ~38 minutes.
  Champion's fold-aggregate fitness held flat at 1.053 across all 15
  generations (975 trades, 37% win, 1% stops, 4 halts, unchanged throughout).
  Best-of-generation fold-fitness ranged 1.423-2.298, never clearing the
  promotion-margin bar. See `runs/2026-09-29-0731-evolve-batch-v3.md`.
  Verified before commit: `python3 -m pytest -q` 441/441 both before
  (baseline) and after `evolve`; top-level key diff of `live_state.json`
  (checked directly in Python against `git show HEAD:live_state.json`, not
  just eyeballed) showed only `updated`/`researcher_memory`/`lineage`
  changed (genome, broker, journal, hard_call_reviews byte-identical);
  `lineage` length unchanged at 202 (bounded ring buffer, no new promotion
  attempt recorded); `tools/edit_bundle_module.py verify`/`sync --check`
  both clean; `holdout-pressure` re-checked (read-only, no state change) —
  margin rose slightly (7.332, was 7.316) at draw 828, same slow-rise
  pattern already tracked under item 13, nothing new; dashboard rebuilt
  with `EVO_STATE` set (`index.html` shows 39355 challenger ideas tried).
  Genome still v3 (1d) live, untouched. Container arrived several commits
  behind `origin/main` in detached HEAD; `git checkout main` reported "up
  to date" from a stale cached ref (recurring shallow-clone staleness), but
  an explicit `git fetch` showed `origin/main` had moved; `tools/git_sync.py`
  fast-forwarded cleanly (43 files, several days of prior sessions' work),
  nothing lost.

- **Run 2026-09-29 (3-hourly check, ~03:47-04:24 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 38945 → 39147 (per
  `researcher_memory.tested`), stagnation/boldness counter 2808 → 2823.** No
  live trading this cycle (tick 46 already handled at the dedicated 00:20
  UTC daily slot, and the prior 3-hourly check's own evolve batch already
  ran at ~01:14 UTC — confirmed via `live_state.json`'s `updated` timestamp
  at session start, `2026-09-29T01:12:14+00:00`, matching
  `runs/2026-09-29-0114-evolve-batch-v3.md`). Freshness checks before
  running: `review-hard-calls` still 0 pending (4 reviewed, unchanged),
  items 6/13 still owner decisions, `AGENTS.md` size 253,571 bytes — under
  the 256KB threshold (~8.5KB margin), worth continued watching but not
  rotated this cycle — so, with nothing else queued, used the slot for one
  more real 15-generation batch via `tools/background_runner.py` (`start` +
  separate `wait`), exit code 0, no truncation, ~35 minutes. Champion's
  fold-aggregate fitness held flat at 1.053 across all 15 generations (975
  trades, 37% win, 1% stops, 4 halts, unchanged throughout). Best-of-generation
  fold-fitness ranged 1.009-2.571, never clearing the promotion-margin bar.
  See `runs/2026-09-29-0424-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 441/441 both before (baseline) and after `evolve`;
  top-level key diff of `live_state.json` (checked directly in Python
  against `git show HEAD:live_state.json`, not just eyeballed) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  `holdout-pressure` re-checked (read-only, no state change) — margin rose
  slightly (7.316, was 7.301) at draw 805, same slow-rise pattern already
  tracked under item 13, nothing new; dashboard rebuilt with `EVO_STATE` set
  (`index.html` shows 39147 challenger ideas tried). Genome still v3 (1d)
  live, untouched. Container arrived several commits behind `origin/main` in
  detached HEAD; `git checkout main` plus `tools/git_sync.py` fast-forwarded
  cleanly (37 commits landed since this container's last checkpoint, all
  from other scheduled sessions across 2026-09-26/27/28), nothing lost.

- **Run 2026-09-29 (3-hourly check, ~00:46-01:14 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 38736 → 38945 (per
  `researcher_memory.tested`), stagnation/boldness counter 2794 → 2808.** No
  live trading this cycle (tick 46 already handled at the dedicated 00:20
  UTC daily slot — confirmed via `live_state.json`'s `updated` timestamp at
  session start, `2026-09-29T00:21:36+00:00`, matching
  `runs/2026-09-29-0020-daily-trading.md`; `46 % 7 == 4` so no `evolve` ran
  as part of that tick). Freshness checks before running: `review-hard-calls`
  still 0 pending (4 reviewed, unchanged), items 6/13 still owner decisions,
  `AGENTS.md` size 251,202 bytes — under the 256KB threshold but with less
  margin than usual (~4.8KB), worth a rotation soon but not done this cycle
  — so, with nothing else queued, used the slot for one more real
  15-generation batch via `tools/background_runner.py` (`start` + separate
  `wait`), exit code 0, no truncation, ~23 minutes. Champion's
  fold-aggregate fitness held flat at 1.053 across all 15 generations (975
  trades, 37% win, 1% stops, 4 halts, unchanged throughout). Best-of-generation
  fold-fitness ranged 1.358-1.945, never clearing the promotion-margin bar.
  See `runs/2026-09-29-0114-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 441/441 both before (baseline) and after `evolve`;
  top-level key diff of `live_state.json` (checked directly in Python
  against `git show HEAD:live_state.json`, not just eyeballed) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  `holdout-pressure` re-checked (read-only, no state change) — margin rose
  slightly (7.301, was 7.288) at draw 783, same slow-rise pattern already
  tracked under item 13, nothing new; dashboard rebuilt with `EVO_STATE` set
  (`index.html` shows 38945 challenger ideas tried). Genome still v3 (1d)
  live, untouched. Container synced cleanly this cycle: `git checkout main`
  plus `tools/git_sync.py` fast-forwarded from several commits behind with
  no divergence, nothing lost.
