# Weekend all-hands, 2026-10-04 ~06:00-09:00 UTC

## Context going in

Synced cleanly from `main` (`git checkout main` + `tools/git_sync.py`,
fast-forwarded 41 commits, no divergence). `requirements.txt` installed.
Skimmed recent `runs/` notes: the last several days have been an unbroken
run of "15 more `evolve` generations against live v3, no promotion" plus
the 2026-10-03 weekend session's two new short-selling diagnostics
(`benchmark_trend_break_short`, `benchmark_combined_short`). At session
start: cumulative candidates tried against v3 47,593
(`researcher_memory.tested`), stagnation/boldness 3,437. `review-hard-calls`
0 pending (4 reviewed). Items 6 (equities/FX data source) and 13
(`HOLDOUT_SIGMA`'s cumulative margin) are both still open owner decisions,
unchanged — nothing new to raise there this session.

`AGENTS.md` was 243,433 bytes at session start, comfortably under the
256KB rotation threshold — no archival needed yet.

## Decision: what to spend the session on

The 2026-10-03 weekend session's own writeup left a concretely scoped,
unbuilt next step for item 5 (short selling): `benchmark_combined_short`
(AND-gated entry, OR-sensitive cover) was found to nearly erase the one
real bear-window payoff either signal has ever produced, because covering
the instant *either* signal disagreed inherited the regime classifier's
documented whipsaw. The flagged fix — gate opening on both signals, but
let trend-break alone govern covering — was explicitly "untested, not yet
built." That's exactly the kind of finishable, high-signal piece of work
this session's bigger time budget is for, so it was built and measured
first; a bigger `evolve` batch ran in the background alongside it for
real search volume, following the same split-the-time pattern the
2026-10-03 session used.

## Item 5: the asymmetric short variant

New `loop.engine.benchmark_asymmetric_short` (8 new tests,
`tests/test_asymmetric_short.py`) opens exactly like
`benchmark_combined_short` — a symbol's own price-only trend-break AND the
basket-wide regime must both agree this bar — but covers on trend-break
ALONE; the regime leaving `short_regimes` no longer forces a cover. Wired
into `short-headroom --asymmetric`. New test
`test_holds_through_a_regime_flip_combined_would_have_covered_on`
constructs a synthetic scenario (one symbol declining monotonically all
window, so its own trend never recovers; a separate anchor symbol crashing
then recovering hard enough that `Analyst._regime` genuinely leaves
bear/crisis partway through) and asserts the asymmetric run holds the
position through the regime flip while `benchmark_combined_short` covers
early on the same data — confirmed numerically before locking in the test
(asymmetric: 121 bars held short / 53.6% return vs. combined: 26 bars /
21.7% return on that construction).

Real 4-year result against the live champion's current fold/holdout
windows (fee+slippage+3bps/bar borrow), trend-break alone / combined /
asymmetric side by side:

| window | trend-break | combined | asymmetric |
|---|---|---|---|
| fold 1 (bull, b&h +76.3%) | -34.9% | **-14.7%** | -38.6% |
| fold 2 (bull, b&h +135.6%) | -45.2% | -48.2% | -48.1% |
| fold 3 (bear, b&h -34.6%) | **+32.8% (95% capt.)** | +0.1% (0% capt.) | +23.2% (67% capt.) |
| holdout (bull, b&h +55.9%) | -22.8% | -14.6% | **-13.7%** |

The fix worked on the problem it targeted: fold 3's captured share went
from combined's 0% back up to 67%, most of the way to trend-break alone's
95%. But the predicted bull-market benefit — "keep combined's quiet
periods, lose none of trend-break's bear capture" — didn't show up. In
fold 1, asymmetric's loss (-38.6%) is actually worse than both
alternatives tried so far, not just worse than combined.

Checked why directly: asymmetric's fold-1 avg concurrent short (10.20) and
flip count (216) are close to trend-break alone's own numbers (10.59 /
216), not combined's lower ones (8.59 / 260). The AND-gated entry barely
filters anything in this fold, because — consistent with the 2026-09-27
finding already on record for this item — `Analyst._regime`'s `bear` leg
is an easily-tripped OR (`anchor_score < -0.03 OR breadth < 0.30`) that
fires almost as often as individual symbols' own price-only trend-break
during ordinary pullbacks, even inside an overall-bull fold. So the entry
gate contributes little, and once a position opens, asymmetric holds it
exactly as long as trend-break alone would (identical cover rule) —
inheriting nearly all of trend-break's bull-market duration risk, none of
combined's early-exit protection. Fold 2 is close to a three-way tie.
Holdout's -13.7% (best of the three, barely) comes from the entry gate
blocking a handful of bad entries, not from any cover-side benefit — one
window, not enough to read as a general pattern.

**Conclusion recorded in AGENTS.md item 5**: three combination shapes have
now been measured (AND/OR, AND/trend-alone, and the two signals run
separately) and none dominates — each trades bear-window capture against
bull-market loss in a different place, and none beats trend-break alone in
the bear window while also beating combined in the bull windows at the
same time. The honest read is that the *regime* signal itself is the weak
link in every combination tried (noisy `bear` leg, rarely adds real
filtering), not the particular way it's wired to trend-break. No further
recombination of these same two signals is queued; a genuinely different
signal to pair with trend-break — not another AND/OR variant on the
existing regime classifier — is what a future session on this item should
consider. Does not decide whether to build real short-opening wiring
either way.

This work was committed and pushed cleanly (`118dae1`) before the evolve
batch below ran into a collision.

