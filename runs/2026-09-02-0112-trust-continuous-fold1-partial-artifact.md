# The pre-ramp fold-1 hard-fail that started the whole cold-start-ramp thread is partly a measurement artifact, not pure real risk

**3-hourly check, ~00:50-01:12 UTC.** Today's daily bar was already handled
by the 00:20 UTC run (`live_state.json` `updated` 00:22:38 UTC) — no trading
this cycle.

Direct follow-up to the 2026-09-01 21:59 UTC entry's own recommendation
(item 2, option 2b: "step back from patching this seed genome further").
Before doing that, checked something no session in this whole thread (since
2026-08-31) had asked: is fold 1's from-cold-start `max_dd` — the number
every cold-start-ramp gene has been built and hand-tuned against — actually
trustworthy, or does it overstate real risk?

## What was built and run

`tools/shadow_4h_trust_continuous_check.py` (committed separately, 7 tests,
full suite 316/316, no engine/constitution/gene change): applies
`loop.evolve.dd_trust_continuous_stats()` — built 2026-08-22 for the bundled
`succession-audit` command, applied there only to past 1d champions, never
before to this 4h-shadow genome family — to `x6`, `consv_trailing`, and
`consv_trailing_ramp` (120/0.20). `dd_corrected_stats()` (what `accepts()`
actually gates a real promotion on) is one-sided: `min(fold-merged,
continuous)`, which can only ever make `max_dd` more negative, correcting
for a drawdown that spans a fold boundary invisible to the fold-local
number. `dd_trust_continuous_stats()` is the two-sided sibling: it always
trusts the continuous number, correcting for the *opposite* direction too —
a fold's own local peak rebasing to a fresh, lower value right at its
boundary can turn a moderate decline into a much larger *fraction* of that
reset peak, overstating true risk. Ran against today's real 4h Binance data
(27 symbols, 4.0y, `n_folds=3`).

## Result

| recipe | per-fold max_dd | one-sided gate (current) | two-sided (`trust_continuous`) |
|---|---|---|---|
| `x6` (bare) | [-37.9%, **-44.5%**, -35.3%] | -44.5%, **hard-fails**, fitness -inf | -44.3%, **still hard-fails**, fitness -inf |
| `consv_trailing` (no ramp) | [-30.5%, **-43.8%**, -35.8%] | -43.8%, **hard-fails**, fitness -inf | **-32.7%, clears, fitness +0.406** |
| `consv_trailing_ramp` (120/0.20) | [-30.5%, -34.8%, -27.2%] | -34.8%, clears, fitness 0.734 | -32.7%, clears, fitness 0.777 |

Fold 1 (the middle fold, index 1) is the worst fold in every recipe here,
consistent with every prior session's finding.

**`x6`'s fold-1 failure is real: both correction policies agree it
hard-fails, so there's no artifact hiding in this recipe's number.**

**`consv_trailing`'s fold-1 failure — the exact genome and the exact
finding (2026-09-01 01:14 UTC, "-44.1% max_dd on fold [0.283, 0.567]")
that started this entire cold-start-ramp gene-building effort three days
ago — flips.** Under the one-sided gate it hard-fails at -43.8% (today's
snapshot, close to the 01:14 UTC session's own -44.1%). Under the two-sided
`trust_continuous` view it clears comfortably at -32.7%, with a genuinely
positive fitness (0.406) instead of `-inf`. That means at least part of
fold 1's reported severity for this specific genome is fold-rebasing
overstatement (the fold restarts the broker from flat cash right as a real
but more moderate decline is underway, so the decline reads as a much
larger fraction of the fold's own reset local peak than it is of the
account's true, longer-accumulated peak) — not that the strategy is safe on
this window, but that -43.8% overstates how unsafe it is.

## What this means for item 2

**Not a reversal of the 21:59 UTC recommendation, but a real qualification
of it.** Every gene built against fold 1 since 04:18 UTC (`cold_start_ramp_
bars`/`start_scale`, `min_conviction_boost`, `vol_cap`) was tuned to make
the *one-sided* fold-local number clear the gate — a real, measurable
target, and the ramp genes do measurably reduce it (-43.8% → -34.8% here).
But this session's finding says that target itself was inflated for
`consv_trailing`'s pre-ramp baseline: the "real" risk (continuous view) was
already only -32.7%, under the 40% cutoff, before any cold-start gene
existed. The ramp genes' actual, defensible contribution may be smaller
than "fixed a hard-failing genome" — closer to "improved an already-passing
genome's reported number, and incidentally made the one-sided fold-local
reading agree with what the two-sided reading already said."

This does **not** mean `x6` (the un-tightened base seed) is fine — its
fold-1 failure is confirmed real under both views, so the `consv1 +
trailing_stop` tightening genuinely did fix a real problem there; only the
*fold-1-specific residual* on top of that tightening is where this
session's artifact finding applies. And it does not touch the still-valid,
independent finding that whichever number you trust, three separate
"best-of-day" grid picks for the ramp genes have failed most nearby days
(13:16/16:47 UTC) — boundary fragility is a real, separate problem from
fold-rebasing overstatement, and both can be true on the same fold.

**Recommend against reopening the ramp genes to re-tune them "now that the
target was smaller than we thought"** — same standing caution as every
prior entry in this thread: don't hand-tune magnitude against one session's
numbers. The actionable next step this opens, sized for a future session:
run this same `trust_continuous` check across the `--shift`-day walk the
`fold-date-sensitivity` tool already does, to see whether the flip found
here at one snapshot is itself boundary-stable or just as fragile as every
other point-in-time reading in this thread has turned out to be. Until
that's checked, treat today's flip as suggestive, not settled — consistent
with `dd_trust_continuous_stats()`'s own docstring: diagnostic-only, never
wired into `accepts()`, and changing the gate's policy to ever use it stays
an explicit owner decision (AGENTS.md item 2), not something a diagnostic
finding enacts on its own.

`live_state.json` untouched (md5 unchanged from the 00:20 UTC daily-trading
run), no protected file touched, `python3 -m pytest -q` 316/316, `tools/
edit_bundle_module.py sync --check` confirmed no drift. Genome still v3
(1d) live, untouched.
