# 3-hourly check — 2026-08-28 ~09:45 UTC — `guardian-gene-test`

## State check

- Cloud clone started detached at a stale shallow snapshot of `origin/main`
  (same expected shallow-clone-window artifact the 00:56/04:04/06:56/09:00
  UTC entries already named this cycle, confirmed not a force-push).
  `git checkout main && git reset --hard origin/main` realigned to
  `ef5fd8e`, "Daily discussion note: 2026-08-28 09:00 UTC check-in".
- `live_state.json` `updated`: `2026-08-28T00:28:04+00:00` (today's 00:20
  UTC daily-trading run). No new bar since — confirmed via the timestamp
  and today's `runs/` notes (`0020-daily-trading`, `0056`, `0404`, `0656`,
  `0900-daily-discussion`, this one). No `tick` run this session, no
  double-trade risk.

## What shipped

New read-only diagnostic `guardian-gene-test [--also-version N]` — the
fold-3-mechanism fix `fold3-anatomy`'s own trailing note (04:04 UTC) named
as the real next step, and the complementary test `exit-gene-test`
explicitly did not run.

**Why this, not another exit-gene variant**: `fold3-anatomy` (04:04 UTC)
found fold 3's worst trades, for both champion v3 and `exit-gene-test`'s
"no discretionary exit" candidate, exit via Guardian's *mechanical*
stop-loss, trailing stop, or time stop (`agents/trader.py`'s
`Guardian.forced_exits`) — never via any discretionary consult.
`exit-gene-test` (00:56/06:56 UTC) already confirmed patching the
*discretionary* exit can't touch fold 3 (only ~1pt of depth, -46.8% →
-45.8%). This diagnostic instead builds real `Genome.child()` patches to
the actual genes that fire in fold 3 — `risk.stop_loss`, `risk.trailing_stop`,
`risk.max_bars_held` — and runs them through the exact same acceptance-gate
machinery `exit-gene-test` used: `Evaluator.evaluate()`, `dd_corrected_stats()`
before `constitution.accepts()`, then (only for whichever clears that gate)
`constitution.holdout_accepts()` against the sealed holdout, using the
champion's real cumulative `researcher_memory` counts for the
multiple-testing margin. Same `--also-version N` convention and the same
"optimistic upper bound" caveat for a reconstructed past champion
(`researcher_memory` only ever holds counts for whichever version is
champion *right now*, so v1/v2 always take the `n_tested_before=0` branch).

Four variants per champion, each gene halved in magnitude (clamped to
`agents.researcher.GENE_SPACE`'s own bounds) *relative* to that champion's
current value — not a fixed absolute number — so the same code fairly
tests a "tighter" hypothesis against v1/v2/v3 despite their current Guardian
genes differing substantially (v3: stop_loss -0.336, trailing_stop -0.199,
max_bars_held 15 vs the v1/v2 seed values -0.12/-0.15/60):
`tighter stop-loss (halved)`, `tighter trailing stop (halved)`,
`shorter time stop (halved)`, `combined tighter exits`.

## Finding — a real, different result from every exit-gene variant so far

Ran against all three real champions (v3 live, v1 and v2 reconstructed).
**11 of 12 variant/champion combinations clear the fold-aggregate
acceptance gate** — the same gate every `exit-gene-test` candidate on v1/v3
hard-failed immediately. Only one combination (v3 + "tighter trailing stop"
alone) still hard-fails (-43.2%, still above the -40% `MAX_DD_HARD_FAIL`
line). This is the first time tightening a *mechanical* Guardian gene, not
a discretionary consult gene, has moved the gate-visible drawdown enough to
clear it at all:

| champion | variant | gate max_dd (baseline in parens) | fold gate | holdout |
|---|---|---|---|---|
| v3 | tighter stop-loss | -37.7% (-46.8%) | OK | failed (0.476 vs required) |
| v3 | tighter trailing stop | -43.2% (-46.8%) | **NO** | not reached |
| v3 | shorter time stop | -34.6% (-46.8%) | OK | failed (0.174) |
| v3 | combined | -38.3% (-46.8%) | OK | failed (-0.676) |
| v1 | tighter stop-loss | -34.8% (-45.3%) | OK | failed (0.462) |
| v1 | tighter trailing stop | -29.5% (-45.3%) | OK | failed (0.407) |
| v1 | shorter time stop | -38.0% (-45.3%) | OK | failed (0.586) |
| v1 | combined | -31.9% (-45.3%) | OK | failed (-0.106) |
| v2 | tighter stop-loss | -33.9% (-41.8%) | OK | failed (0.100) |
| v2 | tighter trailing stop | -30.6% (-41.8%) | OK | failed (0.171) |
| v2 | shorter time stop | -38.0% (-41.8%) | OK | failed (0.666) |
| v2 | combined | -35.7% (-41.8%) | OK | failed (-0.215) |

Every single one still fails the sealed holdout — several by a wide margin
(e.g. v3 "shorter time stop" holdout fitness 0.174 vs whatever
`holdout_accepts()` required against champion v3's real holdout fitness
0.625 plus the multiple-testing margin). **Net**: fold3-anatomy's diagnosis
was right — Guardian's own mechanical thresholds are the real lever for
fold 3's drawdown, not any consult's discretionary exit — and unlike every
exit-gene variant tried so far, tightening them for real moves the
gate-visible number enough to clear the fold-aggregate gate on 3 champions
at once. But clearing the fold gate was never the hard part historically
(`holdout-pressure`'s 9/9 finding, 2026-08-18): the sealed holdout is. This
is the same "clears fold gate, loses at holdout" shape `exit-gene-test`
already found once for v2's exit-gene candidate — now reproduced 11 times
over with a structurally different, more targeted patch.

## Verified safe

- `py_compile evotrader_bundle.py` clean.
- `tools/edit_bundle_module.py sync --check` clean — CLI-only code, no
  `_SRC` module touched.
- Full test suite: 235 passed (matches baseline, no new pure function so no
  new test file — this diagnostic composes only already-tested
  `Evaluator.evaluate`/`dd_corrected_stats`/`Genome.child`/
  `constitution.accepts`/`holdout_accepts`, the same precedent
  `exit-gene-test` used).
- `git diff --stat`: only `evotrader_bundle.py` touched (+180 lines).
- `live_state.json` md5 `0fa0731311baab0508f959f79a01214e` and
  `evotrader.manifest` md5 `0bf3a7d9411ee692d0a9f152a7533803` both unchanged
  before and after every run (checked explicitly, all three `--also-version`
  invocations included).
- No genome promotion, no trading touched, today's bar already processed
  before this session.

## Next

The fold-3-mechanism thread is now answered as far as *single-gene or
simple-combination* Guardian tightening goes: it can clear the fold gate,
it cannot clear the holdout. Two genuinely untried directions from here:
(1) whether a **smaller** tightening (not halved — e.g. 25% tighter) trades
away less upside and holds up better at the holdout, since halving is a
fairly blunt first probe and every variant here overshot into holdout
failure; (2) whether this is the same lucky-holdout-draw entrenchment
`holdout-pressure`/the 2026-08-18 4h-shadow findings already documented for
*discretionary* changes, now showing up for mechanical ones too — in which
case no single-gene patch will ever clear it and the real fix is a genuine
`evolve()` search from this starting point (letting the Researcher's blind
perturbation try many points in the Guardian gene sub-space at once,
already inside `agents.researcher.GENE_SPACE`, rather than four
hand-picked ones), or accepting the holdout gate as a structural feature,
not a bug to route around gene-by-gene.
