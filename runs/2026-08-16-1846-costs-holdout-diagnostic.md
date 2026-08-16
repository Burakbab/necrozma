# Cost sensitivity on the sealed holdout window, 2026-08-16 ~18:46 UTC

3-hourly check. `live_state.json.updated` was 2026-08-16T06:56:33Z (the
weekend all-hands v2→v3 promotion); the last journal entry is still bar
2026-08-15 and today's bar doesn't close until 2026-08-17T00:00Z. Nothing to
do on the trading side, as expected on almost every 3-hourly firing — the
00:20 UTC daily run handles it.

Used the slot on the open item the 15:52 UTC cost-sensitivity run left
behind: "point the same tool at the sealed holdout window specifically to
see if the drawdown-gate margin is thinner out of sample."

## What changed

Added a `--holdout` flag to `evotrader_bundle.py costs`. Same guarantees as
before (never touches `live_state.json` or the champion, read-only,
replays history through the real Council). With the flag, the five cost
scenarios (baseline / 1.5x / 2x / 3x / 5x-slippage-only) run against only
the sealed `HOLDOUT_FRAC` slice — the newest 15% of history, the same bars
`loop.evolve.Evaluator.holdout_check` uses and the search never sees —
instead of the full 4 years. 21 lines changed in `evotrader_bundle.py`'s
`main()`; no core/loop/constitution module touched, so no risk to the
bundle's embedded-string modules.

`python3 -m py_compile evotrader_bundle.py` and the full `pytest tests/`
suite (36 tests) both pass unchanged after the edit.

## Result

```
COST SENSITIVITY — champion v3 — sealed holdout (newest 15% of history)
================================================================================================
  scenario                fitness    return  sharpe   maxDD  trades   fees paid  excess ret
  baseline                 -1.172   -15.0%   -0.75  -26.2%     158 $      191      21.7%
  1.5x costs                -1.167  -14.7%   -0.74  -26.2%     155 $      286      22.0%
  2x costs                  -2.051  -22.5%   -1.24  -31.7%     128 $      345      14.2%
  3x costs                  -1.814  -20.9%   -1.11  -29.5%     130 $      544      15.8%
  slippage stress (5x)      -1.648  -19.3%   -1.01  -28.9%     130 $      183      17.3%

  baseline fitness -1.172 -> worst scenario '2x costs' fitness -2.051 (-0.879)
```

Sanity check first: baseline holdout excess return is **+21.7%**, exactly
matching the v3 promotion record's sealed-holdout number in AGENTS.md's
"Current state" ("excess return +21.7%"). That is the same window computed
two different ways (the evolution loop's `Evaluator.holdout_check` vs. this
new CLI path) landing on the same number — confidence the `--holdout` slicing
is correct, not an independent re-measurement.

## Reading it: the answer is the opposite of what was suspected

The 15:52 run flagged that full-history baseline maxDD (-34.1%) was
uncomfortably close to the 40% hard-fail gate, and a 1.5x cost multiplier was
enough to cross it (-45.1%, `fitness = -inf`). The open question was whether
the *holdout* window — untouched during search, therefore the honest
out-of-sample check — had an even thinner margin.

It doesn't. On the holdout slice, baseline maxDD is **-26.2%**, and even at
2x costs (the worst scenario here) it only reaches **-31.7%** — nowhere near
40%, and meaningfully *safer* than every full-history scenario measured
15:52 UTC (-34.1% to -45.1%). No scenario here produces `fitness = -inf`;
the drawdown gate never fires on this window at any cost multiplier tried.

But read this next to the return numbers, not instead of them: the champion
is **losing money outright** on this specific holdout slice under every
scenario (baseline total return -15.0%, fitness -1.172 — negative, same sign
as the full "Current state" holdout numbers already on record). It still
clears buy-and-hold by the same +21.7% margin that passed the original
promotion gate, so the promotion decision was correct on its own terms — this
is a genuinely hard window for the strategy (net loser in absolute terms),
just not one that comes anywhere near tripping the drawdown circuit breaker
or the hard-fail gate. Those are two different claims and the raw fitness
column conflates them the same way the 15:52 note flagged for the
full-history run.

## What this doesn't answer

It doesn't localize *where* in the full 4-year history the -34.1% baseline
maxDD (and the -45.1% at 1.5x costs) actually comes from. The holdout is
only the newest 15% of the replay; the full-history run averages over
everything including that slice. Since the holdout's own drawdown is mild,
the thin-margin drawdown must live somewhere in the other 85% (the
search-visible region) — plausibly a specific bear-market segment or a
handful of crash bars, not evenly distributed. `costs` (full) and
`costs --holdout` now bracket the two ends that have been measured; nothing
yet isolates the middle. Flagged as the next step in AGENTS.md.

## Commands used

```
python3 evotrader_bundle.py costs --holdout
```
