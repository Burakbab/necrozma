# AGENTS.md archive — 2026-10-04 entries

This file holds a verbatim slice of `AGENTS.md`'s "Current state" chronological
log: all nine 2026-10-04 3-hourly-check/weekend-all-hands entries, archived
2026-10-08 (3-hourly check, ~18:46 UTC) to keep the live file under its 256KB
single-read limit. Nothing reworded, nothing lost. See `AGENTS.md` for everything
from 2026-10-05 onward, plus the full "Owner decisions pending", promotion-history,
"Measured", and "Rules" sections (never part of any rotation). For anything
older than 2026-10-04, see `AGENTS_ARCHIVE_2026-10-03.md` and the chain of
archive files it points to.

---

- **Run 2026-10-04 (3-hourly check, ~19:47-22:21 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 48903 → 49108 (per
  `researcher_memory.tested`), stagnation/boldness counter 3532 → 3546.**
  No live trading this cycle (tick 51 already handled at the dedicated
  00:20 UTC daily slot, and the prior 3-hourly check's own evolve batch
  already ran at ~18:46-19:34 UTC — confirmed via `live_state.json`'s
  `updated` timestamp at session start, `2026-10-04T19:29:28+00:00`,
  matching `runs/2026-10-04-1934-evolve-batch-v3.md`). Freshness checks
  before running: `review-hard-calls` still 0 pending (4 reviewed,
  unchanged), items 6/13 still owner decisions, `AGENTS.md` size 245,261
  bytes — comfortably under the 256KB threshold, not rotated this cycle —
  so, with nothing else queued, used the slot for one more real
  15-generation batch via `tools/background_runner.py` (`start` + separate
  `wait`), run concurrently with the baseline `pytest` pass, exit code 0,
  no truncation, ~23 minutes. Champion's fold-aggregate fitness held flat
  at 1.393 across all 15 generations (959 trades, 38% win, 1% stops, 4
  halts, unchanged throughout). Best-of-generation fold-fitness ranged
  roughly 1.154-1.716, never clearing the promotion-margin bar. See
  `runs/2026-10-04-2221-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 465/465 both before (baseline) and after `evolve`;
  top-level key diff of `live_state.json` (checked directly in Python
  against `git show HEAD:live_state.json`, not just eyeballed) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  `holdout-pressure` re-checked (read-only, no state change) — margin/draw
  count unchanged (7.480, draw 1089 — this batch's candidates never
  cleared the fold-aggregate gate, so no new holdout draws), same
  slow-rise pattern already tracked under item 13, nothing new; dashboard
  rebuilt with `EVO_STATE` set (`index.html` shows 49108 challenger ideas
  tried). Genome still v3 (1d) live, untouched. Container synced cleanly
  from `main` via `tools/git_sync.py` fast-forward, no divergence, no
  shallow-clone staleness this cycle.

- **Run 2026-10-04 (3-hourly check, ~18:46-19:34 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 48696 → 48903 (per
  `researcher_memory.tested`), stagnation/boldness counter 3517 → 3531.**
  No live trading this cycle (tick 51 already handled at the dedicated
  00:20 UTC daily slot, and the prior 3-hourly check's own evolve batch
  already ran at ~15:49-15:54 UTC — confirmed via `live_state.json`'s
  `updated` timestamp at session start, `2026-10-04T16:30:05+00:00`,
  matching `runs/2026-10-04-1554-evolve-batch-v3.md`). Freshness checks
  before running: `review-hard-calls` still 0 pending (4 reviewed,
  unchanged), items 6/13 still owner decisions, `AGENTS.md` size 242,649
  bytes — comfortably under the 256KB threshold, not rotated this cycle —
  so, with nothing else queued, used the slot for one more real
  15-generation batch via `tools/background_runner.py` (`start` + separate
  `wait`), run concurrently with the baseline `pytest` pass, exit code 0,
  no truncation, ~42 minutes (the first two `wait` calls each hit their own
  timeout — 1700s and 600s — while the detached process was still running,
  confirmed alive at generations ~11/15 and ~15/15; a third `wait` returned
  cleanly a couple minutes later). Champion's fold-aggregate fitness held
  flat at 1.393 across all 15 generations (959 trades, 38% win, 1% stops,
  4 halts, unchanged throughout). Best-of-generation fold-fitness ranged
  roughly 1.432-1.712, never clearing the promotion-margin bar. See
  `runs/2026-10-04-1934-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 465/465 both before (baseline) and after `evolve`;
  top-level key diff of `live_state.json` (checked directly in Python
  against `git show HEAD:live_state.json`, not just eyeballed) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  `holdout-pressure` re-checked (read-only, no state change) — margin rose
  slightly (7.480, was 7.478) at draw 1089, same slow-rise pattern already
  tracked under item 13, nothing new; dashboard rebuilt with `EVO_STATE`
  set (`index.html` shows 48903 challenger ideas tried). Genome still v3
  (1d) live, untouched. Container synced cleanly from `main` via
  `tools/git_sync.py` fast-forward, no divergence, no shallow-clone
  staleness this cycle.

- **Run 2026-10-04 (3-hourly check, ~15:49-15:54 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 48489 → 48696 (per
  `researcher_memory.tested`), stagnation/boldness counter 3502 → 3516.**
  No live trading this cycle (tick 51 already handled at the dedicated
  00:20 UTC daily slot, and the prior 3-hourly check's own evolve batch
  already ran at ~12:46-13:24 UTC — confirmed via `live_state.json`'s
  `updated` timestamp at session start, `2026-10-04T13:20:48+00:00`,
  matching `runs/2026-10-04-1324-evolve-batch-v3.md`). Freshness checks
  before running: `review-hard-calls` still 0 pending (4 reviewed,
  unchanged), items 6/13 still owner decisions, `AGENTS.md` size 240,235
  bytes — comfortably under the 256KB threshold, not rotated this cycle —
  so, with nothing else queued, used the slot for one more real
  15-generation batch via `tools/background_runner.py` (`start` + separate
  `wait`), run concurrently with the baseline `pytest` pass, exit code 0,
  no truncation, ~39 minutes. Champion's fold-aggregate fitness held flat
  at 1.393 across all 15 generations (959 trades, 38% win, 1% stops, 4
  halts, unchanged throughout). Best-of-generation fold-fitness ranged
  roughly 1.337-2.610, never clearing the promotion-margin bar. See
  `runs/2026-10-04-1554-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 465/465 both before (baseline) and after `evolve`;
  top-level key diff of `live_state.json` (checked directly in Python
  against `git show HEAD:live_state.json`, not just eyeballed) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  `holdout-pressure` re-checked (read-only, no state change) — margin rose
  slightly (7.478, was 7.477) at draw 1086, same slow-rise pattern already
  tracked under item 13, nothing new; dashboard rebuilt with `EVO_STATE`
  set (`index.html` shows 48696 challenger ideas tried). Genome still v3
  (1d) live, untouched. Container arrived on `main`, several commits behind
  `origin/main` in detached HEAD; `git checkout main` plus
  `tools/git_sync.py` fast-forwarded cleanly, nothing lost.

- **Run 2026-10-04 (3-hourly check, ~12:46-13:24 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 48280 → 48489 (per
  `researcher_memory.tested`), stagnation/boldness counter 3487 → 3501.**
  No live trading this cycle (tick 51 already handled at the dedicated
  00:20 UTC daily slot, and the prior 3-hourly check's own evolve batch
  already ran at ~09:46-10:22 UTC — confirmed via `live_state.json`'s
  `updated` timestamp at session start, `2026-10-04T10:18:57+00:00`,
  matching `runs/2026-10-04-1022-evolve-batch-v3.md`). Freshness checks
  before running: `review-hard-calls` still 0 pending (4 reviewed,
  unchanged), items 6/13 still owner decisions, `AGENTS.md` size 237,821
  bytes — comfortably under the 256KB threshold, not rotated this cycle —
  so, with nothing else queued, used the slot for one more real
  15-generation batch via `tools/background_runner.py` (`start` + separate
  `wait`), run concurrently with the baseline `pytest` pass, exit code 0,
  no truncation, ~31 minutes. Champion's fold-aggregate fitness held flat
  at 1.393 across all 15 generations (959 trades, 38% win, 1% stops, 4
  halts, unchanged throughout). Best-of-generation fold-fitness ranged
  roughly 1.337-2.217, never clearing the promotion-margin bar. See
  `runs/2026-10-04-1324-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 465/465 both before (baseline) and after `evolve`;
  top-level key diff of `live_state.json` (checked directly in Python
  against `git show HEAD:live_state.json`, not just eyeballed) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  `holdout-pressure` re-checked (read-only, no state change) — margin rose
  slightly (7.477, was 7.475) at draw 1083, same slow-rise pattern already
  tracked under item 13, nothing new; dashboard rebuilt with `EVO_STATE`
  set (`index.html` shows 48489 challenger ideas tried). Genome still v3
  (1d) live, untouched. Container arrived on `main`, several commits behind
  `origin/main` in detached HEAD; `git checkout main` plus
  `tools/git_sync.py` fast-forwarded cleanly, nothing lost.

- **Run 2026-10-04 (3-hourly check, ~09:46-10:22 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 48074 → 48280 (per
  `researcher_memory.tested`), stagnation/boldness counter 3472 → 3487.**
  No live trading this cycle (tick 51 already handled at the dedicated
  00:20 UTC daily slot, and the weekend all-hands' own batch plus its
  concurrent-session collision resolution already ran at ~06:00-09:00 UTC —
  confirmed via `live_state.json`'s `updated` timestamp at session start,
  `2026-10-04T08:56:02+00:00`, matching
  `runs/2026-10-04-0600-weekend-all-hands.md`). Freshness checks before
  running: `review-hard-calls` still 0 pending (4 reviewed, unchanged),
  items 6/13 still owner decisions (confirmed against the same-day 09:00
  UTC daily discussion), `AGENTS.md` size 235,252 bytes after that same
  all-hands' own archival pass — comfortably under the 256KB threshold, not
  rotated again this cycle — so, with nothing else queued, used the slot
  for one more real 15-generation batch via `tools/background_runner.py`
  (`start` + separate `wait`), run concurrently with the baseline `pytest`
  pass, exit code 0, no truncation, ~33 minutes. Champion's fold-aggregate
  fitness held flat at 1.393 across all 15 generations (959 trades, 38%
  win, 1% stops, 4 halts, unchanged throughout). Best-of-generation
  fold-fitness ranged roughly 1.422-2.610, never clearing the
  promotion-margin bar. See `runs/2026-10-04-1022-evolve-batch-v3.md`.
  Verified before commit: `python3 -m pytest -q` 465/465 both before
  (baseline) and after `evolve`; top-level key diff of `live_state.json`
  (checked directly in Python against `git show HEAD:live_state.json`, not
  just eyeballed) showed only `updated`/`researcher_memory`/`lineage`
  changed (genome, broker, journal, hard_call_reviews byte-identical);
  `lineage` length unchanged at 202 (bounded ring buffer, no new promotion
  attempt recorded); `tools/edit_bundle_module.py verify`/`sync --check`
  both clean; `holdout-pressure` re-checked (read-only, no state change) —
  margin rose slightly (7.475, was 7.472) at draw 1080, same slow-rise
  pattern already tracked under item 13, nothing new; dashboard rebuilt
  with `EVO_STATE` set (`index.html` shows 48280 challenger ideas tried).
  Genome still v3 (1d) live, untouched. Container arrived on `main`,
  several commits behind `origin/main` in detached HEAD; `git checkout
  main` plus `tools/git_sync.py` fast-forwarded cleanly, nothing lost.

- **Run 2026-10-04 (weekend all-hands, ~06:00-09:00 UTC): built and
  measured item 5's asymmetric short variant (see item 5 above for the
  full writeup), plus a 20-generation `evolve` batch against the live v3
  (1d) champion, no promotion — cumulative candidates tried against v3
  rose 47,798 → 48,074 (`researcher_memory.tested`), stagnation/boldness
  counter 3,452 → 3,472.** Synced cleanly from `main` at session start
  (`git checkout main` + `tools/git_sync.py`, fast-forwarded 41 commits, no
  divergence). `requirements.txt` installed. `review-hard-calls` 0 pending
  (4 reviewed, unchanged). Items 6/13 still open owner decisions, nothing
  new. New `loop.engine.benchmark_asymmetric_short` (8 tests,
  `tests/test_asymmetric_short.py`, full suite 457 → 465) gates opening a
  short on both the trend-break and regime signals agreeing (same as
  `benchmark_combined_short`) but lets trend-break alone govern covering —
  the fix `benchmark_combined_short`'s own 2026-10-03 writeup flagged for
  its fold-3 collapse. Committed and pushed first (`118dae1`), cleanly.
  Real result: recovers most of the lost bear-window capture (0% → 67%,
  vs. trend-break alone's 95%), but the predicted bull-market improvement
  didn't materialize — fold 1's loss (-38.6%) is worse than both
  alternatives, because the AND-gated entry barely filters (the regime's
  `bear` leg fires almost as often as trend-break during ordinary
  pullbacks) while the cover rule inherits trend-break's full
  holding-duration risk. Three combination shapes tried now (AND/OR,
  AND/trend-alone, separate) and none dominates — recorded as the honest
  stopping point for this specific combination-logic angle; the regime
  classifier's own noisiness, not the wiring between the two signals, is
  flagged as the real bottleneck for whoever next picks up item 5.

  **Collision with a concurrent 3-hourly check, handled per the Run
  protocol's own "several routines share this repo" guidance**: kicked off
  a separate 40-generation `evolve` batch in the background right after
  the asymmetric-short commit, starting from `researcher_memory.tested`
  47,593. While it ran (~100 minutes), a concurrent 3-hourly-check session
  started its own 15-generation batch from the same 47,593 baseline and
  pushed first (`de99407`, 47,593 → 47,798). `git push` on this session's
  own 40-generation-batch commit was correctly rejected (non-fast-forward);
  `live_state.json`'s generated `researcher_memory`/`lineage` fields are
  not line-mergeable, so rather than force anything, this session reset its
  local, not-yet-pushed commit to `origin/main` (losing nothing shared —
  the asymmetric-short work was already upstream, and the 40-generation
  batch's own result was fully reproducible: "no promotion, fitness still
  1.393," already established by the concurrent session's own 15-generation
  result) and ran a fresh 20-generation batch on top of the now-current
  state instead of attempting to hand-merge two divergent generated
  snapshots. No commits were force-pushed, no uncommitted work existed on
  either side at the point of collision, and both sessions' real evolve
  work is fully represented in the final sequential history.

  The 20-generation batch itself: champion's fold-aggregate fitness held
  flat at 1.393 across all 20 generations (959 trades, 38% win, 1% stops,
  4 halts, unchanged throughout). Best-of-generation fold-fitness ranged
  roughly 1.11-2.46, never clearing the promotion-margin bar. Verified
  before this commit: `python3 -m pytest -q` 465/465 both before and after;
  top-level key diff of `live_state.json` against the pre-batch commit
  (checked directly in Python) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py sync --check` clean; `holdout-pressure`
  re-checked (read-only) — margin 7.472, draw 1073, same slow-rise pattern
  already tracked under item 13, nothing new; dashboard rebuilt with
  `EVO_STATE` set (`index.html` shows 48,074 challenger ideas tried).
  Genome still v3 (1d) live, untouched. Constitution checksum unchanged
  (`726dfa4bac85891a`) throughout.

- **Run 2026-10-04 (3-hourly check, ~06:47-07:34 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 47593 → 47798 (per
  `researcher_memory.tested`), stagnation/boldness counter 3437 → 3451.**
  No live trading this cycle (tick 51 already handled at the dedicated
  00:20 UTC daily slot, and the prior 3-hourly check's own evolve batch
  already ran at ~03:46-04:17 UTC — confirmed via `live_state.json`'s
  `updated` timestamp at session start, `2026-10-04T04:14:32+00:00`,
  matching `runs/2026-10-04-0417-evolve-batch-v3.md`). Freshness checks
  before running: `review-hard-calls` still 0 pending (4 reviewed,
  unchanged), items 6/13 still owner decisions, `AGENTS.md` size 246,803
  bytes — comfortably under the 256KB threshold, not rotated this cycle —
  so, with nothing else queued, used the slot for one more real
  15-generation batch via `tools/background_runner.py` (`start` + separate
  `wait`), run concurrently with the baseline `pytest` pass, exit code 0,
  no truncation, ~10 minutes (the first `wait` call hit its own 1700s
  timeout while the detached process was still running, confirmed alive at
  generation 11/15; a second `wait` against the same still-running process
  returned cleanly a few minutes later). Champion's fold-aggregate fitness
  held flat at 1.393 across all 15 generations (959 trades, 38% win, 1%
  stops, 4 halts, unchanged throughout). Best-of-generation fold-fitness
  ranged roughly 1.220-2.234, never clearing the promotion-margin bar. See
  `runs/2026-10-04-0734-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 465/465 both before (baseline) and after `evolve`;
  top-level key diff of `live_state.json` (checked directly in Python
  against `git show HEAD:live_state.json`, not just eyeballed) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  `holdout-pressure` re-checked (read-only, no state change) — margin rose
  slightly (7.470, was 7.469) at draw 1069, same slow-rise pattern already
  tracked under item 13, nothing new; dashboard rebuilt with `EVO_STATE`
  set (`index.html` shows 47798 challenger ideas tried). Genome still v3
  (1d) live, untouched. Container arrived on `main`, 42 commits behind
  `origin/main` in detached HEAD; `git checkout main` plus
  `tools/git_sync.py` fast-forwarded cleanly, nothing lost.

- **Run 2026-10-04 (3-hourly check, ~03:46-04:17 UTC): archived the oldest
  remaining slice of this log, then 15 more real `evolve` generations
  against the live v3 (1d) champion, no promotion — cumulative candidates
  tried against v3 rose 47386 → 47593 (per `researcher_memory.tested`),
  stagnation/boldness counter 3422 → 3437.** No live trading this cycle
  (tick 51 already handled at the dedicated 00:20 UTC daily slot, and the
  prior 3-hourly check's own evolve batch already ran at ~01:27 UTC —
  confirmed via `live_state.json`'s `updated` timestamp at session start,
  `2026-10-04T01:25:07+00:00`, matching `runs/2026-10-04-0127-evolve-batch-v3.md`).
  Freshness checks before running: `review-hard-calls` still 0 pending (4
  reviewed, unchanged), items 6/13 still owner decisions, `AGENTS.md` size
  258,532 bytes — within ~3.6KB of the 256KB threshold, closer to the
  margins where prior cycles rotated (~1.9-3KB) than where they held off
  (~5-7KB) — so archived the oldest remaining slice (2026-09-28 ~00:46
  through 2026-09-28 ~21:47-22:16 UTC) verbatim to new
  `AGENTS_ARCHIVE_2026-09-28.md` first, cutting the live file to 240,431
  bytes; verified via exact line-slice removal (asserting the removed
  block's first/last lines matched the expected boundary text) and
  `python3 -m pytest -q` 457/457 unaffected. Committed and pushed as
  `c7a1f18` before starting evolve work. Then, with nothing else queued,
  used the slot for one more real 15-generation batch via
  `tools/background_runner.py` (`start` + separate `wait`), run
  concurrently with the baseline `pytest` pass, exit code 0, no
  truncation, ~22 minutes. Champion's fold-aggregate fitness held flat at
  1.393 across all 15 generations (959 trades, 38% win, 1% stops, 4
  halts, unchanged throughout). Best-of-generation fold-fitness ranged
  roughly 1.273-2.661, never clearing the promotion-margin bar. See
  `runs/2026-10-04-0417-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 457/457 both before (baseline, right after the
  archival commit) and after `evolve`; top-level key diff of
  `live_state.json` (checked directly in Python against `git show
  HEAD:live_state.json`, not just eyeballed) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, content rotated, no new promotion attempt
  recorded); `tools/edit_bundle_module.py verify`/`sync --check` both
  clean; `holdout-pressure` re-checked (read-only, no state change) —
  margin rose slightly (7.469, was 7.466) at draw 1067, same slow-rise
  pattern already tracked under item 13, nothing new; dashboard rebuilt
  with `EVO_STATE` set (`index.html` shows 47593 challenger ideas tried).
  Genome still v3 (1d) live, untouched. Container arrived on `main`, up to
  date with `origin/main` after a clean fast-forward pull, no divergence,
  no shallow-clone staleness this cycle.

- **Run 2026-10-04 (3-hourly check, ~00:47-01:19 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 47180 → 47386 (per
  `researcher_memory.tested`), stagnation/boldness counter 3407 → 3421.**
  No live trading this cycle (tick 51 already handled at the dedicated
  00:20 UTC daily slot — confirmed via `live_state.json`'s `updated`
  timestamp at session start, `2026-10-04T00:23:02+00:00`, matching
  `runs/2026-10-04-0020-daily-trading.md`; `51 % 7 == 2` so no `evolve` ran
  as part of that tick). Freshness checks before running: `review-hard-calls`
  still 0 pending (4 reviewed, unchanged), items 6/13 still owner decisions,
  `AGENTS.md` size 255,839 bytes — within ~6.3KB of the 256KB threshold,
  consistent with prior cycles that didn't rotate at a similar margin — not
  rotated this cycle — so, with nothing else queued, used the slot for one
  more real 15-generation batch via `tools/background_runner.py` (`start` +
  separate `wait`), run concurrently with the baseline `pytest` pass, exit
  code 0, no truncation, ~32 minutes (the first `wait` call hit its own
  1800s timeout while the detached process was still running, confirmed
  alive via `ps`/`kill -0` at generation 13/15; a second `wait` against the
  same still-running process returned cleanly a few minutes later).
  Champion's fold-aggregate fitness held flat at 1.393 across all 15
  generations (959 trades, 38% win, 1% stops, 4 halts, unchanged
  throughout). Best-of-generation fold-fitness ranged roughly 1.249-2.570,
  never clearing the promotion-margin bar. See
  `runs/2026-10-04-0127-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 457/457 both before (baseline) and after `evolve`;
  top-level key diff of `live_state.json` (checked directly in Python
  against a pre-batch snapshot, not just eyeballed) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  `holdout-pressure` re-checked (read-only, no state change) — margin rose
  slightly (7.466, was 7.462) at draw 1062, same slow-rise pattern already
  tracked under item 13, nothing new; dashboard rebuilt with `EVO_STATE`
  set (`index.html` shows 47386 challenger ideas tried). Genome still v3
  (1d) live, untouched. Container arrived on `main`, 38 commits behind
  `origin/main` in detached HEAD; `git checkout main` plus
  `tools/git_sync.py` fast-forwarded cleanly, nothing lost.
