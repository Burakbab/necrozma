# Weekend all-hands, 2026-11-15 ~06:00-08:41 UTC

## Setup

- `git config user.name "Burk"` / `user.email` to the noreply address (local
  config only).
- Container started in detached HEAD. `git checkout main` +
  `python3 tools/git_sync.py` fast-forwarded cleanly through the
  2026-11-14/11-15 commits already pushed by weekday sessions (through
  `908e7fd`), no divergence, no shallow-clone staleness.
- `pip3 install -r requirements.txt -q` left numpy/pandas missing again —
  the recurring split tracked under AGENTS.md items 9/12's history.
  `python3 -m pip install -r requirements.txt -q` fixed it immediately.
- Baseline `python3 -m pytest -q` → 505/505 before any change.
- `review-hard-calls` → 0 pending (6 reviewed, unchanged).
- `AGENTS.md` size at session start: 229,313 bytes — ~27KB under the 256KB
  single-read threshold, comfortably clear. Not archived this cycle.

## Roadmap survey

Read `AGENTS.md`'s "Current state" and "Next steps" in full plus the last
week of `runs/` (2026-11-13 through 2026-11-15) before deciding what to
spend this session's larger time budget on. Finding: essentially every
substantive item on the numbered roadmap is either closed or genuinely
blocked on the owner, not on more engineering or diagnostics from this
session:

- Item 5 (short selling) reached "a real ceiling, not bad luck" as of the
  2026-11-08 weekend session's own writeup — three independently-built
  non-regime confirmation dimensions (temporal, cross-sectional,
  volatility-character) and two regime combinations have all shown the
  identical shape (in-sample sweet spot, fails or only partially survives
  out-of-sample, never profits in a real severe crash). The explicitly
  recommended next step is "a different kind of input... not another sweep
  of another scalar threshold on the same daily OHLCV data" — nothing in
  this container can supply that, so picking this back up today would just
  be another variation on an already-exhausted family.
- Item 6 (equities/FX) is blocked on a human picking a real data source —
  explicitly "no code has a reason to exist yet."
- Item 13 (`HOLDOUT_SIGMA` cumulative correction) has a full quantified
  design pass (2026-10-10) already on record; only the owner's own
  risk-appetite call is missing.
- Items 1-4, 7-12 are closed, shipped, or routine-automatic.

Given that, decided the honest highest-value use of this session's deeper
time budget was a single, properly-finished, larger-than-usual real search
batch against the live champion — weekday 3-hourly checks have been running
15 generations at a time all week — rather than inventing a new structural
thread under time pressure.

## First attempt collided with a concurrent session

Snapshotted `live_state.json` (`researcher_memory.tested` = 117,762) and ran
a continuous **50-generation** `evolve` batch via `tools/background_runner.py`
(`start` + separate `wait`, no `nohup`/`&`). It completed cleanly (exit 0,
tested 117,762 → 118,444, stagnation 8540 → 8590, no promotion,
`pytest` 505/505 before and after), and the commit was prepared.

`git push` was rejected: another session (a routine 15-generation batch, not
itself a weekend entry) had pushed in the meantime, starting from the exact
same base (`researcher_memory.tested` = 117,762) and landing its own real
evolve run (117,762 → 117,967) first. `git pull --rebase` produced genuine,
unresolvable conflicts in `live_state.json` — two independently-RNG-seeded
`evolve` continuations from the same starting state cannot be hand-merged at
the JSON level; there is no meaningful line-level diff between two separate
random searches. This is a real instance of the collision the run protocol's
own `git_sync.py` section warns about ("several routines share this repo and
collide otherwise"), just manifesting in `live_state.json`'s evolution
history instead of in a shallow-clone divergence.

**Resolution**: aborted the rebase, then `git reset --hard origin/main` to
adopt the already-pushed, already-canonical state as the single source of
truth, discarding this session's own local, unpushed, now-orphaned
50-generation result. Nothing public was lost — the discarded commit had
never been pushed, and the other session's real work (117,967 cumulative
candidates) is the one that survives. The 50-generation run itself wasn't
wasted compute in any harmful sense (it was a legitimate real search that
found nothing, same as every other batch this week), it's just not part of
the committed history.

**For future sessions**: if a scheduled run is going to background a
long `evolve` batch and there's reason to think another session might run
concurrently (e.g. a weekend all-hands overlapping a 3-hourly check's
schedule near a boundary), there's no good way to avoid this short of
checking `git fetch`/`origin/main` immediately before `git push` and, on
conflict, accepting that the loser's `evolve` result is simply discarded
(never force-push, never hand-merge `live_state.json`'s evolution fields).
That's what happened here and it's the right call, not a process failure to
fix — flagging it mainly so a future session recognizes the pattern quickly
instead of attempting a risky manual JSON merge.

## Second, successful batch

Re-snapshotted `live_state.json` on the new base (`tested` = 117,967,
stagnation 8555) and ran a fresh **40-generation** `evolve` batch the same
way. Completed cleanly: exit 0, no truncation, champion's fold-aggregate
fitness held flat at 1.556 throughout (974 trades, 39% win, 1% stops,
3 halts). Best-of-generation fold-fitness ranged roughly 1.164-2.655 across
the 40 generations, never clearing the promotion-margin bar. Cumulative
candidates tried against v3 rose **117,967 → 118,514** (547 new candidates);
stagnation/boldness counter **8555 → 8595**.

## Verification

- `python3 -m pytest -q` 505/505 both before (post-reset baseline) and after
  this second batch.
- Top-level key diff of `live_state.json` (snapshotted immediately after the
  reset, before `start`) showed only `updated`/`researcher_memory`/
  `lineage` changed. `genome` byte-identical (still v3, untouched),
  `broker`/`journal`/`hard_call_reviews` untouched. `lineage` length
  unchanged at 202.
- `tools/edit_bundle_module.py sync --check` → bundle already matches real
  files, no drift.
- `holdout-pressure` re-checked post-batch: margin flat at 7.829, draw count
  rose to 2127 (new sealed-holdout draws from this batch's
  fold-aggregate-gate-clearing candidates, all correctly rejected, same
  slow-rise pattern already tracked under item 13).
- `review-hard-calls` still 0 pending (6 reviewed, unchanged).
- Dashboard rebuilt with `EVO_STATE` set; `index.html` now reports 118,514
  challenger idea(s) tried.
- `git fetch origin main` immediately before this commit confirmed no new
  remote commits landed since the reset, so this push should apply cleanly.
- Genome still v3 (1d) live, untouched throughout. No constitution change,
  no `AMENDMENTS.md` row needed. No promotion, so no `README.md` `## Status`
  update needed.

## Reading

Across both batches (90 real generations run this session, 118,444 and then
118,514 cumulative candidates reached at various points, only the latter
committed), nothing cleared the cumulative multiple-testing margin even with
far more search depth in one sitting than any weekday slot gets — consistent
with item 13's own finding that the margin, not search depth or boldness
saturation, is the dominant force keeping v3 in place at this draw count.
The more interesting finding this session produced wasn't about the genome
at all: it's the first documented case of two scheduled routines actually
colliding on `live_state.json`'s evolution fields in real time, not just the
shallow-clone staleness `git_sync.py` was built for.

## Next

Nothing newly queued on the trading/evolution side. The roadmap's remaining
open items (5, 6, 13) all still need either a human decision or a genuinely
different data source before another session can move them forward with
diagnostics alone — the next weekend session should check whether either
owner-call has landed before defaulting to "run more evolve generations"
again, since that is now the only unblocked lever left and has an
increasingly well-documented flat return on repetition at this draw count.
