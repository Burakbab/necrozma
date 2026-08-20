# Agent operating context

This is the working memory for the scheduled agents that run this repo
unattended. It replaces the old `docs/` folder, which is now local-only and not
in version control — **do not expect `docs/` to exist in a fresh clone.**

If you are a scheduled run: read this file first, do the work, then update the
**Current state** and **Next steps** sections here before you commit. This file
is how you talk to the next run. Nothing else persists except `live_state.json`.

---

## Run protocol

Every scheduled run, in order:

1. **Git identity** (local config, never global):
   ```
   git config user.name "Burk"
   git config user.email "81077487+Burakbab@users.noreply.github.com"
   ```
   Use the noreply address. Never commit a personal email address — not in
   commit metadata, not in file contents. This is a standing rule.

   **Never** add a `Co-Authored-By` trailer or any AI-identity signature to a
   commit. Also a standing rule, not optional.

2. **Get onto the branch, then pull.** The cloud clone starts in **detached
   HEAD**, so a bare `git pull` fails with "You are not currently on a branch":
   ```
   git checkout main
   git pull --rebase origin main
   ```
   Several routines share this repo and collide otherwise. If local `main` has
   diverged from `origin/main` (history here has been rewritten before, and may
   be again), **`origin/main` is authoritative** — `git reset --hard
   origin/main` and carry on. Never force-push.

3. **`pip3 install -r requirements.txt -q`** — the cloud sandbox starts bare with
   no numpy/pandas.

4. **Do the work** (see the per-routine task, and Next steps below).

5. **Rebuild the dashboard** if state changed:
   ```
   EVO_STATE="$(pwd)/live_state.json" python3 evotrader_dashboard.py
   ```
   This writes `index.html` at the repo root, which GitHub Pages serves as the
   public site. It is written for a general audience, not for us — plain
   language, jargon explained, caveats included. Keep it that way: if you add a
   panel, add the one-line explanation and any glossary entry alongside it.

6. **Write a run note** — one NEW dated file at `runs/YYYY-MM-DD-HHMM-<slug>.md`.
   Never append to a shared file; concurrent runs clobber each other. Keep run
   notes **technical**: NAV, decisions, what changed, what you tried and why.
   No personal content — this directory is public.

7. **If this run promoted a new live champion** (`live_state.json`'s genome
   version increased), update `README.md`'s `## Status` section in the same
   commit — name the new version and why. That section is hand-written prose,
   not generated, and it renders on the repo's GitHub landing page
   (`github.com/.../tree/main`), which is a different surface from the
   generated dashboard `index.html`. It does not update itself: it said
   "genome v2" for a day after the v2→v3 promotion because nothing was
   responsible for touching it. Mandatory, not optional — same standing as
   the `AMENDMENTS.md` rule below.

8. **Update this file's Current state / Next steps**, then commit and push.

### Commands

```
python3 evotrader_bundle.py tick        # one live paper tick, real prices
python3 evotrader_bundle.py summary     # account status, no trading
python3 evotrader_bundle.py signals     # today's decision in plain language
python3 evotrader_bundle.py evolve N    # N generations of self-improvement
python3 evotrader_bundle.py anatomy     # P&L post-mortem on every closed trade
python3 evotrader_bundle.py consults    # are the three consults actually independent?
python3 evotrader_bundle.py costs       # fee/slippage perturbation sensitivity
python3 evotrader_bundle.py regime      # what market regime does each fold/holdout window contain?
python3 evotrader_bundle.py hard-calls  # how often would agents.judges.flag_hard_call fire?
python3 evotrader_bundle.py review-hard-calls  # list/record verdicts on flagged bars
python3 evotrader_bundle.py holdout-pressure  # real fold-aggregate winners the sealed holdout has rejected
python3 evotrader_bundle.py fold-scheme       # fold-count sensitivity of fold-aggregate fitness
python3 evotrader_bundle.py drawdown          # which date range actually drives maxDD, ranked by depth
python3 evotrader_bundle.py correlation-universe  # full-universe pairwise return correlation by fold/holdout
python3 evotrader_bundle.py holdout-noise         # block-bootstrap sigma of a sealed-holdout fitness score
```

`anatomy`, `consults`, `costs`, `regime` and `hard-calls` are diagnostics:
they replay history and report, they never touch `live_state.json` or the
champion. `anatomy`/`consults`/`costs`/`hard-calls` take a few minutes
(`costs` replays history once per cost scenario, so longer). `regime` is
cheap — no genome or council involved, just equal-weight buy-and-hold over
each walk-forward fold and the sealed holdout — and takes `--interval
1h|4h|1d` to inspect a bar size other than the champion's own.

`tick` refuses to trade the same bar twice — if it prints `already traded`, that
is the idempotency guard working correctly, not an error. It decides on the last
*closed* daily bar, which is why the daily run fires at 00:20 UTC.

`review-hard-calls` is not a diagnostic like the five above: run with no args
it's read-only (lists flagged-but-unreviewed bars), but `--tick N --verdict
'...'` deliberately writes a review record onto `live_state.json` — the one
intentional exception to "diagnostics never touch state" in this list. It
never touches trading, cash, positions, or the genome, only the
`hard_call_reviews` field.

`holdout-pressure` is the cheapest diagnostic here — it never runs a
backtest or touches market data, just reads `acct.lineage` (already in
`live_state.json`) and reports every individual real challenger that has
cleared the fold-aggregate gate against the current champion and then lost
at the sealed holdout, since that champion's promotion. Run it after any
`evolve` call that doesn't promote, to see whether the champion is holding
because nothing better exists or because a lucky holdout draw is entrenching
it against genuinely fold-superior challengers (see "Current state").

`correlation-universe` is read-only, same cost class as `regime` (~80s: one
`load_universe` call, no backtest, no Council). For each walk-forward fold and
the sealed holdout it samples `--samples` points (default 8) spaced through
the window, computes the full pairwise Pearson correlation matrix of
`--lookback`-bar (default 30, matching the `correlation_lookback` gene's
default) raw returns across every universe symbol at each point
(`loop.engine.pairwise_correlation_stats`), and reports the mean/range per
window. Genome-independent (raw price correlation, not any consult or
genome signal) — exists to check what `agents.judges.RiskJudge.
_correlation_scale` never looks at: the live mechanism only ever compares a
buy candidate against symbols already *held*, never the wider universe. See
"Current state" for the first result and what it means for AGENTS.md item 3's
open drop-vs-build decision.

`correlation-universe --realized` adds the portfolio-realized half of that
same question: not "how correlated is the universe" but "how correlated are
the symbols the champion actually holds *together*". Runs one real
full-history backtest (same cost class as `anatomy`/`consults`/`costs` — a
few minutes, heavier than the ~80s base command) and reconstructs the held
set per bar via the new `loop.engine.holding_mask` (a pure function built
from `run_backtest`'s own `closed_trades`/`open_positions` records — no
genome, broker, or replay access, just timestamp bookkeeping; tested,
`tests/test_holding_mask.py`, 10 new tests, full suite 104 passed up from
94), then feeds each bar's held subset through the same
`pairwise_correlation_stats` used above and prints a directly-comparable
held-only-vs-universe-wide table per fold/holdout window. Still read-only:
never touches `live_state.json` or the champion. See "Current state" for the
first result.

`fold-scheme` re-evaluates the live champion under alternative `n_folds`
counts (via `loop.evolve.Evaluator`, which already accepted `n_folds` as a
constructor argument — no engine or constitution change) and reports how
much one outlier calendar fold dominates `aggregate_fitness` at each count.
Read-only, full replay per scheme (same cost class as `regime`/`costs`). Only
valid for relative comparison across fold counts on the same data snapshot —
its absolute `aggregate_fitness` numbers will not match a champion's
recorded promotion-time fold-aggregate fitness (different sliding 4-year
window). See "Current state" for the first result. `--also-version N`
reconstructs a past champion (by version) from `live_state.json`'s own
`lineage` and runs the same sweep on it alongside the live champion, for
checking whether a fold-scheme finding is genome-specific or general —
e.g. `fold-scheme --also-version 2`. See "Current state" 2026-08-18 for
why the outlier-gap column is guaranteed identical across any champion
(it's buy-and-hold-only) while `aggregate_fitness` is the column that
actually differs.

`holdout-noise` answers `constitution.holdout_accepts()`'s own docstring —
"measure the sigma before trusting the number" — for real: one real backtest
over the sealed holdout window (same cost class as `costs --holdout`), then
pure-numpy block-bootstrap resampling of that backtest's own `nav_history`
(`--n-boot` draws, default 1000, no market reload or genome re-evaluation per
draw, so this step itself is fast). Reports the empirical standard deviation
of the resulting `fitness()` distribution next to
`constitution.MULTIPLE_TESTING_SIGMA`, the constant `required_margin()`
assumes. First result (2026-08-20): ~24-25x, not 1x — see "Current state".
`--also-version N` works the same way as `fold-scheme`/`correlation-universe`.

If a run reports **CONSTITUTION MODIFIED**, stop. Do not re-seal it. Investigate
and check `AMENDMENTS.md` first.

---

## Where things live

| path | what it is |
|---|---|
| `evotrader_bundle.py` | the entire runtime flattened into one file — agents, judges, broker, evolution loop |
| `evotrader_dashboard.py` | dashboard builder (zero external deps, hand-rolled SVG) |
| `evotrader.manifest` | constitution checksum (`dfae6a697f51fb49`) — the anti-tampering seal |
| `live_state.json` | **the account**: cash, positions, trade ledger, NAV history, current genome, evolution lineage, researcher memory |
| `AMENDMENTS.md` | the constitution amendment log — every gate change, argued in writing |
| `runs/` | one dated note per scheduled run |
| `tools/edit_bundle_module.py` | extract/reinsert a module's source from `evotrader_bundle.py`'s embedded `_SRC` dict for editing without hand-touching its giant single-line strings — see item 7 and `runs/2026-08-20-0348-bundle-edit-tool.md` |
| `index.html` | generated public dashboard, served by GitHub Pages — rebuilt each run, never hand-edited |
| `README.md` | hand-written, renders on the GitHub repo page — its `## Status` section names the current genome version and must be updated on every promotion (see Run protocol step 7) |

`live_state.json` is the irreplaceable one. Everything else can be rebuilt.

## No credentials, anywhere

Prices come from Binance's public market-data endpoint: no API key, no signup, no
KYC. The portfolio is tracked in `live_state.json`, which *is* the ledger. There
is no brokerage account in this design and there does not need to be one.

---

## Current state

- **Measured 2026-08-20 (3-hourly check): checked the holdout-noise finding
  against the third and final real champion (v1), closing the "is this
  v3-specific" question.** (see
  `runs/2026-08-20-0948-holdout-noise-third-champion.md`) One-line
  `holdout-noise --also-version 1` (no code change — existing CLI flag).
  Result: v1's bootstrap sigma is **18.90x** `MULTIPLE_TESTING_SIGMA`,
  between v3's 23.83x and v2's already-recorded 14.3x. All three real
  champions this account has ever had now show `boot_fitness_std` in the
  14-24x range — none anywhere near the 1x the margin formula assumes, and
  the spread across genomes is narrower than the gap from any of them to the
  assumed constant. Exhausts the "check another real champion" data source
  (same shape as every other cross-champion sweep in this file) — no fourth
  real genome exists until a new promotion happens. Verified safe: purely
  read-only, `live_state.json` md5 identical before/after
  (`cca58deb976cef403c5010f2e2b9528b`), `evotrader.manifest` md5 identical
  (`6a4434574ff424f74ff300ebdb50d194`), `constitution verified
  dfae6a697f51fb49` unchanged, `git status --short` empty before this run's
  own commit, today's 2026-08-20 bar confirmed already processed by the
  00:20 UTC daily run before this check started (no double-trade, `tick` not
  run this session). Also noted: this session's cloud clone started with
  local `main` detached and two commits behind a stale pre-restart ref;
  reset to `origin/main` per the run protocol's "origin/main is
  authoritative" rule (no work lost — the two divergent local commits were
  already-superseded Aug 15-16 initial-import commits). Next: the
  recalibration decision (bump `MULTIPLE_TESTING_SIGMA` or add a separate
  holdout-specific constant) is still an unstarted constitution change —
  checksummed, needs its own `AMENDMENTS.md` row, and reads best combined
  with the fold-scheme outlier-fold finding as one regime-stratified/rolling
  redesign, not a number to bump alone. No further cheap data points remain
  on the noise-magnitude question itself.
