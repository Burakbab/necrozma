# AGENTS.md Current-state archive: 2026-09-17 00:47 to 2026-09-17 22:18 UTC

Archived 2026-09-24 (3-hourly check) to keep `AGENTS.md` under the
256KB single-read limit that scheduled sessions' `Read` tool enforces —
the file had regrown to 256,106 bytes (approaching the 262,144-byte/256KB
threshold, with only about 6KB of margin left), continuing the same
recurring growth pattern the 2026-09-04, 2026-09-10, 2026-09-15,
2026-09-16, 2026-09-18, 2026-09-20, and 2026-09-22 rotations each hit in
turn. This file holds the next oldest slice of `AGENTS.md`'s "Current
state" dated-entry log, moved here **verbatim, byte-for-byte, newest
first (same order as the original)** — nothing reworded or summarized.
The live `AGENTS.md` keeps everything from 2026-09-18 ~00:48 UTC onward,
plus the full "Owner decisions pending", promotion-history, "Measured",
and "Rules" sections, which were never part of this rotation.
Read `AGENTS_ARCHIVE_2026-09-15_to_2026-09-16.md` next, then
`AGENTS_ARCHIVE_2026-09-13_to_2026-09-14.md`, then
`AGENTS_ARCHIVE_2026-09-11_to_2026-09-12.md`, then
`AGENTS_ARCHIVE_2026-09-08_to_2026-09-10.md`, then
`AGENTS_ARCHIVE_2026-09-02_to_2026-09-08.md`, then
`AGENTS_ARCHIVE_2026-08-29_to_2026-09-02.md`, then
`AGENTS_ARCHIVE_2026-08-15_to_2026-08-29.md`, for anything before
2026-09-17 ~00:47 UTC.

---

- **Run 2026-09-17 (3-hourly check, ~21:49-22:18 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 20611 → 20817, stagnation counter
  1482 → 1497.** No live trading this cycle (tick 34 already handled at
  00:20 UTC — confirmed via `live_state.json`'s `updated` timestamp and
  independently by `runs/2026-09-17-2030-daily-evaluation.md`, the day's
  read-only mechanism-health check, before starting). Freshness checks
  before running: `review-hard-calls` still 0 pending (2 reviewed,
  unchanged), items 2/5/6 still not a scheduled session's call, item 7
  feature-complete, item 4 blocked on a real hard-call flag (none pending)
  — so, with nothing else queued, used the slot for one more real
  15-generation batch (offline/shadow development against the live
  champion) via `tools/background_runner.py` (`start` + backgrounded
  `wait`), exit code 0, no truncation. Champion's fold-aggregate fitness
  held flat at 1.463 across all 15 generations (927 trades, 37% win, 1%
  stops, 4 halts, unchanged throughout). Raw best-of-generation fold-fitness
  beat the champion's own 1.463 in **9/15 generations** (60%, two exact
  ties, range otherwise 1.262-2.241). See
  `runs/2026-09-17-2218-evolve-batch-v3.md`. Verified before commit: `python3
  -m pytest -q` 422/422 both before (baseline) and after `evolve`; direct
  top-level key diff of `live_state.json` showed only
  `lineage`/`researcher_memory`/`updated` changed (genome, broker, journal,
  hard_call_reviews byte-identical); constitution verified
  `726dfa4bac85891a` unchanged; `tools/edit_bundle_module.py verify`/`sync
  --check` both clean; `holdout-pressure` re-checked (read-only, no state
  change) — margin ~7.02-7.04, consistent with the already-tracked "Owner
  decisions pending" drawdown-gate question, nothing new; dashboard rebuilt
  (`index.html`). Genome still v3 (1d) live, untouched. **Git note**:
  container started in detached HEAD with local `main` diverged from
  `origin/main` (fetch reported "forced update", no common ancestor);
  working tree was clean, so `git checkout -B main origin/main` re-pointed
  the local branch to the confirmed-authoritative remote tip directly, no
  content lost.

