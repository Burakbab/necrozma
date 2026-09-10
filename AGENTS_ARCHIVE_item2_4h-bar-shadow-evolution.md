# Archive: item 2 (4h-bar shadow evolution), full pointer history

This is the complete, verbatim "Pointer" history that used to sit inline
under `AGENTS.md`'s Next-steps item 2 ("4h bars for ~6x more observations and
a tighter fitness estimate"). Moved here 2026-09-10 (3-hourly check) because
item 2 was decided by the owner on 2026-09-08 (parked, redirect effort — see
`AGENTS.md`'s "Owner decisions pending" section for the decision itself) and
this ~76KB of now-closed evidence-gathering was the largest single reason
`AGENTS.md` had regrown past its 256KB single-read limit (264KB at time of
this cut) only six days after the last archival pass. Nothing reworded,
nothing lost — every entry below is unchanged from its original text, in its
original (reverse-chronological, newest-first) order. `AGENTS.md` itself now
carries a short summary in item 2's place, pointing here for the full trail.

---

   **Pointer (2026-09-04 ~00:46-01:xx UTC): the "3 fold-clears" in the tally
   just below are confirmed, by directly testing `Researcher.structural()`,
   to be one deterministic candidate (`remove_agent` on `consult_moderate`)
   guaranteed to recur at generation 1 of any memory-less `EvolutionRun`
   against this champion, regardless of RNG seed — not 3 independent search
   outcomes.** See "Current state" above and
   `tests/test_researcher_structural_determinism.py`. Real independent
   evidence from option (i) is closer to 0 fold-clears than 3; this makes the
   existing "treat option (i) as exhausted" recommendation below stronger,
   not weaker. Still does not decide the accept-vs-redirect fork itself —
   still the owner's call.

   **Pointer (2026-09-03 ~03:46-04:16 UTC): a fifth seed clears the fold gate a
   third time, via the exact same `consult_moderate`-disabling mutation that
   cleared it last time (identical fold fitness) -- again fails the sealed
   holdout. Sample is now 5 seeds/9 generations, 3 fold-clears, 0 clearing
   both. Recommend treating option (i) as exhausted for the `x6` recipe and
   making the accept-vs-redirect call below explicitly, rather than a sixth
   seed.** See "Current state" above and
   `runs/2026-09-03-0416-shadow-4h-x6-seed9105.md`.
   `tools/shadow_4h_ramp_generation.py --recipe x6 --generations 2 --seed
   9105` (unmodified tool, fresh seed): generation 1's `consult_moderate`-
   disabling candidate (fold fitness 0.0443, identical to seed 9104's same
   candidate) cleared the real fold gate then lost the sealed holdout (-0.724
   vs. champion -0.222 + margin 2.355); generation 2 found nothing that
   cleared the gate. The recurring identical candidate is evidence this
   specific fold-clear is a structural/deterministic member of the
   researcher's mutation set, not fresh search finding something new --
   weaker independent evidence than a genuinely novel clear would be, which
   is why this entry's recommendation is sharper than the last: not decided
   here, still the next session/owner's call. Does not touch the owner-
   decision fork below.

   **Pointer (2026-09-03 ~00:46-01:11 UTC): a fourth seed clears the fold gate
   again (second clear in the sub-thread) and again fails the sealed holdout --
   sample is now 4 seeds/7 generations, 2 fold-clears, 0 clearing both.**
   See "Current state" above and `runs/2026-09-03-0111-shadow-4h-x6-seed9104.md`.
   `tools/shadow_4h_ramp_generation.py --recipe x6 --generations 2 --seed
   9104` (unmodified tool, fresh seed): generation 1's `consult_moderate`-
   disabling candidate cleared the real fold gate then lost the sealed
   holdout (-0.770 vs. champion -0.265 + margin 2.355); generation 2 found
   nothing that cleared the gate. **This session's read: four seeds/seven
   generations without a single holdout-clear, two independent fold-clears
   both failing holdout the same way, has shifted the evidence bar further
   toward closing option (i) in favor of item 2's accept-vs-redirect
   decision** -- not closed here, still the next session/owner's call. Does
   not touch the owner-decision fork below.

   **Pointer (2026-09-02 ~21:47-22:12 UTC): a third seed clears the fold gate
   zero times in 2 generations -- sample is now 3 seeds/5 generations, only
   1 fold-clear (which failed holdout), 0 clearing both.** See "Current
   state" above and `runs/2026-09-02-2212-shadow-4h-x6-seed9103.md`.
   `tools/shadow_4h_ramp_generation.py --recipe x6 --generations 2 --seed
   9103` (unmodified tool, fresh seed): both generations' top candidates
   hard-fail `dd_corrected_stats()`, including a not-previously-tried
   concentration-limit hypothesis (`risk_judge.max_position_pct=0.175`)
   that still hard-fails the same way. **Option (i) (more generations/seeds)
   is not closed by this, but the running tally (1/5 fold-clears, 0/5
   holdout-clears) is worth the next session weighing against treating it
   as similarly exhausted to the single-lever alternatives closed at
   12:47-13:09 UTC** -- not decided here. Does not touch the owner-decision
   fork below.

   **Pointer (2026-09-02 ~19:00-19:27 UTC): a fresh seed's second generation
   is the first candidate in the unconstrained-search sub-thread to clear
   the real fold-aggregate hard gate -- it still fails the sealed holdout.**
   See "Current state" above and
   `runs/2026-09-02-1927-shadow-4h-x6-seed9102-fold-gate-cleared.md`.
   `tools/shadow_4h_ramp_generation.py --recipe x6 --generations 2 --seed
   9102` (unmodified tool, fresh seed): generation 2's top candidate
   (`consult_moderate.rsi_hi` + `risk_judge.cash_floor_pct` ~0.48, a blunt
   de-risking move) cleared `dd_corrected_stats()` for the first time this
   sub-thread has seen, then lost at the sealed holdout (-1.808 vs. champion
   -0.281 + margin). **Nuances, doesn't reverse, the 06:46-07:15 UTC
   finding** -- unconstrained search can occasionally clear the fold gate
   this seed champion has died on before, but nothing across 3
   generations/2 seeds so far has cleared *both* fold and holdout. Option
   (i) (more generations/seeds) stays open, not closed by this; still a
   small sample. Does not touch the owner-decision fork below.

   **Pointer (2026-09-02 ~12:47-13:09 UTC): the last named single-lever
   alternative under (2b), `consv1` alone (no `trailing_stop`), is now
   checked too -- all 9 grid points hard-fail fold 1's real gate, and
   `trailing_stop` (not `consv1`) turns out to be the lever carrying the
   22:07 UTC "super-additive" synergy. Recommend closing (2b) as exhausted
   for single-lever alternatives.** See "Current state" above and
   `runs/2026-09-02-1309-consv1-threshold-sweep-isolated.md`. New
   `tools/consv1_threshold_sweep.py` grid-searches `rsi_buy_below` x
   `z_buy_below` on the bare `x6` seed (`trailing_stop` left at its
   untightened default, `scale=6` fixed) against the real
   `Evaluator`/`dd_corrected_stats()` gate: all 9 points hard-fail
   (-42.6% to -44.3% gate max_dd, barely different from the -44.3%
   untightened baseline), and tightening `consv1` alone makes
   `aggregate_fitness` slightly *worse* (-2.450 -> -2.565), not better.
   **What's left under item 2 is no longer "which single lever fixes fold
   1" (answered: none does) but a decision the next session/owner should
   make explicitly: accept the full `consv1 + trailing_stop + ramp` stack
   and move toward a real (non-shadow) promotion attempt for this genome
   family, or park 4h-bar shadow evolution and redirect effort (parked
   short-selling Phase 1, or item 4's LLM-backed consults).** Not decided
   this cycle.

   **Pointer (2026-09-02 ~09:47-10:10 UTC): (2b)(ii)'s bar-scaling-multiplier
   half is checked and closed -- scale 4/6/8 all hard-fail fold 1, scale 6 is
   the least-bad of the three, not an unexamined pick. The `consv1`
   consult-tightening thresholds are the only untried piece of "reconsider
   the base recipe" left.** See "Current state" above and
   `runs/2026-09-02-0956-x6-scale-parametrized.md`. `tools/shadow_4h_x6_seed.py`
   and `shadow_4h_fold_date_sensitivity.py` now take `--scale` (default 6,
   backward compatible) so this check could be run at all. **Three live
   threads left under item 2, none tried yet in isolation:** (i) more
   generations/seeds of the unconstrained `--recipe x6` search; (ii-remaining)
   sweep the `consv1` thresholds (`rsi_buy_below`/`z_buy_below`) themselves
   against fold 1, holding scale=6 fixed, instead of only ever measuring them
   stacked with trailing-stop and ramp genes; or accept that this genome
   family's fold-1 fix requires the full stack and stop looking for a
   single-lever alternative.

   **Pointer (2026-09-02 ~06:46-07:15 UTC): option (2b)'s first slice --
   unconstrained search on the unpatched `x6` seed -- hits the same fold-1
   wall as every hand patch; the more literal reading of (2b) (reconsider
   the base recipe itself) is the untried half now.** See "Current state"
   above and `runs/2026-09-02-0656-fresh-search-x6-recipe.md`.
   `shadow_4h_ramp_generation.py --recipe x6` (new this entry) ran one real
   generation from the unpatched seed: the top proposal by a wide margin
   (fold-aggregate 0.856 vs 0.435, a bear-regime size cut) still hard-fails
   `dd_corrected_stats()`'s drawdown gate -- one generation, one seed, not
   exhaustive, but it argues against "a fresh search would easily route
   around fold 1." **Two live options left under (2b), neither tried yet:**
   (i) more generations/seeds of the same unconstrained `--recipe x6` search
   (the tool now supports this directly), in case one generation was simply
   unlucky; or (ii) reconsider the *base recipe* itself -- the x6 bar-scaling
   multiplier approach, or the `consv1` consult-tightening choice -- rather
   than searching on top of either. (ii) is untried by every session in this
   thread so far and is the more literal reading of "step back ... and
   reconsider the base recipe" from the entry that first proposed (2b). (2a)
   stays closed; nothing here reopens it.

   **Pointer (2026-09-02 ~04:13 UTC): the 01:12 UTC "fold-rebasing artifact"
   finding doesn't hold across nearby days -- 1 of 7 shifts hard-fails under
   BOTH the one-sided and two-sided correction, so `dd_trust_continuous_stats`
   does not settle whether fold 1's drawdown is real for this genome family.
   Does not reopen (2a)/close-out; (2b) is still the only untried option.**
   See "Current state" above and
   `runs/2026-09-02-0413-trust-continuous-flip-day-sensitivity.md`. New
   `tools/shadow_4h_fold_date_sensitivity_trust_check.py` (7 tests, full
   suite 322/322) runs the two-sided correction across the same 7-day
   `fold-date-sensitivity` walk instead of a single snapshot. `consv_trailing`
   result: 2/7 shifts flip (today and 2026-08-27), 4/7 don't even hard-fail
   one-sided, but 2026-08-29 hard-fails under both views (-46.8%/-42.9%) --
   real risk that day. Third instance of this genome family's "best
   snapshot doesn't generalize" pattern (grid-point instability 16:47 UTC,
   generation-vs-sweep boundary flip 10:27 UTC). **Do not treat the
   trust_continuous view as a shortcut past (2b)** -- it's exactly as
   day-sensitive as the raw one-sided number.

   **Pointer (2026-09-01 ~22:20 UTC): option (2a) from the 19:21 UTC entry
   below is now closed -- a volatility-scaled cold-start cap doesn't help
   fold 1 either, and when it actually binds it makes the drawdown worse,
   not better.** See "Current state" above and
   `runs/2026-09-01-2159-cold-start-vol-cap-shipped.md`. New
   `risk_judge.cold_start_ramp_vol_cap` gene shipped and tested (default
   0.0, no-op, GENE_SPACE-registered, threaded through both shadow tools).
   The first-guess cap range (0.3-0.8, by analogy to
   `consult_conservative`'s 1.10 `max_vol` veto) turned out to be the wrong
   scale -- fold 1's actual buy-candidate vol distribution is 0.033-0.342,
   so that whole range was a guaranteed no-op. Sweeping caps inside the
   real range found: 0.30 negligible, 0.20 and 0.05 both make the real
   gate's max_dd *worse* (not better), and 0.10-0.15 flip fold 1 from
   passing to hard-failing outright. **Every lever tried against fold 1's
   cold start so far has now failed**: the size ramp alone is
   boundary-fragile (13:16/16:47 UTC), the conviction floor found no
   marginal band (19:21 UTC), and the vol cap backfires when it bites
   (this entry). **Option (2b) -- step back from patching this `consv1 +
   trailing_stop -0.06` seed genome further and reconsider the base recipe
   -- is now the only untried option left on this thread.** It is a
   bigger, multi-session task: needs either a different seed genome
   through the same `consv_trailing_ramp`-family fold-1 diagnostic, or a
   fresh `Researcher`-driven search that isn't anchored to hand-picked
   patches on top of one fixed 22:07 UTC starting point.

   **Pointer (2026-09-01 19:21 UTC): option (1) below (a structurally
   different, non-size lever on fold 1) has now been tried in its most
   direct form — a cold-start conviction floor — and is closed too: swept
   0.0 to 0.40 (80% of its allowed range) against the 120/0.20 ramp point,
   byte-identical results at every value.** See "Current state" above and
   `runs/2026-09-01-1921-cold-start-conviction-boost-no-bite.md`. New
   `risk_judge.cold_start_ramp_min_conviction_boost` gene (default 0.0,
   no-op) vetoes marginal-conviction buys during the cold-start window
   instead of just sizing them down. Instrumented directly against fold 1's
   own backtest window: buy-candidate conviction there is bimodal (mostly
   0.80-0.96 unanimous trades; the only low-conviction candidates were
   already below the *un-boosted* 0.30 floor) — no marginal band exists for
   a conviction filter to catch, so the drawdown is adverse price action on
   already-high-conviction trades, not weak signals slipping through. Gene
   kept (tested, no-op default, may still combine usefully in a real
   `Researcher` search or a different seed genome) but not worth hand-tuning
   further against this specific genome. **Narrows to two options, neither a
   single-session task: (2a) a non-conviction structural lever — e.g. a
   volatility-scaled position cap, or restricting which symbols/regimes can
   open cold-start positions at all — since the failing trades are
   unanimous/high-conviction, so the lever needs to key on something other
   than agent conviction; or (2b) step back from patching this `consv1 +
   trailing_stop -0.06` seed genome further and reconsider the base recipe.**

   **Pointer (2026-09-01 16:47 UTC): option (a) below is closed — three
   independent "best point" picks for `cold_start_ramp_bars`/
   `cold_start_ramp_start_scale` have each now been checked and each fails
   most nearby days; do not run another point-in-time sweep expecting a
   better answer.** See "Current state" above and
   `runs/2026-09-01-1647-cold-start-ramp-grid-instability.md`. Re-ran the
   08:08 UTC sweep ~8h later: only 20/37 points clear now (was 35/37), and
   120/0.20 itself flipped from -34.6% (pass) to -44.0% (hard-fail). Took
   today's new top pick (150/0.20) through the 7-day fold-date-sensitivity
   tool: 6/7 shifts hard-fail, worse than 120/0.20's own 4/7. **Two real
   next steps remain, both bigger than one 3-hourly session**: (1) a
   structurally different lever on fold 1 (e.g. a stricter entry threshold
   during the cold-start window, not just smaller position size), or (2)
   step back from patching this specific `consv1 + trailing_stop` seed
   genome further and reconsider the base. `tools/shadow_4h_x6_seed.py`'s
   `build_consv_trailing_ramp_seed()` and
   `tools/shadow_4h_fold_date_sensitivity.py` now take `ramp_bars`/
   `ramp_start_scale` overrides (`--ramp-bars`/`--ramp-scale`), so whoever
   picks up (1) or (2) can still reuse the multi-day check on whatever they
   try next.

   **Pointer (2026-09-01 13:16 UTC): the shadow fold-date-sensitivity tool the
   10:27 UTC entry below asked for is now built and run — the systematic
   check settles "boundary-fragile" into something worse.** See "Current
   state" above and
   `runs/2026-09-01-1316-shadow-4h-fold-date-sensitivity.md`. New
   `tools/shadow_4h_fold_date_sensitivity.py` (11 tests) re-evaluates a
   4h-shadow genome builder across a week of "as-of" dates with the real
   `dd_corrected_stats()` gate check applied at each. Result for the 08:08
   UTC sweep's recommended `cold_start_ramp_bars=120,
   cold_start_ramp_start_scale=0.20`: **4 of 7 recent days hard-fail
   `MAX_DD_HARD_FAIL` outright**, and the 3 that clear do so by at most +5.6
   points of margin. **Do not treat 120/0.20 (or 120/0.10) as a settled fix
   for the 01:14 UTC cold-start-fold problem** — it fails the real gate more
   often than it passes across nearby run dates, which the two prior
   same-day snapshots (08:08 UTC pass, 10:27 UTC fail) only hinted at.
   Two untried next steps, either usable with the new tool directly: (a)
   sweep other points from the 08:08 UTC grid search (larger `ramp_bars`
   or `start_scale`) through `--recipe consv_trailing_ramp --shift 7` for a
   wider-margin point, or (b) treat this seed genome's (`consv1 +
   trailing_stop -0.06`) fold 1 as structurally fragile and look for a
   different lever entirely rather than continuing to tune the ramp genes
   against it.

   **Pointer (2026-09-01 10:27 UTC): the 08:08 UTC sweep's 120/0.20
   recommendation is boundary-fragile, not settled — a same-day
   `EvolutionRun.generation()` re-check (seed 9002, `tools/
   shadow_4h_ramp_generation.py`, new this session) found the identical
   120/0.20 genome hard-failing `MAX_DD_HARD_FAIL` again (fold 1 max_dd
   -43.4% vs. the sweep's -34.6%), traced to one extra 4h bar in the loaded
   data (a fold-boundary-shift artifact `fold-date-sensitivity`'s own notes
   already flagged as consequential, not a market crash or a bug — see
   `runs/2026-09-01-1027-shadow-4h-ramp-generation-boundary-flip.md`).**
   Since the champion itself no longer cleared the gate this run, "champion
   held against 3 generations of blind proposals" isn't a real stability
   signal here — most challengers likely hard-failed the same structural
   fold for the same reason. **Recommend treating 120/0.20's ~5.4-point
   margin as too thin to trust from a single snapshot**; the natural fix is
   a shadow equivalent of the existing `fold-date-sensitivity` CLI (same
   mechanism, parameterized for a 4h-shadow genome builder instead of just
   the live 1d champion) rather than more one-off point measurements. Not
   built yet.

   **Pointer (2026-09-01 08:08 UTC): the recommended "real search over just
   those two genes" from the 04:18 UTC entry below is now done — 37-point
   grid search, see "Current state" above and
   `runs/2026-09-01-0808-cold-start-ramp-sweep.md`.** Found `ramp_bars=120,
   start_scale=0.20` strictly better than the hand-picked 120/0.10 on the
   real gate (aggregate_fitness 0.454 vs 0.368, same -34.6% gate max_dd,
   holdout still beats benchmark) — `tools/shadow_4h_x6_seed.py`'s
   `build_consv_trailing_ramp_seed()` now builds 120/0.20. Also found the
   two-gene landscape is jagged (two interior grid points hard-fail next to
   comfortably-clearing neighbors) — worth knowing before trusting a
   `Researcher`-driven hill-climb here. **Still open**: no fresh
   `EvolutionRun.generation()` has run against the new 120/0.20 point as
   champion yet (the natural next check, mirroring what the 04:18 UTC session
   did for 120/0.10); still no established prior champion for this seed
   lineage to compare against for a real promotion decision; the sweep only
   covers this one seed genome (`consv1 + trailing_stop -0.06`), untested
   against other trailing-stop values or a different seed. Also flagged, not
   resolved: this session's own measured `aggregate_fitness` for 120/0.10
   (0.368) didn't match the 04:18 UTC note's 0.467 despite matching gate
   max_dd exactly — see the run note for the caveat this leaves on any single
   hand-run number from a prior session.

   **Pointer (2026-09-01 04:18 UTC): the 01:14 UTC session's cold-start-fold
   dead end now has a real fix — `risk_judge.cold_start_ramp_bars`/
   `cold_start_ramp_start_scale` (shipped this session, see "Current state"
   above and `runs/2026-09-01-0418-cold-start-ramp-clears-fold-gate.md`). The
   22:07 UTC session's `consv1 + trailing_stop -0.06` genome plus this ramp
   (120 bars, 0.10x start scale — via `build_consv_trailing_ramp_seed()` in
   `tools/shadow_4h_x6_seed.py`) is the first genome in this whole thread to
   clear `MAX_DD_HARD_FAIL` on the real fold-based gate, not just a continuous
   replay. One real `EvolutionRun.generation()` has now run against it as
   champion (seed 9001, 34 blind proposals, see the same run note's
   addendum): champion held, best challenger fitness 0.611 vs. its 0.467,
   nothing cleared the acceptance bar — a real stability signal, not a
   promotion (nothing beat it by enough to even reach the sealed-holdout
   gate). Still open: `cold_start_ramp_bars`/`cold_start_ramp_start_scale`
   are now in `agents.researcher.GENE_SPACE` but 120/0.10 was hand-picked
   from a small sweep, never searched, and whether that generation's 34
   proposals happened to touch either gene wasn't recorded (the script only
   captured the summary) — a real search over just those two genes, or a
   re-run that also prints the per-candidate patch list, is the natural next
   step.**
   Infrastructure shipped 2026-08-15: `genome.bar_interval` (defaults `"1d"`,
   zero behavior change for existing genomes), threaded through `core.live`,
   `loop.engine`'s backtest + annualization (`core.market.BARS_PER_YEAR`), and
   the `evolve` CLI. Verified against real 4h Binance data end-to-end.
   **Decision 2026-08-15: stays off.** Live cadence stays daily — speeding it to
   ~4h would multiply scheduled-task usage. When there's spare capacity, run a
   fresh evolution from the seed genome at 4h granularity as a shadow/offline
   exercise (compute only, must not touch `live_state.json`) to get real
   comparative data before ever switching the live cadence.

   **First shadow evolution run 2026-08-16** (see `runs/2026-08-16-0000-shadow-4h-evolution.md`
   for full numbers): the raw seed genome at 4h bars is not just worse, it's
   broken — bar-count genes (`trend_slow`, `regime_ma`, `max_bars_held`, ...)
   mean 6x less wall-clock time at 4h, so the system overtrades and every
   evolved candidate across 2 generations failed a hard drawdown/trade-count
   gate outright (fitness −4.46, halts 9–10/run). Hand-scaling those genes ×6
   before evolving fixed it: fitness went −2.42 → 0.81 in one accepted
   promotion (sealed holdout passed), max_dd −43%→−19%, halts to 0. Still just
   2 generations on a scaled-not-retuned starting point, not checked against
   live champion v2 head-to-head — **not a promotion case**, but it does answer
   the open question from the plan sketch: a 1d-tuned genome cannot be ported
   to 4h as-is, and "reset to seed + let evolution retune" needs the periods
   pre-scaled to even be searchable, not just picked as the honest option.
   Next: more generations from the scaled starting point, or a longer blind
   search from a genuinely fresh (unscaled) seed to see if it converges to
   similar period values on its own.

   **Second shadow run 2026-08-16 (weekend all-hands)** (see
   `runs/2026-08-16-0600-weekend-all-hands.md`): a fresh scaled-seed 4h run
   (correctly isolated this time — the first attempt that session
   accidentally re-ran the real 1d champion v2 due to a scratch-dir setup
   bug, logged in the same run note as a caught mistake) found its own
   generation-1 promotion, fitness −2.374 → 0.469 (`breakout_len`,
   `max_position_pct`), then held at generation 2. Weaker magnitude than the
   first run's 0.81 but the same qualitative shape: catastrophic unscaled
   seed → workable after ×6 scaling → quick first promotion → stagnation.
   Stopped after 2 generations on a time-budget call — at `n_blind=14`
   (the CLI default, calibrated for 1d cost) each 4h generation took
   ~25-27 minutes, ~6x the 1d cost as expected from ~6.3x more bars per
   fold. **Open item, sharper than before**: run 4h shadow evolution with
   `n_blind=5-8` instead of the default, or fewer generations per
   invocation — the default proposal batch size is not calibrated for this
   bar size's backtest cost.

   **Resolved 2026-08-16 (3-hourly check): `n_blind=6` confirmed workable**
   (see `runs/2026-08-16-1404-4h-shadow-nblind6-correlation.md`). The
   bundled CLI's `evolve` command hardcodes `n_blind=14`, so this needed a
   small standalone script calling `EvolutionRun.run()` directly — same
   scratch-isolation discipline as prior runs. 6 generations at `n_blind=6`
   took ~72 minutes total (~10-12 min/generation vs. 25-27 at the default),
   workable inside a 3-hourly slot if kicked off early. Result: a fourth
   independent x6-scaled-seed generation-1 promotion (fitness −4.231 → 0.839,
   holdout passed, real edge over benchmark), via `correlation_penalty`
   0.0→0.75 this time, then held through 5 more generations. Same
   catastrophic-seed → quick-fix → plateau shape as the three prior runs,
   each via a different unrelated gene — read this as one more draw from
   that distribution, not a convergent search, and see the note for why it
   does NOT reopen item 3 below (different value tried against a broken
   champion vs. a competent one). Next, still not attempted: a genuinely
   fresh unscaled-seed 4h search, or 10+ generations past the first plateau
   at the now-workable `n_blind=6` to see if a second plateau exists.

   **Resolved 2026-08-17 (3-hourly check): a second plateau exists.** (see
   `runs/2026-08-17-0510-4h-shadow-second-plateau.md`) A fresh x6-scaled-seed
   run, 10 generations at `n_blind=6` in one continuous script (~82 min
   wall time), found **two** promotions, not one. Generation 1: the usual
   quick fix (v1 −2.369 → v2 0.618, `correlation_penalty` 0.0→0.1 — a
   *different* magnitude than the 2026-08-16-1404 run's 0.75, both fixing
   different broken seeds on the first try, reinforcing that this gene isn't
   specially validated at either value against a catastrophic baseline).
   Then 7 generations of real stagnation (boldness climbing 0→7, 52
   candidates cumulatively tried, none clearing the bar). Generation 9: v2
   → **v3**, fitness 0.618 → 1.010, via a genuinely combined 5-gene patch
   (`consult_conservative.z_buy_below`/`min_trend`,
   `consult_moderate.min_trend`, `risk_judge.max_positions`/
   `cash_floor_pct`) — sealed holdout passed convincingly (challenger 0.008
   vs champion −2.242, excess return +35.3%, excess Sharpe +1.29,
   `beat_benchmark: true`). Generation 10 then held, and did so via the
   holdout gate specifically: the top fold-aggregate candidate (fitness
   1.364, would have cleared the multiple-testing margin) **failed the
   sealed holdout** (−0.021 vs champion 0.008 + margin) and was correctly
   rejected — a clean live example of the holdout gate overruling a
   fold-winning candidate. Answers the open question: yes, a second plateau
   is reachable past the first, it just takes patience (7 stagnant
   generations here) and the boldness mechanism's wider mutation batches.
   One data point, not a law — still open: whether a third plateau exists
   past generation 10, and whether a genuinely unscaled fresh seed shows the
   same shape.

   **Resolved 2026-08-17 (3-hourly check): the unscaled seed does NOT show
   the same shape** (see `runs/2026-08-17-0820-4h-shadow-unscaled-seed.md`).
   10 generations at `n_blind=6` from the seed genome with `bar_interval`
   flipped to `"4h"` but every period gene left at its 1d value (no x6
   scaling at all) — same isolation discipline as every prior 4h shadow run.
   Unlike every x6-scaled run (one quick fix in generation 1, straight to
   positive fitness 0.6-0.8+), the unscaled seed needed **three** separate
   generations to claw back from catastrophic (-4.515) to -0.445 (disable
   `consult_moderate` as an entry source entirely, then
   `correlation_penalty` 0.9, then halve chop-regime sizing), then held flat
   through 7 more generations (53 candidates tried, boldness to 6) — fold-
   aggregate fitness never went positive at all. Sharper anomaly worth
   following up: every accepted version's fold-aggregate fitness stayed
   negative (0/3 folds beat benchmark) while its sealed-holdout fitness was
   strongly positive and rising (0.815 -> 1.704 -> 2.486, all
   `beat_benchmark: true`) — the opposite of typical overfitting, and unlike
   any x6-scaled run, where fold and holdout fitness moved together. Most
   likely a regime mismatch between the newest 15% holdout slice and the
   older 85% search folds for this specific genome, not evidence of genuine
   generalization; not chased further this run. Answers the open question:
   manual pre-scaling before evolving isn't just a head start, it reaches a
   categorically different (positive-fitness, fewer-trades, fold/holdout-
   aligned) outcome than blind search alone gets to from the raw seed in a
   workable generation budget. Still open: whether more generations past 10
   let the unscaled seed's fold fitness eventually turn positive too.

   **Resolved 2026-08-19 (3-hourly check): checked whether a third plateau
   exists past generation 10 on a fresh x6-scaled-seed run — no fourth
   promotion surfaced, but the count of promotions before the wall (3, not
   2) didn't replicate either, and 9 stagnant generations is the deepest
   probe of this question yet.** (see "Current state" above and
   `runs/2026-08-19-2137-4h-shadow-third-plateau.md`) 15 generations at
   `n_blind=6`: three promotions all inside generations 1-6, then 9 straight
   stagnant generations (boldness to 8, 65 cumulative candidates) with
   nothing clearing the bar. Shape replicates the 2026-08-17-0510 run
   (quick fixes then a wall); exact promotion count and plateau generation
   don't. Still open whether a much longer run (30+ generations) ever breaks
   the wall — flagged as a judgment call given the ~6-7 min/generation cost
   and the falling marginal value of "still flat" as more generations are
   spent confirming it.

   **Resolved 2026-08-18 (3-hourly check): no, 16 generations still doesn't
   get there, and now there's a mechanism, not just a data point.** (see
   "Current state" above and
   `runs/2026-08-18-0232-4h-shadow-unscaled-seed-16gen.md`) From generation 8
   onward, dozens of candidates cleared the fold-aggregate acceptance bar
   with fitness well above champion v3's -0.241, and every one was rejected
   at the sealed holdout: v3's own holdout draw landed at a strong 1.079,
   and every challenger's holdout score is one noisy point estimate on the
   same short window (7 draws ranged -1.664 to +0.907) that almost never
   clears that bar. This reframes the open question: it isn't "does the
   unscaled seed need more generations," it's "a champion that draws a
   lucky holdout score becomes hard to unseat regardless of how many
   generations run after it" — a property of the fixed 85/15 holdout split
   plus per-candidate draw noise, not of this seed or bar size specifically.
   Not chased further this run (one lucky draw, not proof of a systemic
   problem) but worth checking whether the live 1d champion shows the same
   fold-vs-holdout gap the next time a promotion is evaluated.

   **Resolved 2026-08-18 (3-hourly check): didn't need to wait for a new
   promotion — the live 1d champion's own post-promotion search history,
   already recorded in `live_state.json`, shows the same pattern.** See
   "Current state" above and
   `runs/2026-08-18-0655-holdout-pressure-diagnostic.md`. New diagnostic
   `evotrader_bundle.py holdout-pressure` found 9/9 real post-promotion
   challengers against champion v3 that cleared the fold-aggregate gate
   still lost the sealed holdout, 6 of them by tying the champion's exact
   holdout score rather than losing outright. Confirms the 4h-shadow
   hypothesis with real 1d data, not a shadow-run anomaly. Next: run this
   after every future non-promoting `evolve` call, live or shadow.

   **Resolved 2026-08-17 (3-hourly check): the fold/holdout split anomaly
   chased down, and the answer is the opposite of the "easier holdout
   window" guess.** New read-only diagnostic `evotrader_bundle.py regime
   [--interval ...]` (same guarantees as `anatomy`/`consults`/`costs`) reports
   equal-weight buy-and-hold return/sharpe/maxDD per walk-forward fold and
   the sealed holdout, independent of any genome. Full numbers in
   `runs/2026-08-17-0956-regime-diagnostic-fold-holdout.md`. Headline: 1d and
   4h bars see essentially the *same* calendar regimes per window (same
   universe, same fraction-based split of the same history) — fold 2 is a
   +200%+ melt-up (sharpe ~1.7-1.8), the holdout is the worst window of the
   four by raw buy-and-hold terms (-36%, sharpe ~-1.2), not a lucky bull run.
   That rules out "the genome got lucky on an easy holdout" and points at the
   real mechanism instead: fitness is *relative* to buy-and-hold, and the
   08:20 run's unscaled-seed fixes were all risk-reducing (disabled
   `consult_moderate`, near-max `correlation_penalty`, halved chop sizing) —
   exactly the profile that structurally underperforms a +200% melt-up
   (dragging fold-aggregate fitness negative) and structurally outperforms a
   -36% crash (driving holdout fitness up), for the same underlying reason.
   Not evidence the policy generalises — raw fold-aggregate fitness never
   went positive, so it still lost to benchmark in 2 of 3 folds — but it
   replaces a vague "regime mismatch" guess with a mechanistic one. Flags a
   sharper open question for whoever next touches the fold scheme: is
   `FOLD_CONSISTENCY_WEIGHT`'s cross-fold variance penalty enough when one of
   three fixed folds is permanently a +200% outlier, or does that call for a
   rolling/regime-stratified fold scheme instead of the current fixed 85/15
   split? Not attempted this run — `regime` only characterised the existing
   windows, it doesn't propose a new fold scheme.

   **Resolved 2026-08-18 (3-hourly check): first quantified answer — the
   outlier's dominance is a fold-count artefact, but raising `N_FOLDS` alone
   isn't the fix.** New diagnostic `evotrader_bundle.py fold-scheme` (see
   "Current state" above and
   `runs/2026-08-18-0952-fold-scheme-sensitivity.md`) re-evaluates champion
   v3 at `n_folds` 3/5/8: fold 2's outlier gap over the other folds shrinks
   monotonically (+219.4% → +53.8% → +52.0%), but `aggregate_fitness`
   itself swings non-monotonically (-1.224 → +1.633 → -0.500) and at n=8 a
   fold came close to `run_backtest`'s hard 120-bar minimum and one fold
   failed a hard gate outright. Next: a regime-stratified/rolling scheme,
   not a higher fixed `N_FOLDS`, looks like the right direction — but that's
   a constitution change (checksummed, needs an `AMENDMENTS.md` row) and
   deserves its own design pass, plus checking the pattern on more than one
   champion/snapshot, before anything gets proposed.

   **Resolved 2026-08-18 (3-hourly check): checked against a second
   champion (v2), and it sharpens rather than confirms the finding above.**
   (see "Current state" above and
   `runs/2026-08-18-1256-fold-scheme-champion-replication.md`) New
   `fold-scheme --also-version N` reconstructs any past champion from
   `live_state.json`'s own lineage (verified bit-exact, tested) and runs
   the same sweep on it. The outlier gap matches v3's to the decimal at
   every fold count — but that's guaranteed by construction (it's a
   buy-and-hold-only number, genome-independent), not evidence of anything.
   `aggregate_fitness`, which *is* genome-dependent, does **not** show the
   same shape: v2 decreases monotonically with fold count where v3 swings.
   So the "aggregate_fitness swings non-monotonically" half of the finding
   above is v3-specific, not a general fold-scheme property. Still open:
   whether a third champion looks like v2's shape, v3's shape, or a third
   one; `--also-version N` makes that a one-line check next time a
   champion promotes.

   **Resolved 2026-08-18 (3-hourly check): checked the third champion (v1,
   the seed) and it reverses the read above.** (see "Current state" above
   and `runs/2026-08-18-1549-fold-scheme-third-champion.md`) v1 swings
   non-monotonically too (-2.577 → 0.244 → -0.938), the same shape as v3,
   not v2's monotonic decrease — so 2 of 3 known champions swing and only
   1 decreases monotonically. Non-monotonicity is not v3-specific; it looks
   like the more common shape on this fixed 3-fold split. `--also-version
   N` has now swept all three real champions this account has had (1, 2,
   3) — closed until a fourth champion is promoted. Any future
   regime-stratified/rolling fold-scheme redesign should treat
   non-monotonicity as a property worth designing around, not a
   champion-specific artefact.

   **Tried 2026-08-20 (3-hourly check): the rolling half of the
   regime-stratified/rolling idea, and it doesn't fix the instability by
   itself.** (see "Current state" above and
   `runs/2026-08-20-1254-rolling-folds-and-holdout-noise-convergence.md`) New
   `rolling-folds` diagnostic (`loop.evolve.rolling_folds`, fixed-width
   overlapping windows instead of shrinking disjoint ones) shrinks the raw
   outlier gap as overlap rises but makes `aggregate_fitness` swing *more*
   than `fold-scheme`'s own n_folds sweep did, not less — `overlap`
   0.85/0.7/0.5/baseline gives 0.306/2.003/1.399/1.480. Reading: the cross-
   fold consistency penalty itself is sensitive to how many correlated
   windows feed it, so windowing changes alone (rolling or otherwise) likely
   need to come paired with a `FOLD_CONSISTENCY_WEIGHT` change, or the fix
   needs genuine regime-stratification (grouping by market character, not
   calendar position) instead of a denser calendar slide. Regime-
   stratification itself remains untried — would need a regime definition
   independent of the window under test (candidate: `regime`'s own per-
   window buy-and-hold characterization), and is real design work, not a
   tail-end addition.

   **Measured 2026-08-20 (3-hourly check): decomposed the aggregate swing,
   and it's the mean term, not the penalty term.** (see "Current state" above
   and `runs/2026-08-20-1556-fitness-decomposition-diagnostic.md`) The
   rolling-folds entry just above *inferred* the `FOLD_CONSISTENCY_WEIGHT *
   std` penalty term was driving the aggregate instability. New `fitness-decomp`
   diagnostic (`loop.evolve.fitness_decomposition`, `mean_term - penalty_term`
   reconstructs `aggregate_fitness` exactly, tested) measures the split
   directly across five schemes (disjoint `n_folds` 3/5, rolling overlap
   0.5/0.7/0.85): for v3 the aggregate ranges 2.100, mean term 1.500, penalty
   term only 0.610; for v1, aggregate 0.426, mean 0.609, penalty 0.183. Both
   champions: the mean of the fold fitnesses varies more than twice as much as
   the penalty. So retuning `FOLD_CONSISTENCY_WEIGHT` alone would *not*
   stabilize the aggregate — the dominant instability is the mean being
   dominated by one outlier window, which points more firmly at genuine
   regime-stratification (kill the permanent +200% outlier window) over the
   penalty-weight tweak the rolling-folds entry floated as one option.
   `fitness-decomp --also-version 2` (third champion) is a one-line follow-up
   not yet run.

   **Resolved 2026-08-20 (3-hourly check): ran that one-liner AND put a number
   on whether regime-stratification is worth the engine work — the melt-up is
   concentrated (~2.5x its even share at every resolution), so the answer is
   yes.** (see "Current state" above and
   `runs/2026-08-20-1855-regime-scan-melt-up-concentration.md`)
   `fitness-decomp --also-version 2` confirms the mean term (not the penalty)
   drives the aggregate swing in all three champions (v2 mean range 2.173 vs
   penalty 0.370). New `regime-scan` diagnostic
   (`loop.evolve.regime_concentration`, pure, tested, 8 tests, suite 151 up from
   143; read-only, genome-independent) measures how concentrated the searchable
   region's compounded growth is: `concentration_ratio` 2.75x at n=3 (one of
   three folds = 92% of |log-growth|), 2.57x at n=6, 2.45x at n=12 — the ratio
   holds ~2.5x as resolution rises, so the concentration is real, not a binning
   artefact. The n=12 scan exposes the mechanism: fold 2 is **two separated bull
   runs** (2023-10 +92.5%, 2024-08 +102.1%) colliding in one calendar fold —
   separable, i.e. exactly what a stratified scheme can split across folds
   without inventing or dropping data. This resolves the "is it worth the engine
   work" question in favour of yes, and hands the next builder the regime label
   to group on (`regime-scan`'s per-window b&h return). Still not started (it's a
   constitution change): `Evaluator` accepting a fold as a *set* of windows and
   `run_backtest` replaying a non-contiguous union of bars — needs a design pass
   + `AMENDMENTS.md` row.

   **Checked 2026-08-20 (3-hourly check): the 4h track shows the same
   concentration.** (see "Current state" above and
   `runs/2026-08-20-2200-regime-scan-4h.md`) `regime-scan --interval 4h`
   (12 windows, 8,766 4h bars): concentration ratio 2.47x, same order of
   magnitude as the 1d track's 2.45x, richest window's melt-up overlapping the
   same 2024-08 to 2024-11 bull run the 1d n=12 scan found. Closes the cheap
   follow-up the entry above flagged — no further regime-scan data is queued.
   The remaining work is the fold-scheme redesign itself, unstarted, needs a
   design pass + `AMENDMENTS.md` row, and is bigger than a 3-hourly slot.

   **Shipped 2026-08-21 (3-hourly check): the "needs engine work" assumption
   above turned out to be wrong for a first test, and `regime-folds` is that
   test.** (see "Current state" above and
   `runs/2026-08-21-0056-regime-folds-and-holdout-pressure.md`) A fold can be
   scored as several independently-backtested sub-windows merged together
   (`loop.evolve.regime_stratified_groups` + `Evaluator.evaluate_grouped`,
   both pure additions, tested, 16 new tests, suite 167 up from 151) without
   `run_backtest` or the constitution changing at all — no engine work, no
   `AMENDMENTS.md` row needed for this diagnostic itself. First reading
   against all three real champions: mixed (v3 +0.723, v1 +0.057, v2
   −0.065), and the dominant sub-window ends up isolated alone in its own
   fold rather than diluted across folds, which may not be the fix item 2's
   framing wanted. Next: sweep `--n-subwindows`/`--n-folds`, and settle
   whether isolating vs. forcing the dominant window to share a fold is the
   right objective before treating this as a verdict on regime-stratification
   either way. A genuine non-contiguous *single-replay* engine change (shared
   positions/compounding across a fold's sub-windows) is still unbuilt and
   would be a different, bigger question from what this diagnostic answers.

   **Swept 2026-08-21 (3-hourly check): the sweep is done, and it answers the
   isolating-vs-objective question — isolating is a double-edged mechanism,
   not a clean fix.** (see "Current state" above and
   `runs/2026-08-21-0351-regime-folds-nfolds-sweep.md`) At fixed 6
   sub-windows, raising `n_folds` 3→4→5 against v3 gives a clean monotonic
   trend +0.723 → +0.126 → −0.249: LPT balance isolates only the good
   outlier at low fold counts, but at higher counts it starts isolating a
   *bad* sub-window too, and the consistency penalty punishes that wide
   isolated-fold spread more than it rewards the good isolate. Cross-checked
   at `n_folds=5` against v1/v2: 2 of 3 champions lower, the third a wash —
   more consistent than the earlier `n_folds=3` mixed reading, suggesting
   that mixed result was itself a fold-count artefact. Reading: "isolate the
   dominant window" is not a general-purpose fix — it has no obviously
   correct fold-count operating point. Next: this points design attention
   away from windowing schemes entirely and toward a fix that targets the
   mean term's outlier sensitivity directly (e.g. capping/down-weighting one
   fold's contribution before averaging) — untried, real design work, still
   bigger than a 3-hourly slot, and would need its own `AMENDMENTS.md` row
   since any change to how promotion decisions are made should be argued in
   writing the same way constitution changes are. A genuine non-contiguous
   single-replay engine change remains a separate, unbuilt, bigger question.

   **Measured 2026-08-21 (3-hourly check): tried the mean-capping fix as a
   diagnostic, and it's the fourth independent windowing/capping mechanism to
   show the same champion-dependent, non-generalizing shape — recommend
   treating this whole line as exhausted.** (see "Current state" above and
   `runs/2026-08-21-0653-fold-cap-mean-winsorize.md`) New
   `loop.evolve.capped_fitness_decomposition(fold_fits, cap_z)` winsorizes
   each fold fitness to `mean + cap_z*std` before averaging (penalty term
   left uncapped, to isolate the mean-only effect), swept under the same 5
   fold schemes `fitness-decomp` uses. Against v3, capping made the
   cross-scheme range wider at every `cap_z` tested (0.657 → up to 0.977);
   against v1, the same mechanism tightened it (0.663 → down to 0.446).
   Mechanism: capping pulls down whichever scheme currently has the fattest
   single within-scheme outlier fold, and which scheme that is (relative to
   the other schemes' own aggregate) differs by champion, so the direction of
   the effect on the cross-scheme range isn't controlled by `cap_z` alone.
   This is the fourth mechanism in this thread (`fold-scheme`'s n_folds
   sweep, `rolling-folds`, `regime-folds`'s n_folds/n_subwindows sweep, now
   this) to independently land on the same shape: plausible per-champion, not
   general. Next: stop trying further windowing/capping variants on this
   line — the sharper, already-quantified, still-unstarted next step on the
   walk-forward-honesty question is `MULTIPLE_TESTING_SIGMA` recalibration
   (`holdout-noise` found the real sealed-holdout noise is 14-25x the
   constant `required_margin()` assumes, across all three real champions) —
   a constitution change needing its own design pass and `AMENDMENTS.md` row,
   not a fold-scheme tweak.

   **Shipped 2026-08-21 (3-hourly check): done — see "Current state" above and
   `runs/2026-08-21-0951-holdout-sigma-recalibration.md`.** New `HOLDOUT_SIGMA
   = 2.0` constant, used only by `holdout_accepts()`'s margin (via
   `required_margin()`'s new optional `sigma` parameter); `MULTIPLE_TESTING_SIGMA`
   and the fold-aggregate margin it protects are untouched. `AMENDMENTS.md` row
   added, full suite 179 passed, `evotrader.manifest` resealed at
   `8b74865634b1db07`. This closes the walk-forward-honesty thread's second
   half (the first half — the windowing/capping line above — is set aside as
   exhausted across four independent mechanisms, not closed, just not worth
   further variants for now). Remaining open question, carried into the new
   constant's own docstring: `HOLDOUT_SIGMA` measures realized-return-path
   resampling noise only, not the added noise from a candidate arriving
   pre-selected by correlated folds — a harder, unquantified question, not
   picked up this run.

   **Measured 2026-08-21 (3-hourly check): new `margin-curve` diagnostic puts
   real numbers on "gets harder to clear as n rises" instead of leaving it a
   qualitative claim, and it turns out the two gates are not in the same
   place on that curve.** (see "Current state" above and
   `runs/2026-08-21-1553-margin-curve-diagnostic.md`) Pure arithmetic on
   `constitution.required_margin` (`sigma * sqrt(2*ln(n))`, unchanged), no
   market data or backtest. At the real live counts (182 fold-aggregate
   candidates, 13 sealed-holdout draws): the fold-aggregate margin is nearly
   saturated (0.258 now, +0.10 more needs ~123x more candidates, +0.25 more
   needs ~574 million) — so a near-miss fold-aggregate candidate is not
   meaningfully pushed further out of reach by more search volume, live or
   shadow. The sealed-holdout margin is NOT saturated at its much smaller
   real draw count — only 4 more draws raise it +0.25. Reading: the rising-bar
   stagnation mechanism the 13:07 run named applies for real to the holdout
   gate (which never resets its cumulative count on a promotion) far more
   than to the fold-aggregate gate, which is already close to flat. Next:
   whoever next gets a real candidate to the sealed-holdout check should note
   the cumulative-draw count at that moment alongside the `HOLDOUT_SIGMA`
   outcome — it visibly moves at today's scale, unlike the fold-aggregate
   count.

   **Mapped 2026-08-21 (3-hourly check): the universe-perturb drawdown cliff
   from the 19:02 run is at the doorstep, not 20% away.** (see "Current
   state" above and
   `runs/2026-08-21-2210-universe-perturb-single-symbol-cliff.md`) No new
   code — a `--drop-frac` sweep (noisy at n=6/frac, not conclusive) plus an
   exhaustive `--drop SYM` census of all 27 symbols individually. Result:
   14/27 symbols (51.9%) hard-fail `MAX_DD_HARD_FAIL` when dropped ALONE
   (baseline maxDD -34.1% vs the 40% threshold, only 5.9pp margin). Next: an
   honest design pass on whether `MAX_DD_HARD_FAIL`'s margin is right given
   this — a constitution change needing its own `AMENDMENTS.md` argument —
   not attempted; this line is otherwise answered for now.

   **Superseded 2026-08-22 (3-hourly check): the -34.1% baseline this whole
   sub-thread rests on may itself be wrong — do not resume the design pass
   until re-checked.** (see "Current state" above and
   `runs/2026-08-22-0100-maxdd-jump-and-fetch-truncation-bug.md`) Same
   computation, this session: -46.5% baseline maxDD, already past
   `MAX_DD_HARD_FAIL`, no perturbation at all. Traced to (and fixed) a real
   silent-truncation vulnerability in `core.market.fetch_klines`'s pagination
   (a short page was treated as unconditional end-of-history, indistinguishable
   from a transient partial response) plus a new `find_gaps`/`load_universe`
   warning to catch it going forward — but whether this bug is *why* every
   prior session this week read -34.1% is a plausible, evidence-fitting
   explanation, not a proven one; there's no way to audit a past container's
   gitignored cache after the fact. Next, before anything else on this line:
   re-run the full 27-symbol single-drop census fresh (now gap-checked) and
   see which number survives. If -46.5% (or close) holds up clean, that's a
   bigger deal than a design pass on the gate's margin — it means the live
   champion's own unperturbed full-history backtest may be failing its own
   risk gate right now.

   **Fixed 2026-08-22 (weekend all-hands): -46.5% held up clean
   (`fold-dd-blindspot`, same day), and the design pass this sub-thread was
   waiting on is done.** See "Current state" above for the full mechanism
   and `AMENDMENTS.md` for the constitution-level argument.
   `EvolutionRun.generation()`'s promotion gate now checks a genome's max_dd
   as the worse of its fold-merged number and one true continuous replay
   over the same span, closing the exact blind spot this sub-thread traced
   from a suspected data bug through to a real structural gate failure.
   Verified against real data and a live shadow-evolve run, not just unit
   tests. This closes the `MAX_DD_HARD_FAIL`-margin design pass this
   sub-thread (and the 2026-08-21 universe-perturb-cliff entry before it)
   both deferred — not by moving the margin, but by fixing what the gate
   actually measures, which was the sharper and more honest of the two
   options. Open remainder, deliberately not decided by this fix: champion
   v3's own true drawdown already exceeds the corrected gate, and whether
   that should trigger a demotion/re-evolution is unresolved — see "Current
   state" above.

   **Sharpened 2026-08-22 (3-hourly check): the open remainder above isn't
   just a paper-loss/optics question — while v3 stays champion, its own
   `fitness() == -inf` disables one of `accepts()`'s two champion-relative
   safety checks entirely and loosens the other, confirmed firing in real
   shadow generations (2/30 candidates checked).** See "Current state" above
   and `runs/2026-08-22-1015-dd-gate-vacuous-regression-check.md`. No code
   change, no promotion incorrectly let through (both cases still correctly
   failed the sealed holdout) — but each such pass burns a scarce,
   never-reset holdout draw the gate wouldn't otherwise have spent. Adds a
   mechanistic reason, not just a magnitude one, to the still-unresolved
   demotion question.

   **Tracked further 2026-08-22 (two more 3-hourly checks): cumulative rate
   now 5/144 real shadow candidates, session counts 2/30, 0/54, 3/60 — noisy
   but non-vanishing, and round 3 also produced the first case where the
   intended-tightening direction was the actual reason for a rejection.**
   See "Current state" above and
   `runs/2026-08-22-1322-shadow-evolve-vacuous-check-round2.md` /
   `runs/2026-08-22-1629-shadow-evolve-vacuous-check-round3.md`. Still no
   incorrect promotion in any of the three sessions' samples. Still the
   owner's call whether this sharpens the case for prioritizing the
   demotion/rollback design pass.

   **Built 2026-08-22 (3-hourly check): new `succession-audit` diagnostic
   answers the one fact this whole demotion/rollback sub-thread had never
   asked — would v1/v2 actually pass today's dd-corrected gate if
   reinstated — and no real champion does.** See "Current state" above and
   `runs/2026-08-22-1854-succession-audit-diagnostic.md`. v1/v3 fail the
   simple full-history maxDD test outright. v2's full-history number looks
   clean (-38.1%, under the 40% line) but its fold-merged maxDD (-40.1%,
   fold 2's own rebased-NAV local peak-to-trough) still hard-fails the
   dd-corrected gate a real promotion decision actually uses — a new,
   opposite-direction wrinkle in `dd_corrected_stats()`'s `min()`-only design
   (it can tighten an understated fold-merged number, per the original
   blind-spot fix, but can't loosen an overstated one). "Revert to v2" is
   therefore not the easy fix it looks like from the headline full-history
   number. If/when the owner opens the demotion/rollback design pass, this
   is the fact base to start from.

   **Resolved 2026-08-23 (3-hourly check, 22:16 UTC): the "convergence
   across independent seeds" open question, never tested at the live 1d
   cadence (only at 4h, above) — a fresh unscaled seed does NOT reliably
   converge to anything within a realistic budget.** See "Current state"
   above and `runs/2026-08-23-2216-fresh-seed-1d-shadow-evolution.md`. 16
   generations, 235 proposals, zero promotions — unlike every 4h run's
   quick first fix. Root cause: the plain `SEED_GENOME`'s own sealed-holdout
   fitness (`-2.566`) is far worse than its fold-aggregate fitness
   (`-0.022`), and `holdout_accepts()`'s multiple-testing margin (by design)
   grew from 2.355 to 4.761 across the 17 candidates that reached the
   holdout gate, so even the best holdout score any candidate drew
   (`+0.290`) never came close. Mirrors, and sharpens, the 2026-08-18
   "lucky champion is hard to unseat" finding: an unlucky seed traps itself
   the same way, and more generations only deepen the trap (each
   fold-clearing proposal burns another draw and raises the bar) rather than
   escaping it. Not chased further: whether this fold/holdout gap is
   specific to the current 4-year data window or a durable property of
   `SEED_GENOME` itself.

   **Measured 2026-08-24 (3-hourly check): the seed's poor holdout score is an
   ordinary draw from its own noise, not an outlier.** See "Current state"
   above and `runs/2026-08-24-0049-seed-holdout-noise-diagnostic.md`. A
   one-off script (not a new CLI command — this genome isn't in
   `live_state.json`'s lineage, so `holdout-noise`'s own `--also-version`
   flag doesn't reach it) block-bootstrapped the seed's own sealed-holdout
   return path (fresh window, one day later than the prior entry: -1.194
   this time, not -2.566, purely from the date shift) 2000 times across 4
   RNG seeds. Real fitness lands within 0.13 sigma of its own bootstrap mean
   every time, and the bootstrap sigma itself (~1.77-1.85) matches the same
   range `holdout-noise` already measured for all three real champions
   (1.21-2.04) — not exceptional either way. Reading: the seed genuinely
   performs badly on this holdout window; it isn't a fluke of return-order
   noise. Combined with the entry above, the picture is a genuinely bad seed
   on a genuinely bad window, correctly and consistently rejected by the
   gates — not a bug. Still open, and explicitly bigger than a
   noise-vs-signal question: whether a *different* 4-year data pull would
   show the seed in a better light at all (a question about `SEED_GENOME`'s
   robustness across market regimes generally, not attempted here).

   **Built 2026-08-24 (3-hourly check, ~12:47 UTC): `succession-audit` gets
   the two-sided comparison the 2026-08-22 entry above flagged as missing.**
   See "Current state" above and `tests/test_continuous_max_dd.py`'s four
   new tests. New `loop.evolve.dd_trust_continuous_stats()` is a
   diagnostic-only sibling of `dd_corrected_stats()` — instead of
   `min(fold-merged, continuous)`, it always trusts the continuous replay's
   `max_dd` outright, so it can recover a truer, better number in the
   overstatement direction `min()` can't (v2's case). `succession-audit`
   now prints this as a `trust-cont fit` column next to the existing
   `dd-corr fit` one. Explicitly NOT wired into `accepts()` or
   `EvolutionRun.generation()` — no live gate behavior changed, no opinion
   offered on whether it should be. This closes the specific "build the
   missing case" loose end the 2026-08-22 entry named, but does not restart
   or resolve the demotion/rollback design question itself, which remains
   the owner's call, unchanged.

   **Closed 2026-08-30 (3-hourly check, ~18:51 UTC): the demotion/rollback
   design question this sub-thread flagged as unstarted across every entry
   above finally has a design pass and a recommendation.** See "Current
   state" above and
   `runs/2026-08-30-1851-demotion-rollback-design-pass.md`. Recommendation:
   status quo, no demotion mechanism — a fresh `succession-audit` shows v3
   is the best of the three real champions on both drawdown-gate-closeness
   and full-history excess return (+68.2%, the only positive one of the
   three), so there is nothing better to demote *to*. Same closure pattern
   as the 06:00 UTC weekend all-hands used for the fitness-vs-excess-return
   question, with three named revisit triggers. **Future sessions: do not
   re-open this from scratch — point to the write-up unless one of its
   three triggers has actually fired.**

   **Measured 2026-08-24 (3-hourly check, ~16:15 UTC): a first number on the
   "harder, unquantified" selection-noise question the 2026-08-21
   `holdout-sigma-recalibration` entry left unchased.** See "Current state"
   above and `runs/2026-08-24-1615-selection-noise-diagnostic.md`. Six
   independent draws of real `Researcher.propose`/`Evaluator.evaluate`
   batches against real champion v3: each draw's fold-aggregate winner (what
   `EvolutionRun.generation()` actually carries to the holdout gate) and one
   randomly-picked non-winner from the same batch both ran through the
   sealed holdout (`generation()` itself never evaluates holdout for a
   non-finalist). Caught and fixed a real methodology bug first — a fresh
   `exclude=set()` every draw let the same deterministic
   `from_diagnosis()`/`structural()` proposal win all 6 draws identically,
   since only `perturb()` depends on the Researcher's seed; fixed by
   accumulating `exclude` across draws like `EvolutionRun.tested` really
   does. Result: winner's mean (fold − holdout) gap +2.172 (std 0.928, n=6)
   vs random's +0.990 (std 1.274, n=6), winner larger in 4/6 draws, paired
   t≈1.55 — directionally consistent with a winner's-curse-style selection
   effect, **not statistically significant at n=6**. A first measurement,
   not a settled answer: still open, and not attempted here — more draws to
   sharpen significance, a second champion, or (if a larger sample confirms
   the effect) translating it into an actual correction, which would be a
   constitution change needing its own design pass and `AMENDMENTS.md` row,
   not a natural extension of one measurement session.

   **Measured 2026-08-24 (3-hourly check, ~18:57 UTC): the "more draws" follow-up
   weakens the signal instead of sharpening it.** See "Current state" above and
   `runs/2026-08-24-1857-selection-noise-batch2.md`. Same method, 6 more
   independent draws (n_blind=10, exclude accumulated) against the same real
   champion v3. Batch 2 alone reverses the direction (random gap mean 1.818 >
   winner gap mean 1.679, paired t=−0.218). Combined 12-draw sample: paired
   t≈1.02 (df=11), weaker than batch 1's t≈1.55 alone — the opposite of what
   "just needs more data" would predict if the effect were real, driven by a
   variance blowup in batch 2's random-gap draws (one outlier at −1.358, the
   only negative gap either batch produced). **Reading revised**: no good
   evidence yet of a winner's-curse selection effect distinct from ordinary
   per-candidate holdout noise; batch 1's number now looks like a favorable
   draw from a noisy distribution rather than the start of a sharpenable
   signal. Leaving this question here — further identical-method batches are
   unlikely to resolve it either way; would need an order-of-magnitude more
   draws or a genuinely different check (e.g. a second champion) to be worth
   another session. No `HOLDOUT_SIGMA`-style correction proposed; the evidence
   doesn't support one.

   **Measured 2026-08-24 (3-hourly check, ~22:01 UTC): the "second champion"
   check named above — and it replicates the direction.** See "Current
   state" above and `runs/2026-08-24-2201-selection-noise-second-champion.md`.
   Same six-draw method against reconstructed champion v2 instead of v3:
   winner gap mean +1.851 vs random gap mean +0.237, winner larger in 5/6
   draws, paired t≈1.667 (df=5) — similar shape and strength to v3 batch 1
   (t≈1.55), not diluted the way v3's own batch 2 diluted it. Neither
   champion is individually significant, but two unrelated genomes landing
   on the same direction and similar magnitude is meaningfully stronger
   evidence than either alone, without being strong enough to justify a
   `HOLDOUT_SIGMA` change. Next, if this stays worth resolving: a
   genome-stratified or mixed-effects pooled test across all 18 draws so
   far (6 v3-batch1 + 6 v3-batch2 + 6 v2), not another same-shape batch.

   **Measured 2026-08-25 (3-hourly check, ~01:00 UTC): the genome-stratified
   pooled test named above — done.** See "Current state" above and
   `runs/2026-08-25-0100-selection-noise-genome-stratified.md`. Pure
   arithmetic on the 18 already-collected draws, no new backtests: Cochran's
   Q (0.994, df=1) found no detectable heterogeneity between v3 and v2, so
   the "samples aren't from one distribution" objection that blocked pooling
   isn't supported by this data (weak evidence at df=1, but not the
   roadblock it looked like). Properly pooled: fixed-effect mean +0.761
   (z≈1.678, one-sided p≈0.047); a block-stratified sign-permutation test
   (200,000 resamples, assumption-light) gives p≈0.0635 — closer to
   conventional significance than either genome alone but not a clean
   cross. Still not enough to justify touching `HOLDOUT_SIGMA`. Closes this
   specific design loose end; the concrete next step if this stays worth
   pursuing is a third genome (v1, or a future champion) to give the
   heterogeneity test real power, not another batch or permutation variant
   on the same two genomes.

   **Measured 2026-08-25 (3-hourly check, ~04:02 UTC): the third genome
   named above -- done, and it closes this line of inquiry.** See "Current
   state" above and `runs/2026-08-25-0402-selection-noise-third-genome.md`.
   Champion v1 (the unevolved seed) shows essentially no selection-noise
   signal (paired t~0.121, winner gap larger in only 2/6 draws) -- the
   weakest of the three genomes tested. Extending the pooled design to 3
   blocks moves the evidence away from significance (z 1.678->1.340,
   permutation p 0.0635->0.0815, Cochran's Q 0.994->2.030 at df=2, still not
   significant). Four sessions in, every new independent unit of evidence (a
   second v3 batch, a second champion, now a third genome) has weakened the
   pooled estimate rather than sharpening it toward significance -- the
   signature of a null or sub-noise effect. `HOLDOUT_SIGMA` untouched.
   **Closing this line of inquiry**: worth reopening only on a cheap fourth
   genome (a future v4+ promotion) or a genuinely different, sharper
   hypothesis -- not another same-method batch or genome.

   **Found 2026-08-30 (3-hourly check, ~23:05 UTC): a fresh 4h shadow run —
   the first since the dd-corrected gate was wired into `generation()`'s
   acceptance loop (2026-08-21/22) — shows the "reliable gen-1 quick fix"
   pattern every prior 4h-shadow run relied on no longer holds, plus a
   first, caveated 4h `holdout-noise` number.** See "Current state" above
   and `runs/2026-08-30-2305-4h-shadow-dd-corrected-gate-and-holdout-noise.md`.
   8 generations, x6-scaled seed, `n_blind=6`, same isolation discipline as
   every prior run here: **zero promotions**, where every prior run (all
   pre-dating the fix) found one in generation 1. Each generation's top
   fold-aggregate candidate looked like the usual fix but got rejected by
   the dd-corrected hard gate (continuous-replay maxDD > 40%, invisible to
   the fold-merged number) about as often as by the sealed holdout.
   Block-bootstrapped the only genome produced (the never-promoted seed):
   boot_fitness_std 1.461, 0.73x `HOLDOUT_SIGMA` — weakly supports "more
   holdout bars (~6x here), less relative noise" but isn't apples-to-apples
   with the 1d measurement (real promoted champions there, a rejected seed
   here). **Next, concretely**: a longer or differently-seeded x6-scaled 4h
   run to check whether *any* genome can clear the dd-corrected gate
   post-fix — the prerequisite for both a real 4h holdout-noise measurement
   and for meaningfully re-asking this thread's older "does a second
   plateau exist" question, which implicitly assumed the now-invalidated
   easy-gen-1-promotion shape. Not attempted further this session (time
   budget after the ~70 min evolution phase already spent).

   **Found 2026-08-31 (3-hourly check, ~02:43 UTC): a second, differently-seeded
   run also found zero promotions, via a different rejection-mechanism split.**
   See "Current state" above and
   `runs/2026-08-31-0243-4h-shadow-seed9001-still-zero-promotions.md`.
   `EvolutionRun(seed=9001)` instead of the default `seed=7` every prior
   4h-shadow session had used (this thread's own flagged follow-up), 14
   generations, same x6-scaled seed and isolation discipline. Champion
   pinned at fitness -4.296 throughout; of 42 rejections, 74% failed the
   dd-corrected hard gate and 26% failed the sealed holdout -- roughly
   inverted from the 23:05 UTC run's 40%/60% split, but the same end result
   (zero promotions). Two independent seeds now agree: this isn't a
   seed-specific artifact of one `Researcher` proposal sequence.
   **Recommend not running further seeds of this same scaled-seed
   construction** -- the open question is now which of two structurally
   different things is true: the x6-scaled seed itself is too aggressive
   (4413 search-fold trades, halts 5, fitness -4.296 -- none of which any
   real live 1d champion has ever shown) for this gate to clear from at
   all, or a genuinely retuned (not just scaled) 4h starting point would
   behave differently. That's a bigger experiment than another
   same-seed-genome run and wasn't attempted this session.

   **Ruled out 2026-08-31 (3-hourly check, ~04:07 UTC): two un-scaled
   bar-count harness constants are not the explanation -- see "Current
   state" above and
   `runs/2026-08-31-0407-4h-shadow-warmup-cooldown-ruled-out.md`.** Tested
   `run_backtest`'s `warmup=60` default and `constitution.
   CIRCUIT_BREAKER_COOLDOWN=20`, both of which the x6-period-gene-scaling
   recipe never touched, against their own x6-scaled values (360, 120) on the
   same seed genome and data. Neither changed fitness, trade count, halt
   count, or drawdown beyond noise (fitness -4.30 to -4.32 vs. baseline
   -4.296). Reframes the still-open question from "might this be a harness
   artifact" to a cleaner "the seed is genuinely this aggressive on its own
   terms" -- strengthens rather than settles hypothesis 1, and still leaves
   hypothesis 2 (a genuinely hand-retuned, not scaled, 4h starting point) as
   the next real experiment, not attempted here.

   **Found 2026-08-31 (3-hourly check, ~07:05 UTC): the overtrading mechanism
   is entry frequency, not faster round-trips, and a new candidate confound
   is tested and ruled out -- see "Current state" above and
   `runs/2026-08-31-0705-4h-shadow-entry-frequency-diagnostic.md`.** Three
   single-shot `run_backtest()` calls (v3 at 1d, x6-scaled seed at 4h,
   raw-unscaled seed at 4h -- no evolution needed) found the x6-scaled seed
   trades 4.6x more often per year than v3 but holds each position for a
   similar-or-longer time (10.71 vs 9.09 days) -- many more distinct entries,
   not quicker exits. Then tested `superior_judge.max_new_positions_per_bar`
   (seed value 3, a per-*bar* cap never touched by any x6-scaling recipe --
   at 4h it's up to 18 new positions/day vs the 1d-intended 3/day): tightening
   it to 1 moved every metric by noise-scale amounts only. **Ruled out**, same
   shape as the 04:07 UTC warmup/cooldown result. Sharpens hypothesis 2 into
   something concretely scoped for the next session: the consult *threshold*
   genes (RSI bands, z-score bands, `min_trend`/`min_breakout`/`min_rank_mom`)
   were never touched by any scaling or hand-tuning attempt so far -- widening/
   tightening those specifically, independent of period scaling, and
   re-measuring trade frequency the same way, is the recommended next concrete
   step, not another same-construction run or a from-scratch full hand-retune.

   **Tested 2026-08-31 (3-hourly check, ~10:02 UTC): tightened nine consult
   threshold genes as recommended -- trades/yr dropped as predicted but
   drawdown got worse, not better -- and this session's baseline didn't
   reproduce the 07:05 UTC session's baseline, an unresolved discrepancy.**
   See "Current state" above and
   `runs/2026-08-31-1002-4h-shadow-threshold-tighten.md`. Tightened
   `min_rank_mom`/`rsi_max`/`min_breakout` (consult_risky), `min_trend`/
   `rsi_lo`/`rsi_hi`/`min_rank_mom` (consult_moderate), `rsi_buy_below`/
   `z_buy_below` (consult_conservative) on the x6-scaled seed. Trades/yr:
   392.7 -> 327.8 (-16.5%, confirms the noise-threshold hypothesis
   qualitatively), but max_dd -44.3% -> -48.0% (worse), halts 6 -> 8,
   sortino 0.94 -> 0.76, sharpe 0.77 -> 0.65 -- fewer entries did not mean a
   shallower drawdown. **Ruled out "just tighten the thresholds" as a
   free-lunch fix** (one specific combination/direction tried, not
   exhaustive). Separately and more sharply: this session's own baseline for
   the *same* x6-scaled seed construction (392.7 trades/yr, -44.3% max_dd,
   sortino +0.94) doesn't match the 07:05 UTC session's recorded baseline
   (1278 trades/yr, -66.1% max_dd, sortino -0.29) -- checked and ruled out
   gene-construction mismatch (full genome dump verified gene-by-gene
   against the documented x6 recipe), data gaps (clean 8766-bar/symbol
   fetch, no warnings), and `run_backtest`'s `warmup` default (60 vs. 360
   moves the baseline by noise only, ~393 vs ~406 trades/yr). No RNG is
   reachable from a plain `run_backtest()` call, ruling out non-determinism
   too. Neither session's scratch script was committed, so a direct diff
   isn't possible after the fact. **Recommend a future session commit a
   small, never-scheduled, reusable scratch harness for this specific
   recipe** (build x6-seed, fetch 4h universe, single-shot full-history
   `run_backtest()`) so results become diffable and this class of
   cross-session discrepancy stops recurring silently -- and treat any
   single prior 4h-shadow baseline number with more caution until then.
   `git status` clean, `live_state.json` md5 unchanged
   (`37a1b00bee3f7cb1ad2f4adde0ab9ed0`), `python3 -m pytest -q` 243/243
   confirmed at session start, no code changed, genome still v3 (1d).

   **Shipped 2026-08-31 (3-hourly check, ~12:47 UTC): the recommended reusable
   scratch harness — see "Current state" above and
   `runs/2026-08-31-1247-shadow-4h-harness.md`.** `tools/shadow_4h_x6_seed.py`
   commits the x6-scaled-seed recipe as one importable function
   (`build_x6_scaled_seed`, via `Genome.child()`) plus a CLI that fetches the 4h
   universe and runs one single-shot full-history `run_backtest()`, so every
   future session gets the same genome construction instead of re-deriving it
   from this thread's prose. 9 new hermetic tests (no network) check the
   scaling math and leave-untouched genes; a live run against warm-cached data
   reproduced the 10:02 UTC session's baseline exactly (392.7 trades/yr, -44.3%
   max_dd, sortino 0.94), which is strong evidence the 07:05-vs-10:02 gap was a
   real construction difference in an uncommitted script, not noise — though
   without that script the exact divergence stays unrecoverable. Use this
   harness, not a fresh scratch script, for the next variant test (correlation
   penalty on the x6-scaled seed is the standing suggestion from 07:05 UTC).

   **Isolated 2026-08-31 (3-hourly check, ~16:00 UTC): the 10:02 UTC combination's
   worse-drawdown result was driven by `consult_risky`/`consult_moderate`, masking a
   quietly-positive `consult_conservative`-only result — see "Current state" above and
   `runs/2026-08-31-1600-4h-shadow-isolate-consult-threshold.md`.** Also caught: the
   07:05/10:02/12:47 UTC sessions' carried-forward "test correlation_penalty next"
   suggestion pointed at a gene fully removed 2026-08-20 (item 3, closed) — corrected
   here so a third session doesn't repeat it. `consult_conservative`-only tightening
   (`rsi_buy_below` 38→30, `z_buy_below` -0.8→-1.2) moves trades/drawdown by noise only
   but beats baseline on sortino (0.94→1.02) and sharpe (0.77→0.85) — the only one of
   four isolated variants that improves on baseline at all. Recommended trying this as
   its own starting point combined with something that attacks drawdown directly.

   **Found 2026-08-31 (3-hourly check, ~22:07 UTC): that combination — done. Pairing
   `consult_conservative` tightening with trailing-stop tightening is super-additive and
   clears `MAX_DD_HARD_FAIL` outright, the first variant in this thread's history to do
   so — see "Current state" above and
   `runs/2026-08-31-2207-4h-shadow-consv-trailing-synergy-clears-dd-gate.md`.**
   `consv1` (the 16:00 UTC variant) + `risk.trailing_stop` -0.06 (seed -0.15): -32.7%
   max_dd, sortino 1.35, sharpe 1.09 — best risk-adjusted numbers this thread has ever
   recorded. `consv1` + `trailing_stop` -0.08 + `cash_floor_pct` 0.15: -35.1% max_dd,
   fitness +0.146 — first positive full-history fitness this thread has recorded.
   Neither lever alone gets close (best single-lever result: `trailing_stop` -0.08 alone,
   -39.3%, barely clears). Also found: pushing `consult_conservative` past `consv1` has
   zero further effect (ruling out that as a lever), and `stop_loss`/`max_position_pct`
   tightening both make drawdown worse. Not yet run through the real promotion pipeline
   (fold-aggregate acceptance + sealed holdout) — only a single full-history backtest,
   same measurement every prior session here used. **Recommend a future session seed a
   fresh 4h shadow `EvolutionRun` from this genome** (instead of the plain x6-scaled
   seed) and check whether it survives fold-aggregate acceptance and the sealed holdout
   as a champion in its own right — this thread's first real candidate worth running
   through the full pipeline.

