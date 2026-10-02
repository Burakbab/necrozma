# Archived: AGENTS.md "Current state" log, 2026-09-26

Moved verbatim out of `AGENTS.md` on 2026-10-02 (3-hourly check) to keep
that file under its 256KB single-read limit -- same recurring pattern as
every prior `AGENTS_ARCHIVE_*` rotation (see `AGENTS.md`'s own archive index
at the end of its "Current state" section for the full list). Nothing
reworded, nothing lost. Chronological order preserved (newest first, matching
the live file's own convention). For anything older, see
`AGENTS_ARCHIVE_2026-09-25.md` and the archive files it in turn points to.

---

- **Run 2026-09-26 (3-hourly check, ~21:46-22:18 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 35210 → 35418 (per
  `researcher_memory.tested`), stagnation/boldness counter 2538 → 2553.** No
  live trading this cycle (tick 43 already handled at the dedicated 00:20
  UTC daily slot, and the prior 3-hourly check's own evolve batch already
  ran at ~18:46-19:22 UTC — confirmed via `live_state.json`'s `updated`
  timestamp at session start, `2026-09-26T19:12:28+00:00`, matching
  `runs/2026-09-26-1922-evolve-batch-v3.md`). Freshness checks before
  running: `review-hard-calls` still 0 pending (4 reviewed, unchanged),
  items 6/13 still owner decisions, `AGENTS.md` size 239,313 bytes — well
  under the 256KB threshold — so, with nothing else queued, used the slot
  for one more real 15-generation batch via `tools/background_runner.py`
  (`start` + separate `wait`), exit code 0, no truncation, ~28.7 minutes.
  Champion's fold-aggregate fitness held flat at 1.751 across all 15
  generations (959 trades, 38% win, 1% stops, 4 halts, unchanged
  throughout). Best-of-generation fold-fitness ranged 1.673-2.336, never
  clearing the promotion-margin bar. See
  `runs/2026-09-26-2218-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 434/434 both before (baseline) and after `evolve`;
  top-level key diff of `live_state.json` (checked directly in Python
  against `git show HEAD:live_state.json`, not just eyeballed) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  `holdout-pressure` re-checked (read-only, no state change) — margin
  unchanged at 7.205, draw 658 (this batch's candidates never cleared the
  fold-aggregate gate, so no new holdout draws), same slow-rise pattern
  already tracked under item 13, nothing new; dashboard rebuilt with
  `EVO_STATE` set (`index.html` shows 35418 challenger ideas tried).
  Genome still v3 (1d) live, untouched. Container arrived on `main`, one
  commit behind `origin/main` in detached HEAD; `git checkout main` plus
  `tools/git_sync.py` fast-forwarded cleanly, nothing lost.

- **Run 2026-09-26 (3-hourly check, ~18:46-19:22 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 35003 → 35210 (per
  `researcher_memory.tested`), stagnation/boldness counter 2524 → 2538.** No
  live trading this cycle (tick 43 already handled at the dedicated 00:20
  UTC daily slot, and the prior 3-hourly check's own evolve batch already
  ran at ~15:47-16:15 UTC — confirmed via `live_state.json`'s `updated`
  timestamp at session start, `2026-09-26T16:14:51+00:00`, matching
  `runs/2026-09-26-1615-evolve-batch-v3.md`). Freshness checks before
  running: `review-hard-calls` still 0 pending (4 reviewed, unchanged),
  items 6/13 still owner decisions, `AGENTS.md` size 237,026 bytes — well
  under the 256KB threshold — so, with nothing else queued, used the slot
  for one more real 15-generation batch via `tools/background_runner.py`
  (`start` + separate `wait`), exit code 0, no truncation, ~25.4 minutes.
  Champion's fold-aggregate fitness held flat at 1.751 across all 15
  generations (959 trades, 38% win, 1% stops, 4 halts, unchanged
  throughout). Best-of-generation fold-fitness ranged 1.566-2.149, never
  clearing the promotion-margin bar. See
  `runs/2026-09-26-1922-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 434/434; top-level key diff of `live_state.json`
  (checked directly in Python against `git show HEAD:live_state.json`, not
  just eyeballed) showed only `updated`/`researcher_memory`/`lineage`
  changed (genome, broker, journal, hard_call_reviews byte-identical);
  `lineage` length unchanged at 202 (bounded ring buffer, no new promotion
  attempt recorded); `tools/edit_bundle_module.py verify`/`sync --check`
  both clean; `holdout-pressure` re-checked (read-only, no state change) —
  margin rose slightly (7.205, was 7.204) at draw 658, same slow-rise
  pattern already tracked under item 13, nothing new; dashboard rebuilt
  with `EVO_STATE` set (`index.html` shows 35210 challenger ideas tried).
  Genome still v3 (1d) live, untouched. Container arrived detached HEAD one
  commit behind (the prior 3-hourly check's own commit); `git checkout
  main` plus `tools/git_sync.py` fast-forwarded cleanly, nothing lost.

- **Run 2026-09-26 (3-hourly check, ~15:47-16:15 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 34794 → 35003 (per
  `researcher_memory.tested`), stagnation/boldness counter 2509 → 2524.** No
  live trading this cycle (tick 43 already handled at the dedicated 00:20
  UTC daily slot, and the prior 3-hourly check's own evolve batch already
  ran at ~12:45-12:52 UTC — confirmed via `live_state.json`'s `updated`
  timestamp at session start, `2026-09-26T13:15:58+00:00`, matching
  `runs/2026-09-26-1252-evolve-batch-v3.md`). Freshness checks before
  running: `review-hard-calls` still 0 pending (4 reviewed, unchanged),
  items 6/13 still owner decisions, `AGENTS.md` size 234,622 bytes — well
  under the 256KB threshold — so, with nothing else queued, used the slot
  for one more real 15-generation batch via `tools/background_runner.py`
  (`start` + separate `wait`), exit code 0, no truncation, ~29 minutes.
  Champion's fold-aggregate fitness held flat at 1.751 across all 15
  generations (959 trades, 38% win, 1% stops, 4 halts, unchanged
  throughout). Best-of-generation fold-fitness ranged 1.183-2.955, never
  clearing the promotion-margin bar. See
  `runs/2026-09-26-1615-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 434/434 both before (baseline) and after `evolve`;
  top-level key diff of `live_state.json` (checked directly in Python
  against `git show HEAD:live_state.json`, not just eyeballed) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  `holdout-pressure` re-checked (read-only, no state change) — margin
  unchanged at 7.204, draw 657 (this batch's candidates never cleared the
  fold-aggregate gate, so no new holdout draws), same slow-rise pattern
  already tracked under item 13, nothing new; dashboard rebuilt with
  `EVO_STATE` set (`index.html` shows 35003 challenger ideas tried).
  Genome still v3 (1d) live, untouched. Container arrived detached HEAD one
  commit behind (the prior 3-hourly check's own commit); `git checkout
  main` plus `tools/git_sync.py` fast-forwarded cleanly, nothing lost.

- **Run 2026-09-26 (3-hourly check, ~12:45-12:52 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 34586 → 34794 (per
  `researcher_memory.tested`), stagnation/boldness counter 2494 → 2508.** No
  live trading this cycle (tick 43 already handled at the dedicated 00:20
  UTC daily slot, and the prior 3-hourly check's own evolve batch already
  ran at ~10:28 UTC — confirmed via `live_state.json`'s `updated` timestamp
  at session start, `2026-09-26T10:28:01+00:00`, matching
  `runs/2026-09-26-1033-evolve-batch-v3.md`). Freshness checks before
  running: `review-hard-calls` still 0 pending (4 reviewed, unchanged),
  items 6/13 still owner decisions, `AGENTS.md` size 232,258 bytes — well
  under the 256KB threshold — so, with nothing else queued, used the slot
  for one more real 15-generation batch via `tools/background_runner.py`
  (`start` + separate `wait`), exit code 0, no truncation, ~13 minutes.
  Champion's fold-aggregate fitness held flat at 1.751 across all 15
  generations (959 trades, 38% win, 1% stops, 4 halts, unchanged
  throughout). Best-of-generation fold-fitness ranged 1.636-2.955, never
  clearing the promotion-margin bar. See
  `runs/2026-09-26-1252-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 434/434 both before (baseline) and after `evolve`;
  top-level key diff of `live_state.json` (checked directly in Python
  against `git show HEAD:live_state.json`, not just eyeballed) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  `holdout-pressure` re-checked (read-only, no state change) — margin rose
  slightly (7.202, was 7.199) at draw 654, same slow-rise pattern already
  tracked under item 13, nothing new; dashboard rebuilt with `EVO_STATE` set
  (`index.html` shows 34794 challenger ideas tried). Genome still v3 (1d)
  live, untouched. Container arrived detached HEAD seven commits behind
  (weekend all-hands + daily discussion + prior 3-hourly check's own
  commits); `git checkout main` plus `tools/git_sync.py` fast-forwarded
  cleanly, nothing lost.

- **Run 2026-09-26 (3-hourly check, ~09:45-10:33 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 34379 → 34586 (per
  `researcher_memory.tested`), stagnation/boldness counter 2479 → 2493.** No
  live trading this cycle (tick 43 already handled at the dedicated 00:20
  UTC daily slot, and the weekend all-hands session's own 30-generation
  evolve batch already ran at ~07:07 UTC — confirmed via `live_state.json`'s
  `updated` timestamp at session start, `2026-09-26T07:07:10+00:00`,
  matching `runs/2026-09-26-0600-weekend-all-hands.md`; the intervening
  09:00 UTC daily discussion, `runs/2026-09-26-0900-daily-discussion.md`,
  was read-only and didn't touch state). Freshness checks before running:
  `review-hard-calls` still 0 pending (4 reviewed, unchanged), items 6/13
  still owner decisions, `AGENTS.md` size 229,826 bytes — well under the
  256KB threshold — so, with nothing else queued, used the slot for one
  more real 15-generation batch via `tools/background_runner.py` (`start` +
  separate `wait`), exit code 0, no truncation, ~30 minutes. Champion's
  fold-aggregate fitness held flat at 1.751 across all 15 generations (959
  trades, 38% win, 1% stops, 4 halts, unchanged throughout). Best-of-generation
  fold-fitness ranged 1.265-2.255, never clearing the promotion-margin bar.
  Verified before commit: `python3 -m pytest -q` 434/434 both before
  (baseline) and after `evolve`; top-level key diff of `live_state.json`
  (checked directly in Python against `git show HEAD:live_state.json`, not
  just eyeballed) showed only `updated`/`researcher_memory`/`lineage`
  changed (genome, broker, journal, hard_call_reviews byte-identical);
  `lineage` length unchanged at 202 (bounded ring buffer, no new promotion
  attempt recorded); `tools/edit_bundle_module.py verify`/`sync --check`
  both clean; `holdout-pressure` re-checked (read-only, no state change) —
  margin rose slightly (7.202, was 7.199) at draw 654, same slow-rise
  pattern already tracked under item 13, nothing new; dashboard rebuilt
  with `EVO_STATE` set (`index.html` shows 34586 challenger ideas tried).
  Genome still v3 (1d) live, untouched. Container arrived detached HEAD six
  commits behind (the weekend all-hands session's own commits); `git
  checkout main` plus `tools/git_sync.py` fast-forwarded cleanly, nothing
  lost.

- **Run 2026-09-26 (weekend all-hands, ~06:00-07:15 UTC): shipped
  `short-headroom`, a new read-only diagnostic answering item 5's
  "is there real upside on the table from shorting at all" question, and
  ran it against the live v3 champion for the first time.** New
  `loop.engine.benchmark_sell_short` (real `PaperBroker.short()`/`.mark()`/
  `.cover()` mechanics, not raw zero-cost math) plus a new CLI command,
  `evotrader_bundle.py short-headroom`, that reports it next to
  `benchmark_buy_hold` over the champion's exact `regime`-style fold/holdout
  windows. 8 new tests (`tests/test_short_headroom_benchmark.py`), full
  suite 426 → 434 passed, both before and after the change. First real
  result: a static, unmanaged, equal-weight short of the champion's own
  27-symbol universe would have been catastrophic in 3 of 4 real windows
  (fold 1 -85.3%/-99.4%, fold 2 -136.9%/-157.9%, holdout -61.1%/-67.9%,
  short-0bp/short-with-modelled-borrow respectively — all bull windows) and
  only helped in fold 3, the one real bear window (buy&hold -39.1%, short
  captured +69% of that theoretical edge after realistic costs, +26.8% real
  return). See "Owner decisions pending" item 5 and the `### Commands`
  section above for the full write-up and what this does/doesn't decide
  (nothing — no genome, council, mutation-range, or `live_state.json`
  change; this is evidence for a future owner-gated design pass, same
  "measure before building" discipline as item 3's correlation-penalty
  saga). Verified: `tools/edit_bundle_module.py sync`/`verify` both clean
  (bundle regenerated from the real `loop/engine.py` edit, not hand-touched),
  `evotrader.manifest` unchanged (`726dfa4bac85891a` — `core/portfolio.py`,
  the actually-protected file, was never touched; only `loop/engine.py` and
  `evotrader_bundle.py`'s own CLI dispatch section, neither checksummed),
  `live_state.json` untouched throughout. Second, after committing/pushing
  the diagnostic: with nothing else queued and more time budget than a
  3-hourly check, ran one real 30-generation `evolve` batch against the
  live v3 champion (bigger than a weekday session's usual 15, to use the
  extra slot depth-first rather than as two separate smaller runs) via
  `tools/background_runner.py`, exit code 0, no truncation, ~30 minutes.
  No promotion — champion's fold-aggregate fitness held flat at 1.751
  across all 30 generations (959 trades, 38% win, 1% stops, 4 halts,
  unchanged throughout); cumulative candidates tried against v3 rose
  33963 → 34379 (per `researcher_memory.tested`), stagnation/boldness
  counter 2449 → 2479; best-of-generation fold-fitness ranged 1.511-2.265,
  never clearing the promotion-margin bar (several generations' best did
  beat the champion's own raw 1.751, which is why `holdout-pressure`'s
  cumulative draw count still advanced 648 → 651 — clearing that easier,
  raw-comparison bar is enough to trigger a holdout check, clearing the
  much higher multiple-testing-adjusted margin is not the same thing and
  is what "no proposal cleared the bar" in the per-generation log means). Verified before commit: `python3
  -m pytest -q` 434/434 both before (right after the diagnostic commit) and
  after `evolve`; top-level key diff of `live_state.json` (checked directly
  in Python against `git show HEAD:live_state.json`, not just eyeballed)
  showed only `updated`/`researcher_memory`/`lineage` changed (genome,
  broker, journal, hard_call_reviews byte-identical); `lineage` length
  unchanged at 202 (bounded ring buffer, no new promotion attempt
  recorded); `tools/edit_bundle_module.py verify`/`sync --check` both
  clean; `holdout-pressure` re-checked (read-only, no state change) —
  margin rose slightly (7.199, was 7.197) at draw 651 (three more
  fold-aggregate-clearing candidates from this batch each lost their own
  sealed-holdout draw), same slow-rise pattern already tracked under item
  13, nothing new; `review-hard-calls`
  still 0 pending (4 reviewed, unchanged); dashboard rebuilt with
  `EVO_STATE` set (`index.html` shows 34379 challenger ideas tried).
  Genome still v3 (1d) live, untouched. See
  `runs/2026-09-26-0600-weekend-all-hands.md` for the full write-up of both
  pieces of this session.

- **Run 2026-09-26 (3-hourly check, ~03:46-04:22 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 33759 → 33963 (per
  `researcher_memory.tested`), stagnation/boldness counter 2434 → 2448.** No
  live trading this cycle (tick 43 already handled at the dedicated 00:20
  UTC daily slot, `43 % 7 == 1` so no `evolve` ran as part of that tick, and
  the prior 3-hourly check's own evolve batch already ran at ~01:25 UTC —
  confirmed via `live_state.json`'s `updated` timestamp at session start,
  `2026-09-26T01:25:33+00:00`, matching `runs/2026-09-26-0129-evolve-batch-v3.md`).
  Freshness checks before running: `review-hard-calls` still 0 pending (4
  reviewed, unchanged), items 6/13 still owner decisions, `AGENTS.md` size
  219,407 bytes — comfortably under the 256KB threshold — so, with nothing
  else queued, used the slot for one more real 15-generation batch via
  `tools/background_runner.py` (`start` + separate `wait`), exit code 0, no
  truncation, ~20.5 minutes. Champion's fold-aggregate fitness held flat at
  1.751 across all 15 generations (959 trades, 38% win, 1% stops, 4 halts,
  unchanged throughout). Best-of-generation fold-fitness ranged 1.434-2.711,
  never clearing the promotion-margin bar. See
  `runs/2026-09-26-0422-evolve-batch-v3.md`. Verified before commit: `python3
  -m pytest -q` 426/426 both before (baseline) and after `evolve`; top-level
  key diff of `live_state.json` (checked directly in Python against `git
  show HEAD:live_state.json`, not just eyeballed) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  `holdout-pressure` re-checked (read-only, no state change) — margin rose
  slightly (7.197, was 7.194) at draw 648, same slow-rise pattern already
  tracked under item 13, nothing new; dashboard rebuilt with `EVO_STATE` set
  (`index.html` shows 33963 challenger ideas tried). Genome still v3 (1d)
  live, untouched. No git sync issues this cycle — container arrived
  detached HEAD two commits behind (the prior evolve batch's own commit);
  `git checkout main` plus `tools/git_sync.py` fast-forwarded cleanly.

- **Run 2026-09-26 (3-hourly check, ~00:48-01:22 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 33552 → 33759 (per
  `researcher_memory.tested`), stagnation/boldness counter 2419 → 2434.** No
  live trading this cycle (tick 43 already handled at the dedicated 00:20
  UTC daily slot, `43 % 7 == 1` so no `evolve` ran as part of that tick —
  confirmed via `runs/2026-09-26-0022-daily-trading.md`). Freshness checks
  before running: `review-hard-calls` still 0 pending (4 reviewed,
  unchanged), items 6/13 still owner decisions, `AGENTS.md` size 217,188
  bytes — well under the 256KB threshold — so, with nothing else queued,
  used the slot for one more real 15-generation batch via
  `tools/background_runner.py` (`start` + separate `wait`), exit code 0, no
  truncation, ~34 minutes. Champion's fold-aggregate fitness held flat at
  1.751 across all 15 generations (959 trades, 38% win, 1% stops, 4 halts,
  unchanged throughout). Best-of-generation fold-fitness ranged
  1.555-2.646, never clearing the promotion-margin bar. See
  `runs/2026-09-26-0129-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 426/426 both before (baseline) and after `evolve`;
  top-level key diff of `live_state.json` (checked directly in Python
  against `git show HEAD:live_state.json`, not just eyeballed) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  `holdout-pressure` re-checked (read-only, no state change) — margin rose
  slightly (7.194, was 7.192) at draw 645, same slow-rise pattern already
  tracked under item 13, nothing new; dashboard rebuilt with `EVO_STATE` set
  (`index.html` shows 33759 challenger ideas tried). Genome still v3 (1d)
  live, untouched. No git sync issues this cycle — container arrived
  detached HEAD one commit behind (the daily-trading tick's own commit);
  `git checkout main` plus `tools/git_sync.py` fast-forwarded cleanly.

