# Selection noise: a second champion — 2026-08-24 ~22:01 UTC

Scheduled 3-hourly check. Today's daily bar was already handled by the 00:20
UTC run (`live_state.json` `updated` 2026-08-24T00:22:01+00:00, genome
version still 3, md5 `0b628cf88674a6de938b4a806f33cf70` unchanged throughout
this session) — nothing new to trade this cycle. `review-hard-calls` still 0
pending.

The 2026-08-24 ~18:57 UTC entry (batch 2 of the same-champion selection-noise
diagnostic) left the question open with one concrete next step named: "would
need... a genuinely different check (e.g. a second champion) to be worth
another session." Took that step.

## Method

Same script shape as the two prior sessions (`runs/2026-08-24-1615-*.md`,
`runs/2026-08-24-1857-*.md`), same fixed-methodology bug fix already baked
in (`exclude` accumulated across draws, not reset — mirrors
`EvolutionRun.tested`'s real per-champion behavior). The only change:
reconstructed champion **v2** from `live_state.json`'s own `lineage` (the
same replay-accepted-patches-from-seed logic `_reconstruct_champion_genome`
uses for `--also-version`) instead of using live champion v3. v2 is a real
former live champion — a genuinely different genome, different gene values,
different regime it was tuned against — not just a different random draw
against the same one. Six independent draws (`n_blind=10`, `exclude`
accumulated), each taking the fold-aggregate winner and one uniformly-random
non-winning candidate from the same batch, running **both** through the
sealed holdout.

## Result: same direction, similar strength, still not significant alone

| draw | n | winner fold | winner holdout | winner gap | random fold | random holdout | random gap |
|---|---|---|---|---|---|---|---|
| 0 | 21 | 0.476 | −0.071 | +0.547 | −2.507 | −1.174 | −1.333 |
| 1 | 10 | 0.135 | −0.033 | +0.168 | −0.069 | −2.872 | +2.803 |
| 2 | 10 | 0.198 | −2.773 | +2.971 | −2.818 | −1.616 | −1.202 |
| 3 | 10 | 0.183 | −1.447 | +1.630 | −2.651 | −2.734 | +0.083 |
| 4 | 10 | 0.097 | −2.687 | +2.784 | −0.566 | −2.075 | +1.509 |
| 5 | 10 | 0.295 | −2.711 | +3.007 | −0.346 | +0.093 | −0.438 |

Champion v2 itself: fold-aggregate fitness 0.133, holdout fitness −2.737 (a
real former champion doing badly on the *current* holdout window — expected,
since v2 was tuned against an older window and the holdout slice has moved
on; not itself evidence of anything here).

Winner gap: mean **+1.851**, std 1.158, n=6. Random gap: mean **+0.237**,
std 1.484, n=6. Winner's gap larger in 5 of 6 draws (all but draw 1). Paired
t≈1.667 (df=5) — directionally consistent with the winner's-curse hypothesis
again, still short of conventional significance (~t≈2.57 at 5 df), but a
close replication of v3 batch 1's shape (t≈1.55, 4/6 draws) on a genuinely
different genome and a slightly *stronger* signal than v3's own combined
12-draw number (t≈1.02) that batch 2 diluted.

**Reading**: two independent champions, same qualitative shape (winner gap
mean higher than random gap mean, mid-1-range paired t, most but not all
draws agreeing on direction), neither individually significant. This is
weak-to-moderate evidence *for* a real selection effect distinct from
per-candidate holdout noise — stronger than "one favorable draw" now that a
second, unrelated genome shows the same pattern, but still not strong enough
to justify a constitution change (`HOLDOUT_SIGMA` is already a measured,
not guessed, floor — see 2026-08-21 `holdout-sigma-recalibration`). Not
chased further this session: a rigorous combined-champion test would need to
account for the two samples not being independent draws from one
distribution (different genomes, different windows), which is a real
statistics design question, not a quick follow-up. Leaving this here as the
strongest evidence gathered on this question so far; a future session could
pool all 18 draws (6 v3-batch1 + 6 v3-batch2 + 6 v2) with a mixed-effects or
genome-stratified test if this remains worth resolving, or treat two
directionally-consistent-but-individually-null champions as enough to stop
without a third.

## Verified safe

- `git status --short` clean before and after (script lives in the session
  scratchpad, not the repo).
- `live_state.json` md5 unchanged throughout (`0b628cf88674a6de938b4a806f33cf70`).
- Full test suite: 235 passed (confirmed at session start; no code changed
  this session).
- `review-hard-calls` still 0 pending. No genome promotion anywhere real, so
  no README Status staleness.
- Champion v2 reconstruction uses the same code path `--also-version` already
  relies on elsewhere in this codebase, applied by hand here since this
  diagnostic isn't wired into a permanent CLI command (same precedent as the
  two same-champion sessions before it).

No push notification — a read-only research finding (directionally
suggestive, not conclusive) with zero effect on live trading behavior, same
threshold every prior diagnostic-only 3-hourly session in this history has
used.
