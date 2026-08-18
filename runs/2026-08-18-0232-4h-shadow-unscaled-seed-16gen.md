# 4h unscaled-seed shadow evolution, 16 generations — 2026-08-18 00:49-02:32 UTC

Follow-up to the open item at the bottom of the 2026-08-17-0820 run note
("whether more generations past 10 let the unscaled seed's fold fitness
eventually turn positive too"). That run stopped at generation 10 on a
time-budget call with fold-aggregate fitness stuck at -0.445 across 7
stagnant generations. This run is a fresh draw (not a continuation — no
state persists between separate scratch-dir invocations), pushed to 16
generations to give it real room to keep searching.

Same isolation discipline as every prior 4h shadow run: fresh scratch dir
under the session scratchpad, only `evotrader_bundle.py` +
`evotrader.manifest` copied in, no `live_state.json` anywhere near it, so
`Genome.champion()` falls back to a hand-built seed (bar_interval flipped to
`"4h"`, every period gene left at its 1d value — genuinely unscaled) instead
of touching this repo's `state/` or the real champion. Verified after the
run: real repo `git status` clean, `live_state.json` md5 unchanged, genome
still v3 (1d). `n_blind=6` (the by-now-standard workable rate for this bar
size, via a standalone script calling `EvolutionRun.run()` directly —
bypasses the bundled CLI's hardcoded `n_blind=14`). 27 symbols x ~4 years of
4h bars loaded fresh (400s), 16 generations took ~96 min, ~103 min total
wall time.

## Result: still never turns positive, and now we know why

| gen | champion | fold-aggregate fitness | accepted? |
|---|---|---|---|
| 1-3 | v1 | -4.508 | — |
| 4 | v1→**v2** | -4.508 → **-1.054** | `exit_trend_below` -0.03→-0.227, `max_positions` 6→2, `rsi_max` 82→95 |
| 5-7 | v2 | -1.054 | — |
| 8 | v2→**v3** | -1.054 → **-0.241** | `trend_slow` 50→**93**, `cash_floor_pct` 0.05→0.444, `rsi_len` 14→36 |
| 9-16 | v3 | -0.241 (final) | — |

Two promotions instead of the prior run's three, one generation later each
(gen 4 and 8 here vs. gen 1 and 2 there) — a slower climb this draw, same
qualitative shape (multi-gene combined patches, not single-gene fixes,
matching this run's earlier finding that the unscaled seed needs compound
fixes unlike the x6-scaled seed's one-gene jumps). Trade count fell
7388→2808→1769 across the two promotions, same overtrading-correction
pattern as before. **Fold-aggregate fitness never went positive across all
16 generations** — the open question from the prior run is answered: no,
more generations alone doesn't get there, at least not by 16.

Note gen 8's patch actually retunes `trend_slow` (50→93) itself, roughly a
manual-x6-scaling-sized move on that one gene — search finding its own
partial period correction rather than needing it hand-scaled in, though only
on one of the several period genes (`max_bars_held`, `regime_ma`, etc. were
untouched), and not enough by itself to reach positive fold fitness the way
the hand-scaled seed's single fix did.

## Why nothing displaces v3 after generation 8: the champion is holdout-lucky

This is the sharper, more useful finding. From generation 9 onward, dozens
of candidates reached the acceptance gate's *fold-aggregate* bar (best
fold-fitness per generation: 0.099, 1.080, 0.401, 0.267, 0.498, 0.678 —
solidly positive, well above champion v3's -0.241 fold fitness) and every
single one still got rejected — not by the fold-fitness margin, but at the
**sealed holdout** step:

| draw | champion holdout | challenger holdout | passed |
|---|---|---|---|
| 8 | 1.079 | 0.907 | no |
| 10 | 1.079 | -1.006 | no |
| 12 | 1.079 | 0.080 | no |
| 14 | 1.079 | -1.664 | no |
| 16 | 1.079 | -0.096 | no |
| 18 | 1.079 | -0.149 | no |
| 19 | 1.079 | -1.626 | no |

Champion v3's own holdout draw (generation 8's promotion) happened to land
at **1.079** — a very strong score on a genome whose fold-aggregate fitness
is -0.241. This is the same fold/holdout split anomaly the
2026-08-17-0820 run first flagged and the 2026-08-17-0956 `regime`
diagnostic explained mechanistically (search folds contain a +200% melt-up
that punishes risk-reducing genomes, the sealed holdout is a -36% crash that
rewards them) — but this run shows its second-order effect for the first
time: once a champion gets a *lucky* holdout draw, it becomes very hard to
beat, because every challenger's own holdout score is a **single noisy point
estimate** on the same short crash window (7 challenger draws above range
from -1.664 to +0.907, no visible correlation to how good the challenger's
fold-aggregate fitness was) rather than a stable measurement. The gate is
working exactly as designed — the holdout is supposed to be a hard, honest
final check — but it means an unlucky (for search) holdout draw at
promotion time can entrench a champion whose fold performance keeps getting
beaten, for as long as nothing draws a big enough holdout score to clear a
rising margin (0.144 → 0.194 by draw 19, since holdout margin scales with
cumulative draws same as fold-side multiple testing).

This is a structural point about the acceptance gate that isn't specific to
4h or the unscaled seed — the fixed 85/15 holdout split makes any single
promotion's holdout luck sticky, in direct proportion to how few
independent bars the holdout window contains. 4h's holdout window has ~6.3x
more bars than 1d's for the same wall-clock slice, so if anything this
should be a *smaller* effect here than for the live 1d champion — worth
keeping in mind if the live account ever shows the same pattern (a
`fold-aggregate` that keeps losing to challengers while the promoted
champion's `holdout` stays untouchable). Not investigated further this run;
flagging it as a finding, not proposing a gate change — the sample size
here is one lucky draw, not evidence the mechanism is mistuned.

## Not attempted

- Whether a *rolling* or regime-stratified holdout (instead of one fixed
  85/15 split) would reduce this stickiness — the `regime` diagnostic run
  already flagged this as an open question for the fold scheme; this run's
  finding is a second, independent reason to consider it.
- Running past 16 generations — 63 candidates cumulatively tried against
  v3, stagnation counter at 7, no sign either number was about to break the
  pattern differently.
- Comparing head-to-head against a resumed continuation of the prior run
  (not possible — no state persists across separate scratch invocations,
  confirmed by design, not by mistake).

Shadow-only throughout: `live_state.json`, `researcher_memory`, and the real
v3 (1d) champion were never touched. Verified via `git status` (clean) and
`live_state.json` md5 unchanged before/after.
