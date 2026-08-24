# 2026-08-24 03:52 UTC — `tick-dry-run` non-skip branch gets automated coverage

## Context

3-hourly self-improvement check. Today's daily bar (2026-08-24) was already
processed by the 00:20 UTC run before this session started (`live_state.json`
`updated: 2026-08-24T00:22:01+00:00`, and `runs/2026-08-24-0020-daily-trading.md`
exists) — no tick run this session, no double-trade risk.

Picked up AGENTS.md item 7 (`run_from_files.py` / the unflatten cutover).
Its most recent entries (2026-08-23 18:45 UTC onward) all flagged the same
open gap: `tick-dry-run`'s non-skip branch — the code path that actually
builds and prints a real would-be order list, as opposed to the "already
traded, nothing to do" skip path — had never been exercised, automated or
manual, because doing so against real data requires a session to start in
the narrow window after a new bar closes and before the 00:20 UTC daily run
claims it. No session had landed in that window yet, and there was no way
to force it deterministically. Rather than keep waiting for a lucky timing
window, this session built a fully synthetic scratch universe so both
branches can be exercised on demand.

## What shipped

`tests/test_run_from_files_matches_bundle.py`: two new tests plus a shared
`synthetic_universe` fixture.

- The fixture writes `state/cache/ZZTESTAUSDT_1d.pkl` and
  `state/cache/ZZTESTBUSDT_1d.pkl` — 600 bars of synthetic OHLCV data (fixed
  RNG seed, geometric-random-walk closes) for two symbols named to be
  obviously fake and never collide with a real Binance pair. The 600-bar
  span comfortably covers `LiveAccount.tick()`'s 1.5-year `load_universe`
  window, and the last bar is dated to today, so neither of
  `core.market.load()`'s two fetch branches ("need older history", "need
  newer bars") ever fires — the part of `tick()` that matters runs with zero
  network dependency. (`live_prices()`'s separate ticker-price fetch can
  still attempt the network, but it's wrapped in a broad try/except that
  falls back to the synthetic closes regardless of whether that call
  succeeds, so it doesn't affect determinism.)
- The fixture also builds a scratch genome: the real seed genome
  (`core.genome.SEED_GENOME`, already resolved via the bundle's meta-path
  finder that `tests/conftest.py` installs for the whole test session) with
  `universe` and `analyst.regime_anchor` swapped to the two fake symbols.
- `test_tick_dry_run_computes_real_decision_for_untraded_bar`: scratch
  `live_state.json` with an empty `journal`, run via `EVO_STATE` env
  override (never the real file). Empty journal means `tick()`'s
  idempotency check has nothing to match, so the non-skip branch is
  guaranteed. Asserts the "a real decision was computed for an UNTRADED
  bar" banner appears, the bar/tick numbers are right, the scratch state
  file is byte-identical before and after (proving `acct.save()` really
  isn't called), and the real `live_state.json` never moves.
- `test_tick_dry_run_skips_already_traded_bar`: same fixture, but the
  scratch journal is pre-seeded with an entry for the exact bar `tick()`
  will compute (`idx[-2]`, the last closed bar), forcing the skip branch.
  Same safety assertions.
- Cache files are removed in the fixture's `finally` block after every test,
  regardless of outcome.
- Updated the module docstring: it used to say `tick-dry-run` was
  manual-verification-only for the same network-dependency reason as
  `regime`/`fold-dd-blindspot`; that was true for the skip path but the
  non-skip path had no verification at all (automated or manual) until now.

## Verification

- `python3 -m pytest tests/test_run_from_files_matches_bundle.py -v` — 6/6
  passed (was 4/4 before this session).
- `python3 -m pytest -q` — full suite 225 passed (was 223; +2 new, 0 broken).
- `ls state/cache` empty after the run — fixture cleanup confirmed, no
  leftover synthetic files.
- `git status --porcelain` before committing shows only the test file and
  `AGENTS.md` changed — no accidental cache files staged (gitignored anyway,
  but confirmed).
- `md5sum live_state.json` unchanged across the whole session; `git diff`
  never touches it.
- `python3 tools/edit_bundle_module.py sync --check` — "bundle already
  matches real files, no changes" (run_from_files.py and core/ weren't
  touched this session, only the test file).
- `python3 -m py_compile run_from_files.py tests/test_run_from_files_matches_bundle.py`
  — clean.
- `python3 evotrader_bundle.py summary` — runs clean, confirming the real
  bundle path is unaffected.
- `review-hard-calls` — checked, 0 pending.
- No genome promotion this session — no README `## Status` change needed.

## What this does and doesn't close

Closes: "the non-skip branch has zero test coverage" — it now has
deterministic, network-independent, on-demand coverage for both branches.

Does NOT close: verifying `tick-dry-run` against a genuinely untraded bar
in the *real* universe with *real* market data. That's a different check
(catches anything specific to the real genome/universe/data shape that a
synthetic 2-symbol universe can't) and still requires a session to land in
the narrow post-close-pre-00:20-UTC window, same as every prior entry on
this item said. Whoever next lands in that window should still run
`tick-dry-run` first as originally suggested — this session's work makes
that a second, complementary check rather than the only one.

The actual item-7 cutover — `tick`/`evolve` saving against the real files,
and the decision to ever point a scheduled run at `run_from_files.py`
instead of the bundle — remains untouched, separate, and riskier.
