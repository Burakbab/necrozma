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
```

`anatomy`, `consults` and `costs` are diagnostics: they replay history and
report, they never touch `live_state.json` or the champion. All three take a
few minutes (`costs` replays history once per cost scenario, so longer).

`tick` refuses to trade the same bar twice — if it prints `already traded`, that
is the idempotency guard working correctly, not an error. It decides on the last
*closed* daily bar, which is why the daily run fires at 00:20 UTC.

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
| `index.html` | generated public dashboard, served by GitHub Pages — rebuilt each run, never hand-edited |
| `README.md` | hand-written, renders on the GitHub repo page — its `## Status` section names the current genome version and must be updated on every promotion (see Run protocol step 7) |

`live_state.json` is the irreplaceable one. Everything else can be rebuilt.

## No credentials, anywhere

Prices come from Binance's public market-data endpoint: no API key, no signup, no
KYC. The portfolio is tracked in `live_state.json`, which *is* the ledger. There
is no brokerage account in this design and there does not need to be one.

---

## Current state

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
  caveat as `anatomy`/`consults`. Next: point the same tool at the sealed
  holdout window specifically to see if the drawdown-gate margin is
  thinner out of sample.

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

3. **Cross-asset correlation awareness for the Risk Judge** — the first genuinely
   structural proposal, not a retune. Infrastructure shipped 2026-08-15 after
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
   API call. Not yet built: needs `evotrader_bundle.py`'s tick flow split into an
   "analyze & flag hard calls" phase and an "apply consult verdict & execute"
   phase. Queued as the next real code-build task.

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
