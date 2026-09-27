# Weekend all-hands, 2026-09-27 (~06:00-07:20 UTC)

One piece of work this session: testing the first real regime-conditional
short design against the live v3 champion, and an AGENTS.md size rotation.

## Why this, not another `evolve` batch

Read `AGENTS.md`'s "Owner decisions pending" and "Next steps" before
starting, and skimmed the last several days of `runs/` notes. Items 6
(equities/FX data source) and 13 (`HOLDOUT_SIGMA` calibration) are both
explicit owner-only calls the file says not to re-litigate with more
diagnostics. Items 2/3/3a/8/9/10/11/12 are closed or resolved. Item 7
(bundle unflatten) is feature-complete and explicitly optional/last. Every
3-hourly check for the last several days has run one more 15-generation
`evolve` batch against the live v3 champion with the same result each
time: fold-aggregate fitness holds flat, no candidate clears the
ever-rising cumulative multiple-testing margin (item 13's own subject).
That pattern is real and worth continuing on the weekday cadence, but a
weekend slot's extra time budget is better spent on the one open item
with real, un-owner-gated engineering room left: item 5 (short selling).

Yesterday's weekend session (2026-09-26) shipped `short-headroom` and
found a permanent, always-on equal-weight short would have been
catastrophic in 3 of the champion's 4 real windows (all bull markets) and
only helped in the one real bear window. That result explicitly sharpened
the open question rather than closing it: "what this argues for, if this
is ever built, is a regime-conditional entry signal... rather than a
standing position." This session picked up exactly that thread — same
"measure before building" discipline item 3's correlation-penalty saga
established (measure the simplest possible construction first, before
designing anything new), applied to the simplest possible
regime-conditional short: gate it on the regime classifier that already
exists live, rather than inventing a new one.

## What was built

`loop.engine.benchmark_regime_conditional_short(replay, genome, symbols,
start, end, cash, fee_bps, slippage_bps, borrow_bps_per_bar, bars_per_year,
short_regimes)` — a sibling to `benchmark_sell_short`. Same equal-weight
basket and real `PaperBroker.short()`/`.mark()`/`.cover()` mechanics, but
instead of opening once and holding for the whole window, it walks the
window bar-by-bar the same way `run_backtest`/`Council.tick` do (mark at
bar i's close, decide, fill at bar i+1's open) and calls
`agents.analyst.Analyst.brief()` once per bar to read `Briefing.regime` —
the exact, causal classifier `RiskJudge.rule`'s own `regime_scale` gene
already uses to gate *long* entries, computed only from data each
`ReplayWindow` can see. The short opens (basket re-sized off the broker's
own current cash, split evenly, no leverage) the first bar the regime
reads one of `short_regimes` (default `("bear", "crisis")`) and covers in
full the first bar it doesn't. `equity`/`cash`/`weights` passed into
`brief()` only feed fields `_regime` never reads, so they can't bias the
regime call itself.

New CLI flag: `short-headroom --regime-conditional [--short-regimes
bear,crisis|crisis|bear]`. Prints a second table next to the existing one,
split into a zero-cost column (isolates whether the signal is even
directionally right) and a real-cost column (adds the fee/slippage/borrow
drag from repeated flip/re-entry), plus bars-short and flip counts —
mirroring `short-headroom`'s own 0bp-vs-+borrow decomposition for the
permanent short.

8 new tests, `tests/test_regime_conditional_short.py`: a hand-built small
genome (small analyst gene periods so a ~150-bar synthetic series clears
warmup well before the test's own `start` index) against a pure bull run
(never shorts, zero trades, zero return), a pure decline (shorts through
it, profits), a bull-then-bear window (flat through the bull half,
engages only once the decline starts — the actual "conditional" behavior
under test), the costs/borrow-only-ever-reduce-return invariant, two
symbols both traded in a shared decline, and the two empty-result
contracts (`benchmark_sell_short` already has). Full suite 434 → 441
passed, both before and after.

Mechanical note carried over from yesterday's session: this repo's test
suite imports through `evotrader_bundle.py`'s meta-path finder, not the
real files directly, so `tools/edit_bundle_module.py sync` was run
immediately after editing `loop/engine.py`, before the first test run.

## First result

```
$ python3 evotrader_bundle.py short-headroom --regime-conditional

SHORT-THE-INDEX HEADROOM BY FOLD/HOLDOUT -- equal-weight, static, un-managed
  window       bars   buy&hold  short 0bp  short+borrow   captured
  fold 1        353    +89.0%    -85.6%       -99.8% n/a (bull)
  fold 2        414   +141.8%   -134.4%      -153.8% n/a (bull)
  fold 3        414    -42.3%    +38.5%       +28.7%       +68%
  holdout       219    +58.0%    -59.1%       -65.8% n/a (bull)

REGIME-CONDITIONAL SHORT -- gated on Analyst._regime in bear/crisis (borrow=3.0bps/bar)
  window       bars  bars short  flips  regime 0bp  regime+borrow   captured
  fold 1        353    170/353      14      -5.0%        -11.4% n/a (bull)
  fold 2        414    146/414      12     -30.2%        -34.7% n/a (bull)
  fold 3        414    258/414      17      -5.6%        -13.9%       -33%
  holdout       219     92/219       6      +2.5%         -0.9% n/a (bull)
```

(Yesterday's `short-headroom` numbers moved a few tenths of a point
between sessions — `-85.3%`→`-85.6%` etc. — because both runs pull fresh
market data via `market.load_universe`, and the trailing 4-year "as-of"
window shifts by a day between sessions. Not a discrepancy, just the same
day-to-day drift `fold-date-sensitivity` already documents.)

Gating on `bear,crisis` — the default, mirroring `regime_scale`'s own
gate exactly — is **worse than the permanent short in all four windows,
including the one real bear window.** The number that matters most is
fold 3's zero-cost column: `-5.6%`, a loss, in the one window where the
market itself fell -42.3% and the *always-on* short's zero-cost return
was `+38.5%` in the same span. Conditioning on this signal doesn't just
add cost drag on top of a good idea — it's directionally wrong often
enough, even before any cost, to erase the edge that was sitting there
for the taking.

Checked why directly: `Analyst._regime`'s `bear` branch is
`anchor_score < -0.03 or breadth < 0.30` — an easily-tripped OR, tuned to
gate long entries defensively (better to miss a few good entries than
buy into a real decline), not to time a short. It fires on ordinary
pullbacks inside a still-intact trend as readily as on the start of a real
bear leg, so the position flips on and off 12-17 times per window and a
meaningful share of "bear" bars are dip-buying opportunities in disguise.

Narrowing to `--short-regimes crisis` — the classifier's much stricter
AND-gated branch (`anchor_dd < -0.22 and anchor_volr > 1.35`) — fixes the
false-positive problem outright: zero bars short in either bull fold
(0/353, 0/414), and fold 3's zero-cost return flips positive (+4.2%,
real-cost +3.2%, capturing +8% of the theoretical edge). But that's a
small fraction of the always-on short's +68% captured in the same window,
for being short only 13 of fold 3's 414 bars — safe, but not worth much.

```
$ python3 evotrader_bundle.py short-headroom --regime-conditional --short-regimes crisis
  window       bars  bars short  flips  regime 0bp  regime+borrow   captured
  fold 1        353      0/353       0      +0.0%         +0.0% n/a (bull)
  fold 2        414      0/414       0      +0.0%         +0.0% n/a (bull)
  fold 3        414     13/414       4      +4.2%         +3.2%        +8%
  holdout       219      5/219       2      +1.3%         +0.9% n/a (bull)
```

## Reading, and what this does/doesn't decide

This rules out the cheapest version of "add regime-gating to the short" —
reusing the long-entry regime signal as-is — the same way yesterday's
result ruled out "just add a permanent short overlay." Neither of the
classifier's two thresholds is a usable short-timing signal: `bear` is too
noisy (loses money on the exact window it's supposed to catch, before any
cost), `crisis` is safe but too rare to capture meaningful edge (13 bars
out of a 414-bar bear market). A real regime-conditional short would need
a purpose-built, short-specific timing signal — something that
distinguishes "this decline is real" from "this is a pullback in an
uptrend" more precisely than either existing threshold — which is
materially more design and validation work than "gate on regime" implied
before this was measured. This sharpens the still-open Phase 2 design
question again rather than answering it, same as yesterday's result did
for the "just add a short" version.

Nothing here is a proposal, gene, or code path a real search can reach: no
genome field changed, no `RiskJudge`/`SuperiorJudge` code path for opening
a short exists yet, `short_regimes` is a plain function parameter (and
now a CLI flag) with no mutation range, and `live_state.json` was
untouched throughout. The two owner-gated constitution questions from the
2026-08-30 design pass (a short-exposure cap; whether `MAX_DD_HARD_FAIL`
needs a short-specific instrument) still need a human decision before any
real wiring, whatever this measurement found.

Verified before commit: `python3 -m pytest -q` 441/441, both immediately
after this piece and again after the housekeeping below; `tools/
edit_bundle_module.py sync --check`/`verify` both clean; `evotrader.manifest`
unchanged (`726dfa4bac85891a`) — only `loop/engine.py` (a new function,
additive) and `evotrader_bundle.py`'s own CLI dispatch section changed,
neither checksummed; `core/portfolio.py` untouched. `live_state.json`
untouched throughout.

## Housekeeping: AGENTS.md size rotation

`AGENTS.md` was at 253,356 bytes after writing up the finding above —
close enough to the 256KB single-read limit (same recurring pattern every
prior rotation in its own archive index has hit) that another day or two
of 3-hourly `evolve`-batch entries would have crossed it. Archived the
next oldest slice of the chronological "Current state" log — 2026-09-21
~00:46 through 2026-09-22 ~21:46 UTC, 17 entries — verbatim into new
`AGENTS_ARCHIVE_2026-09-21_to_2026-09-22.md`, using an exact-marker Python
line-slice (not manual counting) and verifying the moved slice's entry
count matched exactly and none were left behind or duplicated in the main
file afterward. `AGENTS.md` now 215,718 bytes; keeps everything from
2026-09-23 ~00:48 UTC onward, plus the full "Owner decisions pending",
promotion-history, "Measured", and "Rules" sections, which have never
been part of any rotation. No code touched by this step; `python3 -m
pytest -q` re-confirmed 441/441 after it (expected — text-only change).

## Not attempted this session

Designing or building an actual short-timing signal (the result above
argues one would need to be purpose-built, not a reuse of `_regime`) — that's
real design work, appropriately scoped to a future session, not a
tail-end addition here. Also not attempted: checking whether a
differently-tuned `anchor_score`/`breadth` threshold (short of a full new
signal) narrows the gap between `bear`'s false-positive rate and
`crisis`'s low capture rate — a natural next question if this thread is
picked up again, but this session judged the three-way comparison already
run (permanent / bear-gated / crisis-gated) as a complete, well-verified
piece of evidence on its own, not something to keep tuning speculatively
in the same sitting.
