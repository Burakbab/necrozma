# Universe-perturb: mapping the drawdown cliff's edge — 2026-08-21 22:10 UTC

## Scope

Follow-up flagged by the 19:02 UTC `universe-perturb` run ("Current state" /
AGENTS.md Next steps item 2): that run found a random 20%-of-universe drop
hard-fails 2 of 6 trials on `MAX_DD_HARD_FAIL`, and proposed a `--drop-frac`
sweep to map how close to the full universe the cliff actually sits. No code
changed — `universe-perturb`'s `--drop-frac`, `--n-trials`, `--seed` and
`--drop` flags already existed; this run just uses them more exhaustively
than the diagnostic's own first outing did.

## What was run

1. `--drop-frac` sweep at 0.05/0.10/0.15/0.25/0.30 (n_trials=6, seed=0 each,
   full history, champion v3 live), alongside the existing 0.20 baseline from
   the 19:02 run.
2. Exhaustive **single-symbol** drop (`--drop SYM`) for all 27 universe
   symbols individually — every symbol removed alone, once each, against the
   same full-history baseline.

## Result 1: the `--drop-frac` sweep is noisy at n=6, not cleanly monotonic

Random-trial hard-fail counts (of 6 trials per frac; the deterministic
"drop PAXG only" trial never hard-fails at any frac and is excluded from
these counts):

| drop-frac | k (symbols dropped) | hard-fails / 6 |
|---|---|---|
| 0.05 | 1 | 3 |
| 0.10 | 3 | 3 |
| 0.15 | 4 | 4 |
| 0.20 | 5 | 2 |
| 0.25 | 7 | 3 |
| 0.30 | 8 | 5 |

Not monotonic — expected, since each frac draws an independent `rng.sample`
call (different k consumes the seeded RNG differently), so 6 samples per
frac is too few to trust the *shape* of this curve. But every single row,
including the smallest (`k=1`, one symbol gone), already shows a
non-trivial hard-fail rate. That pushed toward result 2: don't sample, just
run the full census at k=1.

## Result 2: the real finding — 14 of 27 symbols (51.9%) hard-fail the champion when dropped ALONE

`universe-perturb --drop SYM` run once per symbol, all 27, no sampling:

**Hard-fail alone** (maxDD crosses -40%, `fitness = -inf`): AAVE (-44.9%),
ADA (-44.7%), AVAX (-51.0%), BNB (-42.1%), DOGE (-46.7%), DOT (-44.1%), ETH
(-55.6%), FIL (-50.1%), INJ (-42.2%), SHIB (-44.9%), SOL (-44.1%), TRX
(-41.9%), XLM (-44.6%), ZEC (-50.4%).

**Survives alone** (finite fitness, still beats benchmark in every case):
ATOM, BCH, BTC, CRV, FET, HBAR, ICP, LINK, LTC, NEAR, PAXG, UNI, XRP.

Baseline (all 27 symbols): maxDD -34.1%, `MAX_DD_HARD_FAIL` threshold 40%.
The margin is 5.9 percentage points — and for a *majority* of this
27-symbol universe, removing that one symbol alone (no other perturbation)
is enough to cross it. This is a sharper, precise version of the 19:02
run's "drawdown cliff" characterization: it isn't a property of random 20%
subsets, it's already true at the smallest possible perturbation (losing
any one of 14 specific symbols). ETH is the most extreme single point
(-55.6% alone, the single largest jump of any symbol) despite being one of
the most liquid/least likely to actually vanish from a real universe — a
reminder this is a mechanical sensitivity of the backtest's maxDD path, not
a comment on any symbol's real-world reliability.

Reading, same caveat as the 19:02 run: this characterizes the champion's
current risk margin against its own hard-fail gate, it doesn't propose a
fix. It sharpens "the cliff exists" (19:02 finding) into "the cliff is
essentially at the doorstep, not 20% of the universe away" — worth citing
together the next time `MAX_DD_HARD_FAIL`'s own margin comes up, alongside
`margin-curve`'s finding on the multiple-testing gates.

## Verification

- No code changed — both the sweep and the exhaustive single-drop pass use
  `universe-perturb`'s existing `--drop-frac`/`--drop` flags. `git status
  --short` clean throughout.
- `py_compile`/tests: full suite still 179 passed (no new code to test).
- `live_state.json` md5 unchanged throughout: `8b3dc413c9a85fda04bdeb0ad4c63733`.
- `evotrader.manifest` md5 unchanged: `0bf3a7d9411ee692d0a9f152a7533803`.
- `constitution verified 8b74865634b1db07` on every invocation (33 total:
  6 sweep runs + 27 single-symbol runs), never "CONSTITUTION MODIFIED".
- Today's 2026-08-21 daily bar already confirmed processed by the 00:20 UTC
  run and re-confirmed by the 20:30 UTC mechanism check before this session
  started (`updated` timestamp `2026-08-21T00:27:21+00:00`); `tick` not run
  this session, no double-trade.
- `review-hard-calls` checked: 0 pending.
- No genome promotion, no README `## Status` change needed.
- Repo-state note: this session's cloud clone started with local `main`
  detached, 2 commits ahead of an unrelated pre-restart seed history with no
  merge-base against a force-updated `origin/main` (same recurring
  container-seed artifact prior sessions have logged, not real divergent
  work) — reset to `origin/main` per the run protocol, no work lost.

## Next

The fold-windowing/holdout-margin thread (item 2) and now this
universe-composition sub-thread both point at the same underlying theme:
several of the champion's acceptance/hard-fail gates sit close to their own
edges given the current champion's actual behavior. Nothing here proposes a
fix — that would mean either loosening `MAX_DD_HARD_FAIL`'s margin (a
constitution change, needs its own design pass + `AMENDMENTS.md` argument)
or accepting that single-symbol fragility as a known, measured property of
this champion. No further cheap follow-up queued on the universe-perturb
line specifically; treat it as answered for now the same way the
windowing/capping line was set aside 2026-08-21.
