# Shadow evolve against real live champion v2 — 2026-08-16 ~00:59 UTC

Scheduled 3-hourly check. Today's daily bar was already handled by the 00:20
UTC daily run (`live_state.json` `updated` at `2026-08-16T00:21:55Z`, tick
already recorded in `runs/2026-08-16-0020-daily-trading.md`) — nothing to
trade this cycle. Used the rest of the slot on Next-steps item 3: run the
Researcher's automatic `correlation_penalty` proposal "against live champion
v2 under the actual walk-forward/holdout/multiple-testing gates", which had
been shipped but never run.

## Setup

Copied `live_state.json` (champion v2, real genome, real accumulated
`researcher_memory`) into a scratch directory outside the repo and ran
`EVO_STATE=shadow_state.json python3 evotrader_bundle.py evolve 6` there —
same 27-symbol, 1d-bar universe and real Binance data the live account
trades on, same constitution gates, but writing only to the scratch copy.
**Nothing here touched the real `live_state.json`.**

## Result: the correlation gene lost, but two other real promotions were found

Generation 1 (14 fresh proposals, 152 already excluded from prior live
`evolve` runs against v2): a blind-search combination beat the champion —

- **v2 → v3**: `consult_conservative.exit_rsi` 68→50.0,
  `consult_moderate.rsi_lo` 35.18→60.0, `consult_risky.conviction_scale`
  0.7356→1.9437, `consult_risky.min_breakout` −0.02→−0.0148,
  `consult_moderate.rsi_hi` 72→92.0.
  Selection fitness 0.682→1.560, merged fitness 0.805→1.837, max_dd
  30.0%→5.9%, sealed holdout: champion −2.058, challenger −0.330 (passed).

Generation 2 (fresh proposal batch against the new champion): another real
improvement —

- **v3 → v4**: `risk_judge.max_positions` 6→4, `consult_conservative.exit_rsi`
  50.0→50.934.
  Selection fitness 1.560→2.461, merged fitness 1.837→2.949, max_dd
  5.9%→4.4%, sealed holdout: champion −0.330, challenger −0.251 (passed).

Generations 3–6 found nothing that beat v4 (best candidates 2.73, 2.33,
2.46, 2.58 vs champion 2.461 — close but none cleared the rising
multiple-testing margin plus holdout check). Final shadow champion: **v4**.

**The correlation-penalty proposal (`correlation_penalty` 0.0→0.5) was
actually the top-ranked candidate in generation 3** (fold-aggregate fitness
2.7318, ahead of the v4 champion's 2.461) — but it **failed the sealed
holdout**: challenger fitness −0.482 vs champion −0.251. Correctly rejected.
Answer to the open question: at `0.5`, correlation-awareness looks good on
the search folds but doesn't generalize to the untouched holdout slice — not
a promotion candidate as tuned. It surfaced twice more earlier (fitness 0.42
against v2, fitness 1.82 against v3) and lost the ranking outright both
times. Nothing here says the correlation mechanism is broken, only that
`0.5` specifically doesn't hold up; a different penalty value or the
Researcher proposing other values was not tried this cycle.

## Why this matters: the live champion (v2) is measurably behind

The live account has been trading champion v2 (fitness 0.889, max_dd ~30%)
since 2026-08-15, "plateaued... for 13+ generations" per `AGENTS.md`. This
shadow run, using the exact same accumulated `researcher_memory` the live
account carries, found a **real, gate-passing improvement to v4** (fitness
2.461, max_dd 4.4%) inside 2 generations. This is not a different genome
lineage or a different bar size — it is the same champion, same real 1d
data, same constitution, just a second independent blind-search draw. The
full patch from live v2 to this shadow v4, for reference:

| gene | live v2 | shadow v4 |
|---|---|---|
| `consult_moderate.rsi_lo` | 35.1764 | 60.0 |
| `consult_moderate.rsi_hi` | 72.0 | 92.0 |
| `consult_risky.conviction_scale` | 0.7356 | 1.9437 |
| `consult_risky.min_breakout` | −0.02 | −0.0148 |
| `consult_conservative.exit_rsi` | 68.0 | 50.934 |
| `risk_judge.max_positions` | 6 | 4 |

**This was not applied to the live account.** This 3-hourly slot is
explicitly scoped to shadow/offline work only; promoting a champion is out
of scope here even when the shadow result looks this strong — that's what
the weekday daily run's `evolve 3` (every 7th tick) or the weekend all-hands
session are for. Flagging clearly: the daily run's own `evolve` may or may
not stumble onto this same combination (blind search is randomized each
invocation), so this is worth a deliberate look rather than assuming it'll
be found on its own soon.

Total runtime: ~13 minutes (data already cached from the 00:20 UTC run;
6 generations, `n_blind=14` each).
