# Selection noise: a third genome (v1) — 2026-08-25 ~04:02 UTC

Scheduled 3-hourly check. Today's daily bar was already handled by the 00:20
UTC run (`live_state.json` `updated` 2026-08-25T00:22:01+00:00, genome
version still 3, md5 `f7590581b893d3866e00e28c87fe1c02` unchanged throughout
this session) — nothing new to trade this cycle. `review-hard-calls` still 0
pending.

The 2026-08-25 ~01:00 UTC entry (genome-stratified pooled test across v3+v2)
closed its own design loose end and named the concrete next step explicitly:
"A third or fourth genome (v1, or a future champion) would sharpen both the
Q-test's power and the pooled estimate's precision far more than a fourth or
fifth batch of draws against the same two genomes." Took that step.

## Method

Same six-draw script shape as the three prior sessions in this thread
(`runs/2026-08-24-1615-*.md`, `-1857-*.md`, `-2201-*.md`), same fixed
methodology (`exclude` accumulated across draws, not reset). Only change:
reconstructed champion **v1** — the seed genome, `Genome.champion()`, no
lineage patches needed since v1 predates any accepted promotion — instead of
v2 or v3. `n_blind=10`, 6 independent draws, each taking the fold-aggregate
winner and one uniformly-random non-winning candidate from the same batch,
running both through `Evaluator.holdout_check`.

Then a second, pure-arithmetic script extended the 01:00 UTC session's
2-block (v3, v2) Cochran's Q / fixed-effect pooling / block-stratified
sign-permutation design to 3 blocks by adding these new v1 draws — no new
backtests needed for that part, transcribing the already-published
`(winner_gap, random_gap)` pairs from the three prior run notes.

## Result: v1 shows no effect at all, and adding it as a third block weakens the pooled evidence

Champion v1 itself: fold-aggregate fitness −2.709 (the raw, unevolved seed —
expected to be weak), holdout fitness −0.763.

| draw | n | winner fold | winner holdout | winner gap | random fold | random holdout | random gap |
|---|---|---|---|---|---|---|---|
| 0 | 22 | 0.362 | 0.305 | +0.056 | −0.325 | −1.165 | +0.839 |
| 1 | 10 | −0.019 | −0.856 | +0.837 | −0.106 | −1.090 | +0.984 |
| 2 | 10 | 0.716 | 1.006 | −0.289 | −0.045 | −0.292 | +0.248 |
| 3 | 10 | 0.043 | −0.647 | +0.690 | −0.212 | −1.747 | +1.535 |
| 4 | 10 | −0.064 | −0.930 | +0.866 | −2.618 | −0.972 | −1.646 |
| 5 | 10 | −0.009 | −0.505 | +0.496 | −0.309 | −0.630 | +0.321 |

Winner gap: mean **+0.443**, std 0.425, n=6. Random gap: mean **+0.380**, std
1.003, n=6. Winner gap larger in only **2/6** draws (unlike v3 batch1's 4/6
and v2's 5/6). Paired t ≈ **0.121** (df=5) — essentially zero signal, the
weakest of the three genomes tested so far by a wide margin (v3 combined
t≈1.02, v2 t≈1.667, v1 t≈0.12).

Three-block genome-stratified pooling (v3 n=12, v2 n=6, v1 n=6, same design
as the 01:00 UTC entry):

| block | n | mean diff | sd | t |
|---|---|---|---|---|
| v3 (12 draws) | 12 | +0.521 | 1.777 | 1.016 |
| v2 (6 draws) | 6 | +1.614 | 2.373 | 1.667 |
| v1 (6 draws) | 6 | +0.063 | 1.261 | 0.121 |

- **3-block fixed-effect pooled mean: +0.456, se 0.340, z≈1.340** (one-sided
  p≈0.090 under a normal approximation) — down from the 2-block run's
  z≈1.678 (p≈0.047).
- **Cochran's Q = 2.030 (df=2)**, still well under the df=2 critical value
  (5.991) — still cannot reject homogeneity between the three genomes, but Q
  rose from 0.994 (df=1) with only two blocks, consistent with v1 sitting
  further from the other two than they sit from each other.
- **Block-stratified sign-permutation p ≈ 0.0815** (one-sided, 200,000
  resamples, same Stouffer-combined-by-`sqrt(n)` design as the 01:00 UTC
  run) — up from 0.0635 with two blocks, moving further from conventional
  significance, not closer.

## Reading

This is a real, if unglamorous, answer to the flagged next step: the
specific prediction that a third genome would sharpen the picture turned out
right about the *power* (Q now has 2 degrees of freedom instead of 1) but
wrong about the *direction* — more power revealed a weaker pooled effect,
not a stronger one. v1 is a legitimately different genome (the unevolved
seed, never promoted, genuinely different gene values from either real
champion), and it shows next to no selection-noise signal by this method.
Read together with batch 2's earlier same-champion reversal (2026-08-24
~18:57 UTC), the pattern across this whole four-session thread is now: every
time this question got a genuinely new, independent unit of evidence (a
second batch, a second champion, now a third genome), the pooled estimate
moved *away* from significance, never toward it. That is itself informative
— it is the signature of an effect that either doesn't exist or is much
smaller than the per-draw noise this method can resolve, not a signal that
just needs one more push. **Not touching `HOLDOUT_SIGMA`** — already the
conclusion at every step of this thread, now on firmer ground.

**Closing this line of inquiry, not just this session's slice of it.** A
fourth genome or another batch of draws would cost the same ~10-15 minutes
as every prior step here and, going by this thread's own track record, is
more likely to weaken the pooled estimate further than to finally cross a
significance line that has receded every time more data arrived. Worth
reopening only if a future champion promotion (v4+) makes a fresh genome
available essentially for free, or if someone has a sharper hypothesis about
*why* the effect should exist mechanistically (rather than continuing to
test "does it show up in more draws," which this thread has now done four
times).

## Verified safe

- `git status --short` clean before and after (both scripts live in the
  session scratchpad, not the repo).
- `live_state.json` md5 unchanged throughout
  (`f7590581b893d3866e00e28c87fe1c02`).
- Full test suite: 235 passed (no code changed this session, confirmed as a
  baseline health check).
- `review-hard-calls` still 0 pending. No genome promotion anywhere real, so
  no README `## Status` staleness.
- Champion v1 reconstruction is just `Genome.champion()` — the seed itself,
  no lineage replay needed (v1 predates any accepted promotion), same
  precedent as `--also-version 1` elsewhere in this codebase.
- Total diagnostic compute: ~2 minutes for the 6-draw v1 batch (faster than
  v2/v3's ~10 minutes — the unevolved seed's fold-aggregate search space
  runs to fewer candidates on average), plus a few seconds for the
  pure-arithmetic pooling script, plus ~2.5 minutes for the full test suite
  baseline.

No push notification — a read-only research finding (a negative one, closing
a four-session thread) with zero effect on live trading behavior, same
threshold every prior diagnostic-only 3-hourly session in this history has
used.
