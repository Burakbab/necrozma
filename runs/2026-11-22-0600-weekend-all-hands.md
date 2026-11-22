# Weekend all-hands — 2026-11-22 ~06:00-07:10 UTC

## Setup

- `git checkout main` + `python3 tools/git_sync.py`: clean fast-forward
  through 50 other sessions' already-pushed commits from the last two
  days (`d5958cf` at session start). No divergence, no shallow-clone
  staleness.
- `python3 -m pip install -r requirements.txt -q`, then a baseline
  `python3 -m pytest -q`: **505/505**, clean.
- `review-hard-calls`: 0 pending (6 reviewed, unchanged).
- `AGENTS.md` size at session start: 240,633 bytes — under the ~252KB+
  range that has triggered archival in recent cycles, not archived this
  cycle.
- `live_state.json` check: champion v3, `researcher_memory.tested`
  130,176 entries, `stagnation` 9443, `holdout_draws` 2327, last `updated`
  2026-11-22T04:11:19Z (the prior 3-hourly check's own evolve batch — no
  new live trading needed this cycle beyond what the daily 00:20 UTC slot
  and the 3-hourly checks already handled).

## What this session worked on

Rather than another routine 15-generation `evolve` batch (the pattern
nearly every 3-hourly check this week has used when nothing else was
queued), this session picked up a specific, overdue re-measurement from
the open-items list: **item 13's `boldness-scan` diagnostic hadn't been
re-run since 2026-09-20/2026-10-10**, and the champion's undefeated streak
has grown roughly 5x since then — `stagnation` 1801 → 9443,
`holdout_draws` 522-523 → 2327, `required_margin()` 7.076 → 7.875. Both
the September boldness-scan runs and the October design pass were
measurements taken at a specific, now-stale point in the search's
lifetime; nobody had checked whether the "boldness isn't the real
bottleneck, the holdout margin is" diagnosis still holds at today's much
higher stagnation level, or whether raising the champion's streak by
another ~7,600 tried candidates had changed anything.

This also fit the session's own mandate well: item 5 (short selling) has
an explicit note from its own 2026-11-08 entry that further scalar-sweep
search inside the existing signal family is "unlikely to be the
highest-value use of a future session's time" without a genuinely new
kind of input (a measured borrow rate, on-chain/order-book data) — checked
whether Binance's futures funding-rate endpoint (`fapi.binance.com`) was
reachable as that new input; it returned HTTP 451 (geo-restricted), so
that avenue is closed for now and wasn't pursued further. Item 6
(equities/FX) is blocked on an owner data-source decision. Item 13 itself
is explicitly "not a scheduled session's call to decide" — but *measuring*
it again, the same way the 2026-10-10 design pass did, is squarely
within a scheduled session's remit, and is the kind of "investigate an
open structural question" work this slot is for.

## What ran

`python3 evotrader_bundle.py boldness-scan --generations 20 --cap 20`
(all other flags at default: `--seed 7`, `--n-blind 14`, seeded from the
real live `researcher_memory`). Backgrounded via
`tools/background_runner.py start`/`wait` (no `nohup`/`&`, per item 9's
standing rule). Took roughly 50 minutes end to end — two full
20-generation shadow searches over the real 27-symbol, 4-year, 1d-bar
universe, double the cost of a normal 20-generation `evolve` batch. The
first `wait` call hit its own 30-minute background-task limit and was
killed; confirmed via `ps`/CPU-time that the actual detached
`boldness-scan` process (PID 887, launched by `background_runner.py
start`, not a child of the killed `wait` wrapper) was still running
untouched, then re-issued `wait` with a longer budget — exactly the
decoupled start/wait behavior `tools/background_runner.py` was built to
provide under item 9, and it worked as designed.

## Result

**UNCAPPED** (mirrors real production; effective boldness climbed
9443→9462, one-for-one with the real stagnation counter):
- best-of-generation fold-fitness: 1.539, 1.760, 1.700, 1.350, **3.229**,
  1.195, 1.307, 1.749, 1.306, 1.798, 2.128, 1.700, 1.447, 1.464, 1.767,
  2.210, 1.355, 1.621, 1.273, 1.289
- fold-aggregate gate clears: **10/20**
- sealed-holdout gate clears (= shadow promotions): **0/20**

