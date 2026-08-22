# 2026-08-22 18:54 UTC — 3-hourly check: `succession-audit` diagnostic

## Context

Today's bar already processed by the 00:20 UTC daily run (`live_state.json`
`updated` timestamp `2026-08-22T00:21:18+00:00`). `tick` not run this session,
no double-trade. `review-hard-calls` checked: 0 pending.

Three earlier sessions today (10:15, 13:22, 16:29) tracked the
dd-corrected-gate vacuous-accept pattern via repeated shadow-evolve rounds
against the live champion, and each closed with the same unresolved thread:
"whether v3 itself should be demoted or re-evolved now that its true drawdown
is visible is explicitly NOT decided... picking what replaces a demoted
champion (revert to v2? a fresh search from the seed?) is its own design
question." Four sessions in one day had flagged this without adding the one
fact a real decision would need: whether the other two real champions this
account has had would even pass today's dd-corrected drawdown gate if
reinstated, or whether v3's problem is shared by every past champion.

## What was built

New read-only CLI `succession-audit` (`evotrader_bundle.py`, plain-script CLI
section only — `git diff --stat` confirms a pure addition, no `_SRC[...]`
lines touched, `tools/edit_bundle_module.py verify` round-trip clean,
`py_compile` clean). For every real champion this account has had (v1, v2,
v3, discovered from `acct.lineage`'s own accepted-promotion records via the
already-tested `_reconstruct_champion_genome`), reports side by side:

- **fold-agg fit**: `aggregate_fitness` a fresh `Evaluator.evaluate()` call
  against today's data would give this genome as a brand-new candidate.
- **dd-corr fit**: `fitness()` of that same `evaluate()` call's merged stats
  after `dd_corrected_stats()` — the exact number `accepts()` gates a real
  promotion decision on since the 2026-08-22 weekend all-hands fix.
- **full-hist maxDD/fit**: one continuous `[0, 1]` replay, no fold
  boundaries at all — the same "true" number `universe-perturb`/`drawdown`/
  `anatomy`/`fold-dd-blindspot` report.
- **hard-fail?** and **excess ret** (vs buy-and-hold, full history).

Composes only already-tested `_reconstruct_champion_genome`/
`Evaluator.evaluate`/`dd_corrected_stats`/`run_backtest` — no engine or
constitution change, no new pure function, same precedent as every other
diagnostic in this file (`fold-scheme`, `fold-dd-blindspot`, etc.). No new
test file for the same reason. Read-only: never touches `live_state.json`,
never proposes or applies a promotion.

## Result

```
   version fold-agg fit dd-corr fit full-hist maxDD full-hist fit hard-fail? excess ret
---------------------------------------------------------------------------------------
        v1       -2.657        -inf          -54.4%          -inf        YES    -122.7%
        v2       -2.504        -inf          -38.1%         0.132         no     -77.1%
 v3 (live)        1.126        -inf          -46.5%          -inf        YES    +110.9%
```

Headline: **none of the three real champions this account has ever promoted
would currently clear the dd-corrected fold-aggregate gate if re-evaluated as
a fresh candidate today.** v1 and v3 fail outright even on the simpler
full-history test. v2 is the interesting case and the reason this diagnostic
is worth more than "the full-history number already answers this":

- v2's **true full-history maxDD is -38.1%**, under the 40% hard-fail line —
  by that number alone, v2 looks like a safe reinstatement candidate.
- But v2's **fold-merged maxDD is -40.1%**, driven entirely by fold 2's own
  independently-backtested local peak-to-trough (fold 1: -22.2%, fold 2:
  **-40.1%**, fold 3: -21.0%) — worse than either the continuous search-span
  replay (-38.1%) or the continuous full-history replay (-38.1%).
  Cross-checked directly (scratch script, not committed, composes the same
  already-tested functions): `dd_corrected_stats()` takes `min(fold-merged,
  continuous)` by design ("can only tighten the gate, never loosen it" —
  AGENTS.md item 2, weekend all-hands entry) — so when the fold-merged number
  is *itself* an artifact that overstates the true drawdown, the correction
  has no way to recover the truer, better continuous number. It can only
  keep or worsen a pessimistic fold-local read, never replace it with a more
  accurate one.

This is the **opposite direction** from the original `fold-dd-blindspot` bug
(fold-merged *understating* a true continuous drawdown that spans a fold
boundary, invisible to the gate). Here fold-merged *overstates* the risk
relative to the true continuous number, because each fold's NAV rebases to a
fresh peak at its own boundary — a decline that would be a modest fraction of
a long-accumulated peak in continuous replay becomes a much larger fraction
of the lower, freshly-reset local peak. `dd_corrected_stats()`'s `min()`
design (correctly conservative for the blind-spot direction) has no
mechanism to catch this direction — it only ever tightens, never loosens,
so a fold-local overstatement passes straight through uncorrected.

## Verified safe

- `py_compile` clean, `tools/edit_bundle_module.py verify` round-trip clean
  (bundle byte-identical after extract/reinsert of every module).
- `git diff --stat`: `evotrader_bundle.py` only, 73 insertions, 0 deletions
  outside the docstring's one-line help addition — confirmed no `_SRC[...]`
  line touched.
- Full suite still 192 passed (unchanged — no new pure function to test).
- `live_state.json` md5 unchanged throughout (`3f71d6ab111ecd646eda9e0e595a9970`),
  `evotrader.manifest` md5 unchanged (`0bf3a7d9411ee692d0a9f152a7533803`),
  `constitution verified 8b74865634b1db07` unchanged on every invocation.
- No promotion, shadow or otherwise (no `evolve` run this session) — no
  README Status change needed.

## Not decided

This diagnostic answers a factual question the demotion/rollback thread
needed and had not yet asked ("would the alternatives even pass"); it does
not answer or attempt to answer whether v3 should actually be demoted, or
what should replace it if so. That remains explicitly the owner's call, same
standing note as every session today. The practical reading it adds: reverting
to v2 is **not** a clean fix even though its raw full-history number looks
fine — it fails the same gate v3 does, for a different, now-documented reason.
A fresh search from the seed (or building the `dd_corrected_stats` fix's
missing case — recovering a fold-local overstatement toward the true
continuous number, not just correcting understatement) are the two
directions this leaves open, neither attempted here.

## Next

- If the owner does open the demotion/rollback design pass, this table (and
  the fold-2-rebasing mechanism specifically) is the fact base to start from
  — no real champion currently has a clean pass.
- The `dd_corrected_stats()` `min()`-only design is now known to have this
  one-directional blind spot (can't loosen an overstated fold-local number
  toward a truer continuous one). Not urgent to fix on its own — the
  overstated direction is conservative, not unsafe — but worth noting
  alongside the original blind-spot fix's own documentation if anyone
  revisits that function.
- `succession-audit` re-runs automatically pick up any future promotion
  (reads `acct.lineage` for the full version list, same pattern as
  `--also-version` elsewhere) — no maintenance needed to add a fourth
  champion later.
