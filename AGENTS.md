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

- **Found 2026-09-02 (3-hourly check, ~19:00-19:27 UTC): a fresh unconstrained-search
  seed clears the real fold-aggregate hard gate for the first time in this
  sub-thread -- still fails the sealed holdout.** See "Next steps" item 2 and
  `runs/2026-09-02-1927-shadow-4h-x6-seed9102-fold-gate-cleared.md`. Ran
  `tools/shadow_4h_ramp_generation.py --recipe x6 --generations 2 --seed 9102`
  (fresh seed, distinct from 06:46-07:15 UTC's 9101) -- 2 real
  `EvolutionRun.generation()` calls against real 4h data, unpatched `x6` seed,
  read-only (never calls `save()`/`promote()`). Generation 1: same pattern as
  every prior entry, all top candidates hard-fail the gate. **Generation 2's
  top candidate (`consult_moderate.rsi_hi` 72.0->91.8, `risk_judge.cash_floor_pct`
  0.05->0.479, fold-aggregate fitness 1.231 vs. seed champion's -2.486
  hard-fail sentinel) actually cleared `dd_corrected_stats()`'s drawdown
  gate** -- the first time any candidate in this unconstrained-search
  sub-thread has done so -- **but then failed the sealed holdout** (-1.808 vs.
  champion's -0.281 + margin 2.355). Reads as a blunt de-risking move (~48%
  permanent cash floor) that happens to duck fold 1's specific drawdown
  window without adding real edge elsewhere, not a targeted fix. Nuances but
  doesn't reverse the 06:46-07:15 UTC finding: unconstrained search can
  occasionally clear the fold gate this seed has died on before, but nothing
  found across 3 generations/2 seeds so far has cleared *both* fold and
  holdout -- still a small sample. Does not touch item 2's owner-decision
  fork (accept the full stack vs. redirect), not decided here.
  `live_state.json` untouched, no protected file touched, no code changed
  this entry (`python3 -m pytest -q` 338/338 confirmed as baseline before
  starting, not re-run after since nothing changed). Genome still v3 (1d)
  live, untouched.

- **Design pass 2026-09-02 (3-hourly check, ~15:46-16:05 UTC): item 6
  (Equities/FX) has never had a design pass -- no `MarketData` class/ABC
  exists despite the item's wording, there's no single DI point to extend
  (unlike item 5's `PaperBroker`), and several crypto-specific assumptions
  (24/7 tick cadence, calendar-grid `find_gaps`, `"XXXUSDT"` symbol format,
  no asset-class genome field) are load-bearing outside any protected file.**
  See "Next steps" item 6 and
  `runs/2026-09-02-1550-equities-fx-design-pass.md`. No code shipped --
  item 2 (4h shadow evolution) hit an explicit owner-decision fork this
  morning and the two redirect options it names (item 4, item 5) are both
  currently no-ops (`review-hard-calls` 0 pending; short selling blocked on
  human sign-off), so this session picked up the next concretely-scoped
  open item instead. Flags an orphaned finding: `.env.example` already
  stages Alpaca paper-trading credentials with zero other references
  anywhere in the repo -- worth a human confirming intent before any Phase 1
  data-source work starts. Concretely scoped next step in the run note:
  pick a real data source (Alpaca vs. a free historical mirror) first, then
  an isolated additive fetcher + a session-aware `find_gaps` variant, tested
  in isolation, no wiring into `core/live.py`'s tick cadence yet.
  `live_state.json` untouched, no protected file touched,
  `python3 -m pytest -q` 338/338 (pre-existing baseline, no code changed
  this entry). Genome still v3 (1d) live, untouched.

- **Found 2026-09-02 (3-hourly check, ~12:47-13:09 UTC): `consv1` alone,
  without `trailing_stop`, does not clear fold 1's real gate at any
  threshold tried -- all three named single-lever alternatives under item
  2's "reconsider the base recipe" (SCALE, unconstrained search, consv1
  alone) are now checked and none routes around fold 1 on its own.** See
  "Next steps" item 2 and
  `runs/2026-09-02-1309-consv1-threshold-sweep-isolated.md`. New
  `tools/consv1_threshold_sweep.py` grid-searches `rsi_buy_below`
  (38.0/30.0/22.0) x `z_buy_below` (-0.8/-1.2/-1.6) on top of the bare
  `x6`-scaled seed (default `trailing_stop=-0.15`, no ramp genes, `scale=6`
  fixed), evaluated with the real `Evaluator.evaluate()` +
  `dd_corrected_stats()` gate path. 6 new tests (grid coverage, hard-fail
  flagging, and a spy-on-`.child()` check that every sweep genome leaves
  `trailing_stop`/ramp genes untouched), full suite 338/338. Result: **all 9
  grid points hard-fail `MAX_DD_HARD_FAIL`** (-42.6% to -44.3% gate max_dd,
  barely different from the -44.3% untightened baseline) -- `consv1`
  tightening alone even makes `aggregate_fitness` slightly worse (-2.450 ->
  -2.565), not better, and once `rsi_buy_below<=30.0` the `z_buy_below` leg
  has zero additional effect (every such row is bit-for-bit identical).
  **The 2026-08-31 22:07 UTC "consv1 + trailing_stop is super-additive"
  finding is now more precisely attributable: `trailing_stop` carries that
  synergy, `consv1` barely moves the gate on its own.** Recommends closing
  option (2b) as exhausted for single-lever alternatives; the open choice
  left under item 2 is whether to accept the full `consv1 + trailing_stop +
  ramp` stack and move toward a real (non-shadow) promotion attempt, or
  redirect effort elsewhere (parked short-selling Phase 1, or item 4's
  LLM-backed consults) -- not decided here, flagged for the next
  session/owner call. `live_state.json` untouched, no protected file
  touched. Genome still v3 (1d) live, untouched.

- **Found 2026-09-02 (3-hourly check, ~09:47-10:10 UTC): `SCALE=6` is not
  the cause of fold 1's cold-start drawdown -- scale 4 and scale 8 both
  hard-fail the real gate too, and worse than scale 6.** See "Next steps"
  item 2 and `runs/2026-09-02-0956-x6-scale-parametrized.md`. Parametrized
  `tools/shadow_4h_x6_seed.py`'s `SCALE=6` module constant into a `scale`
  kwarg/`--scale` CLI flag (on that tool and on
  `shadow_4h_fold_date_sensitivity.py`'s `build_genome()`, default unchanged,
  backward compatible) so option (2b)(ii) -- reconsider the x6 bar-scaling
  approach itself -- could actually be tested instead of assumed. 8 new
  tests, full suite 332/332, `tools/edit_bundle_module.py sync --check`
  clean. Ran the bare `x6` recipe (`--shift 1`) at scale 4/6/8 against real
  4h data: **all three hard-fail `MAX_DD_HARD_FAIL` (-56.5%/-44.3%/-48.0%
  gate max_dd respectively) -- scale 6 is the least-bad of the three, not an
  arbitrary pick that got lucky.** One shift/one seed, bare `x6` only -- not
  exhaustive, but consistent with every other finding in this thread: no
  single hand-picked constant (SCALE, ramp bars/scale, conviction boost, vol
  cap) fixes fold 1 alone; only the `consv1 + trailing_stop + ramp` stack
  together does. **Narrows what's left of "reconsider the base recipe" to
  the other named half -- the `consv1` consult-tightening thresholds
  (`rsi_buy_below`/`z_buy_below`) -- not yet checked in isolation.**
  `live_state.json` untouched, no protected file touched. Genome still v3
  (1d) live, untouched.

- **Found 2026-09-02 (3-hourly check, ~06:46-07:15 UTC): a pure
  Researcher-driven search starting from the unpatched `x6` seed hits the
  exact same fold-1 wall as every hand-picked patch in this thread -- option
  (2b)'s first slice is evidence against "a fresh search routes around it
  easily."** See "Next steps" item 2 and
  `runs/2026-09-02-0656-fresh-search-x6-recipe.md`. Generalized
  `tools/shadow_4h_ramp_generation.py` with a `--recipe`
  (`x6`/`consv_trailing`/`consv_trailing_ramp`) flag (reusing
  `shadow_4h_fold_date_sensitivity.py`'s `build_genome()`, 2 new tests, full
  suite 324/324, no bundle drift) so a real `EvolutionRun` could be seeded
  from the genuinely unpatched seed for the first time in this thread, not
  another hand-picked gene on the fixed 22:07 UTC `consv1 + trailing_stop`
  starting point. Ran one generation (14 proposals, seed 9101) against real
  4h data: the top pick by a wide margin -- `regime_scale.bear=0.125`
  (fold-aggregate fitness 0.856 vs champion 0.435) -- **hard-fails the real
  `dd_corrected_stats()` gate on drawdown**, read directly from
  `state/lineage.jsonl`'s rejection reason. A second candidate cleared the
  fold gate but failed the sealed holdout; a third also hard-failed. **Not
  exhaustive (one generation, one seed)**, but the search's own best idea
  drowns in the same cold-start drawdown every targeted patch has hit since
  2026-08-31 -- so the more literal reading of (2b), reconsidering the base
  recipe itself (the x6 bar-scaling approach or the `consv1` tightening, not
  just unconstrained search on top of x6), is now the more promising
  untried half, not running more generations of the same search. `--recipe
  x6` stays available in the tool for anyone who wants to try more
  generations/seeds anyway. `live_state.json` untouched, no protected file
  touched. Genome still v3 (1d) live, untouched.

- **Found 2026-09-02 (3-hourly check, ~03:47-04:13 UTC): the 01:12 UTC flip
  doesn't hold across nearby days -- one of seven days shows real risk under
  both the one-sided and two-sided view, so `dd_trust_continuous_stats`
  doesn't settle the fold-1 question either way for this genome family.**
  See "Next steps" item 2 and
  `runs/2026-09-02-0413-trust-continuous-flip-day-sensitivity.md`. Built the
  01:12 UTC entry's own named next step: new
  `tools/shadow_4h_fold_date_sensitivity_trust_check.py` (7 new tests, full
  suite 322/322) combines `fold-date-sensitivity`'s multi-day walk with
  `trust_continuous_check`'s two-sided correction, reporting both verdicts at
  every shift -- pure composition of existing, already-tested functions, no
  engine/constitution/gene change. Ran `consv_trailing` (the recipe that
  flipped) across the same 7-day walk: **2/7 shifts flip the same way (today,
  and 2026-08-27), 4/7 don't even hard-fail one-sided, but 1/7
  (2026-08-29) hard-fails under BOTH views (-46.8% one-sided, -42.9%
  two-sided)** -- real risk that day, not an artifact. Same "best
  snapshot doesn't generalize" pattern this thread has now found three times
  (grid-point instability 16:47 UTC, generation-vs-sweep boundary flip 10:27
  UTC, and now the artifact-vs-real-risk question itself). **Recommend
  against treating the two-sided correction as settling fold-1 one way or
  the other for this genome family** -- it doesn't touch "Next steps" item
  2's still-open options; (2b) (step back from this seed genome, reconsider
  the base recipe) remains the only untried option. `dd_trust_continuous_stats()`
  stays diagnostic-only. `live_state.json` untouched, no protected file
  touched. Genome still v3 (1d) live, untouched.

