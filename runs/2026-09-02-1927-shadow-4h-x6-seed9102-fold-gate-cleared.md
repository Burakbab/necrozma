# 2026-09-02 ~19:27 UTC — 3-hourly check: a fresh unconstrained-search seed clears the fold gate for the first time (still fails holdout)

## Context

AGENTS.md item 2's fold-1 cold-start-drawdown thread has, since 2026-08-31,
tried and closed every hand-picked single-lever fix (SCALE, `consv1` alone,
various ramp/cap/boost genes) and, at 2026-09-02 ~06:46-07:15 UTC, ran one
generation of unconstrained `Researcher`-driven search on the *unpatched*
`x6` seed (seed 9101): its own best idea also hard-failed the real
`dd_corrected_stats()` drawdown gate. That entry left "more generations/seeds
of the same unconstrained search" as an untried, non-owner-decision-gated
option under item 2 — this session picked that up with a fresh seed.

Also checked before starting: `live_state.json`'s `updated` timestamp
(2026-09-02T00:22:38Z) matches today's already-handled 00:20 UTC daily tick
(`runs/2026-09-02-0020-daily-trading.md`) — nothing new to trade this cycle.
Every other AGENTS.md "Next steps" item is currently blocked on a human/owner
call (item 2's own accept-the-stack-vs-redirect fork, item 4 has zero pending
hard calls, item 5 needs sign-off, item 6 needs a data-source pick); item 7 is
feature-complete. `python3 -m pytest -q` 338/338 baseline before touching
anything, confirmed clean.

## What ran

```
python3 tools/shadow_4h_ramp_generation.py --recipe x6 --generations 2 --seed 9102
```

A fresh seed (9102, distinct from 06:46-07:15 UTC's 9101), 2 real
`EvolutionRun.generation()` calls against real 4h data, the unpatched `x6`
seed genome (no hand-picked `consv1`/`trailing_stop`/ramp genes). Read-only:
this tool never calls `save()`/`promote()` against the live account —
`live_state.json` untouched throughout, verified unmodified after the run.
Took ~28 minutes (1699s) total for 2 generations against 4h data — in line
with this thread's previously-noted 6-27 min/generation range for 4h shadow
work.

## Result

Generation 1 (16 proposals): all top candidates hard-fail the real gate
(`state/lineage.jsonl` rejection reason: `"challenger failed a hard gate (too
few trades, too short, or drawdown > 40%)"`), consistent with every prior
entry in this thread.

**Generation 2 (6 new proposals, 22 cumulative tried against this seed
champion) is different: the top candidate actually cleared the fold-aggregate
hard gate for the first time in this entire unconstrained-search sub-thread**
— `agents.consult_moderate.genes.rsi_hi: 72.0 -> 91.8463` +
`agents.risk_judge.genes.cash_floor_pct: 0.05 -> 0.479` (i.e. loosen
`consult_moderate`'s exit RSI ceiling and force ~48% of the portfolio to sit
in cash at all times), fold-aggregate fitness 1.2314 vs. the seed champion's
own -2.486 (itself a hard-fail sentinel — this `x6` seed is the same
already-known-hard-failing genome every prior entry in this thread has
used as its starting point). It then reached the sealed holdout check and
**failed there**: holdout fitness -1.808 vs. champion holdout fitness
-0.281, short of the required margin (`"failed sealed holdout: -1.808 did
not clear champion -0.281 + margin 2.355 (1 cumulative draws against this
holdout)"`). Two other generation-2 candidates hard-failed the fold gate the
same way generation 1's did.

## Reading

**This nuances, but does not reverse, the 06:46-07:15 UTC finding.**
"Unconstrained search on the unpatched seed always hard-fails the real gate"
was true for one generation/one seed; it is not true in general — a second
seed's second generation found a genome (blunt cash-floor de-risking, not a
targeted drawdown fix) that clears the *fold* gate. But it still lost on the
*holdout*, and by a wide margin (holdout fitness -1.8 vs. champion's already-
weak -0.28) — consistent with the cash-floor patch being a crude "hold less
of the account at risk" move that happens to duck fold 1's specific drawdown
window without adding real edge elsewhere. **Net effect on item 2's open
question is small**: the search can occasionally clear the fold gate this
seed champion has died on before, but nothing found so far (across 3 total
generations now run on this seed, 2 seeds) has cleared *both* fold and
holdout. This is one more data point toward "more generations/seeds keep
finding near-misses, not real solutions" rather than toward "a bigger search
budget would obviously solve this" — but 3 generations across 2 seeds is
still a small sample; not treated as closing option (i) here.

## What this does not change

- Item 2's owner-decision fork (accept the full `consv1 + trailing_stop +
  ramp` stack and move toward a real promotion attempt, or redirect effort)
  is untouched — still flagged for the next session/owner call, not decided
  here.
- No code changed this entry — pure use of already-committed, already-tested
  tooling (`tools/shadow_4h_ramp_generation.py`, unmodified). `python3 -m
  pytest -q` not re-run after (no code touched); baseline 338/338 confirmed
  before this entry's work started.
- `live_state.json` untouched, no protected file touched, no
  `AMENDMENTS.md` row needed (no constitution change). Genome still v3 (1d)
  live, untouched.

## Next

If another session picks up option (i) again: try a third seed, or widen
`n_blind`/generations per run, and specifically watch whether any future
fold-gate-clearing candidate is ever a *targeted* drawdown fix (touches
Guardian/risk-judge sizing genes near the fold-1 window) rather than another
blunt de-risking move like this one — that would be the more informative
signal for whether unconstrained search is a real alternative to the
hand-built stack.
