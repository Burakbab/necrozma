# 3-hourly self-improvement check — 2026-09-05 09:58 UTC

## Session start

`git checkout main && git pull origin main` was a plain fast-forward (9
commits behind, no divergence). `pip3 install -r requirements.txt -q` (bare
container, as usual). Daily bar already handled: tick 22 at 00:20 UTC,
confirmed via `live_state.json`'s `updated` timestamp and
`runs/2026-09-05-0020-daily-trading.md` — no tick this cycle.
`review-hard-calls` reports 0 pending.

## What was picked and why

Read `AGENTS.md`'s "Owner decisions pending" and "Next steps": items 2
(4h-bar shadow evolution), 5 (short selling), and 6 (equities/FX) are all
genuinely blocked on a human decision, and item 2 explicitly says not to run
another shadow seed without one. Item 4's remaining piece is event-driven
(review the first real flagged hard call) and there is nothing pending.
Items 7/8/9 are closed or process notes, not open work.

That leaves "run more real `evolve` generations against the live champion"
as the usual default (and what the last five sessions, including this
morning's weekend all-hands, did) — but this scheduled task's own
instructions say not to let this cycle's work touch `live_state.json`
unless it's actually promoting a champion, and 45 such generations already
ran a few hours ago today with the champion holding flat at fitness 1.055.
So this cycle picked a small, real, tested, non-live-state-touching
improvement instead: the public dashboard's "genome" stat tile.

## What shipped

`evotrader_dashboard.py`'s `genome` stat tile previously only showed the
lifetime generation count ("9 generation(s) run"). It now also surfaces
`live_state.json`'s own `researcher_memory.tested` count — the number of
challenger ideas already tried against the *current* champion specifically
(924 as of this writing) — via a new pure helper, `_genome_sub(live, champ,
lineage)`. The extra clause only appears when
`researcher_memory.champion_version` matches the genome's own `version`, so
a stale count can't show up right after a promotion before
`researcher_memory` reseeds for the new champion. This is a more honest
"how hard has self-improvement search tried and failed" number for a
general audience than the raw generation count alone, and it's the exact
figure the CLI diagnostics (`holdout-pressure`, `fold-scheme`, etc.) already
treat as the per-champion multiple-testing tally — just never surfaced on
the public page before.

New `tests/test_dashboard_champion_stat.py` — the first tests
`evotrader_dashboard.py` has ever had — covers the matching-champion case,
the stale-memory-mismatch case (count omitted), a missing
`researcher_memory` key (no crash), and an empty `tested` list (suffix
omitted). Full suite: 355/355 (was 351, +4).

Rebuilt `index.html` (`EVO_STATE="$(pwd)/live_state.json" python3
evotrader_dashboard.py`) and confirmed the new text renders correctly:
`10 generation(s) run · 924 challenger idea(s) tried since, none better yet`.

`live_state.json` was never opened for writing this cycle — `git diff
--stat -- live_state.json` shows no change. No protected file touched, no
constitution change. Genome still v3 (1d) live, untouched.

## Next

Same three owner decisions as every recent session (item 2 accept/redirect,
item 5 sign-off, item 6 data source) — still nothing new to add, see
`AGENTS.md`'s "Owner decisions pending". Next session: if still nothing
decided and no new hard-call flag, keep doing small non-live-state pieces
like this one, or resume real `evolve` against the live champion once
that's judged the right default again.
