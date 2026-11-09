# Archive: AGENTS.md 3-hourly-check / weekend-all-hands log, 2026-11-07

Moved verbatim out of `AGENTS.md`'s "Current state" section on 2026-11-09 (3-hourly check) to keep that file under its 256KB single-read limit. Nothing reworded, nothing lost — see `AGENTS.md`
for the current log and the full archive index.

---

- **Run 2026-11-07 (3-hourly check, ~21:46-22:0x UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 105774 → 105980 (per
  `researcher_memory.tested`), stagnation/boldness counter 7667 → 7682.**
  No live trading this cycle (tick 85 already handled at the dedicated
  00:20 UTC daily slot, and the weekend all-hands, the 09:00 UTC daily
  discussion, and four prior 3-hourly checks' own evolve batches already
  covered the rest of the day — confirmed via `live_state.json`'s `updated`
  timestamp at session start, `2026-11-07T19:14:26+00:00`, matching
  `runs/2026-11-07-1917-evolve-batch-v3.md`). Freshness checks before
  running: `review-hard-calls` still 0 pending (6 reviewed, unchanged),
  items 6/13 still owner decisions, `AGENTS.md` size 237,213 bytes —
  comfortably under the 256KB threshold, not rotated this cycle — so, with
  nothing else queued, used the slot for one more real 15-generation batch
  via `tools/background_runner.py` (`start` + separate `wait`), run after a
  baseline `pytest` pass, exit code 0, no truncation. Champion's
  fold-aggregate fitness held flat at 1.670 across all 15 generations (1010
  trades, 40% win, 0% stops, 3 halts, unchanged throughout).
  Best-of-generation fold-fitness ranged roughly 1.164-2.933, never
  clearing the promotion-margin bar. See
  `runs/2026-11-07-2200-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 493/493 both before (baseline) and after `evolve`;
  top-level key diff of `live_state.json` (snapshotted before `start`,
  checked directly in Python against the pre-batch copy) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  `holdout-pressure` re-checked post-batch — margin held flat (7.766), draw
  count 1879 → 1880 (one new sealed-holdout draw from this batch's
  fold-aggregate-gate-clearing candidate, correctly rejected), same
  slow-rise pattern already tracked under item 13, nothing new; dashboard
  rebuilt with `EVO_STATE` set (`index.html` shows 105980 challenger
  idea(s) tried). Genome still v3 (1d) live, untouched. Container synced
  cleanly from `main` via `git checkout main` + `tools/git_sync.py`
  fast-forward, no divergence, no shallow-clone staleness this cycle. Hit
  the recurring `pip3` vs `python3 -m pip` numpy/pandas split on this
  container (already tracked under items 9/12's history) — `python3 -m pip
  install -r requirements.txt -q` fixed it immediately.

- **Run 2026-11-07 (3-hourly check, ~18:46-19:17 UTC): archived the oldest
  remaining AGENTS.md slice, then 15 more real `evolve` generations against
  the live v3 (1d) champion, no promotion — cumulative candidates tried
  against v3 rose 105566 → 105774 (per `researcher_memory.tested`),
  stagnation/boldness counter 7651 → 7666.** No live trading this cycle
  (tick 85 already handled at the dedicated 00:20 UTC daily slot, and the
  06:00 UTC weekend all-hands, the 09:00 UTC daily discussion, and four
  prior 3-hourly checks' own evolve batches already covered the rest of
  the day — confirmed via `live_state.json`'s `updated` timestamp at
  session start, `2026-11-07T16:13:14+00:00`, matching
  `runs/2026-11-07-1615-evolve-batch-v3.md`). Freshness checks before
  running: `review-hard-calls` still 0 pending (6 reviewed, unchanged),
  items 6/13 still owner decisions, `AGENTS.md` size 255,947 bytes —
  within ~6.0KB of the 256KB threshold, within the margin range every
  prior rotation in this index has used to trigger one — so archived the
  oldest remaining slice (all eight 2026-11-05 3-hourly-check entries)
  verbatim to new `AGENTS_ARCHIVE_2026-11-05.md` first, cutting the live
  file to 234,064 bytes; verified via exact line-range removal (the
  removed 320-line block diffed byte-for-byte identical against the new
  archive file's body) and `python3 -m pytest -q` 493/493 unaffected.
  Committed and pushed as `2897ded` before starting evolve work. Then,
  with nothing else queued, used the slot for one more real 15-generation
  batch via `tools/background_runner.py` (`start` + separate `wait`), run
  after a baseline `pytest` pass, exit code 0, no truncation. Champion's
  fold-aggregate fitness held flat at 1.670 across all 15 generations
  (1010 trades, 40% win, 0% stops, 3 halts, unchanged throughout).
  Best-of-generation fold-fitness ranged roughly 1.543-2.933, never
  clearing the promotion-margin bar. See
  `runs/2026-11-07-1917-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 493/493 both before (baseline, right after the
  archival commit) and after `evolve`; top-level key diff of
  `live_state.json` (snapshotted before `start`, checked directly in
  Python against the pre-batch copy) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker,
  journal, hard_call_reviews byte-identical); `lineage` length unchanged
  at 202 (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  `holdout-pressure` re-checked post-batch — margin rose slightly
  (7.765 → 7.766), draw count 1877 → 1879 (two new sealed-holdout draws
  from this batch's fold-aggregate-gate-clearing candidates, both correctly
  rejected), same slow-rise pattern already tracked under item 13, nothing
  new; dashboard rebuilt with `EVO_STATE` set (`index.html` shows 105774
  challenger idea(s) tried). Genome still v3 (1d) live, untouched.
  Container synced cleanly from `main` via `git checkout main` +
  `tools/git_sync.py` fast-forward, no divergence, no shallow-clone
  staleness this cycle.

- **Run 2026-11-07 (3-hourly check, ~15:46-16:15 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 105360 → 105566 (per
  `researcher_memory.tested`), stagnation/boldness counter 7637 → 7651.**
  No live trading this cycle (tick 85 already handled at the dedicated
  00:20 UTC daily slot, and the 06:00 UTC weekend all-hands, the 09:00 UTC
  daily discussion, and three prior 3-hourly checks' own evolve batches
  already covered the rest of the day — confirmed via `live_state.json`'s
  `updated` timestamp at session start, `2026-11-07T13:12:51+00:00`,
  matching `runs/2026-11-07-1315-evolve-batch-v3.md`). Freshness checks
  before running: `review-hard-calls` still 0 pending (6 reviewed,
  unchanged), items 6/13 still owner decisions, `AGENTS.md` size 253,037
  bytes — within ~8.9KB of the 256KB threshold, a wider margin than the
  tightest rotations logged in this index but comparable to a couple of
  prior "not rotated" calls at similar margins — judged comfortable enough
  to skip archival this cycle and spend the slot on real search work
  instead. With nothing else queued, used the slot for one more real
  15-generation batch via `tools/background_runner.py` (`start` + separate
  `wait`), run after a baseline `pytest` pass, exit code 0, no truncation.
  Champion's fold-aggregate fitness held flat at 1.670 across all 15
  generations (1010 trades, 40% win, 0% stops, 3 halts, unchanged
  throughout). Best-of-generation fold-fitness ranged roughly 1.541-2.254,
  never clearing the promotion-margin bar. See
  `runs/2026-11-07-1615-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 493/493 both before (baseline) and after `evolve`;
  top-level key diff of `live_state.json` (snapshotted before `start`, not
  after `wait`, checked directly in Python against the pre-batch copy)
  showed only `updated`/`researcher_memory`/`lineage` changed (genome,
  broker, journal, hard_call_reviews byte-identical); `lineage` length
  unchanged at 202 (bounded ring buffer, no new promotion attempt
  recorded); `tools/edit_bundle_module.py verify`/`sync --check` both
  clean; `holdout-pressure` re-checked post-batch — margin rose slightly
  (7.764 → 7.765), draw count 1874 → 1877 (three new sealed-holdout draws
  from this batch's fold-aggregate-gate-clearing candidates, all correctly
  rejected), same slow-rise pattern already tracked under item 13, nothing
  new; dashboard rebuilt with `EVO_STATE` set (`index.html` shows 105566
  challenger idea(s) tried). Genome still v3 (1d) live, untouched.
  Container synced cleanly from `main` via `git checkout main` +
  `tools/git_sync.py` fast-forward through today's weekend all-hands,
  daily-discussion, and prior 3-hourly checks' own commits already
  pushed, no divergence, no shallow-clone staleness this cycle.

- **Run 2026-11-07 (3-hourly check, ~12:47-13:1x UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 105154 → 105360 (per
  `researcher_memory.tested`), stagnation/boldness counter 7622 → 7637.**
  No live trading this cycle (tick 85 already handled at the dedicated
  00:20 UTC daily slot, and the 06:00 UTC weekend all-hands, the 09:00 UTC
  daily discussion, and two prior 3-hourly checks' own evolve batches
  already covered the rest of the morning — confirmed via `live_state.json`'s
  `updated` timestamp at session start, `2026-11-07T10:07:19+00:00`,
  matching `runs/2026-11-07-0946-evolve-batch-v3.md`). Freshness checks
  before running: `review-hard-calls` still 0 pending (6 reviewed,
  unchanged), items 6/13 still owner decisions, `AGENTS.md` size 250,120
  bytes — comfortably under the 256KB threshold, not rotated this cycle —
  so, with nothing else queued, used the slot for one more real
  15-generation batch via `tools/background_runner.py` (`start` + separate
  `wait`), run after a baseline `pytest` pass, exit code 0, no truncation.
  Champion's fold-aggregate fitness held flat at 1.670 across all 15
  generations (1010 trades, 40% win, 0% stops, 3 halts, unchanged
  throughout). Best-of-generation fold-fitness ranged roughly 1.345-2.254,
  never clearing the promotion-margin bar. See
  `runs/2026-11-07-1315-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 493/493 both before (baseline) and after `evolve`;
  top-level key diff of `live_state.json` (snapshotted before `start`, not
  after `wait`, checked directly in Python against the pre-batch copy, not
  just eyeballed) showed only `updated`/`researcher_memory`/`lineage`
  changed (genome, broker, journal, hard_call_reviews byte-identical);
  `lineage` length unchanged at 202 (bounded ring buffer, no new promotion
  attempt recorded); `tools/edit_bundle_module.py verify`/`sync --check`
  both clean; `holdout-pressure` re-checked post-batch — margin held
  essentially flat (7.764), draw count 1872 → 1874 (two new sealed-holdout
  draws from this batch's fold-aggregate-gate-clearing candidates, both
  correctly rejected), same slow-rise pattern already tracked under item
  13, nothing new; dashboard rebuilt with `EVO_STATE` set (`index.html`
  shows 105360 challenger idea(s) tried). Genome still v3 (1d) live,
  untouched. Container synced cleanly from `main` via `git checkout main`
  + `tools/git_sync.py` fast-forward through today's weekend all-hands,
  daily-discussion, and two prior 3-hourly checks' commits already pushed,
  no divergence, no shallow-clone staleness this cycle. Hit the recurring
  `pip3` vs `python3 -m pip` numpy/pandas split on this container (already
  tracked under items 9/12's history) — `python3 -m pip install -r
  requirements.txt -q` fixed it immediately.

- **Run 2026-11-07 (3-hourly check, ~09:46-10:1x UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 104949 → 105154 (per
  `researcher_memory.tested`), stagnation/boldness counter 7607 → 7622.**
  No live trading this cycle (tick 85 already handled at the dedicated
  00:20 UTC daily slot, and the 06:00 UTC weekend all-hands, the 09:00 UTC
  daily discussion, and the prior 3-hourly check's own evolve batch already
  covered the rest of the morning — confirmed via `live_state.json`'s
  `updated` timestamp at session start, `2026-11-07T07:15:17+00:00`,
  matching `runs/2026-11-07-0716-evolve-batch-v3.md`). Freshness checks
  before running: `review-hard-calls` still 0 pending (6 reviewed,
  unchanged), items 6/13 still owner decisions, `AGENTS.md` size 247,485
  bytes — comfortably under the 256KB threshold, not rotated this cycle —
  so, with nothing else queued, used the slot for one more real
  15-generation batch via `tools/background_runner.py` (`start` + separate
  `wait`), run after a baseline `pytest` pass, exit code 0, no truncation.
  Champion's fold-aggregate fitness held flat at 1.670 across all 15
  generations (1010 trades, 40% win, 0% stops, 3 halts, unchanged
  throughout). Best-of-generation fold-fitness ranged roughly 1.658-2.931,
  never clearing the promotion-margin bar. See
  `runs/2026-11-07-0946-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 493/493 both before (baseline) and after `evolve`;
  top-level key diff of `live_state.json` (checked directly in Python
  against the pre-batch copy, not just eyeballed) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  `holdout-pressure` re-checked post-batch — margin rose slightly
  (7.763 → 7.764), draw count 1870 → 1872 (two new sealed-holdout draws
  from this batch's fold-aggregate-gate-clearing candidates, both correctly
  rejected), same slow-rise pattern already tracked under item 13, nothing
  new; dashboard rebuilt with `EVO_STATE` set (`index.html` shows 105154
  challenger idea(s) tried). Genome still v3 (1d) live, untouched. Container
  synced cleanly from `main` via `git checkout main` + `tools/git_sync.py`
  fast-forward through today's weekend all-hands and daily-discussion
  commits already pushed, no divergence, no shallow-clone staleness this
  cycle.

- **Run 2026-11-07 (3-hourly check, ~06:47-07:16 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 104743 → 104949 (per
  `researcher_memory.tested`), stagnation/boldness counter 7592 → 7607.**
  No live trading this cycle (tick 85 already handled at the dedicated
  00:20 UTC daily slot, and the 06:00 UTC weekend all-hands already shipped
  a real item-5 result this morning — confirmed via `live_state.json`'s
  `updated` timestamp at session start, `2026-11-07T04:10:58+00:00`,
  matching `runs/2026-11-07-0413-evolve-batch-v3.md`). Freshness checks
  before running: `review-hard-calls` still 0 pending (6 reviewed,
  unchanged), items 6/13 still owner decisions, `AGENTS.md` size 244,402
  bytes — comfortably under the 256KB threshold, not rotated this cycle —
  so, with nothing else queued, used the slot for one more real
  15-generation batch via `tools/background_runner.py` (`start` + separate
  `wait`), run after a baseline `pytest` pass, exit code 0, no truncation.
  Champion's fold-aggregate fitness held flat at 1.670 across all 15
  generations (1010 trades, 40% win, 0% stops, 3 halts, unchanged
  throughout). Best-of-generation fold-fitness ranged roughly 1.094-2.581,
  never clearing the promotion-margin bar. See
  `runs/2026-11-07-0716-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 493/493 both before and after `evolve` (one
  transient failure seen mid-verification traced to this session
  accidentally running two pytest invocations concurrently, not a real
  regression — a clean re-run came back 493/493); genome version still 3
  (checked directly), `lineage` length unchanged at 202 (bounded ring
  buffer, no new promotion attempt recorded) — confirmed via the evolve
  log's own generation-by-generation output since this session's attempted
  pre/post snapshot diff was taken too late to be a true before-batch copy
  (flagged in the run note so a future session snapshots `live_state.json`
  *before* calling `background_runner start`, not after the `wait`
  notification arrives); `tools/edit_bundle_module.py verify`/`sync --check`
  both clean; `holdout-pressure` re-checked post-batch — margin and draw
  count both held exactly flat (7.763, draw 1870 — same as the prior 04:13
  batch's end state, none of this batch's candidates cleared the
  fold-aggregate gate at a new draw), same slow-rise pattern already
  tracked under item 13, nothing new; dashboard rebuilt with `EVO_STATE`
  set (`index.html` shows 104949 challenger idea(s) tried). Genome still v3
  (1d) live, untouched. Container synced cleanly from `main` via `git
  checkout main` + `tools/git_sync.py` fast-forward through the weekend
  all-hands commit already pushed today, no divergence, no shallow-clone
  staleness this cycle. Hit the recurring `pip3` vs `python3 -m pip`
  numpy/pandas split on this container (already tracked under items
  9/12's history) — `python3 -m pip install -r requirements.txt -q` fixed
  it immediately.

- **Run 2026-11-07 (weekend all-hands, ~06:00-07:xx UTC): shipped item 5's
  dual-breadth-trend short signal (combines dual-trend's temporal filter
  with breadth-trend's cross-sectional filter) and out-of-sample-checked
  it against each ingredient's own already-validated parameter values —
  the first positive mean-return result anywhere in this item's whole
  `-oos` history, but non-dominant across tilings and still a loss in the
  one real crash window.** New `loop.engine.benchmark_dual_breadth_trend_short`
  (9 new tests, `tests/test_dual_breadth_trend_short.py`, full suite
  484 → 493), wired into `short-headroom --dual-breadth` and new CLI
  `dual-breadth-trend-oos`. At the 1.1333y independent tiling (9 windows,
  2 bearish), `slope_lookback=20, breadth_threshold=0.5` scored +2.1% mean
  return across all 8 valid windows — beating trend-break (−10.3%) and
  both breadth-alone thresholds (−9.5%/−9.8%), and the first positive
  number any variant has scored in this metric across regime-combo,
  dual-trend, or breadth-trend's own prior `-oos` checks. At the 2.0y
  tiling (5 windows, all bull) that same cell was only middling (+0.9%);
  breadth-alone at threshold 0.7 was best there (+4.9%) — no single cell
  dominates both tilings, the same non-dominance pattern this item's
  history keeps finding. One sub-finding held in both tilings: adding the
  slope filter on top of `breadth_threshold=0.5` helped in every case
  checked, on top of `0.7` hurt in every case checked. The LUNA/FTX crash
  window is still a net loss for every variant, including the best cell
  found (−23.9%, the smallest loss recorded this session but not a
  profit). No `live_state.json` or constitution change — see item 5 below
  for the full writeup and `runs/2026-11-07-0600-weekend-all-hands.md`.

- **Run 2026-11-07 (3-hourly check, ~03:46-04:13 UTC): archived the oldest
  remaining AGENTS.md slice, then 15 more real `evolve` generations against
  the live v3 (1d) champion, no promotion — cumulative candidates tried
  against v3 rose 104537 → 104743 (per `researcher_memory.tested`),
  stagnation/boldness counter 7577 → 7591.** No live trading this cycle
  (tick 85 already handled at the dedicated 00:20 UTC daily slot, and the
  prior 3-hourly check's own evolve batch already ran at ~00:46-01:17 UTC —
  confirmed via `live_state.json`'s `updated` timestamp at session start,
  `2026-11-07T01:15:02+00:00`, matching `runs/2026-11-07-0117-evolve-batch-v3.md`).
  Freshness checks before running: `review-hard-calls` still 0 pending (6
  reviewed, unchanged), items 6/13 still owner decisions, `AGENTS.md` size
  256,667 bytes — within ~5.4KB of the 256KB threshold, within the margin
  range every prior rotation in this index has used to trigger one — so
  archived the oldest remaining slice (all nine 2026-11-04 3-hourly-check
  entries) verbatim to new `AGENTS_ARCHIVE_2026-11-04.md` first, cutting
  the live file to 234,058 bytes; verified via exact line-range removal
  (the removed 331-line block diffed byte-for-byte identical against the
  new archive file's body) and `python3 -m pytest -q` 484/484 unaffected.
  Committed and pushed as `3c98ff6` before starting evolve work. Then, with
  nothing else queued, used the slot for one more real 15-generation batch
  via `tools/background_runner.py` (`start` + separate `wait`), run after a
  baseline `pytest` pass, exit code 0, no truncation. Champion's
  fold-aggregate fitness held flat at 1.670 across all 15 generations (1010
  trades, 40% win, 0% stops, 3 halts, unchanged throughout).
  Best-of-generation fold-fitness ranged roughly 1.471-2.086, never
  clearing the promotion-margin bar. See
  `runs/2026-11-07-0413-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 484/484 both before (baseline, right after the
  archival commit) and after `evolve`; top-level key diff of
  `live_state.json` (checked directly in Python against the pre-batch
  copy, not just eyeballed) showed only `updated`/`researcher_memory`/
  `lineage` changed (genome, broker, journal, hard_call_reviews
  byte-identical); `lineage` length unchanged at 202 (bounded ring buffer,
  no new promotion attempt recorded); `tools/edit_bundle_module.py
  verify`/`sync --check` both clean; `holdout-pressure` re-checked against
  pre/post-batch snapshots directly (read-only, no state change) — margin
  held flat (7.763), draw count 1867 → 1868 (one new sealed-holdout draw
  from this batch's fold-aggregate-gate-clearing candidate, correctly
  rejected), same slow-rise pattern already tracked under item 13, nothing
  new; dashboard rebuilt with `EVO_STATE` set (`index.html` shows 104743
  challenger idea(s) tried). Genome still v3 (1d) live, untouched. Container
  started in detached HEAD; `git checkout main` + `tools/git_sync.py`
  fast-forwarded cleanly, no shallow-clone staleness this cycle.

- **Run 2026-11-07 (3-hourly check, ~00:46-01:17 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 104333 → 104537 (per
  `researcher_memory.tested`), stagnation/boldness counter 7562 → 7576.**
  No live trading this cycle (tick 85 already handled at the dedicated
  00:20 UTC daily slot — confirmed via `live_state.json`'s `updated`
  timestamp at session start, `2026-11-07T00:22:35+00:00`, matching
  `runs/2026-11-07-0020-daily-trading.md`; `85 % 7 == 1` so no `evolve` ran
  as part of that tick either). Freshness checks before running:
  `review-hard-calls` still 0 pending (6 reviewed, unchanged), items 6/13
  still owner decisions, `AGENTS.md` size 248,346 bytes — comfortably under
  the 256KB threshold, not rotated this cycle — so, with nothing else
  queued, used the slot for one more real 15-generation batch via
  `tools/background_runner.py` (`start` + separate `wait`), run after a
  baseline `pytest` pass, exit code 0, no truncation. Champion's
  fold-aggregate fitness held flat at 1.670 across all 15 generations (1010
  trades, 40% win, 0% stops, 3 halts, unchanged throughout).
  Best-of-generation fold-fitness ranged roughly 1.566-2.581, never
  clearing the promotion-margin bar. See
  `runs/2026-11-07-0117-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 484/484 both before (baseline) and after `evolve`;
  top-level key diff of `live_state.json` (checked directly in Python
  against the pre-batch copy, not just eyeballed) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  `holdout-pressure` re-checked against pre/post-batch snapshots directly
  (read-only, no net state change) — margin rose slightly (7.762 → 7.763),
  draw count 1865 → 1867 (two new sealed-holdout draws from this batch's
  fold-aggregate-gate-clearing candidates, both correctly rejected), same
  slow-rise pattern already tracked under item 13, nothing new; dashboard
  rebuilt with `EVO_STATE` set (`index.html` shows 104537 challenger
  idea(s) tried). Genome still v3 (1d) live, untouched. Container synced
  cleanly from `main` via `git checkout main` + `tools/git_sync.py`
  fast-forward through a large batch of other sessions' 2026-11-06/11-07
  commits already pushed, no divergence, no shallow-clone staleness this
  cycle. Hit the recurring `pip3` vs `python3 -m pip` numpy/pandas split on
  this container (already tracked under items 9/12's history) — `python3
  -m pip install -r requirements.txt -q` fixed it immediately.
