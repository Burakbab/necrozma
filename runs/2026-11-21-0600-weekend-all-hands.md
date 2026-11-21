# Weekend all-hands, 2026-11-21 ~06:00-07:00 UTC

## Setup

- `git config user.name "Burk"` / `user.email` to the noreply address (local
  config only).
- Container started in detached HEAD. `git checkout main` +
  `python3 tools/git_sync.py` fast-forwarded cleanly through 38 commits other
  sessions had already pushed since the container was built (through
  `44d475c`), no divergence, no shallow-clone staleness.
- `python3 -m pip install -r requirements.txt -q` (plain `pip3` form worked
  this time, no numpy/pandas split to fix).
- Baseline `python3 -m pytest -q` → 505/505 before any change.
- `AGENTS.md` size at session start: 235,281 bytes — comfortably under the
  256KB single-read threshold. Not archived this cycle.

## Roadmap survey

Read `AGENTS.md`'s "Current state" and "Next steps" in full, plus the most
recent weekend session's own writeup
(`runs/2026-11-15-0841-weekend-all-hands.md`). That session's explicit
closing note: items 5/6/13 are all genuinely blocked on either a human
decision or a different kind of data this container can't supply, and
"running more evolve generations" was flagged as having an "increasingly
well-documented flat return on repetition at this draw count" — it
explicitly asked the next weekend session to check whether an owner
decision had landed before defaulting to that again. Checked: nothing new
in "Owner decisions pending" since 2026-09-08 for items 6/13, and no new
data source for item 5. Confirmed those three remain blocked exactly as
described.

Given that, the highest-value use of this session's deeper time budget
wasn't going to be another large blind `evolve` batch or another variation
inside item 5's already-exhausted OHLCV-confirmation-signal family. Instead,
re-read the full roadmap for anything that had gone stale from simple
neglect rather than being genuinely blocked — and found one: item 0's own
"Measured" record of the live account's real forward-test performance
against buy-and-hold, which nothing had re-checked in over ten weeks.

## Main finding: `live-benchmark` has flipped from -13.21% to +28.20% excess, unchecked for 10+ weeks

`grep -rl "live-benchmark\|excess (live" runs/` shows the last session to
actually run and record this diagnostic was the 2026-09-12 weekend
all-hands, which reported **28 bars, -13.21% excess** (live account behind
buy-and-hold). Nobody re-ran it since — not the 2026-09-19/09-20/09-26/09-27,
10-03/10-04/10-10/10-11/10-17/10-18/10-24/10-31/11-01/11-07/11-08 weekend
sessions, nor any weekday 3-hourly check or daily evaluation in between (none
of those run this command as part of their routine; it's explicitly
descriptive-only and not part of the standard verification checklist).

Ran it fresh this session:

```
LIVE ACCOUNT vs. EQUAL-WEIGHT BUY-AND-HOLD, 2026-08-14 to 2026-11-20 (98 1d bar(s))
                            return   sharpe    maxDD
  live paper account      +26.03%     2.03   -21.6%
  buy & hold (universe)    -2.17%     0.21   -41.6%
  excess (live - b&h)     +28.20%
```

That's a swing of **+41.4 points** over the 70 additional bars since the
last check. Cross-checked against `summary`: end NAV $12,602.84 from $10,000
start, 88 real trades, 31.8% win rate, profit factor 2.04, sortino 3.05,
max_dd -21.6% — all consistent with the benchmark command's own numbers (it
reads the same `nav_history`).

**Checked the genome-purity caveat the tool itself prints** ("the real
journal shows the account traded under genome version(s) [1, 2, 3] across
these bars") rather than taking it at face value — it's technically true but
practically negligible: `Counter(e['genome_version'] for e in journal)` is
`{3: 97, 1: 1, 2: 1}`. Only the account's first two ticks (2026-08-15,
2026-08-16) ran under v1/v2 before the v2→v3 promotion on 2026-08-16; every
other bar — 97 of 99, 98% — ran under the current champion. This is about as
close to a clean single-genome real forward test as this account will ever
produce without a wipe, which neither this nor any prior session has done.

**Checked what's actually driving it, not just the headline number.** Today's
own `signals` output reads "Market read: bear, breadth 0%" for the latest
bar, and the benchmark window's buy-and-hold return is -2.17% — i.e. the
27-symbol universe has been roughly flat-to-down over this exact stretch,
not a runaway bull market the live account could have ridden passively. The
live account's +26.03% in that same window is not beta captured from a
rising market; it came from real entries/exits during a choppy-to-bearish
10-week stretch, which is closer to the kind of environment v1→v2→v3's whole
promotion history has always framed as the actual test ("losing less than
buy-and-hold in a downturn is a start, not a strategy" — this is the first
live window where the account didn't just lose less, it made money while
the benchmark lost money).

