# Weekend all-hands, 2026-10-03 ~06:00-07:08 UTC

## Context going in

Synced cleanly from `main` (`git checkout main` + `tools/git_sync.py`, no
divergence). `requirements.txt` installed. Skimmed recent `runs/` notes: the
last several days of 3-hourly checks have been an unbroken run of "15 more
`evolve` generations against live v3, no promotion" — cumulative candidates
tried against v3 at session start: 45,812 (`researcher_memory.tested`),
stagnation/boldness 3,307. `review-hard-calls` 0 pending. Items 6
(equities/FX data source) and 13 (`HOLDOUT_SIGMA`'s cumulative margin) are
both still open owner decisions, restated unchanged in every recent daily
discussion — nothing new to raise there this session.

`AGENTS.md` was 238,544 bytes at session start, comfortably under the 256KB
rotation threshold — no archival needed this cycle.

## Decision: what to spend the extra weekend time budget on

Weekday 3-hourly checks have been running the same 15-generation `evolve`
batch every cycle for weeks with no promotion, which is the correct default
when nothing else is queued but is genuinely low-signal use of a bigger
slot: item 13's own finding (restated in every discussion since
2026-09-20) is that `HOLDOUT_SIGMA`'s never-resetting cumulative
multiple-testing correction, not search quality or boldness, is now the
dominant force keeping v3 in place — the required margin rises with
cumulative draw count alone, so more generations against the same
mechanism was unlikely to be the highest-value use of a long session.
Decided to split the time: kick off a bigger (40-generation, vs. the
weekday default of 15) `evolve` batch in the background for real search
volume, and spend the session's own attention on a genuinely new
structural question — item 5 (short selling)'s still-open "is there a
usable short-timing signal at all" thread, which the 2026-09-26/09-27
weekend sessions had sharpened but not closed.

## Evolve batch (background, ~61 minutes wall clock)

`tools/background_runner.py start`/`wait` against `python3
evotrader_bundle.py evolve 40`, run concurrently with this session's own
diagnostic work (which visibly slowed it in the middle third — generation
13 took unusually long while two real-data `short-headroom` backtests and
a full `pytest` pass were running at the same time; CPU contention, not a
hang, confirmed via `ps` showing the process alive and at ~92% CPU
throughout).

No promotion. Champion's fold-aggregate fitness held flat at 1.831 across
all 40 generations (992 trades, 40% win, 1% stops, 3 halts, unchanged
throughout). Best-of-generation fold-fitness ranged roughly 1.27-2.89 —
several individual generations' best candidate nominally exceeded
champion's own 1.831 (e.g. generation 36's 1.832, generation 12's 1.833)
but never by enough to clear the cumulative multiple-testing margin, so
"champion holds" every time. Cumulative candidates tried against v3 rose
45,812 → 46,356 (`researcher_memory.tested`), stagnation/boldness counter
3,307 → 3,347.

`holdout-pressure` re-checked before and after (read-only): margin and draw
count both **unchanged** at 7.461 / draw 1051 — none of this batch's 544
new candidates (14/gen × ~39 full generations) cleared even the
fold-aggregate gate, let alone reached a sealed-holdout check. This is
itself a data point for item 13: at the current margin, a 40-generation
batch — nearly 3x a normal weekday slot — produced zero fold-gate clears,
not just zero promotions.

Verified before committing the state change:
- `python3 -m pytest -q`: 457/457 both before (baseline, 441 + this
  session's 16 new tests) and after the evolve batch
- Top-level key diff of `live_state.json` against a pre-batch snapshot
  (checked directly in Python): only `updated`/`researcher_memory`/
  `lineage` changed; genome, broker, journal, hard_call_reviews
  byte-identical
- `lineage` length unchanged at 202 (bounded ring buffer, no new promotion
  attempt recorded)
- `tools/edit_bundle_module.py sync --check` clean
- Dashboard rebuilt with `EVO_STATE` set (`index.html` now shows 46,356
  challenger ideas tried)

Genome still v3 (1d) live, untouched.

## Item 5 (short selling): two new diagnostics, one real result, one correction

The 2026-09-27 weekend session measured the only short-timing signal that
existed at the time — `agents.analyst.Analyst._regime`, the basket-wide,
anchor-only classifier `RiskJudge.rule`'s `regime_scale` gene already uses
to gate *long* entries — and found it unusable for shorts: its noisy `bear`
leg loses money on the exact window it's meant to catch (false positives
from ordinary pullbacks inside a still-intact uptrend), and its strict
`crisis` leg is safe but too rare to matter (captured only 8% of the
theoretical edge). That session's writeup explicitly said a real
short-timing signal would need to be purpose-built, not a reuse of the
long-entry gate. This session built one and measured it.

### `benchmark_trend_break_short` — per-symbol, price-only trend breakdown

