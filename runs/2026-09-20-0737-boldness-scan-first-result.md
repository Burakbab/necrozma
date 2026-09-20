# 3-hourly check — 2026-09-20 ~06:46-07:37 UTC

## Daily-bar freshness check (before doing anything else)

- `live_state.json`'s `updated` timestamp at start of this cycle:
  `2026-09-20T04:08:55+00:00` — from the prior 3-hourly check's own evolve
  batch (`runs/2026-09-20-0411-evolve-batch-v3.md`), not new trading.
- Daily tick 37 already handled at the dedicated 00:20 UTC slot per
  `runs/2026-09-20-0020-daily-trading.md`.
- Container started in detached HEAD again (as usual for this environment).
  `git checkout main && git pull --ff-only origin main` fast-forwarded
  cleanly (`aaee4c8..b40f716`, 21 commits, all already reachable — nothing
  lost).
- Conclusion: no new bar to process this cycle, as expected for a 3-hourly
  firing between daily ticks.

## Freshness checks on the "Next steps" queue

- `review-hard-calls`: "no hard calls pending review (2 reviewed so far)" —
  unchanged, nothing to act on for item 4.
- Items 0/1/3/7/8/9/10/12: resolved/closed/feature-complete/ongoing-passively.
- Items 2/5/6: owner-decided or blocked on an owner data-source decision, not
  a scheduled session's call.
- Item 11 (AGENTS.md rotation): file measured 244,177 bytes before this
  session's edits — still under the 256KB single-read threshold, not due.
- New this cycle: the immediately-prior commit (`b40f716`, landed ~06:15 UTC,
  just before this session started) shipped a `boldness-scan` diagnostic
  (`loop.evolve.boldness_scan`, `tests/test_boldness_scan.py`, 4 new tests,
  full suite 426/426 at ship time) but never ran it for a real result, and
  never added it to this file's Commands list. Rather than another routine
  15-gen `evolve` batch (the pattern for roughly the last dozen 3-hourly
  cycles with nothing else queued), this session closed that gap: documented
  the command in `AGENTS.md` and ran it for its first real result.

## What ran

`python3 evotrader_bundle.py boldness-scan` with all defaults (20
generations/arm, `--cap 20.0`, `--seed 7`, `--n-blind 14`, seeded from live
`researcher_memory`: tested=25025, stagnation=1801, holdout_draws=522).
Read-only by contract (never calls `Genome.save()`/`.promote()`/
`EvolutionRun._record()`) — confirmed after the fact via `git status` /
`git diff --stat live_state.json`, both clean.

(Incidental note: the run was actually kicked off by a `boldness-scan --help`
invocation — the command's arg parsing only looks for specific `--flag value`
pairs and doesn't recognize or reject `--help`, so it silently ran the full
diagnostic with defaults instead of printing usage. Not a bug worth fixing
under this session's scope — `--help` isn't a documented flag for any
command in this codebase — but worth knowing if a future session tries
`--help` on any of these expecting it to be free.)

## Result

**UNCAPPED** (mirrors production; effective boldness climbed 1801→1820 across
the 20 generations, tracking the live stagnation counter exactly):
- best-of-generation fold-fitness: 1.618, 2.069, 1.708, 1.889, **4.199**,
  1.833, 1.776, 2.165, 1.728, 2.020, 1.732, 1.869, 1.758, 1.749, 1.701, 2.133,
  1.749, 1.720, 1.436, 1.519 (one outlier generation at 4.199, the rest
  clustered 1.4-2.2)
- fold-aggregate gate clears: **3/20**
- sealed-holdout gate clears (= shadow promotions): **0/20**

**CAPPED at boldness=20** (same seeded Researcher stream, same starting
point, boldness held at 20 every generation instead of climbing):
- best-of-generation fold-fitness: 1.618, 1.728, 2.251, 1.728, 1.338, 1.729,
  1.796, 1.952, 1.729, 2.177, 1.808, 1.728, 2.120, 1.728, 1.728, 1.884, 1.862,
  1.916, 1.785, 2.349
- fold-aggregate gate clears: **4/20**
- sealed-holdout gate clears (= shadow promotions): **0/20**

Both arms: final stagnation counter 1821, final in-memory champion unchanged
at v3.

## Reading it

The hypothesis under test (from `Researcher.perturb`'s own docstring,
arithmetic only until now): once boldness passes ~82, `jump_p` and
`genes_per` are both already fully saturated, so a stagnation counter
climbing into the thousands should search identically to one artificially
capped much lower. This run's gate-clear counts — 3 vs 4 on fold-aggregate,
0 vs 0 on sealed holdout — are close enough on one seeded draw to **support,
not overturn**, that hypothesis: capping boldness at 20 (vs. production's
effectively-unbounded ~1800+) did not produce a meaningfully different search
outcome here.

Caveat worth being explicit about: this is one seed. A 3-vs-4 gap could be
genuine capped-arm noise-tolerance or could just be which candidates a single
RNG stream happened to draw in that generation. `boldness-scan --seed N`
supports re-running at other seeds cheaply (same cost class as this run, no
new code needed) — a natural follow-up for a future session is 2-3 more
seeds to see whether the small gate-clear edge for the capped arm is
consistent or washes out.

## Verification

- `git status` / `git diff --stat live_state.json`: both clean — read-only
  contract held, nothing to diff.
- `python3 -m pytest -q`: 426/426 after the run (matches the count at
  `boldness-scan`'s ship time in `b40f716`).
- `tools/edit_bundle_module.py verify`: not re-run this cycle — no bundle
  edit made, only `AGENTS.md` prose changed.

No genome, broker, journal, or `hard_call_reviews` touched. Genome still v3
(1d) live, untouched. No live trading this cycle (correctly deferred to the
dedicated daily slot).
