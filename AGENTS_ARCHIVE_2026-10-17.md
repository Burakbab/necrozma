# Archived AGENTS.md entries — 2026-10-17

This file holds a verbatim slice of `AGENTS.md`'s "Current state" log, moved
out to keep the live file under its 256KB single-read limit. Nothing here was
reworded or lost — it's an exact cut of the eight 2026-10-17 3-hourly-check /
weekend-all-hands entries, in original order. See `AGENTS.md` itself for
everything from 2026-10-18 onward, the full "Owner decisions pending",
promotion-history, "Measured", and "Rules" sections (never part of any
rotation), and the index of all other archive files.

---

- **Run 2026-10-17 (3-hourly check, ~21:46-22:20 UTC): archived the oldest
  remaining AGENTS.md slice, then 15 more real `evolve` generations against
  the live v3 (1d) champion, no promotion — cumulative candidates tried
  against v3 rose 70469 → 70674 (per `researcher_memory.tested`),
  stagnation/boldness counter 5098 → 5113.** No live trading this cycle
  (tick 64 already handled at the dedicated 00:20 UTC daily slot, and the
  09:00 UTC daily discussion plus five prior 3-hourly checks today already
  covered the rest of today — confirmed via `live_state.json`'s `updated`
  timestamp at session start, `2026-10-17T19:14:15+00:00`, matching
  `runs/2026-10-17-1920-evolve-batch-v3.md`). Freshness checks before
  running: `review-hard-calls` still 0 pending (6 reviewed, unchanged),
  items 6/13 still owner decisions, `AGENTS.md` size 252,940 bytes — within
  ~3KB of the 256KB threshold, close enough to the margin prior rotations
  have used to trigger one — so archived the oldest remaining slice (all
  eight 2026-10-14 3-hourly-check entries) verbatim to new
  `AGENTS_ARCHIVE_2026-10-14.md` first, cutting the live file to 231,156
  bytes; verified via exact line-slice removal (the removed 329-line block
  diffed byte-for-byte identical against the new archive file's body) and
  `python3 -m pytest -q` 474/474 unaffected. Committed and pushed as
  `cb5b44c` before starting evolve work. Then, with nothing else queued,
  used the slot for one more real 15-generation batch via
  `tools/background_runner.py` (`start` + separate `wait`), run after a
  baseline `pytest` pass, exit code 0, no truncation, ~25 minutes
  (`waited_seconds: 1500.07`). Champion's fold-aggregate fitness held flat
  at 1.287 across all 15 generations (972 trades, 37% win, 1% stops, 4
  halts, unchanged throughout). Best-of-generation fold-fitness ranged
  roughly 1.180-2.582, never clearing the promotion-margin bar. See
  `runs/2026-10-17-2220-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 474/474 both before (baseline, right after the
  archival commit) and after `evolve`; top-level key diff of
  `live_state.json` (checked directly in Python against the pre-batch
  baseline copy, not just eyeballed) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  `holdout-pressure` re-checked (read-only, no state change) — margin rose
  slightly (7.592 → 7.593), draw count 1346 → 1349 (three new sealed-holdout
  draws from this batch's fold-aggregate-gate-clearing candidates, all
  correctly rejected), same slow-rise pattern already tracked under item
  13, nothing new; dashboard rebuilt with `EVO_STATE` set (`index.html`
  shows 70674 challenger ideas tried). Genome still v3 (1d) live, untouched.
  Container synced cleanly from `main` via `git checkout main` + `git pull
  --rebase` at session start (fetch reported a "forced update" on `main`,
  matching the documented shallow-clone-staleness pattern — rebase applied
  cleanly, no real divergence).

- **Run 2026-10-17 (3-hourly check, ~18:46-19:20 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 70261 → 70469 (per
  `researcher_memory.tested`), stagnation/boldness counter 5082 → 5097.**
  No live trading this cycle (tick 64 already handled at the dedicated
  00:20 UTC daily slot, and the 09:00 UTC daily discussion plus three prior
  3-hourly checks' own evolve batches already covered the rest of today —
  confirmed via `live_state.json`'s `updated` timestamp at session start,
  `2026-10-17T16:12:44+00:00`, matching `runs/2026-10-17-1613-evolve-batch-v3.md`).
  Freshness checks before running: `review-hard-calls` still 0 pending (6
  reviewed, unchanged), items 6/13 still owner decisions, `AGENTS.md` size
  250,125 bytes — comfortably under the 256KB threshold, not rotated this
  cycle — so, with nothing else queued, used the slot for one more real
  15-generation batch via `tools/background_runner.py` (`start` + separate
  `wait`), run concurrently with the baseline `pytest` pass, exit code 0,
  no truncation, ~19 minutes of actual evolve runtime (three `wait` calls
  needed across the session, each hitting its own 600s backgrounding
  timeout while the detached process kept running, confirmed alive via
  `ps`/log at generations 6/15 and 12/15; the final `wait` returned
  cleanly at 15/15). Champion's fold-aggregate fitness held flat at 1.287
  across all 15 generations (972 trades, 37% win, 1% stops, 4 halts,
  unchanged throughout). Best-of-generation fold-fitness ranged roughly
  1.264-2.853, never clearing the promotion-margin bar. See
  `runs/2026-10-17-1920-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 474/474 both before (baseline) and after `evolve`;
  top-level key diff of `live_state.json` (checked directly in Python
  against the pre-batch baseline copy, not just eyeballed) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  `holdout-pressure` re-checked (read-only, no state change) — margin rose
  slightly (7.590 → 7.592), draw count 1342 → 1346 (four new sealed-holdout
  draws from this batch's fold-aggregate-gate-clearing candidates, all
  correctly rejected), same slow-rise pattern already tracked under item
  13, nothing new; dashboard rebuilt with `EVO_STATE` set (`index.html`
  shows 70469 challenger ideas tried). Genome still v3 (1d) live, untouched.
  Container synced cleanly from `main` via `tools/git_sync.py` fast-forward,
  no divergence, no shallow-clone staleness this cycle.

- **Run 2026-10-17 (3-hourly check, ~15:46-16:13 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 70056 → 70261 (per
  `researcher_memory.tested`), stagnation/boldness counter 5067 → 5082.**
  No live trading this cycle (tick 64 already handled at the dedicated
  00:20 UTC daily slot, and the 09:00 UTC daily discussion plus two prior
  3-hourly checks' own evolve batches already covered the rest of today —
  confirmed via `live_state.json`'s `updated` timestamp at session start,
  `2026-10-17T13:12:01+00:00`, matching `runs/2026-10-17-1313-evolve-batch-v3.md`).
  Freshness checks before running: `review-hard-calls` still 0 pending (6
  reviewed, unchanged), items 6/13 still owner decisions, `AGENTS.md` size
  247,052 bytes — comfortably under the 256KB threshold, not rotated this
  cycle — so, with nothing else queued, used the slot for one more real
  15-generation batch via `tools/background_runner.py` (`start` + separate
  `wait`), run concurrently with the baseline `pytest` pass, exit code 0,
  no truncation, ~25 minutes (two `wait` calls each hit their own 600s
  backgrounding timeout while the detached process kept running, confirmed
  alive via `ps`/log at generations 6/15 and 13/15 respectively; a third
  `wait` returned cleanly). Champion's fold-aggregate fitness held flat at
  1.287 across all 15 generations (972 trades, 37% win, 1% stops, 4 halts,
  unchanged throughout). Best-of-generation fold-fitness ranged roughly
  1.319-2.221, never clearing the promotion-margin bar. See
  `runs/2026-10-17-1613-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 474/474 both before (baseline) and after `evolve`;
  top-level key diff of `live_state.json` (checked directly in Python
  against the pre-batch baseline copy, not just eyeballed) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  `holdout-pressure` re-checked (read-only, no state change) — margin rose
  slightly (7.588 → 7.590), draw count 1335 → 1342 (seven new sealed-holdout
  draws from this batch's fold-aggregate-gate-clearing candidates, all
  correctly rejected), same slow-rise pattern already tracked under item
  13, nothing new; dashboard rebuilt with `EVO_STATE` set (`index.html`
  shows 70261 challenger ideas tried). Genome still v3 (1d) live, untouched.
  Container synced cleanly from `main` via `git checkout main` + `git pull
  --rebase` (fetch reported a "forced update" on `main`, matching the
  documented shallow-clone-staleness pattern — rebase applied cleanly, no
  real divergence). Hit the recurring `pip3` vs `python3 -m pip`
  numpy/pandas split on this container (already tracked under items 9/12's
  history) — `python3 -m pip install -r requirements.txt -q` fixed it
  immediately.

- **Run 2026-10-17 (3-hourly check, ~12:46-13:13 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 69848 → 70056 (per
  `researcher_memory.tested`), stagnation/boldness counter 5053 → 5067.**
  No live trading this cycle (tick 64 already handled at the dedicated
  00:20 UTC daily slot, and the 09:00 UTC daily discussion plus the prior
  3-hourly check's own evolve batch already covered the rest of today —
  confirmed via `live_state.json`'s `updated` timestamp at session start,
  `2026-10-17T10:12:31+00:00`, matching `runs/2026-10-17-1012-evolve-batch-v3.md`).
  Freshness checks before running: `review-hard-calls` still 0 pending (6
  reviewed, unchanged), items 6/13 still owner decisions, `AGENTS.md` size
  244,475 bytes — comfortably under the 256KB threshold, not rotated this
  cycle — so, with nothing else queued, used the slot for one more real
  15-generation batch via `tools/background_runner.py` (`start` + separate
  `wait`), run concurrently with the baseline `pytest` pass, exit code 0,
  no truncation, ~23.3 minutes (`waited_seconds: 1400.07`). Champion's
  fold-aggregate fitness held flat at 1.287 across all 15 generations (972
  trades, 37% win, 1% stops, 4 halts, unchanged throughout). Best-of-generation
  fold-fitness ranged roughly 1.218-2.853, never clearing the promotion-margin
  bar. See `runs/2026-10-17-1313-evolve-batch-v3.md`. Verified before
  commit: `python3 -m pytest -q` 474/474 both before (baseline) and after
  `evolve`; top-level key diff of `live_state.json` (checked directly in
  Python against the pre-batch baseline copy, not just eyeballed) showed
  only `updated`/`researcher_memory`/`lineage` changed (genome, broker,
  journal, hard_call_reviews byte-identical); `lineage` length unchanged at
  202 (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  `holdout-pressure` re-checked (read-only, no state change) — margin rose
  slightly (7.585 → 7.588), draw count 1330 → 1335 (five new sealed-holdout
  draws from this batch's fold-aggregate-gate-clearing candidates, all
  correctly rejected), same slow-rise pattern already tracked under item
  13, nothing new; dashboard rebuilt with `EVO_STATE` set (`index.html`
  shows 70056 challenger ideas tried). Genome still v3 (1d) live, untouched.
  Container synced cleanly from `main` via `git checkout main` + `git pull
  --rebase`, no divergence, no shallow-clone staleness this cycle.

- **Run 2026-10-17 (3-hourly check, ~09:46-10:12 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 69641 → 69848 (per
  `researcher_memory.tested`), stagnation/boldness counter 5038 → 5053.**
  No live trading this cycle (tick 64 already handled at the dedicated
  00:20 UTC daily slot, and the 09:00 UTC daily discussion plus the prior
  3-hourly check's own evolve batch already covered the rest of today —
  confirmed via `live_state.json`'s `updated` timestamp at session start,
  `2026-10-17T07:18:22+00:00`, matching `runs/2026-10-17-0718-evolve-batch-v3.md`).
  Freshness checks before running: `review-hard-calls` still 0 pending (6
  reviewed, unchanged), items 6/13 still owner decisions, `AGENTS.md` size
  241,681 bytes — comfortably under the 256KB threshold, not rotated this
  cycle — so, with nothing else queued, used the slot for one more real
  15-generation batch via `tools/background_runner.py` (`start` + separate
  `wait`), run concurrently with the baseline `pytest` pass, exit code 0,
  no truncation, ~27 minutes. Champion's fold-aggregate fitness held flat
  at 1.287 across all 15 generations (972 trades, 37% win, 1% stops, 4
  halts, unchanged throughout). Best-of-generation fold-fitness ranged
  roughly 1.111-2.297, never clearing the promotion-margin bar. See
  `runs/2026-10-17-1012-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 474/474 both before (baseline) and after `evolve`;
  top-level key diff of `live_state.json` (checked directly in Python
  against the pre-batch baseline copy, not just eyeballed) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  `holdout-pressure` re-checked (read-only, no state change) — margin rose
  slightly (7.583 → 7.585), draw count 1324 → 1329 (five new sealed-holdout
  draws from this batch's fold-aggregate-gate-clearing candidates, all
  correctly rejected), same slow-rise pattern already tracked under item
  13, nothing new; dashboard rebuilt with `EVO_STATE` set (`index.html`
  shows 69848 challenger ideas tried). Genome still v3 (1d) live, untouched.
  Container started in detached HEAD (50 commits behind), `git checkout
  main` + `git pull --rebase` fast-forwarded cleanly, no divergence, no
  shallow-clone staleness this cycle. Hit the recurring `pip3` vs `python3
  -m pip` numpy/pandas split on this container (already tracked under
  items 9/12's history) — `python3 -m pip install -r requirements.txt -q`
  fixed it immediately.

- **Run 2026-10-17 (3-hourly check, ~06:46-07:18 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 69435 → 69641 (per
  `researcher_memory.tested`), stagnation/boldness counter 5023 → 5037.**
  No live trading this cycle (tick 64 already handled at the dedicated
  00:20 UTC daily slot, and the prior 3-hourly check's own `dual-trend-oos`
  work plus evolve batch already ran at ~03:47-04:22 UTC — confirmed via
  `live_state.json`'s `updated` timestamp at session start,
  `2026-10-17T04:16:24+00:00`). Freshness checks before running:
  `review-hard-calls` still 0 pending (6 reviewed, unchanged), items 6/13
  still owner decisions, `AGENTS.md` size 238,765 bytes — comfortably under
  the 256KB threshold, not rotated this cycle — so, with nothing else
  queued, used the slot for one more real 15-generation batch via
  `tools/background_runner.py` (`start` + separate `wait`), run
  concurrently with the baseline `pytest` pass, exit code 0, no truncation,
  ~32 minutes (the first `wait` call hit its own 1700s backgrounding
  timeout while the detached process was still finishing generation 15/15,
  confirmed alive via `ps`; a second `wait` with a 600s timeout returned
  cleanly ~50s later). Champion's fold-aggregate fitness held flat at 1.287
  across all 15 generations (972 trades, 37% win, 1% stops, 4 halts,
  unchanged throughout). Best-of-generation fold-fitness ranged roughly
  1.360-1.920, never clearing the promotion-margin bar. See
  `runs/2026-10-17-0718-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 474/474 both before (baseline) and after `evolve`;
  top-level key diff of `live_state.json` (checked directly in Python
  against the pre-batch baseline copy, not just eyeballed) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  `holdout-pressure` re-checked (read-only, no state change) — margin rose
  slightly (7.581 → 7.583), draw count 1319 → 1324 (five new sealed-holdout
  draws from this batch's fold-aggregate-gate-clearing candidates, all
  correctly rejected), same slow-rise pattern already tracked under item
  13, nothing new; dashboard rebuilt with `EVO_STATE` set (`index.html`
  shows 69641 challenger ideas tried). Genome still v3 (1d) live, untouched.
  Container synced cleanly from `main` via `git checkout main` + `git pull
  --rebase`, no divergence, no shallow-clone staleness this cycle. Hit the
  recurring `pip3` vs `python3 -m pip` numpy/pandas split on this container
  (already tracked under items 9/12's history) — `python3 -m pip install -r
  requirements.txt -q` fixed it immediately.

- **Run 2026-10-17 (weekend all-hands, ~06:00-07:10 UTC): shipped a new
  read-only diagnostic (`dual-trend-oos`) and used it to run the
  out-of-sample validation the 2026-10-11 dual-trend `slope_lookback`
  sweep's own writeup flagged as missing — result is a clean negative:
  the claimed 40-50 "sweet spot" does not survive contact with windows it
  wasn't tuned on.** New `evotrader_bundle.py dual-trend-oos` (168 lines,
  CLI glue only — reuses the already-shipped, already-tested
  `loop.engine.benchmark_trend_break_short`/`benchmark_dual_trend_short`
  as-is, no new library function, no bundle sync needed since CLI
  dispatch isn't a `_SRC` module) re-runs the identical `slope_lookback`
  sweep against `history-perturb --independent`'s own fixed-width,
  non-overlapping window tiling instead of the champion's own 4
  fold/holdout windows the original sweep was read directly off. Ran it
  twice: at the default 2.0y window width, every one of the 5 independent
  windows spanning 2017-2026 turned out to be a bull market (buy&hold
  +18% to +250%), so there was no bear window anywhere in the sweep for
  the captured-edge metric to even be defined — mean return across
  windows favored `lb=20` (-3.1%), not `lb=40-50` (-5.9%/-5.6%). Re-ran at
  1.1333y (the champion's own actual per-fold width) to get real bear
  windows: 2 of 9 windows were genuinely bearish (buy&hold -30.2% and
  -53.3%), and captured-edge there was positive only at `lb=10` (+11.9%,
  and even that was a net loss in the deeper of the two bear windows,
  -34.9% captured) — `lb=40`/`50`, the shipped "sweet spot," captured
  **-6.8%/-8.3%**, i.e. lost money during the real bear markets it exists
  to profit from. Mean return across all 8 valid windows at this width
  also favors `lb=10` (-4.1%) over `lb=40-50` (-9.6%/-7.7%). Both
  independent runs point the same direction — away from, not toward, the
  in-sample sweep's favorite region. See AGENTS.md item 5's new entry
  below (inserted directly after the 2026-10-11 dual-trend writeup) for
  the full numbers and reasoning, and
  `runs/2026-10-17-0600-weekend-all-hands.md` for the session writeup.
  Verified: `python3 -m pytest -q` 474/474 both before and after (no
  library code touched, only CLI glue); `live_state.json` byte-identical
  throughout (diffed directly against a pre-session copy, not just
  eyeballed) — this was genome-independent and read-only the whole way,
  same discipline as every other `short-headroom` variant in this item's
  history. Does not change the shipped function's default
  (`slope_lookback=20`, deliberately never reset to either sweep's
  favorite) or the still-open, owner-gated question of whether to let the
  Researcher open a short at all.

- **Run 2026-10-17 (3-hourly check, ~03:47-04:22 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 69230 → 69435 (per
  `researcher_memory.tested`), stagnation/boldness counter 5008 → 5023.**
  No live trading this cycle (tick 64 already handled at the dedicated
  00:20 UTC daily slot, and the prior 3-hourly check's own evolve batch
  already ran at ~00:47-01:32 UTC — confirmed via `live_state.json`'s
  `updated` timestamp at session start, `2026-10-17T01:28:28+00:00`,
  matching `runs/2026-10-17-0132-evolve-batch-v3.md`). Freshness checks
  before running: `review-hard-calls` still 0 pending (6 reviewed,
  unchanged), items 6/13 still owner decisions, `AGENTS.md` size 252,073
  bytes — comfortably under the 256KB threshold, not rotated this cycle —
  so, with nothing else queued, used the slot for one more real
  15-generation batch via `tools/background_runner.py` (`start` + separate
  `wait`), run concurrently with the baseline `pytest` pass, exit code 0,
  no truncation, ~24.3 minutes (`waited_seconds: 1460.07`). Champion's
  fold-aggregate fitness held flat at 1.287 across all 15 generations (972
  trades, 37% win, 1% stops, 4 halts, unchanged throughout). Best-of-generation
  fold-fitness ranged roughly 1.383-2.464, never clearing the promotion-margin
  bar. See `runs/2026-10-17-0422-evolve-batch-v3.md`. Verified before
  commit: `python3 -m pytest -q` 474/474 both before (baseline) and after
  `evolve`; top-level key diff of `live_state.json` (checked directly in
  Python against the pre-batch baseline copy, not just eyeballed) showed
  only `updated`/`researcher_memory`/`lineage` changed (genome, broker,
  journal, hard_call_reviews byte-identical); `lineage` length unchanged at
  202 (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  `holdout-pressure` re-checked (read-only, no state change) — margin rose
  slightly (7.580 → 7.581), draw count 1315 → 1319 (four new sealed-holdout
  draws from this batch's fold-aggregate-gate-clearing candidates, all
  correctly rejected), same slow-rise pattern already tracked under item
  13, nothing new; dashboard rebuilt with `EVO_STATE` set (`index.html`
  shows 69435 challenger ideas tried). Genome still v3 (1d) live, untouched.
  Container synced cleanly from `main` via `git checkout main` fast-forward,
  no divergence, no shallow-clone staleness this cycle. Hit the recurring
  `pip3` vs `python3 -m pip` numpy/pandas split on this container (already
  tracked under items 9/12's history) — `python3 -m pip install -r
  requirements.txt -q` fixed it immediately.

- **Run 2026-10-17 (3-hourly check, ~00:47-01:32 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 69023 → 69230 (per
  `researcher_memory.tested`), stagnation/boldness counter 4992 → 5007.**
  No live trading this cycle (tick 64 already handled at the dedicated
  00:20 UTC daily slot — confirmed via `live_state.json`'s `updated`
  timestamp at session start, `2026-10-17T00:22:27+00:00`, matching
  `runs/2026-10-17-0020-daily-trading.md`; `64 % 7 == 1` so no `evolve` ran
  as part of that tick). Freshness checks before running: `review-hard-calls`
  still 0 pending (6 reviewed, unchanged), items 6/13 still owner decisions,
  `AGENTS.md` size 249,346 bytes — comfortably under the 256KB threshold,
  not rotated this cycle — so, with nothing else queued, used the slot for
  one more real 15-generation batch via `tools/background_runner.py`
  (`start` + separate `wait`), run concurrently with the baseline `pytest`
  pass, exit code 0, no truncation, ~10 minutes for the evolve process
  itself (two `wait` calls each hit their own backgrounding timeout — 1700s
  then 605s — while the detached process kept running, confirmed alive via
  `ps`/log at generation 12/15; the second `wait` returned cleanly at
  15/15). Champion's fold-aggregate fitness held flat at 1.287 across all
  15 generations (972 trades, 37% win, 1% stops, 4 halts, unchanged
  throughout). Best-of-generation fold-fitness ranged roughly 1.171-1.877,
  never clearing the promotion-margin bar. See
  `runs/2026-10-17-0132-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 474/474 both before (baseline) and after `evolve`;
  top-level key diff of `live_state.json` (checked directly in Python
  against the pre-batch baseline copy, not just eyeballed) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  `holdout-pressure` re-checked (read-only, no state change) — margin rose
  slightly (7.579 → 7.580), draw count 1311 → 1315 (four new sealed-holdout
  draws from this batch's fold-aggregate-gate-clearing candidates, all
  correctly rejected), same slow-rise pattern already tracked under item
  13, nothing new; dashboard rebuilt with `EVO_STATE` set (`index.html`
  shows 69230 challenger ideas tried). Genome still v3 (1d) live, untouched.
  Container synced cleanly from `main` via `git checkout main` fast-forward,
  no divergence, no shallow-clone staleness this cycle.
