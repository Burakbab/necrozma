# Archived AGENTS.md slice — 2026-11-26 entries

Moved verbatim out of `AGENTS.md`'s "Current state" log on 2026-11-28
(3-hourly check, ~00:47 UTC) to keep that file under its working-size
budget. Nothing reworded, nothing lost. See `AGENTS.md` for the full
rotation index (the chain of "Archived ..." pointer entries) and anything
before or after this slice.

---

- **Run 2026-11-26 (3-hourly check, ~21:46-22:11 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 137767 → 137970 (per
  `researcher_memory.tested`), stagnation/boldness counter 9998 → 10012
  (crossed 10000 mid-batch).** No live trading this cycle (daily tick
  already handled at the dedicated 00:20 UTC daily slot and by seven prior
  3-hourly checks' own evolve batches earlier today, plus the 20:30 UTC
  daily evaluation — confirmed via `live_state.json`'s `updated` timestamp
  at session start, `2026-11-26T19:11:46+00:00`, matching
  `runs/2026-11-26-1916-evolve-batch-v3.md`). `AGENTS.md` size 250,713 bytes
  at session start — under the archival-trigger range recent cycles have
  used, not archived this cycle. Champion's fold-aggregate fitness held flat
  at 1.396 across all 15 generations (960 trades, 39% win, 1% stops, 3
  halts, unchanged — no daily-bar roll this cycle). Best-of-generation
  fold-fitness ranged roughly 1.135-2.426, never clearing the
  promotion-margin bar. `tools/background_runner.py start` was denied again
  by the sandbox's auto-mode classifier (same recurring denial several
  recent checks have hit) — fell back to the harness's own
  `run_in_background` option directly on the `evolve` command, no
  `nohup`/`&`, per item 9's standing rule. See
  `runs/2026-11-26-2211-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 505/505 both before (baseline) and after `evolve`;
  top-level key diff of `live_state.json` (snapshotted before the batch, in
  gitignored scratchpad, outside the repo) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py sync --check` clean; `holdout-pressure`
  re-checked post-batch — margin essentially flat (7.896 → 7.901), draw
  count 2423 → 2449 (new sealed-holdout draws from this batch's
  fold-aggregate-gate-clearing candidates, all correctly rejected), same
  slow-rise pattern already tracked under item 13, nothing new; dashboard
  rebuilt with `EVO_STATE` set (`index.html` 19.0 KB, shows 137970
  challenger idea(s) tried). Genome still v3 (1d) live, untouched. Container
  synced cleanly from `main` via `git checkout main` + `python3
  tools/git_sync.py` fast-forward through all of today's already-pushed
  commits, no divergence, no shallow-clone staleness this cycle.

