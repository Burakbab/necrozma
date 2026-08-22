# 2026-08-22 06:00 UTC — weekend all-hands: fixing the maxDD gate's fold-boundary blind spot

## Context

This session picked up the clearest, highest-priority open item in
`AGENTS.md`'s Current state: the previous session's `fold-dd-blindspot`
diagnostic (`runs/2026-08-22-0356-fold-dd-blindspot.md`) had found a real,
structural blind spot in `MAX_DD_HARD_FAIL` — the drawdown safety gate that is
supposed to hard-fail any genome whose historical drawdown exceeds 40% — and
explicitly deferred the fix as needing "a real design pass" and "more runway
than a 3-hour slot should gamble on." A weekend session has that runway, so
this is that design pass, plus the implementation, plus verification.

Also cleaned up house at the start: local `main` was in detached HEAD 50
commits behind a force-updated `origin/main` (the same recurring container-seed
artifact prior sessions have logged — the two commits unique to local `main`
were pre-restart upload artifacts superseded by the real history, not lost
work). Reset to `origin/main` per the run protocol, no work lost.

## The mechanism, restated

`Evaluator._merge` (`loop.evolve.py`) is what builds the merged stats
`constitution.accepts()`/`fitness()` actually gate promotion on. It set:

```python
"max_dd": float(np.min([x.get("max_dd", 0) for x in s])),
```

— the worst of the three walk-forward folds' own **independently** backtested
local peak-to-troughs. Each fold's `run_backtest` call resets NAV and position
state fresh at that fold's own boundary. A drawdown that starts near the end of
one fold and bottoms out early in the next is invisible to *either* fold's own
local number, and therefore invisible to the merged number the gate checks —
structurally, not as a bug in the arithmetic. `fold-dd-blindspot` proved this
directly on the live champion: v3's gate-visible fold-merged max_dd is -34.1%,
but one continuous, unbroken replay over the identical search span already
reads -46.5%, past the 40% threshold the gate is supposed to enforce.

## Design choices, and why

Three things had to be decided before writing any code.