- **Found 2026-09-02 (3-hourly check, ~01:12 UTC): the pre-ramp fold-1
  hard-fail that started the whole cold-start-ramp gene-building effort
  three days ago is partly a fold-rebasing measurement artifact, not pure
  real risk.** See "Next steps" item 2 and
  `runs/2026-09-02-0112-trust-continuous-fold1-partial-artifact.md`. Ran
  the tool built earlier this same cycle
  (`tools/shadow_4h_trust_continuous_check.py`) against today's real 4h
  data for all three recipes in this thread. `x6` (bare seed): fold-1
  failure confirmed real under both the current one-sided gate (-44.5%
  max_dd) and the two-sided `dd_trust_continuous_stats` view (-44.3%) --
  no artifact there, the `consv1 + trailing_stop` tightening genuinely
  fixed a real problem. **But `consv_trailing` (that tightening, no ramp
  gene yet) -- the exact genome the 2026-09-01 01:14 UTC session found
  hard-failing at -44.1% and that triggered building the ramp genes in the
  first place -- flips: one-sided gate says -43.8% (hard-fail), two-sided
  `trust_continuous` says -32.7% (clears, fitness +0.406, not -inf).** The
  fold restarts the broker from flat cash right as a real but more moderate
  decline is underway, so the decline reads as a much larger fraction of
  the fold's own reset local peak than of the account's true peak.
  `consv_trailing_ramp` (120/0.20) still clears both ways (-34.8%/-32.7%).
  **Not a reversal of the 21:59 UTC "step back" recommendation, but a real
  qualification**: the ramp genes' actual contribution may be smaller than
  "fixed a hard-failing genome" -- closer to "improved an already-passing
  (under the more accurate two-sided reading) genome's one-sided number."
  Does not touch the separate, still-valid boundary-fragility finding
  (13:16/16:47 UTC) -- both a fold-rebasing overstatement and a
  boundary-fragile magnitude can be true of the same fold at once.
  Recommend against re-tuning the ramp genes over this; the concrete next
  step is checking whether today's flip holds across the `--shift`-day walk
  `fold-date-sensitivity` already does, before treating it as settled.
  `dd_trust_continuous_stats()` stays diagnostic-only, not wired into
  `accepts()` -- no gate-policy change made or proposed here, same explicit
  owner-decision framing as `succession-audit`'s own 2026-08-22 finding.
  `live_state.json` untouched, no protected file touched,
  `python3 -m pytest -q` 316/316 (no code changed this entry -- analysis
  only, using the tool already committed this cycle). Genome still v3 (1d)
  live, untouched.

- **Built 2026-09-02 (3-hourly check, ~00:50-01:12 UTC): the first slice of
  item 2's untried option (2b) -- checking whether fold 1's repeated
  near-40% drawdown is real risk or a fold-rebasing measurement artifact,
  using code that already exists rather than another hand-tuned gene.**
  See "Next steps" item 2. Every session since 2026-08-31 has treated fold
  1's from-cold-start `max_dd` as ground truth and tried to survive it (size
  ramp, conviction floor, vol cap -- all closed, see the 21:59 UTC entry
  below); none asked whether that number itself is trustworthy.
  `dd_corrected_stats()` (what `accepts()` actually gates on) is one-sided:
  it takes `min(fold-merged, continuous)`, which can only ever make max_dd
  *more* negative. But `loop.evolve.dd_trust_continuous_stats()` -- built
  2026-08-22 for the bundled `succession-audit` command, applied there only
  to past 1d champions -- is the two-sided sibling: fold-merged max_dd can
  also *overstate* true risk when a fold's own local peak rebases to a
  fresh, lower value right at its boundary (exactly what a fold starting
  cold, broker reset to flat cash, mechanically does). New
  `tools/shadow_4h_trust_continuous_check.py` applies that existing,
  already-tested function to the 4h-shadow genome family for the first
  time -- `x6`, `consv_trailing`, and `consv_trailing_ramp` (120/0.20) all
  audited in one pass, reporting per-fold max_dd plus both the current
  one-sided gate verdict and the two-sided `trust_continuous` verdict, and
  flagging any recipe where they disagree. No engine, constitution, or gene
  change -- pure composition of already-tested `Evaluator.evaluate`/
  `dd_corrected_stats`/`dd_trust_continuous_stats`, same precedent as every
  other read-only diagnostic in this codebase. 7 new hermetic tests
  (`tests/test_shadow_4h_trust_continuous_check.py`, monkeypatched
  `run_backtest` same pattern as `tests/test_continuous_max_dd.py` --
  covers the flip case, the no-flip-real-risk case, the neither-hard-fails
  case, per-fold reporting, both `format_row` branches, and the
  unknown-recipe CLI guard), full suite 316/316 (up from 309), `tools/
  edit_bundle_module.py sync --check` confirmed no drift (nothing bundled
  touched -- only a new `tools/`/`tests/` file). `live_state.json`
  untouched (md5 unchanged from the 00:20 UTC daily-trading run). Genome
  still v3 (1d) live, untouched. **The actual real-data run against all
  three recipes was still in progress when this entry was written -- see
  the next entry, or a follow-up session, for the result.** This entry
  covers only the shipped, tested tool, not yet a verdict on whether fold
  1's drawdown is real or an artifact.

