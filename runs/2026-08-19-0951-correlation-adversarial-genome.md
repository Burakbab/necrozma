# Adversarial-genome correlation check (3-hourly self-improvement check)

AGENTS.md item 3's correlation question had exhausted every real champion this
account has ever had (v1, v2, v3, via `correlation-universe --realized
--also-version N`): all three land on a held-set that's *less* correlated
than the wider universe, purely as a side effect of ordinary entry/exit
tuning — nothing in any of them rewards diversification (`correlation_penalty`
sits at its default `0.0` in all three). The open caveat every one of those
runs flagged: that's three organically-found genomes, not a genome
*deliberately* built to concentrate exposure. This run does that check.

## What was built

New `evotrader_bundle._adversarial_concentration_genome(base)` (plain
function, `evotrader_bundle.py:99-140`, right after
`_reconstruct_champion_genome`) builds a genome via the same `Genome.child()`
patch mechanism every real promotion uses, starting from the live champion
(v3) and loosening every entry gate across all three consults to near
pass-through (rank/trend/RSI/vol filters that normally stagger entries across
symbols and time), plus raising every position-count/cash-floor limit so the
council can act on all of that permissiveness inside a single bar instead of
trickling positions in one at a time. `correlation_penalty` is deliberately
left at `0.0` — same as every real champion — because the question is
whether *losing selectivity* alone is enough to concentrate exposure, not
whether the existing (already-proven-inert) penalty gene would catch it.

Full patch list (21 dotted-path changes): loosened `min_rank_mom`,
`min_breakout`, `min_slope`, `rsi_max` (risky); `min_trend`, `rsi_lo`/`rsi_hi`,
`min_rank_mom`, `max_vol` (moderate); `rsi_buy_below`, `z_buy_below`,
`require_uptrend=False`, `min_trend`, `max_vol` (conservative);
`min_conviction`, `max_positions` 6→20, `cash_floor_pct` 0.05→0.0 (risk_judge);
`hard_max_positions` 8→20, `max_new_positions_per_bar` 3→15,
`hard_cash_floor_pct` 0.02→0.0 (superior_judge); `max_bars_held` 60→90.

Wired into the existing `correlation-universe --realized` CLI as a new
`--adversarial` flag (alongside the existing `--also-version N`), reusing the
identical held-set measurement (`loop.engine.holding_mask` +
`pairwise_correlation_stats`) and printing it in the same cross-genome
comparison table. Purely additive: no existing behavior changed, no new
dependency, no constitution touch (`core.genome`/CLI glue only, neither in
the checksummed set).

## Result

Ran `correlation-universe --realized --also-version` is not needed here since
the adversarial genome is built directly from `g0` (v3); ran
`correlation-universe --realized --adversarial`:

| window  | v3 (live) held-only | adversarial held-only | universe-wide | v3 gap below universe | adversarial gap below universe |
|---|---|---|---|---|---|
| fold 1  | +0.523 | +0.530 | +0.630 | −0.108 | −0.100 |
| fold 2  | +0.470 | +0.467 | +0.509 | −0.039 | −0.042 |
| fold 3  | +0.427 | **+0.603** | +0.616 | −0.189 | **−0.013** |
| holdout | +0.437 | **+0.542** | +0.572 | −0.135 | **−0.030** |

**This is the first genome, real or constructed, whose held-set correlation
approaches the universe-wide baseline instead of sitting clearly below it.**
In fold 3 and the holdout the adversarial genome's gap below universe-wide
shrinks by 6-9x compared to v3's own gap in the same windows (fold 3: −0.189
→ −0.013; holdout: −0.135 → −0.030) — deliberately removing selectivity does
measurably concentrate exposure, at least in these two windows. Fold 1 and
fold 2 barely move (adversarial ≈ v3, both windows), so the effect isn't
uniform across regimes — plausible since a market-wide breakout period drives
this genome's simultaneous entries harder than a chop/mixed period would, and
folds 1/2 cover different calendar regimes than folds 3/holdout (see the
`regime`/`fold-scheme` diagnostics from earlier runs).

## Reading this against item 3's drop-vs-build decision

Sharper, not simply reversed. The prior four measurements (universe-wide,
v3/v1/v2 portfolio-realized) all supported "no real champion this account has
produced needs `correlation_penalty` — drop it" — that conclusion still
stands unchanged for real champions. This adds: the reason no real champion
needed it isn't that concentration is structurally impossible for this
system — it's that ordinary fitness-driven selectivity (each consult's
rank/trend/RSI/vol gates staggering which symbols qualify, when) happens to
keep the held set less correlated than the universe as an incidental
byproduct. An adversarial genome that specifically discards that selectivity
gets measurably closer to universe-wide correlation in the windows where it
matters most (fold 3 and the holdout — not coincidentally the two most recent
windows, where the search folds and evolution history actually operate).
That's a reason to keep `correlation_penalty` as an available (if currently
unused) safety valve rather than deleting the gene outright, even though
dropping it from *active use* against the current champion lineage remains
supported. Not run to promotion-grade rigor — one hand-built genome, one
backtest, no evolution search validated it, no holdout gate was applied to
it (it's a diagnostic construction, not a challenger).

## Verification

- `python3 -m py_compile evotrader_bundle.py` — clean.
- `pytest tests/` — 104 passed (unchanged from before this change; no new
  tests needed, this is CLI/function glue over already-tested primitives,
  same bar `--also-version` was held to).
- `live_state.json` md5 identical before/after
  (`09c35b692da1d694c5a3cace5d488f40`).
- `git status --short` clean of anything but the `evotrader_bundle.py` diff.
- `constitution verified dfae6a697f51fb49` unchanged throughout.
- Today's 2026-08-18 daily bar (tick 5) was already processed by the 00:20
  UTC daily run before this check started (`live_state.json`'s `updated`
  timestamp `2026-08-19T00:21:55+00:00`) — no double-trade, `tick` not run
  this session.

## Next

The adversarial construction here is one hand-picked direction (loosen every
selectivity gate at once). Not tried: a genome tuned the *opposite* way
(tight, correlation-agnostic selectivity that happens to cluster on one
sector/theme rather than losing selectivity broadly) — a narrower, more
surgical adversarial genome might concentrate harder than this blunt one did.
Also not tried: does the concentration effect measured here in fold 3/holdout
actually translate into a lower Sortino/higher drawdown for this genome (this
run only measured correlation structure, not `fitness`/`stats` for the
adversarial genome — it was never meant to be evaluated as a trading
candidate). If item 3 is revisited to actually delete `correlation_penalty`/
`correlation_lookback`/`_correlation_scale`, this result is a reason to keep
the mechanism available rather than delete it outright, even though no real
promoted champion has needed it yet.
