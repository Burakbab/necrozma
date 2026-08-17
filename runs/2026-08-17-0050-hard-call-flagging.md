# 3-hourly check — 2026-08-17 00:50 UTC — hard-call flagging shipped

## Git state on entry

Container came up in detached HEAD on a local `main` that had diverged from
`origin/main` with **no shared history at all** (`git merge-base` returned
nothing) — local `main` was two old "upload" commits, origin had 30 real
commits of project history. Per AGENTS.md's rule that `origin/main` is
authoritative when history has diverged, `git checkout main` then
`git reset --hard origin/main`, no force-push involved (nothing was pushed
from the stale local state).

## Daily bar

Already handled. `live_state.json` `updated: 2026-08-17T00:26:31+00:00`,
`runs/2026-08-17-0020-daily-trading.md` recorded tick 3 (NAV $10,024.40,
bought CRVUSDT/BNBUSDT/LINKUSDT). No trading performed this cycle.

## What was built

The "flag hard calls" half of AGENTS.md item 4 (LLM-backed consults). A new
pure function, `agents.judges.flag_hard_call(agreement_score, orders,
just_halted, overrides_this_bar, low_agreement_threshold=0.4)`, labels a bar
as worth a slower second look when:

- the circuit breaker just tripped this bar, or
- the Superior Judge overrode/trimmed/blocked at least one Risk-Judge-approved
  order this bar, or
- a live buy went through behind consult agreement below 0.4 (weak
  three-way consensus, real money moving anyway).

Wired into `loop.engine.Council.tick`: every already-logged decision-log entry
now carries a `"hard_call": {"is_hard_call": bool, "reasons": [str, ...]}`
field. Nothing reads this field yet — it only marks candidates for a future
"apply consult verdict" phase, which is not built (see AGENTS.md's updated
item 4 for why that half is a real design question, not just more code: an
unattended scheduled tick can't pause mid-execution for a slower opinion the
way the plan originally imagined).

## Why this is safe

- Purely additive: the flag is computed strictly *after*
  `Trader.execute(ts, final.orders, fill_prices)` has already run. Nothing
  upstream of execution changed.
- `agents.judges` and `loop.engine` are not in the constitution's checksummed
  set (`constitution` + `core.portfolio` only) — verified live,
  `evotrader_bundle.py summary`/`signals`/`tick` all still report
  `constitution verified dfae6a697f51fb49` after the change.
- New test `tests/test_hard_calls.py::test_hard_call_computation_cannot_affect_execution`
  runs the same synthetic backtest with `log_detail=True` and `log_detail=False`
  and asserts byte-identical `stats` and `closed_trades` — the flag cannot
  move a trade.
- Full suite: 45 passed (36 existing + 9 new), up from 36.
- `tick` against the real `live_state.json` still correctly reports "bar
  2026-08-16 already traded" (idempotency guard unaffected) — never touched
  live state this cycle.

## Mechanics note for future edits to `evotrader_bundle.py`

The bundle stores every module's source as a single-line, single-quoted
Python string literal in the `_SRC` dict (per AGENTS.md item 7 — it isn't
unflattened yet). Hand-editing that line is exactly the transcription-risk
pattern AGENTS.md warns about. Instead: `ast.parse` the file, find the
`_SRC[key] = <literal>` assignment's exact source span via the string node's
`lineno`/`col_offset`/`end_lineno`/`end_col_offset`, `ast.literal_eval` it to
get the real module source, edit that source as an ordinary Python string,
`repr()` it back, and splice the new literal into the original line at the
same column span. Verified afterward with `py_compile`, the real test suite,
and a live `summary`/`signals`/`tick` smoke test. No manual edits to the raw
`_SRC` line were made.

## Next steps carried forward

Unchanged from AGENTS.md except item 4, which now has a concrete open
question: whether "apply consult verdict & execute" should (a) split `tick`
into a stop-before-execution-on-hard-call phase plus a resume-and-execute
phase run by a later scheduled step, or (b) auto-downgrade hard calls
(smaller size / skip) and let a session review the log after the fact rather
than gating execution in real time. See AGENTS.md item 4 for the tradeoff.
Also worth doing before building further on this: run a few more live/backtest
ticks and check whether the 0.4 agreement threshold actually fires on real
decision-log data, or whether it needs recalibrating.
