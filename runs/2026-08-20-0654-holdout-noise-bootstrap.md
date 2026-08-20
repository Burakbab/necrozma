# 3-hourly check: measuring the sealed-holdout margin's assumed sigma against reality

`constitution.holdout_accepts()`'s own docstring names an open question it
never answers: "This margin is a floor, not a calibration, and should not be
mistaken for one. A single holdout window is a noisier estimate than a
fold-aggregate, so its true sigma is larger than `MULTIPLE_TESTING_SIGMA`...
Measure the sigma before trusting the number." Every `holdout-pressure`/4h-shadow
entry in AGENTS.md's Current state has described a challenger's sealed-holdout
score as "one noisy point estimate" without ever putting a number on the noise.
This session built the measurement.

## What was built

New pure functions in `loop.engine`:

- `block_bootstrap_resample(rets, length, block_size, rng)` — circular
  moving-block bootstrap of a return series. Resamples whole `block_size`-bar
  chunks from randomly chosen (circularly wrapped) starting positions, rather
  than shuffling individual bars, so short-range autocorrelation (volatility
  clustering, multi-bar trends) in the real return path survives the resample.
- `stats_from_returns(rets, trades, turnover_annual, bars_per_year)` — the
  return-derived subset of `core.portfolio.PaperBroker.stats()` (total_return,
  cagr, vol, sharpe, sortino, max_dd), recomputed from a bare return array
  instead of a live broker. Deliberately duplicates those formulas rather than
  importing them, because trade-derived fields (trades, turnover) can't be
  regenerated from a resampled return path — reordering bars doesn't tell you
  which trades would have fired in that order — so those are passed through
  unchanged from the real backtest instead. Verified to reproduce
  `PaperBroker.stats()` exactly when fed that broker's own unshuffled returns
  (`tests/test_bootstrap_holdout_noise.py`).
- `bootstrap_fitness_distribution(nav_history, trades, turnover_annual,
  bars_per_year, n_boot=1000, block_size=10, seed=0)` — block-bootstraps a
  real backtest's observed return path `n_boot` times, recomputes
  `constitution.fitness()` for each resample, and reports the resulting
  distribution (mean, std, p05/p95, hard-fail rate) alongside the real
  (unshuffled) point estimate as a consistency check.

New read-only CLI command `evotrader_bundle.py holdout-noise
[--n-boot N] [--block-size B] [--seed S] [--also-version N]`: runs one real
full backtest over the sealed holdout window (same cost class as `costs
--holdout`), then bootstraps its own already-computed `nav_history` — no
second genome evaluation, no market data reload per bootstrap draw. Prints the
empirical `boot_fitness_std` next to `constitution.MULTIPLE_TESTING_SIGMA`
(0.08) as a direct ratio. `--also-version N` reconstructs a past champion
(same mechanism `fold-scheme`/`correlation-universe` use) for a cross-champion
check.

Tested: `tests/test_bootstrap_holdout_noise.py`, 16 new tests — resample
length/determinism/subset-of-original/empty-input/clamped-block-size/constant-series
behavior, `stats_from_returns` cross-checked bit-for-bit against
`PaperBroker.stats()` on the same path, `bootstrap_fitness_distribution`
determinism given a fixed seed, a constant-return degenerate case (should have
exactly zero empirical sigma — a sanity check on the bootstrap mechanism
itself before trusting it on real noisy data), and a real-input sanity check
that `real_fitness` matches directly calling `fitness(stats_from_returns(...))`
on the unshuffled path. Full suite 127 passed, up from 111.

## Result

Against the live champion v3, sealed holdout, `n_boot=2000`:

| block_size | seed | real holdout fitness | boot mean | boot std | boot std / 0.08 |
|---|---|---|---|---|---|
| 15 | 0 | -1.018 | -0.515 | 2.035 | **25.4x** |
| 15 | 99 | -1.018 | -0.554 | 1.901 | 23.8x |
| 5 | 0 | -1.018 | -0.453 | 1.918 | 24.0x |
| 30 | 0 | -1.018 | -0.461 | 2.042 | 25.5x |

(The -1.018 real holdout fitness differs from the previously-recorded -1.172
because `load_universe(..., 4.0)` loads a sliding 4-year window ending today,
not the promotion-time snapshot — same caveat every other diagnostic in this
file already carries.)

