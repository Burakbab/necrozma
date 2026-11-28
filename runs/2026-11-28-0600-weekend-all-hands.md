# Weekend all-hands, 2026-11-28 (~06:00-07:03 UTC)

## Context at session start

Container synced cleanly from `main` via `git checkout main` + `python3
tools/git_sync.py` (fast-forward, no divergence, no shallow-clone
staleness). `AGENTS.md` was 242,594 bytes at session start — comfortably
under the ~250-256KB range that has triggered archival in recent cycles,
so no archival this session.

Reviewed "Current state" and "Next steps" before picking work. Status of
the open structural items:

- **Item 5 (short selling)**: the 2026-11-08 vol-expansion result closed
  out the third independently-constructed confirmation dimension (temporal,
  cross-sectional, volatility-character) tried against trend-break's entry,
  all three showing the same shape — an apparent in-sample sweet spot that
  fails or only partially survives an out-of-sample check, and none ever
  profiting in a real severe crash. That write-up's own recommendation is
  explicit: "further search inside this same family... is unlikely to be
  the highest-value use of a future session's time... A different kind of
  input... would be needed... not another sweep of another scalar threshold
  on the same data." This repo has no measured crypto borrow rate, no
  on-chain data, and no credentials mechanism to get one (by design — see
  "No credentials, anywhere" in `AGENTS.md`), so that different-kind-of-input
  bar isn't reachable this session. Did not pick this item back up.
- **Item 13 (HOLDOUT_SIGMA calibration)**: explicitly the owner's risk-appetite
  call, not a scheduled session's to decide, and the 2026-11-22 re-check
  already confirmed the diagnosis holds at 5x higher stagnation. No new
  evidence to gather here without re-litigating a closed question.
- **Item 6 (equities/FX)**: blocked on an owner decision (data source).
- **Item 2 (4h-bar shadow evolution)**: parked by owner decision.
- Items 3, 8, 9, 10, 11, 12: closed/resolved, nothing to act on.
- **Item 4 (hard-call reviews)**: checked `review-hard-calls` — 0 pending
  (6 reviewed so far, same as last check). Nothing new to review.
- **Item 0 (fitness-vs-excess-return)**: `live-benchmark` is "recommended,
  not mandated" to run as routine on weekend sessions per the 2026-11-21
  entry, and it had been exactly 7 days since that last run — good timing
  to re-check.

Given essentially every open structural item is either blocked on the
owner, parked, or has run into a wall its own write-up already diagnosed,
this session's highest-value use of the deeper weekend time budget was the
core standing task (push the real `evolve` search harder than the 3-hourly
checks' usual 15-generation batches) plus the routine health checks that
have fallen behind their own recommended cadence.

## Work done

**1. `live-benchmark` re-run (routine, last run 2026-11-21).** 105 1d bars
of real trading history (2026-08-14 to 2026-11-27): live account +26.02%
(sharpe 1.96, maxDD -21.6%) vs. equal-weight buy-and-hold +0.69% (sharpe
0.36, maxDD -41.7%) — **excess +25.33%**, down slightly from last week's
+28.20% but still strongly positive. Item 0's trigger 1 (persistent
*negative* excess) still does not fire. Descriptive only, no gate/promotion
effect, no decision point reached.

**2. `holdout-pressure` snapshot before/after the evolve batch.** Margin
7.903 → 7.908 (draw count 2468 → 2482, all from this batch's fold-aggregate-
gate-clearing candidates, all correctly rejected at the sealed holdout) —
same slow-rise pattern item 13 already has fully diagnosed, nothing new.

**3. 40 real `evolve` generations against the live v3 (1d) champion, no
promotion** — a deliberately larger batch than the 3-hourly checks' usual
15, using the weekend session's bigger time budget on the core search
rather than spreading it across more diagnostics. Cumulative candidates
tried against v3 rose 140072 → 140616 (per `researcher_memory.tested`),
stagnation/boldness counter 10165 → 10205. Backgrounded via the harness's
own `run_in_background` option directly on the `evolve` command, no
`nohup`/`&`, per item 9's standing rule — ran cleanly for its full ~57
minutes with no detachment issues. Champion's fold-aggregate fitness held
flat at 1.390 across all 40 generations (966 trades, 38% win, 1% stops, 3
halts, unchanged — no daily-bar roll this cycle since it's a weekend).
Best-of-generation fold-fitness ranged roughly 1.221-2.698 across the 40
generations, never clearing the promotion-margin bar (current margin
~7.9x the best raw holdout edge any fold-aggregate winner has shown so
far, per item 13's standing diagnosis).

## Verification

- `python3 -m pytest -q`: 505/505 both before (baseline, taken before the
  evolve batch started) and after.
- Top-level key diff of `live_state.json` (snapshotted to the gitignored
  scratchpad before the batch): only `updated`/`researcher_memory`/
  `lineage` changed. `genome`, broker/account fields, journal,
  `hard_call_reviews` all byte-identical. `lineage` length unchanged at
  202 (bounded ring buffer — no new promotion attempt was recorded, as
  expected since nothing cleared the fold-aggregate margin).
- `tools/edit_bundle_module.py sync --check`: clean, no drift between the
  bundle and the real unflattened files.
- Dashboard rebuilt with `EVO_STATE` set: `index.html` 21.1 KB, shows
  140616 challenger idea(s) tried.
- Genome still v3 (1d) live, untouched. No trading this session (weekend —
  the daily tick runs at the dedicated 00:20 UTC slot, not this one).

## What's next

Nothing new opened this session — the honest state of "Next steps" right
now is that the remaining open items are either owner-gated (items 5, 6,
13) or already closed, and the standing task (push `evolve` against v3,
watch `holdout-pressure`'s margin, keep `live-benchmark` on its weekly
cadence) is what's left to do until either the owner weighs in on one of
the gated items or a genuinely new idea for item 5's "different kind of
input" problem surfaces. Future weekend sessions: keep running
`live-benchmark` weekly per item 0's recommendation, and don't re-run
another parameter sweep inside item 5's existing signal family without a
new data source to back it — that door was explicitly closed by the
2026-11-08 write-up.
