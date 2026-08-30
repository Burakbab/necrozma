# v3 demotion/rollback design pass — 2026-08-30 ~18:51 UTC

## What this session did

Scheduled 3-hourly check. Today's daily bar was already handled by the 00:20
UTC run (`live_state.json` `updated` 2026-08-30T00:48:35+00:00, genome
version still 3) — nothing new to trade this cycle. `review-hard-calls`: 0
pending. This slot went to a design pass on the question this file has
raised and reaffirmed, unresolved, every day since 2026-08-22: **should
champion v3 be demoted or rolled back now that its true continuous drawdown
is known to exceed `MAX_DD_HARD_FAIL`?** Per grep, this exact phrase
("demotion/rollback") appears in 19 places across `AGENTS.md`'s history —
raised 2026-08-22, sharpened across five sessions that day, referenced again
2026-08-23/24/25, and reaffirmed in every daily discussion through
2026-08-30 without a single session stepping back to weigh the accumulated
facts and write a recommendation. That is exactly the gap the 2026-08-30
06:00 UTC weekend all-hands closed for the fitness-vs-excess-return
question; this write-up does the same thing for this one.

Baseline verified before starting: `git status --short` clean (after
pulling 8 commits from earlier today), `python3 -m pytest -q` 243/243,
`md5sum live_state.json` (`81922c6011c986449f635dbf43553d0e`) recorded and
unchanged throughout — nothing run this session writes to it. No code
changed, no constitution touched, no `AMENDMENTS.md` row needed (same as
the 06:00 UTC precedent: a policy recommendation without a gate change).

## The question

The 2026-08-22 weekend all-hands fixed a real structural blind spot: the
fold-aggregate `max_dd` `MAX_DD_HARD_FAIL` (0.40) gates on is the worst of
three *independently* backtested folds' own local peak-to-troughs, which is
structurally blind to a drawdown spanning a fold boundary. The fix
(`dd_corrected_stats()`, `min()` of fold-merged and one continuous replay)
is strictly more honest and was applied going forward inside
`EvolutionRun.generation()`. Its side effect, observed and left undecided at
the time: champion v3's own corrected max_dd is -46.5%, over the 40% line —
a fact that was always true, just invisible to the old gate. `fitness(v3)`
has read `-inf` inside `accepts()` ever since, for every generation, real or
shadow.

