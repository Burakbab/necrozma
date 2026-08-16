# Correlation-penalty grid was exhausted against v2 — widened it — 2026-08-16 ~07:16 UTC

Scheduled 3-hourly check. Today's daily bar was already handled by the 00:20
UTC daily run (`live_state.json` `updated` at `2026-08-16T06:20:56Z`, tick 3,
no halt) — nothing to trade this cycle. Also cleaned up a stale local
repo checkout: this container's `main` had diverged from `origin/main` on
totally unrelated pre-history (`fa43c4b`/`a4f81e0`, not this project's real
lineage). No uncommitted work was on it, so `git reset --hard origin/main`
per the run protocol's authoritative-remote rule.

## What this cycle found

Continued the open item from Next-steps 3: "needs more generations, or a run
where the champion actually gets beaten first" for the `correlation_penalty`
range search. Ran a 10-generation shadow `evolve` against a scratch copy of
the real live champion v2 (real 27-symbol data, real gates, real
`researcher_memory` — 252 candidates already tried going in). **No
`correlation_penalty` candidate appeared in any of the 10 generations.**

Traced why: `Researcher.structural()` proposes `correlation_penalty` at
`0.25`/`0.5`/`0.75` only while the gene is cold (`<= 0.0`), and proposals are
excluded by exact patch value once tried against a given champion version
(`researcher_memory.tested`). All three values were tried and rejected
against v2 in earlier runs (2026-08-16 00:59 and 04:03 sessions) — so the
correlation branch has been silently exhausted since then. It will not fire
again for champion v2 no matter how many more generations run, and this
would keep being invisible (14 blind-search proposals per generation looks
identical whether or not structural proposals are also firing) until someone
checked the exclusion set directly. Confirmed against the real repo's
`live_state.json`, not just the scratch copy — all three values are excluded
there too, so this affects any future evolve (shadow or live) against the
current champion.

## Change

Widened `Researcher.structural()`'s cold-start `correlation_penalty` grid
from `(0.25, 0.5, 0.75)` to `(0.1, 0.25, 0.5, 0.75, 0.9)`, so there are fresh,
untested values for the next evolve (shadow or live) to draw from. Edited via
the same `repr()` round-trip splice as the previous researcher edit (no
`bundle.py` build script in this clone). Verified:

- `py_compile` clean
- `evotrader_bundle.py summary` against the real `live_state.json` byte-identical
  before/after (`git stash` diff)
- Direct import of `agents.researcher`: `structural()` now yields 5 distinct
  `correlation_penalty_*` mutations; checked against the real
  `researcher_memory.tested` set — `0.25`/`0.5`/`0.75` are already excluded,
  `0.1`/`0.9` are fresh
- A 2-generation shadow `evolve` (separate scratch copy, real data/gates)
  confirms both new values actually get proposed and evaluated:
  `correlation_penalty_0.1` scored fold-aggregate fitness **0.7021** (above
  the champion's raw 0.682, but short of the required margin of 0.318 over
  252+ cumulative candidates — rejected, correctly), `correlation_penalty_0.9`
  scored 0.3174 (well below). `0.1` is the highest fold-aggregate score any
  correlation_penalty value has recorded across all runs so far (prior best
  was `0.75` at 0.5912 in the 2026-08-16 00:59 session) — one draw, not
  conclusive, but the first hint that a smaller penalty might be closer to
  useful than the values tried up front.

**Nothing here touched the real `live_state.json`** — this is a code change
to the Researcher's proposal generator (committed) plus two scratch-only
shadow runs for verification (scratch state and cache deleted after).

## Next

Still not resolved which `correlation_penalty` magnitude generalizes — `0.1`
is now the most promising untested-until-today value but hasn't cleared the
holdout gate. Whoever continues this: check `researcher_memory.tested`
directly before assuming a widened grid means "will get retested" — proposals
are excluded by exact value, permanently, until the champion changes version.
If this grid also gets exhausted with no promotion, the next honest move is
either accepting `correlation_penalty` doesn't help at any single fixed value
tried so far, or building the fuller cross-universe factor-model version
flagged as a bigger separate step in Next-steps item 3.
