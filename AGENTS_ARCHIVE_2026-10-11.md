# Archived: 2026-10-11 3-hourly-check / weekend-all-hands log entries

Moved verbatim out of `AGENTS.md`'s "Current state" section on 2026-10-15
(3-hourly check, ~03:46 UTC) to keep that file under its 256KB single-read
limit. Nothing reworded, nothing lost. See `AGENTS.md`'s "Where things live"
table and its own archival-index entries for how this fits into the full
chronological history.

---

- **Run 2026-10-11 (3-hourly check, ~21:48-22:19 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 60533 → 60741 (per
  `researcher_memory.tested`), stagnation/boldness counter 4374 → 4389.**
  No live trading this cycle (tick 58 already handled at the dedicated
  00:20 UTC daily slot, and the prior 3-hourly check's own evolve batch
  already ran at ~18:46-19:22 UTC — confirmed via `live_state.json`'s
  `updated` timestamp at session start, `2026-10-11T19:16:02+00:00`,
  matching `runs/2026-10-11-1922-evolve-batch-v3.md`). Freshness checks
  before running: `review-hard-calls` still 0 pending (5 reviewed,
  unchanged), items 6/13 still owner decisions, `AGENTS.md` size 245,269
  bytes — comfortably under the 256KB threshold, not rotated this cycle —
  so, with nothing else queued, used the slot for one more real
  15-generation batch via `tools/background_runner.py` (`start` + separate
  `wait`), run concurrently with the baseline `pytest` pass, exit code 0,
  no truncation, ~22 minutes (both `wait` calls returned cleanly within
  their own windows). Champion's fold-aggregate fitness held flat at 1.839
  across all 15 generations (995 trades, 40% win, 1% stops, 3 halts,
  unchanged throughout). Best-of-generation fold-fitness ranged roughly
  1.489-2.018, never clearing the promotion-margin bar (generation 10's
  best tied the champion exactly, not a strict improvement). See
  `runs/2026-10-11-2219-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 474/474 both before (baseline) and after `evolve`;
  top-level key diff of `live_state.json` (checked directly in Python
  against the pre-batch baseline copy, not just eyeballed) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  `holdout-pressure` re-checked (read-only, no state change) — margin/draw
  count unchanged (7.532, draw 1202 — this batch's candidates never
  cleared the fold-aggregate gate at a new draw beyond the one already on
  record), same slow-rise pattern already tracked under item 13, nothing
  new; dashboard rebuilt with `EVO_STATE` set (`index.html` shows 60741
  challenger ideas tried). Genome still v3 (1d) live, untouched. Container
  synced cleanly from `main` via `tools/git_sync.py` fast-forward (29
  files), no divergence, no shallow-clone staleness this cycle. Hit the
  recurring `pip3` vs `python3 -m pip` numpy/pandas split on this container
  (already tracked under items 9/12's history) — `python3 -m pip install -r
  requirements.txt -q` fixed it immediately.

- **Run 2026-10-11 (3-hourly check, ~18:46-19:22 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 60328 → 60533 (per
  `researcher_memory.tested`), stagnation/boldness counter 4360 → 4374.**
  No live trading this cycle (tick 58 already handled at the dedicated
  00:20 UTC daily slot, and the prior 3-hourly check's own evolve batch
  already ran at ~15:47-16:41 UTC — confirmed via `live_state.json`'s
  `updated` timestamp at session start, `2026-10-11T16:35:53+00:00`,
  matching `runs/2026-10-11-1641-evolve-batch-v3.md`). Freshness checks
  before running: `review-hard-calls` still 0 pending (5 reviewed,
  unchanged), items 6/13 still owner decisions, `AGENTS.md` size 242,559
  bytes — comfortably under the 256KB threshold, not rotated this cycle —
  so, with nothing else queued, used the slot for one more real
  15-generation batch via `tools/background_runner.py` (`start` + separate
  `wait`), run concurrently with the baseline `pytest` pass, exit code 0,
  no truncation, ~27 minutes (the `wait` call returned cleanly within its
  own window this time, no timeout hit). Champion's fold-aggregate fitness
  held flat at 1.839 across all 15 generations (995 trades, 40% win, 1%
  stops, 3 halts, unchanged throughout). Best-of-generation fold-fitness
  ranged roughly 1.559-2.084, never clearing the promotion-margin bar. See
  `runs/2026-10-11-1922-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 474/474 both before (baseline) and after `evolve`;
  top-level key diff of `live_state.json` (checked directly in Python
  against the pre-batch baseline copy, not just eyeballed) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  `holdout-pressure` re-checked (read-only, no state change) — margin/draw
  count unchanged (7.532, draw 1202 — this batch's candidates never
  cleared the fold-aggregate gate at a new draw beyond the one already on
  record), same slow-rise pattern already tracked under item 13, nothing
  new; dashboard rebuilt with `EVO_STATE` set (`index.html` shows 60533
  challenger ideas tried). Genome still v3 (1d) live, untouched. Container
  synced cleanly from `main` via `tools/git_sync.py` fast-forward (picked
  up a large batch of recent commits, including the day's weekend all-hands
  dual-trend-short writeup and several more evolve batches), no divergence,
  no shallow-clone staleness this cycle.

- **Run 2026-10-11 (3-hourly check, ~15:47-16:41 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 60120 → 60328 (per
  `researcher_memory.tested`), stagnation/boldness counter 4345 → 4359.**
  No live trading this cycle (tick 58 already handled at the dedicated
  00:20 UTC daily slot, and the prior 3-hourly check's own evolve batch
  already ran at ~12:47-13:23 UTC — confirmed via `live_state.json`'s
  `updated` timestamp at session start, `2026-10-11T13:36:07+00:00`,
  matching `runs/2026-10-11-1323-evolve-batch-v3.md`). Freshness checks
  before running: `review-hard-calls` still 0 pending (5 reviewed,
  unchanged), items 6/13 still owner decisions, `AGENTS.md` size 239,702
  bytes — comfortably under the 256KB threshold, not rotated this cycle —
  so, with nothing else queued, used the slot for one more real
  15-generation batch via `tools/background_runner.py` (`start` + separate
  `wait`), run concurrently with the baseline `pytest` pass, exit code 0,
  no truncation, ~51 minutes (several `wait` calls hit their own
  backgrounding timeout while the detached process kept running, confirmed
  alive via `ps`/log at generations 8-14/15 each time, never lost; a
  foreground `wait` with a 580s timeout finally returned cleanly once the
  process reached exit). Champion's fold-aggregate fitness held flat at
  1.839 across all 15 generations (995 trades, 40% win, 1% stops, 3 halts,
  unchanged throughout). Best-of-generation fold-fitness ranged roughly
  1.747-2.060, never clearing the promotion-margin bar. See
  `runs/2026-10-11-1641-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 474/474 both before (baseline) and after `evolve`;
  top-level key diff of `live_state.json` (checked directly in Python
  against the pre-batch baseline copy, not just eyeballed) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  `holdout-pressure` re-checked (read-only, no state change) — margin rose
  slightly (7.532, was 7.531) at draw 1202, same slow-rise pattern already
  tracked under item 13, nothing new; dashboard rebuilt with `EVO_STATE`
  set (`index.html` shows 60328 challenger ideas tried). Genome still v3
  (1d) live, untouched. Container synced cleanly from `main` via
  `tools/git_sync.py` fast-forward, no divergence, no shallow-clone
  staleness this cycle. Hit the recurring `pip3` vs `python3 -m pip`
  numpy/pandas split on this container (already tracked under items 9/12's
  history) — `python3 -m pip install -r requirements.txt -q` fixed it
  immediately.

- **Run 2026-10-11 (3-hourly check, ~12:47-13:23 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 59914 → 60120 (per
  `researcher_memory.tested`), stagnation/boldness counter 4330 → 4345.**
  No live trading this cycle (tick 58 already handled at the dedicated
  00:20 UTC daily slot, and both the same-day 09:00 UTC daily discussion
  and the prior 3-hourly check's own evolve batch already covered this
  stretch — confirmed via `live_state.json`'s `updated` timestamp at
  session start, `2026-10-11T10:20:15+00:00`, matching
  `runs/2026-10-11-1023-evolve-batch-v3.md`). Freshness checks before
  running: `review-hard-calls` still 0 pending (5 reviewed, unchanged),
  items 6/13 still owner decisions, `AGENTS.md` size 237,141 bytes —
  comfortably under the 256KB threshold, not rotated this cycle — so, with
  nothing else queued, used the slot for one more real 15-generation batch
  via `tools/background_runner.py` (`start` + separate `wait`), run
  concurrently with the baseline `pytest` pass, exit code 0, no truncation,
  ~17.6 minutes (the first `wait` call hit its own timeout while the
  detached process was still on generation 10/15; a second `wait` returned
  cleanly). Champion's fold-aggregate fitness held flat at 1.839 across all
  15 generations (995 trades, 40% win, 1% stops, 3 halts, unchanged
  throughout). Best-of-generation fold-fitness ranged roughly 1.451-2.269,
  never clearing the promotion-margin bar. See
  `runs/2026-10-11-1323-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 474/474 both before (baseline) and after `evolve`;
  top-level key diff of `live_state.json` (checked directly in Python
  against the pre-batch baseline copy, not just eyeballed) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  `holdout-pressure` re-checked (read-only, no state change) — margin rose
  slightly (7.532, was 7.531) at draw 1202, same slow-rise pattern already
  tracked under item 13, nothing new; dashboard rebuilt with `EVO_STATE`
  set (`index.html` shows 60120 challenger ideas tried). Genome still v3
  (1d) live, untouched. Container synced cleanly from `main` via
  `tools/git_sync.py` fast-forward, no divergence, no shallow-clone
  staleness this cycle.

- **Run 2026-10-11 (3-hourly check, ~09:46-10:23 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 59705 → 59914 (per
  `researcher_memory.tested`), stagnation/boldness counter 4314 → 4329.**
  No live trading this cycle (tick 58 already handled at the dedicated
  00:20 UTC daily slot, and both the same-day 09:00 UTC daily discussion
  and the prior 3-hourly check's own evolve batch already covered this
  stretch — confirmed via `live_state.json`'s `updated` timestamp at
  session start, `2026-10-11T07:08:00+00:00`, matching
  `runs/2026-10-11-0721-evolve-batch-v3.md`). Freshness checks before
  running: `review-hard-calls` still 0 pending (5 reviewed, unchanged),
  items 6/13 still owner decisions (confirmed unchanged by the same-day
  09:00 UTC daily discussion), `AGENTS.md` size 234,478 bytes —
  comfortably under the 256KB threshold, not rotated this cycle — so, with
  nothing else queued, used the slot for one more real 15-generation batch
  via `tools/background_runner.py` (`start` + separate `wait`), run
  concurrently with the baseline `pytest` pass, exit code 0, no truncation,
  ~31 minutes (the first `wait` call hit its own 600s timeout while the
  detached process was still on generation 14/15; a second `wait` returned
  cleanly ~140s later). Champion's fold-aggregate fitness held flat at
  1.839 across all 15 generations (995 trades, 40% win, 1% stops, 3 halts,
  unchanged throughout). Best-of-generation fold-fitness ranged roughly
  1.009-2.112, never clearing the promotion-margin bar. See
  `runs/2026-10-11-1023-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 474/474 both before (baseline) and after `evolve`;
  top-level key diff of `live_state.json` (checked directly in Python
  against the pre-batch baseline copy, not just eyeballed) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  `holdout-pressure` re-checked (read-only, no state change) — margin rose
  slightly (7.532, was 7.531) at draw 1201, same slow-rise pattern already
  tracked under item 13, nothing new; dashboard rebuilt with `EVO_STATE`
  set (`index.html` shows 59914 challenger ideas tried). Genome still v3
  (1d) live, untouched. Container arrived detached HEAD, 50 commits behind
  `origin/main`; `git checkout main` plus `tools/git_sync.py`
  fast-forwarded cleanly, nothing lost.

- **Run 2026-10-11 (3-hourly check, ~06:46-07:21 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 59500 → 59705 (per
  `researcher_memory.tested`), stagnation/boldness counter 4299 → 4314.**
  No live trading this cycle (tick 58 already handled at the dedicated
  00:20 UTC daily slot, and both the prior 3-hourly check's own evolve
  batch and this morning's weekend all-hands dual-trend-short measurement
  already covered this stretch — confirmed via `live_state.json`'s
  `updated` timestamp at session start, `2026-10-11T04:13:22+00:00`,
  matching `runs/2026-10-11-0427-evolve-batch-v3.md`). Freshness checks
  before running: `review-hard-calls` still 0 pending (5 reviewed,
  unchanged), items 6/13 still owner decisions, `AGENTS.md` size 231,929
  bytes — comfortably under the 256KB threshold, not rotated this cycle —
  so, with nothing else queued, used the slot for one more real
  15-generation batch via `tools/background_runner.py` (`start` + separate
  `wait`), run concurrently with the baseline `pytest` pass, exit code 0,
  no truncation, ~22 minutes. Champion's fold-aggregate fitness held flat
  at 1.839 across all 15 generations (995 trades, 40% win, 1% stops, 3
  halts, unchanged throughout). Best-of-generation fold-fitness ranged
  roughly 1.484-2.213, never clearing the promotion-margin bar. See
  `runs/2026-10-11-0721-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 474/474 both before (baseline) and after `evolve`;
  top-level key diff of `live_state.json` (checked directly in Python
  against a pre-batch baseline copy, not just eyeballed) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  `holdout-pressure` re-checked (read-only, no state change) — margin/draw
  count unchanged (7.531, draw 1200 — this batch's candidates never
  cleared the fold-aggregate gate at a new draw beyond the one already on
  record), same slow-rise pattern already tracked under item 13, nothing
  new; dashboard rebuilt with `EVO_STATE` set (`index.html` shows 59705
  challenger ideas tried). Genome still v3 (1d) live, untouched. Container
  synced cleanly from `main` via `tools/git_sync.py` fast-forward, no
  divergence, no shallow-clone staleness this cycle.

- **Archived 2026-10-11 (weekend all-hands, ~07:40 UTC): the next oldest
  slice of this log (all eight 2026-10-07 entries) moved verbatim to new
  `AGENTS_ARCHIVE_2026-10-07.md`, cutting this file from 252,467 bytes back
  down** (within ~3.5KB of the 256KB threshold, the margin this session's
  own item-5 writeup just used up). Nothing reworded, nothing lost — see
  that file (and, for anything older, the rest of this index below) for the
  full history. This file now keeps everything from 2026-10-08 ~00:20 UTC
  onward, plus the full "Owner decisions pending", promotion-history,
  "Measured", and "Rules" sections, never part of any rotation. No code
  changed, no protected file touched, `live_state.json` untouched by this
  housekeeping step itself.

- **Run 2026-10-11 (weekend all-hands, ~06:00-07:40 UTC): built and measured a
  genuinely new short-timing confirmation signal for item 5 (short selling)
  — `loop.engine.benchmark_dual_trend_short`, a per-symbol TIMEFRAME-agreement
  filter layered onto `benchmark_trend_break_short`'s existing entry, instead
  of yet another way of wiring the basket-wide regime classifier that every
  prior combination (2026-09-27 regime-conditional, 2026-10-03 combined,
  2026-10-04 asymmetric) had already found to be the weak link.** Full
  writeup is in item 5's "Next steps" entry below (new 2026-10-11 bullet) —
  short version: at the shipped default (`slope_lookback=20`) the first
  real-data result was a wash, but a direct parameter sweep against the live
  champion's real four windows found a real, non-monotonic sweet spot at
  `slope_lookback` 40-50 where fold 1/fold 2's bull-market losses shrink by
  20-25 points while the one real bear window's capture barely moves
  (82-86% vs plain trend-break's 101%) — the best frontier point this item
  has found across its whole combination history, though still net-losing
  in 3 of 4 windows and explicitly not adopted as a new default (picking a
  value off the same table it's scored against would be exactly the
  in-sample mining this repo's fold/holdout discipline exists to prevent).
  9 new tests (`tests/test_dual_trend_short.py`, full suite 465 → 474, all
  passing both before and after against the real repo). New CLI flag
  `short-headroom --dual-trend`, wired and verified against real 4-year
  Binance data (`short-headroom --dual-trend --trend-break` run directly).
  `tools/edit_bundle_module.py sync`/`verify` both clean throughout — the
  real `loop/engine.py` function was written first, synced into
  `evotrader_bundle.py`'s `_SRC['loop.engine']`, then the CLI dispatch
  block (plain top-level script code, not part of `_SRC`) was hand-edited
  to add the new flag and report table, same pattern every prior
  trend-break/combined/asymmetric flag addition used. Read-only throughout:
  no genome, `RiskJudge`/`SuperiorJudge`, or `live_state.json` touch — a
  measurement to inform a future design, never itself that design. Does not
  touch live trading, the champion, or the still-open owner-gated question
  of whether/how the Researcher should ever be allowed to open a short. See
  `runs/2026-10-11-0600-weekend-all-hands.md` for the session writeup.

- **Run 2026-10-11 (3-hourly check, ~03:46-04:27 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 59292 → 59500 (per
  `researcher_memory.tested`), stagnation/boldness counter 4285 → 4299.**
  No live trading this cycle (tick 58 already handled at the dedicated
  00:20 UTC daily slot, and the prior 3-hourly check's own evolve batch
  already ran at ~00:47-01:22 UTC — confirmed via `live_state.json`'s
  `updated` timestamp at session start, `2026-10-11T01:11:25+00:00`,
  matching `runs/2026-10-11-0122-evolve-batch-v3.md`). Freshness checks
  before running: `review-hard-calls` still 0 pending (5 reviewed,
  unchanged), items 6/13 still owner decisions, `AGENTS.md` size 242,556
  bytes — comfortably under the 256KB threshold, not rotated this cycle —
  so, with nothing else queued, used the slot for one more real
  15-generation batch via `tools/background_runner.py` (`start` + separate
  `wait`), run concurrently with the baseline `pytest` pass, exit code 0,
  no truncation, ~41 minutes (the `wait` call exceeded the tool's own
  foreground timeout mid-run and was moved to background automatically;
  confirmed the real process, PID 879, alive via `ps` at ~10 minutes
  elapsed, then received a completion notification when it finished —
  process never lost). Champion's fold-aggregate fitness held flat at
  1.839 across all 15 generations (995 trades, 40% win, 1% stops, 3 halts,
  unchanged throughout). Best-of-generation fold-fitness ranged roughly
  1.686-2.213, never clearing the promotion-margin bar. See
  `runs/2026-10-11-0427-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 465/465 both before (baseline) and after `evolve`;
  top-level key diff of `live_state.json` (checked directly in Python
  against a pre-batch baseline copy, not just eyeballed) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  `holdout-pressure` re-checked (read-only, no state change) — margin/draw
  count unchanged (7.531, draw 1200 — this batch's candidates never
  cleared the fold-aggregate gate at a new draw beyond the one already on
  record), same slow-rise pattern already tracked under item 13, nothing
  new; dashboard rebuilt with `EVO_STATE` set (`index.html` shows 59500
  challenger ideas tried). Genome still v3 (1d) live, untouched. Container
  synced cleanly from `main` via `tools/git_sync.py` fast-forward, no
  divergence, no shallow-clone staleness this cycle.

- **Run 2026-10-11 (3-hourly check, ~00:47-01:22 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 59086 → 59292 (per
  `researcher_memory.tested`), stagnation/boldness counter 4270 → 4285.**
  No live trading this cycle (tick 58 already handled at the dedicated
  00:20 UTC daily slot — confirmed via `live_state.json`'s `updated`
  timestamp at session start, `2026-10-11T00:22:05+00:00`, matching
  `runs/2026-10-11-0020-daily-trading.md`; `58 % 7 == 2` so no `evolve` ran
  as part of that tick). Freshness checks before running: `review-hard-calls`
  still 0 pending (5 reviewed, unchanged), items 6/13 still owner decisions,
  `AGENTS.md` size 239,938 bytes — comfortably under the 256KB threshold,
  not rotated this cycle — so, with nothing else queued, used the slot for
  one more real 15-generation batch via `tools/background_runner.py`
  (`start` + separate `wait`), run concurrently with the baseline `pytest`
  pass, exit code 0, no truncation, ~35 minutes (the `wait` call exceeded
  the tool's own foreground timeout mid-run and was moved to background
  automatically; confirmed the real process alive via `ps` at generation
  8/15 in the meantime, then received a completion notification when it
  finished — process never lost). Champion's fold-aggregate fitness held
  flat at 1.839 across all 15 generations (995 trades, 40% win, 1% stops, 3
  halts, unchanged throughout). Best-of-generation fold-fitness ranged
  roughly 1.418-2.209, never clearing the promotion-margin bar. See
  `runs/2026-10-11-0122-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 465/465 both before (baseline) and after `evolve`;
  top-level key diff of `live_state.json` (checked directly in Python
  against a pre-batch baseline copy, not just eyeballed) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  `holdout-pressure` re-checked (read-only, no state change) — margin rose
  slightly (7.531, draw 1200), same slow-rise pattern already tracked under
  item 13, nothing new; dashboard rebuilt with `EVO_STATE` set
  (`index.html` shows 59292 challenger ideas tried). Genome still v3 (1d)
  live, untouched. Container synced cleanly from `main` via
  `tools/git_sync.py` fast-forward (50 commits), no divergence, no
  shallow-clone staleness this cycle.

