# Weekend all-hands, 2026-11-08 ~06:00-07:xx UTC

## Setup

- `git config user.name "Burk"` / `user.email` to the noreply address (local
  config only).
- Container started in detached HEAD (12 unrelated commits left behind from
  this container's own earlier history, not a real divergence). `git
  checkout main` + `tools/git_sync.py` fast-forwarded cleanly through a
  batch of 2026-11-07/11-08 commits already pushed by other sessions
  (`4bf11f6`), no divergence, no shallow-clone staleness.
- `python3 -m pip install -r requirements.txt -q` — the recurring `pip3` vs
  `python3 -m pip` split on this container (tracked under AGENTS.md items
  9/12's history); `pip3 install ...` failed with no numpy/pandas, `python3
  -m pip install ...` fixed it immediately.
- Baseline `python3 -m pytest -q` → 493/493 before any change.
- `review-hard-calls` → 0 pending (6 reviewed, unchanged).
- `AGENTS.md` size at session start: 245,541 bytes — comfortably under the
  256KB single-read threshold at that point.

## What this session worked on

Picked up AGENTS.md item 5 (short selling). The last several weekend
all-hands sessions (2026-09-26 through 2026-11-07) have built an increasingly
deep evidence base on whether a usable short-timing signal exists for this
universe using only daily OHLCV data: a basket-wide regime switch
(2026-09-27), a per-symbol price-only trend-break (2026-10-03), two
regime-based AND/OR combinations with trend-break (`combined`/`asymmetric`,
2026-10-03/04), a TEMPORAL confirmation dimension (`dual-trend`, the slow
SMA's own slope, 2026-10-11, OOS-checked 2026-10-17), a CROSS-SECTIONAL
confirmation dimension (`breadth-trend`, fraction of the universe also
breaking down, 2026-10-31, OOS-checked 2026-11-01), and a combination of the
two non-regime dimensions (`dual-breadth-trend`, 2026-11-07). The 2026-11-07
writeup's own "Next" section named the concretely scoped next step: "a
genuinely different kind of signal (not another temporal/cross-sectional
combination of the same two price-only primitives)."

### New signal: realized volatility expansion

Built `loop.engine.benchmark_vol_expansion_short` — a third, structurally
different confirmation dimension. Instead of asking whether the trend is
confirmed over a longer timeframe (dual-trend) or confirmed across the
universe (breadth-trend), this asks about the *character* of the move
itself: is the pullback accompanied by a real expansion in realized return
volatility (short-term stdev well above long-term), the signature of a
genuine breakdown, or is it a quiet drift that happens to clear the
trend-break threshold? Computed directly from the same per-symbol closes
every sibling benchmark in `loop/engine.py` reads — never
`agents.analyst.Analyst`'s own `vol_ratio` feature or any genome, same
genome-independence discipline the whole module uses. Entry requires
trend-break's own condition (fast/slow SMA ratio below `short_enter`) AND
`vol_ratio` (short-term/long-term realized return stdev) at or above
`vol_ratio_threshold`; covering is trend-break alone, same ablation
discipline every sibling here uses so the entry filter's effect is isolated.

12 new tests (`tests/test_vol_expansion_short.py`): never shorts a sustained
bull run, a calm low-noise decline gets filtered out by a high threshold
while plain trend-break fires freely on it, a genuinely volatile decline
does get shorted, costs/borrow only ever reduce the return, per-symbol
independence in a mixed basket, the usual empty/too-short/bars-accounting
edge cases, and three direct unit tests of the new `_realized_vol_ratio`
helper. Full suite 493 → 505. Wired into `short-headroom --vol-expansion
[--vol-ratio-threshold/--vol-short/--vol-long]` and a new `vol-expansion-oos`
command, built from the same template `dual-trend-oos`/`breadth-trend-oos`
already established (sweep against `history-perturb --independent`'s
tiling instead of the champion's own 4 windows, mean return as the primary
statistic, captured-edge reported separately with the thin-headroom
caution this item's history has already learned to apply).

`loop/engine.py` is not `_PROTECTED` — `evotrader.manifest`/the constitution
checksum (`726dfa4bac85891a`) is unchanged throughout. Synced into
`evotrader_bundle.py` via `tools/edit_bundle_module.py sync` before any test
ran against it (the bundle's own meta-path finder is what every test
actually imports from — a lesson re-learned mid-session when the new test
file failed to import `benchmark_vol_expansion_short` from a pristine
`loop.engine` import but worked when imported directly: `tests/conftest.py`
imports `evotrader_bundle` to install its embedded modules, so until `sync`
ran, the tests were seeing the *old* bundle's `loop.engine`, not the real
file just edited).

### First read: in-sample, against the live champion's own 4 windows

Run in the same session, same data snapshot as `trend-break`/`dual-trend`/
`breadth-trend`, so directly comparable:

| window | trend-break | dual-trend | breadth-trend | vol-expansion (th=1.3, default) |
|---|---|---|---|---|
| fold 1 (bull) | -31.7% | -11.9% | -36.6% | -19.6% |
| fold 2 (bull) | -39.2% | -24.6% | -43.8% | -28.8% |
| fold 3 (bear, % captured) | +18.3% (78%) | +13.6% (58%) | +24.6% (105%) | +2.8% (12%) |
| holdout (bull) | -8.9% | -9.6% | -1.3% | -10.5% |

vol-expansion is the most selective of the four (avg concurrent short
3.84-8.79, vs. 6.78-13.90 for the other three): it beats plain trend-break
and breadth-trend in both bull folds, but loses to dual-trend there, and its
bear-window capture (12%) is far below all three others (58-105%) — the
worst showing of any variant tried in this item's whole history on the one
window that actually matters.

Swept `vol_ratio_threshold` ∈ {1.0, 1.1, 1.2, 1.3, 1.5, 2.0} against the same
4 windows: bear-window capture rose roughly monotonically with the threshold
(-41% at 1.0 up to +22% at 1.5, then **zero trades at all** at 2.0 — too
strict for this universe at `vol_short=10`/`vol_long=40`), and mean return
across all 4 windows was best at 1.5 (-7.2%, vs. the shipped default 1.3's
-14.0%). This is exactly the shape of dual-trend's own `slope_lookback`
40-50 "sweet spot" before `dual-trend-oos` checked it and found it didn't
survive — so the obvious next step was to check this one the same way
before trusting it.

### Out-of-sample check

`vol-expansion-oos`, both tilings, same discipline `dual-trend-oos`/
`breadth-trend-oos` used:

**2.0y tiling** (5 windows, all bull — the same "no 2-year stretch in this
history nets bearish" finding every prior `-oos` check on this universe has
made):

| | trend-break | th=1.0 | th=1.1 | th=1.2 | th=1.3 | th=1.5 | th=2.0 |
|---|---|---|---|---|---|---|---|
| mean return | -3.4% | **+4.1%** | **+1.2%** | -15.6% | -16.6% | -13.0% | +0.0% |

The in-sample "best" value (1.5) is one of the worst here; the two values
that actually beat trend-break (1.0/1.1) are the loosest ones tried — the
opposite direction from what the in-sample sweep suggested.

**1.1333y tiling** (9 windows, 2 genuinely bearish — window 2, 2017-10 to
2018-12, buy&hold -45.9%; window 6, 2022-04 to 2023-06, buy&hold -50.8%, the
LUNA/FTX era):

| | trend-break | th=1.0 | th=1.1 | th=1.2 | th=1.3 | th=1.5 | th=2.0 |
|---|---|---|---|---|---|---|---|
| mean return | -9.2% | -11.6% | -12.1% | -16.5% | -16.4% | **-5.4%** | +0.0% |
| bear-window captured-edge | — | +22.0% | +22.5% | -22.6% | -23.6% | +5.0% | +0.0% |

On this tiling, 1.5 *does* win on mean return — but the bear-window capture
ranking inverts relative to both the in-sample read and the mean-return
ranking on this same tiling: the lowest thresholds (1.0/1.1) capture the
most of the two real bear windows' edge, while 1.2/1.3 are net losses and
1.5 (the mean-return winner) barely captures anything.

No single `vol_ratio_threshold` wins on both tilings, and no threshold's
bear-window behavior is consistent between the in-sample read and either
out-of-sample tiling.

## Reading, for item 5 overall

Three structurally different price-only confirmation dimensions have now
been tried against trend-break's entry — temporal (dual-trend),
cross-sectional (breadth-trend), and volatility-character (vol-expansion) —
plus two regime-based combinations and one dimension-combination
(dual-breadth-trend). Every one of these six variants has shown the same
shape: an apparent in-sample improvement at some parameter value that either
fails its out-of-sample check outright (dual-trend, vol-expansion) or
survives only partially and non-dominantly across tilings (breadth-trend,
dual-breadth-trend), and none has ever been shown, out of sample, to
reliably profit in a real severe crash — the thing a short-selling
capability would actually be for.

This is now a consistent pattern across three independently-constructed
signal types, not a property of one unlucky dimension. Recorded as a
recommendation, not a decision (this item's real design work still needs
owner sign-off per "Owner decisions pending" before any of it could be wired
into a real short-opening path): further search inside this same family —
another confirmation dimension computed from the same daily OHLCV data,
swept and OOS-checked the same way — looks to be running into a real
ceiling, not a string of bad luck, and is unlikely to be the highest-value
use of a future session's time on this item. A genuinely different kind of
input (a measured crypto borrow rate instead of the modelled constant every
result in this item has used, on-chain or order-book data, or accepting that
daily OHLCV alone may not contain a reliably-OOS short-timing signal for
this universe) looks more promising than another scalar-threshold sweep on
the same data.

## Verification

- `python3 -m pytest -q` 493 → 505 passed, both before and after the new
  code (baseline run at session start, full run again after the commit).
- `python3 tools/edit_bundle_module.py sync --check` clean after the
  `loop/engine.py` edit was synced into `evotrader_bundle.py` (confirmed the
  bundle's own meta-path finder is what tests import from, not the bare
  files — `tools/edit_bundle_module.py sync` had to run before the new
  tests could even import the new function).
- `from constitution import checksum` → `726dfa4bac85891a`, unchanged
  (`loop/engine.py` is not `_PROTECTED`); `evotrader.manifest` untouched.
- `live_state.json` md5 checked identical before and after this session's
  entire diagnostic work — all of it was read-only (new benchmark function,
  new CLI flags/command, new tests), no genome mutation, no council, no
  trading.
- No dashboard rebuild this session: nothing in `live_state.json` changed,
  so `index.html` would be byte-identical to its current committed state.

## Housekeeping

`AGENTS.md` had regrown to 254,330 bytes after this session's own additions
(within ~1.7KB of the 256KB single-read threshold, the same tight margin
that has triggered every prior rotation in this index) — archived the
oldest remaining slice (all eight 2026-11-06 3-hourly-check entries)
verbatim to new `AGENTS_ARCHIVE_2026-11-06.md`, verified via exact
line-range removal (the removed 320-line block diffed byte-for-byte
identical against the new archive file's body) and `python3 -m pytest -q`
unaffected (text-only change). File now 233,480 bytes.

## Next

If item 5 is picked up again: per the reading above, prefer a genuinely
different *kind* of input over another price-only confirmation dimension on
the same daily OHLCV data — three of those have now been tried and all
three show the identical in-sample-sweet-spot-doesn't-survive-OOS shape.
Otherwise, this item's real remaining work is still the owner-gated design
question from "Owner decisions pending" — whether/how the Researcher should
ever be allowed to propose a short at all — which no amount of further
signal search resolves on its own.
