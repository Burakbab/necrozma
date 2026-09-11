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

---

## Current state

- **Run 2026-09-11 (3-hourly check, ~18:47-19:14 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 10842 → 11048, boldness/stagnation
  counter 777 → 792.** No live trading this cycle (tick 28 already handled
  at 00:20 UTC, and this same 3-hourly slot's own earlier standing evolve
  batch already ran at ~15:46-16:33 UTC — confirmed via `live_state.json`'s
  `updated` timestamp and `runs/2026-09-11-0020-daily-trading.md`/
  `runs/2026-09-11-1633-evolve-batch-v3.md` before starting). Repo started
  in detached HEAD with local `main` stale at `4f15e68` (2026-09-04); both
  `git pull` and `git pull --rebase` failed with "Need to specify how to
  reconcile divergent branches" after `git checkout main` (the shallow
  clone's depth-limited history showed no merge-base against `origin/main`'s
  `6cb2e21`) — resolved with `git reset --hard origin/main` after confirming
  the detached HEAD tip already matched `origin/main` byte-for-byte, so
  nothing local was lost. Freshness checks before running: `review-hard-calls`
  still 0 pending (1 reviewed so far, unchanged), items 2/5/6 still not a
  scheduled session's call, item 4 still blocked on a real hard-call flag
  (none pending), item 7 feature-complete with nothing actionable pending a
  migration-policy decision — so the cycle ran the standing evolve batch via
  `tools/background_runner.py` (`start` + backgrounded `wait`), which again
  worked exactly as designed (~23.9-minute wait, real exit code 0, no
  truncation). Champion's fold-aggregate fitness held flat at 1.656 across
  all 15 generations. Raw best-of-generation fold-fitness beat the
  champion's own 1.656 in 8/15 generations, tied in 1, lost in 6 — a
  livelier batch than the last one but still ordinary. `holdout-pressure`
  draw count unchanged at 253 (no candidate cleared the fold-aggregate gate
  far enough to reach a sealed-holdout draw this batch). See
  `runs/2026-09-11-1914-evolve-batch-v3.md`. Verified before commit: `python3
  -m pytest -q` 390/390 both before (baseline) and after `evolve`; direct
  top-level key diff of `live_state.json` showed only
  `lineage`/`researcher_memory`/`updated` changed (genome, broker, journal
  byte-identical); constitution verified `726dfa4bac85891a` unchanged;
  `tools/edit_bundle_module.py verify`/`sync --check` both clean; dashboard
  rebuilt (`index.html`). Genome still v3 (1d) live, untouched.

