# Flipped fold-aggregate candidates fail the sealed holdout anyway — the holdout gate backstops the date-sensitivity, at least this draw

**3-hourly self-improvement check, ~00:52 UTC.**

## Why

Today's bar (2026-08-27) was already traded by the dedicated 00:20 UTC daily
run before this session started (`live_state.json` `updated`
`2026-08-27T00:21:49+00:00`, tick 13) — nothing to do on the trading side.
Picked up both open items the 2026-08-26 21:52 UTC `fold-date-sensitivity`
verdict-flip entry left:

1. Whether the flip pattern (candidates that ACCEPT the fold-aggregate gate
   on some as-of days and reject on others, with nothing about the candidate
   itself changing) reproduces on a *different* real proposal batch, or was
   specific to that one draw.
2. Whether a flipped candidate that reaches the holdout gate on an
   accept-verdict day would actually pass the sealed holdout too — i.e.
   whether this mechanism alone could let a real promotion through that
   wouldn't otherwise happen.

## Method

One-off script (same precedent as the 21:52 UTC entry — a question answered
without a new `evotrader_bundle.py` command), scratch-only, read-only, never
calls `acct.save()` or `Genome.promote()`:

1. Loaded the real `live_state.json` via `core.live.LiveAccount.load()`
   (`run_from_files.py`'s own loader) — champion v3, `researcher_memory`: 182
   already-tested proposals excluded, stagnation 12, holdout_draws 13, same
   accumulated state a real `evolve` call would resume from right now.
2. Ran ONE fresh real generation's worth of work exactly as
   `loop.evolve.EvolutionRun.generation()` does internally (real
   `Researcher.propose` with `seed=None`, real `Evaluator.evaluate`, real
   market data, `n_blind=14`), stopping short of the `accepts()`/holdout loop
   so the batch could be inspected — same isolation as the 21:52 UTC run,
   this time a genuinely new non-deterministic draw (14 fresh proposals, 196
   cumulative against v3).
3. Computed the champion's fold-aggregate fitness at 7 as-of shifts (0-6 days
   back), same method as `fold-date-sensitivity --shift 7`: 1.054 (today) down
   to -1.652 (yesterday) up to 1.396 (6 days back) — spread 3.05, same
   order of magnitude as every prior measurement of this swing.
4. For the top-3 ranked finite candidates, re-ran `constitution.accepts()`
   at all 7 shifts, swapping only `champion_score` (challenger's own real
   fold-aggregate fitness, both gate-stats dicts, `n_candidates`,
   `complexity_delta` held fixed) — same isolation as 21:52 UTC.
5. **New this session**: for every candidate that flipped, took its first
   accept-verdict shift, rebuilt the shifted "as-of" market data window the
   same way `fold-date-sensitivity` does, built a fresh `Evaluator` on it,
   and called the real `Evaluator.holdout_check()` for both champion and
   challenger on that shifted window — the actual sealed-holdout check a
   real `generation()` would run if this candidate reached that gate on that
   day. Judged with the real `constitution.holdout_accepts()`, `n_draws =
   init_holdout_draws + 1` (13 + 1 = 14, matching what a real call would
   count as the first holdout draw this generation).

```
python3 <scratch>/flip_holdout_check.py
```

## Result

