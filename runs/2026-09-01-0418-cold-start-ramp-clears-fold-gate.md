# A cold-start position-size ramp clears the fold-2 hard-fail the 01:14 UTC session found — shipped as a genuine gene, not a diagnostic

**3-hourly check, ~01:14-04:18 UTC.** Direct follow-up to the 01:14 UTC
session's own flagged next step: *"does a longer warmup or a smaller initial
position size in the first N bars of a fold fix [the cold-start drawdown
artifact]?"* Traced the `warmup` argument to `run_backtest()` first and ruled
it out mechanically — it only raises `start = max(warmup, int(n*start_frac))`,
which does nothing for fold 2 (`[0.283, 0.567]`) since `int(n*0.283)` is
already far past any reasonable warmup value, and indicators already read
back past the fold boundary regardless (`ReplayWindow._col` slices the full,
un-fold-restricted array). The actual cold start is the broker: every
`run_backtest()` call opens a fresh `PaperBroker` with empty positions and
full cash, so a fold that starts mid-crash gets hit at full risk with none of
the de-risking a seasoned position would already have.

## What was built

Two new `risk_judge` genes in `core/genome.py`: `cold_start_ramp_bars`
(default `0`) and `cold_start_ramp_start_scale` (default `1.0`) — a true
no-op pair, verified by inspection (`ramp_scale` stays `1.0` whenever
`ramp_bars <= 0`) and by test. Wired into `RiskJudge.rule()`
(`agents/judges.py`): a per-instance bar counter (reset to 0 in `__init__`,
incremented once per `rule()` call, so it tracks bars since *this broker's*
cold start — a fresh fold, a fresh live account, or a fresh shadow run all
start at 0 again) scales new buy `Order.quote_amount` linearly from
`start_scale`x at bar 0 up to `1.0`x at `ramp_bars`, then stays at `1.0`x
forever after. Added to `agents.researcher.GENE_SPACE` too
(`cold_start_ramp_bars: (0, 300, int)`, `cold_start_ramp_start_scale: (0.0,
1.0, float)`) so real evolution search can tune it, not just a hand-picked
value.

**One real correctness bug caught before shipping**: the first implementation
scaled `amount` *before* deducting it from `cash_avail`/counting it against
`open_count`. That let the ramp free up cash for *more*, still-full-size-ish
positions to fill the same bar instead of actually reducing total exposure —
verified this washed out almost the entire effect (fold 2 max_dd only moved
-44.1%→-43.8%, against a direct monkeypatch diagnostic that had shown
-44.1%→-34.6% for the identical parameters). Fixed by computing room/slot
accounting against the *unramped* would-be amount and only scaling the
actually-recorded order — same selection and prioritization as an unramped
bar, just smaller size on what gets filled. After the fix, the real
gene-based path reproduces the monkeypatch diagnostic's numbers exactly. New
`tests/test_cold_start_ramp.py` (5 tests) locks in both the no-op default and
this specific semantics (room accounting uses the full amount) so this
doesn't silently regress.

## Result on the 01:14 UTC session's dead-end genome

Applied to `consv1 + trailing_stop -0.06` (the x6-scaled 4h seed genome that
session found dead-on-arrival) via new `tools/shadow_4h_x6_seed.py`
`build_consv_trailing_ramp_seed()` (`ramp_bars=120`, `start_scale=0.10`,
picked from a small hand sweep — 30/60 bars barely moved the number, 120
bars was the first to clear the gate, 180 bars was slightly worse than 120).
Measured with the exact real functions `EvolutionRun.generation()` calls
before `accepts()`'s hard-fail check (`Evaluator.evaluate()` +
`dd_corrected_stats()`), not a continuous-replay proxy:

| | fold 0 max_dd | fold 1 max_dd | fold 2 max_dd | agg. fitness | dd_corrected max_dd | holdout fitness |
|---|---|---|---|---|---|---|
| baseline (no ramp) | -30.5% | **-44.1%** (hard-fail) | -26.6% | -2.481 | -44.1% | -0.262 |
| +cold_start_ramp 120/0.10 | -30.5% (unchanged) | **-34.6%** (clears) | -25.7% | **+0.467** | -34.6% | -0.288 |

Fold 0 is byte-identical — the ramp only bites during a genuine cold start
that coincides with a hard move, which fold 0's own first-120-bars window
apparently doesn't hit; this isn't a blanket risk-off, it's specifically a
cold-start guard. Fold 1's sortino also improves (3.12→4.12) alongside the
drawdown fix — this isn't a naive "just trade less" result trading return for
safety, trade count actually rises slightly (636→663). Holdout is
essentially unchanged (still `beat_benchmark=True`) since the sealed holdout
window isn't a fresh cold start in this construction (same continuous
replay), so the ramp bites for at most its first `ramp_bars` bars there too
and mostly passes through.

**This is the first genome in this whole 4h-shadow thread (since 2026-08-16)
to clear `MAX_DD_HARD_FAIL` on the actual fold-based gate the real pipeline
uses**, not just a continuous full-history replay — the 22:07 UTC session's
"-32.7% max_dd" headline never survived contact with that gate; this one
does, checked with the identical functions.

## What this doesn't yet establish

Not run through a full `accepts()` promotion decision against a real prior
champion (there isn't one for this seed lineage — every session here treats
the seed fresh). Kicked off one real `EvolutionRun.generation()` (seed 9001)
with this genome as champion to see whether fresh search finds something
even better around it. **Result (ran to completion after this note was
first drafted, ~45min wall clock — the first attempt hit its own 590s
harness timeout with nothing captured due to output buffering through
`tail`, not a real failure): 34 fresh blind proposals, best fitness 0.611
vs. champion's 0.467, none cleared the acceptance bar — champion (the
cold-start-ramp genome) held.** This isn't a promotion (there is still no
sealed-holdout comparison here, since nothing beat the champion's
fold-aggregate fitness by enough to reach that gate at all) but it is a real
stability signal: the genome isn't obviously beaten by a generation of
nearby blind perturbations, which the 01:14 UTC session's genome never got
the chance to show (it never got as far as an accepted generation because it
was already failing the hard-fail gate outright). Also not tried: letting
the Researcher search `cold_start_ramp_bars`/`cold_start_ramp_start_scale`
themselves now that they're in `GENE_SPACE`, rather than the hand-picked
120/0.10 — a real search might find a materially better point. This
session's script only captured the generation's summary (champion held, best
challenger fitness), not the per-candidate patch list, so whether any of the
34 proposals actually touched either new gene is unknown — a follow-up
re-run that also prints `record["top"]` would answer that for free.

`git status` clean before commit, `live_state.json` md5 unchanged
throughout (`1b5e230bb4e7440ed8fd7778425f8ea9`), constitution checksum
unchanged (`8b74865634b1db07` — neither `core/portfolio.py` nor
`constitution/__init__.py` touched), `python3 -m pytest -q` 262/262 (up from
255, +2 builder tests +5 ramp tests), `tools/edit_bundle_module.py sync`
run and confirmed no drift after. Genome still v3 (1d) live, untouched.