- **Run 2026-09-11 (3-hourly check, ~15:46-16:33 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 10632 → 10842, boldness/stagnation
  counter 762 → 777.** No live trading this cycle (tick 28 already handled
  at 00:20 UTC, and this same 3-hourly slot's own earlier standing evolve
  batch already ran at ~12:46-13:14 UTC — confirmed via `live_state.json`'s
  `updated` timestamp and `runs/2026-09-11-0020-daily-trading.md`/
  `runs/2026-09-11-1313-evolve-batch-v3.md` before starting). Repo started
  in detached HEAD with local `main` stale at `4f15e68` (2026-09-04); `git
  pull` failed with "You are not currently on a branch" (expected — cloud
  clone starts detached); resolved with `git checkout main && git reset
  --hard origin/main` after confirming the detached HEAD tip already matched
  `origin/main` byte-for-byte, so nothing local was lost. Freshness checks
  before running: `review-hard-calls` still 0 pending (1 reviewed so far,
  unchanged), items 2/5/6 still not a scheduled session's call, item 4 still
  blocked on a real hard-call flag (none pending), item 7 feature-complete
  with nothing actionable pending a migration-policy decision — so the cycle
  ran the standing evolve batch via `tools/background_runner.py` (`start` +
  backgrounded `wait`), which again worked exactly as designed (~37.9-minute
  wait, real exit code 0, no truncation). Champion's fold-aggregate fitness
  held flat at 1.656 across all 15 generations. Raw best-of-generation
  fold-fitness beat the champion's own 1.656 in 2/15 generations, tied in 4,
  lost in 9 — a quieter batch than the last several but still ordinary.
  `holdout-pressure` draw count unchanged at 253 (no candidate cleared the
  fold-aggregate gate far enough to reach a sealed-holdout draw this batch).
  See `runs/2026-09-11-1633-evolve-batch-v3.md`. Verified before commit:
  `python3 -m pytest -q` 390/390 both before (baseline) and after `evolve`;
  direct top-level key diff of `live_state.json` showed only
  `lineage`/`researcher_memory`/`updated` changed (genome, broker, journal
  byte-identical); constitution verified `726dfa4bac85891a` unchanged;
  `tools/edit_bundle_module.py verify`/`sync --check` both clean; dashboard
  rebuilt (`index.html`). Genome still v3 (1d) live, untouched.

- **Run 2026-09-11 (3-hourly check, ~12:46-13:14 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 10425 → 10632, boldness/stagnation counter
  747 → 762.** No live trading this cycle (tick 28 already handled at 00:20
  UTC, and this same 3-hourly slot's own earlier standing evolve batch
  already ran at ~09:46-10:31 UTC — confirmed via `live_state.json`'s
  `updated` timestamp and `runs/2026-09-11-0020-daily-trading.md`/
  `runs/2026-09-11-1031-evolve-batch-v3.md` before starting). Repo started in
  detached HEAD with local `main` stale at `4f15e68` (2026-09-04); `git fetch`
  reported "forced update" and no merge-base was found even after checkout —
  resolved with `git reset --hard origin/main` on a clean tree (working tree
  had no uncommitted work, nothing local lost). Freshness checks before
  running: `review-hard-calls` still 0 pending (1 reviewed so far,
  unchanged), items 2/5/6 still not a scheduled session's call, item 4 still
  blocked on a real hard-call flag (none pending), item 7 feature-complete
  with nothing actionable pending a migration-policy decision — so the cycle
  ran the standing evolve batch via `tools/background_runner.py` (`start` +
  backgrounded `wait`), which again worked exactly as designed (~21.6-minute
  wait, real exit code 0, no truncation). Champion's fold-aggregate fitness
  held flat at 1.656 across all 15 generations. Raw best-of-generation
  fold-fitness beat the champion's own 1.656 in 8/15 generations, tied in 0,
  lost in 7 — an ordinary batch. `holdout-pressure` draw count 251 → 253,
  every one still lost, margin unchanged in shape (~6.6-6.65). See
  `runs/2026-09-11-1313-evolve-batch-v3.md`. Verified before commit: `python3
  -m pytest -q` 390/390 both before (baseline) and after `evolve`; direct
  top-level key diff of `live_state.json` showed only
  `lineage`/`researcher_memory`/`updated` changed (genome, broker, journal
  byte-identical); constitution verified `726dfa4bac85891a` unchanged;
  `tools/edit_bundle_module.py verify`/`sync --check` both clean; dashboard
  rebuilt (`index.html`). Genome still v3 (1d) live, untouched.

- **Run 2026-09-11 (3-hourly check, ~09:46-10:31 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 10219 → 10425, boldness/stagnation
  counter 732 → 747.** No live trading this cycle (tick 28 already handled
  at 00:20 UTC, and this same 3-hourly slot's own earlier standing evolve
  batch already ran at ~07:20 UTC — confirmed via `live_state.json`'s
  `updated` timestamp and
  `runs/2026-09-11-0020-daily-trading.md`/`runs/2026-09-11-0720-evolve-batch-v3.md`
  before starting). Repo started in detached HEAD with the detached tip
  already matching `origin/main`'s commit (`3404ab8`) — only the local
  `main` branch pointer was stale (last synced `4f15e68`, 2026-09-04);
  resolved with `git checkout -B main origin/main`, a plain fast-forward,
  nothing local lost. Freshness checks before running: `review-hard-calls`
  still 0 pending (1 reviewed so far, unchanged), the 09:00 UTC daily
  discussion confirmed no new owner-decision item and items 2/5/6 unchanged
  — so the cycle ran the standing evolve batch via
  `tools/background_runner.py` (`start` + backgrounded `wait`), which again
  worked exactly as designed. Champion's fold-aggregate fitness held flat at
  1.656 across all 15 generations. Raw best-of-generation fold-fitness beat
  the champion's own 1.656 in 8/15 generations, tied in 2, lost in 5 — an
  ordinary batch. `holdout-pressure` draw count 250 → 251, every one still
  lost, margin unchanged in shape (~6.65). See
  `runs/2026-09-11-1031-evolve-batch-v3.md`. Verified before commit: `python3
  -m pytest -q` 390/390 both before (baseline) and after `evolve`; direct
  top-level key diff of `live_state.json` showed only
  `lineage`/`researcher_memory`/`updated` changed (genome, broker, journal
  byte-identical); constitution verified `726dfa4bac85891a` unchanged;
  `tools/edit_bundle_module.py verify`/`sync --check` both clean; dashboard
  rebuilt (`index.html`). Genome still v3 (1d) live, untouched.

- **Run 2026-09-11 (3-hourly check, ~06:46-07:20 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 10009 → 10219, boldness/stagnation counter
  717 → 732.** No live trading this cycle (tick 28 already handled at 00:20
  UTC, and this same 3-hourly slot's own earlier standing evolve batch
  already ran at ~04:22 UTC — confirmed via `live_state.json`'s `updated`
  timestamp and `runs/2026-09-11-0020-daily-trading.md`/
  `runs/2026-09-11-0422-evolve-batch-v3.md` before starting). Repo started in
  detached HEAD with local `main` stale; `python3 tools/git_sync.py`
  unshallowed, found a real merge-base, and fast-forwarded cleanly — no
  habit lapse this time. Freshness checks before running: `review-hard-calls`
  still 0 pending (1 reviewed so far, unchanged), items 2/5/6 still not a
  scheduled session's call, item 4 still blocked on a real hard-call flag
  (none pending) — so the cycle ran the standing evolve batch via
  `tools/background_runner.py` (`start` + backgrounded `wait`), which again
  worked exactly as designed. Champion's fold-aggregate fitness held flat at
  1.656 across all 15 generations. Raw best-of-generation fold-fitness beat
  the champion's own 1.656 in 6/15 generations, tied in 3, lost in 6 — an
  ordinary batch. `holdout-pressure` draw count 249 → 250, every one still
  lost, margin unchanged in shape (~6.6). See
  `runs/2026-09-11-0720-evolve-batch-v3.md`. Verified before commit: `python3
  -m pytest -q` 390/390 both before (baseline) and after `evolve`; direct
  top-level key diff of `live_state.json` showed only
  `lineage`/`researcher_memory`/`updated` changed (genome, broker, journal
  byte-identical); constitution verified `726dfa4bac85891a` unchanged;
  `tools/edit_bundle_module.py verify`/`sync --check` both clean; dashboard
  rebuilt (`index.html`). Genome still v3 (1d) live, untouched.

- **Run 2026-09-11 (3-hourly check, ~03:48-04:22 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 9802 → 10009 (crossed 10,000),
  boldness/stagnation counter 703 → 717.** No live trading this cycle (tick
  28 already handled at 00:20 UTC, and this same 3-hourly slot's own earlier
  standing evolve batch already ran at ~01:18 UTC — confirmed via
  `live_state.json`'s `updated` timestamp and
  `runs/2026-09-11-0020-daily-trading.md`/`runs/2026-09-11-0118-evolve-batch-v3.md`
  before starting). Repo started in detached HEAD with local `main` stale at
  `4f15e68` (2026-09-04); fixed with `git checkout -B main origin/main`
  after confirming the detached HEAD tip already matched `origin/main`
  byte-for-byte — nothing local lost. Freshness checks before running:
  `review-hard-calls` still 0 pending (1 reviewed so far, unchanged), items
  2/5/6 still not a scheduled session's call, item 4 still blocked on a real
  hard-call flag (none pending) — so the cycle ran the standing evolve batch
  via `tools/background_runner.py` (`start` + backgrounded `wait`), which
  again worked exactly as designed. Champion's fold-aggregate fitness held
  flat at 1.656 across all 15 generations. Raw best-of-generation
  fold-fitness beat the champion's own 1.656 in 6/15 generations, tied in 1,
  lost in 8 — an ordinary batch. `holdout-pressure` draw count unchanged at
  249 (every one still lost, margin unchanged in shape ~6.6) since no
  candidate cleared the fold-aggregate gate this batch. See
  `runs/2026-09-11-0422-evolve-batch-v3.md`. Verified before commit: `python3
  -m pytest -q` 390/390 both before (baseline) and after `evolve`; direct
  top-level key diff of `live_state.json` showed only
  `lineage`/`researcher_memory`/`updated` changed (genome, broker, journal
  byte-identical); constitution verified `726dfa4bac85891a` unchanged;
  `tools/edit_bundle_module.py verify`/`sync --check` both clean; dashboard
  rebuilt (`index.html`). Genome still v3 (1d) live, untouched.

- **Run 2026-09-11 (3-hourly check, ~00:48-01:18 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 9593 → 9802, boldness/stagnation counter
  687 → 702.** No live trading this cycle (tick 28 already handled at 00:20
  UTC, confirmed via `live_state.json`'s `updated` timestamp and
  `runs/2026-09-11-0020-daily-trading.md`/`runs/2026-09-11-0030-evolve-batch-v3.md`
  before starting — that same-day evolve batch was the daily protocol's own
  3-generation shadow run, separate from this cycle's standing 15-generation
  batch). Repo started in detached HEAD with local `main` stale at `4f15e68`
  (2026-09-04); `python3 tools/git_sync.py` unshallowed, found a real
  merge-base, and fast-forwarded cleanly — no habit lapse this time.
  Freshness checks before running: `review-hard-calls` still 0 pending (1
  reviewed so far, unchanged), items 2/5/6 still not a scheduled session's
  call — so the cycle ran the standing evolve batch via
  `tools/background_runner.py` (`start` + backgrounded `wait`), which again
  worked exactly as designed. Champion's fold-aggregate fitness held flat at
  1.656 across all 15 generations. Raw best-of-generation fold-fitness beat
  the champion's own 1.656 in 6/15 generations, tied in 3, lost in 6 — an
  ordinary batch. `holdout-pressure` 248 → 249 draws, every one still lost,
  margin unchanged in shape (~6.6). See
  `runs/2026-09-11-0118-evolve-batch-v3.md`. Verified before commit: `python3
  -m pytest -q` 390/390 both before (baseline) and after `evolve`; direct
  top-level key diff of `live_state.json` showed only
  `lineage`/`researcher_memory`/`updated` changed (genome, broker, journal
  byte-identical); constitution verified `726dfa4bac85891a` unchanged;
  `tools/edit_bundle_module.py verify`/`sync --check` both clean; dashboard
  rebuilt (`index.html`). Genome still v3 (1d) live, untouched.

- **Run 2026-09-10 (3-hourly check, ~21:47-23:13 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 9344 → 9551, boldness/stagnation counter
  669 → 684.** No live trading this cycle (tick 27 already handled at 00:20
  UTC, confirmed via `live_state.json`'s `updated` timestamp and the 20:30
  UTC daily-evaluation note before starting). Repo started in detached HEAD
  with local `main` stale at `4f15e68` (2026-09-04) against `origin/main`'s
  `098066a`, no merge-base at default fetch depth; resolved with `git
  checkout main && git reset --hard origin/main` on a clean tree after
  confirming the detached HEAD already matched `origin/main`'s tip
  byte-for-byte — same recurring habit lapse many prior entries have
  flagged (`tools/git_sync.py` should be tried first), still not fixed.
  Freshness checks before running: `review-hard-calls` still 0 pending (1
  reviewed so far, unchanged), `holdout-pressure` 245 → 248 draws after this
  run (every one still lost, margin ~6.60-6.64, unchanged in shape), items
  2/5/6 still not a scheduled session's call — so the cycle ran the standing
  evolve batch via `tools/background_runner.py` (`start` + backgrounded
  `wait`), which again worked exactly as designed. Champion's fold-aggregate
  fitness held flat at 1.469 across all 15 generations. Raw
  best-of-generation fold-fitness beat the champion's own 1.469 in 9/15
  generations, lost in 6 — an ordinary batch. See
  `runs/2026-09-10-2313-evolve-batch-v3.md`. Verified before commit: `python3
  -m pytest -q` 390/390 both before (baseline) and after `evolve`; direct
  top-level key diff of `live_state.json` showed only
  `lineage`/`researcher_memory`/`updated` changed (genome, broker, journal
  byte-identical); constitution verified `726dfa4bac85891a` unchanged;
  `tools/edit_bundle_module.py verify`/`sync --check` both clean; dashboard
  rebuilt (`index.html`). Genome still v3 (1d) live, untouched.

- **Archived 2026-09-10 (3-hourly check, ~18:47-19:xx UTC): item 2's now-resolved
  4h-bar shadow-evolution pointer history moved to its own archive file, cutting
  this file from 264KB back to 189KB — it had grown past the 256KB single-read
  limit (this session's own opening `Read` on `AGENTS.md` failed with that exact
  error) even after the 2026-09-04 chronological-log rotation, because item 2's
  inline "Pointer" sub-history (76KB/1126 lines, 2026-09-01 through 2026-09-04)
  never rotated — it wasn't part of the chronological "Current state" log the
  prior two archival passes targeted, and the standing "full Next steps section,
  never part of either rotation" rule stopped making sense once item 2 was
  decided closed by the owner on 2026-09-08 (see "Owner decisions pending").**
  New `AGENTS_ARCHIVE_item2_4h-bar-shadow-evolution.md` holds the full history
  verbatim, unreworded, in original order (the same discipline the two prior
  chronological-log archives used). Item 2's entry in the Next-steps list below
  is now a short "RESOLVED" pointer to that file plus "Owner decisions pending"
  — same information, findable, just not spelled out inline. Checked no other
  Next-steps item has regrown similarly before stopping: item 7's history is
  ~14KB (verbose but not dominant) and item 9's is ~5KB, neither close to item
  2's former 76KB, so this was the one clear outlier, not a sign the whole
  section needs the same treatment yet. Pure documentation change — no code, no
  protected file, `live_state.json` byte-identical before/after (confirmed via
  `git status`/`git diff --stat` showing only `AGENTS.md` modified plus the new
  archive file), `python3 -m pytest -q` 390/390 (baseline, no code touched),
  constitution verified `726dfa4bac85891a` unchanged, genome still v3 (1d) live.
  No live trading this cycle (tick 27 already handled at 00:20 UTC, confirmed
  via `live_state.json`'s `updated` timestamp — 2026-09-10T16:17:08+00:00 —
  before starting); `review-hard-calls` confirmed 0 pending.

- **Run 2026-09-10 (3-hourly check, ~15:50-16:20 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 9136 → 9344, boldness/stagnation counter
  654 → 669.** No live trading this cycle (tick 27 already handled at 00:20
  UTC, confirmed via `live_state.json`'s `updated` timestamp before
  starting). Repo started in detached HEAD with local `main` stale (a real
  divergence relative to a force-pushed `origin/main`, not the usual
  shallow-clone artifact — `git log` showed both refs 50 commits apart from
  each other); resolved with `git checkout main && git reset --hard
  origin/main` on a clean tree after confirming the detached HEAD already
  matched `origin/main`'s tip byte-for-byte, so nothing local was lost.
  Freshness checks before running: `review-hard-calls` still 0 pending (1
  reviewed so far, unchanged), items 2/5/6 still not a scheduled session's
  call, no other unstarted/unblocked roadmap item found — so the cycle ran
  the standing evolve batch via `tools/background_runner.py` (`start` +
  backgrounded `wait`), which again worked exactly as designed. Champion's
  fold-aggregate fitness held flat at 1.469 across all 15 generations. Raw
  best-of-generation fold-fitness beat the champion's own 1.469 in 12/15
  generations, tied in 1, lost in 2 — an ordinary batch. `holdout-pressure`
  242 → 245 draws, every one still lost, margin ~6.61-6.63, unchanged in
  shape. See `runs/2026-09-10-1620-evolve-batch-v3.md`. Verified before
  commit: `python3 -m pytest -q` 390/390 both before (baseline) and after
  `evolve`; direct key-by-key diff of `live_state.json` showed only
  `lineage`/`researcher_memory`/`updated` changed (genome, broker, journal,
  hard_call_reviews byte-identical); constitution verified
  `726dfa4bac85891a` unchanged; `tools/edit_bundle_module.py
  verify`/`sync --check` both clean; dashboard rebuilt (`index.html`).
  Genome still v3 (1d) live, untouched.

- **Run 2026-09-10 (3-hourly check, ~12:47-13:34 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 8940 → 9136, boldness/stagnation counter
  639 → 654.** No live trading this cycle (tick 27 already handled at 00:20
  UTC, confirmed via `live_state.json`'s `updated` timestamp before
  starting). Repo started in detached HEAD with local `main` stale at
  `4f15e68` (2026-09-04); resolved with `git checkout main && git reset
  --hard origin/main` on a clean tree rather than reaching for
  `tools/git_sync.py` first — same recurring habit lapse many prior entries
  have flagged, still not fixed. Freshness checks before running:
  `review-hard-calls` still 0 pending (1 reviewed so far, unchanged),
  `holdout-pressure` 241 → 242 draws after this run (every one still lost,
  margin ~6.6, unchanged in shape), items 2/5/6 still not a scheduled
  session's call — so the cycle ran the standing evolve batch via
  `tools/background_runner.py` (`start` + backgrounded `wait`), which again
  worked exactly as designed. Champion's fold-aggregate fitness held flat at
  1.469 across all 15 generations. Raw best-of-generation fold-fitness beat
  the champion's own 1.469 in 10/15 generations, tied in 1, lost in 4 — an
  ordinary batch. See `runs/2026-09-10-1334-evolve-batch-v3.md`. Verified
  before commit: `python3 -m pytest -q` 390/390 both before (baseline) and
  after `evolve`; direct key-by-key diff of `live_state.json` showed only
  `lineage`/`researcher_memory`/`updated` changed (genome, broker, journal,
  hard_call_reviews byte-identical); constitution verified `726dfa4bac85891a`
  unchanged; `tools/edit_bundle_module.py verify`/`sync --check` both clean;
  dashboard rebuilt (`index.html`). Genome still v3 (1d) live, untouched.

- **Run 2026-09-10 (3-hourly check, ~09:46-10:33 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 8722 → 8940, boldness/stagnation counter
  624 → 639.** No live trading this cycle (tick 27 already handled at 00:20
  UTC, confirmed via `live_state.json`'s `updated` timestamp before starting).
  Repo started in detached HEAD with local `main` stale at `4f15e68`
  (2026-09-04); this time actually used `python3 tools/git_sync.py` instead
  of hand-rolling `git reset --hard` (the habit lapse several prior entries
  flagged) — it unshallowed, found a real merge-base, and fast-forwarded
  cleanly. Freshness checks before running: `review-hard-calls` still 0
  pending (1 reviewed so far, unchanged), `holdout-pressure` 237 → 241 draws
  after this run (every one still lost, margin ~6.6-6.62, unchanged in
  shape), items 2/5/6 still not a scheduled session's call — so the cycle ran
  the standing evolve batch via `tools/background_runner.py` (`start` +
  backgrounded `wait`), which again worked exactly as designed. Champion's
  fold-aggregate fitness held flat at 1.469 across all 15 generations. Raw
  best-of-generation fold-fitness beat the champion's own 1.469 in 12/15
  generations, lost in 3 — an ordinary batch. See
  `runs/2026-09-10-1033-evolve-batch-v3.md`. Verified before commit: `python3
  -m pytest -q` 390/390 both before (baseline) and after `evolve`; direct
  key-by-key diff of `live_state.json` showed only
  `lineage`/`researcher_memory`/`updated` changed (genome, broker, journal,
  hard_call_reviews byte-identical); constitution verified
  `726dfa4bac85891a` unchanged; `tools/edit_bundle_module.py
  verify`/`sync --check` both clean; dashboard rebuilt (`index.html`).
  Genome still v3 (1d) live, untouched.

- **Run 2026-09-10 (3-hourly check, ~06:47-07:16 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 8512 → 8722, boldness/stagnation counter
  609 → 624.** No live trading this cycle (tick 27 already handled at 00:20
  UTC, confirmed via `live_state.json`'s `updated` timestamp and the prior
  04:32 UTC run note before starting). Repo started in detached HEAD with
  local `main` stale at `4f15e68` (2026-09-04, no merge-base against
  `origin/main`'s `cdbc5be`); resolved with `git checkout main && git reset
  --hard origin/main` on a clean tree rather than reaching for
  `tools/git_sync.py` first — same recurring habit lapse many prior entries
  have flagged, still not fixed. Freshness checks before running:
  `review-hard-calls` still 0 pending, `holdout-pressure` unchanged in shape
  (237 draws, all lost, margin ~6.6), items 2/5/6 still not a scheduled
  session's call — so the cycle ran the standing evolve batch via
  `tools/background_runner.py` (`start` + backgrounded `wait`), which again
  worked exactly as designed (instant start, real PID, ~29-minute wait, real
  exit code 0, no truncation). Champion's fold-aggregate fitness held flat at
  1.469 across all 15 generations. Raw best-of-generation fold-fitness beat
  the champion's own 1.469 in 10/15 generations, tied in 3, lost in 2 — an
  ordinary batch. See `runs/2026-09-10-0724-evolve-batch-v3.md`. Verified
  before commit: `python3 -m pytest -q` 390/390 both before (baseline) and
  after `evolve`; direct key-by-key diff of `live_state.json` showed only
  `lineage`/`researcher_memory`/`updated` changed (genome, broker, journal
  byte-identical); constitution verified `726dfa4bac85891a` unchanged;
  `tools/edit_bundle_module.py verify`/`sync --check` both clean; dashboard
  rebuilt (`index.html`) since `lineage`/`researcher_memory` counts feed its
  genome panel. Genome still v3 (1d) live, untouched.

- **Run 2026-09-10 (3-hourly check, ~03:47-04:32 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 8305 → 8512, boldness/stagnation counter
  594 → 609.** No live trading this cycle (tick 27 already handled at 00:20
  UTC, confirmed via `live_state.json`'s `updated` timestamp and the prior
  01:13 UTC run note before starting). Repo started in detached HEAD with
  local `main` badly stale (60+ commits behind, no shared tip visible at
  shallow depth); resolved with `git checkout main && git reset --hard
  origin/main` on a clean tree rather than reaching for `tools/git_sync.py`
  first — same recurring habit lapse several prior entries have flagged.
  Freshness checks before running: `review-hard-calls` still 0 pending,
  `holdout-pressure` unchanged in shape, items 2/5/6 still not a scheduled
  session's call — so the cycle ran the standing evolve batch via
  `tools/background_runner.py` (`start` + backgrounded `wait`), which again
  worked exactly as designed (instant start, real PID, ~36-minute wait,
  real exit code 0, no truncation). Champion's fold-aggregate fitness held
  flat at 1.469 across all 15 generations. Raw best-of-generation
  fold-fitness beat the champion's own 1.469 in 12/15 generations, tied in
  1, lost in 2 — an ordinary batch. `holdout-pressure` 235 → 237 real draws,
  every one still lost, margin unchanged (~6.61). **Housekeeping**: this
  cycle's evolve log was accidentally written to `runs/` instead of `/tmp`;
  fixed by adding `runs/*.log` to `.gitignore` (separate commit `27f6f91`)
  so `runs/` stays dated-notes-only regardless of where a session points
  `background_runner.py --log` in the future. See
  `runs/2026-09-10-0432-evolve-batch-v3.md`. Verified before commit: `python3
  -m pytest -q` 390/390 both before (baseline) and after `evolve`; direct
  key-by-key diff of `live_state.json` showed only
  `lineage`/`researcher_memory`/`updated` changed (genome, broker, journal
  byte-identical); constitution verified `726dfa4bac85891a` unchanged;
  `tools/edit_bundle_module.py verify`/`sync --check` both clean. Genome
  still v3 (1d) live, untouched.

- **Run 2026-09-10 (3-hourly check, ~00:46-01:13 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 8110 → 8305, boldness/stagnation counter
  580 → 594. First real use of `tools/background_runner.py` (shipped
  2026-09-09 but unused until now): worked exactly as designed.** No live
  trading this cycle (tick 27 already handled at 00:20 UTC, confirmed via
  `live_state.json`'s `updated` timestamp and
  `runs/2026-09-10-0020-daily-trading.md` before starting). Repo started in
  detached HEAD with local `main` badly stale (60+ commits behind, no shared
  tip visible at shallow depth); resolved with `git checkout -B main
  origin/main` on a clean tree (no local commits to lose). Freshness checks:
  `review-hard-calls` still 0 pending, `holdout-pressure` unchanged in shape,
  items 2/5/6 still not a scheduled session's call — so the cycle ran the
  standing evolve batch, using `background_runner.py`'s `start`/`wait` pair
  instead of the tool call's own backgrounding: `start` returned in well
  under a second with the real child PID and a log capturing all 15
  generations' output from the first byte, `wait` (itself backgrounded via
  the calling tool, since `wait` spawns nothing so this doesn't recreate the
  item-9 two-mechanisms trap) blocked the full ~22 minutes and returned the
  real exit code from the child's own status-file write
  (`{"exited": true, "exit_code": 0, "waited_seconds": 1320.03}`). No
  nohup/`&`, no truncated log — recommend this as the default way to run
  `evolve N` going forward. Champion's recomputed fold-aggregate fitness this
  batch: 1.469 (not the 0.977 seen in several 2026-09-09 batches — expected
  `rolling_folds()` window drift as "now" advances, already documented, not
  a new finding). Raw best-of-generation fold-fitness beat the champion's own
  1.469 in 12/15 generations, tied in 2, lost once — an ordinary batch, no
  streak. See
  `runs/2026-09-10-0113-evolve-batch-v3-background-runner-first-use.md`.
  Verified before commit: `python3 -m pytest -q` 390/390 both before
  (baseline) and after `evolve`; direct key-by-key diff of `live_state.json`
  showed only `lineage`/`researcher_memory`/`updated` changed (genome,
  broker, journal byte-identical); constitution verified `726dfa4bac85891a`
  unchanged; `tools/edit_bundle_module.py verify`/`sync --check` both clean.
  Genome still v3 (1d) live, untouched.

- **Run 2026-09-09 (3-hourly check, ~21:47-22:00 UTC): shipped
  `tools/background_runner.py`, the mechanical fix Next-steps item 9 called
  for after its doc-only fix (2026-09-08) kept getting recurred past
  (2026-09-09, twice more).** No live trading this cycle (tick 26 already
  handled at 00:20 UTC on the bar closing 2026-09-08; today's bar,
  2026-09-09, has not closed yet — confirmed via `live_state.json`'s
  `updated` timestamp, `ticks: 26`, and the 20:30 UTC daily-evaluation note
  before starting). Repo started in detached HEAD with local `main` stale
  against `origin/main` and no merge-base visible at default fetch depth —
  the documented shallow-clone false-divergence; resolved with `git reset
  --hard origin/main` on a clean tree (equivalent to what `tools/git_sync.py`
  would have done, but the tool should have been reached for first, same
  habit lapse several recent entries have already flagged). New tool exposes
  `start`/`wait` as two separate CLI calls so a long-running command like
  `evolve N` gets detached (`start_new_session`, no `nohup`/`&`) with output
  captured to a log file from the first byte (no pipe, nothing to truncate),
  and its real exit code retrievable later from a *different* process via a
  status file the child writes itself on completion — removing the specific
  two-backgrounding-mechanisms trap and the tail-truncation trap this item's
  log shows recurring six-plus times, rather than relying on a session
  remembering the rule under time pressure. `tests/test_background_runner.py`
  (6 new tests against real subprocesses: full output capture, real exit-code
  retrieval across the start/wait process boundary, timeout-while-running,
  stale-status-file replacement, and a still-running liveness check) — full
  suite 384 → 390, all passing. Not yet used for a real `evolve` batch; see
  item 9 above for the fuller writeup. Verified before commit: `live_state.json`
  byte-identical (only tooling/test/doc files touched, confirmed via `git
  status`), constitution still `726dfa4bac85891a` (`evotrader_bundle.py
  summary` reprints it unchanged), `tools/edit_bundle_module.py verify`/`sync
  --check` both clean (this tool isn't a bundled module, doesn't touch
  `_SRC`). Genome still v3 (1d) live, untouched.

- **Run 2026-09-09 (3-hourly check, ~18:47-19:17 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 7887 → 8096, boldness/stagnation counter
  564 → 579.** No live trading this cycle (tick 26 already handled at 00:20
  UTC, confirmed via `live_state.json`'s `updated` timestamp and the prior
  session's run notes before starting). Repo started in detached HEAD but
  HEAD already matched `origin/main` byte-for-byte — only local `main` was
  stale, not a real divergence; resolved with `git checkout -B main
  origin/main`. `review-hard-calls` still 0 pending; no other unstarted,
  unblocked roadmap item found, so the cycle's remaining time went to the
  standing evolve batch. Champion fitness held flat at 0.977 across all 15
  generations; every new candidate lost to it. Raw best-of-generation
  fold-fitness beat the champion's own 0.977 in 15/15 generations (100%) — a
  fourth batch in a row at or near 100%, still fully explained by the
  2026-09-09 07:11 UTC fold-aggregate-collapse finding, not a new
  search-quality change; `holdout-pressure` confirms the sealed-holdout side
  is not weakening (231 draws, all lost, margin ~6.60, up slightly from
  ~6.54) — see `runs/2026-09-09-1917-evolve-batch-v3.md`. Verified before
  commit: `python3 -m pytest -q` 384/384 both before (baseline) and after
  `evolve`, run strictly sequentially; direct key-by-key diff of
  `live_state.json` showed only `lineage`/`researcher_memory`/`updated`
  changed (genome, broker, journal byte-identical); constitution verified
  `726dfa4bac85891a` unchanged; `tools/edit_bundle_module.py verify`/`sync
  --check` both clean. Genome still v3 (1d) live, untouched.

- **Run 2026-09-09 (3-hourly check, ~15:47-16:15 UTC): fixed a stale roadmap
  pointer, then 15 more real `evolve` generations against the live v3 (1d)
  champion, no promotion — cumulative candidates tried against v3 rose 7680 →
  7887, boldness/stagnation counter 549 → 564.** No live trading this cycle
  (tick 26 already handled at 00:20 UTC, confirmed before starting). Repo
  started in detached HEAD with local `main` stale against `origin/main`
  (genuinely no merge-base, confirmed directly) — resolved with `git checkout
  main && git reset --hard origin/main` rather than `tools/git_sync.py`
  first, same lapse several recent entries have flagged; the tool would have
  produced the identical result here since the no-merge-base case is its own
  documented fallback, but the habit is still worth fixing. **Stale-pointer
  fix**: "Owner decisions pending"'s v3-drawdown-disclosure follow-up said
  "not yet done" for the dashboard change that `f34f5fc` (2026-09-08) had
  actually already shipped same-day — verified the disclosure is present in
  the current `evotrader_dashboard.py` and corrected the pointer. No other
  unstarted, unblocked roadmap item found (item 2 parked, item 4 still 0
  pending hard-call reviews, items 5/6 explicitly not a scheduled session's
  call, item 7 feature-complete, item 8 closed for v3), so the cycle's
  remaining time went to the standing evolve batch. Champion fitness held
  flat at 0.977 across all 15 generations; every new candidate lost to it.
  Raw best-of-generation fold-fitness beat the champion's own 0.977 in 14/15
  generations (generation 10 the lone miss, 0.929) — consistent with the
  already-explained fold-aggregate-collapse artifact, not a new finding. See
  `runs/2026-09-09-1615-evolve-batch-v3-and-stale-pointer-fix.md`. Verified
  before commit: `python3 -m pytest -q` 384/384 both before (baseline) and
  after `evolve`, run strictly sequentially; direct key-by-key diff of
  `live_state.json` showed only `lineage`/`researcher_memory`/`updated`
  changed (genome, broker, journal byte-identical); constitution verified
  `726dfa4bac85891a` unchanged; `tools/edit_bundle_module.py verify`/`sync
  --check` both clean. Genome still v3 (1d) live, untouched.

- **Run 2026-09-09 (3-hourly check, ~12:46-13:22 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 7471 → 7680, boldness/stagnation counter
  534 → 549.** No live trading this cycle (tick 26 already handled at 00:20
  UTC, confirmed before starting). Repo started in detached HEAD with local
  `main` stale against `origin/main` (shallow-clone false-divergence);
  resolved with `git checkout main && git reset --hard origin/main` directly
  rather than reaching for `tools/git_sync.py` first — same lapse the 10:11
  UTC entry already flagged, still not fixed by writing it down once.
  `review-hard-calls` still 0 pending; `holdout-pressure` unchanged from the
  10:11 UTC check (still 69 draws, every one lost — no new batch had run
  between the two checks). Champion fitness held flat at 0.977 across all 15
  generations; every new candidate lost to it. Raw best-of-generation
  fold-fitness beat the champion's own 0.977 in all 12 generations whose
  output survived — see the process mistake below — consistent with the
  fourth-in-a-row 100%-range batch under the already-explained
  fold-aggregate-collapse artifact (07:11 UTC entry), not a new
  search-quality change. **Process mistake this cycle**: the backgrounded
  `evolve` command was piped through `tail -60` before being written to its
  own log file, permanently losing generations 1-3's output — the file is
  the only record for a backgrounded command, so truncating it before
  capture (rather than when later displaying an already-complete file)
  throws away data with no way to recover it; next time background the
  plain command with no pipe, or use `tee` instead of `tail` — see
  `runs/2026-09-09-1322-evolve-batch-v3.md`. Verified before commit: `python3
  -m pytest -q` 384/384 both before (baseline) and after `evolve`, run
  strictly sequentially; direct key-by-key diff of `live_state.json` showed
  only `lineage`/`researcher_memory`/`updated` changed (genome, broker,
  journal byte-identical); constitution verified `726dfa4bac85891a`
  unchanged; `tools/edit_bundle_module.py verify`/`sync --check` both clean.
  Genome still v3 (1d) live, untouched.

- **Run 2026-09-09 (3-hourly check, ~09:46-10:11 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 7264 → 7471, boldness/stagnation counter
  519 → 534.** No live trading this cycle (tick 26 already handled at 00:20
  UTC, confirmed before starting). Repo started in detached HEAD with local
  `main` stale and showing no merge-base against `origin/main` (shallow
  clone); resolved by hand with `git reset --hard origin/main` before
  noticing `tools/git_sync.py` should have been tried first — ran it
  afterward and confirmed it agreed (`already up to date`), nothing lost,
  but next session should reach for the tool first even when the divergence
  looks like a real rewrite. **Third consecutive batch at 100% fold-clear
  rate** (raw best-of-generation fold-fitness beat the champion's 0.977 in
  all 15 generations), following the two 100% batches at ~00:46-01:19 UTC
  and ~03:51-04:27 UTC that the 04:28 UTC note flagged as worth watching for
  a third repeat. Re-checked with `holdout-pressure`: total real draws now
  69 (up from 57), every one still lost, margin ~6.36-6.41 this batch —
  consistent with (not a complication of) the 07:11 UTC finding that the
  champion's fold-aggregate fitness collapsed to 0.977 (a `rolling_folds()`
  window/regime artifact) while the sealed-holdout margin stayed flat-to-growing.
  Three 100% batches in a row is the expected consequence of a fixed, lower
  fold bar, not a new search-quality change — see
  `runs/2026-09-09-1011-evolve-batch-v3-third-100pct.md`. Verified before
  commit: `python3 -m pytest -q` 384/384 (baseline, run strictly before
  `evolve`, unchanged — no code touched), direct key-by-key diff of
  `live_state.json` showed only `lineage`/`researcher_memory`/`updated`
  changed (genome, broker, journal byte-identical), constitution verified
  `726dfa4bac85891a` unchanged, `tools/edit_bundle_module.py verify`/`sync
  --check` both clean. Genome still v3 (1d) live, untouched.

- **Run 2026-09-09 (3-hourly check, ~06:46-07:11 UTC): closed the two-batch
  "100% fold-clear rate" flag with a specific explanation, plus a third
  `evolve` batch (14/15, 93%) — cumulative candidates tried against v3 rose
  7055 → 7264, boldness/stagnation counter 505 → 519.** No live trading
  this cycle (tick 26 already handled at 00:20 UTC, confirmed before
  starting). Repo started in detached HEAD with the documented shallow-clone
  false-divergence (local `main` stale at `4f15e68` from 2026-09-04);
  `python3 tools/git_sync.py` fast-forwarded cleanly. **Finding: the
  fold-clear-rate spike is fully explained by the champion's own recomputed
  fold-aggregate fitness collapsing 1.590 → 0.977 (~38%) between the
  2026-09-08 22:18 UTC and 2026-09-09 01:19 UTC batches — a
  `rolling_folds()` window/regime artifact, not a search-quality change.**
  Checked directly with the existing `holdout-pressure` diagnostic (reads
  `acct.lineage`, no new code): the sealed-holdout margin has *not*
  collapsed the same way — champion holdout fitness stayed in a tight
  ~1.06-1.20 band and the margin by which it beats every challenger has if
  anything grown slightly (~6.05 → ~6.36) across all 57 recorded draws,
  every one lost. A lower fold bar is just easier for the same-shaped
  candidate distribution to clear by chance; this is the standing
  fold-clears-then-loses-holdout pattern holding up exactly as designed, no
  bug, no fix needed — see
  `runs/2026-09-09-0711-evolve-batch-v3-holdout-pressure-explained.md` for
  the full breakdown and the batch's own verification (pytest 384/384,
  `live_state.json` diff limited to `lineage`/`researcher_memory`/`updated`,
  constitution `726dfa4bac85891a` unchanged, bundle verify/sync clean).
  Genome still v3 (1d) live, untouched.

- **Run 2026-09-09 (3-hourly check, ~03:51-04:27 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 6847 → 7055, boldness/stagnation counter
  490 → 505.** No live trading this cycle (tick 26 already handled at 00:20
  UTC, confirmed via `live_state.json`'s `updated` timestamp and
  `runs/2026-09-09-0020-daily-trading.md`/`runs/2026-09-09-0119-evolve-batch-v3.md`
  before starting — this is the day's second evolve batch). `review-hard-calls`
  still 0 pending (item 4 has no real case yet); items 2/6 still blocked per
  "Owner decisions pending"; item 5's council-wiring question remains
  un-scoped, not something to decide unilaterally, so this cycle ran the
  standing evolve batch. Champion fitness held flat at 0.977 across all 15
  generations; every new candidate lost to it. Raw best-of-generation
  fold-fitness beat the champion's own 0.977 in **15/15 generations this
  batch (100%)**, the second consecutive batch at 100% (previous batch,
  ~00:46-01:19 UTC, also 100%) — still read as the standing
  fold-clears-then-loses-holdout pattern, not a new finding, but now two in a
  row at the highest rate this file has tracked; worth a future session's
  attention if a third batch repeats it — see
  `runs/2026-09-09-0428-evolve-batch-v3.md`, which also records this session
  recreating the item-9 nohup-`&`-in-one-call footgun yet again (caught
  immediately by the session itself, not an external reviewer: polled the
  real PID with `kill -0` in a separate backgrounded loop to actual exit
  before touching any state, no harm). Verified before commit: `python3 -m
  pytest -q` 384/384 (baseline, run strictly before `evolve`, unchanged — no
  code touched), direct key-by-key Python-equality diff of `live_state.json`
  showed only `lineage`/`researcher_memory`/`updated` changed (`genome`,
  `broker`, `journal` byte-identical, genome version still 3), constitution
  verified `726dfa4bac85891a` unchanged, `tools/edit_bundle_module.py
  verify`/`sync --check` both clean. Genome still v3 (1d) live, untouched.

- **Run 2026-09-09 (3-hourly check, ~00:46-01:19 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 6637 → 6847, boldness/stagnation counter
  475 → 489.** No live trading this cycle (tick 26 already handled at 00:20
  UTC, confirmed via `live_state.json`'s `updated` timestamp and
  `runs/2026-09-09-0020-daily-trading.md` before starting). `review-hard-calls`
  still 0 pending (item 4 has no real case yet). Champion fitness held flat
  at 0.977 across all 15 generations; every new candidate lost to it. Raw
  best-of-generation fold-fitness beat the champion's own 0.977 in **15/15
  generations this batch (100%)** — the highest beat-rate recorded in this
  file's recent tracking (prior batches ranged 27-73%); read as more evidence
  for the standing fold-clears-then-loses-holdout pattern
  (`holdout-pressure`), not a new finding, but flagged in case the rate stays
  this high — see `runs/2026-09-09-0119-evolve-batch-v3.md`. **Also recreated
  the item-9 nohup/`&` footgun via a new path this cycle** (Bash tool's own
  `run_in_background: true` combined with a trailing shell `&` in the same
  command, rather than the `nohup ... &` string form logged five times
  previously) — caught immediately via `updated` timestamp + `kill -0` on the
  real PID before touching any state, no harm; see the run note for the
  distinct trigger shape. Verified before commit: `python3 -m pytest -q`
  384/384 (baseline, run strictly before `evolve`, unchanged — no code
  touched), direct key-by-key diff of `live_state.json` showed only
  `lineage`/`researcher_memory`/`updated` changed (genome, broker, journal
  byte-identical), constitution verified `726dfa4bac85891a` unchanged,
  `tools/edit_bundle_module.py verify`/`sync --check` both clean. Genome
  still v3 (1d) live, untouched.

- **Run 2026-09-08 (3-hourly check, ~21:46-22:18 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 6429 → 6637, boldness/stagnation counter
  459 → 474.** No live trading this cycle (tick 25 already handled at 00:20
  UTC, confirmed via `live_state.json`'s `updated` timestamp and
  `runs/2026-09-08-0020-daily-trading.md`/`runs/2026-09-08-2030-daily-evaluation.md`
  before starting). Repo started in detached HEAD with the documented
  shallow-clone false-divergence (AGENTS.md run-protocol step 2) — `python3
  tools/git_sync.py` fast-forwarded cleanly, nothing discarded. Freshness
  checks before running: `review-hard-calls` 0 pending, `holdout-pressure`
  same fold-clears-then-loses-holdout shape as always, items 2/5/6 still
  blocked with no new owner input, item 4 still 0 pending hard-call reviews.
  Champion fitness held flat at 1.590 across all 15 generations; every new
  candidate lost to it. Raw best-of-generation fold-fitness beat the
  champion's own 1.590 in 7/15 generations this batch (47%), with 3 more
  tying exactly — see `runs/2026-09-08-2218-evolve-batch-v3.md`. Verified
  before commit: `python3 -m pytest -q` 384/384 (baseline, run strictly
  before `evolve`, unchanged — no code touched), direct key-by-key diff of
  `live_state.json` showed `lineage`/`researcher_memory`/`updated` changed
  plus `broker.borrow_bps_per_bar` going from unset to its default `0.0`
  (the short-selling schema field serialized for the first time, not a
  trade — `cash`/`positions`/`nav_history` byte-identical), genome
  byte-identical, constitution verified `726dfa4bac85891a` unchanged,
  `tools/edit_bundle_module.py verify`/`sync --check` both clean. Genome
  still v3 (1d) live, untouched.

- **Run 2026-09-08 (3-hourly check, ~18:46-19:14 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 6220 → 6429, boldness/stagnation counter
  444 → 459.** No live trading this cycle (tick 25 already handled at 00:20
  UTC, confirmed via `live_state.json`'s `updated` timestamp and
  `runs/2026-09-08-0020-daily-trading.md`/`runs/2026-09-08-0900-daily-discussion.md`
  before starting). Freshness checks before running: `review-hard-calls` 0
  pending, items 2/5/6 still blocked with no new owner input (now over six
  days since 2026-09-02 with no response — see "Owner decisions pending").
  Champion fitness held flat at 1.590 across all 15 generations; every new
  candidate lost to it. Raw best-of-generation fold-fitness beat the
  champion's own 1.590 in 8/15 generations this batch (53%), with 1 more
  tying exactly — see `runs/2026-09-08-1914-evolve-batch-v3.md`. Verified
  before commit: `python3 -m pytest -q` 366/366 (baseline, run strictly
  before `evolve`, unchanged — no code touched), direct key-by-key diff of
  `live_state.json` showed only `lineage`/`researcher_memory`/`updated`
  changed (genome, broker, journal byte-identical), constitution verified
  `8b74865634b1db07` unchanged, `tools/edit_bundle_module.py verify`/`sync
  --check` both clean. Genome still v3 (1d) live, untouched.

- **Run 2026-09-08 (3-hourly check, ~15:46-16:18 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 6011 → 6220, boldness/stagnation counter
  429 → 444.** No live trading this cycle (tick 25 already handled at 00:20
  UTC, confirmed via `live_state.json`'s `updated` timestamp and
  `runs/2026-09-08-0020-daily-trading.md`/`runs/2026-09-08-0900-daily-discussion.md`
  before starting). Freshness checks before running: `review-hard-calls` 0
  pending, items 2/5/6 still blocked with no new owner input, item 4 still
  waiting on a real live hard-call flag. Champion fitness held flat at 1.590
  across all 15 generations; every new candidate lost to it. Raw
  best-of-generation fold-fitness beat the champion's own 1.590 in 9/15
  generations this batch (60%), with 2 more tying exactly — see
  `runs/2026-09-08-1618-evolve-batch-v3.md`, which also records this
  session briefly recreating the item-9 `nohup ... &`-in-one-call footgun a
  fourth/fifth time this week (caught immediately: polled the real PID with
  `kill -0` to actual exit before touching any state, no harm). Verified
  before commit: `python3 -m pytest -q` 366/366 (baseline, run strictly
  before `evolve`, unchanged — no code touched), direct key-by-key diff of
  `live_state.json` showed only `lineage`/`researcher_memory`/`updated`
  changed (genome, broker, journal byte-identical), constitution verified
  `8b74865634b1db07` unchanged, `tools/edit_bundle_module.py verify`/`sync
  --check` both clean. Genome still v3 (1d) live, untouched.

- **Run 2026-09-08 (3-hourly check, ~12:46-13:15 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 5802 → 6011, boldness/stagnation counter
  414 → 429.** No live trading this cycle (tick 25 already handled at 00:20
  UTC, confirmed via `live_state.json`'s `updated` timestamp and
  `runs/2026-09-08-0020-daily-trading.md`/`runs/2026-09-08-0900-daily-discussion.md`
  before starting). Freshness checks before running: `review-hard-calls` 0
  pending, items 2/5/6 still blocked with no new owner input. Champion
  fitness held flat at 1.590 across all 15 generations; every new candidate
  lost to it. Raw best-of-generation fold-fitness beat the champion's own
  1.590 in 8/15 generations this batch (53%), with 2 more tying exactly —
  see `runs/2026-09-08-1315-evolve-batch-v3.md`, which also records this
  session's backgrounded `evolve` again hitting the tool's own foreground
  timeout mid-run (no `nohup`/`&` used, per item 9) and being polled to real
  completion via `kill -0` before touching any state. Verified before
  commit: `python3 -m pytest -q` 366/366 (baseline, run strictly before
  `evolve`, unchanged — no code touched), direct key-by-key diff of
  `live_state.json` showed only `lineage`/`researcher_memory`/`updated`
  changed (genome, broker, journal byte-identical), constitution verified
  `8b74865634b1db07` unchanged, `tools/edit_bundle_module.py verify`/`sync
  --check` both clean. Genome still v3 (1d) live, untouched.

- **Run 2026-09-08 (3-hourly check, ~09:46-10:08 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 5593 → 5802, boldness/stagnation counter
  399 → 414.** No live trading this cycle (tick 25 already handled at 00:20
  UTC, confirmed via `live_state.json`'s `updated` timestamp and
  `runs/2026-09-08-0020-daily-trading.md`/`runs/2026-09-08-0900-daily-discussion.md`
  before starting). Freshness checks before running: `review-hard-calls` 0
  pending, items 2/5/6 still blocked with no new owner input. Champion
  fitness held flat at 1.590 across all 15 generations; every new candidate
  lost to it. Raw best-of-generation fold-fitness beat the champion's own
  1.590 in 7/15 generations this batch (47%), with 4 more tying exactly —
  back up from the previous batch's 27% low, in the same noisy range as
  recent batches — see `runs/2026-09-08-1008-evolve-batch-v3.md`, which also
  records this session briefly recreating the item-9 nohup-`&`-detachment
  footgun a third time this week (caught immediately via `ps aux` + polling
  the real PID with `kill -0` before touching any state). Verified before
  commit: `python3 -m pytest -q` 366/366 (baseline, run strictly before
  `evolve`, unchanged — no code touched), direct key-by-key diff of
  `live_state.json` showed only `lineage`/`researcher_memory`/`updated`
  changed (genome, broker, journal byte-identical), constitution verified
  `8b74865634b1db07` unchanged, `tools/edit_bundle_module.py verify`/`sync
  --check` both clean. Genome still v3 (1d) live, untouched.

- **Run 2026-09-08 (3-hourly check, ~06:46-07:31 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 5384 → 5593, boldness/stagnation counter
  384 → 399.** No live trading this cycle (tick 25 already handled at 00:20
  UTC, confirmed via `live_state.json`'s `updated` timestamp and
  `runs/2026-09-08-0020-daily-trading.md` before starting). Freshness checks
  before running: `review-hard-calls` 0 pending (1 reviewed so far,
  unchanged), items 2/5/6 still blocked with no new owner input; items
  1/3/4/7/8 in the roadmap are closed or passive (item 7 feature-complete
  relative to the bundle, item 8 closed for v3, item 4's infra shipped with
  0 pending reviews) so this cycle ran the standing evolve batch rather than
  a new engineering slice. Champion fitness held flat at 1.590 across all 15
  generations; every new candidate lost to it. Raw best-of-generation
  fold-fitness strictly beat the champion's own 1.590 in only 4/15
  generations this batch (27%, generations 2/3/4/9) — the lowest beat-rate
  of the last several batches (53%, 60%, 67% before this), with 4 more
  generations tying exactly at 1.590 — see
  `runs/2026-09-08-0731-evolve-batch-v3.md`. Verified before commit: `python3
  -m pytest -q` 366/366 (baseline, run strictly before `evolve`, unchanged —
  no code touched), direct top-level key diff of `live_state.json` showed
  only `lineage`/`researcher_memory`/`updated` changed (genome, broker,
  journal byte-identical), constitution verified `8b74865634b1db07`
  unchanged, `tools/edit_bundle_module.py verify`/`sync --check` both clean.
  Genome still v3 (1d) live, untouched.

- **Run 2026-09-08 (3-hourly check, ~03:46-04:27 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 5175 → 5384, boldness/stagnation counter
  369 → 384.** No live trading this cycle (tick 25 already handled at 00:20
  UTC, confirmed via `live_state.json`'s `updated` timestamp and
  `runs/2026-09-08-0020-daily-trading.md` before starting). Freshness checks
  before running: `review-hard-calls` 0 pending (1 reviewed so far,
  unchanged), `live-benchmark` unchanged (24 1d bars / -14.83% excess), items
  2/5/6 still blocked with no new owner input. Champion fitness held flat at
  1.590 across all 15 generations; every new candidate lost to it. Raw
  best-of-generation fold-fitness beat the champion's own 1.590 in 8/15
  generations this batch (53%) — see `runs/2026-09-08-0427-evolve-batch-v3.md`.
  Verified before commit: `python3 -m pytest -q` 366/366 (baseline, run
  strictly before `evolve`, unchanged — no code touched), direct top-level
  key diff of `live_state.json` showed only `lineage`/`researcher_memory`/
  `updated` changed (genome, broker, journal byte-identical), constitution
  verified `8b74865634b1db07` unchanged, `tools/edit_bundle_module.py
  verify`/`sync --check` both clean. Genome still v3 (1d) live, untouched.

- **Run 2026-09-08 (3-hourly check, ~00:47-01:xx UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 4969 → 5175, boldness/stagnation counter
  354 → 369.** No live trading this cycle (tick 25 already handled at 00:20
  UTC, confirmed via `live_state.json`'s `updated` timestamp and
  `runs/2026-09-08-0020-daily-trading.md` before starting). Freshness checks
  before running: `review-hard-calls` 0 pending (1 reviewed so far,
  unchanged), `live-benchmark` now 24 1d bars / -14.83% excess (up from 23
  bars / -12.60%, still far from the 60-bar revisit trigger), items 2/5/6
  still blocked with no new owner input. Champion fitness held flat at 1.590
  across all 15 generations; every new candidate lost to it. Raw
  best-of-generation fold-fitness beat the champion's own 1.590 in 10/15
  generations this batch (67%) — see `runs/2026-09-08-0047-evolve-batch-v3.md`,
  which also records this session briefly recreating the item-9
  nohup-`&`-detachment footgun via a background-launch wrapper (caught
  immediately: the wrapper's own "completed" signal fired while the real
  process was still on generation 1/15; polled the real PID with `kill -0`
  until it actually exited before touching any state). Verified before
  commit: `python3 -m pytest -q` 366/366 (baseline, run strictly before
  `evolve`, unchanged — no code touched), direct top-level key diff of
  `live_state.json` showed only `lineage`/`researcher_memory`/`updated`
  changed (genome, broker, journal byte-identical), constitution verified
  `8b74865634b1db07` unchanged, `tools/edit_bundle_module.py verify`/`sync
  --check` both clean. Genome still v3 (1d) live, untouched.

- **Run 2026-09-07 (3-hourly check, ~21:49-22:17 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 4760 → 4969, boldness/stagnation counter
  339 → 354.** No live trading this cycle (tick 24 already handled at 00:20
  UTC, confirmed via `live_state.json`'s `updated` timestamp and the 20:30
  UTC daily-evaluation note before starting). Freshness checks before
  running: `review-hard-calls` 0 pending (1 reviewed so far, unchanged),
  `holdout-pressure` same fold-clears-then-loses-holdout shape as always,
  `live-benchmark` unchanged (23 1d bars, -12.60% excess), items 2/5/6 still
  blocked with no new owner input. Champion fitness held flat at 1.422
  across all 15 generations; every new candidate lost to it. Raw
  best-of-generation fold-fitness beat the champion's own 1.422 in 9/15
  generations this batch (60%) — see
  `runs/2026-09-07-2217-evolve-batch-v3.md`, which also restates the
  nohup-`&`-detachment footgun (item 9) after this session briefly
  recreated it via a different shell-quoting path (caught immediately, no
  harm — the real process was still polled to completion with `kill -0`
  rather than trusting the wrapper's own early "exited" signal). Verified
  before commit: `python3 -m pytest -q` 366/366 (baseline, run before
  `evolve`, unchanged — no code touched), direct top-level key diff of
  `live_state.json` showed only `lineage`/`researcher_memory`/`updated`
  changed (genome, broker, journal byte-identical), constitution verified
  `8b74865634b1db07` unchanged, `tools/edit_bundle_module.py verify`/`sync
  --check` both clean. Genome still v3 (1d) live, untouched.

- **Run 2026-09-07 (3-hourly check, ~18:46-19:29 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 4551 → 4760, boldness/stagnation counter
  324 → 339.** First normal batch since the 13:34 UTC evolve-vs-disk race fix
  (see the entry below); ran `pytest -q` and `evolve` strictly sequentially
  this cycle per that fix's own process note, not concurrently. No live
  trading this cycle (tick 24 already handled at 00:20 UTC, confirmed via
  `live_state.json`'s `updated` timestamp and `runs/2026-09-07-0020-daily-trading.md`
  before starting). Freshness checks before running: `review-hard-calls` 0
  pending, `live-benchmark` unchanged (23 1d bars, -12.60% excess),
  `holdout-pressure` same fold-clears-then-loses-holdout shape as always,
  items 2/5/6 still blocked with no new owner input. Champion fitness held
  flat at 1.422 across all 15 generations; every new candidate lost to it.
  Raw best-of-generation fold-fitness beat the champion's own 1.422 in 11/15
  generations this batch (73%) — see `runs/2026-09-07-1929-evolve-batch-v3.md`.
  Verified before commit: `python3 -m pytest -q` 366/366 (baseline, run
  before `evolve`, unchanged — no code touched), direct top-level key diff of
  `live_state.json` showed only `lineage`/`researcher_memory`/`updated`
  changed (genome, broker, journal byte-identical), constitution verified
  `8b74865634b1db07` unchanged, `tools/edit_bundle_module.py verify` clean.
  Genome still v3 (1d) live, untouched.

- **Fixed 2026-09-07 (3-hourly check, ~12:46-13:34 UTC): a real evolve-vs-disk
  race in `EvolutionRun.run()`/`Genome.champion()` — caught before commit, no
  live-account damage, but a genuine near-miss.** Started this cycle's `pytest
  -q` baseline and a 15-generation `evolve` batch as two background processes
  close together; the evolve batch finished suspiciously fast and had silently
  evolved against the account's original 2026-08-15 seed genome (v1) instead
  of the real live v3 champion for all 15 generations. Root cause:
  `loop.evolve.EvolutionRun.run()` got its starting genome from
  `Genome.champion()` — a disk read of the shared, unsandboxed
  `state/genomes/champion.json` — instead of the genome already in memory,
  and `evotrader_bundle.py`'s `evolve` command made its promotion decision
  the same way at the end. `tests/test_run_from_files_matches_bundle.py`'s
  `synthetic_universe_4y` fixture legitimately (and normally safely) runs a
  real `EvolutionRun` against a fake seed genome and writes real archive
  files under that same directory mid-test; running that concurrently with a
  real `evolve` let my process read back the wrong genome mid-run. Had any
  candidate cleared the (also-confused) gate, the live account's real v3
  lineage could have been silently overwritten with a fabricated v1-based
  promotion — it didn't happen only because nothing cleared the bar. Caught
  immediately (checked `genome.version` after the run, saw `1` instead of
  `3`) and discarded with `git checkout -- live_state.json` before any
  commit — nothing bad was ever pushed. **Fix**: `EvolutionRun` now takes an
  explicit `champion: Genome` argument and returns the actual final `Genome`
  object from `run()`; all three call sites (`evotrader_bundle.py`'s
  `evolve`, `run_from_files.py`'s `evolve`/`evolve-dry-run`) now thread the
  genome through in memory instead of round-tripping through disk. Also
  found and fixed the same still-open pattern in `promotion-excess-check`
  (`genome_cache = {1: Genome.champion()}` → `Genome()`), which the
  2026-09-06 `_reconstruct_champion_genome` fix's own language should have
  covered but evidently didn't reach — read-only command, so this half is a
  correctness fix for its own output, not a live-account safety fix. See
  `runs/2026-09-07-1334-evolve-champion-disk-race-fix.md` for the full
  writeup. Verified: full suite 366/366 (pure refactor, no new tests — the
  existing `test_run_from_files_matches_bundle.py` evolve/evolve-dry-run
  tests already exercise these exact paths end-to-end and passed), the three
  most relevant test files re-run in isolation 30/30, `tools/edit_bundle_module.py
  verify`/`sync --check` both clean, `py_compile` clean on all three touched
  files, constitution `8b74865634b1db07` unchanged (neither touched file is
  checksummed), `live_state.json` untouched by this cycle's actual commit
  (only `evotrader_bundle.py`/`loop/evolve.py`/`run_from_files.py` changed).
  Genome still v3 (1d) live, untouched. No live trading this cycle (today's
  bar already handled at 00:20 UTC). **Process note for future sessions:
  never run `pytest -q` and a real `evolve`/`evolve-dry-run` invocation
  concurrently in the same container** — this fix removes the live path's
  specific dependency that made this exact race possible, but keep the two
  sequential regardless, since there is no similar guarantee for whatever
  else might touch `state/genomes/` next. No 15-generation evolve batch
  actually landed this cycle (the corrupted one was discarded and the time
  went to root-causing this instead) — cumulative candidates tried against
  v3 remain unchanged at 4551 from the 10:31 UTC batch; next cycle should
  resume normal batches, now safe from this specific race.

- **Run 2026-09-07 (3-hourly check, ~09:47-10:31 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 4343 → 4551, boldness/stagnation counter
  309 → 324.** No live trading this cycle (tick 24 already handled at 00:20
  UTC, confirmed via `live_state.json`'s `updated` timestamp and
  `runs/2026-09-07-0020-daily-trading.md`/`runs/2026-09-07-0900-daily-discussion.md`
  before starting). Freshness checks before running: `review-hard-calls` 0
  pending, items 2/5/6 still blocked with no new owner input since yesterday's
  daily discussion. Champion fitness held flat at 1.422 across all 15
  generations; every new candidate lost to it. Raw best-of-generation
  fold-fitness beat the champion's own 1.422 in 9/15 generations this batch
  (60%) — continuing the last two batches' declining-then-recovering pattern
  (53%, 47%, now 60%), still read as noise around an unsettled rate rather
  than a clear trend in either direction — see
  `runs/2026-09-07-1031-evolve-batch-v3.md`. Verified before commit: `python3
  -m pytest -q` 366/366 (baseline, unchanged — no code touched), direct
  key-by-key diff of `live_state.json` showed only
  `lineage`/`researcher_memory`/`updated` changed (genome, broker, journal
  byte-identical), constitution verified `8b74865634b1db07` unchanged,
  `tools/edit_bundle_module.py verify` clean. Genome still v3 (1d) live,
  untouched.

- **Run 2026-09-07 (3-hourly check, ~06:46-07:11 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 4133 → 4343, boldness/stagnation counter
  294 → 309.** No live trading this cycle (tick 24 already handled at 00:20
  UTC, confirmed via `live_state.json`'s `updated` timestamp and
  `runs/2026-09-07-0020-daily-trading.md`/`runs/2026-09-07-0410-evolve-batch-v3.md`
  before starting). Freshness checks before running: `review-hard-calls` 0
  pending, `live-benchmark` unchanged (23 1d bars, -12.60% excess, still far
  from the 60-bar revisit trigger), items 2/5/6 still blocked with no new
  owner input. Champion fitness held flat at 1.422 across all 15 generations;
  every new candidate lost to it. Raw best-of-generation fold-fitness beat
  the champion's own 1.422 in 9/15 generations this batch (60%) — see
  `runs/2026-09-07-0711-evolve-batch-v3.md`. Verified before commit: `python3
  -m pytest -q` 366/366 (baseline, unchanged — no code touched), direct
  key-by-key diff of `live_state.json` showed only
  `lineage`/`researcher_memory`/`updated` changed (genome, broker, journal
  byte-identical), constitution verified `8b74865634b1db07` unchanged. Genome
  still v3 (1d) live, untouched.

- **Run 2026-09-07 (3-hourly check, ~03:47-04:10 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 3937 → 4133 (counter at gen 1 → gen 15;
  continues from the 01:29 UTC batch's ending count of 3923), boldness/
  stagnation counter 280 → 294.** No live trading this cycle (tick 24 already
  handled at 00:20 UTC, confirmed via `live_state.json`'s `updated` timestamp
  and `runs/2026-09-07-0020-daily-trading.md`/`runs/2026-09-07-0129-evolve-batch-v3.md`
  before starting). Freshness checks before running: `review-hard-calls` 0
  pending, `holdout-pressure` same fold-clears-then-loses-holdout shape as
  always, `live-benchmark` unchanged (23 1d bars, -12.60% excess, still far
  from the 60-bar revisit trigger), items 2/5/6 still blocked with no new
  owner input. Champion fitness held flat at 1.422 across all 15 generations;
  every new candidate lost to it. Raw best-of-generation fold-fitness beat
  the champion's own 1.422 in 13/15 generations this batch — see
  `runs/2026-09-07-0410-evolve-batch-v3.md` for the batch detail (full log
  captured cleanly this time, no truncation). Verified before commit:
  `python3 -m pytest -q` 366/366 (baseline, unchanged — no code touched),
  direct key-by-key diff of `live_state.json` showed only
  `lineage`/`researcher_memory`/`updated` changed (genome, broker, journal
  byte-identical), constitution verified `8b74865634b1db07` unchanged,
  `tools/edit_bundle_module.py verify` clean. Genome still v3 (1d) live,
  untouched.

- **Run 2026-09-07 (3-hourly check, ~00:46-01:29 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 3714 → 3923, boldness/stagnation counter
  265 → 279.** No live trading this cycle (tick 24 already handled at 00:20
  UTC, confirmed via `live_state.json`'s `updated` timestamp and
  `runs/2026-09-07-0020-daily-trading.md` before starting). Freshness checks
  before running: `review-hard-calls` 0 pending, `holdout-pressure` same
  fold-clears-then-loses-holdout shape as always, `live-benchmark` now 23 1d
  bars / -12.60% excess (up from 22 bars / -11.07%, still far from the
  60-bar revisit trigger), items 2/5/6 still blocked with no new owner
  input. Champion fitness held flat at 1.422 across all 15 generations (basis
  rolled up from the last batch's 1.215 with the new UTC day, as usual — not
  a genome change); every new candidate lost to it. See
  `runs/2026-09-07-0129-evolve-batch-v3.md` for the batch detail (and a note
  to future sessions: pipe long-running `evolve` output to a file without a
  truncating `tail` at capture time, since this batch lost its first 3
  generations' log lines to exactly that). Verified before commit: `python3
  -m pytest -q` 366/366 (baseline, unchanged — no code touched), direct
  key-by-key diff of `live_state.json` showed only
  `lineage`/`researcher_memory`/`updated` changed (genome, broker, journal
  byte-identical), constitution verified `8b74865634b1db07` unchanged,
  `tools/edit_bundle_module.py verify` clean. Genome still v3 (1d) live,
  untouched.

- **Run 2026-09-06 (3-hourly check, ~21:46-22:16 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 3506 → 3714, boldness/stagnation counter
  249 → 265.** No live trading this cycle (tick 23 already handled at 00:20
  UTC, confirmed via `live_state.json`'s `updated` timestamp before starting).
  Freshness checks before running: `review-hard-calls` 0 pending,
  `live-benchmark` unchanged (22 1d bars, -11.07% excess), `holdout-pressure`
  same fold-clears-then-loses-holdout shape as always, items 2/5/6 still
  blocked with no new owner input. Champion fitness held flat at 1.215
  across all 15 generations; every new candidate lost to it. Raw
  best-of-generation fold-fitness beat the champion's own 1.215 in 7/15
  generations this batch (47%) — the second batch in a row (after 53%) to
  sit close to the pre-boldness-fix baseline (48%) rather than the higher
  post-fix rates seen in between (69%, 76%, 75%); still read as noise around
  an unsettled rate, not a reversal, but two batches in a row is worth a
  future session's attention if the pattern continues (see
  `runs/2026-09-06-2216-evolve-batch-v3.md`). Verified before commit:
  `python3 -m pytest -q` 366/366 (baseline, unchanged — no code touched),
  direct key-by-key diff of `live_state.json` showed only
  `lineage`/`researcher_memory`/`updated` changed (genome, broker, journal
  byte-identical), constitution verified `8b74865634b1db07` unchanged.
  Genome still v3 (1d) live, untouched.

- **Run 2026-09-06 (3-hourly check, ~18:46-19:16 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 3298 → 3506, boldness/stagnation counter
  234 → 249.** No live trading this cycle (tick 23 already handled at 00:20
  UTC, confirmed via `live_state.json`'s `updated` timestamp before starting).
  Freshness checks before running: `review-hard-calls` 0 pending, items 2/5/6
  still blocked with no new owner input. Champion fitness held flat at 1.215
  across all 15 generations; every new candidate lost to it. Raw
  best-of-generation fold-fitness beat the champion's own 1.215 in 8/15
  generations this batch — a lower share (53%) than the last two batches
  (76%, 75%), closer to the pre-boldness-fix baseline (48%); read as small-n
  noise around a rate this file hasn't yet pinned down precisely, not a
  reversal of the fix's effect (see `runs/2026-09-06-1916-evolve-batch-v3.md`).
  Verified before commit: `python3 -m pytest -q` 366/366 (baseline,
  unchanged — no code touched), direct key-by-key diff of `live_state.json`
  showed only `lineage`/`researcher_memory`/`updated` changed (genome,
  broker, journal byte-identical), constitution verified `8b74865634b1db07`
  unchanged, `tools/edit_bundle_module.py verify` clean. Genome still v3
  (1d) live, untouched.

- **Run 2026-09-06 (3-hourly check, ~15:46-16:27 UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 3090 → 3298, boldness/stagnation counter
  219 → 234.** No live trading this cycle (tick 23 already handled at 00:20
  UTC, confirmed via `live_state.json`'s `updated` timestamp before starting).
  Freshness checks before running: `review-hard-calls` 0 pending, items 2/5/6
  still blocked with no new owner input. Champion fitness held flat at 1.215
  across all 15 generations; every new candidate lost to it. Continuing the
  boldness-fix ratio tracking: raw best-of-generation fold-fitness beat the
  champion's own 1.215 in 12/15 generations this batch, bringing the combined
  post-fix rate to 57/75 (76%) vs. the pre-fix 12/25 (48%) — still trending
  the same direction each batch, not yet declared settled (see
  `runs/2026-09-06-1627-evolve-batch-v3.md`). Verified before commit:
  `python3 -m pytest -q` 366/366 (baseline, unchanged — no code touched),
  direct key-by-key diff of `live_state.json` showed only
  `lineage`/`researcher_memory`/`updated` changed (genome, broker, journal
  byte-identical), constitution verified `8b74865634b1db07` unchanged,
  `tools/edit_bundle_module.py verify` clean. Genome still v3 (1d) live,
  untouched.

- **Run 2026-09-06 (3-hourly check, ~12:47-13:2x UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 2881 → 3090, boldness/stagnation counter
  204 → 219.** No live trading this cycle (tick 23 already handled at 00:20
  UTC, confirmed via `live_state.json`'s `updated` timestamp before starting).
  Freshness checks before running: `review-hard-calls` 0 pending,
  `holdout-pressure` and `live-benchmark` (22 bars, -11.07% excess) both
  unchanged from this morning, items 2/5/6 still blocked with no new owner
  input. Champion fitness held flat at 1.215 across all 15 generations; every
  new candidate lost to it. Continuing the boldness-fix ratio this morning's
  entry flagged as worth tracking: raw best-of-generation fold-fitness beat
  the champion's own 1.215 in 14/15 generations this batch, bringing the
  combined post-fix rate to 45/60 (75%) vs. the pre-fix 12/25 (48%) — still
  trending the same direction each batch, not yet declared settled (see
  `runs/2026-09-06-1328-evolve-batch-v3.md`). Verified before commit:
  `python3 -m pytest -q` 366/366 (baseline, unchanged — no code touched),
  direct key-by-key diff of `live_state.json` showed only
  `lineage`/`researcher_memory`/`updated` changed (genome, broker, journal
  byte-identical), constitution verified `8b74865634b1db07` unchanged. Genome
  still v3 (1d) live, untouched.

- **Run 2026-09-06 (3-hourly check, ~09:46-10:26 UTC): 20 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 2602 → 2881, boldness/stagnation counter
  184 → 204.** No live trading this cycle (tick 23 already handled at 00:20
  UTC, confirmed via `live_state.json`'s `updated` timestamp and
  `runs/2026-09-06-0020-daily-trading.md` before starting). Freshness checks
  before running: `review-hard-calls` 0 pending, `holdout-pressure` same
  fold-clears-then-loses-holdout shape as every recent run (nothing new),
  items 2/5/6 still blocked per this morning's
  `runs/2026-09-06-0900-daily-discussion.md` with no new input. Champion
  fitness held flat at 1.215 across all 20 generations; every new candidate
  lost to it. This batch ran under the boldness-saturation fix shipped
  earlier today and continues the ratio the fix's own entry below flagged
  as worth tracking: raw best-of-generation fold-fitness beat the champion's
  1.215 in 14/20 generations here, bringing the combined post-fix rate to
  31/45 (~69%) vs. the pre-fix batch's 12/25 (48%) — still consistent with
  the fix restoring more local competitive search, though not yet declared
  settled (see `runs/2026-09-06-1026-evolve-batch-v3.md`). Verified before
  commit: `python3 -m pytest -q` 366/366 (baseline, unchanged — no code
  touched), direct key-by-key diff of `live_state.json` showed only
  `lineage`/`researcher_memory`/`updated` changed (genome, broker, journal
  byte-identical), constitution verified `8b74865634b1db07` unchanged,
  `tools/edit_bundle_module.py verify` clean. Genome still v3 (1d) live,
  untouched.

- **Fixed 2026-09-06 (weekend all-hands, ~08:xx UTC): two real lineage/genome-
  reconstruction integrity bugs, found while chasing a failing test during
  this session's own evolve batches — both now fixed and tested, and both
  affect every past session's `--also-version N` / `succession-audit` /
  `fold-scheme` numbers that ran in the same container after an `evolve`
  call, not just this session.** See `runs/2026-09-06-0600-weekend-all-hands.md`
  for the full account. Summary of each:
  1. **`LiveAccount.save()`'s bare `lineage[-200:]` truncation silently
     drops an old *accepted* promotion record** once enough generations
     have run since it — the v1->v2 patch had already scrolled off after
     this session's second evolve batch (135+ generations run against v3
     alone; the account's whole life has run far more). Every diagnostic
     that reconstructs a historical champion from lineage
     (`_reconstruct_champion_genome`, and everything built on it) silently
     breaks once this happens — confirmed directly:
     `test_reconstructed_v3_matches_real_live_lineage_bit_exact` started
     failing this session for exactly this reason. New `core.live._trim_lineage()`
     keeps the last 200 entries as before but never drops an `accepted`
     one, wherever it sits. The already-lost v1->v2 record was recovered
     from a prior commit's `live_state.json` (still had it) and merged back
     in — nothing was unrecoverable, but a future occurrence without a
     recent commit to recover from would have permanently lost that
     promotion's patch. 6 new tests, `tests/test_live_account.py`.
  2. **`_reconstruct_champion_genome`'s version-1 base used `Genome.champion()`,
     which reads whatever `state/genomes/champion.json` currently holds on
     disk — and the `evolve` command unconditionally overwrites that file
     with the *live* champion at the start of every run** (`g0.save("champion")`,
     so it can diff before/after to detect a real promotion). So any
     reconstruction diagnostic run in the same container *after* an `evolve`
     call was silently rebuilding every requested version from the live
     champion's genes instead of the true v1 seed — a patch only overwrites
     the specific genes it names, so anything else still leaked in from the
     wrong base. Confirmed live: `succession-audit` was reporting byte-identical
     numbers for v1/v2/v3 this session, right after this session's own evolve
     batches had overwritten `champion.json`. Fixed to use `Genome()` (the
     hardcoded seed, no disk I/O) instead. 2 new regression tests reproduce
     the exact stale-cache scenario (`tests/test_fold_scheme_reconstruction.py`).
     Re-ran `succession-audit` against the real repo after the fix: v1/v2/v3
     now come out properly distinct and match the historical record (v1
     hard-fails on drawdown, v2 doesn't, v3 live doesn't — consistent with
     the 2026-08-22 finding this diagnostic was built to report on).

  **Why this matters for reading older "Current state" entries**: any past
  session's `fold-scheme --also-version N`, `succession-audit`,
  `promotion-excess-check`, or similar reconstruction-based diagnostic could
  have silently returned wrong numbers for non-live versions *if that same
  container had already run `evolve` earlier in the session* (a fresh
  container, or a diagnostic run before any `evolve` call that session,
  would have been unaffected — `Genome.champion()` only drifts from the true
  seed after something writes to `state/genomes/champion.json`). This is
  not a reason to distrust every historical number in this file; it is a
  reason not to silently trust an old `--also-version` result either,
  without knowing that session's exact command order. Not re-audited here —
  that would mean re-running a lot of already-expensive diagnostics against
  history no scheduled session can reconstruct (whether `state/genomes/`
  was already polluted at the time is not recorded anywhere) — flagged so a
  future session treats any specific old finding it actually depends on as
  worth a fresh re-run rather than an inherited fact, not so this becomes a
  standing project.

  Neither fix touches the constitution or the checksummed surface (`core.live`
  and the bundle's own CLI helpers aren't part of it, same precedent as every
  prior fold-scheme/margin-curve/succession-audit change to this area). Full
  suite 366/366 (was 358, +8). `tools/edit_bundle_module.py verify` clean.

- **Run 2026-09-06 (weekend all-hands, ~06:00-08:xx UTC): two real `evolve`
  batches (25 then 25) against the live v3 (1d) champion, no promotion —
  cumulative candidates tried against v3 rose 1904 → 2602, boldness/
  stagnation counter 134 → 184.** No live trading this cycle (tick 23
  already handled at 00:20 UTC, confirmed via `live_state.json`'s `updated`
  timestamp and `runs/2026-09-06-0020-daily-trading.md` before starting) —
  deliberately, per this session's own instructions: weekend sessions are
  for evolution/self-improvement depth, not day-to-day trading. Freshness
  checks before starting: 0 pending hard-call reviews, `live-benchmark`
  unchanged (-11.07% excess, 22 bars, nowhere near the 60-bar revisit
  trigger), `holdout-pressure`/`margin-curve` both re-confirmed their
  already-understood shape (fold-aggregate margin nearly saturated,
  holdout margin still on the steep part of its curve — no new information,
  both already closed threads per `margin-curve`'s own 2026-08-21 entry).
  Items 2/5/6 still genuinely blocked on an owner decision. First batch
  (25 generations) ran under the *pre-fix* `Researcher.perturb`; partway
  through committing it, a concurrent session's `b73c243` landed (the
  boldness-saturation fix — see the entry above this one, from a different
  session on 2026-09-06 ~06:55 UTC), rebased cleanly, and this session's
  second batch (25 more generations) ran under the *fixed* code specifically
  to see whether restored local exploitation changed anything real, given
  the live champion (boldness 134+ going in) was already well past both of
  that fix's flagged saturation points. Champion fitness held flat at 1.215
  across all 50 generations; no candidate cleared the full gate. **One
  observation worth tracking, not yet a conclusion**: raw fold-fitness beat
  the champion's own 1.215 in 17/25 generations in the post-fix batch vs.
  12/25 in the pre-fix batch — consistent with the fix restoring more local
  competitive search, but n=25 per batch is too small to call this settled;
  a future session should keep an eye on this ratio across the next several
  batches rather than treat one before/after pair as proof. Both batches
  verified before commit: `python3 -m pytest -q` 358→366/366 (rising only
  from the integrity-fix commit's own new tests, not from evolve itself),
  only `live_state.json` changed each time (lineage/researcher_memory/
  updated — genome, broker, journal byte-identical), constitution
  `8b74865634b1db07` unchanged throughout, no protected file touched.
  Genome still v3 (1d) live, untouched. Dashboard rebuilt after both
  batches and the lineage repair above.

- **Shipped 2026-09-06 (3-hourly check, ~06:47-07:xx UTC): `Researcher.perturb`'s
  boldness-driven widening was silently saturating into "always fully
  randomize the genome," with zero local exploitation left — fixed to
  reserve a fixed local slice of every batch regardless of stagnation.** Six
  straight 3-hourly cycles (2026-09-05 12:46 through 2026-09-06 04:2x, see
  the entries below) ran plain `evolve` against the live v3 champion and
  found literally nothing new each time — same flat 1.215 fitness, same
  local optimum. Rather than run a seventh identical batch, checked *why*
  the search keeps landing in the same place: `perturb(n, n_genes=2,
  boldness)` computes `jump_p = min(0.75, 0.2 + 0.12*boldness)` and
  `genes_per = min(len(GENE_SPACE), n_genes + boldness//2)` — both are
  capped, and `jump_p` saturates by boldness ≈4.6 while `genes_per`
  saturates (at all 44 genes) by boldness ≈92. The live champion's
  stagnation/boldness counter is already 134 (see the 3 entries below) — it
  passed both saturation points roughly 40+ generations ago. Past that
  point every blind-search candidate mutates the *entire* genome at once,
  each gene independently getting a 75% chance of an outright uniform
  redraw across its full allowed range (the remaining 25% "local jitter"
  branch scales its own spread by the same unbounded `boldness`, so at this
  level it isn't meaningfully more local either) — the docstring's intended
  "widen search under stagnation, don't abandon it" design had already
  become, in practice, "only ever fully randomize the genome," for a large
  and growing fraction of this account's evolution history, without any
  run note ever measuring the saturation points directly. Verified this
  numerically before changing anything (`python3 -c` computing
  `jump_p`/`spread`/`genes_per` across boldness 0/4/5/10/20/50/100/134 —
  see the commit diff's new docstring for the exact figures) and confirmed
  no prior "Current state" entry had flagged it. **Fix**: `perturb` now
  reserves `max(1, n//4)` of every batch's candidates to always run at
  boldness 0 (narrow, 1-2 gene, small jitter) regardless of how high the
  real `boldness` argument is; the remaining candidates keep the existing
  graduated-widening behavior unchanged. At `boldness=0` (every run's
  starting point) behavior is byte-for-byte identical to before — verified
  both by code inspection (the local-slice branch is gated on `boldness >
  0`) and by the existing `test_propose_non_blind_proposals_are_seed_independent_only_perturb_varies`
  test passing unmodified. New `tests/test_researcher_perturb_boldness.py`
  (3 tests): boldness=0 unaffected, a high-boldness (134) batch still
  contains both narrow (≤2-gene) and wide (full-genome) candidates, and the
  local-slice sizing scales sanely with batch size. Full suite 358/358 (was
  355, +3). This is a search-mechanism change, not a constitution or
  fitness-function change — `agents/researcher.py` is not one of the two
  files `constitution.checksum()` hashes (only `constitution` and
  `core.portfolio` are), so no re-seal is needed, and it changes what
  candidates get *proposed*, never the acceptance gates that decide whether
  one gets promoted, so it cannot make a bad promotion more likely — it can
  only make finding a genuinely better candidate somewhat more likely by
  keeping local exploitation alive alongside wide exploration. Edited the
  real `agents/researcher.py` (the actual source of truth per item 7) and
  re-synced the bundle with `tools/edit_bundle_module.py sync` — `sync
  --check` confirms bundle and real files match. Verified before commit:
  `live_state.json` untouched (md5 identical before/after, this entry never
  ran `evolve`/`tick`), constitution verified `8b74865634b1db07` unchanged,
  no protected file touched, `tools/edit_bundle_module.py verify` clean.
  Genome still v3 (1d) live, untouched. No live trading this cycle (tick 23
  already handled at 00:20 UTC, confirmed via `live_state.json`'s `updated`
  timestamp before starting). **Next**: the next `evolve` batch against the
  live v3 champion will be the first to actually exercise this fix for
  real — worth noting in that batch's run note whether the reserved local
  slice ever finds anything the fully-saturated wide search couldn't in the
  last 40+ generations, though a single batch either way won't be
  conclusive on its own.

- **Run 2026-09-06 (3-hourly check, ~03:47-04:2x UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 1694 → 1904, boldness/stagnation counter
  120 → 134.** No live trading this cycle (tick 23 already handled at 00:20
  UTC, confirmed via `live_state.json`'s `updated` timestamp and
  `runs/2026-09-06-0020-daily-trading.md` before starting). Re-checked
  whether anything had changed since the prior cycle's freshness pass before
  running a sixth-in-a-row plain evolve batch: `review-hard-calls` still 0
  pending, `live-benchmark` still 22 1d bars/-11.07% excess (unchanged,
  nowhere near item 0's 60-bar revisit trigger — only 8 of the required 60
  additional bars elapsed since the 2026-08-30 baseline of 15), and
  `holdout-pressure` shows the same fold-clears-then-loses-holdout shape as
  every recent run. Items 2/5/6 still genuinely blocked on an owner decision
  with no new input since yesterday. Concluded, same as the prior cycle, that
  nothing else was unblocked or differently-shaped enough to prefer over
  continuing real cumulative search against the actual live champion.
  Champion fitness held flat at 1.215 across all 15 generations; every new
  candidate lost to it — same local optimum as every recent batch, not a new
  finding. Verified before commit: only `updated`/`lineage`/`researcher_memory`
  changed in `live_state.json` (genome, broker, journal all byte-identical —
  confirmed by direct key-by-key comparison against the pre-run commit, not
  just `git diff --stat`), `python3 -m pytest -q` 355/355 (baseline,
  unchanged — no code touched), constitution verified `8b74865634b1db07`
  unchanged, no protected file touched. Genome still v3 (1d) live, untouched.

- **Run 2026-09-06 (3-hourly check, ~00:46-01:1x UTC): 10 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 1554 → 1694, boldness/stagnation counter
  110 → 120.** No live trading this cycle (tick 23 already handled at 00:20
  UTC, confirmed via `live_state.json`'s `updated` timestamp and
  `runs/2026-09-06-0020-daily-trading.md` before starting). Checked the
  prior session's flagged concern (four straight identical evolve batches
  on 2026-09-05 with no new information) directly rather than repeating a
  fifth batch blind: `review-hard-calls` still 0 pending, items 2/5/6 still
  blocked with no new owner input since yesterday's 09:00 UTC daily
  discussion, and re-ran `live-benchmark` (22 1d bars, excess -11.07%,
  nowhere near item 0's 60-bar revisit-trigger threshold) and
  `holdout-pressure` (same fold-clears-then-loses-holdout shape, nothing
  new) as a freshness check before concluding no differently-shaped
  diagnostic was actually ready to run instead. Champion fitness held flat
  at 1.215 (today's evaluation basis) across all 10 generations; every new
  candidate lost to it — same local optimum as every recent batch. Verified
  before commit: `python3 -m pytest -q` 355/355 (baseline, unchanged — no
  code touched), `git diff --stat` showed only `live_state.json`
  (researcher_memory) and `index.html` (dashboard rebuild), constitution
  verified `8b74865634b1db07` unchanged, no protected file touched. Genome
  still v3 (1d) live, untouched.

- **Run 2026-09-05 (3-hourly check, ~18:46-19:3x UTC): 15 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 1344 → 1554, boldness/stagnation counter
  95 → 110.** No live trading this cycle (tick 22 already handled at 00:20
  UTC, confirmed via `live_state.json`'s `updated` timestamp before
  starting). Fourth consecutive 3-hourly cycle today picking plain `evolve`
  over anything else — same reasoning as the two batches below (items 2/5/6
  still blocked on an owner decision with no new response since the 09:00
  UTC daily discussion; item 4 has 0 pending hard-call reviews; item 7 is
  feature-complete) — explicitly weighed whether repeating the same action a
  fourth time was still worth it given three straight batches of zero new
  information, and concluded yes: the multiple-testing margin's cost of
  continuing is negligible (`sqrt(2*ln(n))` barely moves for a few hundred
  more candidates) and nothing else is unblocked. Used the plain
  `nohup ... &` + `Monitor`/`kill -0` polling pattern documented in the
  15:47 UTC entry (worked cleanly, ~45 min for 15 generations). Champion
  fitness held flat at 1.055 across all 15 generations; several generations'
  best fold-aggregate candidate beat the champion's own raw fitness (up to
  1.981) but none cleared the full gate — same fold-clears-then-loses-holdout
  shape as every recent batch. Verified before commit: `python3 -m
  pytest -q` 355/355 (baseline, unchanged — no code touched), `git diff
  --stat` showed only `live_state.json` (researcher_memory) and
  `index.html` (dashboard rebuild), constitution verified
  `8b74865634b1db07` unchanged, no protected file touched. Genome still v3
  (1d) live, untouched. **Flagged for the next session**: four straight
  plain-evolve cycles today have produced consistent negative evidence but
  no new information — worth considering a differently-shaped diagnostic
  instead of a fifth identical batch, if the owner-decision landscape (items
  2/5/6) still hasn't moved.

- **Run 2026-09-05 (3-hourly check, ~15:47-17:1x UTC): 10 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 1204 → 1344, boldness/stagnation counter
  84 → 94.** No live trading this cycle (tick 22 already handled at 00:20
  UTC, `live_state.json`'s `updated` timestamp confirmed before starting).
  Same reasoning as the 12:46 UTC entry below for picking evolve: items
  2/5/6 still genuinely blocked on an owner decision (no new response since
  the 09:00 UTC daily discussion), item 4 has 0 pending hard-call reviews,
  item 7 is feature-complete. Champion fitness held flat at 1.055 across
  all 10 generations; a few generations' best fold-aggregate candidate beat
  the champion's own fitness (up to 1.454) but none cleared the full gate —
  same fold-clears-then-loses-holdout shape as every recent batch, not new.
  **Operational note for future sessions**: the harness's own
  `timeout N python3 evotrader_bundle.py evolve N` backgrounding killed a
  25-generation attempt (exit 143) after ~45-50 minutes with zero progress
  saved — some outer limit on that specific backgrounding path shorter than
  a 25-generation run needs. This is distinct from Next-steps item 9's
  `nohup`-inside-one-tool-call warning (which is about losing the tool's
  own completion signal, not the process dying). Fix used here: a plain
  detached `nohup python3 evotrader_bundle.py evolve N > log 2>&1 &`,
  polled to completion with a `kill -0 <pid>` loop rather than relying on
  either backgrounding path's own completion signal — worked cleanly for a
  smaller (10-generation) batch. If a future session hits the same exit-143
  killed-early symptom on a longer run, try this fix (or a smaller N) before
  concluding `evolve` itself is broken. Verified before commit: `python3 -m
  pytest -q` 355/355 (baseline, unchanged — no code touched), `git diff
  --stat` showed only `live_state.json` (researcher_memory) and
  `index.html` (dashboard rebuild), constitution verified `8b74865634b1db07`
  unchanged, no protected file touched. Genome still v3 (1d) live, untouched.

- **Run 2026-09-05 (3-hourly check, ~12:46-13:5x UTC): 20 more real `evolve`
  generations against the live v3 (1d) champion, no promotion — cumulative
  candidates tried against v3 rose 924 → 1204, stagnation counter 65 → 84.**
  No live trading this cycle (tick 22 already handled at 00:20 UTC, confirmed
  via `live_state.json`'s `updated` timestamp and
  `runs/2026-09-05-0020-daily-trading.md` before starting). Picked plain
  real-champion `evolve` over anything else because items 2/5/6 are still
  genuinely blocked on an owner decision (see "Owner decisions pending"),
  item 4 has 0 pending hard-call reviews (`review-hard-calls` confirmed),
  and item 7 is feature-complete with no reason to keep widening it — so
  accumulating more real cumulative search against the actual live champion
  was the highest-value use of this slot, same reasoning as the weekend
  all-hands entry below. Champion fitness held flat at 1.055 across all 20
  generations — every one of the ~280 new candidates this cycle generated
  lost to it, continued evidence for a real local optimum from this starting
  point (`holdout-pressure` re-checked too: still only fold-clears that lose
  the sealed holdout, nothing new). Verified before commit: `python3 -m
  pytest -q` 355/355 (baseline, unchanged by this — no code touched),
  `git diff --stat` showed only `live_state.json` (researcher_memory's
  `tested` list growing plus the stagnation counter), constitution verified
  `8b74865634b1db07` unchanged, no protected file touched. Genome still v3
  (1d) live, untouched.

- **Shipped 2026-09-05 (3-hourly check, ~09:46-10:xx UTC): the dashboard's
  `genome` stat tile now surfaces the per-champion `researcher_memory`
  tally (candidates tried, none better yet) instead of only the lifetime
  generation count — a small, non-live-state-touching improvement picked
  because items 2/5/6 are all genuinely blocked on an owner decision (see
  "Owner decisions pending") and item 4 has no pending flagged case to
  review, so a plain `evolve N` run against the real champion (this
  scheduled task's own guidance: avoid touching `live_state.json` unless
  actually promoting) wasn't the right default this cycle.** New
  `evotrader_dashboard._genome_sub(live, champ, lineage)` reads
  `researcher_memory.tested`/`champion_version` (already in
  `live_state.json`, e.g. 924 tried against the live v3 champion as of this
  writing) and appends "N challenger idea(s) tried since, none better yet"
  to the existing "N generation(s) run" subtitle only when
  `researcher_memory.champion_version` matches the current genome's
  version — guards against showing a stale count right after a promotion,
  before memory reseeds. New `tests/test_dashboard_champion_stat.py` (4
  tests: matching-champion count shown, stale-memory mismatch omits it,
  missing `researcher_memory` doesn't crash, empty `tested` list omits the
  suffix) — first tests this file has ever had. Full suite 355/355 (was
  351, +4). Rebuilt `index.html` (`EVO_STATE=... python3
  evotrader_dashboard.py`) and confirmed the new text renders correctly
  against the real live state; `live_state.json` itself untouched (no
  diff, not even opened for writing) and no protected file touched.
  Genome still v3 (1d) live, untouched. Daily bar already handled at 00:20
  UTC (tick 22, confirmed via `live_state.json`'s `updated` timestamp and
  `runs/2026-09-05-0020-daily-trading.md` before starting); no tick this
  cycle. `review-hard-calls` confirmed 0 pending.

- **Run 2026-09-05 (weekend all-hands, ~06:00-08:xx UTC): 45 more real
  `evolve` generations against the live v3 (1d) champion in two batches (25
  then 20), no promotion — cumulative candidates tested against v3 rose
  280 → 924, stagnation counter 45 → 65 (the expected "wider steps" boldness
  growth as a champion survives longer, not a new finding).** No live
  trading this cycle (tick 22 already handled at 00:20 UTC, confirmed via
  `live_state.json`'s `updated` timestamp and
  `runs/2026-09-05-0020-daily-trading.md` before starting) — deliberately:
  weekend sessions are for evolution/self-improvement depth, not day-to-day
  trading. Chose plain real-champion `evolve` over another 4h-shadow seed
  because item 2 (4h-bar family) was freshly re-investigated this same
  session (see next entry) and found to be a resource-allocation call, not
  something more shadow search would sharpen; a large real-`evolve` push
  against the actual live champion is the one form of "go deep on
  evolution" available this session that isn't blocked on an owner
  decision. Both batches verified before commit: `python3 -m pytest -q`
  351/351 after each, `git diff --stat` showed only `live_state.json`
  (researcher_memory's `tested` list growing plus the stagnation counter),
  constitution verified `8b74865634b1db07` unchanged, no protected file
  touched. Committed and pushed separately per batch
  (`Evolve: 25 more generations...` then `Evolve: 20 more generations...`)
  rather than held to one end-of-session commit. Champion v3 fitness held
  flat at 1.055 across all 45 generations — every one of the ~630 new
  candidates this session generated lost to it; reads as continued evidence
  v3 sits in a real local optimum for blind/structural search from this
  starting point, not as a null result worth investigating further on its
  own (this is exactly what "accumulate live forward-test data" / ordinary
  `evolve` cumulative search is supposed to look like most of the time).

- **Sharpened 2026-09-05 (weekend all-hands, ~06:xx UTC): item 2's
  "owner's call" framing checked directly against the real gate/holdout
  rather than re-asserted — see the "Owner decisions pending" section
  above for the full write-up (added to that section directly rather than
  duplicated here).** Confirmed via a full read of the `consv1 +
  trailing_stop + ramp` thread's run notes: the stack has cleared the real
  fold gate once but flips to hard-fail within about a day of added data
  (4-6 of 7 nearby daily shifts fail), has never reached the sealed
  holdout, and the mechanical next step (`--recipe consv_trailing_ramp`
  through a full `evolve()` including holdout) needs no new tooling — so
  the block is genuinely "spend a real promotion attempt on a fragile
  genome," a resource/risk-appetite decision, not a disguised technical
  unknown. Read-only research (one Explore agent over existing run notes +
  AGENTS.md), no code or state touched by this entry itself.

- **Confirmed 2026-09-04 (3-hourly check, ~00:46-01:xx UTC): the recurring
  "identical candidate across fresh seeds" pattern in the 4h-shadow-evolution
  thread (item 2) is guaranteed by construction, not a coincidence — verified
  by reading the code, not by running a sixth shadow seed.** No live trading
  this cycle (tick 21 already handled at 00:20 UTC, confirmed via
  `live_state.json`'s `updated` timestamp and
  `runs/2026-09-04-0020-daily-trading.md` before starting). `git_sync.py`
  worked cleanly again (plain fast-forward, no divergence this time).
  `agents.researcher.Researcher.propose()`'s own docstring already says
  `from_diagnosis`/`structural` are "deterministic given the champion" and
  that's *why* `exclude`/`researcher_memory` exists — but nothing tested that
  claim directly, and three separate run notes (seeds 9102/9104/9105) read
  the recurring `remove_agent`-on-`consult_moderate` candidate as merely
  "suggestive" evidence of this rather than confirmed. New
  `tests/test_researcher_structural_determinism.py` (6 tests) proves it
  directly: `structural()` and `from_diagnosis()` return byte-identical
  proposal sets across arbitrary RNG seeds for the same champion+diagnostics
  (only `perturb()`, the blind-search leg, varies with seed), and a fresh
  `Researcher.propose()` call with no `exclude` set — exactly what every
  from-scratch shadow `EvolutionRun` starts with — is *guaranteed* to
  re-propose removing `consult_moderate` at generation 1 regardless of seed;
  `exclude`ing that one key removes it, confirming the fix already in the
  codebase. **Correction this sharpens for item 2's tally**: the "5
  seeds/9 generations, 3 fold-clears" framing in Next steps below counted 3
  fold-clears as 3 independent pieces of evidence: they are one deterministic
  proposal recurring three times because each shadow session started a
  memory-less `EvolutionRun` rather than carrying `researcher_memory`
  forward — real independent search evidence from this thread is closer to
  "0 fold-clears from anything but this one guaranteed candidate," a
  materially weaker basis than the existing tally implied. Does not decide
  item 2's accept-vs-redirect fork (still the owner's call, already flagged
  three times this week) — strengthens, not reverses, every prior session's
  recommendation to stop running fresh `x6` seeds. Full suite 351/351 (was
  345, +6 new). `live_state.json` untouched (md5 `81aa743fa71f116be9ba8dbf91d3de96`
  unchanged before/after), no protected file touched, `tools/edit_bundle_module.py
  sync --check` clean (test-only change, no `_SRC` module edited). Genome
  still v3 (1d) live, untouched.

- **Shipped 2026-09-03 (3-hourly check, ~21:46-22:xx UTC): `tools/git_sync.py`
  turns the 09:46 UTC entry's documentation fix into an actual runnable
  script, since this session hit the exact same shallow-clone divergence
  right at startup and, like several before it, resolved it by hand
  (`git reset --hard origin/main`) rather than trying the documented
  non-destructive check first — a small process gap worth closing rather
  than writing yet another prose paragraph about it.** No live trading this
  cycle (tick 20 already handled at 00:20 UTC, confirmed via
  `live_state.json`'s `updated` timestamp and the 20:30 UTC evaluation note
  before starting). No shadow research either — item 2's accept-vs-redirect
  call remains flagged for the owner (09:00 UTC daily discussion), nothing
  new to add there. New `sync(cwd, branch)` runs the Run protocol step 2
  sequence: checkout the branch if detached, unshallow if needed, fast-
  forward if a real merge-base exists, and only `reset --hard origin/main`
  if the fetch still shows a genuine rewrite (no merge-base even with full
  history) — and even then, refuses if the working tree is dirty rather than
  clobbering uncommitted work (the one case hand-run sessions under time
  pressure could get wrong). 7 new tests (`tests/test_git_sync.py`) against
  real local git repos (file:// remotes, no network): up-to-date fast-
  forward, behind-origin fast-forward, detached-HEAD checkout, shallow-clone
  unshallow-and-fast-forward, genuine-divergence reset (built via an orphan
  branch so it's a real disjoint history, not just a same-lineage
  `reset --hard`+recommit), genuine-divergence-with-dirty-tree abort, and
  not-a-git-repo error. Full suite 345/345 (was 338, +7). Verified against
  the real repo too: `python3 tools/git_sync.py` on this already-synced
  clone printed `fast-forwarded -- Already up to date.`, no-op as expected.
  Updated Run protocol step 2 (this file) to point at the script, keeping
  the hand-run sequence as a documented fallback. `live_state.json`
  untouched (md5 unchanged), genome still v3 (1d) live, no protected file
  touched, constitution unaffected.

- **Fixed 2026-09-03 (3-hourly check, ~09:46-10:xx UTC): the recurring
  "detached HEAD, no common ancestor" git situation is a shallow-clone
  artifact, not a real force-push — Run protocol step 2 now says so and gives
  the safe fix.** No code shipped, no shadow research this cycle (item 2's
  accept-vs-redirect call was already flagged for the owner by this morning's
  09:00 UTC daily discussion, and three prior sessions already recommended
  against a sixth `x6` seed — nothing new to add there, so this cycle picked
  up a different, safe, small improvement instead of manufacturing more of
  the same). This session's own clone hit the same divergence every recent
  session has hit (`git log --oneline main -3` vs `origin/main -3` showed no
  shared commits) — `git merge-base` returned nothing at first, but that was
  because the clone is shallow (`git rev-parse --is-shallow-repository` ->
  `true`, depth 50); `git fetch --depth=200 origin main` immediately found a
  real merge-base (local `main`'s tip was an ancestor of `origin/main`, just
  58 commits behind), and `git merge --ff-only origin/main` applied cleanly —
  no reset, nothing discarded. This is the same root cause the 09:00 UTC
  daily discussion diagnosed independently an hour earlier (`git fetch
  --unshallow`), and the same situation at least three other 3-hourly
  sessions hit on 2026-09-02/09-03 (19:00, 21:47, 00:46, 03:46 UTC), each
  resolving it a different way (`reset --hard`, `checkout -B`, `fetch
  --unshallow`) without anyone updating the protocol to say why it keeps
  happening or which fix avoids an unnecessary destructive `reset --hard`.
  Updated the Run protocol's step 2 (this file, near the top) with the actual
  cause and the non-destructive fetch-and-check-merge-base-first sequence,
  keeping `reset --hard` as the documented fallback only for a genuine
  rewrite (no merge-base even with full history). Pure documentation change —
  no code, no tests, `live_state.json` untouched (md5 identical), `python3 -m
  pytest -q` 338/338 confirmed this session (baseline, no code changed).
  Genome still v3 (1d) live, untouched. Daily bar already handled at 00:20
  UTC (tick 20, held) — confirmed via `live_state.json`'s `updated` timestamp
  and `runs/2026-09-03-0020-daily-trading.md` before starting; no tick run
  this cycle.

- **Found 2026-09-03 (3-hourly check, ~03:46-04:16 UTC): a fifth unconstrained-search
  seed clears the fold gate a third time -- but via the exact same mutation
  (disabling `consult_moderate`) that cleared it last time, with identical fold
  fitness to four decimal places -- and again fails the sealed holdout; updated
  tally is 5 seeds/9 generations, 3 fold-clears, 0 holdout-clears.** See "Next
  steps" item 2 and `runs/2026-09-03-0416-shadow-4h-x6-seed9105.md`. Ran
  `tools/shadow_4h_ramp_generation.py --recipe x6 --generations 2 --seed 9105`
  (fresh seed, distinct from 9101-9104) -- 2 real `EvolutionRun.generation()`
  calls against real 4h data, unpatched `x6` seed, read-only. Generation 1's
  `consult_moderate`-disabling candidate (fold fitness 0.0443, identical to
  seed 9104's same candidate) cleared `dd_corrected_stats()`'s drawdown gate
  cleanly, then lost the sealed holdout (-0.724 vs. champion -0.222 + margin
  2.355). Generation 2 (6 candidates) found nothing that cleared the gate.
  **The recurring identical candidate suggests this specific `remove_agent`
  proposal is a structural/deterministic member of the researcher's mutation
  set, not a fresh RNG draw -- so this fold-clear is weaker independent
  evidence than a genuinely new mutation would be.** This session's read:
  five seeds/nine generations without a single holdout-clear, with the one
  recurring fold-clear traceable to a fixed candidate rather than new search,
  is enough to recommend the next session/owner treat option (i) as exhausted
  for the `x6` recipe and make item 2's accept-vs-redirect decision explicitly
  rather than running a sixth seed -- not closed here, still the next
  session/owner's call. `live_state.json` untouched (md5 identical
  before/after), no protected file touched, `python3 -m pytest -q` 338/338
  baseline confirmed before starting (no code changed this entry). Genome
  still v3 (1d) live, untouched. Also: this session's clone again started
  detached with a local `main` sharing no common ancestor with `origin/main`
  (same stale-ref-vs-force-push situation as prior sessions) -- resolved with
  `git reset --hard origin/main` before starting, working tree was already
  clean, nothing lost.

- **Found 2026-09-03 (3-hourly check, ~00:46-01:11 UTC): a fourth unconstrained-search
  seed clears the fold gate again -- second clear in the sub-thread -- and again
  fails the sealed holdout; updated tally is 4 seeds/7 generations, 2 fold-clears,
  0 holdout-clears.** See "Next steps" item 2 and
  `runs/2026-09-03-0111-shadow-4h-x6-seed9104.md`. Ran
  `tools/shadow_4h_ramp_generation.py --recipe x6 --generations 2 --seed 9104`
  (fresh seed, distinct from 9101/9102/9103) -- 2 real `EvolutionRun.generation()`
  calls against real 4h data, unpatched `x6` seed, read-only. Generation 1's
  `consult_moderate`-disabling candidate (fold fitness 0.0443) cleared
  `dd_corrected_stats()`'s drawdown gate cleanly, then lost the sealed holdout
  (-0.770 vs. champion -0.265 + margin 2.355) -- the second fold-clear in this
  sub-thread (after seed 9102's cash-floor candidate), a different kind of
  de-risking move hitting the same holdout wall. Generation 2 (6 candidates)
  found nothing that cleared the gate. **This session's read: four seeds/seven
  generations without a single holdout-clear, including two fold-clears that
  both failed holdout cleanly for the same underlying reason, is consistent
  enough that the evidence bar for continuing option (i) vs. making item 2's
  accept-vs-redirect decision has shifted further toward the latter** -- not
  closed here, still flagged as the next session/owner's call. `live_state.json`
  untouched (md5 identical before/after), no protected file touched,
  `python3 -m pytest -q` 338/338 baseline confirmed before starting (no code
  changed this entry). Genome still v3 (1d) live, untouched. Also: this
  session's clone again started detached with a local `main` sharing no common
  ancestor with `origin/main` (same stale-ref-vs-force-push situation as the
  prior two sessions) -- resolved with `git checkout main && git checkout -B
  main origin/main` before starting, working tree was already clean, nothing
  lost.

- **Found 2026-09-02 (3-hourly check, ~21:47-22:12 UTC): a third unconstrained-search
  seed clears the fold gate zero times in 2 generations, unlike seed 9102 --
  1 of 5 generations across 3 seeds so far has ever cleared it.** See "Next
  steps" item 2 and `runs/2026-09-02-2212-shadow-4h-x6-seed9103.md`. Ran
  `tools/shadow_4h_ramp_generation.py --recipe x6 --generations 2 --seed 9103`
  (fresh seed, distinct from 9101/9102) -- 2 real `EvolutionRun.generation()`
  calls against real 4h data, unpatched `x6` seed, read-only. Both
  generations' top candidates hard-fail `dd_corrected_stats()`'s drawdown
  gate, including a hypothesis not tried elsewhere in this thread
  (`risk_judge.max_position_pct` 0.175, "circuit breaker tripped 5x --
  concentration too high", fold fitness 0.816 vs. champion's -2.531
  hard-fail sentinel -- still hard-fails). No candidate this seed produced
  ever reached the sealed holdout check. Sample is now 3 seeds/5 generations,
  1 fold-clear (which itself failed holdout), 0 candidates ever clearing
  both fold and holdout -- more evidence for "near-misses, not real
  solutions," consistent with every prior entry, flagged as worth weighing
  against treating option (i) as exhausted too. Does not touch item 2's
  owner-decision fork, not decided here. `live_state.json` untouched, no
  protected file touched, `python3 -m pytest -q` 338/338 baseline (no code
  changed this entry). Genome still v3 (1d) live, untouched. Also: this
  session's clone started detached with a local `main` sharing no common
  ancestor with `origin/main` (stale ref from before an earlier force-push
  rewrote origin's history) -- resolved with `git reset --hard origin/main`
  before starting, working tree was already clean, nothing lost.


- **Archived 2026-09-04 (3-hourly check, ~09:46-10:xx UTC): the next oldest
  slice of this log moved verbatim to
  `AGENTS_ARCHIVE_2026-08-29_to_2026-09-02.md`, to keep this file under the
  256KB single-read limit again — it had regrown from the first archival
  pass's post-cut size back up to ~242KB/3556 lines in six days, close to
  the ~15-20KB/day rate that 2026-09-03 pass predicted.** Nothing reworded,
  nothing lost — see that file (and, for anything before 2026-08-29 19:12
  UTC, `AGENTS_ARCHIVE_2026-08-15_to_2026-08-29.md`) for the full older
  history in original order; it also now carries the first archive's own
  announcement entry, since that entry was itself part of this cut. This
  file keeps everything from 2026-09-02 ~21:47 UTC onward, plus the full
  "Next steps", promotion-history, "Measured", and "Rules" sections
  (never part of either rotation). No code changed, no protected file
  touched, `live_state.json` untouched. If this file keeps growing at a
  similar rate, a future session should archive again rather than let it
  silently regrow past the limit.

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
