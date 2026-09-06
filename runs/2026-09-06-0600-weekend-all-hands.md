# Weekend all-hands — 2026-09-06 06:00 UTC

Deep-focus weekend session. No live trading this cycle (tick 23 already
handled at 00:20 UTC, confirmed via `live_state.json`'s `updated` timestamp
and `runs/2026-09-06-0020-daily-trading.md` before starting) — deliberately:
weekend sessions are for evolution/self-improvement depth, not day-to-day
trading.

## What was decided, and why

**Freshness pass before committing to an action.** Before running anything,
re-checked whether the picture from the last several 3-hourly cycles had
moved: `review-hard-calls` still 0 pending, `live-benchmark` unchanged
(-11.07% excess, 22 bars, nowhere near item 0's 60-bar revisit trigger),
`holdout-pressure` and `margin-curve` both re-confirmed their
already-understood, already-closed shape (fold-aggregate margin nearly
saturated at today's candidate count; holdout margin still on the steep part
of its own curve). Items 2 (4h-bar shadow evolution), 5 (short selling), and
6 (equities/FX) remain genuinely blocked on an owner decision, unchanged
since the last several sessions flagged them. Nothing new was unblocked, so
the highest-value unblocked activity remained plain real-`evolve` search
against the live v3 champion — same reasoning as every recent weekend/
3-hourly session that reached the same conclusion.

**A concurrent session's fix changed the picture mid-session.** Partway
through committing the first evolve batch, `git push` was rejected — a
different session (also running this morning, presumably the 3-hourly check
firing around the same 06:00 UTC window) had landed `b73c243`: a real fix to
`Researcher.perturb`'s boldness-driven widening, which was silently
saturating into "always fully randomize the entire genome" past boldness
~92, with zero local exploitation left for 40+ generations. The live
champion's boldness counter was already at 134 going into this session (now
184). This was directly relevant enough to change plan: rather than running
a third identical-shaped batch, this session ran its second 25-generation
batch specifically under the *fixed* code, to see whether restored local
search changed anything real for a champion this deep into saturation.

Result: still no promotion, champion fitness held flat at 1.215 across both
batches (50 generations total, cumulative candidates 1904 → 2602). But one
observation worth tracking rather than dismissing as noise: raw fold-fitness
beat the champion's own 1.215 in 17 of 25 generations in the post-fix batch,
versus 12 of 25 in the pre-fix batch — same champion, same day, only the
search code differed. This is consistent with the fix doing what it was
built to do (more competitive local candidates, not just wide misses), but
n=25 per batch is nowhere near enough to call this settled on its own. Noted
in AGENTS.md as something to watch across the next several batches, not
claimed as proof here.

## The bug found along the way

Running `python3 -m pytest -q` after the second evolve batch turned up a
real failure: `test_reconstructed_v3_matches_real_live_lineage_bit_exact`,
which replays `live_state.json`'s own recorded `lineage` to rebuild the live
genome and checks it matches exactly. It didn't — the rebuilt genome came
back as version 2, not 3.

Tracing it down surfaced two separate, real bugs, both now fixed and tested:

**Bug 1 — lineage truncation drops old promotions.** `LiveAccount.save()`
wrote `"lineage": self.lineage[-200:]`, a bare trailing-window cap. Lineage
entries are almost all per-generation telemetry (thousands of them over the
account's life, fine to cap), but a handful are `accepted` entries — the
only durable record of a real promotion's patch. There have only ever been
two: v1→v2 and v2→v3. Once 200+ generations have run since a given
promotion, a plain trailing cap drops it — which is exactly what happened:
the v1→v2 patch, recorded 2026-08-16, had scrolled off by the time this
session's second evolve batch pushed the account past its 200-generation
window for the third time (v1 has been superseded for a while; the account
has now run 135+ generations against v3 alone). Every diagnostic that
reconstructs a historical champion from lineage — `fold-scheme
--also-version N`, `succession-audit`, `promotion-excess-check`,
`holdout-pressure`'s per-champion tally — silently degrades once this
happens, because the reconstruction chain has a gap it can't detect (no
error is raised; it just produces a genome with the wrong genes and a
mismatched `.version` attribute, as the failing test caught).

Fix: `core.live._trim_lineage()` keeps the same 200-entry recency window as
before, but pulls out and preserves any `accepted` entry that would
otherwise have been dropped, regardless of where it sits in the list. The
lost v1→v2 record itself was recoverable this time — a prior commit
(`aaee44e`, pushed earlier this session, before the second batch) still had
it in full — so it was reconstructed by replaying that commit's lineage plus
this batch's newly-appended entries through the fixed trim function, and
written back. Nothing was permanently lost. But this was luck: had this
bug gone unnoticed for longer, or had the losing commit already been
squashed out of recent history, the v1→v2 patch would have been gone for
good, with no way to answer "what genes did v2 actually run with" ever
again. 6 new tests in `tests/test_live_account.py`, including one that
reproduces the exact bug scenario and one that checks `save()` itself uses
the fixed function rather than a bare slice.

