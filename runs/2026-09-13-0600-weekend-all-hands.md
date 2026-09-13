# Weekend all-hands — 2026-09-13 (~06:00-07:20 UTC)

Two threads this session: a structural finding on item 5 (short selling)
that needed writing up and testing before anyone attempts Phase 2 wiring,
and a deep real `evolve` batch that turned out to answer a question the
last three 3-hourly sessions had been flagging but not chasing down.

## 1. Item 5 landmine: `open_positions` sign semantics aren't ready for a real short

Item 5's Phase 1 (`PaperBroker.short()`/`.cover()`) shipped 2026-09-08 with
owner sign-off, but nothing in the live path calls it yet — "whether/how the
Researcher should be allowed to propose short positions" (Phase 2) was left
an explicitly un-scoped question. Picking that up seemed like the
higher-value use of a deep session than another routine evolve batch alone,
so the first hour went into scoping it properly before touching any code
that would need a constitution re-seal.

Reading `core/portfolio.py`'s already-shipped `position_weight()`
(`qty * price / equity`) against the fact that a short's `qty` is negative
by the signed-qty convention documented there, it was immediately obvious
this method already returns a *negative* weight for an open short. Verified
directly rather than trusted from reading:

```
b.short("t0", "XUSDT", 1000.0, 100.0)
b.position_weight("XUSDT", {"XUSDT": 90.0})  # -> -0.089
```

That weight flows unmodified into `Briefing.open_positions`
(`loop/engine.py`'s `weights = {s: b.position_weight(s, prices) ...}` into
`agents/analyst.py`'s `brief()`). Grepping every reader of
`open_positions` turned up eight call sites across all three consults and
both judges that assume a non-positive weight means "flat" — true today
only because nothing has ever called `.short()` in the live path. Built
five tests (`tests/test_short_position_sign_landmine.py`) against the real
Phase 1 broker mechanics (not hand-typed weights) to check whether this is
actually load-bearing, not just theoretically wrong:

- A shorted symbol is invisible to `RiskJudge`'s and `SuperiorJudge`'s
  `max_positions`/`hard_max_positions` slot counting (`sum(w > 0)` reads a
  negative weight as zero positions used).
- `RiskJudge`'s buy-sizing cap `max_position_pct - held_w` actually *grows*
  for a shorted symbol instead of shrinking, because subtracting a negative
  number adds room.
- `ConservativeConsult`'s (and the other two consults') exit check
  `held = ... > 0` never fires for an open short, so a consult has no way to
  reason about closing a short position it should be watching.
- The sharpest one: `SuperiorJudge`'s hard concentration cap,
  `room = (hard_cap - held) * equity` — documented as the one gate that's
  supposed to be a hard, non-tunable limit — actually *loosens* past
  `hard_max_position_pct * equity` for a symbol that already carries
  directional risk. Confirmed: with `hard_max_position_pct = 0.35` and a
  short weight of about -0.10, the computed room came out around 0.45x
  equity, not 0.35x.

All five tests pass against today's code (they document current behavior,
they don't change it) and the full suite is 396/396 (391 baseline + 5 new).
Neither `core/portfolio.py` nor `constitution/__init__.py` — the two
checksum-protected files — needed touching for any of this, so no re-seal
was required; manifest is unchanged at `726dfa4bac85891a`.

**Why this matters for whoever picks up Phase 2 next**: the original
2026-08-30 design pass scoped Phase 2 as "genome/agent wiring" across five
files. That framing is accurate but not sufficient — wiring the *routing*
of short/cover intents through `RiskJudge`/`SuperiorJudge` before fixing
these eight sign-unaware read sites would ship a live regression in the one
gate that's explicitly meant to be a hard safety limit, the first time any
genome or Researcher proposal actually opens a short. Fix direction is
straightforward (sign-aware exposure/slot accounting, explicit
`is_long`/`is_short` helpers) and doesn't touch either protected file, so it
needs no additional sign-off — only the separate, still-open constitution
question (does `MAX_DD_HARD_FAIL` need a short-specific instrument given
unbounded downside) still waits on the owner. Recorded in AGENTS.md item 5
as the concretely-scoped next step, commit `5c680cc` (pushed before the
evolve batch below finished, so it wouldn't sit uncommitted through a long
run).