**Open item 1 — reproduces, with different specific candidates.** 2 of 3
top-ranked candidates flip again (same 2-of-3 ratio as the 21:52 UTC draw,
though that's two data points, not a law): both ACCEPT only at shift 1
(as-of 2026-08-26, champion fold-aggregate -1.652 — the same anomalous low
day the 21:52 UTC run's shift-1 also landed on) and reject at every other
shift. The third candidate hard-fails a gate on every shift, same as last
time — confirms the earlier reading that only candidates sitting close to
the champion's own swing range are shift-sensitive.

**Open item 2 — no, neither flipped candidate passes the sealed holdout on
its accept-verdict day.** Both fail decisively:

- Candidate #1 (8-gene tune, `regime_ma`/`min_trend`/`rsi_buy_below`/...):
  holdout fitness challenger -0.259 vs champion 0.176 + margin 4.595 (14
  cumulative draws) — rejected, not close.
- Candidate #2 (8-gene tune, `regime_ma`/`max_dd_from_high`/...): holdout
  fitness challenger -0.373 vs champion 0.176 + margin 4.595 — rejected,
  also not close.

## Reading

This sharpens the framing question further, and this time in the reassuring
direction: the fold-aggregate gate's date-sensitivity is real and
reproduces on a second independent draw, but for these two candidates the
sealed holdout's own accumulated-draws multiple-testing margin (`HOLDOUT_SIGMA
= 2.0`, 14 draws deep against this specific holdout window) is currently
large enough (margin 4.595) to reject both regardless of which day let them
through the first gate. The two gates are not independent in the way that
matters here — a candidate that only clears the fold-aggregate gate because
of a lucky champion-score day still has to clear a second, much stricter
gate on real out-of-sample data, and neither did.

Important scope limits, same caveats as 21:52 UTC plus one new one:

- One more draw is still not a proof the holdout always backstops this —
  both flip candidates happened to be genuinely weak on the holdout window
  (both hard-negative), not close calls. A future flip candidate that is
  merely mediocre rather than bad on the holdout (say, holdout fitness
  0.0-0.15, close to the champion's 0.176) would test the backstop's actual
  margin rather than its direction. Not observed yet.
- The holdout margin (4.595, driven by 14 cumulative draws) is specifically
  large right now because this lineage has spent many draws against this
  holdout already — the backstop's strength is itself a function of
  accumulated search pressure, not a fixed property of the gate design. A
  younger lineage with fewer holdout draws would have a smaller margin here
  and less protection from exactly this mechanism.
- Still not run: a case where a flip candidate's holdout fitness is itself
  close to the champion's, which is the actual stress test of whether the
  holdout gate reliably backstops the fold-aggregate gate's date-sensitivity
  or just happened to in the two candidates checked so far.

## Verified safe

- No code changed in the repo — the script lives only in the session
  scratch directory, never touches `evotrader_bundle.py`, `loop/`,
  `constitution/`, `core/`, or any committed file. Never called
  `Genome.promote()` or `acct.save()` at any point (stopped before
  `generation()`'s own accepts()/holdout loop, built parallel gate/holdout
  checks by hand instead of calling the real loop). No test suite run
  needed (same precedent as prior no-code-change diagnostic sessions).
- `live_state.json` untouched: md5 `1add861014e44aa69e814491cbd22e00`
  before and after, still reflects tick 13 from the 00:20 UTC daily run.
- `evotrader.manifest` md5 unchanged: `0bf3a7d9411ee692d0a9f152a7533803`.
- `tools/edit_bundle_module.py sync --check`: bundle already matches real
  files, no changes.
- `git status --short` clean before and after this note.
- Today's bar already processed before this session started (`tick` not run
  this session, no double-trade).
- No genome promotion — no README `## Status` update needed.

## Next, if this thread stays worth pursuing

- The stress-test case: keep drawing generations (or deliberately search for
  one) until a flip candidate's holdout fitness lands close to the
  champion's, to see whether the holdout margin still holds it back or
  whether a close call actually gets through.
- Whether smoothing the champion's fold-aggregate baseline across several
  trailing as-of dates would still be worth doing given the holdout backstop
  found here — the case for it is weaker now that two draws show the second
  gate catching what the first gate's date-sensitivity would have let
  through, but not zero, since the backstop's margin is itself lineage-age
  dependent (see above).
- The day-1-allocation-redesign question (proportional/ranked instead of
  greedy-first-come) and the window-5 `anatomy` post-mortem, both still open
  from the 09:50 UTC (2026-08-26) entry, untouched by this thread.
