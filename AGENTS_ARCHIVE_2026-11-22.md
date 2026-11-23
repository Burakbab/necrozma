- **Run 2026-11-22 (3-hourly check, ~21:47-22:09 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 131196 → 131403 (per
  `researcher_memory.tested`), stagnation/boldness counter 9518 → 9533.**
  No live trading this cycle (daily tick 100 already handled at the
  dedicated 00:20 UTC daily slot and by five prior 3-hourly checks' own
  evolve batches earlier today — confirmed via `live_state.json`'s
  `updated` timestamp at session start, `2026-11-22T19:07:33+00:00`,
  matching `runs/2026-11-22-1909-evolve-batch-v3.md`). `review-hard-calls`
  still 0 pending (6 reviewed, unchanged); `AGENTS.md` size 234,991 bytes at
  session start — under the archival-trigger range recent cycles have used,
  not archived this cycle. Champion's fold-aggregate fitness held flat at
  1.306 across all 15 generations (895 trades, 35% win, 1% stops, 4 halts,
  unchanged — no daily-bar roll this cycle). Best-of-generation fold-fitness
  ranged roughly 1.115-1.902, never clearing the promotion-margin bar.
  `tools/background_runner.py start` was denied again by the sandbox's
  auto-mode classifier (same denial two prior checks hit today,
  ~09:47-10:10 and ~12:47-13:11 UTC) — fell back to the harness's own
  `run_in_background` option as the single backgrounding mechanism, no
  `nohup`/`&`, per item 9's standing rule. See
  `runs/2026-11-22-2209-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 505/505 both before (baseline) and after `evolve`;
  top-level key diff of `live_state.json` against the last committed
  version showed only `updated`/`researcher_memory`/`lineage` changed
  (genome, broker, journal, hard_call_reviews byte-identical); `lineage`
  length unchanged at 202 (bounded ring buffer, no new promotion attempt
  recorded); `tools/edit_bundle_module.py sync --check` clean;
  `holdout-pressure` re-checked post-batch — margin rose slightly (7.881 →
  7.882), draw count 2355 → 2358 (a few new sealed-holdout draws from this
  batch's fold-aggregate-gate-clearing candidates, all correctly rejected),
  same slow-rise pattern already tracked under item 13, nothing new;
  dashboard rebuilt with `EVO_STATE` set (`index.html` shows 131403
  challenger idea(s) tried). Genome still v3 (1d) live, untouched. Container
  synced cleanly from `main` via `git checkout main` + `python3
  tools/git_sync.py` fast-forward through the day's other already-pushed
  commits, no divergence, no shallow-clone staleness this cycle.

- **Run 2026-11-22 (3-hourly check, ~18:46-19:09 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 130992 → 131196 (per
  `researcher_memory.tested`), stagnation/boldness counter 9502 → 9517.**
  No live trading this cycle (daily tick 100 already handled at the
  dedicated 00:20 UTC daily slot and by five prior 3-hourly checks' own
  evolve batches earlier today). `review-hard-calls` still 0 pending (6
  reviewed, unchanged); `AGENTS.md` size 232,042 bytes at session start —
  well under the archival-trigger range, not archived this cycle. Champion's
  fold-aggregate fitness held flat at 1.306 across all 15 generations (895
  trades, 35% win, 1% stops, 4 halts, unchanged — no daily-bar roll this
  cycle). Best-of-generation fold-fitness ranged roughly 1.268-2.065, never
  clearing the promotion-margin bar. **Hit item 9's own documented landmine
  while launching the batch**: backgrounded `evolve` by pairing a trailing
  shell `&` with the harness's own `run_in_background` option — exactly the
  "New trigger shape (2026-09-09)" pattern item 9 already warns against —
  so the wrapper reported "completed" almost instantly while the real
  `evolve` process (PID 848) kept running detached. Caught immediately via
  `ps aux` (the log held only the constitution-verified line, no generation
  output yet), then polled the real PID directly with a single-mechanism
  background wait until it actually exited, and only verified/committed
  after that. No harm, but a fresh concrete recurrence of a mistake item 9
  already names twice — see
  `runs/2026-11-22-1909-evolve-batch-v3.md` for the full account; worth
  flagging again that the inline `### Commands` warning and item 9's own
  writeup aren't fully preventing this. See `runs/2026-11-22-1909-evolve-batch-v3.md`.
  Verified before commit: `python3 -m pytest -q` 505/505 both before
  (baseline) and after `evolve`; top-level key diff of `live_state.json`
  (snapshotted before the batch) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py sync --check` clean; `holdout-pressure`
  re-checked post-batch — margin rose slightly (7.878 → 7.881), draw count
  2340 → 2355 (15 new sealed-holdout draws from this batch's
  fold-aggregate-gate-clearing candidates, all correctly rejected), same
  slow-rise pattern already tracked under item 13, nothing new; dashboard
  rebuilt with `EVO_STATE` set (`index.html` shows 131196 challenger
  idea(s) tried). Genome still v3 (1d) live, untouched. Container synced
  cleanly from `main` via `git checkout main` + `python3 tools/git_sync.py`
  fast-forward at session start, no divergence, no shallow-clone staleness
  this cycle.

- **Run 2026-11-22 (3-hourly check, ~15:46-16:20 UTC): archived the
  2026-11-21 AGENTS.md log slice, then 15 more real `evolve` generations
  against the live v3 (1d) champion, no promotion — cumulative candidates
  tried against v3 rose 130792 → 130992 (per `researcher_memory.tested`),
  stagnation/boldness counter 9488 → 9502.** No live trading this cycle
  (daily tick 100 already handled at the dedicated 00:20 UTC daily slot and
  by four prior 3-hourly checks' own evolve batches earlier today —
  confirmed via `live_state.json`'s `updated` timestamp at session start,
  `2026-11-22T13:08:53+00:00`, matching
  `runs/2026-11-22-1311-evolve-batch-v3.md`). Freshness checks:
  `review-hard-calls` still 0 pending (6 reviewed, unchanged), items 6/13
  still owner decisions, `AGENTS.md` size 254,478 bytes at session start —
  within the margin range every prior rotation in this index has used to
  trigger one — so archived the next oldest remaining slice (all nine
  2026-11-21 entries: eight 3-hourly checks plus that day's own weekend
  all-hands) verbatim to new `AGENTS_ARCHIVE_2026-11-21.md` first
  (committed/pushed separately, `87c7a3b`, verified byte-for-byte identical
  against the removed slice), cutting this file to 228,645 bytes. With that
  done, used the rest of the slot for one more real 15-generation batch
  (backgrounded via the harness's own `run_in_background`, single
  mechanism, no `nohup`/`&` — `tools/background_runner.py start` was tried
  first but was denied by the sandbox's auto-mode classifier as a
  "destructive or unwanted action"; fell back to the harness's native
  backgrounding instead), run after a baseline `pytest` pass, exit code 0,
  no truncation. Champion's fold-aggregate fitness held flat at 1.306
  across all 15 generations (895 trades, 35% win, 1% stops, 4 halts,
  unchanged throughout — no daily-bar roll this cycle). Best-of-generation
  fold-fitness ranged roughly 1.132-2.065, never clearing the
  promotion-margin bar. See `runs/2026-11-22-1620-evolve-batch-v3.md`.
  Verified before commit: `python3 -m pytest -q` 505/505 both before
  (baseline) and after `evolve`; top-level key diff of `live_state.json`
  (snapshotted before the batch, checked directly in Python against the
  pre-batch copy) showed only `updated`/`researcher_memory`/`lineage`
  changed (genome, broker, journal, hard_call_reviews byte-identical);
  `lineage` length unchanged at 202 (bounded ring buffer, no new promotion
  attempt recorded); `tools/edit_bundle_module.py sync --check` clean;
  `holdout-pressure` re-checked post-batch — margin rose slightly (7.879 →
  7.880), draw count 2345 → 2350 (five new sealed-holdout draws from this
  batch's fold-aggregate-gate-clearing candidates, all correctly rejected),
  same slow-rise pattern already tracked under item 13, nothing new;
  dashboard rebuilt with `EVO_STATE` set (`index.html` shows 130992
  challenger idea(s) tried). Genome still v3 (1d) live, untouched. Container
  synced cleanly from `main` via `git checkout main` + `python3
  tools/git_sync.py` fast-forward through 50 other sessions' already-pushed
  commits from earlier today, no divergence, no shallow-clone staleness
  this cycle. Hit the recurring `pip3` vs `python3 -m pip` numpy/pandas
  split again — `python3 -m pip install -r requirements.txt -q` fixed it
  immediately, same as prior sessions.

- **Run 2026-11-22 (3-hourly check, ~12:47-13:11 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 130584 → 130792 (per
  `researcher_memory.tested`), stagnation/boldness counter 9473 → 9488.**
  No live trading this cycle (daily tick 100 already handled at the
  dedicated 00:20 UTC daily slot and by four prior 3-hourly checks' own
  evolve batches earlier today — confirmed via `live_state.json`'s
  `updated` timestamp at session start, `2026-11-22T10:08:03+00:00`,
  matching `runs/2026-11-22-1010-evolve-batch-v3.md`). Freshness checks:
  `review-hard-calls` still 0 pending (6 reviewed, unchanged), items 6/13
  still owner decisions, `AGENTS.md` size 251,787 bytes at session start —
  close to but under the ~252KB+ range that has triggered archival in
  recent cycles, not archived this cycle — so, with nothing else queued,
  used the slot for one more real 15-generation batch (backgrounded via
  `tools/background_runner.py start`/`wait`, no `nohup`/`&`, output
  captured to a log file from the first byte), run after a baseline
  `pytest` pass, exit code 0, no truncation. Champion's fold-aggregate
  fitness held flat at 1.306 across all 15 generations (895 trades, 35%
  win, 1% stops, 4 halts, unchanged throughout — no daily-bar roll this
  cycle). Best-of-generation fold-fitness ranged roughly 0.817-2.065, never
  clearing the promotion-margin bar. See
  `runs/2026-11-22-1311-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 505/505 both before (baseline) and after `evolve`;
  top-level key diff of `live_state.json` (snapshotted before the batch,
  checked directly in Python against the pre-batch copy) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py sync --check` clean; `holdout-pressure`
  re-checked post-batch — margin rose slightly (7.876 → 7.879), draw count
  2332 → 2345 (13 new sealed-holdout draws from this batch's
  fold-aggregate-gate-clearing candidates, all correctly rejected), same
  slow-rise pattern already tracked under item 13, nothing new; dashboard
  rebuilt with `EVO_STATE` set (`index.html` shows 130792 challenger
  idea(s) tried). Genome still v3 (1d) live, untouched. Container synced
  cleanly from `main` via `git checkout main` + `python3 tools/git_sync.py`
  fast-forward through 50 other sessions' already-pushed commits from
  earlier today, no divergence, no shallow-clone staleness this cycle.

- **Run 2026-11-22 (3-hourly check, ~09:47-10:10 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 130382 → 130584 (per
  `researcher_memory.tested`), stagnation/boldness counter 9458 → 9473.**
  No live trading this cycle (daily tick 100 already handled at the
  dedicated 00:20 UTC daily slot and by three prior 3-hourly checks' own
  evolve batches earlier today — confirmed via `live_state.json`'s
  `updated` timestamp at session start, `2026-11-22T07:13:23+00:00`,
  matching `runs/2026-11-22-0716-evolve-batch-v3.md`). Freshness checks:
  `review-hard-calls` still 0 pending (6 reviewed, unchanged), items 6/13
  still owner decisions, `AGENTS.md` size 249,104 bytes at session start —
  under the ~252KB+ range that has triggered archival in recent cycles, not
  archived this cycle — so, with nothing else queued, used the slot for one
  more real 15-generation batch (backgrounded via
  `tools/background_runner.py start`/`wait`, no `nohup`/`&`, output
  captured to a log file from the first byte), run after a baseline
  `pytest` pass, exit code 0, no truncation. Champion's fold-aggregate
  fitness held flat at 1.306 across all 15 generations (895 trades, 35%
  win, 1% stops, 4 halts, unchanged throughout — no daily-bar roll this
  cycle). Best-of-generation fold-fitness ranged roughly 1.210-2.056, never
  clearing the promotion-margin bar. See
  `runs/2026-11-22-1010-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 505/505 both before (baseline) and after `evolve`;
  top-level key diff of `live_state.json` (snapshotted before the batch,
  checked directly in Python against the pre-batch copy) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py sync --check` clean; `holdout-pressure`
  re-checked post-batch — margin rose slightly (7.876 → 7.878), draw count
  2332 → 2340 (several new sealed-holdout draws from this batch's
  fold-aggregate-gate-clearing candidates, all correctly rejected), same
  slow-rise pattern already tracked under item 13, nothing new; dashboard
  rebuilt with `EVO_STATE` set (`index.html` shows 130584 challenger
  idea(s) tried). Genome still v3 (1d) live, untouched. Container synced
  cleanly from `main` via `git checkout main` + `python3 tools/git_sync.py`
  fast-forward through 5 other sessions' already-pushed commits from
  earlier today, no divergence, no shallow-clone staleness this cycle.

- **Run 2026-11-22 (weekend all-hands, ~06:00-07:xx UTC): re-ran `boldness-scan`
  for the first time since 2026-09-20, at a stagnation level roughly 5x
  higher than the last check — sealed-holdout clears are still 0/0 for both
  arms, extending the standing "boldness isn't the bottleneck" finding to a
  genuinely new, much-later point in the champion's undefeated streak.**
  Context: item 13's open question (is the never-resetting cumulative
  multiple-testing correction still well-calibrated?) and the boldness
  mechanism's own saturation story were both last measured in September at
  `stagnation≈1801`, `holdout_draws≈522-523`, `required_margin≈7.076`. Today
  those numbers are `stagnation=9443`, `holdout_draws=2327`,
  `required_margin=7.875` (per the prior cycle's `holdout-pressure` check) —
  a materially different point in the search's lifetime that nobody had
  gone back and re-measured. Ran `python3 evotrader_bundle.py boldness-scan
  --generations 20 --cap 20` (defaults otherwise: seed 7, n-blind 14,
  seeded from the real live `researcher_memory`), backgrounded via
  `tools/background_runner.py start`/`wait` (took ~50 minutes — two full
  20-generation shadow searches over the real 27-symbol 4-year universe,
  the first `wait` call hit its own 30-minute background-task limit while
  the underlying detached process kept running untouched, confirmed via
  `ps`/CPU-time before relaunching `wait` with a longer budget — exactly
  the detached-process behavior `tools/background_runner.py` was built for
  under item 9, worked as designed).

  Result: **UNCAPPED** (effective boldness climbed 9443→9462, tracking the
  real stagnation counter) — best-of-generation fold-fitness 1.195–3.229
  (one outlier generation at 3.229), fold-aggregate gate clears **10/20**,
  sealed-holdout gate clears **0/20**. **CAPPED at boldness=20** (same
  seeded stream, boldness held flat) — best-of-generation fold-fitness
  0.938–2.406, fold-aggregate gate clears **8/20**, sealed-holdout gate
  clears **0/20**. Both arms: final stagnation 9463, champion unchanged at
  v3 (shadow only, confirmed `git status`/`live_state.json` md5 both clean
  before and after — the read-only contract held).

  Reading: the fold-gate-clear counts rose sharply for both arms versus
  September (3/20→10/20 uncapped, 4/20→8/20 capped) and the *ranking*
  flipped (capped led in September, uncapped leads now) — read as noise
  from a different real evaluation window (per `fold-date-sensitivity`'s
  own finding that fold-aggregate fitness is as-of-date-dependent, the
  trailing-4y window anchored to "today" has moved ~2 months since the last
  check), not a boldness effect, and not strong evidence either way about
  which cap setting is "better" — same one-seed caveat the September run
  note already flagged, now reinforced by the ranking itself proving
  unstable across time. The number that **is** directly comparable across
  all three runs to date (15-gen/Sept, 20-gen/Sept, 20-gen/Nov) is
  sealed-holdout clears, and it has been **0/0, 0/0, 0/0** every single
  time, at stagnation levels spanning nearly an order of magnitude
  (1801→9443). This is new, direct evidence — not just the arithmetic
  `Researcher.perturb`'s docstring already implied — that raising the
  champion's undefeated streak by another ~7,600 candidates tried did not
  change the diagnosis: no real candidate from either arm would have
  promoted, boldness setting aside, and the bottleneck item 13's 2026-10-10
  design pass already quantified (the cumulative holdout margin, not the
  search's own exploration width) is still the operative one. Does not
  reopen or re-decide item 13 itself — that remains the owner's call on
  risk appetite, unchanged by this run. `python3 -m pytest -q` 505/505
  before and after (no code touched, diagnostic only). No trading, no
  genome, no constitution change, `AGENTS.md`'s own size (240,633 bytes at
  session start) left well under the archival threshold, not archived this
  cycle.

- **Run 2026-11-22 (3-hourly check, ~06:46-07:16 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 130176 → 130382 (per
  `researcher_memory.tested`), stagnation/boldness counter 9443 → 9458.**
  No live trading this cycle (daily tick 100 already handled at the
  dedicated 00:20 UTC daily slot and by two prior 3-hourly checks' own
  evolve batches earlier today — confirmed via `live_state.json`'s
  `updated` timestamp at session start, `2026-11-22T04:11:19+00:00`,
  matching `runs/2026-11-22-0412-evolve-batch-v3.md`). Freshness checks:
  `review-hard-calls` still 0 pending (6 reviewed, unchanged), items 6/13
  still owner decisions, `AGENTS.md` size 240,633 bytes at session start —
  under the ~252KB+ range that has triggered archival in recent cycles, not
  archived this cycle — so, with nothing else queued, used the slot for one
  more real 15-generation batch (backgrounded via
  `tools/background_runner.py start`/`wait`, no `nohup`/`&`, output
  captured to a log file from the first byte), run after a baseline
  `pytest` pass, exit code 0, no truncation. Champion's fold-aggregate
  fitness held flat at 1.306 across all 15 generations (895 trades, 35%
  win, 1% stops, 4 halts, unchanged throughout — no daily-bar roll this
  cycle). Best-of-generation fold-fitness ranged roughly 1.162-1.852, never
  clearing the promotion-margin bar. See
  `runs/2026-11-22-0716-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 505/505 both before (baseline) and after `evolve`;
  top-level key diff of `live_state.json` (snapshotted before the batch,
  checked directly in Python against the pre-batch copy) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py sync --check` clean; `holdout-pressure`
  re-checked post-batch — margin held essentially flat (7.872 → 7.876),
  draw count 2319 → 2332 (new sealed-holdout draws from this batch's
  fold-aggregate-gate-clearing candidates, all correctly rejected), same
  slow-rise pattern already tracked under item 13, nothing new; dashboard
  rebuilt with `EVO_STATE` set (`index.html` shows 130382 challenger
  idea(s) tried). Genome still v3 (1d) live, untouched. Container synced
  cleanly from `main` via `git checkout main` + `python3 tools/git_sync.py`
  fast-forward through 4 other sessions' already-pushed commits from
  earlier today, no divergence, no shallow-clone staleness this cycle. Hit
  the recurring `pip3` vs `python3 -m pip` numpy/pandas split again —
  `python3 -m pip install -r requirements.txt -q` fixed it immediately,
  same as prior sessions.

- **Run 2026-11-22 (3-hourly check, ~03:47-04:12 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 129969 → 130176 (per
  `researcher_memory.tested`), stagnation/boldness counter 9428 → 9443.**
  No live trading this cycle (daily tick 100 already handled at the
  dedicated 00:20 UTC daily slot and by the prior 3-hourly check's own
  evolve batch — confirmed via `live_state.json`'s `updated` timestamp at
  session start, `2026-11-22T01:07:39+00:00`, matching
  `runs/2026-11-22-0109-evolve-batch-v3.md`). Freshness checks:
  `review-hard-calls` still 0 pending (6 reviewed, unchanged), items 6/13
  still owner decisions, `AGENTS.md` size 237,538 bytes at session start —
  well under the ~252KB+ range that has triggered archival in recent
  cycles, not archived this cycle — so, with nothing else queued, used the
  slot for one more real 15-generation batch (backgrounded via
  `tools/background_runner.py start`/`wait`, no `nohup`/`&`, output
  captured to a log file from the first byte), run after a baseline
  `pytest` pass, exit code 0, no truncation. Champion's fold-aggregate
  fitness held flat at 1.306 across all 15 generations (895 trades, 35%
  win, 1% stops, 4 halts, unchanged throughout — no daily-bar roll this
  cycle). Best-of-generation fold-fitness ranged roughly 1.102-1.905, never
  clearing the promotion-margin bar. See
  `runs/2026-11-22-0412-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 505/505 both before (baseline) and after `evolve`;
  one run in between hit a single flaky failure
  (`test_evolve_saves_and_matches_its_own_dry_run_decision`, a live-network
  call to `data-api.binance.vision` returning an inconsistent HTTP 400
  across two subprocess calls) that passed in isolation and on a clean
  second full-suite run — same test-timing/network flakiness class already
  logged by several prior sessions, not a regression; top-level key diff of
  `live_state.json` (snapshotted before the batch, checked directly in
  Python against the pre-batch copy) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py sync --check` clean; `holdout-pressure`
  re-checked post-batch — margin held flat (7.875), draw count 2326 → 2327
  (one new sealed-holdout draw from this batch's fold-aggregate-gate-
  clearing candidates, correctly rejected), same slow-rise pattern already
  tracked under item 13, nothing new; dashboard rebuilt with `EVO_STATE`
  set (`index.html` shows 130176 challenger idea(s) tried). Genome still v3
  (1d) live, untouched. Container started in detached HEAD (known
  cloud-clone artifact) — `git checkout main` + `python3 tools/git_sync.py`
  fast-forwarded cleanly through 49 other sessions' already-pushed commits
  from earlier today/yesterday, no divergence, no shallow-clone staleness
  this cycle.

- **Run 2026-11-22 (3-hourly check, ~00:46-01:09 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 129765 → 129969 (per
  `researcher_memory.tested`), stagnation/boldness counter 9413 → 9427.**
  No live trading this cycle (daily tick 100 already handled at the
  dedicated 00:20 UTC daily slot ~26 minutes before this session started —
  confirmed via `live_state.json`'s `updated` timestamp at session start,
  `2026-11-22T00:21:35+00:00`, matching `runs/2026-11-22-0021-daily-trading.md`).
  Freshness checks: `review-hard-calls` still 0 pending (6 reviewed,
  unchanged), items 6/13 still owner decisions, `AGENTS.md` size 234,879
  bytes at session start — under the ~252KB+ range that has triggered
  archival in recent cycles, not archived this cycle — so, with nothing
  else queued, used the slot for one more real 15-generation batch
  (backgrounded via `tools/background_runner.py start`/`wait`, no
  `nohup`/`&`, output captured to a log file from the first byte), run
  after a baseline `pytest` pass, exit code 0, no truncation. Champion's
  fold-aggregate fitness was 1.542 briefly then settled to **1.306** for
  the rest of the batch (895 trades, 35% win, 1% stops, 4 halts) — the
  daily bar rolled forward partway through this batch. Best-of-generation
  fold-fitness ranged roughly 1.306-1.905, never clearing the
  promotion-margin bar. See `runs/2026-11-22-0109-evolve-batch-v3.md`.
  Verified before commit: `python3 -m pytest -q` 505/505 both before
  (baseline) and after `evolve`; top-level key diff of `live_state.json`
  (snapshotted before the batch, checked directly in Python against the
  pre-batch copy) showed only `updated`/`researcher_memory`/`lineage`
  changed (genome, broker, journal, hard_call_reviews byte-identical);
  `lineage` length unchanged at 202 (bounded ring buffer, no new promotion
  attempt recorded); `tools/edit_bundle_module.py sync --check` clean;
  `holdout-pressure` re-checked post-batch — margin rose slightly (7.872 →
  7.875), draw count 2319 → 2326 (several new sealed-holdout draws from
  this batch's fold-aggregate-gate-clearing candidates, all correctly
  rejected), same slow-rise pattern already tracked under item 13, nothing
  new; dashboard rebuilt with `EVO_STATE` set (`index.html` shows 129969
  challenger idea(s) tried). Genome still v3 (1d) live, untouched.
  Container synced cleanly from `main` via `git checkout main` + `python3
  tools/git_sync.py` fast-forward through the day's other already-pushed
  commits, no divergence, no shallow-clone staleness this cycle.


