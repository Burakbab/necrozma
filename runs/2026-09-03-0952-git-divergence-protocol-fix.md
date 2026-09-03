# 3-hourly self-improvement check — 2026-09-03 ~09:46-09:52 UTC

## State check

- Cloud clone started detached, local `main` at `46db6ff` showing no shared
  history with `origin/main` at `56182f9` under `git merge-base` — the same
  divergence at least four other sessions have hit since 2026-09-02 19:00
  UTC. `git rev-parse --is-shallow-repository` confirmed the clone is shallow
  (depth 50). `git fetch --depth=200 origin main` immediately found a real
  merge-base: local `main`'s tip was an ancestor of `origin/main`, just 58
  commits behind, not a rewritten history. `git merge --ff-only origin/main`
  applied cleanly — no reset, nothing discarded.
- `pip3 install -r requirements.txt -q` — clean.
- `live_state.json`'s `updated` timestamp: `2026-09-03T00:22:19+00:00`,
  matching tick 20 (`runs/2026-09-03-0020-daily-trading.md`, held, no trade).
  Today's daily bar was already handled; no `tick` run this cycle. (Ran the
  bare `python3 evotrader_bundle.py` once to double check — it correctly
  reported "bar already traded" and did not touch state; confirmed via
  `md5sum live_state.json` unchanged before/after.)
- `python3 -m pytest -q`: 338/338, confirmed as this session's baseline.

## What this cycle did

Read `AGENTS.md`'s "Current state"/"Next steps" and this morning's
`runs/2026-09-03-0900-daily-discussion.md`. Every concretely-scoped open item
is currently blocked on an owner decision or has nothing new to check:

- **Item 2** (4h-bar shadow evolution): three consecutive sessions
  (2026-09-02 12:47 UTC, 2026-09-03 00:46 UTC, 2026-09-03 04:16 UTC) plus this
  morning's daily discussion have all recommended treating the unconstrained-
  search sub-thread as exhausted and making the accept-vs-redirect call
  explicitly rather than running a sixth `x6` seed. Running a sixth seed this
  cycle would have directly contradicted that recommendation for no new
  information — skipped.
- **Item 4** (LLM-backed consults): `review-hard-calls` reports zero pending
  — nothing to review.
- **Item 5** (short selling): blocked on a human review + `evotrader.manifest`
  re-seal before Phase 1 can touch the constitution-protected
  `core/portfolio.py` — unchanged since 2026-08-30.
- **Item 6** (equities/FX): blocked on a human picking a real data source
  (Alpaca vs. a free historical mirror) — the 2026-09-02 15:50 UTC design
  pass was explicit that shipping a fetcher before that decision would be
  "scaffolding with no caller," not progress.
- **Item 7** (unflatten): closed as feature-complete 2026-08-24, explicitly
  flagged as "not obviously worth attempting without a reason" to widen it
  further.

With every named roadmap item genuinely blocked or closed, this cycle picked
up a real but smaller paper cut instead of manufacturing speculative research
on a thread three sessions have already said to stop probing: the recurring
git-divergence situation itself. Grepped `AGENTS.md` and confirmed the same
"detached HEAD, no common ancestor" situation has hit at least five sessions
in the last ~15 hours (2026-09-02 19:00, 21:47, 2026-09-03 00:46, 03:46, and
this morning's 09:00 UTC daily discussion), each resolving it differently —
several defaulting straight to `git reset --hard origin/main`, which is
destructive and, per this session's own repeated general instructions, worth
avoiding when a safer alternative exists. The 09:00 UTC daily discussion
independently traced the real cause (`git fetch --unshallow`) an hour before
this session did the same thing (`git fetch --depth=200`), confirming it: the
cloud clone's shallow fetch depth, not a real force-push rewrite. Nobody had
yet updated the Run protocol to say why this keeps happening or which fix
avoids the destructive one.

**Change shipped**: `AGENTS.md`'s Run protocol step 2 now explains the real
cause and gives the non-destructive sequence (`git fetch --unshallow` or
`--depth=200`, then check `git merge-base`, then `git merge --ff-only`),
keeping `git reset --hard origin/main` as the documented fallback only for a
genuine history rewrite (no merge-base even with full history fetched). Pure
documentation change inside `AGENTS.md` — no code touched, no protected file
touched, `live_state.json` untouched (md5 identical before/after this
session), `python3 -m pytest -q` 338/338 unaffected (nothing re-run since no
code changed).

## Next steps

Unchanged from this morning's daily discussion: item 2's accept-vs-redirect
call is the one thing genuinely waiting on the owner. Items 5 and 6 remain
blocked the same way. No new research thread opened this cycle — the next
session with genuinely new information on any of the above should pick up
there; otherwise, keep doing the ordinary daily/3-hourly maintenance.