## Evolve batches, and a real multi-session collision

Kicked off a 40-generation `evolve` batch in the background right after
the asymmetric-short commit, starting from `researcher_memory.tested`
47,593, via `tools/background_runner.py` (`start`/`wait`). It took ~100
minutes (two `wait` calls hit their own timeout while the detached process
was still healthy, confirmed alive via `ps` both times; a third `wait`
with a longer timeout caught the real exit cleanly, code 0, no promotion,
fitness held flat at 1.393 across all 40 generations).

While it ran, a **concurrent 3-hourly-check session** started its own
15-generation batch from the same 47,593 baseline and pushed first
(`de99407`: 47,593 → 47,798). This session's own `git push` on the
40-generation-batch commit was correctly rejected (non-fast-forward).
`live_state.json`'s generated `researcher_memory`/`lineage` fields aren't
line-mergeable the way text is, so a `git rebase` hit real conflicts in
`live_state.json`/`index.html`/`AGENTS.md`. Rather than hand-resolve a
generated-data conflict or force anything, this session:

1. Aborted the rebase.
2. Reset the local, not-yet-pushed 40-generation-batch commit to
   `origin/main` — losing nothing shared (the asymmetric-short work was
   already upstream at `118dae1`; the 40-generation batch's own specific
   result was fully reproducible: "no promotion, fitness still 1.393,"
   already established independently by the concurrent session's own
   15-generation result on the same champion).
3. Ran a fresh 20-generation batch on top of the now-current state
   (`tested` 47,798 → 48,074) instead of attempting to hand-merge two
   divergent generated snapshots.

No force-push, no destructive operation on shared history, no uncommitted
work lost on either side — this is exactly the "several routines share
this repo and collide" scenario the Run protocol already anticipates, just
for `evolve`'s own generated state rather than a shallow-clone staleness
case. Final state represents both sessions' real evolve work in sequence:
47,593 → 47,798 (concurrent session) → 48,074 (this session, on top).

The final 20-generation batch: champion's fold-aggregate fitness held flat
at 1.393 across all 20 generations (959 trades, 38% win, 1% stops, 4
halts, unchanged throughout). Best-of-generation fold-fitness ranged
roughly 1.11-2.46, never clearing the promotion-margin bar.

## Verification discipline

- `python3 -m pytest -q`: 457 (baseline) → 465 (after the asymmetric-short
  code) → 465 (after the final 20-generation evolve batch), green at every
  step
- Top-level key diff of `live_state.json` against the pre-batch commit
  (checked directly in Python, not eyeballed): only
  `updated`/`researcher_memory`/`lineage` changed; genome, broker, journal,
  `hard_call_reviews` byte-identical
- `lineage` length unchanged at 202 (bounded ring buffer, no new promotion
  attempt recorded)
- `tools/edit_bundle_module.py sync --check`/`verify` both clean throughout
- `python3 -c "import py_compile; py_compile.compile('evotrader_bundle.py', doraise=True)"`
  clean after every CLI-section edit
- Constitution checksum unchanged (`726dfa4bac85891a`) — neither change
  touches a `_PROTECTED` file
- `holdout-pressure` re-checked (read-only): margin 7.472, draw 1073 — a
  few new fold-aggregate gate clears across the combined evolve work, same
  slow-rise pattern already tracked under item 13, nothing new

## Housekeeping: AGENTS.md archival

After this session's additions, `AGENTS.md` reached 253,766 bytes — within
~2.4KB of the 256KB single-read threshold, the tightest margin yet logged.
Archived all eight 2026-09-29 "Current state" entries verbatim to new
`AGENTS_ARCHIVE_2026-09-29.md` (verified byte-identical via direct line
slice comparison before removal), cutting the live file to 235,252 bytes.
Nothing reworded, nothing lost. No code changed, no protected file
touched, `live_state.json` untouched by this step itself.

## State at end of session

- Genome: v3 (1d), unchanged, live
- `researcher_memory.tested`: 48,074 (was 47,593 at session start; two
  sessions' real work landed in sequence: 47,798 then 48,074)
- stagnation/boldness: 3,472 (was 3,437)
- `holdout-pressure` margin: 7.472, draw 1073
- `review-hard-calls`: 0 pending (unchanged)
- Full test suite: 465/465
- Dashboard rebuilt (`index.html`, 48,074 challenger ideas shown)
- Items 6 and 13: still open owner decisions, nothing new this session
- `AGENTS.md`: 235,252 bytes after archiving the 2026-09-29 slice

## Next steps for whoever picks this up

1. Item 5's three measured combination shapes (AND/OR, AND/trend-alone,
   separate) don't dominate each other — per this session's conclusion,
   recombining the same two signals again is unlikely to be the
   highest-value next move. A genuinely different short-timing signal to
   pair with trend-break (not another wiring of the existing regime
   classifier) is the concretely scoped idea for a future session, if this
   item is picked back up.
2. Items 6/13 remain blocked on owner risk-appetite decisions; per item
   13's own instruction, do not try to resolve it with more diagnostics.
3. `AGENTS.md` is back to a healthy ~235KB after this session's archival —
   no rotation needed for a while.
4. If a future session hits a `git push` rejection right after an `evolve`
   batch finishes, this session's collision-handling approach (reset the
   local, not-yet-pushed, fully-reproducible generated-state commit to
   `origin/main` rather than hand-merging `live_state.json`; re-run the
   batch on top if the search volume still matters) worked cleanly and is
   worth reusing rather than re-deriving from scratch.
