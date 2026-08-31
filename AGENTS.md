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
python3 evotrader_bundle.py fold-date-sensitivity  # does the real evolve() fold-aggregate fitness depend on which day it's run?
python3 evotrader_bundle.py rolling-folds     # overlapping fixed-width windows vs the disjoint fold split
python3 evotrader_bundle.py fitness-decomp    # split aggregate_fitness into its mean term vs consistency-penalty term across fold schemes
python3 evotrader_bundle.py drawdown          # which date range actually drives maxDD, ranked by depth
python3 evotrader_bundle.py correlation-universe  # full-universe pairwise return correlation by fold/holdout
python3 evotrader_bundle.py holdout-noise         # block-bootstrap sigma of a sealed-holdout fitness score
python3 evotrader_bundle.py fold-dd-blindspot     # does the fold-merged maxDD gate see drawdowns spanning a fold boundary?
python3 evotrader_bundle.py succession-audit      # would each past real champion pass today's dd-corrected drawdown gate if reinstated?
python3 evotrader_bundle.py promotion-excess-check  # did either real promotion depend on raw fitness vs. excess-return disagreeing?
python3 evotrader_bundle.py live-benchmark        # the live account's own real return vs. equal-weight buy-and-hold, same real window
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

`fold-date-sensitivity` re-evaluates the live champion under the exact same
`loop.evolve.Evaluator(data, n_folds=N_FOLDS).evaluate(genome)` call `evolve`
makes internally, at `--shift N` (default 7) different "as-of" dates walking
back from today, each with its own trailing-4y-ending-"as-of" window built
the same way `market.load_universe(..., 4.0)` builds it live. Answers
whether the `history-perturb --boundary-shift` day-1-allocation artifact has
any bearing on real promotion decisions (it does — see "Current state").
Read-only, full replay per shift (same cost class as `fold-scheme`).
`--also-version N` works the same as every other diagnostic here.

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
Convergence checked 2026-08-20 at `--n-boot` up to 50000: stable by ~5000
draws at refined per-champion estimates v3 ≈25.5x / v1 ≈18.5x / v2 ≈15.1x —
see "Current state".

`history-perturb` sweeps start-date sensitivity: `--years Y1,Y2,...` (default
2/3/4/5/6) runs nested scenarios all ending "now"; `--independent
[--window-years Y]` (default 2.0) instead tiles fixed-width, non-overlapping
windows walking backward from "now" over the full available history per
symbol, so each window is a genuinely independent draw rather than sharing
the same recent stretch. Both modes take `--also-version N`. Read-only, same
cost class as `costs`/`universe-perturb` (one real backtest per scenario/
window). First `--independent` result (2026-08-25): champion v3 beats
benchmark in 4 of 5 independent windows spanning 2017-2024, but hard-fails
in the most recent one (2024-2026) — see "Current state". `--independent
--sub-slice N [--sub-slice-window I]` splits window `I` (default: the most
recent) into `N` equal contiguous sub-windows and backtests each separately
(reuses the already-loaded history, no new data loading). `--independent
--drawdown [--sub-slice-window I]` instead runs one continuous backtest over
window `I` and reports `loop.engine.drawdown_episodes` (peak/trough
date, depth, recovery) for it, so a maxDD that a sub-slice view spreads
across several locally-shallow pieces can still be pinned to its real,
possibly cross-boundary, peak-to-trough span. Both flags require
`--independent`. See "Current state" for the first `--sub-slice` and
`--drawdown` results on window 5. `--independent --anatomy
[--sub-slice-window I]` (added 2026-08-27) runs the same already-tested
`loop.engine.trade_anatomy` the plain `anatomy` command uses, scoped to
window `I` instead of the full `[0,1]` history — the per-trade breakdown
(entry agent, exit mechanism, regime, holding period, worst/best trades)
none of the other window-5 flags provide. Also requires `--independent`.
See "Current state" for the first result.

`fold-dd-blindspot` explains the "-34.1% vs -46.5% maxDD" reproducibility question
`universe-perturb` and `drawdown` kept raising: `loop.evolve.Evaluator._merge`
computes the merged max_dd the acceptance gates check as the worst of the 3
folds' own independently-backtested local peak-to-troughs, never one continuous
replay across a fold boundary — so a drawdown that straddles two folds is
structurally invisible to `accepts()`/`fitness()` no matter how real it is.
Prints each fold's own local max_dd, the gate-visible merged number, and one
unbroken `run_backtest` over the identical search span next to each other so
the gap is visible directly, plus the same comparison over the full [0,1]
history (what `universe-perturb`/`drawdown`/`anatomy` report). Read-only, same
cost class as `fold-scheme` (one backtest per fold plus two continuous
replays). `--also-version N` same convention as the other diagnostics. First
result (2026-08-22): v3's gate sees -34.1%, one continuous replay of the exact
same span sees -46.5% — the entire discrepancy the previous two sessions spent
investigating as a possible data bug. See "Current state".

`succession-audit` extends `fold-dd-blindspot`'s per-champion comparison to
every real champion this account has had at once, discovered from
`acct.lineage` (no `--also-version` flag needed), and adds the
`dd_corrected_stats()`/`fitness()` numbers a real promotion decision would
actually gate on, not just the raw maxDD figures. Same cost class as
`fold-dd-blindspot` times the number of known champions (3 as of 2026-08-22:
~2 minutes). Answers the "what would replace a demoted champion" half of the
still-open demotion/rollback question with facts, not a decision — see
"Current state" for the first result (no real champion currently clears the
gate, v2 for a different reason than v1/v3).

`rolling-folds` is the untried alternative `fold-scheme`'s own notes have
flagged since 2026-08-18: instead of raising `Evaluator`'s `n_folds` (which
shrinks every window as count rises), `loop.evolve.rolling_folds(search_end,
base_n_folds, overlap)` keeps window width fixed at whatever
`Evaluator.folds()` uses for `base_n_folds` and slides that fixed-size window
across the searchable region by `(1 - overlap) * width` per step, feeding the
result into `Evaluator.evaluate(g, folds=...)` (already accepted a custom
fold list, no `Evaluator`/constitution change needed). `--overlap` (default
`0.5`), `--base-n-folds` (default `N_FOLDS`) and `--also-version N` (same
convention as `fold-scheme`/`correlation-universe`) control it. Read-only,
same cost class as `fold-scheme`. First result (2026-08-20): shrinks the raw
outlier gap but does **not** stabilize `aggregate_fitness` — see "Current
state" for why this is real negative evidence, not a null result.

`fitness-decomp` follows `rolling-folds` directly: it splits
`aggregate_fitness` into the two terms `Evaluator.evaluate` builds it from —
`mean(fold_fits)` and the `FOLD_CONSISTENCY_WEIGHT * std(fold_fits)`
consistency penalty (`loop.evolve.fitness_decomposition`, a pure identity:
`mean_term - penalty_term` reconstructs `aggregate_fitness` exactly, tested).
`rolling-folds` could only see the aggregate swing, not *which term* drove it;
this evaluates the live champion (and `--also-version N`) under five schemes
(disjoint `n_folds` 3/5, rolling overlap 0.5/0.7/0.85) and prints the
mean/penalty split plus each term's across-scheme range. Read-only, same cost
class as `fold-scheme`/`rolling-folds` (one backtest per window per scheme).
First result (2026-08-20): the **mean term** varies more than the penalty term
across schemes, for both v3 and v1 — see "Current state".

If a run reports **CONSTITUTION MODIFIED**, stop. Do not re-seal it. Investigate
and check `AMENDMENTS.md` first.

---

## Where things live

| path | what it is |
|---|---|
| `evotrader_bundle.py` | **the live path** — the entire runtime flattened into one file (agents, judges, broker, evolution loop). Every scheduled run executes this, not the real files below. |
| `core/`, `agents/`, `loop/`, `constitution/` | real, normally-importable copies of every module `evotrader_bundle.py` embeds in `_SRC`, added 2026-08-23 (weekend all-hands) as item 7's unflatten — see "Current state" and `runs/2026-08-23-0600-weekend-all-hands.md`. **Not the live path**: only the equivalence test and `run_from_files.py` import these; `evotrader_bundle.py` is untouched and still what every scheduled command actually runs. Kept byte-identical to the bundle's `_SRC` entries by `tests/test_unflattened_files_match_bundle.py` — edit a module with `tools/edit_bundle_module.py`, then hand-sync (or re-extract) the real file, or the test fails. |
| `run_from_files.py` | read-only CLI entrypoint (`summary`/`signals`/`holdout-pressure`/`regime`) that runs against the real files above instead of the bundle, added 2026-08-23 (3-hourly check) as a safe first step of item 7's cutover, extended the same day with two more read-only diagnostics — see "Current state" and `runs/2026-08-23-0946-run-from-files-entrypoint.md` / `runs/2026-08-23-1254-run-from-files-diagnostics.md`. **Not wired into any scheduled run** — `evotrader_bundle.py` is still what every scheduled command executes. |
| `evotrader_dashboard.py` | dashboard builder (zero external deps, hand-rolled SVG) |
| `evotrader.manifest` | constitution checksum (`8b74865634b1db07` as of 2026-08-21's `HOLDOUT_SIGMA` amendment — rotates on every constitution change, don't hardcode-trust this table over the file itself) — the anti-tampering seal |
| `live_state.json` | **the account**: cash, positions, trade ledger, NAV history, current genome, evolution lineage, researcher memory |
| `AMENDMENTS.md` | the constitution amendment log — every gate change, argued in writing |
| `runs/` | one dated note per scheduled run |
| `tools/edit_bundle_module.py` | extract/reinsert a module's source from `evotrader_bundle.py`'s embedded `_SRC` dict for editing without hand-touching its giant single-line strings — see item 7 and `runs/2026-08-20-0348-bundle-edit-tool.md`. Also now the intended way to keep `core/`/`agents/`/`loop/`/`constitution/` in sync after a bundle edit. |
| `index.html` | generated public dashboard, served by GitHub Pages — rebuilt each run, never hand-edited |
| `README.md` | hand-written, renders on the GitHub repo page — its `## Status` section names the current genome version and must be updated on every promotion (see Run protocol step 7) |

`live_state.json` is the irreplaceable one. Everything else can be rebuilt.

## No credentials, anywhere

Prices come from Binance's public market-data endpoint: no API key, no signup, no
KYC. The portfolio is tracked in `live_state.json`, which *is* the ledger. There
is no brokerage account in this design and there does not need to be one.

---

## Current state

- **Shipped 2026-08-31 (3-hourly check, ~12:47 UTC): the reusable 4h-shadow x6-scaled-seed
  harness the 10:02 UTC session recommended now exists and is committed —
  `tools/shadow_4h_x6_seed.py`, tested (`tests/test_shadow_4h_x6_seed.py`, 9 new tests,
  full suite 252/252), no code path change, nothing live touched.** See "Next steps"
  item 2 and `runs/2026-08-31-1247-shadow-4h-harness.md`. `build_x6_scaled_seed()`
  builds the exact recipe every prior 4h-shadow session hand-rolled from scratch
  (bar_interval="4h" + trend_fast/slow, rsi_len, vol_short/long, breakout_len, z_len,
  regime_ma, volume_len, max_bars_held, min_bars_held all x6) via `Genome.child()`
  instead of ad hoc dict mutation, so it's provenance-tracked like any real evolution
  step. Ran it live (warm cache, 27-symbol 4h universe, 4y): trades/yr 392.7, avg days
  held 15.54, win rate 49.4%, halts 6, max_dd -44.3%, sortino 0.94, sharpe 0.77 —
  **exactly reproduces the 10:02 UTC session's own baseline**, byte-for-byte on every
  reported metric. That's the strongest evidence yet that the 07:05-vs-10:02 UTC
  baseline discrepancy (1278 vs. 392.7 trades/yr for the "same" recipe) was a real
  construction difference in the 07:05 session's uncommitted script, not environment
  noise or non-determinism — but since that script was never committed, the exact
  divergence still can't be pinned down after the fact. `fitness` reports `-inf`
  (`max_dd` -44.3% exceeds `constitution.MAX_DD_HARD_FAIL` = 40%) — expected given
  every prior session's numbers for this exact seed, not a harness bug. Next: use
  this harness as the fixed baseline for any future consult-threshold or
  correlation-penalty variant test on the x6-scaled seed (07:05 UTC's still-open
  suggestion), so results are diffable against this run instead of re-described in
  prose.

- **Tested 2026-08-31 (3-hourly check, ~10:02 UTC): tightening nine consult threshold
  genes on the x6-scaled 4h seed cuts trade frequency as predicted, but does not fix
  drawdown — a genuine negative result — and this session's own baseline didn't
  reproduce the 07:05 UTC session's baseline numbers, an unresolved discrepancy now
  flagged rather than papered over.** See "Next steps" item 2 and
  `runs/2026-08-31-1002-4h-shadow-threshold-tighten.md`. Tightened `min_rank_mom`/
  `rsi_max`/`min_breakout` (consult_risky), `min_trend`/`rsi_lo`/`rsi_hi`/`min_rank_mom`
  (consult_moderate), `rsi_buy_below`/`z_buy_below` (consult_conservative) — the
  threshold genes the 07:05 UTC session flagged as never touched by any x6-scaling
  recipe. Trades/yr dropped 392.7 → 327.8 (-16.5%) as the noise hypothesis predicted,
  but max_dd got *worse* (-44.3% → -48.0%), halts rose (6 → 8), sortino/sharpe both
  fell — fewer entries didn't translate into a shallower drawdown here. Ruled out
  "just tighten the consult thresholds" as a free-lunch fix, though only one specific
  combination and direction was tried. Separately: this session's baseline (392.7
  trades/yr, -44.3% max_dd, sortino +0.94) doesn't match the 07:05 UTC session's
  reported baseline (1278 trades/yr, -66.1% max_dd, sortino -0.29) for what should be
  the identical x6-scaled seed — checked and ruled out gene-construction mismatch
  (full genome dump verified gene-by-gene against the documented recipe), data
  gaps (none, clean 8766-bar/symbol fetch), and the `run_backtest` `warmup` default
  (60 vs. 360 moves the baseline by noise only). No RNG is reachable from a plain
  `run_backtest()` call, so it isn't seed non-determinism either. Neither session's
  scratch script was committed, so a line-by-line diff isn't possible after the fact.
  **Recommend a future session either commit a small reusable (never-scheduled)
  scratch harness for this recipe so runs are diffable, or re-run the same recipe
  twice in one session to confirm stability, before trusting any single 4h-shadow
  baseline number in isolation again.** `git status` clean, `live_state.json` md5
  unchanged (`37a1b00bee3f7cb1ad2f4adde0ab9ed0`), `python3 -m pytest -q` 243/243
  confirmed at session start, no code changed (three standalone scratch scripts, not
  committed), genome still v3 (1d).

- **Found 2026-08-31 (3-hourly check, ~07:05 UTC): the x6-scaled 4h seed's trade-count
  inflation comes from entry frequency, not faster round-trips, and a new candidate
  confound (`max_new_positions_per_bar`) is tested and ruled out.** See "Next steps"
  item 2 and `runs/2026-08-31-0705-4h-shadow-entry-frequency-diagnostic.md`. Instead
  of testing more harness constants, characterized *how* the seed overtrades via three
  single-shot `run_backtest()` calls (v3 at 1d, x6-scaled seed at 4h, raw-unscaled seed
  at 4h — no evolution needed): the x6-scaled seed trades 4.6x more often per year than
  v3 (1278 vs 277 trades/yr) but holds each position for a *similar or slightly longer*
  time (10.71 vs 9.09 days) — ruling out "positions flip faster" as the mechanism; it's
  many more distinct new entries, not quicker exits. Also notable: the scaled seed's
  win rate (67.7%) is higher than v3's own (35.7%) despite negative Sortino and much
  worse drawdown (-66.1% vs -46.5%) — small wins offset by large, poorly-controlled
  losses, not a signal-quality problem. Then tested one previously-unexamined un-scaled
  genome gene, `superior_judge.max_new_positions_per_bar` (seed value 3, a per-*bar*
  cap — at 4h that's up to 18 new positions/day vs the 1d-intended 3/day, and no prior
  x6-scaling recipe ever touched it): tightening it to 1 moved trades/max_dd/sortino by
  noise-scale amounts only (1278→1306 trades/yr, -66.1%→-65.7% max_dd) — **ruled out**,
  same conclusion shape as the 04:07 UTC session's warmup/cooldown check. Sharpens the
  open question to something new and concretely scoped: the *threshold* genes that gate
  individual entries/exits (RSI bands, z-score bands, `min_trend`/`min_breakout`/
  `min_rank_mom` minimums across all three consults) were never touched by any x6-
  scaling recipe or any prior hand-tuning attempt — only period-length and bars-held
  genes were ever scaled. If 4h bars are simply noisier per-bar than daily closes, the
  same thresholds tuned against 1d noise firing far more often against 4h noise would
  produce exactly the entry-frequency-not-hold-time shape measured here. **Recommend
  this — widening/tightening the consult threshold genes independent of period scaling,
  re-measured the same way — as the next concrete step toward "genuinely hand-retuned,
  not just scaled,"** sharper than the prior framing's bare "hand-retune it somehow."
  Read-only throughout: imported `core.genome`/`core.market`/`loop.engine` directly
  (same pattern `run_from_files.py` already uses), never opened the real
  `live_state.json` (v3's genome was exported once to a standalone JSON file), fresh
  `state/cache/` entries only (gitignored, not `live_state.json`). `git status` clean,
  `live_state.json` md5 unchanged, `python3 -m pytest -q` 243/243 confirmed at session
  start, no code changed (two standalone scratch scripts, not committed), genome still
  v3 (1d).

- **Ruled out 2026-08-31 (3-hourly check, ~04:07 UTC): two un-scaled bar-count
  harness constants (`run_backtest`'s `warmup` default, `constitution.
  CIRCUIT_BREAKER_COOLDOWN`) are NOT why the x6-scaled 4h seed hard-fails the
  dd-corrected gate — the seed is genuinely this aggressive on its own terms.**
  See "Next steps" item 2 and
  `runs/2026-08-31-0407-4h-shadow-warmup-cooldown-ruled-out.md`. Before
  spending a bigger session on a genuinely hand-retuned 4h starting point (the
  02:43 UTC note's open question), checked a cheaper alternative first: every
  4h-shadow run since 2026-08-16 hand-scaled the seed's *period genes* by x6
  but never touched `run_backtest`'s `warmup=60` default (several x6-scaled
  genes, e.g. `trend_slow`/`regime_ma`=300, exceed it, so early fold bars could
  run on incompletely-primed indicators) or `CIRCUIT_BREAKER_COOLDOWN=20`
  (a 20-day freeze at 1d, only ~3.3 days at 4h). Tested both in isolation
  (warmup 60 vs. 360=60x6; cooldown 20 vs. 120=20x6) via direct
  `run_backtest`/`Evaluator` calls, no evolution needed. Neither moved any
  metric beyond noise: fitness stayed -4.30 to -4.32 (baseline -4.296), trades
  4225-4468, halts 6-7, continuous max_dd -0.517 to -0.568 — nowhere close to
  closing the ~13-17 point gap to `MAX_DD_HARD_FAIL` (0.40). Baseline
  reproduced the 02:43 UTC session's recorded numbers closely (fitness
  -4.296 exactly; trades/halts within a few percent, plausibly from a
  slightly later `years=4.0` fetch window). **Sharpens, doesn't reopen, the
  open question**: this is evidence for "the x6-scaled seed is structurally
  too aggressive" and against "it's a scaling-recipe artifact in the eval
  harness," at least along these two dimensions — a genuinely hand-retuned
  (not just scaled) 4h starting point is still the next real test, now on
  firmer footing that the seed's own numbers aren't a harness bug. Did not
  check `constitution.MIN_BARS`/the 120-bar minimum-slice-length checks
  (gate validity, not risk-taking — weaker candidate for a 50%+ drawdown, not
  tested on a time-budget call). `git status` clean, `live_state.json`
  unchanged, `python3 -m pytest -q` 243/243 confirmed at session start, no
  code changed (two standalone scratch scripts, not committed), genome still
  v3 (1d).

- **Found 2026-08-31 (3-hourly check, ~02:43 UTC): a second, differently-seeded
  x6-scaled 4h shadow run also found zero promotions across 14 generations —
  same outcome as the 23:05 UTC run, via a different rejection-mechanism
  split.** See "Next steps" item 2 and
  `runs/2026-08-31-0243-4h-shadow-seed9001-still-zero-promotions.md`.
  `EvolutionRun(data, seed=9001)` instead of the default `seed=7` every prior
  4h-shadow session (including 23:05 UTC's) had used — the seed=7 run's own
  flagged follow-up. Champion (the scaled seed) stayed pinned at fitness
  -4.296 the whole run. Of 42 total rejections (3 top candidates x 14
  generations), 31 (74%) failed the dd-corrected hard gate (too few trades,
  too short, or continuous-replay drawdown > 40%) and 11 (26%) failed the
  sealed holdout — roughly inverted from the 23:05 UTC run's split (40%
  hard-gate / 60% holdout). Same end result, different failure mix: read as
  stronger evidence the "x6-scaled seed can't clear the post-2026-08-22
  promotion funnel" finding isn't specific to one `Researcher` seed's
  proposal sequence. Sharpest single data point: a generation-5 candidate at
  fold-fitness +1.310 (a huge nominal improvement) still failed holdout
  (-0.976 vs a required -1.787 + 2.965 margin at 3 cumulative draws) — the
  fold/holdout regime mismatch this thread has documented on the live 1d
  path, reproduced cleanly in the 4h shadow track. **Recommend not running
  more seeds of this same scaled-seed genome** — the open question is now
  sharper (is the x6-scaled seed itself structurally too aggressive — 4413
  search-fold trades, halts 5, fitness -4.296, none of which any real live
  1d champion has ever shown — for this gate to clear from at all, versus a
  genuinely retuned, not just scaled, 4h starting point), not "try yet
  another seed of the same construction." `git status` clean, `live_state.json`
  unchanged, `python3 -m pytest -q` 243/243, no code changed (standalone
  scratch script, not committed), genome still v3 (1d).

- **Found 2026-08-30 (3-hourly check, ~23:05 UTC): the first fresh 4h shadow
  evolution since the dd-corrected gate landed shows the item-2 thread's
  "reliable gen-1 quick fix" pattern no longer holds, plus a first (caveated)
  4h holdout-noise number.** See "Next steps" item 2 and
  `runs/2026-08-30-2305-4h-shadow-dd-corrected-gate-and-holdout-noise.md`.
  8 generations, x6-scaled seed, `n_blind=6` (same recipe as every prior 4h-
  shadow run) — unlike every one of those prior runs (all dated 2026-08-16
  through -19, before `dd_corrected_stats()` was wired into `generation()`'s
  acceptance loop at the 2026-08-21/22 weekend all-hands), this run found
  **zero** promotions across all 8 generations. Each generation's top
  fold-aggregate candidate looked like the usual quick fix (fitness -0.131 to
  0.459, comfortably clearing champion's -4.200) but got rejected either by
  the dd-corrected hard gate (continuous-replay maxDD > 40%, invisible to the
  fold-merged number — 6 of ~15 top-3 candidates checked) or the sealed
  holdout (the rest). Reads as: the fold-dd-blindspot fix that closed a real
  gap in the 1d live path also closes off this specific 4h-shadow thread's
  easy early promotions, not previously observed because no 4h run had used
  the fixed gate before now. Block-bootstrapped the only genome this run
  produced (the never-promoted seed itself) the same way `holdout-noise`
  measures the live 1d champions: boot_fitness_std 1.461, 0.73x
  `HOLDOUT_SIGMA` (2.0) — directionally supports the "more holdout bars, less
  relative noise" hypothesis `holdout-noise`'s notes flagged but never
  measured, but weakly (lands inside the existing 1d range, ~0.74x-1.02x
  across v1/v2/v3, not below it) and on a genome that never cleared the
  search gate, not a real promoted champion — not apples-to-apples with the
  1d measurement. `md5sum live_state.json` unchanged
  (`81922c6011c986449f635dbf43553d0e`), `python3 -m pytest -q` 243/243, no
  code changed (standalone scratch script, not committed), genome still v3.

- **Closed 2026-08-30 (3-hourly check, ~18:51 UTC): the v3 demotion/rollback
  question — raised 2026-08-22, reaffirmed unresolved in every daily
  discussion since — now has a full design pass with a recommendation,
  same closure pattern the 06:00 UTC weekend all-hands used for the
  fitness-vs-excess-return question.** See
  `runs/2026-08-30-1851-demotion-rollback-design-pass.md`. Fresh
  `succession-audit`: v3 (live) and v1 both hard-fail the corrected
  drawdown gate outright (-46.5%/-54.4% continuous maxDD); v2 doesn't
  hard-fail but only marginally (dd-corr fitness 0.234, and its
  full-history maxDD passing the 40% line looks more like an artifact of
  `dd_corrected_stats()`'s one-directional `min()` blind spot than a clean
  pass, per the 2026-08-24 two-sided-diagnostic finding). New fact this
  session adds: v3's full-history excess return over buy-and-hold is
  **+68.2%**, the only positive number of the three (v1 -115.7%, v2
  -73.8%) — whichever selection metric you prefer, v3 is the best of the
  three real champions on both, despite being the only one that hard-fails
  drawdown. **Recommendation: status quo, no demotion mechanism, no
  constitution change** — `MAX_DD_HARD_FAIL` is a prospective gate on new
  candidates (its job, per every amendment-log entry that touches it, is
  stopping the search from mining noise into a false promotion), not a
  retroactive license revocation for a sitting champion whose own past
  performance looks worse under a later-discovered measurement correction;
  and no real champion this account has ever had is both closer to
  clearing the gate cleanly and better on excess return than v3, so an
  automatic mechanism would have nowhere better to send the champion.
  Three named revisit triggers (a real `evolve()` challenger that actually
  clears `accepts()`/`holdout_accepts()` against v3 — already automatic,
  no new code needed; `succession-audit` ever showing a candidate that beats
  v3 on both drawdown-gate-closeness and excess return; the live paper
  account realizing a real drawdown near `CIRCUIT_BREAKER_DD` (0.25)).
  None has fired. `md5sum live_state.json` unchanged
  (`81922c6011c986449f635dbf43553d0e`), `python3 -m pytest -q` 243/243
  confirmed at session start, no code or constitution changed, no
  `AMENDMENTS.md` row needed.

- **Corrected 2026-08-30 (3-hourly check, ~13:01 UTC): the 09:51 UTC short-selling
  design pass's Phase 1 scoping was wrong about who can ship it — `core/portfolio.py`
  is not "under the constitution in spirit," it is one of exactly two files
  `constitution.checksum()` literally hashes (`_PROTECTED = ["__init__.py",
  "../core/portfolio.py"]`), sealed by `evotrader.manifest`.** Attempted to actually
  build Phase 1 this session (`short()`/`cover()` + borrow accrual on
  `PaperBroker`, signed-`qty` convention, 16 new unit tests covering short→mark→cover
  round trips, borrow accrual, the cross-side buy/short guards, and a mid-short
  circuit-breaker trip) — the tests passed and the implementation matched the design
  doc, but `python3 -m pytest -q` on the full suite then failed 12 tests in
  `tests/test_run_from_files_matches_bundle.py` with `CONSTITUTION MODIFIED: expected
  8b74865634b1db07, found ...` the moment `tools/edit_bundle_module.py sync` folded
  the edited `core/portfolio.py` into the bundle. This file's own standing rule
  (`## Run protocol`, "If a run reports CONSTITUTION MODIFIED, stop. Do not re-seal
  it.") means a scheduled session cannot ship this change and move on — every
  scheduled command (`tick`, `evolve`, the daily run) calls `constitution.verify()`
  at startup and refuses to run once the seal breaks, and there is no CLI path that
  re-seals it; only a human editing `evotrader.manifest` by hand can. **Reverted
  everything this session** (`git checkout -- core/portfolio.py evotrader_bundle.py`,
  deleted the new test file) rather than leave the seal broken for whatever runs
  next — confirmed `evotrader.manifest` itself was never touched (`verify()` only
  reads and compares, never auto-writes on mismatch) and `python3 -m pytest -q`
  is back to 243/243 clean, `md5sum live_state.json` unchanged
  (`81922c6011c986449f635dbf43553d0e`). **What this changes for item 5**: Phase 1
  is not the safe, no-sign-off engineering slice the design pass described — it
  needs the same human-reviewed `AMENDMENTS.md` row and manifest re-seal the design
  pass had deferred to Phase 2's constitution questions, just to land the broker
  mechanics at all, before any testing or wiring can follow. A future session
  should not attempt to ship Phase 1 code again without that sign-off in hand; the
  design itself (signed-`qty` `Position`, `short()`/`cover()` mirroring `buy()`/
  `sell()`, `borrow_bps_per_bar` accrued in `mark()`) held up under real
  implementation and is worth keeping as the starting point once a human has
  reviewed and re-sealed.

- **Written 2026-08-30 (3-hourly check, ~09:51 UTC): a design pass for item 5
  (short selling), which had zero history before this — every other open
  item had prior sessions behind it, this one didn't.** See "Next steps"
  item 5 and `runs/2026-08-30-0951-short-selling-design-pass.md`. Traced
  "long-only" to five independent places that would each need real work,
  not a relabeling: `core.portfolio.PaperBroker` (docstring says it
  outright; `buy`/`sell`/`equity` all assume `qty` moves one direction),
  `core.types.Intent`/`Order`'s `side` vocabulary (`"sell"` means "close a
  long" everywhere it's read, there's no "open a short"), all three
  `agents.consults` modules (every `Intent` construction is `"buy"` or
  `"sell"`, none propose opening a short), `agents.judges.RiskJudge.rule`
  (buys/sells are two structurally different code paths, a short needs its
  own entry+exit logic, not a flag), and the risk gates themselves
  (`mark()`'s circuit breaker assumes bounded long-only downside; a short's
  loss is unbounded). Borrow cost: no public keyless lending-rate feed
  exists (this project's `## No credentials, anywhere` design only covers
  price data), but a modelled constant rate is the same *kind* of
  approximation `fee_bps`/`slippage_bps` already are, not a new one.
  Recommends a phased build — Phase 1 (`short()`/`cover()` + borrow accrual
  on `PaperBroker`, tested in isolation, zero behavior change for existing
  callers) is scoped concretely enough for a future session to actually
  build; Phase 2 (genome/agent wiring + the two constitution questions this
  write-up surfaces but doesn't answer: a short-exposure cap, and whether
  `MAX_DD_HARD_FAIL` needs a short-specific instrument) and Phase 3 (shadow
  evolution) come after, each needing their own `AMENDMENTS.md` argument
  before touching promotion gates. No code changed this session — deliberate:
  money-tracking-core correctness deserves the same measure-before-code
  discipline already applied to `HOLDOUT_SIGMA` and the dd-corrected maxDD
  fix, not both a design pass and a broker rewrite in one slot. `md5sum
  live_state.json` unchanged, `python3 -m pytest -q` 243/243 confirmed at
  session start, no genome or constitution touched.

- **Closed 2026-08-30 (3-hourly check, ~09:15 UTC): the narrow "does
  `lone_voice_scale > two_agree_bonus` contribute to the disagreement-sweep
  thread's risky-direction skew" side-question, tried against real
  champions instead of a hand-built clamp — recommend treating it as
  exhausted for now.** (see "Next steps" item 0 and
  `runs/2026-08-30-0915-lone-voice-real-champion-check.md`) The 05:18 UTC
  session's own flagged follow-up ("compare against a second real champion
  ... rather than a hand-built counterfactual that also moves fitness")
  attempted: this account's real lineage splits 2-vs-1 on the inequality
  (v1/v2 both `lone=0.6<two=1.2`, only live v3 has `lone=1.4791>two=1.2`), a
  genuine natural experiment. `disagreement_scan` against all three real
  champions (fresh `Evaluator`, same `Researcher(seed=4242)`,
  `generations=15, n_blind=14`, blank memory) found a much bigger swing than
  the clamp test — risky share 58.1% (v1), 28.2% (v2, the first-ever
  conservative-majority point in this thread), 90.9% (v3) — but sorted by
  fold-fitness instead (+0.112, -0.151, -1.669) the same three points line
  up exactly as monotonically: fitness and the gene inequality covary in the
  same direction across every real champion this account has ever had, so
  three uncontrolled real points can't separate "the gene pairing drives the
  skew" from "worse fold-fitness drives it" (the keep_frac sweep's own
  established pattern) any better than the clamp test could — if anything,
  worse, since the real lineage never offers a case where the two
  explanations disagree. One incidental resolution: the 05:18 UTC clamp
  test's anomalous reversal of the fitness-predicts-disagreement-rate
  pattern did not replicate here (rate tracks fitness monotonically again,
  16.9%→26.8%→44.8%), reading as a hand-clamp-specific artifact, not a
  general genome-perturbation property. Three independent looks at this
  narrow side-question (clamp, real-champion comparison, the underlying
  fitness-decomposition work) now land on the same structural problem —
  recommend the same "exhausted, not wrong to revisit, not worth another
  data point without a genuinely constructed fitness-held-fixed
  counterfactual" standing as the fold-scheme windowing chain's own
  2026-08-21 exhaustion finding. Does not touch the broader
  selection-metric-redefinition question, which stays closed per the 06:00
  UTC weekend all-hands write-up. `md5sum live_state.json` unchanged
  (`81922c6011c986449f635dbf43553d0e`), no code changed, `python3 -m
  pytest -q` 243/243 confirmed at session start.

- **Closed 2026-08-30 (weekend all-hands, 06:00 UTC): the fitness-vs-excess-return
  selection-metric thread's measurement phase is done — full design pass written,
  recommendation is status quo (no constitution change), with three explicit
  revisit triggers.** (see "Next steps" item 0 and
  `runs/2026-08-30-0600-weekend-all-hands.md`) Seven independent angles measured
  across ten sessions since 2026-08-16 (original underperformance finding, the
  06:00 UTC as-of-drift mechanism, the 16:26 UTC direction/disagreement study, the
  19:12 UTC favorable-window control, the 22:50 UTC keep_frac sweep, the
  selection-noise winner's-curse test, this morning's gene-pairing counterfactual)
  converge on the same shape: real, mechanistically understood (long-only
  champions inherit market beta, so Sortino-shaped fitness rewards absolute
  return far more than skill-over-benchmark), largest exactly when the champion
  is already losing on raw terms — and, the load-bearing fact, **never once shown
  to flip a real promotion decision**. Both real promotions this account has ever
  made (v1→v2, v2→v3) agree under fitness and excess-return criteria alike
  (`promotion-excess-check`, re-run fresh this session: v2→v3's recorded
  challenger fold-agg excess +6.8% vs champion −35.1%, holdout excess +21.7%,
  `beat_benchmark=True` — never in tension). Every real sealed-holdout-stage
  disagreement found so far (6/40 in the 16:26 UTC sample) is a near-tie on
  excess return (0.1-1.1pp), not a lopsided flip. Considered and rejected:
  (A) redefining `fitness()` around excess return — same overfitting-the-scoreboard
  objection as 2026-08-16, sharpened by this session's finding that the
  disagreement itself tracks the champion's *current* window fitness, i.e. an
  excess-return objective would likely just overfit to a different window
  instead. (B) a hard `beat_benchmark` gate at the sealed holdout — narrower, but
  would not have changed either real promotion and has no measured false-reject
  rate of its own, the same gap `HOLDOUT_SIGMA` closed with real measurement
  before that gate was touched. (C) status quo, recommended: the monitoring this
  question would ask for already exists and runs (`edge_vs_benchmark()` on every
  fold/holdout, `beat_benchmark` on every generation record, `live-benchmark` CLI,
  the dashboard's buy-and-hold panel) — there is no visibility gap for code to
  close, only a policy question, which stays explicitly the owner's call per this
  file's own repeated framing, not something this session enacts. Fresh
  `live-benchmark` re-run this session: live account now −8.42% excess over 15
  real bars (was −7.88%/14 bars two weeks ago) — still the single most important,
  least gameable number in this thread, and the first of the three concrete
  revisit triggers the write-up names (60 more real trading days still negative
  with no narrowing; a real, not shadow, promotion where the two criteria
  disagree at holdout; or a fourth real champion). None has fired yet. No code
  changed, no `AMENDMENTS.md` row (explicit no-change, not a calibration),
  `md5sum live_state.json` unchanged (`81922c6011c986449f635dbf43553d0e`),
  `python3 -m pytest -q` 243/243 confirmed at session start.

- **Measured 2026-08-30 (3-hourly check, ~05:18 UTC): weak evidence against
  the 00:46 UTC entry's flagged hypothesis — clamping `lone_voice_scale` down
  to `two_agree_bonus` did not meaningfully shrink the disagreement-sweep
  thread's risky-direction skew.** (see "Next steps" item 0 and
  `runs/2026-08-30-0518-lone-voice-counterfactual.md`) One-off scratch
  script (same never-save discipline as every prior throwaway shadow script
  in the disagreement-sweep thread), `loop.evolve.disagreement_scan` against
  real champion v3 and an in-memory-only counterfactual (`g0.child([...
  lone_voice_scale -> two_agree_bonus's own value ...])`, so `lone_voice_scale
  == two_agree_bonus == 1.2`, everything else identical), same
  `Researcher(seed=4242)`, same universe/window, both blank
  `researcher_memory`. Risky share of fold-stage disagreements: 90.9% (real)
  vs. 86.1% (counterfactual) — within noise for n=99/79, not the sharp
  reduction the hypothesis predicted. Unplanned confound, itself worth
  flagging: the clamp also changed the champion's own fold-fitness a lot
  (-1.669 -> -2.637) and the fold-stage disagreement rate moved *opposite*
  to what the 2026-08-29 22:50 UTC keep_frac sweep's monotonic
  fitness-predicts-disagreement pattern would predict (worse fitness, lower
  disagreement rate here) — the first case in this thread where that pattern
  didn't hold, though that sweep only ever varied the calendar window, never
  the genome, so it was never actually tested against this kind of
  perturbation. One counterfactual, one seed, one champion — a first data
  point, not settled. Does not touch the still-open "should the selection
  metric be redefined" question, which remains the owner's call.
  `md5sum live_state.json` unchanged, no code changed this session (pure
  scratch-script measurement), baseline `python3 -m pytest -q` 243/243
  confirmed at session start.

- **Resolved 2026-08-30 (3-hourly check, ~00:46 UTC): tick 16's hard-call
  flag reviewed — the first real verdict this infrastructure has ever
  recorded.** (see `runs/2026-08-30-0046-hard-call-review-tick16.md`) Rather
  than taking the "lone-voice buy, agreement 0.33" flag at face value,
  reconstructed `RiskJudge.rule`'s scoring arithmetic by hand against
  champion v3's real evolved `risk_judge` genes and matched it to the actual
  order to the cent: v3's evolved `lone_voice_scale` (1.4791) is *higher*
  than `two_agree_bonus` (1.2), so LINKUSDT's solo-conviction score (0.938 ×
  1.4791 = 1.387) legitimately outranked the bar's only multi-agree
  candidate, UNIUSDT (0.794) — not a fluke. The evolved `cash_floor_pct`
  (35.03%) left only 16.97% of equity deployable that bar, which LINK's
  order consumed in full (`min(base_size_pct*score, max_position_pct)`
  capped by `cash_avail` = $1915.45, exact match), correctly starving every
  other candidate via `"no room"` rather than any processing-order bug.
  Size (17.0%) sits within both position caps; the underlying signal was an
  ordinary confirmed-trend read. **Verdict: `approve`**, recorded via
  `review-hard-calls --tick 16 --verdict approve --notes '...'` —
  `review-hard-calls` now reports 0 pending, 1 reviewed. Flags an open
  observation for later, not actioned this cycle: v3's
  `lone_voice_scale > two_agree_bonus` structurally favors solo conviction
  over cross-consultant consensus, the same direction the disagreement-sweep
  work (previous entries below) keeps finding a risky-direction skew in —
  worth a future session checking whether this gene pairing is a
  contributor. `md5sum live_state.json` changed only by the new
  `hard_call_reviews` entry (expected — this is the one command that
  intentionally writes state); everything else untouched.

