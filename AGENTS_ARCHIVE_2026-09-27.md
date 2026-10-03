# AGENTS.md archive — 2026-09-27

Chronological slice of AGENTS.md's "Current state" log archived verbatim
on 2026-10-03 (3-hourly check) to keep the live file under its 256KB
single-read limit. Nothing reworded, nothing lost. See AGENTS.md for the
full index of archives and everything from 2026-09-28 onward.

---

- **Run 2026-09-27 (3-hourly check, ~21:47-22:16 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 36866 → 37073 (per
  `researcher_memory.tested`), stagnation/boldness counter 2658 → 2673.** No
  live trading this cycle (tick 44 already handled at the dedicated 00:20
  UTC daily slot, and the prior 3-hourly check's own evolve batch already
  ran at ~18:46-19:19 UTC — confirmed via `live_state.json`'s `updated`
  timestamp at session start, `2026-09-27T19:19:09+00:00`, matching
  `runs/2026-09-27-1919-evolve-batch-v3.md`). Freshness checks before
  running: `review-hard-calls` still 0 pending (4 reviewed, unchanged),
  items 6/13 still owner decisions, `AGENTS.md` size 229,934 bytes —
  comfortably under the 256KB threshold — so, with nothing else queued,
  used the slot for one more real 15-generation batch via
  `tools/background_runner.py` (`start` + separate `wait`), exit code 0, no
  truncation, ~29 minutes. Champion's fold-aggregate fitness held flat at
  1.850 across all 15 generations (962 trades, 38% win, 1% stops, 4 halts,
  unchanged throughout). Best-of-generation fold-fitness ranged 1.850-2.407,
  never clearing the promotion-margin bar. See
  `runs/2026-09-27-2216-evolve-batch-v3.md`. Verified before commit: `python3
  -m pytest -q` 441/441 both before (baseline) and after `evolve`; top-level
  key diff of `live_state.json` (checked directly in Python against `git
  show HEAD:live_state.json`, not just eyeballed) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  `holdout-pressure` re-checked (read-only, no state change) — margin rose
  slightly (7.217, was 7.213) at draw 672, same slow-rise pattern already
  tracked under item 13, nothing new; dashboard rebuilt with `EVO_STATE` set
  (`index.html` shows 37073 challenger ideas tried). Genome still v3 (1d)
  live, untouched. Container arrived on `main`, 22 commits behind
  `origin/main` in detached HEAD; `git checkout main` plus
  `tools/git_sync.py` fast-forwarded cleanly, nothing lost.

- **Run 2026-09-27 (3-hourly check, ~18:46-19:19 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 36661 → 36866 (per
  `researcher_memory.tested`), stagnation/boldness counter 2644 → 2658.** No
  live trading this cycle (tick 44 already handled at the dedicated 00:20
  UTC daily slot, and the prior 3-hourly check's own evolve batch already
  ran at ~15:46-16:15 UTC — confirmed via `live_state.json`'s `updated`
  timestamp at session start, `2026-09-27T16:12:53+00:00`, matching
  `runs/2026-09-27-1615-evolve-batch-v3.md`). Freshness checks before
  running: `review-hard-calls` still 0 pending (4 reviewed, unchanged),
  items 6/13 still owner decisions, `AGENTS.md` size 227,626 bytes —
  comfortably under the 256KB threshold — so, with nothing else queued,
  used the slot for one more real 15-generation batch via
  `tools/background_runner.py` (`start` + separate `wait`), exit code 0, no
  truncation, ~26 minutes. Champion's fold-aggregate fitness held flat at
  1.850 across all 15 generations (962 trades, 38% win, 1% stops, 4 halts,
  unchanged throughout). Best-of-generation fold-fitness ranged 1.395-2.955,
  never clearing the promotion-margin bar. See
  `runs/2026-09-27-1919-evolve-batch-v3.md`. Verified before commit: `python3
  -m pytest -q` 441/441 both before (baseline) and after `evolve`; top-level
  key diff of `live_state.json` (checked directly in Python against `git
  show HEAD:live_state.json`, not just eyeballed) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  `holdout-pressure` re-checked (read-only, no state change) — margin rose
  slightly (7.213, was 7.213) at draw 669, same slow-rise pattern already
  tracked under item 13, nothing new; dashboard rebuilt with `EVO_STATE` set
  (`index.html` shows 36866 challenger ideas tried). Genome still v3 (1d)
  live, untouched. Container arrived on `main`, up to date with
  `origin/main` after a clean fast-forward pull, no divergence, no
  shallow-clone staleness this cycle.

- **Run 2026-09-27 (3-hourly check, ~15:46-16:15 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 36452 → 36661 (per
  `researcher_memory.tested`), stagnation/boldness counter 2629 → 2644.** No
  live trading this cycle (tick 44 already handled at the dedicated 00:20
  UTC daily slot, and the prior 3-hourly check's own evolve batch already
  ran at ~12:47-13:18 UTC — confirmed via `live_state.json`'s `updated`
  timestamp at session start, `2026-09-27T13:15:25+00:00`, matching
  `runs/2026-09-27-1318-evolve-batch-v3.md`). Freshness checks before
  running: `review-hard-calls` still 0 pending (4 reviewed, unchanged),
  items 6/13 still owner decisions, `AGENTS.md` size 225,206 bytes —
  comfortably under the 256KB threshold — so, with nothing else queued,
  used the slot for one more real 15-generation batch via
  `tools/background_runner.py` (`start` + separate `wait`), exit code 0, no
  truncation, ~26 minutes. Champion's fold-aggregate fitness held flat at
  1.850 across all 15 generations (962 trades, 38% win, 1% stops, 4 halts,
  unchanged throughout). Best-of-generation fold-fitness ranged 1.606-2.955,
  never clearing the promotion-margin bar. See
  `runs/2026-09-27-1615-evolve-batch-v3.md`. Verified before commit: `python3
  -m pytest -q` 441/441 both before (baseline) and after `evolve`; top-level
  key diff of `live_state.json` (checked directly in Python against a
  pre-batch snapshot, not just eyeballed) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  `holdout-pressure` re-checked (read-only, no state change) — margin rose
  slightly (7.213, was 7.211) at draw 668, same slow-rise pattern already
  tracked under item 13, nothing new; dashboard rebuilt with `EVO_STATE` set
  (`index.html` shows 36661 challenger ideas tried). Genome still v3 (1d)
  live, untouched. Container arrived on `main`, up to date with
  `origin/main` after a clean fast-forward pull (20 commits landed since
  this container's last checkpoint, all from other scheduled sessions
  throughout 2026-09-26/27, no divergence, no shallow-clone staleness this
  cycle).

- **Run 2026-09-27 (3-hourly check, ~12:47-13:18 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 36244 → 36452 (per
  `researcher_memory.tested`), stagnation/boldness counter 2614 → 2629.** No
  live trading this cycle (tick 44 already handled at the dedicated 00:20
  UTC daily slot, and the prior 3-hourly check's own evolve batch already
  ran at ~09:47-09:54 UTC — confirmed via `live_state.json`'s `updated`
  timestamp at session start, `2026-09-27T10:32:11+00:00`, matching
  `runs/2026-09-27-0954-evolve-batch-v3.md`). Freshness checks before
  running: `review-hard-calls` still 0 pending (4 reviewed, unchanged),
  items 6/13 still owner decisions, `AGENTS.md` size 222,786 bytes —
  comfortably under the 256KB threshold — so, with nothing else queued,
  used the slot for one more real 15-generation batch via
  `tools/background_runner.py` (`start` + separate `wait`), exit code 0, no
  truncation, ~27 minutes. Champion's fold-aggregate fitness held flat at
  1.850 across all 15 generations (962 trades, 38% win, 1% stops, 4 halts,
  unchanged throughout). Best-of-generation fold-fitness ranged 1.664-2.085,
  never clearing the promotion-margin bar. See
  `runs/2026-09-27-1318-evolve-batch-v3.md`. Verified before commit: `python3
  -m pytest -q` 441/441 both before (baseline) and after `evolve`; top-level
  key diff of `live_state.json` (checked directly in Python against a
  pre-batch snapshot, not just eyeballed) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  `holdout-pressure` re-checked (read-only, no state change) — margin rose
  slightly (7.211, was 7.210) at draw 665, same slow-rise pattern already
  tracked under item 13, nothing new; dashboard rebuilt with `EVO_STATE` set
  (`index.html` shows 36452 challenger ideas tried). Genome still v3 (1d)
  live, untouched. Container arrived on `main`, up to date with
  `origin/main` after a clean fast-forward pull (19 commits landed since
  this container's last checkpoint, all from other scheduled sessions
  throughout 2026-09-26/27, no divergence, no shallow-clone staleness this
  cycle).

- **Run 2026-09-27 (3-hourly check, ~09:47-09:54 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 36035 → 36244 (per
  `researcher_memory.tested`), stagnation/boldness counter 2599 → 2613.** No
  live trading this cycle (tick 44 already handled at the dedicated 00:20
  UTC daily slot, and the prior 3-hourly check's own evolve batch already
  ran at ~06:47-07:15 UTC — confirmed via `live_state.json`'s `updated`
  timestamp at session start, `2026-09-27T07:10:57+00:00`, matching
  `runs/2026-09-27-0715-evolve-batch-v3.md`; the intervening weekend
  all-hands session's own concurrent-batch race is described in the entry
  directly below and didn't touch state). Freshness checks before running:
  `review-hard-calls` still 0 pending (4 reviewed, unchanged), items 6/13
  still owner decisions, `AGENTS.md` size 220,372 bytes — comfortably under
  the 256KB threshold — so, with nothing else queued, used the slot for one
  more real 15-generation batch via `tools/background_runner.py` (`start` +
  separate `wait`), exit code 0, no truncation, ~40 minutes. Champion's
  fold-aggregate fitness held flat at 1.850 across all 15 generations (962
  trades, 38% win, 1% stops, 4 halts, unchanged throughout). Best-of-generation
  fold-fitness ranged 1.607-2.274, never clearing the promotion-margin bar.
  See `runs/2026-09-27-0954-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 441/441 both before (baseline) and after `evolve`;
  top-level key diff of `live_state.json` (checked directly in Python
  against the pre-batch snapshot, not just eyeballed) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  `holdout-pressure` re-checked (read-only, no state change) — margin rose
  slightly (7.210, was 7.208) at draw 664, same slow-rise pattern already
  tracked under item 13, nothing new; dashboard rebuilt with `EVO_STATE` set
  (`index.html` shows 36244 challenger ideas tried). Genome still v3 (1d)
  live, untouched. Container arrived on `main`, up to date with
  `origin/main`; `tools/git_sync.py` confirmed fast-forward/no-op, nothing
  lost.

- **Run 2026-09-27 (weekend all-hands, ~07:20-07:50 UTC): a second real
  30-generation `evolve` batch against the live v3 champion, run
  concurrently with the 3-hourly check's own 15-generation batch below —
  lost the push race, no state persisted, no harm.** Both batches started
  from the same base (`abbf182`, tested=35830) at roughly the same time;
  the 3-hourly check's commit (`0ddb6b3`, tested 35830→36035) reached
  `origin/main` first. `git push` for this session's own batch
  (tested 35830→36248 in isolation) was rejected as non-fast-forward;
  `git pull --rebase` produced real content conflicts in `live_state.json`
  itself (not the usual shallow-clone staleness `tools/git_sync.py`
  handles — this was two independently-advanced copies of the same live
  JSON state, which can't be textually merged), so per the run protocol's
  own "never force-push, never discard uncommitted work without checking"
  discipline: aborted the rebase, confirmed the only at-risk content was
  this session's own now-superseded evolve-batch commit (no source code,
  only `live_state.json`/`index.html`/doc updates describing a state that
  had already lost the race), and `git reset --hard origin/main` to adopt
  the already-canonical, already-verified state instead of hand-splicing
  two divergent `researcher_memory.tested` lists. Nothing lost: this
  session's batch found no promotion either (same as the one that won the
  race), so the only cost was ~65 minutes of redundant compute, not lost
  search progress or lost account state. Flagging here since this is the
  first time two sessions have raced on a real `live_state.json` write
  (not just git history) closely enough to actually collide — future
  sessions hitting the same rejected-push-with-real-JSON-conflicts pattern
  (as opposed to the shallow-clone-staleness pattern `git_sync.py` already
  handles) should recognize it as "someone else advanced the same file
  concurrently, adopt their state rather than hand-merge JSON" rather than
  assuming something is broken.

- **Run 2026-09-27 (3-hourly check, ~06:47-07:15 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 35830 → 36035 (per
  `researcher_memory.tested`), stagnation/boldness counter 2584 → 2599.** No
  live trading this cycle (tick 44 already handled at the dedicated 00:20
  UTC daily slot, and the prior 3-hourly check's own evolve batch already
  ran at ~03:46-04:14 UTC — confirmed via `live_state.json`'s `updated`
  timestamp at session start, `2026-09-27T04:11:51+00:00`, matching
  `runs/2026-09-27-0414-evolve-batch-v3.md`; the intervening weekend
  all-hands session, `runs/2026-09-27-0600-weekend-all-hands.md`, shipped
  the `regime-conditional-short` diagnostic and measured it against the
  live champion but never touched `live_state.json`). Freshness checks
  before running: `review-hard-calls` still 0 pending (4 reviewed,
  unchanged), items 6/13 still owner decisions, `AGENTS.md` size 215,718
  bytes — comfortably under the 256KB threshold — so, with nothing else
  queued, used the slot for one more real 15-generation batch via
  `tools/background_runner.py` (`start` + separate `wait`), exit code 0, no
  truncation, ~21.3 minutes. Champion's fold-aggregate fitness held flat at
  1.850 across all 15 generations (962 trades, 38% win, 1% stops, 4 halts,
  unchanged throughout). Best-of-generation fold-fitness ranged 1.332-2.378,
  never clearing the promotion-margin bar. See
  `runs/2026-09-27-0715-evolve-batch-v3.md`. Verified before commit: `python3
  -m pytest -q` 441/441 both before (baseline) and after `evolve`; top-level
  key diff of `live_state.json` (checked directly in Python against `git
  show HEAD:live_state.json`, not just eyeballed) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  `holdout-pressure` re-checked (read-only, no state change) — margin rose
  slightly (7.208, was 7.206) at draw 662, same slow-rise pattern already
  tracked under item 13, nothing new; dashboard rebuilt with `EVO_STATE` set
  (`index.html` shows 36035 challenger ideas tried). Genome still v3 (1d)
  live, untouched. Container arrived on `main`, one commit behind
  `origin/main` in detached HEAD (the weekend all-hands session's own
  commit); `git checkout main` plus `tools/git_sync.py` fast-forwarded
  cleanly, nothing lost.

- **Run 2026-09-27 (weekend all-hands, ~06:00-07:15 UTC): shipped
  `benchmark_regime_conditional_short` and tested the first real
  regime-conditional short design against the live v3 champion — and it
  loses.** Picked this over another `evolve` batch because it's the
  concretely-scoped next step the 2026-09-26 weekend session's own
  `short-headroom` finding left open ("a permanent short overlay is
  reckless 3 windows out of 4; a regime-conditional entry signal is the
  open question") and, per this repo's own "measure before building"
  culture (item 3's correlation-penalty saga), the natural first thing to
  measure is the simplest possible construction: gate the short on the
  regime classifier that already exists live, before designing anything
  new. New `loop.engine.benchmark_regime_conditional_short` opens/closes
  an equal-weight short bar-by-bar, gated on `agents.analyst.Analyst._regime`
  — the exact causal, per-bar signal `RiskJudge.rule`'s `regime_scale` gene
  already uses to gate long entries, called the same way `Council.tick`
  does — instead of holding a static position for the whole window. 8 new
  tests (`tests/test_regime_conditional_short.py`), full suite 434 → 441
  passed both before and after. New CLI flag `short-headroom
  --regime-conditional [--short-regimes bear,crisis|crisis|bear]`.

  Result: gating on `bear,crisis` (mirroring `regime_scale`'s own gate) is
  **worse than the always-on short in all four real windows, including the
  one real bear window** — fold 3's zero-cost return is −5.6% under this
  gating vs. the permanent short's +38.5% zero-cost in the same window,
  because `_regime`'s `bear` leg (`anchor_score < -0.03 OR breadth < 0.30`)
  fires on ordinary pullbacks inside intact trends, not just real declines,
  and flips 12-17 times a window. Narrowing to `--short-regimes crisis`
  (the classifier's strict AND-gated leg) fixes the false-positive problem
  (zero bars short in either bull fold) and fold 3 turns zero-cost-positive
  (+4.2%, capturing +8% of the theoretical edge) — but that's a small
  fraction of the always-on short's +68% captured in the same window, for
  being short only 13 of 414 bars. See item 5 in "Next steps" for the full
  numbers and reasoning. **Reading: the existing long-entry regime signal
  is not a usable short-timing signal at either threshold** — this rules
  out the cheapest version of "just add regime-gating" the same way
  2026-09-26's result ruled out "just add a permanent short", and sharpens
  what a real design would need (a purpose-built short-timing signal, not
  a reuse of the long-side gate) rather than answering whether to build it.
  Nothing here changes live behavior: read-only, genome-unmutated, no
  `RiskJudge`/`SuperiorJudge` code path touched. Verified before commit:
  `python3 -m pytest -q` 441/441 both before and after;
  `tools/edit_bundle_module.py sync --check`/`verify` both clean;
  `evotrader.manifest` unchanged (`726dfa4bac85891a` — only `loop/engine.py`
  and `evotrader_bundle.py`'s own CLI dispatch section changed, neither
  checksummed); `live_state.json` untouched throughout. Container arrived
  detached HEAD 14 commits behind `origin/main`; `git checkout main` plus
  `tools/git_sync.py` fast-forwarded cleanly, nothing lost.

- **Run 2026-09-27 (3-hourly check, ~03:46-04:14 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 35623 → 35830 (per
  `researcher_memory.tested`), stagnation/boldness counter 2568 → 2584.** No
  live trading this cycle (tick 44 already handled at the dedicated 00:20
  UTC daily slot, and the prior 3-hourly check's own evolve batch already
  ran at ~00:46-01:19 UTC — confirmed via `live_state.json`'s `updated`
  timestamp at session start, `2026-09-27T01:16:59+00:00`, matching
  `runs/2026-09-27-0119-evolve-batch-v3.md`). Freshness checks before
  running: `review-hard-calls` still 0 pending (4 reviewed, unchanged),
  items 6/13 still owner decisions, `AGENTS.md` size 243,987 bytes —
  comfortably under the 256KB threshold — so, with nothing else queued,
  used the slot for one more real 15-generation batch via
  `tools/background_runner.py` (`start` + separate `wait`), exit code 0, no
  truncation, ~22.4 minutes. Champion's fold-aggregate fitness held flat at
  1.850 across all 15 generations (962 trades, 38% win, 1% stops, 4 halts,
  unchanged throughout). Best-of-generation fold-fitness ranged 1.547-2.203,
  never clearing the promotion-margin bar. See
  `runs/2026-09-27-0414-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 434/434 both before (baseline) and after `evolve`;
  top-level key diff of `live_state.json` (checked directly in Python
  against `git show HEAD:live_state.json`, not just eyeballed) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  `holdout-pressure` re-checked (read-only, no state change) — margin
  unchanged at 7.208, draw 661 (this batch's candidates never cleared the
  fold-aggregate gate, so no new holdout draws), same slow-rise pattern
  already tracked under item 13, nothing new; dashboard rebuilt with
  `EVO_STATE` set (`index.html` shows 35830 challenger ideas tried). Genome
  still v3 (1d) live, untouched. Container arrived detached HEAD 13 commits
  behind `origin/main`; `git checkout main` plus `tools/git_sync.py`
  fast-forwarded cleanly, nothing lost.

- **Run 2026-09-27 (3-hourly check, ~00:46-01:19 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 35418 → 35623 (per
  `researcher_memory.tested`), stagnation/boldness counter 2553 → 2568.** No
  live trading this cycle (tick 44 already handled at the dedicated 00:20
  UTC daily slot, `44 % 7 == 2` so no `evolve` ran as part of that tick —
  confirmed via `live_state.json`'s `updated` timestamp at session start,
  `2026-09-27T00:22:21+00:00`, matching `runs/2026-09-27-0020-daily-trading.md`).
  Freshness checks before running: `review-hard-calls` still 0 pending (4
  reviewed, unchanged), items 6/13 still owner decisions, `AGENTS.md` size
  241,707 bytes — comfortably under the 256KB threshold — so, with nothing
  else queued, used the slot for one more real 15-generation batch via
  `tools/background_runner.py` (`start` + separate `wait`), exit code 0, no
  truncation, ~28 minutes. Champion's fold-aggregate fitness held flat at
  1.850 across all 15 generations (962 trades, 38% win, 1% stops, 4 halts,
  unchanged throughout). Best-of-generation fold-fitness ranged 0.637-2.453,
  never clearing the promotion-margin bar. See
  `runs/2026-09-27-0119-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 434/434 both before (baseline) and after `evolve`;
  top-level key diff of `live_state.json` (checked directly in Python
  against `git show HEAD:live_state.json`, not just eyeballed) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  `holdout-pressure` re-checked (read-only, no state change) — margin rose
  slightly (7.208, was 7.206) at draw 661, same slow-rise pattern already
  tracked under item 13, nothing new; dashboard rebuilt with `EVO_STATE` set
  (`index.html` shows 35623 challenger ideas tried). Genome still v3 (1d)
  live, untouched. Container arrived detached HEAD 12 commits behind
  `origin/main`; `git checkout main` plus `tools/git_sync.py` fast-forwarded
  cleanly, nothing lost.