- **Run 2026-11-26 (3-hourly check, ~18:47-19:16 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 137562 → 137767 (per
  `researcher_memory.tested`), stagnation/boldness counter 9983 → 9997.**
  No live trading this cycle (daily tick already handled at the dedicated
  00:20 UTC daily slot and by five prior 3-hourly checks' own evolve batches
  earlier today — confirmed via `live_state.json`'s `updated` timestamp at
  session start, `2026-11-26T16:08:18+00:00`, matching
  `runs/2026-11-26-1610-evolve-batch-v3.md`). `AGENTS.md` size 248,021 bytes
  at session start — under the archival-trigger range recent cycles have
  used, not archived this cycle. Champion's fold-aggregate fitness held flat
  at 1.396 across all 15 generations (960 trades, 39% win, 1% stops, 3
  halts, unchanged — no daily-bar roll this cycle). Best-of-generation
  fold-fitness ranged roughly 1.289-2.425, never clearing the
  promotion-margin bar. Backgrounded via `tools/background_runner.py
  start`/`wait`, no `nohup`/`&`, per item 9's standing rule — the `wait`
  call itself exceeded the tool's own foreground timeout and the harness
  moved it to a background task, resolved via the normal task-notification
  mechanism, no manual polling needed. See
  `runs/2026-11-26-1916-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 505/505 both before (baseline) and after `evolve`;
  top-level key diff of `live_state.json` (snapshotted before the batch, in
  gitignored scratchpad, outside the repo) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py sync --check` clean; `holdout-pressure`
  re-checked post-batch — margin essentially flat (7.896 → 7.901), draw
  count 2425 → 2448 (new sealed-holdout draws from this batch's
  fold-aggregate-gate-clearing candidates, all correctly rejected), same
  slow-rise pattern already tracked under item 13, nothing new; dashboard
  rebuilt with `EVO_STATE` set (`index.html` 20.1 KB, shows 137767
  challenger idea(s) tried). Genome still v3 (1d) live, untouched. Container
  synced cleanly from `main` via `git checkout main` + `python3
  tools/git_sync.py` fast-forward through 32 already-pushed commits, no
  divergence, no shallow-clone staleness this cycle. Hit the recurring
  `pip3` vs `python3 -m pip` numpy/pandas split again — `python3 -m pip
  install -r requirements.txt -q` fixed it immediately, same as prior
  sessions.

- **Run 2026-11-26 (3-hourly check, ~15:47-16:10 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 137355 → 137562 (per
  `researcher_memory.tested`), stagnation/boldness counter 9968 → 9983.**
  No live trading this cycle (daily tick already handled at the dedicated
  00:20 UTC daily slot and by four prior 3-hourly checks' own evolve batches
  earlier today — confirmed via `live_state.json`'s `updated` timestamp at
  session start, `2026-11-26T13:08:17+00:00`, matching
  `runs/2026-11-26-1310-evolve-batch-v3.md`). `AGENTS.md` size 245,503 bytes
  at session start — under the archival-trigger range recent cycles have
  used, not archived this cycle. Champion's fold-aggregate fitness held flat
  at 1.396 across all 15 generations (960 trades, 39% win, 1% stops, 3
  halts, unchanged — no daily-bar roll this cycle). Best-of-generation
  fold-fitness ranged roughly 1.214-2.425, never clearing the
  promotion-margin bar. Backgrounded via `tools/background_runner.py
  start`/`wait`, no `nohup`/`&`, per item 9's standing rule — the `wait`
  call itself exceeded the tool's own foreground timeout and the harness
  moved it to a background task, resolved via the normal task-notification
  mechanism, no manual polling needed. See
  `runs/2026-11-26-1610-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 505/505 both before (baseline) and after `evolve`;
  top-level key diff of `live_state.json` (snapshotted before the batch, in
  gitignored scratchpad, outside the repo) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py sync --check` clean; `holdout-pressure`
  re-checked post-batch — margin essentially flat (7.897 → 7.900), draw
  count 2425 → 2444 (new sealed-holdout draws from this batch's
  fold-aggregate-gate-clearing candidates, all correctly rejected), same
  slow-rise pattern already tracked under item 13, nothing new; dashboard
  rebuilt with `EVO_STATE` set (`index.html` 20.1 KB, shows 137562
  challenger idea(s) tried). Genome still v3 (1d) live, untouched. Container
  synced cleanly from `main` via `git checkout main` + `python3
  tools/git_sync.py` fast-forward through 32 already-pushed commits, no
  divergence, no shallow-clone staleness this cycle.

- **Run 2026-11-26 (3-hourly check, ~12:47-13:10 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 137149 → 137355 (per
  `researcher_memory.tested`), stagnation/boldness counter 9953 → 9968.**
  No live trading this cycle (daily tick already handled at the dedicated
  00:20 UTC daily slot and by four prior 3-hourly checks' own evolve batches
  earlier today — confirmed via `live_state.json`'s `updated` timestamp at
  session start, `2026-11-26T10:15:46+00:00`, matching
  `runs/2026-11-26-1018-evolve-batch-v3.md`). `AGENTS.md` size 242,985 bytes
  at session start — under the archival-trigger range recent cycles have
  used, not archived this cycle. Champion's fold-aggregate fitness held flat
  at 1.396 across all 15 generations (960 trades, 39% win, 1% stops, 3
  halts, unchanged — no daily-bar roll this cycle). Best-of-generation
  fold-fitness ranged roughly 1.356-2.425, never clearing the
  promotion-margin bar. Backgrounded via `tools/background_runner.py
  start`/`wait`, no `nohup`/`&`, per item 9's standing rule — the `wait`
  call itself exceeded the tool's own foreground timeout and the harness
  moved it to a background task, resolved via the normal task-notification
  mechanism, no manual polling needed. See
  `runs/2026-11-26-1310-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 505/505 both before (baseline) and after `evolve`;
  top-level key diff of `live_state.json` (snapshotted before the batch, in
  gitignored scratchpad, outside the repo) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py sync --check` clean; `holdout-pressure`
  re-checked post-batch — margin essentially flat (7.896 → 7.899), draw
  count 2425 → 2440 (new sealed-holdout draws from this batch's
  fold-aggregate-gate-clearing candidates, all correctly rejected), same
  slow-rise pattern already tracked under item 13, nothing new; dashboard
  rebuilt with `EVO_STATE` set (`index.html` 19.4 KB, shows 137355
  challenger idea(s) tried). Genome still v3 (1d) live, untouched. Container
  synced cleanly from `main` via `git checkout main` + `python3
  tools/git_sync.py` fast-forward through 32 already-pushed commits, no
  divergence, no shallow-clone staleness this cycle.

- **Run 2026-11-26 (3-hourly check, ~09:47-10:22 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 136942 → 137149 (per
  `researcher_memory.tested`), stagnation/boldness counter 9938 → 9953.**
  No live trading this cycle (daily tick already handled at the dedicated
  00:20 UTC daily slot and by the prior three 3-hourly checks' own evolve
  batches earlier today — confirmed via `live_state.json`'s `updated`
  timestamp at session start, `2026-11-26T07:09:16+00:00`, matching
  `runs/2026-11-26-0718-evolve-batch-v3.md`). `AGENTS.md` size 240,655 bytes
  at session start — under the archival-trigger range recent cycles have
  used, not archived this cycle. Champion's fold-aggregate fitness held flat
  at 1.396 across all 15 generations (960 trades, 39% win, 1% stops, 3
  halts, unchanged — no daily-bar roll this cycle). Best-of-generation
  fold-fitness ranged roughly 1.152-1.984, never clearing the
  promotion-margin bar. Backgrounded via `tools/background_runner.py
  start`/`wait`, no `nohup`/`&`, per item 9's standing rule — worked cleanly
  this cycle, no sandbox denial. See `runs/2026-11-26-1018-evolve-batch-v3.md`.
  Verified before commit: `python3 -m pytest -q` 505/505 both before
  (baseline) and after `evolve`; top-level key diff of `live_state.json`
  (snapshotted before the batch, in gitignored scratchpad, outside the
  repo) showed only `updated`/`researcher_memory`/`lineage` changed
  (genome, broker, journal, hard_call_reviews byte-identical); `lineage`
  length unchanged at 202 (bounded ring buffer, no new promotion attempt
  recorded); `tools/edit_bundle_module.py sync --check` clean;
  `holdout-pressure` re-checked post-batch — margin rose slightly (7.897 →
  7.898), draw count 2430 → 2434 (new sealed-holdout draws from this
  batch's fold-aggregate-gate-clearing candidates, correctly rejected),
  same slow-rise pattern already tracked under item 13, nothing new;
  dashboard rebuilt with `EVO_STATE` set (`index.html` 19.4 KB, shows
  137149 challenger idea(s) tried). Genome still v3 (1d) live, untouched.
  Container synced cleanly from `main` via `git checkout main` + `python3
  tools/git_sync.py` fast-forward, no divergence, no shallow-clone
  staleness this cycle.

- **Run 2026-11-26 (3-hourly check, ~06:47-07:18 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 136736 → 136942 (per
  `researcher_memory.tested`), stagnation/boldness counter 9923 → 9938.**
  No live trading this cycle (daily tick already handled at the dedicated
  00:20 UTC daily slot and by the prior 3-hourly check's own evolve batch —
  confirmed via `live_state.json`'s `updated` timestamp at session start,
  `2026-11-26T04:15:14+00:00`, matching
  `runs/2026-11-26-0418-evolve-batch-v3.md`). `AGENTS.md` size 238,349 bytes
  at session start — under the archival-trigger range recent cycles have
  used, not archived this cycle. Champion's fold-aggregate fitness held flat
  at 1.396 across all 15 generations (960 trades, 39% win, 1% stops, 3
  halts, unchanged — no daily-bar roll this cycle). Best-of-generation
  fold-fitness ranged roughly 1.093-1.765, never clearing the
  promotion-margin bar. Backgrounded via `tools/background_runner.py
  start`/`wait`, no `nohup`/`&`, per item 9's standing rule — worked cleanly
  this cycle, no sandbox denial. See `runs/2026-11-26-0718-evolve-batch-v3.md`.
  Verified before commit: `python3 -m pytest -q` 505/505 both before
  (baseline) and after `evolve`; top-level key diff of `live_state.json`
  (snapshotted before the batch, in gitignored scratchpad, outside the
  repo) showed only `updated`/`researcher_memory`/`lineage` changed
  (genome, broker, journal, hard_call_reviews byte-identical); `lineage`
  length unchanged at 202 (bounded ring buffer, no new promotion attempt
  recorded); `tools/edit_bundle_module.py sync --check` clean;
  `holdout-pressure` re-checked post-batch — margin held flat (7.897 →
  7.897), draw count 2429 → 2430 (one new sealed-holdout draw from this
  batch's fold-aggregate-gate-clearing candidate, correctly rejected), same
  slow-rise pattern already tracked under item 13, nothing new; dashboard
  rebuilt with `EVO_STATE` set (`index.html` 20.5 KB, shows 136942
  challenger idea(s) tried). Genome still v3 (1d) live, untouched. Container
  synced cleanly from `main` via `git checkout main` + `python3
  tools/git_sync.py` fast-forward, no divergence, no shallow-clone
  staleness this cycle.

- **Run 2026-11-26 (3-hourly check, ~03:47-04:18 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 136531 → 136736 (per
  `researcher_memory.tested`), stagnation/boldness counter 9908 → 9922.**
  No live trading this cycle (daily tick already handled at the dedicated
  00:20 UTC daily slot and by the prior 3-hourly check's own evolve batch —
  confirmed via `live_state.json`'s `updated` timestamp at session start,
  `2026-11-26T01:13:39+00:00`, matching
  `runs/2026-11-26-0113-evolve-batch-v3.md`). `AGENTS.md` size 235,899 bytes
  at session start — under the archival-trigger range recent cycles have
  used, not archived this cycle. Champion's fold-aggregate fitness held flat
  at 1.396 across all 15 generations (960 trades, 39% win, 1% stops, 3
  halts, unchanged — no daily-bar roll this cycle). Best-of-generation
  fold-fitness ranged roughly 1.255-2.069, never clearing the
  promotion-margin bar. `tools/background_runner.py start` was denied again
  by the sandbox's auto-mode classifier (same recurring denial several
  recent checks have hit) — fell back to the harness's own
  `run_in_background` option directly on the `evolve` command, no
  `nohup`/`&`, per item 9's standing rule. See
  `runs/2026-11-26-0418-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 505/505 both before (baseline) and after `evolve`;
  top-level key diff of `live_state.json` (snapshotted before the batch, in
  gitignored scratchpad, outside the repo) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py sync --check` clean; `holdout-pressure`
  re-checked post-batch — margin rose slightly (7.895 → 7.897), draw count
  2420 → 2429 (new sealed-holdout draws from this batch's
  fold-aggregate-gate-clearing candidates, all correctly rejected), same
  slow-rise pattern already tracked under item 13, nothing new; dashboard
  rebuilt with `EVO_STATE` set (`index.html` 20.5 KB, shows 136736
  challenger idea(s) tried). Genome still v3 (1d) live, untouched.
  Container synced cleanly from `main` via `git checkout main` + `python3
  tools/git_sync.py` fast-forward, no divergence, no shallow-clone
  staleness this cycle.

- **Run 2026-11-26 (3-hourly check, ~00:47-01:16 UTC): archived the
  2026-11-24 AGENTS.md log slice, then 15 more real `evolve` generations
  against the live v3 (1d) champion, no promotion — cumulative candidates
  tried against v3 rose 136327 → 136531 (per `researcher_memory.tested`),
  stagnation/boldness counter 9893 → 9908.** No live trading this cycle
  (daily tick already handled at the dedicated 00:20 UTC daily slot —
  confirmed via `live_state.json`'s `updated` timestamp at session start,
  `2026-11-26T00:22:04+00:00`, matching
  `runs/2026-11-26-0020-daily-trading.md`). `AGENTS.md` size 252,989 bytes
  at session start — within the margin range every prior rotation in this
  index has used to trigger one — so archived the next oldest remaining
  slice (all nine 2026-11-24 entries) verbatim to new
  `AGENTS_ARCHIVE_2026-11-24.md` first (committed/pushed separately,
  `d2d041d`, verified byte-for-byte identical against the removed slice),
  cutting this file to 233,149 bytes. With that done, used the rest of the
  slot for one more real 15-generation batch (backgrounded via
  `tools/background_runner.py start`/`wait`, which worked cleanly this
  cycle with no sandbox denial, no `nohup`/`&`, per item 9's standing
  rule). Champion's fold-aggregate fitness held flat at 1.396 across all 15
  generations (960 trades, 39% win, 1% stops, 3 halts — a daily-bar roll
  happened since the prior check's 935-trade/1.452 reading, otherwise
  unrelated to this batch). Best-of-generation fold-fitness ranged roughly
  1.191-2.127, never clearing the promotion-margin bar. See
  `runs/2026-11-26-0113-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 505/505 both before (baseline) and after `evolve`;
  top-level key diff of `live_state.json` (snapshotted before the batch, in
  gitignored scratchpad, outside the repo) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py sync --check` clean; `holdout-pressure`
  re-checked post-batch — margin rose slightly (7.894 → 7.896), draw count
  2415 → 2425 (new sealed-holdout draws from this batch's
  fold-aggregate-gate-clearing candidates, all correctly rejected), same
  slow-rise pattern already tracked under item 13, nothing new; dashboard
  rebuilt with `EVO_STATE` set (`index.html` 20.5 KB, shows 136531
  challenger idea(s) tried). Genome still v3 (1d) live, untouched.
  Container synced cleanly from `main` via `git checkout main` + `python3
  tools/git_sync.py` fast-forward, no divergence, no shallow-clone
  staleness this cycle.