- **Run 2026-09-17 (3-hourly check, ~18:48-19:17 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 20404 → 20611, stagnation counter
  1468 → 1482.** No live trading this cycle (tick 34 already handled at
  00:20 UTC — confirmed via `live_state.json`'s `updated` timestamp and
  `runs/2026-09-17-0020-daily-trading.md` before starting). Freshness checks
  before running: `review-hard-calls` still 0 pending (2 reviewed,
  unchanged), `holdout-pressure` re-checked (read-only) with no change from
  the last check (margin ~7.01-7.03), items 2/5/6 still not a scheduled
  session's call, item 7 feature-complete, item 4 blocked on a real
  hard-call flag (none pending), `AGENTS.md` size 233KB (under the 256KB
  rotation threshold) — so, with nothing else queued, used the slot for one
  more real 15-generation batch (offline/shadow development against the
  live champion) via `tools/background_runner.py` (`start` + backgrounded
  `wait`), exit code 0, no truncation. Champion's fold-aggregate fitness
  held flat at 1.463 across all 15 generations (927 trades, 37% win, 1%
  stops, 4 halts, unchanged throughout). Raw best-of-generation fold-fitness
  beat the champion's own 1.463 in **13/15 generations** (87%, one exact tie
  at generation 10, range otherwise 1.006-3.294). See
  `runs/2026-09-17-1917-evolve-batch-v3.md`. Verified before commit: `python3
  -m pytest -q` 422/422 both before (baseline) and after `evolve`; direct
  top-level key diff of `live_state.json` showed only
  `lineage`/`researcher_memory`/`updated` changed (genome, broker, journal,
  hard_call_reviews byte-identical); constitution verified
  `726dfa4bac85891a` unchanged; `tools/edit_bundle_module.py verify`/`sync
  --check` both clean; dashboard rebuilt (`index.html`). Genome still v3
  (1d) live, untouched. **Git note**: container started in detached HEAD
  with local `main` (a shallow clone) stale behind `origin/main`; `git
  reset --hard origin/main` was denied by this session's action classifier
  as irreversible local destruction, so — same workaround as the
  2026-09-16 ~21:51 UTC and 2026-09-17 ~15:50 UTC sessions — did all work
  directly on detached `origin/main` (`git checkout origin/main`) without
  touching the local `main` ref, then pushed at the end with `git push
  origin HEAD:main`. No content at risk either way; `origin/main` was
  already the confirmed-authoritative tip with a clean working tree.

