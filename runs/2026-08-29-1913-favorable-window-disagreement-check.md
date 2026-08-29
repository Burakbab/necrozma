# Fitness-vs-excess-return disagreement on a favorable calendar window

2026-08-29, ~18:50-19:12 UTC (3-hourly check)

## Why

The 16:28 UTC session (see
`runs/2026-08-29-1628-candidate-excess-disagreement-direction.md`) found the
fold-stage disagreement rate (63.3%) and its risky-direction skew (88.7%) on
*today's* fold/holdout window, where champion v3's own fold-aggregate fitness
is deeply negative (-1.695, an unfavorable calendar window per the weekend
all-hands' as-of-drift finding). Its own "Next" flagged the obvious
confound directly: "a run against a favorable fold window ... to check
whether the 63.3% fold-stage disagreement rate and its 88.7% risky-direction
skew are themselves as-of-drift artifacts, or hold up on a friendlier
window." This session ran that check.

## What

Standalone sandbox script (not committed, deleted after extracting results —
same discipline as every other real-search shadow script this project has
run: no `Genome.save()`/`.promote()`-to-disk/`EvolutionRun.run()` anywhere,
`live_state.json` opened read-only once, shadow champion lives only in a
local variable). Same disagreement-direction classification as the 16:28 UTC
script (`Researcher.propose`, `Evaluator.evaluate`/`holdout_check`,
`dd_corrected_stats`, `constitution.accepts`/`holdout_accepts`, mirroring
`EvolutionRun.generation()`'s exact gating), but run against a **favorable**
window instead of today's current one: `core.market.load_universe` loaded
normally, then each symbol's DataFrame truncated to its first 90% of bars
(`keep_frac=0.90`) before handing the dict to `Evaluator` — this shifts the
existing 85%-search/15%-holdout fractional split onto an earlier, friendlier
slice of the same real history (window ends 2026-04-04 instead of
2026-08-29) without fetching different data or touching the live fold
scheme. Checked champion v3's own fold-aggregate fitness at several
truncation points first (`keep_frac` 1.00 → -1.695, 0.95 → +0.949, 0.90 →
+1.398, 0.85 → +1.263, ...) and picked 0.90 as clearly favorable and
representative of the group. 15 generations, `n_blind=14`, seeded from the
same real `researcher_memory` the 16:28 UTC run used (224 tested proposals,
stagnation 15, holdout_draws 22 — the champion's actual state, not reset).

## Result

**Both effects the 16:28 UTC session flagged as open turned out to be
window-dependent, not fixed properties of the champion.**

Fold-aggregate: 210 candidates compared (same count as every 15-gen,
`n_blind=14` run against this unbeaten champion), but only **18
disagreements (8.6%)** — a large drop from 63.3%/66.2% on the unfavorable
window. Of those 18: 14 (77.8%) still the "risky" direction, 4 (22.2%)
conservative-miss — the directional skew survives on a much smaller sample,
but the disagreement rate itself collapses when the champion isn't
underwater on raw fitness. The champion dominated almost every candidate on
both metrics at once here (192/210 "both favor champion" vs 0 "both favor
challenger") — a much stronger champion on this window than on today's,
consistent with the fold-aggregate fitness gap (+1.398 vs -1.695).

Sealed-holdout — the gate a real promotion is decided at: only **4**
candidates reached it this run (vs 40 and 45 on the two unfavorable-window
sessions, because so few candidates cleared the now much-stronger
fold-aggregate gate at all), and **0 disagreements (0.0%)** — every one of
the 4 candidates that reached the holdout gate had raw fitness and excess
return agree on the verdict (all 4 lost to the champion on both). Champion
held all 15 generations, no shadow promotion.

## What this settles, and doesn't

Directly answers the 16:28 UTC session's flagged question: the 63.3%
fold-stage disagreement rate is substantially an as-of-drift artifact — it
falls to 8.6% on a window where the champion doesn't start deeply
underwater. The risky-direction skew when disagreements do happen (77.8%
here vs 88.7%/83.3% before) partially survives, but now on 18 fold-stage
cases and 0 holdout-stage cases instead of 133+40 — far too thin a sample on
this one window to call it confirmed at the same strength. The holdout-stage
result is the sharper one: zero disagreements out of 4, where the two
unfavorable-window sessions found 15.0% and 8.9% — consistent with (not
proof of) the near-tie characterization those sessions already gave every
holdout disagreement they found (0.1-1.1pp), since a stronger, more
dominant champion leaves less room for a near-tie to occur at all.

One truncation point on one champion, one random seed — not a sweep across
`keep_frac`, not repeated with a different seed to check this isn't itself a
lucky draw, and not tried against a different champion (still blocked on
reconstructed old champions lacking their own real `researcher_memory`, as
the 16:28 UTC session's "Next" already noted). Still, and explicitly, the
owner-level design decision the weekend all-hands and the 09:00 UTC daily
discussion already flagged ("should the selection metric be redefined
around excess return") remains untouched by this — if anything, this
session's finding argues for patience: the apparent disagreement problem
shrinks a great deal once the champion isn't fighting a hostile calendar
window, which is itself a temporary, drifting condition, not a fixed flaw in
the metric.

## Verified safe

- No file written anywhere by the shadow script: `git status --short` clean
  before, during, and after; sandbox script deleted after extracting
  results.
- `md5sum live_state.json` unchanged throughout:
  `bf360fc7f86f6bae2bc46bb6f6dc6026` (same as the 16:28 UTC run's own
  reading).
- Today's bar (00:20 UTC) was already processed before this session started
  (`runs/2026-08-29-0020-daily-trading.md` exists); no `tick` run, no
  double-trade risk. No `evolve` run against real state either.
- `python3 -m pytest -q` 240/240 (no repo code changed this session, only a
  since-deleted sandbox script outside the tested surface).
- `tools/edit_bundle_module.py sync --check`: "bundle already matches real
  files, no changes."

## Next

- A `keep_frac` sweep (e.g. 0.95/0.90/0.85/0.80) with disagreement-direction
  tabulated at each point would show whether the disagreement rate scales
  smoothly with how favorable the window is, or whether today's result is
  itself noisy at n=18/n=4.
- Repeating on a favorable window with a second random seed would separate
  "this window is genuinely easier" from "this specific run got a lucky
  batch of proposals."
- Still not attempted, still the owner's call: redefining the selection
  metric itself.
