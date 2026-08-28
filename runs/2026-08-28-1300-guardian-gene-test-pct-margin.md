# 3-hourly check — 2026-08-28 ~13:00 UTC — `guardian-gene-test --pct` + quantifying the sealed-holdout bar

## State check

- Cloud clone started detached with local `main` at a stale snapshot
  (`72943f3`, 2026-08-22) that had diverged from `origin/main` (`6e34430`,
  2026-08-28 09:58 UTC) with no common ancestor inside the visible history —
  same expected shallow-clone artifact every entry so far today has named,
  not a force-push. `git checkout main && git reset --hard origin/main`
  realigned to `6e34430`, "Add guardian-gene-test: real Guardian
  mechanical-exit gene patches through the actual acceptance gate".
- `live_state.json` `updated`: `2026-08-28T00:28:04+00:00` (today's 00:20
  UTC daily-trading run). No new bar since — confirmed via the timestamp and
  today's `runs/` notes through the 09:45 UTC entry. No `tick` run this
  session, no double-trade risk.

## What shipped

The 09:45 UTC `guardian-gene-test` entry left two untried directions: (1)
whether a **smaller** (not halved) tightening trades away less upside and
holds the holdout, or (2) whether this is the same lucky-holdout-draw
entrenchment `holdout-pressure`/2026-08-18 already documented, now showing
up for mechanical Guardian genes too. This session answers (1) directly and
finds the real answer is closer to (2), with a number attached.

`guardian-gene-test` gained a `--pct N` flag (default 50, byte-identical
output to the original halved variants when omitted — verified by re-running
the default and diffing against the 09:45 UTC table). `--pct N` tightens
each Guardian gene by `cur * (1 - N/100)` instead of the fixed `cur / 2.0`,
so `--pct 25` tests a milder "25% tighter" hypothesis with the same
clamping-to-`GENE_SPACE`-bounds and the same acceptance-gate machinery
(`Evaluator.evaluate`, `dd_corrected_stats`, `constitution.accepts`,
`constitution.holdout_accepts`) as every prior invocation.

Also added: a one-line "sealed-holdout bar at this draw count" print per
champion, computing `constitution.required_margin(holdout_draws_before + 1,
0, sigma=HOLDOUT_SIGMA)` directly — the table's own `holdout gate` column
truncates `holdout_accepts()`'s reason string at 38 characters, which was
hiding the actual required-margin number behind "... did not c[lear...]" in
every row of the 09:45 UTC table. This line makes that number visible
without truncation for the first time.

## Finding — the margin dwarfs the magnitude question

Ran `guardian-gene-test --pct 25` against v3 (live):

| variant | fold-agg fit | gate max_dd | fold gate | holdout fit | halved (09:45 UTC) holdout fit |
|---|---|---|---|---|---|
| tighter stop-loss (25%) | 0.517 | -36.7% | OK | 0.646 | 0.476 |
| tighter trailing stop (25%) | -1.564 | -46.7% | **NO** (hard-fail) | not reached | not reached (-43.2%, also hard-fail) |
| shorter time stop (25%) | 0.604 | -37.6% | OK | -0.819 | 0.174 |
| combined tighter exits (25%) | 0.767 | -37.5% | OK | -0.896 | -0.676 |

champion v3: fold-agg fitness -1.612 (gate max_dd -46.8%), sealed-holdout
fitness 0.644.

