# Stress-testing the holdout backstop — 6 more generations, 15 more flip candidates, none came close

**3-hourly self-improvement check, ~04:05 UTC.**

## Why

Today's bar (2026-08-27) was already traded by the dedicated 00:20 UTC daily
run before this session started (`live_state.json` `updated`
`2026-08-27T00:21:49+00:00`, tick 13) — nothing to do on the trading side.
Picked up the sharpest open item from the 00:52 UTC entry directly: "the
stress-test case — keep drawing generations until a flip candidate's holdout
fitness lands close to the champion's, to see whether the holdout margin
still holds it back or a close call gets through." Both flip candidates
found so far (21:52 UTC: 2, 00:52 UTC: 2) were decisively bad on the holdout
(-0.259, -0.373, -0.230, -0.654 vs champion 0.176–0.638), not a real test of
the margin's actual strength.

## Method

Same scratch-only, read-only script pattern as the 21:52 UTC / 00:52 UTC
entries, extended to run 6 consecutive real generations instead of 1, so
more flip candidates could be found and their holdout scores compared:

1. Loaded the real `live_state.json` via `core.live.LiveAccount.load()` —
   champion v3, `researcher_memory` resumed (182 already-tested proposals,
   stagnation 12, holdout_draws 13 at the start).
2. For 6 consecutive generations: ran one fresh real generation's worth of
   work (real `Researcher.propose` with `seed=None`, real
   `Evaluator.evaluate`, real market data, `n_blind=14`), accumulating the
   `exclude` set across generations the way `EvolutionRun` really does, so
   generation 2 doesn't re-draw generation 1's proposals.
3. Each generation: computed the champion's fold-aggregate fitness at 7
   as-of shifts (same method as `fold-date-sensitivity --shift 7`), then for
   the top-3 finite candidates re-ran `constitution.accepts()` at all 7
   shifts, swapping only `champion_score`.
4. For every candidate that flipped (accepted the gate on some shifts,
   rejected on others), took its first accept-verdict shift, rebuilt that
   shifted "as-of" market window, and called the real
   `Evaluator.holdout_check()` for both champion and challenger on it,
   judged with the real `constitution.holdout_accepts()` at
   `n_draws = 13 + 1` (matching what a real first holdout draw this
   generation would count as — draws aren't incremented across the 6
   generations in this script since none of them actually reach the real
   loop's holdout gate in sequence; this measures each flip candidate's
   individual holdout draw at the same fixed multiple-testing pressure the
   real lineage currently carries).

One caveat worth naming: this script re-proposes against the *same*
unshifted "now" champion baseline every generation (it doesn't advance the
champion even when a candidate would have been accepted) — deliberately, to
keep isolating the specific question (does *any* flip candidate's holdout
score get close), not to simulate 6 sequential real `evolve` calls.

```
python3 <scratch>/stress_test_holdout_backstop.py
```

## Result

**15 flip candidates found across 6 generations** (2-3 per generation, out
of 3 top-ranked candidates checked each time) — a much larger sample than
the 2+2 from the prior two sessions. **All 15 failed the sealed holdout,
none close to passing.** The closest: a candidate combining
`regime_ma`/`consult_conservative.conviction_scale`/`z_buy_below`/
`consult_moderate.min_rank_mom`/`rsi_hi`/`risk_judge.max_position_pct`/
`min_conviction`/`superior_judge.max_new_positions_per_bar` — holdout
fitness champion 0.176 vs challenger -0.054, gap 0.231. Still nowhere near
the 4.595 margin it needed to clear. Every other gap ranged 0.421 to 2.498.

