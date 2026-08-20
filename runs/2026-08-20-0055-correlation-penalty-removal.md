# Correlation-penalty removal (item 3, closed)

2026-08-20 00:20-00:55 UTC, 3-hourly self-improvement check.

## Context

Today's daily bar (2026-08-20) was already processed by the 00:20 UTC daily
run before this check started (`live_state.json` `updated`
2026-08-20T00:21:36+00:00, journal length 6, matches `runs/2026-08-20-0020-daily-trading.md`).
No tick run this session, no double-trade.

AGENTS.md item 3's evidence base had been complete since the 2026-08-19 22:18
run: 4 real champions (v1/v2/v3, +v2-reconstruction) plus 2 independent
hand-built adversarial constructions plus one real unconstrained-search run
all agreed `correlation_penalty` is dead weight — every real champion's
held-set correlation already sits below universe-wide as a side effect of
ordinary fitness-driven selectivity, no genome has ever benefited from the
gene, and every attempt to force concentration (loosened selectivity, or
tighter position limits) blew the existing drawdown gate before
`correlation_penalty` could matter. The last several 3-hourly entries in
AGENTS.md were increasingly clear that the honest next step was to act on
this, not keep re-measuring it — the 22:18 run explicitly flagged "the
removal itself ... is a multi-file surgery that deserves a dedicated
session, not a tail-end addition to a diagnostic one." This session had a
clear 3-hour slot and no daily-tick work to do, so it took that on.

## What was removed

- `core.genome.SEED_GENOME`: the `correlation_penalty` (default `0.0`) and
  `correlation_lookback` (default `30`) genes under `risk_judge`, plus their
  explanatory comment.
- `agents.judges.RiskJudge._correlation_scale` (the method that read those
  genes and scaled/vetoed buy sizing) and its helper `_pairwise_corr`
  (Pearson correlation over two return series) — both deleted entirely.
  `rule()`'s call site (`corr_scale = self._correlation_scale(...)`, the
  `corr_scale <= 0.0` veto branch, and the `* corr_scale` term in the
  position-size formula) removed too. `import numpy as np` in
  `agents.judges` dropped since it was only used by `_pairwise_corr`.
- `agents.researcher`: both `GENE_SPACE` mutation-range entries
  (`correlation_penalty`, `correlation_lookback`) and the entire structural
  proposal block in `Researcher.structural()` that proposed
  `correlation_penalty` at `(0.1, 0.25, 0.5, 0.75, 0.9)` from cold.
- `core.types.Briefing.rets_by_symbol` (the field) and, in
  `agents.analyst.Analyst.brief`, the per-symbol per-bar computation that
  populated it (`np.diff(c) / np.maximum(c[:-1], 1e-12)`, computed for every
  symbol on every bar of every backtest and every live tick, purely to feed
  a gene that was always `0.0`). This was a real if small live cost, not
  just dead code — one array diff per symbol per bar, every tick and every
  backtest replay, for a feature nothing ever read at a nonzero penalty.

## What was deliberately kept

`loop.engine.pairwise_correlation_stats` and `holding_mask` (the
`correlation-universe` CLI diagnostic, both realized and universe-wide
modes) — these compute correlation directly from raw closes via their own
code path and never depended on `Briefing.rets_by_symbol` or
`RiskJudge._correlation_scale`. They were the tool that built the evidence
base for this removal and remain generically useful for any future
concentration/diversification question, genome-independent. Their
docstrings, and the `_adversarial_concentration_genome`/
`_adversarial_concentration_genome_tight` genome builders' docstrings and
patch lists (which used to explicitly hold `correlation_penalty` at `0.0`),
were updated to stop referencing the now-deleted mechanism as if it still
existed, and the now-meaningless `correlation_penalty: 0.0` patches were
dropped from both builders' patch lists.

## Why this is safe

The constitution package (`constitution/`, checksummed at
`dfae6a697f51fb49`) never touched `correlation_penalty` — it lived entirely
in `agents.judges`/`core.genome`/`agents.researcher`/`core.types`/
`agents.analyst`, none of which are in the checksummed set. No
`AMENDMENTS.md` row needed; `constitution verified dfae6a697f51fb49`
unchanged throughout (checked via `summary` before and after).

