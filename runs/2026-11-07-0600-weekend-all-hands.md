# 2026-11-07 ~06:00-07:xx UTC — weekend all-hands

## What this session worked on

AGENTS.md's item 5 (short selling) has accumulated a long weekly history of
measuring individual confirmation signals for a short-timing entry: a
basket-wide regime switch (2026-09-27), a per-symbol price-only trend-break
(2026-10-03), two ways of combining trend-break with the regime signal
(2026-10-03/04), a temporal confirmation — the slow SMA's own trajectory
(`dual-trend`, 2026-10-11, out-of-sample-checked 2026-10-17), and a
cross-sectional confirmation — breadth across the universe (`breadth-trend`,
2026-10-31, out-of-sample-checked 2026-11-01). The 2026-10-31/11-01 writeups
both explicitly named the obvious next step: combine the two non-regime,
genuinely-independent confirmation dimensions (temporal + cross-sectional)
that had each been validated separately, instead of trying yet another
regime-based variant. This session did that.

## What shipped

New `loop.engine.benchmark_dual_breadth_trend_short`: opens a short only
when a symbol's own trend-break fires AND the slow SMA's trajectory is
flat-or-declining over `slope_lookback` bars (dual-trend's filter) AND at
least `breadth_threshold` of the universe is also breaking down the same
bar (breadth-trend's filter). Covering is trend-break alone, the same
ablation discipline every sibling benchmark in this module already uses —
isolates the entry filter's own effect without also changing exit timing.
9 new tests (`tests/test_dual_breadth_trend_short.py`): never-shorts-a-bull-run,
profits-on-a-synchronized-decline, blocks a single-symbol dip inside an
otherwise-climbing universe that plain trend-break alone would open, never
more permissive than either filter alone (it's an AND), monotonic in
`breadth_threshold`, costs/borrow only reduce return, empty-input and
too-short-window guards, bookkeeping consistency. Full suite 484 → 493.

Wired into two CLI surfaces in `evotrader_bundle.py`:
- `short-headroom --dual-breadth [--slope-lookback N] [--breadth-threshold X]`
  — same reporting shape as every sibling flag on this command.
- `dual-breadth-trend-oos [--window-years Y] [--slope-lookbacks ...] [--thresholds ...]`
  — a new out-of-sample check, modeled on `dual-trend-oos`/`breadth-trend-oos`.

`loop/engine.py` is a real, normally-importable file (AGENTS.md item 7); the
edit was made there directly and folded back into `evotrader_bundle.py`'s
embedded `_SRC` with `tools/edit_bundle_module.py sync`, verified clean with
`sync --check` and `verify` immediately after. `loop/engine.py` is not in
`constitution`'s `_PROTECTED` list, so `evotrader.manifest`'s checksum is
unaffected — confirmed unchanged (`726dfa4bac85891a`) before and after.

## Methodology: learning from this item's own mistakes

Both `dual-trend` and `breadth-trend` originally reported an apparent
in-sample "sweet spot" parameter value from a sweep against the live
champion's own 4 fold/holdout windows, and in both cases a follow-up
`-oos` session found that sweet spot did **not** survive contact with
calendar windows it was never tuned on (`dual-trend-oos`,
`breadth-trend-oos`) — the genuine out-of-sample-best values turned out to
be different from, sometimes the opposite of, what the in-sample table
pointed to. Rather than repeat that mistake with a fresh 2D grid mined
against this new combination's own 4-window output, this session tested
the combination directly, immediately, on each ingredient's own
already-individually-oos-validated values: `slope_lookback` ∈ {10, 20}
(the region `dual-trend-oos` found held up, not the in-sample 40-50 "sweet
spot" it debunked) crossed with `breadth_threshold` ∈ {0.5, 0.7} (the
values `breadth-trend-oos` found held up, not 0.2-0.4). Four cells, no
mining.

(A quick in-sample run against the live 4-window table was also done first,
for context and to sanity-check the mechanics worked — at its own default
parameters, `slope_lookback=20, breadth_threshold=0.4`, it looked
dramatically better than every sibling in 3 of 4 windows. That table is
*not* reported as a finding here, deliberately — it is exactly the kind of
in-sample read this item's own history has twice already shown not to be
trustworthy on its own.)

## Results

**1.1333y independent tiling** (the champion's own per-fold window width;
9 tiles walking backward from today over the full ~2017-2026 history, 2
genuinely bearish: window 2, 2017-10-13 to 2018-12-01, buy&hold −47.9%;
window 6, 2022-04-26 to 2023-06-14, buy&hold −51.6%, the LUNA/FTX era):

| variant | mean return (8 windows) |
|---|---|
| trend-break (no filter) | −10.3% |
| breadth-alone, th=0.5 | −9.5% |
| breadth-alone, th=0.7 | −9.8% |
| **dual-breadth, lb=20, th=0.5** | **+2.1%** |
| dual-breadth, lb=10, th=0.5 | −3.1% |
| dual-breadth, lb=20, th=0.7 | −5.5% |
| dual-breadth, lb=10, th=0.7 | −11.0% |

`lb=20, th=0.5` is the first positive mean-return number anywhere in this
item's whole `-oos` history (every prior best — `regime-combo-oos`,
`dual-trend-oos`, `breadth-trend-oos` — topped out negative).

**2.0y independent tiling** (5 tiles, all bull — the same "no 2-year
stretch in this universe's history nets bearish" finding every prior
`-oos` check has made):

| variant | mean return (5 windows) |
|---|---|
| trend-break | −4.8% |
| breadth-alone, th=0.5 | +0.4% |
| **breadth-alone, th=0.7** | **+4.9%** |
| dual-breadth, lb=10, th=0.5 | +2.4% |
| dual-breadth, lb=20, th=0.5 | +0.9% |
| dual-breadth, lb=10, th=0.7 | −8.5% |
| dual-breadth, lb=20, th=0.7 | −10.7% |

Here breadth-alone at 0.7 wins outright, and `lb=20, th=0.5` — the
1.1333y tiling's best cell — is only middling. **No single
(slope_lookback, breadth_threshold) cell dominates both tilings.** Same
non-dominance pattern this item's history has repeatedly found between
every pair of variants tried so far (regime vs. trend-break, combined vs.
asymmetric, dual-trend vs. breadth-trend).

One sub-finding is consistent across *both* tilings, and reads as more
trustworthy than any single cell's headline number, because it's a
direction rather than a point estimate: adding the slope filter on top of
`breadth_threshold=0.5` helped or was roughly neutral in all four
cross-tiling comparisons checked; adding it on top of
`breadth_threshold=0.7` hurt in all four. Whatever is happening
mechanically, the slope filter and a 0.5 breadth bar seem to compose, and
the slope filter and a 0.7 breadth bar seem to fight.

The crash window still doesn't pay. Even `lb=20, th=0.5` — the best cell
found anywhere in this session — loses money in window 6 (−23.9%), the
smallest loss recorded in this session's own table for that window but
still a loss, not a profit. This extends rather than breaks the standing
finding tracked throughout item 5's history: no signal tried so far
(regime, trend-break, dual-trend, breadth-trend, or any combination) has
ever actually profited in a real severe crash — only reduced the loss
elsewhere.

## What this does and doesn't decide

Does not change the still-open, still owner-gated question of whether to
let the Researcher open a short at all (AGENTS.md item 5's standing
framing). It does add the first positive out-of-sample mean-return result
in this item's multi-month research trail, which is worth flagging
precisely for what it is: real, but narrow (one tiling, one cell, small
sample — 8-9 independent windows is not a lot of statistical power), and
not yet a case for building anything live. The consistent
slope-filter-composes-with-0.5 direction is the part of this result most
likely to still be true on data neither tiling has seen.

## Verification

- `python3 -m pytest -q`: 484/484 baseline before any edit; 493/493 after
  (9 new tests, `tests/test_dual_breadth_trend_short.py`).
- `tools/edit_bundle_module.py sync --check` clean before commit (no
  drift between `loop/engine.py` and the bundle's embedded copy).
- `tools/edit_bundle_module.py verify`: round-trip clean.
- `python3 -c "import constitution; print(constitution.checksum())"` ==
  `726dfa4bac85891a`, unchanged (`loop/engine.py` is not `_PROTECTED`).
- `live_state.json`: untouched throughout — this was all read-only
  diagnostic work (new benchmark function, new CLI flags/command, new
  tests), no genome mutation, no council, no trading.
- No dashboard rebuild this session: nothing in `live_state.json` changed,
  so `index.html` would be byte-identical to its current committed state.

## Next

If item 5 is picked up again: the slope-filter-composes-with-0.5 direction
is the one piece of this session's result worth trying to explain
mechanically (why would a stricter temporal filter help *more* at a looser
breadth bar and hurt at a stricter one?) rather than just re-measuring.
Beyond that, this item's multi-month pattern holds — every new
confirmation dimension or combination tried reduces average losses in some
slice of history without ever producing a signal that profits in the one
real severe crash this universe's history contains. A genuinely different
kind of signal (not another temporal/cross-sectional combination of the
same two price-only primitives) is probably needed before that changes,
not another combination of what's already been tried.
