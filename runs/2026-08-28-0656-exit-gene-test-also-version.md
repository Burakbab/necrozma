# 2026-08-28 06:56 UTC — 3-hourly check: `exit-gene-test --also-version N`

## Context

The 00:56 and 04:04 UTC entries today both flagged the same limitation:
`exit-gene-test` only worked against the live champion (v3) because its
researcher_memory lookup (needed for the multiple-testing margin on the fold
gate and the holdout draw count) was hardcoded to `acct.researcher_memory`.
Every other `--also-version` diagnostic in this file already reconstructs a
past champion via `_reconstruct_champion_genome(version, acct.lineage)` — this
session wired the same pattern into `exit-gene-test`.

## What changed

`evotrader_bundle.py`'s `exit-gene-test` command body refactored to loop over
a `champions` list: `[("v{live}", g0)]` plus, if `--also-version N` is given,
`[("v{N} (reconstructed)", _reconstruct_champion_genome(N, acct.lineage))]`.
Each champion gets its own baseline evaluation, its own
`n_tested_before`/`holdout_draws_before` lookup, and its own printed table —
same two hand-designed variants ("no discretionary exit",
"narrower exit (harder to trigger)") tested against each.

The one substantive limitation, documented in both the code and the CLI's own
trailing explanation: `live_state.json`'s `researcher_memory` only ever holds
cumulative counts for whichever version is champion *right now* — it resets
on every promotion. A reconstructed past champion therefore always takes the
`n_tested_before=0`/`holdout_draws_before=0` branch (the same fallback the
command already had for a `champion_version` mismatch), which is an
optimistic upper bound on the real historical margin that version would have
faced, not a replay of its actual history. No way to recover the real
historical count exists — `state/genomes/` is gitignored/rebuildable-cache-only
and lineage doesn't record per-version cumulative researcher_memory snapshots.

## Results

**v1** (reconstructed): both candidates hard-fail the dd-corrected drawdown
gate before ever reaching a champion comparison — fold-agg fitness
-2.959 ("no discretionary exit") / -2.832 ("narrower exit") vs v1's own
-2.787. Same failure mode as v3 (hard gate fail on the *challenger* itself).

**v2** (reconstructed): different story. "no discretionary exit" still
hard-fails (-2.924 vs v2's own -2.575). But **"narrower exit (harder to
trigger)" clears the fold gate** — fold-agg fitness -0.129, a genuine
champion-relative pass over v2's -2.575 — the first time either variant has
cleared the fold gate against any of the three real champions checked so
far. It then fails the sealed holdout (-1.301, well short of
`holdout_accepts()`'s margin).

**v3** (live, re-run for comparison in the same session): both candidates
still hard-fail, same shape as the 00:56 UTC run (today's numbers shifted
slightly from three hours ago — fold-agg -1.612 vs earlier session's
recorded figures — expected day-over-day market-data drift, not a
regression; `fold-date-sensitivity` already established real numbers move
with the "as-of" date).

## Reading

Three real champions now checked, and every one still rejects both
hand-designed exit-gene variants — but for two structurally different
reasons: v1/v3 reject at the fold gate itself (the challenger's own maxDD is
too severe to ever reach a champion comparison), while v2 rejects at the
holdout (the challenger genuinely beats v2 fold-aggregate, then loses the
draw). This sharpens exit-role-test's original "let search decide" framing:
search deciding wouldn't help v1/v3 clear a drawdown problem these two fixed
gene values can't touch, but it might matter for v2, where the fold gate is
already cleared and only the holdout margin stands in the way — a genuinely
evolved (not hand-patched) value in this gene's neighborhood, run through
real `evolve` against a v2 copy, is the untried next check that could
actually answer whether this is a real lever for that specific champion.

## Verification

- `python3 -m py_compile evotrader_bundle.py` — clean.
- `python3 tools/edit_bundle_module.py sync --check` — clean (CLI-only code,
  no `_SRC` module touched).
- `python3 -m pytest -q` — 235 passed (127.06s), matches baseline; no new
  pure function, so no new test file.
- `git diff --stat` — only `evotrader_bundle.py` touched.
- `live_state.json` md5 `0fa0731311baab0508f959f79a01214e` and
  `evotrader.manifest` md5 `0bf3a7d9411ee692d0a9f152a7533803` — both
  unchanged before and after every diagnostic run in this session.
- Today's daily bar already processed at 00:28 UTC before this session
  started (`live_state.json`'s `updated` timestamp, `runs/2026-08-28-0020-daily-trading.md`)
  — no tick run, no double-trade.
- No genome promotion.

## Also this session

Found local `main` diverged from `origin/main` again on `git pull` (same
shallow-clone-window artifact the 00:56/04:04 UTC entries already
identified, not a force-push): `git rev-parse --is-shallow-repository`
confirmed the clone is shallow, and `git merge-base --all main origin/main`
returned no common ancestor purely because both branches' available history
windows (50 commits each) don't overlap after enough commits landed upstream
between this container's clone time and this session's `git pull`. Working
tree was clean throughout. Realigned with `git reset --hard origin/main`
per the Run protocol's step 2 — no force-push, nothing lost.

## Next

- Fold 3's drawdown mechanism (Guardian's mechanical stop-loss/time-stop and
  the circuit breaker, not any discretionary consult — see the 04:04 UTC
  `fold3-anatomy` entry) is still the open thread for actually fixing v3's
  drawdown exposure.
- v2's fold-gate clear on "narrower exit" is one hand-patched data point —
  running real `evolve` generations against an isolated v2 copy, seeded or
  biased toward this gene's neighborhood, would show whether an evolved
  value in that region could also clear the holdout, which this diagnostic
  alone cannot answer.