**What this does and doesn't mean.** This does **not** overturn the
2026-08-16 "Measured" section's full-4-year-backtest finding that the
champion underperforms buy-and-hold by -28.4% over its entire replay
history — that's a different window (4 years of backtest vs. 98 days of
real trading) and a different kind of evidence (replay vs. real fills).
Both are true at once: the system is still, on its full historical replay,
behind a lazy buy-and-hold; and on its actual live track record so far, in
a real downturn-ish window, it is ahead by a wide margin. Item 1's whole
premise ("accumulate live forward-test data — the only track record not
contaminated by hindsight") is exactly what this result is: the first
genuinely good-looking stretch of that uncontaminated record.

**Checked against item 0's three stated revisit triggers** (the only
documented reason this question would need re-opening): (1) "live account's
trailing excess return still negative after 60 more real trading days with
no narrowing" — not met; it's not negative, it swung sharply positive, so
this trigger specifically does not fire (it was written to catch persistent
underperformance, not reward outperformance); (2) a real promotion where
fitness and excess return disagree at holdout — no promotion happened this
session or recently; (3) a fourth real champion — still v3. **None of the
three triggers fire, so item 0's 2026-08-30 recommendation (status quo, no
fitness-metric change) stands un-revisited by design** — this finding is
new evidence, not a decision point, and is recorded here as exactly that.

**Process gap flagged, not fixed**: this metric went unchecked for over two
months purely because no routine in `AGENTS.md`'s run protocol calls for it
— `review-hard-calls`, `holdout-pressure`, and the test suite are checked
every cycle, but `live-benchmark` isn't part of any session's standard
verification list, so it only gets run when a session happens to think of
it. Recommending (not mandating, since this is a documentation change a
future session can make or skip): weekend all-hands sessions should run
`live-benchmark` as a matter of routine (it's cheap — one `load_universe`
call, no backtest) rather than leaving it to be rediscovered at
unpredictable intervals. Not adding it to AGENTS.md's formal run protocol
this session — that would be a process change worth a deliberate decision,
not a tail-end addition to a session that happened to notice the gap.

## Real evolve batch

With the main finding of the session written up, used the remainder of the
slot for one real, moderate `evolve` batch rather than either a token-sized
one or another oversized one that risks the exact git-push collision the
2026-11-15 weekend session hit (that session's 50-generation run collided
with a concurrent 3-hourly check and had to be discarded). Snapshotted
`live_state.json` first (`researcher_memory.tested` = 128255, stagnation
9303). Ran 20 generations via `tools/background_runner.py start`/`wait` (no
`nohup`/`&`), output captured to a log file from the first byte.

Completed cleanly: exit 0, no truncation. Champion's fold-aggregate fitness
held flat at 1.542 across all 20 generations (921 trades, 37% win, 1%
stops, 4 halts, unchanged throughout). Best-of-generation fold-fitness
ranged roughly 1.253-2.649, never clearing the promotion-margin bar.
Cumulative candidates tried against v3 rose **128255 → 128531** (276 new
candidates); stagnation/boldness counter **9303 → 9322**.

## Verification

- `python3 -m pytest -q` 505/505 both before (baseline) and after the
  `evolve` batch.
- Top-level key diff of `live_state.json` (snapshotted before the batch,
  checked directly in Python against the pre-batch copy): only
  `updated`/`researcher_memory`/`lineage` changed. `genome`, `broker`,
  `journal`, `hard_call_reviews` byte-identical. `lineage` length unchanged
  at 202 (bounded ring buffer, no new promotion attempt recorded).
- `tools/edit_bundle_module.py sync --check` → bundle already matches real
  files, no drift.
- `holdout-pressure` re-checked post-batch: margin rose slightly (7.871 →
  7.872), draw count 2307 → 2311 (four new sealed-holdout draws from this
  batch's fold-aggregate-gate-clearing candidates, all correctly rejected),
  same slow-rise pattern already tracked under item 13, nothing new.
- Dashboard rebuilt with `EVO_STATE` set; `index.html` shows 128531
  challenger idea(s) tried.
- Genome still v3 (1d) live, untouched throughout. No constitution change,
  no `AMENDMENTS.md` row needed. No promotion, so no `README.md` `##
  Status` update needed.
- Checked `git fetch origin main` immediately before this commit for new
  remote commits (the 2026-11-15 collision lesson) before pushing.

## Next

- The live-benchmark result is the thing worth a human actually reading —
  it's the first time this project's real forward-test track record has
  clearly beaten its own benchmark over a meaningful live stretch, in a
  window that wasn't simply a rising market. Nothing to decide here, just
  worth surfacing prominently (done: see `AGENTS.md`'s "Current state" and
  item 0 cross-reference in the same commit as this note).
- Items 5/6/13 remain exactly as blocked as the 2026-11-15 session found
  them. The next weekend session should keep checking for an owner
  decision before defaulting to more `evolve` generations, same as this
  session did — and, now that this gap has been found once, consider
  running `live-benchmark` as a matter of course rather than waiting for
  another multi-month gap to be noticed by chance.
