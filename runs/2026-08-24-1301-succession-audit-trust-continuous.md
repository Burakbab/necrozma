# `succession-audit`'s two-sided drawdown comparison — 2026-08-24 ~12:47-13:01 UTC

Scheduled 3-hourly check. Today's daily bar was already handled by the 00:20
UTC run (`live_state.json` `updated` 2026-08-24T00:22:01+00:00, genome
version still 3, md5 `0b628cf88674a6de938b4a806f33cf70` unchanged throughout
this session) — nothing new to trade this cycle. `review-hard-calls` still 0
pending.

## Context

The 2026-08-22 `succession-audit-diagnostic` run (see that run's own note and
AGENTS.md item 2) found that champion v2's fold-merged max_dd (-40.1%)
*overstates* its true continuous max_dd (-38.1%), the opposite direction from
the original `fold-dd-blindspot` bug. `dd_corrected_stats()` — the function
`accepts()` actually gates real promotions on — takes
`min(fold-merged, continuous)`, which can only ever tighten the gate: correct
for the original blind spot (fold-merged *understating* true risk) but blind
to this one, since `min()` has no way to recover a truer, better continuous
number from an overstated fold-local one. That run's "Next" section flagged
this explicitly as one of two open directions, neither attempted at the time.

## What was built

New `loop.evolve.dd_trust_continuous_stats(evaluator, g, stats, folds=None)`:
a diagnostic-only sibling of `dd_corrected_stats()` that always replaces
`max_dd` with `evaluator.continuous_max_dd()`'s number outright (when
available) instead of taking the worse of the two. This is a genuine
loosening in the overstatement case — deliberately not wired into
`accepts()` or `EvolutionRun.generation()`, and won't be without a separate,
explicit decision to change the live gate's policy. It exists purely so a
read-only report can show what the gate's verdict would look like under a
two-sided correction, alongside the current one-sided one.

`succession-audit` (the CLI diagnostic built 2026-08-22 for exactly this
kind of cross-champion comparison) now prints a `trust-cont fit` column next
to the existing `dd-corr fit` one, computed the same way (via
`constitution.fitness()` on the corrected stats). Four new tests in
`tests/test_continuous_max_dd.py` mirror the existing `dd_corrected_stats`
test suite: replaces a worse fold-local number (the v2 case), also replaces
a better fold-local number (the original blind-spot direction, same outcome
as `dd_corrected_stats` there), falls back to the original on a backtest
error, and preserves unrelated stat fields.

New function lives in the real, unflattened `loop/evolve.py` (item 7's
package tree) — `tools/edit_bundle_module.py sync` propagated it into the
bundle's `_SRC['loop.evolve']` entry so `evotrader_bundle.py`'s own runtime
(what every scheduled command actually executes) picks it up too. The CLI
column addition itself is a plain-script edit to `evotrader_bundle.py`'s
`succession-audit` command body, not a `_SRC[...]` line.

## Verified safe

- Full suite: 235 passed (was 231; +4 new, 0 broken).
- `tools/edit_bundle_module.py sync --check`: clean (bundle already matched
  the real files after `sync` was run).
- `tools/edit_bundle_module.py verify`: round-trip clean, bundle byte-for-byte
  unchanged after extract/reinsert of every module.
- `py_compile` clean on `evotrader_bundle.py`, `loop/evolve.py`, and the
  edited test file.
- `live_state.json` md5 (`0b628cf88674a6de938b4a806f33cf70`) unchanged across
  every command run this session: `succession-audit` (twice — once before
  the header-width fix below, once after), `summary`, `review-hard-calls`.
- `evotrader_bundle.py summary` and `review-hard-calls` both still run clean
  (0 hard-call reviews pending).
- Manually ran `succession-audit` against real data (27 symbols, 3 known
  champions). Caught and fixed a cosmetic bug on the first run: the new
  column's header ran into the previous one with no separating space
  (`dd-corr fittrust-cont fit`) because the fixed-width columns were sized
  to their header text with no padding margin — fixed by widening both
  columns by a couple of characters. Data rows were never affected (numeric
  values are shorter than the header text), only the header line.
- Today's real numbers differ from the 2026-08-22 diagnostic's (data window
  has moved 2 days): v2's `dd-corr fit` and `trust-cont fit` happen to
  coincide today (`0.114` both) rather than diverge, because the underlying
  fold-merged and continuous max_dd numbers are themselves date-dependent
  snapshots, not fixed properties of a genome. Not a contradiction of the
  2026-08-22 finding, just confirms these tables are re-derived fresh each
  run rather than cached facts.

## Not decided

This does not change `accepts()`'s actual policy, and offers no opinion on
whether the gate should ever really use a two-sided correction — that
remains a real design decision, tied to the still-open v3 demotion/rollback
question (AGENTS.md item 2), which stays explicitly the owner's call,
unchanged by this session. What this closes is narrower: the 2026-08-22
entry's "build the missing case" loose end now exists as a ready-made
comparison column, so whoever next opens that design pass doesn't have to
build the two-sided arithmetic from scratch — they can just run
`succession-audit` and read both columns off the same table.

No push notification sent — read-only diagnostic tooling, zero effect on
live trading behavior, and the standing v3 demotion/rollback question itself
is unchanged (already raised to the owner 2026-08-22, reaffirmed 2026-08-23
and 2026-08-24, no new facts here that change that status).
