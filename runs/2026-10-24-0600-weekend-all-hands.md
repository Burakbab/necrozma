# Weekend all-hands, 2026-10-24 ~06:00-06:40 UTC

## Scope

Weekend slot, deep-focus rather than wide. Picked up AGENTS.md item 5 (short
selling / "whether a real short-opening signal exists") at its most recent
open thread: the 2026-10-17 weekend session (`dual-trend-oos`) found that the
2026-10-11 session's `slope_lookback` "sweet spot" for `benchmark_
dual_trend_short` was pure in-sample mining — it reversed completely when
checked against calendar windows the original sweep never saw. That raised an
obvious question nobody had asked yet about the *other* half of this item's
combination-search history: the 2026-10-03/04 `COMBINED`/`ASYMMETRIC` short
signals (`loop.engine.benchmark_combined_short`/`benchmark_asymmetric_short`)
made an equally strong-sounding claim — "AND-gating trend-break with the
regime classifier reduces bull-market losses" — off the exact same 4
fold/holdout windows, and that claim had never been out-of-sample checked
either. Today closes that gap.

## What shipped

New read-only CLI command, `evotrader_bundle.py regime-combo-oos`. No new
`loop.engine` function needed — it calls the existing `benchmark_buy_hold`/
`benchmark_trend_break_short`/`benchmark_combined_short`/
`benchmark_asymmetric_short` exactly the way `short-headroom --combined/
--asymmetric` already does, just against `history-perturb`'s own
`--independent` tiling (fixed-width, non-overlapping windows walking backward
from "now" over the full ~2017-2026 history) instead of the champion's own 4
windows. Same `--window-years`/`--short-regimes`/`--borrow-bps-per-bar` flag
conventions as `dual-trend-oos`.

Shipped and committed (`b9b79df`) *before* running it — `python3 -m pytest -q`
474/474 unaffected (pure CLI addition, no module source changed, so no bundle
sync needed) and `py_compile` clean. Then ran it twice, same two widths
`dual-trend-oos` used.

## Results

**2.0y tiling (5 windows).** All 5 turned out to be bull markets — the same
finding `dual-trend-oos` already made about this universe's real history, so
there's no 2-year stretch in it that nets out bearish. Mean return:
trend-break −7.4%, combined −6.7%, asymmetric **+1.2%** (positive on average).

**1.1333y tiling (the champion's own per-fold width, 9 windows, one too short
to use).** This time 3 of the 8 valid windows were genuinely bearish
(buy&hold −6.2%, −5.0%, −46.9%) — note the window boundaries and bear-window
count differ slightly from `dual-trend-oos`'s own 1.1333y run a week earlier
(it found 2 bear windows, not 3); both tilings walk backward from "now" so a
week's drift shifts every boundary by the same amount — not a bug, not a
contradiction, just the tiling's own floating anchor.

Mean return across all 8 valid windows: trend-break −11.1%, combined −7.9%,
asymmetric −7.3%. Unlike the slope_lookback sweep (which flipped completely),
**both filtered signals beat the unfiltered baseline on average here** — a
genuinely different outcome from `dual-trend-oos`'s clean-negative result.

That's not the whole story, though. Per-window "which signal lost least /
gained most":

| window | buy&hold | trend-break | combined | asymmetric | best |
|---|---|---|---|---|---|
| 2 (2017-09→2018-11) | −6.2% | **+30.8%** | −2.5% | +28.2% | trend-break |
| 3 (2018-11→2020-01) | −5.0% | −11.8% | **+4.7%** | +0.9% | combined |
| 4 (2020-01→2021-02) | +1032.7% | −32.6% | **+5.4%** | −7.7% | combined |
| 5 (2021-02→2022-04) | +41.1% | **+7.7%** | −1.5% | +3.0% | trend-break |
| 6 (2022-04→2023-05) | −46.9% | −25.6% | **−17.0%** | −29.5% | combined |
| 7 (2023-05→2024-07) | +102.9% | **−26.6%** | −35.9% | −40.8% | trend-break |
| 8 (2024-07→2025-09) | +53.5% | −17.8% | −9.4% | **−8.4%** | asymmetric |
| 9 (2025-09→2026-10) | +45.8% | −13.2% | −6.9% | **−3.8%** | asymmetric |

Tally: trend-break wins 3, combined wins 3, asymmetric wins 2 — a genuine
three-way split, not a consistent winner.

Combined's mean advantage over trend-break (−7.9% vs −11.1%) turns out to be
concentrated almost entirely in window 4 — the single most extreme bull
window in the sample (buy&hold +1032.7%), where combined alone stayed
profitable (+5.4%) while trend-break lost −32.6%. Drop that one window and
the ranking changes: trend-break −8.1%, combined **−9.8% (now the worst of
the three)**, asymmetric −7.2% (essentially unchanged). Asymmetric's edge is
the more robust of the two — smaller, but stable with or without the
outlier, and it never relies on one window to look good.

In the one real severe bear window (window 6, 2022-04 to 2023-05 — the
LUNA/FTX crash era), combined actually did best (−17.0%, vs trend-break's
−25.6% and asymmetric's −29.5%) — the *opposite* of the whipsaw problem the
2026-10-03 writeup documented for combined in-sample. Read directly from the
mechanics: covering the moment the regime leaves bear/crisis hurts during an
ordinary pullback inside a still-intact uptrend (whipsaw), but helps during a
genuine crash by exiting before a post-crash bounce gives back gains — same
mechanism, opposite effect depending on what kind of decline it actually is.

**A measurement-reliability problem, found and flagged rather than worked
around:** the "captured-edge" percentage this item's prior writeups have used
throughout breaks down badly here. Two of the three bear windows have tiny
headroom (buy&hold only −6.2%/−5.0%), so dividing a strategy's return by that
small denominator amplifies ordinary variance into swings past ±400% —
trend-break's own "captured" figure in window 2 comes out to 497%, which is
not a real measurement of anything, just noise divided by a near-zero number.
Raw mean return, not mean captured-edge, is the number to trust when headroom
is this small. Flagging this for any future session that reaches for the
captured-edge summary on a narrow-window sweep: check the headroom magnitude
first.

## Reading

The directional claim behind COMBINED/ASYMMETRIC — "requiring the regime
signal to agree with trend-break reduces average losses" — survives this
out-of-sample check meaningfully better than the slope_lookback sweet spot
did. But "better on average across 8 independent windows" and "a reliable
signal" are different claims, and this data supports only the first one: no
single variant wins consistently, and the strongest-looking candidate on
paper (combined) owes most of its apparent edge to a single extreme window.
Asymmetric is the more trustworthy of the two on this evidence — smaller
average edge, but it doesn't evaporate when the lucky window is removed.

This does not change the still-open, still owner-gated question of whether
or how the Researcher should ever be allowed to open a short position — if
anything it sharpens the bar again, the same way the 2026-10-17 result did:
even the item's best-looking result so far is "modestly better than the
unfiltered baseline on average, inconsistent window to window," not
"profitable" or "reliable." If this item is picked up again, the next step
is the kind of question `dual-trend-oos` raised for its own result — whether
a genuinely different combination or signal can be found whose advantage
doesn't concentrate in one window — not re-reading today's output again.

## Verification

- `python3 -m pytest -q`: 474/474, both after shipping the new CLI command
  (before running it) and unaffected throughout (no module source touched).
- `py_compile` clean on `evotrader_bundle.py`.
- `regime-combo-oos` is read-only by construction (same discipline as every
  other `short-headroom`/`*-oos` diagnostic in this repo): no genome
  mutation beyond what `Analyst._regime` already reads from the live
  genome, no `RiskJudge`/`SuperiorJudge` code path, no `live_state.json`
  touch, no council. `live_state.json` md5 unchanged across this entire
  session.
- Genome still v3 (1d) live, untouched. No trading this session (markets
  don't need weekend attention; this was deliberately evolution/research
  time, not a trading tick).

## Commits

- `b9b79df` — `Add regime-combo-oos diagnostic: OOS check for combined/asymmetric short signals`
- (this writeup + AGENTS.md update, same session)
