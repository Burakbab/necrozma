# AGENTS.md archive — 2026-11-12 entries

Verbatim slice moved out of `AGENTS.md`'s "Current state" chronological log
by the 2026-11-14 weekend all-hands, to keep that file under its 256KB
single-read limit. Nothing reworded, nothing lost. These are all nine
3-hourly-check entries dated 2026-11-12. See `AGENTS.md` for the full index
of older archives and the current log.

---

- **Run 2026-11-12 (3-hourly check, ~21:47-22:18 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 113811 → 114018 (per
  `researcher_memory.tested`), stagnation/boldness counter 8252 → 8267.**
  No live trading this cycle (tick 90 already handled at the dedicated
  00:20 UTC daily slot, and the 20:30 UTC daily evaluation and the prior
  3-hourly check's own evolve batch already ran at ~18:48-19:26 UTC —
  confirmed via `live_state.json`'s `updated` timestamp at session start,
  `2026-11-12T19:09:00+00:00`, matching `runs/2026-11-12-1926-evolve-batch-v3.md`).
  Freshness checks: `review-hard-calls` still 0 pending (6 reviewed,
  unchanged), items 6/13 still owner decisions, `AGENTS.md` size 242,372
  bytes at session start — ~13.6KB under the 256KB threshold, a margin
  recent sessions have judged wide enough to skip archival, not archived
  this cycle — so, with nothing else queued, used the slot for one more
  real 15-generation batch via `tools/background_runner.py` (`start` +
  separate `wait`), run after a baseline `pytest` pass, exit code 0, no
  truncation. Champion's fold-aggregate fitness held flat at 1.691 across
  all 15 generations (977 trades, 37% win, 1% stops, 4 halts, unchanged
  throughout). Best-of-generation fold-fitness ranged roughly 1.184-2.135,
  never clearing the promotion-margin bar. See
  `runs/2026-11-12-2218-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 505/505 both before (baseline) and after `evolve`;
  top-level key diff of `live_state.json` (snapshotted before `start`,
  checked directly in Python against the pre-batch copy) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  `holdout-pressure` re-checked post-batch — margin essentially flat
  (7.807 → 7.809), draw count 2034 → 2043 (nine new sealed-holdout draws
  from this batch's fold-aggregate-gate-clearing candidates, all correctly
  rejected), same slow-rise pattern already tracked under item 13, nothing
  new; dashboard rebuilt with `EVO_STATE` set (`index.html` shows 114018
  challenger idea(s) tried). Genome still v3 (1d) live, untouched. Container
  synced cleanly from `main` via `git checkout main` + `python3
  tools/git_sync.py` fast-forward through other sessions' 2026-11-12
  commits already pushed, no divergence, no shallow-clone staleness this
  cycle.

- **Run 2026-11-12 (3-hourly check, ~18:48-19:26 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 113603 → 113811 (per
  `researcher_memory.tested`), stagnation/boldness counter 8237 → 8252.**
  No live trading this cycle (tick 90 already handled at the dedicated
  00:20 UTC daily slot, and the prior 3-hourly check's own evolve batch
  already ran at ~15:48-16:12 UTC — confirmed via `live_state.json`'s
  `updated` timestamp at session start, `2026-11-12T16:09:41+00:00`,
  matching `runs/2026-11-12-1612-evolve-batch-v3.md`). Freshness checks:
  `review-hard-calls` still 0 pending (6 reviewed, unchanged), items 6/13
  still owner decisions, `AGENTS.md` size 239,957 bytes at session start —
  comfortably under the 256KB threshold, not archived this cycle — so, with
  nothing else queued, used the slot for one more real 15-generation batch
  via `tools/background_runner.py` (`start` + separate `wait`), run after a
  baseline `pytest` pass, exit code 0, no truncation. Champion's
  fold-aggregate fitness held flat at 1.691 across all 15 generations (977
  trades, 37% win, 1% stops, 4 halts, unchanged throughout). Best-of-generation
  fold-fitness ranged roughly 1.259-2.020, never clearing the
  promotion-margin bar. See `runs/2026-11-12-1926-evolve-batch-v3.md`.
  Verified before commit: `python3 -m pytest -q` 505/505 both before
  (baseline) and after `evolve`; top-level key diff of `live_state.json`
  (snapshotted before `start`, checked directly in Python against the
  pre-batch copy) showed only `updated`/`researcher_memory`/`lineage`
  changed (genome, broker, journal, hard_call_reviews byte-identical);
  `lineage` length unchanged at 202 (bounded ring buffer, no new promotion
  attempt recorded); `tools/edit_bundle_module.py verify`/`sync --check`
  both clean; `holdout-pressure` re-checked post-batch — margin and draw
  count both unchanged (7.809, 2042) since no candidate this batch cleared
  the fold-aggregate gate; dashboard rebuilt with `EVO_STATE` set
  (`index.html` shows 113811 challenger idea(s) tried). Genome still v3 (1d)
  live, untouched. Container synced cleanly from `main` via `git checkout
  main` + `python3 tools/git_sync.py` fast-forward through other sessions'
  2026-11-12 commits already pushed, no divergence, no shallow-clone
  staleness this cycle.

- **Run 2026-11-12 (3-hourly check, ~15:48-16:12 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 113397 → 113603 (per
  `researcher_memory.tested`), stagnation/boldness counter 8222 → 8237.**
  No live trading this cycle (tick 90 already handled at the dedicated
  00:20 UTC daily slot, and the prior 3-hourly check's own evolve batch
  already ran at ~12:48-13:10 UTC — confirmed via `live_state.json`'s
  `updated` timestamp at session start, `2026-11-12T13:09:31+00:00`,
  matching `runs/2026-11-12-1310-evolve-batch-v3.md`). Freshness checks:
  `review-hard-calls` still 0 pending (6 reviewed, unchanged), items 6/13
  still owner decisions, `AGENTS.md` size 237,402 bytes at session start —
  comfortably under the 256KB threshold, not archived this cycle — so, with
  nothing else queued, used the slot for one more real 15-generation batch
  via `tools/background_runner.py` (`start` + separate `wait`), run after a
  baseline `pytest` pass, exit code 0, no truncation. Champion's
  fold-aggregate fitness held flat at 1.691 across all 15 generations (977
  trades, 37% win, 1% stops, 4 halts, unchanged throughout). Best-of-generation
  fold-fitness ranged roughly 1.575-2.629, never clearing the
  promotion-margin bar. See `runs/2026-11-12-1612-evolve-batch-v3.md`.
  Verified before commit: `python3 -m pytest -q` 505/505 both before
  (baseline) and after `evolve`; top-level key diff of `live_state.json`
  (snapshotted before `start`, checked directly in Python against the
  pre-batch copy) showed only `updated`/`researcher_memory`/`lineage`
  changed (genome, broker, journal, hard_call_reviews byte-identical);
  `lineage` length unchanged at 202 (bounded ring buffer, no new promotion
  attempt recorded); `tools/edit_bundle_module.py verify`/`sync --check`
  both clean; `holdout-pressure` re-checked post-batch — margin essentially
  flat (7.808 → 7.809), draw count 2040 → 2042 (two new sealed-holdout draws
  from this batch's fold-aggregate-gate-clearing candidates, both correctly
  rejected), same slow-rise pattern already tracked under item 13, nothing
  new; dashboard rebuilt with `EVO_STATE` set (`index.html` shows 113603
  challenger idea(s) tried). Genome still v3 (1d) live, untouched. Container
  synced cleanly from `main` via `git checkout main` + `python3
  tools/git_sync.py` fast-forward through other sessions' 2026-11-12
  commits already pushed, no divergence, no shallow-clone staleness this
  cycle.

- **Run 2026-11-12 (3-hourly check, ~12:48-13:10 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 113193 → 113397 (per
  `researcher_memory.tested`), stagnation/boldness counter 8206 → 8221.**
  No live trading this cycle (tick 90 already handled at the dedicated
  00:20 UTC daily slot, and the prior 3-hourly check's own evolve batch
  already ran at ~09:48-10:15 UTC — confirmed via `live_state.json`'s
  `updated` timestamp at session start, `2026-11-12T10:12:48+00:00`,
  matching `runs/2026-11-12-1015-evolve-batch-v3.md`). Freshness checks:
  `review-hard-calls` still 0 pending (6 reviewed, unchanged), items 6/13
  still owner decisions, `AGENTS.md` size 234,853 bytes at session start —
  comfortably under the 256KB threshold, not archived this cycle — so, with
  nothing else queued, used the slot for one more real 15-generation batch
  via `tools/background_runner.py` (`start` + separate `wait`), run after a
  baseline `pytest` pass, exit code 0, no truncation. Champion's
  fold-aggregate fitness held flat at 1.691 across all 15 generations (977
  trades, 37% win, 1% stops, 4 halts, unchanged throughout). Best-of-generation
  fold-fitness ranged roughly 1.336-2.629, never clearing the
  promotion-margin bar. See `runs/2026-11-12-1310-evolve-batch-v3.md`.
  Verified before commit: `python3 -m pytest -q` 505/505 both before
  (baseline) and after `evolve`; top-level key diff of `live_state.json`
  (snapshotted before `start`, checked directly in Python against the
  pre-batch copy) showed only `updated`/`researcher_memory`/`lineage`
  changed (genome, broker, journal, hard_call_reviews byte-identical);
  `lineage` length unchanged at 202 (bounded ring buffer, no new promotion
  attempt recorded); `tools/edit_bundle_module.py verify`/`sync --check`
  both clean; `holdout-pressure` re-checked post-batch — margin essentially
  flat (7.808 → 7.808), draw count 2040 → 2041 (one new sealed-holdout draw
  from this batch's fold-aggregate-gate-clearing candidates, correctly
  rejected), same slow-rise pattern already tracked under item 13, nothing
  new; dashboard rebuilt with `EVO_STATE` set (`index.html` shows 113397
  challenger idea(s) tried). Genome still v3 (1d) live, untouched. Container
  synced cleanly from `main` via `git checkout main` + `python3
  tools/git_sync.py` fast-forward through other sessions' 2026-11-12
  commits already pushed, no divergence, no shallow-clone staleness this
  cycle.

- **Run 2026-11-12 (3-hourly check, ~09:48-10:15 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 112986 → 113193 (per
  `researcher_memory.tested`), stagnation/boldness counter 8192 → 8206.**
  No live trading this cycle (tick 90 already handled at the dedicated
  00:20 UTC daily slot, and the prior 3-hourly check's own evolve batch
  already ran at ~06:47-07:20 UTC — confirmed via `live_state.json`'s
  `updated` timestamp at session start, `2026-11-12T07:15:03+00:00`,
  matching `runs/2026-11-12-0720-evolve-batch-v3.md`). Freshness checks:
  `review-hard-calls` still 0 pending (6 reviewed, unchanged), items 6/13
  still owner decisions, `AGENTS.md` size 232,262 bytes at session start —
  comfortably under the 256KB threshold (~24KB margin, wider than most
  prior rotations in this index have used to trigger one), not archived
  this cycle — so, with nothing else queued, used the slot for one more
  real 15-generation batch via `tools/background_runner.py` (`start` +
  separate `wait`), run after a baseline `pytest` pass, exit code 0, no
  truncation. Champion's fold-aggregate fitness held flat at 1.691 across
  all 15 generations (977 trades, 37% win, 1% stops, 4 halts, unchanged
  throughout). Best-of-generation fold-fitness ranged roughly 1.447-2.629 —
  several candidates scored above the champion's own raw fitness but still
  didn't clear the multiple-testing-adjusted bar. See
  `runs/2026-11-12-1015-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 505/505 both before (baseline) and after `evolve`;
  top-level key diff of `live_state.json` (snapshotted before `start`,
  checked directly in Python against the pre-batch copy) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  `holdout-pressure` re-checked post-batch — margin and draw count both
  unchanged (7.808, 2040) since no candidate this batch cleared the
  fold-aggregate gate; dashboard rebuilt with `EVO_STATE` set (`index.html`
  shows 113193 challenger idea(s) tried). Genome still v3 (1d) live,
  untouched. Container synced cleanly from `main` via `git checkout main` +
  `python3 tools/git_sync.py` fast-forward through other sessions'
  2026-11-12 commits already pushed, no divergence, no shallow-clone
  staleness this cycle.

- **Run 2026-11-12 (3-hourly check, ~06:47-07:20 UTC): archived the oldest
  remaining AGENTS.md slice, then 15 more real `evolve` generations against
  the live v3 (1d) champion, no promotion — cumulative candidates tried
  against v3 rose 112779 → 112986 (per `researcher_memory.tested`),
  stagnation/boldness counter 8177 → 8191.** No live trading this cycle
  (tick 90 already handled at the dedicated 00:20 UTC daily slot, and the
  prior 3-hourly check's own evolve batch already ran at ~03:46-04:17 UTC —
  confirmed via `live_state.json`'s `updated` timestamp at session start,
  `2026-11-12T04:11:34+00:00`, matching `runs/2026-11-12-0417-evolve-batch-v3.md`).
  `AGENTS.md` size at session start was 250,290 bytes — within ~5.7KB of
  the 256KB threshold, within the margin range every prior rotation in
  this index has used to trigger one — so archived the oldest remaining
  slice (all nine 2026-11-10 entries) verbatim to new
  `AGENTS_ARCHIVE_2026-11-10.md` first, cutting the live file to 229,207
  bytes; verified via exact line-range removal (the removed 313-line
  block diffed byte-for-byte identical against the new archive file's
  body) and `python3 -m pytest -q` 505/505 unaffected. Committed and
  pushed as `9d5d2e3` before starting evolve work. Freshness checks:
  `review-hard-calls` still 0 pending (6 reviewed, unchanged), items 6/13
  still owner decisions. Then, with nothing else queued, used the slot for
  one more real 15-generation batch via `tools/background_runner.py`
  (`start` + separate `wait`), run after a baseline `pytest` pass, exit
  code 0, no truncation. Champion's fold-aggregate fitness held flat at
  1.691 across all 15 generations (977 trades, 37% win, 1% stops, 4 halts,
  unchanged throughout). Best-of-generation fold-fitness ranged roughly
  1.629-2.429, never clearing the promotion-margin bar. See
  `runs/2026-11-12-0720-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 505/505 both before (baseline, right after the
  archival commit) and after `evolve`; top-level key diff of
  `live_state.json` (snapshotted before `start`, checked directly in
  Python against the pre-batch copy) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker,
  journal, hard_call_reviews byte-identical); `lineage` length unchanged
  at 202 (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  `holdout-pressure` re-checked post-batch — margin essentially flat
  (7.807 → 7.808), draw count 2034 → 2040 (six new sealed-holdout draws
  from this batch's fold-aggregate-gate-clearing candidates, all correctly
  rejected), same slow-rise pattern already tracked under item 13, nothing
  new; dashboard rebuilt with `EVO_STATE` set (`index.html` shows 112986
  challenger idea(s) tried). Genome still v3 (1d) live, untouched.
  Container synced cleanly from `main` via `git checkout main` + `python3
  tools/git_sync.py`, no divergence, no shallow-clone staleness this
  cycle.

- **Run 2026-11-12 (3-hourly check, ~03:46-04:17 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 112576 → 112779 (per
  `researcher_memory.tested`), stagnation/boldness counter 8162 → 8176.**
  No live trading this cycle (tick 90 already handled at the dedicated
  00:20 UTC daily slot, and the prior 3-hourly check's own evolve batch
  already ran at ~00:47-01:17 UTC — confirmed via `live_state.json`'s
  `updated` timestamp at session start, `2026-11-12T01:14:53+00:00`,
  matching `runs/2026-11-12-0117-evolve-batch-v3.md`). Freshness checks:
  `review-hard-calls` still 0 pending (6 reviewed, unchanged), items 6/13
  still owner decisions, `AGENTS.md` size 247,631 bytes at session start —
  within ~14.2KB of the 256KB threshold, a wider margin than most prior
  rotations in this index have used to trigger one, so not archived this
  cycle — so, with nothing else queued, used the slot for one more real
  15-generation batch via `tools/background_runner.py` (`start` + separate
  `wait`), run after a baseline `pytest` pass, exit code 0, no truncation.
  Champion's fold-aggregate fitness held flat at 1.691 across all 15
  generations (977 trades, 37% win, 1% stops, 4 halts, unchanged
  throughout). Best-of-generation fold-fitness ranged roughly 1.252-2.629,
  never clearing the promotion-margin bar. See
  `runs/2026-11-12-0417-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 505/505 both before (baseline) and after `evolve`;
  top-level key diff of `live_state.json` (snapshotted before `start`,
  checked directly in Python against the pre-batch copy) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  `holdout-pressure` re-checked post-batch — margin rose slightly
  (7.804 → 7.808), draw count 2034 → 2039 (five new sealed-holdout draws
  from this batch's fold-aggregate-gate-clearing candidates, all correctly
  rejected), same slow-rise pattern already tracked under item 13, nothing
  new; dashboard rebuilt with `EVO_STATE` set (`index.html` shows 112779
  challenger idea(s) tried). Genome still v3 (1d) live, untouched. Container
  synced cleanly from `main` via `git checkout main` + `python3
  tools/git_sync.py` fast-forward through other sessions' 2026-11-09/11-10/
  11-11/11-12 commits already pushed, no divergence, no shallow-clone
  staleness this cycle.

- **Run 2026-11-12 (3-hourly check, ~00:47-01:17 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 112368 → 112576 (per
  `researcher_memory.tested`), stagnation/boldness counter 8147 → 8161.**
  No live trading this cycle (tick 90 already handled at the dedicated
  00:20 UTC daily slot — confirmed via `live_state.json`'s `updated`
  timestamp at session start, `2026-11-12T00:22:01+00:00`, matching
  `runs/2026-11-12-0020-daily-trading.md`). Freshness checks:
  `review-hard-calls` still 0 pending (6 reviewed, unchanged), items 6/13
  still owner decisions, `AGENTS.md` size 244,986 bytes at session start —
  comfortably under the 256KB threshold, not archived this cycle — so, with
  nothing else queued, used the slot for one more real 15-generation batch
  via `tools/background_runner.py` (`start` + separate `wait`), run after a
  baseline `pytest` pass, exit code 0, no truncation. Champion's
  fold-aggregate fitness held flat at 1.691 across all 15 generations (977
  trades, 37% win, 1% stops, 4 halts, unchanged throughout). Best-of-generation
  fold-fitness ranged roughly 1.613-2.629, never clearing the
  promotion-margin bar. See `runs/2026-11-12-0117-evolve-batch-v3.md`.
  Verified before commit: `python3 -m pytest -q` 505/505 both before
  (baseline) and after `evolve`; top-level key diff of `live_state.json`
  (snapshotted before `start`, checked directly in Python against the
  pre-batch copy) showed only `updated`/`researcher_memory`/`lineage`
  changed (genome, broker, journal, hard_call_reviews byte-identical);
  `lineage` length unchanged at 202 (bounded ring buffer, no new promotion
  attempt recorded); `tools/edit_bundle_module.py verify`/`sync --check`
  both clean; `holdout-pressure` re-checked post-batch — margin rose
  slightly (7.807 → 7.808), draw count 2034 → 2038 (four new sealed-holdout
  draws from this batch's fold-aggregate-gate-clearing candidates, all
  correctly rejected), same slow-rise pattern already tracked under item
  13, nothing new; dashboard rebuilt with `EVO_STATE` set (`index.html`
  shows 112576 challenger idea(s) tried). Genome still v3 (1d) live,
  untouched. Container synced cleanly from `main` via `git checkout main` +
  `python3 tools/git_sync.py` fast-forward through other sessions'
  2026-11-11/11-12 commits already pushed, no divergence, no shallow-clone
  staleness this cycle. Hit the recurring `pip3` vs `python3 -m pip`
  numpy/pandas split again — `python3 -m pip install -r requirements.txt -q`
  fixed it immediately, same as prior sessions.
