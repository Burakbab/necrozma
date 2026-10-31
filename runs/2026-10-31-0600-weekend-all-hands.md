# Weekend all-hands, 2026-10-31

## Context

Synced cleanly from `main` (one commit, `322282a`, a 3-hourly evolve batch,
already merged into `origin/main` by the time this session checked out `main`
— fast-forwarded with no divergence). `AGENTS.md` was 247,608 bytes at session
start, comfortably under the 256KB single-read rotation threshold, so no
archival pass was needed this cycle.

Reviewed recent `runs/` history: the last ~2 weeks of 3-hourly checks have
been almost entirely 15-generation `evolve` batches against the live v3 (1d)
champion, none promoting (stagnation counter at 6749 as of the most recent
one). Item 13 (holdout-sigma calibration) has a quantified design pass
(2026-10-10) already sitting with the owner. Item 6 (equities/FX) needs an
owner decision on data source before any code is worth writing. Item 5
(short selling) has the most active open research thread: the 2026-10-24
session (`regime-combo-oos`) closed with an explicit instruction for
whoever picks this up next — "whether a genuinely different combination can
be found whose advantage doesn't concentrate in one window, not re-reading
this same output" — and separately flagged that "the regime half of every
combination tried is the weak link... a genuinely new signal to pair with
trend-break, not another way of wiring the existing regime classifier to
it" is what the next session should try. This session picked that up.

## What was built

