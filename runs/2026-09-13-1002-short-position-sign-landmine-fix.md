# 3-hourly check, 2026-09-13 ~09:47-10:20 UTC — short-position sign-landmine fix

## Trading

No new bar to process: tick 30 already handled at 00:20 UTC
(`runs/2026-09-13-0020-daily-trading.md`), and `live_state.json`'s `updated`
was `2026-09-13T07:16:05+00:00` (from the weekend all-hands' evolve batch)
before this session started. Repo was already on `main`, up to date with
`origin/main` — no divergence to resolve. No `tick` run this cycle.

## What was done

Picked up AGENTS.md item 5's own concretely-scoped next step from the
2026-09-13 weekend all-hands session: `agents/judges.py`'s five
`open_positions` read sites assumed a non-positive weight meant "flat," so
an open short (negative `position_weight()`, confirmed by the prior
session's `tests/test_short_position_sign_landmine.py`) was invisible to
position-slot limits and — worst case — silently *loosened*
`SuperiorJudge`'s hard concentration cap instead of tightening it.

Fixed the four accounting bugs, all in ordinary (non-`_PROTECTED`)
strategy-layer files:

- `RiskJudge.rule`'s entry `open_count` (was `w > 0`, now `w != 0` — a short
  occupies a slot too).
- `RiskJudge.rule`'s `held_w`-based buy-sizing headroom (`target = min(target,
  max_position_pct - held_w)` → `- abs(held_w)`, plus the two `held_w <= 0`
  slot checks around it now `held_w == 0`).
- `SuperiorJudge.review`'s `open_count` (same `w != 0` fix).
- `SuperiorJudge.review`'s hard-cap `room = (hard_cap - held) * equity` →
  `(hard_cap - abs(held)) * equity`, plus its two `held <= 0` checks now
  `held == 0`.

Added `is_long`/`is_short` helpers to `core/types.py`. `agents/consults.py`'s
three `held = b.open_positions.get(sym, 0.0) > 0` exit checks now read
`held = is_long(...)` — self-documenting, but **deliberately unchanged in
behavior**: these are long-only "sell to exit" heuristics, and closing a
short needs a distinct "cover" intent shape that doesn't exist yet (real
Phase 2 routing work, not a sign bug in these particular sites). Recorded
this explicitly in AGENTS.md so a future session doesn't assume that gap
was also closed here, and scoped the concrete next step (a cover-intent
shape, threaded through `RiskJudge.rule`'s exits-first loop) for whoever
picks it up.

`tests/test_short_position_sign_landmine.py` rewritten in place (not left
as a "documents a known bug" file): it now asserts the four fixed
RiskJudge/SuperiorJudge behaviors directly (a shorted symbol counts as an
open slot, gets no extra buy headroom vs. an equivalent flat symbol, and
the hard cap holds for it) and keeps one test (renamed) documenting the
still-open consult-exit gap as scoped, not a regression.

## A real gotcha, resolved

After editing `agents/judges.py` / `agents/consults.py` / `core/types.py`
directly and writing the two new regression tests, they failed — but only
under `pytest`, not when exercising the exact same import/call sequence via
a plain `python3 -c` script. Root cause: `tests/conftest.py` imports
`evotrader_bundle` at collection time, and that module installs a
meta-path finder that serves `agents.judges` / `agents.consults` /
`core.types` from the bundle's own embedded `_SRC` dict — the *pre-fix*
source — rather than the edited real files on disk, so the tests were
silently exercising stale logic. Running `tools/edit_bundle_module.py sync`
(the documented step after any real-file edit — I'd read this in AGENTS.md
but the failure output initially looked like the fix hadn't worked at all,
which was momentarily confusing since the numbers matched the *old* bug
almost exactly) resolved it immediately. Flagging the specific symptom
(pytest-only failure with numbers matching the pre-fix bug, passes fine via
bare `python3 -c`) in case another session hits the same shape and wants a
faster diagnosis than I had.

## Verification before commit

- `python3 -m pytest -q`: 396/396 (unchanged count — this rewrote existing
  tests rather than adding new ones) after `tools/edit_bundle_module.py
  sync`.
- `tools/edit_bundle_module.py verify` / `sync --check`: both clean.
- `evotrader_bundle.py summary`: `constitution verified 726dfa4bac85891a`
  (unchanged — none of the four touched files is `_PROTECTED`).
- `git status`: only `agents/consults.py`, `agents/judges.py`,
  `core/types.py`, `evotrader_bundle.py`, `tests/test_short_position_sign_landmine.py`,
  and `AGENTS.md` changed. `live_state.json` untouched.
- No dashboard rebuild: no state changed, only strategy-layer code.

Genome still v3 (1d) live, untouched. `.short()` still has zero callers in
the live trading/evolution path — this fix only closes the accounting gap
that Phase 2 routing would otherwise trip over the moment a short is ever
open.

## Next

Whoever picks item 5 back up next: design the cover-intent shape (a new
`Intent.side` value, or an explicit `is_short(...)` branch per consult
emitting a differently-typed exit intent), thread it through
`RiskJudge.rule`'s exits-first loop (currently only handles
`side == "sell"`), then revisit the two still-open constitution questions
(short-exposure cap, `MAX_DD_HARD_FAIL` short-specific instrument) before
routing any real "short"/"cover" order through to `PaperBroker`.
