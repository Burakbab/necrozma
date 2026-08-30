# Does lone_voice_scale > two_agree_bonus contribute to the risky-direction skew?

2026-08-30, ~03:50-05:18 UTC (3-hourly check)

## Why

The 00:46 UTC hard-call review (tick 16) flagged an open observation without
acting on it: champion v3's evolved `risk_judge` genes have `lone_voice_scale`
(1.4791) higher than `two_agree_bonus` (1.2), so a solo-conviction buy can
legitimately outrank a two-consult-agree candidate. This is structurally the
same "favor confident-minority over corroborated-consensus" shape as the
risky-direction skew the disagreement-sweep thread (2026-08-29, several
entries) keeps finding — raw `ranking_fitness` disagreeing with excess-return
in the "risky" direction (fitness ranks a challenger above champion, excess
return doesn't) 61-89% of the time it disagrees at all, never the reverse
majority. The 00:46 UTC entry named this "worth a future session checking
whether this gene pairing is a contributor" without attempting it. This
session attempts it.

## What

One-off scratch script (not a new CLI command — a genuinely counterfactual
genome doesn't belong as a permanent tool the way `disagreement-sweep`'s
`keep_frac` sweep did), same discipline as every throwaway sandbox script in
this thread: never calls `Genome.save()`/`.promote()`, never touches
`live_state.json`, deleted after extracting results.

Built `g1 = g0.child([("agents.risk_judge.genes.lone_voice_scale",
g0.gene("risk_judge", "two_agree_bonus"))], ...)` — champion v3 with
`lone_voice_scale` clamped down to exactly equal `two_agree_bonus` (1.2 ==
1.2), neutralizing the specific inequality flagged, everything else
byte-identical to the real champion. Ran `loop.evolve.disagreement_scan`
against both `g0` (real) and `g1` (counterfactual) with the **same**
`Researcher(seed=4242)`, same 27-symbol/4-year universe, same
`generations=15, n_blind=14`, both starting from a blank `researcher_memory`
(fresh, not `g0`'s real memory — `g1` is a hypothetical genome with no lineage
of its own, so seeding only `g0` from the real memory would have confounded
the comparison with unequal starting `tested`/`stagnation` state).

## Result

| genome | champ fold-fit | fold n | fold dis% | risky | cons | risky share | ho n | ho dis% | risky | cons |
|---|---|---|---|---|---|---|---|---|---|---|
| real (lone=1.4791>two=1.2) | -1.669 | 221 | 44.8% | 90 | 9 | 90.9% | 44 | 0.0% | 0 | 0 |
| counterfactual (lone=two=1.2) | -2.637 | 221 | 35.7% | 68 | 11 | 86.1% | 42 | 2.4% | 1 | 0 |

Two things, not one:

1. **The risky-direction skew barely moved.** 90.9% risky (real) vs. 86.1%
   risky (counterfactual) — well within noise for samples of this size (99
   and 79 disagreements respectively), not the sharp reduction the flagged
   hypothesis would predict if this specific gene pairing were a real
   contributor to the skew's *direction*. Both variants land squarely in the
   same 61-89% risky range every other point in this thread has shown,
   never close to a conservative-majority. **This one counterfactual does
   not support "this gene pairing is a contributor" to the skew.**

2. **Unplanned confound, itself a real finding: clamping the gene changed the
   champion's own fold-fitness substantially** (-1.669 -> -2.637, both
   already-negative/unfavorable-window numbers but a big swing) **and the
   fold-stage disagreement rate moved the "wrong" way relative to the
   2026-08-29 22:50 UTC keep_frac sweep's own finding** ("disagreement rate
   tracks the champion's own fold-aggregate fitness... monotonically" —
   worse fitness there always meant *more* disagreement). Here, the
   counterfactual's fitness got *worse* (-2.637 vs -1.669) while its
   fold-stage disagreement rate got *lower* (35.7% vs 44.8%), the opposite
   direction. One data point can't overturn a 5-point monotonic pattern from
   that sweep, but it's the first case in this thread where fold-fitness and
   disagreement rate moved in opposite directions rather than together —
   worth flagging as a caveat on that pattern's generality, not a refutation
   of it. Likely explanation, not confirmed: that sweep only ever varied the
   *calendar window* under a fixed genome; this varies the *genome* under a
   fixed window, a different kind of perturbation the monotonic pattern was
   never actually tested against.

Holdout-stage numbers are too thin to read (0/44 and 1/42 disagreements) —
consistent with, not independent confirmation of, prior sessions' finding
that holdout-stage disagreement all but disappears once a search has run
enough generations to mostly exhaust easy wins either way.

## What this settles, and doesn't

Weak evidence against the flagged hypothesis: a single clamp of
`lone_voice_scale` down to `two_agree_bonus` did not meaningfully shrink the
risky-direction skew share, so this specific gene pairing does not look like
a primary driver of *why* raw fitness disagreements skew risky rather than
conservative. Does not rule out a *contributing* (as opposed to primary) role
— disentangling that would need holding fold-fitness constant across the
comparison (this run didn't, see the confound above), which would need a
different construction (e.g. re-tuning some other gene to restore the
champion's original fold-fitness after the clamp, or comparing against
several champions/windows) — not attempted here. Does not touch the
still-open "should the selection metric be redefined around excess return"
question, which remains the owner's call, same as every entry in this thread.

One counterfactual, one seed, one champion, one window — a first data point,
not a settled answer.

## Verified safe

- `git status --short`: clean before and after (scratch script lived in the
  session scratchpad, not the repo; deleted after use).
- `md5sum live_state.json`: unchanged (`81922c6011c986449f635dbf43553d0e`,
  same as before this session started — `disagreement_scan`'s own contract,
  never calls `Genome.save()`/`.promote()`/`EvolutionRun._record()`).
- No `tick`/`evolve` run against real state; today's bar (00:20 UTC, tick 16)
  was already processed and reviewed before this session started.
- No code changed this session, so no test suite / bundle-sync delta —
  `python3 -m pytest -q` was already confirmed 243/243 at session start.

## Next

- If this line is worth another data point: hold fold-fitness constant
  (compare against a second real champion, e.g. v1/v2 reconstructed, rather
  than a hand-built counterfactual that also moves fitness) before treating
  the "not a contributor" reading as settled.
- The fold-fitness/disagreement-rate "moved opposite ways" wrinkle is a loose
  end worth someone deliberately re-testing with a genome-only perturbation
  that's designed to hold fold-fitness roughly fixed, if the keep_frac
  sweep's monotonic pattern becomes load-bearing for a future design
  decision.
