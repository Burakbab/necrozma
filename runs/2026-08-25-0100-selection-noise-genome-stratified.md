# Selection noise: the genome-stratified pooled test the 2026-08-24 22:01 UTC entry flagged — 2026-08-25 ~01:00 UTC

Scheduled 3-hourly check. Today's daily bar was already handled by the 00:20
UTC run (`live_state.json` `updated` 2026-08-25T00:22:01+00:00, genome
version still 3, md5 unchanged throughout this session) — nothing new to
trade this cycle. `review-hard-calls` still 0 pending.

Picked up the loose end the second-champion entry explicitly left open:
"A rigorous pooled test across champions would need a genome-stratified or
mixed-effects design (the samples aren't draws from one distribution) —
flagged as a real next step if this remains worth resolving, not attempted
here." Three prior sessions had, between them, already collected 18
independent draws across two genomes (v3: 12 draws, batches at 16:15 and
18:57 UTC on 2026-08-24; v2: 6 draws at 22:01 UTC) — no new backtests were
needed, just the right statistical design applied to numbers already
published in those run notes.

## Method

Pure arithmetic, no market data or backtest calls — same precedent as
`runs/2026-08-21-1553-margin-curve-diagnostic.md`. One-off script (session
scratchpad, not the repo). Transcribed all 18 `(winner_gap, random_gap)`
pairs verbatim from the three source run notes, computed
`diff = winner_gap - random_gap` per draw, and treated genome (v3 vs v2) as
a block rather than pooling all 18 diffs into one naive sample:

1. **Per-block paired t** (what the prior three sessions already reported
   individually): v3 combined batches, v2 alone.
2. **Fixed-effect inverse-variance-weighted pooled mean** across the two
   blocks — the correct way to combine two differently-sized, differently-
   spread samples into one estimate without letting the larger block (v3,
   n=12) implicitly dominate by simple concatenation.
3. **Cochran's Q test** for heterogeneity between the two blocks — directly
   answers the "are these draws from one distribution" concern: if Q is
   large, the two genomes' effects genuinely differ and shouldn't be pooled
   as one number; if not, pooling is statistically defensible.
4. **DerSimonian-Laird random-effects estimate** — the standard "genome as
   random effect" design named in the flagged next step, computed and
   reported honestly as unstable with only 2 studies (0 residual degrees of
   freedom for the between-genome variance component beyond the point
   estimate itself).
5. **Block-stratified sign-permutation test** (200,000 resamples, seeded):
   within each genome block independently, randomly flip the sign of each
   paired diff (valid under the weaker null that each diff is symmetric
   around zero, no normality or cross-genome exchangeability assumption
   needed), recompute each block's t-statistic, Stouffer-combine the two
   blocks' t-statistics weighted by `sqrt(n)`, and compare the observed
   combined statistic against the permutation null. This is the sharpest,
   least-assumption-laden test attempted on this question so far.

## Result

| block | n | mean diff | sd | t |
|---|---|---|---|---|
| v3 (12 draws) | 12 | +0.521 | 1.777 | 1.016 |
| v2 (6 draws) | 6 | +1.614 | 2.373 | 1.667 |

- **Fixed-effect pooled mean: +0.761, se 0.453, z≈1.678** (one-sided
  p≈0.047 under a normal approximation — right at the conventional 0.05
  line, but a z-approximation with this little data is itself not fully
  trustworthy).
- **Cochran's Q = 0.994 on df=1** (critical value 3.841 for p<0.05) — cannot
  reject homogeneity between the two genomes. The specific worry the
  22:01 UTC entry raised ("the samples aren't draws from one
  distribution") is **not supported by this data**: two genomes' effects
  look statistically indistinguishable from each other, for whatever that's
  worth with only 1 degree of freedom to detect a difference (very low
  power — this is weak evidence *for* homogeneity, not proof of it).
- **DerSimonian-Laird tau²=0** (collapses to the fixed-effect estimate above)
  — reported for completeness per the flagged design, but honestly
  uninformative with only 2 studies.
- **Block-stratified sign-permutation p≈0.0635** (one-sided, 200,000
  resamples) — the most assumption-light test run on this question,
  and it lands closer to conventional significance than any single-genome
  number so far (v3 alone t≈1.02, v2 alone t≈1.667) but still doesn't cross
  the conventional 0.05 line.

## Reading

This is the most rigorous number this thread has produced, and it changes
the picture slightly: the specific methodological objection that blocked a
pooled conclusion ("genomes aren't from one distribution") turns out not to
be supported by the two genomes actually measured — Cochran's Q found no
detectable heterogeneity, so pooling both genomes together, done properly
(inverse-variance weighted, not naive concatenation), is not the invalid
move it was flagged as risking. The properly-pooled estimate (p≈0.05-0.064
depending on method) is close to, but still not clearly past, a
conventional significance threshold. **Still not enough to justify touching
`HOLDOUT_SIGMA`** (a constitution change needs a clearly confirmed effect,
not a borderline p-value under a design that is itself low-powered at
G=2 genomes) — but this closes the specific "needs a genome-stratified
design" loose end cleanly: the design has now been run, its central worry
was checked and not confirmed, and the honest bottom line is that 2 genomes
is simply too few for either the heterogeneity check or the pooled estimate
to be fully trustworthy either way. A third or fourth genome (v1, or a
future champion) would sharpen both the Q-test's power and the pooled
estimate's precision far more than a fourth or fifth batch of draws against
the same two genomes would — that is now the concrete, well-defined next
step on this line if it stays worth pursuing, not "more draws" or
"more permutation" of what's already been measured.

## Verified safe

- `git status --short` clean before this commit (script lives in the
  session scratchpad, not the repo; no market data or backtest calls made,
  so no `state/cache/` writes either).
- `live_state.json` md5 unchanged throughout (no command that could touch
  it was run this session before this point).
- No code changed — full suite was run once as a baseline health check at
  session start (235 passed, matching the last-known count), not re-run
  after this analysis since nothing in the repo changed.
- `review-hard-calls` still 0 pending. No genome promotion anywhere real,
  so no README `## Status` staleness.

No push notification — a read-only statistical finding on an already-flagged
open research question, borderline-but-not-conclusive, zero effect on live
trading.
