# AGENTS.md Current-state archive: 2026-09-18 00:48 to 2026-09-18 19:12 UTC

Archived 2026-09-24 (3-hourly check, ~21:47 UTC) to keep `AGENTS.md` under
the 256KB single-read limit that scheduled sessions' `Read` tool enforces —
the file had regrown to 255,429 bytes (approaching the 262,144-byte/256KB
threshold, with only about 6.7KB of margin left), continuing the same
recurring growth pattern the 2026-09-04, 2026-09-10, 2026-09-15, 2026-09-16,
2026-09-18, 2026-09-20, 2026-09-22, and 2026-09-24 rotations each hit in
turn. This file holds the next oldest slice of `AGENTS.md`'s "Current
state" dated-entry log, moved here **verbatim, byte-for-byte, newest
first (same order as the original)** — nothing reworded or summarized.
The live `AGENTS.md` keeps everything from 2026-09-18 ~19:12 UTC onward,
plus the full "Owner decisions pending", promotion-history, "Measured",
and "Rules" sections, which were never part of this rotation.
Read `AGENTS_ARCHIVE_2026-09-17.md` next, then
`AGENTS_ARCHIVE_2026-09-15_to_2026-09-16.md`, then
`AGENTS_ARCHIVE_2026-09-13_to_2026-09-14.md`, then
`AGENTS_ARCHIVE_2026-09-11_to_2026-09-12.md`, then
`AGENTS_ARCHIVE_2026-09-08_to_2026-09-10.md`, then
`AGENTS_ARCHIVE_2026-09-02_to_2026-09-08.md`, then
`AGENTS_ARCHIVE_2026-08-29_to_2026-09-02.md`, then
`AGENTS_ARCHIVE_2026-08-15_to_2026-08-29.md` for the full older history.

---

- **Run 2026-09-18 (3-hourly check, ~18:47-19:12 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 21898 → 22107, stagnation counter
  1575 → 1590.** No live trading this cycle (tick 35 already handled at
  00:20 UTC — confirmed via `live_state.json`'s `updated` timestamp,
  `2026-09-18T16:16:44+00:00` from the prior 3-hourly check's own evolve
  batch, and `runs/2026-09-18-0020-daily-trading.md` before starting).
  Freshness checks before running: `review-hard-calls` still 0 pending (2
  reviewed, unchanged), items 2/5/6 still not a scheduled session's call,
  item 7 feature-complete, item 4 blocked on a real hard-call flag (none
  pending), `AGENTS.md` size 250,925 bytes (under the 256KB rotation
  threshold) — so, with nothing else queued, used the slot for one more
  real 15-generation batch (offline/shadow development against the live
  champion) via `tools/background_runner.py` (`start` + backgrounded
  `wait`), exit code 0, no truncation. Champion's fold-aggregate fitness
  held flat at 1.858 across all 15 generations (970 trades, 41% win, 1%
  stops, 3 halts, unchanged throughout). Raw best-of-generation fold-fitness
  beat or tied the champion's own 1.858 in **6/15 generations** (40%: 3
  strict beats, 3 exact ties), range 1.497-2.057. See
  `runs/2026-09-18-1912-evolve-batch-v3.md`. Verified before commit: `python3
  -m pytest -q` 422/422 both before (baseline) and after `evolve`; direct
  top-level key diff of `live_state.json` showed only
  `lineage`/`researcher_memory`/`updated` changed (genome, broker, journal,
  hard_call_reviews byte-identical); constitution verified
  `726dfa4bac85891a` unchanged; `tools/edit_bundle_module.py verify`/`sync
  --check` both clean; `holdout-pressure` re-checked (read-only, no state
  change) — margin still rising slowly (last value 7.040), consistent with
  the already-tracked "Owner decisions pending" drawdown-gate question,
  nothing new; dashboard rebuilt (`index.html`). Genome still v3 (1d) live,
  untouched. **Git note**: container started in detached HEAD with local
  `main` matching `origin/main`'s tip exactly (`723e6a8`, `git fetch`
  reported "forced update" but no actual divergence); `git checkout -B main
  origin/main` re-pointed the local branch cleanly, no content lost, no
  reset needed this cycle.

