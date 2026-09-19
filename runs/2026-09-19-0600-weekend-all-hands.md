# Weekend all-hands — 2026-09-19 (~06:15-09:10 UTC)

Two threads this session: a deeper real `evolve` batch than a routine 3-hourly
check (using this session's larger time budget), and — the actual deep-focus
piece — a genuinely controlled "convergence across independent seeds"
experiment that AGENTS.md's own "Measured 2026-08-16" section has called for
as a priority evidence type since last month, and that nobody had picked up.
Also handled an unplanned real-world event along the way: a genuine
concurrent-write collision with a 3-hourly check that pushed mid-session,
resolved by reconciling `live_state.json` rather than discarding either
side's work.

## 0. Freshness check before starting

Before touching anything: `succession-audit` re-run fresh — unchanged from
the picture already in AGENTS.md (neither v1 nor v2 clears the dd-corrected
gate either, each for a different reason; v3 stays live). `holdout-pressure`
re-run fresh — 497 draws, margin 7.048, same shape as already recorded,
nothing new. `python3 -m pytest -q` 422/422 baseline. Items 2/5/6 still not a
scheduled session's call (short-selling Phase 2's "should a consult be
allowed to open a short" question and the equities/FX data-source pick both
remain explicitly unscoped owner decisions — verified directly against
`agents/judges.py`/`agents/consults.py`/`agents/trader.py` that the sign
landmines flagged 2026-09-13 are in fact already fixed and `.short()` still
has zero live callers, contradicting an earlier draft summary that claimed
otherwise; trust the code over any summary, including this file's own past
entries). Items 7-12 all closed/feature-complete/self-sustaining — no live,
unblocked roadmap item was sitting available this weekend, which is why this
session's main investment went into evidence-production instead (exactly
what the "Measured 2026-08-16" section says to prefer when that's the case).

## 1. A deeper real evolve batch — 60 generations vs. the routine 15

Ran `tools/background_runner.py` (`start` + backgrounded `wait`) against
`evotrader_bundle.py evolve 60`, ~85 real minutes, exit 0, no truncation.
Champion's fold-aggregate fitness held flat at 1.465 throughout (943 trades,
38% win, 1% stops, 4 halts). Cumulative candidates tried against v3 rose
22523 → 23354 (+831), stagnation/boldness counter 1620 → 1680. No promotion —
best-of-generation ranged 1.293-2.554, regularly beating the champion's own
number but never by enough to clear a bar now built on 23k+ prior draws. Full
detail: `runs/2026-09-19-0752-evolve-batch-v3-60gen.md`.

**Real concurrency collision, handled properly rather than force-pushed
through.** While this batch ran, a routine 3-hourly check ran its own real
15-generation batch against the *same* starting champion state (base commit
`3a051e5`, tested=22523) and pushed first (`4f48c8d`, tested→22733). This is
exactly the kind of collision AGENTS.md's Run protocol has warned about since
its first line ("several routines share this repo and collide otherwise") —
but previously-recorded incidents were all git-ref staleness (shallow clones,
stale local branches), not two *real* evolve searches genuinely diverging
from the same live-account base at the same time. `git push` was rejected
("fetch first"); `git merge origin/main` produced real content conflicts on
`live_state.json`/`index.html` — the first time this account has hit that,
as far as this file's history shows.

