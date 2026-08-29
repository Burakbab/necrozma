# Weekend all-hands, 2026-08-29 06:00 UTC

## What this session did

Picked up the sharpest open thread at the top of "Current state": the
03:56 UTC 3-hourly check found that `history-perturb --champion-only`'s
as-of-drift spread (empirical std ~0.83 for live champion v3) isn't
symmetric noise around a fixed mean — it's a trend with calendar recency
(Pearson r = 0.686 between as-of index and fitness) — and explicitly flagged
"the actual driver of the recent/older split is still unidentified" as the
next step, ahead of resolving the still-open question of whether to combine
this noise source with `holdout-noise`'s resampling std "in quadrature" for
`HOLDOUT_SIGMA`. This is exactly the kind of question that's been repeatedly
punted from 3-hourly sessions as "deserving more scrutiny than a 3-hourly
session" — the weekend slot's job today.

No code changes. Three read-only `history-perturb --champion-only 30
--as-of-step-days 14` sweeps (live v3, plus `--also-version 1` and
`--also-version 2` to reconstruct the other two real champions this account
has had), keeping the full per-row table this time instead of just the
summary stats the earlier sessions logged, then reconstructing each row's
implied benchmark buy-and-hold return as `total_return - excess_return`
(both already printed by the command — no new computation needed inside the
tool itself).

## Finding: the driver is market beta, not calendar age

Correlating across all 30 as-of points, on all three champions independently:

| champion | Pearson(fitness, own return) | Pearson(fitness, bench return) | Pearson(fitness, excess return) | Pearson(as-of idx, fitness) |
|---|---|---|---|---|
| v1 (seed) | 0.99 | 0.76 | **-0.52** | 0.75 |
| v2 | 0.99 | 0.82 | **-0.59** | 0.77 |
| v3 (live) | 0.96 | 0.81 | 0.21 | 0.69 |

Reading, in order:

1. **Fitness (Sortino-shaped) is almost entirely a function of the
   challenger's own absolute return over the window**, not of how it did
   relative to the benchmark. The excess-return correlation is weak-positive
   for v3 and outright **negative** for v1 and v2 — for two of the three
   real champions this account has ever fielded, scoring *better* on the
   sealed holdout is mildly *anti*-correlated with actually beating the
   benchmark by more.
2. **The champion's own return correlates strongly with the benchmark's own
   return over the same window** (0.71-0.77 across all three) — expected,
   since every real champion so far is long-only and net-long biased, so it
   inherits a large share of the underlying crypto market's own beta.
3. Reconstructed `bench_ret` per as-of index matched to 0.1 percentage point
   across all three champions' independent sweeps — a genome-independent
   quantity, as it must be (same fixed universe, equal-weight buy-and-hold),
   and a useful internal consistency check on the reconstruction itself.
4. Splitting the 30 as-of points at the midpoint (idx 0-14 = holdout windows
   starting 2024-11 through 2025-04, idx 15-29 = holdout windows starting
   2024-05 through 2024-11): mean benchmark return is **-9.3%** in the recent
   half and **+67.7% to +67.8%** in the older half — nearly identical across
   all three champions, because it's the same fixed universe's own price
   history, not a genome effect. This is the actual mechanism behind the
   03:56 UTC entry's recency correlation: recency is a proxy for which
   calendar-fixed market regime the sliding `HOLDOUT_FRAC` window happens to
   land on (2024's crypto bull run vs. 2025's much weaker stretch), not a
   driver in its own right.
5. This is the same structural mechanism the 2026-08-17 `regime` diagnostic
   already named generically for the walk-forward folds (fold 2's permanent
   +200% melt-up structurally favoring or penalizing a genome by its own
   beta, independent of skill) — this session shows it recurring in the
   as-of-drift dimension too, and confirms it on all three real champions
   rather than one fold on one genome, matching the evidentiary bar this
   repo has used before drawing conclusions on similar multi-champion
   questions (e.g. the correlation-penalty removal, item 3, checked 4
   champions plus two adversarial constructions before acting).

## What this settles: no, do not combine in quadrature

