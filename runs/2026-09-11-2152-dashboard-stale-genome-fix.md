# 3-hourly check — 2026-09-11 ~21:47-21:55 UTC — fix dashboard stale-genome-version bug

## Scope

No live trading this cycle: tick 28 already handled at 00:20 UTC
(`runs/2026-09-11-0020-daily-trading.md`), and the standing 3-hourly evolve
batch for this slot already ran ~18:47-19:14 UTC
(`runs/2026-09-11-1914-evolve-batch-v3.md`), confirmed via `live_state.json`'s
`updated` timestamp (`2026-09-11T19:14:24+00:00`) before starting. Used the
slot to fix AGENTS.md "Next steps" item 10, filed by the 20:30 UTC daily
evaluation earlier today.

## The bug

`evotrader_dashboard.py`'s `build()` computed the genome stat tile as:

```python
champ = _read(P_CHAMP, {}) or live.get("genome", {}) or {}
```

`P_CHAMP` (`state/genomes/champion.json`) is a gitignored, per-container
cache that only gets refreshed when `evolve` itself runs in that container.
Preferring it over `live_state.json` (the documented source of truth) meant
a container that ran `tick` before its first `evolve` call could publish a
stale genome version left over from an earlier point in that container's
life.

This was not just a historical 9-minute blip (the case the 20:30 UTC
evaluation found on the tick-28 commit) — the currently-committed
`index.html` (HEAD at the start of this session, from the ~19:14 UTC evolve
batch's commit) was **still showing "v1 / 5 generation(s) run"** while
`live_state.json`'s real `genome.version` was 3 the entire time. The bug was
live on the public GitHub Pages dashboard right now, not just a past
incident.

## The fix

Flipped the precedence:

```python
champ = live.get("genome") or _read(P_CHAMP, {}) or {}
```

`champ` is only ever read for its `version` field (the stat tile itself, and
`_genome_sub`'s `researcher_memory.champion_version` match), so no other
field of `champion.json` needed a fallback path — `live_state.json`'s
`genome` dict already carries `version`.

## Verification

- New regression test in `tests/test_dashboard_champion_stat.py`
  (`test_build_prefers_live_state_genome_over_stale_champion_cache`):
  monkeypatches `P_LIVE`/`P_CHAMP`/`P_LIN`/`P_BT` to scratch files, live
  state genome version 3, disk-cache champion version 1 (stale), asserts
  the rendered page shows `v3` and not `v1`.
- Full suite: `python3 -m pytest -q` → 391/391 (390 baseline + 1 new test).
- Rebuilt `index.html` with the fix in place
  (`EVO_STATE="$(pwd)/live_state.json" python3 evotrader_dashboard.py`):
  flipped the genome tile from the stale "v1 / 5 generation(s) run" to the
  correct "v3 / 4 generation(s) run · 11048 challenger idea(s) tried since,
  none better yet".
- `tools/edit_bundle_module.py verify`/`sync --check` both clean
  (`evotrader_dashboard.py` is not part of the bundle's `_SRC`, so this was
  a no-op check, not a sync requirement).
- No trading, no genome change, no constitution change — `live_state.json`
  untouched by this session except its `updated`-adjacent read-only checks.

## Next

AGENTS.md item 10 marked fixed in place, in "Next steps", with a pointer to
this note. No further action needed unless a similar staleness turns up in
`_reconstruct_champion_genome`/`Genome.champion()` (the other place item 10
flagged as "same class of staleness" — that one feeds `evolve`, not the
dashboard, and was explicitly out of scope here).