No code path in this system ever removes a sitting champion. `accepts()` and
`holdout_accepts()` only run when a *challenger* is being evaluated against
the current champion; nothing periodically re-checks whether the champion
itself would still be accepted today. So v3 has kept trading, unaffected in
practice — the `-inf` only vacuously satisfies the merged-fitness-regression
check inside a challenger comparison (already measured: ~2% of real shadow
candidates ride this vacuous path to the sealed holdout, none incorrectly
promoted, see item 2's history). The open question was always narrower than
"is the gate honest" (yes, now) — it is "given the gate says the sitting
champion would fail if it were a new candidate today, should something
_act_ on that," and if so, what.

## Evidence base, synthesized

**No rollback/demotion mechanism exists.** Confirmed again this session —
no code anywhere flattens the account, resets the genome, or halts trading
based on a champion's own fitness or drawdown. Building one is a real
engineering task, not a flag flip.

**`succession-audit`, re-run fresh this session** (fresh 27-symbol replay,
`live_state.json` untouched):

```
   version fold-agg fit dd-corr fit  trust-cont fit full-hist maxDD full-hist fit hard-fail? excess ret
-------------------------------------------------------------------------------------------------------
        v1       -0.151        -inf            -inf          -54.4%          -inf        YES    -115.7%
        v2        0.112       0.234           0.234          -38.1%         0.092         no     -73.8%
 v3 (live)       -1.669        -inf            -inf          -46.5%          -inf        YES     +68.2%
```

Three findings this table has held steady since 2026-08-22, reconfirmed with
today's data:

1. **v3 hard-fails** the same corrected gate a fresh candidate would be held
   to (-46.5% continuous maxDD, over the 40% line).
2. **v1 also hard-fails outright** (-54.4%) — not a clean fallback either.
3. **v2 is the genuinely interesting case**: its full-history maxDD (-38.1%)
   clears the 40% line, but its fold-merged number (driven by fold 2's own
   locally-rebased peak, independent of the true continuous drawdown) still
   pushes its dd-corrected fitness to a real, finite, but weak 0.234 — not a
   hard-fail, but not a strong number either. (2026-08-24's
   `dd_trust_continuous_stats()` two-sided diagnostic gives it the identical
   0.234 today, so the two corrections happen to agree on v2 as of this data
   snapshot — a coincidence of which window is current, not a settled
   property, per that entry's own note.)

**The new fact this session's fresh run adds, not measured together with
the drawdown picture before**: v3's full-history **excess return over
equal-weight buy-and-hold is +68.2%** — strongly positive, and the only
positive number of the three. v1 and v2 are both deeply negative on the same
measure (-115.7%, -73.8%). This connects directly to the 2026-08-30 06:00
UTC weekend all-hands' own closed thread (fitness vs. excess-return as a
selection metric): that write-up found the two metrics have never once
disagreed on a real promotion decision. This table is the same fact
restated for the demotion question specifically — **whichever of the two
selection metrics you'd rather use, v3 is the best of the three real
champions on both**, despite being the only one that hard-fails the
drawdown gate. There is no fallback candidate that is both safer on
drawdown and better on return; v2 is less bad on drawdown but far worse on
everything else, v1 is worse on both axes.

**Paper account, not real capital.** Reconfirmed from `## No credentials,
anywhere`: prices come from a public feed, the ledger is `live_state.json`,
there is no brokerage account. The 40% `MAX_DD_HARD_FAIL` line exists to
stop the *search* from crowning a candidate that took catastrophic risk to
get lucky returns — a search-time discipline. It was never framed anywhere
in this file or the constitution's own docstrings as a live-trading circuit
breaker for a sitting champion; that role is `CIRCUIT_BREAKER_DD` (0.25,
already wired into `PaperBroker.mark()` and firing live, independent of
this question entirely).

## Options considered

**A. Build an automatic demote-on-breach mechanism.** When a champion's own
freshly-recomputed corrected fitness reads `-inf`, revert to some prior
state. Rejected: `succession-audit` shows there is no strictly-better
prior champion to revert *to* — both alternatives are worse on the metric
that matters (excess return) and one of them (v1) is worse on drawdown too.
An automatic mechanism with no good target either has to fall back to the
untrained `SEED_GENOME` (a real regression — 2026-08-23's fresh-seed shadow
run found the raw seed goes 16 generations without a single promotion) or
halt trading entirely (throws away the one champion that has ever beaten
benchmark). Either destination is a worse outcome than doing nothing, so
automating the trigger without a good destination is automating a
mistake.

**B. Manually revert to v2 now**, since it's the only one of the three that
doesn't hard-fail outright. Rejected on the evidence above: v2's
full-history maxDD passing is closer to an artifact of `min()`'s
one-directional blind spot (2026-08-24 finding) than a clean pass, and its
excess return (-73.8%) is dramatically worse than v3's (+68.2%). This would
trade a real, working, benchmark-beating champion for a fold-fragile one
that has never beaten benchmark over its own full history, to satisfy a
drawdown line that v2 itself only marginally and ambiguously clears.

**C. Status quo: no demotion, no automatic mechanism, treat
`MAX_DD_HARD_FAIL` as a prospective gate on new candidates, not a
retroactive one on sitting champions.** This is close to what already
happens by default (nothing in the code ever forces a demotion), made
explicit and deliberate instead of an unstated default. The reasoning: the
gate's job, by its own docstring and every amendment-log entry that has
touched it, is to stop the *search* from mining noise into a false
promotion. It has never been framed as a policy for un-crowning an existing
champion when a later-discovered measurement correction makes its own past
performance look worse under today's stricter accounting — that is
retroactive rule application, not the gate doing its designed job. Real
evolution (daily, live) keeps searching for a genuine replacement the whole
time this stands; if one ever clears `accepts()`/`holdout_accepts()`
against v3 for real, it is promoted automatically, no policy change needed
for that to happen.

## Recommendation: C, status quo, with three concrete revisit triggers

No code change. No constitution change. No `AMENDMENTS.md` row (this
doesn't touch the gate itself, and the "gates apply prospectively to new
candidates, not retroactively to a sitting champion" reading is consistent
with how the code already, silently, behaves — this write-up makes that
default an argued position rather than an unexamined one).

Concrete, checkable triggers for revisiting this, named so a future session
doesn't have to re-derive them:

1. **A real (non-shadow) `evolve()` run produces a challenger that clears
   `accepts()` and `holdout_accepts()` against live champion v3.** This
   needs no new mechanism — the existing gates already promote it
   automatically — but it's worth flagging explicitly here because when it
   happens it retires this whole question by making it moot, not because
   any new code is required.
2. **`succession-audit` (or a future champion via the same diagnostic) ever
   shows a candidate that is both closer to clearing the corrected drawdown
   gate cleanly *and* has better full-history excess return than v3.**
   Today's table shows no such candidate exists among the three real
   champions this account has ever had; the moment one does, "revert" stops
   being strictly worse on both axes and becomes a genuine decision worth
   raising to the owner.
3. **The live paper account itself realizes a real (not backtested)
   drawdown approaching `CIRCUIT_BREAKER_DD` (0.25) or beyond.** That is a
   distinct, already-armed live safety mechanism (forced flatten + 20-bar
   cooldown), independent of this question, but a real trip is the kind of
   live evidence — not another backtest replay of the same fixed historical
   window — that would make re-litigating this design pass urgent rather
   than a background hold.

None of the three has fired. Until one does, this question moves from "the
owner's call, unstarted" to "the owner's call, argued, with a status-quo
recommendation and named triggers" — the same closure item 0's
fitness-vs-excess-return question got on 2026-08-30 06:00 UTC.

## Verified safe

- `python3 -m pytest -q`: 243 passed (confirmed at session start, before any
  diagnostic ran).
- `succession-audit` is read-only (never touches `live_state.json` or the
  champion) — same guarantee as every other diagnostic in `## Where things
  live`.
- `md5sum live_state.json` = `81922c6011c986449f635dbf43553d0e` before and
  after this session's only two commands (`succession-audit`,
  `review-hard-calls`) — unchanged.
- `evotrader.manifest` untouched, `constitution verified 8b74865634b1db07`
  on every invocation.
- Today's bar already processed by the 00:20 UTC daily run before this
  session started — `tick` not run this session, no double-trade risk.
- `review-hard-calls`: 0 pending.
- No genome promotion — no README `## Status` change needed.
- `git status --short` clean at session end besides this note and the
  `AGENTS.md` update in the same commit.

## Next

Nothing queued from this specific thread beyond the three triggers above.
Whoever next has a 3-hourly slot: check `succession-audit`'s numbers only
when something has actually changed (a new promotion, a new champion, or a
material live drawdown) — re-running it on an unchanged live champion just
re-derives the same table from a slightly shifted window, which is exactly
the diminishing-return pattern this file has already flagged for several
other closed measurement threads.
