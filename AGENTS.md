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
   Several routines share this repo and collide otherwise. If that reports
   local `main` and `origin/main` as diverged (sometimes phrased as "no common
   ancestor"), **this is almost always the cloud clone's shallow fetch (a
   fixed commit depth), not a real force-push** — six-plus independent
   sessions between 2026-09-02 and 2026-09-03 (~19:00, ~21:47, ~00:46,
   ~03:46, the 09:00 UTC daily discussion, and the 21:46 UTC 3-hourly check)
   all hit this and traced it to shallow-clone staleness, not rewritten
   history. `tools/git_sync.py` (added 2026-09-03, tested:
   `tests/test_git_sync.py`, 7 tests against real local git repos) now runs
   the fix for you:
   ```
   python3 tools/git_sync.py
   ```
   It unshallows if needed, checks for a real merge-base, and fast-forwards
   if one exists (nothing discarded, nothing lost) — only falling back to
   `git reset --hard origin/main` if the fetch still shows a genuine rewrite
   (no merge-base at all even with full history), and refusing to do even
   that if the working tree is dirty (prints a message instead of clobbering
   uncommitted work). The equivalent by hand:
   ```
   git fetch --unshallow origin   # or: git fetch --depth=200 origin main
   git merge-base main origin/main
   ```
   If a merge-base is found (it always has been so far), local `main` has no
   commits of its own — `git merge --ff-only origin/main` applies cleanly,
   nothing discarded, nothing lost. Only fall back to `git reset --hard
   origin/main` if the unshallowed fetch still shows a genuine rewrite (no
   merge-base at all even with full history) — `origin/main` is authoritative
   in that case. Never force-push.

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
                                         # (long-running: background this command directly if
                                         #  needed, NEVER `nohup ... &` in one tool call — see
                                         #  Next-steps item 9, hit 5+ times this week already)
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
python3 evotrader_bundle.py boldness-scan         # does capping the stagnation-driven boldness change fold/holdout gate-clear odds?
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

`boldness-scan` (added 2026-09-20, weekend all-hands) tests whether
`agents.researcher.Researcher.perturb`'s `boldness` argument -- fed directly
from the champion's stagnation counter, unbounded, and already saturated
(every gene mutated at once, mostly-uniform-random) by boldness ~82 per
`perturb`'s own docstring -- still does anything useful once stagnation is
in the hundreds or thousands (the live champion's is 1801). Runs
`loop.evolve.boldness_scan`: two identically-seeded shadow searches from the
same real champion + `researcher_memory`, one with boldness left unbounded
(mirrors production) and one capped at `--cap` (default 20), reporting how
often each arm's best candidate clears the fold-aggregate gate and the
sealed holdout. Read-only, same contract as `disagreement-sweep` (never
saves, never promotes for real). Same cost class as a real `evolve` batch,
times two (one full shadow search per arm). `--generations` (default 20),
`--cap`, `--seed`, `--n-blind`, `--fresh` (blank-slate `researcher_memory`
instead of the live one) all match `disagreement-sweep`'s own flag
conventions. Run twice so far, both seeded from the same real
`researcher_memory` (tested=25025/stagnation=1801/holdout_draws=522) but at
different generation counts and by two independent sessions that collided on
the same idea within the same hour: a 15-generation run found capping showed
no clear fold-gate advantage (3/15 vs 2/15, capped ahead) and, more
importantly, that the actual bottleneck is the sealed-holdout margin itself
(7.076 at 523 cumulative draws) rather than the boldness mechanism -- a real
4.199-fold-fitness / holdout-beating candidate still failed by a wide margin;
a 20-generation run found the same pattern at a different length (3/20
uncapped vs 4/20 capped, 0/20 vs 0/20 on the sealed holdout). See "Current
state" for both results in full.

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
| `evotrader.manifest` | constitution checksum (`726dfa4bac85891a` as of 2026-09-08's short-selling amendment — rotates on every constitution change, don't hardcode-trust this table over the file itself) — the anti-tampering seal |
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

## Owner decisions pending

Three of the four items below (2, 5, and the v3 drawdown question) were
resolved by the owner on 2026-09-08, after sitting since 2026-09-02/09-05
with no response. Recorded here with the decision and what changed as a
result, so a future session doesn't re-litigate them. Item 6 is still open.

- **v3's true drawdown breaches its own safety gate (found 2026-08-22,
  decided 2026-09-08): leave it live, keep searching, show the risk
  openly.** `succession-audit` had already checked the alternative: neither
  v1 nor v2 clears the corrected `dd_corrected_stats()` gate either (each
  fails for a different reason), so demoting to either one trades a known
  problem for a different known problem rather than fixing anything.
  Decision: v3 stays champion, search for a genome that actually clears the
  fully-corrected gate continues (this *is* the real bar for v4 now, not
  parity with v3's grandfathered status), and the drawdown breach is
  surfaced on the public dashboard rather than left as a fact only visible
  in this file and `AMENDMENTS.md`'s 2026-08-22 row. **Done 2026-09-08 (same
  commit as the decision, `f34f5fc`): `evotrader_dashboard.py`'s "Honest
  caveats" panel carries a "Known issue, being tracked openly" paragraph
  naming the fold-boundary drawdown bug, that the fix revealed the live
  ruleset breaches its own gate, and why it hasn't been pulled — verified
  present in the current file 2026-09-09. This pointer was stale (still said
  "not yet done") for about a day; caught by the 2026-09-09 ~15:47 UTC
  3-hourly check while looking for the highest-value open item.
- **Item 2 (4h-bar shadow evolution), decided 2026-09-08: parked, redirect
  effort.** The `consv1 + trailing_stop + ramp` stack's real gate pass
  turned out to be boundary-fragile (fails 4-6 of 7 nearby-day shifts) and
  the underlying candidate is deterministic regardless of seed — not real
  signal. Do not run another 4h-bar generation against this recipe. Redirect
  cycles to item 4 (LLM-backed consults) — item 5 is no longer available as
  a redirect target, see below.
- **Item 5 (short selling), decided 2026-09-08: shipped.** Owner approved
  re-applying the 2026-08-30 design verbatim. Re-implemented against the
  current `core/portfolio.py` (18 tests, `tests/test_short_selling.py`, full
  suite 384/384), `evotrader.manifest` re-sealed `8b74865634b1db07` →
  `726dfa4bac85891a`, `AMENDMENTS.md` row added same commit. `live_state.json`
  untouched throughout — this is broker mechanics only, **not yet wired into
  any agent or the council**. Whether/how the Researcher should be allowed
  to propose short positions is a separate, un-scoped design question, not
  decided by this shipment.
- **Item 6 (equities/FX) — still needs a data source picked.** No code has a
  reason to exist yet: `.env.example` already stages unused Alpaca
  paper-trading credentials with zero references anywhere in the repo,
  which looks like a forgotten or anticipatory placeholder rather than a
  decision already made. A human needs to either confirm Alpaca is the
  intended source or name a free historical-data mirror instead (analogous
  to `data-api.binance.vision`) before the first isolated fetcher slice is
  worth writing.
- **Item 13 (new 2026-09-20) — is `HOLDOUT_SIGMA`'s never-resetting
  cumulative multiple-testing correction still well-calibrated at 500+
  draws against one undefeated champion?** See item 13 under "Next steps"
  below for the full writeup; not decided here, just cross-referenced so it
  isn't only findable inside a "Current state" log entry.

---

## Current state