Deliberately not attempted this session: actually wiring the fix or any
consult-side bearish logic. That's real strategy design (how should
`RiskyConsult`/`ConservativeConsult`/`ModerateConsult` decide to short
something, mirroring but not identical to their existing long entry logic)
and deserves its own session rather than a tail-end addition to a landmine
write-up.

## 2. 45-generation real `evolve` batch — and the "third consecutive lively batch" question resolved

The last three 3-hourly sessions (00:46, 01:20-ish note, 03:46-04:13 UTC
today) had each flagged their batch as livelier than usual — raw
best-of-generation fold-fitness beating the champion's own fitness in
14/15, then 15/15 generations — and the 04:13 note explicitly said: "if a
third consecutive batch repeats the pattern, that's the point to look
closer (e.g. `fold-date-sensitivity`) rather than just logging it again."

This session ran a 45-generation batch (via `tools/background_runner.py`,
`start` + backgrounded `wait`, ~62-minute real run, exit code 0, no
truncation) as this weekend's deep search pass, and it became exactly that
third data point — more extreme than either prior one:

- Champion's fold-aggregate fitness held flat at **1.057** across all 45
  generations (965 trades, win 39%, stops 1%, halts 3 — unchanged).
- Raw best-of-generation fold-fitness beat the champion's own 1.057 in
  **41 of 45 generations** (91%), tied in 2, lost in 2.
- Cumulative candidates tried against v3 rose 13755 → 14380 (+625),
  boldness/stagnation counter climbed accordingly.
- `holdout-pressure` draw count rose from 284 to **310** (+26 new losing
  draws), margin unchanged in shape (~6.77). Every fold-aggregate-clearing
  candidate still lost its own sealed-holdout draw — no promotion.

Given three consecutive batches all showing this and the third being the
most extreme yet, this was the point to actually run
`fold-date-sensitivity` rather than flag it a fourth time. Result
(`runs/fold_date_sensitivity_0913.log`):

```
shift  as-of        aggregate_fitness
  0    2026-09-13    1.057
  1    2026-09-12    1.508
  2    2026-09-11    1.656
  3    2026-09-10    1.469
  4    2026-09-09    0.977
  5    2026-09-08    1.590
  6    2026-09-07    1.422
-> range [0.977, 1.656], spread 0.679 across a 7-day as-of window
```

**This resolves the question, and the answer is mundane rather than
alarming**: today's champion fold-aggregate fitness (1.057) sits near the
bottom of a 7-day range that swings as high as 1.656 purely from the
trailing 4-year evaluation window sliding by a few days — the same
day-to-day drift AGENTS.md has already documented elsewhere as expected.
The "beat the bar" ratio a batch reports is measured against *today's*
specific fitness number, so on a day where that number happens to be
unusually low relative to its own week, more random candidates will clear
it by construction — without needing the search to have actually found
anything better than it would find on a higher-fitness day. Three
consecutive lively batches are explained by three consecutive days sitting
on the low side of this window's natural range (1.508 → 1.057, with today
the lowest of the last 7 shifts except one), not by a change in what the
Researcher is finding or a problem with the champion. `holdout-pressure`'s
unchanged margin shape across all of this is consistent evidence pointing
the same way — nothing about the sealed-holdout comparison moved either.

**Conclusion for future sessions**: a livelier-than-usual "beat ratio" on
any single batch is not on its own informative about search quality or
champion staleness — it should be read next to that day's own
fold-aggregate fitness relative to nearby days (a quick
`fold-date-sensitivity` check, ~a few minutes, same cost class as
`fold-scheme`), not treated as a trend worth escalating by itself. Don't
re-run this same check reflexively on every lively batch going forward —
the mechanism is now understood and documented here; only worth repeating
if a batch's beat ratio is unusual **and** its fold-aggregate fitness is
*not* an obvious recent-window low (i.e., the fitness explanation doesn't
apply and something else would need to).

Verified before commit: `python3 -m pytest -q` 396/396 both before
(baseline, already includes the 5 new landmine tests from part 1) and after
`evolve`; direct top-level key diff of `live_state.json` showed only
`lineage`/`researcher_memory`/`updated` changed (genome, broker, journal
byte-identical); constitution verified `726dfa4bac85891a` unchanged
(manifest md5 identical); `tools/edit_bundle_module.py verify`/
`sync --check` both clean; dashboard rebuilt (`index.html`). Genome still
v3 (1d) live, untouched. No live trading this session (tick 30 already
handled at 00:20 UTC well before this session started).
