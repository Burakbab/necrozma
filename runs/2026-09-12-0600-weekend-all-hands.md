# Weekend all-hands — 2026-09-12 06:00 UTC

Deep-focus weekend session. No live trading this cycle (tick 29 already
handled at 00:20 UTC, confirmed via `live_state.json`'s `updated` timestamp
and `runs/2026-09-12-0020-daily-trading.md` before starting) — deliberately:
weekend sessions are for evolution/self-improvement depth, not day-to-day
trading.

## What was decided, and why

**Freshness pass before committing to an action.** Read `AGENTS.md`'s full
"Next steps" roadmap (items 1-10) before doing anything. All ten are closed,
passive/ongoing, or genuinely blocked on an owner decision: item 2 (4h-bar
shadow evolution) parked by owner decision 2026-09-08; item 4 (LLM-backed
consults' "apply verdict" half) still blocked on a real live hard-call flag
actually occurring (`review-hard-calls` confirmed 0 pending); item 5 (short
selling) blocked on a human sign-off before touching the checksummed
`core/portfolio.py`; item 6 (equities/FX) blocked on a human picking a data
source; item 7 (unflatten) feature-complete pending a migration-policy
decision; items 1/3/8/9/10 are closed or self-sustaining. `live-benchmark`
re-checked (28 bars, -13.21% excess) — nowhere near item 0's 60-bar revisit
trigger. `holdout-pressure` re-checked (257 draws pre-session, every one
lost, margin unchanged in shape).

With nothing new unblocked, this session spent its larger time budget on two
things instead of the usual single 15-generation batch: (1) closing a stale
diagnostic gap, and (2) a much deeper real `evolve` run than a 3-hourly check
has room for.

## 1. Re-measured the 2026-08-16 consult-correlation finding

The "Measured 2026-08-16" section's finding #2 — moderate/risky consult
signal correlation +0.39 overall, rising to +0.51/+0.58 in bear/crisis —
explicitly instructs "run `evotrader_bundle.py consults` after any roster
change." That instruction had not actually been followed since the finding
shipped, despite 13+ generations of tuning and two full promotions (v1→v2,
v2→v3) happening in between. This is the same kind of staleness item 8 (the
`consult_conservative` entry/exit asymmetry) already found once — a measured
problem that search quietly moves without anyone re-checking.

Re-ran `consults` against live v3 (1386 logged bars, 10269 proposal points).
Result: the echo has weakened substantially but not disappeared.

| pair | 2026-08-16 | 2026-09-12 (v3) |
|---|---|---|
| conservative/moderate | +0.03 | +0.101 |
| conservative/risky | -0.13 | -0.045 |
| moderate/risky (overall) | +0.39 | +0.172 |
| moderate/risky (bear) | +0.51 | +0.45 |
| moderate/risky (crisis) | +0.58 | +0.43 |
| same-side agreement (mod/risky) | 93.2% | 96.1% |

Reading: moderate/risky correlation roughly halved in magnitude, and
conservative/risky flipped to genuinely near-independent (1.5% same-side
when both fire, versus a fixed theory-at-two-speeds relationship). But the
shape of the problem is identical to 2026-08-16 — bear and crisis are still
the two regimes where the Risk Judge's "agreement" signal most reads its own
echo, just at smaller magnitude. Unlike item 8's asymmetry (which search
fully corrected for v3), this one is reduced, not resolved. Not treated as a
proposal or gene change here — no code touched, no genome change — just the
overdue re-measurement the section's own text calls for. Written up as a new
addendum under "Measured 2026-08-16" in `AGENTS.md` rather than a new
Next-steps item, since it doesn't (yet) suggest a concrete structural change,
only that the next session picking this up again shouldn't start from the
2026-08-16 numbers. Committed and pushed early (`633e286`), separately from
the evolve work below, since it stood on its own.

## 2. A deep evolve batch, interrupted by a real push collision

The standing 3-hourly cadence runs 15-generation batches; this session
wanted to use its larger time allowance to run one real 60-generation batch
instead (4x normal). Started one via `tools/background_runner.py` from
cumulative-candidates baseline 11465 and let it run in the background
(~73 minutes wall-clock) while doing other read-only checks.