- **Run 2026-09-18 (3-hourly check, ~15:47-16:19 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 21691 → 21898, stagnation counter
  1561 → 1575.** No live trading this cycle (tick 35 already handled at
  00:20 UTC — confirmed via `live_state.json`'s `updated` timestamp,
  `2026-09-18T13:12:04+00:00` from the prior 3-hourly check's own evolve
  batch, and `runs/2026-09-18-0020-daily-trading.md` before starting).
  Freshness checks before running: `review-hard-calls` still 0 pending (2
  reviewed, unchanged), items 2/5/6 still not a scheduled session's call,
  item 7 feature-complete, item 4 blocked on a real hard-call flag (none
  pending), `AGENTS.md` size 247,916 bytes (under the 256KB rotation
  threshold) — so, with nothing else queued, used the slot for one more
  real 15-generation batch (offline/shadow development against the live
  champion) via `tools/background_runner.py` (`start` + backgrounded
  `wait`), exit code 0, no truncation. Champion's fold-aggregate fitness
  held flat at 1.858 across all 15 generations (970 trades, 41% win, 1%
  stops, 3 halts, unchanged throughout). Raw best-of-generation fold-fitness
  ranged 1.321-1.928, never clearing the promotion bar. See
  `runs/2026-09-18-1619-evolve-batch-v3.md`. Verified before commit: `python3
  -m pytest -q` 422/422 both before (baseline) and after `evolve`; direct
  top-level key diff of `live_state.json` showed only
  `lineage`/`researcher_memory`/`updated` changed (genome, broker, journal,
  hard_call_reviews byte-identical); constitution verified
  `726dfa4bac85891a` unchanged; `tools/edit_bundle_module.py verify`/`sync
  --check` both clean; `holdout-pressure` re-checked (read-only, no state
  change) — margin still rising slowly (~7.03-7.04), consistent with the
  already-tracked "Owner decisions pending" drawdown-gate question, nothing
  new; dashboard rebuilt (`index.html`). Genome still v3 (1d) live,
  untouched. **Git note**: container started in detached HEAD with local
  `main` exactly matching `origin/main`'s tip (`12cd252`, `git fetch`
  reported "forced update" but no actual divergence); `git checkout main`
  then showed the local `main` branch *ref* itself ~50 commits stale
  (pointing at an old `71ae680`-rooted history superseded by upstream's
  rewrite) even though the already-checked-out working tree matched
  `origin/main` exactly — `git reset --hard origin/main` re-pointed the
  branch cleanly, no content lost. Also: `tools/background_runner.py wait`
  first called with an unsupported `--pid` flag failed argument parsing but
  still exited 0 (usage text printed, no real wait performed) — caught by
  `kill -0 <pid>` showing the evolve process still alive, then re-run with
  only supported flags, which waited correctly. New lesson: check
  `background_runner.py wait`'s stdout for an argument error, not just its
  exit code, before trusting that it actually blocked.