- **Built 2026-08-29 (3-hourly check, ~22:00 UTC): the keep_frac sweep the
  19:12 UTC entry's own "Next" flagged is now a real, tested, reusable tool
  instead of a fifth throwaway shadow script.** New `loop.evolve.
  disagreement_scan` (tested, `tests/test_disagreement_scan.py`, 3 new tests,
  full suite 243 passed up from 240) mirrors `EvolutionRun.generation()`'s
  exact proposal/gating pipeline (`Researcher.propose`, `Evaluator.evaluate`,
  `dd_corrected_stats`, `constitution.accepts`, `Evaluator.holdout_check`,
  `constitution.holdout_accepts`) but never calls
  `Genome.save()`/`.promote()`/`EvolutionRun._record()` — an in-generation
  "would-promote" only swaps the champion in memory for the rest of the scan,
  the same no-disk-writes discipline every throwaway script this project has
  run today already followed by hand. Classifies every candidate's
  fold-stage (and, for candidates that clear the fold gate, holdout-stage)
  verdict as "agree"/"risky"/"conservative", the same terms the 16:28/19:12
  UTC run notes already used. New CLI `disagreement-sweep [--keep-fracs
  1.0,0.90,...] [--generations 15] [--n-blind 14] [--fresh]` truncates each
  symbol's loaded history to its first `keep_frac` of bars (same trick the
  19:12 UTC session used by hand to shift the 85/15 fold/holdout split onto
  an earlier, friendlier calendar window) and runs `disagreement_scan` at
  each point, seeded from the live champion's real `researcher_memory` by
  default. Smoke-tested against real data at `keep_frac=1.0`,
  `--generations 1`: champion fold-fitness -1.695 (matches the 16:28/10:17
  UTC sessions' own reading of today's window exactly), 14 fold-stage
  candidates (10 risky, 1 conservative), 3 holdout-stage (0 disagreements) —
  consistent with, not identical to (different random proposal batch), those
  two sessions' full 15-generation numbers. Read-only, verified safe:
  `md5sum live_state.json` unchanged, `tools/edit_bundle_module.py sync
  --check` clean (the CLI dispatch lives in the bundle's own `main()`, same
  precedent as `promotion-excess-check`/`live-benchmark`; `disagreement_scan`
  itself lives in `loop/evolve.py`, synced into the bundle's `_SRC` the
  normal way). A real 15-generation sweep at `--keep-fracs 0.95,0.85` was
  kicked off in the same session to extend today's existing 1.00/0.90 data
  points — see the next entry for the result.

- **Found 2026-08-29 (3-hourly check, ~22:50 UTC): the keep_frac sweep ran
  for real, and the driver isn't keep_frac itself — it's the champion's own
  fold-fitness on the window.** (see
  `runs/2026-08-29-2250-disagreement-sweep.md`) `disagreement-sweep
  --keep-fracs 0.95,0.85 --generations 15` (new tool, previous entry) adds
  two real data points to today's existing 1.00 (two sessions, 63.3%/66.2%
  fold-stage disagreement) and 0.90 (8.6%) readings: 0.95 -> 21.0%, 0.85 ->
  20.4%. Sorted by `keep_frac` this looks noisy (66%, 21%, 8.6%, 20%); sorted
  by the champion's own fold-aggregate fitness on each window instead
  (-1.695, 0.949, 1.263, 1.398) the disagreement rate decreases
  monotonically (66.2%, 21.0%, 20.4%, 8.6%) — `keep_frac=0.90` just happens
  to land on an unusually favorable window (champion fold-fit 1.398, higher
  than the less-truncated 0.95's 0.949), which is why one data point looked
  like a smooth keep_frac trend. Holdout-stage disagreement shows the same
  split more starkly: 8.9-15.0% on the two windows where the champion is
  underwater, 0.0-4.2% on the three where it dominates. The risky-direction
  skew persists at every point (61-89% risky, never conservative-majority).
  Reads as a sharper version of the 19:12 UTC entry's own conclusion, not a
  contradiction of it: the apparent disagreement problem tracks how much the
  champion is already struggling on raw fitness, which is also the situation
  where a promotion decision is least likely to hinge on excess return
  specifically — more evidence for patience on the still-open "redefine the
  selection metric" question, not for urgency. 5 points, 2 seeds, 1 champion
  (v3 real `researcher_memory`, independent per point) — a pattern, not a
  proven law. `md5sum live_state.json` unchanged throughout,
  `python3 -m pytest -q` 243/243, `tools/edit_bundle_module.py sync --check`
  clean.

- **Found 2026-08-29 (3-hourly check, ~19:12 UTC): the 16:28 UTC session's
  own flagged confound checked — both the 63.3% fold-stage disagreement
  rate and the near-tie holdout disagreements are substantially as-of-drift
  artifacts, not fixed properties of champion v3.** (see
  `runs/2026-08-29-1913-favorable-window-disagreement-check.md`) Same
  sandbox-only shadow-search discipline, same real `researcher_memory`
  seeding, 15 generations, `n_blind=14` — but this time each symbol's
  loaded data was truncated to its first 90% of bars before evaluation, so
  the existing 85/15 fold/holdout split lands on an earlier, friendlier
  window (ending 2026-04-04) where champion v3's own fold-aggregate fitness
  is +1.398 instead of today's -1.695. Result: fold-stage disagreements
  fell from 63.3% to **8.6%** (18/210, still skewed 77.8% risky but on a
  much thinner sample), and sealed-holdout disagreements — 15.0% and 8.9%
  on the two unfavorable-window sessions — fell to **0.0%** (0/4; only 4
  candidates even reached that gate, since the stronger champion dominated
  192/210 candidates outright on both metrics at once). Reads as evidence
  *for* patience on the still-open "redefine the selection metric" question
  rather than against it: the apparent disagreement problem shrinks a great
  deal once the champion isn't fighting a hostile calendar window, which is
  itself temporary and drifting, not a fixed flaw in raw fitness. One
  truncation point, one seed, one champion — not a `keep_frac` sweep, not
  repeated with a second seed, not yet tried against a different champion.
  Read-only: no file written by the shadow script (deleted after
  extraction), `md5sum live_state.json` unchanged
  (`bf360fc7f86f6bae2bc46bb6f6dc6026`), `python3 -m pytest -q` 240/240,
  `tools/edit_bundle_module.py sync --check` clean.

- **Found 2026-08-29 (3-hourly check, ~16:26 UTC): the 10:17 UTC session's
  open "is the disagreement direction mixed or one-sided?" question is
  answered — it's heavily one-sided, at both stages.** (see
  `runs/2026-08-29-1628-candidate-excess-disagreement-direction.md`)
  Same sandbox-only discipline (nothing written to disk, script deleted
  after extracting results), same seeding (live champion v3's real
  `researcher_memory`), 15 generations, but this time every candidate's
  fitness-vs-excess-return comparison is classified by *direction*, not
  just counted as agree/disagree. Fold-aggregate: 210 candidates, 133
  disagreements (63.3%, matching the 10:17 UTC session's 66.2% on a
  different random seed) — of those, **118 (88.7%) are the "risky"
  direction** (raw fitness ranks the challenger above the champion while
  excess return ranks it below), only 15 (11.3%) the reverse.
  Sealed-holdout (the gate a real promotion is decided at): 40 candidates
  reached it, 6 disagreements (15.0%) — **5 (83.3%) risky**, 1 (16.7%)
  reverse, matching the 10:17 UTC session's own qualitative description
  of its 4 holdout disagreements. Read together with that session's
  finding that every holdout-stage disagreement so far is a *near-tie*
  on excess return (0.1-1.1pp): raw fitness's blind spot is real,
  systematic, and consistently one-sided, but every real instance found
  so far is a near-miss, not a lopsided flip that would have driven a
  bad promotion. One 15-generation sample against one champion on one
  calendar window — not validated across champions or fold windows yet.
  Does not touch the still-open "should the selection metric be
  redefined" question, which stays the owner's call.

- **Built 2026-08-29 (3-hourly check, ~12:54 UTC): new `live-benchmark`
  diagnostic answers the fitness-vs-excess-return question with the live
  paper account's own real fills for the first time — not a backtest, not a
  shadow search — and it trails buy-and-hold by 7.9pp so far.** (see
  `runs/2026-08-29-1254-live-benchmark-diagnostic.md`) Every earlier session
  on this question today (06:00, 06:59, 10:17) replayed backtests. New
  `evotrader_bundle.py live-benchmark` instead reads
  `acct.broker.nav_history` (the account's real, already-executed NAV path)
  and compares it to an equal-weight buy-and-hold of the same universe over
  the identical real calendar window (`core.market.load_universe` +
  `loop.engine.benchmark_buy_hold`, both already-tested primitives — no new
  pure function). First real numbers, 2026-08-14 to 2026-08-28 (14 daily
  bars): live account +12.27% vs. buy-and-hold +20.15%, excess **-7.88%** —
  directionally consistent with the weekend all-hands' mechanistic finding
  and today's 10:17 UTC shadow-check, but this is the account's own genuine
  track record, not a replay. Important caveat the diagnostic prints
  automatically: this window is NOT a clean single-genome test — the real
  journal shows the account traded under v1 (day 1), v2 (day 2), then v3
  (days 3-15), two promotions happened mid-window, so this measures "how has
  the account actually done" (including transition costs), not "how has
  champion v3 done" specifically. Only 14 bars, far too short to be a
  verdict — but it grows for free every day, and re-running this
  periodically as real history accumulates is a genuinely different signal
  from anything a backtest or shadow search can produce. Read-only: never
  touches `live_state.json` (`md5sum` unchanged), `python3 -m pytest -q`
  full suite green, `tools/edit_bundle_module.py sync --check` clean (new
  code lives in the bundle's own CLI dispatch, same precedent as
  `succession-audit`/`promotion-excess-check`). Not wired into the
  dashboard this session — would add a network fetch to every dashboard
  rebuild, which happens far more often than this is worth recomputing;
  flagged as a cheap follow-up if this stays valuable. Does not touch the
  still-open "should the selection metric be redefined" question, which
  stays the owner's call.

- **Found 2026-08-29 (3-hourly check, ~10:17 UTC): among real generated
  candidates (not just the two real promotions), raw fitness and
  excess-return DO disagree sometimes, including at the sealed-holdout gate
  — but every disagreement found is a near-tie on excess return, not a
  lopsided flip.** (see `runs/2026-08-29-1017-candidate-excess-shadow-check.md`)
  A sandboxed 15-generation shadow search against live champion v3 (seeded
  from its real `researcher_memory`, same discipline as the 2026-08-28
  guardian-weighted-shadow-evolve session but touching *zero* files on disk
  this time — no `Genome.save()`/`.promote()`/`EvolutionRun.run()`
  anywhere, the whole loop carries the champion `Genome` object in memory)
  compared every candidate's raw-fitness verdict against its excess-return
  verdict at both stages. Fold-aggregate: 210 candidates, 139 disagreements
  (66.2%) — but this replay's fold window has the champion's own
  fold-aggregate fitness deeply negative (-1.695, an unfavorable calendar
  window, same as-of-drift mechanism the weekend entry identified), so this
  number is more evidence for that mechanism, not an independent one.
  Sealed-holdout (the gate a real promotion is decided at): 45 candidates
  that cleared the fold gate, 4 disagreements (8.9%) — the first time this
  account has seen the two criteria disagree at the gate that matters, vs.
  0/2 on the two real promotions the 06:59 UTC check looked at. All 4 cases:
  the challenger clearly beat the champion's holdout fitness (0.503 baseline
  vs. 0.521-1.070) while its holdout excess return was marginally *below*
  the champion's own 23.12% (within 0.1-1.1pp) — none were actually
  promoted (multiple-testing margin rejected all 4 on raw fitness terms
  alone, the same "raw beat, margin rejected" pattern 2026-08-28's
  `holdout-margin-audit` already quantified), so no real decision changed.
  Sharpens, doesn't settle, the weekend entry's question: disagreement is
  real and reaches the promotion gate, but only as a near-tie so far, not
  evidence of a case where the two criteria would pick opposite winners by
  a wide margin. Redefining the selection metric itself remains the
  owner-level design decision the weekend entry and today's 09:00 UTC daily
  discussion already flagged it as — not attempted here.

- **Answered 2026-08-29 (3-hourly check, ~06:59 UTC): checked the weekend
  all-hands entry's flagged question against real data for the first time —
  no, an excess-return-based selection criterion has never actually
  disagreed with raw Sortino `fitness()` on either of this account's two
  real promotions.** (see `runs/2026-08-29-0659-promotion-excess-check.md`)
  New diagnostic `promotion-excess-check` reconstructs champion and
  challenger for each real promotion (v1→v2, v2→v3) and replays both on
  identical footing against today's data (`Evaluator.evaluate` +
  `Evaluator.holdout_check`), comparing fold-aggregate and sealed-holdout
  fitness against fold-aggregate and sealed-holdout excess return. Both
  promotions: challenger wins on all four measures, no disagreement. For
  v2→v3 the actual promotion-time recorded `champion_edge`/`edge`/
  `holdout_edge` (only promotion with edge data — v1→v2 predates edge
  tracking) point the same direction as the same-basis replay. Two data
  points only, not proof the two criteria are equivalent in general — this
  answers "has this ever been checked" (no, until now), not "should the
  selection metric be redefined" (still open, still an owner-level design
  question, not attempted here — see the weekend entry below for why).
  Read-only: composes only already-tested `_reconstruct_champion_genome`/
  `Evaluator.evaluate`/`Evaluator.holdout_check`, no new pure function, no
  constitution or `live_state.json` touch (`md5sum` unchanged), `python3 -m
  pytest -q` 240/240, `tools/edit_bundle_module.py sync --check` clean (the
  new code is in the bundle's own CLI dispatch, not a `_SRC` module).

- **Resolved 2026-08-29 (weekend all-hands): the 03:56 UTC entry's "actual
  driver still unidentified" flag is closed — the driver is market beta, not
  calendar recency, and it settles the open `HOLDOUT_SIGMA` quadrature
  question with a firm no.** (see
  `runs/2026-08-29-0600-weekend-all-hands.md`) Re-ran `history-perturb
  --champion-only 30 --as-of-step-days 14` against all three real champions
  this account has ever had (v3 live, v1/v2 reconstructed via
  `--also-version`), this time keeping the full per-row table instead of just
  the summary stats, and reconstructed each row's benchmark buy-and-hold
  return as `total_return - excess_return` (both already printed per row).
  Three findings, all confirmed on all three champions independently
  (`bench_ret` reconstruction itself matched to 0.1pp across all three, as it
  must — same fixed universe, genome-independent):
  1. **Fitness (Sortino-shaped) is almost entirely explained by the
     challenger's own absolute return, not by excess-over-benchmark.**
     Pearson(fitness, own return) = 0.96 (v3) / 0.99 (v1) / 0.99 (v2).
     Pearson(fitness, excess_return) is weak-positive for v3 (0.21) and
     **negative** for v1 (-0.52) and v2 (-0.59) — for two of three real
     champions, scoring *better* on the sealed holdout is mildly anti-
     correlated with actually beating the benchmark more.
  2. **The champion's own return correlates strongly with the benchmark's own
     return over the same window** (Pearson 0.71-0.77 across all three) —
     expected, since every real champion so far is long-only and net-long
     biased, so it inherits a large chunk of the underlying crypto market's
     own beta. Older as-of dates (idx 15-29, holdout windows starting
     2024-05 through 2024-11) land inside 2024's crypto bull run — mean
     benchmark return **+67.7% to +67.8%** across all three champions, nearly
     identical — while newer as-of dates (idx 0-14, holdout windows starting
     2024-11 through 2025-04) land inside a much weaker/negative 2025 stretch
     — mean benchmark return **-9.3%** across all three, again nearly
     identical. This is the actual mechanism behind the recency correlation
     the 03:56 UTC entry found (Pearson(idx, fitness) 0.69-0.77 across the
     three) — recency is a proxy for which calendar-fixed regime the sliding
     `HOLDOUT_FRAC` window happens to land on, not a driver in its own right.
  3. **This is the same mechanism the 2026-08-17 `regime` diagnostic already
     named generically** (fold 2's permanent +200% melt-up outlier structurally
     favoring/penalizing a genome by its own beta, independent of skill) —
     this session shows it recurring in the as-of-drift dimension too, and
     confirms it on all three champions rather than one fold on one genome.

  **What this settles.** The 00:56/03:56 UTC entries left open whether to
  combine this session's as-of-drift std with `holdout-noise`'s block-
  bootstrap resampling std "in quadrature." **No** — not because the number
  is small, but because this isn't a noise source at all: it's explained
  variance (market beta, mechanistically identified above), not an
  independent zero-mean perturbation around the champion's true score. A
  quantity that is *negatively* correlated with genuine skill-over-benchmark
  for two of three real champions is not a candidate for folding into a
  safety-margin sigma via quadrature-sum, regardless of its empirical std.
  `HOLDOUT_SIGMA` (2.0), calibrated 2026-08-21 purely from `holdout-noise`'s
  resampling of one fixed realized price path — a genuinely different,
  cleaner, closer-to-iid noise source — is **not adjusted by this finding**.
  This closes the specific quadrature-combination question the last two
  3-hourly sessions left open; it does not touch `HOLDOUT_SIGMA` itself.

  **New, sharper open question this surfaces, not acted on here**: since the
  sealed-holdout fitness that gates every real promotion is dominated by a
  challenger's own market-beta-driven absolute return rather than its skill
  relative to a passive benchmark, a promotion decision's outcome depends
  materially on which slice of calendar history the ever-growing,
  fixed-fraction holdout window happens to be sitting on at evaluation time —
  not only on whether the challenger's policy is actually better. This is the
  same root concern as "Measured 2026-08-16" finding #1 (the system
  underperforms buy-and-hold) and the fold-2-outlier finding, now shown to
  reach directly into the sealed-holdout *promotion gate* itself, not just
  into reported diagnostics. Whether the holdout/fold selection metrics
  should be redefined around excess return rather than raw Sortino-shaped
  fitness is a real, larger design question — flagged here, explicitly not
  attempted this session (a metric redefinition touches the checksummed
  constitution and every acceptance gate built on `fitness()`, and deserves
  its own dedicated design pass and evidence base the way the
  correlation-penalty item got, not a same-session follow-on to a
  measurement run).

  Verified safe throughout: three full 30-point sweeps (one per champion, one
  already-run v3 sweep from the 03:56 UTC entry reused, two new
  `--also-version` runs for v1/v2), all read-only — `md5sum live_state.json
  evotrader.manifest` unchanged across every run
  (`bf360fc7f86f6bae2bc46bb6f6dc6026` / `0bf3a7d9411ee692d0a9f152a7533803`),
  `python3 -m pytest -q` 240/240 (no code changed, no new tests needed —
  pure data analysis of existing CLI output), `tools/edit_bundle_module.py
  sync --check` clean, today's bar (00:20 UTC) already processed before this
  session (confirmed via `runs/2026-08-29-0020-daily-trading.md` existing),
  no `tick`/`evolve` call.

- **Found 2026-08-29 (3-hourly check, ~03:56 UTC): the 00:56 UTC entry's
  as-of-drift std was an underestimate of the plateau value, and — more
  important — the spread isn't symmetric noise, it's a trend.** (see
  `runs/2026-08-29-0356-champion-only-span-and-trend.md`) Ran
  `history-perturb --champion-only` three times against live champion v3 at
  increasing span (10pts/189d, 20pts/266d, 30pts/406d, no code changes):
  empirical std went 0.613 -> 0.830 -> 0.832 — genuinely plateaus by ~266
  days, but at ~0.83, ~35% higher than the first run's 0.613 (0.42x
  `HOLDOUT_SIGMA` now, not 0.31x). Bigger finding: Pearson r = 0.686 between
  as-of recency and fitness on the 30-point run — the older half of the as-of
  range (idx 15-29, holdout windows ending 2025-07 through 2026-02) scores a
  full point higher on average (mean 1.829, std 0.326) than the recent half
  (idx 0-14, mean 0.464, std 0.613), and the recent half accounts for nearly
  all the internal spread. Checked and ruled out one candidate mechanism (the
  known fold-2 melt-up episode falling inside the older windows' holdout
  slice) — the elevation starts at a holdout window that begins three months
  after that episode's own recovery date, so it isn't that. Actual driver
  still unidentified. **Matters for the still-open `HOLDOUT_SIGMA`
  combination question**: "combine in quadrature" assumes independent
  zero-mean noise sources; a real trend/regime-split inside this sample means
  that assumption doesn't hold as cleanly as the 00:56 UTC entry's framing
  implied, regardless of the exact std number. Doesn't touch `HOLDOUT_SIGMA`
  or propose a value — still a constitution-amendment-level decision, out of
  scope for a 3-hourly session. Read-only throughout: `md5sum
  live_state.json evotrader.manifest` unchanged across all three runs,
  today's bar (00:20 UTC) already processed before this session, no
  `tick`/`evolve` call.

- **Shipped 2026-08-29 (3-hourly check, ~00:56 UTC): `history-perturb
  --champion-only N [--as-of-step-days D]` — the follow-up the 2026-08-28
  21:53 UTC champion-anchor-drift entry flagged, turning its one-off 3-point
  real-lineage observation into a controlled, calibrated number.** (see
  `runs/2026-08-29-0056-champion-only-as-of-drift.md`) New mode, CLI-only
  (no new pure function, no constitution/engine change): unlike every other
  `history-perturb` mode, which tiles fixed-width windows, this replicates
  the sealed holdout's own definition ("newest `HOLDOUT_FRAC` of however
  much history exists") at N as-of dates D days apart walking back from
  "now" — truncate history to `index <= as_of`, run
  `run_backtest(genome, data, 1 - HOLDOUT_FRAC, 1.0)`, exactly the split
  `Evaluator.holdout_check()` computes inside `evolve()`. Mutually exclusive
  with `--independent` (different window scheme). **Finding (10 as-of
  points, 21 days apart, live champion v3)**: 7/10 finite (3 hit the maxDD
  hard gate outright), fitness range [-0.824, 1.167], spread 1.991, mean
  0.149, **empirical std 0.613** — 7.66x `MULTIPLE_TESTING_SIGMA` (0.08,
  confirming the fold-aggregate margin has no defense against this noise)
  but only 0.31x `HOLDOUT_SIGMA` (2.0, so the sealed-holdout margin as
  calibrated already comfortably covers this specific noise source alone).
  **Open, not resolved here**: `HOLDOUT_SIGMA` was calibrated from
  `holdout-noise`'s block-bootstrap *resampling* noise (~2.04 for v3, a
  different, independent noise source from this session's as-of-drift
  noise) — whether the two should combine (e.g. in quadrature, ≈2.13, a
  modest ~4% increase) or already overlap enough that 2.04 covers both is
  an open statistical question for whoever next touches `HOLDOUT_SIGMA`.
  Read-only throughout: `md5sum live_state.json evotrader.manifest`
  unchanged across every run including with `--also-version`, full test
  suite green (240/240, no regressions), `tools/edit_bundle_module.py sync
  --check` clean (this command lives only in the bundle's CLI dispatch, not
  a `_SRC` module), today's bar (00:20 UTC) already processed before this
  session, no `tick`/`evolve` call. Does not change the still-open
  constitution-amendment-level design question from 2026-08-28 (refresh the
  champion's holdout score periodically, vs. an absolute/percentile holdout
  bar) — sharpens it with a real number, doesn't resolve it.

