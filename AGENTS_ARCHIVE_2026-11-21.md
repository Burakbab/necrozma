- **Run 2026-11-21 (3-hourly check, ~21:46-22:17 UTC): archived the
  2026-11-20 AGENTS.md log slice, then 15 more real `evolve` generations
  against the live v3 (1d) champion, no promotion — cumulative candidates
  tried against v3 rose 129557 → 129765 (per `researcher_memory.tested`),
  stagnation/boldness counter 9398 → 9413.** No live trading this cycle
  (tick 99 already handled at the dedicated 00:20 UTC daily slot and by
  several prior 3-hourly checks' own evolve batches today — confirmed via
  `live_state.json`'s `updated` timestamp at session start,
  `2026-11-21T19:07:36+00:00`, matching `runs/2026-11-21-1909-evolve-batch-v3.md`).
  Freshness checks: `review-hard-calls` still 0 pending (6 reviewed,
  unchanged), items 6/13 still owner decisions, `AGENTS.md` size 254,181
  bytes at session start — within the margin range every prior rotation in
  this index has used to trigger one — so archived the next oldest
  remaining slice (all nine 2026-11-20 entries: eight 3-hourly checks plus
  that day's own daily-trading entry) verbatim to new
  `AGENTS_ARCHIVE_2026-11-20.md` first (committed/pushed separately,
  `516066b`, verified byte-for-byte identical against the removed slice),
  cutting this file to 231,659 bytes. With that done, used the rest of the
  slot for one more real 15-generation batch (backgrounded via
  `tools/background_runner.py start`/`wait`, no `nohup`/`&`, output
  captured to a log file from the first byte), run after a baseline
  `pytest` pass, exit code 0, no truncation. Champion's fold-aggregate
  fitness held flat at 1.542 across all 15 generations (921 trades, 37%
  win, 1% stops, 4 halts, unchanged throughout — no daily-bar roll this
  cycle). Best-of-generation fold-fitness ranged roughly 1.542-2.900, never
  clearing the promotion-margin bar. See
  `runs/2026-11-21-2217-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 505/505 both before (baseline) and after `evolve`;
  top-level key diff of `live_state.json` (snapshotted before the batch,
  checked directly in Python against the pre-batch copy) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer — no new promotion attempt recorded);
  `tools/edit_bundle_module.py sync --check` clean; `holdout-pressure`
  re-checked post-batch — margin rose slightly (7.873 → 7.874), draw count
  2319 → 2321 (two new sealed-holdout draws from this batch's
  fold-aggregate-gate-clearing candidates, both correctly rejected), same
  slow-rise pattern already tracked under item 13, nothing new; dashboard
  rebuilt with `EVO_STATE` set (`index.html` shows 129765 challenger
  idea(s) tried). Genome still v3 (1d) live, untouched. Container synced
  cleanly from `main` via `git checkout main` + `python3 tools/git_sync.py`
  fast-forward through 45 other sessions' already-pushed commits from
  earlier today, no divergence, no shallow-clone staleness this cycle. Hit
  the recurring `pip3` vs `python3 -m pip` numpy/pandas split again —
  `python3 -m pip install -r requirements.txt -q` fixed it immediately,
  same as prior sessions.

- **Run 2026-11-21 (3-hourly check, ~18:46-19:09 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 129351 → 129557 (per
  `researcher_memory.tested`), stagnation/boldness counter 9383 → 9397.**
  No live trading this cycle (tick 99 already handled at the dedicated
  00:20 UTC daily slot and by several prior 3-hourly checks' own evolve
  batches today — confirmed via `live_state.json`'s `updated` timestamp at
  session start, `2026-11-21T16:12:17+00:00`, matching
  `runs/2026-11-21-1620-evolve-batch-v3.md`). Freshness checks:
  `review-hard-calls` still 0 pending (6 reviewed, unchanged), items 6/13
  still owner decisions, `AGENTS.md` size 251,534 bytes at session start —
  under the ~252-254KB range that has recently triggered archival, not
  archived this cycle — so, with nothing else queued, used the slot for one
  more real 15-generation batch (backgrounded via
  `tools/background_runner.py start`/`wait`, no `nohup`/`&`, output
  captured to a log file from the first byte), run after a baseline
  `pytest` pass, exit code 0, no truncation. Champion's fold-aggregate
  fitness held flat at 1.542 across all 15 generations (921 trades, 37%
  win, 1% stops, 4 halts, unchanged throughout — no daily-bar roll this
  cycle). Best-of-generation fold-fitness ranged roughly 1.332-1.776, never
  clearing the promotion-margin bar. See
  `runs/2026-11-21-1909-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 505/505 both before (baseline) and after `evolve`;
  top-level key diff of `live_state.json` (snapshotted before the batch,
  checked directly in Python against the pre-batch copy) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer — no new promotion attempt recorded);
  `tools/edit_bundle_module.py sync --check` clean; `holdout-pressure`
  re-checked post-batch — margin held flat (7.873), draw count 2318 → 2319
  (one new sealed-holdout draw from this batch's fold-aggregate-gate-
  clearing candidates, correctly rejected), same slow-rise pattern already
  tracked under item 13, nothing new; dashboard rebuilt with `EVO_STATE`
  set (`index.html` shows 129557 challenger idea(s) tried). Genome still v3
  (1d) live, untouched. Container synced cleanly from `main` via `git
  checkout main` + `python3 tools/git_sync.py` fast-forward through 44
  other sessions' already-pushed commits from earlier today, no
  divergence, no shallow-clone staleness this cycle.

