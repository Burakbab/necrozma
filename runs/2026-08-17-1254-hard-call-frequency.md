# Hard-call frequency measurement — 2026-08-17 12:54 UTC (3-hourly check)

## What ran

No new daily bar to trade (last `tick` was tick 3 on bar 2026-08-16,
`live_state.json.updated` = 2026-08-17T00:26:31Z, matching the
2026-08-17-0020 daily run note; today's bar isn't closed yet). Spent the
slot on item 4 of `AGENTS.md`'s Next steps: the "flag hard calls" feature
shipped 2026-08-17 with nothing yet measuring how often it actually fires.
That was the explicit next step recorded after it shipped.

## What was built

- `agents.judges.summarize_hard_calls(decision_log)` — pure aggregator,
  reads `hard_call` fields already attached to a decision log (backtest or
  live journal), returns bar counts, flag rate, a per-trigger breakdown, and
  the flagged bars themselves. Tolerates entries that predate the field
  (treats a missing key as "not flagged") so it can run over the live
  journal unconditionally.
- `evotrader_bundle.py hard-calls` — new CLI diagnostic, same guarantees as
  `anatomy`/`consults`/`costs`/`regime`: full-history replay via the
  existing `run_backtest(..., log_detail=True)`, read-only, never touches
  `live_state.json` or the champion. Reports the full-history rate, then
  separately reports on the real live journal.
- 5 new tests in `tests/test_hard_calls.py` (7 → 12; full suite 45 → 49
  passed): empty-log shape, category counting, tolerance for missing
  `hard_call` keys, and an end-to-end check against a real
  `run_backtest` output.

## What it found

Against the real champion (v3, 1d bars, full 4-year replay):

```
535/1386 logged bars flagged (38.6%)
  circuit_breaker          4
  superior_override       85
  low_agreement_buy      455
```

(Categories don't sum to 535 — some bars trip more than one trigger.)

**38.6% is not a "hard call" rate, it's most of the traffic.** The
low-agreement-buy trigger dominates and is close to meaningless as a
filter: with exactly 3 consults, the agreement score is discretized to
0/0.33/0.67/1.0, so "agreement < 0.4 behind a buy" is mechanically
identical to "exactly one consult proposed this buy." That's a normal,
frequent pattern the system already prices in procedurally
(`risk_judge.lone_voice_scale` sizes lone-voice buys down rather than
treating them as anomalies) — not a rare disagreement worth a slower
second look.

Drop that one trigger and the rate falls to `circuit_breaker` +
`superior_override` ≈ 89/1386 (6.4%) — a rate a human or LLM review pass
could plausibly keep up with.

The live journal (3 ticks) shows 0 flagged so far, but all 3 predate the
`hard_call` field — it shipped after tick 3 ran. Nothing to compare against
from real trading yet; tick 4 (tomorrow's 00:20 UTC run) will be the first
with real data, and `evotrader_bundle.py hard-calls` will report it.

## What this means for the open design question

`AGENTS.md` item 4 flagged two designs for "apply consult verdict" — (a)
pause mid-tick and resume later, or (b) auto-downgrade + review after the
fact — and said the choice needed a decision. This run doesn't make that
choice; it makes the choice more tractable. At 38.6%, neither design is
really workable: (b)'s "review after the fact" doesn't scale to a third of
all bars, and (a)'s "occasional slow path" stops being occasional. The
sharper next step, recorded in `AGENTS.md`, is narrowing the trigger set
*before* picking (a) vs (b) — drop or rework low-agreement-buy, then
re-check the rate with `hard-calls`.

## Verification

- `flag_hard_call` and its wiring in `loop.engine.Council.tick` were not
  touched — this run only reads what's already logged.
- `agents.judges`/`loop.engine` aren't in the checksummed constitution set;
  `evotrader_bundle.py summary` still reports `constitution verified
  dfae6a697f51fb49`.
- Full test suite: 49 passed (up from 45).
- `live_state.json` untouched (confirmed via `git status` — no diff).
- `index.html` not rebuilt — no state change to reflect.