**Bug 2 — reconstruction's "seed" isn't always the seed.**
`_reconstruct_champion_genome`'s version-1 base was `Genome.champion()`,
which — per its own implementation — loads whatever
`state/genomes/champion.json` currently holds on disk, falling back to the
true hardcoded seed only if that file doesn't exist yet. The `evolve`
command calls `g0.save("champion")` unconditionally at the very start of
every run (so it can diff `Genome.champion()` before and after to detect
whether a real promotion happened) — which means it overwrites
`champion.json` with the *live* champion's genes every single time `evolve`
runs, whether or not anything gets promoted. So any reconstruction-based
diagnostic run in the same container *after* an `evolve` call was silently
rebuilding every requested historical version from the live champion's own
genes instead of the true v1 seed. A recorded patch only overwrites the
specific gene paths it names, so any gene a given promotion's patch never
touched still leaked in from the wrong (live-champion) base — meaning this
wasn't just "version 1 is wrong," it was "every reconstructed version is
wrong in every gene no patch explicitly touched."

This was directly visible once looked for: running `succession-audit`
against the real repo (in this same container, after this session's own two
evolve batches had already overwritten `champion.json`) reported
byte-for-byte identical fold-aggregate fitness, dd-corrected fitness, maxDD,
and excess return for v1, v2, *and* v3 — a result that should have been an
immediate red flag on its own (three genuinely different genomes producing
identical six-decimal backtest output is not plausible), but nothing in the
existing tooling would have caught it without today's test failure pointing
at the reconstruction path specifically.

Fix: use `Genome()` (the bare constructor, always the hardcoded
`SEED_GENOME`, no disk I/O, no dependency on what any other command may have
written to disk earlier in the session) for the version-1 base instead.
Applied to both copies of this function — `evotrader_bundle.py` (the live
path) and `run_from_files.py` (the not-yet-wired read-only entrypoint),
since they're hand-duplicated on purpose (`_reconstruct_champion_genome`
isn't part of any `_SRC` module the bundle-sync tooling covers). 2 new
regression tests in `tests/test_fold_scheme_reconstruction.py` populate a
deliberately-polluted `champion.json` (fake version-3-shaped genes) before
calling the reconstruction function, and assert version 1 comes back as the
true seed regardless — reproducing the exact failure mode directly rather
than only via the accidental real-repo state that surfaced it today.

Re-ran `succession-audit` against the real repo after both fixes: v1, v2,
and v3 now come out properly distinct. v1 hard-fails today's dd-corrected
drawdown gate (-54.4% maxDD, -127.7% excess return), v2 doesn't (-38.1%
maxDD, fitness 0.287), v3 (live) doesn't either (-34.1% maxDD, fitness
1.711) — this matches the historical finding this diagnostic was built to
support (2026-08-22: "no real champion currently clears the gate, v2 for a
different reason than v1/v3"), which is reassuring: it means that specific
past finding was very likely computed correctly (probably run in a container
where `evolve` hadn't run yet that session, or a fresh one), not silently
wrong the whole time.

**What this means for reading older entries in this file.** Any past
session's `fold-scheme --also-version N`, `succession-audit`,
`promotion-excess-check`, or similar reconstruction-based diagnostic result
*could* have been silently wrong, specifically if that session had already
run `evolve` earlier in the same container before running the diagnostic.
There is no record anywhere of each past session's exact command order or
whether its container's `state/genomes/` was already polluted at the time,
so a blanket re-audit isn't practical and wasn't attempted here — most
individual findings in this file are corroborated by more than one signal
anyway (the succession-audit spot-check above being one example of a
finding that checks out). This is flagged so a *future* session treats any
one specific old `--also-version` number it actually needs to rely on as
worth a fresh, cheap re-run rather than an inherited fact — not so this
becomes its own standing audit project.

## Verification

- `python3 -m pytest -q`: 355 (session start baseline) → 358 (after
  `b73c243` landed) → 366/366 (after this session's two new test files'
  worth of additions). No regressions at any step.
- `tools/edit_bundle_module.py verify`: round-trip clean after the
  `core.live` sync.
- `tools/edit_bundle_module.py sync --check`: bundle matches real files.
- Constitution checksum `8b74865634b1db07` unchanged throughout — neither
  fix touches the checksummed surface (`core.live`, and the bundle's own CLI
  helper functions, are not part of it).
- `live_state.json` diffed key-by-key after each evolve batch: only
  `updated`/`lineage`/`researcher_memory` changed; `genome`/`broker`/
  `journal` byte-identical. The lineage repair itself was verified by
  re-running the previously-failing test and confirming
  `_reconstruct_champion_genome(3, ...)` now matches the live genome
  field-for-field.
- Dashboard (`index.html`) rebuilt after both evolve batches and the
  lineage repair; genome challenger-tally tile confirmed showing 2602.

## What's next

- Genome still v3 (1d) live, untouched — no promotion this session.
- Items 2/5/6 remain the owner's call, no new input this session.
- Keep an eye on the raw-fold-fitness-beats-champion ratio (17/25 post-fix
  vs. 12/25 pre-fix this session) across the next several evolve batches —
  one before/after pair is suggestive, not conclusive, that the
  boldness-saturation fix is restoring real local search quality.
- No re-audit of historical `--also-version`/`succession-audit` findings is
  queued — only re-run one if a future session actually needs to rely on
  its specific number for a decision.