- **Run 2026-11-21 (3-hourly check, ~16:12-16:20 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 129144 → 129351 (per
  `researcher_memory.tested`), stagnation/boldness counter 9367 → 9383.**
  No live trading this cycle (tick 99 already handled at the dedicated
  00:20 UTC daily slot and by several prior 3-hourly checks' own evolve
  batches today — confirmed via `live_state.json`'s `updated` timestamp at
  session start, `2026-11-21T13:17:33+00:00`, matching
  `runs/2026-11-21-1320-evolve-batch-v3.md`). Freshness checks:
  `review-hard-calls` still 0 pending (6 reviewed, unchanged), items 6/13
  still owner decisions, `AGENTS.md` size 248,876 bytes at session start —
  under the ~252KB+ range that has triggered archival in recent cycles, not
  archived this cycle — so, with nothing else queued, used the slot for one
  more real 15-generation batch (backgrounded via
  `tools/background_runner.py start`/`wait`, no `nohup`/`&`, output
  captured to a log file from the first byte), run after a baseline
  `pytest` pass, exit code 0, no truncation. Champion's fold-aggregate
  fitness held flat at 1.542 across all 15 generations (921 trades, 37%
  win, 1% stops, 4 halts, unchanged throughout — no daily-bar roll this
  cycle). Best-of-generation fold-fitness ranged roughly 1.059-2.900, never
  clearing the promotion-margin bar. See
  `runs/2026-11-21-1620-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 505/505 both before (baseline) and after `evolve`;
  top-level key diff of `live_state.json` (snapshotted before the batch,
  checked directly in Python against the pre-batch copy) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer — no new promotion attempt recorded);
  `tools/edit_bundle_module.py sync --check` clean; `holdout-pressure`
  re-checked post-batch — margin unchanged (7.873), draw count 2316 → 2318
  (two new sealed-holdout draws from this batch's fold-aggregate-gate-
  clearing candidates, both correctly rejected), same slow-rise pattern
  already tracked under item 13, nothing new; dashboard rebuilt with
  `EVO_STATE` set (`index.html` shows 129351 challenger idea(s) tried).
  Genome still v3 (1d) live, untouched. Container synced cleanly from
  `main` via `git checkout main` + `python3 tools/git_sync.py` fast-forward
  through 43 other sessions' already-pushed commits from earlier today, no
  divergence, no shallow-clone staleness this cycle.

- **Run 2026-11-21 (3-hourly check, ~12:48-13:20 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 128941 → 129144 (per
  `researcher_memory.tested`), stagnation/boldness counter 9353 → 9367.**
  No live trading this cycle (tick 99 already handled at the dedicated
  00:20 UTC daily slot and by the prior 3-hourly check's own evolve batch —
  confirmed via `live_state.json`'s `updated` timestamp at session start,
  `2026-11-21T10:16:12+00:00`, matching `runs/2026-11-21-0946-self-improvement.md`).
  Freshness checks: `review-hard-calls` still 0 pending (6 reviewed,
  unchanged), items 6/13 still owner decisions, `AGENTS.md` size 246,016
  bytes at session start — ~10KB under the 256KB threshold, not archived
  this cycle — so, with nothing else queued, used the slot for one more
  real 15-generation batch (backgrounded via `tools/background_runner.py
  start`/`wait`, no `nohup`/`&`, output captured to a log file from the
  first byte), run after a baseline `pytest` pass, exit code 0, no
  truncation. Champion's fold-aggregate fitness held flat at 1.542 across
  all 15 generations (921 trades, 37% win, 1% stops, 4 halts, unchanged
  throughout — no daily-bar roll this cycle). Best-of-generation
  fold-fitness ranged roughly 1.217-2.117, never clearing the
  promotion-margin bar. See `runs/2026-11-21-1320-evolve-batch-v3.md`.
  Verified before commit: `python3 -m pytest -q` 505/505 both before
  (baseline) and after `evolve`; top-level key diff of `live_state.json`
  (snapshotted before the batch, checked directly in Python against the
  pre-batch copy) showed only `updated`/`researcher_memory`/`lineage`
  changed (genome, broker, journal, hard_call_reviews byte-identical);
  `lineage` length unchanged at 202 (bounded ring buffer — content rotated
  with this batch's own new per-generation record, no new promotion
  attempt recorded); `tools/edit_bundle_module.py sync --check` clean;
  `holdout-pressure` re-checked post-batch — margin rose slightly (7.872 →
  7.873), draw count 2314 → 2316 (two new sealed-holdout draws from this
  batch's fold-aggregate-gate-clearing candidates, both correctly rejected),
  same slow-rise pattern already tracked under item 13, nothing new;
  dashboard rebuilt with `EVO_STATE` set (`index.html` shows 129144
  challenger idea(s) tried). Genome still v3 (1d) live, untouched. Container
  synced cleanly from `main` via `git checkout main` + `python3
  tools/git_sync.py` fast-forward through 42 other sessions' already-pushed
  commits from earlier today, no divergence, no shallow-clone staleness
  this cycle. Hit the recurring `pip3` vs `python3 -m pip` numpy/pandas
  split again — `python3 -m pip install -r requirements.txt -q` fixed it
  immediately, same as prior sessions.

- **Run 2026-11-21 (3-hourly check, ~09:46-10:20 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 128735 → 128941 (per
  `researcher_memory.tested`), stagnation/boldness counter 9338 → 9352.**
  No live trading this cycle (tick 99 already handled at the dedicated
  00:20 UTC daily slot and by the prior 3-hourly check's own evolve batch —
  confirmed via `live_state.json`'s `updated` timestamp at session start,
  `2026-11-21T07:35:40+00:00`, matching `runs/2026-11-21-0738-evolve-batch-v3.md`).
  Freshness checks: `review-hard-calls` still 0 pending (6 reviewed,
  unchanged), items 6/13 still owner decisions, `AGENTS.md` size 243,222
  bytes at session start — ~13KB under the 256KB threshold, not archived
  this cycle — so, with nothing else queued, used the slot for one more
  real 15-generation batch (backgrounded via `tools/background_runner.py
  start`/`wait`, no `nohup`/`&`, output captured to a log file from the
  first byte). A flaky, order-dependent `pytest -q` failure
  (`tests/test_fold_scheme_reconstruction.py::test_version_1_is_the_seed_and_needs_no_lineage`)
  showed up on the very first full-suite run this cycle but passed in
  isolation and on an immediate rerun (505/505) and did not recur on any
  later run — read as test-ordering/timing flakiness, not a real
  regression, and not investigated further. Champion's fold-aggregate
  fitness held flat at 1.542 across all 15 generations (921 trades, 37%
  win, 1% stops, 4 halts, unchanged throughout — no daily-bar roll this
  cycle). Best-of-generation fold-fitness ranged roughly 0.622-2.200, never
  clearing the promotion-margin bar. See
  `runs/2026-11-21-0946-self-improvement.md`. Verified before commit:
  `python3 -m pytest -q` 505/505 both before (baseline, after the flake
  was dismissed) and after `evolve`; top-level key diff of `live_state.json`
  (snapshotted before the batch) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py sync --check` clean; `holdout-pressure`
  re-checked post-batch — margin rose slightly (7.869 → 7.872), draw count
  2300 → 2314 (new sealed-holdout draws from this batch's
  fold-aggregate-gate-clearing candidates, all correctly rejected), same
  slow-rise pattern already tracked under item 13, nothing new; dashboard
  rebuilt with `EVO_STATE` set (`index.html` shows 128941 challenger
  idea(s) tried). Genome still v3 (1d) live, untouched. No git-push
  collision this cycle — fetched `origin/main` immediately before this
  commit, no divergence.

- **Run 2026-11-21 (weekend all-hands, ~06:00-07:00 UTC): `live-benchmark`
  re-checked for the first time in 10+ weeks and flipped sign — live
  account now beats buy-and-hold by +28.20% excess over its real trading
  life, not behind it — then 20 more real `evolve` generations against v3,
  no promotion.** Main finding: the last session to run `live-benchmark`
  was the 2026-09-12 weekend all-hands (28 bars, -13.21% excess); nothing
  re-ran it since. Fresh result this session: 98 real 1d bars
  (2026-08-14 to 2026-11-20), live account +26.03% (sharpe 2.03, maxDD
  -21.6%) vs. equal-weight buy-and-hold of the same 27-symbol universe
  -2.17% (maxDD -41.6%) — **excess +28.20%**, a +41.4-point swing from the
  last check. Checked, not just quoted, the tool's own "traded under
  multiple genome versions" caveat: `Counter` of the real journal's
  `genome_version` field is `{3: 97, 1: 1, 2: 1}` — only the account's
  first two ticks predate the v2→v3 promotion, so 98% of this track record
  is a clean single-genome (v3) real forward test. Checked what's driving
  it: today's own `signals` reads "Market read: bear, breadth 0%" and the
  benchmark window's buy-and-hold is itself negative (-2.17%) — this is not
  beta captured from a rising market, it's real alpha generated across a
  choppy-to-bearish 10-week stretch, the first live window where the
  account didn't just lose less than the benchmark but made money while
  the benchmark lost money. Does not overturn the 2026-08-16 "Measured"
  section's full-4-year-backtest finding (-28.4% excess over the complete
  replay history) — different window, different kind of evidence (replay
  vs. real fills) — both are true simultaneously; this is item 1's
  "accumulate live forward-test data" premise finally producing its first
  genuinely good-looking stretch. Checked against item 0's three revisit
  triggers below: none fire (trigger 1 is specifically about *persistent
  negative* excess, which this isn't anymore), so item 0's 2026-08-30
  recommendation stands un-revisited by design — this is new evidence, not
  a decision point. Flagged, not fixed: `live-benchmark` isn't part of any
  session's standard verification checklist, which is why a 10-week gap
  went unnoticed; recommended (not mandated) that weekend sessions run it
  as routine going forward. See `runs/2026-11-21-0600-weekend-all-hands.md`
  for the full writeup.

  Second half of the session: one real 20-generation `evolve` batch
  (backgrounded via `tools/background_runner.py start`/`wait`, no
  `nohup`/`&`), run after a baseline `pytest` pass, exit code 0, no
  truncation, deliberately moderate-sized to avoid the git-push collision
  the 2026-11-15 weekend session hit with an oversized 50-generation batch.
  Champion's fold-aggregate fitness held flat at 1.542 across all 20
  generations (921 trades, 37% win, 1% stops, 4 halts, unchanged
  throughout). Best-of-generation fold-fitness ranged roughly 1.253-2.649,
  never clearing the promotion-margin bar. Cumulative candidates tried
  against v3 rose **128255 → 128531**; stagnation/boldness counter
  **9303 → 9322**. Verified before commit: `python3 -m pytest -q` 505/505
  both before and after; top-level key diff of `live_state.json` showed
  only `updated`/`researcher_memory`/`lineage` changed (genome, broker,
  journal, hard_call_reviews byte-identical; `lineage` length unchanged at
  202, no new promotion attempt); `tools/edit_bundle_module.py sync
  --check` clean; `holdout-pressure` re-checked post-batch — margin rose
  slightly (7.871 → 7.872), draw count 2307 → 2311 (four new sealed-holdout
  draws, all correctly rejected), same slow-rise pattern tracked under item
  13; dashboard rebuilt with `EVO_STATE` set (`index.html` shows 128531
  challenger idea(s) tried). Genome still v3 (1d) live, untouched. No
  constitution change, no promotion, no README.md update needed. Container
  synced cleanly from `main` via `git checkout main` + `python3
  tools/git_sync.py` fast-forward through 38 other sessions' already-pushed
  commits, no divergence, no shallow-clone staleness this cycle; `git
  fetch origin main` re-checked immediately before this commit per the
  2026-11-15 collision lesson.

- **Run 2026-11-21 (3-hourly check, ~06:46-07:38 UTC): hit a git-push
  collision with the weekend-all-hands session above, resolved by resetting
  to the fresher remote state rather than hand-merging `live_state.json`,
  then 15 more real `evolve` generations against the live v3 (1d) champion
  — cumulative candidates tried against v3 rose 128531 → 128735 (per
  `researcher_memory.tested`), stagnation/boldness counter 9323 → 9337.**
  No live trading this cycle (tick 99 already handled earlier today).
  Freshness checks before starting: `review-hard-calls` 0 pending (6
  reviewed), `AGENTS.md` 235,281 bytes at session start, not archived. Ran
  and committed a first 15-generation evolve batch (same verification
  discipline as every prior cycle), but the push was rejected — the
  weekend-all-hands session above had pushed its own 20-generation batch +
  `live-benchmark` re-check in the interim, touching the same
  `live_state.json`/`index.html`/`AGENTS.md` paths. `git rebase origin/main`
  produced unmergeable conflicts inside `live_state.json` itself (not the
  shallow-clone staleness `tools/git_sync.py` is built for — two sessions'
  real, divergent JSON mutations to the same ~7MB state file). Rather than
  hand-merge a file whose `researcher_memory.tested` alone holds 128k+
  entries (real risk of silently corrupting the 2026-08-15 dedup-memory
  fix), confirmed the working tree was clean, aborted the rebase, and
  `git reset --hard origin/main` — discarding my own unpushed commit, whose
  only unique content (another "no promotion" evolve batch) was already
  superseded in substance by the colliding session's own. Redid the work
  fresh against the post-collision state instead: 15 more generations,
  fitness held flat at 1.542 (921 trades, 37% win, 1% stops, 4 halts)
  throughout, best-of-generation 1.374-1.844, no promotion. Verified before
  this commit: `python3 -m pytest -q` 505/505 (both before this batch and
  again after, since the reset also re-confirms the colliding commit
  changed no code, only state/notes); top-level key diff of `live_state.json`
  showed only `updated`/`researcher_memory`/`lineage` changed (lineage
  length unchanged at 202, no new promotion attempt); `tools/edit_bundle_module.py
  sync --check` clean; `holdout-pressure` re-checked post-batch — margin
  7.872, draw count 2313; dashboard rebuilt with `EVO_STATE` set (`index.html`
  shows 128735 challenger idea(s) tried). Genome still v3 (1d) live,
  untouched. See `runs/2026-11-21-0738-evolve-batch-v3.md` for the full
  collision writeup and the takeaway for future sessions: when a rebase
  shows conflicts *inside* `live_state.json` itself, don't hand-merge it —
  confirm the tree is clean, abort, hard-reset to `origin/main`, and redo
  any lost work against the fresh state.

- **Run 2026-11-21 (3-hourly check, ~03:46-04:09 UTC): archived the oldest
  remaining `AGENTS.md` log slice, then 15 more real `evolve` generations
  against the live v3 (1d) champion, no promotion — cumulative candidates
  tried against v3 rose 128050 → 128255 (per `researcher_memory.tested`),
  stagnation/boldness counter 9288 → 9303.** No live trading this cycle
  (tick 99 already handled at the dedicated 00:20 UTC daily slot and by the
  prior 3-hourly check's own evolve batch — confirmed via `live_state.json`'s
  `updated` timestamp at session start, `2026-11-21T01:14:56+00:00`,
  matching `runs/2026-11-21-0118-evolve-batch-v3.md`). `AGENTS.md` size
  253,412 bytes at session start — within the margin range every prior
  rotation in this index has used to trigger one — so archived the next
  oldest remaining slice (all eight 2026-11-19 3-hourly-check entries)
  verbatim to new `AGENTS_ARCHIVE_2026-11-19.md` first (committed/pushed
  separately, `a77e742`, verified byte-for-byte identical against the
  removed slice), cutting this file to 231,396 bytes. With that done, used
  the rest of the slot for one more real 15-generation batch (backgrounded
  via `tools/background_runner.py start`/`wait`, no `nohup`/`&`, output
  captured to a log file from the first byte), run after a baseline
  `pytest` pass, exit code 0, no truncation. Champion's fold-aggregate
  fitness held flat at 1.542 across all 15 generations (921 trades, 37%
  win, 1% stops, 4 halts, unchanged throughout — no daily-bar roll this
  cycle). Best-of-generation fold-fitness ranged roughly 1.447-2.687, never
  clearing the promotion-margin bar. See
  `runs/2026-11-21-0409-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 505/505 both before (baseline) and after `evolve`;
  top-level key diff of `live_state.json` (snapshotted before the batch,
  checked directly in Python against the pre-batch copy) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py sync --check` clean; `holdout-pressure`
  re-checked post-batch — margin rose slightly (7.870 → 7.871), draw count
  2305 → 2307 (two new sealed-holdout draws from this batch's
  fold-aggregate-gate-clearing candidates, both correctly rejected), same
  slow-rise pattern already tracked under item 13, nothing new; dashboard
  rebuilt with `EVO_STATE` set (`index.html` shows 128255 challenger
  idea(s) tried). Genome still v3 (1d) live, untouched. Container synced
  cleanly from `main` via `git checkout main` + `python3 tools/git_sync.py`
  fast-forward through 36 other sessions' already-pushed commits from
  earlier today, no divergence, no shallow-clone staleness this cycle.

- **Run 2026-11-21 (3-hourly check, ~00:47-01:18 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 127842 → 128050 (per
  `researcher_memory.tested`), stagnation/boldness counter 9272 → 9287.**
  No live trading this cycle (tick 99 already handled at the dedicated
  00:20 UTC daily slot ~27 minutes before this session started — confirmed
  via `live_state.json`'s `updated` timestamp at session start,
  `2026-11-21T00:21:43+00:00`, matching `runs/2026-11-21-0020-daily-trading.md`;
  `99 % 7 == 1`, not a dedicated evolve slot either). Freshness checks:
  `review-hard-calls` still 0 pending (6 reviewed, unchanged), items 6/13
  still owner decisions, `AGENTS.md` size 250,639 bytes at session start —
  under the 256KB threshold, not archived this cycle — so, with nothing
  else queued, used the slot for one more real 15-generation batch
  (backgrounded via `tools/background_runner.py start`/`wait`, no
  `nohup`/`&`, output captured to a log file from the first byte), run
  after a baseline `pytest` pass, exit code 0, no truncation. Champion's
  fold-aggregate fitness held flat at **1.542** across all 15 generations
  (921 trades, 37% win, 1% stops, 4 halts, unchanged throughout — higher
  than the prior cycle's 1.460 because the daily bar rolled forward between
  batches, same mechanism every prior session has observed). Best-of-
  generation fold-fitness ranged roughly 1.258-2.058, never clearing the
  promotion-margin bar. See `runs/2026-11-21-0118-evolve-batch-v3.md`.
  Verified before commit: `python3 -m pytest -q` 505/505 both before
  (baseline) and after `evolve`; top-level key diff of `live_state.json`
  (snapshotted before the batch, checked directly in Python against the
  pre-batch copy) showed only `updated`/`researcher_memory`/`lineage`
  changed (genome, broker, journal, hard_call_reviews byte-identical);
  `lineage` length unchanged at 202 (bounded ring buffer, no new promotion
  attempt recorded); `tools/edit_bundle_module.py sync --check` clean;
  `holdout-pressure` re-checked post-batch — margin rose slightly (7.869 →
  7.870), draw count 2302 → 2305 (three new sealed-holdout draws from this
  batch's fold-aggregate-gate-clearing candidates, all correctly rejected),
  same slow-rise pattern already tracked under item 13, nothing new;
  dashboard rebuilt with `EVO_STATE` set (`index.html` shows 128050
  challenger idea(s) tried). Genome still v3 (1d) live, untouched. Container
  synced cleanly from `main` via `git checkout main` + `python3
  tools/git_sync.py` fast-forward through several other sessions'
  already-pushed commits from earlier today, no divergence, no
  shallow-clone staleness this cycle.