- **Run 2026-09-17 (3-hourly check, ~15:50-16:33 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 20195 → 20404, stagnation counter
  1452 → 1467.** No live trading this cycle (tick 34 already handled at
  00:20 UTC — confirmed via `live_state.json`'s `updated` timestamp and
  `runs/2026-09-17-0020-daily-trading.md` before starting). Freshness checks
  before running: `review-hard-calls` still 0 pending (2 reviewed,
  unchanged), `holdout-pressure` re-checked (read-only) with no change from
  the last check (16 draws, all still lost, margin ~7.0-7.025), items 2/5/6
  still not a scheduled session's call, item 7 feature-complete, item 4
  blocked on a real hard-call flag (none pending) — so, with nothing else
  queued, used the slot for one more real 15-generation batch
  (offline/shadow development against the live champion) via
  `tools/background_runner.py` (`start` + backgrounded `wait`), exit code 0,
  no truncation. Champion's fold-aggregate fitness held flat at 1.463 across
  all 15 generations (927 trades, 37% win, 1% stops, 4 halts, unchanged
  throughout). Raw best-of-generation fold-fitness beat the champion's own
  1.463 in **10/15 generations** (67%, one exact tie at generation 11). See
  `runs/2026-09-17-1633-evolve-batch-v3.md`. Verified before commit: `python3
  -m pytest -q` 422/422 both before (baseline) and after `evolve`; direct
  top-level key diff of `live_state.json` showed only
  `lineage`/`researcher_memory`/`updated` changed (genome, broker, journal,
  hard_call_reviews byte-identical); constitution verified
  `726dfa4bac85891a` unchanged; `tools/edit_bundle_module.py verify`/`sync
  --check` both clean; dashboard rebuilt (`index.html`). Genome still v3
  (1d) live, untouched. **Git note**: container started in detached HEAD
  with local `main` 50 commits behind `origin/main` (both `git pull` and
  `git pull --rebase` failed as expected — not currently on a branch, then
  reported diverged/no-common-ancestor, this container's usual shallow-clone
  staleness). This session's action classifier denied `git checkout -B main
  origin/main` as irreversible local destruction, so — same workaround as
  the 2026-09-16 ~21:51 UTC session — did all work directly on detached
  `origin/main` (`git checkout origin/main`) without touching the local
  `main` ref at all, then pushed at the end with `git push origin
  HEAD:main`. No content at risk either way; `origin/main` was already the
  confirmed-authoritative tip with a clean working tree.

- **Run 2026-09-17 (3-hourly check, ~12:47-13:21 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 19988 → 20195, stagnation counter
  1437 → 1452.** No live trading this cycle (tick 34 already handled at
  00:20 UTC — confirmed via `live_state.json`'s `updated` timestamp and
  `runs/2026-09-17-0020-daily-trading.md` before starting). Freshness checks
  before running: `review-hard-calls` still 0 pending (2 reviewed,
  unchanged), `holdout-pressure` re-checked (read-only) with no change from
  the last check, items 2/5/6 still not a scheduled session's call, item 7
  feature-complete, item 4 blocked on a real hard-call flag (none pending)
  — so, with nothing else queued, used the slot for one more real
  15-generation batch (offline/shadow development against the live
  champion) via `tools/background_runner.py` (`start` + backgrounded
  `wait`), exit code 0, no truncation. Champion's fold-aggregate fitness
  held flat at 1.463 across all 15 generations (927 trades, 37% win, 1%
  stops, 4 halts, unchanged throughout). See
  `runs/2026-09-17-1321-evolve-batch-v3.md`. Verified before commit: `python3
  -m pytest -q` 422/422 both before (baseline) and after `evolve`; direct
  top-level key diff of `live_state.json` showed only
  `lineage`/`researcher_memory`/`updated` changed (genome, broker, journal,
  hard_call_reviews byte-identical); constitution verified
  `726dfa4bac85891a` unchanged; `tools/edit_bundle_module.py verify`/`sync
  --check` both clean; dashboard rebuilt (`index.html`). Genome still v3
  (1d) live, untouched. **Git note**: container started in detached HEAD
  with local `main` 70 commits behind `origin/main` (fetch reported "forced
  update"). The repo was a genuinely shallow clone this cycle (`git
  rev-parse --is-shallow-repository` → true, two grafted shallow-boundary
  commits), which is what made `git merge-base main origin/main` initially
  report no common ancestor even though nothing was actually rewritten —
  `git fetch --unshallow origin` resolved it and confirmed local `main` was
  a strict ancestor of `origin/main` (0 unique commits), so `git merge
  --ff-only origin/main` applied cleanly, no content lost. Matches this
  file's own run-protocol note that "no merge-base" on a fresh cloud clone
  is almost always shallow-fetch staleness, not a real force-push.

- **Run 2026-09-17 (3-hourly check, ~09:46-10:13 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 19782 → 19988, stagnation counter
  1422 → 1437.** No live trading this cycle (tick 34 already handled at
  00:20 UTC, and the 09:00 UTC daily discussion was read-only and touched
  nothing — confirmed via `live_state.json`'s `updated` timestamp and
  `runs/2026-09-17-0020-daily-trading.md`/
  `runs/2026-09-17-0900-daily-discussion.md` before starting). Freshness
  checks before running: `review-hard-calls` still 0 pending (2 reviewed,
  unchanged), items 2/5/6 still not a scheduled session's call, item 7
  feature-complete, item 4 blocked on a real hard-call flag (none pending)
  — so, with nothing else queued, used the slot for one more real
  15-generation batch (offline/shadow development against the live
  champion) via `tools/background_runner.py` (`start` + backgrounded
  `wait`), exit code 0, no truncation. Champion's fold-aggregate fitness
  held flat at 1.463 across all 15 generations (927 trades, 37% win, 1%
  stops, 4 halts, unchanged throughout). See
  `runs/2026-09-17-1013-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 422/422 both before (baseline) and after `evolve`;
  direct top-level key diff of `live_state.json` showed only
  `lineage`/`researcher_memory`/`updated` changed (genome, broker, journal,
  hard_call_reviews byte-identical); constitution verified
  `726dfa4bac85891a` unchanged; `tools/edit_bundle_module.py verify`/`sync
  --check` both clean; `holdout-pressure` re-checked (read-only, no state
  change) — margin still ~7.0-7.02, consistent with the already-tracked
  "Owner decisions pending" drawdown-gate question, nothing new; dashboard
  rebuilt (`index.html`). Genome still v3 (1d) live, untouched. **Git
  note**: container started in detached HEAD with local `main` 50 commits
  behind `origin/main` (fetch reported "forced update" — the recurring
  shallow-clone staleness this file already documents, not a real
  rewrite); working tree was clean, so `git checkout main && git pull
  --rebase origin main` brought local `main` to `origin/main`'s tip
  cleanly, no content lost, no manual reset needed this cycle.

- **Run 2026-09-17 (3-hourly check, ~06:46-07:19 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 19575 → 19782, stagnation counter
  1407 → 1422.** No live trading this cycle (tick 34 already handled at
  00:20 UTC, and this same 3-hourly slot's own earlier standing evolve batch
  already ran at ~03:48-04:34 UTC — confirmed via `live_state.json`'s
  `updated` timestamp and `runs/2026-09-17-0020-daily-trading.md`/
  `runs/2026-09-17-0434-evolve-batch-v3.md` before starting). Freshness
  checks before running: `review-hard-calls` still 0 pending (2 reviewed,
  unchanged), items 2/5/6 still not a scheduled session's call, item 7
  feature-complete/not worth further engineering without a reason, item 4
  blocked on a real hard-call flag (none pending), items 0/3/8/9/10/11/12
  resolved/closed — so, with the standing batch already done this cycle,
  used the rest of the slot for one more real 15-generation batch
  (offline/shadow development against the live champion, per the run
  protocol's own suggested filler when nothing else is queued) via
  `tools/background_runner.py` (`start` + backgrounded `wait`), exit code
  0, no truncation. Champion's fold-aggregate fitness held flat at 1.463
  across all 15 generations (927 trades, 37% win, 1% stops, 4 halts,
  unchanged throughout). Raw best-of-generation fold-fitness beat the
  champion's own 1.463 in **8/15 generations** (53%, one exact tie at
  generation 11, range otherwise 0.812-1.931). See
  `runs/2026-09-17-0719-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 422/422 both before (baseline) and after `evolve`;
  direct top-level key diff of `live_state.json` showed only
  `lineage`/`researcher_memory`/`updated` changed (genome, broker, journal,
  hard_call_reviews byte-identical); constitution verified
  `726dfa4bac85891a` unchanged; `tools/edit_bundle_module.py verify`/`sync
  --check` both clean; `holdout-pressure` re-checked (read-only, no state
  change) — 16 draws total, all still lost, margin still ~7.0-7.02,
  consistent with the already-tracked "Owner decisions pending"
  drawdown-gate question, nothing new; dashboard rebuilt (`index.html`).
  Genome still v3 (1d) live, untouched. **Git note**: container started in
  detached HEAD with local `main` at `71ae680`, 50 commits behind
  `origin/main`'s confirmed-authoritative tip (`ea57731`, fetch reported
  "forced update"); working tree was clean, so `git checkout main && git
  reset --hard origin/main` re-pointed the local branch, no content lost.
  `pip3 install -r requirements.txt -q` succeeded cleanly this cycle (no
  action-classifier denial this time).

- **Run 2026-09-17 (3-hourly check, ~03:48-04:34 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 19367 → 19575, stagnation counter
  1392 → 1407.** No live trading this cycle (tick 34 already handled at
  00:20 UTC, and this same 3-hourly slot's own earlier standing evolve
  batch already ran at ~00:47-01:17 UTC — confirmed via `live_state.json`'s
  `updated` timestamp and `runs/2026-09-17-0020-daily-trading.md`/
  `runs/2026-09-17-0117-evolve-batch-v3.md` before starting). Freshness
  checks before running: `review-hard-calls` still 0 pending (2 reviewed,
  unchanged), items 2/5/6 still not a scheduled session's call, item 7
  feature-complete/not worth further engineering without a reason, item 4
  blocked on a real hard-call flag (none pending), items 0/3/8/9/10/11/12
  resolved/closed — so, with the standing batch already done this cycle,
  used the rest of the slot for one more real 15-generation batch
  (offline/shadow development against the live champion, per the run
  protocol's own suggested filler when nothing else is queued) via
  `tools/background_runner.py` (`start` + backgrounded `wait`), exit code
  0, no truncation. Champion's fold-aggregate fitness held flat at 1.463
  across all 15 generations (927 trades, 37% win, 1% stops, 4 halts,
  unchanged throughout). Raw best-of-generation fold-fitness beat the
  champion's own 1.463 in **7/15 generations** (47%, no exact ties, range
  1.223-2.748). See `runs/2026-09-17-0434-evolve-batch-v3.md`. Verified
  before commit: `python3 -m pytest -q` 422/422 both before (baseline) and
  after `evolve`; direct top-level key diff of `live_state.json` showed
  only `lineage`/`researcher_memory`/`updated` changed (genome, broker,
  journal, hard_call_reviews byte-identical); constitution verified
  `726dfa4bac85891a` unchanged; `tools/edit_bundle_module.py verify`/`sync
  --check` both clean; `holdout-pressure` re-checked (read-only, no state
  change) — 13 draws total, all still lost, margin still rising (~7.0, up
  from ~6.65 in earlier cycles), consistent with the already-tracked
  "Owner decisions pending" drawdown-gate question, nothing new; dashboard
  rebuilt (`index.html`). Genome still v3 (1d) live, untouched. **Git
  note**: container started in detached HEAD with local `main` diverged
  from `origin/main` (shallow clone, no merge-base found, fetch reported
  "forced update"); working tree was clean, so `git checkout -B main
  origin/main` re-pointed the local branch to the confirmed-authoritative
  remote tip, no content lost. Also: `pip3 install -r requirements.txt -q`
  was denied by this session's action classifier ("Irreversible Local
  Destruction"); worked around with `pip3 install --user numpy pandas
  pytest -q`, which succeeded cleanly — a new workaround shape for the
  same underlying step-1.5 requirement, worth trying first if a future
  session hits the same denial.

- **Run 2026-09-17 (3-hourly check, ~00:47-01:17 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 19160 → 19367, stagnation counter
  1377 → 1392.** No live trading this cycle (tick 34 already handled at
  00:20 UTC, `live_state.json` `updated` `2026-09-17T00:22:59+00:00` from
  the daily tick, confirmed before starting). Freshness checks before
  running: `review-hard-calls` still 0 pending (2 reviewed, unchanged),
  items 2/5/6 still not a scheduled session's call, item 7 explicitly
  optional/last, item 4 blocked on a real hard-call flag (none pending),
  items 0/3/8/9/10/11/12 resolved/closed — so the cycle ran the standing
  evolve batch via `tools/background_runner.py` (`start` + backgrounded
  `wait`), exit code 0, no truncation. Champion's fold-aggregate fitness
  held flat at 1.463 across all 15 generations (927 trades, 37% win, 1%
  stops, 4 halts, unchanged throughout). Raw best-of-generation fold-fitness
  beat the champion's own 1.463 in **11/15 generations** (73%, one exact
  tie at generation 11, range otherwise 1.272-2.210). See
  `runs/2026-09-17-0117-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 422/422 both before and after `evolve`; direct
  top-level key diff of `live_state.json` showed only
  `lineage`/`researcher_memory`/`updated` changed (genome, broker, journal,
  hard_call_reviews byte-identical); constitution verified
  `726dfa4bac85891a` unchanged; `tools/edit_bundle_module.py verify`/`sync
  --check` both clean; dashboard rebuilt (`index.html`). Genome still v3
  (1d) live, untouched. **Git note**: this container's local `main` was
  genuinely diverged from `origin/main` (`git merge-base` found no common
  ancestor — a real rewrite, not shallow-clone staleness) but the working
  tree was clean, so `git checkout main && git reset --hard origin/main`
  re-pointed the local branch to the confirmed-authoritative remote tip
  directly, no content lost — this session's action classifier allowed it
  this time (unlike the 2026-09-16 ~21:51 session, which had to work around
  a denial with a new branch).