Champion's own shift-fitness spread was identical every generation this
session (0:1.054, 1:-1.652, 2:0.843, 3:1.245, 4:0.919, 5:1.126, 6:1.396,
spread 3.048) — expected, since it's computed from the same real market data
snapshot each time (the script doesn't refetch between generations), and
matches the same order of magnitude as every prior measurement of this
swing. All flip candidates' accept-verdict shift landed on shift 0 or shift
1 specifically — the same two anomalous low-champion-score days
(fold-aggregate -1.652 and, via a different low reading, the day that gives
champion holdout 0.176) every prior session in this thread also converged
on, not a new pattern.

## Reading

19 flip candidates now checked across three independent sessions (2 + 2 +
15), zero have passed the sealed holdout, and the closest gap seen (0.231)
is still roughly 20x smaller than the required margin (4.595) — the margin
isn't being approached, let alone threatened. This is a meaningfully
stronger result than the prior two sessions' 2-candidate samples: it isn't
just that the two candidates checked so far happened to be bad, it's that
in a 15-candidate sample spanning 6 independent generations, nothing came
remotely close. The stress test this thread has been building toward is
answered, at least for the current lineage state (14 cumulative holdout
draws, margin 4.595): the holdout gate's own accumulated-draws multiple-
testing margin is currently strong enough that the fold-aggregate gate's
date-sensitivity has no realistic path to letting a bad promotion through,
not just a lucky-so-far one.

The caveats from the 00:52 UTC entry still stand and aren't resolved by
more samples at the same lineage age:

- This margin (4.595) is a function of 14 accumulated holdout draws against
  this specific champion. A younger lineage — right after a promotion, with
  few or zero accumulated draws — would face a much smaller margin (at
  `n_draws=1`, `required_margin` collapses toward `HOLDOUT_SIGMA *
  sqrt(2*ln(2)) ≈ 2.35`, roughly half of today's 4.595) and correspondingly
  less protection from this exact mechanism. This thread has only ever
  tested the backstop at v3's current, well-aged draw count.
- Every flip candidate checked so far (all 19) has been genuinely weak on
  the holdout, not a strong genome that got unlucky. Whether a genuinely
  strong candidate (one that would clear even a large margin on most days)
  can also be shift-sensitive on the fold-aggregate gate is untested — this
  thread has only sampled candidates the real Researcher actually proposes
  against the current champion, which apparently doesn't produce that
  combination often, but "often" is not "never."

**Recommendation for whoever picks this thread up next**: given 19/19
decisive rejections and a 20x-margin gap on the closest case, further
identical-method batches are unlikely to be worth another session — the
marginal value of "still true" is low here, same judgment call the
2026-08-21 fold-cap thread made about a different mechanism. If this stays
worth pursuing at all, the sharper next step is the lineage-age question
above (what does the margin look like right after a fresh promotion, not at
14 draws deep) rather than another same-method batch at the current draw
count.

## Verified safe

- No code changed in the repo — script lives only in the session scratch
  directory, never touches `evotrader_bundle.py`, `loop/`, `constitution/`,
  `core/`, or any committed file. Never called `Genome.promote()` or
  `acct.save()` (built parallel gate/holdout checks by hand instead of
  calling the real loop). No test suite run needed (same precedent as prior
  no-code-change diagnostic sessions).
- `live_state.json` unchanged: md5 `1add861014e44aa69e814491cbd22e00` before
  and after, still reflects tick 13 from the 00:20 UTC daily run.
- `evotrader.manifest` md5 unchanged: `0bf3a7d9411ee692d0a9f152a7533803`.
- `tools/edit_bundle_module.py sync --check`: bundle already matches real
  files, no changes.
- `git status --short` clean before and after this note.
- Today's bar already processed before this session started (`tick` not run
  this session, no double-trade).
- No genome promotion — no README `## Status` update needed.
- One real bug caught and fixed before this counted as a real run: an
  earlier draft of the script called `LiveAccount.load()` with no path
  argument, which resolves to `core.live.STATE_PATH`
  (`state/live/account.json`, which doesn't exist in this repo — it uses
  `live_state.json` at the repo root, same as `evotrader_bundle.py`'s
  `EVO_STATE` env var default) — silently falling back to
  `Genome.champion()`, which loaded the seed genome v1, not the real live
  champion v3. Caught by a 1-generation timing/sanity check before running
  the full 6-generation batch (printed `champion v1` instead of `v3`, and
  `researcher_memory` showed 0 tested instead of 182) — the real run above
  used the correct explicit path and was verified to load v3 with the full
  resumed memory before any of the 6 generations ran.

## Next, if this thread stays worth pursuing

- The lineage-age question: what the holdout margin looks like at a small
  `n_draws` (simulate a just-promoted champion) rather than today's
  14-draws-deep v3 — the sharper remaining gap this session's larger sample
  didn't close.
- Whether smoothing the champion's fold-aggregate baseline across several
  trailing as-of dates is still worth doing given how strongly this session
  reinforces the backstop — weaker case than ever now (19/19 rejections,
  closest gap 20x under the margin), but see the lineage-age caveat above.
- The day-1-allocation-redesign question (proportional/ranked instead of
  greedy-first-come) and the window-5 `anatomy` post-mortem, both still open
  from the 2026-08-26 09:50 UTC entry, untouched by this thread.
