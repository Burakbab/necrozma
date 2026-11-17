# AGENTS.md archive — 2026-11-15 entries

Verbatim slice moved out of `AGENTS.md`'s "Current state" chronological log
by the 2026-11-17 3-hourly check (~03:46 UTC), to keep that file under its
256KB single-read limit. Nothing reworded, nothing lost. These are all
nine entries dated 2026-11-15 (eight 3-hourly checks plus that day's
weekend all-hands). See `AGENTS.md` for the full index of older archives
and the current log.

- **Run 2026-11-15 (3-hourly check, ~21:47-22:18 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 119345 → 119552 (per
  `researcher_memory.tested`), stagnation/boldness counter 8654 → 8669.**
  No live trading this cycle (tick 93 already handled at the dedicated
  00:20 UTC daily slot, and the prior 3-hourly check's own evolve batch
  already ran at ~18:46-19:19 UTC — confirmed via `live_state.json`'s
  `updated` timestamp at session start, `2026-11-15T19:16:46+00:00`,
  matching `runs/2026-11-15-1919-evolve-batch-v3.md`). Freshness checks:
  `review-hard-calls` still 0 pending (6 reviewed, unchanged), items 5/6/13
  still owner decisions, `AGENTS.md` size 245,932 bytes at session start —
  ~9.8KB under the 256KB threshold, narrower than the preceding entry's own
  ~12.8KB margin and explicitly flagged by that entry as closing in on the
  range recent rotations have used to trigger one — so archived the next
  oldest remaining slice (all eight 2026-11-14 entries) verbatim to new
  `AGENTS_ARCHIVE_2026-11-14.md` first (committed/pushed separately,
  `fbbfe6b`, verified byte-for-byte identical against the removed slice),
  cutting this file to 224,115 bytes. With that done, used the rest of the
  slot for one more real 15-generation batch via
  `tools/background_runner.py` (`start` + separate `wait`), run after a
  baseline `pytest` pass, exit code 0, no truncation. Champion's
  fold-aggregate fitness held flat at 1.556 across all 15 generations (974
  trades, 39% win, 1% stops, 3 halts, unchanged throughout). Best-of-generation
  fold-fitness ranged roughly 1.432-2.186, never clearing the
  promotion-margin bar. See `runs/2026-11-15-2218-evolve-batch-v3.md`.
  Verified before commit: `python3 -m pytest -q` 505/505 both before
  (baseline) and after `evolve`; top-level key diff of `live_state.json`
  (snapshotted before `start`, checked directly in Python against the
  pre-batch copy) showed only `updated`/`researcher_memory`/`lineage`
  changed (genome, broker, journal, hard_call_reviews byte-identical);
  `lineage` length unchanged at 202 (bounded ring buffer, no new promotion
  attempt recorded); `tools/edit_bundle_module.py sync --check` clean;
  `holdout-pressure` re-checked post-batch — margin and draw count both
  unchanged (7.831, 2135), no candidate this batch cleared the full
  fold-aggregate gate; dashboard rebuilt with `EVO_STATE` set (`index.html`
  shows 119552 challenger idea(s) tried). Genome still v3 (1d) live,
  untouched. Container synced cleanly from `main` via `git checkout main` +
  `python3 tools/git_sync.py` fast-forward through other sessions'
  2026-11-15 commits already pushed, no divergence, no shallow-clone
  staleness this cycle.

- **Archived 2026-11-15 (3-hourly check, ~21:47 UTC): the next oldest
  remaining slice of this log (all eight 2026-11-14 3-hourly-check entries)
  moved verbatim to new `AGENTS_ARCHIVE_2026-11-14.md`, cutting this file
  from 245,932 bytes back down** — the pre-write size was within ~9.8KB of
  the 256KB threshold, narrower than the immediately preceding ~18:46-19:19
  UTC entry's own ~12.8KB margin and flagged by that entry as worth
  watching since it was closing in on the range recent rotations have used
  to trigger one. Verified via exact line-range removal (the removed
  318-line block diffed byte-for-byte identical against the new archive
  file's body) and `python3 -m pytest -q` 505/505 unaffected (text-only
  change, no code touched). Nothing reworded, nothing lost — see that file
  (and, for anything older, the rest of this index below) for the full
  history. This file now keeps everything from 2026-11-15 ~00:47 UTC
  onward, plus the full "Owner decisions pending", promotion-history,
  "Measured", and "Rules" sections, never part of any rotation. No
  protected file touched, `live_state.json` untouched by this housekeeping
  step itself.

- **Run 2026-11-15 (3-hourly check, ~18:46-19:19 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 119136 → 119345 (per
  `researcher_memory.tested`), stagnation/boldness counter 8639 → 8654.**
  No live trading this cycle (tick 93 already handled at the dedicated
  00:20 UTC daily slot, and the prior 3-hourly check's own evolve batch
  already ran at ~15:47-16:26 UTC — confirmed via `live_state.json`'s
  `updated` timestamp at session start, `2026-11-15T16:22:24+00:00`,
  matching `runs/2026-11-15-1626-evolve-batch-v3.md`). Freshness checks:
  `review-hard-calls` still 0 pending (6 reviewed, unchanged), items 5/6/13
  still owner decisions, `AGENTS.md` size 243,206 bytes at session start —
  ~12.8KB under the 256KB threshold, tighter than several recent "comfortably
  clear" margins but not archived this cycle — flagging for a future session
  to watch, since the margin is closing in on the range recent rotations
  have used to trigger one. With nothing else queued, used the slot for one
  more real 15-generation batch via `tools/background_runner.py` (`start` +
  separate `wait`), run after a baseline `pytest` pass, exit code 0, no
  truncation. Champion's fold-aggregate fitness held flat at 1.556 across
  all 15 generations (974 trades, 39% win, 1% stops, 3 halts, unchanged
  throughout). Best-of-generation fold-fitness ranged roughly 1.402-2.826,
  never clearing the promotion-margin bar. See
  `runs/2026-11-15-1919-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 505/505 both before (baseline) and after `evolve`;
  top-level key diff of `live_state.json` (snapshotted before `start`,
  checked directly in Python against the pre-batch copy) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py sync --check` clean; `holdout-pressure`
  re-checked post-batch — margin essentially flat (7.831 → 7.831), draw
  count 2133 → 2135 (two new sealed-holdout draws from this batch's
  fold-aggregate-gate-clearing candidates, both correctly rejected), same
  slow-rise pattern already tracked under item 13, nothing new; dashboard
  rebuilt with `EVO_STATE` set (`index.html` shows 119345 challenger
  idea(s) tried). Genome still v3 (1d) live, untouched. Container synced
  cleanly from `main` via `git checkout main` + `python3 tools/git_sync.py`
  fast-forward through other sessions' 2026-11-15 commits already pushed,
  no divergence, no shallow-clone staleness this cycle.

- **Run 2026-11-15 (3-hourly check, ~15:47-16:26 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 118931 → 119136 (per
  `researcher_memory.tested`), stagnation/boldness counter 8625 → 8640.**
  No live trading this cycle (tick 93 already handled at the dedicated
  00:20 UTC daily slot, and the prior 3-hourly check's own evolve batch
  already ran at ~12:46-13:14 UTC — confirmed via `live_state.json`'s
  `updated` timestamp at session start, `2026-11-15T13:11:12+00:00`,
  matching `runs/2026-11-15-1314-evolve-batch-v3.md`). Freshness checks:
  `review-hard-calls` still 0 pending (6 reviewed, unchanged), items 6/13
  still owner decisions, `AGENTS.md` size 240,503 bytes at session start —
  ~15.5KB under the 256KB threshold, comfortably clear, not archived this
  cycle — so, with nothing else queued, used the slot for one more real
  15-generation batch via `tools/background_runner.py` (`start` + separate
  `wait`), run after a baseline `pytest` pass, exit code 0, no truncation.
  Champion's fold-aggregate fitness held flat at 1.556 across all 15
  generations (974 trades, 39% win, 1% stops, 3 halts, unchanged
  throughout). Best-of-generation fold-fitness ranged roughly 1.360-1.696,
  never clearing the promotion-margin bar. The `wait` call's own 1700s
  timeout elapsed while the real process was still on generation 14/15 —
  same already-documented pattern, not a real failure, confirmed by
  polling the real PID directly until it exited with code 0. See
  `runs/2026-11-15-1626-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 505/505 both before (baseline) and after `evolve`;
  top-level key diff of `live_state.json` (snapshotted before `start`,
  checked directly in Python against the pre-batch copy) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py sync --check` clean; `holdout-pressure`
  re-checked post-batch — margin and draw count both unchanged (7.831,
  2133) since no candidate this batch cleared the full fold-aggregate gate
  by enough to register a new sealed-holdout draw; dashboard rebuilt with
  `EVO_STATE` set (`index.html` shows 119136 challenger idea(s) tried).
  Genome still v3 (1d) live, untouched. Container synced cleanly from
  `main` via `git checkout main` + `python3 tools/git_sync.py` fast-forward
  through other sessions' 2026-11-15 commits already pushed, no divergence,
  no shallow-clone staleness this cycle.

- **Run 2026-11-15 (3-hourly check, ~12:46-13:14 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 118723 → 118931 (per
  `researcher_memory.tested`), stagnation/boldness counter 8610 → 8625.**
  No live trading this cycle (tick 93 already handled at the dedicated
  00:20 UTC daily slot, and the prior 3-hourly check's own evolve batch
  already ran at ~09:47-10:23 UTC — confirmed via `live_state.json`'s
  `updated` timestamp at session start, `2026-11-15T10:18:48+00:00`,
  matching `runs/2026-11-15-1023-evolve-batch-v3.md`). Freshness checks:
  `review-hard-calls` still 0 pending (6 reviewed, unchanged), items 6/13
  still owner decisions, `AGENTS.md` size 238,103 bytes at session start —
  ~18KB under the 256KB threshold, comfortably clear, not archived this
  cycle — so, with nothing else queued, used the slot for one more real
  15-generation batch via `tools/background_runner.py` (`start` + separate
  `wait`), run after a baseline `pytest` pass, exit code 0, no truncation.
  Champion's fold-aggregate fitness held flat at 1.556 across all 15
  generations (974 trades, 39% win, 1% stops, 3 halts, unchanged
  throughout). Best-of-generation fold-fitness ranged roughly 1.213-1.893,
  never clearing the promotion-margin bar. See
  `runs/2026-11-15-1314-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 505/505 both before (baseline) and after `evolve`;
  top-level key diff of `live_state.json` (snapshotted before `start`,
  checked directly in Python against the pre-batch copy) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py sync --check` clean; `holdout-pressure`
  re-checked post-batch — margin and draw count both unchanged (7.831,
  2133) since no candidate this batch cleared the full fold-aggregate gate
  by enough to register a new sealed-holdout draw; dashboard rebuilt with
  `EVO_STATE` set (`index.html` shows 118931 challenger idea(s) tried).
  Genome still v3 (1d) live, untouched. Container synced cleanly from
  `main` via `git checkout main` + `git pull --rebase origin main`, no
  divergence, no shallow-clone staleness this cycle.

- **Run 2026-11-15 (3-hourly check, ~09:47-10:23 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 118514 → 118723 (per
  `researcher_memory.tested`), stagnation/boldness counter 8595 → 8610.**
  No live trading this cycle (tick 93 already handled at the dedicated
  00:20 UTC daily slot, and the weekend all-hands session's own second
  evolve attempt already ran at ~08:41 UTC — confirmed via
  `live_state.json`'s `updated` timestamp at session start,
  `2026-11-15T08:38:18+00:00`, matching
  `runs/2026-11-15-0841-weekend-all-hands.md`). Freshness checks:
  `AGENTS.md` size 235,528 bytes at session start — ~20.5KB under the
  256KB threshold, comfortably clear, not archived this cycle; items 5/6/13
  still owner- or data-blocked per the weekend all-hands' own same-day
  roadmap survey, nothing new to add — so, with nothing else queued, used
  the slot for one more real 15-generation batch via
  `tools/background_runner.py` (`start` + separate `wait`), run after a
  baseline `pytest` pass, exit code 0, no truncation. Champion's
  fold-aggregate fitness held flat at 1.556 across all 15 generations (974
  trades, 39% win, 1% stops, 3 halts, unchanged throughout). Best-of-generation
  fold-fitness ranged roughly 1.343-2.826, never clearing the
  promotion-margin bar. See `runs/2026-11-15-1023-evolve-batch-v3.md`.
  Verified before commit: `python3 -m pytest -q` 505/505 both before
  (baseline) and after `evolve`; top-level key diff of `live_state.json`
  (snapshotted before `start`, checked directly in Python against the
  pre-batch copy) showed only `updated`/`researcher_memory`/`lineage`
  changed (genome, broker, journal, hard_call_reviews byte-identical);
  `lineage` length unchanged at 202 (bounded ring buffer, no new promotion
  attempt recorded); `tools/edit_bundle_module.py sync --check` clean;
  `holdout-pressure` re-checked post-batch — margin rose slightly
  (7.827 → 7.831), draw count 2118 → 2133 (new sealed-holdout draws from
  this batch's fold-aggregate-gate-clearing candidates, all correctly
  rejected), same slow-rise pattern already tracked under item 13, nothing
  new; dashboard rebuilt with `EVO_STATE` set (`index.html` shows 118723
  challenger idea(s) tried). Genome still v3 (1d) live, untouched. Container
  synced cleanly from `main` via `git checkout main` + `python3
  tools/git_sync.py` fast-forward through earlier 2026-11-15 commits already
  pushed, no divergence, no shallow-clone staleness this cycle.

- **Run 2026-11-15 (weekend all-hands, ~06:00-08:41 UTC): 40 more real
  `evolve` generations against the live v3 (1d) champion, no promotion —
  cumulative candidates tried against v3 rose 117967 → 118514 (per
  `researcher_memory.tested`), stagnation/boldness counter 8555 → 8595. A
  first, larger 50-generation attempt on the same slot collided with a
  concurrent session's own evolve batch and was discarded — see below.**
  Surveyed the roadmap first: every substantive "Next steps" item is either
  closed or genuinely owner-blocked (item 5's short-selling signal search
  reached "a real ceiling, not bad luck" per the 2026-11-08 weekend writeup
  and needs a different kind of data input this container can't supply;
  items 6/13 need an owner decision already fully written up with no new
  evidence to add). Decided to use this session's deeper time budget on a
  real search batch larger than any weekday 3-hourly slot (15 generations
  each all week) rather than invent a new structural thread under time
  pressure. **First attempt**: a 50-generation batch from
  `tested`=117762, completed cleanly (118444, stagnation 8590), but
  `git push` was rejected — a concurrent session had already pushed its own
  15-generation batch from the identical starting state (117762 → 117967,
  the entry directly below this one). `git pull --rebase` hit a genuine,
  unresolvable conflict in `live_state.json`: two independently-RNG-seeded
  `evolve` continuations from the same base cannot be hand-merged. Aborted
  the rebase, `git reset --hard origin/main` to adopt the already-pushed
  canonical state, discarding this session's own local, never-pushed,
  now-orphaned 50-generation result (no public history lost — the other
  session's real work is the one that survives). **Second attempt**, on the
  new base (`tested`=117967): a fresh 40-generation batch via
  `tools/background_runner.py` (`start` + separate `wait`), run after a
  baseline `pytest` pass, exit code 0, no truncation. Champion's
  fold-aggregate fitness held flat at 1.556 throughout (974 trades, 39%
  win, 1% stops, 3 halts). Best-of-generation fold-fitness ranged roughly
  1.164-2.655, never clearing the promotion-margin bar. See
  `runs/2026-11-15-0841-weekend-all-hands.md` for the full account,
  including a note for future sessions on this exact collision pattern
  (two scheduled routines evolving from the same base concurrently — a new
  failure mode beyond the shallow-clone staleness `git_sync.py` already
  handles; no code change needed, just recognize it and reset rather than
  attempt a manual JSON merge). Verified before commit: `python3 -m
  pytest -q` 505/505 both before (post-reset baseline) and after; top-level
  key diff of `live_state.json` showed only `updated`/`researcher_memory`/
  `lineage` changed (genome, broker, journal, hard_call_reviews
  byte-identical); `lineage` length unchanged at 202; `tools/
  edit_bundle_module.py sync --check` clean; `holdout-pressure` re-checked
  post-batch — margin flat at 7.829, draw count rose to 2127 (new
  sealed-holdout draws, all correctly rejected); `review-hard-calls` still
  0 pending; dashboard rebuilt with `EVO_STATE` set (`index.html` shows
  118514 challenger idea(s) tried); `git fetch origin main` immediately
  before this commit confirmed no further remote commits had landed.
  Genome still v3 (1d) live, untouched throughout. Nothing newly queued on
  the trading/evolution side; the next session should check whether either
  owner-call (items 5/6/13) has landed before defaulting to another plain
  evolve batch, since that is now the only unblocked lever left.

- **Run 2026-11-15 (3-hourly check, ~06:47-07:13 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 117762 → 117967 (per
  `researcher_memory.tested`), stagnation/boldness counter 8539 → 8554.**
  No live trading this cycle (tick 93 already handled at the dedicated
  00:20 UTC daily slot, and the prior 3-hourly check's own evolve batch
  already ran at ~03:47-04:00 UTC — confirmed via `live_state.json`'s
  `updated` timestamp at session start, `2026-11-15T04:18:36+00:00`,
  matching `runs/2026-11-15-0400-evolve-batch-v3.md`). Freshness checks:
  `review-hard-calls` still 0 pending (6 reviewed, unchanged), `AGENTS.md`
  size 229,313 bytes at session start — ~26.7KB under the 256KB threshold,
  comfortably clear, not archived this cycle — so, with nothing else
  queued, used the slot for one more real 15-generation batch via
  `tools/background_runner.py` (`start` + separate `wait`), run after a
  baseline `pytest` pass, exit code 0, no truncation. Champion's
  fold-aggregate fitness held flat at 1.556 across all 15 generations (974
  trades, 39% win, 1% stops, 3 halts, unchanged throughout). Best-of-generation
  fold-fitness ranged roughly 1.103-1.891, never clearing the
  promotion-margin bar. See `runs/2026-11-15-0713-evolve-batch-v3.md`.
  Verified before commit: `python3 -m pytest -q` 505/505 both before
  (baseline) and after `evolve`; top-level key diff of `live_state.json`
  (snapshotted before `start`, checked directly in Python against the
  pre-batch copy) showed only `updated`/`researcher_memory`/`lineage`
  changed (genome, broker, journal, hard_call_reviews byte-identical);
  `lineage` length unchanged at 202 (bounded ring buffer, no new promotion
  attempt recorded); `tools/edit_bundle_module.py sync --check` clean;
  `holdout-pressure` re-checked post-batch — margin and draw count both
  unchanged (7.828, 2120) since no candidate this batch cleared the full
  fold-aggregate gate; dashboard rebuilt with `EVO_STATE` set (`index.html`
  shows 117967 challenger idea(s) tried). Genome still v3 (1d) live,
  untouched. Container synced cleanly from `main` via `git checkout main` +
  `python3 tools/git_sync.py` fast-forward through other sessions'
  2026-11-15 commits already pushed, no divergence, no shallow-clone
  staleness this cycle. Hit the recurring `pip3` vs `python3 -m pip`
  numpy/pandas split again — `python3 -m pip install -r requirements.txt
  -q` fixed it immediately, same as prior sessions.

- **Run 2026-11-15 (3-hourly check, ~03:47-04:00 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 117556 → 117762 (per
  `researcher_memory.tested`), stagnation/boldness counter 8524 → 8539.**
  No live trading this cycle (tick 93 already handled at the dedicated
  00:20 UTC daily slot, and the prior 3-hourly check's own evolve batch
  already ran at ~00:47-01:16 UTC — confirmed via `live_state.json`'s
  `updated` timestamp at session start, `2026-11-15T01:13:32+00:00`,
  matching `runs/2026-11-15-0116-evolve-batch-v3.md`). Freshness checks:
  `review-hard-calls` still 0 pending (6 reviewed, unchanged), items 6/13
  still owner decisions, `AGENTS.md` size 249,317 bytes at session start —
  ~6.9KB under the 256KB threshold, tighter than several recent sessions'
  "comfortable to skip" margins (8-25KB) — so archived the next oldest
  remaining slice (all nine 2026-11-13 entries, including that day's own
  embedded archival-action entry) verbatim to new
  `AGENTS_ARCHIVE_2026-11-13.md` first (committed/pushed separately,
  `1f0ada9`, verified byte-for-byte identical against the removed slice),
  cutting this file to 226,527 bytes. With that done, used the rest of the
  slot for one more real 15-generation batch via
  `tools/background_runner.py` (`start` + separate `wait`), run after a
  baseline `pytest` pass, exit code 0, no truncation. Champion's
  fold-aggregate fitness held flat at 1.556 across all 15 generations (974
  trades, 39% win, 1% stops, 3 halts, unchanged throughout). Best-of-generation
  fold-fitness ranged roughly 0.983-1.940, never clearing the
  promotion-margin bar. See `runs/2026-11-15-0400-evolve-batch-v3.md`.
  Verified before commit: `python3 -m pytest -q` 505/505 both before
  (baseline) and after `evolve`; top-level key diff of `live_state.json`
  (snapshotted before `start`, checked directly in Python against the
  pre-batch copy) showed only `updated`/`researcher_memory`/`lineage`
  changed (genome, broker, journal, hard_call_reviews byte-identical);
  `lineage` length unchanged at 202 (bounded ring buffer, no new promotion
  attempt recorded); `tools/edit_bundle_module.py sync --check` clean;
  `holdout-pressure` re-checked post-batch — margin and draw count both
  unchanged (7.828, 2120) since no candidate this batch cleared the full
  fold-aggregate gate; dashboard rebuilt with `EVO_STATE` set (`index.html`
  shows 117762 challenger idea(s) tried). Genome still v3 (1d) live,
  untouched. Container synced cleanly from `main` via `git checkout main` +
  `python3 tools/git_sync.py` fast-forward through other sessions'
  2026-11-15 commits already pushed, no divergence, no shallow-clone
  staleness this cycle.

- **Run 2026-11-15 (3-hourly check, ~00:47-01:16 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 117353 → 117556 (per
  `researcher_memory.tested`), stagnation/boldness counter 8510 → 8524.**
  No live trading this cycle (tick 93 already handled at the dedicated
  00:20 UTC daily slot — confirmed via `live_state.json`'s `updated`
  timestamp at session start, `2026-11-15T00:22:21+00:00`, matching
  `runs/2026-11-15-0020-daily-trading.md`; that run's own `93 % 7 != 0`, so
  no evolve-3 batch ran there either). Freshness checks: `AGENTS.md` size
  246,515 bytes at session start — ~9.6KB under the 256KB threshold, a
  margin recent sessions have judged comfortable enough to skip archival,
  not archived this cycle — so, with nothing else queued, used the slot
  for one more real 15-generation batch via `tools/background_runner.py`
  (`start` + separate `wait`), run after a baseline `pytest` pass, exit
  code 0, no truncation. Champion's fold-aggregate fitness shifted
  1.059 → 1.556 partway through the batch (the daily bar from tick 93
  rolled the fold windows forward, same mechanism every prior session has
  observed) then held flat at 1.556 for the rest (974 trades, 39% win, 1%
  stops, 3 halts, unchanged throughout). Best-of-generation fold-fitness
  ranged roughly 1.074-2.381, never clearing the promotion-margin bar. See
  `runs/2026-11-15-0116-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 505/505 both before (baseline) and after `evolve`;
  top-level key diff of `live_state.json` (snapshotted before `start`,
  checked directly in Python against the pre-batch copy) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  `holdout-pressure` re-checked post-batch — margin essentially flat
  (7.825 → 7.828, tracking the champion's own fitness shift noted above),
  draw count 2110 → 2120 (ten new sealed-holdout draws from this batch's
  fold-aggregate-gate-clearing candidates, all correctly rejected), same
  slow-rise pattern already tracked under item 13, nothing new; dashboard
  rebuilt with `EVO_STATE` set (`index.html` shows 117556 challenger
  idea(s) tried). Genome still v3 (1d) live, untouched. Container synced
  cleanly from `main` via `git checkout main` + `python3 tools/git_sync.py`
  fast-forward through other sessions' 2026-11-14 commits already pushed
  (several evolve batches plus the day's daily discussion and daily
  trading), no divergence, no shallow-clone staleness this cycle.