- **Run 2026-09-18 (3-hourly check, ~12:47-13:15 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 21483 → 21691, stagnation counter
  1545 → 1561.** No live trading this cycle (tick 35 already handled at
  00:20 UTC — confirmed via `live_state.json`'s `updated` timestamp,
  `2026-09-18T10:18:54+00:00` from the prior 3-hourly check's own evolve
  batch, and `runs/2026-09-18-0020-daily-trading.md` before starting).
  Freshness checks before running: `review-hard-calls` still 0 pending (2
  reviewed, unchanged), items 2/5/6 still not a scheduled session's call,
  item 7 feature-complete, item 4 blocked on a real hard-call flag (none
  pending), `AGENTS.md` size 244,990 bytes (under the 256KB rotation
  threshold) — so, with nothing else queued, used the slot for one more
  real 15-generation batch (offline/shadow development against the live
  champion) via `tools/background_runner.py` (`start` + backgrounded
  `wait`), exit code 0, no truncation. Champion's fold-aggregate fitness
  held flat at 1.858 across all 15 generations (970 trades, 41% win, 1%
  stops, 3 halts, unchanged throughout). Raw best-of-generation fold-fitness
  ranged 1.330-2.554, never clearing the promotion bar. See
  `runs/2026-09-18-1315-evolve-batch-v3.md`. Verified before commit: `python3
  -m pytest -q` 422/422 both before (baseline) and after `evolve`; direct
  top-level key diff of `live_state.json` showed only
  `lineage`/`researcher_memory`/`updated` changed (genome, broker, journal,
  hard_call_reviews byte-identical); constitution verified
  `726dfa4bac85891a` unchanged; `tools/edit_bundle_module.py verify`/`sync
  --check` both clean; `holdout-pressure` re-checked (read-only, no state
  change) — margin still rising slowly (~7.02-7.04), consistent with the
  already-tracked "Owner decisions pending" drawdown-gate question, nothing
  new; dashboard rebuilt (`index.html`). Genome still v3 (1d) live,
  untouched. **Git note**: container started in detached HEAD with local
  `main` ~50 commits behind `origin/main` (fetch reported "forced update" —
  the recurring shallow-clone staleness this file already documents, not a
  real rewrite); working tree was clean, so `git checkout main && git pull
  --rebase origin main` brought local `main` to `origin/main`'s tip cleanly,
  no content lost. Also: a verification-step `python3 -m pytest -q > log
  2>&1 &` wrapped inside a tool-level `run_in_background: true` call hit the
  exact item 9 anti-pattern (tool reported "completed" almost instantly
  while the real pytest process kept running detached ~2 more minutes) —
  caught by polling `kill -0 <pid>` directly rather than trusting the tool's
  completion signal; worth remembering that item 9's concern applies to any
  ad hoc `command > log 2>&1 &` inside `run_in_background: true`, not just
  `evolve`.

- **Run 2026-09-18 (3-hourly check, ~09:48-10:21 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 21276 → 21483, stagnation/boldness
  counter 1530 → 1545.** No live trading this cycle (tick 35 already handled
  at 00:20 UTC — confirmed via `live_state.json`'s `updated` timestamp,
  `2026-09-18T07:19:41+00:00` from the prior 3-hourly check's own evolve
  batch, and `runs/2026-09-18-0020-daily-trading.md` before starting).
  Freshness checks before running: `review-hard-calls` still 0 pending (2
  reviewed, unchanged), items 2/5/6 still not a scheduled session's call,
  item 7 feature-complete, item 4 blocked on a real hard-call flag (none
  pending) — so, with nothing else queued, used the slot for one more real
  15-generation batch (offline/shadow development against the live
  champion) via `tools/background_runner.py` (`start` + backgrounded
  `wait`), exit code 0, no truncation. Champion's fold-aggregate fitness
  held flat at 1.858 across all 15 generations (970 trades, 41% win, 1%
  stops, 3 halts, unchanged throughout). Raw best-of-generation fold-fitness
  beat or tied the champion's own 1.858 in **5/15 generations** (33%: 4
  strict beats, 1 exact tie). See
  `runs/2026-09-18-1021-evolve-batch-v3.md`. Verified before commit: `python3
  -m pytest -q` 422/422 both before (baseline) and after `evolve`; direct
  top-level key diff of `live_state.json` showed only
  `lineage`/`researcher_memory`/`updated` changed (genome, broker, journal,
  hard_call_reviews byte-identical); constitution verified
  `726dfa4bac85891a` unchanged; `tools/edit_bundle_module.py verify`/`sync
  --check` both clean; dashboard rebuilt (`index.html`). Genome still v3
  (1d) live, untouched. **Git note**: container started in detached HEAD
  with local `main` at `1c4fbff`, matching `origin/main`'s tip exactly
  (`git fetch` reported a "forced update" but `git log` on both refs showed
  identical history at that commit — no actual divergence this cycle); `git
  checkout main && git reset --hard origin/main` re-pointed the local
  branch cleanly, no content lost. Also: plain `pip3 install -r
  requirements.txt -q` timed out twice against `files.pythonhosted.org`;
  `pip3 install --user -r requirements.txt -q --timeout 60 --retries 5`
  worked cleanly — a new workaround shape for the same recurring step-1.5
  flake this file already documents multiple fixes for.

- **Run 2026-09-18 (3-hourly check, ~06:47-07:30 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 21068 → 21276, stagnation/boldness
  counter 1515 → 1530.** No live trading this cycle (tick 35 already handled
  at 00:20 UTC — confirmed via `live_state.json`'s `updated` timestamp and
  `runs/2026-09-18-0020-daily-trading.md` before starting). Freshness checks
  before running: `review-hard-calls` still 0 pending (2 reviewed,
  unchanged), items 2/5/6 still not a scheduled session's call, item 7
  feature-complete, item 4 blocked on a real hard-call flag (none pending),
  items 9-12 resolved — so, with nothing else queued, used the slot for one
  more real 15-generation batch (offline/shadow development against the live
  champion) via `tools/background_runner.py` (`start` + backgrounded
  `wait`), exit code 0, no truncation. Champion's fold-aggregate fitness
  held flat at 1.858 across all 15 generations (970 trades, 41% win, 1%
  stops, 3 halts, unchanged throughout). Raw best-of-generation fold-fitness
  beat or tied the champion's own 1.858 in **8/15 generations** (53%: 5
  strict beats, 3 exact ties). See
  `runs/2026-09-18-0730-evolve-batch-v3.md`. Verified before commit: `python3
  -m pytest -q` 422/422 both before (baseline) and after `evolve`; direct
  top-level key diff of `live_state.json` showed only
  `lineage`/`researcher_memory`/`updated` changed (genome, broker, journal,
  hard_call_reviews byte-identical); constitution verified
  `726dfa4bac85891a` unchanged; `tools/edit_bundle_module.py verify`/`sync
  --check` both clean; dashboard rebuilt (`index.html`). Genome still v3
  (1d) live, untouched. **Git note**: container started in detached HEAD
  with local `main` stale (~50 commits behind `origin/main`, reported as
  diverged/"forced update" — the recurring shallow-clone staleness this file
  already documents, not a real rewrite); working tree was clean, so `git
  checkout main && git reset --hard origin/main` re-pointed the local branch
  to the confirmed-authoritative remote tip, no content lost.

- **Run 2026-09-18 (3-hourly check, ~00:48-01:13 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 20859 → 21068, stagnation/boldness
  counter 1500 → 1515.** No live trading this cycle (tick 35 already handled
  at 00:20 UTC, including its own tick-35 `evolve 3` — confirmed via
  `live_state.json`'s `updated` timestamp and
  `runs/2026-09-18-0020-daily-trading.md` before starting). Freshness checks
  before running: `review-hard-calls` still 0 pending (2 reviewed,
  unchanged), items 2/5/6 still not a scheduled session's call, item 7
  feature-complete, item 4 blocked on a real hard-call flag (none pending),
  items 9-12 resolved — so, with nothing else queued, used the slot for one
  more real 15-generation batch (offline/shadow development against the live
  champion) via `tools/background_runner.py` (`start` + backgrounded
  `wait`), exit code 0, no truncation. Champion's fold-aggregate fitness held
  flat at 1.858 across all 15 generations (970 trades, 41% win, 1% stops, 3
  halts, unchanged throughout). Raw best-of-generation fold-fitness beat or
  tied the champion's own 1.858 in **6/15 generations** (40%: 3 strict beats
  at 1.860/1.860/2.099, 3 exact ties). See
  `runs/2026-09-18-0113-evolve-batch-v3.md`. Verified before commit: `python3
  -m pytest -q` 422/422 both before (baseline) and after `evolve`; direct
  top-level key diff of `live_state.json` showed only
  `lineage`/`researcher_memory`/`updated` changed (genome, broker, journal,
  hard_call_reviews byte-identical); constitution verified
  `726dfa4bac85891a` unchanged; `tools/edit_bundle_module.py verify`/`sync
  --check` both clean; dashboard rebuilt (`index.html`). Genome still v3
  (1d) live, untouched. **Git note**: container started in detached HEAD
  with local `main` stale (~50 commits behind `origin/main`, reported as
  diverged/"forced update" — the recurring shallow-clone staleness this file
  already documents, not a real rewrite); `tools/git_sync.py` fast-forwarded
  cleanly (`71ae680..3ba1ff7`), no content lost.