**CAPPED at boldness=20** (same seeded Researcher stream, boldness held
flat instead of climbing):
- best-of-generation fold-fitness: 1.452, 1.397, 1.738, 1.673, 0.938,
  1.605, 1.471, 1.458, 1.321, 1.810, 1.850, 1.625, 1.713, 1.386, 1.383,
  1.890, **2.406**, 1.817, 1.373, 1.898
- fold-aggregate gate clears: **8/20**
- sealed-holdout gate clears (= shadow promotions): **0/20**

Both arms: final stagnation counter 9463, final in-memory champion
unchanged at v3 (shadow only — confirmed `git status` and a direct
`live_state.json` md5 both showed no change before/after this run; the
command's own read-only contract, `boldness_scan` never calls
`Genome.save()`/`.promote()`/`EvolutionRun._record()`).

## Reading it

Compared against the two September runs (15-gen: 3/15 vs 2/15 capped
ahead; 20-gen: 3/20 vs 4/20 capped ahead; both at
`stagnation≈1801-1821`), two things changed and one thing didn't:

1. **Fold-aggregate gate clears rose sharply for both arms** (3-4/20 →
   8-10/20) and **the ranking between arms flipped** (capped led in
   September; uncapped leads now). The most plausible explanation isn't a
   boldness effect at all — `fold-date-sensitivity`'s own standing finding
   is that the real `evolve()` fold-aggregate fitness is as-of-date
   dependent, and the trailing-4-year window this command builds (via
   `market.load_universe(..., 4.0)` anchored to "today") has moved by
   about two months since the last check. Read this as the evaluation
   window shifting, not the search or the champion changing character —
   and it reinforces, rather than undercuts, the September run note's own
   caveat that a single-seed gate-clear gap is not strong evidence either
   way about which boldness setting is "better": the direction of that gap
   has now been shown to flip entirely between two otherwise-comparable
   runs.

2. **Sealed-holdout gate clears did not change: 0/20 for both arms, every
   single time this diagnostic has ever been run**, across three
   independent runs (15-gen/September, 20-gen/September, 20-gen/today) at
   stagnation levels spanning nearly an order of magnitude (1801 → 9443).
   This is the number that actually bears on item 13's question. It is new,
   direct evidence — not an extrapolation from `Researcher.perturb`'s own
   docstring arithmetic, and not a re-statement of the 2026-10-10 design
   pass's formula-level analysis — that letting the champion's undefeated
   streak run another ~7,600 candidates longer did not change the
   diagnosis: the bottleneck is still the cumulative holdout margin itself
   (now 7.875, up from 7.076), not the search's exploration width at either
   boldness setting. Nothing about this session's result argues for or
   against any of the three options the 2026-10-10 design pass laid out
   (status quo / rolling window / full reset) — it just confirms the
   premise those options were built on still holds at a materially later
   point in the champion's lifetime.

## Verification

- `git status` / direct `live_state.json` md5 comparison: clean before and
  after — the boldness-scan read-only contract held.
- `python3 -m pytest -q`: 505/505, both the session's baseline run and a
  second run after the diagnostic completed (no code touched either way —
  this was a measurement, not a code change).
- `tools/edit_bundle_module.py sync --check`: not re-run — no bundle
  module was edited this session, only `AGENTS.md` prose.
- No genome, broker, journal, `hard_call_reviews`, or constitution touched.
  Genome still v3 (1d) live, untouched. No live trading this cycle
  (already handled by the dedicated daily slot and the 3-hourly checks
  earlier today).

## Next steps for whoever picks this up

- Item 13 remains the owner's call — this session only re-measured it, it
  did not and should not decide it.
- If `boldness-scan` is re-run again in the future, consider running it at
  a couple of different seeds in the same sitting (`--seed`, cheap to vary)
  since this session's own finding is that single-seed fold-gate-clear
  counts and even their ranking between arms are not stable across time —
  multiple seeds in one sitting would at least separate "noisy within one
  run" from "noisy across runs taken months apart," which this session's
  design could not distinguish.
- Item 5 (short selling): the "measured borrow rate" follow-up this
  session considered is blocked — Binance's futures funding-rate endpoint
  returns HTTP 451 from this environment (geo-restriction), and spot
  margin-rate history needs signed/authenticated access this account
  doesn't have. Not worth requesting a credential for a host that's
  already geo-blocked regardless. If this avenue is revisited, a
  differently-sourced dataset (not a Binance endpoint) would be needed
  first.