The live champion (v3) never used this gene — its `risk_judge` genes in
`live_state.json` don't even contain `correlation_penalty`/
`correlation_lookback` keys (never touched by v3's lineage), so
`.get(..., 0.0)` always returned the no-op default. Removing the code path
entirely should therefore be a true behavioral no-op for the live account.

Verified:
- `py_compile evotrader_bundle.py` clean throughout every edit.
- Full test suite: 104 passed (same count as before — two assertions in
  `tests/test_genome.py` that referenced the deleted gene were updated
  in place rather than deleted: `test_seed_genome_defaults` dropped its
  `correlation_penalty == 0.0` assertion, `test_child_applies_nested_dotted_path`
  now uses `max_position_pct` instead to keep testing the same
  dotted-path-patch mechanism without depending on a gene that no longer
  exists. `tests/test_universe_correlation.py`'s module docstring, which
  described the diagnostic's motivation in terms of the now-removed
  mechanism, updated to past tense.
- `live_state.json` md5 identical before/after edits
  (`cca58deb976cef403c5010f2e2b9528b`).
- `evotrader_bundle.py summary` prints `constitution verified
  dfae6a697f51fb49` both before and after.
- Constructed both adversarial genomes post-removal
  (`_adversarial_concentration_genome`/`_adversarial_concentration_genome_tight`)
  against the real live champion — both build without error, and
  `correlation_penalty` is confirmed absent from the resulting genes.
- Ran a real full-history backtest (`run_backtest`, 4-year sliding window,
  live champion v3's exact genome from `live_state.json`) after all edits:
  1159 trades, fitness 0.790, **max_dd -0.34088... — matches the
  previously-recorded -34.1% full-history maxDD for v3 to 5 significant
  figures** (small differences in trade count/fitness vs. the exact
  2026-08-19 numbers are expected and already documented elsewhere in
  AGENTS.md: `load_universe(..., 4.0)` loads a sliding 4-year window ending
  "today", so the exact window shifts by a few days between runs). This is
  strong evidence the removal changed nothing about live trading behavior.

## A note on how the edit was actually done

`evotrader_bundle.py` embeds every module's source as a single-quoted
Python string literal with `\n` as literal two-character escapes — each
`_SRC['module.name'] = '...'` line is one physically enormous line (tens of
KB), not real newlines. There is no `bundle.py` generator or per-module
source tree anywhere in this repo (the header comment "generated by
bundle.py; do not hand-edit" is aspirational — see AGENTS.md item 7, still
not done) — `evotrader_bundle.py` is the only copy of the source that
exists. Editing these lines directly with exact-string-match tools is
impractical given the escaping and line length.

Built a small two-function script instead (lived in `/tmp`, not committed,
gone with this container):
- `extract(key, path)`: find the `_SRC['key'] = '...'` line, `ast.literal_eval`
  the right-hand side back into a real string, write it to a normal `.py`
  file.
- `reinsert(key, path)`: read the edited `.py` file back, `repr()` it, and
  splice it back into that exact line in `evotrader_bundle.py`.

Round-trip verified byte-identical on an untouched extract/reinsert of
`core.types` before trusting it on the real edits (`core.genome`,
`agents.judges`, `agents.researcher`, `core.types`, `agents.analyst`,
`loop.engine`). Every extracted file was `py_compile`'d individually before
reinsertion, and the whole bundle was `py_compile`'d again after. The next
session that needs to touch bundle internals will want to rebuild the same
tool rather than hand-edit the giant lines — it's about 30 lines of Python,
not worth persisting as a repo artifact for how rarely bundle surgery like
this comes up, but worth knowing it's a solved problem rather than
reinventing string-splicing under time pressure.

## Result

Item 3 (cross-asset correlation awareness for the Risk Judge) is closed.
Full history: infrastructure shipped 2026-08-15, single-value search
2026-08-16, range search + grid exhaustion 2026-08-16, universe-wide and
portfolio-realized measurement across 3 real champions 2026-08-18/19,
2 independent adversarial constructions 2026-08-19, real unconstrained
search against the real champion 2026-08-19, removal 2026-08-20. No further
action needed unless a genuinely new structural proposal (the "fuller
cross-universe factor-model version" this item's infrastructure note always
named as the alternative to dropping) is designed from scratch — that would
be new work, not a continuation of this one.