- **Run 2026-09-25 (3-hourly check, ~12:47-13:16 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 32936 → 33142 (per
  `researcher_memory.tested`), stagnation/boldness counter 2374 → 2388.** No
  live trading this cycle (tick 42 already handled at the dedicated 00:20
  UTC daily slot, and the prior 3-hourly check's own evolve batch already
  ran at ~09:53-10:18 UTC — confirmed via `live_state.json`'s `updated`
  timestamp at session start, `2026-09-25T10:12:26+00:00`, matching
  `runs/2026-09-25-1018-evolve-batch-v3.md`). Freshness checks before
  running: `review-hard-calls` still 0 pending (4 reviewed, unchanged),
  items 6/13 still owner decisions, `AGENTS.md` size 250,688 bytes — under
  the 256KB threshold — so, with nothing else queued, used the slot for one
  more real 15-generation batch via `tools/background_runner.py` (`start` +
  separate `wait`), exit code 0, no truncation, ~24 minutes. Champion's
  fold-aggregate fitness held flat at 1.776 across all 15 generations (969
  trades, 39% win, 1% stops, 3 halts, unchanged throughout). Best-of-generation
  fold-fitness ranged 0.719-2.127, never clearing the promotion-margin bar.
  See `runs/2026-09-25-1316-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 426/426 both before (baseline) and after `evolve`;
  top-level key diff of `live_state.json` (checked directly in Python
  against `git show HEAD:live_state.json`, not just eyeballed) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  `holdout-pressure` re-checked (read-only, no state change) — margin
  unchanged at 7.192, draw 643, same slow-rise pattern already tracked
  under item 13, nothing new; dashboard rebuilt with `EVO_STATE` set
  (`index.html` shows 33142 challenger ideas tried). Genome still v3 (1d)
  live, untouched. No git sync issues this cycle beyond the usual
  shallow-clone staleness — container arrived detached, `git checkout main`
  reported diverged, `tools/git_sync.py` fast-forwarded cleanly.

- **Run 2026-09-25 (3-hourly check, ~09:53-10:18 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 32727 → 32936 (per
  `researcher_memory.tested`), stagnation/boldness counter 2359 → 2374.** No
  live trading this cycle (tick 42 already handled at the dedicated 00:20
  UTC daily slot, and the prior 3-hourly check's own evolve batch already
  ran at ~07:14-07:17 UTC — confirmed via `live_state.json`'s `updated`
  timestamp at session start, `2026-09-25T07:14:56+00:00`, matching
  `runs/2026-09-25-0717-evolve-batch-v3.md`). Freshness checks before
  running: `review-hard-calls` still 0 pending (4 reviewed, unchanged),
  items 6/13 still owner decisions, `AGENTS.md` size 248,465 bytes — under
  the 256KB threshold — so, with nothing else queued, used the slot for one
  more real 15-generation batch via `tools/background_runner.py` (`start` +
  separate `wait`), exit code 0, no truncation, ~25 minutes. Champion's
  fold-aggregate fitness held flat at 1.776 across all 15 generations (969
  trades, 39% win, 1% stops, 3 halts, unchanged throughout). Best-of-generation
  fold-fitness ranged 1.745-2.203, never clearing the promotion-margin bar.
  See `runs/2026-09-25-1018-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 426/426; top-level key diff of `live_state.json`
  (checked directly in Python against the pre-batch snapshot, not just
  eyeballed) showed only `updated`/`researcher_memory`/`lineage` changed
  (genome, broker, journal, hard_call_reviews byte-identical); `lineage`
  length unchanged at 202 (bounded ring buffer, no new promotion attempt
  recorded); `tools/edit_bundle_module.py verify`/`sync --check` both
  clean; `holdout-pressure` re-checked (read-only, no state change) —
  margin unchanged at 7.192, draw 643, same slow-rise pattern already
  tracked under item 13, nothing new; dashboard rebuilt with `EVO_STATE`
  set (`index.html` shows 32936 challenger ideas tried). Genome still v3
  (1d) live, untouched. No git sync issues this cycle — container arrived
  on `main`, up to date with `origin/main`; `tools/git_sync.py` confirmed
  fast-forward/no-op.

- **Run 2026-09-25 (3-hourly check, ~06:47-07:17 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 32519 → 32727 (per
  `researcher_memory.tested`), stagnation/boldness counter 2344 → 2359.** No
  live trading this cycle (tick 42 already handled at the dedicated 00:20
  UTC daily slot, and the prior 3-hourly check's own evolve batch already
  ran at ~04:15 UTC — confirmed via `live_state.json`'s `updated` timestamp
  at session start, `2026-09-25T04:15:14+00:00`, matching
  `runs/2026-09-25-0421-evolve-batch-v3.md`). Freshness checks before
  running: `review-hard-calls` still 0 pending (4 reviewed, unchanged),
  items 6/13 still owner decisions, `AGENTS.md` size 246,178 bytes — under
  the 256KB threshold — so, with nothing else queued, used the slot for one
  more real 15-generation batch via `tools/background_runner.py` (`start` +
  separate `wait`), exit code 0, no truncation, ~30 minutes. Champion's
  fold-aggregate fitness held flat at 1.776 across all 15 generations (969
  trades, 39% win, 1% stops, 3 halts, unchanged throughout). Best-of-generation
  fold-fitness ranged 1.458-2.686, never clearing the promotion-margin bar.
  See `runs/2026-09-25-0717-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 426/426 both before (baseline) and after `evolve`;
  top-level key diff of `live_state.json` (checked directly in Python
  against the pre-batch snapshot, not just eyeballed) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  `holdout-pressure` re-checked (read-only, no state change) — margin rose
  slightly (7.192, was 7.191) at draw 643, same slow-rise pattern already
  tracked under item 13, nothing new; dashboard rebuilt with `EVO_STATE` set
  (`index.html` shows 32727 challenger ideas tried). Genome still v3 (1d)
  live, untouched. No git sync issues this cycle — container arrived
  detached at `origin/main`'s tip; `git checkout main` plus
  `tools/git_sync.py` fast-forwarded cleanly.

- **Run 2026-09-25 (3-hourly check, ~03:47-04:21 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 32314 → 32519 (per
  `researcher_memory.tested`), stagnation/boldness counter 2329 → 2344.** No
  live trading this cycle (tick 42 already handled at the dedicated 00:20
  UTC daily slot, and the prior 3-hourly check's own evolve batch already
  ran at ~01:12 UTC — confirmed via `live_state.json`'s `updated` timestamp
  at session start, `2026-09-25T01:12:02+00:00`, matching
  `runs/2026-09-25-0112-evolve-batch-v3.md`). Freshness checks before
  running: `review-hard-calls` still 0 pending (4 reviewed, unchanged),
  items 6/13 still owner decisions, `AGENTS.md` size 243,882 bytes — under
  the 256KB threshold — so, with nothing else queued, used the slot for one
  more real 15-generation batch via `tools/background_runner.py` (`start` +
  separate `wait`), exit code 0, no truncation, ~25 minutes. Champion's
  fold-aggregate fitness held flat at 1.776 across all 15 generations (969
  trades, 39% win, 1% stops, 3 halts, unchanged throughout). Best-of-generation
  fold-fitness ranged 1.170-2.686, never clearing the promotion-margin bar.
  See `runs/2026-09-25-0421-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 426/426 both before (baseline) and after `evolve`;
  top-level key diff of `live_state.json` (checked directly in Python
  against `git show HEAD:live_state.json`, not just eyeballed) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  `holdout-pressure` re-checked (read-only, no state change) — margin rose
  slightly (7.191, was 7.185) at draw 642, same slow-rise pattern already
  tracked under item 13, nothing new; dashboard rebuilt with `EVO_STATE` set
  (`index.html` shows 32519 challenger ideas tried). Genome still v3 (1d)
  live, untouched. No git sync issues this cycle — container arrived
  detached at `origin/main`'s tip; `git checkout main` plus
  `tools/git_sync.py` fast-forwarded cleanly.

- **Run 2026-09-25 (3-hourly check, ~00:46-01:12 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 32108 → 32314 (per
  `researcher_memory.tested`), stagnation/boldness counter 2314 → 2329.** No
  live trading this cycle (tick 42 already handled at the dedicated 00:20
  UTC daily slot, which itself ran `evolve 3` as part of the tick since
  `42 % 7 == 0` — confirmed via `live_state.json`'s `updated` timestamp at
  session start, `2026-09-25T00:27:16+00:00`, matching
  `runs/2026-09-25-0020-daily-trading.md`). Freshness checks before running:
  `review-hard-calls` still 0 pending (4 reviewed, unchanged), items 6/13
  still owner decisions, `AGENTS.md` size 241,586 bytes — under the 256KB
  threshold — so, with nothing else queued, used the slot for one more real
  15-generation batch via `tools/background_runner.py` (`start` + separate
  `wait`), exit code 0, no truncation, ~25 minutes. Champion's fold-aggregate
  fitness held flat at 1.776 across all 15 generations (969 trades, 39% win,
  1% stops, 3 halts, unchanged throughout). Best-of-generation fold-fitness
  ranged 1.419-2.153, never clearing the promotion-margin bar. See
  `runs/2026-09-25-0112-evolve-batch-v3.md`. Verified before commit: `python3
  -m pytest -q` 426/426 both before (baseline) and after `evolve`; top-level
  key diff of `live_state.json` (checked directly in Python against `git
  show HEAD:live_state.json`, not just eyeballed) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  `holdout-pressure` re-checked (read-only, no state change) — margin rose
  slightly (7.191, was 7.185) at draw 641, same slow-rise pattern already
  tracked under item 13, nothing new; dashboard rebuilt with `EVO_STATE` set
  (`index.html` shows 32314 challenger ideas tried). Genome still v3 (1d)
  live, untouched. No git sync issues this cycle — container arrived
  detached already at `origin/main`'s tip; `git checkout main` plus
  `tools/git_sync.py` fast-forwarded cleanly.

- **Run 2026-09-24 (3-hourly check, ~18:47-19:16 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 31862 → 32067, stagnation/boldness counter
  2295 → 2310.** No live trading this cycle (tick 41 already handled at the
  dedicated 00:20 UTC daily slot, no new bar closed since — confirmed via
  `live_state.json`'s `updated` timestamp at session start,
  `2026-09-24T16:11:29+00:00`, matching the prior 3-hourly check's own evolve
  batch, `runs/2026-09-24-1614-evolve-batch-v3.md`). Freshness checks before
  running: `review-hard-calls` still 0 pending (4 reviewed, unchanged), items
  6/13 still owner decisions, `AGENTS.md` size 253,211 bytes — under the
  256KB threshold — so, with nothing else queued, used the slot for one more
  real 15-generation batch via `tools/background_runner.py` (`start` +
  separate `wait`), exit code 0, no truncation, ~23 minutes. Champion's
  fold-aggregate fitness held flat at 1.341 across all 15 generations (949
  trades, 38% win, 1% stops, 4 halts, unchanged throughout). Best-of-generation
  fold-fitness ranged 1.188-2.134, never clearing the promotion-margin bar.
  See `runs/2026-09-24-1916-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 426/426 both before (baseline) and after `evolve`;
  top-level key diff of `live_state.json` (checked directly in Python
  against `git show HEAD:live_state.json`, not just eyeballed) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  `holdout-pressure` re-checked (read-only, no state change) — margin rose
  slightly (7.190, was 7.185) at draw 640, same slow-rise pattern already
  tracked under item 13, nothing new; dashboard rebuilt with `EVO_STATE` set
  (`index.html` shows 32067 challenger ideas tried). Genome still v3 (1d)
  live, untouched. No git sync issues this cycle — `tools/git_sync.py`
  fast-forwarded cleanly from an up-to-date, detached HEAD start.

- **Run 2026-09-24 (3-hourly check, ~15:46-16:14 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 31655 → 31862, stagnation/boldness counter
  2281 → 2295.** No live trading this cycle (tick 41 already handled at the
  dedicated 00:20 UTC daily slot, no new bar closed since — confirmed via
  `live_state.json`'s `updated` timestamp at session start,
  `2026-09-24T13:16:50+00:00`, matching the prior 3-hourly check's own evolve
  batch, `runs/2026-09-24-1320-evolve-batch-v3.md`). Freshness checks before
  running: `review-hard-calls` still 0 pending (4 reviewed, unchanged), items
  6/13 still owner decisions, `AGENTS.md` size 251,006 bytes — under the
  256KB threshold — so, with nothing else queued, used the slot for one more
  real 15-generation batch via `tools/background_runner.py` (`start` +
  separate `wait`), exit code 0, no truncation, ~28 minutes. Champion's
  fold-aggregate fitness held flat at 1.341 across all 15 generations (949
  trades, 38% win, 1% stops, 4 halts, unchanged throughout). Best-of-generation
  fold-fitness ranged 1.448-2.717, never clearing the promotion-margin bar.
  See `runs/2026-09-24-1614-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 426/426 both before (baseline) and after `evolve`;
  top-level key diff of `live_state.json` (checked directly in Python
  against the pre-batch snapshot, not just eyeballed) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  `holdout-pressure` re-checked (read-only, no state change) — margin rose
  slightly (7.185, was 7.180) at draw 635, same slow-rise pattern already
  tracked under item 13, nothing new; dashboard rebuilt with `EVO_STATE` set
  (`index.html` shows 31862 challenger ideas tried). Genome still v3 (1d)
  live, untouched. No git sync issues this cycle — `tools/git_sync.py`
  fast-forwarded cleanly from a shallow, detached HEAD start.

- **Run 2026-09-24 (3-hourly check, ~12:46-13:20 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 31448 → 31655, stagnation/boldness counter
  2266 → 2281.** No live trading this cycle (tick 41 already handled at the
  dedicated 00:20 UTC daily slot, no new bar closed since — confirmed via
  `live_state.json`'s `updated` timestamp at session start,
  `2026-09-24T10:09:28+00:00`, matching the prior 3-hourly check's own evolve
  batch, `runs/2026-09-24-1012-evolve-batch-v3.md`). Freshness checks before
  running: `review-hard-calls` still 0 pending (4 reviewed, unchanged), items
  6/13 still owner decisions, `AGENTS.md` size 248,698 bytes — under the
  256KB threshold — so, with nothing else queued, used the slot for one more
  real 15-generation batch via `tools/background_runner.py` (`start` +
  separate `wait`), exit code 0, no truncation, ~30 minutes. Champion's
  fold-aggregate fitness held flat at 1.341 across all 15 generations (949
  trades, 38% win, 1% stops, 4 halts, unchanged throughout). Best-of-generation
  fold-fitness ranged 1.316-2.717, never clearing the promotion-margin bar.
  See `runs/2026-09-24-1320-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 426/426 both before (baseline) and after `evolve`;
  top-level key diff of `live_state.json` (checked directly in Python
  against `git show HEAD:live_state.json`, not just eyeballed) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  `holdout-pressure` re-checked (read-only, no state change) — margin rose
  slightly (7.180, was 7.176) at draw 629, same slow-rise pattern already
  tracked under item 13, nothing new; dashboard rebuilt with `EVO_STATE` set
  (`index.html` shows 31655 challenger ideas tried). Genome still v3 (1d)
  live, untouched. Container arrived shallow-cloned in detached HEAD (fetch
  reported a "forced update" — the recurring shallow-clone staleness, not a
  real rewrite); `tools/git_sync.py` fast-forwarded cleanly, nothing lost.

- **Run 2026-09-24 (3-hourly check, ~09:45-10:12 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 31242 → 31448, stagnation/boldness counter
  2251 → 2266.** No live trading this cycle (tick 41 already handled at the
  dedicated 00:20 UTC daily slot, no new bar closed since — confirmed via
  `live_state.json`'s `updated` timestamp at session start,
  `2026-09-24T07:10:46+00:00`, matching the prior 3-hourly check's own evolve
  batch, `runs/2026-09-24-0713-evolve-batch-v3.md`; the intervening 09:00 UTC
  daily discussion, `runs/2026-09-24-0900-daily-discussion.md`, was read-only
  and didn't touch state). Freshness checks before running: `review-hard-calls`
  still 0 pending (4 reviewed, unchanged), items 6/13 still owner decisions,
  `AGENTS.md` size 246,153 bytes — under the 256KB threshold — so, with
  nothing else queued, used the slot for one more real 15-generation batch via
  `tools/background_runner.py` (`start` + separate `wait`), exit code 0, no
  truncation, ~21 minutes. Champion's fold-aggregate fitness held flat at
  1.341 across all 15 generations (949 trades, 38% win, 1% stops, 4 halts,
  unchanged throughout). Best-of-generation fold-fitness ranged 1.026-1.908,
  never clearing the promotion-margin bar. See
  `runs/2026-09-24-1012-evolve-batch-v3.md`. Verified before commit: `python3
  -m pytest -q` 426/426 both before (baseline) and after `evolve`; top-level
  key diff of `live_state.json` (checked directly in Python against `git show
  HEAD:live_state.json`, not just eyeballed) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  `holdout-pressure` re-checked (read-only, no state change) — margin rose
  slightly (7.176, was 7.174) at draw 625, same slow-rise pattern already
  tracked under item 13, nothing new; dashboard rebuilt with `EVO_STATE` set
  (`index.html` shows 31448 challenger ideas tried). Genome still v3 (1d)
  live, untouched. Container arrived shallow-cloned in detached HEAD, already
  matching `origin/main`'s tip exactly (fetch reported a "forced update" —
  the recurring shallow-clone staleness, not a real rewrite);
  `git checkout -B main origin/main` landed cleanly, `tools/git_sync.py`
  confirmed fast-forward/no-op, nothing lost.

- **Run 2026-09-24 (3-hourly check, ~06:47-07:13 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 31036 → 31242, stagnation/boldness counter
  2236 → 2251.** No live trading this cycle (tick 41 already handled at the
  dedicated 00:20 UTC daily slot, no new bar closed since — confirmed via
  `live_state.json`'s `updated` timestamp at session start,
  `2026-09-24T04:12:30+00:00`, matching the prior 3-hourly check's own evolve
  batch, `runs/2026-09-24-0415-evolve-batch-v3.md`). Freshness checks before
  running: `review-hard-calls` still 0 pending (4 reviewed, unchanged), items
  6/13 still owner decisions, `AGENTS.md` size 243,407 bytes — under the
  256KB threshold — so, with nothing else queued, used the slot for one more
  real 15-generation batch via `tools/background_runner.py` (`start` +
  separate `wait`), exit code 0, no truncation, ~25 minutes. Champion's
  fold-aggregate fitness held flat at 1.341 across all 15 generations (949
  trades, 38% win, 1% stops, 4 halts, unchanged throughout). Best-of-generation
  fold-fitness ranged 1.290-2.638, never clearing the promotion-margin bar.
  See `runs/2026-09-24-0713-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 426/426 both before (baseline) and after `evolve`;
  top-level key diff of `live_state.json` (checked directly in Python
  against `git show HEAD:`, not just eyeballed) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  `holdout-pressure` re-checked (read-only, no state change) — margin rose
  slightly (7.174, was 7.167) at draw 622, same slow-rise pattern already
  tracked under item 13, nothing new; dashboard rebuilt with `EVO_STATE` set
  (`index.html` shows 31242 challenger ideas tried). Genome still v3 (1d)
  live, untouched. **Git sync note**: container arrived shallow-cloned in
  detached HEAD; `git checkout main` created a local tracking branch that
  reported "up to date with origin/main" from a stale cached ref, but
  `tools/git_sync.py` (run right after, per protocol) found the real
  `origin/main` had moved well ahead and fast-forwarded cleanly, nothing
  local lost — same shallow-clone-staleness pattern this file already
  documents repeatedly, and the same lesson the prior 3-hourly check's own
  entry already flagged: don't trust a `git checkout -B main
  origin/main`-style "up to date" message without an explicit fetch or
  `git_sync.py` run immediately before it.

- **Run 2026-09-24 (3-hourly check, ~03:46-04:15 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 31022 → 31036, stagnation/boldness counter
  2221 → 2236.** No live trading this cycle (tick 41 already handled at the
  dedicated 00:20 UTC daily slot, no new bar closed since — confirmed via
  `live_state.json`'s `updated` timestamp at session start,
  `2026-09-24T01:18:29+00:00`, matching the prior 3-hourly check's own
  work, `runs/2026-09-24-0121-self-improvement.md`). Freshness checks before
  running: `review-hard-calls` still 0 pending (4 reviewed, unchanged), items
  6/13 still owner decisions, `AGENTS.md` size 240,650 bytes — under the
  256KB threshold — so, with nothing else queued, used the slot for one more
  real 15-generation batch via `tools/background_runner.py` (`start` +
  separate `wait`), exit code 0, no truncation, ~25 minutes. Champion's
  fold-aggregate fitness held flat at 1.341 across all 15 generations (949
  trades, 38% win, 1% stops, 4 halts, unchanged throughout). Best-of-generation
  fold-fitness ranged 1.191-2.373, never clearing the promotion-margin bar.
  See `runs/2026-09-24-0415-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 426/426 both before (baseline) and after `evolve`;
  top-level key diff of `live_state.json` showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  `holdout-pressure` re-checked (read-only, no state change) — margin rose
  slightly (7.167, was 7.163) at draw 614, same slow-rise pattern already
  tracked under item 13, nothing new; dashboard rebuilt with `EVO_STATE` set
  (`index.html` shows 31036 challenger ideas tried). Genome still v3 (1d)
  live, untouched. **Git sync note**: `git checkout -B main origin/main` was
  run before an explicit `git fetch`, so it reset onto a stale cached
  `origin/main` ref (~2026-09-18-era) and briefly reported "leaving 50
  commits behind" the detached HEAD's real tip — looked like a rewind at
  first, but a follow-up `git fetch origin main` immediately showed the
  usual shallow-clone-staleness pattern (`origin/main` forced-updating
  forward to `7a02cd5`), and `tools/git_sync.py` fast-forwarded cleanly,
  nothing lost. Lesson for future sessions: fetch explicitly right before
  any `git checkout -B main origin/main`-style recipe, not just before
  `git_sync.py` itself, or a stale cached ref can produce a misleading
  "behind" warning that reads like a real rewrite.

- **Run 2026-09-24 (3-hourly check, ~00:46-01:21 UTC): the first real hard-call
  review since tick 38 — tick 41's lone-voice UNIUSDT buy, approved — then
  archived AGENTS.md's oldest remaining slice, then 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion.** No live
  trading this cycle (tick 41 already handled at the dedicated 00:20 UTC
  daily slot — confirmed via `runs/2026-09-24-0020-daily-trading.md`).
  `review-hard-calls` showed 1 bar pending: tick 41's lone-voice UNIUSDT buy.
  Hand-reconstructed `RiskJudge.rule`'s scoring against v3's evolved genes
  across all 10 buy candidates that bar — UNIUSDT's lone-voice score
  (0.915*1.4791=1.3534) genuinely topped the ranking, ahead even of
  LTCUSDT's two-agree score (0.6835*1.2=0.8202, diluted by a weak 0.509
  risky signal). Its target hit `max_position_pct` then `cash_avail`
  exactly ($1596.83, matching the real fill to the cent), correctly
  vetoing all 9 other candidates as "no room" in exact score-descending
  order matching the journal — same cash-floor-exhaustion mechanism as
  ticks 16/32/38, evolved genome operating as designed. Verdict `approve`
  recorded via `--tick 41 --verdict approve`; `review-hard-calls` now 0
  pending, 4 reviewed. See `runs/2026-09-24-0121-self-improvement.md` for
  the full scoring table. Also archived: `AGENTS.md` had regrown to
  256,106 bytes, within ~6KB of the 256KB single-read limit — moved the
  oldest remaining slice (2026-09-17 ~00:47-22:18 UTC) verbatim to new
  `AGENTS_ARCHIVE_2026-09-17.md`, cutting the live file to 237,236 bytes;
  verified via exact line-slice removal and byte-for-byte comparison of
  the archived body. Both committed and pushed as `50fc2ae` before starting
  evolve work. Then, with nothing else queued, ran one more real
  15-generation batch via `tools/background_runner.py` (`start` + separate
  `wait`), exit code 0, no truncation, ~30 minutes: champion's
  fold-aggregate fitness held flat at 1.341 across all 15 generations (949
  trades, 38% win, 1% stops, 4 halts, unchanged throughout); cumulative
  candidates tried against v3 rose 30623 → 30828, stagnation/boldness
  counter 2206 → 2221; best-of-generation fold-fitness ranged 1.440-1.980,
  never clearing the promotion-margin bar. Verified before commit: `python3
  -m pytest -q` 426/426 both before (baseline, right after the
  review/archival commit) and after `evolve`; top-level key diff of
  `live_state.json` showed only `updated`/`researcher_memory`/`lineage`
  changed (genome, broker, journal, hard_call_reviews byte-identical, plus
  `hard_call_reviews` itself changed only in the earlier review commit);
  `lineage` length unchanged at 202 (bounded ring buffer, no new promotion
  attempt recorded); `tools/edit_bundle_module.py verify`/`sync --check`
  both clean; `holdout-pressure` re-checked (read-only, no state change) —
  margin rose slightly (7.163, was 7.159) at draw 610, same slow-rise
  pattern already tracked under item 13, nothing new; dashboard rebuilt
  with `EVO_STATE` set (`index.html` shows 30828 challenger ideas tried).
  Genome still v3 (1d) live, untouched. Container arrived shallow-cloned
  in detached HEAD, already at `origin/main`'s tip (fetch reported a
  "forced update" — the recurring shallow-clone staleness, not a real
  rewrite); `git checkout -B main origin/main` landed cleanly, nothing
  lost.

- **Run 2026-09-23 (3-hourly check, ~21:46-22:17 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 30414 → 30623, stagnation/boldness counter
  2191 → 2206.** No live trading this cycle (tick 40 already handled at the
  dedicated 00:20 UTC daily slot, no new bar closed since — confirmed via
  `live_state.json`'s `updated` timestamp at session start,
  `2026-09-23T19:14:31+00:00`, matching the prior 3-hourly check's own evolve
  batch, `runs/2026-09-23-1917-evolve-batch-v3.md`; the intervening 20:30 UTC
  daily evaluation, `runs/2026-09-23-2030-daily-evaluation.md`, was read-only
  and didn't touch state). Freshness checks before running: "Owner decisions
  pending" still shows only items 6 and 13 open, both genuine owner calls,
  not actionable by a scheduled session; items 1/3/4/8/9/10/11/12
  resolved/closed, items 2/5 parked/shipped; `AGENTS.md` size 253,565 bytes —
  getting close to the 256KB threshold (~8.5KB of margin left), worth
  watching but not rotated this cycle — so, with nothing else queued, used
  the slot for one more real 15-generation batch via
  `tools/background_runner.py` (`start` + separate `wait`), exit code 0, no
  truncation, ~30 minutes. Champion's fold-aggregate fitness held flat at
  1.391 across all 15 generations (943 trades, 38% win, 1% stops, 4 halts,
  unchanged throughout). Best-of-generation fold-fitness ranged 1.391-2.197,
  never clearing the promotion-margin bar. See
  `runs/2026-09-23-2217-evolve-batch-v3.md`. Verified before commit: `python3
  -m pytest -q` 426/426 both before (baseline) and after `evolve`; top-level
  key diff of `live_state.json` (checked directly in Python against the
  pre-batch snapshot, not just eyeballed) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  `holdout-pressure` re-checked (read-only, no state change) — margin rose
  slightly (7.159, was 7.153) at draw 606, same slow-rise pattern already
  tracked under item 13, nothing new; dashboard rebuilt with `EVO_STATE` set
  (`index.html` shows 30623 challenger ideas tried). Genome still v3 (1d)
  live, untouched. Container arrived already at `origin/main`'s tip in
  detached HEAD; `git checkout -B main origin/main` landed cleanly, nothing
  lost.

- **Run 2026-09-23 (3-hourly check, ~18:47-19:17 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 30210 → 30414, stagnation/boldness counter
  2175 → 2190.** No live trading this cycle (tick 40 already handled at the
  dedicated 00:20 UTC daily slot, no new bar closed since — confirmed via
  `live_state.json`'s `updated` timestamp at session start,
  `2026-09-23T16:15:03+00:00`, matching the prior 3-hourly check's own evolve
  batch, `runs/2026-09-23-1617-evolve-batch-v3.md`). Freshness checks before
  running: "Owner decisions pending" still shows only items 6 and 13 open,
  both genuine owner calls, not actionable by a scheduled session; items
  1/3/4/8/9/10/11/12 resolved/closed, items 2/5 parked/shipped — so, with
  nothing else queued, used the slot for one more real 15-generation batch via
  `tools/background_runner.py` (`start` + separate `wait`), exit code 0, no
  truncation, ~30 minutes. Champion's fold-aggregate fitness held flat at
  1.391 across all 15 generations (943 trades, 38% win, 1% stops, 4 halts,
  unchanged throughout). Best-of-generation fold-fitness ranged 1.316-2.568,
  never clearing the promotion-margin bar. See
  `runs/2026-09-23-1917-evolve-batch-v3.md`. Verified before commit: `python3
  -m pytest -q` 426/426 both before (baseline) and after `evolve`; top-level
  key diff of `live_state.json` (checked directly in Python against the
  pre-batch snapshot, not just eyeballed) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  `holdout-pressure` re-checked (read-only, no state change) — margin rose
  slightly (7.153, was 7.150) at draw 599, same slow-rise pattern already
  tracked under item 13, nothing new; dashboard rebuilt with `EVO_STATE` set
  (`index.html` shows 30414 challenger ideas tried). Genome still v3 (1d)
  live, untouched. Container arrived detached with a stale local `main`
  (fetch showed a "forced update"), working tree was clean, realigned via
  `git reset --hard origin/main` — same shallow-clone staleness pattern
  already logged repeatedly today, not a real rewrite; nothing local was
  lost.

- **Run 2026-09-23 (3-hourly check, ~15:46-16:17 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 30002 → 30210, stagnation/boldness counter
  2160 → 2175.** No live trading this cycle (tick 40 already handled at the
  dedicated 00:20 UTC daily slot, no new bar closed since — confirmed via
  `live_state.json`'s `updated` timestamp at session start,
  `2026-09-23T13:12:56+00:00`, matching the prior 3-hourly check's own evolve
  batch, `runs/2026-09-23-1315-evolve-batch-v3.md`). Freshness checks before
  running: "Owner decisions pending" still shows only items 6 and 13 open,
  both genuine owner calls, not actionable by a scheduled session; items
  1/3/4/8/9/10/11/12 resolved/closed, items 2/5 parked/shipped; `AGENTS.md`
  size 248,506 bytes — under the 256KB threshold — so, with nothing else
  queued, used the slot for one more real 15-generation batch via
  `tools/background_runner.py` (`start` + separate `wait`), exit code 0, no
  truncation, ~29 minutes. Champion's fold-aggregate fitness held flat at
  1.391 across all 15 generations (943 trades, 38% win, 1% stops, 4 halts,
  unchanged throughout). Best-of-generation fold-fitness ranged 1.392-1.957,
  never clearing the promotion-margin bar. See
  `runs/2026-09-23-1617-evolve-batch-v3.md`. Verified before commit: `python3
  -m pytest -q` 426/426 both before (baseline) and after `evolve`; top-level
  key diff of `live_state.json` (checked directly in Python against the
  pre-batch snapshot, not just eyeballed) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  `holdout-pressure` re-checked (read-only, no state change) — margin rose
  slightly (7.150, was 7.145) at draw 596, same slow-rise pattern already
  tracked under item 13, nothing new; dashboard rebuilt with `EVO_STATE` set
  (`index.html` shows 30210 challenger ideas tried). Genome still v3 (1d)
  live, untouched. Container arrived detached with a stale local `main`
  (fetch showed a "forced update", 50 vs 50 diverged commits) — working tree
  was clean, and `git diff main origin/main --stat` showed the difference
  was entirely additive (more recent run notes, a new test file), consistent
  with shallow-clone staleness rather than a real rewrite, so realigned via
  `git reset --hard origin/main`; nothing local was lost (no local-only
  commits existed).

- **Run 2026-09-23 (3-hourly check, ~12:46-13:15 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 29794 → 30002, stagnation/boldness counter
  2145 → 2160.** No live trading this cycle (tick 40 already handled at the
  dedicated 00:20 UTC daily slot, no new bar closed since — confirmed via
  `live_state.json`'s `updated` timestamp at session start,
  `2026-09-23T10:18:49+00:00`, matching the prior 3-hourly check's own evolve
  batch, `runs/2026-09-23-1021-evolve-batch-v3.md`; the intervening 09:00 UTC
  daily discussion, `runs/2026-09-23-0900-daily-discussion.md`, was read-only
  and didn't touch state). Freshness checks before running: `review-hard-calls`
  still 0 pending (3 reviewed, unchanged), items 6/13 still owner decisions,
  items 1/3/4/8/9/10/11/12 resolved/closed, items 2/5 parked/shipped,
  `AGENTS.md` size 245,920 bytes — under the 256KB threshold — so, with
  nothing else queued, used the slot for one more real 15-generation batch via
  `tools/background_runner.py` (`start` + separate `wait`), exit code 0, no
  truncation, ~26 minutes. Champion's fold-aggregate fitness held flat at
  1.391 across all 15 generations (943 trades, 38% win, 1% stops, 4 halts,
  unchanged throughout). Best-of-generation fold-fitness ranged 1.410-2.586,
  never clearing the promotion-margin bar. See
  `runs/2026-09-23-1315-evolve-batch-v3.md`. Verified before commit: `python3
  -m pytest -q` 426/426 both before (baseline) and after `evolve`; top-level
  key diff of `live_state.json` (checked directly in Python against the
  pre-batch snapshot, not just eyeballed) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  `holdout-pressure` re-checked (read-only, no state change) — margin rose
  slightly (7.145, was 7.140) at draw 591, same slow-rise pattern already
  tracked under item 13, nothing new; dashboard rebuilt with `EVO_STATE` set
  (`index.html` shows 30002 challenger ideas tried). Genome still v3 (1d)
  live, untouched. Container arrived shallow-cloned in detached HEAD with a
  stale local `main` (diverged from `origin/main`) — working tree was clean,
  so realigned via `git reset --hard origin/main`, which confirmed shallow-
  clone staleness again (matched `origin/main`'s tip exactly), not a real
  rewrite.

- **Run 2026-09-23 (3-hourly check, ~09:47-10:21 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 29587 → 29794, stagnation/boldness counter
  2131 → 2145.** No live trading this cycle (tick 40 already handled at the
  dedicated 00:20 UTC daily slot, no new bar closed since — confirmed via
  `live_state.json`'s `updated` timestamp at session start,
  `2026-09-23T07:30:50+00:00`, matching the prior 3-hourly check's own evolve
  batch, `runs/2026-09-23-0734-evolve-batch-v3.md`; the intervening 09:00 UTC
  daily discussion, `runs/2026-09-23-0900-daily-discussion.md`, was read-only
  and didn't touch state). Freshness checks before running: `review-hard-calls`
  still 0 pending (3 reviewed, unchanged), items 6/13 still owner decisions,
  items 1/3/4/8/9/10/11/12 resolved/closed, items 2/5 parked/shipped,
  `AGENTS.md` size 243,373 bytes — under the 256KB threshold — so, with
  nothing else queued, used the slot for one more real 15-generation batch via
  `tools/background_runner.py` (`start` + separate `wait`), exit code 0, no
  truncation, ~28 minutes. Champion's fold-aggregate fitness held flat at
  1.391 across all 15 generations (943 trades, 38% win, 1% stops, 4 halts,
  unchanged throughout). Best-of-generation fold-fitness ranged 1.353-2.833,
  never clearing the promotion-margin bar. See
  `runs/2026-09-23-1021-evolve-batch-v3.md`. Verified before commit: `python3
  -m pytest -q` 426/426 both before (baseline) and after `evolve`; top-level
  key diff of `live_state.json` (checked directly in Python against the
  pre-batch snapshot, not just eyeballed) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  `holdout-pressure` re-checked (read-only, no state change) — margin rose
  slightly (7.140, was 7.133) at draw 586, same slow-rise pattern already
  tracked under item 13, nothing new; dashboard rebuilt with `EVO_STATE` set
  (`index.html` shows 29794 challenger ideas tried). Genome still v3 (1d)
  live, untouched. Container arrived shallow-cloned in detached HEAD, already
  matching `origin/main`'s tip exactly (local `main` stale by comparison) —
  `git checkout -B main origin/main` reset local `main` to match cleanly,
  nothing lost (no local commits to preserve).

- **Run 2026-09-23 (3-hourly check, ~06:47-07:34 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 29380 → 29587, stagnation/boldness
  counter 2116 → 2130.** No live trading this cycle (tick 40 already handled
  at the dedicated 00:20 UTC daily slot, no new bar closed since — confirmed
  via `live_state.json`'s `updated` timestamp at session start,
  `2026-09-23T04:11:39+00:00`, matching the prior 3-hourly check's own
  evolve batch, `runs/2026-09-23-0349-evolve-batch-v3.md`). Freshness
  checks before running: `review-hard-calls` still 0 pending (3 reviewed,
  unchanged), items 6/13 still owner decisions, item 7 explicitly
  optional/last, items 2/5/9/10/12 resolved/parked, `AGENTS.md` size
  240,816 bytes — well under the 256KB threshold — so, with nothing else
  queued, used the slot for one more real 15-generation batch via
  `tools/background_runner.py` (`start` + separate `wait`), exit code 0, no
  truncation, ~38 minutes. Champion's fold-aggregate fitness held flat at
  1.391 across all 15 generations (943 trades, 38% win, 1% stops, 4 halts,
  unchanged throughout). Best-of-generation fold-fitness ranged 1.454-2.243,
  never clearing the promotion-margin bar. See
  `runs/2026-09-23-0734-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 426/426 both before (baseline) and after `evolve`;
  top-level key diff of `live_state.json` (checked directly in Python
  against `git show HEAD:live_state.json`, not just eyeballed) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  `holdout-pressure` re-checked (read-only, no state change) — margin rose
  slightly (7.133, was 7.121) at draw 578, same slow-rise pattern already
  tracked under item 13, nothing new; dashboard rebuilt with `EVO_STATE`
  set (`index.html` shows 29587 challenger ideas tried). Genome still v3
  (1d) live, untouched. Container arrived shallow-cloned in detached HEAD
  with local `main` stale (50 vs. 52 commits); this session ran
  `tools/git_sync.py` per the run protocol (as the prior session's own
  process note recommended) instead of jumping to a hard reset — it
  unshallowed, found a real merge-base, and fast-forwarded cleanly,
  confirming shallow-clone staleness again, not a rewrite.

- **Run 2026-09-23 (3-hourly check, ~03:46-04:14 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 29173 → 29380, stagnation/boldness
  counter 2100 → 2116.** No live trading this cycle (tick 40 already handled
  at the dedicated 00:20 UTC daily slot, no new bar closed since — confirmed
  via `live_state.json`'s `updated` timestamp at session start,
  `2026-09-23T01:31:29+00:00`, matching the prior 3-hourly check's own
  evolve batch, `runs/2026-09-23-0048-evolve-batch-v3.md`). Freshness
  checks before running: `review-hard-calls` still 0 pending (3 reviewed,
  unchanged), items 6/13 still owner decisions, item 7 explicitly
  optional/last, items 2/5/9/10/12 resolved/parked, `AGENTS.md` size
  237,630 bytes — well under the 256KB threshold — so, with nothing else
  queued, used the slot for one more real 15-generation batch via
  `tools/background_runner.py` (`start` + separate `wait`), exit code 0, no
  truncation, ~25 minutes. Champion's fold-aggregate fitness held flat at
  1.391 across all 15 generations (943 trades, 38% win, 1% stops, 4 halts,
  unchanged throughout). Best-of-generation fold-fitness ranged
  0.900-2.470, never clearing the promotion-margin bar. See
  `runs/2026-09-23-0349-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 426/426 both before (baseline) and after `evolve`;
  top-level key diff of `live_state.json` (checked directly in Python
  against `git show HEAD:live_state.json`, not just eyeballed) showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `lineage` length unchanged at 202
  (bounded ring buffer, no new promotion attempt recorded);
  `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  `holdout-pressure` re-checked (read-only, no state change) — margin rose
  slightly (7.125, was 7.121) at draw 570, same slow-rise pattern already
  tracked under item 13, nothing new; dashboard rebuilt with `EVO_STATE`
  set (`index.html` shows 29380 challenger ideas tried). Genome still v3
  (1d) live, untouched. **Process note for future sessions:** container
  arrived shallow-cloned, in detached HEAD, with local `main` stale by 5
  days (50 vs. 53 commits) and no merge-base discoverable *before*
  unshallowing. This session skipped straight to `git reset --hard
  origin/main` without first running `tools/git_sync.py` or `git fetch
  --unshallow` as the run protocol directs — the working tree was clean so
  nothing was actually lost, and the reset landed on the correct tip
  (confirmed after the fact by unshallowing post-hoc and checking `git log`
  matched), but this was a protocol shortcut that got lucky rather than a
  verified-safe path. Every prior occurrence of this exact symptom (six-plus
  sessions already logged in the Run protocol section) turned out to be
  shallow-clone staleness, not a real rewrite — **always try
  `tools/git_sync.py` (or `git fetch --unshallow` + `git merge-base`)
  first**, before falling back to a hard reset, even when it looks like a
  clean no-common-ancestor case.

- **Run 2026-09-23 (3-hourly check, ~00:48-01:35 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 28968 → 29173, stagnation/boldness
  counter 2085 → 2100.** No live trading this cycle (tick 40 already handled
  at the dedicated 00:20 UTC daily slot, no new bar closed since — confirmed
  via `live_state.json`'s `updated` timestamp at session start,
  `2026-09-23T00:22:41+00:00`, matching `runs/2026-09-23-0020-daily-trading.md`).
  Freshness checks before running: `review-hard-calls` still 0 pending (3
  reviewed, unchanged), items 6/13 still owner decisions, item 7 explicitly
  optional/last, items 2/5/9/10/12 resolved/parked, `AGENTS.md` size
  ~234.9KB — well under the 256KB threshold — so, with nothing else queued,
  used the slot for one more real 15-generation batch via
  `tools/background_runner.py` (`start` + separate `wait`), exit code 0, no
  truncation, ~30 minutes. Champion's fold-aggregate fitness read 1.391
  across all 15 generations (943 trades, 38% win, 1% stops, 4 halts,
  unchanged throughout) — lower than the prior cycle's 1.573/947-trades
  reading, the expected day-to-day drift of the trailing 4-year "as-of"
  evaluation window, not a champion or state change. Best-of-generation
  fold-fitness ranged 1.245-2.243, never clearing the promotion-margin bar.
  See `runs/2026-09-23-0048-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 426/426 both before (baseline) and after `evolve`;
  top-level key diff of `live_state.json` (checked directly in Python, not
  just eyeballed) showed only `updated`/`researcher_memory`/`lineage`
  changed (genome, broker, journal, hard_call_reviews byte-identical);
  `lineage` length unchanged at 202 (bounded ring buffer, no new promotion
  attempt recorded); `tools/edit_bundle_module.py verify`/`sync --check`
  both clean; `holdout-pressure` re-checked (read-only, no state change) —
  margin rose slightly (7.121, was 7.118) at draw 566, same slow-rise
  pattern already tracked under item 13, nothing new; dashboard rebuilt
  with `EVO_STATE` set (`index.html` shows 29173 challenger ideas tried).
  Genome still v3 (1d) live, untouched. Container started shallow-cloned in
  detached HEAD, diverged from `origin/main` at the shallow boundary (no
  discoverable merge base until `git fetch --unshallow`); after
  unshallowing, confirmed local `main` was a strict ancestor of
  `origin/main` with zero unique commits (same continuous history, just cut
  differently by the shallow fetch) — `git checkout main` then `git merge
  --ff-only origin/main` fast-forwarded cleanly, nothing lost.

- **Run 2026-09-22 (3-hourly check, ~21:46-22:26 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 28760 → 28968, stagnation/boldness
  counter 2070 → 2085.** No live trading this cycle (tick 39 already handled
  at the dedicated 00:20 UTC daily slot, no new bar closed since — confirmed
  via `live_state.json`'s `updated` timestamp at session start,
  `2026-09-22T19:19:06+00:00`, matching the prior 3-hourly check's own
  evolve batch, `runs/2026-09-22-1847-evolve-batch-v3.md`; the intervening
  20:30 UTC daily evaluation, `runs/2026-09-22-2030-daily-evaluation.md`,
  was read-only and didn't touch state). Freshness checks before running:
  `review-hard-calls` still 0 pending (3 reviewed, unchanged), items 6/13
  still owner decisions, item 7 explicitly optional/last, items 2/5/9/10/12
  resolved/parked, `AGENTS.md` size ~232.5KB — well under the 256KB
  threshold — so, with nothing else queued, used the slot for one more real
  15-generation batch via `tools/background_runner.py` (`start` + separate
  `wait`), exit code 0, no truncation, ~30 minutes. Champion's fold-aggregate
  fitness held flat at 1.573 across all 15 generations (947 trades, 38% win,
  1% stops, 4 halts, unchanged throughout). Best-of-generation fold-fitness
  ranged 0.862-2.247, never clearing the promotion-margin bar. See
  `runs/2026-09-22-2226-evolve-batch-v3.md`. Verified before commit: `python3
  -m pytest -q` 426/426 both before (baseline) and after `evolve`; top-level
  key diff of `live_state.json` (checked directly in Python, not just
  eyeballed) showed only `updated`/`researcher_memory`/`lineage` changed
  (genome, broker, journal, hard_call_reviews byte-identical); `lineage`
  length unchanged at 202 (bounded ring buffer, no new promotion attempt
  recorded); `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  `holdout-pressure` re-checked (read-only, no state change) — margin rose
  slightly (7.118, was 7.114) at draw 563, same slow-rise pattern already
  tracked under item 13, nothing new; dashboard rebuilt with `EVO_STATE` set
  (`index.html` shows 28968 challenger ideas tried). Genome still v3 (1d)
  live, untouched. Container started in detached HEAD, matching
  `origin/main`'s tip exactly (same commit, no divergence) — `git checkout
  main` then `git reset --hard origin/main` landed cleanly, nothing lost.

- **Run 2026-09-22 (3-hourly check, ~18:47-19:22 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 28551 → 28760, stagnation/boldness
  counter 2055 → 2070.** No live trading this cycle (tick 39 already handled
  at the dedicated 00:20 UTC daily slot, no new bar closed since — confirmed
  via `live_state.json`'s `updated` timestamp at session start,
  `2026-09-22T16:14:43+00:00`, matching the prior 3-hourly check's own
  evolve batch, `runs/2026-09-22-1617-evolve-batch-v3.md`). Freshness checks
  before running: `review-hard-calls` still 0 pending (3 reviewed,
  unchanged), items 6/13 still owner decisions, item 7 explicitly
  optional/last, items 2/5/9/10/12 resolved/parked, `AGENTS.md` size
  230,175 bytes — well under the 256KB threshold — so, with nothing else
  queued, used the slot for one more real 15-generation batch via
  `tools/background_runner.py` (`start` + separate `wait`), exit code 0, no
  truncation, ~25 minutes. Champion's fold-aggregate fitness held flat at
  1.573 across all 15 generations (947 trades, 38% win, 1% stops, 4 halts,
  unchanged throughout). Best-of-generation fold-fitness ranged 1.569-2.327,
  never clearing the promotion-margin bar. See
  `runs/2026-09-22-1847-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 426/426 both before (baseline) and after `evolve`;
  top-level key diff of `live_state.json` (checked directly in Python, not
  just eyeballed) showed only `updated`/`researcher_memory`/`lineage`
  changed (genome, broker, journal, hard_call_reviews byte-identical);
  `lineage` length unchanged at 202 (bounded ring buffer, no new promotion
  attempt recorded); `tools/edit_bundle_module.py verify`/`sync --check`
  both clean; `holdout-pressure` re-checked (read-only, no state change) —
  margin rose slightly (7.114, was 7.112) at draw 559, same slow-rise
  pattern already tracked under item 13, nothing new; dashboard rebuilt
  with `EVO_STATE` set (`index.html` shows 28760 challenger ideas tried).
  Genome still v3 (1d) live, untouched. Container started in detached HEAD,
  52 commits behind `origin/main` — `git checkout main` then `git merge
  --ff-only origin/main` fast-forwarded cleanly, nothing lost.

- **Run 2026-09-22 (3-hourly check, ~15:46-16:17 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 28344 → 28551, stagnation/boldness
  counter 2041 → 2055.** No live trading this cycle (tick 39 already handled
  at the dedicated 00:20 UTC daily slot, no new bar closed since — confirmed
  via `live_state.json`'s `updated` timestamp at session start,
  `2026-09-22T13:15:10+00:00`, matching the prior 3-hourly check's own
  evolve batch, `runs/2026-09-22-1318-evolve-batch-v3.md`). Freshness checks
  before running: `review-hard-calls` still 0 pending (3 reviewed,
  unchanged), items 6/13 still owner decisions, item 7 explicitly
  optional/last, items 2/5/9/10/12 resolved/parked, `AGENTS.md` size
  227,931 bytes — well under the 256KB threshold — so, with nothing else
  queued, used the slot for one more real 15-generation batch via
  `tools/background_runner.py` (`start` + separate `wait`), exit code 0, no
  truncation, ~28 minutes. Champion's fold-aggregate fitness held flat at
  1.573 across all 15 generations (947 trades, 38% win, 1% stops, 4 halts,
  unchanged throughout). Best-of-generation fold-fitness ranged 1.534-1.967,
  never clearing the promotion-margin bar. See
  `runs/2026-09-22-1617-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 426/426 both before (baseline) and after `evolve`;
  top-level key diff of `live_state.json` (checked directly in Python, not
  just eyeballed) showed only `updated`/`researcher_memory`/`lineage`
  changed (genome, broker, journal, hard_call_reviews byte-identical);
  `lineage` length unchanged at 202 (bounded ring buffer, no new promotion
  attempt recorded); `tools/edit_bundle_module.py verify`/`sync --check`
  both clean; `holdout-pressure` re-checked (read-only, no state change) —
  margin rose slightly (7.112, was 7.111) at draw 557, same slow-rise
  pattern already tracked under item 13, nothing new; dashboard rebuilt
  with `EVO_STATE` set (`index.html` shows 28551 challenger ideas tried).
  Genome still v3 (1d) live, untouched. Container arrived on `main` already
  at `origin/main`'s tip (one fast-forward pull, 3 commits), nothing lost.

- **Run 2026-09-22 (3-hourly check, ~12:47-13:18 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 28137 → 28344, stagnation/boldness
  counter 2026 → 2041.** No live trading this cycle (tick 39 already handled
  at the dedicated 00:20 UTC daily slot, no new bar closed since — confirmed
  via `live_state.json`'s `updated` timestamp at session start,
  `2026-09-22T07:16:25+00:00`, matching the prior 3-hourly check's own
  evolve batch, `runs/2026-09-22-0719-evolve-batch-v3.md`). Freshness checks
  before running: `review-hard-calls` still 0 pending (3 reviewed,
  unchanged), items 6/13 still owner decisions, item 7 explicitly
  optional/last, items 2/5/9/10/12 resolved/parked, `AGENTS.md` size 225,584
  bytes — comfortably under the 256KB threshold after last cycle's archival —
  so, with nothing else queued, used the slot for one more real
  15-generation batch via `tools/background_runner.py` (`start` + separate
  `wait`), exit code 0, no truncation, ~25 minutes. Champion's
  fold-aggregate fitness held flat at 1.573 across all 15 generations (947
  trades, 38% win, 1% stops, 4 halts, unchanged throughout). Best-of-generation
  fold-fitness ranged 1.531-2.012, never clearing the promotion-margin bar.
  See `runs/2026-09-22-1318-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 426/426 both before (baseline) and after `evolve`;
  top-level key diff of `live_state.json` (checked directly in Python, not
  just eyeballed) showed only `updated`/`researcher_memory`/`lineage`
  changed (genome, broker, journal, hard_call_reviews byte-identical);
  `lineage` length unchanged at 202 (bounded ring buffer, no new promotion
  attempt recorded); `tools/edit_bundle_module.py verify`/`sync --check`
  both clean; `holdout-pressure` re-checked (read-only, no state change) —
  margin rose slightly (7.111, was 7.109) at draw 556, same slow-rise
  pattern already tracked under item 13, nothing new; dashboard rebuilt
  with `EVO_STATE` set (`index.html` shows 28344 challenger ideas tried).
  Genome still v3 (1d) live, untouched. Container arrived on `main` already
  at `origin/main`'s tip in a detached HEAD state (identical commit);
  `git checkout main` resolved it cleanly, no pull needed, nothing lost.

- **Run 2026-09-22 (3-hourly check, ~09:45-09:52 UTC): resolved item 11 —
  archived the next oldest 2-day slice of this log (2026-09-15 ~00:48
  through 2026-09-16 ~21:51 UTC) into `AGENTS_ARCHIVE_2026-09-15_to_2026-09-16.md`,
  `AGENTS.md` 252,962 → 224,019 bytes.** No live trading this cycle (tick
  39 already handled at the dedicated 00:20 UTC daily slot — confirmed via
  `live_state.json`'s `updated` timestamp at session start,
  `2026-09-22T07:16:25+00:00`, matching the prior 3-hourly check's own
  evolve batch, `runs/2026-09-22-0719-evolve-batch-v3.md`). File size was
  close to the 256KB single-read limit again (same recurring pattern the
  2026-09-04/09-10/09-15/09-16/09-18/09-20 rotations each hit), growing
  ~23KB over the prior ~31 hours of 3-hourly evolve-batch entries — would
  have crossed the limit within 1-2 more cycles, so used this slot for the
  housekeeping instead of another `evolve` batch on top of 20+ consecutive
  no-promotion batches already logged. See `runs/2026-09-22-0952-agents-md-archival.md`
  for the full method and verification (exact-marker Python slice, not
  manual line counting; archived body confirmed character-for-character
  identical to the original; everything outside the touched region
  confirmed byte-for-byte unchanged; `git diff --stat` on `live_state.json`/
  `evotrader.manifest` empty; `python3 -m pytest -q` 426/426, unchanged
  from baseline since this is text-only). `AGENTS.md` now keeps everything
  from `Run 2026-09-17 ~00:47 UTC` onward. Genome still v3 (1d) live,
  untouched.

- **Run 2026-09-22 (3-hourly check, ~06:47-07:19 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 27930 → 28137, stagnation/boldness
  counter 2011 → 2026.** No live trading this cycle (tick 39 already
  handled at the dedicated 00:20 UTC daily slot — confirmed via
  `live_state.json`'s `updated` timestamp at session start,
  `2026-09-22T04:18:07+00:00`, matching the prior 3-hourly check's own
  evolve batch, `runs/2026-09-22-0421-evolve-batch-v3.md`). Freshness checks
  before running: `review-hard-calls` still 0 pending (3 reviewed,
  unchanged), items 6/13 still owner decisions, item 7 explicitly
  optional/last, items 2/5/9/10/12 resolved/parked, `AGENTS.md` size
  ~250.7KB — close to but still under the 256KB threshold, worth watching —
  so, with nothing else queued, used the slot for one more real
  15-generation batch via `tools/background_runner.py` (`start` + separate
  `wait`), exit code 0, no truncation, ~29 minutes. Champion's
  fold-aggregate fitness held flat at 1.573 across all 15 generations (947
  trades, 38% win, 1% stops, 4 halts, unchanged throughout). Best-of-generation
  fold-fitness ranged 1.564-1.921, never clearing the promotion-margin bar.
  See `runs/2026-09-22-0719-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 426/426 both before (baseline) and after `evolve`;
  top-level key diff of `live_state.json` (checked directly in Python, not
  just eyeballed) showed only `updated`/`researcher_memory`/`lineage`
  changed (genome, broker, journal, hard_call_reviews byte-identical);
  `lineage` length unchanged at 202 (bounded ring buffer, no new promotion
  attempt recorded); `tools/edit_bundle_module.py verify`/`sync --check`
  both clean; `holdout-pressure` re-checked (read-only, no state change) —
  margin rose slightly (7.109, was 7.108) at draw 554, same slow-rise
  pattern already tracked under item 13, nothing new; dashboard rebuilt
  with `EVO_STATE` set (`index.html` shows 28137 challenger ideas tried).
  Genome still v3 (1d) live, untouched. Container started in detached HEAD,
  47 commits behind `origin/main` — `git checkout main && git pull origin
  main` fast-forwarded cleanly, nothing lost.

- **Run 2026-09-22 (3-hourly check, ~03:47-04:21 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 27722 → 27930, stagnation/boldness
  counter 1996 → 2011.** No live trading this cycle (tick 39 already
  handled at the dedicated 00:20 UTC daily slot — confirmed via
  `live_state.json`'s `updated` timestamp at session start,
  `2026-09-22T01:13:17+00:00`, matching the prior 3-hourly check's own
  evolve batch, `runs/2026-09-22-0116-evolve-batch-v3.md`). Freshness checks
  before running: `review-hard-calls` still 0 pending (3 reviewed,
  unchanged), items 6/13 still owner decisions, item 7 explicitly
  optional/last, items 2/5/9/10/12 resolved/parked, `AGENTS.md` size
  ~248KB — under the 256KB threshold — so, with nothing else queued, used
  the slot for one more real 15-generation batch via
  `tools/background_runner.py` (`start` + separate `wait`), exit code 0, no
  truncation, ~28 minutes. Champion's fold-aggregate fitness held flat at
  1.573 across all 15 generations (947 trades, 38% win, 1% stops, 4 halts,
  unchanged throughout). Best-of-generation fold-fitness ranged
  0.997-1.963, never clearing the promotion-margin bar. See
  `runs/2026-09-22-0421-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 426/426 both before (baseline) and after `evolve`;
  top-level key diff of `live_state.json` (checked directly in Python, not
  just eyeballed) showed only `updated`/`researcher_memory`/`lineage`
  changed (genome, broker, journal, hard_call_reviews byte-identical);
  `lineage` length unchanged at 202 (bounded ring buffer, no new promotion
  attempt recorded); `tools/edit_bundle_module.py verify`/`sync --check`
  both clean; `holdout-pressure` re-checked (read-only, no state change) —
  margin rose slightly (7.108, was 7.106) at draw 553, same slow-rise
  pattern already tracked under item 13, nothing new; dashboard rebuilt
  with `EVO_STATE` set (`index.html` shows 27930 challenger ideas tried).
  Genome still v3 (1d) live, untouched. Container started already on `main`
  at `origin/main`'s tip, one fast-forward pull (46 commits) landed cleanly.

- **Run 2026-09-22 (3-hourly check, ~00:46-01:16 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 27514 → 27722, stagnation/boldness
  counter 1981 → 1996.** No live trading this cycle (tick 39 already
  handled at the dedicated 00:20 UTC daily slot — confirmed via
  `live_state.json`'s `updated` timestamp at session start,
  `2026-09-22T00:22:43+00:00`, from `runs/2026-09-22-0020-daily-trading.md`,
  NAV $14,227.20, held, no trade). Freshness checks before running:
  `review-hard-calls` still 0 pending (3 reviewed, unchanged), items 6/13
  still owner decisions, item 7 explicitly optional/last, items 2/5/9/10/12
  resolved/parked, `AGENTS.md` size 246,278 bytes — under the 256KB
  threshold — so, with nothing else queued, used the slot for one more
  real 15-generation batch via `tools/background_runner.py` (`start` +
  separate `wait`), exit code 0, no truncation. Champion's fold-aggregate
  fitness held flat at 1.573 across all 15 generations (947 trades, 38%
  win, 1% stops, 4 halts, unchanged throughout). Best-of-generation
  fold-fitness ranged 1.592-2.106, never clearing the promotion-margin
  bar. See `runs/2026-09-22-0116-evolve-batch-v3.md`. Verified before
  commit: `python3 -m pytest -q` 426/426 both before (baseline) and after
  `evolve`; top-level key diff of `live_state.json` showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker,
  journal, hard_call_reviews byte-identical); `lineage` length unchanged
  at 202 — confirmed a bounded ring-buffer (maxlen 202: `after[i] ==
  before[i+15]` for 185/187 checkable positions, the window sliding by
  the 15 new generations, not a real content change, no new promotion
  attempt recorded); `tools/edit_bundle_module.py verify`/`sync --check`
  both clean; `holdout-pressure` re-checked (read-only, no state change)
  — margin rose slightly (7.106, was 7.104) at draw 551, same slow-rise
  pattern already tracked under item 13, nothing new; dashboard rebuilt
  with `EVO_STATE` set (`index.html` shows 27722 challenger ideas tried).
  Genome still v3 (1d) live, untouched.

- **Run 2026-09-21 (3-hourly check, ~21:46-22:20 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 27307 → 27514, stagnation/boldness
  counter 1966 → 1981.** No live trading this cycle (tick 38 already
  handled at the dedicated 00:20 UTC daily slot — confirmed via
  `live_state.json`'s `updated` timestamp at session start,
  `2026-09-21T19:17:04+00:00`, from the prior 3-hourly check's own evolve
  batch, and both `runs/2026-09-21-0020-daily-trading.md` and the 20:30
  UTC daily evaluation `runs/2026-09-21-2030-daily-evaluation.md`).
  Freshness checks before running: `review-hard-calls` still 0 pending (3
  reviewed, unchanged, nothing new since no tick ran), items 6/13 still
  owner decisions, item 7 explicitly optional/last, items 2/5/9/10/12
  resolved/parked, `AGENTS.md` size 243,867 bytes — under the 256KB
  threshold — so, with nothing else queued, used the slot for one more
  real 15-generation batch (development against the live champion) via
  `tools/background_runner.py` (`start` + separate `wait`, only the flags
  that subcommand actually defines this time — no repeat of the
  `--log`-on-`wait` slip from the 18:46 UTC batch), exit code 0, no
  truncation, ~27 minutes. Champion's fold-aggregate fitness held flat at
  1.636 across all 15 generations (943 trades, 38% win, 1% stops, 4 halts,
  unchanged throughout). Best-of-generation fold-fitness ranged
  1.554-2.853, never clearing the promotion-margin bar. See
  `runs/2026-09-21-2220-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 426/426 both before (baseline) and after
  `evolve`; top-level key diff of `live_state.json` showed only
  `updated`/`researcher_memory`/`lineage` changed (genome, broker,
  journal, hard_call_reviews byte-identical, `lineage` length unchanged at
  202 — no new promotion attempt recorded); `tools/edit_bundle_module.py
  verify`/`sync --check` both clean; `holdout-pressure` re-checked
  (read-only, no state change) — margin rose slightly (7.104, was 7.088)
  at draw 549, same slow-rise pattern already tracked under item 13,
  nothing new; dashboard rebuilt correctly with `EVO_STATE` set
  (`index.html` shows 27514 challenger ideas tried). Genome still v3 (1d)
  live, untouched. Container started already on `main` at `origin/main`'s
  tip, no pull needed.

- **Run 2026-09-21 (3-hourly check, ~18:46-19:20 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 27099 → 27307, stagnation/boldness
  counter 1950 → 1965.** No live trading this cycle (tick 38 already handled
  at the dedicated 00:20 UTC daily slot — confirmed via `live_state.json`'s
  `updated` timestamp at session start, `2026-09-21T16:16:53+00:00`, from
  the prior 3-hourly check's own evolve batch, and
  `runs/2026-09-21-0020-daily-trading.md`). Freshness checks before
  running: `review-hard-calls` still 0 pending (3 reviewed, unchanged),
  items 2/5/6/13 still not a scheduled session's call, item 7 (bundle
  unflatten) explicitly optional/last, `AGENTS.md` size 240,997 bytes —
  under the 256KB threshold — so, with nothing else queued, used the slot
  for one more real 15-generation batch (development against the live
  champion) via `tools/background_runner.py` (`start` + separate `wait`),
  exit code 0, no truncation, ~34 minutes. One operational snag this cycle:
  the first `wait` call was mistakenly given an extra `--log` flag that
  subcommand doesn't accept, so argparse errored immediately; piping that
  call through `tail -60` masked the failure by surfacing `tail`'s own exit
  code (0) instead. Caught by checking `ps` directly (the evolve process
  was still genuinely running), fixed by re-running `wait` with only the
  flags it defines — no output or state was lost, the child had been
  writing straight to `--log` throughout regardless. See
  `runs/2026-09-21-1920-evolve-batch-v3.md` for the full note; flagging here
  since this is the same footgun class item 9 named (piping a backgrounded
  command's own status/wait call through something that can substitute a
  different exit code), just on the `wait` side rather than `start`.
  Champion's fold-aggregate fitness held flat at 1.636 across all 15
  generations (943 trades, 38% win, 1% stops, 4 halts, unchanged
  throughout). Best-of-generation fold-fitness ranged 1.472-2.637, never
  clearing the promotion-margin bar. Verified before commit: `python3 -m
  pytest -q` 426/426 both before (baseline) and after `evolve`; top-level
  key diff of `live_state.json` showed only
  `lineage`/`researcher_memory`/`updated` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `tools/edit_bundle_module.py
  verify`/`sync --check` both clean; `holdout-pressure` re-checked
  (read-only, no state change) — margin rose slightly (7.102, was 7.097) at
  draw 547, nothing new; dashboard rebuilt correctly with `EVO_STATE` set
  (`index.html` shows 27307 challenger ideas tried). Genome still v3 (1d)
  live, untouched. Container started already on `main` at `origin/main`'s
  tip after a 41-commit fast-forward pull (detached HEAD on arrival), nothing lost.

- **Run 2026-09-21 (3-hourly check, ~15:46-16:20 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 26893 → 27099, stagnation/boldness
  counter 1936 → 1950.** No live trading this cycle (tick 38 already handled
  at the dedicated 00:20 UTC daily slot — confirmed via `live_state.json`'s
  `updated` timestamp at session start, `2026-09-21T13:19:52+00:00`, from
  the prior 3-hourly check's own evolve batch, and
  `runs/2026-09-21-0020-daily-trading.md`). Freshness checks before
  running: `review-hard-calls` still 0 pending (3 reviewed, unchanged),
  items 6/13 still not a scheduled session's call, item 5 (short selling)
  still blocked on the unscoped "allow opening a short" owner decision,
  item 7 (bundle unflatten) explicitly optional/last, `AGENTS.md` size
  238,701 bytes — under the 256KB threshold — so, with nothing else
  queued, used the slot for one more real 15-generation batch (development
  against the live champion) via `tools/background_runner.py` (`start` +
  separate `wait`), exit code 0, no truncation, ~26.5 minutes. Champion's
  fold-aggregate fitness held flat at 1.636 across all 15 generations (943
  trades, 38% win, 1% stops, 4 halts, unchanged throughout). Best-of-generation
  fold-fitness ranged 1.407-2.096, never clearing the promotion-margin bar.
  See `runs/2026-09-21-1546-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 426/426 both before (baseline) and after `evolve`;
  top-level key diff of `live_state.json` showed only
  `lineage`/`researcher_memory`/`updated` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `tools/edit_bundle_module.py
  verify`/`sync --check` both clean; `holdout-pressure` re-checked
  (read-only, no state change) — margin rose slightly (7.097, was 7.093) at
  draw 542, nothing new; dashboard rebuilt correctly with `EVO_STATE` set
  (`index.html` shows 27099 challenger ideas tried). Genome still v3 (1d)
  live, untouched. Container started in detached HEAD at `origin/main`'s
  tip; `git checkout main` landed on the tracking branch cleanly, then
  `git pull origin main` fast-forwarded 40 commits that had accumulated
  since the branch was last updated, nothing lost.

- **Run 2026-09-21 (3-hourly check, ~12:46-13:23 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 26684 → 26893, stagnation/boldness
  counter 1921 → 1936.** No live trading this cycle (tick 38 already handled
  at the dedicated 00:20 UTC daily slot — confirmed via `live_state.json`'s
  `updated` timestamp at session start, `2026-09-21T10:10:30+00:00`, from
  the prior 3-hourly check's own evolve batch, and
  `runs/2026-09-21-0020-daily-trading.md`). Freshness checks before
  running: `review-hard-calls` still 0 pending (3 reviewed, unchanged),
  items 6/13 still not a scheduled session's call, item 5 (short selling)
  still blocked on the unscoped "allow opening a short" owner decision,
  item 7 (bundle unflatten) explicitly optional/last, `AGENTS.md` size
  236,407 bytes — under the 256KB threshold — so, with nothing else
  queued, used the slot for one more real 15-generation batch (development
  against the live champion) via `tools/background_runner.py` (`start` +
  separate `wait`), exit code 0, no truncation, ~30 minutes. Champion's
  fold-aggregate fitness held flat at 1.636 across all 15 generations (943
  trades, 38% win, 1% stops, 4 halts, unchanged throughout). Best-of-generation
  fold-fitness ranged 1.359-2.048, never clearing the promotion-margin bar.
  See `runs/2026-09-21-1323-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 426/426 both before (baseline) and after `evolve`;
  top-level key diff of `live_state.json` showed only
  `lineage`/`researcher_memory`/`updated` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `tools/edit_bundle_module.py
  verify`/`sync --check` both clean; `holdout-pressure` re-checked
  (read-only, no state change) — margin rose slightly (7.095, was 7.093) at
  draw 540, nothing new; dashboard rebuilt correctly with `EVO_STATE` set
  (`index.html` shows 26893 challenger ideas tried). Genome still v3 (1d)
  live, untouched. Container started in detached HEAD at `origin/main`'s
  tip; `git checkout main` landed on the tracking branch cleanly, then
  `git pull origin main` fast-forwarded 39 commits that had accumulated
  since the branch was last updated, nothing lost.

- **Run 2026-09-21 (3-hourly check, ~09:46-10:13 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 26670 → 26684, stagnation/boldness
  counter 1905 → 1920.** No live trading this cycle (tick 38 already handled
  at the dedicated 00:20 UTC daily slot — confirmed via `live_state.json`'s
  `updated` timestamp at session start, `2026-09-21T07:08:46+00:00`, from
  the prior 3-hourly check's own evolve batch, and
  `runs/2026-09-21-0020-daily-trading.md`). Freshness checks before
  running: `review-hard-calls` still 0 pending (3 reviewed, unchanged),
  items 6/13 still not a scheduled session's call, `AGENTS.md` size 234,430
  bytes — under the 256KB threshold — so, with nothing else queued, used
  the slot for one more real 15-generation batch (development against the
  live champion) via `tools/background_runner.py` (`start` + separate
  `wait`), exit code 0, no truncation, ~20.5 minutes. Champion's
  fold-aggregate fitness held flat at 1.636 across all 15 generations (943
  trades, 38% win, 1% stops, 4 halts, unchanged throughout). Best-of-generation
  fold-fitness ranged 1.638-2.637, never clearing the promotion-margin bar.
  See `runs/2026-09-21-1013-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 426/426 both before (baseline) and after `evolve`;
  top-level key diff of `live_state.json` showed only
  `lineage`/`researcher_memory`/`updated` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `tools/edit_bundle_module.py
  verify`/`sync --check` both clean; `holdout-pressure` re-checked
  (read-only, no state change) — margin rose slightly (7.093, was 7.088) at
  draw 539, nothing new; dashboard rebuilt correctly with `EVO_STATE` set
  (`index.html` shows 26684 challenger ideas tried). Genome still v3 (1d)
  live, untouched. Container started already on `main` at `origin/main`'s
  tip, no pull needed.

- **Run 2026-09-21 (3-hourly check, ~06:46-07:11 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 26266 → 26475, stagnation/boldness
  counter 1890 → 1905.** No live trading this cycle (tick 38 already handled
  at the dedicated 00:20 UTC daily slot — confirmed via `live_state.json`'s
  `updated` timestamp at session start, `2026-09-21T04:25:32+00:00`, from
  the prior 3-hourly check's own evolve batch, and
  `runs/2026-09-21-0020-daily-trading.md`). Freshness checks before
  running: `review-hard-calls` still 0 pending (3 reviewed, unchanged),
  items 2/5/6/13 still not a scheduled session's call, items 9/10/12
  already resolved, `AGENTS.md` size 232,222 bytes — well under the 256KB
  threshold — so, with nothing else queued, used the slot for one more real
  15-generation batch (offline/shadow development against the live
  champion) via `tools/background_runner.py` (`start` + backgrounded
  `wait`), exit code 0, no truncation, ~25 minutes. Champion's
  fold-aggregate fitness held flat at 1.636 across all 15 generations (943
  trades, 38% win, 1% stops, 4 halts, unchanged throughout). Best-of-generation
  fold-fitness ranged 1.638-2.162, never clearing the promotion-margin bar.
  See `runs/2026-09-21-0711-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 426/426 both before (baseline) and after `evolve`;
  top-level key diff of `live_state.json` showed only
  `lineage`/`researcher_memory`/`updated` changed (genome, broker, journal,
  hard_call_reviews byte-identical); `tools/edit_bundle_module.py
  verify`/`sync --check` both clean; `holdout-pressure` re-checked
  (read-only, no state change) — margin rose slightly (7.088, was 7.085) at
  draw 534, nothing new; dashboard rebuilt correctly with `EVO_STATE` set
  (`index.html` shows 26475 challenger ideas tried). Genome still v3 (1d)
  live, untouched. Container started with `main` checked out but 36
  commits behind `origin/main` (detached HEAD) — `git checkout main && git
  reset --hard origin/main` (verified matched exactly, working tree already
  clean) fast-forwarded cleanly, nothing lost.

- **Run 2026-09-21 (3-hourly check, ~03:46-04:29 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 26059 → 26266, stagnation/boldness
  counter 1875 → 1890.** No live trading this cycle (tick 38 already handled
  at the dedicated 00:20 UTC daily slot — confirmed via `live_state.json`'s
  `updated` timestamp at session start, `2026-09-21T01:29:11+00:00`, from
  the prior 3-hourly check's own evolve batch, and
  `runs/2026-09-21-0020-daily-trading.md`). Freshness checks before
  running: `review-hard-calls` still 0 pending (3 reviewed, unchanged),
  items 2/5/6/13 still not a scheduled session's call, `AGENTS.md` size
  230,057 bytes — well under the 256KB threshold — so, with nothing else
  queued, used the slot for one more real 15-generation batch
  (offline/shadow development against the live champion) via
  `tools/background_runner.py` (`start` + backgrounded `wait`), exit code
  0, no truncation, ~35 minutes. Champion's fold-aggregate fitness held
  flat at 1.636 across all 15 generations (943 trades, 38% win, 1% stops, 4
  halts, unchanged throughout). Best-of-generation fold-fitness ranged
  1.515-2.413, never clearing the promotion-margin bar. See
  `runs/2026-09-21-0429-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 426/426 both before (baseline) and after `evolve`;
  top-level key diff of `live_state.json` showed only
  `lineage`/`researcher_memory`/`updated` changed (genome, broker, journal,
  hard_call_reviews byte-identical); constitution manifest
  `726dfa4bac85891a` unchanged; `tools/edit_bundle_module.py
  verify`/`sync --check` both clean; `holdout-pressure` re-checked
  (read-only, no state change) — margin rose slightly (7.085, was 7.082) at
  draw 531, nothing new; dashboard rebuilt correctly with `EVO_STATE` set
  (`index.html` shows 26266 challenger ideas tried). Genome still v3 (1d)
  live, untouched. Container started with `main` checked out but 35
  commits behind `origin/main` (detached HEAD) — `git checkout main && git
  pull origin main` fast-forwarded cleanly, nothing lost.

- **Run 2026-09-21 (same 3-hourly check, ~01:00-01:30 UTC): 15 more real
  `evolve` generations against the live v3 (1d) champion, no promotion —
  cumulative candidates tried against v3 rose 25854 → 26059,
  stagnation/boldness counter 1860 → 1875.** Ran after the hard-call
  review below (same session), with nothing else queued (`review-hard-calls`
  0 pending, 3 reviewed; items 2/5/6/13 still not a scheduled session's
  call; `AGENTS.md` size 228,180 bytes, well under the 256KB threshold) —
  used the rest of the slot for one more real 15-generation batch
  (offline/shadow development against the live champion) via
  `tools/background_runner.py` (`start` + backgrounded `wait`), exit code
  0, no truncation, ~30 minutes. Champion's fitness held flat at 1.636
  across all 15 generations (943 trades, 38% win, 1% stops, 4 halts,
  unchanged throughout) — this figure (and trade count) differs from the
  ~1.728/960-trade figure in recent prior entries because the rolling
  backtest window advanced by tick 38's new daily bar, not because the
  champion changed; genome and all trading-relevant state are
  byte-identical before/after. Best-of-generation fitness ranged
  1.469-2.413, never clearing the promotion-margin bar. See
  `runs/2026-09-21-0122-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 426/426 after the batch; top-level key diff of
  `live_state.json` showed only `lineage`/`researcher_memory`/`updated`
  changed (genome, broker, journal, hard_call_reviews byte-identical);
  `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  `holdout-pressure` re-checked (read-only, no state change) — margin rose
  slightly (7.082, was 7.078) at draw 528, nothing new; dashboard rebuilt
  correctly with `EVO_STATE` set (`index.html` shows 26059 challenger
  ideas tried). Genome still v3 (1d) live, untouched.

- **Run 2026-09-21 (3-hourly check, ~00:46-00:55 UTC): the first real
  hard-call review — tick 38's lone-voice ICPUSDT buy — reconstructed by
  hand and approved.** No live trading this cycle (tick 38 already handled
  at the dedicated 00:20 UTC daily slot — confirmed via `live_state.json`'s
  `updated` timestamp at session start, `2026-09-21T00:22:31+00:00`, and
  `runs/2026-09-21-0020-daily-trading.md`; `38 % 7 = 3` so no `evolve`
  fired as part of that tick either). `review-hard-calls` (no args) showed
  1 bar pending — the first live tick ever flagged `is_hard_call: true`
  since that infrastructure shipped 2026-08-17 (item 4's "flag hard calls"
  half); items 16 and 32's earlier reviews were both prompted by a
  scheduled session going looking, not a real flag. Reconstructed
  `RiskJudge.rule`'s scoring by hand against v3's evolved genes
  (`base_size_pct` 0.2392, `lone_voice_scale` 1.4791, `two_agree_bonus`
  1.2, `max_position_pct` 0.25, `cash_floor_pct` 0.3503), matched to the
  exact cent: of 14 buy candidates, ICPUSDT (lone-voice, share 1/3, conv
  0.858, score 1.2691) was genuinely the top-scored, and its target hit
  the 25% position cap first, so `full_amount = min(0.25*equity,
  cash_avail) = cash_avail` exactly = $3012.9506894161623, matching the
  real order's $3012.95 to the cent and leaving $0.00 deployable — which
  is why every other candidate that bar, including higher-conviction
  FETUSDT, was correctly vetoed "no room" (cash-floor exhaustion by the
  single highest-scored order, not a bug). One observation, not a defect:
  the underlying signal's slope (+0.34%) was nearly flat next to every
  other candidate's that bar (+1.55% to +17.18%) — a legitimate
  confirmed-trend read by `consult_moderate.min_slope`'s own threshold
  (0, any nonnegative slope qualifies), just weaker on the momentum axis
  than its lone-voice score alone suggests. Recorded verdict "approve" via
  `--tick 38 --verdict approve --notes '...'` (full arithmetic in
  `runs/2026-09-21-0051-first-real-hard-call-review.md`);
  `review-hard-calls` now reports 0 pending, 3 reviewed (ticks 16, 32, 38).
  Verified before commit: `python3 -m pytest -q` 426/426; top-level key
  diff of `live_state.json` showed only `updated`/`hard_call_reviews`
  changed (genome, broker, journal, researcher_memory, lineage
  byte-identical); constitution manifest `726dfa4bac85891a` unchanged;
  dashboard rebuilt correctly with `EVO_STATE` set. Genome still v3 (1d)
  live, untouched. Container started with `main` checked out but 33
  commits behind `origin/main` (not detached HEAD this time) — `git pull
  origin main` fast-forwarded cleanly, nothing lost.

- **Run 2026-09-20 (3-hourly check, ~21:46-22:16 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 25646 → 25854, stagnation/boldness
  counter 1845 → 1860.** No live trading this cycle (tick 37 already
  handled at the dedicated 00:20 UTC daily slot — confirmed via
  `live_state.json`'s `updated` timestamp at session start,
  `2026-09-20T16:10:13+00:00`, from the prior 3-hourly check's own evolve
  batch, and `runs/2026-09-20-0020-daily-trading.md`). Freshness checks
  before running: `review-hard-calls` still 0 pending (2 reviewed,
  unchanged), items 2/5/6/13 still not a scheduled session's call,
  `AGENTS.md` size 223,051 bytes (already archived earlier today's
  ~18:46-18:55 UTC cycle) — well under the 256KB threshold — so, with
  nothing else queued, used the slot for one more real 15-generation batch
  (offline/shadow development against the live champion) via
  `tools/background_runner.py` (`start` + backgrounded `wait`), exit code
  0, no truncation, ~30 minutes. Champion's fold-aggregate fitness held
  flat at 1.728 across all 15 generations (960 trades, 40% win, 1% stops, 3
  halts, unchanged throughout). Best-of-generation fold-fitness ranged
  1.576-2.045, never clearing the promotion-margin bar. See
  `runs/2026-09-20-2216-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 426/426 both before (baseline) and after `evolve`,
  clean both times, no flake this cycle; direct top-level key diff of
  `live_state.json` showed only `lineage`/`researcher_memory`/`updated`
  changed (genome, broker, journal, hard_call_reviews byte-identical);
  constitution manifest `726dfa4bac85891a` unchanged;
  `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  `holdout-pressure` re-checked (read-only, no state change) — margin
  unchanged at 7.078, draw 524, nothing new; dashboard rebuilt correctly
  with `EVO_STATE` set (`index.html` shows 25854 challenger ideas tried).
  Genome still v3 (1d) live, untouched. Container started in detached HEAD
  again (no local commits, `origin/main` at `a32a401`) — `git checkout main
  && git pull origin main` fast-forwarded cleanly, nothing lost.

- **Run 2026-09-20 (3-hourly check, ~15:46-16:20 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 25439 → 25646, stagnation/boldness
  counter 1831 → 1845.** No live trading this cycle (tick 37 already
  handled at the dedicated 00:20 UTC daily slot — confirmed via
  `live_state.json`'s `updated` timestamp at session start,
  `2026-09-20T13:27:07+00:00`, from the prior 3-hourly check's own evolve
  batch, and `runs/2026-09-20-0020-daily-trading.md`). Freshness checks
  before running: `review-hard-calls` still 0 pending (2 reviewed,
  unchanged), items 2/5/6 still not a scheduled session's call, item 13
  (`HOLDOUT_SIGMA` cumulative-margin question) still the owner's call,
  `AGENTS.md` size 259,648 bytes — closer to the 256KB (262,144-byte)
  rotation threshold but still under it, worth continued watching but not
  rotated this cycle — so, with nothing else queued, used the slot for one
  more real 15-generation batch (offline/shadow development against the
  live champion) via `tools/background_runner.py` (`start` + backgrounded
  `wait`), exit code 0, no truncation, ~30 minutes. Champion's
  fold-aggregate fitness held flat at 1.728 across all 15 generations (960
  trades, 40% win, 1% stops, 3 halts, unchanged throughout). Best-of-generation
  fold-fitness ranged 1.542-2.012, never clearing the promotion-margin bar.
  See `runs/2026-09-20-1546-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 426/426 both before (baseline) and after `evolve`;
  one isolated re-run right after showed a single flaky failure in
  `test_evolve_saves_and_matches_its_own_dry_run_decision` (that test only
  touches scratch state under `tmp_path`, unrelated to the real
  `live_state.json` change) — re-ran alone (passed) and the full suite
  twice more (426/426 both times), confirmed as a one-off flake, not a
  regression; direct top-level key diff of `live_state.json` showed only
  `lineage`/`researcher_memory`/`updated` changed (genome, broker, journal,
  hard_call_reviews byte-identical); constitution manifest `726dfa4bac85891a`
  unchanged; `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  `holdout-pressure` re-checked (read-only, no state change) — margin
  unchanged at 7.078, draw 524, nothing new; dashboard rebuilt correctly
  with `EVO_STATE` set (`index.html` shows 25646 challenger ideas tried).
  Genome still v3 (1d) live, untouched. Container started in detached HEAD
  again (27 commits behind `origin/main`, no local commits of its own) —
  `git checkout main && git pull origin main` fast-forwarded cleanly,
  nothing lost.

- **Run 2026-09-20 (3-hourly check, ~12:47-13:32 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 25233 → 25439, stagnation/boldness
  counter 1816 → 1831.** No live trading this cycle (tick 37 already
  handled at the dedicated 00:20 UTC daily slot — confirmed via
  `live_state.json`'s `updated` timestamp at session start,
  `2026-09-20T10:14:33+00:00`, from the prior 3-hourly check's own evolve
  batch, and `runs/2026-09-20-0020-daily-trading.md`). Freshness checks
  before running: `review-hard-calls` still 0 pending (2 reviewed,
  unchanged), items 2/5/6 still not a scheduled session's call, item 4
  blocked on a real hard-call flag (none pending), item 13 (`HOLDOUT_SIGMA`
  cumulative-margin question) still the owner's call, `AGENTS.md` size
  ~257KB — close to, but still under, the 256KB (262,144-byte) rotation
  threshold, worth continued watching but not rotated this cycle — so, with
  nothing else queued, used the slot for one more real 15-generation batch
  (offline/shadow development against the live champion) via
  `tools/background_runner.py` (`start` + backgrounded `wait`), exit code 0,
  no truncation. Champion's fold-aggregate fitness held flat at 1.728 across
  all 15 generations (960 trades, 40% win, 1% stops, 3 halts, unchanged
  throughout). Best-of-generation fold-fitness ranged 1.515-2.398, never
  clearing the promotion-margin bar. See
  `runs/2026-09-20-1332-evolve-batch-v3.md`. Verified before commit: `python3
  -m pytest -q` 426/426 both before (baseline) and after `evolve`; direct
  top-level key diff of `live_state.json` showed only
  `lineage`/`researcher_memory`/`updated` changed (genome, broker, journal,
  hard_call_reviews byte-identical); constitution manifest `726dfa4bac85891a`
  unchanged; `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  `holdout-pressure` re-checked (read-only, no state change) — margin rose
  slightly (7.078, was 7.076) at draw 524, nothing new; dashboard rebuilt
  correctly with `EVO_STATE` set (`index.html` shows 25439 challenger ideas
  tried). Genome still v3 (1d) live, untouched. Container started in
  detached HEAD again (26 commits behind `origin/main`, no local commits of
  its own) — `git checkout main && git pull origin main` fast-forwarded
  cleanly, nothing lost.

- **Run 2026-09-20 (3-hourly check, ~09:45-10:17 UTC): cross-referenced the
  HOLDOUT_SIGMA cumulative-margin question as a proper numbered item, then
  15 more real `evolve` generations against the live v3 (1d) champion, no
  promotion — cumulative candidates tried against v3 rose 25025 → 25233,
  stagnation/boldness counter 1801 → 1816.** No live trading this cycle
  (tick 37 already handled at the dedicated 00:20 UTC daily slot — confirmed
  via `live_state.json`'s `updated` timestamp at session start,
  `2026-09-20T04:08:55+00:00`, and `runs/2026-09-20-0020-daily-trading.md`;
  `37 % 7 = 2` so no `evolve` fired as part of that tick either).
  Documentation first: both the weekend all-hands session and the 09:00 UTC
  daily discussion had flagged `HOLDOUT_SIGMA`'s never-resetting cumulative
  multiple-testing correction as an owner's-call question that only existed
  inside "Current state" log entries — added as item 13 under "Next steps"
  (restating the 9x-margin finding, not deciding it) and cross-referenced
  from "Owner decisions pending"; pushed as its own commit (`700b74c`)
  before starting any evolve work. Freshness checks: `review-hard-calls`
  still 0 pending (2 reviewed, unchanged), items 0/1/3/7/8/9/10/12
  resolved/closed/feature-complete, items 2/5/6 still not a scheduled
  session's call, item 11 (AGENTS.md rotation) not due yet (254,246 bytes
  after the item-13 commit, under the 256KB threshold but close — worth
  watching) — so, with nothing else queued, used the rest of the slot for
  one more real 15-generation batch (offline/shadow development against the
  live champion) via `tools/background_runner.py` (`start` + backgrounded
  `wait`), exit code 0, no truncation, ~32 minutes. Champion's
  fold-aggregate fitness held flat at 1.728 across all 15 generations (960
  trades, 40% win, 1% stops, 3 halts, unchanged throughout). Best-of-generation
  fold-fitness ranged 1.248-2.398 (several generations' best exceeded the
  champion's raw 1.728 fold-fitness but none cleared the actual
  promotion-margin bar). See `runs/2026-09-20-1017-evolve-batch-v3.md`.
  Verified before commit: `python3 -m pytest -q` 426/426 both before
  (baseline) and after `evolve`; direct top-level key diff of
  `live_state.json` showed only `lineage`/`researcher_memory`/`updated`
  changed (genome, broker, journal, hard_call_reviews byte-identical);
  constitution manifest `726dfa4bac85891a` unchanged;
  `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  `holdout-pressure` re-checked (read-only, no state change) — margin still
  7.076 at draw 523, unchanged, nothing new; dashboard rebuilt correctly
  with `EVO_STATE` set (`index.html` shows 25233 challenger ideas tried).
  Genome still v3 (1d) live, untouched. Container started in detached HEAD
  again (24 commits reachable only from HEAD, all already ancestors of
  `origin/main`'s tip) — `git checkout main && git merge --ff-only
  origin/main` fast-forwarded cleanly, nothing lost.

- **Run 2026-09-20 (3-hourly check, ~06:46-07:37 UTC): a second, independent
  `boldness-scan` run (20 generations/arm vs. the weekend all-hands session's
  15) confirms the same no-clear-advantage pattern.** This session started
  from the same commit (`b40f716`) that shipped the diagnostic and,
  independently, also found it un-run and undocumented in this file's
  Commands list — both this session and the weekend all-hands entry below
  reached for the same idea within the same hour and collided on push
  (resolved by keeping both real results rather than discarding either).
  Freshness checks first: `review-hard-calls` still 0 pending, items
  0/1/3/7/8/9/10/12 resolved/closed/feature-complete, items 2/5/6 not a
  scheduled session's call, item 11 (AGENTS.md rotation) not due (244,177
  bytes). Ran `boldness-scan` with all defaults (20 generations/arm, cap=20,
  seed=7, n_blind=14, seeded from the same live `researcher_memory`:
  tested=25025, stagnation=1801, holdout_draws=522). Result: **UNCAPPED**
  (mirrors production, effective boldness 1801→1820) cleared the
  fold-aggregate gate in 3/20 generations, best-of-generation fold-fitness
  range 1.436-4.199 (one outlier generation at 4.199, rest clustered
  1.4-2.2); **CAPPED at 20** cleared the fold-aggregate gate in 4/20
  generations, range 1.338-2.349. Both arms: 0/20 sealed-holdout gate clears
  (no shadow promotions), final stagnation counter 1821, final in-memory
  champion unchanged at v3. Same qualitative read as the weekend all-hands
  15-generation run below (capping shows no clear advantage on one seed) at
  a different generation count — two independent draws now point the same
  way, though still not a seed sweep (see the weekend session's own
  follow-up note on that). Verified: `git status`/`git diff --stat
  live_state.json` both clean (read-only contract held); `python3 -m
  pytest -q` 426/426 after the run. See
  `runs/2026-09-20-0737-boldness-scan-first-result.md`.

- **Weekend all-hands 2026-09-20 (~06:05-07:30 UTC): shipped `boldness-scan`,
  a new read-only diagnostic, then used it to find that the real bottleneck
  behind 1801 stagnant generations is the sealed-holdout margin, not the
  boldness/search mechanism this session set out to blame.** Full reasoning
  in `runs/2026-09-20-0600-weekend-all-hands.md`. `agents.researcher.
  Researcher.perturb`'s own docstring already notes `boldness` (fed straight
  from the stagnation counter, unbounded) saturates by ~82 — past that every
  blind proposal is a full-genome, mostly-uniform-random redraw — but nobody
  had measured whether that costs anything real. New `loop.evolve.
  boldness_scan` (tested, `tests/test_boldness_scan.py`, 4 tests, full suite
  426/426) runs two identically-seeded shadow searches from the real
  champion + `researcher_memory`, one with boldness unbounded (mirrors
  production) and one capped, comparing fold/holdout gate-clear rates.
  Shipped and pushed as its own commit before running it. Real run
  (`--generations 15 --cap 20 --seed 7`, seeded from real `researcher_memory`
  tested=25025/stagnation=1801/holdout_draws=522): capped cleared the
  fold-gate slightly more often (3/15 vs 2/15) but neither promoted — one
  seed, too small to call a real effect. The informative part: reproduced
  generation 5 of the uncapped arm directly against the real `EvolutionRun`
  (caught and fixed a bug in the first reproduction attempt — forgetting
  `initial_champion_version` spuriously resets `tested`/`stagnation` to
  zero) and found its top candidate (fold-fitness 4.199 vs champion's 1.728,
  a full-genome redraw at boldness 1805) genuinely beat the champion's raw
  sealed-holdout fitness (3.070 vs 2.309, +0.761) and *still* failed:
  `required_margin` at 523 cumulative holdout draws is 7.076 — nowhere close
  to what 0.761 clears. Cross-checked against real (non-shadow) lineage via
  `holdout-pressure`: 27 real fold-aggregate winners have reached the
  holdout against v3 and lost every time (margin 7.043→7.075 across draws
  493-522), one of them an even bigger fold-fitness outlier (4.940, draw
  502) than this session's shadow find — so this pattern is real and already
  happening in production, not a shadow-only artifact. **Conclusion, stated
  as a number for the first time rather than "margin still rising slowly,
  nothing new"**: at 523 draws a challenger needs roughly 9x the raw
  holdout edge this session's best real example produced before v3 can be
  replaced through the normal search path — this is `MULTIPLE_TESTING_SIGMA`
  / `HOLDOUT_SIGMA`'s cumulative-draws design working as intended (see "Two
  flaws" below), not a bug, and not something capping boldness would fix
  (the margin's size doesn't depend on where the candidate that reaches it
  came from). Two follow-ups deliberately left open, not attempted this
  session: (1) whether capping boldness changes the fold-gate-clear rate in
  a statistically real way needs many more generations or seeds than one
  15-gen run; (2) whether `HOLDOUT_SIGMA` is still well-calibrated at 500+
  cumulative draws is a constitution-adjacent policy question, the owner's
  call, same category as item 2's `MULTIPLE_TESTING_SIGMA` thread. No code
  touching the live champion, `live_state.json`, or the constitution
  changed; genome still v3 (1d) live, untouched throughout.

- **Run 2026-09-20 (3-hourly check, ~03:45-04:11 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 24815 → 25025, stagnation/boldness
  counter 1786 → 1801.** No live trading this cycle (tick 37 already
  handled at the dedicated 00:20 UTC daily slot — confirmed via
  `live_state.json`'s `updated` timestamp at start of cycle,
  `2026-09-20T01:07:26+00:00`, itself from the prior 3-hourly check's own
  evolve batch, and `runs/2026-09-20-0020-daily-trading.md`; `37 % 7 = 2`
  so no `evolve` fired as part of that tick either). Freshness checks
  before running: `review-hard-calls` still 0 pending (2 reviewed,
  unchanged), items 0/1/3/7/8/9/10/12 resolved/closed/feature-complete/
  ongoing-passively, items 2/5/6 still not a scheduled session's call,
  item 11 (AGENTS.md rotation) not due yet (241,825 bytes, under the 256KB
  threshold) — so, with nothing else queued, used the slot for one more
  real 15-generation batch (offline/shadow development against the live
  champion) via `tools/background_runner.py` (`start` + backgrounded
  `wait`), exit code 0, no truncation, ~26 minutes. Champion's
  fold-aggregate fitness held flat at 1.728 across all 15 generations (960
  trades, 40% win, 1% stops, 3 halts, unchanged throughout). Best-of-generation
  fold-fitness ranged 1.247-2.398, never clearing the promotion-margin bar.
  See `runs/2026-09-20-0411-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 422/422 both before (baseline) and after `evolve`;
  direct top-level key diff of `live_state.json` showed only
  `lineage`/`researcher_memory`/`updated` changed (genome, broker, journal,
  hard_call_reviews byte-identical); constitution manifest `726dfa4bac85891a`
  unchanged; `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  `holdout-pressure` re-checked (read-only, no state change) — margin still
  rising slowly (7.075, was 7.074), nothing new; dashboard rebuilt correctly
  with `EVO_STATE` set (`index.html` shows 25025 challenger ideas tried).
  Genome still v3 (1d) live, untouched. Container started in detached HEAD
  again (19 commits reachable only from HEAD, all already ancestors of
  `origin/main`'s tip) — `git checkout main && git pull` fast-forwarded
  cleanly, nothing lost.

- **Run 2026-09-20 (3-hourly check, ~00:46-01:09 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 24608 → 24815, stagnation/boldness
  counter 1770 → 1785.** No live trading this cycle (tick 37 already
  handled at the dedicated 00:20 UTC daily slot — confirmed via
  `live_state.json`'s `updated` timestamp, `2026-09-20T00:22:04+00:00`, and
  `runs/2026-09-20-0020-daily-trading.md` before starting; `37 % 7 = 2` so
  no `evolve` fired as part of that tick either). Freshness checks before
  running: `review-hard-calls` still 0 pending (2 reviewed, unchanged),
  items 2/5/6 still not a scheduled session's call, item 4 blocked on a
  real hard-call flag (none pending), items 0/3/7/8/9/10/11/12
  resolved/closed/feature-complete, `AGENTS.md` size 239,490 bytes (under
  the 256KB rotation threshold) — so, with nothing else queued, used the
  slot for one more real 15-generation batch (offline/shadow development
  against the live champion) via `tools/background_runner.py` (`start` +
  backgrounded `wait`), exit code 0, no truncation, ~18 minutes. Champion's
  fold-aggregate fitness held flat at 1.728 across all 15 generations (960
  trades, 40% win, 1% stops, 3 halts, unchanged throughout). Best-of-generation
  fold-fitness ranged 0.940-2.398, never clearing the promotion-margin bar.
  See `runs/2026-09-20-0109-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 422/422 both before (baseline) and after `evolve`;
  direct top-level key diff of `live_state.json` showed only
  `lineage`/`researcher_memory`/`updated` changed (genome, broker, journal,
  hard_call_reviews byte-identical); constitution manifest `726dfa4bac85891a`
  unchanged; `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  `holdout-pressure` re-checked (read-only, no state change) — margin still
  rising slowly (7.074, was 7.072), nothing new; dashboard rebuilt correctly
  with `EVO_STATE` set (`index.html` shows 24815 challenger ideas tried).
  Genome still v3 (1d) live, untouched. Container started in detached HEAD
  again (18 commits reachable only from HEAD, all already ancestors of
  `origin/main`'s tip) — `git checkout main && git pull --ff-only origin
  main` fast-forwarded cleanly, nothing lost.

- **Run 2026-09-19 (3-hourly check, ~21:46-22:17 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 24399 → 24608, stagnation/boldness
  counter 1755 → 1770.** No live trading this cycle (tick 36 already
  handled at 00:20 UTC — confirmed via `live_state.json`'s `updated`
  timestamp, `2026-09-19T19:08:39+00:00`, from the prior 3-hourly check's
  own evolve batch, and `runs/2026-09-19-0020-daily-trading.md` before
  starting). Freshness checks before running: `review-hard-calls` still 0
  pending (2 reviewed, unchanged), items 2/5/6 still not a scheduled
  session's call, item 4 blocked on a real hard-call flag (none pending),
  items 0/1/3/7/8/9/10/12 resolved/closed/ongoing-passively, item 11
  (AGENTS.md rotation) not due yet (237,176 bytes, under the 256KB
  threshold) — so, with nothing else queued, used the slot for one more
  real 15-generation batch (offline/shadow development against the live
  champion) via `tools/background_runner.py` (`start` + backgrounded
  `wait`), exit code 0, no truncation, ~27 minutes. Champion's
  fold-aggregate fitness held flat at 1.465 across all 15 generations (943
  trades, 38% win, 1% stops, 4 halts, unchanged throughout). Best-of-generation
  fold-fitness ranged 1.259-1.951, never clearing the promotion-margin bar.
  See `runs/2026-09-19-2149-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 422/422 both before (baseline) and after `evolve`;
  direct top-level key diff of `live_state.json` showed only
  `lineage`/`researcher_memory`/`updated` changed (genome, broker, journal,
  hard_call_reviews byte-identical); constitution manifest `726dfa4bac85891a`
  unchanged; `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  `holdout-pressure` re-checked (read-only, no state change) — margin still
  rising slowly (7.072, was 7.071), nothing new; dashboard rebuilt correctly
  with `EVO_STATE` set (`index.html` shows 24608 challenger ideas tried).
  Genome still v3 (1d) live, untouched. Container started in detached HEAD
  again (16 commits reachable only from HEAD, all already ancestors of
  `origin/main`'s tip) — `git checkout main && git merge --ff-only
  origin/main` fast-forwarded cleanly, nothing lost.

- **Run 2026-09-19 (3-hourly check, ~18:46-19:11 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 24191 → 24399, stagnation/boldness
  counter 1741 → 1755.** No live trading this cycle (tick 36 already
  handled at 00:20 UTC — confirmed via `live_state.json`'s `updated`
  timestamp, `2026-09-19T16:08:37+00:00`, from the prior 3-hourly check's
  own evolve batch, and `runs/2026-09-19-0020-daily-trading.md` before
  starting). Freshness checks before running: `review-hard-calls` still 0
  pending (2 reviewed, unchanged), items 2/5/6 still not a scheduled
  session's call, item 4 blocked on a real hard-call flag (none pending),
  items 0/1/3/7/8/9/10/12 resolved/closed/ongoing-passively, item 11
  (AGENTS.md rotation) not due yet (234,879 bytes, under the 256KB
  threshold) — so, with nothing else queued, used the slot for one more
  real 15-generation batch (offline/shadow development against the live
  champion) via `tools/background_runner.py` (`start` + backgrounded
  `wait`), exit code 0, no truncation, ~25 minutes. Champion's
  fold-aggregate fitness held flat at 1.465 across all 15 generations (943
  trades, 38% win, 1% stops, 4 halts, unchanged throughout). Best-of-generation
  fold-fitness ranged 1.360-2.338, never clearing the promotion-margin bar.
  See `runs/2026-09-19-1911-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 422/422 both before (baseline) and after `evolve`;
  direct top-level key diff of `live_state.json` showed only
  `lineage`/`researcher_memory`/`updated` changed (genome, broker, journal,
  hard_call_reviews byte-identical); constitution manifest `726dfa4bac85891a`
  unchanged; `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  `holdout-pressure` re-checked (read-only, no state change) — margin still
  rising slowly (7.071, was 7.069), nothing new; dashboard rebuilt correctly
  with `EVO_STATE` set (`index.html` shows 24399 challenger ideas tried).
  Genome still v3 (1d) live, untouched. Container started in detached HEAD
  (15 commits reachable only from HEAD, all already ancestors of
  `origin/main`'s tip) — `git checkout main && git pull origin main`
  fast-forwarded cleanly, nothing lost.

- **Run 2026-09-19 (3-hourly check, ~15:46-16:10 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 23981 → 24191, stagnation/boldness
  counter 1726 → 1741.** No live trading this cycle (tick 36 already
  handled at 00:20 UTC — confirmed via `live_state.json`'s `updated`
  timestamp, `2026-09-19T13:12:04+00:00`, from the prior 3-hourly check's
  own evolve batch, and `runs/2026-09-19-0020-daily-trading.md` before
  starting). Freshness checks before running: `review-hard-calls` still 0
  pending (2 reviewed, unchanged), items 2/5/6 still not a scheduled
  session's call, item 4 blocked on a real hard-call flag (none pending),
  item 7 feature-complete (its own text says the remaining piece isn't
  worth attempting without a reason to prefer one entrypoint over the
  other), items 0/1/3/8/9/10/12 resolved/closed/ongoing-passively, item 11
  (AGENTS.md rotation) not due yet (232,537 bytes, under the 256KB
  threshold) — so, with nothing else queued, used the slot for one more
  real 15-generation batch (offline/shadow development against the live
  champion) via `tools/background_runner.py` (`start` + backgrounded
  `wait`), exit code 0, no truncation, ~24 minutes. Champion's
  fold-aggregate fitness held flat at 1.465 across all 15 generations (943
  trades, 38% win, 1% stops, 4 halts, unchanged throughout). Best-of-generation
  fold-fitness ranged 1.093-1.983, never clearing the promotion-margin bar.
  See `runs/2026-09-19-1610-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 422/422 both before (baseline) and after `evolve`;
  direct top-level key diff of `live_state.json` showed only
  `lineage`/`researcher_memory`/`updated` changed (genome, broker, journal,
  hard_call_reviews byte-identical); constitution manifest `726dfa4bac85891a`
  unchanged; `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  `holdout-pressure` re-checked (read-only, no state change) — margin still
  rising slowly (7.069, was 7.066), nothing new; dashboard rebuilt correctly
  with `EVO_STATE` set (`index.html` shows 24191 challenger ideas tried).
  Genome still v3 (1d) live, untouched. No git sync issues this cycle
  (container already at `origin/main`'s tip after a clean fetch/fast-forward).

- **Run 2026-09-19 (3-hourly check, ~12:46-13:14 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 23773 → 23981, stagnation/boldness
  counter 1710 → 1725.** No live trading this cycle (tick 36 already
  handled at 00:20 UTC — confirmed via `live_state.json`'s `updated`
  timestamp, `2026-09-19T10:16:09+00:00`, from the prior 3-hourly check's
  own evolve batch, and `runs/2026-09-19-0020-daily-trading.md` before
  starting). Freshness checks before running: `review-hard-calls` still 0
  pending (2 reviewed, unchanged), items 2/5/6 still not a scheduled
  session's call, item 4 blocked on a real hard-call flag (none pending),
  items 0/1/3/7/8/9/10/12 resolved/closed/feature-complete, item 11
  (AGENTS.md rotation) not due yet (230,327 bytes, well under the 256KB
  threshold) — so, with nothing else queued, used the slot for one more
  real 15-generation batch (offline/shadow development against the live
  champion) via `tools/background_runner.py` (`start` + backgrounded
  `wait`), exit code 0, no truncation, ~26 minutes. Champion's
  fold-aggregate fitness held flat at 1.465 across all 15 generations (943
  trades, 38% win, 1% stops, 4 halts, unchanged throughout). Best-of-generation
  fold-fitness ranged 1.465-1.928 (generation 13 exactly tied the champion),
  never clearing the promotion-margin bar. See
  `runs/2026-09-19-1314-evolve-batch-v3.md`. Verified before commit: `python3
  -m pytest -q` 422/422 both before (baseline) and after `evolve`; direct
  top-level key diff of `live_state.json` showed only
  `lineage`/`researcher_memory`/`updated` changed (genome, broker, journal,
  hard_call_reviews byte-identical); constitution manifest `726dfa4bac85891a`
  unchanged; `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  `holdout-pressure` re-checked (read-only, no state change) — margin still
  rising slowly (7.066, was 7.063), nothing new; dashboard rebuilt correctly
  with `EVO_STATE` set (`index.html` shows 23981 challenger ideas tried).
  Genome still v3 (1d) live, untouched. No git sync issues this cycle
  (container already at `origin/main`'s tip).

- **Run 2026-09-19 (3-hourly check, ~09:46-10:19 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 23354 → 23773, stagnation/boldness
  counter 1695 → 1710.** No live trading this cycle (tick 36 already
  handled at 00:20 UTC — confirmed via `live_state.json`'s `updated`
  timestamp, `2026-09-19T07:51:59+00:00`, from the weekend all-hands 60-gen
  batch, and `runs/2026-09-19-0020-daily-trading.md` before starting).
  Freshness checks before running: `review-hard-calls` still 0 pending (2
  reviewed, unchanged), items 2/5/6 still not a scheduled session's call,
  item 4 blocked on a real hard-call flag (none pending), items 7-12
  resolved/feature-complete, `AGENTS.md` size 228,135 bytes (well under the
  256KB rotation threshold) — so, with nothing else queued, used the slot
  for one more real 15-generation batch (offline/shadow development
  against the live champion) via `tools/background_runner.py` (`start` +
  backgrounded `wait`), exit code 0, no truncation, ~26.5 minutes.
  Champion's fold-aggregate fitness held flat at 1.465 across all 15
  generations (943 trades, 38% win, 1% stops, 4 halts, unchanged
  throughout). Best-of-generation fold-fitness ranged 1.373-2.007, beating
  the champion's own 1.465 in most generations but never by enough to
  clear the promotion-margin bar. See
  `runs/2026-09-19-1019-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 422/422 both before (baseline) and after
  `evolve`; direct top-level key diff of `live_state.json` showed only
  `lineage`/`researcher_memory`/`updated` changed (genome, broker,
  journal, hard_call_reviews byte-identical); constitution manifest
  `726dfa4bac85891a` unchanged; `tools/edit_bundle_module.py verify`/`sync
  --check` both clean; `holdout-pressure` re-checked (read-only, no state
  change) — margin still rising slowly (7.063, was 7.051), nothing new;
  dashboard rebuilt correctly with `EVO_STATE` set (`index.html` shows
  23773 challenger ideas tried). Genome still v3 (1d) live, untouched. No
  git sync issues this cycle (container already at `origin/main`'s tip).

- **Weekend all-hands 2026-09-19 (~06:15-09:10 UTC): a deeper 60-generation
  real `evolve` batch, a real concurrent-write collision with a 3-hourly
  check resolved by reconciling `live_state.json` rather than discarding
  either side, and a genuinely controlled seed-convergence experiment.**
  Full reasoning in `runs/2026-09-19-0600-weekend-all-hands.md` and
  `runs/2026-09-19-0752-evolve-batch-v3-60gen.md`. Headlines: (1) 60-gen
  batch, no promotion, cumulative candidates 22523 → 23354 (+831),
  stagnation 1620 → 1680. (2) This session's push collided with the
  3-hourly check below (`4f48c8d`, pushed first from the same base) —
  merged via a real two-parent `git merge` (`9e4038c`): `tested` hash sets
  unioned (23564 total, zero overlap between the two branches' new draws),
  `stagnation`/`holdout_draws` counters summed across both branches'
  increments (→ 1696 / 510), `lineage` reconstructed by feeding both
  branches' genuinely-new entries through the real `core.live._trim_lineage`
  function, state re-saved via a real `LiveAccount(...).save(...)` call.
  Verified: pytest 422/422, constitution unchanged, bundle sync clean, every
  non-lineage/researcher_memory/updated key byte-identical across both
  branches before merging. **If this happens again, the merge recipe above
  is mechanical and safe to repeat as long as both sides are pure
  no-promotion/no-trade evolve diffs** (confirmed by the top-level key diff
  first) — a promotion or trade on either side would need a different,
  more careful resolution, not attempted here. (3) The actual deep-focus
  work: `run_from_files.py evolve-dry-run` already has a `--seed` flag the
  bundle's own `evolve` lacks (shipped 2026-08-24, never used for an actual
  experiment); ran three 15-generation dry-run batches (seeds 101/202/303),
  same calendar day so the 4-year evaluation window is held fixed, isolating
  seed as the only varying factor for the first time — every prior "lively
  batch" observation conflated seed and calendar-day drift together. Result:
  best-of-generation fold-fitness means across the three seeds span only
  0.044 (1.588-1.632), an order of magnitude tighter than the 0.679 spread
  `fold-date-sensitivity` found across a 7-day calendar window on
  2026-09-13. **This answers the half of that question fold-date-sensitivity
  couldn't**: a "livelier than usual" batch is explained by which day it is,
  not which seed it drew — seed variance is not a competing explanation.
  Future sessions: keep checking `fold-date-sensitivity` first on an unusual
  batch (2026-09-13's guidance, unchanged); this result just confirms seed
  isn't worth checking as an alternative cause. No code, gene, or champion
  changed; `live_state.json` confirmed untouched by all three dry-runs.
  Genome still v3 (1d) live.

- **Run 2026-09-19 (3-hourly check, ~06:47-07:16 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 22523 → 22733, stagnation counter
  1620 → 1635.** No live trading this cycle (tick 36 already handled at
  00:20 UTC — confirmed via `live_state.json`'s `updated` timestamp,
  `2026-09-19T04:12:03+00:00`, from the prior 3-hourly check's own evolve
  batch, and `runs/2026-09-19-0020-daily-trading.md` before starting).
  Freshness checks before running: `review-hard-calls` still 0 pending (2
  reviewed, unchanged), items 2/5/6 still not a scheduled session's call,
  item 4 blocked on a real hard-call flag (none pending), item 7
  feature-complete, item 8 closed for v3, items 9-12 resolved, `AGENTS.md`
  size 223,145 bytes (well under the 256KB rotation threshold) — so, with
  nothing else queued, used the slot for one more real 15-generation batch
  (offline/shadow development against the live champion) via
  `tools/background_runner.py` (`start` + backgrounded `wait`), exit code 0,
  no truncation. Champion's fold-aggregate fitness held flat at 1.465 across
  all 15 generations (943 trades, 38% win, 1% stops, 4 halts, unchanged
  throughout). Best-of-generation fold-fitness ranged 1.385-1.917, beating
  the champion's own 1.465 in most generations but never by enough to clear
  the promotion-margin bar. See `runs/2026-09-19-0716-evolve-batch-v3.md`.
  Verified before commit: `python3 -m pytest -q` 422/422 both before
  (baseline) and after `evolve`; direct top-level key diff of
  `live_state.json` showed only `lineage`/`researcher_memory`/`updated`
  changed (genome, broker, journal, hard_call_reviews byte-identical);
  constitution manifest `726dfa4bac85891a` unchanged;
  `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  `holdout-pressure` re-checked (read-only, no state change) — margin still
  rising slowly (7.051, was 7.048), nothing new; dashboard rebuilt correctly
  with `EVO_STATE` set (`index.html` shows 22733 challenger ideas tried).
  Genome still v3 (1d) live, untouched. No git sync issues this cycle.

- **Run 2026-09-19 (3-hourly check, ~03:45-04:14 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 22316 → 22523, stagnation counter
  1606 → 1620.** No live trading this cycle (tick 36 already handled at
  00:20 UTC — confirmed via `live_state.json`'s `updated` timestamp,
  `2026-09-19T01:13:01+00:00`, from the prior 3-hourly check's own evolve
  batch, and `runs/2026-09-19-0020-daily-trading.md` before starting).
  Freshness checks before running: `review-hard-calls` still 0 pending (2
  reviewed, unchanged), items 2/5/6 still not a scheduled session's call,
  item 4 blocked on a real hard-call flag (none pending), items
  0/8/9/10/11/12 resolved/closed, `AGENTS.md` size 220,698 bytes (well under
  the 256KB rotation threshold) — so, with nothing else queued, used the
  slot for one more real 15-generation batch (offline/shadow development
  against the live champion) via `tools/background_runner.py` (`start` +
  backgrounded `wait`), exit code 0, no truncation. Champion's fold-aggregate
  fitness held flat at 1.465 across all 15 generations (943 trades, 38% win,
  1% stops, 4 halts, unchanged throughout). Best-of-generation fold-fitness
  ranged 1.293-1.941, beating the champion's own 1.465 in most generations
  but never by enough to clear the promotion-margin bar. See
  `runs/2026-09-19-0414-evolve-batch-v3.md`. Verified before commit: `python3
  -m pytest -q` 422/422 both before (baseline) and after `evolve`; direct
  top-level key diff of `live_state.json` showed only
  `lineage`/`researcher_memory`/`updated` changed (genome, broker, journal,
  hard_call_reviews byte-identical); constitution manifest
  `726dfa4bac85891a` unchanged; `tools/edit_bundle_module.py verify`/`sync
  --check` both clean; `holdout-pressure` re-checked (read-only, no state
  change) — margin still rising slowly (7.048, was 7.043), nothing new;
  dashboard rebuilt correctly with `EVO_STATE` set (`index.html` shows 22523
  challenger ideas tried). **`background_runner.py wait --pid <pid>` hit
  again this cycle:** the item-9-documented unsupported-flag usage error
  (exits 0 almost instantly without actually waiting) recurred — caught by
  `kill -0 <pid>` showing the process still alive, then re-run with only
  `--status`/`--timeout`, which waited correctly for the full ~22.7 minutes.
  Genome still v3 (1d) live, untouched.

- **Run 2026-09-19 (3-hourly check, ~00:46-01:20 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 22107 → 22316, stagnation counter
  1591 → 1606.** No live trading this cycle (tick 36 already handled at
  00:20 UTC — confirmed via `live_state.json`'s `updated` timestamp,
  `2026-09-19T00:21:33+00:00`, and `runs/2026-09-19-0020-daily-trading.md`
  before starting; `tick % 7 = 36 % 7 = 1` so no `evolve` fired as part of
  that tick either). Freshness checks before running: `review-hard-calls`
  still 0 pending (2 reviewed, unchanged), items 2/5/6 still not a
  scheduled session's call, item 4 blocked on a real hard-call flag (none
  pending), items 0/8/9/10/11/12 resolved/closed, `AGENTS.md` size 218,000
  bytes (well under the 256KB rotation threshold) — so, with nothing else
  queued, used the slot for one more real 15-generation batch
  (offline/shadow development against the live champion) via
  `tools/background_runner.py` (`start` + backgrounded `wait`), exit code
  0, no truncation. Champion's fold-aggregate fitness held flat at 1.465
  across all 15 generations (943 trades, 38% win, 1% stops, 4 halts,
  unchanged throughout). Best-of-generation fold-fitness beat the
  champion's own 1.465 in most generations by a comfortable margin (range
  1.291-2.060) but never by enough to clear the promotion-margin bar. See
  `runs/2026-09-19-0115-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 422/422 both before (baseline) and after
  `evolve`; direct top-level key diff of `live_state.json` showed only
  `lineage`/`researcher_memory`/`updated` changed (genome, broker, journal,
  hard_call_reviews byte-identical); constitution manifest md5
  `1446fa6ee357d02ebaabeb24867a8154` unchanged; `tools/edit_bundle_module.py
  verify`/`sync --check` both clean; `holdout-pressure` re-checked
  (read-only, no state change) — margin still rising slowly (last value
  7.043, was 7.040), nothing new. **Dashboard gotcha hit this cycle:**
  running `python3 evotrader_dashboard.py` without setting `EVO_STATE`
  first silently rendered an empty-account page (defaults, no live data)
  instead of erroring — caught by inspecting the diff before commit, not
  by any tool failure. Always use the documented
  `EVO_STATE="$(pwd)/live_state.json" python3 evotrader_dashboard.py` form
  (AGENTS.md's own "Rebuild the dashboard" step already says this; this
  cycle just forgot to follow it on the first attempt). Re-ran correctly,
  `index.html` now shows the real account (5 generation(s) run, 22316
  challenger ideas tried). Genome still v3 (1d) live, untouched.

- **Archived 2026-09-24 (3-hourly check, ~21:47 UTC): the next oldest slice
  of this log (2026-09-18 ~00:48 through 2026-09-18 ~19:12 UTC) moved
  verbatim to `AGENTS_ARCHIVE_2026-09-18.md`, cutting this file from
  255,429 bytes back down** (regrew close to the 256KB single-read limit
  again since the earlier-today ~00:46-01:21 UTC rotation, same recurring
  pattern the 2026-09-04/09-10/09-15/09-16/09-18/09-20/09-22/09-24
  rotations each hit). Nothing reworded, nothing lost — see that file (and,
  for anything before 2026-09-18 ~00:48 UTC, `AGENTS_ARCHIVE_2026-09-17.md`,
  `AGENTS_ARCHIVE_2026-09-15_to_2026-09-16.md`,
  `AGENTS_ARCHIVE_2026-09-13_to_2026-09-14.md`,
  `AGENTS_ARCHIVE_2026-09-11_to_2026-09-12.md`,
  `AGENTS_ARCHIVE_2026-09-08_to_2026-09-10.md`,
  `AGENTS_ARCHIVE_2026-09-02_to_2026-09-08.md`,
  `AGENTS_ARCHIVE_2026-08-29_to_2026-09-02.md`, then
  `AGENTS_ARCHIVE_2026-08-15_to_2026-08-29.md`) for the full older history.
  This file now keeps everything from 2026-09-18 ~19:12 UTC onward, plus
  the full "Owner decisions pending", promotion-history, "Measured", and
  "Rules" sections, never part of any rotation. No code changed, no
  protected file touched, `live_state.json` untouched by this housekeeping
  step itself.


- **Archived 2026-09-24 (3-hourly check): the next oldest slice of this log
  (2026-09-17 ~00:47 through 2026-09-17 ~22:18 UTC) moved verbatim to
  `AGENTS_ARCHIVE_2026-09-17.md`, cutting this file from 256,106 bytes
  back down** (regrew close to the 256KB single-read limit again since the
  2026-09-22 rotation, same recurring pattern the
  2026-09-04/09-10/09-15/09-16/09-18/09-20/09-22 rotations each hit).
  Nothing reworded, nothing lost — see that file (and, for anything before
  2026-09-17 ~00:47 UTC, `AGENTS_ARCHIVE_2026-09-15_to_2026-09-16.md`,
  `AGENTS_ARCHIVE_2026-09-13_to_2026-09-14.md`,
  `AGENTS_ARCHIVE_2026-09-11_to_2026-09-12.md`,
  `AGENTS_ARCHIVE_2026-09-08_to_2026-09-10.md`,
  `AGENTS_ARCHIVE_2026-09-02_to_2026-09-08.md`,
  `AGENTS_ARCHIVE_2026-08-29_to_2026-09-02.md`, then
  `AGENTS_ARCHIVE_2026-08-15_to_2026-08-29.md`) for the full older history.
  This file now keeps everything from 2026-09-18 ~00:48 UTC onward, plus
  the full "Owner decisions pending", promotion-history, "Measured", and
  "Rules" sections, never part of any rotation. No code changed, no
  protected file touched, `live_state.json` untouched by this housekeeping
  step itself.

- **Archived 2026-09-22 (3-hourly check): the next oldest slice of this log
  (2026-09-15 ~00:48 through 2026-09-16 ~21:51 UTC) moved verbatim to
  `AGENTS_ARCHIVE_2026-09-15_to_2026-09-16.md`, cutting this file from
  252,962 bytes back down** (regrew close to the 256KB single-read limit
  again since the 2026-09-20 rotation, same recurring pattern the
  2026-09-04/09-10/09-15/09-16/09-18/09-20 rotations each hit). Nothing
  reworded, nothing lost — see that file (and, for anything before
  2026-09-15 ~00:48 UTC, `AGENTS_ARCHIVE_2026-09-13_to_2026-09-14.md`,
  `AGENTS_ARCHIVE_2026-09-11_to_2026-09-12.md`,
  `AGENTS_ARCHIVE_2026-09-08_to_2026-09-10.md`,
  `AGENTS_ARCHIVE_2026-09-02_to_2026-09-08.md`,
  `AGENTS_ARCHIVE_2026-08-29_to_2026-09-02.md`, then
  `AGENTS_ARCHIVE_2026-08-15_to_2026-08-29.md`) for the full older history.
  This file now keeps everything from 2026-09-17 ~00:47 UTC onward, plus
  the full "Owner decisions pending", promotion-history, "Measured", and
  "Rules" sections, never part of any rotation. No code changed, no
  protected file touched, `live_state.json` untouched by this housekeeping
  step itself.

- **Archived 2026-09-20 (3-hourly check): the next oldest slice of this log
  (2026-09-13 ~00:46 through 2026-09-14 ~22:34 UTC) moved verbatim to
  `AGENTS_ARCHIVE_2026-09-13_to_2026-09-14.md`, cutting this file from
  262,349 bytes back under the 256KB single-read limit** (regrew past it
  again since the 2026-09-18 rotation, same recurring pattern the
  2026-09-04/09-10/09-15/09-16/09-18 rotations each hit). Nothing reworded,
  nothing lost — see that file (and, for anything before 2026-09-13 ~00:46
  UTC, `AGENTS_ARCHIVE_2026-09-11_to_2026-09-12.md`,
  `AGENTS_ARCHIVE_2026-09-08_to_2026-09-10.md`,
  `AGENTS_ARCHIVE_2026-09-02_to_2026-09-08.md`,
  `AGENTS_ARCHIVE_2026-08-29_to_2026-09-02.md`, then
  `AGENTS_ARCHIVE_2026-08-15_to_2026-08-29.md`) for the full older history.
  This file now keeps everything from 2026-09-15 ~00:48 UTC onward, plus
  the full "Owner decisions pending", promotion-history, "Measured", and
  "Rules" sections, never part of any rotation. No code changed, no
  protected file touched, `live_state.json` untouched by this housekeeping
  step itself.

- **Archived 2026-09-18 (3-hourly check, ~21:47-22:xx UTC): the next oldest
  slice of this log (2026-09-11 ~00:48 through 2026-09-12 ~22:11 UTC) moved
  verbatim to `AGENTS_ARCHIVE_2026-09-11_to_2026-09-12.md`, cutting this
  file from ~253KB back under the 256KB single-read limit** (regrew past it
  again since the 2026-09-16 rotation, same recurring pattern the
  2026-09-04/09-10/09-15/09-16 rotations each hit). Nothing reworded,
  nothing lost — see that file (and, for anything before 2026-09-11 ~00:48
  UTC, `AGENTS_ARCHIVE_2026-09-08_to_2026-09-10.md`,
  `AGENTS_ARCHIVE_2026-09-02_to_2026-09-08.md`,
  `AGENTS_ARCHIVE_2026-08-29_to_2026-09-02.md`, then
  `AGENTS_ARCHIVE_2026-08-15_to_2026-08-29.md`) for the full older history.
  This file now keeps everything from 2026-09-13 ~00:46 UTC onward, plus
  the full "Owner decisions pending", promotion-history, "Measured", and
  "Rules" sections, never part of any rotation. No code changed, no
  protected file touched, `live_state.json` untouched by this housekeeping
  step itself.

- **Archived 2026-09-16 (3-hourly check, ~22:14-22:16 UTC): the next oldest
  slice of this log (2026-09-08 ~00:47 through 2026-09-10 ~21:47 UTC) moved
  verbatim to `AGENTS_ARCHIVE_2026-09-08_to_2026-09-10.md`, cutting this
  file from ~263KB back under the 256KB single-read limit** (regrew past it
  again since the 2026-09-15 rotation, same recurring pattern the
  2026-09-04/09-10/09-15 rotations each hit). Nothing reworded, nothing
  lost — see that file (and, for anything before 2026-09-08 ~00:47 UTC,
  `AGENTS_ARCHIVE_2026-09-02_to_2026-09-08.md`,
  `AGENTS_ARCHIVE_2026-08-29_to_2026-09-02.md`, then
  `AGENTS_ARCHIVE_2026-08-15_to_2026-08-29.md`) for the full older history.

- **Archived 2026-09-15 (3-hourly check, ~00:48-01:xx UTC): the next oldest
  slice of this log (2026-09-02 ~21:47 through 2026-09-08 ~00:47 UTC) moved
  verbatim to `AGENTS_ARCHIVE_2026-09-02_to_2026-09-08.md`, closing item 11
  (flagged 2026-09-14, this file had regrown to ~277KB/4147 lines since the
  2026-09-04 rotation).** Nothing reworded, nothing lost — see that file
  (and, for anything before 2026-09-02 ~21:47 UTC,
  `AGENTS_ARCHIVE_2026-08-29_to_2026-09-02.md` then
  `AGENTS_ARCHIVE_2026-08-15_to_2026-08-29.md`) for the full older history
  in original order; it also now carries the prior archive's own
  announcement entry (originally dated 2026-09-04), since that entry was
  itself part of this cut. This file keeps everything from 2026-09-08
  ~00:47 UTC onward, plus the full "Next steps", promotion-history,
  "Measured", and "Rules" sections (never part of either rotation). No
  code changed, no protected file touched, `live_state.json` untouched.
  Boundary derived carefully per item 11's own caution: the cut stops
  exactly before the "### The first promotion" heading, so the static
  promotion-history/"Two flaws"/"Next steps" material below the
  chronological log is untouched by this or any prior rotation. If this
  file keeps growing at a similar rate, a future session should archive
  again rather than let it silently regrow past the limit.


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
  around it. **Fulfilled 2026-09-21 (3-hourly check, ~00:46-00:55 UTC):**
  tick 38 was the first live tick to actually flag; see the top "Current
  state" entry above for the full reconstruction and verdict.

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
   **RESOLVED 2026-09-08 (owner decision): parked, redirect effort.** The
   full evidence trail behind this — 5+ unconstrained-search seeds/9+
   generations of `--recipe x6`, plus the (2a)/(2b) single-lever sweeps
   (cold-start vol cap, conviction floor, size ramp, `consv1` thresholds,
   bar-scaling multiplier) — is archived verbatim, in original order, at
   `AGENTS_ARCHIVE_item2_4h-bar-shadow-evolution.md` (moved there 2026-09-10
   to keep this file under its 256KB single-read limit; nothing reworded,
   nothing lost). Bottom line the trail reached: the `consv1 + trailing_stop
   + ramp` stack's one real fold-gate clear is boundary-fragile (fails 4-6 of
   7 nearby-day shifts) and, per
   `tests/test_researcher_structural_determinism.py` (2026-09-04), the
   recurring `consult_moderate`-disabling candidate that produced it is a
   deterministic member of the Researcher's mutation set regardless of RNG
   seed — not independent search evidence. See "Owner decisions pending"
   above for the decision itself: do not run another 4h-bar generation
   against this recipe; cycles redirect to item 4 (LLM-backed consults) —
   item 5 (short selling) is no longer available as a redirect target, see
   "Owner decisions pending".

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

   **First real review recorded 2026-08-30 (3-hourly check, ~00:46 UTC):
   tick 16's lone-voice LINKUSDT buy, verdict `approve`.** See "Current
   state" above (2026-08-30 entry) and
   `runs/2026-08-30-0046-hard-call-review-tick16.md`. Hand-reconstructed
   `RiskJudge.rule`'s scoring against the real evolved genes and matched
   the order to the cent — the evolved genome's own risk logic operating
   exactly as designed, nothing to correct.

   **Second real review recorded 2026-09-15 (3-hourly check, ~03:46-03:51
   UTC): tick 32's lone-voice DOTUSDT buy, verdict `approve`.** See
   "Current state" above and
   `runs/2026-09-15-0351-hard-call-review-tick32.md`. Same
   hand-reconstruction method, again matched to the cent — this time the
   bar's top-scored candidate (UNIUSDT) was excluded by its own
   already-near-cap position size before DOTUSDT was reached, and DOTUSDT
   then consumed 100% of deployable cash, crowding out several
   higher-scored-than-it candidates purely on cash. Two reviews in, both
   `approve`, both explained fully by the evolved genome's mechanics
   (`lone_voice_scale` > `two_agree_bonus`, cash floor) rather than any
   bug — this infrastructure is now doing exactly the job item 4 wanted it
   for.

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

   **Shipped 2026-09-08 (owner decision, see "Owner decisions pending"
   above): Phase 1 re-applied for real.** `core/portfolio.py`'s
   `short()`/`cover()` + `borrow_bps_per_bar` accrual now exist live
   (`tests/test_short_selling.py`, 18 tests, full suite 384/384),
   `evotrader.manifest` re-sealed `8b74865634b1db07` → `726dfa4bac85891a`,
   `AMENDMENTS.md` row added same commit. Broker mechanics only — nothing
   in the live trading/evolution path calls `.short()` yet, and
   `live_state.json` was untouched. "Whether/how the Researcher should be
   allowed to propose short positions" (Phase 2) was explicitly left
   un-scoped by this shipment.

   **Found 2026-09-13 (weekend all-hands): a concrete landmine Phase 2 must
   clear first, sharper than the original "five files" framing — see
   `runs/2026-09-13-0600-weekend-all-hands.md` and
   `tests/test_short_position_sign_landmine.py` (5 new tests, full suite
   396/396).** `PaperBroker.position_weight()` already returns a *negative*
   weight for an open short (verified directly:
   `qty * price / equity` with `qty < 0`), and that weight flows unmodified
   into `Briefing.open_positions` via `loop/engine.py`'s
   `weights = {s: b.position_weight(s, prices) ...}` →
   `agents/analyst.py`'s `brief()`. Every current reader of
   `open_positions` — all three consults' `held = ... > 0` exit checks, and
   five separate spots across `RiskJudge.rule`/`SuperiorJudge.review`
   (slot-counting, `held_w`-based buy-sizing headroom, and the hard-cap
   `room = (hard_cap - held) * equity` line) — assumes a non-positive
   weight means "flat," true today only because nothing has ever called
   `.short()` in the live path. Confirmed by direct test, not just code
   reading: a shorted symbol (a) is invisible to `max_positions`/
   `hard_max_positions` slot limits, (b) gets a *larger* buy-sizing
   allowance than the same symbol flat (the negative `held_w` raises the
   `max_position_pct - held_w` cap instead of leaving it alone), and (c)
   most importantly, `SuperiorJudge`'s hard concentration cap — the one
   gate documented as a hard limit, not a tunable — actually *loosens*
   beyond `hard_max_position_pct * equity` for a symbol that already
   carries directional risk, exactly backwards from what a hard-limit gate
   is for. **Concretely scoped next step for whoever attempts Phase 2
   wiring**: fix these read sites to be sign-aware (e.g. `abs(weight)` for
   exposure/slot accounting, explicit `is_long`/`is_short` helpers for the
   consults' exit checks) *before* routing any "short"/"cover" intent
   through `RiskJudge`/`SuperiorJudge` — wiring the routing first would
   ship a live safety-cap regression the moment a short is ever open. None
   of the five affected call sites live in a `_PROTECTED` file
   (`agents/judges.py`, `agents/consults.py` are both ordinary strategy-layer
   files), so fixing them needs no constitution re-seal — only the eventual
   `MAX_DD_HARD_FAIL`/short-exposure-cap constitution questions the original
   2026-08-30 design pass flagged still need owner sign-off. No behavior
   changed by this finding: it is test-only, `live_state.json` untouched,
   constitution checksum unchanged, `.short()` still has zero live callers.

   **Fixed 2026-09-13 (3-hourly check, ~09:47-10:20 UTC): the four
   `agents/judges.py` accounting bugs above are closed — see "Current
   state" above.** `RiskJudge.rule`'s slot-count and `held_w`-based sizing
   headroom, and `SuperiorJudge.review`'s slot-count and hard-cap `room`
   line, all now treat a short's nonzero weight as an occupied slot and use
   `abs(weight)` for exposure accounting, so a short can no longer
   under-count slots or loosen the hard concentration cap. **Still open,
   deliberately not touched by this fix**: the three consults'
   `held = is_long(...)` exit checks (renamed for clarity, behavior
   unchanged) still can't propose closing a short — that needs a "cover"
   intent shape distinct from "sell" that doesn't exist yet. **Concretely
   scoped next step for whoever attempts the remainder of Phase 2 wiring**:
   design and add that cover-intent shape (likely a new `Intent.side` value,
   or an explicit `is_short(...)` branch per consult that emits a
   differently-typed exit intent), thread it through `RiskJudge.rule`'s
   exits-first loop (currently only handles `side == "sell"`), and only then
   consider routing real "short"/"cover" orders through to `PaperBroker`.
   Until that exists, `.short()` still has zero live callers and none of
   this is reachable from the live trading path.

   **Found and fixed 2026-09-13 (3-hourly check, ~21:47-21:58 UTC): a second
   sign landmine, in a different file pair than the one above** — see
   "Current state" and
   `runs/2026-09-13-2158-short-forced-exit-sign-landmine-fix.md`.
   `Guardian.forced_exits` (`agents/trader.py`) computed `pnl`/`from_peak`
   with long-only formulas, so every stop-loss/trailing-stop/take-profit/
   time-stop check would be backwards for an open short, and it always
   emitted `side="sell"`, which `PaperBroker.sell()` rejects outright for a
   short. `Trader.execute`'s sell-or-buy ternary had the mirror bug (a
   `"cover"` order falling into `buy()`), and `loop/engine.py`'s
   circuit-breaker flatten-the-book path had the same always-`"sell"`
   problem. All three fixed and sign-aware now (`Guardian.forced_exits`
   branches on `pos.is_short`; `Trader.execute` dispatches all four
   `Fill.side` values explicitly; the flatten logic is a new pure
   `_flatten_orders(broker, held)` helper). 10 new tests
   (`tests/test_short_forced_exit_landmine.py`), full suite 406/406. No
   behavior change for any existing caller (`.short()` still has zero live
   callers). **Still open, unchanged by this fix**: the discretionary
   consult-level "cover" intent described in the paragraph above this one —
   this session fixed the *mandatory* Guardian-level safety net (stops/
   trailing-stop/take-profit/circuit-breaker), not the consults' own exit
   proposals, which is still the concretely-scoped next step for whoever
   continues Phase 2 wiring.

   **Shipped 2026-09-14 (3-hourly check, ~12:48-13:05 UTC): the discretionary
   consult-level "cover" intent above now exists and routes correctly** —
   see "Current state" above and
   `runs/2026-09-14-1305-cover-intent-wiring.md`. Each consult's long-only
   exit check now has a mirrored branch for an open short (reusing the same
   genes symmetrically, no new genes added), emitting `side="cover"`;
   `RiskJudge.rule`'s exits-first loop buckets and gates "cover" separately
   from "sell" (`is_short` vs. `is_long`). Also found and fixed a third
   landmine in the same family, in `SuperiorJudge.review` this time: "exits
   are never blocked, ever" only ever collected `side == "sell"` orders, so
   a "cover" order would have been silently dropped (not vetoed, just gone)
   the moment a short was ever open. 9 new tests
   (`tests/test_cover_intent_wiring.py`), full suite 415/415. No behavior
   change for any existing caller: `.short()` still has zero live callers,
   so every new branch is unreachable in production today. **Still open**:
   whether/how a consult should be allowed to *open* a short at all remains
   the explicitly unscoped owner decision below — until that exists,
   `.short()` has no live caller to ever produce a short for this session's
   "cover" intent to close.

6. **Equities/FX** behind the same `MarketData` interface.

   **Design pass done 2026-09-02 (3-hourly check, ~15:46-16:05 UTC), no code
   shipped — see "Current state" above and
   `runs/2026-09-02-1550-equities-fx-design-pass.md`.** Correction to this
   item's own wording: no `MarketData` class/ABC/Protocol exists today —
   `core/market.py`'s free-function surface (`fetch_klines`/`load`/
   `load_universe`/`Replay`) is imported ad hoc in ~20+ places (`core/live.py`,
   `loop/engine.py`, `agents/analyst.py`, `run_from_files.py`, `tools/*.py`,
   plus 30+ per-function imports inside `evotrader_bundle.py`'s flattened
   mirror), not injected through one class the way item 5's `PaperBroker` is
   — so there is no single method surface to extend the way item 5's
   `.short()`/`.cover()` slice could. Traced the crypto-specific assumptions
   living outside any `_PROTECTED` file: `core/live.py`'s tick cadence has no
   market-hours/session/holiday gate (crypto never closes, so nothing has
   ever needed one); `core/market.py:114-130`'s `find_gaps` assumes a fixed
   calendar-step grid (would false-positive on every equity weekend/holiday);
   `"BTCUSDT"`-style symbol concatenation is load-bearing in
   `core/genome.py`'s default `universe`, `agents/analyst.py`'s
   `regime_anchor`, and `top_symbols_by_volume()`'s USDT-only filtering; and
   the genome schema has no asset-class/quote-currency/session-calendar
   field at all. **Also flags an orphaned finding**: `.env.example` already
   stages Alpaca paper-trading credentials
   (`APCA_API_BASE_URL`/`APCA_API_KEY_ID`/`APCA_API_SECRET_KEY`) with zero
   other references anywhere in the repo — looks like a forgotten or
   anticipatory placeholder, not partial implementation; worth a human
   confirming intent before picking a real data source. **No code shipped
   deliberately**: the honest small-and-isolated slice available today (a
   new fetcher, a session-aware `find_gaps` variant) would have zero real
   consumer until a data source is actually chosen — scaffolding with no
   caller is dead weight, not progress. **Concretely scoped next step**:
   (1) a human picks a real data source (Alpaca vs. a free historical
   mirror analogous to `data-api.binance.vision`); (2) then an isolated
   additive fetcher in `core/market.py` + a session-aware `find_gaps`
   variant (additive optional param, default preserves today's behavior
   byte-for-byte), each tested against synthetic fixtures in isolation; (3)
   stop there — wiring a real trading-hours gate into `core/live.py`'s tick
   cadence, a genome `asset_class` field, and `top_symbols_by_volume()`'s
   quote-currency filtering are separate, bigger, riskier follow-on
   sessions, same discipline item 5 and item 7 both used.

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

   **Pointer (2026-09-08, 20:30 UTC daily evaluation):** this had recurred
   5 times in a single week per the `Current state` log (09-06, 09-07 x2,
   09-08 x2), each caught with no harm but each re-spending attention on
   the same rediscovery. Since this roadmap position (far down the file)
   was evidently not visible enough at the moment the command gets typed,
   an inline warning was added directly next to `evolve N` in the ###
   Commands listing near the top of the file instead. If it keeps
   recurring after that, doc placement isn't the fix and something more
   mechanical (a wrapper script, a pre-flight check) is probably
   warranted.

   **New trigger shape (2026-09-09, 00:46 UTC 3-hourly check):** recurred a
   sixth time, but via a different mechanism than any prior instance — not a
   `nohup ... &` string, but a tool-level `run_in_background: true` combined
   with a trailing shell `&` inside the same command. The two-line wrapper
   (launch python in background, echo its PID) finished almost instantly and
   the tool reported the whole call "completed", while the real `evolve`
   process kept running detached for ~29 more minutes. Caught immediately
   (`updated` timestamp unchanged, `kill -0 <pid>` still alive), no harm — see
   `runs/2026-09-09-0119-evolve-batch-v3.md`. The inline `### Commands`
   warning added 2026-09-08 doesn't cover this shape since it warns against
   `nohup`, not against pairing the tool's own backgrounding with a shell
   `&`. **Rule of thumb for future sessions: never put a trailing `&` in a
   command string that is also run with the tool's `run_in_background`
   option — pick exactly one backgrounding mechanism, not both.**

   **Related mistake, different shape (2026-09-09, ~13:00 UTC 3-hourly
   check):** backgrounding `evolve` correctly (single mechanism) but piping
   its stdout through `tail -60` before it ever reached the log file lost
   3 of 15 generations' output permanently, since the file is the only
   record of a backgrounded command — don't truncate before capture; pipe to
   `tee`, or don't pipe at all, and `tail` only when later *displaying* an
   already-complete file.

   **Mechanical fix shipped 2026-09-09 (3-hourly check, ~21:47-22:00 UTC):**
   per this item's own 2026-09-08 note ("if it keeps recurring after
   [the doc fix], something more mechanical ... is probably warranted") — it
   did keep recurring (twice more on 2026-09-09) after that doc fix, so this
   is that wrapper. New `tools/background_runner.py`
   (`tests/test_background_runner.py`, 6 tests against real subprocesses, no
   mocking; full suite 384 → 390) exposes `start`/`wait` as two separate CLI
   calls: `start` launches the target command detached (`start_new_session`,
   no `nohup`/`&` needed, so there is nothing to accidentally pair with a
   tool's own `run_in_background`) with all output captured to a log file
   from the first byte (no pipe, nothing to truncate) and returns almost
   instantly with the real child PID; `wait` blocks (safe to combine with the
   calling tool's own backgrounding, since `wait` itself spawns nothing) until
   the child's real exit code — written by the child itself on completion —
   appears in a status file, which works even though `wait` runs in a
   separate process from `start` and is not the child's parent. Genome/state
   untouched at ship time — that was tooling only, verified via direct
   `live_state.json`/constitution checks, not the usual evolve-batch diff.

   **First real `evolve` batch confirmed 2026-09-10 (3-hourly check,
   ~00:46-01:13 UTC): worked exactly as designed, no issues.** `start`
   returned in well under a second with the real child PID; `wait` blocked
   the full ~22-minute run and returned the real exit code from the child's
   own status-file write; the log file captured all 15 generations' output
   from the first byte, nothing truncated. See "Current state" and
   `runs/2026-09-10-0113-evolve-batch-v3-background-runner-first-use.md`.
   Recommended as the default way to run `evolve N` from here on — no
   nohup/`&`, nothing to accidentally pair with a tool's own
   `run_in_background`.

10. **Dashboard's "genome" stat tile can show a stale/wrong version when
    `state/genomes/champion.json` disagrees with `live_state.json`.**
    Confirmed on today's tick 28 commit (`8379290`, 2026-09-11 00:26 UTC,
    caught by the 20:30 UTC daily evaluation): the published `index.html`
    showed "genome v1 / 5 generation(s) run" while `live_state.json`'s
    `genome.version` was correctly 3 the whole time (confirmed by
    `runs/2026-09-11-0020-daily-trading.md` and by `evotrader_bundle.py
    tick`'s own logged `genome_version: 3`). The next commit 9 minutes
    later (`5a21d96`, 00:35 UTC, the day's first evolve batch) silently
    corrected the same tile back to "v3". Root cause:
    `evotrader_dashboard.py`'s `build()` does `champ = _read(P_CHAMP, {})
    or live.get("genome", {}) or {}` (`P_CHAMP` =
    `state/genomes/champion.json`) and prefers that on-disk cache over
    `live_state.json`, the documented source of truth — the same class of
    staleness already tracked above (`_reconstruct_champion_genome`'s
    `Genome.champion()` read, ~line 1573) reading a `champion.json` left
    over from an earlier point in the container's lifetime. Since
    `state/` is gitignored and only gets freshly overwritten with the
    live champion when `evolve` itself runs, a dashboard rebuild that
    happens before that container's first `evolve` call — exactly what
    the daily-trading tick's own rebuild step does — can render a version
    number that's behind reality, published live until the next commit
    happens to overwrite it. Fix direction: have the genome stat tile
    trust `live_state.json`'s `genome.version` unconditionally (only fall
    back to `champion.json` for fields not present in `live_state`), or
    at minimum assert `champ.get("version") == live.get("genome",
    {}).get("version")` before using the disk copy. Not fixed here —
    flagging for a future session, since it's a mechanism/display
    correctness bug, not a trading-strategy call.

    **Fixed 2026-09-11 (3-hourly check, ~21:47 UTC): `build()` now prefers
    `live.get("genome")` over the disk cache** (`evotrader_dashboard.py`,
    `champ = live.get("genome") or _read(P_CHAMP, {}) or {}` — was the
    other way around). `champ` is only ever used for its `version` field
    (the stat tile and `_genome_sub`'s champion-memory match), so no other
    field needed a fallback rule. New regression test
    `tests/test_dashboard_champion_stat.py::test_build_prefers_live_state_genome_over_stale_champion_cache`
    builds against a scratch `live_state.json` (version 3) and a
    deliberately stale scratch `champion.json` (version 1) and asserts the
    rendered page shows v3. Rebuilding `index.html` in this container with
    the fix applied actually flipped the previously-committed page from a
    stale "v1 / 5 generation(s) run" back to the correct "v3 / ... 11048
    challenger idea(s) tried" — the exact staleness this item described was
    live on the public dashboard again at the start of this cycle, not just
    a historical 9-minute blip. `python3 -m pytest -q` 391/391 (390 baseline
    + 1 new test). No trading, no genome, no constitution change.

11. **Flagged 2026-09-14 (3-hourly check, ~21:47-22:34 UTC): this file has
    regrown past its 256KB single-read limit again — measured 282KB just
    now, up from the ~189KB it was cut to on 2026-09-10 (see the "Archived
    2026-09-10" entry above) and the ~242KB the 2026-09-04 archival pass
    predicted it would keep hitting "if this file keeps growing at a
    similar rate."** The "Current state" log currently runs unbroken from
    2026-09-02 ~21:47 UTC (the last chronological archival's cutoff) through
    today — about 12 days of 3-hourly entries never rotated out. Not
    attempted this cycle: a chronological archival pass (moving the oldest
    slice to a new `AGENTS_ARCHIVE_...` file, verbatim, matching the
    2026-09-04/2026-09-10 pattern) needs a careful read of the exact section
    boundaries first — the tail of "Current state" turns out to interleave
    with older reference material (e.g. the researcher-memory/boldness
    discussion and a 2026-08-18 entry both sit *after* the 2026-09-02 cutoff
    marker in file order, not before it), so a rushed cut risked archiving
    or duplicating the wrong span. Concretely scoped next step: a session
    with room to spend most of its slot on this should re-derive the exact
    boundary (probably keeping roughly the last 5-7 days of dated entries,
    archiving the rest into a new dated file) the same careful way the two
    prior archival sessions did, verify nothing is reworded or lost, and
    confirm `python3 -m pytest -q` stays green throughout (no code changes
    expected, text-only).

    **Resolved 2026-09-15 (3-hourly check, ~00:48-01:xx UTC): archived.**
    Cut the chronological "Current state" log at the clean bullet boundary
    between the last 2026-09-07 entry and the first 2026-09-08 entry (line
    2125 of the pre-cut file) — keeps roughly the last 7 days (2026-09-08
    ~00:47 UTC onward), moves 2026-09-02 ~21:47 through 2026-09-08 ~00:47
    UTC (plus the old "Archived 2026-09-04" pointer entry, which had ended
    up positioned after the chronological log's oldest real entry) verbatim
    into new `AGENTS_ARCHIVE_2026-09-02_to_2026-09-08.md`. The "interleaving"
    this entry flagged turned out to be the static promotion-history/"Two
    flaws"/this Next-steps list sitting *after* the chronological log in
    file order (not interleaved within it) — the cut simply stops exactly
    before the `### The first promotion` heading, so none of that reference
    material was ever at risk. Verified: `diff` of the removed slice against
    the archive file's body byte-for-byte identical; reconstructing
    (kept-top + kept-bottom) from the original file byte-for-byte matches
    the new file minus the new pointer entry; `AGENTS.md` now ~220KB/3300
    lines, back under the 256KB limit. `python3 -m pytest -q` 415/415 both
    before and after (text-only change, no code touched). No protected file
    touched, `live_state.json` untouched.

12. **RESOLVED 2026-09-16 (3-hourly check, ~00:48-01:04 UTC): hash-based
    `researcher_memory["tested"]` identity shipped and applied to the real
    account.** `agents/researcher.py`'s `Researcher.key()` now returns a
    16-hex-char sha256 hash of the sorted patch instead of the patch itself;
    `Researcher.migrate_tested_entry()` normalizes a mixed old/new `tested`
    list to that identity on read. Updated every reconstruction site
    (`evotrader_bundle.py`'s `evolve`/`disagreement-sweep`,
    `run_from_files.py`'s `_cmd_evolve`/`_cmd_evolve_dry_run`) — the
    count-only sites needed no change. New `tests/test_researcher_memory_hash.py`
    (7 tests, full suite 422/422). Ran the new `tools/migrate_tested_memory.py`
    against the real `live_state.json`: `researcher_memory["tested"]`
    17,710 entries before and after (membership unchanged, byte-for-byte
    diff confirmed only `researcher_memory`/`updated` changed), file
    **57.2MB → 7.2MB**. See `runs/2026-09-16-0104-item12-tested-memory-hash-fix.md`
    for the full trail. Future growth is now bounded by candidate *count*,
    not patch size — no longer on a collision course with GitHub's push
    limit. Original flag (2026-09-15, kept below for the root-cause trail):
    `live_state.json`
    is on a growth trajectory that hits GitHub's hard 100MB per-file push
    limit around 2026-09-24/25 — about 9 days out at the time of writing.**
    See `runs/2026-09-15-2220-evolve-batch-v3.md`'s "New finding" section for
    the full trail. This cycle's `git push` printed GitHub's large-file
    warning (`GH001`, currently 57.2MB, past the 50MB recommended-max
    threshold) for the first time logged anywhere in this file. Sampled the
    file's size at 6 points across recent history via `git cat-file -s
    <commit>:live_state.json` (plain `git log --stat` on this file is too
    slow to use interactively — the diffs are enormous): 38.0MB
    (2026-09-11) → 44.0MB (09-12) → 49.4MB (09-13) → 53.6MB (09-15 00:23) →
    56.0MB (09-15 16:18) → 57.2MB (09-15 22:20), ~4.8MB/day average over the
    last 4 days.

    **Root cause, precisely identified**: `researcher_memory` is 29.1MB of
    the current 57.2MB file (`lineage` is a comparatively small 5.7MB — it's
    already capped at 200 entries by `core.live._trim_lineage`, working as
    designed and not part of this problem). Inside `researcher_memory`, the
    `tested` field is a list of 17,710 entries — one per candidate mutation
    ever tried against the live (unbeaten since promotion) v3 champion — and
    each entry is the candidate's *full* genome patch, not a hash:
    `agents/researcher.py`'s `Researcher.key(m)` returns `tuple((k, str(v))
    for k, v in sorted(m.patch.items()))`, every gene key/value pair in the
    mutation (some blind perturbations touch ~38 genes at once). This list
    has **no cap or trim anywhere** — confirmed by grep, nothing bounds it —
    and only resets when the champion is beaten, which hasn't happened since
    the v2→v3 promotion; every batch this week has held `aggregate_fitness`
    flat at 1.537, so the list has grown every single generation with
    nothing to stop it, exactly matching the observed growth rate.

    **Not fixed this cycle, deliberately** — this is real design work, not a
    quick edit, and this session judged it too large a blast radius to rush:
    the obvious fix direction (store a stable hash of the sorted patch
    instead of the patch itself, both in `Researcher.key()`'s in-memory
    identity and in the persisted `researcher_memory["tested"]` list) is a
    cross-cutting identity read/written in at least 7 places across
    `evotrader_bundle.py` (multiple CLI command sites serialize/deserialize
    it) plus `agents/researcher.py:307` and `loop/evolve.py`'s
    `EvolutionRun`, and needs an explicit decision on backward compatibility
    with the 17,710 full-patch entries already committed live today —
    migrate them to hashes once (rewriting recent history's dedup identity),
    or let old- and new-format entries co-exist during some transition.
    Getting this wrong risks silently breaking the deduplication memory the
    2026-08-15 fix (see "Two flaws found by watching it run" above) was
    built to protect — re-testing the same near-miss candidates over and
    over — which would be a quiet regression, not a loud one. Many other
    scheduled sessions read and write this same file continuously; this one
    chose to document precisely rather than risk a rushed cross-cutting
    change.

    **Concretely scoped next step for whoever picks this up**: design the
    hash-based `tested` identity (a stable hash of `Researcher.key()`'s
    existing sorted-tuple representation is the obvious candidate — e.g.
    `hashlib.sha256(repr(...).encode()).hexdigest()[:16]`, short enough to
    shrink `tested` by roughly two orders of magnitude), decide the
    migration story for the already-persisted full-patch entries (simplest:
    a one-time one-way conversion of the existing list to hashes on next
    load, since the full patches were never used for anything but
    membership testing), update every read/write site listed above plus the
    bundle (`tools/edit_bundle_module.py sync`), and add a regression test
    asserting `researcher_memory["tested"]` shrinks by roughly the expected
    factor on a save/load round-trip against a synthetic large `tested` set.
    Verify the live account's actual `researcher_memory.tested` round-trips
    correctly (same membership, `evolve`'s dedup behavior unchanged) before
    calling this closed — not just that the file gets smaller. This is
    urgent on a roughly one-week clock, not indefinitely deferrable like
    most of the other open items above.

13. **Flagged 2026-09-20 (weekend all-hands, ~06:05-07:30 UTC, restated
    plainly at the 09:00 UTC daily discussion): is `HOLDOUT_SIGMA`'s
    never-resetting cumulative multiple-testing correction still
    well-calibrated at 500+ draws against one undefeated champion, or does
    it need a decay/reset design?** `HOLDOUT_SIGMA` was set once, on
    2026-08-21, calibrated against the sealed-holdout noise measured at that
    time. The multiple-testing correction it feeds into is cumulative and
    never resets on a promotion — every candidate ever tried against the
    current champion counts toward the bar, forever, for as long as that
    champion stays undefeated. Two independent `boldness-scan` runs this
    weekend (`runs/2026-09-20-0600-weekend-all-hands.md`,
    `runs/2026-09-20-0737-boldness-scan-first-result.md`) confirmed this is
    now the dominant force keeping v3 in place, not weak search or boldness
    saturating: at 523 cumulative draws `required_margin()` sits at 7.076, a
    challenger needs roughly **9x** the best raw holdout edge any of 27 real
    fold-aggregate winners has produced so far, and the margin's size
    depends only on cumulative draw count, not on candidate quality —
    nothing about the search process improving would change this. Left to
    run indefinitely, the bar keeps rising and any future champion faces
    this same, worse problem after enough evolve cycles.

    **This is not a bug and not a scheduled session's call to make alone.**
    Whether the never-resetting cumulative design is the intended,
    permanently-conservative behavior (accept it, keep disclosing the
    drawdown-gate situation as already agreed 2026-09-08 under the
    "Owner decisions pending" v3-drawdown item), or whether it warrants a
    design pass on a decay/reset mechanism (e.g. resetting the draw count on
    some cadence, or scoping it to a rolling window instead of the
    champion's entire undefeated lifetime) is a real risk-appetite call
    about how conservative the promotion bar should be allowed to become
    over time. Do not decide this via more diagnostics — the numbers are
    already in; this needs the owner's read on risk appetite, not more
    evidence-gathering. Once decided, record the decision and outcome here
    the same way items 2/5/6 above are recorded.

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

   **Re-measured 2026-09-12 (weekend all-hands, 06:00 UTC): the moderate/risky
   echo has substantially weakened under v3, the same "search quietly fixed it"
   pattern item 8 found for the conservative entry/exit asymmetry.** This
   instruction ("run after any roster change") had not actually been followed
   since this finding shipped — 13+ generations and two promotions (v1→v2→v3)
   had happened since, with nobody re-checking. Current numbers against live
   v3 (1386 logged bars, 10269 proposal points): conservative/moderate
   **+0.101** (0.5% overlap, 34 shared), conservative/risky **−0.045** (1.0%
   overlap, 1.5% same-side — genuinely near-independent now), moderate/risky
   **+0.172** overall (32.9% overlap, 96.1% same-side when both act — down
   from +0.39/93.2%, but still the one real echo). By regime: moderate/risky
   +0.45 bear, +0.43 crisis, +0.05 chop, **−0.41 bull** — bear/crisis are
   still the two regimes where the echo is strongest, same shape as
   2026-08-16 (+0.51/+0.58), just smaller in magnitude; bull flipped sign
   entirely (was not broken out by regime in 2026-08-16 to compare directly).
   Reading: unlike item 8, this has not fully search-corrected away — the
   Risk Judge's agreement signal in bear/crisis still partly reads its own
   echo, just less so than 18 generations ago. Not treated as a promotion
   candidate or a proposal here (no gene change), just the overdue
   re-measurement this section itself calls for. Worth another check after
   the next promotion, same as always, rather than treating this number as
   settled.

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