Robust across both block size (5/15/30 bars) and random seed: the empirical
bootstrap sigma sits consistently around **24-25x** the constitution's
assumed `MULTIPLE_TESTING_SIGMA=0.08`. Also checked against a second,
genuinely different champion (v2, reconstructed, `--also-version 2`,
`n_boot=1500`, `block_size=15`): real holdout fitness -2.821, boot std
1.145, ratio **14.3x** — a different magnitude (v2's holdout window return
path is less volatile in this measure than v3's) but the same qualitative
conclusion: an order of magnitude larger than what the margin formula
assumes, not a v3-specific artifact.

## Reading it

`required_margin()` computes `MULTIPLE_TESTING_SIGMA * sqrt(2 * ln(n_draws))`.
At 24x the assumed sigma, the actual noise band around any single sealed-holdout
fitness score is roughly 24x wider than the margin `holdout_accepts()` currently
requires a challenger to clear. This gives a concrete number behind every
"lucky holdout draw" finding already in this file — `holdout-pressure`'s 9/9
real post-promotion challengers that cleared the fold-aggregate gate and lost
the sealed holdout, several tying the champion's exact score rather than
losing outright; the 4h-shadow work's repeated observation that a champion's
own strong holdout draw can entrench it against fold-superior challengers.
Those were all consistent with under-margined noise; this is the first run
that actually measured it.

Caveats, honestly: (1) this bootstraps the *realized return path* of one
specific backtest, holding trades/turnover fixed — it measures "how much
would recomputed performance metrics move if the same trades' returns had
landed in a different order/selection", not "how much would a genuinely
different holdout slice of history score" (a harder, more expensive question —
would need re-running the full council against resampled *prices*, not just
resampled realized returns, since trade decisions are themselves
price-dependent). (2) Block bootstrap standard error estimates for Sortino-like
ratios are a standard technique but still an approximation, not a closed-form
result — the exact multiplier (24x vs, say, 15x or 35x) shouldn't be
over-read; the qualitative finding (an order of magnitude, not a rounding
error) is what's robust across seeds/block sizes/champions here. (3) Not
chased further this run: whether `required_margin()`'s formula should actually
be recalibrated (raise `MULTIPLE_TESTING_SIGMA` specifically for the holdout
gate vs the fold-aggregate gate — the docstring already says the honest bar
for the holdout is higher than for folds) is a constitution change,
checksummed, needs its own `AMENDMENTS.md` row and a considered decision, not
a same-session addition to a measurement run.

## Verified safe

Purely additive (`loop.engine` isn't in the checksummed set — `constitution` +
`core.portfolio` only), `py_compile` clean, `tools/edit_bundle_module.py
verify` round-trip clean after the `loop.engine` edit, `live_state.json` md5
identical before/after (`cca58deb976cef403c5010f2e2b9528b`),
`evotrader.manifest` md5 identical (`6a4434574ff424f74ff300ebdb50d194`),
`constitution verified dfae6a697f51fb49` unchanged throughout, full test
suite 127 passed (up from 111), `git status` clean of anything but the
`evotrader_bundle.py` diff and the new test file. Today's 2026-08-19 bar
(tick 6) confirmed already processed by the 00:20 UTC daily run before this
check started — `live_state.json`'s `updated` timestamp was
`2026-08-20T00:21:36+00:00` and the journal's last entry was tick 6 before
this session touched anything; `tick` not run this session, no double-trade
risk.

## Next

The concrete number is now in hand; what to do with it is a judgment call for
whoever next has the appetite for a constitution change:

- The most direct fix — raising `MULTIPLE_TESTING_SIGMA` specifically for the
  holdout gate (or adding a separate, larger holdout-sigma constant) — would
  make `holdout_accepts()` much harder to clear, which cuts both ways: fewer
  false "promotions on noise", but also a much higher bar for genuinely better
  challengers to prove themselves against a short, fixed 15% holdout slice.
  Combined with the existing fold-scheme findings (fold 2 as a permanent
  +200% outlier, non-monotonic aggregate_fitness across fold counts on 2 of 3
  champions), this reads less like "the holdout gate needs a bigger number"
  and more like "the whole fixed 85/15 split plus 3-fold walk-forward scheme
  could use a redesign" — the regime-stratified/rolling scheme idea already
  flagged in the fold-scheme entries, now with another independent reason to
  attempt it.
- Cheaper follow-up available without touching the constitution: run
  `holdout-noise --also-version 1` for the third data point (the seed
  champion), and/or re-run at a much higher `n_boot` (5000+) to check whether
  the ~24x estimate itself has converged or is still moving.
- `holdout-noise` is now available as a one-line check any time a future
  fold/holdout scheme redesign needs "does the new scheme's margin look
  properly calibrated" as a concrete answer instead of another guess.
