# Evolve batch + holdout-pressure diagnostic — 2026-09-09 ~06:46-07:11 UTC

3-hourly self-improvement check. No new bar to trade: `live_state.json`'s
`updated` timestamp (04:27 UTC going in) and `runs/2026-09-09-0020-daily-trading.md`
confirmed today's daily bar (tick 26) was already handled at 00:20 UTC.
Repo sync: cloud clone started in detached HEAD at `fbf3dfa` as usual;
`git checkout main` + `python3 tools/git_sync.py` fast-forwarded cleanly
(local `main` was stale at `4f15e68`, from 2026-09-04 — nothing discarded).

Freshness checks before running: `review-hard-calls` 0 pending (item 4 has
no real case yet); items 2/6 still blocked per "Owner decisions pending";
item 5's council-wiring question remains un-scoped. With no new engineering
slice ready to pick up mechanically, this cycle ran the standing `evolve`
batch — but also chased the "worth a future session's attention" flag the
last two batches (2026-09-09 00:46-01:19 and 03:51-04:27 UTC, both 100%
fold-clear rate) left in "Current state", instead of just adding a third
data point and moving on.

## The question: why did the fold-clear rate jump to 100%/100%?

Two consecutive batches had every single generation's best candidate beat
the champion's own fold-aggregate fitness — the highest rate this file has
tracked, versus a normal 27-73% range in batches from the preceding several
days. Worth checking whether this is a real search-quality shift (bad) or
an artifact of something else (fine) before just running a fourth batch on
faith.

**Finding: it's fully explained by the champion's own recomputed
fold-fitness collapsing, not by candidates getting better.** The existing
`holdout-pressure` diagnostic (reads `acct.lineage` directly, no new code,
no backtest) makes this visible directly:

```
$ python3 evotrader_bundle.py holdout-pressure
```

Lining up the `champ fold` column against calendar time across the last
~60 holdout draws:

| when (draw range) | champ fold fitness | champ holdout | margin |
|---|---|---|---|
| draws 97-100 | 1.422 | ~1.16-1.20 | ~6.05-6.07 |
| draws 101-108 | 1.590 | ~1.06-1.15 | ~6.08-6.10 |
| draws 109-142 | **0.977** | ~1.07-1.09 | ~6.13-6.30 |
| draws 143-158 (this batch) | 0.977 | 1.140 | ~6.30-6.36 |

`champ fold` — the champion's fold-aggregate fitness, recomputed fresh
every `evolve` run from `rolling_folds()` windows anchored to the current
date — dropped **~38% (1.590 → 0.977)** between the 22:18 UTC 2026-09-08
batch and the 01:19 UTC 2026-09-09 batch, and has stayed flat at 0.977
across all three batches since (consistent with no new daily bar having
closed in between — `evolve` doesn't touch `live_state.json`'s trading
history, so the fold windows only move when a real day passes). A random
candidate's raw fold-fitness across all three of these regimes clusters in
roughly the same absolute range regardless of the champion's own score —
this batch's per-generation bests ranged 0.970-1.612, no different in
shape from the 1.3-2.3 range seen when the champion itself scored 1.42-1.59.
So when the champion's own bar sinks to 0.977, a much larger fraction of
that same-shaped candidate distribution clears it by chance — mechanically
sufficient to explain the jump from ~27-73% to ~93-100%, no research-side
change required.

**Critically, `champ holdout` and the sealed-holdout margin did *not*
collapse the same way.** Champion holdout fitness only drifted in a tight
~1.06-1.20 band across the same window (nowhere near the fold column's 38%
swing), and the margin by which the champion beats every challenger at the
sealed holdout has if anything grown slightly (~6.05 → ~6.36) as more
draws accumulated. All 57 recorded sealed-holdout draws against this
champion have lost, all by a wide margin. **This is the standing
fold-clears-then-loses-holdout pattern (`holdout-pressure`) holding up
exactly as designed** — the fold gate got easier to clear because the
champion's own fold score fell (a fold-window/regime artifact, the same
kind of instability `rolling_folds()`'s own docstring and the
2026-08-20/21 fitness-decomp/regime-folds research already characterized),
not because search quality changed or the champion is newly vulnerable.
No code bug, no fix needed — this closes the two-batch "worth watching"
flag with a specific, checked explanation rather than carrying it forward
a third time.

## The evolve batch itself

`python3 -m pytest -q` baseline run strictly before `evolve` (separate
process): **384/384 passed**, no code touched.

`python3 evotrader_bundle.py evolve 15` against the live v3 (1d) champion,
launched via the Bash tool's `run_in_background: true` with a plain
redirect (no `nohup`, no trailing `&` in the command string) — the
non-footgun form item 9 asks for — and picked back up cleanly via the
tool's own completion notification, no manual polling needed:

- Champion fitness held flat at **0.977** across all 15 generations (same
  value as both prior batches today — expected, no new bar closed). No
  promotion.
- Cumulative candidates tried against v3 rose **7055 → 7264**, boldness/
  stagnation counter **505 → 519**.
- Raw best-of-generation fold-fitness beat the champion's own 0.977 in
  **14/15 generations (93%)** — generation 13's best (0.970) was the one
  miss. A third consecutive batch in the same elevated range as the prior
  two (100%, 100%), now explained above rather than just re-flagged.

## Verification before commit

- `python3 -m pytest -q`: 384/384, run strictly before `evolve`, unchanged.
- Direct key-by-key Python-equality diff of `live_state.json` before/after:
  only `lineage`, `researcher_memory`, `updated` changed. `genome`,
  `broker`, `journal` byte-identical. Genome version still 3.
- Constitution checksum: `726dfa4bac85891a`, unchanged.
- `tools/edit_bundle_module.py verify`: "round-trip verified: bundle
  unchanged".
- `tools/edit_bundle_module.py sync --check`: "bundle already matches real
  files, no changes".
- Dashboard rebuilt: `EVO_STATE="$(pwd)/live_state.json" python3
  evotrader_dashboard.py` → `index.html` (20.5 KB).

No live trading this cycle. No code changed. Genome still v3 (1d) live,
untouched.
