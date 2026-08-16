# Correlation-penalty range search — 2026-08-16 ~04:03 UTC

Scheduled 3-hourly check. Today's daily bar was already handled by the 00:20
UTC daily run (`live_state.json` `updated` at `2026-08-16T00:21:55Z`) —
nothing to trade this cycle. Used the slot on the open item from Next-steps
item 3: "a different penalty value, or letting the Researcher search a range
instead of one fixed proposal, hasn't been tried."

## Change

`agents.researcher.Researcher.structural()` used to propose exactly one
`correlation_penalty` candidate (`0.0 -> 0.5`) whenever the gene was cold.
Changed it to propose three candidates in the same cold-start branch —
`0.25`, `0.5`, `0.75` — each a distinct `Mutation` with its own patch, so
blind search and the acceptance gates pick the magnitude instead of a human
guessing one value up front. Once any value is promoted (`correlation_penalty
> 0.0`), the branch stops firing, same as before — this only widens the
cold-start proposal, it doesn't change anything once the gene is live.

Edited directly in `evotrader_bundle.py` (no `bundle.py` build script exists
in this clone — extracted the `agents.researcher` module source via its exact
`repr()` round-trip, edited the source, re-encoded with `repr()`, and spliced
it back so the rest of the bundle is byte-identical). Verified:
`py_compile` clean, `evotrader_bundle.py summary` against the real
`live_state.json` unchanged, and a direct import of `agents.researcher`
confirmed `structural()` now yields three distinct
`correlation_penalty_{0.25,0.5,0.75}` mutations with unique patches from the
seed genome.

## Shadow evidence

Copied `live_state.json` (real champion v2, real accumulated
`researcher_memory`, 154 already-excluded proposals) to a scratch directory
and ran `EVO_STATE=... python3 evotrader_bundle.py evolve 6` there — same
27-symbol, 1d universe, real Binance data, real gates. **Champion held at v2
for all 6 generations** (best per-generation fitness 0.925, 0.739, 0.530,
0.892, 0.392, 0.473 vs champion's 0.682 — nothing cleared the rising
multiple-testing margin, which sits on 224 cumulative candidates against this
champion by the end of this run). Unlike the 00:59 UTC shadow run today (same
starting point, different random draw), this draw found no promotion at all —
consistent with blind search being randomized per invocation, not a
regression in the champion or the new code.

The range proposal did fire and got ranked: in generation 1 (cumulative 154),
`correlation_penalty_0.75` scored fitness 0.5912 and `correlation_penalty_0.25`
scored 0.4722, both below the champion's 0.682 but 0.75 clearly ahead of
0.25 in this fold-aggregate. A pre-existing lineage entry from real history
(cumulative 110, old single-value `correlation_penalty` proposal, pre-dating
this code change) scored 0.4233 for reference. Three generations is not
enough to call a winner between penalty magnitudes — this is a mechanism
check (the range proposal works, gets evaluated, ranks candidates
differently by value) rather than a verdict on which value is best.

**Nothing here touched `live_state.json`** — this is a code change to the
Researcher's proposal generator plus a scratch-only search for verification,
not a promotion. Scratch state and cache deleted after the run.

## Side finding: shadow `evolve` invoked from the repo root leaks files

Running `evolve` with `EVO_STATE` pointed at a scratch file, but with cwd
still the repo root, wrote `state/genomes/{champion,v1}.json` and
`state/lineage.jsonl` into the real repo — `GENOME_DIR` in `core.genome`
resolves relative to `os.path.abspath(__file__)`, which is cwd-relative
inside this bundle's import shim, not `EVO_STATE`-relative. Prior shadow runs
avoided this by copying the whole bundle out to a separate scratch directory
and running from there; this run instead redirected only the state file and
leaked genome-archive JSON into the tracked tree (harmless — `tick`/`summary`
never read `GENOME_DIR`, only `live_state.json` — but untracked and
unintended). Deleted the leaked `state/` directory and widened
`.gitignore`'s `state/cache/` to a blanket `state/` so this can't happen
silently again, regardless of which directory a future shadow `evolve` is
launched from.

## Next

Not resolved: which correlation_penalty magnitude (if any) actually
generalizes. Needs more generations, or a run where the champion itself gets
beaten so a challenger with a correlation gene has something better than v2
to be compared against on the sealed holdout — a challenger has to first win
the fold-aggregate ranking before the holdout check is even reached, and none
did with any correlation gene set this cycle.
