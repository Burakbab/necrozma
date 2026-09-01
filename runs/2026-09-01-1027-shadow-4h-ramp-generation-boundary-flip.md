# A fresh generation() against the 120/0.20 ramp champion, and a same-day boundary-shift flip that undercuts the 08:08 UTC "fix" headline

**3-hourly check, ~09:46-10:27 UTC.** Today's daily bar was already handled
by the 00:20 UTC run (`live_state.json` `updated` 00:22:17 UTC, confirmed
by the 09:00 UTC daily-discussion note) — no trading this cycle.

Direct follow-up to the 08:08 UTC grid-search session's own flagged next
step (AGENTS.md item 2): *"no fresh `EvolutionRun.generation()` has run
against the new 120/0.20 point as champion yet... the natural next check,
mirroring what the 04:18 UTC session did for 120/0.10."*

## What was built

`tools/shadow_4h_ramp_generation.py`: runs real `EvolutionRun.generation()`
calls against `build_consv_trailing_ramp_seed()` (now 120/0.20), seed 9002
(distinct from the 04:18 UTC session's 9001). Prints every generation's
`record["top"]` (the per-candidate patch list), which the 04:18 UTC
session's own script never captured — that session could only say "whether
any of the 34 proposals touched either new gene is unknown." This script
flags it directly. Never touches `live_state.json` (`EvolutionRun.generation()`
only appends to the gitignored `state/lineage.jsonl`). 6 new hermetic tests
for the gene-touch-detection helper, no network involved. Committed
separately (`c4471b0`) before running it.

## Result: champion "held" — but because it, and most challengers, now hard-fail the drawdown gate

3 generations, `n_blind=6`, ~24 min wall clock, 28 proposals tried
cumulatively. Champion held every generation (best challenger selection
fitness 0.598 / 0.718 / 0.422 vs. champion's own -2.422) — matching the
04:18 UTC session's qualitative shape (champion survives a generation of
blind proposals). **But this run's champion selection fitness (-2.422) is
nothing like the 08:08 UTC sweep's reported 0.454 for the identical 120/0.20
genome, or even the 04:18 UTC session's 0.467 for 120/0.10 — it matches the
*pre-ramp broken baseline* number instead.**

Traced this directly (not just from the generation log): re-ran
`Evaluator(data).evaluate(g, folds=folds)` on the exact 120/0.20 genome by
hand, twice in the same process (deterministic, identical both times:
-2.422190578603439). `dd_corrected_stats` on it: fold 1 (the middle fold,
`[0.283, 0.567]`) max_dd -43.4%, hard-failing `MAX_DD_HARD_FAIL` (40%) —
the exact same fold this whole thread has been fighting since 01:14 UTC,
now failing again on the genome that was supposed to have fixed it.

**This is very likely the already-documented fold-boundary-shift artifact
(`fold-date-sensitivity`'s own notes: "the `history-perturb
--boundary-shift` day-1-allocation artifact... has [bearing] on real
promotion decisions"), not a new bug or a market crash.** The data loaded
this session runs to 2026-09-01 08:00 UTC (8766 4h bars); the 08:08 UTC
sweep most likely ran against data ending 2026-09-01 04:00 UTC (fetched once
near the start of its ~65 min run, before the 08:00 bar closed) — one extra
bar out of 8766. Fold 1 is the *middle* fold, `[0.283, 0.567]` as a fraction
of the *whole* dataset, so appending one bar at the very end shifts every
fold's absolute bar-index boundary by up to one bar via rounding —
unrelated to the actual price move in that new bar (checked: BTCUSDT's
08:00 UTC candle was a normal ~-0.9% four-hour move, nothing dramatic).
A boundary landing one bar differently inside or outside a local
crash/recovery is enough to move a fold's own max_dd by double digits when
the fold is already sitting close to a peak-to-trough extreme, which fold 1
evidently still is here.

**Why "no proposal cleared the bar" is not really informative this run**:
`accepts()`'s very first check is `if f_chal == float("-inf"): return False`
— a challenger whose own `dd_corrected_stats` also lands over 40% on fold 1
is auto-rejected regardless of how much higher its *selection* fitness
scored, before the margin/regression checks even run. Since fold 1's
cold-start vulnerability is structural (tied to that fold's own opening
bars, not to genes most blind mutations touch), most of this generation's
proposals likely hard-fail the same way the champion now does — this
wasn't really a fair test of "does anything beat the ramp fix," it was 3
generations run against a champion that had (for boundary-shift reasons)
quietly stopped clearing the gate itself.

## What this means for item 2

**The 120/0.20 recommendation from 08:08 UTC should be treated as
boundary-fragile, not settled** — it cleared the gate by ~5.4 points of
margin (-34.6% vs. -40% cutoff), which this session's evidence says is well
within the swing a single bar's boundary shift can cause. Recommend: before
trusting any single point-in-time "clears/fails MAX_DD_HARD_FAIL"
measurement on this genome family again, either (a) build a shadow
equivalent of the existing `fold-date-sensitivity` CLI command (which
already answers exactly this question, but only for the live 1d champion)
so this can be checked systematically instead of by two accidental
same-day snapshots landing on opposite sides, or (b) treat "clears the gate
with <10 points of margin" as not yet a real pass for this seed lineage.
Not built this session — flagging as the natural next step, sized for
whoever picks this up next (a `--bar-interval`/genome-builder parameter on
top of the existing `fold-date-sensitivity` machinery, not a new mechanism).

Does not change anything about the *mechanism* the cold-start-ramp gene
implements (still correctly wired, still a genuine no-op at defaults, still
tested) — only about whether 120/0.20 specifically should be trusted as
"the" point for this genome, given how close to the cutoff it sits.

`live_state.json` untouched throughout (md5 `1b5e230bb4e7440ed8fd7778425f8ea9`,
unchanged from the 04:18 UTC note), constitution checksum unchanged,
`python3 -m pytest -q` 274/274 (up from 268, +6 new tests for this
session's tool), `tools/edit_bundle_module.py sync --check` confirmed no
drift. Genome still v3 (1d) live, untouched.
