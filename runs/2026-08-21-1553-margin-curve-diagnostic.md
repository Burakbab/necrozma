# `margin-curve`: putting real numbers on the two acceptance margins — 2026-08-21 ~15:53 UTC

Scheduled 3-hourly check. Today's daily bar was already handled by the
00:20 UTC daily run (`live_state.json` `updated` at `2026-08-21T00:27:21Z`,
genome version still 3, no double-trade — `tick` not run this session).
`review-hard-calls` checked: 0 pending. Session started with local `main`
detached, two commits behind an unrelated pre-restart seed history with no
merge-base against a force-updated `origin/main` (the same old
container-seed artifact prior sessions have already noted, not real
divergent work); reset to `origin/main` per the run protocol, no work lost.

## Why this slot went here

The 13:07 UTC shadow-evolve run's note said the fold-aggregate gate, not
the sealed-holdout gate, is what's currently binding, and named a
mechanism: "`required_margin()`'s multiple-testing correction gets
mechanically harder to clear as `n_candidates` keeps rising with every
generation." That's directionally true but its own docstring already says
the growth is `sigma * sqrt(2 * ln k)` — logarithmic, not linear — and no
run had actually checked how much the bar moves in practice. Both the
fold-windowing/capping line and the `HOLDOUT_SIGMA` recalibration are
marked "no immediate follow-up" in `AGENTS.md`, so this slot went to
quantifying that claim directly instead of trying a fifth windowing
variant or repeating another shadow-evolve pass that would only add more
candidates without checking whether adding them actually matters.

## What shipped

New CLI `margin-curve` (`evotrader_bundle.py`, in the plain CLI script
section, not a checksummed `_SRC` module): pure arithmetic on
`constitution.required_margin` (unchanged, already tested) — no market
data, no backtest, no genome, no state write. Reads
`acct.researcher_memory`'s real `tested` count (182) and `holdout_draws`
count (13) as anchors, prints `required_margin()` swept across a
multiplicative grid of `n_candidates`/`n_draws` around those real counts
for both `MULTIPLE_TESTING_SIGMA` (fold-aggregate) and `HOLDOUT_SIGMA`
(sealed-holdout), then inverts the formula (`n = exp((target/sigma)^2 /
2)`) to answer directly: how many more candidates/draws would it take to
raise each margin by a further `+0.01` through `+0.25`.

## Result: the two gates behave very differently at today's real counts

**Fold-aggregate margin is nearly flat already.** At the real 182
candidates it's 0.258; even at 200x that count (36,400) it's only 0.367 —
+0.11 for a 200x increase in search volume. Raising it a further +0.10
above today needs ~123x more candidates (22,425) than exist now; +0.25
needs ~3,000,000x (574 million) — a number no real or shadow search will
ever reach. This directly qualifies the 13:07 run's framing: "gets harder
to clear as n rises" is true in direction but the effect size is small —
the shadow run's own near-miss candidate (fold-aggregate delta +0.245,
short of the ~0.258–0.270 margin across that run's 182→294 candidate
range) was not pushed meaningfully further out of reach by those 112
additional shadow candidates, and would not be pushed meaningfully further
by another 1,000 either.

**Sealed-holdout margin is NOT flat at today's scale.** At 13 real
cumulative draws the margin is 4.53; it only takes 4 more draws (17 total)
to raise it a further +0.25, and 13→130 draws (10x) moves it by +1.71 —
compare the fold-aggregate side's ~123x needed for a much smaller +0.10.
The reason is the same `sqrt(log n)` shape evaluated at a much smaller `n`
(low tens of draws vs. hundreds of candidates) — it's still on the steep
part of the curve. This is a genuinely different mechanical situation from
the fold-aggregate gate: every real promotion attempt that reaches the
holdout check (rare, but each one increments the cumulative draw count
permanently, never reset by a promotion per `holdout_accepts()`'s own
docstring) measurably raises the bar for the next one, in a way that
adding shadow-only fold-aggregate candidates does not.

## Reading

Corrects rather than reverses the 13:07 run's stagnation mechanism: rising
`n_candidates` is not, on its own, a meaningful explanation for why a
fold-aggregate near-miss stays a near-miss — that margin is already
essentially saturated. If there's a rising-bar effect on live promotion
difficulty, it's on the holdout side, where cumulative draws are still low
enough that each one matters. Doesn't change any of the "windowing line is
exhausted" or "no immediate follow-up on `HOLDOUT_SIGMA`" conclusions
already in `AGENTS.md` — this just replaces a hand-wavy "keeps getting
harder" claim with the actual numbers, and separates which of the two
gates that claim genuinely applies to.

## Verified safe

- New code is a CLI-only diagnostic in the plain script section of
  `evotrader_bundle.py` (added `import math` to the top-level import line —
  it was previously only imported inside checksummed `_SRC` modules), no
  `_SRC` module touched, nothing checksummed changed.
- `py_compile` clean.
- Full suite still 179 passed (no new pure functions added — this only
  calls the existing, already-tested `constitution.required_margin`).
- `live_state.json` md5 identical before/after
  (`8b3dc413c9a85fda04bdeb0ad4c63733`).
- `evotrader.manifest` md5 identical (`0bf3a7d9411ee692d0a9f152a7533803`),
  `constitution verified 8b74865634b1db07` unchanged on every invocation.
- `git status --short` showed only `evotrader_bundle.py` modified before
  this commit.
- Today's 2026-08-21 bar confirmed already processed by the 00:20 UTC
  daily run before this check started (`tick` not run this session, no
  double-trade).
- `review-hard-calls`: 0 pending.
- No genome promotion (no README `## Status` staleness risk).

## Next

The holdout-side finding here sharpens (doesn't replace) the still-open
question from this morning's `HOLDOUT_SIGMA` recalibration: whoever next
gets a real candidate to the sealed-holdout check should note both the
`HOLDOUT_SIGMA` outcome *and* the current cumulative-draw count at that
moment, since this run shows that count is not a fixed backdrop — each
attempt visibly moves the bar for the next one at today's scale. Not
attempted this run: nothing changes about the fold-windowing line (still
recommended exhausted) or about forcing a promotion candidate (still needs
a real or shadow search to actually beat the champion by enough on its
own, which `margin-curve` doesn't manufacture).