The 00:56 and 03:56 UTC entries left open whether to combine this session's
as-of-drift std with `holdout-noise`'s block-bootstrap resampling std (in
quadrature, `sqrt(2.04^2 + 0.83^2) ≈ 2.20`). **The answer is no** — not
because the number is small (it isn't negligible), but because this isn't a
noise source at all in the sense the formula assumes. Quadrature-combination
is only valid for independent, zero-mean perturbations around a true value.
What was actually measured is explained variance: a challenger's holdout
score depends heavily on the market-beta regime its evaluation window
happens to land on, mechanistically identified above, and for two of three
real champions this quantity is *negatively* correlated with genuine
skill-over-benchmark. A quantity like that is not a candidate for folding
into a safety-margin sigma via quadrature-sum regardless of its empirical
std — doing so would be summing something with a real, non-zero, sometimes
skill-decorrelated mean into a formula that assumes there isn't one.

`HOLDOUT_SIGMA` (2.0), calibrated 2026-08-21 purely from `holdout-noise`'s
block-bootstrap resampling of one fixed realized price path — a genuinely
different, cleaner, much closer to i.i.d. noise source — is **not adjusted
by this finding**. This closes the specific quadrature-combination question
the last two 3-hourly sessions left open. It does not touch `HOLDOUT_SIGMA`
itself, and no `AMENDMENTS.md` row is needed since nothing about the
constitution changed — the conclusion is explicitly "don't make this
change," not a new calibration.

## New open question this surfaces (not acted on)

Since the sealed-holdout fitness gating every real promotion is dominated by
a challenger's own market-beta-driven absolute return rather than its skill
relative to a passive benchmark, a promotion decision's outcome depends
materially on which slice of calendar history the ever-growing,
fixed-fraction holdout window happens to be sitting on at evaluation time —
not only on whether the challenger's policy is actually better. This is the
same root concern as "Measured 2026-08-16" finding #1 (the system
underperforms buy-and-hold) and the fold-2-outlier finding already in this
file, now shown to reach directly into the sealed-holdout *promotion gate*
itself, not just into reported diagnostics.

Whether the holdout/fold selection metrics should be redefined around excess
return rather than raw Sortino-shaped `fitness()` is a real, larger design
question. Deliberately **not attempted this session**: a metric redefinition
touches the checksummed constitution and every acceptance gate built on
`fitness()`, and per this file's own standing pattern (see the
correlation-penalty item's ~15-session measure-then-act arc) deserves its
own dedicated design pass and evidence base, not a same-session follow-on to
a measurement run. Flagging it here so it isn't lost, not deciding it.

## Why this was in scope for a weekend session and not the v3
demotion/rollback question

Checked explicitly before starting: the standing v3 true-drawdown
demotion/rollback question (raised to the owner 2026-08-22, reaffirmed daily
through 2026-08-28) is unchanged by anything measured here, has already been
raised repeatedly, and per the 2026-08-28 09:00 UTC daily discussion's own
judgment, restating it again without new information would be noise, not
signal — it remains explicitly the owner's call, not something this session
had new evidence to act on. The as-of-drift/`HOLDOUT_SIGMA` thread, by
contrast, is a calibration/statistics question this account's own scheduled
sessions have owned and advanced independently since 2026-08-20, exactly the
kind of thing a deep-focus weekend slot is for.

## Verified safe

- No code changed anywhere — pure data analysis of existing, already-shipped
  CLI output (`history-perturb --champion-only`, shipped 2026-08-29 00:56
  UTC). No new tests needed.
- Three full 30-point sweeps run this session (v1, v2 reconstructions; the
  v3 sweep from the 03:56 UTC entry's own third run was re-run fresh at the
  same parameters to get its full per-row table, since only summary stats
  had been logged before).
- `md5sum live_state.json evotrader.manifest` unchanged across every run:
  `bf360fc7f86f6bae2bc46bb6f6dc6026` / `0bf3a7d9411ee692d0a9f152a7533803`,
  matching every prior entry in this thread.
- `python3 -m pytest -q` — 240/240 passed, no regressions (nothing in the
  test surface touched).
- `tools/edit_bundle_module.py sync --check` — clean, no drift.
- `constitution verified 8b74865634b1db07` unchanged on every invocation.
- No `AMENDMENTS.md` row — no constitution value changed; the conclusion is
  an explicit "don't change `HOLDOUT_SIGMA`," not a new calibration.
- No genome promotion — no README `## Status` change needed.
- Today's bar (00:20 UTC) was already processed before this session started
  (`runs/2026-08-29-0020-daily-trading.md` exists); no `tick`/`evolve` call.
- `git status --short` was clean before this note was written.

## Next steps

- The new, sharper open question (excess-return-based selection metric vs.
  raw Sortino `fitness()`) is the natural next thing for whoever next has a
  dedicated design-pass slot — not a quick follow-on.
- `--also-version N` has now swept all three real champions this account has
  had for the as-of-drift question, same as it has for `fold-scheme` and
  `correlation-universe` — closed until a fourth champion is promoted.
- The still-open v3 demotion/rollback design question (2026-08-22) remains
  exactly where the 2026-08-28 daily discussions left it — the owner's call,
  unchanged by this session, not restated further here per the same
  no-noise judgment those sessions already applied.
