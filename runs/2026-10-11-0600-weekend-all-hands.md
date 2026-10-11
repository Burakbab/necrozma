# Weekend all-hands — 2026-10-11 ~06:00-07:40 UTC

## Context

Picked up AGENTS.md item 5 (short selling)'s most recent open thread: the
2026-10-04 writeup had tried three ways of combining `benchmark_trend_break_short`
(a per-symbol, price-only trend-breakdown signal) with
`benchmark_regime_conditional_short` (the basket-wide `Analyst._regime`
classifier already used to gate long entries) — regime-conditional alone,
AND-gated "combined", and the asymmetric variant that covers on trend-break
alone. All three landed on the same conclusion: the *regime* half of every
combination is the weak link. Its `bear` leg fires almost as often as
individual symbols' own trend-break during ordinary pullbacks inside a
still-intact bull market, so it barely filters false-positive entries and
whipsaws badly on the exit side. The writeup's own next step was explicit:
"a genuinely new signal to pair with trend-break, not another way of wiring
the existing regime classifier to it."

Other candidates considered and set aside for this session: item 13
(holdout-sigma calibration) already got a full quantified design pass last
weekend (2026-10-10) and is sitting on an owner decision with nothing new to
measure; item 6 (equities/FX) is blocked on a human picking a data source;
items 2/3/4 are closed/parked. Item 5's "build the genuinely new signal" was
the one open item that was both unblocked and matched "build a queued
roadmap item" from the weekend brief, rather than another routine 15-gen
`evolve` batch (which every 3-hourly check already runs, with the champion's
fold-aggregate fitness flat for weeks).

## What was built

`loop.engine.benchmark_dual_trend_short` — same per-symbol, price-only
entry as `benchmark_trend_break_short` (fast/slow SMA ratio below
`short_enter`), plus a second confirmation dimension that is genuinely
different from basket-wide regime: TIMEFRAME agreement. A short only opens
when the slow SMA's own value is no higher than it was `slope_lookback`
bars ago — i.e. the medium-term trend itself has to be turning down, not
just dip briefly while a longer uptrend keeps climbing. Covering is left to
trend-break alone (`trend > short_exit`), the same ablation discipline
`benchmark_asymmetric_short` used, so the new entry filter's effect is
isolated from any change to exit timing.

9 new tests in `tests/test_dual_trend_short.py`, including one constructed
specifically to demonstrate the filter's mechanism: a brief sharp dip
embedded in an otherwise-rising price path trips plain trend-break's entry
(the fast SMA reacts quickly) but is blocked by the slope filter (the slow
SMA, dominated by the ~27 unaffected bars in its 30-bar window, never shows
a negative slope before the dip itself recovers). Full suite: 465 → 474,
all passing.

Wired into the CLI as `short-headroom --dual-trend`, next to the existing
`--trend-break`/`--combined`/`--asymmetric` tables — same report-table
shape (0bp / +borrow / captured-fraction-of-zero-cost-edge columns).

Mechanically: `loop/engine.py` (the real, normally-importable file) was
edited directly, then `tools/edit_bundle_module.py sync` regenerated
`evotrader_bundle.py`'s embedded `_SRC['loop.engine']` from it. The CLI
dispatch block for `short-headroom` is plain top-level script code in
`evotrader_bundle.py`, not part of `_SRC`, so that was hand-edited
separately (import line, a `dual_trend = "--dual-trend" in sys.argv` flag,
and a new report block mirroring the `asymmetric` block's structure).
`tools/edit_bundle_module.py sync --check` and `verify` both clean
throughout.

## What was measured

Ran `short-headroom --dual-trend --trend-break` against the real live v3
genome's real universe, 4 years of real Binance daily bars, at the
function's shipped default (`slope_lookback=20`):

| window | buy&hold | trend-break (+borrow) | dual-trend (+borrow) |
|---|---|---|---|
| fold 1 (bull) | +89.8% | -33.1% | -34.2% |
| fold 2 (bull) | +152.6% | -49.9% | -33.9% |
| fold 3 (bear) | -43.5% | +44.1% (101% capt.) | +32.4% (75% capt.) |
| holdout (bull) | +54.9% | -23.6% | -20.5% |

Mixed at this one parameterization: fold 2 and holdout improve, fold 1 is
essentially flat (slightly worse), fold 3's bear-window capture drops 26
points. Rather than report that one point as the finding, swept
`slope_lookback` directly against the same four real windows
(`fast`/`slow`/`short_enter`/`short_exit` left at defaults, genome's own
fee/slippage, borrow=3bps/bar) — this is cheap (reuses the already-loaded
4-year `Replay`, no new data fetch) and the earlier items in this thread
(combined, asymmetric) had each only ever reported one fixed
parameterization before concluding, so it was worth checking whether this
one generalizes or whether a different setting tells a different story:

| slope_lookback | fold 1 | fold 2 | fold 3 (% capt.) | holdout |
|---|---|---|---|---|
| 10 | -32.7% | -43.6% | +40.5% (93%) | -20.7% |
| 20 (default) | -34.2% | -33.9% | +32.4% (75%) | -20.5% |
| 30 | -29.3% | -38.5% | +34.9% (80%) | -19.8% |
| 40 | -11.3% | -30.5% | +35.5% (82%) | -21.5% |
| 50 | -8.9% | -29.1% | +37.2% (86%) | -22.3% |
| 60 | -5.6% | -29.6% | +30.5% (70%) | -23.7% |
| 80 | -7.2% | -26.2% | +12.2% (28%) | -18.5% |
| plain trend-break | -33.1% | -49.9% | +44.1% (101%) | -23.6% |

There's a real, non-monotonic sweet spot at 40-50: fold 1's loss shrinks by
roughly 24 points and fold 2's by roughly 20 points relative to plain
trend-break, while fold 3's capture only gives up 15-19 points (82-86% vs
101%) — not the steep trade-off the regime-based combinations always hit.
Past 60 the filter gets strict enough to also block genuine late-decline
entries and fold 3's capture collapses (70%, then 28% at 80).

