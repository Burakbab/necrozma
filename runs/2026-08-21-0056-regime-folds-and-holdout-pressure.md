# 3-hourly self-improvement check — 2026-08-21 00:56 UTC

## Session start

`git pull` failed (`HEAD detached from refs/heads/main`, no branch) —
`git checkout main` then showed local `main` 2 commits ahead, 50 behind a
force-updated `origin/main`, with no merge-base at all: an unrelated,
already-superseded pair of Aug 15-16 initial-import commits from an old
container seed, not real divergent work. Reset to `origin/main`
(`git checkout -B main origin/main`) per AGENTS.md's "origin/main is
authoritative" rule — no work lost. `pip3 install -r requirements.txt`
succeeded first try.

## Step 2: daily bar already handled

`live_state.json` `updated` timestamp (`2026-08-21T00:27:21Z`) and
`runs/2026-08-21-0020-daily-trading.md` confirm the 00:20 UTC daily run
already processed today's bar (tick 7, NAV $10,794.07, no trade, `evolve 3`
ran with no promotion). Did not run `tick` this session.

## holdout-pressure re-run after today's non-promoting evolve

AGENTS.md's holdout-pressure entry says to run this after every future
non-promoting `evolve` call. Today's daily `evolve 3` (00:20 UTC) didn't
promote, so re-ran the diagnostic (no code change):

```
python3 evotrader_bundle.py holdout-pressure
```

Result: **13 individual sealed-holdout draws now recorded against champion
v3, all lost** — up from the 9 recorded as of the last check
(`runs/2026-08-18-0655-holdout-pressure-diagnostic.md`). The three new rows
(fold fitness 1.885/1.774/1.756 vs champion fold fitness 1.396) are exactly
today's three generations — each cleared the fold-aggregate gate as a real
improvement on search data and still lost its single sealed-holdout draw.
Continues the entrenchment pattern (13/13, not 9/9); no new interpretation,
just a bigger sample on an already-recorded finding. Read-only, `git status
--short` empty after this command, `live_state.json`/`evotrader.manifest`
md5 unchanged.

## New diagnostic: `regime-folds`

AGENTS.md's item 2 has been stuck since 2026-08-20 on the assumption that
testing a regime-stratified fold scheme "needs engine work `run_backtest`
can't do yet (non-contiguous folds)" — repeated verbatim in `regime-scan`'s
own CLI comment. That assumption doesn't hold for a first honest test: a
fold doesn't need to be one continuous replay to be *scored*, only to score
a genuinely uninterrupted single equity curve. `run_backtest` already
accepts any contiguous `(a, b)` window; a "fold" can be built from *several*
independently-backtested sub-windows whose results get merged the same way
`Evaluator._merge` already combines folds for the acceptance gates. Genome
state (positions, indicator lookbacks) resets at each sub-window boundary —
exactly what already happens at every existing fold boundary today, just
with more boundaries. This is an approximation of a genuinely non-contiguous
single replay (which would still need `run_backtest` to change), not that
replay — but it needed nothing checksummed to build or test.

Shipped:
- `loop.evolve.regime_stratified_groups(window_returns, n_folds)` — pure,
  genome-independent. Greedy longest-processing-time (LPT) balance of
  sub-window indices into `n_folds` groups by `|log(1+r)|` weight (the same
  weight `regime_concentration` shares its `concentration_ratio` from), so no
  fold hoards a disproportionate share of the region's compounded growth the
  way the fixed calendar 3-fold split hoards the whole melt-up.
  `tests/test_regime_stratified_groups.py`, 9 new tests (LPT balance on a
  known trace, dominant-window isolation, coverage/determinism/edge cases).
- `Evaluator.evaluate_grouped(g, sub_windows, groups, log_detail=False)` —
  scores each fold-as-a-group of sub-windows by independently backtesting
  every sub-window, merging via the existing `_merge`, and applying the same
  `ranking_fitness` + `mean - FOLD_CONSISTENCY_WEIGHT * std` aggregate formula
  `evaluate()` already uses, so the two are directly comparable at the same
  fold count. `tests/test_evaluate_grouped.py`, 7 new tests (merge/fitness
  match a hand-checked reference, aggregate formula, single-sub-window
  degenerate case, partial and total sub-window backtest failure).