Resolution, reasoned from what the fields actually mean rather than picking
a side: `genome`/`broker`/`journal`/`hard_call_reviews` were byte-identical
across the base, the 3-hourly check's push, and this session's batch (both
were pure no-promotion, no-trade evolve runs, verified by direct top-level
key diff) — so there was nothing to reconcile there. The only real divergence
was `lineage` (a rolling, capped-at-200 telemetry window per
`core/live.py`'s `_trim_lineage`, plus permanently-preserved `accepted`
promotion records) and `researcher_memory` (`tested`, `stagnation`,
`holdout_draws`). `tested` is a hash **set** of every candidate patch ever
tried against this fixed champion — the entire point of the cumulative
multiple-testing correction is that this set only grows, so the correct
merge is the **union** of both branches' tested-hash sets (23564 total, and
notably zero overlap between the two branches' 210 and 831 new entries —
independent RNG draws essentially never collide). `stagnation` and
`holdout_draws` are cumulative counters; since both branches ran real,
distinct generations on top of the same base, the correct merge is the base
value plus **both** branches' increments summed (not maxed, not just one
side's) — origin's final value (1636 stagnation / 500 holdout_draws) plus
this session's own increment on top (+60 stagnation / +10 holdout_draws) =
1696 / 510. This is also the *safe* direction if there's any ambiguity: every
prior correction to this system's safety gates (AMENDMENTS.md, every row)
has made promotion strictly harder, never easier, and summing rather than
deduplicating counters can only ever raise the bar, never lower it.
`lineage` was reconstructed by identifying each branch's genuinely-new
entries (via `n_tested_cumulative > 22523`, the base's own maximum),
concatenating base + origin's-new + this-session's-new in chronological
order, and re-running the *actual* `core/live._trim_lineage` function on the
result — not a hand-rolled approximation of it — so the final persisted
window is byte-for-byte what the real code would have produced from that
history. The reconciled state was then round-tripped through a real
`LiveAccount(...).save(...)` call (not hand-written JSON) so field order,
`journal` truncation, and the `updated` timestamp all match what the account
code itself would write.

Verified before treating this as safe to commit: `python3 -m pytest -q`
422/422 on the merged state; constitution `verify()` → `726dfa4bac85891a`
unchanged; `tools/edit_bundle_module.py sync --check` clean; `summary` and
`holdout-pressure` both ran cleanly against the merged file with sane
numbers; every non-`lineage`/`researcher_memory`/`updated` top-level key
confirmed byte-identical between the 3-hourly check's pushed state and this
session's state before merging. Landed as a real two-parent `git merge`
commit (`9e4038c`), not a rebase or force-push — the two-parent history is
the honest record of what actually happened, and resolving conflicts by hand
with `git checkout --ours`-then-fix would have silently discarded one
side's real work instead of reconciling it. **For whoever hits this again**:
if two branches' `live_state.json` changes are both pure evolve-no-promotion
diffs (confirm via the top-level key diff first — this is the load-bearing
check), the merge above is mechanical and safe to repeat: union `tested`,
sum the counter deltas, reconstruct `lineage` via the real `_trim_lineage`,
save via a real `LiveAccount`. If either side had promoted or traded, this
would need a fundamentally different (and much more careful) resolution —
not attempted here because it didn't come up.

## 2. Seed-convergence experiment — the actual deep-focus work

`run_from_files.py`'s `evolve-dry-run` (shipped 2026-08-24, proven equivalent
to the bundle's real `evolve`) already accepts a `--seed N` flag that the
bundle's own `evolve` doesn't — added originally just as a test-only escape
hatch, never used for an actual experiment. That flag, plus `evolve-dry-run`
never calling `acct.save()`, made it possible to run a genuinely controlled
version of the "convergence across independent seeds" check the "Measured
2026-08-16" section names as a priority evidence type, without writing a
line of new code and without ever touching `live_state.json`.

**Why this is a cleaner check than anything run before.** The live
`evolve` command always passes `seed=None` (OS entropy) — every routine
3-hourly batch already uses a fresh random seed, but each one also runs on a
*different calendar day*, so the trailing 4-year evaluation window has
already shifted by the time the next batch runs. The 2026-09-13 weekend
session's `fold-date-sensitivity` check established that this window drift
alone swings fold-aggregate fitness by up to 0.68 over a 7-day span — which
means every prior "this batch was livelier than usual" observation was
confounded: seed and calendar day changed together, so neither factor could
be isolated. Fixing `--seed` and running multiple invocations **on the same
day** (so `market.load_universe`'s 4-year window is identical) isolates the
seed as the only varying factor for the first time.

**Setup**: three sequential `run_from_files.py evolve-dry-run 15 --seed N`
runs (N = 101, 202, 303), each starting from the exact same snapshot —
verified directly: all three logged `23578 tried against v3` at generation 1
`(the merged state's 23564 base + 14 new)`, confirming each run loaded the
identical `researcher_memory`/champion and never carried state between
runs (dry-run never saves, so run 2 and run 3 legitimately re-loaded the
same starting point rather than continuing from run 1). All three ran
against real market data, real folds, the real sealed holdout — same cost
class as a routine batch, just never committed.

**Result** (best-of-generation fold-fitness vs. champion's fixed 1.465,
15 generations each):

| seed | mean | min | max | beat champion | tie | lose |
|---|---|---|---|---|---|---|
| 101 | 1.617 | 0.987 | 2.263 | 9/15 (60%) | 2 | 4 |
| 202 | 1.632 | 1.379 | 2.406 | 11/15 (73%) | 0 | 4 |
| 303 | 1.588 | 1.309 | 1.935 | 11/15 (73%) | 2 | 2 |

The three means span only **0.044** (1.588-1.632) — an order of magnitude
tighter than the 0.679 spread `fold-date-sensitivity` found across a 7-day
calendar window on the same champion. None of the three seeds promoted
(expected: 15 generations is the routine batch size, and no routine batch
has promoted in months at this stagnation level either). None showed a
qualitatively different search outcome — all three found best-candidates
comfortably above the champion in most generations and none found anything
close to clearing the cumulative multiple-testing bar.

**Reading**: this is now a real, controlled answer to a question the
2026-09-13 weekend session could only address by inference. That session's
`fold-date-sensitivity` check argued that a "livelier than usual" batch
reflects which day it is, not what the search is finding — but it never
ruled out seed variance as a contributing factor, because every batch
compared across different days also used a different seed. This experiment
holds the day (and therefore the evaluation window) fixed and varies only
the seed, and finds the search's own output distribution is far more stable
under seed variation than under calendar drift. **Practical consequence for
future sessions**: a batch's "beat ratio" or best-of-generation range being
unusual is still best explained by checking that day's `fold-date-sensitivity`
position first (per the 2026-09-13 session's own guidance, unchanged) — this
result adds the missing half of that argument (seed isn't a competing
explanation) rather than changing the recommendation.

**Also observed, not the main point of this experiment**: `n_tested_cumulative`
increments identically across all three seeds at every generation (14 new
proposals per generation in all three, `n_blind=14` being a fixed parameter
independent of seed) — the *count* of blind proposals per generation isn't
itself seed-sensitive, only which specific patches get drawn is. Consistent
with `agents/researcher.py`'s `Researcher.rng = random.Random(seed)` only
affecting *which* mutations get proposed, not how many.

Nothing here changed any code, gene, or the champion. `live_state.json`
confirmed untouched by all three `evolve-dry-run` calls (git status clean
after each). No live trading this session (tick 36 already handled at 00:20
UTC before this session started).

## Verification summary

`python3 -m pytest -q`: 422/422 at every checkpoint (before the 60-gen batch,
after it, after the merge, unaffected by the three dry-runs since they never
write). Constitution manifest `726dfa4bac85891a` unchanged throughout.
`tools/edit_bundle_module.py verify`/`sync --check` clean. Dashboard rebuilt
with `EVO_STATE` set after the real state change. Genome still v3 (1d) live,
untouched — no promotion this session, no README update needed.
