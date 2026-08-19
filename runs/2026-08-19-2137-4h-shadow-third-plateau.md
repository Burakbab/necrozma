# 4h shadow evolution, 15 generations — third-plateau check — 2026-08-19 ~19:56-21:37 UTC

Follow-up to AGENTS.md item 2's open question since the 2026-08-17 second-plateau
run: does a *third* plateau exist past generation 10, or does a fresh
x6-scaled-seed run reliably stop climbing after two? Same isolation discipline
as every prior 4h shadow run: whole scratch dir (`/tmp/.../shadow_4h_third_plateau`,
gone with this container), no `live_state.json` anywhere in it so
`Genome.champion()` falls back to a hand-built x6-scaled seed, standalone script
calling `EvolutionRun.run()` directly (bypasses the CLI's hardcoded `n_blind=14`)
at `n_blind=6`, 15 generations in one continuous process. Verified `bar_interval:
4h` in the setup log before trusting anything, and `GENOME_DIR`/`LINEAGE_PATH`
asserted to resolve under the scratch dir at runtime, not the repo.

Total wall time: ~101 min (368s to fetch 27 symbols x 4 years of 4h bars, no
cache, then 15 generations at `n_blind=6`).

## Result: three promotions, all inside the first 6 generations — then 9 straight
generations of stagnation with no fourth

- **Generation 1**: scaled seed v1 (fitness **-2.192**) → **v2** via
  `risk_judge.correlation_penalty` 0.0 → **0.9**. Holdout passed
  (`beat_benchmark: true`, excess return +21.5%, excess Sharpe +0.58). Yet
  another distinct magnitude of this gene "fixing" a catastrophically broken
  scaled seed on the first try — 0.1, 0.75, and now 0.9 have each separately
  fixed three different broken 4h seeds across four independent runs. Read the
  same way every prior run has: this is evidence the gene shrinks concentration
  generically against an overtrading baseline, not that any specific value is
  validated — consistent with the resolved-negative finding against three
  *competent* 1d champions.
- **Generation 2**: v2 → **v3**, fitness 0.627 → **0.834**, via
  `consult_conservative.enabled: False` — the researcher's diagnostic literally
  named the reason (`"consult_conservative entries lost -943 over 75
  trades — try removing it"`). Holdout passed (+23.7% excess return, excess
  Sharpe +0.80). Notable against "Measured 2026-08-16"'s finding that
  `consult_conservative` is a bad *buyer* but an excellent *seller* on the 1d
  champion — here, on a still-broken scaled 4h seed, cutting it as an entry
  source outright helped; not directly comparable (different bar size,
  different genome competence level) but worth flagging if this ever
  resurfaces on the 1d side.
- **Generation 3-5**: champion v3 held, 16/6/6 proposals each generation, none
  cleared the bar.
- **Generation 6**: v3 → **v4**, fitness 0.834 → **1.051**, via a genuinely
  combined 3-gene blind-search patch (`cash_floor_pct` 0.05→0.076,
  `trailing_stop` -0.15→-0.202, `lone_voice_scale` 0.6→0.093). Holdout passed
  (+27.2% excess return, excess Sharpe +0.93 — the strongest holdout edge of
  the three promotions this run).
- **Generations 7-15**: **nine straight generations of stagnation**, boldness
  climbing 0→8, 65 candidates cumulatively tried against v4 by generation 15.
  Best candidate each generation ranged from -2.247 to 1.197 against champion's
  1.051 + rising multiple-testing margin — nothing cleared it, including at the
  highest boldness level this or any prior 4h shadow run has reached.

## Answering the open question

**No third plateau surfaced in this run — but the comparison to the
2026-08-17-0510 run sharpens rather than settles the question.** That run found
2 promotions across 10 generations (gen 1, gen 9) and stopped at exactly the
point its second promotion landed — 1 generation of "holding" before the run
ended, not proof of a stable plateau. This run found 3 promotions, all
compressed into the first 6 generations, then held through **9** further
generations at climbing boldness (more stagnation-generations past a plateau
than any prior 4h shadow run has tested) with no fourth. Read together: the
*shape* (quick early fixes, then a hard stop) replicates, but the *specific*
generation count and number of promotions before the wall does not — 2 vs 3
promotions, plateau at generation 9 vs generation 6. That is consistent with
different RNG draws (fresh seed=7 `Researcher` state each run, since no shadow
run's process/RNG state survives its container) finding different numbers of
"easy" fixes for a differently-broken scaled seed before hitting the same kind
of wall, not a fixed number of promotions this recipe always finds. The honest
answer to "does a third (or Nth) plateau exist" is still not proven either way
by a single run reaching a firm stop — what this run adds is the first case of
**9 consecutive stagnant generations at boldness 8** without a further
promotion, the deepest stagnation probe yet, and it stayed flat. If this
question is revisited again, running past 15 generations (this run's own
generation 6 champion, boldness already at 8 with no sign of movement) is
lower-value than it looked before this run — the marginal generation count
needed to falsely conclude "plateaued" keeps rising, and each additional
generation costs the same ~6-7 min this run's did.

## Verified safe

- Isolation asserted at runtime, not just described: `GENOME_DIR` and
  `LINEAGE_PATH` both resolved under the scratch dir (script would have
  raised `AssertionError` otherwise); confirmed no `live_state.json` file
  exists anywhere under the scratch tree.
- Real repo `live_state.json` md5 identical before/after
  (`09c35b692da1d694c5a3cace5d488f40`), `git status --short` empty throughout
  (no code was changed this run — the script lived entirely in `/tmp`).
- `constitution` package untouched (this run never imports or writes to it
  beyond the read-only `accepts`/`fitness`/`holdout_accepts` calls every
  `EvolutionRun` already makes) — full suite still 104 passed after the run,
  same as before it.
- Today's 2026-08-19 daily bar confirmed already processed before this check
  started: `live_state.json.updated` = `2026-08-19T00:21:55+00:00`, journal's
  last 3 entries dated 2026-08-17/18/19, all at ~00:2x UTC (the 00:20 UTC
  daily run) — no double-trade, `tick` not run this session.
- Scratch dir and `result_summary.json`/`state/lineage.jsonl` are ephemeral
  (`/tmp`), gone with this container. Nothing here touched `researcher_memory`
  or promoted anything live — shadow-only, per the standing 2026-08-15
  decision to keep live cadence daily.

Next: still open, now with a sharper cost estimate — whether stagnation this
deep (9 generations, boldness 8) ever breaks in a longer run remains untested;
whether it's worth the wall-clock to find out is a judgment call this run's
result should inform, not settle on its own.