- New read-only CLI `regime-folds [--n-subwindows N] [--n-folds N]
  [--also-version N]` (`evotrader_bundle.py`): default 6 sub-windows (matches
  `regime-scan`'s own n=6 measurement and stays comfortably clear of
  `run_backtest`'s 120-bar hard minimum per call — the searchable region is
  ~1242 1d bars, so 6 sub-windows are ~207 bars each; 12 sub-windows would be
  ~103, under the minimum, the same failure mode `fold-scheme`'s n=8 hit)
  grouped into 3 folds by default, prints the buy-and-hold-based fold
  assignment plus the regime-stratified `aggregate_fitness` next to the
  disjoint calendar baseline at the same fold count.

Full suite: 167 passed, up from 151 (16 new tests).

Verified safe: `loop.evolve` isn't checksummed (`constitution` +
`core.portfolio` only), `tools/edit_bundle_module.py verify` round-trip clean
before and after the edit, `py_compile` clean, `live_state.json` md5
identical throughout (`8b3dc413c9a85fda04bdeb0ad4c63733`),
`evotrader.manifest` md5 identical (`6a4434574ff424f74ff300ebdb50d194`),
`constitution verified dfae6a697f51fb49` unchanged (not touched, no
amendment needed — nothing here is checksummed), `git status --short` clean
of anything but `evotrader_bundle.py` and the two new test files, genome
version unchanged (no promotion, no README Status change needed).

### First real result

```
6 sub-windows -> 3 regime-stratified folds (LPT on buy-and-hold |log-growth|):
  fold 1: w3(+156.8%)                              <- the melt-up, isolated alone
  fold 2: w4(+46.7%), w1(+19.9%), w2(-14.8%)
  fold 3: w5(-27.9%), w6(+32.5%)

                              disjoint baseline    regime-stratified    delta
  v3 (live)                        1.396                2.119          +0.723
  v1 (reconstructed)                0.181                0.238          +0.057
  v2 (reconstructed)                0.293                0.227          -0.065
```

Mixed, not a clean win: stratification raises `aggregate_fitness` for v3
(substantially) and v1 (slightly), lowers it slightly for v2. Three data
points isn't enough to call this settled either way — it's the same "check
across all three real champions" pattern every other fold-scheme finding in
AGENTS.md has been held to before drawing a conclusion, and this is only the
first reading. Note the single dominant sub-window (w3) ends up alone in its
own fold every time (its weight dominates so thoroughly that LPT never has
reason to pair it with anything) — so this doesn't "spread the melt-up
across folds" the way item 2's framing assumed, it isolates it into a
smaller fold instead, changing what the *other* folds average over rather
than diluting the melt-up itself. Whether that's actually the right shape
for what a regime-stratified scheme should do is an open design question,
not resolved by this run.

## Next

- `regime-folds` needs more readings before a conclusion: sweep
  `--n-subwindows`/`--n-folds` (does a different sub-window resolution change
  which champions the stratification helps?), and check whether isolating
  the dominant sub-window alone (rather than pairing it with something) is
  actually the intended fix, or whether a grouping objective that forces the
  dominant window to share a fold would answer item 2's original question
  better.
- Corrected assumption for whoever next touches item 2: a regime-stratified
  fold scheme does **not** strictly need a `run_backtest`/constitution change
  to test — this diagnostic is real evidence of that, not just an argument.
  `regime-scan`'s own CLI comment (and README/AGENTS.md prose repeating
  "needs engine work") should be revisited once this diagnostic's readings
  are more complete — not changed yet, since the approximation's fidelity to
  a genuine non-contiguous single replay is still unverified (no shared
  positions/compounding across a fold's sub-windows the way the real thing
  would need).
- `holdout-pressure` should keep being re-run after every future
  non-promoting `evolve`, live or shadow, per the existing standing note.
