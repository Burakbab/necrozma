# Drawdown episode diagnostic — 2026-08-18 (3-hourly self-improvement check)

## Context

Today's daily bar was already handled by the 00:20 UTC run
(`runs/2026-08-18-0020-daily-trading.md`); `live_state.json`'s `updated`
timestamp matched, so this cycle did not call `tick`.

AGENTS.md's "Next steps" / "Current state" carried an open item since the
2026-08-16 costs/holdout diagnostic: the full-history replay's baseline
maxDD (-34.1%) is thinner against the 40% hard-fail gate than the return
numbers alone suggest, and "a worthwhile follow-up is finding which
sub-period of the full 4 years drives that -34.1% baseline maxDD
(bear-market segment? one specific crash bar?)". Nothing had isolated it —
`costs`/`costs --holdout` bracket the two ends (full history vs. sealed
holdout) but neither points at a date range.

The fold-scheme cross-champion sweep (item 2 in "Next steps") is closed
until a fourth champion is promoted, and no live tick has ever flagged a
hard call yet (`review-hard-calls` reports 0 pending), so item 4's "first
real review" isn't actionable this cycle either. This was the best-scoped,
already-flagged item available.

## What shipped

New pure function `loop.engine.drawdown_episodes(nav_history, top_n=5)`:
walks a `(timestamp, nav)` series (already returned by `run_backtest` as
`nav_history` — nothing new computed) into peak-to-trough-to-recovery
episodes, tracking a running peak and its own trough, closing an episode
either when nav recovers back to a new peak or at the end of the series
(recovery_ts=None). Returns episodes sorted deepest-first.

New CLI command `evotrader_bundle.py drawdown [--holdout]`, wired the same
way as `costs`/`regime`: real champion, real universe, real broker,
never touches `live_state.json`. Runs `run_backtest` (full history or the
sealed `HOLDOUT_FRAC` slice), calls `drawdown_episodes` on the result's
`nav_history`, and tags each episode's peak with the walk-forward fold (or
`holdout`) it falls in, using the same fraction-based split `regime`
already reports against.

## Verification

- `tests/test_drawdown.py`, 7 new tests: empty/too-short series, monotonic
  rise has zero episodes, single episode's peak/trough/recovery/depth,
  unrecovered episode at series end, `top_n` sorts deepest-first and
  limits, and — the one that matters most — the deepest episode's `dd_pct`
  reproduces `PaperBroker.stats()`'s own `max_dd` (`min(nav / running_peak
  - 1)`) to within `1e-9` on a seeded random-walk series, not just on hand
  toy data. Full suite: 85 passed, up from 78.
- Ran `drawdown` for real against champion v3 and cross-checked the CLI's
  own printed "reported max_dd (stats)" vs. "deepest episode reproduces
  it" — both full-history and `--holdout` runs printed `match`.
- `git status` clean before commit except the intended files;
  `live_state.json` untouched (not in `git status`, `md5sum` unchanged
  across the whole session); `constitution verified dfae6a697f51fb49`
  unchanged throughout (`loop.engine` is not in the checksummed set, same
  as every prior diagnostic).
- Editing `evotrader_bundle.py`'s embedded `_SRC['loop.engine']` string
  (the flattened-bundle risk AGENTS.md item 7 flags — the 2026-08-15
  migration once corrupted whitespace this way) was done programmatically:
  extracted the string via `ast.literal_eval` on the assignment node,
  edited the resulting real `.py` source with normal tools, verified it
  with `py_compile`, then re-embedded via `repr()` on the edited source and
  confirmed `repr(original_source) == original_literal_text` beforehand so
  the round-trip format was proven exact before trusting it on the edited
  version. `git diff --stat` after showed exactly one line changed in
  `evotrader_bundle.py` for that step (the single-line `_SRC` assignment),
  no stray whitespace elsewhere.
- One bug caught before commit: the first draft of the fold-tagging logic
  computed each episode's window from full-history fraction math
  regardless of `--holdout`, so a `--holdout` run (all bars already inside
  the sealed slice) printed misleading `fold 1`/`fold 2` labels instead of
  `holdout` for every row. Fixed: `_window_for` now short-circuits to
  `"holdout"` whenever `use_holdout` is set, re-verified against a real
  `--holdout` run.

## Result — champion v3, full history

```
  reported max_dd (stats): -34.1%
  deepest episode reproduces it: -34.1% (match)

     depth  peak date    trough date   bars  recovery     window
   -34.1%  2024-03-31   2024-08-05     127  2024-11-10   fold 2
   -29.2%  2025-11-08   2026-08-14     279  not recovered fold 3
   -27.4%  2023-02-20   2023-09-11     203  2023-11-06   fold 1
   -26.6%  2024-12-08   2025-04-18     131  2025-07-17   fold 2
   -20.9%  2022-11-04   2023-01-01      58  2023-01-13   fold 1
```

The -34.1% baseline maxDD flagged in the 2026-08-16 costs diagnostic is
**one 127-bar episode**, not a spread of several mid-sized ones: 2024-03-31
to 2024-08-05, recovered by 2024-11-10, sitting inside fold 2 — the same
fold every prior `regime`/`fold-scheme` diagnostic has already identified
as a +200%+ melt-up outlier (see `runs/2026-08-17-0956-regime-diagnostic-fold-holdout.md`
and the `fold-scheme` entries in "Current state"). Read together, this
isn't a new independent finding — it's the missing "when and how much" for
something those diagnostics had only characterised in aggregate: a sharp
pullback inside a violently up fold is exactly the shape you'd expect, not
a separate bear-market segment or one specific crash bar as originally
guessed.

## Result — champion v3, sealed holdout only

```
  reported max_dd (stats): -26.6%
  deepest episode reproduces it: -26.6% (match)

     depth  peak date    trough date   bars  recovery     window
   -26.6%  2026-05-08   2026-08-18     102  not recovered holdout
   -14.2%  2026-01-13   2026-04-19      96  2026-05-05   holdout
    -1.7%  2026-05-06   2026-05-07       1  2026-05-08   holdout
    -0.4%  2026-01-11   2026-01-12       1  2026-01-13   holdout
```

Worth noting: the full-history run's second-deepest episode (-29.2%,
2025-11-08 to today, still unrecovered, tagged fold 3) and the holdout
run's deepest episode (-26.6%, 2026-05-08 to today, also still unrecovered)
are the same real ongoing drawdown viewed through two different replay
windows, not two separate findings — the current live drawdown is its own
still-open episode, not an echo of fold 2's 2024 pullback.

## Next

Diagnostic-only, no code path acts on this yet. If the
regime-stratified/rolling fold-scheme redesign discussed throughout the
existing `fold-scheme` entries is ever attempted, `drawdown --holdout` is
now a one-line way to check whether a redesigned holdout window still
contains the same still-open drawdown episode or lands on a cleaner one.
