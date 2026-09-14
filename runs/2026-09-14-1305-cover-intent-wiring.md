# Cover-intent wiring — 2026-09-14 ~12:48-13:05 UTC (3-hourly check)

## Session start

Repo started in detached HEAD, up to date with `origin/main` after
`git checkout main && git pull origin main` (fast-forward, no divergence).
`pip3 install -r requirements.txt -q`. Checked `live_state.json`'s `updated`
(`2026-09-14T07:18:04+00:00`, from the ~06:47-07:21 UTC evolve batch) against
`runs/2026-09-14-0900-daily-discussion.md`: tick 31's daily bar was already
handled at 00:20 UTC, so no `tick` run this cycle.

## What this session did

Picked up AGENTS.md item 5 Phase 2's concretely-scoped next step (repeated
across the last several sessions' "Current state" entries): design and add
the "cover" intent shape so a consult can propose closing an open short,
then thread it through `RiskJudge.rule`'s exits-first loop.

**1. Consults** (`agents/consults.py`): each of the three consults' long-only
exit checks (`held = is_long(...)`) now has a mirrored branch for an open
short, reusing the same genes symmetrically instead of adding new ones:

- `RiskyConsult`: long exit `rsi > exit_rsi(88) or trend < exit_trend_below(-0.03)`
  mirrors to short exit `rsi < 100-exit_rsi or trend > -exit_trend_below`.
- `ConservativeConsult`: long exit `rsi > exit_rsi(68)` mirrors to
  `rsi < 100-exit_rsi`.
- `ModerateConsult`: long exit `trend < exit_trend_below(0.0) or rsi > exit_rsi(80)`
  mirrors to `trend > -exit_trend_below or rsi < 100-exit_rsi`.

Each mirrored branch emits `side="cover"` instead of `side="sell"`.

**2. `RiskJudge.rule`** (`agents/judges.py`): the exits-first loop used to
bucket every non-"buy" intent into a single `sells` dict and gate it on
`b.open_positions.get(sym, 0.0) <= 0` (i.e. `is_long`). A "cover" intent
landing there would have been silently gated out, since a short's weight is
never positive. Split into `sells`/`covers` dicts (factored the shared
scoring logic into a small `_exit()` closure), gated on `is_long`/`is_short`
respectively, emitting `Order(side="sell")`/`Order(side="cover")`. The
same-bar "exit takes precedence over a new buy" check now recognizes both
exit sides.

**3. `SuperiorJudge.review`** (`agents/judges.py`) — **a real landmine found
while wiring this up, not anticipated going in**: "exits are never blocked,
ever" was implemented as `sells = [o for o in v.orders if o.side == "sell"]`
then `kept.extend(sells)`. A "cover" order coming out of `RiskJudge.rule`
satisfies neither that filter nor the `buys` one, so it would have been
silently dropped from the returned `Verdict.orders` entirely — not vetoed,
just gone, the same class of bug as the two sign landmines found earlier
this week in different files. Fixed: `exits = [o for o in v.orders if
o.side in ("sell", "cover")]`.

**Tests**: new `tests/test_cover_intent_wiring.py` (9 tests) covers all
three pieces, including a dedicated regression test for the
`SuperiorJudge.review` landmine (asserts a "cover" order survives `review()`
instead of vanishing — confirmed it fails against the pre-fix code by
checking out the pre-fix `agents/judges.py` and re-running). Updated
`tests/test_short_position_sign_landmine.py`'s
`test_consult_exit_check_still_treats_an_open_short_as_flat_pending_phase2`
(renamed `..._now_proposes_covering_an_open_short`) to test the new fixed
behavior instead of documenting the now-closed gap.

**No behavior change for any existing (long-only) live caller**: `.short()`
still has zero callers in the live trading/evolution path, so
`b.open_positions` is never actually negative in production and every new
`is_short`/"cover" branch is unreachable there today — same invariant every
prior slice of this item preserved. `live_state.json` untouched (md5
identical before/after). Neither `core/portfolio.py` nor
`constitution/__init__.py` (the two checksummed files) touched — constitution
verified `726dfa4bac85891a` unchanged.

Edited the real files directly, then `python3 tools/edit_bundle_module.py
sync` to regenerate `evotrader_bundle.py`'s embedded `_SRC` (confirmed via
`sync --check` clean and `verify` round-tripping unchanged) — tests import
via the bundle's meta-path finder (`tests/conftest.py`), not the real files
directly, so this step is what actually made the new tests exercise the
edited code.

`python3 -m pytest -q`: 415/415 (406 baseline + 9 new). No dashboard
rebuild needed (no state change). Genome still v3 (1d) live, untouched.

## Still open (Phase 2)

Discretionary "cover" intents now exist and route correctly through both
judges, but this is still infrastructure, not a live capability: `.short()`
has zero callers, so nothing can ever open a short for a "cover" intent to
close. The next piece — whether/how a consult should be allowed to *open* a
short in the first place — remains the explicitly unscoped owner decision
AGENTS.md's "Owner decisions pending" already tracks. Also worth flagging
for whoever picks that up: `loop/engine.py`'s `consult_correlation`
diagnostic treats any non-"buy" intent side as direction `-1.0` (bearish),
which is the right sign for "sell" but arguably backwards for "cover" (a
bullish action, closing a short) — not fixed here since it's a read-only
research tool nothing else depends on and `.short()` has no live callers to
ever produce a "cover" row in a real decision log yet.
