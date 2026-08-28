# `holdout-margin-audit` — the real lineage shows the same raw-beat pattern

2026-08-28, ~18:46–19:03 UTC (3-hourly check)

## Why

The 16:32 UTC entry today (guardian-weighted shadow evolve, 25 generations,
361 candidates) found that 16 of 69 holdout-tested candidates (23%) beat
champion v3's own sealed-holdout score in raw terms and were still rejected,
because `holdout_accepts()` requires beating champion **+ margin**, not just
beating champion. Its own "Next" flagged this as a real design tension in
`required_margin()`/`holdout_accepts()` — an unusually lucky champion holdout
draw can entrench indefinitely — but explicitly said the fix (re-drawing the
champion baseline, or an absolute/percentile bar) is a constitution
amendment that "deserves scrutiny from a full session, not a 3-hourly one."

That amendment is still out of scope for this session. What isn't out of
scope: checking whether the same pattern already shows up in the *real*
lineage, using data `live_state.json` already has recorded, no new search
required — the same move `holdout-pressure` made on 2026-08-18 to confirm
the 4h-shadow entrenchment hypothesis with real 1d data.

## What

New pure function `loop.evolve.raw_holdout_beats(holdout_draws)`, built on
top of the existing `summarize_holdout_pressure()` (unchanged). For a list
of recorded holdout-rejection draws (already parsed from real
`holdout_accepts()` rejection strings in `acct.lineage`), it flags which
ones had `holdout_challenger > holdout_champion` — i.e. the challenger beat
the champion's raw score and lost only to the additive margin — and marks
the first such flip per champion reign (later flips in the same reign
aren't independent counterfactuals, since a real promotion at the first
flip would have replaced the champion and changed everything downstream).

New CLI command `holdout-margin-audit`, in both `evotrader_bundle.py` (the
live path) and `run_from_files.py` (mirrored verbatim, per that file's
existing transcription discipline). Reads `acct.lineage` only — no market
data, no backtest, never touches `live_state.json`, same guarantee as
`holdout-pressure`. Iterates every champion version found in lineage, not
just the live one.

Tests: 4 new unit tests in `tests/test_holdout_pressure.py` (empty input,
a real raw-beat-but-rejected case built from the actual `holdout_accepts()`
output, a no-beat case, and a multi-draw case verifying `first_flip_index`
doesn't get pulled forward by a later, larger raw beat). 1 new parametrize
case in `tests/test_run_from_files_matches_bundle.py` proving
`run_from_files.py holdout-margin-audit` and `evotrader_bundle.py
holdout-margin-audit` produce byte-identical stdout against the same real
`live_state.json`. Full suite: 240 passed (was 239 before this session).

## Result

Ran the new command against the real account. v1 and v2 both show 0
recorded sealed-holdout draws (nothing ever reached that gate during their
reigns). v3 shows 20 draws, and **3 of them beat the champion's raw holdout
score of 0.763 outright**:

| cumulative draw | challenger holdout | champion holdout | margin needed |
|---|---|---|---|
| 15 | 1.636 | 0.763 | 4.655 |
| 19 | 1.497 | 0.763 | 4.853 |
| 21 | 1.613 | 0.763 | 4.935 |

The first (cumulative draw 15) is the only valid single-flip counterfactual:
it needed +4.655 margin and missed by nothing on sign, purely on magnitude.

This is a second, independent confirmation of the same tension the 16:32
UTC shadow-evolve session found — smaller sample (3 of 20 vs. 16 of 69, both
in the same ballpark ~15-23%), real data instead of a fresh search, and it
cost a few minutes of reading already-recorded lineage instead of 38 minutes
of `evolve()`.

## Verified safe

- `md5sum live_state.json evotrader.manifest` unchanged throughout:
  `0fa0731311baab0508f959f79a01214e` / `0bf3a7d9411ee692d0a9f152a7533803`.
- `tools/edit_bundle_module.py sync --check` and `verify` both clean before
  and after — the bundle and real files stayed byte-identical.
- Full test suite green (240 passed), including the new byte-identical
  cross-check between `run_from_files.py` and `evotrader_bundle.py`.
- Today's bar (00:20 UTC) was already processed before this session
  started; no `tick` run, no double-trade.
- Local `main` was detached from `origin/main` again at session start (same
  history-rewrite artifact AGENTS.md's own run protocol names) — realigned
  with `git checkout -B main origin/main`, no force-push, nothing lost.

## Next

Same open item as the 16:32 UTC entry: whether to (a) periodically refresh
the champion's own holdout baseline instead of anchoring to one historical
draw, or (b) move to an absolute/percentile holdout bar. Both are
constitution amendments and still deserve a full session, not a 3-hourly
one — not attempted here. This audit is cheap enough (`acct.lineage` read
only) to re-run after every future non-promoting `evolve` call, same as
`holdout-pressure`, to keep tracking whether the raw-beat rate on the real
account holds around this ~15-23% band or moves.