- **Found 2026-08-28 (3-hourly check, ~21:53 UTC): the champion's own
  fold/holdout comparison score isn't fixed either — it's silently
  recomputed every `evolve()` invocation as the search/holdout windows
  slide forward, and the swing is large enough to matter.** (see
  `runs/2026-08-28-2153-champion-anchor-drift.md`) Read-only: grouped every
  real recorded holdout draw against live champion v3
  (`loop.evolve.summarize_holdout_pressure`, same function
  `holdout-pressure`/`holdout-margin-audit` use) by `holdout_champion`
  value. **Finding**: the same, unchanged v3 genome has scored three
  different values across its own reign so far (-1.172, -0.881, 0.763 on
  the holdout fitness scale; 1.389, 1.396, -1.612 on the fold-aggregate
  scale) — not from any code or genome change, just from being re-backtested
  on a later day's calendar-shifted window. Max swing: 1.644 (holdout),
  ~3.01 (fold-aggregate) — the fold-aggregate swing alone is ~10x the fold
  gate's typical `required_margin()` value (0.1-0.3 at realistic n), and
  neither `MULTIPLE_TESTING_SIGMA` nor `HOLDOUT_SIGMA` was calibrated against
  this noise source (`holdout-noise`'s block-bootstrap resamples one fixed
  price path; it can't see window drift). Doesn't change the standing
  conclusion (still a constitution-amendment-level design question,
  deserving more scrutiny than a 3-hourly session, not attempted here) but
  sharpens direction (a) from the 18:46 UTC entry below: "periodically
  refresh the champion's holdout score" isn't a new mechanism to add, it's
  *already happening* uncontrolled, with its own unmeasured noise. Flags a
  concrete, scoped follow-up: a `--champion-only` mode on
  `history-perturb`/`holdout-noise` that re-scores one fixed genome at
  several "as-of" dates, to turn this session's one-off 3-point observation
  into a real calibrated number. Verified safe: `live_state.json`/
  `evotrader.manifest` md5 unchanged throughout, no backtest run, no
  `evolve`/`tick` call, today's bar already processed before this session.

- **Shipped 2026-08-28 (3-hourly check, ~18:46 UTC): `holdout-margin-audit` —
  the same "raw beat but margin-rejected" pattern the 16:32 UTC shadow-evolve
  session found on 361 freshly-generated candidates also shows up in the real,
  already-recorded live lineage, no new search needed.** New read-only
  diagnostic (`evotrader_bundle.py holdout-margin-audit`, mirrored verbatim in
  `run_from_files.py`, proven byte-identical between the two by a new
  parametrize case in `tests/test_run_from_files_matches_bundle.py`) plus a
  new pure function `loop.evolve.raw_holdout_beats()` (4 new tests in
  `tests/test_holdout_pressure.py`) built on top of the existing
  `summarize_holdout_pressure()` — reads `acct.lineage` only, no market data,
  no backtest, never touches `live_state.json`, same guarantee as
  `holdout-pressure`. For every past champion reign, it separates
  sealed-holdout rejections into "the challenger was actually worse" vs. "the
  challenger's raw holdout score beat the champion's but not by
  `required_margin()`'s additive amount." **Finding on the real v3 lineage
  (20 recorded holdout draws)**: 3 of them (cumulative draws 15, 19, 21) beat
  champion v3's holdout score of 0.763 outright (up to 1.636, +114%) and were
  still rejected — the first, at cumulative draw 15, needed +4.655 margin
  and missed by nothing on sign, only on magnitude. v1 and v2 have 0 recorded
  holdout draws (nothing ever reached that gate during their reigns). This is
  a lower-bound diagnostic, not a proposed fix — see the tool's own printed
  caveat and the function's docstring for why a raw beat ignoring
  multiple-testing risk is not the same as "should have promoted," and why
  only the *first* flip in a reign is a valid counterfactual. Does not change
  the open design question from the 16:32 UTC entry below (still a
  constitution-amendment-level decision, still not attempted here) — it adds
  a second, independent, real-data confirmation of the same tension using
  history that was already sitting in `live_state.json`, rather than a new
  25-generation search. Verified safe: `md5sum live_state.json
  evotrader.manifest` unchanged (`0fa0731311baab0508f959f79a01214e` /
  `0bf3a7d9411ee692d0a9f152a7533803`) before and after every manual run of the
  new command, `tools/edit_bundle_module.py sync --check`/`verify` both clean,
  full test suite green, today's bar (00:20 UTC) already processed before
  this session started, no `tick` run. Also this session: local `main` was
  detached from `origin/main` at start (same history-rewrite artifact as
  every recent entry) — realigned with `git checkout -B main origin/main`,
  no force-push, nothing lost.

- **Shipped 2026-08-28 (3-hourly check, ~16:32 UTC): the multi-generation Guardian-weighted
  shadow `evolve()` search the 13:00 UTC entry flagged as the only untried lever —
  25 generations, 361 candidates, no promotion, but a sharper answer than
  "champion holds."** (see `runs/2026-08-28-1632-guardian-weighted-shadow-evolve.md`)
  Standalone script (not committed, same discipline as every prior shadow-evolve
  session), not wired into any CLI: `loop.evolve.EvolutionRun` against the real
  `core/agents/loop/constitution` files, seeded from live champion v3 and the
  account's real cumulative `holdout_draws=22`, with `Researcher.perturb()`
  subclassed so every blind proposal includes one of the 3 Guardian genes
  (`risk.stop_loss`/`trailing_stop`/`max_bars_held`) *combined* with genes from
  the full `GENE_SPACE` — not restricted to the 3-gene subspace
  `guardian-gene-test` already hand-swept. `acct.save()` never called;
  `live_state.json` opened read-only once. 1d bars run ~1.5-2.3 min/generation
  (vs 4h shadow work's 6-27 min), so 25 generations took 38.2 min.
  **Finding**: 69 of 361 candidates cleared the fold-aggregate gate (best fold
  fitness 1.582 vs champion's -1.612) and reached the sealed holdout — roughly
  5-6x more than the two hand-picked guardian-gene-test sessions found combined.
  **All 69 failed the sealed holdout — but 16 of them (23%) beat the champion's
  own holdout draw outright in raw terms**, up to +2.754 vs champion's +0.597
  (4.6x), and were rejected anyway because `holdout_accepts()` requires beating
  champion **+ margin** (5.6-6.0 at these draw counts, `HOLDOUT_SIGMA *
  sqrt(2*ln(draws))`), not just beating champion. Sharpens the entrenchment
  finding from "maybe search intensity would find something" to: **genuinely
  better challengers exist and keep turning up (~20% of holdout-tested
  candidates), the additive-over-one-lucky-draw margin is what keeps rejecting
  them, and more search does not fix this — it can only ever compound the same
  draw count the margin scales against.** Verified safe: `md5sum live_state.json
  evotrader.manifest` unchanged (`0fa0731311baab0508f959f79a01214e` /
  `0bf3a7d9411ee692d0a9f152a7533803`), `git status --short` clean throughout,
  no promotion (`final_version == 3`), today's bar already processed before this
  session, no double-trade. Also this session: local `main` diverged from
  `origin/main` again (expected artifact) — realigned with `git reset --hard
  origin/main`, no force-push, nothing lost. **Next**: this reads as a real
  design tension in `required_margin()`/`holdout_accepts()`, not a bug to patch
  casually — the margin is additive over the champion's own single noisy
  holdout draw rather than an absolute/percentile bar, so a lucky champion draw
  can entrench indefinitely. Two directions worth a full design session (not
  attempted here): (a) periodically refreshing the champion's own holdout score
  instead of anchoring to one historical draw forever, or (b) an
  absolute/percentile holdout bar instead of the additive margin. Either is a
  constitution amendment (checksummed, needs an `AMENDMENTS.md` row) and
  deserves more scrutiny than a 3-hourly session, given how central
  `holdout_accepts()` is to the promote-to-live-money safety story.

- **Shipped 2026-08-28 (3-hourly check, ~13:00 UTC): `guardian-gene-test --pct N`
  plus a required-margin print — the magnitude question the 09:45 UTC entry
  left open has an answer, and it's that the margin, not the magnitude, is
  the real constraint.** (see `runs/2026-08-28-1300-guardian-gene-test-pct-margin.md`)
  Added `--pct N` (default 50, byte-identical to the original halved
  behavior) so the Guardian-gene tightening magnitude is a parameter instead
  of hardcoded halving, plus a new print line computing
  `constitution.required_margin(holdout_draws_before + 1, 0,
  sigma=HOLDOUT_SIGMA)` directly — the table's own `holdout gate` column
  truncates `holdout_accepts()`'s reason string at 38 chars, which was
  hiding the actual margin number in every row of the 09:45 UTC table.
  **Finding**: `--pct 25` (milder than halving) against v3 is
  non-monotonic vs. the halved variants — stop-loss holds the holdout
  better (0.646 vs 0.476, now barely above champion's 0.644) but time-stop
  and combined do worse (-0.819/-0.896 vs 0.174/-0.676) — a real result,
  not noise, but irrelevant next to the margin: at 23 cumulative holdout
  draws, `HOLDOUT_SIGMA=2.0` sets the bar at champion + 5.008 = **5.652**.
  Every hand-picked variant tried across both sessions scores in the -0.9 to
  +0.6 range — the gap between 25%-tighter and halved (≤0.15 fitness
  points) is two orders of magnitude smaller than the gap to the actual
  bar. **No single-gene or few-gene hand-picked patch, at any magnitude,
  could plausibly clear this gate right now.** This sharpens the 09:45 UTC
  "lucky holdout draw entrenchment" hypothesis into something more precise:
  v3's own holdout draw (0.644) isn't an outlier — the multiple-testing
  correction itself, at the account's current cumulative draw count, demands
  more improvement than a hand-picked fold-tuning patch can plausibly
  produce. Verified safe: `py_compile` clean, `sync --check` clean
  (CLI-only), full suite 235 passed (163.93s, matches baseline),
  `git diff --stat` shows only `evotrader_bundle.py` touched (+36/-11),
  `live_state.json` md5 `0fa0731311baab0508f959f79a01214e` and
  `evotrader.manifest` md5 `0bf3a7d9411ee692d0a9f152a7533803` both unchanged
  across every run, today's bar already processed before this session (no
  double-trade), no genome promotion. Also this session: found local `main`
  behind a stale shallow-clone snapshot again (same expected artifact prior
  entries this cycle already named, confirmed no force-push) — realigned
  with `git reset --hard origin/main`, no force-push, nothing lost.
  **Next**: the only genuinely untried lever left is a real `evolve()`
  shadow search seeded from v3 with mutation weight toward the Guardian risk
  genes, run for enough generations that fold-aggregate selection compounds
  many candidates before any one reaches the (heavily-taxed) holdout gate —
  the same shape behind every real holdout-clearing promotion this project
  has seen (the 4h-shadow generation-N promotions in
  `runs/2026-08-1{6,7}-*`). A multi-generation, time-boxed exercise for a
  future session, not a single-invocation diagnostic.

- **Shipped 2026-08-28 (3-hourly check, ~09:45 UTC): `guardian-gene-test
  [--also-version N]` — the fold-3-mechanism fix `fold3-anatomy`'s own
  trailing note named as the real next step, and the first Guardian-gene
  patch to actually clear the fold-aggregate gate on 3 champions at once.**
  (see `runs/2026-08-28-0945-guardian-gene-test.md`) `fold3-anatomy` found
  fold 3's worst trades exit via Guardian's *mechanical* stop-loss/trailing
  stop/time stop, never a discretionary consult; `exit-gene-test` confirmed
  patching the discretionary exit can't touch fold 3. This new diagnostic
  builds real `Genome.child()` patches to the actual genes that fire there
  (`risk.stop_loss`, `risk.trailing_stop`, `risk.max_bars_held`), each
  halved in magnitude relative to whichever champion is under test (clamped
  to `agents.researcher.GENE_SPACE`'s bounds), through the identical
  acceptance-gate machinery `exit-gene-test` used. **Finding**: 11 of 12
  variant/champion combinations (v1/v2/v3, 4 variants each) clear the
  fold-aggregate gate — gate max_dd drops from -46.8%/-45.3%/-41.8% down to
  as low as -29.5%-38.3%, well past the -40% `MAX_DD_HARD_FAIL` line, the
  first time any gene patch tried in this thread has cleared it at all.
  **Every one still fails the sealed holdout**, several by a wide margin —
  same "clears fold gate, loses at holdout" shape `exit-gene-test` found
  once for v2; now reproduced 11 times with a structurally different,
  correctly-targeted patch. Verified safe: `py_compile` clean, `sync
  --check` clean (CLI-only, no `_SRC` module touched), full suite 235
  passed (134.02s, matches baseline), `git diff --stat` shows only
  `evotrader_bundle.py` touched (+180 lines), `live_state.json` md5
  `0fa0731311baab0508f959f79a01214e` and `evotrader.manifest` md5
  `0bf3a7d9411ee692d0a9f152a7533803` both unchanged across all three
  `--also-version` runs, today's bar already processed before this session
  (no double-trade), no genome promotion. Also this session: found local
  `main` behind a stale shallow-clone snapshot again (same expected
  artifact prior entries this cycle already named) — realigned with `git
  reset --hard origin/main`, no force-push, nothing lost. **Next**: whether
  a smaller (not halved) tightening trades away less upside and holds the
  holdout, or whether this is the same lucky-holdout-draw entrenchment
  `holdout-pressure`/2026-08-18 already documented for discretionary
  changes now showing up for mechanical ones too — in which case the real
  test is a genuine `evolve()` search seeded in this gene sub-space, not
  more hand-picked single patches. See run note for the full 12-row table.

- **Shipped 2026-08-28 (3-hourly check, ~06:56 UTC): `exit-gene-test
  --also-version N` — wires the researcher_memory limitation the 00:56/04:04
  UTC entries both flagged, and turns up the first fold-gate clear either
  exit-gene variant has ever gotten.** (see `runs/2026-08-28-0656-exit-gene-test-also-version.md`)
  Refactored `exit-gene-test` to loop over a `champions` list (live champion
  plus an optional `_reconstruct_champion_genome(also_version, ...)` entry,
  the same pattern every other `--also-version` diagnostic here already
  uses) instead of a single hardcoded `g0`. `live_state.json`'s
  `researcher_memory` only ever holds cumulative counts for whichever
  version is champion *right now* (reset on every promotion), so a
  reconstructed past champion always takes the `n_tested_before=0`/
  `holdout_draws_before=0` branch the command already had for a
  champion_version mismatch — documented explicitly in the code and the
  command's own trailing explanation as an optimistic upper bound, not a
  replay of that version's real historical margin. Ran against v1 and v2:
  v1 rejects the same way v3 does (both candidates hard-fail the dd-corrected
  drawdown gate before ever reaching a champion comparison, fold-agg fitness
  -2.959/-2.832 vs its own -2.787). **v2 is the first champion where a
  candidate clears the fold gate at all**: "narrower exit (harder to
  trigger)" scores -0.129 against v2's own -2.575 fold-agg fitness — a real
  champion-relative pass, unlike v1/v3's immediate hard-gate rejection — but
  then fails the sealed holdout (-1.301, well short of what
  `holdout_accepts()` requires). Net: three real champions now checked, and
  every one still rejects both variants, but for two structurally different
  reasons (v1/v3: challenger itself hard-fails the drawdown gate before any
  comparison; v2: challenger clears the fold gate and loses at the holdout
  instead) — the "let search decide" question from exit-role-test's own
  next-step note is now answered with real per-champion gate data on all
  three, not just the live one. Verified safe: `py_compile` clean,
  `tools/edit_bundle_module.py sync --check` clean (CLI-only code, no `_SRC`
  module touched), full suite 235 passed (127.06s, matches baseline, no new
  pure function so no new test file), `git diff --stat` shows only
  `evotrader_bundle.py` touched, `live_state.json` md5
  `0fa0731311baab0508f959f79a01214e` and `evotrader.manifest` md5
  `0bf3a7d9411ee692d0a9f152a7533803` both unchanged before and after every
  run, today's bar already processed before this session (no double-trade,
  confirmed via `live_state.json`'s `updated` timestamp and `runs/`), no
  genome promotion. Also this session: found local `main` behind a stale
  shallow-clone snapshot of `origin/main` again (same expected artifact the
  00:56/04:04 UTC entries already named, confirmed via `git rev-parse
  --is-shallow-repository` and `git merge-base --all` returning no common
  ancestor within the shallow window, not a force-push) — realigned with
  `git reset --hard origin/main` per the Run protocol, no force-push,
  nothing lost. **Next**: fold 3's drawdown mechanism (Guardian's mechanical
  stop-loss/time-stop and the circuit breaker, not any discretionary
  consult) is still the open thread from the 04:04 UTC entry — a real fix
  would target those mechanisms directly; separately, v2's fold-gate clear
  is one data point on one champion, not validated against whether a
  genuinely evolved (not hand-patched) `exit_trend_below`/`exit_rsi` value
  could do better against v2 specifically, which `evolve` itself would be
  needed to check.

- **Shipped 2026-08-28 (3-hourly check, ~04:04 UTC): `fold3-anatomy` — the
  fold-3-scoped drawdown pass the 00:56 UTC entry flagged, and it clears up
  which of two problems the exit gene actually is (and isn't).** (see
  `runs/2026-08-28-0404-fold3-anatomy.md`) New read-only diagnostic; caught
  and fixed a real bug in its own first draft before shipping: `dd_corrected_
  stats()` takes `min(fold-merged, continuous)`, and this diagnostic first
  assumed continuous always binds — checking directly showed the opposite for
  both champion v3 and the "no discretionary exit" candidate, where
  fold-merged (driven entirely by fold 3's own independently-reset replay) is
  the more negative, binding number. The continuous-only version would have
  wrongly reported the candidate at -34.7% (clearing the gate); the real,
  fixed version reproduces exit-gene-test's own -46.80%/-45.76% exactly.
  **Finding**: fold 3's own replay's 10 worst closed trades are virtually
  identical between champion and the exit-suppressed candidate (same
  symbols, same dates, same P&L) — every one exits via Guardian's mechanical
  stop-loss, time-stop, or the circuit breaker, none via `consult_moderate`'s
  own discretionary sell. Suppressing that exit therefore can't touch these
  positions at all, which is exactly why it only buys ~1 point of depth
  (-46.8% → -45.8%) against a ~7-point gap to clear 0.40. **The exit-gene
  finding and fold 3's hard-fail are two different problems that share a
  champion, not the same lever restated.** Verified safe: `py_compile` clean,
  `tools/edit_bundle_module.py sync --check` clean (CLI-only code, no `_SRC`
  module touched), full suite 235 passed (210.06s, no new pure function so no
  new test file), `git diff --stat` shows only `evotrader_bundle.py` touched
  (+127 lines), `live_state.json` md5 `0fa0731311baab0508f959f79a01214e` and
  `evotrader.manifest` md5 `0bf3a7d9411ee692d0a9f152a7533803` both unchanged,
  today's bar already processed before this session (no double-trade), no
  genome promotion. Also this session: found local `main` behind a stale
  shallow-clone snapshot of `origin/main`; confirmed via `git rev-parse
  --is-shallow-repository` this was the expected shallow-clone-window
  artifact (not a force-push/history-rewrite), working tree clean, realigned
  with `git reset --hard origin/main`, no force-push, nothing lost. **Next**:
  fold 3's drawdown is driven by Guardian's mechanical stop-loss/time-stop
  and one circuit-breaker flatten across a cluster of positions, not by any
  discretionary consult — a real fix would have to target those mechanisms
  (thresholds, sizing, correlation limits) or accept v3 is structurally
  exposed on this window; genuinely untried, and possibly a different
  regression than the ones `fold-dd-blindspot`/`succession-audit` already
  track. Separately, `exit-gene-test --also-version N` against v1/v2 is still
  unwired (researcher_memory lookup only supports the live champion).

- **Shipped 2026-08-28 (3-hourly check, ~00:56 UTC): `exit-gene-test` — the
  real gene patch + real acceptance-gate check the 21:48 UTC entry flagged,
  and it rejects both candidates for a reason nobody had checked yet.** (see
  `runs/2026-08-28-0056-exit-gene-test.md`) New diagnostic replaces
  exit-role-test's monkeypatch with two actual `Genome.child()` patches on
  `consult_moderate` ("no discretionary exit": `exit_trend_below=-1.0`,
  `exit_rsi=999`; "narrower exit": `exit_trend_below=-0.05`, `exit_rsi=90`),
  run through the exact machinery `EvolutionRun.generation()` uses for a
  real top-3 candidate — `Evaluator.evaluate()`, `dd_corrected_stats()`,
  `constitution.accepts()`, then (only for whichever clears that gate)
  `constitution.holdout_accepts()` — using champion v3's real cumulative
  `researcher_memory` counts (224 tested, 22 holdout draws) for the margin.
  **Both candidates rejected, and not by losing to the champion**: fold 3
  (`[0.567, 0.85]`, the same fold the fold-dd-blindspot/succession-audit
  thread already named) hard-fails `MAX_DD_HARD_FAIL` (0.40) for the
  champion (-46.80% dd-corrected max_dd) *and* for both candidates (-45.76%
  for "no discretionary exit" — real improvement, ~1 point, nowhere near
  enough). `constitution.accepts()`'s very first check
  (`fitness(challenger) == -inf`) rejects before ever comparing to the
  champion, before the multiple-testing margin, before the holdout. A
  different failure mode than the `vacuous-regression-check` pattern item 2
  has tracked since 2026-08-22 (there the *champion's* -inf fitness makes a
  later comparison vacuous; here the *challenger* itself hard-fails first).
  Net: exit-role-test's full-history-replay win (fitness -inf → 0.659) does
  not survive contact with the fold-merged, dd-corrected metric the real
  gate scores on — "let search decide" cannot decide anything for either of
  these two specific gene values, because neither ever reaches a
  champion-relative comparison. Verified safe: `py_compile` clean,
  `tools/edit_bundle_module.py sync --check` clean (CLI-only code, no `_SRC`
  module touched), full suite 235 passed (136.08s, matches baseline, no new
  pure function so no new test file), `git diff --stat` shows only
  `evotrader_bundle.py` touched (+150 lines), `live_state.json` md5
  `0fa0731311baab0508f959f79a01214e` and `evotrader.manifest` md5
  `0bf3a7d9411ee692d0a9f152a7533803` both unchanged, today's bar already
  processed before this session (no double-trade), no genome promotion.
  Also this session: found local `main` stuck at a stale 2026-08-22
  shallow-clone snapshot while `origin/main` had genuinely advanced to
  today's daily-trading commit — confirmed the local work was already
  upstream, working tree clean, realigned with `git checkout -B main
  origin/main`, no force-push, nothing lost. **Next**: whether a fold-3-
  specific fix (not this exit gene) is what's actually needed before any
  candidate can clear v3's real gate right now — needs a `drawdown`/
  `anatomy` pass scoped to fold 3's window, genuinely untried. Separately,
  `exit-gene-test --also-version N` against v1/v2 (neither known to
  hard-fail fold 3 the way v3 does) would show whether this gene idea
  clears the real gate against a less drawdown-marginal champion — the
  diagnostic doesn't support `--also-version` yet (researcher_memory lookup
  is only wired for the live champion).

- **Checked 2026-08-27 (3-hourly check, ~21:48 UTC): `exit-role-test` against
  v1 — third data point closes the risky-exit genome-dependence question.**
  (see `runs/2026-08-27-2148-exit-role-test-v1.md`) Ran the 18:54 UTC entry's
  flagged next step, `exit-role-test --also-version 1`. `consult_moderate`
  exit suppression now confirmed to help all 3/3 real champions (v1
  -inf→0.112, v2 0.169→0.396, v3 -inf→0.659) — the safe, generalizing target
  for a real gene change, as the 18:54 UTC entry already concluded.
  `consult_risky` exit suppression is now a confirmed **three-way split**
  with no consistent sign: strongly helps v1 (-inf→0.379, its single best
  lever), hurts v2 (0.169→-inf, maxDD to -43.4%), no-op on v3 (live).
  Reinforces rather than changes the scoping conclusion: any real gene
  change must target `consult_moderate`'s exit only, never bundle in
  `consult_risky`. Verified safe: read-only, `git status` clean throughout,
  `live_state.json` md5 `1add861014e44aa69e814491cbd22e00` and
  `evotrader.manifest` md5 `0bf3a7d9411ee692d0a9f152a7533803` both
  unchanged, today's bar already processed before this session (no
  double-trade), no genome promotion. **Next**: the actual
  `consult_moderate`-only exit-threshold gene sketch (narrower
  `exit_trend_below`/`exit_rsi` range, or a "no discretionary exit" variant)
  plus shadow-`evolve` validation against the unmodified champion — still
  genuinely untried, no code sketched, bigger scope than one 3-hourly slot,
  now with all three champions' exit-role data in hand to design against.

- **Shipped 2026-08-27 (3-hourly check, ~18:54 UTC): `exit-role-test`,
  quantifying the exit-mechanism finding by suppressing the discretionary
  exit outright.** (see `runs/2026-08-27-1854-exit-role-test.md`) New
  read-only diagnostic (same monkeypatch-and-restore precedent as
  `consult-role-test`): suppresses `consult_moderate`'s and
  `consult_risky`'s own sell intents (buy rule untouched) so any position
  they'd have sold instead rides until Guardian's unconditional mechanical
  exit catches it, and reports the full-history backtest delta. This was the
  cheap first slice of the 15:49 UTC entry's flagged next step (a real
  gene/threshold change + shadow evolve, explicitly bigger than one slot).
  **Result on v3 (live)**: suppressing `consult_moderate`'s exit alone flips
  the champion from a hard-DD-gate failure (-46.5% maxDD, fitness -inf) to
  fitness 0.659 (+190.3% excess vs benchmark, vs baseline's +90.1%) — the
  strongest single lever this thread has found. Suppressing `consult_risky`'s
  exit alone is a complete no-op on v3 (every stat identical to baseline).
  **Checked against v2 too**: `consult_moderate` suppression helps there as
  well (0.169 → 0.396), confirming it generalizes across the two champions
  checked — but `consult_risky` suppression is the *opposite* of v3: it
  actively hurts v2 (fitness 0.169 → -inf, maxDD to -43.4%). Same
  "search already corrected it for this specific champion, don't assume it
  generalizes" shape as the closed 2026-08-23 `consult-role-test` finding on
  `consult_conservative`'s entries. **Narrows the original scope**: any real
  gene change should target `consult_moderate`'s exit threshold only —
  `consult_risky`'s exit does not belong in the same change given the v2/v3
  disagreement. Verified safe: `py_compile` clean, `tools/edit_bundle_module.py
  sync --check` clean (CLI-only code, no `_SRC` module touched), full suite
  235 passed (136.14s, matches baseline, no new pure function so no new test
  file), `git diff --stat` shows only `evotrader_bundle.py` touched (+111
  lines), `live_state.json` md5 `1add861014e44aa69e814491cbd22e00` and
  `evotrader.manifest` md5 `0bf3a7d9411ee692d0a9f152a7533803` both unchanged,
  today's bar already processed before this session (no double-trade), no
  genome promotion. **Next**: check v1 with `--also-version 1` for a third
  data point on the risky-genome-dependence question, then sketch the actual
  `consult_moderate` exit-threshold gene change (narrower
  `exit_trend_below`/`exit_rsi` range, or a "no discretionary exit" variant)
  and validate with a shadow `evolve` run against the unmodified champion on
  the same folds — still genuinely untried, no gene code sketched, likely
  another full slot given real-evolve cost.

- **Checked 2026-08-27 (3-hourly check, ~15:49 UTC): window-4 anatomy —
  exit-mechanism pattern now confirmed 3/3 independent windows.** (see
  `runs/2026-08-27-1549-history-perturb-window4-anatomy.md`) Ran
  `history-perturb --independent --anatomy --sub-slice-window 4`, the third
  window this thread named as the one to check for replication. Window 4
  (2022-08-27 to 2024-08-27, 497 trades) is a mixed case — +129.6% absolute
  return but -5.5% excess vs a +135.2% benchmark (`beat_bench: false`),
  neither window 3's clean net win nor window 5's outright loss. Same
  exit-mechanism ranking shows up again: `circuit_breaker` -$3,668/15 (7%
  win), `consult_risky` -$2,322/107 (32% win), `consult_moderate` -$2,173/159
  (40% win) all lose; `consult_conservative` +$1,733/22 (95% win) and
  `guardian` +$20,784/194 (52% win) both profit. **Now 3/3 independent
  2-year windows (3, 4, 5) agree**, across three different outcome shapes
  (net winner, mixed, net loser) and three different regime compositions —
  the strongest evidence yet that discretionary consult exits
  (`consult_moderate`/`consult_risky`/`circuit_breaker`) underperforming
  mechanical exits (`guardian`/`consult_conservative`) is a structural
  property of the current genome's exit logic, not a regime artifact.
  Holding-period stays dropped as a lead: 6-20 bars is profitable here too
  (+$10,649/302, matching window 3), 2/3 windows now disagree with window
  5's negative reading. Regime sign also doesn't hold a consistent
  direction across windows (window 4's `bear` bucket is profitable, unlike
  window 5's) — read as window-specific, not general. Verified safe:
  read-only, no code needed (the `--anatomy` flag already existed from the
  09:56 UTC entry), `git status` clean, `live_state.json` md5
  `1add861014e44aa69e814491cbd22e00` and `evotrader.manifest` md5
  `0bf3a7d9411ee692d0a9f152a7533803` both unchanged, today's bar already
  processed before this session (no double-trade), no genome promotion.
  **Next**: with 3/3 windows agreeing, the higher-value move is no longer
  another read-only window check (1 and 2 remain, if wanted) but attempting
  the actual gene/threshold sketch — tightening
  `consult_moderate`/`consult_risky`'s exit conditions toward `guardian`-
  style mechanical stops, validated with a shadow `evolve` run against the
  unmodified champion on the same folds — genuinely untried, no code
  sketched, needs to preserve these same consults' flat-to-positive entry
  role. Bigger scope than one 3-hourly slot; flagged for whoever picks it
  up next.

- **Checked 2026-08-27 (3-hourly check, ~12:54 UTC): window-3 anatomy —
  exit-mechanism pattern replicates, holding-period pattern doesn't.** (see
  `runs/2026-08-27-1254-history-perturb-window3-anatomy.md`) Ran the same
  `history-perturb --independent --anatomy --sub-slice-window 3` the 09:56
  UTC entry flagged as the next check. Window 3 (2020-08-27 to 2022-08-27,
  554 trades) is net **profitable** (+527.2% vs benchmark +303.8%, unlike
  window 5's net loss), but the same exit-mechanism split shows up:
  `consult_moderate`/`consult_risky`/`circuit_breaker` exits all lose money
  (-$15,026/-$4,956/-$4,561) while `guardian`/`consult_conservative` exits
  both profit heavily (+$77,883/+$4,031) — same ranking as window 5, now
  confirmed on a second, opposite-regime window. **Does not replicate**:
  window 5's "6-20 bar holds are the only negative holding-period bucket"
  finding — here that same bucket is the second-most profitable
  (+$29,557/320), so that claim was window-5-specific, not a general
  holding-period defect; drop it as a lead. Reading: the exit-mechanism
  ranking now looks like a real, regime-independent property of the current
  genome's exit logic (2/2 windows checked), worth a third window (1, 2, or
  4) before calling it universal, and eventually a real gene/threshold
  proposal for `consult_moderate`/`consult_risky` exits — still untried,
  no code sketched, would need a real `evolve` run to validate net of those
  same consults' flat-to-positive entry role. Verified safe: read-only, no
  code/state/constitution touched, `live_state.json` md5
  `1add861014e44aa69e814491cbd22e00` and `evotrader.manifest` md5
  `0bf3a7d9411ee692d0a9f152a7533803` both unchanged, today's bar already
  processed before this session (no double-trade), no genome promotion.
  Also noted in passing: `history-perturb --help` isn't a real flag (no
  argparse help handler) and silently runs the default nested-years mode
  instead of erroring — harmless (still read-only) but worth a one-line fix
  someday, not chased this session.

- **Shipped 2026-08-27 (3-hourly check, ~09:56 UTC): `history-perturb
  --independent --anatomy`, the window-5 per-trade post-mortem flagged open
  since the 2026-08-26 09:50 UTC entry.** (see
  `runs/2026-08-27-0956-history-perturb-window5-anatomy.md`) New
  `--anatomy [--sub-slice-window I]` flag, same precedent as
  `--sub-slice`/`--drawdown`/`--boundary-shift` (reuses already-tested
  `trade_anatomy` and `run_backtest`, no engine/constitution change, CLI-only
  code so `tools/edit_bundle_module.py sync --check` stays a no-op). Result
  on window 5 (2024-08-26 to 2026-08-27, 483 trades, -6.1% vs benchmark
  +70.2%): **entries are not the problem in this window** — all three
  consults' entry attribution is flat-to-positive — the loss concentrates in
  **exits**: `consult_moderate`'s own exit call is the single largest loss
  category (-$2,760/126 trades, 33% win), `circuit_breaker` second (-$2,463/
  17 trades, 12% win, worst per-trade EV on the table), `consult_risky`
  third (-$1,615/144, 15% win) — while the *mechanical* exits are strongly
  profitable: `guardian` (stop-loss/take-profit/time-stop) is the best
  category overall (+$4,960/176, 41% win), `consult_conservative`'s exit
  role (already known system-wide, re-confirmed here at n=20) is second-best
  (+$1,078, 90% win). Cuts the same way by holding period: 6-20 bar holds
  (58% of all trades) are the only structurally negative bucket (-$3,734),
  quick exits (1 bar, 2-5 bars) are both positive. 335/483 trades (69%) are
  tagged `bear` and that bucket alone is -$2,623, more than the window's net
  loss — reads as a genuinely harder regime, not a fixed defect, consistent
  with the 2026-08-25 21:55 UTC regime characterization of this same window.
  **One window, not yet a pattern**: this window was already flagged noisy
  (the 2026-08-26 00:59 UTC boundary-shift entry flipped its verdict with a
  1-day shift), so "discretionary consult exits underperform mechanical
  exits in a bear-heavy window" is this session's read of one draw, not a
  confirmed mechanism — needs checking against another regime-mixed window
  (e.g. window 3) before it's treated as real. Also this session: found
  local `main` had diverged from `origin/main` (stale detached-HEAD checkout
  from a prior session's clone, not new work) — resolved per this file's own
  run-protocol rule 2, `git reset --hard origin/main`, no force-push, nothing
  lost. Verified safe: `py_compile` clean, `tools/edit_bundle_module.py sync
  --check` clean, full suite 235 passed (125.68s, matches baseline, no new
  pure function so no new test file), `git diff --stat` shows only
  `evotrader_bundle.py` touched, `live_state.json` md5
  `1add861014e44aa69e814491cbd22e00` unchanged (still tick 13, today's bar
  already processed by the 00:20 UTC daily run, no double-trade),
  `evotrader.manifest` md5 `0bf3a7d9411ee692d0a9f152a7533803` unchanged,
  constitution verified `8b74865634b1db07` unchanged, no genome promotion (no
  README Status change needed, no dashboard rebuild needed). **Next, if this
  thread stays worth pursuing**: re-run `--anatomy` on window 3 (also
  regime-mixed) to see whether the exit-mechanism pattern replicates or is
  window-5-specific; if it replicates, whether tightening
  `consult_moderate`/`consult_risky`'s own exit thresholds is worth
  proposing as an actual gene change is genuinely untried, no code sketched.
  The day-1-allocation-redesign question from the same 09:50 UTC entry is
  still open and untouched by this session.

- **Closed 2026-08-27 (3-hourly check, ~06:48 UTC): the lineage-age
  holdout-margin question the 04:05 UTC entry left open — answered with data
  already on hand, no new generations run.** (see
  `runs/2026-08-27-0648-holdout-margin-never-binding-lineage-age-answer.md`)
  Used two existing read-only diagnostics (`margin-curve`, `holdout-pressure`)
  plus arithmetic: `holdout-pressure` lists all 12 real sealed-holdout draws
  against live champion v3 since promotion, spanning `n_draws=2` (this
  lineage's youngest-ever draw, margin only 0.094) through `n_draws=13`
  (today, margin 4.530). Computed the raw (unmargined) holdout diff
  (`challenger_holdout - champion_holdout`) for all 12: **never once
  positive, including at `n_draws=2`** — every real rejection would have
  happened at any margin, including zero. The margin has never actually been
  the deciding factor in a real promotion attempt against v3, young lineage
  or old; every case was decided by the raw holdout comparison itself
  (6 of the 12 draws tied the champion's holdout score to three decimals,
  the closest this lineage has come — still not a win). Combined with the
  fold-date-flip thread's 19/19 rejections (all decisively bad on holdout,
  closest gap 20x under margin), this closes the specific lineage-age
  question: further probing of the margin's calibration is low-value given
  it has never bound; the open question that remains is about challenger
  quality (does any real search draw ever produce a holdout score genuinely
  better than the champion's), not margin size, and that can only be
  answered by future real search, not more re-derivation of existing data.
  Verified safe: no code changed, only two existing read-only CLI commands
  run; `live_state.json` md5 `1add861014e44aa69e814491cbd22e00` unchanged
  (still tick 13), `evotrader.manifest` md5 `0bf3a7d9411ee692d0a9f152a7533803`
  unchanged, `tools/edit_bundle_module.py sync --check` clean, today's bar
  already processed before this session started (no double-trade), no
  genome promotion.

- **Confirmed 2026-08-27 (3-hourly check, ~04:05 UTC): stress-tested the
  holdout backstop with a much larger sample — 15 more flip candidates
  across 6 real generations, all rejected, closest gap 20x under the
  margin.** (see
  `runs/2026-08-27-0405-fold-date-flip-holdout-backstop-stress-test.md`)
  Picked up the 00:52 UTC entry's open item directly: same method, extended
  to 6 consecutive real generations (real `researcher_memory` resumed — 182
  tested, stagnation 12, holdout_draws 13 — real `Researcher.propose`/
  `Evaluator.evaluate`, `n_blind=14`, exclude accumulated across
  generations). Found 15 flip candidates (2-3 per generation); **all 15
  failed the sealed holdout**, closest gap (champion holdout 0.176 vs
  challenger -0.054) still needing to clear a 4.595 margin it came nowhere
  near. Combined with the 21:52 UTC and 00:52 UTC entries: 19/19 flip
  candidates checked across three independent sessions have now failed the
  holdout decisively, none a real close call. Reading: the stress test this
  thread was building toward is answered for the current lineage state (14
  cumulative holdout draws) — the backstop isn't just holding by luck on a
  couple of draws, a 15-candidate sample found nothing that approached the
  margin either. Caught and fixed a real bug before this counted as a real
  run: an early draft called `LiveAccount.load()` with no path argument,
  which resolves to `core.live.STATE_PATH` (a nonexistent
  `state/live/account.json`, not this repo's `live_state.json`), silently
  falling back to the seed genome v1 instead of live champion v3 — caught by
  a 1-generation sanity check before the real 6-generation batch ran. Still
  open, unresolved by a larger sample at the same draw count: what the
  margin looks like for a lineage with few or zero accumulated holdout
  draws (right after a promotion), where the margin would be roughly half
  today's — this thread has only ever tested v3's current, well-aged draw
  count. Verified safe: no code changed (script lives only in session
  scratch space), `live_state.json` md5 `1add861014e44aa69e814491cbd22e00`
  unchanged (still tick 13), `evotrader.manifest` md5
  `0bf3a7d9411ee692d0a9f152a7533803` unchanged, `tools/edit_bundle_module.py
  sync --check` clean, today's bar already processed before this session
  started (no double-trade), no genome promotion. **Given 19/19 rejections
  and a 20x-margin gap on the closest case, recommend against another
  identical-method batch** — the sharper remaining question is the
  lineage-age one above, not more samples at the current draw count.

- **Found 2026-08-27 (3-hourly check, ~00:52 UTC): flipped fold-aggregate
  candidates fail the sealed holdout anyway — the holdout gate backstops the
  date-sensitivity, at least on the two draws checked so far.** (see
  `runs/2026-08-27-0052-fold-date-flip-holdout-backstop.md`) Picked up both
  open items from the 21:52 UTC entry: ran a second, fresh real generation's
  worth of work (real `researcher_memory` resumed — 182 already-tested
  proposals excluded against v3, stagnation 12, holdout_draws 13, real
  `Researcher.propose`/`Evaluator.evaluate`, `n_blind=14`, 14 fresh
  proposals, 196 cumulative). **Open item 1 (does the flip reproduce on a
  different batch): yes** — 2 of 3 top candidates flip again (same 2-of-3
  ratio, different specific candidates), both ACCEPT only at the same
  anomalous shift-1 day (as-of 2026-08-26, champion fold-aggregate -1.652)
  and reject at the other 6 shifts. **Open item 2 (does a flipped candidate
  actually pass the sealed holdout on its accept-verdict day): no** — built
  the real shifted "as-of" market window and called the real
  `Evaluator.holdout_check()` for both flip candidates at their accept-verdict
  shift; both fail decisively (challenger -0.259 and -0.373 vs champion 0.176
  + margin 4.595, driven by 14 cumulative holdout draws against this specific
  window). Reading: the two gates aren't independent in the way that matters
  here — the sealed holdout's own accumulated-draws multiple-testing margin
  is currently strong enough to catch what the fold-aggregate gate's
  date-sensitivity would have let through, at least for these two (both
  genuinely weak, not close-call) candidates. Important caveat: this margin
  is itself a function of how many holdout draws this lineage has already
  spent (14 here) — a younger lineage would have less protection from
  exactly this mechanism, and neither flip candidate checked so far was a
  close call on the holdout, so the backstop's actual margin under a close
  call is still untested. Verified safe: no code changed (script lives only
  in session scratch space, never touches any committed file, never calls
  `Genome.promote()` or `acct.save()`, so no test suite run needed),
  `live_state.json` untouched (md5 `1add861014e44aa69e814491cbd22e00`
  unchanged, still tick 13 from the 00:20 UTC daily run), `evotrader.manifest`
  md5 unchanged (`0bf3a7d9411ee692d0a9f152a7533803`), `tools/
  edit_bundle_module.py sync --check` reports no drift, today's bar already
  processed before this session started (no double-trade), no genome
  promotion (no README Status change needed). **Next, if this thread stays
  worth pursuing**: the stress-test case — keep drawing generations until a
  flip candidate's holdout fitness lands close to the champion's, to see
  whether the margin still holds or a close call gets through; whether
  smoothing the champion's fold-aggregate baseline is still worth doing given
  this backstop (weaker case now, not zero); the day-1-allocation-redesign
  question and window-5 `anatomy` post-mortem from the 09:50 UTC (2026-08-26)
  entry, still open and untouched by this thread.

- **Confirmed 2026-08-26 (3-hourly check, ~21:52 UTC): the champion-score swing
  flips a real accept/reject verdict — confirmed, not hypothetical.** (see
  `runs/2026-08-26-2152-fold-date-sensitivity-verdict-flip.md`) Picked up the
  sharpest open item from the 12:57 UTC entry directly: ran one real
  generation's worth of work (real `researcher_memory` resumed — 182
  already-tested proposals excluded against v3, stagnation 12, holdout_draws
  13 — real `Researcher.propose`/`Evaluator.evaluate`, `n_blind=14`, 14 fresh
  proposals, 196 cumulative), then re-ran `accepts()` on the top-3 real
  candidates swapping only `champion_score` for the 7 values the 12:57 UTC
  `fold-date-sensitivity --shift 7` run already measured. Result: 2 of the 3
  top candidates (fold-aggregate fitness 1.2371 and 1.2067, both real 8-gene
  blind-search patches) flip — ACCEPT the fold-aggregate gate on 3 of 7
  measured champion-score days (shifts 0/1/3) and reject on the other 4
  (2/4/5/6), with nothing about either candidate changing, only the champion
  baseline it's compared against. The third candidate hard-fails a gate on
  every shift and never reaches the comparison at all — not every candidate
  is shift-sensitive, only ones close to the champion's own swing range.
  Scope limit: "ACCEPT" here means clearing `accepts()`, the fold-aggregate
  gate only — the sealed holdout is a separate, independent, already-
  characterized second gate this experiment didn't re-run per shift, so this
  doesn't claim either candidate would actually promote, only that which
  candidates even reach the holdout gate depends on the calendar day
  `evolve` happens to run. Verified safe: no code changed in the repo (script
  lives only in session scratch space, never touches any committed file, so
  no test suite run needed), `live_state.json` untouched (md5
  `1441d25f45fb4a927f993cbc8c505a5b`, unchanged from the 18:51 UTC entry,
  still tick 12 from the 00:20 UTC daily run — script never calls
  `acct.save()`), `evotrader.manifest` md5 unchanged
  (`0bf3a7d9411ee692d0a9f152a7533803`), today's bar already processed before
  this session started (no double-trade), no genome promotion (no README
  Status change needed). **Next, if this thread stays worth pursuing**:
  whether the same flip pattern holds against a different proposal batch
  (this was one draw); whether a flipped candidate that reaches the holdout
  gate on an accept-verdict day would actually pass the sealed holdout too
  (not attempted — would need to actually run `holdout_check`); whether
  smoothing the champion's fold-aggregate baseline across several as-of
  dates would reduce the flip rate — untried design work, would need its
  own `AMENDMENTS.md` row if pursued; the day-1-allocation-redesign question
  and window-5 `anatomy` post-mortem from the 09:50 UTC entry, still open.

- **Confirmed 2026-08-26 (3-hourly check, ~18:51 UTC): the fold-date-sensitivity
  swing the 12:57 UTC entry found is not v3-specific — v1 and v2 show the
  same order-of-magnitude spread, and hard-fail more often.** (see
  `runs/2026-08-26-1851-fold-date-sensitivity-also-version.md`) Ran
  `fold-date-sensitivity --also-version 2` and `--also-version 1` (existing
  CLI flag, no code change). Aggregate-fitness spread across the same 7-day
  shift window: v3 (live) 3.132 (1/7 shifts hard-fail a fold at
  `RANK_FLOOR`), v2 2.814 (4/7 hard-fail), v1 3.161 (3/7 hard-fail). Answers
  the open item directly: this is a property of the day-1 greedy-allocation
  mechanism itself (the same one the 06:55/09:50 UTC boundary-shift entries
  traced), not an artifact of v3's specific parameters — checking all three
  live-lineage genomes turns the one-genome finding into a general one, same
  pattern as the unrelated selection-noise thread's second/third-genome
  checks. Verified safe: no code changed, so no test suite run (same
  precedent as prior no-code-change diagnostic sessions), `live_state.json`
  untouched (md5 `1441d25f45fb4a927f993cbc8c505a5b`, still tick 12 from the
  00:20 UTC daily run), `evotrader.manifest` md5 unchanged, `tools/
  edit_bundle_module.py sync --check` reports no drift, constitution
  verified `8b74865634b1db07` unchanged, today's bar already processed
  before this session started (no double-trade), no genome promotion (no
  README Status change needed). **Next, if this thread stays worth
  pursuing**: whether this measurably flips any real accept/reject verdict
  in practice (replay a real historical generation's candidate batch against
  the champion re-evaluated at a different shift — needs a `Researcher`
  batch, not just re-evaluating the champion, a bigger next session); the
  day-1-allocation-redesign question (proportional/ranked instead of
  greedy-first-come), still untried design work; the window-5 `anatomy`
  post-mortem, also still open.

- **Resolved 2026-08-26 (3-hourly check, ~12:57 UTC): the 09:50 UTC framing
  question — answered, and not the way "backtest-evaluation artifact, not a
  live-trading risk" would have hoped. The real `evolve()` fold-aggregate
  fitness is date-sensitive too, and it directly moves the bar every
  challenger must clear.** (see "Next steps" item 2 history and
  `runs/2026-08-26-1257-fold-date-sensitivity.md`) New `fold-date-sensitivity
  [--shift N] [--also-version N]` re-evaluates a champion under the exact
  same `loop.evolve.Evaluator(data, n_folds=N_FOLDS).evaluate(genome)` call
  `evolve` makes internally (not `history-perturb`'s own hand-rolled sweep),
  at several different "as-of" dates. Result against live champion v3,
  `--shift 7`: `aggregate_fitness` ranges [-1.652, +1.480] (spread 3.13)
  across 7 consecutive days, and fold 3 hard-fails outright (`-5.000` =
  `RANK_FLOOR`) specifically on today's date while scoring 0.03-1.21 on the
  other six days. Ruled out a partial-forming-bar confound first (today's
  still-forming daily candle, verified present via its low volume, changes
  nothing when dropped before evaluation — identical result to 5 decimals) —
  this is the same day-1 greedy-allocation mechanism the 06:55/09:50 UTC
  entries traced, now confirmed against the real fold scheme. Then read
  `loop.evolve.EvolutionRun.generation()` directly: `champ_fit =
  self.evaluator.evaluate(champion)["aggregate_fitness"]` is computed fresh
  every real `generation()` call and passed straight into `accepts()` as
  `champion_score` — never read from `live_state.json`'s stored
  promotion-time fitness. So this date-sensitivity isn't a side-channel
  curiosity: it directly changes the bar every challenger's fold-aggregate
  fitness is compared against on whatever day `evolve` happens to run.
  Verified safe: full suite 235 passed (133.12s, matches baseline, no new
  test file per the no-new-pure-function precedent), `tools/
  edit_bundle_module.py sync --check` reports no drift, `live_state.json`
  untouched (md5 `1441d25f45fb4a927f993cbc8c505a5b`, still tick 12 from the
  00:20 UTC daily run), `evotrader.manifest` md5 unchanged, constitution
  verified `8b74865634b1db07` unchanged, today's bar already processed
  before this session started (no double-trade), no genome promotion (no
  README Status change needed). **Next, if this thread stays worth
  pursuing**: whether this measurably flips any real accept/reject verdict
  in practice (replay a real historical generation's candidate batch against
  the champion re-evaluated at a different shift, not attempted); `--also-
  version N` to check whether the swing is v3-specific or general; the
  window-5 `anatomy` post-mortem and the day-1-allocation-redesign question
  from the 09:50 UTC entry, both still open.

- **Confirmed 2026-08-26 (3-hourly check, ~09:50 UTC): the day-1 greedy cash
  allocation mechanism found on window 3 is general — it reproduces on
  window 5 too, and more starkly.** (see
  `runs/2026-08-26-0950-boundary-shift-window5-mechanism-check.md`) Picked up
  the 06:55 UTC entry's open item directly: ran the same `--trace-diff 0,1`
  check on window 5 instead of window 3 (no code change, existing flag).
  Result: shift 0 vs shift 1's day-1 fills share **zero** symbols
  (`['DOGEUSDT', 'SOLUSDT', 'ZECUSDT']` vs `['ETHUSDT', 'LINKUSDT',
  'LTCUSDT']` — window 3's pair shared one), and the very first trade in the
  625/603-trade sequence already diverges. Answers the open question: the
  mechanism (a one-day boundary shift changes every asset's rolling
  indicators on the new "day 1," and `risk_judge`'s greedy, hard-capped cash
  allocation lets whichever symbols cross the entry threshold first claim
  all available cash) is general across windows checked so far, not a
  window-3 special case. Doesn't propose a fix, and raises a framing
  question not asked before: since the live account only ever has one real
  "day 1" (account creation), not a swept ensemble, does this
  boundary-shift sensitivity have any live-trading relevance at all, or is
  it purely a backtest-evaluation artifact? Verified safe: no code changed
  this session (existing CLI flag reused, so no test suite run needed, same
  precedent as prior no-code-change diagnostic sessions), `live_state.json`
  untouched (md5 `1441d25f45fb4a927f993cbc8c505a5b`, still tick 12 from the
  00:20 UTC daily run), `evotrader.manifest` md5 unchanged
  (`0bf3a7d9411ee692d0a9f152a7533803`), constitution verified
  `8b74865634b1db07` unchanged, today's bar already processed before this
  session started (no double-trade), no genome promotion (no README Status
  change needed). **Next, if this thread stays worth pursuing**: the
  window-5 per-trade `anatomy` post-mortem, still open; whether a day-1
  allocation redesign (proportional/ranked instead of greedy-first-come) is
  worth attempting — untried design work; and the new live-trading-relevance
  framing question above, which could resolve the whole thread without
  further diagnostics.

- **Traced 2026-08-26 (3-hourly check, ~06:55 UTC): found the boundary-shift
  path-dependence mechanism — it's a hard-capped, order-sensitive day-1 cash
  allocation, not a black box.** (see
  `runs/2026-08-26-0655-boundary-shift-trade-divergence-trace.md`) Picked up
  the 03:53 UTC entry's sharpest open item directly: traced window 3's shift
  2 vs shift 3 (+357.2% vs -148.2% excess return, one day apart) trade by
  trade with `log_detail=True`. Day 1's fills are a **different set of
  symbols entirely** between the two shifts (`['BNBUSDT', 'LINKUSDT',
  'XLMUSDT']` vs `['BCHUSDT', 'BNBUSDT', 'LTCUSDT']`, only one symbol in
  common) — not a ranking change, a different entry set. Mechanism: shifting
  the window start by one day changes every asset's rolling-indicator values
  on what becomes "day 1," and `risk_judge`'s cash allocation that day is
  greedy and hard-capped (most proposals vetoed `"no room: size cap or cash
  floor"` even on bar 1) — whichever symbols cross the entry threshold first
  claim the available cash outright, so a 1-day shift flips who gets funded,
  not just by how much. That single-bar divergence then compounds through
  500+ trades over ~2 years into the wildly different terminal returns the
  03:53 UTC entry measured. Shipped `--trace-diff S1,S2` on
  `history-perturb --boundary-shift` (same file/precedent as
  `--sub-slice`/`--drawdown`/`--boundary-shift` itself: CLI-only code in
  `main()`, not part of the unflattened `_SRC` modules, no new pure function
  so no new test file) — given two already-swept shift indices, re-runs just
  those two with `log_detail=True` and prints the first structurally
  divergent trade plus whether day-1's fills are the same symbol set.
  Verified against the 03:53 UTC entry's own window-3 numbers (reproduces
  1.174/-inf fitness for shifts 2/3 exactly). Doesn't propose a fix — this
  is a fragility of the greedy day-1 allocation scheme under `risk_judge`'s
  caps, and whether that's worth changing (e.g. proportional day-1 sizing)
  is separate, untried design work. Verified safe: full suite 235 passed
  (138.71s), `git status --short` shows only `evotrader_bundle.py` modified,
  `live_state.json` md5 unchanged (this session never calls `acct.save()`),
  constitution verified `8b74865634b1db07` unchanged, today's bar already
  processed before this session started (no double-trade), no genome
  promotion (no README Status change needed). **Next, if this thread stays
  worth pursuing**: check whether the same day-1-allocation mechanism
  explains window 5's noise (the window currently in a real drawdown) the
  same way, or whether window 5 shows something additionally regime-specific
  — not checked this session, only window 3 was traced; the per-trade
  `anatomy` post-mortem on window 5 is also still open.

- **Checked 2026-08-26 (3-hourly check, ~03:53 UTC): the boundary-shift noise
  found in window 5 is general, not a window-5 special case — windows 3 and
  4 show the same order-of-magnitude sensitivity.** (see
  `runs/2026-08-26-0353-history-perturb-boundary-shift-windows3-4.md`) Same
  `--boundary-shift` flag (no code change), pointed at windows 3 and 4
  instead of 5. Window 3: 10/15 shifts beat benchmark, excess return
  [-162.7%, +366.2%] (widest spread of the three windows checked so far),
  2/15 hard-fail. Window 4: 10/15 beat benchmark, excess return [-48.9%,
  +142.5%], 0/15 hard-fail (maxDD never exceeds -34.1%). Window 5 for
  comparison (00:59 UTC entry): 6/15 beat benchmark, excess return [-44.4%,
  +57.3%], 14/15 hard-fail. Reading: the beat-benchmark/excess-return
  verdict is boundary-placement noise in all three windows checked, not
  unique to window 5 — but window 5's much higher hard-fail rate (14/15 vs.
  2/15 and 0/15) is a real difference, consistent with the 00:59 UTC
  entry's split (max-dd/hard-fail = genuine regime signal, beat-benchmark =
  noisy draw). Sharpens the open v3 demotion/rollback question (raised to
  the owner 2026-08-22): any single window's `beat_benchmark` reading is
  unreliable regardless of which window, but window 5's drawdown depth
  specifically is not. Verified safe: full suite 235 passed (129.54s,
  matches baseline, no code changed so no new tests needed),
  `live_state.json` untouched (still reflects tick 12 from the 00:20 UTC
  daily run), `evotrader.manifest` md5 unchanged, constitution verified
  `8b74865634b1db07` unchanged, today's bar already processed before this
  session started (`tick` not run this session, no double-trade), no
  genome promotion (no README Status change needed). **Next, if this
  thread stays worth pursuing**: trace what actually differs between two
  adjacent boundary-shift runs' first few trades (e.g. window 3's shift 2
  vs 3, +357.2% vs -148.2% one day apart) to find the path-dependence
  mechanism directly — the sharpest remaining item across all three
  boundary-shift sessions so far; the per-trade `anatomy` post-mortem on
  window 5 is still open too, with the noise caveat reinforced twice over.

