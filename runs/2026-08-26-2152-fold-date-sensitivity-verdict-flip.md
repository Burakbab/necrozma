# The champion-score swing flips a real accept/reject verdict — confirmed, not hypothetical

**3-hourly self-improvement check, ~21:52 UTC.**

## Why

Today's bar (2026-08-26) was already traded by the dedicated 00:20 UTC daily
run before this session started (`live_state.json` `updated`
`2026-08-26T00:22:17+00:00`) — nothing to do on the trading side. Picked up
the sharpest open item from the 12:57 UTC `fold-date-sensitivity` entry:
"whether this date-sensitivity measurably changes which challengers clear
`accepts()` in practice — e.g. replaying a real historical `evolve`
generation's candidate batch against the champion re-evaluated at a
different `--shift` value and checking whether the accept/reject verdict on
any borderline candidate flips."

## Method

One-off script (precedent: `seed-holdout-noise-diagnostic`,
`selection-noise-diagnostic` — a question answered without a new
`evotrader_bundle.py` command), not committed to the repo (scratch-only,
read-only, never calls `acct.save()`):

1. Loaded the real `live_state.json` (`researcher_memory`: 182 already-tested
   proposals excluded against champion v3, stagnation 12, holdout_draws 13 —
   the actual accumulated state a real `evolve` call would resume from right
   now).
2. Ran ONE real generation's worth of work exactly as
   `loop.evolve.EvolutionRun.generation()` does internally (same
   `Researcher.propose`, same `Evaluator.evaluate`, same real market data,
   `n_blind=14`) — but stopped short of its own `accepts()` loop so the
   candidate batch could be inspected before judgment.
3. For the top-3 ranked finite candidates (the ones a real generation
   actually gates), re-ran `constitution.accepts()` seven times each,
   swapping in ONLY `champion_score` for the seven values the 12:57 UTC
   `fold-date-sensitivity --shift 7` run already measured against v3
   (-1.652, 0.843, 1.245, 0.919, 1.126, 1.396, 1.480 for shifts 0-6). Every
   other input — the challenger's own real fold-aggregate fitness, both
   gate-stats dicts, `n_candidates`, `complexity_delta` — held fixed at its
   real, actually-computed value. This isolates the specific mechanism the
   12:57 UTC entry named (the champion baseline swinging day to day) rather
   than re-running the whole evaluation on shifted data too (a bigger,
   separate experiment).

```
python3 <scratch>/champion_score_swap.py
```

## Result

14 fresh proposals evaluated (196 cumulative against v3). Two of the top
three real candidates flip:

- **#1** (`cash_floor_pct`/`conviction_scale`/`unanimous_bonus`/... 8-gene
  blind-search patch), challenger fold-aggregate fitness **1.2371**: ACCEPTs
  the fold-aggregate gate on 3 of 7 measured champion-score days (shifts 0,
  1, 3 — i.e. today, yesterday, three days ago) and rejects on the other 4
  (shifts 2, 4, 5, 6), purely from which day's champion re-evaluation the
  margin check (`1.2371 <= s_champ + 0.2599`) is compared against.
- **#2** (`trend_slow`/`min_trend`/`rsi_hi`/... 8-gene patch), fitness
  **1.2067**: identical flip pattern — accepts on shifts 0/1/3, rejects on
  2/4/5/6.
- **#3** (`z_buy_below`/`conviction_scale`/... patch), fitness 0.9855:
  stable — hard-fails a gate (drawdown/trade-count) on every shift, never
  reaches the champion-score comparison at all. Not every candidate is
  shift-sensitive; only ones that clear the hard gates and sit close to the
  champion's own swing range are.

## Reading

Answers the open item directly and concretely: **yes, this is a real,
non-hypothetical effect, not just a property of the champion's own isolated
re-evaluation.** Two of three real candidates from an actual, currently-live
proposal batch (excluding the same 182 proposals a live `evolve` call would
exclude right now) would clear the fold-aggregate gate on some days and not
others, with nothing about the candidate itself changing — only the
calendar date `evolve` happens to run on. Concretely, if a real `evolve`
call had been made today (shift 0) instead of, say, four days ago (shift 4),
candidates #1 and #2 would have reached the sealed-holdout gate instead of
being rejected at the fold-aggregate step.

Important scope limit: "ACCEPT" here means clearing `accepts()`, the
fold-aggregate gate — the first of two independent gates a real promotion
needs. This experiment did not run the sealed-holdout check for these
candidates at each shift (that check uses its own separately-drawn holdout
window and its own cumulative multiple-testing count, a different and
already-well-characterized source of noise — see the `holdout-noise` /
`HOLDOUT_SIGMA` thread). So this does not claim either candidate would
actually promote on an accept-verdict day — only that which candidates even
get a chance to try the holdout gate depends on which day `evolve` runs,
which the fold-aggregate gate's design (a fixed multiple-testing margin
against a freshly-recomputed champion baseline) does not currently account
for or protect against.

This sharpens, rather than settles, the still-open framing question from
09:50/12:57 UTC: the date-sensitivity is not a curiosity confined to the
champion's own number — it changes real search outcomes on a real,
currently-pending candidate batch. Whether that's worth fixing (e.g.
smoothing the champion baseline over several as-of dates instead of using
whichever single day `evolve` happens to run on, or reducing sensitivity to
the day-1 greedy-allocation mechanism itself the 06:55/09:50 UTC entries
traced) is a design decision, not attempted here — any change to how
`accepts()` computes its champion baseline would be a constitution change
needing its own design pass and `AMENDMENTS.md` row.

## Verified safe

- No code changed in the repo — the script lives only in the session
  scratch directory, never touches `evotrader_bundle.py`, `loop/`,
  `constitution/`, or any committed file. No test suite run needed (same
  precedent as prior no-code-change diagnostic sessions).
- `live_state.json` untouched: md5 `1441d25f45fb4a927f993cbc8c505a5b`
  (unchanged from the 18:51 UTC entry), still reflects tick 12 from the
  00:20 UTC daily run. The script never calls `acct.save()`.
- `evotrader.manifest` md5 unchanged: `0bf3a7d9411ee692d0a9f152a7533803`.
- `git status --short` clean before this note (nothing in the working tree
  besides this run note and the AGENTS.md update).
- Today's bar already processed before this session started (`tick` not run
  this session, no double-trade).
- No genome promotion — no README `## Status` update needed.

## Next, if this thread stays worth pursuing

- Whether the same flip pattern holds against candidates from a *different*
  generation/proposal batch, or is specific to this one draw — not checked,
  would need another real `Researcher.propose` draw (non-deterministic,
  `seed=None`, same as a real `evolve` call).
- Whether a flipped candidate that reaches the holdout gate on an
  accept-verdict day would actually pass the sealed holdout too (i.e.
  whether this mechanism alone could let a real promotion through that
  wouldn't otherwise happen) — not attempted; would need to actually run
  `holdout_check` for a flipped candidate.
- The day-1-allocation-redesign question (proportional/ranked instead of
  greedy-first-come) and the window-5 `anatomy` post-mortem, both still open
  from the 09:50 UTC entry.
- Whether smoothing the champion's fold-aggregate baseline (e.g. averaging
  `champ_fit` over several trailing as-of dates instead of one) would
  reduce this specific flip-rate without introducing new noise of its own —
  untried design work, would need its own `AMENDMENTS.md` row if pursued.
