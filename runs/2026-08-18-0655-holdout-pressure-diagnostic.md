# Holdout pressure diagnostic — 2026-08-18 06:55 UTC

## Scope

3-hourly self-improvement check. Today's daily bar (2026-08-17 close, tick 4)
was already handled at 00:21 UTC — confirmed via `live_state.json`'s
`updated` timestamp and `runs/2026-08-18-0020-daily-trading.md` before
touching anything. Next bar (2026-08-18) hadn't closed yet at session start
(06:46 UTC), so no `tick` was run this cycle.

Spent the slot on Next-steps item 2's open thread: the 2026-08-18 02:32 UTC
4h-shadow run found that a champion's own holdout draw can entrench it
against genuinely fold-superior challengers, and flagged "worth checking
whether the live 1d champion shows the same fold-vs-holdout gap the next
time a promotion is evaluated" as the follow-up. That follow-up doesn't need
a *new* promotion to check — the real champion v3's own post-promotion
search history is already sitting in `live_state.json`'s `lineage`, recorded
by every real `evolve` call made against the live account since the
2026-08-16 v2→v3 promotion (mostly the weekend all-hands' `evolve 15`, round
2, continuing 9 generations past the promotion). Read that recorded history
directly instead of waiting.

## What was built

New pure function `loop.evolve.summarize_holdout_pressure(lineage,
champion_version)` and CLI command `evotrader_bundle.py holdout-pressure`
(read-only, no backtest, no market data — just reads `acct.lineage`, so it's
near-instant unlike the other diagnostics). It separates two outcomes that
both just look like "champion held" in the generation log:

- **fold-blocked**: nothing that generation even cleared the fold-aggregate
  gate (search found nothing worth a holdout check).
- **individual holdout draws**: a candidate's fold-aggregate fitness *did*
  clear champion + margin, reached the sealed holdout, and lost there.

`EvolutionRun.generation()` holdout-checks every one of its top-3 candidates
that clears the fold gate (not just the best), but only the *last* one
checked survives into `gen_record["holdout"]` — the earlier ones are visible
only as rejection entries with their own `fold_fitness` and a `why` string
in `constitution.holdout_accepts()`'s fixed format. The new function parses
that format via regex to recover every individual draw, not just one
representative per generation; `tests/test_holdout_pressure.py` (8 new
tests, full suite 72 passed up from 64) builds its fixtures' `why` strings
from the real `holdout_accepts()` call so a template change there breaks the
parser loudly instead of silently under-counting.

## Result against the real live champion v3

```
HOLDOUT PRESSURE — champion v3
  9 generation(s) of real search run against this champion since its promotion
      0 no new proposals
      4 fold-aggregate gate blocked
      0 accepted
      9 individual sealed-holdout draws — every one lost

     fold fit  champ fold   holdout  champ holdout  margin  draws
        1.711       1.389    -2.296         -1.172   0.094      2
        1.698       1.389    -1.173         -1.172   0.119      3
        1.683       1.389    -1.172         -1.172   0.133      4
        1.609       1.389    -1.172         -1.172   0.144      5
        1.609       1.389    -1.172         -1.172   0.151      6
        1.608       1.389    -1.172         -1.172   0.158      7
        1.856       1.389    -1.708         -1.172   0.163      8
        1.748       1.389    -1.363         -1.172   0.168      9
        1.976       1.389    -2.273         -1.172   0.172     10
```

**Confirmed: the live 1d champion shows the same pattern the 4h-shadow work
hypothesized.** All 9 real challengers that reached the sealed holdout since
v3's promotion had fold-aggregate fitness 1.6–1.98 — a comfortable,
genuine improvement over champion v3's own 1.389 fold-aggregate score, well
clear of the multiple-testing margin (0.094–0.172 over this range). Every
one still lost on the holdout. Sharper than "lost": **6 of the 9 scored
essentially identical to the champion's own holdout fitness** (-1.172,
repeated to 3 decimal places, vs. champion -1.1717268...) rather than
clearly worse — those specific gene patches apparently make no difference
to trading behavior inside this particular sealed window (short, a crash
regime per the 2026-08-17 `regime` diagnostic), so the holdout check simply
reproduces the champion's own score rather than discriminating between
champion and challenger at all. Only 3 of 9 scored meaningfully worse
(-1.708, -1.363, -2.273). None scored better.

This is a stronger, more specific claim than the 4h-shadow work's "one lucky
draw, not proof of a systemic problem" — it's now 9 independent real draws
against the live account's own holdout, not one shadow-run anomaly, and the
"clears fold gate genuinely, then either ties or loses on holdout" shape is
consistent across all of them.

## What this does and doesn't mean

Not evidence the holdout gate is miscalibrated or should be loosened — it is
doing exactly what it is designed to do (refuse to promote on fold-aggregate
alone). What it does show: on this specific holdout window, the gate is
currently much closer to "a fixed hurdle most patches can't move" than to "a
discriminating test of genuinely different genomes" — for the 6 tied draws,
changing genes that meaningfully move fold-aggregate fitness (regime
scaling, conviction, RSI thresholds, cash floor, etc.) produced *zero*
measurable difference on the holdout slice specifically. That's a
worthwhile flag for whoever next touches the fold/holdout scheme (see
`AGENTS.md`'s existing open question about `FOLD_CONSISTENCY_WEIGHT` and a
rolling/regime-stratified fold scheme) — not something to act on
unilaterally this run.

Not touched: the champion, `live_state.json`, any gate or threshold. This
is read-only introspection over data that was already recorded.

## Verification

- Full suite: 72 passed (up from 64).
- `evotrader_bundle.py summary`/`signals`/`tick` all still report
  `constitution verified dfae6a697f51fb49`; `tick` correctly reported
  "already traded" for tick 4, no duplicate trade.
- `live_state.json` untouched: `git status` shows it unmodified by this
  session (only `evotrader_bundle.py` and the new test file changed).
- `loop.evolve` isn't in the checksummed set (`constitution`,
  `core.portfolio` only), so this change doesn't affect
  `evotrader.manifest`.

## Next

Add `holdout-pressure` to the routine post-`evolve` checklist: any future
scheduled session that runs real `evolve` against the live account should
run this afterward and note the result, the same way `hard-calls` got
folded into daily-evaluation checks. If a future promotion happens, this
diagnostic against the *new* champion answers whether the pattern is
specific to v3's particular holdout draw or a standing property of this
fold/holdout scheme.