- **Shipped 2026-08-26 (3-hourly check, ~00:59 UTC): the "window 5 hard-fails
  benchmark" verdict is largely a boundary-placement artifact — the >40%
  max-dd hard-fail is comparatively robust, but the beat-benchmark call is
  not.** (see `runs/2026-08-26-0059-history-perturb-boundary-shift.md`)
  Discovered while setting up a window-5 anatomy post-mortem: re-running
  `history-perturb --independent` one day after the 2026-08-25 09:56 UTC run
  flipped window 5's excess return from -41.2% (hard-fail) to +3.7% (beats
  benchmark) purely from every window boundary walking back one day. New
  `--boundary-shift N [--sub-slice-window I]` flag (same file/precedent as
  `--sub-slice`/`--drawdown`: requires `--independent`, reuses its loaded
  `raw`/`windows`, one real `run_backtest` per shift, no new pure function)
  confirms this isn't a one-off: walking window 5's end date back 0-14 days
  shows `beat_benchmark` flipping True/False almost at random (6/15 True),
  excess return ranging -44.4% to +57.3% — a ~100-point spread from two
  weeks of boundary placement. The >40% max-dd hard-fail gate is more
  stable (14/15 shifts breach it). Reads as backtest path-dependence (a
  different first bar cascades into a different two-year trade sequence),
  not a regime property. Doesn't erase the last two days of window-5 work —
  the drawdown depth/location findings (2026-08-25 15:53/21:55 UTC entries)
  are about the more-robust half — but the "champion loses to buy-and-hold
  in its current regime" framing specifically was one noisy draw, not a
  settled number; the open v3 demotion/rollback question (raised to the
  owner 2026-08-22) should weigh that. Verified safe: full suite 235 passed
  (150.53s, matches baseline, no new test file per the no-new-pure-function
  precedent), `tools/edit_bundle_module.py sync --check` reports no drift
  (this CLI-dispatch code isn't part of the unflattened `_SRC` modules),
  `git status --short` clean before commit except `evotrader_bundle.py`,
  `live_state.json` untouched by this session (still reflects tick 12 from
  the 00:20 UTC daily run), `evotrader.manifest` md5 unchanged
  (`0bf3a7d9411ee692d0a9f152a7533803`), constitution verified
  `8b74865634b1db07` unchanged, today's bar already processed by the 00:20
  UTC daily run before this session started (`tick` not run this session,
  no double-trade), no genome promotion (no README Status change needed).
  **Next, if this thread stays worth pursuing**: the per-trade `anatomy`
  post-mortem restricted to window 5 that motivated this is still open
  (now with the caveat that "window 5" is one noisy draw); running
  `--boundary-shift` on windows 3/4 to see if they're similarly noisy;
  tracing what actually differs between two adjacent-shift runs' first few
  trades to find the path-dependence mechanism directly.

- **Checked 2026-08-25 (3-hourly check, ~21:55 UTC): trend/chop, volatility,
  benchmark shape, and cross-asset correlation all fail to distinguish
  window 5 from the windows the champion beats — the "what's different
  about 2024-2026" question from 09:56 UTC is not a coarse market-regime
  question.** (see
  `runs/2026-08-25-2155-history-perturb-window5-regime-characterization.md`)
  No code shipped — three throwaway `/tmp` scripts reused already-tested
  pure functions (`benchmark_buy_hold`, `pairwise_correlation_stats`, plus a
  simple efficiency-ratio/volatility calc) over the same 5 independent
  windows `history-perturb --independent` already tiles. Result: window 5's
  mean efficiency ratio (0.036), annualized volatility (84.6%), buy-and-hold
  benchmark shape (+79.5% return, sharpe 0.77 — a genuine melt-up, not a
  crash or chop), and mean pairwise correlation (0.584) all sit inside the
  range of windows 3-4, which the champion clears comfortably (+57.5%/+0.8%
  excess return there vs -41.2% in window 5). Rules out "window 5 is a
  different kind of market" by every genome-independent metric checked here
  — whatever makes the champion fail specifically in window 5 has to be
  about how its own genome/mechanism responds to that window's actual bar
  sequence, not a coarse regime label. Verified safe: no repo files touched
  by the check itself, `live_state.json` md5 unchanged
  (`f7590581b893d3866e00e28c87fe1c02`), `evotrader.manifest` md5 unchanged
  (`0bf3a7d9411ee692d0a9f152a7533803`), today's bar already processed by the
  00:20 UTC daily run before this session started (`tick` not run this
  session, no double-trade), no genome promotion (no README Status change
  needed). **Next, if this thread stays worth pursuing**: an `anatomy`-style
  per-trade post-mortem restricted to window 5, or a trade-count/turnover
  comparison against windows 3-4, since the coarse regime-shape hypotheses
  are now exhausted; otherwise fold this into the already-open v3
  demotion/rollback question (raised to the owner 2026-08-22, reaffirmed
  since) as one more data point that the edge isn't fully regime-general.

- **Checked 2026-08-25 (3-hourly check, ~18:52 UTC): the continuous-exceeds-
  sub-slice drawdown gap is real but not universal — 2 of 4 testable
  windows (2 and 5) show it, 2 (3 and 4) don't, window 1 untestable.** (see
  `runs/2026-08-25-1852-history-perturb-windows1to4-drawdown.md`) No code
  shipped — reused existing tested pieces (`run_backtest`,
  `drawdown_episodes`, `market.load_universe`) from a throwaway `/tmp`
  script, same precedent as the 4h shadow-evolution sessions, to check the
  15:53 UTC entry's open question: do windows 1-4 (which all beat
  benchmark) show the same continuous-run's-maxDD-exceeds-any-of-its-own-
  sub-slices gap that window 5 showed? Result: window 2 (2018-08-25 to
  2020-08-25) shows the same shape — continuous maxDD -37.0% vs worst
  quarter -22.2%, a second real `fold-dd-blindspot`-style instance. Windows
  3 and 4 show essentially no gap (window 3 is actually *shallower*
  continuous than its worst quarter, -34.7% vs -42.3% — a locally deep
  quarter-level dip that isn't part of the real peak-to-trough once the
  quarter boundary resets the running peak). Window 1 (2017-08-17 to
  2018-08-25, the earliest history edge) can't be sub-sliced at all: each
  quarter has too few bars (~93) and too few listed symbols (3-8 of the
  full roster) for the genome's lookback genes, even though the full window
  backtests fine. **Reading: this is boundary-placement dependent, not a
  general continuous-vs-sub-sliced artifact and not unique to window 5's
  current regime** — closes the open question from 15:53 UTC without
  further sub-slicing being the obviously useful next step. Verified safe:
  no repo files touched by the check itself (`git status --short` clean
  before/after except this note + AGENTS.md), `live_state.json` md5
  unchanged (`f7590581b893d3866e00e28c87fe1c02`), `evotrader.manifest` md5
  unchanged (`0bf3a7d9411ee692d0a9f152a7533803`), today's bar already
  processed by the 00:20 UTC daily run before this session started (`tick`
  not run this session, no double-trade), no genome promotion (no README
  Status change needed). **Next, if this thread stays worth pursuing**:
  window 5's drawdown is still unrecovered as of 2026-08-25 (the live
  champion's actual current regime, not a historical curiosity) — worth a
  glance in a future session whether NAV keeps declining or starts
  recovering over the next several daily bars.

- **Shipped 2026-08-25 (3-hourly check, ~15:50 UTC): `history-perturb
  --drawdown` locates window 5's continuous -44.0% drawdown exactly, and it
  is a real cross-sub-window span, confirming the ~12:55 UTC entry's
  hypothesis directly instead of just by shape.** New `--drawdown
  [--sub-slice-window I]` flag on `history-perturb --independent`: runs one
  continuous `run_backtest` over window `I` (default: the most recent) and
  feeds its `nav_history` through the already-existing, already-tested
  `loop.engine.drawdown_episodes` (the same pure function the `drawdown`
  command already uses over the full 4-year history/holdout) to report the
  actual peak/trough dates and depth, ranked, instead of a single max_dd
  number. No new pure function — this only wires an existing one into
  `history-perturb`'s already-loaded window list, same precedent as
  `--sub-slice`. Result on champion v3's window 5 (2024-08-25 to
  2026-08-25): the deepest episode reproduces the reported -44.0% exactly,
  peak **2025-11-08** to trough **2026-08-11** (276 bars, **not yet
  recovered** as of the newest available bar) — a single unbroken decline
  that starts inside the ~12:55 UTC run's sub-window 3 (2025-08-25 to
  2026-02-23) and bottoms out inside sub-window 4 (2026-02-23 to
  2026-08-25), exactly the cross-boundary span that run's shape-based
  argument predicted but couldn't locate without the NAV path. Four shallower
  episodes also reported (-25.9% to -11.2%, all recovered), none close to
  the 40% gate on their own. Answers the ~12:55 UTC "Next" item's first
  option directly (no finer sub-slice needed once the real peak/trough dates
  are in hand) — the second option (whether windows 1-4 show the same
  continuous-exceeds-any-sub-slice gap) is still open, not attempted here.
  Verified safe: full suite 235 passed (156.34s, matches baseline, no new
  test file per the no-new-pure-function precedent), `git status --short`
  clean before commit, `live_state.json` md5 unchanged
  (`f7590581b893d3866e00e28c87fe1c02`), `evotrader.manifest` md5 unchanged
  (`0bf3a7d9411ee692d0a9f152a7533803`), constitution verified
  `8b74865634b1db07` unchanged, today's bar already processed by the 00:20
  UTC daily run before this session started (`tick` not run this session,
  no double-trade), `review-hard-calls` still 0 pending, no genome
  promotion (no README Status change needed). **Next, if this thread stays
  worth pursuing**: check windows 1-4 with the same `--drawdown` flag for
  the continuous-exceeds-any-sub-slice gap; separately, the drawdown being
  *unrecovered as of "now"* (2026-08-25) is itself worth flagging — this is
  the live champion's own current real-time regime, not a historical
  curiosity, so whether NAV keeps falling or starts recovering over the
  next few daily bars is worth a glance in a future session rather than
  assuming it already troughed.

- **Shipped 2026-08-25 (3-hourly check, ~12:55 UTC): `history-perturb
  --sub-slice`, the follow-up the ~09:56 UTC entry below flagged — does the
  newest independent window's hard-fail spread evenly across its 2 years or
  concentrate in a sub-period?** (see
  `runs/2026-08-25-1255-history-perturb-sub-slice-window5.md`) New
  `--sub-slice N [--sub-slice-window I]` flag on `history-perturb
  --independent` (reuses its already-loaded history/window list, no new
  data loading): splits window `I` (default: the most recent) into `N`
  equal contiguous sub-windows, one real `run_backtest` each. Result on
  champion v3's window 5 (2024-08-25 to 2026-08-25), split into 4 six-month
  sub-windows: a clean front/back split, not an even spread — sub 1-2 are
  fitness-positive (sub 1 hits 4.080, the best fitness of *any* window
  measured in this whole thread), sub 3-4 are fitness-negative, and
  benchmark is beaten in only 1/4 sub-windows overall. Sharper structural
  finding: **no individual 6-month sub-window comes within 15 points of the
  40% hard-fail drawdown threshold (worst is -25.2%), yet the full
  continuous 2-year window's own max_dd is -44.0%** — the same *shape* as
  the already-documented `fold-dd-blindspot` mechanism (a continuous
  drawdown spanning a window boundary is invisible to any one
  independently-reset backtest's local max_dd), here surfaced by one
  continuous run exceeding what any of its own sub-slices show locally,
  rather than by merging independent folds. Not proven mechanistically
  identical (would need the actual NAV/drawdown path, not exposed by
  `run_backtest`'s return value today) — a plausible match, not a closed
  case. Verified safe: full suite 235 passed (135.67s, matches baseline, no
  new pure function so no new test file, same precedent as every
  perturbation diagnostic in this family), `git status --short` clean
  before commit, `live_state.json` md5 unchanged
  (`f7590581b893d3866e00e28c87fe1c02`), `evotrader.manifest` md5 unchanged
  (`0bf3a7d9411ee692d0a9f152a7533803`), constitution verified
  `8b74865634b1db07` unchanged, today's bar already processed by the 00:20
  UTC daily run before this session started (`tick` not run this session,
  no double-trade), `review-hard-calls` still 0 pending, no genome
  promotion (no README Status change needed). **Next, if this thread stays
  worth pursuing**: locate the continuous drawdown more precisely (a finer
  `--sub-slice`, e.g. 8 windows of ~3 months, or exposing the internal
  equity curve for a direct plot) and check whether windows 1-4 (which all
  pass) show the same continuous-exceeds-any-sub-slice gap, to tell whether
  this is generic to continuous-vs-sub-sliced backtesting or specific to
  window 5 — not attempted here.

- **Shipped 2026-08-25 (3-hourly check, ~09:56 UTC): `history-perturb
  --independent`, the sharper non-overlapping-windows follow-up the ~07:00
  UTC entry below explicitly flagged as its own next step.** (see
  `runs/2026-08-25-0956-history-perturb-independent-windows.md`) New mode
  on the same command (`[--window-years Y]`, default 2.0): instead of
  nested scenarios all ending "now," tiles fixed-width non-overlapping
  windows walking backward from "now" over the full available history per
  symbol (real Binance listing dates, via a generous 12y load). Result on
  champion v3: 4 genuinely independent windows spanning 2017-2024 all beat
  benchmark (3 by a large margin), but the most recent independent window
  (2024-08-24 → 2026-08-25 — the same span the nested `--years 2` scenario
  already flagged) hard-fails. **This sharpens, not just confirms, the
  07:00 UTC finding**: it rules out "one shared recent stretch is a
  headwind a longer nested window's older gains simply outweigh" (4
  independent non-nested windows still show a real edge), reframing the
  open question from "is the edge start-date dependent" (largely answered:
  no, not broadly) to "what's specifically different about 2024-2026"
  (open). A comparison run against reconstructed v1 (unevolved seed) found
  a different, much weaker pattern (beats benchmark in only 1/5 windows vs
  v3's 4/5, including losing badly in two windows where v3's edge was
  largest) — evidence the edge is a genuine product of evolution, not
  market beta, though v1 doesn't clear window 5 either. Verified safe: full
  suite 235 passed, no new pure function so no new test file (same
  precedent as the nested mode), `git status --short` clean before commit,
  `live_state.json` md5 unchanged (`f7590581b893d3866e00e28c87fe1c02`),
  `evotrader.manifest` md5 unchanged (`0bf3a7d9411ee692d0a9f152a7533803`),
  constitution verified `8b74865634b1db07` unchanged, today's bar already
  processed by the 00:20 UTC daily run before this session started (`tick`
  not run this session, no double-trade), `review-hard-calls` still 0
  pending, no genome promotion (no README Status change needed). **Next**:
  characterize window 5 specifically (`regime` on that exact span, or a
  sub-slice check to see if the failure is concentrated or spread across
  the whole 2 years) — not attempted here.

- **Shipped 2026-08-25 (3-hourly check, ~07:00 UTC): `history-perturb`, the
  last untried leg of the 2026-08-16 "perturbation tests on
  fees/slippage/universe/start-date" note — `costs` covers fees/slippage,
  `universe-perturb` covers universe composition, this covers start-date.**
  New read-only CLI `evotrader_bundle.py history-perturb [--years
  Y1,Y2,...] [--also-version N]`, same guarantees as `costs`/
  `universe-perturb`: real `run_backtest` per scenario, never touches
  `live_state.json` or the champion. Sweeps total lookback length ending
  "now" (default 2/3/4/5/6 years) — a genuinely different start date each
  time, not another fold-windowing variant of the fixed 4y window (that line
  was set aside as exhausted back on 2026-08-21). **Caught a real bug in the
  first draft before shipping it**: `core.market.load()`'s cache is a floor,
  not a window — "the cache only ever grows" means `load_universe(...,
  years=X)` returns the *full* cached range once the cache already covers X,
  not an X-year slice. Passing `years` straight through, as the first draft
  did, silently returned identical multi-year data for every "shorter"
  scenario in one process (whichever request built the cache widest
  satisfies every smaller one too) — verified this concretely with a
  throwaway script (`market.load('BTCUSDT', '1d', 2.0)` and `..., 4.0)`
  returned byte-identical 1461-row frames once the cache held 4y; only
  `6.0` correctly extended it). Fixed by loading once at `max(years_list)`
  and explicitly truncating each symbol's frame to `[now - years, now]`
  before backtesting, independent of whatever the on-disk cache holds.
  Verified against real data post-fix: three genuinely different window
  starts (2y→2024-10-24, 4y→2022-10-25, 6y→2020-10-24) with real variance —
  champion v3 **loses to benchmark at 2y** (-40.6% excess return, hard-fails
  the maxDD gate too) but **beats it at 4y and 6y** (+78.7%, +3065.1%
  excess return; 6y's raw fitness is a further -3.161 despite the huge
  excess return, a separate Sortino/penalty-shape question not chased here).
  First real evidence that the champion's apparent edge is start-date
  dependent, not a settled result — n=3 windows, all sharing the same
  overlapping recent history rather than being independent draws, so this
  is a first measurement to build on, not a verdict. Not chased further this
  session (time-boxed to shipping the working diagnostic plus one real
  finding, not a full sensitivity study). No new pure function added (composes
  already-tested `run_backtest`/`Genome`/`market.load_universe`), so no new
  test file, same precedent as `costs`/`universe-perturb`/`regime`. Verified
  safe: full suite 235 passed (`pytest tests/`, matches baseline, nothing new
  to test), `git status --short` clean before this commit, `live_state.json`
  md5 unchanged (`f7590581b893d3866e00e28c87fe1c02`) and `evotrader.manifest`
  md5 unchanged (`0bf3a7d9411ee692d0a9f152a7533803`) throughout, constitution
  verified `8b74865634b1db07` unchanged, today's bar already processed by the
  00:20 UTC daily run before this session started (`tick` not run this
  session, no double-trade), `review-hard-calls` still 0 pending, no genome
  promotion (no README Status change needed). **Next, if this thread stays
  worth pursuing**: more/denser `--years` points, or (sharper) independent
  non-overlapping windows instead of nested ones sharing the same recent
  history, to tell "recent regime happens to favor this genome" apart from
  genuine start-date robustness — not attempted here.

- **Measured 2026-08-25 (3-hourly check, ~04:02 UTC): the third-genome check
  the ~01:00 UTC entry named as the concrete next step — run, and it closes
  this line of inquiry with a negative result.** (see
  `runs/2026-08-25-0402-selection-noise-third-genome.md`) Same six-draw
  method against reconstructed champion **v1** (the unevolved seed,
  `Genome.champion()`, no lineage patches needed). Result: winner gap mean
  +0.443 vs random gap mean +0.380, winner larger in only 2/6 draws, paired
  t≈0.121 — essentially no signal, far weaker than v3 (t≈1.02 combined) or
  v2 (t≈1.667). Extending the 01:00 UTC entry's 2-block genome-stratified
  design to 3 blocks (v3 n=12, v2 n=6, v1 n=6): fixed-effect pooled mean
  drops to +0.456 (z≈1.340, one-sided p≈0.090, down from z≈1.678/p≈0.047 at
  2 blocks); Cochran's Q rises to 2.030 (df=2, still short of the 5.991
  critical value); block-stratified sign-permutation p rises to 0.0815 (up
  from 0.0635). **Reading: every time this four-session thread got a
  genuinely new unit of evidence — v3's second batch, a second champion, now
  a third genome — the pooled estimate moved away from significance, never
  toward it, which is itself the signature of a null or sub-noise effect,
  not one that just needs more data.** Not touching `HOLDOUT_SIGMA` — the
  conclusion at every step of this thread, now on firmer ground. Closing
  this line of inquiry, not just this session's slice: worth reopening only
  on a cheap fourth genome (a future v4+ promotion) or a sharper mechanistic
  hypothesis, not another same-method batch. Verified safe: `git status
  --short` clean, `live_state.json` md5 unchanged
  (`f7590581b893d3866e00e28c87fe1c02`), full suite 235 passed (no code
  changed), `review-hard-calls` still 0 pending, today's bar already
  processed by the 00:20 UTC run before this session started (no
  double-trade). No push notification — read-only research finding (a
  negative one, closing the thread), zero effect on live trading.