- **Measured 2026-08-20 (3-hourly check): the sealed-holdout margin's own
  docstring names an unanswered question — "measure the sigma before
  trusting the number" — and now it's measured: the real noise is ~24-25x
  larger than the constant the margin formula assumes.** (see
  `runs/2026-08-20-0654-holdout-noise-bootstrap.md`) New
  `loop.engine.block_bootstrap_resample`/`stats_from_returns`/
  `bootstrap_fitness_distribution` block-bootstrap a real backtest's observed
  sealed-holdout return path (preserving short-range autocorrelation an
  i.i.d. per-bar shuffle would destroy) and recompute
  `constitution.fitness()` per resample, holding trades/turnover fixed at
  the real backtest's values (a resampled return order can't regenerate
  which trades would have fired). New read-only CLI `holdout-noise
  [--n-boot N] [--block-size B] [--seed S] [--also-version N]`. Result
  against champion v3: empirical `boot_fitness_std` ≈ 1.9-2.0 across three
  block sizes (5/15/30) and two seeds, a consistent **~24-25x**
  `constitution.MULTIPLE_TESTING_SIGMA` (0.08) — the constant
  `required_margin()` uses to size the sealed-holdout gate. Checked against
  a second champion (v2, reconstructed): ratio 14.3x — different magnitude,
  same order-of-magnitude-off conclusion, not a v3-specific artifact. This
  puts a real number behind every "lucky holdout draw" observation already
  in this file (`holdout-pressure`'s 9/9 real challengers that cleared the
  fold gate and lost the sealed holdout; the 4h-shadow work's repeated
  champion-entrenchment finding) — under-margining this large means a
  "beats the champion" holdout verdict is far less trustworthy than the
  current gate implies. Caveats: bootstraps the *realized return path* of
  one backtest (order/selection noise), not a genuinely different holdout
  slice of history (would need re-running the full council against
  resampled prices, not just resampled returns — a harder, costlier
  question); block-bootstrap standard error of a Sortino-like ratio is a
  standard technique but still an approximation, so the exact multiplier
  shouldn't be over-read, only the order of magnitude. Verified safe:
  purely additive (`loop.engine` isn't checksummed), `tools/
  edit_bundle_module.py verify` round-trip clean, `py_compile` clean,
  tested (`tests/test_bootstrap_holdout_noise.py`, 16 new tests — includes
  a bit-for-bit cross-check of `stats_from_returns` against
  `PaperBroker.stats()` on the same path, and a constant-return degenerate
  case asserting exactly-zero bootstrap sigma as a sanity check on the
  mechanism itself — full suite 127 passed up from 111), `live_state.json`
  md5 identical throughout (`cca58deb976cef403c5010f2e2b9528b`),
  `evotrader.manifest` md5 identical (`6a4434574ff424f74ff300ebdb50d194`),
  `constitution verified dfae6a697f51fb49` unchanged, today's 2026-08-19 bar
  (tick 6) confirmed already processed by the 00:20 UTC daily run before
  this check started (no double-trade, `tick` not run this session). Next:
  whether to actually recalibrate `MULTIPLE_TESTING_SIGMA` (or add a
  separate, larger holdout-specific sigma constant) is a constitution
  change — checksummed, needs its own `AMENDMENTS.md` row — and reads best
  together with the existing fold-scheme findings (fold 2's permanent
  +200% outlier, non-monotonic `aggregate_fitness` across fold counts) as
  one combined case for a regime-stratified/rolling fold-and-holdout
  redesign, not a number to just bump in isolation. **`--also-version 1` run
  2026-08-20 (see the entry above this one) — 18.90x, closing the
  third-data-point follow-up.** The remaining cheap option without touching
  the constitution is a much higher `--n-boot` to check the ~24x estimate
  has converged (not attempted).
- **Shipped 2026-08-20 (3-hourly check): the bundle-editing tool the
  correlation-penalty-removal run flagged as needed for the next session is
  now committed.** (see `runs/2026-08-20-0348-bundle-edit-tool.md`) New
  `tools/edit_bundle_module.py` extracts a named module's source out of
  `evotrader_bundle.py`'s giant single-line `_SRC['dotted.name'] = '...'`
  entries into a real `.py` file for normal editing, and folds an edited
  file back in via `repr()`, replacing only that one line — the same
  extract/reinsert approach the prior run built ad hoc in `/tmp` (and lost,
  since `/tmp` doesn't survive the container) rather than a new mechanism.
  `verify` round-trips every module in the real bundle unmodified and
  asserts byte-identical output; `tests/test_edit_bundle_module.py` (7 new
  tests, full suite 111 passed up from 104) checks this on every `pytest`
  run against synthetic cases plus the real current bundle, not just
  manually before a real edit. Verified safe: full manual extract-edit-
  reinsert workflow tested on a scratch copy in `/tmp` (not this repo, no
  risk to the real bundle), `py_compile` clean, `live_state.json` md5
  identical (`cca58deb976cef403c5010f2e2b9528b`), `evotrader.manifest` md5
  identical (`6a4434574ff424f74ff300ebdb50d194`), `git status` clean of
  anything but the two new tool files and the new test, `constitution
  verified dfae6a697f51fb49` unchanged, today's 2026-08-20 bar confirmed
  already processed by the 00:20 UTC daily run before this check started (no
  double-trade, `tick` not run this session). One bug caught before
  committing: the test suite's first draft hand-wrote a sample module's
  source using a quoting style that didn't match `repr()`'s own canonical
  output, making the round-trip assertion meaningless — fixed by building
  the synthetic sample with `repr()` itself. Next: not used for a real edit
  yet — the next session that needs to touch `evotrader_bundle.py`
  internals (a future item-3-style removal, or item 7's eventual unflatten)
  should use this instead of hand-editing `_SRC` lines or rebuilding an ad
  hoc version.
- **Resolved 2026-08-20 (3-hourly check): item 3 acted on, not just measured
  — `correlation_penalty`/`correlation_lookback`/`_correlation_scale` are
  removed.** (see `runs/2026-08-20-0055-correlation-penalty-removal.md`)
  After 4 real champions + 2 adversarial constructions + real unconstrained
  search all agreed the gene was dead weight (see the 2026-08-19 entries
  below), this was the "dedicated session" the last of those entries said
  the removal deserved. Deleted: the two genes from `SEED_GENOME`'s
  `risk_judge` block (`core.genome`), `RiskJudge._correlation_scale` and its
  helper `_pairwise_corr` (`agents.judges`) plus its call site in `rule()`
  (the `corr_scale` multiplier and its veto branch), the `correlation_penalty`
  structural proposal block and both `GENE_SPACE` entries in
  `agents.researcher`, and `Briefing.rets_by_symbol` (`core.types`) plus the
  per-bar computation that fed it in `Analyst.brief` (`agents.analyst`) — that
  last piece was a real, if small, live performance cost (one extra
  `np.diff` per symbol per bar, on every tick and every backtest, purely to
  feed a gene now gone). Left alone: `loop.engine.pairwise_correlation_stats`
  and `holding_mask` (the `correlation-universe` diagnostic) — they compute
  correlation directly from raw closes, never depended on
  `Briefing.rets_by_symbol`, and remain useful for any future
  concentration/diversification question; the diagnostic's own docstrings
  and the `--adversarial`/`--adversarial-tight` genome builders were updated
  to stop referencing the now-deleted mechanism (and their patch lists no
  longer set `correlation_penalty`, since there's nothing left to set).
  Constitution package untouched (`correlation_penalty` lived in
  `agents.judges`/`core.genome`, neither checksummed) — no `AMENDMENTS.md`
  row needed, `constitution verified dfae6a697f51fb49` unchanged throughout.
  Verified safe: full suite still 104 passed (two assertions in
  `tests/test_genome.py` updated to stop referencing the deleted gene, one
  swapped to `max_position_pct` to keep testing the same dotted-path
  mechanism), `py_compile` clean, `live_state.json` md5 identical
  before/after (`cca58deb976cef403c5010f2e2b9528b`), and a real full-history
  backtest of champion v3 (the live genome, which never touched this gene —
  it defaulted to `0.0`, a proven no-op) reproduces the previously-recorded
  -34.1% maxDD to 5 significant figures (-0.34088... here), the same shape
  of confirmation every other diagnostic-only run in this log has used —
  proof this was a true no-op removal, not a behavior change. Editing
  mechanism note for future sessions: `evotrader_bundle.py`'s `_SRC` dict
  entries are single giant escaped-string lines (one per module, generated
  historically by a `bundle.py` that no longer exists in this repo — item 7
  is still not done); editing them directly with string-match tools is
  impractical. Used a small extract/reinsert script instead (`ast.literal_eval`
  the line's RHS out to a real `.py` file, edit normally, `repr()` it back
  into the `_SRC[...] = ` line) — round-trip verified byte-identical on an
  unmodified extract before trusting it on real edits. Not saved to the repo
  (lived in `/tmp`, gone with the container), so the next session that needs
  to touch bundle internals will want to rebuild the same two-function
  tool rather than hand-edit the giant lines.
- **Resolved 2026-08-19 (3-hourly check): the last open piece of item 3's
  evidence base — does real unconstrained blind search, not a hand-built
  genome, ever wander toward the concentration region on its own — is
  answered, and it doesn't.** (see "Next steps" item 3 and
  `runs/2026-08-19-2218-correlation-real-search-concentration.md`) Ran the
  real `loop.evolve.EvolutionRun` (same code path a live `evolve` call takes)
  for 10 generations against the real live champion v3, in an isolated
  scratch copy (isolation asserted at runtime, not just described). 128 fresh
  proposals, cumulative tested count 140→282, no promotion (champion held at
  fitness 1.737 throughout, continuing the real account's own existing
  stagnation streak). Of the ~30 candidates that touched a concentration gene
  (`max_positions`, `max_position_pct`, `cash_floor_pct`), every one scored
  below champion, and not narrowly — the single best concentration-touching
  candidate anywhere in the run (`max_positions: 10`, fitness 1.4082) was
  actually the *de-concentrating* direction; every candidate that shrank
  `max_positions` toward the adversarial constructions' 2-3 range scored
  0.4-0.8, far off the pace. One earlier single-generation smoke test (used
  only to validate the harness) had drawn a `max_positions: 2` candidate at
  1.988, above champion — flagged explicitly in the run note as a
  non-reproducing lucky draw (`Researcher(seed=None)`, proposals randomized
  per invocation) once the fuller 10-generation run's ~30 concentration
  candidates all scored well below champion instead. Item 3's evidence base
  is now real champions (4) + hand-built adversarial constructions (2) + real
  unconstrained search (this run), all consistent. Verified safe: purely
  read-only against a scratch copy, driver script never committed, `git
  status --short` clean, `live_state.json` md5 identical before/after
  (`09c35b692da1d694c5a3cace5d488f40`), `evotrader.manifest` md5 identical
  (`6a4434574ff424f74ff300ebdb50d194`), today's 2026-08-19 bar confirmed
  already processed by the 00:20 UTC daily run before this check started (no
  double-trade, `tick` not run this session). Next: if item 3 is ever picked
  up to actually act on the now-complete evidence base, the removal itself
  (genome defaults, mutation gene ranges, `Researcher.structural()`'s
  proposal grid, `RiskJudge._correlation_scale`, `Briefing.rets_by_symbol`/
  Analyst plumbing, several tests, and the diagnostic CLI code built to
  measure this question) touches enough interdependent places that it
  deserves its own dedicated session, not a tail-end addition to a
  diagnostic-focused one.
- **Resolved 2026-08-19 (3-hourly check): a fresh 15-generation x6-scaled-seed
  4h shadow run found three promotions, not two, all inside the first 6
  generations, then held through 9 straight stagnant generations at boldness
  climbing to 8 with no fourth — the deepest stagnation probe yet on this
  question, and it stayed flat.** (see
  `runs/2026-08-19-2137-4h-shadow-third-plateau.md`) Follow-up to item 2's
  open "does a third plateau exist past generation 10" question. Same
  isolation discipline as every prior 4h shadow run (isolated scratch dir,
  standalone script bypassing the CLI's hardcoded `n_blind=14`), this time
  with the isolation asserted at runtime (`GENOME_DIR`/`LINEAGE_PATH` checked
  to resolve under the scratch dir, would raise otherwise) rather than only
  described. Result: v1→v2 via `correlation_penalty` 0.0→**0.9** (a *fourth*
  distinct magnitude of this gene fixing a differently-broken scaled seed on
  the first try, after 0.1/0.75/0.9 seen before — still reads as "shrinks
  concentration generically against overtrading," not a validated value),
  v2→v3 via disabling `consult_conservative` as an entry source entirely (the
  researcher's own diagnostic named the reason: -943 P&L over 75 trades),
  v3→v4 via a combined 3-gene patch (`cash_floor_pct`, `trailing_stop`,
  `lone_voice_scale`). All three holdout-passed convincingly (+21.5%/+23.7%/
  +27.2% excess return). Then generations 7-15: 65 cumulative candidates
  tried against v4, boldness to 8, nothing cleared the bar. Reading against
  the 2026-08-17-0510 run (2 promotions across 10 generations, held only 1
  generation before that run ended): the *shape* replicates (quick early
  fixes, then a hard wall) but the *count* doesn't (2 vs 3 promotions,
  plateau at generation 6 vs 9) — consistent with different RNG draws
  finding different numbers of easy fixes for a differently-broken seed
  before hitting the same kind of wall, not a fixed number this recipe
  always produces. Still not proven either way whether a run reaching, say,
  30 generations would eventually break the wall — this run's contribution
  is raising the "held flat with no promotion" bar from 1 stagnant
  generation to 9. Verified safe: `live_state.json` md5 identical before/after
  (`09c35b692da1d694c5a3cace5d488f40`), `git status` clean of anything but
  the new run note (no code changed — script lived entirely in `/tmp`), full
  suite still 104 passed, today's 2026-08-19 bar confirmed already processed
  by the 00:20 UTC daily run before this check started (no double-trade,
  `tick` not run this session). Next: whether stagnation this deep ever
  breaks in a longer run is still open, but each further generation costs
  the same ~6-7 min this run's did and the marginal evidence value of "still
  flat" keeps dropping — a judgment call for whoever next has spare capacity
  and wants to spend it here, not an obviously higher-value use of a
  3-hourly slot than item 3's remaining gap or item 4's still-pending first
  real hard-call review.
- **Resolved 2026-08-19 (3-hourly check): a second, independent adversarial
  construction — selectivity fully untouched, concentration forced only
  through fewer/larger position slots — also fails the drawdown gate, and
  it's the first genome of any construction whose held-set correlation
  exceeds universe-wide in a real window.** (see
  `runs/2026-08-19-1552-correlation-adversarial-tight-concentration.md`) New
  `evotrader_bundle._adversarial_concentration_genome_tight(base)` +
  `correlation-universe --realized --adversarial-tight` answers the question
  the 12:58 run left open: does concentration require losing selectivity to
  show up? No consult entry gate is patched at all — only
  `risk_judge.max_positions` (6→3), `max_position_pct` (0.25→0.9),
  `cash_floor_pct` (0.35→0.05) and the matching `superior_judge` ceilings,
  plus `correlation_penalty` held at its inert `0.0`. Result: held-only
  correlation is higher than v3's own in every window (fold 1 +0.536 vs
  +0.523, fold 2 **+0.561 vs +0.509 universe-wide** — the first time any
  genome's held-set correlation has exceeded universe-wide, not just
  approached it — fold 3 +0.527 vs +0.427, holdout +0.514 vs +0.437), but
  full-history maxDD is **-57.5%** (v3: -34.1%), worse than the
  loosened-gates adversarial genome's -52.6%, still crossing
  `MAX_DD_HARD_FAIL`, fitness -inf. Two structurally different routes to
  concentration (lose selectivity, or keep it but force fewer/larger
  positions) both blow the same drawdown gate — stronger evidence the
  existing gates catch concentrated trading as a side effect, not an
  artefact of one adversarial recipe. Caveat: still a hand-built genome,
  never run through real `evolve` search — whether search itself would ever
  wander here before the gate kills it is untested. False start caught
  before the real run: `max_positions=2` compiles and runs but produces zero
  held-only correlation rows (`pairwise_correlation_stats` needs >=3
  simultaneously-held symbols); bumped to 3. Verified safe: purely additive
  (one new function + one new CLI flag), `py_compile` clean, full suite
  still 104 passed (no new tests, same bar the existing `--adversarial` flag
  was held to), `live_state.json` md5 identical before/after
  (`09c35b692da1d694c5a3cace5d488f40`), `evotrader.manifest` md5 identical
  (`6a4434574ff424f74ff300ebdb50d194`), `git status` clean of anything but
  the `evotrader_bundle.py` diff, `constitution verified dfae6a697f51fb49`
  unchanged throughout, today's 2026-08-18 bar (tick 5) confirmed already
  processed by the 00:20 UTC daily run before this check started (no
  double-trade, `tick` correctly reported "already traded"). Next: item 3's
  decision now has its strongest evidence base yet (4 real champions + 2
  independent adversarial constructions, all consistent) — if ever revisited
  to actually act, this is enough to decide on. The one remaining gap is
  running a concentration-forcing genome through real search rather than
  hand-building it, to see if search itself would ever approach this region.
- **Resolved 2026-08-19 (3-hourly check): the adversarial-concentration
  genome's measured correlation increase is not free — it costs a hard-fail
  on drawdown, sharpening why item 3's "drop the line" lean holds.** (see
  `runs/2026-08-19-1258-correlation-adversarial-fitness-cost.md`) The 09:51
  run's `--realized --adversarial` already runs a full-history
  `run_backtest()` per genome to reconstruct `holding_mask` — `stats`/
  `fitness`/`edge` were already in the return value, just never printed.
  Added one print line per genome, no new backtest. Result: v3 (live)
  full-history maxDD -34.1%, fitness +0.744; the adversarial genome
  (same construction as the 09:51 run — loosened entry gates, raised
  position limits) maxDD **-52.6%**, crossing the constitution's
  `MAX_DD_HARD_FAIL` (40%), fitness **-inf**, trades nearly doubled
  (1165 → 2339) for roughly half the Sortino (2.15 → 0.94). Reading against
  item 3: the genome that concentrates held-set correlation also blows
  through the hard drawdown gate — concentration and poor risk control
  travel together in this system's actual candidate space, so the existing
  `MAX_DD_HARD_FAIL`/Sortino-shaped fitness gates already select against
  concentrated trading as a side effect, not coincidentally. Strengthens
  "drop `correlation_penalty`/`correlation_lookback`/`_correlation_scale`"
  from "no real champion needed it" to "the gates already in place catch
  what it would catch." Caveat: still one adversarial construction
  (blanket-loosened selectivity) — a genome that concentrates *without*
  failing other gates (e.g. tight per-symbol selectivity, no diversification
  requirement) hasn't been tried and would be the first real case *for*
  keeping the gene. Verified safe: purely additive print statements only,
  `py_compile` clean, full suite still 104 passed, `live_state.json` md5
  identical before/after (`09c35b692da1d694c5a3cace5d488f40`), `git status`
  clean of anything but the `evotrader_bundle.py` diff, `constitution
  verified dfae6a697f51fb49` unchanged throughout, today's 2026-08-18 bar
  (tick 5) confirmed already processed by the 00:20 UTC daily run before
  this check started (no double-trade, `tick` not run this session).
- **Resolved 2026-08-19 (3-hourly check): the last remaining honest check on
  item 3's correlation question — an adversarial genome deliberately built
  to concentrate exposure, not another read of an organically-found one —
  is done, and it's the first genome (real or constructed) whose held-set
  correlation approaches universe-wide instead of sitting clearly below
  it.** (see `runs/2026-08-19-0951-correlation-adversarial-genome.md`) New
  `evotrader_bundle._adversarial_concentration_genome(base)` builds a genome
  via the same `Genome.child()` patch mechanism every real promotion uses,
  starting from live champion v3 and loosening every entry gate across all
  three consults to near pass-through plus raising every
  position-count/cash-floor limit, while leaving `correlation_penalty` at
  its default `0.0` (same as every real champion) — the question is whether
  losing selectivity alone concentrates exposure, not whether the
  already-proven-inert penalty gene would catch it. Wired into
  `correlation-universe --realized` as a new `--adversarial` flag, same
  measurement machinery as `--also-version N`. Result against a real
  full-history backtest: in fold 3 and the holdout, the adversarial genome's
  held-only correlation gap below universe-wide shrinks 6-9x versus v3's own
  gap in the same windows (fold 3: v3 −0.189 → adversarial −0.013; holdout:
  v3 −0.135 → adversarial −0.030) — fold 1/2 barely move, so the effect
  isn't uniform across regimes. Reading against the drop-vs-build decision:
  sharper, not reversed — no real champion this account has produced needs
  `correlation_penalty` (that conclusion is unchanged), but the reason is
  that ordinary fitness-driven selectivity happens to keep held sets less
  correlated as an incidental byproduct, not that concentration is
  structurally impossible here. Leans toward keeping the gene available as
  an unused safety valve rather than deleting it outright, even though
  dropping it from active use against the current champion lineage remains
  supported. Verified safe: purely additive (`core.genome`/CLI glue only,
  neither checksummed), `py_compile` clean, full suite still 104 passed (no
  new tests needed, same bar `--also-version` was held to), `live_state.json`
  md5 identical before/after (`09c35b692da1d694c5a3cace5d488f40`),
  `git status` clean of anything but the `evotrader_bundle.py` diff,
  `constitution verified dfae6a697f51fb49` unchanged throughout, today's
  2026-08-18 bar (tick 5) confirmed already processed by the 00:20 UTC daily
  run before this check started (no double-trade, `tick` not run this
  session). Next: not tried — a narrower adversarial genome aimed at one
  sector/theme instead of blanket-loosened selectivity (might concentrate
  harder than this blunt construction did), or checking whether this
  genome's measured concentration actually costs it fitness/drawdown (this
  run only measured correlation structure, never evaluated it as a trading
  candidate).
- **Resolved 2026-08-19 (3-hourly check): closed the "third real champion"
  gap the prior run flagged — v2's portfolio-realized held-set correlation
  checked, same pattern as v3 and v1.** (see
  `runs/2026-08-19-0648-correlation-realized-third-genome.md`) One-line run
  of the already-shipped `correlation-universe --realized --also-version 2`
  (no code change — `_reconstruct_champion_genome` already handles v2).
  Result: v2's held-only mean correlation is lower than universe-wide in all
  four windows (fold 1 +0.424 vs +0.630, fold 2 +0.442 vs +0.509, fold 3
  +0.411 vs +0.616, holdout +0.404 vs +0.572), same shape as v3 and v1.
  **All three real champions this account has ever had now show the
  identical pattern** — four independent measurements total (universe-wide
  structure, plus portfolio-realized for v3/v1/v2) all lean the same way:
  no visible concentration problem for a correlation-aware sizing rule to
  have caught, and not an artefact of any one champion's specific tuning.
  This exhausts the "check another real champion" data source — there is no
  fourth real genome until a new promotion happens. Verified safe:
  read-only, no code changed (`git status --short` empty), `live_state.json`
  md5 identical before/after (`09c35b692da1d694c5a3cace5d488f40`),
  `constitution verified dfae6a697f51fb49` unchanged, full suite still 104
  passed, today's 2026-08-19 bar confirmed already processed by the 00:20
  UTC daily run before this check started (no double-trade). Next: if item
  3 is ever revisited with a decision to actually make, this is now the
  strongest evidentiary base yet (n=4 measurements, 3 genuinely different
  genomes) — either treat it as sufficient and drop `correlation_penalty`/
  `correlation_lookback`/`_correlation_scale`, or run the one remaining
  honest check first: an adversarial genome deliberately built/mutated to
  concentrate exposure, not another read of an organically-found one.
- **Resolved 2026-08-19 (3-hourly check): the "genuinely different genome"
  follow-up the previous run flagged is done — a second, unrelated champion
  (v1, the seed) shows the same held-set-less-correlated-than-universe
  pattern as v3.** (see
  `runs/2026-08-19-0350-correlation-realized-second-genome.md`) New
  `correlation-universe --realized --also-version N` flag (reuses
  `_reconstruct_champion_genome`, already bit-exact-verified for
  `fold-scheme --also-version N` — no new pure function, CLI glue only, no
  new tests needed, same bar that command was held to) reconstructs any past
  champion from `live_state.json`'s own lineage and runs the same held-set
  correlation measurement against it, printing a cross-genome comparison
  table. Ran `--also-version 1`: v1's held-only mean correlation is lower
  than universe-wide in all four windows too (fold 1 +0.443 vs +0.630, fold
  2 +0.409 vs +0.509, fold 3 +0.407 vs +0.616, holdout +0.452 vs +0.572),
  same shape as v3's own numbers despite v1 and v3 differing by 13+
  generations of unrelated parametric tuning (entry/exit thresholds, sizing,
  stop-loss/trailing-stop, regime gating — none of it correlation-aware,
  `correlation_penalty` at the default `0.0` in both). Three independent
  measurements (universe-wide structure, v3's portfolio-realized structure,
  now v1's portfolio-realized structure) now all point the same way: no
  visible concentration problem for a correlation-aware sizing rule to have
  caught, and not an artefact of one champion's specific tuning. This
  answers the open gap the prior run's "Next" line named — not v2 yet (the
  account's only other real champion, could be added the same way in one
  line), but three consistent reads across two genuinely different genomes
  is a reasonable place to treat "drop `correlation_penalty`,
  `correlation_lookback`, `_correlation_scale`" as the supported conclusion,
  if this item is ever revisited to actually make the change (still not
  done this run — diagnostic-only). Verified safe: purely additive (new
  optional flag, default behavior unchanged), full suite still 104 passed
  (no new tests), `live_state.json` md5 identical before/after
  (`09c35b692da1d694c5a3cace5d488f40`), `git status` clean of anything but
  the `evotrader_bundle.py` diff, `constitution verified dfae6a697f51fb49`
  unchanged throughout, `tick` still correctly reports `already traded`
  (today's 2026-08-18 bar was already processed by the 00:20 UTC daily run,
  tick 5, before this 3-hourly check started; no double-trade). Next: if
  item 3 is ever revisited with a decision to actually make, the remaining
  honest caveat is that both measured genomes are real accidental champions,
  not a genome deliberately designed to concentrate exposure — that would be
  a different, adversarial-style check, not another pass over the same two
  data points. v2 is also available as a third real data point in one line
  (`--also-version 2`) if wanted before acting.
- **Resolved 2026-08-19 (3-hourly check): the portfolio-realized follow-up
  to the 2026-08-18 correlation-universe finding is in, and it strengthens
  the "drop the line" lean rather than reversing it.** New
  `evotrader_bundle.py correlation-universe --realized` (see
  `runs/2026-08-19-0052-portfolio-realized-correlation.md`) adds
  `loop.engine.holding_mask`, a pure function that reconstructs which
  symbols champion v3 actually held *together*, per bar, purely from one
  real full-history backtest's own `closed_trades`/`open_positions` records
  (tested, `tests/test_holding_mask.py`, 10 new tests, full suite 104 passed
  up from 94), then measures pairwise correlation restricted to each bar's
  actual held set instead of the whole universe. Result: held-only mean
  correlation is **lower** than universe-wide in all four windows — fold 1
  +0.523 vs +0.630 (−0.108), fold 2 +0.470 vs +0.509 (−0.039), fold 3 +0.427
  vs +0.616 (−0.189), holdout +0.437 vs +0.572 (−0.135). Reading this against
  item 3's open decision: the previous run's universe-wide read already
  leaned toward "drop `correlation_penalty`" because the wider universe
  wasn't hiding a differently-structured opportunity; this adds that the
  champion's own position selection (max 6 slots out of 27 symbols, no
  correlation awareness active at the default `0.0` penalty) already lands
  on a *less* correlated subset than a random universe draw would, in every
  single window measured — there is no concentration problem for a
  correlation-aware sizing rule to have caught here, empirically, not just
  in theory. Still not fully conclusive (6-8 samples per window, and this is
  one champion's one set of entry/exit rules — a differently-tuned genome
  could plausibly cluster harder), but two independent measurements (raw
  universe structure, and now realized portfolio structure) now both point
  the same direction. Verified safe: purely additive (`loop.engine` isn't in
  the checksummed set), `live_state.json` md5 identical before/after
  (`09c35b692da1d694c5a3cace5d488f40`), `git status` clean of anything but
  the new test file and the `evotrader_bundle.py` diff, `constitution
  verified dfae6a697f51fb49` unchanged throughout, `tick` still correctly
  reports `already traded` (checked before touching anything — today's
  2026-08-18 bar was already processed by the 00:20 UTC daily run, tick 5,
  before this 3-hourly check started; no double-trade). Next: if item 3 is
  ever revisited with a decision to actually make, this is now two
  consistent independent reads (universe-wide and portfolio-realized) both
  favoring drop over build — the honest next step before dropping the gene
  outright would be checking whether a genuinely different (not just
  differently-penalized) genome changes the held-set correlation picture,
  not another correlation measurement on the same champion.
- **Resolved 2026-08-18 (3-hourly check): first evidence for item 3's
  open "drop the correlation_penalty line, or build the fuller
  cross-universe factor-model version" decision — the universe is broadly
  and consistently correlated, not clustered, which weakens the case for
  the bigger structural build.** New read-only diagnostic
  `evotrader_bundle.py correlation-universe` (see
  `runs/2026-08-18-2146-correlation-universe-diagnostic.md`) adds
  `loop.engine.pairwise_correlation_stats`, a pure function summarising
  every pairwise Pearson correlation across a set of return series
  (tested, `tests/test_universe_correlation.py`, 9 new tests, full suite 94
  passed up from 85), and wires it into a new CLI command that samples 8
  points per walk-forward fold/holdout window and reports the full-universe
  30-bar-lookback correlation structure — the wider view
  `agents.judges.RiskJudge._correlation_scale` never takes (it only ever
  compares a buy candidate against symbols already *held*). Result against
  the real 27-symbol universe, full history: mean pairwise correlation is
  high everywhere (+0.52 to +0.64 across the three folds, +0.58 on the
  sealed holdout) and the holdout is not meaningfully different from the
  fold mean (+0.577 vs +0.592, a 0.015 gap, smaller than the within-window
  sample spread). Reading this against item 3's open decision: the
  five-magnitude `correlation_penalty` grid already lost against three
  champions using only held-vs-candidate comparison; this result says the
  wider universe wasn't hiding a differently-structured opportunity that a
  fuller factor model would have caught instead — correlation here is high
  and broadly uniform across regimes, not concentrated in clusters or
  spiking specifically on the holdout's crash window the way item 3's
  original crisis-contagion hypothesis expected. That leans the decision
  toward "drop the line" over "build the bigger version", though not
  conclusively — this measures raw price correlation, not
  portfolio-realized correlation (which symbols the champion actually
  holds together), and 8 samples/window is a coarse read of within-window
  variance. Verified safe: purely additive (`loop.engine` isn't in the
  checksummed set — `constitution` + `core.portfolio` only), `git status`
  clean of anything but the diagnostic, `live_state.json` md5 identical
  before/after (`c4289723973ee8ace977f7abaf0003a8`), `constitution verified
  dfae6a697f51fb49` unchanged throughout, `tick` still correctly reports
  "already traded" (no double-trade). Next: if item 3 is revisited, either
  act on this as the deciding evidence (drop `correlation_penalty`,
  `correlation_lookback`, and `_correlation_scale`, all currently dead
  weight at the default `0.0`), or run `correlation-universe` at a tighter
  `--lookback` (this run used 30, matching the gene's own default) or with
  the champion's actual held-symbol history to check whether
  portfolio-realized correlation tells a different story than raw
  universe-wide correlation does.
- **Resolved 2026-08-18 (3-hourly check): the "which sub-period drives the
  -34.1% baseline maxDD" question open since the 2026-08-16 costs/holdout
  diagnostic now has a real answer — one specific 127-bar episode, not a
  spread of many.** New read-only diagnostic `evotrader_bundle.py drawdown
  [--holdout]` (see `runs/2026-08-18-1846-drawdown-episode-diagnostic.md`)
  adds `loop.engine.drawdown_episodes(nav_history)`, a pure function that
  walks the champion's own `nav_history` (already returned by
  `run_backtest`, nothing new computed) into peak-to-trough-to-recovery
  episodes ranked by depth, each tagged with the walk-forward fold (or
  sealed holdout) its peak falls in. Verified the deepest episode
  reproduces `stats()`'s own `max_dd` to the decimal (same running-peak
  definition, cross-checked in `tests/test_drawdown.py`, 7 new tests, full
  suite 85 passed up from 78). Result against champion v3, full history:
  the reported -34.1% maxDD is **one episode**, 2024-03-31 to 2024-08-05
  (127 bars, recovered by 2024-11-10), sitting inside **fold 2** — the same
  fold every prior regime/fold-scheme diagnostic already flagged as a
  +200%+ melt-up outlier. Reading them together: a violent pullback inside
  a violent melt-up is exactly what you'd expect from that fold's own
  character, not a separate finding — this diagnostic supplies the missing
  "when and how much" the regime/fold-scheme work had been inferring
  indirectly. The next-deepest full-history episode (-29.2%,
  2025-11-08 to today, still unrecovered) falls in fold 3, and under
  `--holdout` alone the same still-open episode reappears as the sealed
  holdout's own worst drawdown (-26.6%, 2026-05-08 to today) — the current
  live drawdown is not a fold-2 echo, it is its own ongoing episode.
  Verified safe: purely additive (new CLI branch plus one new pure function
  in `loop.engine`, not in the checksummed set), `live_state.json` md5 and
  `git status` confirm untouched, `constitution verified dfae6a697f51fb49`
  unchanged. One bug caught and fixed before commit: the first draft tagged
  every episode's fold/holdout window using full-history fraction math even
  under `--holdout`, which mislabeled every row "fold 1"/"fold 2" inside a
  replay that was already 100% holdout data — fixed to report `holdout` for
  every row when `--holdout` is passed. Next: this is diagnostic-only, no
  code path acts on it; if the regime-stratified/rolling fold-scheme
  redesign mentioned throughout this file's fold-scheme entries is ever
  attempted, `drawdown --holdout` is now a one-line way to check whether a
  redesigned holdout window still contains the same still-open drawdown or
  a cleaner one.
- **Resolved 2026-08-18 (3-hourly check): swept the third and final real
  champion (v1, the seed) through `fold-scheme`, and it flips the prior
  run's read.** (see `runs/2026-08-18-1549-fold-scheme-third-champion.md`)
  `--also-version 1` needed no code change — `_reconstruct_champion_genome`
  already handles version 1 (the seed, no patches) — so this was a pure
  read-only re-run of the existing diagnostic. `aggregate_fitness` at v1:
  -2.577 (n=3) → 0.244 (n=5) → -0.938 (n=8) — **non-monotonic**, the same
  qualitative swing shape v3 showed, not v2's monotonic decrease. That
  means 2 of 3 known champions swing non-monotonically and only 1
  decreases monotonically — the opposite conclusion from the 12:56 UTC
  run below, which (with only v2 and v3 to compare) called the swing
  "v3-specific." With all three real champions this account has ever had
  now checked, non-monotonicity looks like the more common shape on this
  fixed 3-fold calendar split, not an outlier tied to one genome — though
  n=3 is still small, and v1's fitness was weak throughout (0/3, 1/5, 1/8
  folds beat benchmark), a possible confound not teased apart. Verified
  safe: no code changed, `git status` clean, `live_state.json` md5
  unchanged, `constitution verified dfae6a697f51fb49`, full suite still 78
  passed. Next: `--also-version N` has now swept every champion this
  account has had; the next genuinely new data point only arrives when a
  fourth champion is promoted. If a regime-stratified/rolling fold-scheme
  redesign is ever attempted, treat non-monotonicity as a property of the
  fold split worth designing around, not a v3 quirk to dismiss.
- **Resolved 2026-08-18 (3-hourly check): checked whether the fold-scheme
  finding replicates across champions, as the prior run's "Next" line
  flagged — and it sharpens the finding rather than confirming it as
  stated.** New capability `evotrader_bundle._reconstruct_champion_genome`
  (see `runs/2026-08-18-1256-fold-scheme-champion-replication.md`) rebuilds
  a historical champion genome purely from `live_state.json`'s own recorded
  `lineage` patches (no genome archive persists — `state/genomes/` is
  gitignored, rebuildable-cache-only), verified bit-exact against the real
  live champion's genes before trusting it
  (`tests/test_fold_scheme_reconstruction.py`, 6 new tests built from the
  real lineage, full suite 78 passed up from 72). Wired into the CLI as
  `fold-scheme --also-version N` (purely additive — no flag reproduces the
  exact prior output, verified against the 09:52 run's numbers). Ran it
  against v2 (the account's first real self-promotion) alongside live v3.
  Result: the **outlier gap** (fold 2's b&h-return dominance) is identical
  to the decimal across both champions at every fold count — but that's not
  really a replication finding, since the outlier gap is computed purely
  from buy-and-hold return per fold, which by construction never depends on
  the genome under test; any genome would show the same number. The column
  that actually is genome-dependent, **aggregate_fitness**, does *not*
  replicate the same shape: v3 swings non-monotonically across fold counts
  (-1.224 → +1.633 → -0.500) while v2 decreases monotonically
  (0.581 → 0.196 → -0.836). Two points isn't a law, but it does mean the
  09:52 run's "aggregate_fitness swings non-monotonically" finding is
  specific to v3's genome, not a fold-scheme property every champion would
  show. Next: `--also-version N` is now available for any future
  cross-champion check without re-deriving the reconstruction; if the
  regime-stratified/rolling fold scheme redesign is ever built, evaluate it
  per-genome, not assuming one champion's behavior generalizes.
- **Resolved 2026-08-18 (3-hourly check): the fold-scheme open question from
  the 2026-08-17 regime diagnostic has a first quantified answer — fold 2's
  dominance is a fold-*count* artefact, and fixing it isn't as simple as
  raising `N_FOLDS`.** New read-only diagnostic `evotrader_bundle.py
  fold-scheme` (see `runs/2026-08-18-0952-fold-scheme-sensitivity.md`)
  re-evaluates champion v3 under `n_folds` 3/5/8 via the existing
  `loop.evolve.Evaluator` class (already took `n_folds` as a constructor
  argument, so nothing structural changed). Result: the "outlier gap"
  (fold 2's +220% b&h return vs the mean of the other folds) shrinks sharply
  and monotonically as fold count rises — +219.4% (n=3) → +53.8% (n=5) →
  +52.0% (n=8) — confirming the outlier's leverage over `aggregate_fitness`
  is mostly an artefact of there being only 3 folds. But
  `aggregate_fitness` itself does *not* move safely with fold count: -1.224
  (n=3) → +1.633 (n=5) → -0.500 (n=8), and at n=8 the smallest fold (95
  bars) came within 25 bars of `run_backtest`'s 120-bar hard minimum and one
  fold failed a hard gate outright (`fitness=-inf` despite positive excess
  return). Reading both together: naively raising `N_FOLDS` on the current
  fixed 85/15 calendar split just trades "one big outlier fold" for "small
  folds hitting the MIN_TRADES/MIN_BARS/maxDD floor more often" — not a fix
  by itself. A regime-stratified or rolling fold scheme (not attempted this
  run, bigger scope) looks like the more promising direction: it could
  dilute the outlier the same way more folds do, without shrinking any
  individual fold below the hard-gate minimums. Caveat carried from every
  full-history diagnostic here: this run's -1.224 at n_folds=3 does not
  match v3's recorded 1.389 promotion-time fold-aggregate fitness, because
  `load_universe(..., 4.0)` loads a different sliding 4-year window (ending
  today, not 2026-08-16) — only valid for relative comparison across fold
  counts on the same snapshot. Verified safe: purely additive (only a new
  CLI branch in `main()`, outside the embedded `_SRC` bundle strings; no
  constitution or `Evaluator` code changed), `live_state.json` md5 identical
  before/after, `constitution verified dfae6a697f51fb49` unchanged, full
  test suite still 72 passed (no new tests needed — print-only CLI glue over
  an already-tested class, same bar `regime`/`costs`/`anatomy`/`consults`
  are held to). Next: if a fold-scheme redesign is ever undertaken, target a
  regime-stratified/rolling scheme, not a higher fixed `N_FOLDS` — that is a
  constitution change (checksummed, needs an `AMENDMENTS.md` row and much
  more design than fit in one 3-hourly session) and should not be done
  without first checking whether the pattern replicates on other champions
  (this is one champion, one data snapshot).
- **Resolved 2026-08-18 (3-hourly check): the live 1d champion v3 shows the
  same fold-vs-holdout entrenchment pattern the 2026-08-18 4h-shadow work
  hypothesized, confirmed with 9 real draws, not one shadow anomaly.** New
  read-only diagnostic `evotrader_bundle.py holdout-pressure` (see
  `runs/2026-08-18-0655-holdout-pressure-diagnostic.md`) reads
  `live_state.json`'s own recorded `lineage` — no new `evolve` run needed —
  and separates "nothing cleared the fold-aggregate gate" from "something
  did and the sealed holdout rejected it anyway." Result: since v3's
  promotion, 9 generations of real search (the weekend all-hands' `evolve
  15`, round 2, continuing past the promotion) produced 9 individual
  candidates whose fold-aggregate fitness (1.6–1.98) comfortably beat
  champion v3's own 1.389, cleared the multiple-testing margin, and every
  single one still lost the sealed holdout. Sharper than "lost": 6 of the 9
  scored holdout fitness identical to the champion's own (-1.172 to 3
  decimals) rather than clearly worse — those specific patches apparently
  make no difference to trading behavior inside this particular short,
  crash-regime holdout window, so the gate ties instead of discriminating.
  Only 3 of 9 scored meaningfully worse; none scored better. Not evidence
  the gate is miscalibrated — it's doing what it's designed to do — but a
  concrete, non-hypothetical data point that this specific holdout window is
  currently closer to "a fixed hurdle most patches can't move" than "a
  discriminating out-of-sample test," worth weighing if the fold/holdout
  scheme ever gets revisited (see item 2's existing open question about
  `FOLD_CONSISTENCY_WEIGHT` and a rolling/regime-stratified fold scheme).
  Verified safe: purely additive (`loop.evolve` isn't in the checksummed
  set), tested (`tests/test_holdout_pressure.py`, 8 new tests built from the
  real `constitution.holdout_accepts()` output so a template change breaks
  the parser loudly, full suite 72 passed up from 64), `live_state.json`
  untouched (`git status` confirms), `summary`/`signals`/`tick` all still
  report `constitution verified dfae6a697f51fb49`. Next: run
  `holdout-pressure` after any future `evolve` call that doesn't promote —
  folded into the routine post-evolve checklist alongside `hard-calls`.
- **v0.1 · genome v3** — second self-promotion, found by the live account's
  own blind search on 2026-08-16 (weekend all-hands)
- **Live paper account** opened 2026-08-15 with $10,000 imaginary
- **Universe:** 27 liquid USDT pairs with 4+ years of history, plus PAXG (gold)
  as a deliberately uncorrelated asset
- **Roster:** analyst → risky/moderate/conservative consults → risk judge →
  superior judge → trader, with a guardian issuing unvetoable exits
- **Resolved 2026-08-16 (3-hourly check): a real test suite is now committed**,
  closing the gap flagged earlier the same day (the old "29 tests pass" claim
  was never in git — `git log --all` had no test file, ever). `tests/`
  (36 tests, `pytest`) is hermetic: no network, never touches the real
  `live_state.json` or `state/`. Covers `Genome` save/load/child/promote
  roundtrip, the constitution's `fitness`/`accepts`/`holdout_accepts`/
  `required_margin` gates including the multiple-testing margin's growth
  with candidate count, checksum tamper detection, `LiveAccount.tick`'s
  same-bar idempotency guard (including that it only checks `journal[-1]`,
  by design, and that `force=True` bypasses it), and — the one that matters
  most — anti-lookahead-bias: both a direct unit test on
  `core.market.Replay`/`ReplayWindow`'s slicing, and an end-to-end
  `run_backtest` test that poisons every bar after a backtest's window and
  asserts the result (stats, trades, decision log, fitness) is bit-for-bit
  identical to an unpoisoned run, plus a control test proving the comparison
  is actually sensitive (poisoning a bar *inside* the window does change the
  result). `.github/workflows/ci.yml` now runs `pytest tests/` as its own
  job, ahead of the existing compile/live-path smoke test.
  One caveat worth knowing for next time: `Genome`'s `GENOME_DIR` (and the
  other bundle modules' cwd-derived paths — `core.live.STATE_PATH`,
  `core.market.CACHE_DIR`, `loop.evolve.LINEAGE_PATH`) are computed **once**
  at module-import time from the process's cwd at that moment, not
  re-evaluated per test — `monkeypatch.chdir` alone does nothing for tests
  that exercise them; a first draft of the genome tests briefly wrote real
  files into this repo's `state/` before that was caught and fixed by
  monkeypatching `GENOME_DIR` directly (see `tests/test_genome.py`'s
  `isolated_cwd` fixture). Deleted before committing; nothing tracked was
  ever affected.
- **Resolved 2026-08-16 (3-hourly check): fee/slippage cost-sensitivity now
  measured.** New read-only diagnostic `evotrader_bundle.py costs` (same
  guarantees as `anatomy`/`consults` — full-history replay, never touches
  `live_state.json`) answers the "perturbation tests on fees/slippage" item
  from "Measured 2026-08-16" below. Full numbers in
  `runs/2026-08-16-1552-cost-sensitivity.md`. Headline: excess return over
  buy-and-hold degrades smoothly and stays strongly positive under stress
  (+473% baseline -> +209-261% at 2x-5x cost multipliers on this
  full-history replay) — costs are a real drag, not what breaks the
  strategy. The one number worth carrying forward: baseline maxDD on this
  same replay is already -34.1% against the constitution's 40%
  hard-fail-gate (`MAX_DD_HARD_FAIL`), and a 1.5x cost multiplier is enough
  to cross it (-45.1%) — a thinner margin to that gate than the return
  numbers alone suggest. (Two of the five scenarios show `fitness = -inf`;
  that's the hard-fail gate firing on drawdown, not a monotonic
  cost-sensitivity signal — the run note explains why the fitness column
  and the return columns tell different stories here.) Not promotion-grade,
  not walk-forward — a full-history point estimate per scenario, same
  caveat as `anatomy`/`consults`.
- **Resolved 2026-08-17 (3-hourly check): a genuinely unscaled 4h seed does
  NOT reach the same outcome as the x6-scaled seed used in every prior 4h
  shadow run.** 10 generations, `bar_interval=4h`, period genes left at
  their 1d values: three generations (not one) to claw from fitness -4.515
  to -0.445, never crossing into positive fold-aggregate fitness across 10
  generations, vs. every scaled run's single-generation jump to 0.6-0.8+.
  Also surfaced an anomaly worth a closer look later: every accepted
  version's fold-aggregate fitness stayed negative while its sealed-holdout
  fitness was strongly positive and rising — the opposite of the usual
  overfitting pattern, likely a regime mismatch between the newest-15%
  holdout slice and the older search folds for this genome specifically.
  Full numbers and the fold/holdout table in
  `runs/2026-08-17-0820-4h-shadow-unscaled-seed.md`. Shadow-only, as always:
  did not touch `live_state.json`, `researcher_memory`, or the real
  champion (still v3, 1d bars).
- **Resolved 2026-08-18 (3-hourly check): a fresh 16-generation unscaled-seed
  run answers the follow-up question (more generations alone doesn't help)
  and explains *why* it stalls.** (see
  `runs/2026-08-18-0232-4h-shadow-unscaled-seed-16gen.md`) Same two-promotion
  shape as the 10-generation run (fold-aggregate -4.508 -> -1.054 (gen 4) ->
  -0.241 (gen 8)), then held through 8 more generations despite dozens of
  candidates clearing the fold-aggregate acceptance bar with solidly
  positive fitness (0.099 to 1.080) — every one was rejected at the sealed
  holdout instead. Champion v3's own holdout draw happened to land at a
  strong 1.079 on a genome whose fold fitness is -0.241 (the same
  fold/holdout anomaly as the 10-generation run), and every challenger's
  holdout score is one noisy point estimate on that same short crash window
  (7 challenger draws ranged -1.664 to +0.907, no correlation with
  fold-side quality) that essentially never clears 1.079 plus a
  cumulative-draws margin. **General finding, not 4h-specific: a lucky
  holdout draw at promotion time can entrench a champion against
  genuinely-better-on-search-folds challengers**, for as long as the
  holdout window is short enough for its per-candidate score to be noisy —
  worth watching for on the live 1d account too. Flagged, not fixed; one
  lucky draw, not proof the gate is mistuned. Shadow-only, verified
  `git status` clean and `live_state.json` md5 unchanged.
- **Resolved 2026-08-17 (3-hourly check): the "flag hard calls" half of item
  4 (LLM-backed consults) is now built.** New `agents.judges.flag_hard_call`
  is a pure, deterministic function that labels a decision-log bar as a hard
  call when: the circuit breaker just tripped, the Superior Judge overrode
  the Risk Judge on at least one order that bar, or a live buy went through
  behind agreement below 0.4 (three consults, weak consensus, real money
  moving anyway). Wired into `loop.engine.Council.tick`, which now attaches a
  `"hard_call": {"is_hard_call": bool, "reasons": [...]}` field to every
  decision-log entry it already logs. Purely additive and verified so: the
  flag is computed strictly *after* `Trader.execute()` has already filled the
  bar, and a new test (`tests/test_hard_calls.py`) asserts
  `log_detail=True` vs `log_detail=False` produce byte-identical `stats` and
  `closed_trades` on the same synthetic data — the flag cannot change what
  gets traded, only what gets logged about it. Constitution checksum
  unaffected (`agents.judges`/`loop.engine` aren't in the checksummed set);
  verified live via `evotrader_bundle.py summary`/`signals`/`tick` all still
  reporting `constitution verified dfae6a697f51fb49`, plus the full test
  suite (45 passed, up from 36). Not yet built: the other half of item 4 —
  actually spending a scheduled session's own reasoning on a flagged bar and
  feeding a verdict back into the trading decision. This only marks the
  candidates a future phase would look at; nothing reads `hard_call` yet.
  Next: run a live tick or two and check whether any real bars actually get
  flagged (the 0.4 agreement threshold and the buy-only gating are first
  guesses, not tuned against real decision-log data yet), then design what
  "apply consult verdict" actually means procedurally for an unattended
  schedule that can't pause mid-tick for a human.
- **Resolved 2026-08-17 (3-hourly check): measured how often `flag_hard_call`
  actually fires, and the threshold as shipped is too loose to be useful.**
  New read-only diagnostic `evotrader_bundle.py hard-calls` (same guarantees
  as `anatomy`/`consults`/`costs`/`regime` — full-history replay, never
  touches `live_state.json`) plus a pure aggregator
  `agents.judges.summarize_hard_calls` (tested, `tests/test_hard_calls.py`
  now 12 tests up from 7, full suite 49 passed up from 45) answer the "run a
  live tick or two and check whether any real bars actually get flagged"
  line directly above — a full backtest replay runs every bar through the
  same `Council.tick`/`flag_hard_call` call a live tick would, so it answers
  this across four years of bars instead of one tick a day. Result against
  the real champion v3: **535/1386 logged bars (38.6%) flag as hard calls.**
  Broken down by trigger: `circuit_breaker` 4, `superior_override` 85,
  `low_agreement_buy` 455 (some bars trip more than one, so these don't sum
  to 535). The dominant trigger is nearly meaningless as a filter: with
  exactly 3 consults, agreement is discretized to 0/0.33/0.67/1.0, so
  "agreement < 0.4 behind a buy" is mechanically identical to "exactly one
  consult proposed this buy" — a normal, frequent pattern the system already
  handles procedurally (`risk_judge.lone_voice_scale` sizes it down), not an
  exceptional disagreement worth a slower second look. Drop that one trigger
  and the rate falls to `circuit_breaker` + `superior_override` ≈ 89/1386
  (6.4%) — a rate a human or LLM review pass could plausibly keep up with;
  38.6% is not. The live journal has 0 flagged ticks so far, but all 3 real
  ticks predate the field (it shipped after tick 3 ran) — nothing to compare
  against yet from real trading; `evotrader_bundle.py hard-calls` will start
  reporting real flags from tick 4 onward. Not changed this run:
  `flag_hard_call`'s own logic and threshold are untouched — this only
  measures what the as-shipped definition does. Narrowing what counts as a
  "hard call" (e.g. dropping the low-agreement trigger, or replacing it with
  something that isn't just "lone voice, yes/no") is the judgment call this
  item already flagged as needing a decision — now with real numbers behind
  it instead of a guess.
- **Resolved 2026-08-17 (3-hourly check): the third narrowing axis — size
  relative to portfolio equity, composing with the solo-bar requirement —
  worked, cutting the rate further to 9.6%.** (see
  `runs/2026-08-17-2146-hard-call-size-gate.md`) Rate: 38.6% (original) →
  52.0% (conviction-only, backfired) → 24.4% (solo-bar) → **9.6%** (this
  change), close to the ~6.1% `circuit_breaker`+`superior_override`-only
  floor instead of ~4x it. `agents.judges.flag_hard_call` gained two new
  optional parameters, `nav` and `min_size_pct` (both default to off —
  `min_size_pct=0.0` reproduces the exact solo-bar-only behavior, so this is
  purely additive): when `min_size_pct > 0`, a solo lone-voice buy only
  flags if its `quote_amount / nav` clears that fraction. No `nav` supplied
  while `min_size_pct > 0` fails safe (does not flag) rather than guessing.
  Chose `min_size_pct=0.10` empirically: of the 253 solo lone-voice bars on
  a full-history replay, position sizes ranged continuously from a fraction
  of a percent of equity to 24.8% with no natural break, and 10% was the
  point where this trigger's own contribution drops from 18.3% of all bars
  to 3.5% (48 bars) while still catching every solo bet that risks a real
  slice of the account. Wired into `loop.engine.Council.tick`'s
  `flag_hard_call` call (`nav=nav, min_size_pct=0.10` — `nav` was already
  computed in that scope, nothing new to thread through). Tested
  (`tests/test_hard_calls.py`, 55 passed up from 51, including cases for:
  size gate off by default, a big-enough solo buy flags, a too-small solo
  buy does not, and no-`nav`-supplied fails safe). Verified live path
  unaffected: `constitution verified dfae6a697f51fb49`, `live_state.json`
  md5 identical before/after, `hard-calls` reproduced the projected number
  exactly (133/1386, 4 circuit_breaker + 85 superior_override + 48
  low_agreement_buy). 9.6% is real progress and the closest yet to a rate
  either (a) or (b) from item 4 below could plausibly act on — the fallback
  of dropping `low_agreement_buy` entirely (≈6.4%/6.1%) is now a much
  smaller step down from here than from the original 38.6%, so the next
  useful move is picking (a) vs (b) rather than narrowing further.
- **Resolved 2026-08-17 (3-hourly check): a second narrowing attempt —
  "solo bar" (lone-voice buy must be the bar's *only* order at all, no other
  buy, no sell) — worked, real reduction not another backfire.** (see
  `runs/2026-08-17-1850-hard-call-solo-bar-narrowing.md`) Rate: 38.6%
  (original) → 52.0% (highest-conviction attempt, backfired) → **24.4%**
  (this change). `agents.judges.flag_hard_call`'s low-agreement trigger now
  requires `len(orders) == 1`, distinguishing "the whole council went quiet
  except one loud voice" from "one of several independent picks that bar
  happened to be lone-voice" — the axis the prior run's item explicitly
  named as untried. Tested (`tests/test_hard_calls.py`, 51 passed up from
  50, including a new case the old conviction-only logic couldn't even
  express: a lone-voice buy next to an unrelated *sell* doesn't flag).
  Verified live path unaffected (`constitution verified dfae6a697f51fb49`,
  `live_state.json` md5 identical before/after). 24.4% is real progress but
  still well above the ~6.4% `circuit_breaker`+`superior_override`-only
  floor — not yet at a rate either (a) or (b) from item 4 below can
  comfortably act on. `circuit_breaker` (4) and `superior_override` (85)
  counts unchanged, as expected — this only touches the low-agreement
  trigger.
- **Resolved 2026-08-17 (3-hourly check): tried the suggested narrowing —
  "only fire when a lone-voice buy is also the highest-conviction/largest
  order that bar" — and it made the rate worse, not better.** (see
  `runs/2026-08-17-1553-hard-call-trigger-narrowing.md`)
  `agents.judges.flag_hard_call` reworked to read each buy `Order`'s own
  `agreement` field instead of the old bar-level average `agreement_score`
  (signature changed: `flag_hard_call(orders, just_halted,
  overrides_this_bar, low_agreement_threshold=0.4)`), and only flags the
  bar's single highest-conviction buy if that specific order is lone-voice.
  Tested (`tests/test_hard_calls.py`, 50 passed up from 49, including a new
  test asserting a lone-voice buy sitting next to a stronger better-agreed
  buy does *not* flag). Verified live path unaffected (`summary` still
  reports `constitution verified dfae6a697f51fb49`, same NAV;
  `live_state.json` untouched). Re-ran `hard-calls` against champion v3: the
  `low_agreement_buy` rate rose from 32.8% to 46.4% of bars (total flagged
  38.6% → 52.0%). Diagnosed why: "lone-voice" and "highest-conviction buy
  that bar" are not independent in this system — 73-89% of bars with any buy
  orders have their top-conviction buy also be the lone voice (trivially true
  whenever there's only one buy order that bar, which is most of them; even
  in multi-buy bars a single confident consult routinely outranks
  weaker-conviction unanimous/two-agree proposals). The old bar-aggregate
  version accidentally diluted this by averaging in sell orders' typically
  higher agreement; reading the buy's own agreement directly removes that
  dilution and exposes more bars, not fewer. Real negative result, not a
  wasted change — it rules out "conviction leadership" as a narrowing axis
  and sharpens what's actually still open (see Next steps item 4).
- **Resolved 2026-08-16 (3-hourly check): the holdout-window question above
  answered, and the answer is the opposite of what was suspected.** Added a
  `--holdout` flag to `evotrader_bundle.py costs` (same guarantees, still
  read-only) that replays only the sealed `HOLDOUT_FRAC` slice (newest 15%
  of history, never touched during search) instead of the full 4 years.
  Baseline holdout numbers sanity-check against the known v3 promotion
  record (+21.7% excess return here, matching "Current state" above) —
  confidence the window slicing is correct. Result: baseline holdout maxDD
  is -26.2%, rising only to -31.7% at 2x costs — nowhere near the 40%
  hard-fail gate, and notably *safer* than the full-history stress test's
  -34.1% to -45.1% range, not thinner as speculated. Read this together, not
  separately: the champion is losing money outright on this specific
  holdout slice under every cost scenario (baseline return -15.0%, fitness
  -1.172) while still beating buy-and-hold by the same +21.7% margin that
  passed the original promotion gate — it is a genuinely hard window for
  the strategy, just not one that trips the drawdown gate. Full numbers in
  `runs/2026-08-16-1846-costs-holdout-diagnostic.md`.

  **Resolved 2026-08-18 (3-hourly check): the sub-period question above
  answered.** See "Current state" above and
  `runs/2026-08-18-1846-drawdown-episode-diagnostic.md` — new
  `evotrader_bundle.py drawdown` isolates the -34.1% full-history maxDD to
  one 127-bar episode (2024-03-31 to 2024-08-05) inside fold 2, the same
  fold the regime/fold-scheme diagnostics already flagged as a +200%+
  melt-up outlier — not a bear-market segment, a sharp pullback inside a
  violent bull fold.

### The first promotion (v1 → v2)

Found by blind search, not by diagnosis:

| gene | was | now | effect |
|---|---|---|---|
| `consult_risky.conviction_scale` | 1.20 | 0.74 | the momentum chaser was overconfident; turn it down |
| `consult_moderate.rsi_lo` | 45.0 | 35.2 | let the trend follower buy earlier in the RSI band |

Fold-aggregate fitness 0.576 → 0.889. On the **sealed holdout it never saw**:

| | return | sortino | maxDD | trades |
|---|---|---|---|---|
| v1 seed | −23.6% | −2.29 | −26.3% | 238 |
| **v2 evolved** | **−20.6%** | **−2.15** | **−24.3%** | 240 |
| buy-and-hold | −36.7% | — | −42.2% | — |

Read this honestly: v2 is a real improvement that generalises to unseen data, and
both genomes lost less than the market in a bear window. Neither makes money.
Losing less than buy-and-hold in a downturn is a start, not a strategy.

### The second promotion (v2 → v3), 2026-08-16 weekend all-hands

v2 had plateaued for 13+ generations by the time the 2026-08-16 shadow runs
(see "Measured 2026-08-16" and the run notes from that day) started finding
gate-passing improvements over it in isolated copies but never applied them
live. The weekend all-hands ran real `evolve` against the actual account
instead of splicing in a shadow result: `evolve 8` found nothing (252
candidates tried, cumulatively excluded), `evolve 15` continuing from there
found a promotion at generation 6. Full patch and reasoning in
`runs/2026-08-16-0600-weekend-all-hands.md`. Headline numbers:

Fold-aggregate fitness 0.682 → 1.389, merged fitness 0.805 → 1.591 (no
regression), drawdown 32.6% (within the 15% regression tolerance on v2's
~30%). Sealed holdout: challenger beat both champion and buy-and-hold —
excess return +21.7%, excess Sharpe +0.44, drawdown 16.0 points better than
benchmark in that window. Thirteen genes moved together (tighter
stop-loss/trailing-stop, `max_bars_held` 60→15, retuned RSI/regime/z-score
thresholds across all three consults, larger `base_size_pct` with a much
higher `cash_floor_pct`) — not a one-line tune.

Same caveat as v1→v2: this beats the previous champion and the holdout, it
is not yet evidence the policy beats doing nothing on the full replay — see
"Measured 2026-08-16" below, which still applies unchanged to v3.

### Two flaws found by watching it run

**1. The margin was on the wrong metric.** The multiple-testing correction was
applied to the merged fold stats, which rank nothing, while the fold-aggregate
that actually selects the winner had no correction at all. Selection bias enters
wherever you mine for a maximum. Fixed, and a second gate added (merged fitness
may not regress). The first promotion happened immediately after.

**2. The Researcher had no memory.** Four consecutive generations re-tested the
identical candidate (`regime_scale.bear`, 0.959) and re-rejected it — twelve
fold-backtests spent re-learning one "no". Proposals are now keyed by their patch
and excluded until the champion changes. Two consequences:

- Multiple testing is now counted **cumulatively per champion**. Every candidate
  ever tried against a fixed champion is another draw from the same urn, so an
  unbeaten champion's bar rises the longer it stands.
- **Stagnation-driven boldness**: as generations pass without a promotion, blind
  search takes wider steps and mutates more genes at once. The local hill has
  been climbed; what's left is either further away or isn't there.

A related bug was fixed on 2026-08-15: this memory lived only in the `evolve`
process's RAM, not in `live_state.json`, so it was forgotten between separate CLI
invocations. Now persisted via a `researcher_memory` field, seeded back in on
every `evolve` call.

---

- **Resolved 2026-08-18 (3-hourly check): the "review after the fact" half of
  item 4 (LLM-backed consults) now has its first piece of infrastructure —
  design (b) was chosen over (a).** `LiveAccount` gained a new durable field,
  `hard_call_reviews` (defaults to `[]`, backward-compatible with every
  state saved before this shipped), and a new method
  `add_hard_call_review(tick, verdict, notes)` that appends a reasoned
  verdict onto a flagged journal entry — raising if the tick doesn't exist
  or was never actually flagged, so a typo can't manufacture a review out of
  nothing. A new pure function, `agents.judges.pending_hard_call_reviews`,
  is a read-only set difference between `journal` and `hard_call_reviews`
  (matched by tick). New CLI command `evotrader_bundle.py review-hard-calls`:
  with no args, lists any flagged-but-unreviewed bars in plain language and
  exits; with `--tick N --verdict '...' [--notes '...']`, records a verdict
  and saves — the only thing this command does that touches
  `live_state.json`. Chose (b) over (a) explicitly: the measured flag rate
  (~9.6% as of 2026-08-17, well down from the original 38.6%) is low enough
  that a scheduled session reviewing after the fact is workable — at most
  one live bar a day, so under 1 in 10 days produces anything to review —
  whereas (a)'s stop-before-execution split would still reintroduce the
  fills-happen-later problem `core.live`'s docstring deliberately avoids,
  for a rate that no longer needs it. Verified safe: purely additive (no
  code upstream of this touches trading), tested
  (`tests/test_hard_calls.py` +4, `tests/test_live_account.py` +5, full
  suite 64 passed up from 55, including the ValueError guards and a
  save/load round-trip test), and smoke-tested against a throwaway copy of
  `live_state.json` with a synthetic flagged entry (list → record a verdict
  → list again shows 0 pending) — the real `live_state.json` md5 was
  identical before and after this entire cycle's work, and
  `constitution verified dfae6a697f51fb49` unchanged throughout. As of this
  writing no live journal entry has ever actually flagged
  (`is_hard_call: true`) — tick 4 was the first tick with the field present
  and it was `false` — so this ships ahead of its first real case, not in
  response to one; nothing in the scheduled run protocol calls this command
  yet. Next: once a real live tick actually flags (watch for it in
  `runs/*-daily-trading.md` notes or a `review-hard-calls` check), a
  scheduled session should read the flagged case, reason about it inline,
  and record a verdict via `--tick`/`--verdict`/`--notes` — that first real
  review is the thing this infrastructure was built for, not more tooling
  around it.

## Next steps (rough priority order)

1. **Accumulate live forward-test data** — the only track record not contaminated
   by hindsight. This happens on its own; just don't break it.

2. **4h bars for ~6× more observations and a tighter fitness estimate.**
   Infrastructure shipped 2026-08-15: `genome.bar_interval` (defaults `"1d"`,
   zero behavior change for existing genomes), threaded through `core.live`,
   `loop.engine`'s backtest + annualization (`core.market.BARS_PER_YEAR`), and
   the `evolve` CLI. Verified against real 4h Binance data end-to-end.
   **Decision 2026-08-15: stays off.** Live cadence stays daily — speeding it to
   ~4h would multiply scheduled-task usage. When there's spare capacity, run a
   fresh evolution from the seed genome at 4h granularity as a shadow/offline
   exercise (compute only, must not touch `live_state.json`) to get real
   comparative data before ever switching the live cadence.

   **First shadow evolution run 2026-08-16** (see `runs/2026-08-16-0000-shadow-4h-evolution.md`
   for full numbers): the raw seed genome at 4h bars is not just worse, it's
   broken — bar-count genes (`trend_slow`, `regime_ma`, `max_bars_held`, ...)
   mean 6x less wall-clock time at 4h, so the system overtrades and every
   evolved candidate across 2 generations failed a hard drawdown/trade-count
   gate outright (fitness −4.46, halts 9–10/run). Hand-scaling those genes ×6
   before evolving fixed it: fitness went −2.42 → 0.81 in one accepted
   promotion (sealed holdout passed), max_dd −43%→−19%, halts to 0. Still just
   2 generations on a scaled-not-retuned starting point, not checked against
   live champion v2 head-to-head — **not a promotion case**, but it does answer
   the open question from the plan sketch: a 1d-tuned genome cannot be ported
   to 4h as-is, and "reset to seed + let evolution retune" needs the periods
   pre-scaled to even be searchable, not just picked as the honest option.
   Next: more generations from the scaled starting point, or a longer blind
   search from a genuinely fresh (unscaled) seed to see if it converges to
   similar period values on its own.

   **Second shadow run 2026-08-16 (weekend all-hands)** (see
   `runs/2026-08-16-0600-weekend-all-hands.md`): a fresh scaled-seed 4h run
   (correctly isolated this time — the first attempt that session
   accidentally re-ran the real 1d champion v2 due to a scratch-dir setup
   bug, logged in the same run note as a caught mistake) found its own
   generation-1 promotion, fitness −2.374 → 0.469 (`breakout_len`,
   `max_position_pct`), then held at generation 2. Weaker magnitude than the
   first run's 0.81 but the same qualitative shape: catastrophic unscaled
   seed → workable after ×6 scaling → quick first promotion → stagnation.
   Stopped after 2 generations on a time-budget call — at `n_blind=14`
   (the CLI default, calibrated for 1d cost) each 4h generation took
   ~25-27 minutes, ~6x the 1d cost as expected from ~6.3x more bars per
   fold. **Open item, sharper than before**: run 4h shadow evolution with
   `n_blind=5-8` instead of the default, or fewer generations per
   invocation — the default proposal batch size is not calibrated for this
   bar size's backtest cost.

   **Resolved 2026-08-16 (3-hourly check): `n_blind=6` confirmed workable**
   (see `runs/2026-08-16-1404-4h-shadow-nblind6-correlation.md`). The
   bundled CLI's `evolve` command hardcodes `n_blind=14`, so this needed a
   small standalone script calling `EvolutionRun.run()` directly — same
   scratch-isolation discipline as prior runs. 6 generations at `n_blind=6`
   took ~72 minutes total (~10-12 min/generation vs. 25-27 at the default),
   workable inside a 3-hourly slot if kicked off early. Result: a fourth
   independent x6-scaled-seed generation-1 promotion (fitness −4.231 → 0.839,
   holdout passed, real edge over benchmark), via `correlation_penalty`
   0.0→0.75 this time, then held through 5 more generations. Same
   catastrophic-seed → quick-fix → plateau shape as the three prior runs,
   each via a different unrelated gene — read this as one more draw from
   that distribution, not a convergent search, and see the note for why it
   does NOT reopen item 3 below (different value tried against a broken
   champion vs. a competent one). Next, still not attempted: a genuinely
   fresh unscaled-seed 4h search, or 10+ generations past the first plateau
   at the now-workable `n_blind=6` to see if a second plateau exists.

   **Resolved 2026-08-17 (3-hourly check): a second plateau exists.** (see
   `runs/2026-08-17-0510-4h-shadow-second-plateau.md`) A fresh x6-scaled-seed
   run, 10 generations at `n_blind=6` in one continuous script (~82 min
   wall time), found **two** promotions, not one. Generation 1: the usual
   quick fix (v1 −2.369 → v2 0.618, `correlation_penalty` 0.0→0.1 — a
   *different* magnitude than the 2026-08-16-1404 run's 0.75, both fixing
   different broken seeds on the first try, reinforcing that this gene isn't
   specially validated at either value against a catastrophic baseline).
   Then 7 generations of real stagnation (boldness climbing 0→7, 52
   candidates cumulatively tried, none clearing the bar). Generation 9: v2
   → **v3**, fitness 0.618 → 1.010, via a genuinely combined 5-gene patch
   (`consult_conservative.z_buy_below`/`min_trend`,
   `consult_moderate.min_trend`, `risk_judge.max_positions`/
   `cash_floor_pct`) — sealed holdout passed convincingly (challenger 0.008
   vs champion −2.242, excess return +35.3%, excess Sharpe +1.29,
   `beat_benchmark: true`). Generation 10 then held, and did so via the
   holdout gate specifically: the top fold-aggregate candidate (fitness
   1.364, would have cleared the multiple-testing margin) **failed the
   sealed holdout** (−0.021 vs champion 0.008 + margin) and was correctly
   rejected — a clean live example of the holdout gate overruling a
   fold-winning candidate. Answers the open question: yes, a second plateau
   is reachable past the first, it just takes patience (7 stagnant
   generations here) and the boldness mechanism's wider mutation batches.
   One data point, not a law — still open: whether a third plateau exists
   past generation 10, and whether a genuinely unscaled fresh seed shows the
   same shape.

   **Resolved 2026-08-17 (3-hourly check): the unscaled seed does NOT show
   the same shape** (see `runs/2026-08-17-0820-4h-shadow-unscaled-seed.md`).
   10 generations at `n_blind=6` from the seed genome with `bar_interval`
   flipped to `"4h"` but every period gene left at its 1d value (no x6
   scaling at all) — same isolation discipline as every prior 4h shadow run.
   Unlike every x6-scaled run (one quick fix in generation 1, straight to
   positive fitness 0.6-0.8+), the unscaled seed needed **three** separate
   generations to claw back from catastrophic (-4.515) to -0.445 (disable
   `consult_moderate` as an entry source entirely, then
   `correlation_penalty` 0.9, then halve chop-regime sizing), then held flat
   through 7 more generations (53 candidates tried, boldness to 6) — fold-
   aggregate fitness never went positive at all. Sharper anomaly worth
   following up: every accepted version's fold-aggregate fitness stayed
   negative (0/3 folds beat benchmark) while its sealed-holdout fitness was
   strongly positive and rising (0.815 -> 1.704 -> 2.486, all
   `beat_benchmark: true`) — the opposite of typical overfitting, and unlike
   any x6-scaled run, where fold and holdout fitness moved together. Most
   likely a regime mismatch between the newest 15% holdout slice and the
   older 85% search folds for this specific genome, not evidence of genuine
   generalization; not chased further this run. Answers the open question:
   manual pre-scaling before evolving isn't just a head start, it reaches a
   categorically different (positive-fitness, fewer-trades, fold/holdout-
   aligned) outcome than blind search alone gets to from the raw seed in a
   workable generation budget. Still open: whether more generations past 10
   let the unscaled seed's fold fitness eventually turn positive too.

   **Resolved 2026-08-19 (3-hourly check): checked whether a third plateau
   exists past generation 10 on a fresh x6-scaled-seed run — no fourth
   promotion surfaced, but the count of promotions before the wall (3, not
   2) didn't replicate either, and 9 stagnant generations is the deepest
   probe of this question yet.** (see "Current state" above and
   `runs/2026-08-19-2137-4h-shadow-third-plateau.md`) 15 generations at
   `n_blind=6`: three promotions all inside generations 1-6, then 9 straight
   stagnant generations (boldness to 8, 65 cumulative candidates) with
   nothing clearing the bar. Shape replicates the 2026-08-17-0510 run
   (quick fixes then a wall); exact promotion count and plateau generation
   don't. Still open whether a much longer run (30+ generations) ever breaks
   the wall — flagged as a judgment call given the ~6-7 min/generation cost
   and the falling marginal value of "still flat" as more generations are
   spent confirming it.

   **Resolved 2026-08-18 (3-hourly check): no, 16 generations still doesn't
   get there, and now there's a mechanism, not just a data point.** (see
   "Current state" above and
   `runs/2026-08-18-0232-4h-shadow-unscaled-seed-16gen.md`) From generation 8
   onward, dozens of candidates cleared the fold-aggregate acceptance bar
   with fitness well above champion v3's -0.241, and every one was rejected
   at the sealed holdout: v3's own holdout draw landed at a strong 1.079,
   and every challenger's holdout score is one noisy point estimate on the
   same short window (7 draws ranged -1.664 to +0.907) that almost never
   clears that bar. This reframes the open question: it isn't "does the
   unscaled seed need more generations," it's "a champion that draws a
   lucky holdout score becomes hard to unseat regardless of how many
   generations run after it" — a property of the fixed 85/15 holdout split
   plus per-candidate draw noise, not of this seed or bar size specifically.
   Not chased further this run (one lucky draw, not proof of a systemic
   problem) but worth checking whether the live 1d champion shows the same
   fold-vs-holdout gap the next time a promotion is evaluated.

   **Resolved 2026-08-18 (3-hourly check): didn't need to wait for a new
   promotion — the live 1d champion's own post-promotion search history,
   already recorded in `live_state.json`, shows the same pattern.** See
   "Current state" above and
   `runs/2026-08-18-0655-holdout-pressure-diagnostic.md`. New diagnostic
   `evotrader_bundle.py holdout-pressure` found 9/9 real post-promotion
   challengers against champion v3 that cleared the fold-aggregate gate
   still lost the sealed holdout, 6 of them by tying the champion's exact
   holdout score rather than losing outright. Confirms the 4h-shadow
   hypothesis with real 1d data, not a shadow-run anomaly. Next: run this
   after every future non-promoting `evolve` call, live or shadow.

   **Resolved 2026-08-17 (3-hourly check): the fold/holdout split anomaly
   chased down, and the answer is the opposite of the "easier holdout
   window" guess.** New read-only diagnostic `evotrader_bundle.py regime
   [--interval ...]` (same guarantees as `anatomy`/`consults`/`costs`) reports
   equal-weight buy-and-hold return/sharpe/maxDD per walk-forward fold and
   the sealed holdout, independent of any genome. Full numbers in
   `runs/2026-08-17-0956-regime-diagnostic-fold-holdout.md`. Headline: 1d and
   4h bars see essentially the *same* calendar regimes per window (same
   universe, same fraction-based split of the same history) — fold 2 is a
   +200%+ melt-up (sharpe ~1.7-1.8), the holdout is the worst window of the
   four by raw buy-and-hold terms (-36%, sharpe ~-1.2), not a lucky bull run.
   That rules out "the genome got lucky on an easy holdout" and points at the
   real mechanism instead: fitness is *relative* to buy-and-hold, and the
   08:20 run's unscaled-seed fixes were all risk-reducing (disabled
   `consult_moderate`, near-max `correlation_penalty`, halved chop sizing) —
   exactly the profile that structurally underperforms a +200% melt-up
   (dragging fold-aggregate fitness negative) and structurally outperforms a
   -36% crash (driving holdout fitness up), for the same underlying reason.
   Not evidence the policy generalises — raw fold-aggregate fitness never
   went positive, so it still lost to benchmark in 2 of 3 folds — but it
   replaces a vague "regime mismatch" guess with a mechanistic one. Flags a
   sharper open question for whoever next touches the fold scheme: is
   `FOLD_CONSISTENCY_WEIGHT`'s cross-fold variance penalty enough when one of
   three fixed folds is permanently a +200% outlier, or does that call for a
   rolling/regime-stratified fold scheme instead of the current fixed 85/15
   split? Not attempted this run — `regime` only characterised the existing
   windows, it doesn't propose a new fold scheme.

   **Resolved 2026-08-18 (3-hourly check): first quantified answer — the
   outlier's dominance is a fold-count artefact, but raising `N_FOLDS` alone
   isn't the fix.** New diagnostic `evotrader_bundle.py fold-scheme` (see
   "Current state" above and
   `runs/2026-08-18-0952-fold-scheme-sensitivity.md`) re-evaluates champion
   v3 at `n_folds` 3/5/8: fold 2's outlier gap over the other folds shrinks
   monotonically (+219.4% → +53.8% → +52.0%), but `aggregate_fitness`
   itself swings non-monotonically (-1.224 → +1.633 → -0.500) and at n=8 a
   fold came close to `run_backtest`'s hard 120-bar minimum and one fold
   failed a hard gate outright. Next: a regime-stratified/rolling scheme,
   not a higher fixed `N_FOLDS`, looks like the right direction — but that's
   a constitution change (checksummed, needs an `AMENDMENTS.md` row) and
   deserves its own design pass, plus checking the pattern on more than one
   champion/snapshot, before anything gets proposed.

   **Resolved 2026-08-18 (3-hourly check): checked against a second
   champion (v2), and it sharpens rather than confirms the finding above.**
   (see "Current state" above and
   `runs/2026-08-18-1256-fold-scheme-champion-replication.md`) New
   `fold-scheme --also-version N` reconstructs any past champion from
   `live_state.json`'s own lineage (verified bit-exact, tested) and runs
   the same sweep on it. The outlier gap matches v3's to the decimal at
   every fold count — but that's guaranteed by construction (it's a
   buy-and-hold-only number, genome-independent), not evidence of anything.
   `aggregate_fitness`, which *is* genome-dependent, does **not** show the
   same shape: v2 decreases monotonically with fold count where v3 swings.
   So the "aggregate_fitness swings non-monotonically" half of the finding
   above is v3-specific, not a general fold-scheme property. Still open:
   whether a third champion looks like v2's shape, v3's shape, or a third
   one; `--also-version N` makes that a one-line check next time a
   champion promotes.

   **Resolved 2026-08-18 (3-hourly check): checked the third champion (v1,
   the seed) and it reverses the read above.** (see "Current state" above
   and `runs/2026-08-18-1549-fold-scheme-third-champion.md`) v1 swings
   non-monotonically too (-2.577 → 0.244 → -0.938), the same shape as v3,
   not v2's monotonic decrease — so 2 of 3 known champions swing and only
   1 decreases monotonically. Non-monotonicity is not v3-specific; it looks
   like the more common shape on this fixed 3-fold split. `--also-version
   N` has now swept all three real champions this account has had (1, 2,
   3) — closed until a fourth champion is promoted. Any future
   regime-stratified/rolling fold-scheme redesign should treat
   non-monotonicity as a property worth designing around, not a
   champion-specific artefact.

3. **Cross-asset correlation awareness for the Risk Judge** — CLOSED 2026-08-20,
   see the last entry in this item's history below: the gene was measured
   exhaustively, found to be dead weight, and removed. Kept in full for the
   history (how the evidence was built matters for the next structural
   proposal), but there is nothing left to act on here. Infrastructure
   shipped 2026-08-15 after
   parametric search plateaued at fitness 0.889 for 13+ generations:
   `Briefing.rets_by_symbol` (Analyst computes per-symbol recent return series
   alongside existing features, default empty dict), plus two new `risk_judge`
   genes — `correlation_penalty` (default `0.0`, a proven no-op:
   `RiskJudge._correlation_scale()` short-circuits to `1.0` before touching any
   position or return data) and `correlation_lookback` (default `30` bars). When
   the penalty is above zero, a new buy's size is shrunk (or, at penalty `1.0`,
   fully vetoed) in proportion to its worst pairwise correlation against
   currently-held symbols. Verified backward-compatible both empirically
   (summary/tick byte-identical against the live v2 account) and by direct unit
   assertion on the default. Verified forward-active against real 4-year Binance
   data: with the penalty at 0.8, the same 27-symbol backtest showed fewer and
   less-correlated trades (1,401 vs 1,618), lower turnover (24.6 vs 39.0
   annualized), and a smaller drawdown (−28.1% vs −38.1%) than the default — a
   single full-period point estimate, **not** a promotion-grade result.
   **Search finally run 2026-08-16** (see
   `runs/2026-08-16-0059-shadow-evolve-vs-live-champion.md`): shadow `evolve 6`
   against a copy of the real live champion v2 (real data, real gates,
   real `researcher_memory`), never touching `live_state.json`. The
   `correlation_penalty=0.5` proposal actually topped the fold-aggregate
   ranking once (fitness 2.73, generation 3, ahead of the then-champion's
   2.461) but **failed the sealed holdout** (−0.48 vs champion's −0.25) and
   was correctly rejected. Answer to the open question: `0.5` doesn't
   generalize as tuned — not a promotion candidate. A different penalty
   value, or letting the Researcher search a range instead of one fixed
   proposal, hasn't been tried. Also not attempted: a fuller cross-universe
   factor-model version (the current one only compares a candidate against
   symbols already held, not the whole universe pairwise) — a bigger,
   separate structural step.

   **Range proposal shipped 2026-08-16** (see
   `runs/2026-08-16-0403-correlation-penalty-range-search.md`):
   `Researcher.structural()` now proposes `correlation_penalty` at `0.25`,
   `0.5` and `0.75` from cold instead of a single fixed `0.5`, so search
   picks the magnitude instead of a human guessing it. Verified mechanically
   (all three appear as distinct ranked candidates in a shadow `evolve`) but
   not yet resolved which value generalizes — the champion (v2, same
   cumulative researcher_memory, 224 candidates tried by the end of this run)
   held through 6 more shadow generations with no promotion at all this draw,
   correlation gene or otherwise, so none of the three even reached a
   sealed-holdout check. Needs more generations, or a run where the champion
   actually gets beaten first.

   **Grid was silently exhausted, then widened, 2026-08-16** (see
   `runs/2026-08-16-0716-correlation-penalty-exhausted-widened.md`): a
   10-generation shadow run against v2 produced **zero** `correlation_penalty`
   candidates — all three of `0.25`/`0.5`/`0.75` had already been tried and
   excluded against this exact champion version by the 04:03 run, and
   `Researcher.structural()`'s cold-start branch is deterministic + excluded
   by exact patch value, so it silently stops firing once every value in it
   has been tried once. This is invisible in the generation log (14 blind
   proposals/gen looks the same with or without structural proposals also
   firing) — check `researcher_memory.tested` directly, don't infer from
   generation counts. Widened the grid to `(0.1, 0.25, 0.5, 0.75, 0.9)`.
   Verified live: `correlation_penalty_0.1` scored fold-aggregate fitness
   **0.7021** (above champion's raw 0.682, still short of the ~252-candidate
   multiple-testing margin — correctly rejected) — the best any
   correlation_penalty value has scored yet, though one draw. `0.9` scored
   0.3174. Note this was drawn against **v2** (raw fitness 0.682) — the
   live champion is now v3 (fitness 1.389, see "Current state"), so the
   comparison point for any future correlation-penalty draw has moved and
   this specific number will not be directly comparable. Next: if
   `0.1`/`0.9` also get exhausted with no promotion against whichever
   champion is current, that's reasonably strong evidence this gene doesn't
   help at any single fixed value near the ones tried, and the honest move
   is either dropping this line or building the fuller cross-universe
   factor-model version (bigger, separate structural step, not attempted).

   **All five grid values now exhausted against three separate champions,
   2026-08-16** (see `runs/2026-08-16-1000-shadow-evolve-vs-v3-correlation-check.md`):
   a shadow `evolve 8` against a copy of the real live champion v3 found an
   unrelated blind-search promotion to shadow v4 at generation 2 (fitness
   1.389→1.761, sealed holdout passed, beat benchmark — not applied live,
   same scoping as every prior shadow run), then ran 6 more generations
   against that new v4 champion, during which all five widened-grid
   `correlation_penalty` values (`0.1`/`0.25`/`0.5`/`0.75`/`0.9`) fired as
   fresh structural proposals and every one lost outright (none in the
   top-4 of any generation). Combined with earlier runs against v2 and v3,
   every value in the grid has now lost against three independent
   champions. Recommend treating this as resolved-negative at these five
   magnitudes: either drop the single-fixed-value `correlation_penalty`
   line, or move straight to the cross-universe pairwise factor-model
   version if this is still worth pursuing structurally.

   **Resolved 2026-08-18 (3-hourly check): first evidence on the
   drop-vs-build decision, leaning toward drop.** (see "Current state"
   above and `runs/2026-08-18-2146-correlation-universe-diagnostic.md`) New
   `evotrader_bundle.py correlation-universe` measured the wider universe's
   pairwise correlation structure the held-vs-candidate mechanism never
   looks at. Result: correlation is high (+0.52 to +0.64) and broadly
   uniform across every fold and the sealed holdout, not clustered or
   crisis-spiking the way the factor-model case assumed — weak evidence the
   bigger structural build would find much the fixed-value grid's failure
   didn't already rule out. Not conclusive (raw universe correlation, not
   portfolio-realized correlation of what the champion actually holds
   together) — see "Current state" for the exact caveat and what a
   follow-up measurement would need to check before actually dropping the
   gene.

   **Resolved 2026-08-19 (3-hourly check): the portfolio-realized follow-up
   the run above flagged is done, and it strengthens rather than reverses
   the drop-vs-build lean.** (see "Current state" above and
   `runs/2026-08-19-0052-portfolio-realized-correlation.md`) New
   `correlation-universe --realized` measures correlation restricted to the
   symbols champion v3 actually held together (via new
   `loop.engine.holding_mask`, reconstructed from one real backtest's own
   trade records), directly comparable to the universe-wide table above.
   Result: held-only correlation is lower than universe-wide in all four
   windows (by 0.04 to 0.19), meaning the champion's own position selection
   already lands on a less-correlated subset than the universe average —
   there is no concentration problem visible for a correlation-aware sizing
   rule to have caught, on this champion's actual trading history. Two
   independent measurements (universe structure, portfolio-realized
   structure) now both favor drop over build. Not fully closed: this is
   still one champion's one set of entry/exit rules — see "Current state"
   for exactly what a next check would need (a differently-tuned genome, not
   another read of the same one) before treating this as settled enough to
   actually delete `correlation_penalty`/`correlation_lookback`/
   `_correlation_scale`.

   **Resolved 2026-08-19 (3-hourly check): checked against a genuinely
   different genome (v1, the seed), not just another read of v3.** (see
   "Current state" above and
   `runs/2026-08-19-0350-correlation-realized-second-genome.md`) New
   `correlation-universe --realized --also-version N` reuses
   `_reconstruct_champion_genome` (already verified for `fold-scheme
   --also-version`) to run the same held-set measurement against any past
   champion. v1's held-only correlation is lower than universe-wide in every
   window too, same shape as v3 despite 13+ generations of unrelated tuning
   between them. Three independent measurements (universe-wide, v3
   portfolio-realized, v1 portfolio-realized) now agree — this is the
   "different genome" check the prior run asked for. Still open: v2 as a
   third real data point (one line, `--also-version 2`, not run yet), and
   whether a genome deliberately designed to concentrate would show a
   different picture (an adversarial-style check, not attempted).

   **Resolved 2026-08-19 (3-hourly check): v2 checked too — all three real
   champions now agree, this data source is exhausted.** (see "Current
   state" above and
   `runs/2026-08-19-0648-correlation-realized-third-genome.md`) Same
   one-line `--also-version 2` re-run, no code change. v2's held-only
   correlation is lower than universe-wide in every window too. Four
   independent measurements (universe-wide, v3/v1/v2 portfolio-realized) all
   lean the same way; there is no fourth real champion to check until a new
   promotion happens. Still open: the adversarial-genome check (deliberately
   built/mutated to concentrate exposure) is the only remaining way to add a
   genuinely new data point to this question.

   **Resolved 2026-08-19 (3-hourly check): the adversarial-genome check is
   done, and it's the first result that doesn't just re-confirm "no
   concentration."** (see "Current state" above and
   `runs/2026-08-19-0951-correlation-adversarial-genome.md`) New
   `_adversarial_concentration_genome(base)` + `correlation-universe
   --realized --adversarial` builds a genome from v3 with every consult's
   selectivity gate loosened to near pass-through and every position
   limit raised, `correlation_penalty` left at its inert default `0.0`.
   In fold 3/holdout its held-set correlation gap below universe-wide
   shrinks 6-9x versus v3's own gap in those windows; fold 1/2 barely move.
   This closes the "genuinely different genome" question for item 3 — the
   remaining open questions are narrower (a sector-targeted adversarial
   genome instead of blanket-loosened selectivity, and whether this
   genome's concentration actually costs it fitness) rather than "has an
   adversarial genome been tried at all."

   **Resolved 2026-08-19 (3-hourly check): yes, the concentration costs
   fitness — a lot.** (see "Current state" above and
   `runs/2026-08-19-1258-correlation-adversarial-fitness-cost.md`) The
   adversarial genome's full-history maxDD is -52.6% (v3: -34.1%), crossing
   `MAX_DD_HARD_FAIL` and giving it `fitness = -inf` — it would never clear
   a real search's acceptance gate. Sharpens "drop the line" from "no real
   champion needed it" to "the drawdown/fitness gates already in place would
   catch this kind of concentration on their own." Still open: whether a
   genome can concentrate *without* failing those other gates (tight
   per-symbol selectivity, no diversification requirement) — not tried, and
   would be the first case for keeping `correlation_penalty` rather than
   dropping it.

   **Resolved 2026-08-19 (3-hourly check): tried the narrower construction,
   and it fails the same gate anyway, more severely.** (see "Current state"
   above and
   `runs/2026-08-19-1552-correlation-adversarial-tight-concentration.md`) New
   `_adversarial_concentration_genome_tight` leaves every consult entry gate
   untouched and forces concentration purely through
   `risk_judge.max_positions`/`max_position_pct`/`cash_floor_pct` (6 slots
   → 3, larger each). Result: held-set correlation is the highest measured
   yet — fold 2 (+0.561) is the first window where held-only correlation has
   ever exceeded universe-wide (+0.509) — but full-history maxDD is -57.5%,
   worse than the loosened-gates genome's -52.6%, still hard-fails, fitness
   -inf. Both known routes to concentration (lose selectivity, or keep it
   and force fewer/larger positions) blow the drawdown gate. Item 3's
   evidence base is now 4 real champions + 2 independent adversarial
   constructions, all pointing the same way — if this item is ever revisited
   to actually act, this is enough to decide on, not another read. The one
   remaining gap: a concentration-forcing genome has never been run through
   real `evolve` search, only hand-built.

   **Resolved 2026-08-19 (3-hourly check): closed that one remaining gap —
   ran real unconstrained blind search against the real champion, and it
   never wanders into the concentration region either.** (see "Current
   state" above and
   `runs/2026-08-19-2218-correlation-real-search-concentration.md`) 10
   generations of the real `EvolutionRun` search (same code path a live
   `evolve` call takes) against v3, in an isolated scratch copy: 128 fresh
   proposals, no promotion, and every one of the ~30 candidates that touched
   `max_positions`/`max_position_pct`/`cash_floor_pct` scored well below
   champion — the best concentration-touching candidate anywhere in the run
   was actually the de-concentrating direction (`max_positions: 10`). Item
   3's evidence base is now complete on all three axes: real champions (4),
   hand-built adversarial constructions (2), and real unconstrained search
   (this run). Not attempted this run, and flagged as its own future task:
   the removal itself (genome defaults, mutation gene ranges, the
   Researcher's structural proposal grid, `RiskJudge._correlation_scale`,
   `Briefing.rets_by_symbol`, several tests, and the diagnostic CLI code
   built to measure this question) is a multi-file surgery that deserves a
   dedicated session, not a tail-end addition to a diagnostic one.

   **Done 2026-08-20 (3-hourly check): the removal itself.** (see "Current
   state" above and `runs/2026-08-20-0055-correlation-penalty-removal.md`)
   `correlation_penalty`, `correlation_lookback`, `RiskJudge._correlation_scale`,
   its `_pairwise_corr` helper, the structural proposal grid, both
   `GENE_SPACE` mutation entries, and `Briefing.rets_by_symbol` (plus the
   Analyst computation feeding it) are all gone. The `correlation-universe`
   diagnostic (`loop.engine.pairwise_correlation_stats`/`holding_mask`)
   stays — it never depended on the removed plumbing, computes correlation
   directly from raw closes, and is still useful for future
   concentration/diversification questions. Verified a true no-op: full
   suite 104 passed, constitution checksum unchanged (nothing removed was
   checksummed), `live_state.json` byte-identical, and a fresh full-history
   backtest of live champion v3 reproduces its previously-recorded -34.1%
   maxDD to 5 significant figures. **Item 3 is now closed** — nothing left
   to measure or remove on this question unless a future structural
   cross-universe factor-model version is proposed from scratch, which
   would be new work, not a continuation of this one.

3a. **Resolved 2026-08-16 (weekend all-hands): the live champion caught up
   on its own.** This item used to flag that v2 was measurably behind a
   shadow-found improvement (v4, fitness 2.461) that was deliberately never
   applied live. The weekend all-hands ran real `evolve` against the actual
   account instead of importing that shadow result — `evolve 8` found
   nothing, `evolve 15` continuing from there found a real promotion to
   **v3** (fitness 0.682 → 1.389, sealed holdout passed, beat buy-and-hold
   in that window) at generation 6. Different specific gene combination than
   any shadow run found, same overall story. Full numbers in "Current
   state" above and `runs/2026-08-16-0600-weekend-all-hands.md`. The shadow
   v4 candidates (from this run and an earlier one) were deliberately still
   not hand-applied — using them would mean merging a holdout-draw count
   from an isolated copy into the live account's `researcher_memory`,
   which is more surgery than was justified once honest search found its
   own promotion anyway. v3 is not confirmed to be at the same fitness
   level as any shadow v4 — more generations against v3 may find further
   improvement, unprompted, the normal way.

4. **LLM-backed consults.** Plan changed 2026-08-15: no longer waiting on an
   Anthropic API key. Since every trading/evolution cycle already runs inside a
   live scheduled Claude session, that session itself serves as the LLM
   consultant — read a flagged hard-call case, reason about it inline, write the
   verdict back into state — instead of the executed code making its own separate
   API call.

   **"Flag hard calls" half shipped 2026-08-17** (see "Current state" above
   and `runs/2026-08-17-*-hard-call-flagging.md`): `agents.judges.flag_hard_call`
   + wiring in `loop.engine.Council.tick`, additive-only, tested. What's left is
   the harder half — "apply consult verdict & execute". That still needs a
   real design, not just code: a scheduled tick runs unattended and can't
   pause mid-function waiting on a human/LLM turn, so "consult inline" likely
   means either (a) `tick` stops *before* execution when it sees a hard call,
   writes the flagged case to state, and a second scheduled step later reads
   it, reasons, and calls a resume-and-execute path — or (b) hard calls get
   downgraded automatically (e.g. sized down or skipped) and a session
   reviews the log after the fact rather than gating execution in real time.
   (a) is truer to the original plan but reintroduces the fills-happen-later
   problem the codebase deliberately avoided elsewhere (see `core.live`'s
   "fill at the live price at the moment of execution" convention); (b) is
   weaker but fits the existing single-pass `tick`. Worth a decision before
   more code goes into this, not just more architecture.

   **Frequency measured 2026-08-17** (see "Current state" above and
   `evotrader_bundle.py hard-calls`): as shipped, 38.6% of logged bars flag
   as hard calls on the full-history replay, almost entirely driven by the
   low-agreement-buy trigger, which is mechanically just "exactly one
   consult proposed this buy" (discretized 3-consult agreement) rather than
   a genuinely unusual disagreement — a pattern the system already prices
   in via `lone_voice_scale`, not a rare event worth escalating. That rate
   is too high for either design in (a)/(b) above to be practical — a
   review-after-the-fact session in (b) can't meaningfully look at over a
   third of all trading bars, and (a) pausing mid-tick that often would
   turn "occasional slow path" into "the normal path." **Sharper next step
   before picking (a) vs (b): narrow the trigger set first** (drop
   low-agreement-buy entirely, or replace it with something that isn't a
   simple share-of-3 threshold — e.g. only fire when a lone-voice buy is
   *also* the highest-conviction/largest order that bar) and re-run
   `hard-calls` to see what rate that leaves; the (a)-vs-(b) architecture
   choice is much easier to reason about once the flagged set is actually
   small.

   **Tried 2026-08-17 (3-hourly check): the highest-conviction narrowing,
   and it backfired** (see "Current state" above and
   `runs/2026-08-17-1553-hard-call-trigger-narrowing.md`) — rate rose
   38.6% → 52.0%, because lone-voice and highest-conviction-that-bar turn
   out to be strongly correlated in this system, not independent. Ruled out:
   "which order is the biggest bet" as a discriminating axis by itself.

   **Tried 2026-08-17 (3-hourly check): candidate (ii), "solo bar" —
   requiring zero corroborating signal anywhere that bar — and it worked**
   (see "Current state" above and
   `runs/2026-08-17-1850-hard-call-solo-bar-narrowing.md`): rate fell
   38.6% → **24.4%**, the first narrowing attempt to actually reduce it.

   **Tried 2026-08-17 (3-hourly check): candidate (i), size relative to
   portfolio equity, composed on top of the solo-bar requirement — and it
   also worked** (see "Current state" above and
   `runs/2026-08-17-2146-hard-call-size-gate.md`): rate fell further,
   24.4% → **9.6%** (133/1386 bars: 4 circuit_breaker + 85
   superior_override + 48 low_agreement_buy, `min_size_pct=0.10`). This is
   close enough to the ≈6.1% circuit_breaker+superior_override-only floor
   that the remaining gap is small — **the (a)-vs-(b) architecture decision
   from the top of this item is now the actual next step**, not further
   narrowing. (iii) dropping `low_agreement_buy` outright remains available
   as a fallback if 9.6% still proves too high once (a)/(b) is designed in
   more detail, but hasn't been needed yet.

   **(a)-vs-(b) decided and (b)'s first piece shipped 2026-08-18 (3-hourly
   check)** (see "Current state" above): design (b), review-after-the-fact,
   chosen over (a)'s stop-before-execution split — the 9.6% flag rate is low
   enough (at most one candidate a day off the live daily tick) that a
   scheduled session can plausibly look at every one. `LiveAccount` now has
   a durable `hard_call_reviews` field and `add_hard_call_review(...)`; new
   CLI `review-hard-calls` lists what's pending and records a verdict with
   `--tick`/`--verdict`/`--notes`. No live bar has ever actually flagged
   yet, so this is infrastructure ahead of its first real case. **Next: the
   first time a real live tick flags `is_hard_call: true`, a scheduled
   session should actually use it** — read the flagged case from
   `review-hard-calls`, reason about it inline (this is the "session serves
   as the LLM consultant" idea from the top of this item, now with somewhere
   concrete to write the verdict), and record the verdict. That first real
   review is the point of this infrastructure, not more code around it.

5. **Short selling** with modelled borrow cost — currently long-only, which is why
   a bear market can only be survived, not traded.

6. **Equities/FX** behind the same `MarketData` interface.

7. **Unflatten `evotrader_bundle.py` into real files.** The `_SRC` dict keys map
   directly onto a normal multi-file layout (`_SRC['core.types']` →
   `core/types.py`, etc.). This is the real fix for the transcription-risk
   pattern that caused problems during the 2026-08-15 migration (nbsp characters
   silently corrupting whitespace when the bundle was extracted from a rendered
   view — caught by the constitution checksum and `py_compile`, not by luck).
   Do it as its own isolated commit, keep the bundle working as a fallback until
   the unflattened version is proven equivalent (same checksum, same
   tick/summary output against the same `live_state.json`), and don't switch the
   live trading path until confident. Explicitly optional and explicitly last.

   **Tool shipped 2026-08-20 (3-hourly check), not the unflatten itself:**
   `tools/edit_bundle_module.py` extracts any one `_SRC` module to a real
   `.py` file and reinserts it, with a `verify` round-trip check — see
   "Current state" above and `runs/2026-08-20-0348-bundle-edit-tool.md`. This
   doesn't do the unflatten (still a bigger, separate, isolated-commit task
   as described above), but it's the safer way to touch bundle internals for
   any smaller edit in the meantime, including a future attempt at this item.

---

## Measured 2026-08-16 — read before proposing more genes

An outside review argued the project risks proving "the search can find
something that scores well" rather than "the policy generalises". Three things
were then measured rather than assumed. They are evidence, not opinion, and
they should steer what gets built next.

**1. The system underperforms doing nothing.** Over the full 4-year replay the
champion returns **+34.5% against buy-and-hold's +63.0% — an excess of −28.4%**.
It makes money and still loses to a lazy basket of the same coins. Fitness is
Sortino-shaped and never saw this, which is why `edge_vs_benchmark()` now
reports excess return, excess Sharpe and drawdown delta on every fold, every
holdout check and every generation record. Reported, deliberately not optimised
— folding it into fitness just moves the overfitting target.

**2. Two of the three consults are substantially one opinion.** Measured
signal correlation: conservative/moderate **+0.03**, conservative/risky
**−0.13**, moderate/risky **+0.39** — with 28.6% proposal overlap and **93.2%
same-side agreement when both act**. Worse, moderate/risky correlation *rises*
in exactly the regimes where diversification is supposed to pay: **+0.51 in
bear, +0.58 in crisis**. The conservative consult is a genuinely independent
theory; the other two are close to one theory at two speeds, so the Risk
Judge's "agreement" signal is partly reading its own echo. Run
`evotrader_bundle.py consults` after any roster change.

**3. The damage is broad, not tail-shaped.** The top 5 losses are only **11% of
gross loss**, so this is not a fat-tail problem — expectancy is just thin
($3/trade over 1,619 trades, profit factor 1.13). The sharper finding from
`anatomy` is role asymmetry: `consult_conservative` is **−$8,159 as an entry
signal (38% win)** but **+$25,706 as an exit signal (89% win)**. It is a bad
buyer and an excellent seller. The circuit breaker is −$1,820 over 14 trades at
a 7% win rate. Any future proposal should be argued against these numbers.

**What this means for priorities.** Adding agents, genes or search
sophistication is not the bottleneck — the bottleneck is that nothing yet shows
the policy beating a benchmark out of sample. Prefer work that produces
evidence (perturbation tests on fees/slippage/universe/start-date, convergence
across independent seeds, genuinely untouched forward periods) over work that
adds capability.

## Rules that must not be quietly dropped

- The `constitution/` package is checksummed at every startup. If a run reports
  **CONSTITUTION MODIFIED**, stop and investigate — do not re-seal it.
- Every constitution amendment gets a row in `AMENDMENTS.md`. Five so far, all
  argued in writing.
- Every genome promotion updates `README.md`'s `## Status` section in the same
  commit. It is hand-written and renders on the GitHub repo page — it does not
  update itself, and a stale version number there was already caught once
  (2026-08-16, fixed manually after the v2→v3 promotion).
- Buy-and-hold is reported next to every result, permanently.
- Never commit a personal email address, in metadata or in file contents.
- The system **cannot promote itself to real money.** That is the owner's
  decision, on evidence, and the gate is: 6 months of positive walk-forward, a
  live paper run that matches its own backtest within tolerance, and explicit
  sign-off.
