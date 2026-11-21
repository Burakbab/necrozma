# 3-hourly check — 2026-11-21 ~09:46-10:20 UTC — evolve batch vs v3

## Context

No new daily bar to trade this cycle: at session start `live_state.json`'s
`updated` was `2026-11-21T07:35:40+00:00`, matching the prior 3-hourly
check's own post-collision evolve batch. Tick 99 was already handled at the
dedicated 00:20 UTC daily slot. `review-hard-calls` reported 0 pending (6
reviewed, unchanged). `AGENTS.md` size 243,222 bytes at session start —
~13KB under the 256KB threshold, not archived this cycle.

A flaky, order-dependent test failure showed up on the first full-suite
`pytest -q` run (`1 failed, 504 passed` —
`tests/test_fold_scheme_reconstruction.py::test_version_1_is_the_seed_and_needs_no_lineage`),
but passed in isolation, passed when its whole file was run alone, and
passed on an immediate full-suite rerun (505/505). Not investigated further
— reads as test-ordering/timing flakiness, not a real regression, and did
not recur on any subsequent run this cycle (baseline rerun, post-batch
verification run — both clean 505/505).

## What ran

One real 15-generation `evolve` batch (backgrounded via
`tools/background_runner.py start`/`wait`, no `nohup`/`&`, output captured
to a log file from the first byte), run after a clean baseline `pytest -q`
pass (505/505, after the flake above was dismissed by rerun). Champion's
fold-aggregate fitness held flat at **1.542** across all 15 generations
(921 trades, 37% win, 1% stops, 4 halts — no daily-bar roll this cycle).
Best-of-generation fold-fitness ranged roughly 0.622-2.200, never clearing
the promotion-margin bar. Cumulative candidates tried against v3 rose
**128735 → 128941** (per `researcher_memory.tested`); stagnation/boldness
counter 9338 → 9352.

## Verification before commit

- `python3 -m pytest -q`: 505/505 both before (after the flake dismissal)
  and after the `evolve` batch.
- Top-level key diff of `live_state.json` (snapshotted before the batch):
  only `updated`/`researcher_memory`/`lineage` changed. `genome`, `broker`,
  `journal`, `hard_call_reviews` byte-identical. `lineage` length unchanged
  at 202 (bounded ring buffer, no new promotion attempt recorded).
- `tools/edit_bundle_module.py sync --check`: clean, bundle already
  matches real files.
- `holdout-pressure` re-checked post-batch: margin rose slightly
  (7.869 → 7.872), draw count 2300 → 2314 (new sealed-holdout draws from
  this batch's fold-aggregate-gate-clearing candidates, all correctly
  rejected) — same slow-rise pattern already tracked under item 13,
  nothing new.
- Dashboard rebuilt with `EVO_STATE` set (`index.html` now shows 128941
  challenger idea(s) tried).

Genome still v3 (1d) live, untouched. No constitution change, no
promotion, no README.md update needed, no new git-push collision this
cycle (fetched `origin/main` immediately before this commit; no
divergence).