- **Measured 2026-08-25 (3-hourly check, ~01:00 UTC): the genome-stratified
  pooled test the 2026-08-24 22:01 UTC entry flagged as the real next step —
  run, and it changes the picture slightly.** (see
  `runs/2026-08-25-0100-selection-noise-genome-stratified.md`) Pure
  arithmetic on the 18 draws already collected across two genomes (v3: 12,
  v2: 6) — no new backtests. Cochran's Q test (Q=0.994, df=1) found no
  detectable heterogeneity between the two genomes, so the specific worry
  that blocked a pooled conclusion ("the samples aren't draws from one
  distribution") isn't supported by this data — weak evidence given only 1
  degree of freedom, but not the roadblock it was flagged as. Properly
  pooled (inverse-variance weighted, not naive concatenation): fixed-effect
  mean +0.761 (se 0.453, z≈1.678, one-sided p≈0.047); a block-stratified
  sign-permutation test (200,000 resamples, no normality/pooling
  assumptions) gives p≈0.0635 — closer to conventional significance than
  either genome alone (v3 t≈1.02, v2 t≈1.667) but still not a clean cross.
  **Reading: still not enough to justify touching `HOLDOUT_SIGMA`** (a
  borderline p-value under a design that's low-powered at only 2 genomes
  isn't a confirmed effect), but this closes the "needs a genome-stratified
  design" loose end cleanly. **Sharper next step than more draws or more
  permutation of the same two genomes: a third genome (v1, or a future
  champion) would sharpen both the Q-test's power and the pooled estimate's
  precision far more.** Verified safe: `git status --short` clean before
  the commit (script lives in the session scratchpad), `live_state.json`
  md5 unchanged, `review-hard-calls` still 0 pending, today's bar already
  processed by the 00:20 UTC run before this session started (no
  double-trade). No push notification — read-only research finding,
  borderline not conclusive, zero effect on live trading.

- **Measured 2026-08-24 (3-hourly check, ~22:01 UTC): a second champion
  (reconstructed v2) shows the same winner's-curse-shaped selection-noise
  pattern as v3 did — directionally consistent, still not significant
  alone, but now replicated on a genuinely different genome.** (see
  `runs/2026-08-24-2201-selection-noise-second-champion.md`) The ~18:57 UTC
  entry below explicitly named "a second champion" as the next genuinely
  different check worth running. Same six-draw method (fold-aggregate
  winner vs. one random non-winning candidate from the same batch, both run
  through the sealed holdout, `exclude` accumulated across draws) against
  reconstructed champion v2 instead of live v3. Result: winner gap mean
  +1.851 (std 1.158) vs random gap mean +0.237 (std 1.484), winner's gap
  larger in 5/6 draws, paired t≈1.667 (df=5) — close in shape and strength
  to v3 batch 1's t≈1.55 (4/6 draws), and a bit stronger than v3's own
  diluted 12-draw combined number (t≈1.02). Neither champion is individually
  significant, but two unrelated genomes landing on the same direction and
  similar magnitude is stronger evidence than either alone. **Reading
  revised again**: not strong enough to justify touching `HOLDOUT_SIGMA`
  (already a measured floor, not a guess), but strong enough that this
  isn't "one favorable draw" any more either. A rigorous pooled test across
  champions would need a genome-stratified or mixed-effects design (the
  samples aren't draws from one distribution) — flagged as a real next step
  if this remains worth resolving, not attempted here. Verified safe:
  `git status --short` clean, `live_state.json` md5 unchanged throughout,
  full suite 235 passed (no code changed), `review-hard-calls` still 0
  pending, today's bar already processed by the 00:20 UTC run before this
  session started (no double-trade). No push notification — read-only
  research finding, zero effect on live trading.

- **Measured 2026-08-24 (3-hourly check, ~18:57 UTC): batch 2 of the
  selection-noise diagnostic weakens the signal, not strengthens it —
  the "more draws" follow-up the ~16:15 UTC entry below explicitly left
  open.** (see `runs/2026-08-24-1857-selection-noise-batch2.md`) Same
  method, 6 more independent draws (n_blind=10, exclude accumulated) against
  real champion v3. Batch 2 alone reverses the direction (random gap mean
  1.818 > winner gap mean 1.679, paired t=−0.218, wrong sign for the
  winner's-curse hypothesis), driven partly by one outlier random-gap draw
  (−1.358, batch 2's `exclude` had already burned through the deterministic
  diagnosis-driven proposals so this batch was pulling from a different part
  of the mutation space than batch 1's early draws). Combined 12-draw sample:
  paired t≈1.02 (df=11) — weaker than batch 1's t≈1.55 alone. Doubling the
  sample moved the result further from significance, the opposite of what
  "just needs more data" would predict if the effect were real. **Reading
  revised**: no good evidence yet of a winner's-curse selection effect
  distinct from ordinary per-candidate holdout noise; batch 1's number looks
  like a favorable draw from a noisy distribution, not the start of a
  sharpenable signal. Leaving this question here — further identical-method
  batches are unlikely to resolve it either way given batch 2's own variance
  blowup; would need either an order-of-magnitude more draws or a genuinely
  different check (e.g. a second champion) to be worth another session.
  Verified safe: `git status --short` clean, `live_state.json` md5 unchanged
  throughout, full suite 235 passed (no code changed), `review-hard-calls`
  still 0 pending, today's bar already processed by the 00:20 UTC run before
  this session started (no double-trade). No push notification — read-only
  research finding (a negative one, this time), zero effect on live trading.

- **Measured 2026-08-24 (3-hourly check, ~16:15 UTC): a first number on the
  "harder, unquantified question" `holdout-sigma-recalibration` (2026-08-21)
  left unchased — whether a fold-selected winner's sealed-holdout score is
  optimistically biased relative to a candidate that merely existed in the
  same batch.** (see `runs/2026-08-24-1615-selection-noise-diagnostic.md`)
  One-off script (same precedent as the 2026-08-24 00:49 seed-holdout-noise
  diagnostic — not a new CLI command): six independent draws of real
  `Researcher.propose`/`Evaluator.evaluate` batches against real champion v3,
  each taking the fold-aggregate winner (what `EvolutionRun.generation()`
  actually carries to the holdout gate) and one candidate picked uniformly at
  random from the rest of the batch, running **both** through the sealed
  holdout (`generation()` itself never does this for a non-finalist).
  Caught and fixed a real methodology bug first: with `exclude` reset every
  draw, the same deterministic (non-perturbation) proposal won all 6 draws
  identically, because `from_diagnosis()`/`structural()` don't depend on the
  Researcher's seed — fixed by accumulating `exclude` across draws, mirroring
  `EvolutionRun.tested`'s real cumulative-per-champion behavior. Result:
  winner's mean (fold − holdout) gap +2.172 (std 0.928, n=6) vs random's
  +0.990 (std 1.274, n=6), winner's gap larger in 4/6 draws, paired t≈1.55 —
  directionally consistent with a winner's-curse-style selection effect but
  **not statistically significant at this sample size**. First real
  measurement of this question, not a settled answer or a constitution
  change — see AGENTS.md item 2 below for the full writeup and what's still
  open (more draws, a second champion, or translating a confirmed effect
  into an actual correction). Verified safe: `git status --short` clean
  (script lives in the session scratchpad, not the repo), `live_state.json`
  md5 unchanged throughout, full suite 235 passed (no code changed),
  `review-hard-calls` still 0 pending. No push notification — read-only
  research finding, directionally suggestive not conclusive, zero effect on
  live trading.

- **Done 2026-08-24 (3-hourly check, ~12:47 UTC): `succession-audit` gets a
  new diagnostic-only `trust-cont fit` column, plus the pure function behind
  it — `loop.evolve.dd_trust_continuous_stats`.** (see the 2026-08-22
  `succession-audit` finding under item 2 and
  `tests/test_continuous_max_dd.py`'s four new tests) That finding left a
  concrete loose end: `dd_corrected_stats()` (the fix `accepts()` actually
  gates real promotions on) takes `min(fold-merged, continuous)`, which can
  only ever tighten the gate — correct for the original `fold-dd-blindspot`
  direction (fold-merged understating true risk) but blind to the opposite
  one `succession-audit` found in champion v2 (fold-merged *overstating*
  true risk via fold-2 rebasing to a fresh local peak). `min()` has no way
  to recover a truer, better continuous number from an overstated
  fold-local one. New `dd_trust_continuous_stats()` is a diagnostic-only
  sibling that always trusts the continuous replay instead of taking the
  worse of the two — explicitly NOT wired into `accepts()`/
  `EvolutionRun.generation()`, and does not change any live gate behavior.
  `succession-audit` now prints it alongside the existing `dd-corr fit`
  column so a future demotion/rollback design pass (still the owner's call,
  unchanged by this) has the two-sided comparison already computed instead
  of needing to build it from scratch. Verified safe: full suite 235 passed
  (was 231; +4 new, 0 broken), `sync --check`/`verify` clean (new function
  lives in the real `loop/evolve.py`, synced into the bundle's `_SRC` entry;
  the CLI's own succession-audit code is a plain-script addition, no
  `_SRC[...]` line touched there), `py_compile` clean, real `live_state.json`
  md5 unchanged across every command run this session (`succession-audit`
  ×2, `summary`, `review-hard-calls`), `review-hard-calls` still 0 pending,
  today's bar already processed by the 00:20 UTC run before this session
  started (no double-trade). Manually ran `succession-audit` against real
  data: today's numbers differ from the 2026-08-22 diagnostic's (window has
  moved 2 days, so v2's fold-merged and continuous max_dd happen to coincide
  today rather than diverge) — expected, and not evidence the original
  finding was wrong, just a reminder these numbers are date-dependent
  snapshots, not fixed properties of a genome. **What this does NOT do**: no
  change to `accepts()`'s actual policy, no opinion offered on whether the
  gate should ever really use the two-sided correction — that stays a real
  design decision for whoever eventually opens the demotion/rollback
  question, same standing note as every session since 2026-08-22. No push
  notification — read-only diagnostic tooling, zero effect on live trading.

- **Done 2026-08-24 (3-hourly check, ~09:46 UTC): item 7's actual cutover
  ships -- `run_from_files.py tick`/`evolve` now genuinely call
  `acct.save()`, the same real bodies as `evotrader_bundle.py`'s own
  `tick`/`evolve` commands, transcribed verbatim.** (see `run_from_files.py`'s
  module docstring and `tests/test_run_from_files_matches_bundle.py`'s new
  `test_tick_*`/`test_evolve_*` tests) This is the piece the 06:56 and 09:00
  UTC entries below both named as the natural next checkpoint once both
  dry-run twins existed, and the 09:00 daily discussion explicitly checked
  whether it needed owner sign-off first and concluded it didn't ("an
  engineering/testing milestone... nothing here rises to something the
  system can't decide for itself"). `tick` supports `--force` (unlike
  `tick-dry-run`, which deliberately omits it) since this command is meant
  to be a genuine drop-in replacement for the bundle's own `tick`, not a
  narrower variant. `evolve` keeps the same test-only `--seed N` flag
  `evolve-dry-run` already had (the bundle's own `evolve` has no such flag).
  Verified safe: full suite 231 passed (was 227; +4 new, 0 broken). The two
  new `test_tick_*` tests give the strongest parity check in this file yet
  -- run the bundle's real `tick` and this file's real `tick` against two
  byte-identical copies of the same synthetic scratch starting state and
  assert the resulting state files match once wall-clock timestamps
  (`updated`, `genome.created`, `journal[].ts` -- all stamped by
  `core.live._now()` at save/construction time, not derived from the bar
  being traded) are normalized out; caught a real first-draft test bug this
  way (two subprocesses a moment apart in real time predictably differ on
  those fields even with identical decisions -- not a code defect, a test
  design issue, fixed by recursively blanking ISO-8601-shaped strings
  before comparing rather than relaxing the check to skip real content).
  The two new `test_evolve_*` tests check `evolve` against its own
  `evolve-dry-run` twin instead (same seed, same starting state, same
  decision), since the bundle's `evolve` has no `--seed` flag to pin down
  for a subprocess-level comparison the way `tick`'s does. `sync --check`
  clean (no `_SRC` module touched -- `run_from_files.py` is plain CLI-script
  code, same as every prior addition to this file), `py_compile` clean,
  real `live_state.json` md5 unchanged throughout (confirmed both by `git
  status --short` showing no diff and by re-running `tick-dry-run` against
  the real state afterward: still correctly reports today's bar already
  traded), `evotrader_bundle.py summary`/`review-hard-calls` both still
  clean (0 hard-call reviews pending), today's bar already processed by the
  00:20 UTC run before this session started (no double-trade). **What this
  does NOT do**: no scheduled run has been pointed at `run_from_files.py`
  instead of the bundle -- `evotrader_bundle.py` remains what every
  scheduled `tick`/`evolve`/`summary` actually runs, unchanged by this
  commit, and that stays true until a separate, deliberate decision (not
  made here) says otherwise. No push notification -- test-infrastructure
  work, zero effect on live trading; the file that actually executes on a
  schedule is untouched. **Item 7 is now feature-complete relative to the
  bundle's own state-mutating commands** (both `tick` and `evolve` exist in
  both dry-run and real form against the real files); what remains, if
  anyone ever wants it, is purely the scheduling decision itself, which is
  a policy call about the migration timeline, not an engineering task.

- **Done 2026-08-24 (3-hourly check, ~06:56 UTC): `evolve-dry-run` ships --
  the second and final state-mutating command in item 7's tick/evolve
  cutover now has a dry-run twin, tested.** (see "Next steps" item 7 and
  `runs/2026-08-24-0656-evolve-dry-run.md`) New `run_from_files.py` command
  runs the real `loop.evolve.EvolutionRun` (same class the bundle's
  `evolve` drives, transcribed verbatim including the researcher-memory
  resume) against the real files, but never calls `acct.save()` regardless
  of whether a candidate would have promoted or the champion would have
  held. Needed a new, bigger synthetic fixture (`synthetic_universe_4y`,
  ~1500 daily bars / ~4.1y, vs. `tick-dry-run`'s 600/1.6y) because `evolve`
  requests a 4-year `load_universe` window, not `tick()`'s 1.5y one. Also
  traced a non-obvious wrinkle: `EvolutionRun` writes real files under
  `state/genomes/` and `state/lineage.jsonl` (via `Genome.save`/`.promote`),
  which resolve to the *same* absolute path in bundled and real-files mode
  -- confirmed this is provably inert (both `evolve` and `evolve-dry-run`
  overwrite `champion.json` with the real champion before `EvolutionRun`
  ever reads it back, and nothing outside `core/genome.py` itself reads
  those archive files), but the fixture snapshots/restores them anyway for
  cleanliness. Verified safe: full suite 227 passed (was 225; +2 new, 0
  broken), both new tests run in ~60s combined against the synthetic
  universe (no real market data needed), `state/genomes/` and
  `state/cache/ZZTEST*` confirmed absent after the run, `sync --check`
  clean (no `_SRC` module touched), `py_compile` clean, real
  `live_state.json` byte-identical throughout, `evotrader_bundle.py
  summary` still runs clean, `review-hard-calls` 0 pending, today's bar
  already processed by the 00:20 UTC run before this session started (no
  `tick`/`evolve` run for real). No push notification -- test-
  infrastructure work, zero effect on live trading. Item 7's actual
  remaining piece -- a genuinely *saving* `tick`/`evolve` against the real
  files, and the decision to ever schedule a run against `run_from_files.py`
  instead of the bundle -- remains untouched and separate; with both dry-run
  commands now in place, that decision (not another dry-run/read-only
  addition) is the natural next checkpoint for this item.

- **Done 2026-08-24 (3-hourly check, ~03:5x UTC): `tick-dry-run`'s non-skip
  branch finally gets automated coverage, without waiting for the narrow
  live-timing window every prior session flagged as the blocker.** (see
  "Next steps" item 7 and `tests/test_run_from_files_matches_bundle.py`'s
  two new `test_tick_dry_run_*` tests) Every session since 2026-08-23 18:45
  UTC had only exercised `tick-dry-run` against an already-traded bar (the
  skip path) — its non-skip branch (builds and prints a real would-be order
  list) had zero coverage, automated or manual, because that requires a
  session to start in the gap between a new bar closing and the 00:20 UTC
  daily run claiming it, and no session had landed in that gap yet. Solved
  it by not waiting: a fully synthetic 2-symbol scratch universe
  (`ZZTESTAUSDT`/`ZZTESTBUSDT`, cache-only, never a real Binance pair) with
  `state/cache/{sym}_1d.pkl` pre-populated to already span
  `LiveAccount.tick()`'s full 1.5y `load_universe` window and dated through
  today, so neither of `core.market.load()`'s two fetch branches ("need
  older history", "need newer bars") ever fires — no network dependency for
  the part of `tick()` that matters, unlike the reasoning that kept
  `regime`/`fold-dd-blindspot`/`tick-dry-run`'s *skip* path manual-only. A
  scratch genome (real seed genome, `universe`/`regime_anchor` swapped to
  the fake symbols) plus a scratch `live_state.json` via the existing
  `EVO_STATE` env override (never the real file) drives both branches
  deterministically: empty `journal` forces the non-skip branch, a `journal`
  pre-seeded with the exact bar `tick()` will compute forces the skip
  branch. Both tests assert the scratch state file is byte-identical before
  and after (proving `acct.save()` is genuinely never called, on the branch
  that actually matters this time, not just the one every prior session
  happened to exercise) and that the real `live_state.json` never moves.
  Verified safe: full suite 225 passed (was 223; +2 new, 0 broken), synthetic
  cache files (`state/cache/ZZTEST{A,B}USDT_1d.pkl`) removed by the fixture's
  `finally` block after every run (confirmed empty `state/cache/` afterward),
  `sync --check` clean, `py_compile` clean, real `live_state.json`
  byte-identical throughout (git diff shows only the test file changed),
  `evotrader_bundle.py summary` still runs clean, `review-hard-calls` 0
  pending, today's bar already processed by the 00:20 UTC run before this
  session started (no `tick`/`evolve` run for real). No push notification —
  test-infrastructure work, zero effect on live trading. Item 7's actual
  cutover (`tick`/`evolve` saving against the real files, and the decision
  to ever point a scheduled run here) remains untouched and separate.

- **Measured 2026-08-24 (3-hourly check, ~00:49 UTC): the seed's poor
  sealed-holdout score is an ordinary draw from its own noise, not an
  outlier — closes the open question the entry below left unchased.** (see
  `runs/2026-08-24-0049-seed-holdout-noise-diagnostic.md`) One-off script
  (not a new CLI command; `SEED_GENOME` isn't in `live_state.json`'s
  lineage, so `holdout-noise --also-version` doesn't reach it) reused
  `loop.engine.run_backtest`/`bootstrap_fitness_distribution` directly from
  the real unflattened packages against the seed genome. Block-bootstrapped
  its own sealed-holdout return path (fresh window: -1.194 this time, not
  the prior entry's -2.566, purely from the one-day date shift) 2000 times
  across 4 RNG seeds: real fitness lands within 0.13 sigma of the bootstrap
  mean every time, and the bootstrap sigma itself (~1.77-1.85) matches the
  same range already measured for all three real champions (1.21-2.04).
  Reading: the seed genuinely performs badly on this holdout window, it
  isn't return-order noise — a genuinely bad seed on a genuinely bad window,
  correctly rejected by the gates, not a bug. Verified safe: only
  `state/cache/` (gitignored) touched, `live_state.json` md5 unchanged, full
  test suite still 223 passed (no code changed), `review-hard-calls` still 0
  pending, today's bar already processed by the 00:20 UTC run before this
  session started. No push notification — read-only research finding, zero
  effect on live trading. Still open: whether a different 4-year data pull
  would show the seed in a better light at all — bigger question, not
  attempted.

- **Done 2026-08-23 (3-hourly check, 22:16 UTC): a genuinely fresh, unscaled
  seed evolved at the live 1d cadence for the first time — 16 generations,
  zero promotions, and a mechanistic reason why.** (see "Current state"
  history and `runs/2026-08-23-2216-fresh-seed-1d-shadow-evolution.md`) Every
  prior seed-convergence test in item 2 below was at 4h bars; this is the
  first at 1d, the interval that actually trades live. Deliberately picked
  up a different open item than item 7's read-only-diagnostic thread (which
  five sessions today had already grown, per that item's own flagged
  judgment call) in favor of the "Measured 2026-08-16" section's standing
  preference for evidence over capability. Unlike every 4h fresh/scaled-seed
  run (first promotion within 1-2 generations, every time), this 1d run
  found **no promotion in 16 generations** despite 235 cumulative proposals
  and fold-aggregate fitness climbing as high as 0.885 vs. the seed's
  `-0.022` — because the seed's own sealed-holdout fitness (`-2.566`) is
  catastrophically worse than its fold-aggregate number, and
  `holdout_accepts()`'s multiple-testing margin (by design, not a bug — see
  `constitution.HOLDOUT_SIGMA`) grew from 2.355 to 4.761 across the 17
  candidates that reached it, so even the best holdout score any candidate
  ever drew (`+0.290`) fell short of what was needed. This sharpens the
  2026-08-18 "lucky champion is hard to unseat" finding into its mirror
  case: an *unlucky* seed traps itself the same way, and running more
  generations only deepens the trap (every fold-clearing proposal burns
  another draw and raises the bar) rather than resolving it. Verified safe:
  fully isolated in a scratch dir with no state file at all (no copying of
  the real `live_state.json` needed — a missing `EVO_STATE` path plus no
  `state/genomes/` in this fresh container is what produced the plain
  `SEED_GENOME` as champion v1), real `live_state.json` md5 unchanged
  (`af16ffdc22a57c5d63a83003216a8f99`) throughout, `git status` clean, no
  `state/` created under the real repo path, `review-hard-calls` checked (0
  pending), today's bar already processed by the 00:20 UTC run before this
  session started (no tick run this session). No push notification sent —
  a shadow research finding, zero effect on live trading behavior. Next:
  whether the seed's fold/holdout gap is a property of this specific
  4-year data window or a durable property of `SEED_GENOME` itself is open
  and not chased further this session (see the run note's closing
  paragraph).

- **Done 2026-08-23 (3-hourly check, 18:45 UTC): `run_from_files.py` gets its
  first slice of item 7's actual `tick` cutover — new `tick-dry-run` command
  runs the real `LiveAccount.tick()` decision pipeline (market data, Council,
  both judges, hard-call flagging) against the real files, but never calls
  `acct.save()`, so `live_state.json` is provably untouched no matter what
  the decision turns out to be.** (see module docstring in `run_from_files.py`
  and this entry) This is different in kind from the four prior read-only
  diagnostics added today (`holdout-pressure`/`regime`/`fold-dd-blindspot`
  plus the original `summary`/`signals` entrypoint): those never call
  anything that mutates broker/journal state at all; this one calls the
  exact same state-mutating method the bundle's live `tick` command calls,
  and the safety guarantee is narrower and more load-bearing — "the one line
  that writes to disk (`acct.save()`) is simply never reached" — rather than
  "nothing in the call graph writes to disk." Verified against real data:
  ran both `python3 run_from_files.py tick-dry-run` and
  `python3 evotrader_bundle.py tick` back-to-back against the live
  `live_state.json` — both correctly hit the idempotency skip path (today's
  bar was already traded by the 00:20 UTC run), both report the identical
  bar (`2026-08-22`) and tick number (`9`), and `live_state.json`'s md5
  (`af16ffdc22a57c5d63a83003216a8f99`) was unchanged after either command.
  No automated test added for `tick-dry-run` — same reasoning as
  `regime`/`fold-dd-blindspot`: `LiveAccount.tick()` calls
  `core.market.load_universe(..., refresh=True)`, which hits the network on
  a cold `state/cache`, so it stays manually-verified to keep the suite
  offline-safe; `tests/test_run_from_files_matches_bundle.py`'s docstring
  extended to explain both the network-dependency reasoning and why this
  command's stdout is deliberately NOT byte-identical to the bundle's `tick`
  (every line is prefixed `[tick-dry-run]` with an explicit "will NOT call
  acct.save()" banner, so its output can never be mistaken for a real trade
  confirmation — the parity that matters is the decision itself, not the
  exact text). `--force` deliberately not wired up here (unlike the
  bundle's `tick --force`) — forcing a repeat decision on an already-traded
  bar is a question for a human, not something this file should make easy
  under a 3-hourly schedule. Verified safe: `py_compile` clean, full suite
  still 223 passed (unchanged, matching the no-new-automated-test
  precedent), `tools/edit_bundle_module.py verify` round-trip clean, `sync
  --check` reports no drift, `live_state.json`/`evotrader.manifest`/
  `evotrader_bundle.py` md5s all unchanged from the prior entry's recorded
  values, `constitution verified 8b74865634b1db07` unchanged on every
  invocation, today's bar already processed by the 00:20 UTC daily run
  before this session started (`tick` not run for real this session, only
  the two idempotent no-op skip-path invocations above — no double-trade
  possible either way since both hit the skip guard before any mutation),
  `review-hard-calls` checked (0 pending), no genome promotion (no README
  Status change needed). No push notification sent — infrastructure work
  building toward item 7's cutover, zero effect on live trading behavior
  (nothing was saved, nothing could have been). Next: `tick-dry-run` proves
  the decision pipeline runs correctly against the real files on a skip-path
  bar; it has NOT yet been exercised on an actual untraded bar (the
  non-skip branch, which builds and prints a real would-be order list) —
  whoever next has a 3-hourly slot that starts shortly after a genuinely new
  bar closes (before the 00:20 UTC daily run has processed it) could run
  `tick-dry-run` first as an extra safety check before the real `tick`, and
  should confirm the non-skip branch's output looks sane before ever
  relying on it. The actual cutover — pointing a scheduled run at
  `run_from_files.py tick` (real, saving) instead of
  `evotrader_bundle.py tick` — remains a separate, bigger, riskier decision,
  not moved forward by this session; `evotrader_bundle.py` is still what
  every scheduled command actually executes.

- **Done 2026-08-23 (3-hourly check, 15:46 UTC): `run_from_files.py` grows a
  third read-only diagnostic — `fold-dd-blindspot` — verified byte-identical
  to `evotrader_bundle.py`'s own output, both with no flags and with
  `--also-version 2`.** (see
  `runs/2026-08-23-1548-run-from-files-fold-dd-blindspot.md`) Command body
  transcribed verbatim from the bundle's own `elif cmd ==
  "fold-dd-blindspot"` block, same discipline as the two prior diagnostics.
  This command also needed `_reconstruct_champion_genome` (the
  `--also-version N` reconstruction helper), which lives in
  `evotrader_bundle.py` as plain CLI-script code, not inside any `_SRC`
  module — so it's duplicated verbatim into `run_from_files.py` rather than
  imported; if a future session adds `succession-audit` (the other
  diagnostic that uses it) here too, that duplication is already in place.
  No automated test added — same reasoning as `regime`: this command calls
  `core.market.load_universe` (via `Evaluator`/`run_backtest`), which hits
  the network on a cold `state/cache` (gitignored), so it stays
  manually-verified to keep the suite offline-safe; `tests/
  test_run_from_files_matches_bundle.py`'s docstring updated to name both.
  Verified safe: `py_compile` clean, full suite still 223 passed (unchanged
  — no new pure function or automated test, matching `regime`'s precedent),
  `tools/edit_bundle_module.py verify` round-trip clean, `sync --check`
  reports no drift, `live_state.json` md5 unchanged throughout both manual
  runs (`af16ffdc22a57c5d63a83003216a8f99`), `evotrader.manifest` unchanged
  (`0bf3a7d9411ee692d0a9f152a7533803`), `evotrader_bundle.py` unchanged
  (`3835305b96044055bc17d43358e2bfba`), `constitution verified
  8b74865634b1db07` unchanged on every invocation, today's bar already
  processed by the 00:20 UTC daily run before this session started (`tick`
  not run this session, no double-trade), `review-hard-calls` checked (0
  pending), no genome promotion (no README Status change needed). No push
  notification sent — infrastructure/maintainability work with zero effect
  on live trading behavior, same reasoning as every prior item-7 session
  today. Next: `succession-audit` is the next candidate by the bundle's own
  documented cost class (same helper already duplicated here, just a
  heavier per-champion loop) — but the actual cutover (`tick`/`evolve`
  against the real files) remains the separate, bigger, riskier session it
  has been flagged as all day; today's read-only-surface growth (three
  sessions: `run_from_files.py` entrypoint, then two more diagnostics, now
  a third) has reached a point where whoever picks this up next should
  weigh continuing it against picking up a different open item entirely,
  same judgment call already made for the vacuous-regression-check thread
  below.

- **Done 2026-08-23 (3-hourly check): `run_from_files.py` grows two more
  read-only diagnostics — `holdout-pressure` and `regime` — verified
  byte-identical to `evotrader_bundle.py`'s own output for the same
  commands.** (see `runs/2026-08-23-1254-run-from-files-diagnostics.md`)
  Both commands' bodies are transcribed verbatim from the bundle's own
  `elif cmd == "holdout-pressure"`/`elif cmd == "regime"` blocks — not
  reimplemented. `holdout-pressure` reads only `acct.lineage` (no market
  data, no backtest, the cheapest diagnostic in the whole command table);
  `regime` does one `core.market.load_universe` call plus equal-weight
  buy-and-hold per fold/holdout window, `--interval` passthrough preserved.
  New parametrized case added to `tests/test_run_from_files_matches_bundle.py`
  for `holdout-pressure` (no network dependency, fast — suite 222 → 223
  passed). `regime` deliberately has **no** automated test: it needs a
  network market-data fetch on a cold `state/cache` (gitignored, not
  committed), which would make the whole suite's runtime and
  offline-ability depend on Binance being reachable — verified manually
  instead (bundle vs. `run_from_files.py` at both the live champion's own
  `1d` interval and `--interval 4h`: byte-identical stdout in both cases,
  `live_state.json` md5 unchanged throughout). Verified safe: `py_compile` clean, full suite 223 passed,
  `tools/edit_bundle_module.py verify` round-trip clean, `sync --check`
  reports no drift, `live_state.json` md5 unchanged
  (`af16ffdc22a57c5d63a83003216a8f99`), `evotrader.manifest` unchanged
  (`0bf3a7d9411ee692d0a9f152a7533803`), `evotrader_bundle.py` unchanged
  (`3835305b96044055bc17d43358e2bfba`), `constitution verified
  8b74865634b1db07` unchanged on every invocation, today's bar already
  processed by the 00:20 UTC daily run before this session started (`tick`
  not run this session, no double-trade), `review-hard-calls` checked (0
  pending), no genome promotion (no README Status change needed). No push
  notification sent — infrastructure/maintainability work with zero effect
  on live trading behavior, same reasoning as every prior item-7 session
  today. Next: `run_from_files.py`'s read-only surface can keep growing —
  the next cheapest candidates by the bundle's own documented cost class
  are `fold-scheme`/`rolling-folds`/`fitness-decomp`/`fold-dd-blindspot`/
  `succession-audit` (one backtest per fold, heavier than `regime` but
  still read-only) — but the actual cutover (`tick`/`evolve` against the
  real files, and the decision to ever point a scheduled run at this file)
  remains the separate, bigger, riskier session it has been flagged as all
  day.

- **Done 2026-08-23 (3-hourly check): a safe, read-only stepping stone toward
  item 7's remaining piece — a small CLI entrypoint now runs `summary` and
  `signals` against the real `core`/`agents`/`loop`/`constitution` files on
  disk instead of `evotrader_bundle.py`'s embedded copy, verified
  byte-for-byte identical to the bundle's own output for the same commands
  against the same `live_state.json`.** (see
  `runs/2026-08-23-0946-run-from-files-entrypoint.md`) New `run_from_files.py`
  at the repo root: imports `constitution`/`core.live.LiveAccount` directly
  (normal Python import, no meta-path finder involved — that only gets
  installed by importing `evotrader_bundle`, which this file deliberately
  never does), calls `verify()` the same way `evotrader_bundle.main()` does
  but *without* populating `constitution.EMBEDDED_SOURCES`, so
  `constitution.checksum()` takes its dormant file-based branch and hashes
  the real `constitution/__init__.py` + `core/portfolio.py` on disk — the
  same branch the weekend all-hands session first exercised, confirmed again
  here to reproduce `evotrader.manifest`'s `8b74865634b1db07` exactly.
  Deliberately supports only `summary` and `signals` — the two commands that
  never call `acct.save()` — and exits 1 with an explanatory message on
  anything else (`tick`/`evolve`/...); wiring up state-mutating commands and
  deciding whether any scheduled run should ever point at this file instead
  of the bundle remains the separate, bigger, riskier session item 7's own
  text has flagged three sessions running now, not attempted here. New
  `tests/test_run_from_files_matches_bundle.py` (3 tests, suite 219 → 222):
  runs both entrypoints as subprocesses (deliberately never imported in the
  same interpreter as the bundle-importing test suite, to avoid the
  meta-path finder and the real on-disk packages fighting over the same
  module names) and asserts `summary`/`signals` stdout is byte-identical
  between `run_from_files.py` and `evotrader_bundle.py`, plus that
  `live_state.json` is provably unmodified by either read-only command, plus
  a rejection test for an unsupported command. Verified against real data,
  not just the new tests: `python3 run_from_files.py summary`/`signals` run
  directly against the live `live_state.json`, output eyeballed line-for-line
  identical to `evotrader_bundle.py`'s own output for the same commands.
  Verified safe: `py_compile` clean on both new files, full suite 222
  passed, `tools/edit_bundle_module.py verify` round-trip clean, `sync
  --check` still reports no drift, `git status` confirms a pure addition
  (two new untracked files, zero existing lines touched), `live_state.json`
  md5 unchanged (`af16ffdc22a57c5d63a83003216a8f99`), `evotrader.manifest`
  md5 unchanged (`0bf3a7d9411ee692d0a9f152a7533803`), `evotrader_bundle.py`
  md5 unchanged (`3835305b96044055bc17d43358e2bfba`), `constitution verified
  8b74865634b1db07` unchanged on every invocation, today's 2026-08-23 bar
  confirmed already processed by the 00:20 UTC daily run before this session
  started (`tick` not run this session, no double-trade), `review-hard-calls`
  checked (0 pending), no genome promotion (no README Status change needed).
  No push notification sent — infrastructure/maintainability work with zero
  effect on live trading behavior, same reasoning as the bundler-sync
  session earlier today. Next: item 7's actual cutover still needs
  `tick`/`evolve` wired up against the real files (the state-mutating half,
  meaningfully riskier — a bug here could double-trade or corrupt
  `live_state.json`, unlike a read-only command) and a real decision about
  whether/when a scheduled run should ever point at `run_from_files.py`
  instead of `evotrader_bundle.py` — both still explicitly out of scope for
  a single 3-hourly slot.

- **Done 2026-08-23 (3-hourly check): the bundler half of item 7's remaining
  gap — `evotrader_bundle.py` can now be regenerated from the real
  `core`/`agents`/`loop`/`constitution` files, not just checked for drift
  against them.** (see `runs/2026-08-23-0648-bundle-sync-tool.md`) New
  `sync [--check]` command on `tools/edit_bundle_module.py`: `sync_from_files
  (bundle_text, root)` walks every `_SRC` module and replaces its entry with
  the current content of its corresponding real file (the reverse of
  `extract`) — the real files are now the source of truth for this
  direction. `pkgs`/`module_to_path`, previously private to
  `tests/test_unflattened_files_match_bundle.py`, moved onto
  `tools/edit_bundle_module.py` itself (parameterized by `root` instead of a
  module global) so both the test and the new `sync` share one
  implementation instead of two copies that could themselves drift; the test
  file now imports them, no behavior change. New
  `tests/test_bundle_sync_from_files.py` (10 tests, suite 209 → 219):
  synthetic-tree unit tests via `tmp_path` (package-vs-module path mapping,
  drift pulled in, already-in-sync is a true no-op, missing file raises
  `FileNotFoundError` naming the module) plus one real-repo test confirming
  `sync_from_files` against the actual bundle/tree is a no-op today. Verified
  against real data, not just the synthetic cases: `sync --check` on the
  real repo reports no drift and exits 0; `sync` in write mode leaves
  `evotrader_bundle.py`'s md5 unchanged
  (`3835305b96044055bc17d43358e2bfba`, matching the weekend session's
  recorded value); a deliberately-induced one-line edit to `core/types.py`
  made `sync --check` correctly report `DRIFT`/exit 1, then was reverted
  (`git status` clean afterward) — proves the check path isn't vacuously
  always-pass. `tools/edit_bundle_module.py verify` (pre-existing
  round-trip) still clean, `py_compile` clean, full suite 219 passed,
  `live_state.json` md5 unchanged (`af16ffdc22a57c5d63a83003216a8f99`),
  `evotrader.manifest` unchanged (`0bf3a7d9411ee692d0a9f152a7533803`),
  `constitution verified 8b74865634b1db07` unchanged, today's bar already
  processed by the 00:20 UTC daily run before this session started (`tick`
  not run), `review-hard-calls` checked (0 pending), no genome promotion (no
  README Status change needed). No push notification sent —
  infrastructure/maintainability work with zero effect on live trading
  behavior. **Still open, item 7's last remaining piece**: no CLI entrypoint
  runs the live commands (`tick`/`summary`/`evolve`/...) against the real
  files instead of the bundle — that's the actual cutover, a bigger and
  riskier separate session; `evotrader_bundle.py` remains the live path,
  untouched by this session.

- **Done 2026-08-23 (weekend all-hands): item 7's unflatten, the piece that's real work — a byte-identical, normally-importable copy of every `evotrader_bundle.py` module now exists on disk as real files, verified equivalent by re-running the entire test suite against them, without ever touching the live path.** (see
  `runs/2026-08-23-0600-weekend-all-hands.md`) Per item 7's own instructions
  ("do it as its own isolated commit, keep the bundle working as a fallback
  until the unflattened version is proven equivalent... don't switch the live
  trading path until confident"): extracted all 15 `_SRC` modules with the
  already-built `tools/edit_bundle_module.py extract` and laid them out as
  four real top-level packages — `core/`, `agents/`, `loop/`,
  `constitution/` — mirroring exactly the dotted names the bundle already
  installs at runtime (`core.genome` → `core/genome.py`, the four package
  names in `_PKGS` → `<pkg>/__init__.py`). This wasn't a guess at a layout:
  `constitution/__init__.py`'s own `checksum()` function already had a
  dormant file-based mode (`_PROTECTED = ["__init__.py", "../core/portfolio.py"]`,
  hashing real files by relative path) sitting next to its bundle-mode path
  (hashing `EMBEDDED_SOURCES` strings) — nobody had ever exercised the
  file-based branch because no real files existed yet. Every module's
  imports are already absolute (`from core.genome import Genome`, etc.) and
  every `__file__`-dependent path constant (`GENOME_DIR`, `STATE_DIR`,
  `CACHE_DIR`, `ROOT`) resolves two directories up from the module file,
  which lands on the repo root under a real `<pkg>/<module>.py` layout the
  same way it lands on the bundle's faked `"core/genome.py"`-relative-to-cwd
  path under the bundle — so nothing needed rewriting, only faithful
  extraction. Verified three independent ways: (1) `constitution.checksum()`
  in file mode, run against the real files, reproduces `evotrader.manifest`'s
  recorded `8b74865634b1db07` exactly; (2) the entire existing test suite
  (192 tests, unmodified, copied to a scratch dir with a conftest that
  imports the real packages directly instead of `evotrader_bundle` — no
  meta-path finder involved) passes 192/192 against the real files, matching
  the bundle-sourced baseline exactly; (3) new
  `tests/test_unflattened_files_match_bundle.py` (17 new tests, suite 192 →
  209) asserts every real file is byte-identical to its `_SRC[...]` entry and
  that the two trees have identical shape (no stray or missing files), so
  future drift between the two copies fails loud instead of silently, the
  same tripwire principle as `edit_bundle_module.py verify`. **Deliberately
  not done this session, and not implied by "done" above**: there is still no
  bundler to regenerate `evotrader_bundle.py` *from* these real files (the
  bundle's own docstring says "generated by bundle.py", but no `bundle.py`
  exists in this repo — that generator, if it ever existed, is gone), no CLI
  entrypoint that runs the live commands against the real files instead of
  the bundle, and nothing about the live trading path changed at all —
  `evotrader_bundle.py` is byte-identical before/after
  (`3835305b96044055bc17d43358e2bfba`), still what every scheduled command
  actually executes. This closes the safe half of item 7 (a real, provably
  equivalent multi-file tree exists) and leaves the risky half (actually
  switching what runs) explicitly for later, same as item 7's own text
  said to. Verified safe: `py_compile` clean on all 16 new files plus the
  bundle plus the new test, `tools/edit_bundle_module.py verify` round-trip
  clean, `git diff --stat` against every tracked file empty (pure addition —
  four new untracked directories plus one new test file, zero existing lines
  touched), `live_state.json` md5 unchanged (`af16ffdc22a57c5d63a83003216a8f99`),
  `evotrader.manifest` unchanged (`0bf3a7d9411ee692d0a9f152a7533803`),
  `constitution verified 8b74865634b1db07` unchanged, today's bar already
  processed by the 00:20 UTC daily run before this session started (`tick`
  not run this session), `review-hard-calls` checked (0 pending), no genome
  promotion (no README Status change needed, no AMENDMENTS.md row needed —
  no constitution content changed, only a second copy of it created and
  proven identical). No push notification sent — a structural/maintainability
  improvement with zero effect on live behavior, not a safety finding or a
  promotion. Next: whoever wants to actually retire the bundle needs (a) a
  real bundler script (`_SRC` dict generation from the real files, the
  reverse of what this session did by hand) so the two trees can't drift
  once someone starts editing the real files directly instead of through
  `edit_bundle_module.py`, and (b) a CLI entrypoint exercising the real
  files end-to-end (tick/summary/evolve/etc., not just imports and unit
  tests) before ever pointing a scheduled run at it instead of the bundle —
  both bigger, riskier, separate sessions, not a quick follow-on to this one.

- **Tested 2026-08-23 (3-hourly check): the 2026-08-16 "bad buyer, excellent
  seller" `consult_conservative` finding, unactioned for a week, turns out to
  be genome-dependent rather than a fixed law — and for the current live
  champion specifically, already a non-issue.** (see
  `runs/2026-08-23-0352-consult-role-test-diagnostic.md`) New read-only CLI
  `consult-role-test [--also-version N]` monkeypatches
  `ConservativeConsult.consider` to strip its buy intents for one extra
  full-history `run_backtest` call (its sell rule left untouched), restores
  the original method immediately after, never persists anything — composes
  only already-tested `run_backtest`/`benchmark_buy_hold`/`fitness`/
  `_reconstruct_champion_genome`, same diagnostic-only precedent as every
  other CLI command in this file. Tested against all three real champions:
  **v1** (the seed) gets *worse* with conservative's entries suppressed
  (return -11.8% → -34.4%, maxDD -54.3% → -65.2%) — the opposite direction
  the 08-16 finding's framing would predict, a reminder that a per-trade P&L
  attribution and a counterfactual full replay are different questions.
  **v2** improves sharply (fitness 0.183 → 0.584, maxDD -38.1% → -29.9%,
  return +37.9% → +76.8%, trade count actually rising slightly rather than
  falling) — real evidence the 08-16 finding pointed at something genuine,
  at least for that genome. **v3, the live champion**, is essentially flat:
  4 fewer trades out of 1069, fitness/maxDD/return unchanged to the
  precision reported. Reading: v3's own entry-gate genes
  (`rsi_buy_below`/`z_buy_below`/`max_dd_from_high`) have already been tuned
  tight enough by 13+ generations of unrelated search that
  `consult_conservative` rarely fires as an entry signal at all any more —
  the bad-buyer problem looks like it was search-corrected as a side effect,
  not by any gene that models "this consult should be exit-only." Verified
  safe: `py_compile` clean, `tools/edit_bundle_module.py verify` round-trip
  clean, `git diff --stat` confirms a pure addition (84 insertions, 0
  deletions, zero `_SRC[...]` lines touched), full suite still 192 passed
  (unchanged — no new pure function, just a CLI command composing existing
  ones), `live_state.json` md5 identical throughout
  (`af16ffdc22a57c5d63a83003216a8f99`), `evotrader.manifest` md5 unchanged
  (`0bf3a7d9411ee692d0a9f152a7533803`), `constitution verified
  8b74865634b1db07` unchanged on every invocation, today's 2026-08-23 bar
  confirmed already processed by the 00:20 UTC daily run before this session
  started (`tick` not run this session, no double-trade), `review-hard-calls`
  checked (0 pending), no genome promotion (no README Status change needed).
  No push notification sent — exploratory evidence on an unactioned finding,
  not a safety issue or an incorrect promotion. Next: not worth building a
  real `entry_enabled`/exit-only gene for v3 right now given the near-zero
  delta — but if a future accepted promotion ever re-widens
  `consult_conservative`'s entry gate, re-running `consult-role-test` at that
  point is a one-line check for whether the problem has come back. See "Next
  steps" item 8.

- **Measured 2026-08-23 (3-hourly check): a fifth round of the
  vacuous-regression-check tracking — one more vacuous-accept flip, pulling
  the combined rate down slightly to 6/279 (≈2.15%), still no incorrect
  promotion.** (see `runs/2026-08-23-0046-shadow-evolve-vacuous-check-round5.md`)
  Same scratch-isolation discipline as every prior shadow-evolve session
  (`live_state.json` md5 unchanged throughout, `af16ffdc22a57c5d63a83003216a8f99`),
  same diagnostic-script method as the four prior entries (reimplements
  `EvolutionRun.generation()`'s real top-3 loop verbatim for the NEW
  dd-corrected path, also computes what OLD raw fold-merged `accepts()`
  would have decided on the same candidate, not committed — diagnostic-only,
  composes already-tested `Evaluator.evaluate`/`dd_corrected_stats`/
  `constitution.accepts`). Smoke-tested at 1 generation before the full run
  this time (95s, real file md5 unchanged) — first round to do that check
  explicitly before committing wall-clock to the full run. 25 generations run
  to completion (~40 minutes, faster per-generation than prior rounds —
  ~93-99s vs ~142-166s, likely because this session's larger
  `researcher_memory` seed left `Researcher.propose` less new ground to
  cover), champion held throughout, no promotion shadow or otherwise. **75
  top-3 candidates reached the gate, 32 reached the sealed holdout (all
  correctly rejected), and one showed the vacuous-accept flip** (generation
  3, a clean textbook case: champion's OLD merged max_dd -38.8% gives a
  finite fitness that correctly catches the challenger's merged-fitness
  regression, while NEW's dd-corrected -46.5% makes `fitness(champion) ==
  -inf` and the same check becomes vacuously true) — no intended-tightening
  flip this round. Combined across all five sessions on this thread (four on
  2026-08-22, this one on 2026-08-23): **6/279 real shadow candidates
  (≈2.15%) have shown the vacuous-accept flip** (session counts 2, 0, 3, 0,
  1) and **1/279 (≈0.36%) the intended-tightening flip**. Verified safe: no
  code changed (diagnostic script only, not committed), `live_state.json`
  md5 identical throughout, `evotrader.manifest` untouched, `constitution
  verified 8b74865634b1db07` unchanged on every invocation, today's
  2026-08-23 bar confirmed already processed by the 00:20 UTC daily run
  before this session started (`tick` not run this session, no
  double-trade), `review-hard-calls` checked (0 pending), no genome
  promotion (no README Status change needed). No push notification sent —
  this round narrows rather than changes the already-fully-communicated
  mechanism and severity from the 2026-08-22 10:15 session. Next: the
  combined rate is now 6/279 (≈2.15%), not round 4's 5/204 — cite the
  updated figure. Given this thread now spans five sessions and 279
  candidates without the per-session rate (2, 0, 3, 0, 1) settling to
  something worth anchoring on, and each round costs ~40-90 minutes for one
  marginal data point, whoever next picks this up should weigh another
  round of the same measurement against picking up a different open item
  (the 4h-bar third-plateau question, or item 7's unflatten work) rather
  than treating another round as automatically the highest-value use of a
  session. The demotion/rollback design question itself remains unstarted
  and is still explicitly the owner's call.

- **Measured 2026-08-22 (3-hourly check): a fourth round of the
  vacuous-regression-check tracking, and it pulls the combined rate back
  down — the second zero-flip session out of four, not a continuation of the
  previous round's higher count.** (see
  `runs/2026-08-22-2240-shadow-evolve-vacuous-check-round4.md`) Same
  scratch-isolation discipline as every prior shadow-evolve session
  (`live_state.json` md5 unchanged throughout,
  `3f71d6ab111ecd646eda9e0e595a9970`), same diagnostic-script method as the
  three prior entries (reimplements `EvolutionRun.generation()`'s real top-3
  loop verbatim for the NEW dd-corrected path, also computes what OLD raw
  fold-merged `accepts()` would have decided on the same candidate, not
  committed — diagnostic-only, composes already-tested
  `Evaluator.evaluate`/`dd_corrected_stats`/`constitution.accepts`). 20
  generations run to completion (~49 minutes), champion held throughout, no
  promotion shadow or otherwise. **60 top-3 candidates reached the gate, 13
  reached the sealed holdout (all correctly rejected), and zero showed either
  kind of accept/reject flip** — no vacuous-accept (OLD rejects, NEW accepts)
  and no intended-tightening (OLD accepts, NEW rejects) this round. Combined
  across all four of today's sessions: **5/204 real shadow candidates
  (≈2.5%) have shown the vacuous-accept flip** (session counts 2, 0, 3, 0)
  and **1/204 (≈0.5%) the intended-tightening flip** — this session's zero
  pulls the previous entry's 5/144 (≈3.5%) figure back down toward roughly
  half that, reinforcing "real but noisy background rate" over either "fires
  every generation" or "was a one-off." No incorrect promotion resulted, same
  as every prior round. Verified safe: no code changed (diagnostic script
  only, not committed), `live_state.json` md5 identical throughout,
  `evotrader.manifest` untouched, `constitution verified 8b74865634b1db07`
  unchanged on every invocation, today's 2026-08-22 bar confirmed already
  processed by the 00:20 UTC daily run before this session started (`tick`
  not run this session, no double-trade), `review-hard-calls` checked (0
  pending), no genome promotion (no README Status change needed). No push
  notification sent — this round narrows rather than changes the
  already-fully-communicated mechanism and severity from the 10:15 session.
  Next: the combined rate is now 5/204 (≈2.5%), not 16:29's 5/144 — cite the
  updated figure. The per-session counts (2, 0, 3, 0) are still noisy enough
  that this isn't a number to anchor on; whoever next runs shadow or real
  evolution against v3 should keep adding to the cumulative sample. The
  demotion/rollback design question itself remains unstarted and is still
  explicitly the owner's call.

- **Built 2026-08-22 (3-hourly check): new `succession-audit` diagnostic
  answers a fact the demotion/rollback thread had flagged across four
  sessions today without ever asking — would the *other* two real champions
  even pass today's dd-corrected drawdown gate if reinstated — and the
  answer sharpens rather than resolves the open question: no, none of the
  three do, each for a different reason.** (see
  `runs/2026-08-22-1854-succession-audit-diagnostic.md`) New read-only CLI
  reports, for every real champion this account has had (v1/v2/v3,
  discovered from `acct.lineage`'s own accepted-promotion records via the
  already-tested `_reconstruct_champion_genome`): fold-aggregate fitness a
  fresh `Evaluator.evaluate()` would give it today, the dd-corrected
  fold-merged fitness `accepts()` actually gates a real promotion decision
  on, and the true continuous full-history maxDD/fitness. v1 and v3 fail
  outright even on the simple full-history number (-54.4%/-46.5%, both over
  `MAX_DD_HARD_FAIL`). **v2 is the interesting case**: its true full-history
  maxDD is -38.1%, under the 40% line — looks like a clean reinstatement
  candidate by that number alone — but its fold-merged maxDD is -40.1%,
  driven entirely by fold 2's own independently-backtested local
  peak-to-trough (each fold's NAV rebases to a fresh peak at its boundary, so
  a decline that's a modest fraction of a long-accumulated continuous peak
  becomes a much larger fraction of the lower, freshly-reset local peak).
  `dd_corrected_stats()` takes `min(fold-merged, continuous)` by design ("can
  only tighten the gate, never loosen it" — see the weekend all-hands entry
  below) — so when fold-merged *overstates* the true drawdown (the opposite
  direction from the original `fold-dd-blindspot` bug, which was fold-merged
  *understating* a drawdown spanning a fold boundary), the correction has no
  mechanism to recover the truer, better continuous number; it only ever
  keeps or worsens a pessimistic fold-local read. Net: v2 also hard-fails the
  gate a real promotion decision would actually use, for a reason invisible
  to the full-history number alone. Composes only already-tested
  `_reconstruct_champion_genome`/`Evaluator.evaluate`/`dd_corrected_stats`/
  `run_backtest` — no engine or constitution change, no new pure function, no
  new test file, same precedent as every other diagnostic in this file.
  Verified safe: `py_compile` clean, `tools/edit_bundle_module.py verify`
  round-trip clean, `git diff --stat` confirms a pure addition to the
  plain-script CLI section (73 insertions, 0 deletions besides the one-line
  help-text addition, zero `_SRC[...]` lines touched), full suite still 192
  passed (unchanged), `live_state.json` md5 identical throughout
  (`3f71d6ab111ecd646eda9e0e595a9970`), `evotrader.manifest` md5 unchanged
  (`0bf3a7d9411ee692d0a9f152a7533803`), `constitution verified
  8b74865634b1db07` unchanged on every invocation, today's 2026-08-22 bar
  confirmed already processed by the 00:20 UTC daily run before this session
  started (`tick` not run this session, no double-trade), `review-hard-calls`
  checked (0 pending), no genome promotion (no README Status change needed).
  No push notification sent — sharpens an already-flagged open question with
  a concrete new mechanism, doesn't raise new urgency or reveal an incorrect
  promotion. Next: this is the fact base to start from if the owner opens the
  demotion/rollback design pass — no real champion currently has a clean
  pass, and "revert to v2" specifically is not the easy fix it might look
  like from the full-history number alone. Separately, `dd_corrected_stats()`
  is now known to have a one-directional blind spot of its own (can't loosen
  an overstated fold-local number toward a truer continuous one) — not urgent
  (the overstated direction is conservative, not unsafe) but worth noting if
  anyone revisits that function.

- **Measured 2026-08-22 (3-hourly check): a third round of the
  vacuous-regression-check tracking, and it reverses the previous entry's
  "tempering" read — 20 more shadow generations, 60 more top-3 candidates,
  3 more vacuous-accept flips (the highest single-session count yet), plus
  the first-ever case of the intended tightening actually changing an
  outcome.** (see `runs/2026-08-22-1629-shadow-evolve-vacuous-check-round3.md`)
  Same scratch-isolation discipline as every prior shadow-evolve session
  (`live_state.json` md5 unchanged throughout,
  `3f71d6ab111ecd646eda9e0e595a9970`), same diagnostic-script method as the
  previous two entries (reimplements `EvolutionRun.generation()`'s real top-3
  loop verbatim for the NEW dd-corrected path, also computes what OLD raw
  fold-merged `accepts()` would have decided on the same candidate, not
  committed — diagnostic-only, composes already-tested
  `Evaluator.evaluate`/`dd_corrected_stats`/`constitution.accepts`). Champion
  held all 20 generations, no promotion shadow or otherwise. Of 60 top-3
  candidates that reached the gate this round: **3 showed the vacuous-accept
  pattern** (OLD rejects, NEW accepts — `f_champ == -inf` from champion v3's
  own -46.5% dd-corrected max_dd vacuously passing the merged-fitness-regression
  check, or loosening the drawdown-regression-tolerance check against the same
  much-worse baseline; generations 3, 8, 17) and **1 showed the opposite,
  intended-tightening flip** (OLD accepts, NEW rejects — generation 15's
  candidate had raw max_dd 31.8%, dd-corrected 41.3%, over
  `MAX_DD_HARD_FAIL`; this is the first time across 144 candidates sampled
  today that this direction was the actual reason for a rejection, not a moot
  side observation next to an independent margin rejection). Combined across
  all three of today's sessions: **5/144 real shadow candidates (≈3.5%) have
  now shown the vacuous-accept flip**, session counts 2/30, 0/54, 3/60 — a
  noisy but non-vanishing per-session rate (2, 0, 3), which reverses the
  13:22 session's "occasional, not consistent" tempering back toward "real,
  non-trivial background rate" without settling on an exact number. No
  incorrect promotion resulted this session either — all candidates that
  reached the sealed holdout via either accept path were correctly rejected
  there. No push notification sent — the mechanism and its severity were
  already fully communicated by the 10:15 session; this sharpens the
  cumulative rate and adds one favorable data point (intended tightening
  doing real work) but doesn't raise new urgency. Verified safe: no code
  changed (diagnostic script only, not committed), `live_state.json` md5
  identical throughout, `evotrader.manifest` untouched, `constitution
  verified 8b74865634b1db07` unchanged on every invocation, today's
  2026-08-22 bar confirmed already processed by the 00:20 UTC daily run
  before this session started (`tick` not run this session, no
  double-trade), `review-hard-calls` checked (0 pending), no genome
  promotion (no README Status change needed). Next: the vacuous-regression-
  check rate is now measured at 5/144 across three sessions in one day — the
  per-session variance (2, 0, 3) means the cumulative rate is still worth
  tracking further rather than treating today's total as final; whoever next
  runs shadow or real evolution against v3 should keep adding to it. The
  demotion/rollback design question itself remains unstarted and is still
  explicitly the owner's call.

- **Measured 2026-08-22 (3-hourly check): a second, larger round of the
  vacuous-regression-check tracking the previous entry asked for — 18 more
  shadow generations, 54 more top-3 candidates, and this round found zero
  further occurrences of the pattern.** (see
  `runs/2026-08-22-1322-shadow-evolve-vacuous-check-round2.md`) Same
  scratch-isolation discipline as every prior shadow-evolve session
  (`live_state.json` md5 unchanged throughout,
  `3f71d6ab111ecd646eda9e0e595a9970`), same diagnostic-script method as the
  previous entry (reimplements `EvolutionRun.generation()`'s real top-3 loop
  verbatim for the NEW dd-corrected path, also computes what OLD raw
  fold-merged `accepts()` would have decided on the same candidate, not
  committed — diagnostic-only, composes already-tested
  `Evaluator.evaluate`/`dd_corrected_stats`/`constitution.accepts`). Champion
  held all 18 generations (best fold-aggregate fitness seen: 1.886,
  generation 16, still short of margin at 434 cumulative candidates). Of 54
  top-3 candidates that reached the gate: **0 showed either kind of
  accept/reject flip** — no instance of the intended tightening (OLD
  accepts, NEW rejects) and, unlike the previous session's 2/30, **no further
  instance of the vacuous-accept bug (OLD rejects, NEW accepts) either**.
  Combined across both sessions: 2/84 real shadow candidates have shown the
  vacuous-accept pattern, both from the prior session — one session finding
  it and a larger follow-up session not finding it is evidence the mechanism
  is real but occasional, not a fires-every-generation certainty, which
  tempers (without resolving) the prior entry's "if it does so consistently"
  escalation condition. Separately, this larger sample surfaced a new,
  previously-undocumented variant worth naming: **2/54 candidates
  hard-failed under the NEW dd-corrected max_dd (41.7%/41.3%) while their
  raw uncorrected max_dd was still under 40% (39.0%/32.5%)** — the first
  time either session's sample showed the corrected gate catching a real
  drawdown OLD's number would have missed, though in both cases the
  fold-aggregate margin check already rejected the candidate independently,
  so it never became the deciding factor. 8/54 candidates cleared the
  fold-aggregate gate identically under both OLD and NEW and reached the
  sealed holdout; all 8 were correctly rejected there (consistent with
  `holdout-pressure`'s standing finding). No incorrect promotion resulted,
  same as the prior session. Verified safe: no code changed (diagnostic
  script only, not committed), `live_state.json` md5 identical throughout,
  `evotrader.manifest` untouched, `constitution verified 8b74865634b1db07`
  unchanged on every invocation, today's 2026-08-22 bar confirmed already
  processed by the 00:20 UTC daily run before this session started (`tick`
  not run this session, no double-trade), `review-hard-calls` checked (0
  pending), no genome promotion (no README Status change needed). No push
  notification sent — this finding sharpens but doesn't change the practical
  severity/urgency of the already-communicated open v3 demotion question, and
  no incorrect promotion occurred, same reasoning the prior session used.
  Next: the vacuous-regression-check rate is now measured at 2/84 across two
  sessions, not per-generation — whoever next runs shadow or real evolution
  against v3 should keep adding to this cumulative sample rather than
  treating either session's count as final; the demotion/rollback design
  question itself remains unstarted and is still explicitly the owner's
  call.

- **Found 2026-08-22 (3-hourly check): the weekend all-hands dd-corrected gate
  doesn't just tighten promotion checks — while champion v3 remains champion,
  it also permanently disables one of `accepts()`'s two champion-relative
  safety checks and loosens the other, confirmed firing for real inside live
  shadow generations, not just as a traced-through hypothetical.** (see
  `runs/2026-08-22-1015-dd-gate-vacuous-regression-check.md`) Per the weekend
  all-hands note's own "Next" ask — note whether the new gate changes a real
  promotion outcome — ran 10 more shadow-evolve generations against an
  isolated scratch copy of `live_state.json` (same discipline as every prior
  shadow session, real file md5 unchanged throughout,
  `3f71d6ab111ecd646eda9e0e595a9970`), then cross-checked all 30 top-3
  fold-ranked candidates `accepts()` actually ran through this session under
  both the OLD (fold-merged-only) and NEW (dd-corrected) stats. 0/30 showed
  the intended tightening effect flip a fold-aggregate decision in this
  sample. **2/30 (generations 9, 10) showed the opposite**: OLD rejects
  ("merged fitness regressed"), NEW accepts. Root cause, verified against
  `constitution.accepts()`'s actual source: `f_champ = fitness(champion)`
  reads `-inf` because champion v3's own dd-corrected max_dd (-46.5%) is
  itself over `MAX_DD_HARD_FAIL` — so the `f_chal < f_champ` "merged fitness
  regressed" check can never fire (no finite value is `< -inf`), and the
  separate drawdown-regression-tolerance check (`dd_chal > dd_champ * 1.15`)
  is checked against the same much-worse baseline (~53.5% tolerance instead
  of ~39.2%). Both generation-9/10 candidates rode this vacuous path to the
  sealed holdout and were correctly rejected there — **no incorrect
  promotion resulted** — but each such pass consumes one of the cumulative,
  never-reset sealed-holdout draws `HOLDOUT_SIGMA`'s design deliberately
  never gives back, at the same time `margin-curve` (2026-08-21) already
  showed that margin is nowhere near saturated and every extra draw visibly
  raises the bar for the next real candidate. Net effect: for as long as v3
  remains champion, the fold-aggregate gate admits more candidates to the
  scarce holdout check than a healthy champion's intact regression checks
  would, the opposite of what tightening was supposed to do to overall
  promotion difficulty — even though no single challenger evaluation is
  dishonest. Sharpens, does not reverse, the fold-dd-blindspot fix: the
  per-challenger hard-fail/drawdown checks are still strictly more honest
  than before. No code changed this session (diagnostic script only, not
  committed — composes already-tested `Evaluator.evaluate`/
  `dd_corrected_stats`/`constitution.accepts`, no new pure function needed).
  Verified safe: `live_state.json` md5 identical throughout, `evotrader.manifest`
  untouched, `constitution verified 8b74865634b1db07` unchanged on every
  invocation, today's 2026-08-22 bar confirmed already processed by the
  00:20 UTC daily run before this session started (`tick` not run this
  session, no double-trade), `review-hard-calls` checked (0 pending), no
  genome promotion (no README Status change needed). Separately: this
  morning's 09:00 UTC daily-discussion run note flagged the still-open v3
  demotion question for owner attention but, unlike the two prior sessions
  covering the same thread, had no "push notification sent" record — this
  session sent one, since it looked like a real gap rather than a
  deliberate skip. Next: whoever next runs shadow or real evolution against
  v3 should keep tracking whether this vacuous-regression-check pattern
  keeps consuming extra holdout draws generation after generation — if it
  does so consistently, that sharpens the case for prioritizing the
  demotion/rollback design pass sooner. The mechanism needs no code fix of
  its own; it resolves automatically once/if a healthy champion (own
  corrected max_dd within 40%) is back in place, which is the owner's call
  per the "no rollback mechanism exists yet" note below.

- **Fixed 2026-08-22 (weekend all-hands): the design pass this file deferred
  twice — how `MAX_DD_HARD_FAIL`'s merged max_dd should actually be computed —
  is done. `EvolutionRun.generation()`'s promotion gate now closes the
  fold-boundary blind spot `fold-dd-blindspot` found the same day.** (see
  `runs/2026-08-22-0600-weekend-all-hands.md`, `AMENDMENTS.md`) New
  `Evaluator.continuous_max_dd(g, folds=None)` runs one unbroken `run_backtest`
  over the full fold-covered span; new `loop.evolve.dd_corrected_stats(evaluator,
  g, stats, folds=None)` returns a copy of a stats dict with `max_dd` replaced
  by the worse (more negative) of its own value and that continuous replay —
  `min()`, so the fix can only tighten the gate, never loosen it, and a failed
  or empty continuous replay falls back unchanged rather than blocking a
  promotion on missing data. `EvolutionRun.generation()` applies this to both
  champion and challenger stats immediately before the `accepts()` call that
  actually decides promotion — the one place a real drawdown-gate decision gets
  made — not inside `Evaluator.evaluate()` itself, so the per-candidate
  search/ranking cost paid every generation (tens of candidates) is
  completely unchanged; only the up-to-3 candidates per generation that already cleared
  fold-aggregate ranking and reached the real promotion decision pay for the
  extra continuous-replay backtest, with the champion's own check cached once
  per generation. Deliberately does not touch `Evaluator.evaluate()`'s own
  fold-local max_dd or any of the diagnostics built on it (`fold-scheme`,
  `rolling-folds`, `regime-folds`, `fold-dd-blindspot` itself, ...) — those
  measure fold-windowing effects specifically, and folding the continuous
  number into their own numbers would have confused what they measure, not
  clarified it. Verified against real data, not just synthetic tests: loaded
  the live champion's actual market universe and confirmed
  `dd_corrected_stats` reproduces `fold-dd-blindspot`'s own numbers exactly
  (v3: fold-merged -34.1% -> dd-corrected -46.5%). A 3-generation shadow
  `evolve` run against an isolated scratch copy of `live_state.json` (same
  discipline as every prior shadow-evolve session — never touches the real
  file, `live_state.json` md5 identical before/after) confirmed the full
  pipeline runs end-to-end with the new gate wired into the real decision
  path: generation 3's top candidate (fold-aggregate fitness 1.638) cleared
  the selection margin (champion 1.126 + 0.263) AND the new dd-corrected
  `accepts()` check, reaching the sealed holdout, where it was correctly
  rejected there instead (`-2.237` vs champion `-0.178` + margin `4.595`) —
  proof the new gate doesn't just block everything, a real candidate can
  still pass it. Separately, one candidate in generation 1 was rejected with
  `"challenger failed a hard gate (too few trades, too short, or drawdown >
  40%)"` — the exact `f_chal == -inf` path the fix touches — confirming the
  corrected hard-fail check fires for real, not just in the unit tests.
  Champion held all 3 generations (no promotion, shadow or otherwise).
  **Practical
  consequence, observed directly and left as a documented open question, not
  acted on**: champion v3's own corrected max_dd (-46.5%) already exceeds
  `MAX_DD_HARD_FAIL`, so `fitness(champion)` now reads -inf inside `accepts()`
  for as long as v3 remains champion — traced through and confirmed harmless
  to the mechanics that matter (`f_champ == -inf` only affects the
  merged-fitness-regression check, which becomes vacuously true since no
  finite challenger fitness is ever `< -inf`; promotion still correctly
  requires a challenger to independently clear its own corrected
  `MAX_DD_HARD_FAIL` and the drawdown-regression tolerance measured against
  champion's now-honest, worse baseline dd_champ). Whether v3 itself should be
  demoted or re-evolved now that its true drawdown is visible is explicitly
  NOT decided by this change — no rollback/demotion mechanism exists in this
  codebase yet, and picking what replaces a demoted champion (revert to v2? a
  fresh search from the seed?) is its own design question, not a quick
  follow-on to a gate fix. README.md's `## Status` section updated with a
  transparency note about this (not a genome-version-triggered update, since
  no promotion happened this session, but a real, publicly-relevant fact about
  the live champion's risk profile). Verified safe: `tests/test_continuous_max_dd.py`
  (8 new tests, full suite 192 passed up from 184), `py_compile` clean,
  `tools/edit_bundle_module.py verify` round-trip clean, `git diff --stat`
  confirms a pure single-line `_SRC['loop.evolve']` change (no other module
  touched), `live_state.json` md5 unchanged throughout
  (`3f71d6ab111ecd646eda9e0e595a9970`), `evotrader.manifest` md5 unchanged
  (`0bf3a7d9411ee692d0a9f152a7533803` — `loop.evolve` isn't part of the
  checksummed surface, same as every prior fold-scheme/margin-curve/
  regime-folds diagnostic that touched this module), `constitution verified
  8b74865634b1db07` unchanged on every invocation, `AMENDMENTS.md` row added
  in the same commit (mandatory for a constitution-level policy change, even
  though the touched code lives outside the checksummed surface — this file's
  own standing rule doesn't distinguish by which file houses the mechanism).
  Next: whoever next evaluates a real promotion candidate should note in the
  run record whether the new gate actually rejected anything it wouldn't have
  before — this session's shadow run is the first real exercise of it but 3
  generations is a small sample. Separately, and not urgent: the demotion/
  rollback question flagged above is real unfinished business, worth a
  dedicated design pass of its own rather than a rushed decision inside a gate
  fix.

- **Solved 2026-08-22 (3-hourly check): the "-34.1% vs -46.5% maxDD" mystery the
  previous entry left as "narrowed, not proven" is not a data bug at all — it's the
  MAX_DD_HARD_FAIL gate's own arithmetic having a real, structural blind spot for
  any drawdown that spans a fold boundary.** (see
  `runs/2026-08-22-0356-fold-dd-blindspot.md`) Per the previous entry's own
  instruction, re-ran `universe-perturb`'s full single-symbol census fresh under
  the now gap-checked fetch path first: it reproduced -46.5%/-inf cleanly again
  (15/27 single-symbol drops now hard-fail, up from 14/27 on 2026-08-21, with
  CRVUSDT newly added to the failing set), so the silent-truncation fix does not
  explain the earlier -34.1% reads — clean reproduction under a verified-gapless
  fetch path is exactly the "materially more urgent" branch the previous entry
  flagged. Chased the real explanation instead of stopping at "confirmed, cause
  unknown": `Evaluator._merge` (`loop.evolve.py`), the function that builds the
  merged stats `accepts()`/`fitness()` actually gate promotion on, sets
  `max_dd = np.min([fold.max_dd for fold in folds])` — the worst of the 3
  *independently* backtested folds' own local peak-to-trough, each fold's NAV
  starting fresh at that fold's own boundary. A true continuous drawdown that
  starts near the end of one fold and bottoms out inside the next is invisible to
  every individual fold's own local max_dd, and therefore invisible to the merged
  number the gate checks. New read-only CLI `fold-dd-blindspot [--also-version N]`
  proves it directly: v3's gate-visible max_dd is -34.1% (fold 2's own local
  number, the worst of the three) while one continuous, unbroken backtest over the
  *identical* [0, 0.85] search span — no fold boundaries at all — already reads
  -46.5%, the exact 12.4pp jump the previous entry couldn't explain. The
  discrepancy lives entirely inside the search region, not the holdout slice (the
  full [0,1] number is also -46.5%, unchanged). Cross-checked against v1
  (reconstructed): same mechanism, smaller gap inside the search span (-44.4%
  gate-visible vs -45.3% true, 0.9pp) but a much larger one once the holdout slice
  is included (-54.4% true full-history, matching the 2026-08-21 universe-perturb
  entry's independent -54.3% reading almost exactly) — the blind spot's size is
  genome/window-specific, not a fixed offset. Composes only already-tested
  `Evaluator.evaluate`/`run_backtest` (no engine or constitution change, same
  precedent as `fold-scheme`/`margin-curve`/`regime` — no new pure function, no
  new test file). Verified safe: `py_compile` clean, `tools/edit_bundle_module.py
  verify` round-trip clean, full suite still 184 passed (unchanged — no new pure
  function to test), `live_state.json` md5 identical throughout
  (`3f71d6ab111ecd646eda9e0e595a9970`), `evotrader.manifest` md5 identical
  (`0bf3a7d9411ee692d0a9f152a7533803`), `constitution verified 8b74865634b1db07`
  unchanged on every invocation, `git diff` confirms zero `_SRC[...]` lines
  touched (pure addition to the plain-script CLI section), today's 2026-08-22 bar
  already confirmed processed by the 00:20 UTC daily run before this check
  started (`updated` timestamp `2026-08-22T00:21:18+00:00`, `tick` not run this
  session, no double-trade). **Practical reading, not yet acted on**: the live
  champion v3's true full-history drawdown already exceeds the 40% threshold that
  is supposed to hard-fail it, and the acceptance gate that ran at promotion time
  structurally could not have seen that, because it never runs one continuous
  backtest across fold boundaries — this is a real gap in what MAX_DD_HARD_FAIL
  actually protects against, independent of whether any single champion happens
  to trip it today. Push notification sent to the user this session given the
  severity and the fact that this closes out the previous entry's open safety
  question with a real mechanism, not a shrug. **Fixing it is a genuine
  constitution change** (either recomputing merged max_dd from one continuous
  replay across the search span, or accepting the current per-fold semantics
  explicitly and renaming/documenting it as such) and was deliberately not
  attempted this run — it needs a real design pass on which of several ways to
  reconstruct a "true" merged drawdown is right (continuous replay ignores that
  each fold is supposed to be an independent walk-forward test; some other
  combination might double-count or under-count), plus an `AMENDMENTS.md` row,
  more runway than a 3-hour slot should gamble on. Next: the design pass this
  file has deferred twice now (previous entry deferred it pending this
  confirmation; the 2026-08-21 universe-perturb-cliff entry deferred it pending a
  root cause) has no more reason to wait — whoever picks this up next should
  decide how MAX_DD_HARD_FAIL's merged max_dd should actually be computed and
  write the `AMENDMENTS.md` case for it.

- **Found 2026-08-22 (3-hourly check): a real silent-truncation bug in the market-data
  fetch path, discovered because the champion's full-history baseline maxDD suddenly
  read -46.5% (crossing MAX_DD_HARD_FAIL) instead of the -34.1% every session this
  week had reported — fixed, but the discrepancy's root cause is only narrowed, not
  proven.** (see `runs/2026-08-22-0100-maxdd-jump-and-fetch-truncation-bug.md`) The
  very first `universe-perturb` command this session printed champion v3's own
  unperturbed 27-symbol full-history baseline at -46.5% maxDD, `fitness = -inf`
  (hard-fail) — a 12.4pp jump from the -34.1% figure this file's last several
  entries (2026-08-21 19:02 through 22:10) all independently, consistently
  reported for the identical computation. Reproduced 3 independent ways this
  session (`universe-perturb`, `drawdown`, a hand-rolled `nav_history` trace),
  all agreeing: peak $38,379 on 2024-12-08, trough $20,541 on 2025-06-22, "not
  recovered" through today. Investigated rather than assumed: verified this
  isn't a live-tick/state issue (today's bar already processed, no promotion,
  `live_state.json` untouched); verified the one alarming single-bar move found
  along the way (`TRXUSDT` +67% in one day, 2024-12-02→03) is real exchange
  data, not corruption — queried `data-api.binance.vision` directly with `curl`,
  bypassing this project's own code entirely, got identical numbers with ~13x
  normal volume; corroborated with `regime` (genome-independent buy-and-hold):
  fold 3 maxDD -55.9%, and the **sealed holdout itself** now reads -40.3% maxDD
  / -22.6% return on raw buy-and-hold, materially worse than when `regime` last
  characterized it (2026-08-17); and checked this session's own fetch for the
  specific failure mode that would explain a silent understatement elsewhere —
  found none (all 27 symbols, 1,461 bars each, zero missing calendar days) —
  but that check also exposed a real, previously-unguarded vulnerability:
  `core.market.fetch_klines` treated any page under 1,000 rows as unconditional
  proof a fetch had reached the end of history, which is exactly what a
  transient partial API response looks like too — silently truncating the
  frame with no error, no log line, nothing downstream could ever notice.
  Fixed: a short page that stops before the requested `end_ms` now gets up to
  3 bounded retries before being accepted as real; new pure
  `core.market.find_gaps(df, interval)` diffs a symbol's index against its own
  expected calendar grid, wired into `load_universe` as a loud `[market]
  WARNING` if anything survives the retry. Tested:
  `tests/test_market_gaps.py`, 5 new, full suite 184 passed up from 179.
  `tools/edit_bundle_module.py verify` clean, `py_compile` clean,
  `evotrader.manifest` unchanged (`core.market` isn't checksummed),
  `constitution verified 8b74865634b1db07` throughout, `live_state.json` md5
  constant within this session. **Honest caveat, not resolved**: there's no
  way to retroactively audit a past, ephemeral container's cache (`state/` is
  gitignored, fresh empty every session) to confirm this exact bug produced
  the earlier -34.1% reads — the fix closes the most concrete failure mode
  found and matches the evidence, but "likely explanation" is not "proven
  cause." The originally-planned work this session (a design pass on whether
  `MAX_DD_HARD_FAIL`'s 40% threshold is right, flagged since the 2026-08-21
  universe-perturb cliff mapping below) was **not attempted** — building it on
  a number that may itself be wrong would be worse than not building it.
  Next: re-run `universe-perturb`'s full single-symbol census fresh under the
  now gap-checked fetch path before trusting either -34.1% or -46.5%, and only
  then resume the `MAX_DD_HARD_FAIL` design pass. If -46.5% (or similar)
  reproduces again clean, that's a materially more urgent situation than "cliff
  nearby" — the champion may currently be failing its own risk gate for real.
  Push notification sent to the user this session given the severity.

- **Mapped 2026-08-21 (3-hourly check): the `universe-perturb` drawdown cliff
  the previous 19:02 run found isn't 20%-of-universe away, it's essentially
  at the doorstep — 14 of 27 symbols (51.9%) hard-fail the champion's own
  `MAX_DD_HARD_FAIL` gate when dropped ALONE, no other perturbation.** (see
  `runs/2026-08-21-2210-universe-perturb-single-symbol-cliff.md`) No code
  changed — used `universe-perturb`'s existing `--drop-frac`/`--drop` flags,
  not new ones. First, a `--drop-frac` sweep (0.05/0.10/0.15/0.25/0.30,
  alongside the existing 0.20 baseline) came back noisy at n=6 trials/frac,
  not cleanly monotonic (hard-fail counts 3/3/4/2/3/5 out of 6 as frac rises
  0.05→0.30) — expected, since each frac draws an independent RNG sample, so
  6 trials isn't enough to trust the curve's shape. But every frac, including
  the smallest (`k=1`, one symbol), already showed a non-trivial hard-fail
  rate, which motivated the real test: an exhaustive census instead of
  sampling. `--drop SYM` run once for all 27 universe symbols individually:
  baseline maxDD is -34.1% against a 40% hard-fail threshold (5.9pp margin),
  and dropping any ONE of AAVE/ADA/AVAX/BNB/DOGE/DOT/ETH/FIL/INJ/SHIB/SOL/
  TRX/XLM/ZEC alone pushes maxDD past 40% (ETH alone is the most extreme,
  -55.6%). The other 13 symbols (ATOM/BCH/BTC/CRV/FET/HBAR/ICP/LINK/LTC/
  NEAR/PAXG/UNI/XRP) survive removal alone with finite fitness. Verified
  safe: no code touched, `git status --short` clean throughout, full suite
  still 179 passed (nothing new to test), `live_state.json` md5 identical
  throughout (`8b3dc413c9a85fda04bdeb0ad4c63733`), `evotrader.manifest` md5
  identical (`0bf3a7d9411ee692d0a9f152a7533803`), `constitution verified
  8b74865634b1db07` unchanged across all 33 invocations, today's 2026-08-21
  bar confirmed already processed by the 00:20 UTC daily run and the 20:30
  UTC mechanism check before this session started (`tick` not run this
  session, no double-trade), `review-hard-calls` checked (0 pending), no
  genome promotion (no README Status change needed). Session started with
  local `main` detached, 2 commits ahead of an unrelated pre-restart seed
  history with no merge-base against a force-updated `origin/main` (the
  same recurring container-seed artifact prior sessions have logged, not
  real divergent work) — reset to `origin/main` per the run protocol, no
  work lost. Next: this sharpens but doesn't fix anything — the honest next
  step would be a design pass on whether `MAX_DD_HARD_FAIL`'s margin is
  right given how many single-symbol removals cross it, which is a
  constitution change deserving its own `AMENDMENTS.md` argument, not
  attempted this run. Treat the universe-perturb line as answered for now,
  same as the windowing/capping line was set aside earlier today.

- **Shipped 2026-08-21 (3-hourly check): new `universe-perturb` diagnostic —
  the first to test universe composition instead of another fold-windowing
  variant, and it found a real drawdown cliff the champion sits close to.**
  (see `runs/2026-08-21-1902-universe-perturb-diagnostic.md`) The last two
  entries in the fold-windowing/holdout-margin thread both recommended
  treating that line as exhausted for now, so this picks up a different,
  previously-untried thread from the 2026-08-16 priorities note instead:
  "perturbation tests on fees/slippage/universe/start-date" — `costs` already
  covers fees/slippage, universe composition had never been tested. New
  read-only CLI `universe-perturb [--drop-frac] [--n-trials] [--seed] [--drop
  SYM,...] [--holdout] [--also-version N]`, same guarantees as `costs`: real
  `run_backtest` per scenario (universe loaded once, subsetted per scenario;
  benchmark buy-and-hold recomputed per scenario over the same subset so
  excess-return comparisons stay fair), never touches `live_state.json`. No
  new pure function (composes already-tested `run_backtest`/`Genome`/
  `edge_vs_benchmark`), so no new test file, same precedent as `costs`/
  `regime`/`margin-curve`. Result against champion v3 (full history):
  baseline fitness 0.876 (maxDD -34.1%); dropping PAXG alone costs a real
  -0.236 (the seed genome's own comment calls it "deliberately included" —
  this is the first time that claim was actually tested, and it holds, unlike
  `correlation_penalty`'s measured-dead-weight finding in item 3); **2 of 6
  random 5-symbol drops hard-failed outright** (-inf fitness) purely on the
  `MAX_DD_HARD_FAIL` gate (43.7%/44.2% maxDD vs baseline's 34.1%) even though
  both scenarios still beat benchmark (+51.2%/+119.1% excess return) — the
  champion's drawdown margin to its own hard-fail gate is thin enough that a
  random, non-adversarial fifth of the universe going missing can flip a
  fine-looking scenario into an outright rejection. Cross-checked against v1
  (reconstructed, `--also-version 1`): a separate, previously-unmeasured
  finding surfaced as a side effect — v1's own full-continuous-history
  baseline (unperturbed, all 27 symbols) hard-fails outright (maxDD -54.3%),
  which does not contradict v1's original promotion (that used the
  fold-aggregate + sealed-holdout process, a different metric from one
  continuous 4-year replay) but had genuinely never been checked before
  (every prior `--also-version 1` diagnostic evaluates v1 through folds or
  the holdout slice only). Verified safe: `py_compile` clean, full suite 179
  passed (unchanged), `live_state.json` md5 identical throughout
  (`8b3dc413c9a85fda04bdeb0ad4c63733`), `evotrader.manifest` md5 identical
  (`0bf3a7d9411ee692d0a9f152a7533803`), `constitution verified
  8b74865634b1db07` unchanged, `git diff` confirms zero `_SRC[...]` lines
  touched (pure addition to the plain-script CLI section, same pattern as
  `margin-curve`), today's 2026-08-21 bar confirmed already processed by the
  00:20 UTC daily run before this check started (`updated` timestamp
  `2026-08-21T00:27:21+00:00`, `tick` not run this session, no double-trade),
  `review-hard-calls` checked (0 pending), no genome promotion (no README
  Status change needed). Next: the drawdown-cliff finding is real,
  previously-unmeasured evidence about the champion's current risk margin —
  not immediately actionable (this diagnostic characterizes the cliff, it
  doesn't propose a fix) but worth citing the next time `MAX_DD_HARD_FAIL`'s
  own margin comes up, the same way `holdout-noise` did for the
  multiple-testing margins. A `--drop-frac` sweep (down from 20% to find how
  close to the full universe the cliff sits, or up to find where most trials
  start hard-failing) would map the cliff's edge more precisely — not
  attempted this run, 6 trials at one drop-frac was enough to establish the
  cliff exists.

- **Shipped 2026-08-21 (3-hourly check): new `margin-curve` diagnostic puts real
  numbers on the "gets harder to clear as n rises" claim the previous run made,
  and the two acceptance gates turn out to behave very differently.** (see
  `runs/2026-08-21-1553-margin-curve-diagnostic.md`) Pure arithmetic on
  `constitution.required_margin` (`sigma * sqrt(2*ln(n))`, unchanged, already
  tested) — no market data, no backtest, no state write. At the real live
  counts (182 candidates tested against champion v3, 13 cumulative
  sealed-holdout draws): the **fold-aggregate margin is nearly saturated**
  already (0.258 now; +200x candidates only reaches 0.367; +0.10 more needs
  ~123x more candidates, ~22,425; +0.25 more needs ~574 million) — so the
  13:07 run's "mechanically harder to clear as n_candidates rises" framing is
  directionally right but overstates the effect: a near-miss fold-aggregate
  candidate (that run's best was +0.245 above champion, just short of the
  ~0.258-0.270 margin across its 182→294 candidate range) is not meaningfully
  pushed further out of reach by more shadow candidates. The **sealed-holdout
  margin is NOT saturated** at today's much smaller draw count — only 4 more
  draws (13→17) raise it a further +0.25, 10x more draws (13→130) raises it
  +1.71 — the same sqrt(log n) shape evaluated much earlier on its curve.
  Reading: if there's a real rising-bar effect on promotion difficulty right
  now, it's on the holdout side (every real promotion attempt that reaches
  the sealed-holdout check permanently raises the bar for the next one, per
  `holdout_accepts()`'s own "never reset by a promotion" design), not the
  fold-aggregate side, which is already close to flat. Verified safe: new
  code is CLI-only (plain script section of `evotrader_bundle.py`, `import
  math` added to the top-level import line, no `_SRC` module touched, nothing
  checksummed changed), `py_compile` clean, full suite still 179 passed (no
  new pure functions — reuses the already-tested `required_margin`),
  `live_state.json` md5 identical throughout (`8b3dc413c9a85fda04bdeb0ad4c63733`),
  `evotrader.manifest` md5 identical (`0bf3a7d9411ee692d0a9f152a7533803`),
  `constitution verified 8b74865634b1db07` unchanged, today's 2026-08-21 bar
  confirmed already processed by the 00:20 UTC daily run before this check
  started (`tick` not run this session, no double-trade), `review-hard-calls`
  checked (0 pending), no genome promotion (no README Status change needed).
  Next: whoever next gets a real candidate to the sealed-holdout check should
  note both the `HOLDOUT_SIGMA` outcome and the cumulative-draw count at that
  moment — this run shows that count is not a fixed backdrop, it visibly
  moves the bar at today's scale. Doesn't change the fold-windowing-line or
  `HOLDOUT_SIGMA` "no immediate follow-up" reads already in this file.

- **Measured 2026-08-21 (3-hourly check): 8 more shadow-evolve generations past
  the live account's own researcher_memory, and the finding is which gate is
  actually binding right now — not the sealed holdout this morning's
  `HOLDOUT_SIGMA` recalibration touched, but the earlier fold-aggregate
  multiple-testing gate.** (see
  `runs/2026-08-21-1307-shadow-evolve-post-sigma-recalibration.md`) Isolated
  scratch copy of `live_state.json` (champion v3, real accumulated
  `researcher_memory`, 182 candidates already tried), `evolve 8` against it —
  same real data/gates, nothing written to the real file (md5 identical
  before/after). Champion held throughout at fitness 1.396, boldness climbed
  12→19, cumulative candidates tried in this branch rose 182→294. Two
  generations' best raw fold-aggregate fitness (1.641, 1.462) numerically beat
  champion's 1.396 but neither cleared the multiple-testing-adjusted
  `required_margin()` (which scales with `n_candidates`, now 224+), so **no
  candidate this run ever reached the sealed-holdout check** — meaning this
  morning's `HOLDOUT_SIGMA` change was never exercised by any of these 294
  candidates. Answers the open "worth a one-line note next promotion
  evaluation" flag from this morning's entry with: still open, this run didn't
  produce the candidate needed to close it, because the fold-aggregate gate
  rejected everything first. New-ish mechanism worth naming for whoever next
  looks at the stagnation question: `required_margin()`'s multiple-testing
  correction gets mechanically harder to clear as `n_candidates` keeps rising
  with every generation, live or shadow — a partial, non-regime explanation
  for continued stagnation that doesn't require any of the already-set-aside
  fold-windowing hypotheses. Verified safe: no code changed, `live_state.json`
  md5 identical throughout (`8b3dc413c9a85fda04bdeb0ad4c63733`), `git status
  --short` clean throughout, `constitution verified 8b74865634b1db07`
  unchanged on every invocation, today's 2026-08-21 bar confirmed already
  processed by the 00:20 UTC daily run before this check started (`tick` not
  run this session, no double-trade), `review-hard-calls` checked (0 pending),
  no genome promotion (no README Status change needed). Next: whoever next has
  a real candidate that clears the fold-aggregate gate should note whether the
  new `HOLDOUT_SIGMA` changes the promotion outcome — still unclosed. The
  fold-aggregate-gate-hardness-with-n_candidates observation is flagged, not
  chased further this run (would need either much deeper search or a
  researcher_memory reset that would throw away real history, neither
  attempted).

- **Shipped 2026-08-21 (3-hourly check): the `MULTIPLE_TESTING_SIGMA` recalibration
  the last two runs (fold-cap, daily-discussion) both pointed at is done — new
  `HOLDOUT_SIGMA = 2.0` constant, `holdout_accepts()`'s margin now uses it
  instead of the fold-aggregate sigma.** (see
  `runs/2026-08-21-0951-holdout-sigma-recalibration.md`) `holdout_accepts()`'s
  own docstring has said since 2026-08-16 that its margin is "a floor, not a
  calibration... measure the sigma before trusting the number" — `holdout-noise`
  measured it 2026-08-20/21, converged across all three real champions this
  account has had: empirical sealed-holdout `boot_fitness_std` 1.48/1.21/2.04 in
  fitness units (v1/v2/v3) against the 0.08 the old margin assumed (15-25x too
  small). New `constitution.required_margin(n_candidates, complexity_delta,
  sigma=MULTIPLE_TESTING_SIGMA)` gained an optional `sigma` parameter (default
  unchanged, so `accepts()`'s fold-aggregate margin is byte-for-byte
  unaffected); `holdout_accepts()` now passes `sigma=HOLDOUT_SIGMA`. Set at the
  highest of the three champions' readings, not their average — a safety floor,
  future champions unmeasured. A fresh `holdout-noise --n-boot 300` run against
  live champion v3 after the change measured empirical sigma at 0.91x
  `HOLDOUT_SIGMA` — close to 1x, so the new constant isn't drastically over- or
  under-loose for the actual live champion today. Net effect: strictly stricter
  — the `n_draws=1` holdout margin goes from ~0.094 to ~2.35, ~25x tighter, and
  every future promotion attempt now needs to clear that. Kept
  `MULTIPLE_TESTING_SIGMA` itself untouched (it's a separately-measured,
  structurally-different quantity — fold-aggregate noise averaged over
  `N_FOLDS` windows with its own dedicated cross-fold-variance defense; nothing
  in `holdout-noise` bears on it). Caveat carried into both docstrings: this
  measures realized-return-path resampling noise only, not the second named
  source of extra noise (a candidate arrives at this gate pre-selected by folds
  that correlate with it) — `HOLDOUT_SIGMA` is a real, measured floor on one
  known source of under-margining, not a claim the gate is now fully honest.
  Verified safe: full suite 179 passed (up from 176, 3 new/updated tests in
  `tests/test_constitution.py`), `tools/edit_bundle_module.py verify`
  round-trip clean after reinserting the edited `constitution` module,
  `py_compile` clean, `evotrader_bundle.py summary` correctly reported
  `CONSTITUTION MODIFIED` against the stale manifest before the deliberate
  reseal (proves the checksum mechanism is live), `evotrader.manifest` updated
  to the new checksum `8b74865634b1db07` in this commit (was
  `dfae6a697f51fb49`), `AMENDMENTS.md` row added in the same commit (mandatory
  for a constitution change — this repo's own standing rule), `live_state.json`
  md5 identical throughout (`8b3dc413c9a85fda04bdeb0ad4c63733`), today's
  2026-08-21 bar confirmed already processed by the 00:20 UTC daily run before
  this check started (`updated` timestamp `2026-08-21T00:27:21+00:00`, genome
  version still 3, `tick` not run this session, no double-trade),
  `review-hard-calls` checked (0 pending), no genome promotion (no README
  `## Status` staleness risk). Next: no immediate follow-up required — the
  constant is live for every future promotion attempt. Worth a one-line note
  the next time a real promotion is evaluated, on whether the tighter margin
  changed the outcome vs. what the old 0.08-based margin would have said. The
  windowing/capping line (item 2, see the entries below) stays set aside per
  the last two runs' shared read — four independent mechanisms all showed the
  same champion-specific, non-generalizing shape, and this recalibration was
  the sharper alternative they all pointed at instead.

- **Measured 2026-08-21 (3-hourly check): `fold-cap`, the mean-term-capping fix
  the previous run flagged as the sharper remaining option — and it's the
  fourth independent windowing/capping mechanism to show the same
  champion-dependent, non-generalizing shape.** (see
  `runs/2026-08-21-0653-fold-cap-mean-winsorize.md`) New
  `loop.evolve.capped_fitness_decomposition(fold_fits, cap_z)` winsorizes
  each fold fitness to a ceiling of `mean + cap_z*std` before averaging
  (penalty term left computed from the original uncapped values, so this
  isolates whether capping the mean term *alone* helps); new read-only CLI
  `fold-cap [--cap-z Z] [--also-version N]` sweeps `cap_z` `[0.5, 1.0, 1.5,
  2.0]` under the same 5 fold schemes `fitness-decomp` already uses. Tested:
  `tests/test_capped_fitness_decomposition.py`, 9 new tests, full suite 176
  passed up from 167. Result: against v3 (live), capping makes the
  cross-scheme `aggregate_fitness` range **wider at every cap_z tested**
  (0.657 baseline → 0.977/0.835/0.659/0.657 as cap_z tightens 0.5→2.0) —
  never better than the uncapped baseline. Against v1 (the seed), it's the
  opposite: capping **tightens** the range at the two more aggressive
  settings (0.663 baseline → 0.446/0.493 at cap_z 0.5/1.0). Mechanism: the
  schemes that produce v3's highest aggregate are exactly the ones with the
  fattest single-scheme outlier fold, so capping pulls those schemes down and
  widens the spread; for v1 the correlation runs the other way, so the same
  mechanism narrows it. Not a parameter-free fix waiting for the right
  `cap_z` — the sign of the effect is champion-specific, the same shape
  `fold-scheme`'s n_folds sweep, `rolling-folds`, and `regime-folds`'s
  n_folds/n_subwindows sweep all independently found. Four consistent
  negative results now on this line. Verified safe: `loop.evolve` isn't
  checksummed, `tools/edit_bundle_module.py verify` round-trip clean, full
  suite 176 passed, `live_state.json` md5 identical throughout
  (`8b3dc413c9a85fda04bdeb0ad4c63733`), `evotrader.manifest` md5 identical
  (`6a4434574ff424f74ff300ebdb50d194`), `constitution verified
  dfae6a697f51fb49` unchanged, today's 2026-08-21 bar confirmed already
  processed by the 00:20 UTC daily run before this check started (`tick` not
  run this session, no double-trade), `review-hard-calls` checked (0
  pending). Next: recommend treating the fold-windowing/capping line as
  exhausted rather than trying a fifth variant — redirect effort on the
  walk-forward-honesty thread to the already-quantified, still-unstarted
  `MULTIPLE_TESTING_SIGMA` recalibration from `holdout-noise` (14-25x too
  small across all three real champions), which is a constitution change
  (checksummed, `AMENDMENTS.md` row) deserving its own design pass.

- **Swept 2026-08-21 (3-hourly check): `regime-folds --n-subwindows`/`--n-folds`
  sweep answers the previous run's open question — isolating the dominant
  window only helps net `aggregate_fitness` while fold count stays low; raise
  it and the same mechanism isolates a bad window too, and that costs more
  than the good isolate gains.** (see
  `runs/2026-08-21-0351-regime-folds-nfolds-sweep.md`) No code changed —
  existing CLI flags, purely read-only. At fixed 6 sub-windows, sweeping
  `n_folds` 3→4→5 against champion v3 gives a clean monotonic trend:
  aggregate delta **+0.723 → +0.126 → −0.249**. Mechanism: LPT balance
  isolates only the single dominant sub-window (w3, +156.8% b&h, fold
  fitness 5.696) at low fold counts, but at `n_folds=5` it also isolates a
  *weak* sub-window (w5, −27.9% b&h) alone into its own fold, dropping that
  fold's fitness to −0.544 — the cross-fold consistency penalty reacts to
  that wide isolated-fold spread more than it reacts to the calendar
  baseline's narrower, already-merged range, so the benefit from isolating
  the good outlier gets eaten by the cost of isolating a bad one too.
  Cross-checked at `n_folds=5` against the other two real champions: v1 also
  lowers (−0.160), v2 is a near-zero wash (+0.035) — 2 of 3 lower, none
  strongly positive, a more consistent read than the previous run's mixed
  `n_folds=3` result (v3 +0.723, v1 +0.057, v2 −0.065), suggesting that
  mixed reading was partly a fold-count artefact rather than a clean
  per-genome property. Separately swept `n_subwindows` 4/6/8 at fixed
  `n_folds=3`: still positive at every resolution (+0.714/+0.723/+0.410) but
  weakening at n=8 as finer sub-windows fragment the dominant window's
  concentrated weight. Reading: this is evidence *against* "isolate the
  dominant window" as a general-purpose fix — it's a double-edged mechanism
  that depends on a fold-count parameter with no principled correct value
  identified yet, not a one-directional improvement. Sharpens the case (from
  `fitness-decomp`) that a fix should target the mean term's outlier
  sensitivity directly (e.g. capping one fold's contribution before
  averaging) rather than any windowing/isolation scheme. Verified safe:
  no code touched, `git status --short` clean throughout, `live_state.json`
  md5 identical (`8b3dc413c9a85fda04bdeb0ad4c63733`), `evotrader.manifest`
  md5 identical (`6a4434574ff424f74ff300ebdb50d194`), constitution verified
  `dfae6a697f51fb49` unchanged on every invocation, today's 2026-08-21 bar
  confirmed already processed by the 00:20 UTC daily run before this check
  started (`tick` not run this session, no double-trade). Next: either try
  `n_folds=3` with sub-windows above 8 to see how far the positive effect
  degrades, or — more likely the better use of the next design session —
  shift attention entirely to a fix that caps/down-weights a single
  outlier fold's pull on the mean term, since this sweep shows windowing
  changes alone don't have an obviously correct operating point.

- **Shipped 2026-08-21 (3-hourly check): `regime-folds`, the first real test of
  the regime-stratified fold scheme item 2 has been circling since
  2026-08-20 — and it doesn't need the engine/constitution change AGENTS.md
  assumed.** (see `runs/2026-08-21-0056-regime-folds-and-holdout-pressure.md`)
  Every entry since fitness-decomp settled that aggregate_fitness's
  instability rides the mean term (one dominant fold), and `regime-scan`'s own
  CLI comment says fixing it "needs engine work `run_backtest` can't do yet
  (non-contiguous folds)". That's not true for a first honest test: a fold
  only needs `run_backtest` to change if it must be *one continuous replay*;
  scoring it as several independently-backtested sub-windows merged together
  (the same trade-weighted `_merge` the acceptance gates already use to
  combine folds) needs no engine or constitution change at all. New
  `loop.evolve.regime_stratified_groups(window_returns, n_folds)` (pure,
  genome-independent, greedy LPT balance on each sub-window's
  `|log(1+r)|` weight — the same weight `regime_concentration` uses) plus
  `Evaluator.evaluate_grouped(g, sub_windows, groups)` (independently
  backtests each sub-window in a group, merges via the existing `_merge`,
  scores with the existing `ranking_fitness` and the same
  `mean - FOLD_CONSISTENCY_WEIGHT * std` aggregate formula `evaluate()` uses,
  so the two are directly comparable at the same fold count) back a new
  read-only CLI `regime-folds [--n-subwindows] [--n-folds] [--also-version N]`.
  Default 6 sub-windows (matches `regime-scan`'s own n=6 reading and stays
  comfortably clear of `run_backtest`'s 120-bar hard minimum per call — 12
  sub-windows would not, the same failure mode `fold-scheme`'s n=8 hit).
  Tested: `tests/test_regime_stratified_groups.py` (9 new) +
  `tests/test_evaluate_grouped.py` (7 new), full suite 167 passed up from 151.
  First result, all three real champions: stratification raises
  `aggregate_fitness` for v3 (1.396 → 2.119, +0.723) and v1 (0.181 → 0.238,
  +0.057), lowers it slightly for v2 (0.293 → 0.227, −0.065) — mixed, not a
  clean win, and only one reading. Mechanism worth flagging: the single
  dominant sub-window (the fold-2 melt-up) ends up alone in its own fold every
  time under LPT, since nothing else is heavy enough to make pairing with it
  the balanced choice — so this *isolates* the melt-up into a smaller fold
  rather than *spreading* it the way item 2's framing assumed, which changes
  what the other folds average over instead of diluting the melt-up directly.
  Whether that's the right shape for a fix is still open. Verified safe:
  `loop.evolve` isn't checksummed, `tools/edit_bundle_module.py verify`
  round-trip clean before and after, `py_compile` clean, `live_state.json` md5
  identical throughout (`8b3dc413c9a85fda04bdeb0ad4c63733`),
  `evotrader.manifest` md5 identical (`6a4434574ff424f74ff300ebdb50d194`),
  `constitution verified dfae6a697f51fb49` unchanged (nothing touched here is
  checksummed), today's 2026-08-20 bar (tick 7) confirmed already processed by
  the 00:20 UTC daily run before this check started (no double-trade, `tick`
  not run this session). Also re-ran `holdout-pressure` after today's
  non-promoting daily `evolve 3` per the standing note: 13/13 real challengers
  that cleared the fold-aggregate gate have now lost their sealed-holdout
  draw against champion v3, up from 9/9 — same entrenchment pattern, bigger
  sample, no new interpretation. Session started with local `main` detached,
  2 commits ahead of an unrelated pre-restart seed history with no
  merge-base against a force-updated `origin/main` (an old container-seed
  artifact, not real divergent work); reset to `origin/main` per the run
  protocol, no work lost. Next: `regime-folds` needs more readings
  (`--n-subwindows`/`--n-folds` sweep) before item 2's design question is
  actually settled either way — see the run note for the open design
  question about whether isolating vs. actually splitting the dominant
  window is the right objective.

- **Measured 2026-08-20 (3-hourly check): ran the flagged `regime-scan --interval
  4h` follow-up — the concentration finding holds at 4h resolution too, so it
  isn't a 1d-track artefact.** (see `runs/2026-08-20-2200-regime-scan-4h.md`)
  12 non-overlapping 4h windows across the same searchable region (8,766 total
  4h bars): concentration ratio **2.47x** its even share (richest window w8,
  2024-08-14→2024-11-25, +92.7% b&h return, 20.6% of |log-growth| vs 8.3% even
  share; HHI 0.129 vs 0.083 even). Directly comparable to the 1d track's n=12
  scan (2.45x) — same order of magnitude, same richest-window shape (a
  2024-08→2024-11 melt-up, matching one of the two bull runs the 1d n=12 scan
  found colliding in calendar-fold-2). Answers the question the 2026-08-20
  18:55 entry left open: this isn't a 1d-specific binning quirk, so any future
  regime-stratified fold redesign for the 4h shadow track can reuse the same
  motivation and the same regime label (per-window b&h return) without
  re-deriving it. No code changed — existing CLI, no new flag needed
  (`--interval` already existed). Also fixed a stale factual claim in
  `README.md`'s `## Status` section: it still said cross-asset correlation
  awareness had "shipped" as a dormant/opt-in feature, but that gene was fully
  removed on 2026-08-20 (item 3, closed) — updated to describe the removal and
  why, so the public-facing landing page doesn't contradict `AGENTS.md`'s own
  record. Verified safe: purely read-only diagnostic (no genome, no backtest,
  no state write) plus one docs-only edit, `live_state.json` md5 identical
  (`cca58deb976cef403c5010f2e2b9528b`), `evotrader.manifest` md5 identical
  (`6a4434574ff424f74ff300ebdb50d194`), `constitution verified
  dfae6a697f51fb49` unchanged, full suite still 151 passed, today's 2026-08-19
  bar (the last closed daily bar) confirmed already processed by the 00:20 UTC
  daily run before this check started (`tick` correctly reported "already
  traded", no double-trade), `pip3 install -r requirements.txt` needed a
  retry this session (first attempt hit a `files.pythonhosted.org` read
  timeout, second attempt with `--timeout 180 --retries 5` succeeded) — a
  transient network issue, not a repo problem. Next: the regime-stratified
  fold scheme itself is still the real unstarted work (a constitution change —
  `Evaluator` accepting a fold as a *set* of windows, `run_backtest` replaying
  a non-contiguous union of bars — needs a design pass + `AMENDMENTS.md` row),
  now motivated and measured on both bar sizes. No further cheap
  regime-scan follow-up is queued; the next step here is the design work
  itself, which needs a session with more runway than a 3-hourly slot.
- **Measured 2026-08-20 (3-hourly check): shipped `regime-scan`, and it puts a
  number on the regime-stratification question — the fold-2 melt-up is
  concentrated at ~2.5x its even share at every resolution, and at the fold
  resolution evolution actually uses one of three folds carries 92% of the
  region's compounded growth.** (see
  `runs/2026-08-20-1855-regime-scan-melt-up-concentration.md`) Also ran the
  flagged one-liner `fitness-decomp --also-version 2`: the third champion (v2)
  confirms the mean term drives the aggregate swing (mean range 2.173 vs penalty
  0.370) — now a 3-of-3 property, not a v3/v1 quirk. New pure helper
  `loop.evolve.regime_concentration(window_returns)` (`|log(1+r)|` shares, HHI,
  `concentration_ratio = top_share * n`; tested,
  `tests/test_regime_concentration.py`, 8 new tests, full suite 151 passed up
  from 143) + read-only CLI `regime-scan [--n-windows K] [--interval X]`.
  Genome-independent (buy-and-hold only, no backtest), so `--also-version` would
  change nothing and isn't offered; same guarantees as `regime`. It answers the
  question fitness-decomp left open — is the mean-swinging melt-up *isolated*
  (regime-stratification helps) or *diffuse* (it won't)? Answer: concentrated.
  Concentration ratio is 2.75x at n=3 (fold 2 = +257% b&h, 92% of |log-growth|),
  2.57x at n=6, 2.45x at n=12 — the raw share falls as finer bins split the bull
  runs but the ratio-over-even holds ~2.5x, so it's real, not a coarse-binning
  artefact. Sharper mechanism the n=12 scan exposes: fold 2 isn't one atomic
  melt-up, it's **two separated bull runs** (2023-10→2024-01 +92.5%,
  2024-08→2024-11 +102.1%, a −19% stretch between them) that both land in
  calendar-fold-2 — exactly the separable case regime-stratification is built
  for. Verified safe: `loop.evolve` isn't checksummed, `tools/edit_bundle_module.py
  verify` round-trip clean before and after, `py_compile` clean, `live_state.json`
  md5 identical throughout (`cca58deb976cef403c5010f2e2b9528b`),
  `evotrader.manifest` md5 identical (`6a4434574ff424f74ff300ebdb50d194`),
  `constitution verified dfae6a697f51fb49` unchanged (not touched, no amendment),
  today's 2026-08-19 bar confirmed already processed by the 00:20 UTC daily run
  (no double-trade, `tick` not run this session), genome version unchanged (no
  promotion, no README Status change needed). Next: the regime-stratified fold
  scheme is now motivated *and* measured, but building it is a constitution
  change (`Evaluator` accepting a fold as a *set* of windows, `run_backtest`
  replaying a non-contiguous union of bars) needing a design pass + `AMENDMENTS.md`
  row — flagged, not started; `regime-scan`'s per-window b&h return is the
  genome-independent regime label a stratifier would group on. Cheap follow-up not
  run: `regime-scan --interval 4h`.
- **Measured 2026-08-20 (3-hourly check): shipped `fitness-decomp`, which
  splits `aggregate_fitness` into its mean term and its consistency-penalty
  term — and the result partly corrects the previous run's inference: the
  *mean term*, not the penalty term, drives the across-scheme swing.** (see
  `runs/2026-08-20-1556-fitness-decomposition-diagnostic.md`) The 2026-08-20
  rolling-folds run *guessed* the `FOLD_CONSISTENCY_WEIGHT * std` penalty term
  was the culprit behind the aggregate swinging as windowing changed. New pure
  function `loop.evolve.fitness_decomposition(fold_fits)` (`mean_term -
  penalty_term` reconstructs `aggregate_fitness` exactly — an identity, tested,
  `tests/test_fitness_decomposition.py`, 7 new tests, full suite 143 passed up
  from 136) plus new read-only CLI `fitness-decomp [--also-version N]` (evaluate
  the champion under disjoint `n_folds` 3/5 and rolling overlap 0.5/0.7/0.85,
  print the split) measures it directly instead. Result against v3 (live):
  aggregate ranges 2.100 across the five schemes, of which the **mean term
  ranges 1.500** and the penalty term only **0.610**. Cross-checked against v1
  (reconstructed): same shape, mean term range 0.609 vs penalty 0.183. Both
  terms swing, but the mean of the fold fitnesses varies more than twice as
  much as the penalty in both champions — the aggregate is unstable mostly
  because *which windows capture the permanent fold-2 melt-up* moves the
  average, not because the std penalty over-reacts to how many correlated
  windows feed it. (The extreme overlap=0.85 case is where both terms move the
  aggregate-lowering way at once — mean 1.234 *and* penalty −0.928 → aggregate
  0.306 — so overlap does amplify the penalty, consistent with rolling-folds'
  "worse, not better" observation; but the raw driver across the scheme set is
  the mean term.) Sharpens item 2's redesign direction: retuning
  `FOLD_CONSISTENCY_WEIGHT` alone would not stabilize the aggregate, because the
  dominant instability isn't in the term it controls — it's the mean being
  dominated by one outlier window, which points more firmly at genuine
  regime-stratification (no single window is a permanent +200% outlier) over a
  penalty-weight tweak or a denser calendar slide. Verified safe: `loop.evolve`
  isn't checksummed, `tools/edit_bundle_module.py verify` round-trip clean
  before the edit, `py_compile` clean, `live_state.json` md5 identical
  throughout (`cca58deb976cef403c5010f2e2b9528b`), `evotrader.manifest` md5
  identical (`6a4434574ff424f74ff300ebdb50d194`), `constitution verified
  dfae6a697f51fb49` unchanged, today's 2026-08-20 bar confirmed already
  processed by the 00:20 UTC daily run before this check started (no
  double-trade, `tick` not run this session). Session started detached two
  stale seed-import commits behind a force-updated `origin/main`; reset to
  `origin/main` per the protocol (no work lost). Next: `fitness-decomp
  --also-version 2` is a one-line third-champion follow-up not yet run; the
  regime-stratified fold scheme itself is still unstarted design work, now with
  sharper motivation (design around the mean term's outlier sensitivity, not
  the penalty term).
- **Measured 2026-08-20 (3-hourly check): shipped `rolling-folds`, the rolling
  half of item 2's untried "regime-stratified/rolling fold scheme" idea, and
  it's a negative result — smoothing the calendar split does not stabilize
  `aggregate_fitness`.** (see
  `runs/2026-08-20-1254-rolling-folds-and-holdout-noise-convergence.md`) New
  `loop.evolve.rolling_folds(search_end, base_n_folds, overlap)` (pure
  function, tested, `tests/test_rolling_folds.py`, 9 new tests, full suite
  136 passed up from 127) keeps window width fixed at whatever
  `Evaluator.folds()` uses for `base_n_folds` and slides that fixed-size
  window across the searchable region instead of subdividing it, so more
  (overlapping, correlated) reads of the same span never shrink any window
  below its `base_n_folds` size — the failure mode `fold-scheme` found at
  `n_folds=8` (one window near the 120-bar hard minimum, another hard-gate
  failing outright). New CLI `rolling-folds [--overlap] [--base-n-folds]
  [--also-version N]`, same structure as `fold-scheme`. Against live
  champion v3 at the default `overlap=0.5`: `aggregate_fitness` 1.399 vs the
  disjoint baseline's 1.480 (close), outlier gap shrinks modestly (+252.4% →
  +222.9%, the fold-2 melt-up is still inside one window at this overlap).
  Swept `--overlap 0.7`/`0.85`: `aggregate_fitness` swings 0.306 → 2.003 →
  1.399 → 1.480 across overlap 0.85/0.7/0.5/baseline — a *wider* swing than
  `fold-scheme`'s own n_folds sweep (−1.224 → +1.633 → −0.500), even though
  the raw outlier gap does shrink monotonically with overlap. Reading: naive
  overlap dilutes the one-big-fold problem but doesn't fix
  `aggregate_fitness` instability, because `FOLD_CONSISTENCY_WEIGHT`'s
  cross-fold std penalty is itself sensitive to how many correlated windows
  feed it — adding more overlapping reads adds variance to that penalty term
  at least as fast as it dilutes the outlier's share of the mean.
  Cross-checked against `--also-version 1`: outlier gap identical to v3's at
  every overlap (genome-independent by construction, same shape as
  `fold-scheme`'s finding), `aggregate_fitness` ranks v1 below v3 as
  everywhere else. Verified safe: `loop.evolve` isn't checksummed
  (`constitution` + `core.portfolio` only), `tools/edit_bundle_module.py
  verify` round-trip clean before editing, `py_compile` clean,
  `live_state.json` md5 identical throughout
  (`cca58deb976cef403c5010f2e2b9528b`), `evotrader.manifest` md5 identical
  (`6a4434574ff424f74ff300ebdb50d194`), `constitution verified
  dfae6a697f51fb49` unchanged, today's 2026-08-19 bar (the last closed daily
  bar) confirmed already processed by the 00:20 UTC daily run before this
  check started (no double-trade, `tick` re-checked after all diagnostic
  runs and still correctly reports "already traded"). Also ran the flagged
  cheap follow-up on `holdout-noise`: swept `--n-boot` 1000→50000 across 3
  seeds against v3, plus one 20000-boot pass each on `--also-version 1`/`2`.
  Converges cleanly by ~5000 draws to refined per-champion estimates v3
  ≈25.5x / v1 ≈18.5x / v2 ≈15.1x `MULTIPLE_TESTING_SIGMA` (consistent with,
  slightly above, the earlier 1000-boot reads) — closes the "has the ~24x
  estimate converged" question, diagnostic-only, no code changed for this
  half. Next: this run's finding means the `MULTIPLE_TESTING_SIGMA`
  recalibration + fold-scheme redesign combination flagged since 2026-08-18
  is now sharper, not simpler — a rolling window alone isn't the fix, so
  whoever picks this up next should look at either changing
  `FOLD_CONSISTENCY_WEIGHT` alongside any windowing change, or a genuinely
  regime-stratified split (grouping by market character via something like
  `regime`'s own per-window buy-and-hold characterization, not calendar
  position) — neither attempted yet, both bigger design work than fits this
  session's scope. `rolling-folds --also-version 2` is a one-line follow-up
  not yet run.
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

0. **Closed 2026-08-30 (weekend all-hands, 06:00 UTC): the fitness-vs-excess-return
   selection-metric question — the thing every entry below this line kept
   deferring as "the owner's call" — now has a full design pass with a
   recommendation.** See "Current state" above and
   `runs/2026-08-30-0600-weekend-all-hands.md`. Recommendation: status quo, no
   constitution change — the disagreement between raw fitness and excess return
   is real but has never once flipped a real promotion, and both alternatives
   considered (redefining fitness around excess return, or a hard
   `beat_benchmark` gate at holdout) have their own well-argued problems.
   **Future sessions: do not re-measure this question from scratch.** Point to
   the write-up instead, unless one of its three named revisit triggers has
   actually fired (live account's trailing excess return still negative after
   60 more real trading days with no narrowing; a real, non-shadow promotion
   where fitness and excess return disagree at the sealed holdout; or a fourth
   real champion promoted) — check `live-benchmark`'s current bar count/excess
   figure against that first trigger before starting any new angle on this.

   **Resolved 2026-08-30 (3-hourly check, ~00:46 UTC): tick 16's hard-call
   flag reviewed, verdict `approve`.** See "Current state" above and
   `runs/2026-08-30-0046-hard-call-review-tick16.md` for the full
   reconstruction (v3's evolved `lone_voice_scale` > `two_agree_bonus`
   legitimately made LINKUSDT the bar's top-scored candidate; the evolved
   cash floor left it as the only fillable order). `review-hard-calls`
   reports 0 pending. Nothing else queued from this — the open observation
   about `lone_voice_scale`/`two_agree_bonus` is folded into the
   disagreement-sweep thread (item — see the selection-metric discussion
   in "Current state" above), not a separate action item.

   **Checked 2026-08-30 (3-hourly check, ~05:18 UTC): the flagged
   `lone_voice_scale`/`two_agree_bonus` observation, and it's weak evidence
   against "this gene pairing is a contributor" to the disagreement-sweep
   thread's risky-direction skew.** See "Current state" above and
   `runs/2026-08-30-0518-lone-voice-counterfactual.md`. A counterfactual v3
   with `lone_voice_scale` clamped to equal `two_agree_bonus` showed
   essentially the same risky-direction skew share (86.1% vs. real v3's
   90.9%, within noise at n=79/99) — not the sharp reduction the hypothesis
   predicted. Surfaced an unplanned confound instead: the clamp changed the
   champion's own fold-fitness a lot and, unlike the 2026-08-29 22:50 UTC
   keep_frac sweep's monotonic fitness-predicts-disagreement pattern, the
   disagreement rate moved the opposite way here — that sweep only ever
   varied the calendar window, never the genome, so this is the first check
   of that pattern against a genome-only perturbation. One data point, not
   settled — see the run note's "Next" for what a real follow-up would need
   (hold fold-fitness constant across the comparison). Does not touch the
   still-open selection-metric-redefinition question.

   **Closed 2026-08-30 (3-hourly check, ~09:15 UTC): tried the flagged
   follow-up (real champions instead of a hand-built clamp), and it settles
   into the same confound, harder to escape than before — recommend
   treating this narrow side-question as exhausted.** See "Current state"
   above and `runs/2026-08-30-0915-lone-voice-real-champion-check.md`.
   `disagreement_scan` against all three real champions (v1/v2 both
   `lone<two`, live v3 `lone>two`) found a much bigger risky-share swing
   than the clamp test (58.1%/28.2%/90.9%, v2 the thread's first-ever
   conservative-majority point) — but fold-fitness covaries with the gene
   inequality across every real champion this account has ever had, so the
   same three points sort just as monotonically by fitness as by the gene,
   and three uncontrolled real points can't separate the two explanations
   any better than the clamp could. **Do not pick this narrow side-question
   back up without a genuinely constructed fitness-held-fixed
   counterfactual** (re-tune some other gene after the clamp to restore the
   champion's original fold-fitness) — a real-champion comparison and a
   single-gene clamp have both now been tried and both hit the same wall.
   Does not touch the still-open selection-metric-redefinition question.

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

   **Tried 2026-08-20 (3-hourly check): the rolling half of the
   regime-stratified/rolling idea, and it doesn't fix the instability by
   itself.** (see "Current state" above and
   `runs/2026-08-20-1254-rolling-folds-and-holdout-noise-convergence.md`) New
   `rolling-folds` diagnostic (`loop.evolve.rolling_folds`, fixed-width
   overlapping windows instead of shrinking disjoint ones) shrinks the raw
   outlier gap as overlap rises but makes `aggregate_fitness` swing *more*
   than `fold-scheme`'s own n_folds sweep did, not less — `overlap`
   0.85/0.7/0.5/baseline gives 0.306/2.003/1.399/1.480. Reading: the cross-
   fold consistency penalty itself is sensitive to how many correlated
   windows feed it, so windowing changes alone (rolling or otherwise) likely
   need to come paired with a `FOLD_CONSISTENCY_WEIGHT` change, or the fix
   needs genuine regime-stratification (grouping by market character, not
   calendar position) instead of a denser calendar slide. Regime-
   stratification itself remains untried — would need a regime definition
   independent of the window under test (candidate: `regime`'s own per-
   window buy-and-hold characterization), and is real design work, not a
   tail-end addition.

   **Measured 2026-08-20 (3-hourly check): decomposed the aggregate swing,
   and it's the mean term, not the penalty term.** (see "Current state" above
   and `runs/2026-08-20-1556-fitness-decomposition-diagnostic.md`) The
   rolling-folds entry just above *inferred* the `FOLD_CONSISTENCY_WEIGHT *
   std` penalty term was driving the aggregate instability. New `fitness-decomp`
   diagnostic (`loop.evolve.fitness_decomposition`, `mean_term - penalty_term`
   reconstructs `aggregate_fitness` exactly, tested) measures the split
   directly across five schemes (disjoint `n_folds` 3/5, rolling overlap
   0.5/0.7/0.85): for v3 the aggregate ranges 2.100, mean term 1.500, penalty
   term only 0.610; for v1, aggregate 0.426, mean 0.609, penalty 0.183. Both
   champions: the mean of the fold fitnesses varies more than twice as much as
   the penalty. So retuning `FOLD_CONSISTENCY_WEIGHT` alone would *not*
   stabilize the aggregate — the dominant instability is the mean being
   dominated by one outlier window, which points more firmly at genuine
   regime-stratification (kill the permanent +200% outlier window) over the
   penalty-weight tweak the rolling-folds entry floated as one option.
   `fitness-decomp --also-version 2` (third champion) is a one-line follow-up
   not yet run.

   **Resolved 2026-08-20 (3-hourly check): ran that one-liner AND put a number
   on whether regime-stratification is worth the engine work — the melt-up is
   concentrated (~2.5x its even share at every resolution), so the answer is
   yes.** (see "Current state" above and
   `runs/2026-08-20-1855-regime-scan-melt-up-concentration.md`)
   `fitness-decomp --also-version 2` confirms the mean term (not the penalty)
   drives the aggregate swing in all three champions (v2 mean range 2.173 vs
   penalty 0.370). New `regime-scan` diagnostic
   (`loop.evolve.regime_concentration`, pure, tested, 8 tests, suite 151 up from
   143; read-only, genome-independent) measures how concentrated the searchable
   region's compounded growth is: `concentration_ratio` 2.75x at n=3 (one of
   three folds = 92% of |log-growth|), 2.57x at n=6, 2.45x at n=12 — the ratio
   holds ~2.5x as resolution rises, so the concentration is real, not a binning
   artefact. The n=12 scan exposes the mechanism: fold 2 is **two separated bull
   runs** (2023-10 +92.5%, 2024-08 +102.1%) colliding in one calendar fold —
   separable, i.e. exactly what a stratified scheme can split across folds
   without inventing or dropping data. This resolves the "is it worth the engine
   work" question in favour of yes, and hands the next builder the regime label
   to group on (`regime-scan`'s per-window b&h return). Still not started (it's a
   constitution change): `Evaluator` accepting a fold as a *set* of windows and
   `run_backtest` replaying a non-contiguous union of bars — needs a design pass
   + `AMENDMENTS.md` row.

   **Checked 2026-08-20 (3-hourly check): the 4h track shows the same
   concentration.** (see "Current state" above and
   `runs/2026-08-20-2200-regime-scan-4h.md`) `regime-scan --interval 4h`
   (12 windows, 8,766 4h bars): concentration ratio 2.47x, same order of
   magnitude as the 1d track's 2.45x, richest window's melt-up overlapping the
   same 2024-08 to 2024-11 bull run the 1d n=12 scan found. Closes the cheap
   follow-up the entry above flagged — no further regime-scan data is queued.
   The remaining work is the fold-scheme redesign itself, unstarted, needs a
   design pass + `AMENDMENTS.md` row, and is bigger than a 3-hourly slot.

   **Shipped 2026-08-21 (3-hourly check): the "needs engine work" assumption
   above turned out to be wrong for a first test, and `regime-folds` is that
   test.** (see "Current state" above and
   `runs/2026-08-21-0056-regime-folds-and-holdout-pressure.md`) A fold can be
   scored as several independently-backtested sub-windows merged together
   (`loop.evolve.regime_stratified_groups` + `Evaluator.evaluate_grouped`,
   both pure additions, tested, 16 new tests, suite 167 up from 151) without
   `run_backtest` or the constitution changing at all — no engine work, no
   `AMENDMENTS.md` row needed for this diagnostic itself. First reading
   against all three real champions: mixed (v3 +0.723, v1 +0.057, v2
   −0.065), and the dominant sub-window ends up isolated alone in its own
   fold rather than diluted across folds, which may not be the fix item 2's
   framing wanted. Next: sweep `--n-subwindows`/`--n-folds`, and settle
   whether isolating vs. forcing the dominant window to share a fold is the
   right objective before treating this as a verdict on regime-stratification
   either way. A genuine non-contiguous *single-replay* engine change (shared
   positions/compounding across a fold's sub-windows) is still unbuilt and
   would be a different, bigger question from what this diagnostic answers.

   **Swept 2026-08-21 (3-hourly check): the sweep is done, and it answers the
   isolating-vs-objective question — isolating is a double-edged mechanism,
   not a clean fix.** (see "Current state" above and
   `runs/2026-08-21-0351-regime-folds-nfolds-sweep.md`) At fixed 6
   sub-windows, raising `n_folds` 3→4→5 against v3 gives a clean monotonic
   trend +0.723 → +0.126 → −0.249: LPT balance isolates only the good
   outlier at low fold counts, but at higher counts it starts isolating a
   *bad* sub-window too, and the consistency penalty punishes that wide
   isolated-fold spread more than it rewards the good isolate. Cross-checked
   at `n_folds=5` against v1/v2: 2 of 3 champions lower, the third a wash —
   more consistent than the earlier `n_folds=3` mixed reading, suggesting
   that mixed result was itself a fold-count artefact. Reading: "isolate the
   dominant window" is not a general-purpose fix — it has no obviously
   correct fold-count operating point. Next: this points design attention
   away from windowing schemes entirely and toward a fix that targets the
   mean term's outlier sensitivity directly (e.g. capping/down-weighting one
   fold's contribution before averaging) — untried, real design work, still
   bigger than a 3-hourly slot, and would need its own `AMENDMENTS.md` row
   since any change to how promotion decisions are made should be argued in
   writing the same way constitution changes are. A genuine non-contiguous
   single-replay engine change remains a separate, unbuilt, bigger question.

   **Measured 2026-08-21 (3-hourly check): tried the mean-capping fix as a
   diagnostic, and it's the fourth independent windowing/capping mechanism to
   show the same champion-dependent, non-generalizing shape — recommend
   treating this whole line as exhausted.** (see "Current state" above and
   `runs/2026-08-21-0653-fold-cap-mean-winsorize.md`) New
   `loop.evolve.capped_fitness_decomposition(fold_fits, cap_z)` winsorizes
   each fold fitness to `mean + cap_z*std` before averaging (penalty term
   left uncapped, to isolate the mean-only effect), swept under the same 5
   fold schemes `fitness-decomp` uses. Against v3, capping made the
   cross-scheme range wider at every `cap_z` tested (0.657 → up to 0.977);
   against v1, the same mechanism tightened it (0.663 → down to 0.446).
   Mechanism: capping pulls down whichever scheme currently has the fattest
   single within-scheme outlier fold, and which scheme that is (relative to
   the other schemes' own aggregate) differs by champion, so the direction of
   the effect on the cross-scheme range isn't controlled by `cap_z` alone.
   This is the fourth mechanism in this thread (`fold-scheme`'s n_folds
   sweep, `rolling-folds`, `regime-folds`'s n_folds/n_subwindows sweep, now
   this) to independently land on the same shape: plausible per-champion, not
   general. Next: stop trying further windowing/capping variants on this
   line — the sharper, already-quantified, still-unstarted next step on the
   walk-forward-honesty question is `MULTIPLE_TESTING_SIGMA` recalibration
   (`holdout-noise` found the real sealed-holdout noise is 14-25x the
   constant `required_margin()` assumes, across all three real champions) —
   a constitution change needing its own design pass and `AMENDMENTS.md` row,
   not a fold-scheme tweak.

   **Shipped 2026-08-21 (3-hourly check): done — see "Current state" above and
   `runs/2026-08-21-0951-holdout-sigma-recalibration.md`.** New `HOLDOUT_SIGMA
   = 2.0` constant, used only by `holdout_accepts()`'s margin (via
   `required_margin()`'s new optional `sigma` parameter); `MULTIPLE_TESTING_SIGMA`
   and the fold-aggregate margin it protects are untouched. `AMENDMENTS.md` row
   added, full suite 179 passed, `evotrader.manifest` resealed at
   `8b74865634b1db07`. This closes the walk-forward-honesty thread's second
   half (the first half — the windowing/capping line above — is set aside as
   exhausted across four independent mechanisms, not closed, just not worth
   further variants for now). Remaining open question, carried into the new
   constant's own docstring: `HOLDOUT_SIGMA` measures realized-return-path
   resampling noise only, not the added noise from a candidate arriving
   pre-selected by correlated folds — a harder, unquantified question, not
   picked up this run.

   **Measured 2026-08-21 (3-hourly check): new `margin-curve` diagnostic puts
   real numbers on "gets harder to clear as n rises" instead of leaving it a
   qualitative claim, and it turns out the two gates are not in the same
   place on that curve.** (see "Current state" above and
   `runs/2026-08-21-1553-margin-curve-diagnostic.md`) Pure arithmetic on
   `constitution.required_margin` (`sigma * sqrt(2*ln(n))`, unchanged), no
   market data or backtest. At the real live counts (182 fold-aggregate
   candidates, 13 sealed-holdout draws): the fold-aggregate margin is nearly
   saturated (0.258 now, +0.10 more needs ~123x more candidates, +0.25 more
   needs ~574 million) — so a near-miss fold-aggregate candidate is not
   meaningfully pushed further out of reach by more search volume, live or
   shadow. The sealed-holdout margin is NOT saturated at its much smaller
   real draw count — only 4 more draws raise it +0.25. Reading: the rising-bar
   stagnation mechanism the 13:07 run named applies for real to the holdout
   gate (which never resets its cumulative count on a promotion) far more
   than to the fold-aggregate gate, which is already close to flat. Next:
   whoever next gets a real candidate to the sealed-holdout check should note
   the cumulative-draw count at that moment alongside the `HOLDOUT_SIGMA`
   outcome — it visibly moves at today's scale, unlike the fold-aggregate
   count.

   **Mapped 2026-08-21 (3-hourly check): the universe-perturb drawdown cliff
   from the 19:02 run is at the doorstep, not 20% away.** (see "Current
   state" above and
   `runs/2026-08-21-2210-universe-perturb-single-symbol-cliff.md`) No new
   code — a `--drop-frac` sweep (noisy at n=6/frac, not conclusive) plus an
   exhaustive `--drop SYM` census of all 27 symbols individually. Result:
   14/27 symbols (51.9%) hard-fail `MAX_DD_HARD_FAIL` when dropped ALONE
   (baseline maxDD -34.1% vs the 40% threshold, only 5.9pp margin). Next: an
   honest design pass on whether `MAX_DD_HARD_FAIL`'s margin is right given
   this — a constitution change needing its own `AMENDMENTS.md` argument —
   not attempted; this line is otherwise answered for now.

   **Superseded 2026-08-22 (3-hourly check): the -34.1% baseline this whole
   sub-thread rests on may itself be wrong — do not resume the design pass
   until re-checked.** (see "Current state" above and
   `runs/2026-08-22-0100-maxdd-jump-and-fetch-truncation-bug.md`) Same
   computation, this session: -46.5% baseline maxDD, already past
   `MAX_DD_HARD_FAIL`, no perturbation at all. Traced to (and fixed) a real
   silent-truncation vulnerability in `core.market.fetch_klines`'s pagination
   (a short page was treated as unconditional end-of-history, indistinguishable
   from a transient partial response) plus a new `find_gaps`/`load_universe`
   warning to catch it going forward — but whether this bug is *why* every
   prior session this week read -34.1% is a plausible, evidence-fitting
   explanation, not a proven one; there's no way to audit a past container's
   gitignored cache after the fact. Next, before anything else on this line:
   re-run the full 27-symbol single-drop census fresh (now gap-checked) and
   see which number survives. If -46.5% (or close) holds up clean, that's a
   bigger deal than a design pass on the gate's margin — it means the live
   champion's own unperturbed full-history backtest may be failing its own
   risk gate right now.

   **Fixed 2026-08-22 (weekend all-hands): -46.5% held up clean
   (`fold-dd-blindspot`, same day), and the design pass this sub-thread was
   waiting on is done.** See "Current state" above for the full mechanism
   and `AMENDMENTS.md` for the constitution-level argument.
   `EvolutionRun.generation()`'s promotion gate now checks a genome's max_dd
   as the worse of its fold-merged number and one true continuous replay
   over the same span, closing the exact blind spot this sub-thread traced
   from a suspected data bug through to a real structural gate failure.
   Verified against real data and a live shadow-evolve run, not just unit
   tests. This closes the `MAX_DD_HARD_FAIL`-margin design pass this
   sub-thread (and the 2026-08-21 universe-perturb-cliff entry before it)
   both deferred — not by moving the margin, but by fixing what the gate
   actually measures, which was the sharper and more honest of the two
   options. Open remainder, deliberately not decided by this fix: champion
   v3's own true drawdown already exceeds the corrected gate, and whether
   that should trigger a demotion/re-evolution is unresolved — see "Current
   state" above.

   **Sharpened 2026-08-22 (3-hourly check): the open remainder above isn't
   just a paper-loss/optics question — while v3 stays champion, its own
   `fitness() == -inf` disables one of `accepts()`'s two champion-relative
   safety checks entirely and loosens the other, confirmed firing in real
   shadow generations (2/30 candidates checked).** See "Current state" above
   and `runs/2026-08-22-1015-dd-gate-vacuous-regression-check.md`. No code
   change, no promotion incorrectly let through (both cases still correctly
   failed the sealed holdout) — but each such pass burns a scarce,
   never-reset holdout draw the gate wouldn't otherwise have spent. Adds a
   mechanistic reason, not just a magnitude one, to the still-unresolved
   demotion question.

   **Tracked further 2026-08-22 (two more 3-hourly checks): cumulative rate
   now 5/144 real shadow candidates, session counts 2/30, 0/54, 3/60 — noisy
   but non-vanishing, and round 3 also produced the first case where the
   intended-tightening direction was the actual reason for a rejection.**
   See "Current state" above and
   `runs/2026-08-22-1322-shadow-evolve-vacuous-check-round2.md` /
   `runs/2026-08-22-1629-shadow-evolve-vacuous-check-round3.md`. Still no
   incorrect promotion in any of the three sessions' samples. Still the
   owner's call whether this sharpens the case for prioritizing the
   demotion/rollback design pass.

   **Built 2026-08-22 (3-hourly check): new `succession-audit` diagnostic
   answers the one fact this whole demotion/rollback sub-thread had never
   asked — would v1/v2 actually pass today's dd-corrected gate if
   reinstated — and no real champion does.** See "Current state" above and
   `runs/2026-08-22-1854-succession-audit-diagnostic.md`. v1/v3 fail the
   simple full-history maxDD test outright. v2's full-history number looks
   clean (-38.1%, under the 40% line) but its fold-merged maxDD (-40.1%,
   fold 2's own rebased-NAV local peak-to-trough) still hard-fails the
   dd-corrected gate a real promotion decision actually uses — a new,
   opposite-direction wrinkle in `dd_corrected_stats()`'s `min()`-only design
   (it can tighten an understated fold-merged number, per the original
   blind-spot fix, but can't loosen an overstated one). "Revert to v2" is
   therefore not the easy fix it looks like from the headline full-history
   number. If/when the owner opens the demotion/rollback design pass, this
   is the fact base to start from.

   **Resolved 2026-08-23 (3-hourly check, 22:16 UTC): the "convergence
   across independent seeds" open question, never tested at the live 1d
   cadence (only at 4h, above) — a fresh unscaled seed does NOT reliably
   converge to anything within a realistic budget.** See "Current state"
   above and `runs/2026-08-23-2216-fresh-seed-1d-shadow-evolution.md`. 16
   generations, 235 proposals, zero promotions — unlike every 4h run's
   quick first fix. Root cause: the plain `SEED_GENOME`'s own sealed-holdout
   fitness (`-2.566`) is far worse than its fold-aggregate fitness
   (`-0.022`), and `holdout_accepts()`'s multiple-testing margin (by design)
   grew from 2.355 to 4.761 across the 17 candidates that reached the
   holdout gate, so even the best holdout score any candidate drew
   (`+0.290`) never came close. Mirrors, and sharpens, the 2026-08-18
   "lucky champion is hard to unseat" finding: an unlucky seed traps itself
   the same way, and more generations only deepen the trap (each
   fold-clearing proposal burns another draw and raises the bar) rather than
   escaping it. Not chased further: whether this fold/holdout gap is
   specific to the current 4-year data window or a durable property of
   `SEED_GENOME` itself.

   **Measured 2026-08-24 (3-hourly check): the seed's poor holdout score is an
   ordinary draw from its own noise, not an outlier.** See "Current state"
   above and `runs/2026-08-24-0049-seed-holdout-noise-diagnostic.md`. A
   one-off script (not a new CLI command — this genome isn't in
   `live_state.json`'s lineage, so `holdout-noise`'s own `--also-version`
   flag doesn't reach it) block-bootstrapped the seed's own sealed-holdout
   return path (fresh window, one day later than the prior entry: -1.194
   this time, not -2.566, purely from the date shift) 2000 times across 4
   RNG seeds. Real fitness lands within 0.13 sigma of its own bootstrap mean
   every time, and the bootstrap sigma itself (~1.77-1.85) matches the same
   range `holdout-noise` already measured for all three real champions
   (1.21-2.04) — not exceptional either way. Reading: the seed genuinely
   performs badly on this holdout window; it isn't a fluke of return-order
   noise. Combined with the entry above, the picture is a genuinely bad seed
   on a genuinely bad window, correctly and consistently rejected by the
   gates — not a bug. Still open, and explicitly bigger than a
   noise-vs-signal question: whether a *different* 4-year data pull would
   show the seed in a better light at all (a question about `SEED_GENOME`'s
   robustness across market regimes generally, not attempted here).

   **Built 2026-08-24 (3-hourly check, ~12:47 UTC): `succession-audit` gets
   the two-sided comparison the 2026-08-22 entry above flagged as missing.**
   See "Current state" above and `tests/test_continuous_max_dd.py`'s four
   new tests. New `loop.evolve.dd_trust_continuous_stats()` is a
   diagnostic-only sibling of `dd_corrected_stats()` — instead of
   `min(fold-merged, continuous)`, it always trusts the continuous replay's
   `max_dd` outright, so it can recover a truer, better number in the
   overstatement direction `min()` can't (v2's case). `succession-audit`
   now prints this as a `trust-cont fit` column next to the existing
   `dd-corr fit` one. Explicitly NOT wired into `accepts()` or
   `EvolutionRun.generation()` — no live gate behavior changed, no opinion
   offered on whether it should be. This closes the specific "build the
   missing case" loose end the 2026-08-22 entry named, but does not restart
   or resolve the demotion/rollback design question itself, which remains
   the owner's call, unchanged.

   **Closed 2026-08-30 (3-hourly check, ~18:51 UTC): the demotion/rollback
   design question this sub-thread flagged as unstarted across every entry
   above finally has a design pass and a recommendation.** See "Current
   state" above and
   `runs/2026-08-30-1851-demotion-rollback-design-pass.md`. Recommendation:
   status quo, no demotion mechanism — a fresh `succession-audit` shows v3
   is the best of the three real champions on both drawdown-gate-closeness
   and full-history excess return (+68.2%, the only positive one of the
   three), so there is nothing better to demote *to*. Same closure pattern
   as the 06:00 UTC weekend all-hands used for the fitness-vs-excess-return
   question, with three named revisit triggers. **Future sessions: do not
   re-open this from scratch — point to the write-up unless one of its
   three triggers has actually fired.**

   **Measured 2026-08-24 (3-hourly check, ~16:15 UTC): a first number on the
   "harder, unquantified" selection-noise question the 2026-08-21
   `holdout-sigma-recalibration` entry left unchased.** See "Current state"
   above and `runs/2026-08-24-1615-selection-noise-diagnostic.md`. Six
   independent draws of real `Researcher.propose`/`Evaluator.evaluate`
   batches against real champion v3: each draw's fold-aggregate winner (what
   `EvolutionRun.generation()` actually carries to the holdout gate) and one
   randomly-picked non-winner from the same batch both ran through the
   sealed holdout (`generation()` itself never evaluates holdout for a
   non-finalist). Caught and fixed a real methodology bug first — a fresh
   `exclude=set()` every draw let the same deterministic
   `from_diagnosis()`/`structural()` proposal win all 6 draws identically,
   since only `perturb()` depends on the Researcher's seed; fixed by
   accumulating `exclude` across draws like `EvolutionRun.tested` really
   does. Result: winner's mean (fold − holdout) gap +2.172 (std 0.928, n=6)
   vs random's +0.990 (std 1.274, n=6), winner larger in 4/6 draws, paired
   t≈1.55 — directionally consistent with a winner's-curse-style selection
   effect, **not statistically significant at n=6**. A first measurement,
   not a settled answer: still open, and not attempted here — more draws to
   sharpen significance, a second champion, or (if a larger sample confirms
   the effect) translating it into an actual correction, which would be a
   constitution change needing its own design pass and `AMENDMENTS.md` row,
   not a natural extension of one measurement session.

   **Measured 2026-08-24 (3-hourly check, ~18:57 UTC): the "more draws" follow-up
   weakens the signal instead of sharpening it.** See "Current state" above and
   `runs/2026-08-24-1857-selection-noise-batch2.md`. Same method, 6 more
   independent draws (n_blind=10, exclude accumulated) against the same real
   champion v3. Batch 2 alone reverses the direction (random gap mean 1.818 >
   winner gap mean 1.679, paired t=−0.218). Combined 12-draw sample: paired
   t≈1.02 (df=11), weaker than batch 1's t≈1.55 alone — the opposite of what
   "just needs more data" would predict if the effect were real, driven by a
   variance blowup in batch 2's random-gap draws (one outlier at −1.358, the
   only negative gap either batch produced). **Reading revised**: no good
   evidence yet of a winner's-curse selection effect distinct from ordinary
   per-candidate holdout noise; batch 1's number now looks like a favorable
   draw from a noisy distribution rather than the start of a sharpenable
   signal. Leaving this question here — further identical-method batches are
   unlikely to resolve it either way; would need an order-of-magnitude more
   draws or a genuinely different check (e.g. a second champion) to be worth
   another session. No `HOLDOUT_SIGMA`-style correction proposed; the evidence
   doesn't support one.

   **Measured 2026-08-24 (3-hourly check, ~22:01 UTC): the "second champion"
   check named above — and it replicates the direction.** See "Current
   state" above and `runs/2026-08-24-2201-selection-noise-second-champion.md`.
   Same six-draw method against reconstructed champion v2 instead of v3:
   winner gap mean +1.851 vs random gap mean +0.237, winner larger in 5/6
   draws, paired t≈1.667 (df=5) — similar shape and strength to v3 batch 1
   (t≈1.55), not diluted the way v3's own batch 2 diluted it. Neither
   champion is individually significant, but two unrelated genomes landing
   on the same direction and similar magnitude is meaningfully stronger
   evidence than either alone, without being strong enough to justify a
   `HOLDOUT_SIGMA` change. Next, if this stays worth resolving: a
   genome-stratified or mixed-effects pooled test across all 18 draws so
   far (6 v3-batch1 + 6 v3-batch2 + 6 v2), not another same-shape batch.

   **Measured 2026-08-25 (3-hourly check, ~01:00 UTC): the genome-stratified
   pooled test named above — done.** See "Current state" above and
   `runs/2026-08-25-0100-selection-noise-genome-stratified.md`. Pure
   arithmetic on the 18 already-collected draws, no new backtests: Cochran's
   Q (0.994, df=1) found no detectable heterogeneity between v3 and v2, so
   the "samples aren't from one distribution" objection that blocked pooling
   isn't supported by this data (weak evidence at df=1, but not the
   roadblock it looked like). Properly pooled: fixed-effect mean +0.761
   (z≈1.678, one-sided p≈0.047); a block-stratified sign-permutation test
   (200,000 resamples, assumption-light) gives p≈0.0635 — closer to
   conventional significance than either genome alone but not a clean
   cross. Still not enough to justify touching `HOLDOUT_SIGMA`. Closes this
   specific design loose end; the concrete next step if this stays worth
   pursuing is a third genome (v1, or a future champion) to give the
   heterogeneity test real power, not another batch or permutation variant
   on the same two genomes.

   **Measured 2026-08-25 (3-hourly check, ~04:02 UTC): the third genome
   named above -- done, and it closes this line of inquiry.** See "Current
   state" above and `runs/2026-08-25-0402-selection-noise-third-genome.md`.
   Champion v1 (the unevolved seed) shows essentially no selection-noise
   signal (paired t~0.121, winner gap larger in only 2/6 draws) -- the
   weakest of the three genomes tested. Extending the pooled design to 3
   blocks moves the evidence away from significance (z 1.678->1.340,
   permutation p 0.0635->0.0815, Cochran's Q 0.994->2.030 at df=2, still not
   significant). Four sessions in, every new independent unit of evidence (a
   second v3 batch, a second champion, now a third genome) has weakened the
   pooled estimate rather than sharpening it toward significance -- the
   signature of a null or sub-noise effect. `HOLDOUT_SIGMA` untouched.
   **Closing this line of inquiry**: worth reopening only on a cheap fourth
   genome (a future v4+ promotion) or a genuinely different, sharper
   hypothesis -- not another same-method batch or genome.

   **Found 2026-08-30 (3-hourly check, ~23:05 UTC): a fresh 4h shadow run —
   the first since the dd-corrected gate was wired into `generation()`'s
   acceptance loop (2026-08-21/22) — shows the "reliable gen-1 quick fix"
   pattern every prior 4h-shadow run relied on no longer holds, plus a
   first, caveated 4h `holdout-noise` number.** See "Current state" above
   and `runs/2026-08-30-2305-4h-shadow-dd-corrected-gate-and-holdout-noise.md`.
   8 generations, x6-scaled seed, `n_blind=6`, same isolation discipline as
   every prior run here: **zero promotions**, where every prior run (all
   pre-dating the fix) found one in generation 1. Each generation's top
   fold-aggregate candidate looked like the usual fix but got rejected by
   the dd-corrected hard gate (continuous-replay maxDD > 40%, invisible to
   the fold-merged number) about as often as by the sealed holdout.
   Block-bootstrapped the only genome produced (the never-promoted seed):
   boot_fitness_std 1.461, 0.73x `HOLDOUT_SIGMA` — weakly supports "more
   holdout bars (~6x here), less relative noise" but isn't apples-to-apples
   with the 1d measurement (real promoted champions there, a rejected seed
   here). **Next, concretely**: a longer or differently-seeded x6-scaled 4h
   run to check whether *any* genome can clear the dd-corrected gate
   post-fix — the prerequisite for both a real 4h holdout-noise measurement
   and for meaningfully re-asking this thread's older "does a second
   plateau exist" question, which implicitly assumed the now-invalidated
   easy-gen-1-promotion shape. Not attempted further this session (time
   budget after the ~70 min evolution phase already spent).

   **Found 2026-08-31 (3-hourly check, ~02:43 UTC): a second, differently-seeded
   run also found zero promotions, via a different rejection-mechanism split.**
   See "Current state" above and
   `runs/2026-08-31-0243-4h-shadow-seed9001-still-zero-promotions.md`.
   `EvolutionRun(seed=9001)` instead of the default `seed=7` every prior
   4h-shadow session had used (this thread's own flagged follow-up), 14
   generations, same x6-scaled seed and isolation discipline. Champion
   pinned at fitness -4.296 throughout; of 42 rejections, 74% failed the
   dd-corrected hard gate and 26% failed the sealed holdout -- roughly
   inverted from the 23:05 UTC run's 40%/60% split, but the same end result
   (zero promotions). Two independent seeds now agree: this isn't a
   seed-specific artifact of one `Researcher` proposal sequence.
   **Recommend not running further seeds of this same scaled-seed
   construction** -- the open question is now which of two structurally
   different things is true: the x6-scaled seed itself is too aggressive
   (4413 search-fold trades, halts 5, fitness -4.296 -- none of which any
   real live 1d champion has ever shown) for this gate to clear from at
   all, or a genuinely retuned (not just scaled) 4h starting point would
   behave differently. That's a bigger experiment than another
   same-seed-genome run and wasn't attempted this session.

   **Ruled out 2026-08-31 (3-hourly check, ~04:07 UTC): two un-scaled
   bar-count harness constants are not the explanation -- see "Current
   state" above and
   `runs/2026-08-31-0407-4h-shadow-warmup-cooldown-ruled-out.md`.** Tested
   `run_backtest`'s `warmup=60` default and `constitution.
   CIRCUIT_BREAKER_COOLDOWN=20`, both of which the x6-period-gene-scaling
   recipe never touched, against their own x6-scaled values (360, 120) on the
   same seed genome and data. Neither changed fitness, trade count, halt
   count, or drawdown beyond noise (fitness -4.30 to -4.32 vs. baseline
   -4.296). Reframes the still-open question from "might this be a harness
   artifact" to a cleaner "the seed is genuinely this aggressive on its own
   terms" -- strengthens rather than settles hypothesis 1, and still leaves
   hypothesis 2 (a genuinely hand-retuned, not scaled, 4h starting point) as
   the next real experiment, not attempted here.

   **Found 2026-08-31 (3-hourly check, ~07:05 UTC): the overtrading mechanism
   is entry frequency, not faster round-trips, and a new candidate confound
   is tested and ruled out -- see "Current state" above and
   `runs/2026-08-31-0705-4h-shadow-entry-frequency-diagnostic.md`.** Three
   single-shot `run_backtest()` calls (v3 at 1d, x6-scaled seed at 4h,
   raw-unscaled seed at 4h -- no evolution needed) found the x6-scaled seed
   trades 4.6x more often per year than v3 but holds each position for a
   similar-or-longer time (10.71 vs 9.09 days) -- many more distinct entries,
   not quicker exits. Then tested `superior_judge.max_new_positions_per_bar`
   (seed value 3, a per-*bar* cap never touched by any x6-scaling recipe --
   at 4h it's up to 18 new positions/day vs the 1d-intended 3/day): tightening
   it to 1 moved every metric by noise-scale amounts only. **Ruled out**, same
   shape as the 04:07 UTC warmup/cooldown result. Sharpens hypothesis 2 into
   something concretely scoped for the next session: the consult *threshold*
   genes (RSI bands, z-score bands, `min_trend`/`min_breakout`/`min_rank_mom`)
   were never touched by any scaling or hand-tuning attempt so far -- widening/
   tightening those specifically, independent of period scaling, and
   re-measuring trade frequency the same way, is the recommended next concrete
   step, not another same-construction run or a from-scratch full hand-retune.

   **Tested 2026-08-31 (3-hourly check, ~10:02 UTC): tightened nine consult
   threshold genes as recommended -- trades/yr dropped as predicted but
   drawdown got worse, not better -- and this session's baseline didn't
   reproduce the 07:05 UTC session's baseline, an unresolved discrepancy.**
   See "Current state" above and
   `runs/2026-08-31-1002-4h-shadow-threshold-tighten.md`. Tightened
   `min_rank_mom`/`rsi_max`/`min_breakout` (consult_risky), `min_trend`/
   `rsi_lo`/`rsi_hi`/`min_rank_mom` (consult_moderate), `rsi_buy_below`/
   `z_buy_below` (consult_conservative) on the x6-scaled seed. Trades/yr:
   392.7 -> 327.8 (-16.5%, confirms the noise-threshold hypothesis
   qualitatively), but max_dd -44.3% -> -48.0% (worse), halts 6 -> 8,
   sortino 0.94 -> 0.76, sharpe 0.77 -> 0.65 -- fewer entries did not mean a
   shallower drawdown. **Ruled out "just tighten the thresholds" as a
   free-lunch fix** (one specific combination/direction tried, not
   exhaustive). Separately and more sharply: this session's own baseline for
   the *same* x6-scaled seed construction (392.7 trades/yr, -44.3% max_dd,
   sortino +0.94) doesn't match the 07:05 UTC session's recorded baseline
   (1278 trades/yr, -66.1% max_dd, sortino -0.29) -- checked and ruled out
   gene-construction mismatch (full genome dump verified gene-by-gene
   against the documented x6 recipe), data gaps (clean 8766-bar/symbol
   fetch, no warnings), and `run_backtest`'s `warmup` default (60 vs. 360
   moves the baseline by noise only, ~393 vs ~406 trades/yr). No RNG is
   reachable from a plain `run_backtest()` call, ruling out non-determinism
   too. Neither session's scratch script was committed, so a direct diff
   isn't possible after the fact. **Recommend a future session commit a
   small, never-scheduled, reusable scratch harness for this specific
   recipe** (build x6-seed, fetch 4h universe, single-shot full-history
   `run_backtest()`) so results become diffable and this class of
   cross-session discrepancy stops recurring silently -- and treat any
   single prior 4h-shadow baseline number with more caution until then.
   `git status` clean, `live_state.json` md5 unchanged
   (`37a1b00bee3f7cb1ad2f4adde0ab9ed0`), `python3 -m pytest -q` 243/243
   confirmed at session start, no code changed, genome still v3 (1d).

   **Shipped 2026-08-31 (3-hourly check, ~12:47 UTC): the recommended reusable
   scratch harness — see "Current state" above and
   `runs/2026-08-31-1247-shadow-4h-harness.md`.** `tools/shadow_4h_x6_seed.py`
   commits the x6-scaled-seed recipe as one importable function
   (`build_x6_scaled_seed`, via `Genome.child()`) plus a CLI that fetches the 4h
   universe and runs one single-shot full-history `run_backtest()`, so every
   future session gets the same genome construction instead of re-deriving it
   from this thread's prose. 9 new hermetic tests (no network) check the
   scaling math and leave-untouched genes; a live run against warm-cached data
   reproduced the 10:02 UTC session's baseline exactly (392.7 trades/yr, -44.3%
   max_dd, sortino 0.94), which is strong evidence the 07:05-vs-10:02 gap was a
   real construction difference in an uncommitted script, not noise — though
   without that script the exact divergence stays unrecoverable. Use this
   harness, not a fresh scratch script, for the next variant test (correlation
   penalty on the x6-scaled seed is the standing suggestion from 07:05 UTC).

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

   **Design pass done 2026-08-30 (3-hourly check, ~09:51 UTC), no code
   shipped — see "Current state" above and
   `runs/2026-08-30-0951-short-selling-design-pass.md`.** Traced long-only
   to five independent places needing real work (`core.portfolio.PaperBroker`,
   `core.types.Intent`/`Order`'s side vocabulary, all three
   `agents.consults` modules, `agents.judges.RiskJudge.rule`, and the
   circuit breaker's bounded-downside assumption), worked out the
   borrow-cost approximation is the same *kind* as existing `fee_bps`/
   `slippage_bps` constants, and flagged two constitution questions a real
   proposal would need to resolve (a short-exposure cap; whether
   `MAX_DD_HARD_FAIL` needs a short-specific instrument given the unbounded
   downside). **Next, concretely scoped now**: Phase 1 —
   `PaperBroker.short()`/`.cover()` + per-bar borrow accrual in `.mark()`,
   tested in isolation (short→mark→cover round trips, borrow accrual,
   a circuit-breaker trip mid-short), zero behavior change for every
   existing caller since nothing calls the new methods yet. Phase 2
   (genome/agent wiring + the constitution questions, each needing its own
   `AMENDMENTS.md` row) and Phase 3 (shadow evolution) come after Phase 1,
   not before.

   **Corrected 2026-08-30 (3-hourly check, ~13:01 UTC): Phase 1 above is not a
   no-sign-off engineering slice — see "Current state" above.**
   `core/portfolio.py` is one of exactly two files `constitution.checksum()`
   literally hashes (`_PROTECTED` in the `constitution` module), sealed by
   `evotrader.manifest`; editing it and running `tools/edit_bundle_module.py
   sync` breaks that seal (`CONSTITUTION MODIFIED`), and this file's own Run
   protocol rule says a scheduled session must stop there and not re-seal it,
   not ship and move on. Actually implementing Phase 1 this session
   (signed-`qty` `Position`, `short()`/`cover()` mirroring `buy()`/`sell()`,
   `borrow_bps_per_bar` accrued in `mark()`, 16 passing unit tests exactly
   matching the isolation tests named above) hit exactly this wall; reverted
   in full (`git checkout -- core/portfolio.py evotrader_bundle.py`, deleted
   the new test file) rather than leave the seal broken for the next scheduled
   run. **Do not attempt to ship Phase 1 code again without a human review and
   `evotrader.manifest` re-seal in hand first** — that sign-off was supposed to
   wait for Phase 2's constitution questions, not gate Phase 1's broker
   mechanics too. The design itself held up under real implementation and is
   worth keeping as the starting point once that sign-off exists.

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

   **Done 2026-08-23 (weekend all-hands): the safe half of the unflatten
   itself — see "Current state" above and
   `runs/2026-08-23-0600-weekend-all-hands.md`.** Real `core/`/`agents/`/
   `loop/`/`constitution/` packages now exist on disk, byte-identical to the
   bundle's own `_SRC` entries, verified by re-running the full test suite
   against them directly (192/192, matching baseline) plus a new permanent
   drift guard (`tests/test_unflattened_files_match_bundle.py`, 17 tests).
   The live path is untouched — `evotrader_bundle.py` is still what every
   scheduled command runs, byte-identical before/after. Still open, and
   explicitly the riskier remainder: no bundler exists to regenerate the
   bundle from the real files (so hand-editing a real file today would drift
   silently past the new test's byte-for-byte check unless
   `tools/edit_bundle_module.py reinsert` is also run), and no CLI entrypoint
   runs the live commands against the real files — both needed before this
   item can be called fully closed, both bigger and separate from this
   session's scope.

   **Done 2026-08-23 (3-hourly check): the bundler now exists — see "Current
   state" above and `runs/2026-08-23-0648-bundle-sync-tool.md`.**
   `tools/edit_bundle_module.py sync [--check]` regenerates every `_SRC`
   entry from the real files (or reports drift without writing), verified
   both synthetically (10 new tests) and against the real repo (a true
   no-op today, and correctly flags a deliberately-induced one-line edit as
   drift). Hand-editing a real file directly and running `sync` now keeps
   the bundle honest without needing `tools/edit_bundle_module.py reinsert`
   as a separate manual step. **Item 7's one remaining piece**: no CLI
   entrypoint runs the live commands (`tick`/`summary`/`evolve`/...) against
   the real files instead of the bundle — that's the actual cutover, still a
   bigger, riskier, separate session, not attempted here.

   **Done 2026-08-23 (3-hourly check): a safe first slice of that remaining
   piece — see "Current state" above and
   `runs/2026-08-23-0946-run-from-files-entrypoint.md`.** New
   `run_from_files.py` runs `summary`/`signals` (the two commands that never
   write to `live_state.json`) against the real files, verified
   byte-for-byte identical to the bundle's output for the same commands.
   Still open, and still the riskier remainder: `tick`/`evolve` (the
   state-mutating commands) are not wired up against the real files, and no
   scheduled run has been pointed at this file instead of the bundle — that
   decision, and the work to get there safely, is still a separate, bigger
   session.

   **Grown 2026-08-23 (3-hourly check): `run_from_files.py`'s read-only
   surface widened to `holdout-pressure` and `regime` — see "Current state"
   above and `runs/2026-08-23-1254-run-from-files-diagnostics.md`.** Both
   transcribed verbatim from the bundle, verified byte-identical output.
   Still open, and still the actual point of this item: `tick`/`evolve`
   against the real files, and the decision to ever point a scheduled run
   here instead of at the bundle — a separate, bigger, riskier session, not
   moved forward by this or any prior read-only-surface addition.

   **Grown further 2026-08-23 (3-hourly check, 15:46 UTC): a third
   diagnostic, `fold-dd-blindspot` — see "Current state" above and
   `runs/2026-08-23-1548-run-from-files-fold-dd-blindspot.md`.** Same
   verbatim-transcription discipline, verified byte-identical output with
   and without `--also-version`. Still open, and still the actual point of
   this item: `tick`/`evolve` against the real files, and the decision to
   ever point a scheduled run here instead of the bundle. This makes four
   sessions today growing this read-only surface (entrypoint, then two more
   diagnostics, now this one) without touching that actual cutover — the
   next session picking up item 7 should weigh whether continuing to widen
   the read-only surface is still the highest-value use of a slot, versus
   either attempting a scoped piece of the real cutover (e.g. a `signals`-
   style dry-run of `tick`'s decision logic that stops short of `acct.save()`)
   or picking up a different open item entirely.

   **Done 2026-08-23 (3-hourly check, 18:45 UTC): took the scoped piece the
   entry above floated — see "Current state" above.** New `tick-dry-run`
   command runs the real `LiveAccount.tick()` end-to-end (market data,
   Council, both judges) against the real files but never calls
   `acct.save()`, verified against the live state (matches
   `evotrader_bundle.py tick`'s own bar/tick number on the skip path,
   `live_state.json` md5 unchanged). This is the first command in
   `run_from_files.py` to touch the state-mutating method at all — a
   meaningfully different, narrower kind of safety guarantee than the five
   purely-read-only commands before it. **Still open, and now the sharper
   remaining piece**: `tick-dry-run` has only been exercised on an
   already-traded bar (the skip path) — its non-skip branch (a genuine new
   decision, built from a real would-be order list) is untested against
   live data because no bar has been open-and-untraded at the moment a
   session ran it yet; and the actual cutover — a *saving* `tick` (and
   `evolve`) against the real files, plus the decision to ever point a
   scheduled run at `run_from_files.py` instead of the bundle — remains
   separate, bigger, and riskier, not attempted here.

   **Done 2026-08-24 (3-hourly check): the non-skip branch now has automated
   coverage — see "Current state" above and
   `tests/test_run_from_files_matches_bundle.py`'s two new
   `test_tick_dry_run_*` tests.** Sidesteps the live-timing blocker entirely
   with a fully synthetic scratch universe instead of waiting for a session
   to land in the narrow post-close-pre-00:20-UTC window. This closes the
   "untested against a real decision" gap the entry above flagged, but it is
   deliberately not the same thing as verifying against real live data with
   a real would-be order list — that specific check (real files, real
   universe, a genuinely untraded bar) is still open and still requires that
   narrow window; whoever next lands in it should still run `tick-dry-run`
   first, same as the 2026-08-23 18:45 UTC entry originally suggested. The
   actual cutover — `tick`/`evolve` saving against the real files, and the
   decision to ever point a scheduled run at `run_from_files.py` instead of
   the bundle — remains separate, bigger, and riskier, not attempted here.

   **Done 2026-08-24 (3-hourly check, ~06:56 UTC): `evolve-dry-run` ships —
   see "Current state" above and `runs/2026-08-24-0656-evolve-dry-run.md`.**
   The second and last state-mutating command (`evolve`, alongside `tick`)
   now has a tested dry-run twin: runs the real `loop.evolve.EvolutionRun`
   against the real files but never calls `acct.save()`, verified with a
   new ~4.1-year synthetic universe fixture (`evolve`'s own `load_universe`
   window is 4y, wider than `tick-dry-run`'s 1.5y one) and two new tests
   covering both the never-saves guarantee and the researcher-memory resume
   wiring. Both of `run_from_files.py`'s missing commands relative to the
   bundle are now at least dry-run-safe. **Still the actual remaining
   piece, unchanged by this**: a genuinely *saving* `tick`/`evolve` against
   the real files, and the decision to ever schedule a run against
   `run_from_files.py` instead of the bundle at all — both explicitly
   bigger and riskier, not attempted here. With both dry-run commands done,
   that decision — not another dry-run or read-only addition — is the
   natural next checkpoint for whoever next picks up this item.

   **Done 2026-08-24 (3-hourly check, ~09:46 UTC): the actual cutover
   shipped — see "Current state" above.** `run_from_files.py tick`/`evolve`
   now genuinely call `acct.save()`, transcribed verbatim from the bundle's
   own command bodies. The 09:00 UTC daily discussion the same day checked
   explicitly whether this needed owner sign-off before proceeding and
   concluded it didn't (an engineering/testing milestone the existing
   byte-identical-verification discipline already covers, not a
   real-money or risk-appetite call). Item 7 is now feature-complete
   relative to the bundle: every state-mutating command exists in both
   dry-run and real form against the real files, proven equivalent to the
   bundle's own behavior by direct subprocess comparison (`tick`) or by
   comparison against its own dry-run twin (`evolve`, since the bundle's
   `evolve` has no `--seed` flag to pin a subprocess comparison down with).
   **What's left is deliberately not engineering**: no scheduled run has
   been pointed at `run_from_files.py` instead of the bundle, and
   `evotrader_bundle.py` remains what every scheduled command actually
   runs. Whether to ever make that switch — and if so, whether to cut over
   all at once or command-by-command, and what if anything should keep the
   bundle as a fallback — is a migration-policy question, not a
   correctness one; nothing currently forces it, since the bundle and the
   real files are now proven to behave identically and either can be
   maintained going forward (`tools/edit_bundle_module.py sync` keeps them
   that way). Not attempted here, and not obviously worth attempting
   without a reason to prefer one entrypoint over the other beyond "it's
   more files" — flagging this explicitly so the next session doesn't
   default to treating it as unfinished engineering work.

8. **`consult_conservative`'s entry-vs-exit role asymmetry** — the 2026-08-16
   "Measured" section below found it -$8,159 as an entry signal (38% win) but
   +$25,706 as an exit signal (89% win), and nothing acted on it until now.

   **Tested 2026-08-23 (3-hourly check): genome-dependent, not a fixed law —
   see "Current state" above and
   `runs/2026-08-23-0352-consult-role-test-diagnostic.md`.** New read-only
   `consult-role-test [--also-version N]` (monkeypatches
   `ConservativeConsult.consider` to strip its buy intents for one extra
   `run_backtest` call, restores immediately after, nothing persisted) tested
   all three real champions: v1 gets worse with entries suppressed (-11.8% →
   -34.4% return), v2 improves sharply (fitness 0.183 → 0.584, maxDD -38.1% →
   -29.9%), v3 (live) is essentially flat (4 fewer trades out of 1069,
   everything else unchanged to the precision reported) — reading:
   13+ generations of unrelated tuning already pushed v3's own entry gate
   (`rsi_buy_below`/`z_buy_below`/`max_dd_from_high`) tight enough that it
   rarely fires as an entry any more, so the bad-buyer problem looks
   search-corrected for the current champion specifically, not a general
   property worth building a real gene for right now. Closed for v3 unless a
   future promotion re-widens that gate — if one does, re-running
   `consult-role-test` at that point is a one-line check for whether the
   problem has come back.

9. **Don't wrap a backgrounded `evolve`/long-running command in `nohup ... &`
   inside a single tool call.** Flagged in
   `runs/2026-08-28-0020-daily-trading.md`: doing that detaches the real
   process from the tool call's own lifecycle — the wrapper script returns
   (and the tool reports "completed") almost immediately, while the actual
   `python3 evotrader_bundle.py evolve N` keeps running orphaned under
   `nohup`. Harmless once you know to poll the real PID with `kill -0`
   instead of trusting the tool's completion signal, but it wastes a run's
   attention rediscovering that. Just background the `python3
   evotrader_bundle.py evolve N` command directly — no `nohup`/`&` combo —
   so the tool's own completion notification lines up with the process
   actually exiting.

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
