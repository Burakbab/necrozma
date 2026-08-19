# Real blind search vs. the concentration region — 2026-08-19 ~22:18 UTC

Scheduled 3-hourly check. Today's daily bar was already handled by the 00:20
UTC daily run (`live_state.json` `updated` at `2026-08-19T00:21:55Z`, tick
recorded in `runs/2026-08-19-0020-daily-trading.md`) — nothing to trade this
cycle; `tick` was not run. Used the rest of the slot on item 3's last
explicitly open gap: every prior concentration finding (4 real champions'
held-set correlation, plus two hand-built adversarial genomes that both blew
the drawdown gate) came from either an organically-found real champion or a
deliberately hand-constructed genome — never from unconstrained blind search
itself. Does the Researcher's own proposal mechanism, run for real against
the real champion, ever wander into the concentrated region on its own?

## Setup

Standalone script (`run_shadow_search.py`, not committed — lived entirely in
a scratch dir outside the repo), same isolation discipline as every prior
shadow run: copied the real `live_state.json` (champion v3, real
`researcher_memory`, 27-symbol real Binance data) into a scratch directory,
pointed `EVO_STATE` at the scratch copy, and called `loop.evolve.EvolutionRun`
directly (the bundled CLI's `evolve` command hardcodes `n_blind=14`, matching
what this script also used, so no deviation there — only the driver loop is
custom, to log every top-8 candidate's concentration-relevant genes each
generation instead of just the winner). Isolation asserted at runtime, not
just described: `GENOME_DIR` and `LINEAGE_PATH` both asserted to resolve
under the scratch dir before anything else runs, which printed and held for
the whole run. 10 generations, real walk-forward folds, real sealed holdout
gate, real multiple-testing margin — the exact same code path a live `evolve`
call takes, just writing to a throwaway copy.

Tracked genes: `risk_judge.max_positions`, `max_position_pct`,
`cash_floor_pct` (the three genes both hand-built adversarial constructions
used to force concentration), plus `correlation_penalty`/`correlation_lookback`
for completeness. Every generation's top-8 ranked candidates were scanned for
patches touching any of these; not just the generation's winner.

## Result: no promotion, and no concentration-touching candidate got close

10 generations, 128 fresh proposals (cumulative tested against v3 climbed
140 → 282; boldness climbed 9 → 18, continuing the real account's own
already-long stagnation streak — this picked up mid-search, not from a fresh
champion). Champion v3 (fold-aggregate fitness 1.737) held through all 10;
the best candidate of any kind across the whole run was 1.776 (generation 5,
not concentration-related), still short of the multiple-testing margin.

Of the ~30 individual candidates that touched a concentration gene across
the 10 generations, every single one scored below champion, and the pattern
is not close:

| direction | example patch | best fitness seen |
|---|---|---|
| fewer/larger positions (concentrating) | `max_positions: 2` + `cash_floor_pct: 0.4163` (gen 5) | 0.4012 |
| fewer/larger positions (concentrating) | `max_positions: 3` + `max_position_pct: 0.2367` (gen 7) | 0.8055 |
| larger position size alone | `max_position_pct: 0.34` (gen 1) | 1.1293 |
| lower cash floor alone | `cash_floor_pct: 0.191` + `max_position_pct: 0.0955` (gen 10) | 0.9184 |
| more/smaller positions (de-concentrating) | `max_positions: 10` (gen 7) | 1.4082 |
| `correlation_penalty` (already known dead) | `0.1` (gen 1) | 1.5862 |

The single highest-scoring concentration-touching candidate anywhere in the
run (`max_positions: 10`, fitness 1.4082, generation 7) is actually the
*opposite* direction — more positions, less concentration — and it still
lost by a wide margin. No candidate that shrank `max_positions` toward the
adversarial constructions' 2-3 range, or raised `max_position_pct`/lowered
`cash_floor_pct` toward their values, ever scored within reach of the
champion.

One earlier single-generation smoke test of this same script (not part of
the 10-generation run above, used only to validate the harness before
committing to the full run) had drawn a `max_positions: 2` candidate at
fitness 1.988 — above the champion. That did not reproduce here: proposal
generation is randomized per invocation (`Researcher(seed=None)`), so it was
a lucky one-off draw, not a real signal, and is superseded by this fuller
10-generation, ~30-candidate read. Worth naming explicitly since it would be
easy to over-read from a single number.

## Reading against item 3

This was the one piece item 3's evidence base was missing: not "does a
hand-built concentrated genome fail the gates" (answered twice, yes) but
"does real search, proposing small local mutations one gene at a time
without deliberately forcing concentration, ever get pulled toward that
region on its own." Across 128 real proposals against the real champion, it
did not — concentration-leaning single-gene mutations scored *worse* than
the champion by a wide and consistent margin, not marginally worse. This
closes the gap named in "Current state" as the last remaining piece: item 3
now has real champions (4), hand-built adversarial constructions (2), and
real unconstrained search (this run), all pointing the same direction. If
this item is ever acted on, dropping `correlation_penalty`,
`correlation_lookback`, and `RiskJudge._correlation_scale` as dead weight is
now resting on a genuinely complete evidence base — not deciding whether to
act was still this run's own choice: the removal itself touches several
interdependent places (genome defaults, mutation gene ranges, the
Researcher's structural proposal grid, `RiskJudge`, the `Briefing`/Analyst
`rets_by_symbol` plumbing, several tests, and the diagnostic CLI code built
specifically to measure this question) and is a bigger, multi-file surgery
better scoped as its own dedicated session than squeezed into the tail of
this one.

## Verified safe

- `git status --short` clean throughout and after — no repo file touched,
  the driver script lived entirely in a scratch directory outside the repo.
- `live_state.json` md5 identical before/after: `09c35b692da1d694c5a3cace5d488f40`
  (matches every prior run this cycle checked against).
- `evotrader.manifest` md5 identical before/after:
  `6a4434574ff424f74ff300ebdb50d194`.
- Isolation assertions (`GENOME_DIR`/`LINEAGE_PATH` under the scratch dir)
  held for the whole run, printed at startup.
- `tick` not run this session; today's 2026-08-19 bar was already processed
  by the 00:20 UTC daily run before this check started (confirmed via
  `live_state.json`'s `updated` timestamp and the existing daily-trading run
  note) — no double-trade risk.

## Next

Item 3's evidence base is now as complete as a single-champion, single-search
budget can make it. The only way to add more here would be repeating this
same search from a different champion/seed, which has sharply diminishing
value at this point (three independent evidence types already agree). The
real next step, if this item is ever picked up to actually act on, is the
removal itself — scoped as its own dedicated session per the paragraph
above, not attempted here.
