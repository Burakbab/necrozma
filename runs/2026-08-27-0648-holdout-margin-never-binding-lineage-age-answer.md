# The lineage-age holdout-margin question, closed with data already on hand — the margin has never been the deciding factor for v3

## Context

The 2026-08-27 ~04:05 UTC entry (fold-date-flip holdout-backstop stress test,
19/19 flip candidates rejected) left one open item: what does the sealed-holdout
margin look like for a lineage with few or zero accumulated holdout draws (right
after a promotion), since every flip candidate tested so far was checked at
today's aged 13-14 cumulative draws (margin ~4.53-4.60), roughly double what a
fresh lineage would face (`required_margin` at `n_draws=1` collapses to
`HOLDOUT_SIGMA * sqrt(2*ln(2))` ≈ 2.355, per `margin-curve`). That session
explicitly recommended against another identical-method generation batch (20x
margin gap, diminishing value) but flagged the lineage-age question as still
open.

This session answers it without running any new generations, using two
existing read-only diagnostics plus arithmetic already available in this repo.

## What was checked

1. `python3 evotrader_bundle.py margin-curve` — confirms the young-lineage
   margin value: `n_draws=1` → margin 2.355 (vs 4.530 at today's `n_draws=13`).
2. `python3 evotrader_bundle.py holdout-pressure` — lists every one of the 12
   real sealed-holdout draws run against live champion v3 since its promotion,
   spanning `n_draws=2` (the youngest real draw this champion has ever faced)
   through `n_draws=13` (today). This *is* the lineage-age data: it already
   contains draws from when the lineage was young, recorded historically, not
   synthesized.

For each of the 12 rows, computed the raw holdout diff (`challenger_holdout -
champion_holdout`) and compared it to the margin actually in force that draw:

```
draws  chal_ho  champ_ho  raw_diff  margin  raw_diff > 0?
    2   -2.296    -1.172    -1.124   0.094   False
    3   -1.173    -1.172    -0.001   0.119   False
    4   -1.172    -1.172     0.000   0.133   False
    5   -1.172    -1.172     0.000   0.144   False
    6   -1.172    -1.172     0.000   0.151   False
    7   -1.172    -1.172     0.000   0.158   False
    8   -1.708    -1.172    -0.536   0.163   False
    9   -1.363    -1.172    -0.191   0.168   False
   10   -2.273    -1.172    -1.101   0.172   False
   11   -1.056    -0.881    -0.175   0.175   False
   12   -2.155    -0.881    -1.274   0.178   False
   13   -1.375    -0.881    -0.494   0.181   False
```

## Result

**The raw (unmargined) holdout diff has never once been positive across all 12
real draws — including `n_draws=2`, the youngest draw this lineage has ever
had, where the margin was only 0.094 (a fresh-lineage-scale margin, not
today's aged one).** That means every single one of these 12 real rejections
would have happened at *any* margin, including a hypothetical zero margin: the
challenger's holdout score itself was never even equal to (let alone better
than) the champion's, before any multiple-testing correction is applied.

This directly closes the lineage-age question for v3's actual history: the
margin size has never been the deciding factor in a real promotion attempt so
far. What has decided every case is the raw holdout comparison — challengers
that clear the fold-aggregate gate keep drawing a holdout score at or below the
champion's own, independent of how large or small the margin protecting that
comparison happened to be at the time. This is a different (and cleaner)
answer than the fold-date-flip thread's three sessions found by testing new
flip candidates against today's aged margin: those established the margin is
comfortably clearing hurdle *today*; this establishes the margin was never
actually load-bearing at any point in v3's history, young or old.

Caveat, same shape as prior entries in this thread: this describes v3's real
history specifically (12 draws, one lineage). It is not proof the margin can
never bind for a future, closer-fought champion — 6 of these 12 rows show the
challenger essentially *tying* the champion's holdout score to three decimal
places (`-1.172` repeated across draws 4-7), which is the closest this lineage
has come to a genuine contest, and even those ties needed no margin to reject
since a tie does not exceed zero. A lineage that draws a truly close (not
tied, not worse) challenger has not happened yet for v3 — this remains
unmeasured, not ruled out.

## Why this closes the thread (for now)

Combined with the fold-date-flip thread's 19/19 rejections (all decisively bad
on holdout, closest gap 20x under margin) and now this: every real promotion
attempt against v3, across its entire recorded history and every method used
to hunt for a flip so far, has failed on the raw holdout comparison, not on
the margin. Further identical-method batches (more generations, more flip
candidates) are unlikely to change this picture per the prior session's own
judgment call — and this session's finding removes the remaining reason to
keep probing the margin specifically, since the margin has demonstrably never
been what stood between a challenger and promotion. If this space stays worth
revisiting, the sharper question is now "does any real challenger ever draw a
holdout score genuinely *better* than the champion's, tie or not" — a
question about challenger quality, not about margin calibration, and one that
will only be answered by future real search, not by re-deriving more of this.

## Verified safe

- No code changed; only two existing read-only CLI commands run
  (`margin-curve`, `holdout-pressure`), both already documented as read-only
  in AGENTS.md.
- `live_state.json` md5 `1add861014e44aa69e814491cbd22e00` unchanged (still
  tick 13 from the 00:20 UTC daily run — today's bar already processed before
  this session started, no double-trade).
- `evotrader.manifest` md5 `0bf3a7d9411ee692d0a9f152a7533803` unchanged.
- `tools/edit_bundle_module.py sync --check` reports no drift.
- No genome promotion (no README Status change needed).
- `git status --short` was empty before this note was written.