`loop.engine.benchmark_breadth_trend_short` — a second non-regime
confirmation dimension for `benchmark_trend_break_short`'s entry signal,
after `benchmark_dual_trend_short` (2026-10-03/04) already tried a TEMPORAL
one (the slow SMA's own trajectory over time). This one is CROSS-SECTIONAL:
a symbol opens a short only when (a) its own fast/slow SMA ratio drops below
`short_enter` (trend-break's existing entry trigger) AND (b) at least
`breadth_threshold` (default 0.4) of the universe's own symbols are *also*
reading a breakdown this same bar. The idea: an idiosyncratic single-symbol
pullback inside an otherwise-intact bull market (the exact false-positive
mechanism that makes a naive per-symbol short lose money) should look
different from a broad-based decline where many symbols break down
together — and breadth is a purely price-only way to tell them apart
without touching `agents.analyst.Analyst._regime` (the basket-wide switch
that `regime-conditional`/`combined`/`asymmetric` all found to be a weak,
noisy link) or any genome at all.

Covering is governed by trend-break alone (`trend > short_exit`), same
ablation discipline `dual-trend`/`asymmetric` both used — isolates the new
entry filter's own effect without also changing exit timing.

Implementation: `loop/engine.py` (edited directly, then
`tools/edit_bundle_module.py sync` to regenerate `evotrader_bundle.py`'s
embedded copy — `verify` round-tripped clean, `sync --check` confirmed no
drift after). 10 new tests in `tests/test_breadth_trend_short.py`,
synthetic price paths with known breadth by construction (a lone declining
symbol inside an otherwise-bullish 4-symbol universe is blocked at the
default threshold but let through once the threshold is lowered below the
universe's own breadth ceiling; a majority-declining universe clears the
default threshold normally; cost/borrow monotonicity; bars-short
accounting). Full suite 474 → 484, all green. Wired into
`short-headroom --breadth-trend [--breadth-threshold X]`, docstring/usage
line added, no `_PROTECTED` file touched (`loop/engine.py` isn't one;
`evotrader.manifest` unchanged, confirmed by direct read:
`726dfa4bac85891a`, matches AGENTS.md's recorded value).

## What was measured

Real 4-year backtest against the live champion's current four fold/holdout
windows (genome's own fee/slippage, 3.0bps/bar modelled borrow), trend-break
vs. dual-trend vs. breadth-trend (default threshold 0.4) side by side:

| window | trend-break | dual-trend | breadth-trend |
|---|---|---|---|
| fold 1 (bull, b&h +219.0%) | -45.7% | -11.7% | **-49.5% (worst)** |
| fold 2 (bull, b&h +60.6%) | -36.1% | -20.7% | **-41.0% (worst)** |
| fold 3 (bear, b&h -14.0%) | +12.9% (92% capt.) | +8.9% (63% capt.) | **+18.2% (130% capt.)** |
| holdout (bull, b&h +37.3%) | -15.3% | -12.5% | **-7.2% (best)** |

The headline finding is the fold 1/2 result: breadth-trend is the *worst*
of the three in both bull windows, even worse than plain trend-break with
no confirmation filter at all — the opposite of what dual-trend's temporal
confirmation found (a clear improvement in the same two windows). Checked
directly that this isn't a sizing artifact: avg concurrent short and flip
count are both slightly *lower* for breadth-trend than plain trend-break in
folds 1/2 (8.47/8.75 vs 9.07/9.49, fewer flips too) — the filter is more
selective, not less, and the trades it lets through anyway lose more on
average.

Reading: requiring many symbols to break down together is more likely to
catch a sharp, broad, synchronized pullback than an isolated one — and a
broad synchronized selloff inside an intact bull run is exactly the
"buy-the-dip" shape that tends to resolve in a sharp, broad, synchronized
rally. The cross-sectional filter ends up selecting for the *more*
dangerous setups to be short, not the safer ones. It is a real improvement
only where the champion's one actual bear window and holdout are concerned
— the opposite trade-off from dual-trend.

Swept `breadth_threshold` ∈ {0.2, 0.3, 0.4, 0.5, 0.6, 0.7} against the same
four windows to check whether the relationship is stable: fold 1 worsens
monotonically as the threshold rises (-45.4% → -51.6%); fold 2 moves the
*opposite* direction (-35.6% → -24.6%, improving as the filter gets
stricter); fold 3 — the one window where breadth helps — holds up through
0.5 (+91% to +130% captured) and then flips sign sharply at 0.6 (-145%
captured); holdout's smallest loss is at 0.5 (-0.9%) but is not a smooth
minimum (surrounded by worse values on both sides). No clean curve in any
window, and the window that matters most (fold 3) shows a sharp instability
rather than a gentle slope — the same shape of result `dual-trend`'s own
sweep had before `dual-trend-oos` showed its apparent sweet spot didn't
survive an out-of-sample check. Deliberately did not build a
`breadth-trend-oos` sibling this session or anoint a "best" threshold from
this table — that would repeat exactly the in-sample-mining mistake this
repo's fold/holdout discipline exists to catch, and `dual-trend-oos`
already demonstrated once that reading a parameter choice off the same four
windows it's scored against doesn't hold up.

**Reading for item 5 overall**: two genuinely different non-regime
confirmation dimensions have now been tried — temporal (dual-trend) and
cross-sectional (breadth-trend) — and they help in opposite places, neither
dominating. Dual-trend protects the bull markets but gives up some bear
capture (63% vs. plain trend-break's 92%); breadth-trend gives up
bull-market protection entirely (worse than no filter) but sharpens the one
real bear window to the best capture rate measured anywhere in this item's
history (130%) and improves holdout. This is the same non-dominance pattern
`regime-combo-oos` already found between combined/asymmetric/trend-break —
no single signal variant is a clean win, each trades one window's
protection against another's.

## Not attempted this session

- An out-of-sample check of breadth-trend (a `breadth-trend-oos` sibling to
  `dual-trend-oos`) — concretely scoped next step before trusting any
  threshold choice, same as `dual-trend` needed before this item trusted
  its own sweep.
- Combining breadth-trend with dual-trend (temporal AND cross-sectional
  both required) — an obvious next combination to try given they protect
  different windows, not attempted here; would need the same honest
  measure-first discipline the combined/asymmetric pair used.
- Any evolve batch this cycle — this session's time went to the diagnostic
  above instead; the regular 3-hourly checks continue the evolve cadence
  on their own schedule.
- Any change to item 13 (holdout-sigma) or item 6 (equities/FX) — both
  still explicitly owner-gated, no new information to add this session.

## Verification

- `python3 -m pytest -q` 474/474 baseline before any edit, 484/484 after
  (10 new, nothing broken).
- `tools/edit_bundle_module.py verify` round-tripped clean;
  `sync --check` confirmed zero drift after `sync`.
- `evotrader.manifest` checksum unchanged (`726dfa4bac85891a`) — no
  `_PROTECTED` file touched.
- `live_state.json` untouched throughout (read-only diagnostic, genome
  unmutated, no council, no broker call outside the benchmark's own
  isolated `PaperBroker` instance).
- `git status` clean of anything unexpected before commit (only the two
  edited files and one new test file).