## Reading, and what this doesn't justify

This is the best frontier point this item has found across its whole
combination/confirmation history — a real improvement in 2 of 4 real
windows at a meaningful margin, for a comparatively small giveback in the
one window that matters most. It is still not a profitable signal overall
(fold 1/2/holdout are all still net losses at every `slope_lookback` tried,
just smaller ones), and it is explicitly *not* a cross-validated parameter
choice: the sweep was read directly off the same four windows it's being
judged against. Picking 40 or 50 as "the" value from this table would be
exactly the in-sample parameter mining the repo's whole fold/holdout
discipline exists to catch — so the function's shipped default was left at
20 rather than quietly reset to whatever looked best in this one table. A
real proposal would need to either let `evolve`'s own fold-aggregate-plus-
sealed-holdout gate choose `slope_lookback` (once this signal is wired into
something `evolve` can actually mutate) or justify a fixed value some other
way.

This does not touch the still-open, still owner-gated question of
whether/how the Researcher should ever be allowed to open a short at all —
nothing here is more than a reason to keep refining what a real signal
might look like. Read-only throughout: no genome, no `RiskJudge`/
`SuperiorJudge` code path, no `Analyst` involvement, no `live_state.json`
touch.

## Housekeeping

`AGENTS.md` had grown to 252,467 bytes after this session's own additions
(from 250,026 bytes before). Archived the oldest remaining dated slice (all
eight 2026-10-07 3-hourly-check entries) verbatim to new
`AGENTS_ARCHIVE_2026-10-07.md`, verified byte-identical via direct diff
against the extracted slice before deleting it from the live file. Live
file now 231,929 bytes.

## Verification before commit

- `python3 -m pytest -q`: 465 passed before any change; 474 passed after
  (9 new tests, 0 regressions).
- `tools/edit_bundle_module.py sync --check` / `verify`: clean, no drift,
  round-trip identical.
- `python3 -m py_compile evotrader_bundle.py`: clean.
- `git status`: only `AGENTS.md`, `evotrader_bundle.py`, `loop/engine.py`
  modified, plus two new files (`AGENTS_ARCHIVE_2026-10-07.md`,
  `tests/test_dual_trend_short.py`) — `live_state.json` untouched, as
  expected for a read-only diagnostic session with no `tick`/`evolve` call.
- Constitution checksum unchanged throughout (`loop/engine.py` is not a
  `_PROTECTED` file).

## Next

Per AGENTS.md item 5's own discipline: don't chase a fourth variant in the
same sitting. If this item is picked up again, the concretely scoped next
steps are (a) checking whether the 40-50 sweet spot holds up under a
genuinely out-of-sample check (e.g. `--independent` fixed, non-overlapping
historical windows the way `history-perturb` uses, rather than the same
four fold/holdout windows this sweep used), or (b) scoping what it would
take to let a real search process (not a hand-run sweep) tune
`slope_lookback` against the fold-aggregate-plus-holdout gate directly.
Neither was attempted here — this session stopped at reporting the
sweep honestly, same as the asymmetric/combined writeups before it.
