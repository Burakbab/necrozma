# AGENTS.md archive — 2026-11-13 entries

Verbatim slice moved out of `AGENTS.md`'s "Current state" chronological log
by the 2026-11-15 3-hourly check, to keep that file under its 256KB
single-read limit. Nothing reworded, nothing lost. These are all nine
3-hourly-check entries dated 2026-11-13, including that day's own embedded
archival-action entry (the 2026-11-13 ~09:48 UTC archiving of the
2026-11-11 slice into `AGENTS_ARCHIVE_2026-11-11.md`). See `AGENTS.md` for
the full index of older archives and the current log.

---

- **Run 2026-11-13 (3-hourly check, ~21:46-22:20 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 115504 → 115709 (per
  `researcher_memory.tested`), stagnation/boldness counter 8374 → 8389.**
  No live trading this cycle (tick 91 already handled at the dedicated
  00:20 UTC daily slot, and the 20:30 UTC daily evaluation and the prior
  3-hourly check's own evolve batch already ran at ~18:47-19:11 UTC —
  confirmed via `live_state.json`'s `updated` timestamp at session start,
  `2026-11-13T19:10:15+00:00`, matching `runs/2026-11-13-1917-evolve-batch-v3.md`).
  Freshness checks: `review-hard-calls` still 0 pending (6 reviewed,
  unchanged), items 6/13 still owner decisions, `AGENTS.md` size 242,995
  bytes at session start — ~18.7KB under the 256KB threshold, a margin
  recent sessions have judged comfortable enough to skip archival, not
  archived this cycle — so, with nothing else queued, used the slot for
  one more real 15-generation batch via `tools/background_runner.py`
  (`start` + separate `wait`), run after a baseline `pytest` pass, exit
  code 0, no truncation. Champion's fold-aggregate fitness held flat at
  1.773 across all 15 generations (981 trades, 38% win, 1% stops, 3 halts,
  unchanged throughout). Best-of-generation fold-fitness ranged roughly
  1.295-2.213, never clearing the promotion-margin bar. See
  `runs/2026-11-13-2200-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 505/505 both before (baseline) and after `evolve`;
  top-level key diff of `live_state.json` (snapshotted before `start`,
  checked directly in Python against the pre-batch copy) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  `holdout-pressure` re-checked post-batch — margin essentially flat
  (7.810 → 7.810), draw count 2047 → 2048 (one new sealed-holdout draw from
  this batch's fold-aggregate-gate-clearing candidate, correctly rejected),
  same slow-rise pattern already tracked under item 13, nothing new;
  dashboard rebuilt with `EVO_STATE` set (`index.html` shows 115709
  challenger idea(s) tried). Genome still v3 (1d) live, untouched. Container
  synced cleanly from `main` via `git checkout main` + `python3
  tools/git_sync.py` fast-forward through other sessions' 2026-11-13
  commits already pushed, no divergence, no shallow-clone staleness this
  cycle. Hit the recurring `pip3` vs `python3 -m pip` numpy/pandas split
  again — `python3 -m pip install -r requirements.txt -q` fixed it
  immediately, same as prior sessions.

- **Run 2026-11-13 (3-hourly check, ~18:47-19:11 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 115296 → 115504 (per
  `researcher_memory.tested`), stagnation/boldness counter 8359 → 8374.**
  No live trading this cycle (tick 91 already handled at the dedicated
  00:20 UTC daily slot, and the prior 3-hourly check's own evolve batch
  already ran at ~16:21-16:54 UTC — confirmed via `live_state.json`'s
  `updated` timestamp at session start, `2026-11-13T16:51:46+00:00`,
  matching `runs/2026-11-13-1654-evolve-batch-v3.md`). Freshness checks:
  `review-hard-calls` still 0 pending (6 reviewed, unchanged), items 6/13
  still owner decisions, `AGENTS.md` size 240,508 bytes at session start —
  ~15.7KB under the 256KB threshold, a margin recent sessions have judged
  comfortable enough to skip archival, not archived this cycle — so, with
  nothing else queued, used the slot for one more real 15-generation batch
  via `tools/background_runner.py` (`start` + separate `wait`), run after a
  baseline `pytest` pass, exit code 0, no truncation. Champion's
  fold-aggregate fitness held flat at 1.773 across all 15 generations (981
  trades, 38% win, 1% stops, 3 halts, unchanged throughout). Best-of-generation
  fold-fitness ranged roughly 1.039-2.203, never clearing the
  promotion-margin bar. See `runs/2026-11-13-1917-evolve-batch-v3.md`.
  Verified before commit: `python3 -m pytest -q` 505/505 both before
  (baseline) and after `evolve`; top-level key diff of `live_state.json`
  (snapshotted before `start`, checked directly in Python against the
  pre-batch copy) showed only `updated`/`researcher_memory`/`lineage`
  changed (genome, broker, journal, hard_call_reviews byte-identical);
  `lineage` length unchanged at 202 (bounded ring buffer, no new promotion
  attempt recorded); `tools/edit_bundle_module.py verify`/`sync --check`
  both clean; `holdout-pressure` re-checked post-batch — margin and draw
  count both unchanged (7.810, 2047) since no candidate this batch cleared
  the fold-aggregate gate; dashboard rebuilt with `EVO_STATE` set
  (`index.html` shows 115504 challenger idea(s) tried). Genome still v3 (1d)
  live, untouched. Container synced cleanly from `main` via `git checkout
  main` + `python3 tools/git_sync.py` fast-forward through other sessions'
  2026-11-13 commits already pushed, no divergence, no shallow-clone
  staleness this cycle.

- **Run 2026-11-13 (3-hourly check, ~16:21-16:54 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 115090 → 115296 (per
  `researcher_memory.tested`), stagnation/boldness counter 8345 → 8359.**
  No live trading this cycle (tick 91 already handled at the dedicated
  00:20 UTC daily slot, and the prior 3-hourly check's own evolve batch
  already ran at ~12:47-13:20 UTC — confirmed via `live_state.json`'s
  `updated` timestamp at session start, `2026-11-13T13:17:18+00:00`,
  matching `runs/2026-11-13-1320-evolve-batch-v3.md`). Freshness checks:
  `review-hard-calls` still 0 pending (6 reviewed, unchanged), items 6/13
  still owner decisions, `AGENTS.md` size 237,841 bytes at session start —
  ~18.5KB under the 256KB threshold, comfortably clear, not archived this
  cycle — so, with nothing else queued, used the slot for one more real
  15-generation batch via `tools/background_runner.py` (`start` + separate
  `wait`), run after a baseline `pytest` pass, exit code 0, no truncation.
  Champion's fold-aggregate fitness held flat at 1.773 across all 15
  generations (981 trades, 38% win, 1% stops, 3 halts, unchanged
  throughout). Best-of-generation fold-fitness ranged roughly 1.537-2.203 —
  generation 3's best (2.203) exceeded the champion's raw fitness but still
  didn't clear the full promotion gate (multiple-testing margin). See
  `runs/2026-11-13-1654-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 505/505 both before (baseline) and after `evolve`;
  top-level key diff of `live_state.json` (snapshotted before `start`,
  checked directly in Python against the pre-batch copy) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  `holdout-pressure` re-checked post-batch — margin essentially flat
  (7.809 → 7.810), draw count 2046 → 2047 (one new sealed-holdout draw from
  this batch's fold-aggregate-gate-clearing candidate, correctly rejected),
  same slow-rise pattern already tracked under item 13, nothing new;
  dashboard rebuilt with `EVO_STATE` set (`index.html` shows 115296
  challenger idea(s) tried). Genome still v3 (1d) live, untouched. Container
  synced cleanly from `main` via `git checkout main` + `python3
  tools/git_sync.py` fast-forward through other sessions' 2026-11-13
  commits already pushed, no divergence, no shallow-clone staleness this
  cycle.

- **Run 2026-11-13 (3-hourly check, ~12:47-13:20 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 114881 → 115090 (per
  `researcher_memory.tested`), stagnation/boldness counter 8330 → 8345.**
  No live trading this cycle (tick 91 already handled at the dedicated
  00:20 UTC daily slot, and the prior 3-hourly check's own evolve batch
  already ran at ~09:48-10:13 UTC — confirmed via `live_state.json`'s
  `updated` timestamp at session start, `2026-11-13T10:10:49+00:00`,
  matching `runs/2026-11-13-1013-evolve-batch-v3.md`). Freshness checks:
  `review-hard-calls` still 0 pending (6 reviewed, unchanged), items 6/13
  still owner decisions, `AGENTS.md` size 234,977 bytes at session start —
  ~21KB under the 256KB threshold, comfortably clear, not archived this
  cycle — so, with nothing else queued, used the slot for one more real
  15-generation batch via `tools/background_runner.py` (`start` + separate
  `wait`), run after a baseline `pytest` pass, exit code 0, no truncation.
  Champion's fold-aggregate fitness held flat at 1.773 across all 15
  generations (981 trades, 38% win, 1% stops, 3 halts, unchanged
  throughout). Best-of-generation fold-fitness ranged roughly 1.358-3.032 —
  two generations (11, best 3.032; 13, best 2.180) exceeded the champion's
  raw fitness but neither cleared the full promotion gate (multiple-testing
  margin). See `runs/2026-11-13-1320-evolve-batch-v3.md`. Hit the recurring
  `pip3` vs `python3 -m pip` numpy/pandas split again — `python3 -m pip
  install -r requirements.txt -q` fixed it immediately, same as prior
  sessions. Verified before commit: `python3 -m pytest -q` 505/505 both
  before (baseline) and after `evolve`; top-level key diff of
  `live_state.json` (snapshotted before `start`, checked directly in Python
  against the pre-batch copy) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  `holdout-pressure` re-checked post-batch — margin essentially flat
  (7.809 → 7.810), draw count 2044 → 2046 (two new sealed-holdout draws
  from this batch's fold-aggregate-gate-clearing candidates, both correctly
  rejected), same slow-rise pattern already tracked under item 13, nothing
  new; dashboard rebuilt with `EVO_STATE` set (`index.html` shows 115090
  challenger idea(s) tried). Genome still v3 (1d) live, untouched. Container
  synced cleanly from `main` via `git checkout main` + `python3
  tools/git_sync.py` fast-forward through other sessions' 2026-11-13
  commits already pushed, no divergence, no shallow-clone staleness this
  cycle.

- **Run 2026-11-13 (3-hourly check, ~09:48-10:13 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 114678 → 114881 (per
  `researcher_memory.tested`), stagnation/boldness counter 8315 → 8330.**
  No live trading this cycle (tick 91 already handled at the dedicated
  00:20 UTC daily slot, and the prior 3-hourly check's own evolve batch
  already ran at ~06:47-07:20 UTC — confirmed via `live_state.json`'s
  `updated` timestamp at session start, `2026-11-13T07:16:40+00:00`,
  matching `runs/2026-11-13-0720-evolve-batch-v3.md`). Also archived the
  oldest remaining `AGENTS.md` slice this cycle (see the entry directly
  below), flagged by the same-day 09:00 UTC daily discussion as nearing
  the 256KB threshold — done first, before the evolve batch. Freshness
  checks: `review-hard-calls` still 0 pending (6 reviewed, unchanged),
  items 6/13 still owner decisions. Ran the real 15-generation batch via
  `tools/background_runner.py` (`start` + separate `wait`), after a
  baseline `pytest` pass, exit code 0, no truncation. Champion's
  fold-aggregate fitness held flat at 1.773 across all 15 generations (981
  trades, 38% win, 1% stops, 3 halts, unchanged throughout). Best-of-generation
  fold-fitness ranged roughly 1.186-3.582 — one generation (14, best 1.930)
  exceeded the champion's raw fitness but still didn't clear the full
  promotion gate (multiple-testing margin). See
  `runs/2026-11-13-1013-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 505/505 both before (baseline) and after `evolve`;
  top-level key diff of `live_state.json` (snapshotted before `start`,
  checked directly in Python against the pre-batch copy) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  `holdout-pressure` re-checked post-batch — margin and draw count both
  unchanged (7.809, 2044) since no candidate this batch cleared the full
  fold-aggregate gate; dashboard rebuilt with `EVO_STATE` set (`index.html`
  shows 114881 challenger idea(s) tried). Genome still v3 (1d) live,
  untouched. Container synced cleanly from `main` via `git checkout main` +
  `python3 tools/git_sync.py` fast-forward through other sessions'
  2026-11-13 commits already pushed, no divergence, no shallow-clone
  staleness this cycle.

- **Archived 2026-11-13 (3-hourly check, ~09:48-10:xx UTC): the next oldest
  remaining slice of this log (all nine 2026-11-11 entries) moved verbatim
  to new `AGENTS_ARCHIVE_2026-11-11.md`, cutting this file from 253,312
  bytes back down** — the pre-write size was within ~2.6KB of the 256KB
  threshold, the tightest margin in a while and one the same-day 09:00 UTC
  daily discussion had already flagged for the next 3-hourly check to pick
  up. Verified via exact line-range removal (the removed 320-line block
  diffed byte-for-byte identical against the new archive file's body) and
  `python3 -m pytest -q` unaffected (text-only change, no code touched).
  Nothing reworded, nothing lost — see that file (and, for anything older,
  the rest of this index below) for the full history. This file now keeps
  everything from 2026-11-12 ~00:47 UTC onward, plus the full "Owner
  decisions pending", promotion-history, "Measured", and "Rules" sections,
  never part of any rotation. No protected file touched, `live_state.json`
  untouched by this housekeeping step itself.

- **Run 2026-11-13 (3-hourly check, ~06:47-07:20 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 114474 → 114678 (per
  `researcher_memory.tested`), stagnation/boldness counter 8300 → 8314.**
  No live trading this cycle (tick 91 already handled at the dedicated
  00:20 UTC daily slot, and the prior 3-hourly check's own evolve batch
  already ran at ~03:48-04:17 UTC — confirmed via `live_state.json`'s
  `updated` timestamp at session start, `2026-11-13T04:12:58+00:00`,
  matching `runs/2026-11-13-0417-evolve-batch-v3.md`). Freshness checks:
  `review-hard-calls` still 0 pending (6 reviewed, unchanged), items 6/13
  still owner decisions, `AGENTS.md` size 250,669 bytes at session start —
  ~11.2KB under the 256KB threshold, a margin comparable to others recent
  sessions have judged comfortable enough to skip archival, not archived
  this cycle — so, with nothing else queued, used the slot for one more
  real 15-generation batch via `tools/background_runner.py` (`start` +
  separate `wait`), run after a baseline `pytest` pass, exit code 0, no
  truncation. Champion's fold-aggregate fitness held flat at 1.773 across
  all 15 generations (981 trades, 38% win, 1% stops, 3 halts, unchanged
  throughout). Best-of-generation fold-fitness ranged roughly 1.222-3.582,
  never clearing the promotion-margin bar. See
  `runs/2026-11-13-0720-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 505/505 both before (baseline) and after `evolve`;
  top-level key diff of `live_state.json` (snapshotted before `start`,
  checked directly in Python against the pre-batch copy) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  `holdout-pressure` re-checked post-batch — margin essentially flat
  (7.809 → 7.809), draw count 2043 → 2044 (one new sealed-holdout draw from
  this batch's fold-aggregate-gate-clearing candidate, correctly rejected),
  same slow-rise pattern already tracked under item 13, nothing new;
  dashboard rebuilt with `EVO_STATE` set (`index.html` shows 114678
  challenger idea(s) tried). Genome still v3 (1d) live, untouched. Container
  synced cleanly from `main` via `git checkout main` + `python3
  tools/git_sync.py` fast-forward through other sessions' 2026-11-13
  commits already pushed, no divergence, no shallow-clone staleness this
  cycle.

- **Run 2026-11-13 (3-hourly check, ~03:48-04:17 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 114266 → 114474 (per
  `researcher_memory.tested`), stagnation/boldness counter 8285 → 8299.**
  No live trading this cycle (tick 91 already handled at the dedicated
  00:20 UTC daily slot, and the prior 3-hourly check's own evolve batch
  already ran at ~00:47-01:13 UTC — confirmed via `live_state.json`'s
  `updated` timestamp at session start, `2026-11-13T01:11:54+00:00`,
  matching `runs/2026-11-13-0113-evolve-batch-v3.md`). Freshness checks:
  `review-hard-calls` still 0 pending (6 reviewed, unchanged), items 6/13
  still owner decisions, `AGENTS.md` size 247,629 bytes at session start —
  ~8.4KB under the 256KB threshold, in the range several recent sessions
  have judged comfortable enough to skip archival, not archived this
  cycle — so, with nothing else queued, used the slot for one more real
  15-generation batch via `tools/background_runner.py` (`start` + separate
  `wait`), run after a baseline `pytest` pass, exit code 0, no truncation.
  Champion's fold-aggregate fitness held flat at 1.773 across all 15
  generations (981 trades, 38% win, 1% stops, 3 halts, unchanged
  throughout). Best-of-generation fold-fitness ranged roughly 1.242-2.136,
  never clearing the promotion-margin bar. See
  `runs/2026-11-13-0417-evolve-batch-v3.md`. Also hit the AGENTS.md item-9
  landmine once, in the *verification* pytest run rather than the evolve
  batch itself (paired a tool-level `run_in_background: true` with a
  trailing shell `&` in the same command, detaching the real pytest from
  the wrapper's own lifecycle) — caught immediately via `ps aux`/`kill -0`
  on the real PID, no harm, pytest finished 505/505 once actually waited
  for. Verified before commit: `python3 -m pytest -q` 505/505 both before
  (baseline) and after `evolve`; top-level key diff of `live_state.json`
  (snapshotted before `start`, checked directly in Python against the
  pre-batch copy) showed only `updated`/`researcher_memory`/`lineage`
  changed (genome, broker, journal, hard_call_reviews byte-identical);
  `lineage` length unchanged at 202 (bounded ring buffer, no new promotion
  attempt recorded); `tools/edit_bundle_module.py verify`/`sync --check`
  both clean; `holdout-pressure` re-checked post-batch — margin essentially
  flat (7.805 → 7.809), draw count 2034 → 2043 (nine new sealed-holdout
  draws from this batch's fold-aggregate-gate-clearing candidates, all
  correctly rejected), same slow-rise pattern already tracked under item
  13, nothing new; dashboard rebuilt with `EVO_STATE` set (`index.html`
  shows 114474 challenger idea(s) tried). Genome still v3 (1d) live,
  untouched. Container synced cleanly from `main` via `git checkout main` +
  `python3 tools/git_sync.py` fast-forward through other sessions'
  2026-11-13 commits already pushed, no divergence, no shallow-clone
  staleness this cycle.

- **Run 2026-11-13 (3-hourly check, ~00:47-01:13 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 114058 → 114266 (per
  `researcher_memory.tested`), stagnation/boldness counter 8270 → 8284.**
  No live trading this cycle (tick 91 already handled at the dedicated
  00:20 UTC daily slot, including its own `tick % 7 == 0` evolve-3 batch —
  confirmed via `runs/2026-11-13-0020-daily-trading.md` and
  `live_state.json`'s `updated` timestamp at session start,
  `2026-11-13T00:31:38+00:00`). Freshness checks: `review-hard-calls` still
  0 pending (6 reviewed, unchanged), items 6/13 still owner decisions,
  `AGENTS.md` size 245,029 bytes at session start — ~16.7KB under the 256KB
  threshold, a margin recent sessions have judged wide enough to skip
  archival, not archived this cycle — so, with nothing else queued, used
  the slot for one more real 15-generation batch via
  `tools/background_runner.py` (`start` + separate `wait`), run after a
  baseline `pytest` pass, exit code 0, no truncation. Champion's
  fold-aggregate fitness held flat at 1.773 across all 15 generations (981
  trades, 38% win, 1% stops, 3 halts, unchanged throughout). Best-of-generation
  fold-fitness ranged roughly 1.242-2.136, never clearing the
  promotion-margin bar. See `runs/2026-11-13-0113-evolve-batch-v3.md`.
  Verified before commit: `python3 -m pytest -q` 505/505 both before
  (baseline) and after `evolve`; top-level key diff of `live_state.json`
  (snapshotted before `start`, checked directly in Python against the
  pre-batch copy) showed only `updated`/`researcher_memory`/`lineage`
  changed (genome, broker, journal, hard_call_reviews byte-identical);
  `lineage` length unchanged at 202 (bounded ring buffer, no new promotion
  attempt recorded); `tools/edit_bundle_module.py verify`/`sync --check`
  both clean; `holdout-pressure` re-checked post-batch — margin essentially
  flat (7.807 → 7.809), draw count 2034 → 2043 (nine new sealed-holdout
  draws from this batch's fold-aggregate-gate-clearing candidates, all
  correctly rejected), same slow-rise pattern already tracked under item
  13, nothing new; dashboard rebuilt with `EVO_STATE` set (`index.html`
  shows 114266 challenger idea(s) tried). Genome still v3 (1d) live,
  untouched. Container synced cleanly from `main` via `git checkout main` +
  `python3 tools/git_sync.py` fast-forward through other sessions'
  2026-11-07 through 2026-11-13 commits already pushed, no divergence, no
  shallow-clone staleness this cycle.

