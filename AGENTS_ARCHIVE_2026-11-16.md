# AGENTS.md archive — 2026-11-16 entries

Verbatim slice moved out of `AGENTS.md`'s "Current state" chronological log
by the 2026-11-18 3-hourly check (~06:46 UTC), to keep that file under its
256KB single-read limit. Nothing reworded, nothing lost. These are all
eight entries dated 2026-11-16 (3-hourly checks). See `AGENTS.md` for the
full index of older archives and the current log.

- **Run 2026-11-16 (3-hourly check, ~21:47-22:20 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 120999 → 121202 (per
  `researcher_memory.tested`), stagnation/boldness counter 8775 → 8789.**
  No live trading this cycle (tick 94 already handled at the dedicated
  00:20 UTC daily slot, and the 20:30 UTC daily evaluation earlier today
  had already confirmed the mechanism was healthy — confirmed via
  `live_state.json`'s `updated` timestamp at session start,
  `2026-11-16T19:12:43+00:00`, matching
  `runs/2026-11-16-1915-evolve-batch-v3.md`). Freshness checks:
  `review-hard-calls` still 0 pending (6 reviewed, unchanged), items 6/13
  still owner decisions, `AGENTS.md` size 247,319 bytes at session start —
  ~8.7KB under the 256KB threshold, tighter than several recent
  "comfortably clear" margins but not archived this cycle (not urgent per
  the 20:30 UTC daily evaluation's own read of the same number) — so, with
  nothing else queued, used the slot for one more real 15-generation batch
  via `tools/background_runner.py` (`start` + separate `wait`), run after a
  baseline `pytest` pass, exit code 0, no truncation. Champion's
  fold-aggregate fitness held flat at 1.504 across all 15 generations (917
  trades, 38% win, 1% stops, 4 halts, unchanged throughout). Best-of-generation
  fold-fitness ranged roughly 0.901-2.566, never clearing the
  promotion-margin bar. See `runs/2026-11-16-2220-evolve-batch-v3.md`.
  Verified before commit: `python3 -m pytest -q` 505/505 both before
  (baseline) and after `evolve`; top-level key diff of `live_state.json`
  (snapshotted before `start`, checked directly in Python against the
  pre-batch copy) showed only `updated`/`researcher_memory`/`lineage`
  changed (genome, broker, journal, hard_call_reviews byte-identical);
  `lineage` length unchanged at 202 (bounded ring buffer, no new promotion
  attempt recorded); `tools/edit_bundle_module.py sync --check` clean;
  `holdout-pressure` re-checked post-batch — margin rose slightly (7.835 →
  7.837), draw count 2151 → 2159 (new sealed-holdout draws from this
  batch's fold-aggregate-gate-clearing candidates, all correctly rejected),
  same slow-rise pattern already tracked under item 13, nothing new;
  dashboard rebuilt with `EVO_STATE` set (`index.html` shows 121202
  challenger idea(s) tried). Genome still v3 (1d) live, untouched. Container
  synced cleanly from `main` via `git checkout main` + `python3
  tools/git_sync.py` fast-forward through other sessions' already-pushed
  commits, no divergence, no shallow-clone staleness this cycle.

- **Run 2026-11-16 (3-hourly check, ~18:46-19:15 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 120793 → 120999 (per
  `researcher_memory.tested`), stagnation/boldness counter 8760 → 8774.**
  No live trading this cycle (tick 94 already handled at the dedicated
  00:20 UTC daily slot, and the prior 3-hourly check's own evolve batch
  already ran at ~15:47-16:16 UTC — confirmed via `live_state.json`'s
  `updated` timestamp at session start, `2026-11-16T16:14:01+00:00`,
  matching `runs/2026-11-16-1616-evolve-batch-v3.md`). Freshness checks:
  `review-hard-calls` still 0 pending (6 reviewed, unchanged), items 6/13
  still owner decisions, `AGENTS.md` size 244,413 bytes at session start —
  ~11.9KB under the 256KB threshold (narrower than several recent
  "comfortably clear" margins but wider than the last archival trigger
  point of ~9.8KB) — not archived this cycle, flagging for a future
  session on a tighter margin — so, with nothing else queued, used the
  slot for one more real 15-generation batch via
  `tools/background_runner.py` (`start` + separate `wait`), run after a
  baseline `pytest` pass, exit code 0, no truncation. Champion's
  fold-aggregate fitness held flat at 1.504 across all 15 generations (917
  trades, 38% win, 1% stops, 4 halts, unchanged throughout). Best-of-generation
  fold-fitness ranged roughly 0.832-2.566, never clearing the
  promotion-margin bar. See `runs/2026-11-16-1915-evolve-batch-v3.md`.
  Verified before commit: `python3 -m pytest -q` 505/505 both before
  (baseline) and after `evolve`; top-level key diff of `live_state.json`
  (snapshotted before `start`, checked directly in Python against the
  pre-batch copy) showed only `updated`/`researcher_memory`/`lineage`
  changed (genome, broker, journal, hard_call_reviews byte-identical);
  `lineage` length unchanged at 202 (bounded ring buffer, no new promotion
  attempt recorded); `tools/edit_bundle_module.py sync --check` clean;
  `holdout-pressure` re-checked post-batch — margin rose slightly (7.834 →
  7.837), draw count 2148 → 2158 (ten new sealed-holdout draws from this
  batch's fold-aggregate-gate-clearing candidates, all correctly rejected),
  same slow-rise pattern already tracked under item 13, nothing new;
  dashboard rebuilt with `EVO_STATE` set (`index.html` shows 120999
  challenger idea(s) tried). Genome still v3 (1d) live, untouched. Container
  synced cleanly from `main` via `git checkout main` + `python3
  tools/git_sync.py` fast-forward through other sessions' already-pushed
  commits (32 commits ahead at session start), no divergence, no
  shallow-clone staleness this cycle. Hit the recurring `pip3` vs `python3
  -m pip` numpy/pandas split again — `python3 -m pip install -r
  requirements.txt -q` fixed it immediately, same as prior sessions.

- **Run 2026-11-16 (3-hourly check, ~15:47-16:16 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 120587 → 120793 (per
  `researcher_memory.tested`), stagnation/boldness counter 8745 → 8760.**
  No live trading this cycle (tick 94 already handled at the dedicated
  00:20 UTC daily slot, and the prior 3-hourly check's own evolve batch
  already ran at ~12:47-13:22 UTC — confirmed via `live_state.json`'s
  `updated` timestamp at session start, `2026-11-16T13:22:06+00:00`,
  matching `runs/2026-11-16-1322-evolve-batch-v3.md`). Freshness checks:
  `review-hard-calls` still 0 pending (6 reviewed, unchanged), items 6/13
  still owner decisions, `AGENTS.md` size 241,358 bytes at session start —
  ~14.6KB under the 256KB threshold, comfortably clear, not archived this
  cycle — so, with nothing else queued, used the slot for one more real
  15-generation batch via `tools/background_runner.py` (`start` + separate
  `wait`, re-armed twice while the real process ran to generation 15/15),
  run after a baseline `pytest` pass, exit code 0, no truncation.
  Champion's fold-aggregate fitness held flat at 1.504 across all 15
  generations (917 trades, 38% win, 1% stops, 4 halts, unchanged
  throughout). Best-of-generation fold-fitness ranged roughly 1.472-1.918,
  never clearing the promotion-margin bar. Two of the `wait` calls' own
  1700s/600s timeouts elapsed while the real process was still running —
  same already-documented pattern, not a real failure, confirmed by
  polling the real PID directly each time until it exited with code 0.
  See `runs/2026-11-16-1616-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 505/505 both before (baseline) and after `evolve`;
  top-level key diff of `live_state.json` (snapshotted before `start`,
  checked directly in Python against the pre-batch copy) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py sync --check` clean; `holdout-pressure`
  re-checked post-batch — margin rose slightly (7.835 → 7.836), draw count
  2151 → 2153 (new sealed-holdout draws from this batch's
  fold-aggregate-gate-clearing candidates, all correctly rejected), same
  slow-rise pattern already tracked under item 13, nothing new; dashboard
  rebuilt with `EVO_STATE` set (`index.html` shows 120793 challenger
  idea(s) tried). Genome still v3 (1d) live, untouched. Container synced
  cleanly from `main` via `git checkout main` + `python3 tools/git_sync.py`
  fast-forward through other sessions' already-pushed commits (28 commits
  ahead at session start), no divergence, no shallow-clone staleness this
  cycle. Hit the recurring `pip3` vs `python3 -m pip` numpy/pandas split
  again — `python3 -m pip install -r requirements.txt -q` fixed it
  immediately, same as prior sessions.

- **Run 2026-11-16 (3-hourly check, ~12:47-13:22 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 120381 → 120587 (per
  `researcher_memory.tested`), stagnation/boldness counter 8730 → 8745.**
  No live trading this cycle (tick 94 already handled at the dedicated
  00:20 UTC daily slot, and the prior 3-hourly check's own evolve batch
  already ran at ~09:47-10:23 UTC — confirmed via `live_state.json`'s
  `updated` timestamp at session start, `2026-11-16T10:18:40+00:00`,
  matching `runs/2026-11-16-1023-evolve-batch-v3.md`). Freshness checks:
  `review-hard-calls` still 0 pending (6 reviewed, unchanged), items 6/13
  still owner decisions, `AGENTS.md` size 238,545 bytes at session start —
  ~17.9KB under the 256KB threshold, comfortably clear, not archived this
  cycle — so, with nothing else queued, used the slot for one more real
  15-generation batch via `tools/background_runner.py` (`start` + separate
  `wait`), run after a baseline `pytest` pass, exit code 0, no truncation.
  Champion's fold-aggregate fitness held flat at 1.504 across all 15
  generations (917 trades, 38% win, 1% stops, 4 halts, unchanged
  throughout). Best-of-generation fold-fitness ranged roughly 1.527-2.436,
  never clearing the promotion-margin bar. The `wait` call's own 1700s
  timeout elapsed while the real process was still on generation 15/15 —
  same already-documented pattern, not a real failure, confirmed by
  polling the real PID directly until it exited with code 0. See
  `runs/2026-11-16-1322-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 505/505 both before (baseline) and after `evolve`;
  top-level key diff of `live_state.json` (snapshotted before `start`,
  checked directly in Python against the pre-batch copy) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py sync --check` clean; `holdout-pressure`
  re-checked post-batch — margin rose slightly (7.834 → 7.835), draw count
  2148 → 2151 (three new sealed-holdout draws from this batch's
  fold-aggregate-gate-clearing candidates, all correctly rejected), same
  slow-rise pattern already tracked under item 13, nothing new; dashboard
  rebuilt with `EVO_STATE` set (`index.html` shows 120587 challenger
  idea(s) tried). Genome still v3 (1d) live, untouched. Container synced
  cleanly from `main` via `git checkout main` + `python3 tools/git_sync.py`
  fast-forward through other sessions' already-pushed commits (27 commits
  ahead at session start), no divergence, no shallow-clone staleness this
  cycle.

- **Run 2026-11-16 (3-hourly check, ~09:47-10:23 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 120172 → 120381 (per
  `researcher_memory.tested`), stagnation/boldness counter 8715 → 8730.**
  No live trading this cycle (tick 94 already handled at the dedicated
  00:20 UTC daily slot, and the 09:00 UTC daily discussion earlier today had
  already confirmed nothing new was pending). Freshness checks:
  `review-hard-calls` still 0 pending (6 reviewed, unchanged), items 6/13
  still owner decisions, `AGENTS.md` size 236,127 bytes at session start —
  ~20KB under the 256KB threshold, comfortably clear, not archived this
  cycle — so, with nothing else queued, used the slot for one more real
  15-generation batch via `tools/background_runner.py` (`start` + separate
  `wait`), run after a baseline `pytest` pass, exit code 0, no truncation.
  Champion's fold-aggregate fitness held flat at 1.504 across all 15
  generations (917 trades, 38% win, 1% stops, 4 halts, unchanged
  throughout). Best-of-generation fold-fitness ranged roughly 1.163-1.971,
  never clearing the promotion-margin bar. See
  `runs/2026-11-16-1023-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 505/505 both before (baseline) and after `evolve`;
  top-level key diff of `live_state.json` (snapshotted before `start`,
  checked directly in Python against the pre-batch copy) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py sync --check` clean; `holdout-pressure`
  re-checked post-batch — margin flat (7.834 → 7.834), draw count 2147 →
  2148 (one new sealed-holdout draw from this batch's
  fold-aggregate-gate-clearing candidates, correctly rejected), same
  slow-rise pattern already tracked under item 13, nothing new; dashboard
  rebuilt with `EVO_STATE` set (`index.html` shows 120381 challenger
  idea(s) tried). Genome still v3 (1d) live, untouched. Container synced
  cleanly from `main` via `git checkout main` + `python3 tools/git_sync.py`
  fast-forward through other sessions' already-pushed commits (24 commits
  ahead at session start), no divergence, no shallow-clone staleness this
  cycle.

- **Run 2026-11-16 (3-hourly check, ~06:46-07:20 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 119965 → 120172 (per
  `researcher_memory.tested`), stagnation/boldness counter 8699 → 8714.**
  No live trading this cycle (tick 94 already handled at the dedicated
  00:20 UTC daily slot, and the prior 3-hourly check's own evolve batch
  already ran at ~03:46-04:20 UTC — confirmed via `live_state.json`'s
  `updated` timestamp at session start, `2026-11-16T04:17:26+00:00`,
  matching `runs/2026-11-16-0420-evolve-batch-v3.md`). Freshness checks:
  `review-hard-calls` still 0 pending (6 reviewed, unchanged), items 5/6/13
  still owner decisions, `AGENTS.md` size 233,512 bytes at session start —
  ~22.5KB under the 256KB threshold, comfortably clear, not archived this
  cycle — so, with nothing else queued, used the slot for one more real
  15-generation batch via `tools/background_runner.py` (`start` + separate
  `wait`), run after a baseline `pytest` pass, exit code 0, no truncation.
  Champion's fold-aggregate fitness held flat at 1.504 across all 15
  generations (917 trades, 38% win, 1% stops, 4 halts, unchanged throughout
  — no daily-bar roll this cycle). Best-of-generation fold-fitness ranged
  roughly 1.504-2.826, never clearing the promotion-margin bar. See
  `runs/2026-11-16-0720-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 505/505 both before (baseline) and after `evolve`;
  top-level key diff of `live_state.json` (snapshotted before `start`,
  checked directly in Python against the pre-batch copy) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py sync --check` clean; `holdout-pressure`
  re-checked post-batch — margin rose slightly (7.832 → 7.834), draw count
  2142 → 2147 (five new sealed-holdout draws from this batch's
  fold-aggregate-gate-clearing candidates, all correctly rejected), same
  slow-rise pattern already tracked under item 13, nothing new; dashboard
  rebuilt with `EVO_STATE` set (`index.html` shows 120172 challenger
  idea(s) tried). Genome still v3 (1d) live, untouched. Container synced
  cleanly from `main` via `git checkout main` + `python3 tools/git_sync.py`
  fast-forward through other sessions' already-pushed commits (24 commits
  ahead at session start), no divergence, no shallow-clone staleness this
  cycle.

- **Run 2026-11-16 (3-hourly check, ~03:46-04:20 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 119760 → 119965 (per
  `researcher_memory.tested`), stagnation/boldness counter 8684 → 8699.**
  No live trading this cycle (tick 94 already handled at the dedicated
  00:20 UTC daily slot, and the prior 3-hourly check's own evolve batch
  already ran at ~00:46-01:18 UTC — confirmed via `live_state.json`'s
  `updated` timestamp at session start, `2026-11-16T01:16:04+00:00`,
  matching `runs/2026-11-16-0118-evolve-batch-v3.md`). Freshness checks:
  `review-hard-calls` still 0 pending (6 reviewed, unchanged), items 5/6/13
  still owner decisions, `AGENTS.md` size 230,762 bytes at session start —
  ~25KB under the 256KB threshold, comfortably clear, not archived this
  cycle — so, with nothing else queued, used the slot for one more real
  15-generation batch via `tools/background_runner.py` (`start` + separate
  `wait`), run after a baseline `pytest` pass, exit code 0, no truncation.
  Champion's fold-aggregate fitness held flat at 1.504 across all 15
  generations (917 trades, 38% win, 1% stops, 4 halts, unchanged throughout
  — no daily-bar roll this cycle). Best-of-generation fold-fitness ranged
  roughly 1.218-1.894, never clearing the promotion-margin bar. See
  `runs/2026-11-16-0420-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 505/505 both before (baseline) and after `evolve`;
  top-level key diff of `live_state.json` (snapshotted before `start`,
  checked directly in Python against the pre-batch copy) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py sync --check` clean; `holdout-pressure`
  re-checked post-batch — margin rose slightly (7.832 → 7.833), draw count
  2139 → 2142 (three new sealed-holdout draws from this batch's
  fold-aggregate-gate-clearing candidates, all correctly rejected), same
  slow-rise pattern already tracked under item 13, nothing new; dashboard
  rebuilt with `EVO_STATE` set (`index.html` shows 119965 challenger
  idea(s) tried). Genome still v3 (1d) live, untouched. Container synced
  cleanly from `main` via `git checkout main` + `python3 tools/git_sync.py`
  fast-forward through other sessions' already-pushed commits, no
  divergence, no shallow-clone staleness this cycle. Hit the recurring
  `pip3` vs `python3 -m pip` numpy/pandas split again — `python3 -m pip
  install -r requirements.txt -q` fixed it immediately, same as prior
  sessions.

- **Run 2026-11-16 (3-hourly check, ~00:46-01:18 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 119552 → 119760 (per
  `researcher_memory.tested`), stagnation/boldness counter 8669 → 8684.**
  No live trading this cycle (tick 94 already handled at the dedicated
  00:20 UTC daily slot — confirmed via `live_state.json`'s `updated`
  timestamp at session start, `2026-11-16T00:22:23+00:00`, matching
  `runs/2026-11-16-0020-daily-trading.md`; that run's own `94 % 7 == 3`, so
  no evolve-3 batch ran there either). Freshness checks: `review-hard-calls`
  still 0 pending (6 reviewed, unchanged), items 5/6/13 still owner
  decisions, `AGENTS.md` size 228,100 bytes at session start — ~28KB under
  the 256KB threshold, comfortably clear, not archived this cycle — so, with
  nothing else queued, used the slot for one more real 15-generation batch
  via `tools/background_runner.py` (`start` + separate `wait`), run after a
  baseline `pytest` pass, exit code 0, no truncation. Champion's
  fold-aggregate fitness shifted mid-batch, 1.556 → 1.504 (the daily bar
  from tick 94 rolled the fold windows forward, same mechanism every prior
  session has observed), then held flat at 1.504 for the rest (917 trades,
  38% win, 1% stops, 4 halts after the shift). Best-of-generation
  fold-fitness ranged roughly 1.504-2.826, never clearing the
  promotion-margin bar. See `runs/2026-11-16-0118-evolve-batch-v3.md`.
  Verified before commit: `python3 -m pytest -q` 505/505 both before
  (baseline) and after `evolve`; top-level key diff of `live_state.json`
  (snapshotted before `start`, checked directly in Python against the
  pre-batch copy) showed only `updated`/`researcher_memory`/`lineage`
  changed (genome, broker, journal, hard_call_reviews byte-identical);
  `lineage` length unchanged at 202 (bounded ring buffer, no new promotion
  attempt recorded); `tools/edit_bundle_module.py sync --check` clean;
  `holdout-pressure` re-checked post-batch — margin rose slightly (7.831 →
  7.832), draw count 2135 → 2139 (four new sealed-holdout draws from this
  batch's fold-aggregate-gate-clearing candidates, all correctly rejected),
  same slow-rise pattern already tracked under item 13, nothing new;
  dashboard rebuilt with `EVO_STATE` set (`index.html` shows 119760
  challenger idea(s) tried). Genome still v3 (1d) live, untouched. Container
  synced cleanly from `main` via `git checkout main` + `python3
  tools/git_sync.py` fast-forward through other sessions' already-pushed
  commits, no divergence, no shallow-clone staleness this cycle.
