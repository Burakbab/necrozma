# Daily evaluation — 2026-09-08 20:30 UTC

## Session start

Cloud clone started in detached HEAD (usual state). `git checkout main` +
`git pull` fast-forwarded cleanly, `4f15e68` → `de04a8f`, no divergence, 49
commits behind at start.

## Did today's trading run smoothly?

Yes. `runs/2026-09-08-0020-daily-trading.md`: tick 25 on bar
`2026-09-07 00:00:00+00:00`, NAV $12,185.03 → $12,179.04, no trades (held
LINKUSDT/XRPUSDT/AAVEUSDT/SOLUSDT), constitution verified unchanged, no
`already traded` hit, no `CONSTITUTION MODIFIED` warning. `25 % 7 = 4`, so
`evolve` correctly did not run as part of the daily trading cycle per
protocol. Cross-checked directly against `live_state.json`: `ticks` = 25,
`broker.positions` and `broker.cash` ($4,231.83) match the note exactly,
genome still v3 (1d), untouched. No day-to-day P&L judgment made here — the
NAV move is noise, not a mechanism concern.

Seven 3-hourly `evolve` batches ran today (00:47, 04:27, 07:31, 10:08,
13:15, 16:18, 19:14 UTC) per `AGENTS.md`'s "Current state" log, each 15
generations against the live v3 champion, all no promotion, fitness held
flat at 1.590 throughout. Each entry documents `pytest -q` 366/366 run
before `evolve` (baseline, no code touched), a key-by-key `live_state.json`
diff showing only `lineage`/`researcher_memory`/`updated` changed, and
constitution hash unchanged — consistent, disciplined verification
discipline across all seven. No promotion is expected and not itself a
fault; the champion has now fielded ~6,429 candidates without losing.

## Mechanism observations (not trading-strategy calls)

**Recurring, not new: the `nohup ... &`-in-one-tool-call footgun (roadmap
item 9).** The "Current state" log shows this being re-triggered and caught
5 times in a single week (2026-09-06, twice on 09-07, twice on 09-08) —
each time harmless (caught immediately via `ps aux` / `kill -0` polling to
real exit before touching state), but each time re-spending a session's
attention rediscovering a documented pitfall. The existing writeup lives at
roadmap item 9, ~3300 lines into `AGENTS.md`, far from where the `evolve`
command actually gets typed. Since burying it there evidently isn't
preventing recurrence, this session added a short inline warning directly
next to `python3 evotrader_bundle.py evolve N` in the `### Commands`
listing near the top of the file, and left a pointer under item 9 itself.
This is a low-risk, doc-only change — worth revisiting if the pattern keeps
recurring after today, since at that point doc placement isn't the fix and
something more mechanical (a wrapper script, a pre-flight lint) probably
is.

**This evaluation session's own environment lacked `numpy`/`pytest`
entirely** (fresh container, `pip3 show numpy`/`pytest` both empty at
start) — had to `pip3 install numpy pandas pytest` before re-verifying the
suite (confirmed 366/366 passing after, matching today's `evolve` batches'
own count). This is almost certainly this session's fresh-container
baggage rather than a repo problem — no `requirements.txt`/dependency
pinning exists in the repo to fix, and every same-day `evolve` batch
independently ran and passed `pytest -q` from its own environment without
issue. Noting only because a `requirements.txt` (or equivalent) would make
this reproducible across environments instead of relying on each fresh
container coincidentally having the right packages preinstalled; not
urgent enough to add to Next steps unless a future session hits it as a
real blocker.

## Owner decisions pending

Unchanged: items 2 (4h-bar shadow evolution), 5 (short selling), 6
(equities/FX) are still open with no new owner input, per today's 09:00 UTC
daily discussion. Not re-derived here.

## Changes this session

- `AGENTS.md`: added an inline warning next to the `evolve N` command in
  `### Commands`, and a pointer under roadmap item 9 explaining why.
- This file.

No code, genome, or `live_state.json` changes. Dashboard not rebuilt (no
state change to reflect).