While preparing to commit the finished batch, `git push` was rejected: a
concurrent 3-hourly check session had *also* started from the same 11465
baseline (it began right around when this session's own batch did) and
pushed its own real 15-generation batch (11465 → 11672) first. This is not
the usual "stale local branch" collision `tools/git_sync.py` handles —
`git fetch` showed a real divergence, and unlike a docs-only conflict, both
sides had genuinely different `live_state.json` `lineage`/
`researcher_memory` content built from the same starting point by two
independent stochastic search runs. There is no principled way to
line-merge two different RNG draws of evolutionary search into one
coherent history, and no tooling in this repo attempts it (nor should it —
`lineage` is an append-only audit trail of a live process, not a
mergeable artifact like a lockfile).

Rather than force a text-level merge or discard either side's real
30+ minutes of compute, this session took the already-pushed
`origin/main` state as canonical (`git reset --hard origin/main` after
confirming the only divergence was in `live_state.json`/`index.html`/the
`AGENTS.md` insertion point — genome, broker, and journal were identical on
both sides, since neither run promoted) and ran 45 more generations on top
of that real, canonical base instead of re-litigating the discarded batch.
This restores the intended ~60-generation combined depth for this weekend
slot (15 by the concurrent 3-hourly check + 45 here = 60 total generations
of real search run against v3 in this UTC hour), without discarding either
session's actual work or inventing a synthetic merge.

**Numbers that describe the actual committed history** (the standalone
60-gen batch that lost the race is not part of it and its specific figures,
e.g. its 42/60 raw-beat ratio, should not be cited going forward):

- Concurrent 3-hourly check (`runs/2026-09-12-0713-evolve-batch-v3.md`):
  11465 → 11672 candidates, 12/15 generations beat champion fitness 1.508.
- This session's continuation: 11672 → 12298 candidates, 22/45 generations
  (49%) beat champion fitness 1.508, tied 3, lost 20 — an ordinary ratio,
  not the livelier one the discarded run happened to show.
- Combined for the slot: 11465 → 12298 (833 new candidates), boldness/
  stagnation counter 822 → 882. Champion's fold-aggregate fitness held flat
  at 1.508 throughout both pieces — no promotion.
- `holdout-pressure` draw count: 257 (session start) → 259 (after the
  3-hourly check's 15 gens) → 261 (after this session's 45 more) — 4 new
  draws total this slot, every one lost, margin unchanged in shape
  (~6.64-6.68).

## The flake, revisited

Today's earlier 3-hourly check (~03:50-04:24 UTC,
`runs/2026-09-12-0424-evolve-batch-v3.md`) reported a one-off, non-
reproducible failure in `test_run_from_files_matches_bundle_output` for the
`holdout-pressure` and `holdout-margin-audit` parameters — the `after ==
before` byte-identity assertion on the real `live_state.json` failed once,
then passed cleanly on immediate re-run and on a full second suite run, with
no code change and no stray process found.

Before starting this session's own batches, re-checked the code path
directly rather than trying to force a reproduction: grepped every
`acct.save(...)` call site in `evotrader_bundle.py` (four total — `tick`,
both `evolve` save points, and `review-hard-calls --tick`) and confirmed
neither `holdout-pressure` nor `holdout-margin-audit` is anywhere near one;
both read `acct.lineage` only, exactly as their own code comments claim. No
other test file in the suite touches the real `live_state.json` at all
(grepped for it) — every other test uses the `EVO_STATE`-scratch-file
discipline `tests/test_run_from_files_matches_bundle.py`'s own docstring
describes. So there is no in-repo mechanism that could produce the observed
byte difference; whatever happened was external to this codebase (most
likely sandbox filesystem timing, not a real race in the trading code).
Both full-suite runs this session (391/391 after the 60-gen attempt, and
391/391 again after the 45-gen continuation) came back clean — no
recurrence. Not treating this as an open item needing a mechanical fix —
there is nothing to fix without a reproducible mechanism, and building
retry/locking machinery around a single unreproduced event would be solving
a problem that hasn't actually been shown to exist. Flag it again only if it
recurs a second time.

## Verification

- `python3 -m pytest -q`: 391/391 on every run this session (baseline before
  each evolve invocation, and after) — the earlier same-day flake did not
  recur either time.
- Direct top-level key diff of `live_state.json` (baseline snapshot before
  the 45-gen continuation vs. after): only `lineage`/`researcher_memory`/
  `updated` changed; `genome` (still v3), `broker`, `journal`,
  `hard_call_reviews` byte-identical.
- Constitution verified `726dfa4bac85891a` unchanged throughout.
- `tools/edit_bundle_module.py verify`/`sync --check`: both clean.
- Dashboard (`index.html`) rebuilt against the final, correctly-merged
  state; genome tile and challenger tally (12298) confirmed correct.
- Confirmed before resetting to `origin/main` that the only real divergence
  from this session's discarded local commit was `live_state.json`/
  `index.html`/the `AGENTS.md` insertion point — `genome`, `broker`, and
  `journal` were byte-identical between the discarded commit and
  `origin/main`, so nothing about the live trading state itself was at risk
  from taking `origin/main` as canonical.

## What's next

- Genome still v3 (1d) live, untouched — no promotion this session.
- The re-measured moderate/risky consult echo (item under "Measured
  2026-08-16") is reduced but not resolved — worth another check after the
  next real promotion, same as always, rather than a scheduled re-audit.
- Items 2/5/6 remain the owner's call, no new input this session.
- The `holdout-pressure`/`holdout-margin-audit` test flake from earlier today
  did not recur (twice checked this session) and has no identified in-repo
  mechanism; no action queued unless it happens again.
- No new tooling proposed for the push-collision case encountered here — a
  real divergence in `live_state.json` between two concurrent evolve batches
  is rare (this is the first time it's been hit; prior AGENTS.md collision
  entries were all the stale-local-branch kind `tools/git_sync.py` already
  handles) and the resolution taken (defer to whichever real batch pushed
  first, continue searching from there) is simple enough not to need
  automation yet. Worth automating only if this starts recurring.
