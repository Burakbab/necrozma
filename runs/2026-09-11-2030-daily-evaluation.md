# Daily evaluation — 2026-09-11 20:30 UTC

## Scope

Read-only assessment of today's mechanism health: the 00:20 UTC daily
trading run, the day's scheduled `evolve` batches, and the 09:00 UTC daily
discussion note. No code or state changed by this session except this note
and one `AGENTS.md` "Next steps" addition (item 10, below).

## Daily trading run (00:20 UTC, tick 28)

Ran cleanly per `runs/2026-09-11-0020-daily-trading.md`: repo synced via
`tools/git_sync.py`, `evotrader_bundle.py tick` executed once (bar
`2026-09-10`, NAV $11,522.59 → $11,553.62, filled buy UNIUSDT), logged
`genome_version: 3`, `halted: false`. No "already traded", no constitution
change. `tick % 7 == 28 % 7 == 0`, so `evolve(3)` correctly triggered and
was backgrounded via `tools/background_runner.py` — completed later at
00:30 UTC (`runs/2026-09-11-0030-evolve-batch-v3.md`), no promotion,
390/390 tests passed before and after.

Five further 3-hourly `evolve` batches ran through the day (07:20, 10:31,
13:14, 16:33, 19:14 UTC), all 15-generation batches against the live v3
champion, all no promotion — ordinary. Cumulative candidates tried against
v3 rose from 9551 to 11048 over the day; `holdout-pressure` draws keep
losing with an unchanged margin shape. The 09:00 UTC daily-discussion note
found nothing new needing the owner's attention (same single open item,
#6 equities/FX data source, unchanged for days).

## Mechanism finding: stale genome version briefly published on the dashboard

One real (if minor and self-correcting) mechanism bug, not a trading
decision: the tick-28 commit (`8379290`, 00:26 UTC) published `index.html`
showing the "genome" stat tile as **"v1 / 5 generation(s) run"**, while
`live_state.json`'s actual `genome.version` was 3 the entire time (also
confirmed by the tick's own logged `genome_version: 3`). The next commit 9
minutes later (`5a21d96`, 00:35 UTC, the day's first evolve batch) silently
rebuilt the dashboard and corrected it back to "v3". So the public page
displayed a wrong genome version for about 9 minutes — no impact on
trading, state, or the account itself, but a real display-correctness bug.

Root cause: `evotrader_dashboard.py`'s `build()` prefers
`state/genomes/champion.json` over `live_state.json` (the documented
source of truth) for the genome-version tile, and that gitignored,
per-container cache file can be stale relative to `live_state.json` until
`evolve` itself next overwrites it. This is the same class of staleness
`AGENTS.md` already tracks for `_reconstruct_champion_genome`/
`Genome.champion()` (~line 1573), now confirmed in a second location (the
dashboard's own header tile). Filed as new item 10 in `AGENTS.md`'s "Next
steps" with a proposed fix direction (trust `live_state.json`'s
`genome.version` unconditionally, or validate against it before using the
disk copy) — not fixed in this session since it's outside this evaluation's
scope and the daily-trading run already produces the correct number on its
own within minutes.

## Verdict

Today went smoothly. The one mechanism issue found (stale genome version
transiently shown on the dashboard) is real but low-impact and
self-correcting; it's now tracked with a concrete fix direction rather than
left for a future session to rediscover from scratch.