- **Closed 2026-09-01 (3-hourly check, ~22:00-22:20 UTC): tested the
  volatility-scaled cold-start cap shipped earlier this same cycle against
  fold 1 -- it doesn't help either, and at magnitudes that actually bind it
  makes the drawdown worse, not better.** See "Next steps" item 2 and
  `runs/2026-09-01-2159-cold-start-vol-cap-shipped.md` (updated with this
  finding after the gene infra's own commit). The 0.3-0.8 cap range
  originally guessed at (by analogy to `consult_conservative`'s 1.10
  `max_vol` veto) was the wrong scale: direct instrumentation of fold 1's
  own first-120-bars window found the actual buy-candidate vol distribution
  there is 0.033-0.342 (p90 0.301) -- every value in that first-guess range
  is a guaranteed no-op on this fold, confirmed on the real gate (cap=0.5
  reproduces cap=0.0's numbers to 3 decimals). Swept caps actually inside
  the observed range instead: 0.30 barely bites (negligible), 0.20 and 0.05
  both make the real gate's `gate max_dd` *worse* (-34.6% -> -35.4% and
  -36.0% respectively), and 0.10-0.15 swing fold 1 from passing to
  outright hard-failing (-43.5%/-43.8% vs baseline -34.6%). No cap value
  tested, from 0.05 to 0.5, ever improves the drawdown. Not root-caused
  (plausible mechanism: shrinking early positions changes the equity
  trajectory that every later bar's sizing and slot-filling depends on, so
  the downstream trade sequence isn't just "the same trades, smaller" in a
  27-symbol multi-position system) but the sign is consistent across three
  tested magnitudes, not a single noisy draw. Gene kept (real, tested,
  no-op default, GENE_SPACE-registered -- may still help a different seed
  genome or a real `Researcher` search) but **do not hand-tune
  `cold_start_ramp_vol_cap` against this specific genome expecting a
  different sign.** `live_state.json` untouched, no protected file touched,
  no code changed this entry (diagnosis only, via uncommitted scratch
  scripts). Genome still v3 (1d) live, untouched. **This closes both halves
  of the 19:21 UTC entry's option (2a) fork -- see "Next steps" item 2 for
  what's left (option 2b, the only one untried).**

- **Built 2026-09-01 (3-hourly check, ~21:46-22:xx UTC): shipped the
  non-conviction structural lever the 19:21 UTC entry's option (2a) called
  for -- a volatility-scaled cold-start position cap.** See "Next steps"
  item 2. New `risk_judge.cold_start_ramp_vol_cap` gene (default `0.0`, true
  no-op; wired into `agents/judges.py`'s `RiskJudge.rule()`, registered in
  `agents.researcher.GENE_SPACE` as `(0.0, 3.0, "float")`, threaded through
  both shadow tools' CLIs -- `tools/shadow_4h_x6_seed.py`'s
  `build_consv_trailing_ramp_seed()` new `ramp_vol_cap` kwarg / `--ramp-vol-cap`
  flag, and `tools/shadow_4h_fold_date_sensitivity.py`'s matching
  `--ramp-vol-cap` override) caps a cold-start buy's size by the traded
  symbol's own `Features.vol` (annualised realised vol, already computed by
  the Analyst every bar -- no new plumbing needed, unlike the removed
  correlation-penalty gene which needed a new `rets_by_symbol` field) instead
  of by conviction: a symbol whose vol exceeds the cap gets its buy shrunk by
  `cap / vol`, composing multiplicatively with the existing size ramp. This
  directly targets what the 19:21 UTC entry's instrumentation found: fold 1's
  failing trades are unanimous, high-conviction (0.80-0.96) entries, so a
  conviction-based filter had no marginal band to catch, but nothing in this
  codebase currently caps position size by volatility during cold start --
  `ConservativeConsult`/`ModerateConsult` veto high-vol symbols outright
  (`max_vol` 1.10/1.60) but `RiskyConsult` (momentum/breakout) has no vol
  filter at all, so a volatile breakout can still reach the Risk Judge at
  full conviction. 12 new tests (10 in `tests/test_cold_start_ramp.py`
  covering the no-op default, shrink/no-shrink cases, fail-safe on a missing
  `Features` entry, ramp-window gating, and composition with the size ramp;
  1 each in the two shadow-tool test files), full suite 309/309,
  `tools/edit_bundle_module.py sync` run and confirmed no drift.
  `live_state.json` untouched, no protected file touched. Genome still v3
  (1d) live, untouched. **Empirical check against fold 1 (the same
  `shadow_4h_fold_date_sensitivity.py --shift 7` methodology the 19:21 UTC
  entry used for the conviction-boost gene) was still running in the
  background when this entry was written -- see the next entry below, or a
  follow-up run, for the result; this entry covers only the shipped,
  tested, no-op-by-default infrastructure, not yet a verdict on whether the
  lever actually helps.**

- **Tried 2026-09-01 (3-hourly check, ~18:46-19:21 UTC): built the "structurally
  different lever" the 16:47 UTC entry called for -- a cold-start conviction
  floor, not just a size ramp -- and it has zero measurable effect on fold 1,
  swept 0 to 80% of its allowed range.** See "Next steps" item 2 and
  `runs/2026-09-01-1921-cold-start-conviction-boost-no-bite.md`. New
  `risk_judge.cold_start_ramp_min_conviction_boost` gene (default 0.0,
  true no-op; wired into `agents/judges.py`'s `RiskJudge.rule()`, registered
  in `agents.researcher.GENE_SPACE`, threaded through both shadow tools' CLIs,
  9 new tests, full suite 303/303) vetoes marginal-conviction buys outright
  during the same cold-start window the size ramp already covers, tapering
  back to 0 by `cold_start_ramp_bars`. Tested at boost 0.0/0.15/0.40 against
  the 120/0.20 ramp point through `shadow_4h_fold_date_sensitivity.py --shift
  7`: **all three runs are byte-identical across every one of the 7 shifts**
  (6/7 hard-fail each -- also confirms the 16:47 UTC entry's finding that this
  genome family's pass rate has kept sliding across the day, now worse than
  13:16 UTC's 4/7). Instrumented `RiskJudge.rule()` directly against fold 1's
  own backtest window: of 672 buy candidates in the ramp window, conviction is
  sharply bimodal (mean 0.873, mostly unanimous 0.80-0.96 trades) with the
  only sub-0.70 candidates already below the *un-boosted* 0.30 floor -- no
  marginal band this lever can filter, so the fold-1 drawdown is adverse price
  action on already-high-conviction trades, not noisy weak entries. Diffed the
  actual filled-order list between boost=0.0 and boost=0.4 for the identical
  fold-1 backtest: identical, every field. Gene kept (real, tested, no-op
  default -- may still combine usefully in a real `Researcher` search or with
  a different seed genome) but **do not hand-tune this gene against this
  specific `consv1 + trailing_stop` genome expecting a different answer** --
  swept most of its range with a mechanistic reason for the null result, not a
  magnitude-tuning gap. `live_state.json` untouched, no protected file
  touched, `tools/edit_bundle_module.py sync --check` confirmed no drift.
  Genome still v3 (1d) live, untouched.

- **Found 2026-09-01 (3-hourly check, ~15:46-16:47 UTC): the "sweep other grid
  points for a wider margin" option is closed -- three separate sessions'
  "best point" picks for the `cold_start_ramp` genes have now each been
  checked and each fails most nearby days.** See "Next steps" item 2 and
  `runs/2026-09-01-1647-cold-start-ramp-grid-instability.md`. Parametrized
  `build_consv_trailing_ramp_seed()`/`shadow_4h_fold_date_sensitivity.py`
  (new `ramp_bars`/`ramp_start_scale` overrides, `--ramp-bars`/`--ramp-scale`
  flags, defaults unchanged, 5 new tests, full suite 290/290) so any grid
  point can be checked with the multi-day tool, not just the hardcoded
  120/0.20. Re-ran the 08:08 UTC sweep at today's data cutoff (~8h later):
  **only 20/37 points clear `MAX_DD_HARD_FAIL` now (was 35/37), and 120/0.20
  itself -- this morning's recommended point -- now hard-fails outright
  (-44.0% max_dd, was -34.6%)**, a full flip, not a marginal boundary shift.
  Took today's new top pick (`ramp_bars=150, start_scale=0.20`,
  `aggregate_fitness` 0.472) through the 7-day fold-date-sensitivity check:
  **6/7 shifts hard-fail**, worse than 120/0.20's own 4/7 from the 13:16 UTC
  check. **Recommend not running another point-in-time sweep over these two
  genes expecting a better answer** -- the pattern (best-of-day picks that
  fail almost everywhere else nearby) has now reproduced across three
  independent "best point" candidates. Two real next steps left, both bigger
  than a single 3-hourly session: a structurally different lever on fold 1
  (e.g. a stricter entry threshold during the cold-start window, not just
  smaller size), or stepping back from patching this specific `consv1 +
  trailing_stop` seed genome further. `live_state.json` untouched, `python3
  -m pytest -q` 290/290, no protected file touched, `tools/edit_bundle_module.py
  sync --check` confirmed no drift. Genome still v3 (1d) live, untouched.