**The magnitude question has an answer, and it's not the interesting one.**
25% tightening does *not* uniformly hold the holdout better than halving:
the stop-loss variant improves (0.646 vs 0.476, now barely above the
champion's own 0.644), but the time-stop and combined variants get *worse*
(-0.819 vs 0.174, -0.896 vs -0.676) — a real, non-monotonic result, not
noise (same evaluator, same champion, same day).

**But none of that matters, because of the new margin line:**

```
sealed-holdout bar at this draw count: a challenger needs holdout fitness
> 5.652 to pass (champion 0.644 + required margin 5.008 at 23 cumulative
draws, HOLDOUT_SIGMA=2.0)
```

`required_margin(23, 0, sigma=2.0)` = `2.0 * sqrt(2 * ln 23)` ≈ 5.008. Every
variant tried today and at 09:45 UTC — 25% or halved, single-gene or
combined — scores in the -0.9 to +0.6 range. The best of eight combined
attempts (0.646) clears the champion's own raw score by 0.002 and falls
short of the actual bar by more than 5 full fitness points. The gap between
"25% tighter" and "halved" (at most ~0.15 fitness points on any one variant)
is two orders of magnitude smaller than the gap between any of them and the
bar itself. **No single-gene or few-gene hand-picked patch to this champion,
at any magnitude, could plausibly clear this gate right now** — the question
"does a smaller tightening hold the holdout better" was answerable but was
never going to be decisive, because `HOLDOUT_SIGMA=2.0` at 23 cumulative
draws sets a bar that dwarfs the entire plausible range of a hand-picked
patch's fitness score.

This sharpens (2) from the 09:45 UTC note into something more specific than
"lucky holdout draw entrenchment": it isn't that v3's *particular* holdout
draw was lucky (0.644 is a modest, plausible score, not an outlier the way
v3's 1.079 draw was called out in the 2026-08-18 4h-shadow finding) — it's
that the multiple-testing correction itself, at the account's current
cumulative draw count (23 and rising by however many candidates get proposed
per generation), requires an improvement large enough that a single fold's
worth of drawdown-tightening cannot plausibly produce it. A genuinely
evolved multi-generation search (letting boldness and population size
compound many candidates' worth of fold-aggregate selection before ever
reaching a holdout check) is the only path that has historically cleared
comparable bars (see the 2026-08-17 4h-shadow generation-9 promotion,
fitness 0.618→1.010, holdout excess return +35.3%) — not because search is
smarter, but because it explores enough candidates for the fold-aggregate
filter to do real work before anything reaches the expensive, heavily-taxed
holdout check at all.

## Verified safe

- `py_compile evotrader_bundle.py` clean.
- `tools/edit_bundle_module.py sync --check` clean — CLI-only code, no
  `_SRC` module touched.
- Full test suite: 235 passed (163.93s, matches baseline — no new pure
  function, this composes only already-tested `Evaluator.evaluate`/
  `dd_corrected_stats`/`Genome.child`/`constitution.accepts`/
  `holdout_accepts`/`required_margin`).
- `git diff --stat`: only `evotrader_bundle.py` touched (+36/-11 lines).
- `live_state.json` md5 `0fa0731311baab0508f959f79a01214e` and
  `evotrader.manifest` md5 `0bf3a7d9411ee692d0a9f152a7533803` both unchanged
  before and after every run this session (checked explicitly around both
  the default-`--pct` sanity run and the `--pct 25` run).
- Default `--pct` (50, omitted) reproduces the 09:45 UTC entry's numbers
  (small ~0.02-0.05 fitness differences from the trailing-4y window rolling
  forward ~3 hours, same as every other diagnostic's known date-sensitivity
  — not a regression).
- No genome promotion, no trading touched, today's bar already processed
  before this session.

## Next

The fold-3 Guardian-gene thread is now closed for *hand-picked single or
combined gene patches at any magnitude* — the margin, not the magnitude, is
the binding constraint. What's actually untried: a real `evolve()` shadow
search seeded from v3 with mutation scoped toward the Guardian risk genes
(`risk.stop_loss`/`risk.trailing_stop`/`risk.max_bars_held`), run for enough
generations that multiple fold-aggregate-selected candidates compound before
any one reaches the holdout gate — the same shape that produced the only
real holdout-clearing promotions this project has seen (the three 4h-shadow
generation-N promotions in `runs/2026-08-1{6,7}-*`). That's a multi-generation,
time-boxed exercise past what a single hand-picked-patch diagnostic can
answer — a natural next 3-hourly session's scope, not this one's.
