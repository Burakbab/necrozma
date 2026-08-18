# 3-hourly check — 2026-08-18 03:53 UTC — hard-call review-after-the-fact shipped

## Git state on entry

Container came up in detached HEAD, local `main` two commits behind
`origin/main` with shared history (unlike the 2026-08-17 00:50 run, no
force-reset needed). `git checkout main && git pull --rebase origin main`
rebased cleanly.

## Daily bar

Already handled. `live_state.json` `updated: 2026-08-18T00:21:43+00:00`,
`runs/2026-08-18-0020-daily-trading.md` recorded tick 4 (bar 2026-08-17,
NAV $9,981.63 → $9,985.97, no trade — a proposed CRVUSDT buy was rejected
downstream). No trading performed this cycle; next bar (2026-08-18) isn't
closed until the 2026-08-19 00:20 UTC daily run.

## What was built

The "review after the fact" half of AGENTS.md item 4 (LLM-backed consults) —
the (a)-vs-(b) architecture decision AGENTS.md had flagged as "the actual
next step" after the 2026-08-17 narrowing work brought the flag rate down to
9.6%. Chose **(b)**: hard calls are never gated in real time; a later
scheduled session reads the flag, reasons about it, and writes a verdict
back into durable state after the fact. Rejected (a) (stop-before-execution)
because it would reintroduce the fills-happen-later problem `core.live`'s
own docstring deliberately avoids ("fill at the live price at the moment of
execution"), for a rate (~9.6%, at most one live bar a day) that no longer
needs that tradeoff.

Three pieces, all additive:

- `core.live.LiveAccount` gains a durable `hard_call_reviews` field
  (`self.state.get("hard_call_reviews", [])` — defaults to `[]`, so every
  state file saved before this shipped loads unchanged) and a new method
  `add_hard_call_review(tick, verdict, notes="")` that looks up the journal
  entry for `tick`, raises `ValueError` if it doesn't exist or was never
  flagged (`decision.hard_call.is_hard_call` falsy), and otherwise appends
  `{tick, bar, reviewed_at, verdict, notes, reasons}` to
  `hard_call_reviews`. `save()` now persists the field.
- `agents.judges.pending_hard_call_reviews(journal, reviews)` — a pure
  function, read-only by construction (takes two already-built lists, never
  state itself): the set difference between flagged journal entries and
  reviewed ticks, matched by `tick`.
- New CLI `evotrader_bundle.py review-hard-calls`: with no args, lists
  pending flagged bars in plain language (or "no hard calls pending review"
  if none); with `--tick N --verdict '...' [--notes '...']`, calls
  `add_hard_call_review` and saves — the only thing this command does that
  writes to `live_state.json`.

## Why this is safe

- Purely additive: nothing upstream of `Trader.execute()` changed: the
  reviewed tick already ran, long before any review is ever written.
- Bundle mechanics: followed the `ast.parse` → locate the `_SRC[key] = ...`
  line → `ast.literal_eval` → edit as ordinary Python → `repr()` → splice
  back method documented in `runs/2026-08-17-0050-hard-call-flagging.md`.
  First attempt at the splice (an offset-based `ast` node-span approach) had
  an offset bug and silently corrupted the file — caught immediately by
  `py_compile` failing, before anything was tested or committed; recovered
  with `git checkout -- evotrader_bundle.py` and redid it with a simpler
  line-based approach (each `_SRC[key] = ...` assignment is confirmed to be
  exactly one physical line), then verified the round-trip by re-extracting
  both modules and diffing byte-for-byte against the edited source before
  moving on.
- Tested: `tests/test_hard_calls.py` +4 (`pending_hard_call_reviews`:
  empty/nothing-flagged, lists flagged-with-no-review, excludes
  already-reviewed ticks, tolerates missing `decision`/`hard_call` keys).
  `tests/test_live_account.py` +5 (backward-compat load with the field
  absent, a successful review records the right fields, `ValueError` on an
  unknown tick, `ValueError` on a tick that wasn't flagged, a full
  save-then-reload round-trip). Full suite: **64 passed, up from 55**.
- Smoke-tested end-to-end against a **throwaway copy** of `live_state.json`
  (`EVO_STATE=<scratch path>`), synthetically flagging tick 4's decision to
  exercise a real write: `review-hard-calls` listed it pending →
  `--tick 4 --verdict proceed --notes "..."` recorded it → a second
  `review-hard-calls` call correctly showed 0 pending. Never touched the
  real file for this part.
- Verified against the real `live_state.json`: `summary`, `signals`, `tick`
  (correctly reported "already traded", no double-trade) and
  `review-hard-calls` (correctly reported "no hard calls pending review — 0
  reviewed so far", since tick 4's real `hard_call.is_hard_call` is `false`)
  all ran clean, `constitution verified dfae6a697f51fb49` throughout, and
  `md5sum live_state.json` was **identical before and after this entire
  cycle's work** (`c4289723973ee8ace977f7abaf0003a8`).

## Honest caveat

No live journal entry has ever actually flagged (`is_hard_call: true`) —
tick 4 was the first tick with the field present and it came back `false`.
This ships ahead of its first real case, not in response to one. The next
useful step isn't more code here: it's a future scheduled session actually
using `review-hard-calls` the first time a real live tick flags something —
reading the case, reasoning about it inline, and recording a verdict. That
first real review is the point of this infrastructure.

## AGENTS.md updated

"Current state" (new dated entry) and item 4 of "Next steps" (the
(a)-vs-(b) decision recorded as made, with the concrete next action spelled
out), plus the `review-hard-calls` command added to both command reference
lists and a clarifying note that unlike the five true diagnostics, this one
command intentionally writes to `live_state.json` when given `--tick`.
