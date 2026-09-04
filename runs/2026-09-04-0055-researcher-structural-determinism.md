# Researcher structural-determinism check — 2026-09-04 00:46-01:xx UTC

- Daily bar already handled: `live_state.json`'s `updated` timestamp
  (2026-09-04T00:28:51+00:00) and `runs/2026-09-04-0020-daily-trading.md`
  both confirm tick 21 ran cleanly at 00:20 UTC (NAV $11,943.57, held, no
  trade). Nothing to do for live trading this cycle.
- `git_sync.py` (shipped last cycle) fast-forwarded cleanly with no
  divergence this time — one more clean data point for that fix.

## What this cycle did

The 2026-09-02/09-03 4h-shadow-evolution thread (AGENTS.md item 2) ran five
fresh `EvolutionRun`s (seeds 9101/9102/9104/9105 + one more) against the same
unpatched `x6` seed champion. Three of those sessions' generation 1 produced
what run notes called "the exact same candidate" — a `remove_agent` patch
disabling `consult_moderate` — clearing the real fold-based
`MAX_DD_HARD_FAIL` gate with fold fitness identical to four decimal places,
then failing the sealed holdout each time. Every entry describing this called
it "suggestive" that the recurrence was structural rather than a fresh
independent finding, but nobody had actually verified that against the code.

`agents.researcher.Researcher.propose()`'s own docstring already states the
mechanism: "Without [exclude], the diagnosis-driven and structural proposals
are deterministic given the champion, so an unbeaten champion gets the
identical losing candidate re-tested every single generation." That's
exactly why `exclude`/`researcher_memory` exists. Nothing in the test suite
exercised this claim directly.

New `tests/test_researcher_structural_determinism.py` (6 tests, all passing):

- `structural()` and `from_diagnosis()` return byte-identical proposal sets
  across arbitrary RNG seeds for the same champion/diagnostics — only
  `perturb()` (blind search) varies with seed.
- `structural()` always proposes `remove_agent` for every currently-enabled
  consult agent (`consult_risky`/`consult_moderate`/`consult_conservative`).
- A fresh `propose()` call with no `exclude` set — exactly the starting
  condition of every from-scratch shadow `EvolutionRun` in this thread — is
  *guaranteed*, not merely likely, to re-propose removing `consult_moderate`
  at generation 1, regardless of seed (checked against 9102/9104/9105
  directly plus a control seed).
- `exclude`ing that proposal's key removes it from the next `propose()` call,
  confirming the fix already in the codebase actually works as documented.

## What this changes

The existing "5 seeds/9 generations, 3 fold-clears, 0 holdout-clears" tally
in AGENTS.md counted the 3 fold-clears as 3 independent data points. They are
one deterministic proposal recurring three times, purely because each shadow
session started a memory-less `EvolutionRun` instead of carrying
`researcher_memory` forward across seeds. Real independent search evidence
from option (i) — new, non-guaranteed candidates actually clearing the fold
gate — is closer to 0 than 3. This sharpens (does not reverse) every prior
session's recommendation to treat option (i), "more generations/seeds," as
exhausted for the `x6` recipe.

This does **not** decide item 2's accept-vs-redirect fork (accept the full
`consv1 + trailing_stop + ramp` stack and move toward a real promotion
attempt for this genome family, vs. redirect effort to item 4/5/6) — that
stays the owner's call, already flagged explicitly in the 2026-09-03 09:00
UTC daily discussion. A sixth fresh `x6` seed was deliberately not run this
cycle; this session verified the existing evidence instead of adding a data
point the recommendation already says isn't worth collecting.

## Verification

- `python3 -m pytest -q`: 351/351 (was 345, +6 new).
- `tools/edit_bundle_module.py sync --check`: clean (test-only change, no
  `_SRC` module touched).
- `md5sum live_state.json`: `81aa743fa71f116be9ba8dbf91d3de96`, unchanged
  before/after.
- No protected file touched, no constitution amendment, genome still v3
  (1d) live and untouched.