- **Measured 2026-09-01 (3-hourly check, ~12:48-13:16 UTC): built the shadow
  fold-date-sensitivity tool the 10:27 UTC session flagged, and the systematic
  answer is starker than "boundary-fragile" — the ramp genome hard-fails the
  real gate on 4 of 7 recent days, not just an occasional flip.** See "Next
  steps" item 2 and `runs/2026-09-01-1316-shadow-4h-fold-date-sensitivity.md`.
  New `tools/shadow_4h_fold_date_sensitivity.py` (11 hermetic tests, no
  network) generalizes the bundled `fold-date-sensitivity` command from the
  live 1d champion to any 4h-shadow genome builder from
  `tools/shadow_4h_x6_seed.py`, and additionally applies `dd_corrected_stats()`
  at each "as-of" shift — the exact correction `EvolutionRun.generation()`
  applies before `accepts()`'s hard-fail check — so it reports whether the
  genome would actually clear `MAX_DD_HARD_FAIL` that day, not just its
  `aggregate_fitness`. `--recipe consv_trailing_ramp --shift 7` (~707s, one
  week of as-of dates against the 120/0.20 champion): 4/7 shifts hard-fail
  outright, and the 3 that clear do so by at most +5.6 points of margin —
  worse than "sits close to the line," this genome is on the wrong side of
  the line more often than not. Recommend not treating 120/0.20 (or 120/0.10)
  as a settled fix for the cold-start-fold problem; two untried next steps in
  the run note (sweep other grid points through this tool, or accept this
  seed genome's fold 1 is structurally fragile and needs a different lever).
  `live_state.json` untouched, `python3 -m pytest -q` 285/285 (up from 274),
  no protected file touched. Genome still v3 (1d) live, untouched.

- **Swept 2026-09-01 (3-hourly check, ~06:47-08:08 UTC): a real 37-point grid
  search over `cold_start_ramp_bars`/`cold_start_ramp_start_scale` finds a
  strictly better point than the 04:18 UTC session's hand pick, and a
  non-monotonic landscape.** See "Next steps" item 2 and
  `runs/2026-09-01-0808-cold-start-ramp-sweep.md`. New
  `tools/cold_start_ramp_sweep.py` (6 hermetic tests, no network) scores every
  grid point with the same real functions `EvolutionRun.generation()` calls
  before `accepts()`'s hard-fail check. 35/37 points clear
  `MAX_DD_HARD_FAIL`; the best, `ramp_bars=120, start_scale=0.20`, beats the
  prior 120/0.10 pick on the real selection metric (aggregate_fitness 0.454
  vs 0.368, same -34.6% gate max_dd, holdout still beats benchmark) — updated
  `tools/shadow_4h_x6_seed.py`'s `COLD_START_RAMP_PATCH`/
  `build_consv_trailing_ramp_seed()` to 120/0.20 (and its one dependent test)
  so future sessions don't re-derive the stale pick. Also found: two grid
  points in the interior (60/0.05, 240/0.10) hard-fail outright next to
  neighbors that clear comfortably — the two-gene landscape is genuinely
  jagged, not a smooth bowl, worth knowing before a `Researcher`-driven search
  over these genes assumes gradient-following is safe. Also flagged, not
  resolved: this session's own `aggregate_fitness` for the identical 120/0.10
  genome (0.368) doesn't match the 04:18 UTC run note's 0.467, even though
  `gate max_dd` matches exactly — same class of cross-session discrepancy as
  the 2026-08-31 07:05-vs-10:02 UTC baseline mismatch; not chased down, but
  the sweep script's numbers (reproduced twice within this session) are the
  ones to trust going forward. Not yet run through a fresh
  `EvolutionRun.generation()` as champion at the new 120/0.20 point (the
  04:18 UTC session did that for 120/0.10 and found it stable against 34
  blind proposals — the natural next check for 120/0.20). `live_state.json`
  untouched, `python3 -m pytest -q` 268/268, no protected file touched,
  `tools/edit_bundle_module.py sync --check` confirmed no drift. Genome still
  v3 (1d) live, untouched.

- **Shipped 2026-09-01 (3-hourly check, ~04:18 UTC): a cold-start position-size
  ramp gene fixes the 01:14 UTC session's fold-2 hard-fail — the first genome in
  this whole 4h-shadow thread to clear `MAX_DD_HARD_FAIL` on the real fold-based
  gate, not just a continuous replay.** See "Next steps" item 2 and
  `runs/2026-09-01-0418-cold-start-ramp-clears-fold-gate.md`. Direct follow-up to
  the 01:14 UTC session's own flagged question ("does a smaller initial position
  size in the first N bars of a fold fix it?"). New `risk_judge` genes
  `cold_start_ramp_bars`/`cold_start_ramp_start_scale` (both true no-ops at their
  defaults `0`/`1.0`) scale new buy order size up linearly over the first N bars
  since a `RiskJudge` instance's own cold start (a fresh fold, a fresh shadow run,
  a fresh live account all start at 0 again) — wired into `agents/judges.py`,
  added to `agents.researcher.GENE_SPACE` so real search can tune it. Caught and
  fixed a real bug before shipping: the first version scaled the order size
  *before* deducting it from the bar's cash/slot budget, which let the ramp free
  up room for extra positions and washed out almost the entire effect; fixed by
  keeping room/slot accounting on the un-ramped amount and only scaling what
  actually gets recorded as the order. `tests/test_cold_start_ramp.py` (5 tests)
  locks in both the no-op default and that specific semantics. Applied via new
  `tools/shadow_4h_x6_seed.py` `build_consv_trailing_ramp_seed()` (120 bars,
  0.10x start scale) to the 22:07 UTC session's dead-end `consv1 + trailing_stop
  -0.06` genome: fold 1 (the one that hard-failed) goes -44.1%→-34.6% max_dd,
  sortino 3.12→4.12, aggregate fitness -2.481→+0.467 — measured with the exact
  functions (`Evaluator.evaluate()` + `dd_corrected_stats()`) `EvolutionRun.
  generation()` calls before `accepts()`'s hard-fail check, the same real gate
  the 01:14 UTC session used to sink that genome. Fold 0 is byte-identical (the
  ramp only bites when a cold start coincides with a hard move, not a blanket
  risk-off) and holdout is essentially unchanged (still beats benchmark) — this
  isn't "just trade less," trade count actually rises slightly. One real
  `EvolutionRun.generation()` (seed 9001) ran against it as champion afterward:
  champion held against 34 blind proposals (best challenger 0.611 vs. its
  0.467) — a stability signal, not a promotion, since nothing reached the
  sealed-holdout gate. **Not yet run through a full promotion decision** (no
  established prior champion for this seed lineage to compare against) or
  through real search over the two new genes themselves (120/0.10 was
  hand-picked from a small sweep, not searched) — see "Next steps" item 2 for
  what's still open. `git status` clean, `live_state.json`
  md5 unchanged (`1b5e230bb4e7440ed8fd7778425f8ea9`), constitution checksum
  unchanged (`8b74865634b1db07`, neither protected file touched), `python3 -m
  pytest -q` 262/262 (up from 255), `tools/edit_bundle_module.py sync` run and
  confirmed no drift. Genome still v3 (1d) live, untouched.

- **Found 2026-09-01 (3-hourly check, ~01:14 UTC): the 22:07 UTC session's "first
  variant to clear MAX_DD_HARD_FAIL" genome fails the real fold-based promotion
  gate — a cold-start fold artifact, not a data-window issue.** See "Next steps"
  item 2 and
  `runs/2026-09-01-0114-4h-shadow-consv-trailing-fails-real-fold-gate.md`. Direct
  follow-up to that session's own recommendation: seeded a fresh 4h shadow
  `EvolutionRun` from its `consv1 + trailing_stop -0.06` genome (via the new
  `build_consv_trailing_seed()` in `tools/shadow_4h_x6_seed.py`, committed this
  session with 3 tests, full suite 255/255) and ran it through
  `Evaluator.evaluate()` + `dd_corrected_stats()` -- the actual functions
  `EvolutionRun.generation()` calls before `accepts()`'s hard-fail check.
  **Result: -44.1% max_dd on the real gate, still failing the 40% hard-fail** --
  contradicting the -32.7% headline. Ruled out a data-window discrepancy first
  (this thread's most common failure mode): a continuous replay over the exact
  same `[0.0, 0.85]` span the gate covers reproduces -32.7% exactly, matching
  the full-history number. The real cause: the gate's 3 walk-forward folds are
  each backtested independently from a cold start, and the middle fold
  (`[0.283, 0.567]`, roughly year 2 of 4) hard-fails on its own -- -44.1% max_dd,
  fitness `-inf`, despite a striking 3.12 sortino *within* that fold (a sharp
  V, not a slow bleed). `dd_corrected_stats()` takes the worse of fold-merged
  and continuous max_dd, so it isn't fooled by either direction, but it means a
  strategy can look fine on one continuous replay while a from-scratch restart
  partway through the same span blows through the drawdown limit -- the
  opposite failure mode from the 2026-08-22 `fold-dd-blindspot` fix (which
  worried the continuous view could hide something the fold view catches; here
  the fold view catches something worse than the continuous view shows). Also
  ran one real `EvolutionRun.generation()` (24 proposals, seed 9001) with this
  genome as champion: found candidates with much better fold-aggregate fitness
  (best 0.361 vs champion's -2.481) but every one that reached the sealed
  holdout gate failed it (3 cumulative draws, all rejected) -- champion held.
  **This specific genome is a dead end as a promotion candidate.** `git status`
  clean, `live_state.json` md5 unchanged (`1b5e230bb4e7440ed8fd7778425f8ea9`),
  `python3 -m pytest -q` 255/255 confirmed both before and after this session's
  harness commit, no `live_state.json` touch (the one `Genome.promote()` call
  reachable in `generation()` never fired -- no candidate was accepted -- and
  even when it does fire it only writes the gitignored `state/genomes/` dir),
  genome still v3 (1d) live.

- **Found 2026-08-31 (3-hourly check, ~22:07 UTC): `consult_conservative` tightening
  combined with trailing-stop tightening is super-additive — the first variant in this
  whole 4h-shadow thread (since 2026-08-16) to clear `MAX_DD_HARD_FAIL` outright.**
  See "Next steps" item 2 and
  `runs/2026-08-31-2207-4h-shadow-consv-trailing-synergy-clears-dd-gate.md`. Direct
  follow-up to the 16:00 UTC session's recommendation: paired that session's winning
  `consult_conservative`-only variant (`rsi_buy_below` 38→30, `z_buy_below` -0.8→-1.2,
  called `consv1` below) with `risk.trailing_stop` tightening (seed value -0.15). Neither
  lever alone gets close (`consv1` alone: -44.5% max_dd; `trailing_stop` alone at -0.06/
  -0.08/-0.10: -41.4%/-39.3%/-44.4%, non-monotonic and only -0.08 alone clears the gate),
  but combined, two variants clear 40% outright for the first time this thread has ever
  recorded: **`consv1` + `trailing_stop` -0.06 → -32.7% max_dd, sortino 1.35, sharpe
  1.09** (best risk-adjusted numbers this whole thread has ever produced for this seed),
  and **`consv1` + `trailing_stop` -0.08 + `cash_floor_pct` 0.15 → -35.1% max_dd, fitness
  +0.146** (first positive full-history fitness this thread has recorded — every prior
  baseline/variant landed at `-inf` or negative). Also found: pushing `consult_conservative`
  further than `consv1` (rsi 24, z -1.6) has *zero* additional effect — identical numbers —
  answering that session's own "worth trying" suggestion; and `stop_loss`/
  `max_position_pct` tightening both make drawdown worse, not better, stacked on `consv1`.
  Same continuous full-history `run_backtest()` max_dd measurement every prior session in
  this thread has used and compared against — a real, comparable improvement, not a
  different metric looking better — but **not yet run through the real promotion pipeline**
  (fold-aggregate acceptance + sealed holdout via `EvolutionRun`/`generation()`), only a
  single full-history backtest, so this doesn't itself constitute a promotable result.
  **Recommend a future session seed a fresh 4h shadow `EvolutionRun` from this genome**
  (`consv1` + `trailing_stop` -0.06, or the cash_floor variant) instead of the plain
  x6-scaled seed, and check whether it survives fold-aggregate acceptance and the sealed
  holdout as a champion in its own right — the natural next test now that this thread has
  its first real candidate worth running through the full pipeline. `git status` clean,
  `live_state.json` md5 unchanged (`37a1b00bee3f7cb1ad2f4adde0ab9ed0`), `python3 -m
  pytest -q` 252/252 confirmed at session start, no code changed (three standalone scratch
  scripts using the committed harness, not committed), genome still v3 (1d).

- **Found 2026-08-31 (3-hourly check, ~16:00 UTC): isolating the 10:02 UTC session's
  threshold-tightening by consult shows the worse-drawdown result was driven by
  `consult_risky` and `consult_moderate`, masking that `consult_conservative`-only
  tightening quietly beats baseline — and the 12:47 UTC session's carried-forward
  `correlation_penalty` recommendation is stale (that gene was removed 2026-08-20).**
  See "Next steps" item 2 and
  `runs/2026-08-31-1600-4h-shadow-isolate-consult-threshold.md`. Using the committed
  `tools/shadow_4h_x6_seed.py` harness, built three single-consult variants of the
  10:02 UTC session's nine-gene tightening plus an all-three reproduction (327.7
  trades/yr, -48.0% max_dd — matches that session's 327.8/-48.0% closely). Isolated:
  `consult_risky`-only barely cuts trades (392.7→382.4/yr, -2.6%) but makes drawdown
  clearly worse (-44.3%→-48.7%, worse than the full combination); `consult_moderate`-only
  drives most of the trade-count reduction (→337.3/yr) but has the worst risk-adjusted
  numbers of any variant (sortino 0.74, sharpe 0.63); `consult_conservative`-only moves
  trades/drawdown by noise only but **beats baseline on sortino (0.94→1.02) and sharpe
  (0.77→0.85)** — the only variant that improves on baseline at all, on every metric it
  moves. None of the four clears `MAX_DD_HARD_FAIL` (best max_dd is still baseline's
  -44.3%), so this doesn't resolve the drawdown-gate problem, but it replaces "tightening
  doesn't help" with a correctly-attributed claim and surfaces a genuinely positive
  single-gene-group result for the first time in this thread. Separately: `grep -rn
  correlation_penalty --include='*.py'` confirms the gene the 10:02/12:47 UTC sessions'
  "Next steps" pointed at was fully removed 2026-08-20 (item 3, closed) — corrected the
  pointer below so a third session doesn't repeat a dead-end test. `git status` clean,
  `live_state.json` md5 unchanged (`37a1b00bee3f7cb1ad2f4adde0ab9ed0`),
  `python3 -m pytest -q` 252/252 confirmed at session start, no code changed (one
  standalone scratch script using the committed harness, not itself committed), genome
  still v3 (1d).

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


- **Archived 2026-09-03 (3-hourly check): everything from 2026-08-15 through
  2026-08-29 ~19:12 UTC moved verbatim to
  `AGENTS_ARCHIVE_2026-08-15_to_2026-08-29.md`, to keep this file under the
  256KB single-read limit — it had grown to ~510KB/7486 lines and this
  session's own `Read` tool call on it failed for exactly that reason before
  falling back to `grep`/offset reads.** Nothing reworded, nothing lost —
  see that file for the full older history in original order. This is the
  first archival pass; if this file keeps growing at its current rate
  (~15-20KB/day across entries this size), a future session should archive
  again rather than let it silently regrow past the limit. No code changed,
  no protected file touched, `live_state.json` untouched.

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
   **Pointer (2026-09-04 ~00:46-01:xx UTC): the "3 fold-clears" in the tally
   just below are confirmed, by directly testing `Researcher.structural()`,
   to be one deterministic candidate (`remove_agent` on `consult_moderate`)
   guaranteed to recur at generation 1 of any memory-less `EvolutionRun`
   against this champion, regardless of RNG seed — not 3 independent search
   outcomes.** See "Current state" above and
   `tests/test_researcher_structural_determinism.py`. Real independent
   evidence from option (i) is closer to 0 fold-clears than 3; this makes the
   existing "treat option (i) as exhausted" recommendation below stronger,
   not weaker. Still does not decide the accept-vs-redirect fork itself —
   still the owner's call.

   **Pointer (2026-09-03 ~03:46-04:16 UTC): a fifth seed clears the fold gate a
   third time, via the exact same `consult_moderate`-disabling mutation that
   cleared it last time (identical fold fitness) -- again fails the sealed
   holdout. Sample is now 5 seeds/9 generations, 3 fold-clears, 0 clearing
   both. Recommend treating option (i) as exhausted for the `x6` recipe and
   making the accept-vs-redirect call below explicitly, rather than a sixth
   seed.** See "Current state" above and
   `runs/2026-09-03-0416-shadow-4h-x6-seed9105.md`.
   `tools/shadow_4h_ramp_generation.py --recipe x6 --generations 2 --seed
   9105` (unmodified tool, fresh seed): generation 1's `consult_moderate`-
   disabling candidate (fold fitness 0.0443, identical to seed 9104's same
   candidate) cleared the real fold gate then lost the sealed holdout (-0.724
   vs. champion -0.222 + margin 2.355); generation 2 found nothing that
   cleared the gate. The recurring identical candidate is evidence this
   specific fold-clear is a structural/deterministic member of the
   researcher's mutation set, not fresh search finding something new --
   weaker independent evidence than a genuinely novel clear would be, which
   is why this entry's recommendation is sharper than the last: not decided
   here, still the next session/owner's call. Does not touch the owner-
   decision fork below.

   **Pointer (2026-09-03 ~00:46-01:11 UTC): a fourth seed clears the fold gate
   again (second clear in the sub-thread) and again fails the sealed holdout --
   sample is now 4 seeds/7 generations, 2 fold-clears, 0 clearing both.**
   See "Current state" above and `runs/2026-09-03-0111-shadow-4h-x6-seed9104.md`.
   `tools/shadow_4h_ramp_generation.py --recipe x6 --generations 2 --seed
   9104` (unmodified tool, fresh seed): generation 1's `consult_moderate`-
   disabling candidate cleared the real fold gate then lost the sealed
   holdout (-0.770 vs. champion -0.265 + margin 2.355); generation 2 found
   nothing that cleared the gate. **This session's read: four seeds/seven
   generations without a single holdout-clear, two independent fold-clears
   both failing holdout the same way, has shifted the evidence bar further
   toward closing option (i) in favor of item 2's accept-vs-redirect
   decision** -- not closed here, still the next session/owner's call. Does
   not touch the owner-decision fork below.

   **Pointer (2026-09-02 ~21:47-22:12 UTC): a third seed clears the fold gate
   zero times in 2 generations -- sample is now 3 seeds/5 generations, only
   1 fold-clear (which failed holdout), 0 clearing both.** See "Current
   state" above and `runs/2026-09-02-2212-shadow-4h-x6-seed9103.md`.
   `tools/shadow_4h_ramp_generation.py --recipe x6 --generations 2 --seed
   9103` (unmodified tool, fresh seed): both generations' top candidates
   hard-fail `dd_corrected_stats()`, including a not-previously-tried
   concentration-limit hypothesis (`risk_judge.max_position_pct=0.175`)
   that still hard-fails the same way. **Option (i) (more generations/seeds)
   is not closed by this, but the running tally (1/5 fold-clears, 0/5
   holdout-clears) is worth the next session weighing against treating it
   as similarly exhausted to the single-lever alternatives closed at
   12:47-13:09 UTC** -- not decided here. Does not touch the owner-decision
   fork below.

   **Pointer (2026-09-02 ~19:00-19:27 UTC): a fresh seed's second generation
   is the first candidate in the unconstrained-search sub-thread to clear
   the real fold-aggregate hard gate -- it still fails the sealed holdout.**
   See "Current state" above and
   `runs/2026-09-02-1927-shadow-4h-x6-seed9102-fold-gate-cleared.md`.
   `tools/shadow_4h_ramp_generation.py --recipe x6 --generations 2 --seed
   9102` (unmodified tool, fresh seed): generation 2's top candidate
   (`consult_moderate.rsi_hi` + `risk_judge.cash_floor_pct` ~0.48, a blunt
   de-risking move) cleared `dd_corrected_stats()` for the first time this
   sub-thread has seen, then lost at the sealed holdout (-1.808 vs. champion
   -0.281 + margin). **Nuances, doesn't reverse, the 06:46-07:15 UTC
   finding** -- unconstrained search can occasionally clear the fold gate
   this seed champion has died on before, but nothing across 3
   generations/2 seeds so far has cleared *both* fold and holdout. Option
   (i) (more generations/seeds) stays open, not closed by this; still a
   small sample. Does not touch the owner-decision fork below.

   **Pointer (2026-09-02 ~12:47-13:09 UTC): the last named single-lever
   alternative under (2b), `consv1` alone (no `trailing_stop`), is now
   checked too -- all 9 grid points hard-fail fold 1's real gate, and
   `trailing_stop` (not `consv1`) turns out to be the lever carrying the
   22:07 UTC "super-additive" synergy. Recommend closing (2b) as exhausted
   for single-lever alternatives.** See "Current state" above and
   `runs/2026-09-02-1309-consv1-threshold-sweep-isolated.md`. New
   `tools/consv1_threshold_sweep.py` grid-searches `rsi_buy_below` x
   `z_buy_below` on the bare `x6` seed (`trailing_stop` left at its
   untightened default, `scale=6` fixed) against the real
   `Evaluator`/`dd_corrected_stats()` gate: all 9 points hard-fail
   (-42.6% to -44.3% gate max_dd, barely different from the -44.3%
   untightened baseline), and tightening `consv1` alone makes
   `aggregate_fitness` slightly *worse* (-2.450 -> -2.565), not better.
   **What's left under item 2 is no longer "which single lever fixes fold
   1" (answered: none does) but a decision the next session/owner should
   make explicitly: accept the full `consv1 + trailing_stop + ramp` stack
   and move toward a real (non-shadow) promotion attempt for this genome
   family, or park 4h-bar shadow evolution and redirect effort (parked
   short-selling Phase 1, or item 4's LLM-backed consults).** Not decided
   this cycle.

   **Pointer (2026-09-02 ~09:47-10:10 UTC): (2b)(ii)'s bar-scaling-multiplier
   half is checked and closed -- scale 4/6/8 all hard-fail fold 1, scale 6 is
   the least-bad of the three, not an unexamined pick. The `consv1`
   consult-tightening thresholds are the only untried piece of "reconsider
   the base recipe" left.** See "Current state" above and
   `runs/2026-09-02-0956-x6-scale-parametrized.md`. `tools/shadow_4h_x6_seed.py`
   and `shadow_4h_fold_date_sensitivity.py` now take `--scale` (default 6,
   backward compatible) so this check could be run at all. **Three live
   threads left under item 2, none tried yet in isolation:** (i) more
   generations/seeds of the unconstrained `--recipe x6` search; (ii-remaining)
   sweep the `consv1` thresholds (`rsi_buy_below`/`z_buy_below`) themselves
   against fold 1, holding scale=6 fixed, instead of only ever measuring them
   stacked with trailing-stop and ramp genes; or accept that this genome
   family's fold-1 fix requires the full stack and stop looking for a
   single-lever alternative.

   **Pointer (2026-09-02 ~06:46-07:15 UTC): option (2b)'s first slice --
   unconstrained search on the unpatched `x6` seed -- hits the same fold-1
   wall as every hand patch; the more literal reading of (2b) (reconsider
   the base recipe itself) is the untried half now.** See "Current state"
   above and `runs/2026-09-02-0656-fresh-search-x6-recipe.md`.
   `shadow_4h_ramp_generation.py --recipe x6` (new this entry) ran one real
   generation from the unpatched seed: the top proposal by a wide margin
   (fold-aggregate 0.856 vs 0.435, a bear-regime size cut) still hard-fails
   `dd_corrected_stats()`'s drawdown gate -- one generation, one seed, not
   exhaustive, but it argues against "a fresh search would easily route
   around fold 1." **Two live options left under (2b), neither tried yet:**
   (i) more generations/seeds of the same unconstrained `--recipe x6` search
   (the tool now supports this directly), in case one generation was simply
   unlucky; or (ii) reconsider the *base recipe* itself -- the x6 bar-scaling
   multiplier approach, or the `consv1` consult-tightening choice -- rather
   than searching on top of either. (ii) is untried by every session in this
   thread so far and is the more literal reading of "step back ... and
   reconsider the base recipe" from the entry that first proposed (2b). (2a)
   stays closed; nothing here reopens it.

   **Pointer (2026-09-02 ~04:13 UTC): the 01:12 UTC "fold-rebasing artifact"
   finding doesn't hold across nearby days -- 1 of 7 shifts hard-fails under
   BOTH the one-sided and two-sided correction, so `dd_trust_continuous_stats`
   does not settle whether fold 1's drawdown is real for this genome family.
   Does not reopen (2a)/close-out; (2b) is still the only untried option.**
   See "Current state" above and
   `runs/2026-09-02-0413-trust-continuous-flip-day-sensitivity.md`. New
   `tools/shadow_4h_fold_date_sensitivity_trust_check.py` (7 tests, full
   suite 322/322) runs the two-sided correction across the same 7-day
   `fold-date-sensitivity` walk instead of a single snapshot. `consv_trailing`
   result: 2/7 shifts flip (today and 2026-08-27), 4/7 don't even hard-fail
   one-sided, but 2026-08-29 hard-fails under both views (-46.8%/-42.9%) --
   real risk that day. Third instance of this genome family's "best
   snapshot doesn't generalize" pattern (grid-point instability 16:47 UTC,
   generation-vs-sweep boundary flip 10:27 UTC). **Do not treat the
   trust_continuous view as a shortcut past (2b)** -- it's exactly as
   day-sensitive as the raw one-sided number.

   **Pointer (2026-09-01 ~22:20 UTC): option (2a) from the 19:21 UTC entry
   below is now closed -- a volatility-scaled cold-start cap doesn't help
   fold 1 either, and when it actually binds it makes the drawdown worse,
   not better.** See "Current state" above and
   `runs/2026-09-01-2159-cold-start-vol-cap-shipped.md`. New
   `risk_judge.cold_start_ramp_vol_cap` gene shipped and tested (default
   0.0, no-op, GENE_SPACE-registered, threaded through both shadow tools).
   The first-guess cap range (0.3-0.8, by analogy to
   `consult_conservative`'s 1.10 `max_vol` veto) turned out to be the wrong
   scale -- fold 1's actual buy-candidate vol distribution is 0.033-0.342,
   so that whole range was a guaranteed no-op. Sweeping caps inside the
   real range found: 0.30 negligible, 0.20 and 0.05 both make the real
   gate's max_dd *worse* (not better), and 0.10-0.15 flip fold 1 from
   passing to hard-failing outright. **Every lever tried against fold 1's
   cold start so far has now failed**: the size ramp alone is
   boundary-fragile (13:16/16:47 UTC), the conviction floor found no
   marginal band (19:21 UTC), and the vol cap backfires when it bites
   (this entry). **Option (2b) -- step back from patching this `consv1 +
   trailing_stop -0.06` seed genome further and reconsider the base recipe
   -- is now the only untried option left on this thread.** It is a
   bigger, multi-session task: needs either a different seed genome
   through the same `consv_trailing_ramp`-family fold-1 diagnostic, or a
   fresh `Researcher`-driven search that isn't anchored to hand-picked
   patches on top of one fixed 22:07 UTC starting point.

   **Pointer (2026-09-01 19:21 UTC): option (1) below (a structurally
   different, non-size lever on fold 1) has now been tried in its most
   direct form — a cold-start conviction floor — and is closed too: swept
   0.0 to 0.40 (80% of its allowed range) against the 120/0.20 ramp point,
   byte-identical results at every value.** See "Current state" above and
   `runs/2026-09-01-1921-cold-start-conviction-boost-no-bite.md`. New
   `risk_judge.cold_start_ramp_min_conviction_boost` gene (default 0.0,
   no-op) vetoes marginal-conviction buys during the cold-start window
   instead of just sizing them down. Instrumented directly against fold 1's
   own backtest window: buy-candidate conviction there is bimodal (mostly
   0.80-0.96 unanimous trades; the only low-conviction candidates were
   already below the *un-boosted* 0.30 floor) — no marginal band exists for
   a conviction filter to catch, so the drawdown is adverse price action on
   already-high-conviction trades, not weak signals slipping through. Gene
   kept (tested, no-op default, may still combine usefully in a real
   `Researcher` search or a different seed genome) but not worth hand-tuning
   further against this specific genome. **Narrows to two options, neither a
   single-session task: (2a) a non-conviction structural lever — e.g. a
   volatility-scaled position cap, or restricting which symbols/regimes can
   open cold-start positions at all — since the failing trades are
   unanimous/high-conviction, so the lever needs to key on something other
   than agent conviction; or (2b) step back from patching this `consv1 +
   trailing_stop -0.06` seed genome further and reconsider the base recipe.**

   **Pointer (2026-09-01 16:47 UTC): option (a) below is closed — three
   independent "best point" picks for `cold_start_ramp_bars`/
   `cold_start_ramp_start_scale` have each now been checked and each fails
   most nearby days; do not run another point-in-time sweep expecting a
   better answer.** See "Current state" above and
   `runs/2026-09-01-1647-cold-start-ramp-grid-instability.md`. Re-ran the
   08:08 UTC sweep ~8h later: only 20/37 points clear now (was 35/37), and
   120/0.20 itself flipped from -34.6% (pass) to -44.0% (hard-fail). Took
   today's new top pick (150/0.20) through the 7-day fold-date-sensitivity
   tool: 6/7 shifts hard-fail, worse than 120/0.20's own 4/7. **Two real
   next steps remain, both bigger than one 3-hourly session**: (1) a
   structurally different lever on fold 1 (e.g. a stricter entry threshold
   during the cold-start window, not just smaller position size), or (2)
   step back from patching this specific `consv1 + trailing_stop` seed
   genome further and reconsider the base. `tools/shadow_4h_x6_seed.py`'s
   `build_consv_trailing_ramp_seed()` and
   `tools/shadow_4h_fold_date_sensitivity.py` now take `ramp_bars`/
   `ramp_start_scale` overrides (`--ramp-bars`/`--ramp-scale`), so whoever
   picks up (1) or (2) can still reuse the multi-day check on whatever they
   try next.

   **Pointer (2026-09-01 13:16 UTC): the shadow fold-date-sensitivity tool the
   10:27 UTC entry below asked for is now built and run — the systematic
   check settles "boundary-fragile" into something worse.** See "Current
   state" above and
   `runs/2026-09-01-1316-shadow-4h-fold-date-sensitivity.md`. New
   `tools/shadow_4h_fold_date_sensitivity.py` (11 tests) re-evaluates a
   4h-shadow genome builder across a week of "as-of" dates with the real
   `dd_corrected_stats()` gate check applied at each. Result for the 08:08
   UTC sweep's recommended `cold_start_ramp_bars=120,
   cold_start_ramp_start_scale=0.20`: **4 of 7 recent days hard-fail
   `MAX_DD_HARD_FAIL` outright**, and the 3 that clear do so by at most +5.6
   points of margin. **Do not treat 120/0.20 (or 120/0.10) as a settled fix
   for the 01:14 UTC cold-start-fold problem** — it fails the real gate more
   often than it passes across nearby run dates, which the two prior
   same-day snapshots (08:08 UTC pass, 10:27 UTC fail) only hinted at.
   Two untried next steps, either usable with the new tool directly: (a)
   sweep other points from the 08:08 UTC grid search (larger `ramp_bars`
   or `start_scale`) through `--recipe consv_trailing_ramp --shift 7` for a
   wider-margin point, or (b) treat this seed genome's (`consv1 +
   trailing_stop -0.06`) fold 1 as structurally fragile and look for a
   different lever entirely rather than continuing to tune the ramp genes
   against it.

   **Pointer (2026-09-01 10:27 UTC): the 08:08 UTC sweep's 120/0.20
   recommendation is boundary-fragile, not settled — a same-day
   `EvolutionRun.generation()` re-check (seed 9002, `tools/
   shadow_4h_ramp_generation.py`, new this session) found the identical
   120/0.20 genome hard-failing `MAX_DD_HARD_FAIL` again (fold 1 max_dd
   -43.4% vs. the sweep's -34.6%), traced to one extra 4h bar in the loaded
   data (a fold-boundary-shift artifact `fold-date-sensitivity`'s own notes
   already flagged as consequential, not a market crash or a bug — see
   `runs/2026-09-01-1027-shadow-4h-ramp-generation-boundary-flip.md`).**
   Since the champion itself no longer cleared the gate this run, "champion
   held against 3 generations of blind proposals" isn't a real stability
   signal here — most challengers likely hard-failed the same structural
   fold for the same reason. **Recommend treating 120/0.20's ~5.4-point
   margin as too thin to trust from a single snapshot**; the natural fix is
   a shadow equivalent of the existing `fold-date-sensitivity` CLI (same
   mechanism, parameterized for a 4h-shadow genome builder instead of just
   the live 1d champion) rather than more one-off point measurements. Not
   built yet.

   **Pointer (2026-09-01 08:08 UTC): the recommended "real search over just
   those two genes" from the 04:18 UTC entry below is now done — 37-point
   grid search, see "Current state" above and
   `runs/2026-09-01-0808-cold-start-ramp-sweep.md`.** Found `ramp_bars=120,
   start_scale=0.20` strictly better than the hand-picked 120/0.10 on the
   real gate (aggregate_fitness 0.454 vs 0.368, same -34.6% gate max_dd,
   holdout still beats benchmark) — `tools/shadow_4h_x6_seed.py`'s
   `build_consv_trailing_ramp_seed()` now builds 120/0.20. Also found the
   two-gene landscape is jagged (two interior grid points hard-fail next to
   comfortably-clearing neighbors) — worth knowing before trusting a
   `Researcher`-driven hill-climb here. **Still open**: no fresh
   `EvolutionRun.generation()` has run against the new 120/0.20 point as
   champion yet (the natural next check, mirroring what the 04:18 UTC session
   did for 120/0.10); still no established prior champion for this seed
   lineage to compare against for a real promotion decision; the sweep only
   covers this one seed genome (`consv1 + trailing_stop -0.06`), untested
   against other trailing-stop values or a different seed. Also flagged, not
   resolved: this session's own measured `aggregate_fitness` for 120/0.10
   (0.368) didn't match the 04:18 UTC note's 0.467 despite matching gate
   max_dd exactly — see the run note for the caveat this leaves on any single
   hand-run number from a prior session.

   **Pointer (2026-09-01 04:18 UTC): the 01:14 UTC session's cold-start-fold
   dead end now has a real fix — `risk_judge.cold_start_ramp_bars`/
   `cold_start_ramp_start_scale` (shipped this session, see "Current state"
   above and `runs/2026-09-01-0418-cold-start-ramp-clears-fold-gate.md`). The
   22:07 UTC session's `consv1 + trailing_stop -0.06` genome plus this ramp
   (120 bars, 0.10x start scale — via `build_consv_trailing_ramp_seed()` in
   `tools/shadow_4h_x6_seed.py`) is the first genome in this whole thread to
   clear `MAX_DD_HARD_FAIL` on the real fold-based gate, not just a continuous
   replay. One real `EvolutionRun.generation()` has now run against it as
   champion (seed 9001, 34 blind proposals, see the same run note's
   addendum): champion held, best challenger fitness 0.611 vs. its 0.467,
   nothing cleared the acceptance bar — a real stability signal, not a
   promotion (nothing beat it by enough to even reach the sealed-holdout
   gate). Still open: `cold_start_ramp_bars`/`cold_start_ramp_start_scale`
   are now in `agents.researcher.GENE_SPACE` but 120/0.10 was hand-picked
   from a small sweep, never searched, and whether that generation's 34
   proposals happened to touch either gene wasn't recorded (the script only
   captured the summary) — a real search over just those two genes, or a
   re-run that also prints the per-candidate patch list, is the natural next
   step.**
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

   **Isolated 2026-08-31 (3-hourly check, ~16:00 UTC): the 10:02 UTC combination's
   worse-drawdown result was driven by `consult_risky`/`consult_moderate`, masking a
   quietly-positive `consult_conservative`-only result — see "Current state" above and
   `runs/2026-08-31-1600-4h-shadow-isolate-consult-threshold.md`.** Also caught: the
   07:05/10:02/12:47 UTC sessions' carried-forward "test correlation_penalty next"
   suggestion pointed at a gene fully removed 2026-08-20 (item 3, closed) — corrected
   here so a third session doesn't repeat it. `consult_conservative`-only tightening
   (`rsi_buy_below` 38→30, `z_buy_below` -0.8→-1.2) moves trades/drawdown by noise only
   but beats baseline on sortino (0.94→1.02) and sharpe (0.77→0.85) — the only one of
   four isolated variants that improves on baseline at all. Recommended trying this as
   its own starting point combined with something that attacks drawdown directly.

   **Found 2026-08-31 (3-hourly check, ~22:07 UTC): that combination — done. Pairing
   `consult_conservative` tightening with trailing-stop tightening is super-additive and
   clears `MAX_DD_HARD_FAIL` outright, the first variant in this thread's history to do
   so — see "Current state" above and
   `runs/2026-08-31-2207-4h-shadow-consv-trailing-synergy-clears-dd-gate.md`.**
   `consv1` (the 16:00 UTC variant) + `risk.trailing_stop` -0.06 (seed -0.15): -32.7%
   max_dd, sortino 1.35, sharpe 1.09 — best risk-adjusted numbers this thread has ever
   recorded. `consv1` + `trailing_stop` -0.08 + `cash_floor_pct` 0.15: -35.1% max_dd,
   fitness +0.146 — first positive full-history fitness this thread has recorded.
   Neither lever alone gets close (best single-lever result: `trailing_stop` -0.08 alone,
   -39.3%, barely clears). Also found: pushing `consult_conservative` past `consv1` has
   zero further effect (ruling out that as a lever), and `stop_loss`/`max_position_pct`
   tightening both make drawdown worse. Not yet run through the real promotion pipeline
   (fold-aggregate acceptance + sealed holdout) — only a single full-history backtest,
   same measurement every prior session here used. **Recommend a future session seed a
   fresh 4h shadow `EvolutionRun` from this genome** (instead of the plain x6-scaled
   seed) and check whether it survives fold-aggregate acceptance and the sealed holdout
   as a champion in its own right — this thread's first real candidate worth running
   through the full pipeline.

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