**1. What should the "true" merged max_dd be?** The obvious fix — replace the
fold-merged number with one continuous replay over the fold-covered span — is
also the simplest, and it matches what the live system actually does (it never
resets state at arbitrary calendar boundaries; it runs continuously). The
alternative, keeping per-fold independence intact and inventing some other
combination rule, doesn't have an obviously correct form and risks
double-counting or under-counting a drawdown that's partially visible to
multiple folds. Went with continuous replay, but **combined via `min()` with
the existing fold-merged number**, not a straight replacement — this
guarantees the fix can only tighten the gate, never loosen it (same standing
direction as every prior `AMENDMENTS.md` row), and it's robust to the
continuous run happening to read *better* than a fold-local worst case (not
guaranteed to always read worse, since portfolio state at a continuous run's
starting point differs from each fold's own fresh-capital start).

**2. Where should the correction apply — every candidate, or just the ones
that reach a real promotion decision?** `Evaluator.evaluate()` is called for
every one of ~14 blind candidates per generation, used both to rank candidates
for search direction and to build the merged stats `accepts()` reads. Adding
one continuous backtest to *every* `evaluate()` call would raise per-candidate
search cost by roughly a third, for a large volume of candidates that never
get near a promotion decision anyway (only the top 3 fold-ranked candidates
per generation ever reach `accepts()`). The blind spot only actually matters
where a real accept/reject decision happens — `EvolutionRun.generation()`'s
`accepts()` call for those top-3 candidates. So the fix lives there instead:
`Evaluator.continuous_max_dd()` and `loop.evolve.dd_corrected_stats()` are
called only for the up-to-3 candidates that reach that gate each generation
(and the champion's check is cached once per generation, since the champion
doesn't change between candidates within it). `Evaluator.evaluate()` itself,
and every diagnostic built on it (`fold-scheme`, `rolling-folds`,
`regime-folds`, `fold-dd-blindspot` itself), is completely untouched — those
diagnostics exist specifically to measure fold-windowing effects, and folding
a continuous number into their own numbers would have confused what they
measure rather than clarified it.

**3. What to do about the live champion v3, which already fails the corrected
gate retroactively?** Decided **not** to force a demotion or rollback this
session. Reasons: (a) this is a paper account with no real money, explicitly
by design (`AGENTS.md`'s "No credentials, anywhere" section) — the urgency is
about research integrity, not real financial exposure; (b) there is no
rollback/demotion mechanism in this codebase at all yet, and building one
well (what does a demoted champion fall back to — v2? a fresh search from
seed?) is its own design question, not a five-minute addition bolted onto a
gate fix; (c) forcing that decision without more deliberation risks a rushed,
under-designed rollback path. Instead: documented the fact prominently in
`AGENTS.md`'s Current state and, since it's a real risk-relevant fact about a
publicly visible live system, added a transparency note to `README.md`'s
`## Status` section even though no genome version changed (the mandatory
trigger for that section is a promotion, but the spirit of keeping it honest
applies here too).

## Implementation

`loop.evolve.py`, via `tools/edit_bundle_module.py` (extract/edit/reinsert,
never hand-touching the bundle's escaped-string `_SRC` lines):

- New `Evaluator.continuous_max_dd(g, folds=None)`: runs one `run_backtest`
  over `[folds[0][0], folds[-1][1]]` (defaulting to `self.folds()`, i.e.
  `[0, search_end]` for the standard disjoint split — deliberately never
  extends into the sealed holdout, so search still never touches it). Returns
  `None`, not `0.0`, on an empty fold list or a backtest error, so a caller
  can't mistake "unknown" for "no drawdown."
- New `loop.evolve.dd_corrected_stats(evaluator, g, stats, folds=None)`: a
  copy of `stats` with `max_dd` replaced by
  `min(stats["max_dd"], continuous_max_dd)` when the continuous check
  succeeds, unchanged otherwise. Pure, small, independently testable without
  touching `EvolutionRun`.
- `EvolutionRun.generation()`: right before the `accepts()` call for each of
  the top-3 fold-ranked candidates, both champion and challenger stats are run
  through `dd_corrected_stats` first. Champion's continuous check is computed
  once (lazily, only if at least one candidate has finite fitness) and reused
  across the loop.

No engine or constitution-file change — `constitution.py`'s `accepts()`/
`fitness()` are unchanged; they just now receive a stats dict whose `max_dd`
field means something more honest. `loop.evolve` isn't part of the
checksummed surface (`constitution.checksum()` only hashes `constitution` and
`core.portfolio`), same as every prior fold-scheme/margin-curve/regime-folds
diagnostic that has touched this module — but this is still a genuine
constitution-level *policy* change (what the acceptance gates actually
measure), so it gets an `AMENDMENTS.md` row regardless of which file houses
the mechanism, per this repo's own standing rule.

## Verification

**Unit tests.** New `tests/test_continuous_max_dd.py`, 8 tests, mocking
`run_backtest` the same way `test_fitness_decomposition.py`'s
`test_matches_evaluator_evaluate_on_synthetic_data` already does:
`continuous_max_dd` calls the backtest over the right span (default folds,
explicit folds, empty folds, backtest error); `dd_corrected_stats` picks the
worse number, never loosens when the continuous number is better, falls back
cleanly on a backtest error, and doesn't touch unrelated stats fields or
mutate its input dict in place. Full suite: 192 passed, up from 184.

**Real-data check.** Loaded the live champion's actual market universe
(`market.load_universe`) and ran `Evaluator.evaluate` +
`dd_corrected_stats` directly against it:

```
fold-merged max_dd (old gate-visible number): -0.3407278955043227
dd-corrected max_dd (new gate-visible number): -0.46479365658391314
MAX_DD_HARD_FAIL: 0.4
champion now hard-fails its own corrected gate: True
```

Reproduces `fold-dd-blindspot`'s own numbers exactly (-34.1% -> -46.5%),
confirming the wiring is correct, not just internally consistent with mocks.

**Live shadow-evolve integration check.** 3 generations of `evolve` against an
isolated scratch copy of `live_state.json` (`EVO_STATE=<scratch copy>`, same
discipline as every prior shadow-evolve session — the real file's md5 was
identical before and after: `3f71d6ab111ecd646eda9e0e595a9970`). This is the
first time the new gate ran inside the real `EvolutionRun.generation()` path,
not a unit test:

- Champion held all 3 generations (no promotion, shadow or otherwise).
- Generation 3's top-ranked candidate (fold-aggregate fitness 1.638) cleared
  both the selection-fitness margin (champion 1.126 + required margin 0.263)
  **and** the new dd-corrected `accepts()` check, reaching the sealed
  holdout, where it was correctly rejected there instead (challenger `-2.237`
  vs champion `-0.178` + margin `4.595`, 14 cumulative draws). This is the
  useful negative case: the new gate does not just block everything — a
  genuinely viable candidate still passes it and gets a fair shot at the next
  gate.
- Separately, one generation-1 candidate was rejected with `"challenger
  failed a hard gate (too few trades, too short, or drawdown > 40%)"` — the
  exact `f_chal == -inf` path this fix touches — confirming the corrected
  hard-fail branch fires for real inside a live run, not just inside a mock.

**Standard safety checks, all clean:** `py_compile evotrader_bundle.py`;
`python3 tools/edit_bundle_module.py verify` (round-trip byte-identical);
`git diff --stat` on the fix commit shows a pure single-line
`_SRC['loop.evolve']` change, no other module touched; `live_state.json` md5
identical throughout (`3f71d6ab111ecd646eda9e0e595a9970`);
`evotrader.manifest` md5 identical (`0bf3a7d9411ee692d0a9f152a7533803`);
`constitution verified 8b74865634b1db07` unchanged on every invocation;
today's 2026-08-22 daily bar already confirmed processed by the 00:20 UTC
run before this session started (`tick` not run this session, no
double-trade); `state/lineage.jsonl` picked up the shadow run's records (that
path isn't `EVO_STATE`-scoped — it's a known, gitignored, rebuildable side
effect, not committed).

## What's still open

The demotion/rollback question is real and unresolved, flagged clearly in
both `AGENTS.md`'s Current state and `README.md`'s `## Status` section rather
than acted on unilaterally: champion v3's own corrected max_dd (-46.5%)
already exceeds `MAX_DD_HARD_FAIL`, `fitness(champion)` now reads `-inf`
inside every future `accepts()` call while v3 remains champion (traced
through and confirmed harmless to the checks that matter — it only affects
the merged-fitness-regression check, which becomes vacuously true, never a
promotion blocker), but nothing currently forces a champion to prove it can
still clear its own gate once that gate gets more honest. That is a
deliberate scope boundary for this session, not an oversight — building a
rollback mechanism well needs its own design pass (what does a demoted
champion fall back to?), and rushing one inside a gate-correctness fix would
have been the wrong trade.

Whoever next evaluates a real (non-shadow) promotion candidate should note in
the run record whether the corrected gate actually changed a promotion
outcome it wouldn't have under the old fold-merged-only check — this
session's shadow run is the first real exercise of the new code path, but 3
generations against a single champion is a small sample.

## Push notification

Not sent this session — the previous two sessions already surfaced this
finding's severity to the user (the blind spot's discovery and its
confirmation both triggered notifications). This session closes the loop
that those left open ("fixing it... was deliberately not attempted this
run... needs a real design pass") rather than surfacing new severity, so a
routine end-of-session summary is enough.
