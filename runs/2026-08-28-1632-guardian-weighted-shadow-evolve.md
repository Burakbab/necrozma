# Guardian-weighted shadow evolve — 25 generations, 361 candidates

2026-08-28, ~15:53–16:32 UTC (3-hourly check)

## Why

The 13:00 UTC entry today (`guardian-gene-test --pct N`) closed off the
hand-picked-single/few-gene-patch line of investigation: every magnitude of
Guardian-gene tightening tried across two sessions scores in a narrow band,
two orders of magnitude below the actual multiple-testing bar. Its own
"Next" flagged the one lever nobody had tried yet: "a real `evolve()` shadow
search seeded from v3 with mutation weight toward the Guardian risk genes,
run for enough generations that fold-aggregate selection compounds many
candidates before any one reaches the (heavily-taxed) holdout gate."

This session ran that search.

## What

Standalone script, not committed (same "lives entirely in the sandbox"
discipline as every prior shadow-evolve session — see `runs/2026-08-16-0059-*`
and friends). Not `evotrader_bundle.py`'s `evolve`, not `run_from_files.py`'s
`evolve-dry-run` either, but the same underlying `loop.evolve.EvolutionRun`
against the same real `core/agents/loop/constitution` files, with one change:
`Researcher.perturb()` subclassed so every blind-search proposal is
guaranteed to include one of `risk.stop_loss` / `risk.trailing_stop` /
`risk.max_bars_held`, with its remaining gene picks (per the existing
`n_genes`/boldness formula) still drawn from the *full* `GENE_SPACE` — so
Guardian-gene changes get tested standalone and combined with entry/sizing
genes, not restricted to the 3-gene subspace `guardian-gene-test` already
hand-swept.

Seeded from the live champion (v3), 4-year real market data
(`market.load_universe`, 27 symbols), `n_blind=14` (the CLI default),
25 generations, `EvolutionRun` constructed directly (bypassing
`__init__`'s `data` param, which is market data, not a genome — the real
starting genome comes from `Genome.champion()` reading `state/genomes/
champion.json`, seeded via `g0.save("champion")` first, same as
`evolve-dry-run`'s own pattern). Seeded `holdout_draws=22`, the account's
actual current cumulative count (`live_state.json`'s `researcher_memory`),
so the search faced the real bar, not an artificially reset one.
**`acct.save()` is never called anywhere in the script — `live_state.json`
is opened read-only once, to read the seed genome and `researcher_memory`.**
`state/genomes/` and `state/lineage.jsonl` (both gitignored) are the only
files touched on disk.

Runtime: 1 generation ≈ 1.5–2.3 min on 1d bars (much cheaper than the 4h
shadow work's 6–27 min/generation), so 25 generations completed in 38.2 min
— well inside a 3-hourly slot with room to spare.

## Result

**Champion held at v3 through all 25 generations. No promotion, real or
shadow.** But the shape of *why* is the finding:

- 361 total candidates tried across 25 generations (25 in generation 1
  including diagnosis/structural proposals, 14 blind proposals/generation
  after — structural/diagnosis proposals are deterministic given an
  unchanged champion and get excluded as already-tested).
- **69 candidates cleared the fold-aggregate acceptance gate** (best fold
  fitness 1.582, vs. champion's own fold-aggregate fitness of −1.612 for
  this 4-year-ending-today window) and reached the sealed holdout check —
  roughly 5–6x more fold-gate-clearing candidates than the two hand-picked
  guardian-gene-test sessions combined found (11 of 12 there, but those were
  single/few-gene halvings against 3 champions, not a real search).
- **Every one of the 69 failed the sealed holdout.** Cumulative holdout
  draws climbed 22 → 91 over the run (required margin grew from 4.97 to
  5.99 as a result — `constitution.required_margin()`'s `sigma *
  sqrt(2*ln(n))` form, so this compounding cost stayed modest, not
  runaway).
- **The sharper finding: 16 of the 69 holdout-tested candidates (23%) beat
  the champion's own holdout score outright, in raw terms** — up to
  **+2.754 vs. champion's +0.597** (4.6x), several others in the +1.6 to
  +2.7 range — and every single one was still rejected, because
  `holdout_accepts()` requires beating champion **+ margin** (5.6–6.0 at
  these draw counts), not just beating champion. The best raw holdout score
  found (+2.754) needed +6.246 to pass and missed by 3.49.

This is the same "clears fold gate, loses at holdout" shape
`holdout-pressure` first named 2026-08-18 and `guardian-gene-test` found
again this morning, now reproduced with an order of magnitude more
candidates and a real search rather than hand-picked patches — and it
sharpens the mechanism from "maybe search intensity would find something"
to a specific, quantified answer: **no, not because nothing better exists
(23% of holdout-tested candidates *were* genuinely better on the sealed
holdout), but because the additive margin, measured against the champion's
own (0.597) holdout draw, sets a bar high enough that "genuinely better" is
not the same thing as "clears the gate."** More generations of this same
search would very likely keep finding raw-holdout-beating candidates at a
similar ~20% rate and keep rejecting all of them, since the margin scales
with `sqrt(ln(cumulative draws))` — slow, but never zero, and always
measured against the same fixed, possibly-lucky 0.597 baseline rather than
against an absolute or percentile bar.

## Verified safe

- `md5sum live_state.json evotrader.manifest` unchanged before/after:
  `0fa0731311baab0508f959f79a01214e` / `0bf3a7d9411ee692d0a9f152a7533803`
  (same hashes cited in every entry today).
- `git status --short` clean throughout — nothing in the working tree
  touched, script lived entirely under the session scratch directory.
- No genome promotion, real or shadow (`final_version == 3`, the seed
  champion's own version).
- Today's bar (00:20 UTC) was already processed before this session
  started; no `tick` run, no double-trade.
- Local `main` had again diverged from `origin/main` at session start
  (history-rewrite artifact AGENTS.md's own run protocol names as
  expected) — realigned with `git reset --hard origin/main`, no
  force-push, nothing lost.

## Next

This is not a mechanism bug to fix casually — it's a real design tension in
`required_margin()`/`holdout_accepts()` worth naming plainly for whoever
next touches the constitution: the margin is additive over the champion's
own single noisy holdout draw, not an absolute or percentile bar, so an
unusually lucky champion draw (0.597 here, and multiple past entries have
called it "lucky") can entrench indefinitely against genuinely-better
challengers, and the entrenchment gets *slightly* worse (not better) the
more the search tries, since every fold-gate-clearing candidate that reaches
holdout adds to the cumulative draw count that sets the champion's own bar
too. Two directions worth a real design pass (not attempted here — this
was a search/measurement session, not a constitution-change session):
(a) re-drawing/refreshing the champion's own holdout score periodically
instead of anchoring to one historical draw forever, or (b) an absolute
or percentile-based holdout bar instead of (or alongside) the additive
margin. Either is a constitution amendment — checksummed, needs an
`AMENDMENTS.md` row, and deserves scrutiny from a full session, not a
3-hourly one, given how central `holdout_accepts()` is to the system's
promote-to-live-money safety story.