New `loop.engine.benchmark_trend_break_short` (9 tests,
`tests/test_trend_break_short.py`) opens/covers each symbol
**independently** off its own `SMA(fast)/SMA(slow) - 1` trend ratio — enter
below -5%, cover above -2% (hysteresis, not one threshold, so a partial
recovery doesn't immediately re-trigger) — instead of one basket-wide
switch. Deliberately genome-independent: fixed price-only thresholds, no
`Genome`/`Analyst`/`RiskJudge` involvement. Wired into `short-headroom
--trend-break`.

Real 4-year result against the live champion's universe:

| window | buy&hold | permanent short | trend-break (real cost) |
|---|---|---|---|
| fold 1 (bull) | +92.0% | -110.7% | **-37.1%** |
| fold 2 (bull) | +140.3% | -181.0% | **-46.5%** |
| fold 3 (bear) | -31.8% | +23.6% (74% captured) | **+31.6% (99% captured)** |
| holdout (bull) | +54.2% | -57.2% | **-19.3%** |

Reading: a real improvement in risk shape over both alternatives tried so
far — far milder bull-market losses than a permanent short, and it
captures almost the entire theoretical bear-window edge (99% vs. the
regime signal's best showing of 8%). But it is still net-negative in 3 of
the champion's 4 real windows, because any individual symbol can have a
sharp enough pullback inside a broader bull run to false-trigger a short
that then eats losses when the uptrend resumes — the same false-positive
mechanism that breaks trend-following *entries* on the long side, mirrored
to shorts.

### `benchmark_combined_short` — AND-gated, and it backfires

The natural next question: does requiring *both* signals (trend-break AND
regime bear/crisis) combine their strengths? New
`loop.engine.benchmark_combined_short` (7 tests,
`tests/test_combined_short.py`) opens a short only when both agree, covers
the moment either disagrees. Wired into `short-headroom --combined`.
Measured rather than assumed — and the hypothesis was wrong:

| window | trend-break alone | combined |
|---|---|---|
| fold 1 (bull) | -37.1% | **-17.1%** (better) |
| fold 2 (bull) | -46.5% | -49.1% (~tied) |
| fold 3 (bear) | **+31.6% (99% captured)** | **+0.3% (1% captured)** |
| holdout (bull) | -19.3% | **-10.6%** (better) |

Bull-market losses shrank as hoped, but fold 3 — the one window either
signal has ever actually made money in — nearly collapsed. Checked why
directly: flips rose 245 → 293 and avg concurrent short fell 14.02 → 12.46
in that window specifically. Covering the instant *either* signal
disagrees means the regime classifier's already-documented whipsaw (same
"easily-tripped OR... reads as bear during ordinary pullbacks" from
2026-09-27) now also forces premature covers out of a position trend-break
alone would have correctly held through the real decline.

**Conclusion for item 5, recorded in `AGENTS.md`**: "AND to open,
OR-sensitive to cover" does not cleanly combine two signals' strengths — it
inherits the weaker signal's exit-timing weakness on the cover side while
only partially gaining its quiet periods on the entry side. A real
combination would need an asymmetric rule (gate opening on both, let
trend-break alone govern covering) — flagged as the next thing to try, not
built in the same session as the measurement that motivated it, matching
this item's established measure-then-report discipline. Both diagnostics
are read-only throughout: no genome mutation, no `RiskJudge`/
`SuperiorJudge` code path, no `live_state.json` touch. Neither result
settles "whether/how to let the Researcher propose shorts" — they sharpen
the open question with real numbers instead of resolving it.

## Verification discipline for the code changes

- `python3 -m pytest -q`: 441 (baseline) → 450 (after trend-break) → 457
  (after combined), green at each step
- `tools/edit_bundle_module.py sync` run after each `loop/engine.py` edit,
  `verify` and `sync --check` both clean throughout
- `python3 -c "import py_compile; py_compile.compile('evotrader_bundle.py', doraise=True)"`
  clean after every CLI-section edit
- Constitution checksum unchanged (`726dfa4bac85891a`) throughout — neither
  change touches a `_PROTECTED` file
- Three commits, pushed individually as the work landed rather than
  hoarded: the trend-break diagnostic, the combined diagnostic +
  AGENTS.md writeup, and a one-line docstring fix the stop-hook caught
  uncommitted

## State at end of session

- Genome: v3 (1d), unchanged, live
- `researcher_memory.tested`: 46,356 (was 45,812)
- stagnation/boldness: 3,347 (was 3,307)
- `holdout-pressure` margin: 7.461, draw 1051 (unchanged by this session's
  evolve batch — no new fold-gate clears)
- `review-hard-calls`: 0 pending (unchanged)
- Full test suite: 457/457
- Dashboard rebuilt (`index.html`, 46,356 challenger ideas shown)
- Items 6 and 13: still open owner decisions, nothing new this session

## Next steps for whoever picks this up

1. If item 5 is revisited: the asymmetric-rule variant flagged above (gate
   opening on both signals, let trend-break alone govern covering) is the
   concretely scoped next measurement — untested, not yet built.
2. Items 6/13 remain blocked on owner risk-appetite decisions; per item
   13's own instruction, do not try to resolve it with more diagnostics.
3. `AGENTS.md` is ~243KB after this session's additions — comfortably
   under the 256KB rotation threshold, but a weekday session should check
   freshly before adding much more.
