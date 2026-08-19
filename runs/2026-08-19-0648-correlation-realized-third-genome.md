# Correlation-realized: third champion (v2), closing the "different genome" check

3-hourly self-improvement check. Today's daily bar (2026-08-19) was already
processed by the 00:20 UTC daily run (tick 5) before this check started —
`live_state.json`'s `updated` timestamp was `2026-08-19T00:21:55+00:00`,
well before this run; no tick attempted, no double-trade risk.

## What this run did

The 2026-08-19-0350 run ("correlation-realized-second-genome") closed with
an open line: two genuinely different genomes (v3, v1) had been checked with
`correlation-universe --realized --also-version N` and both showed
held-only correlation lower than universe-wide in every fold/holdout window,
but "v2 is also available as a third real data point in one line... if
wanted before acting" was left unresolved. This run took that one line:

```
python3 evotrader_bundle.py correlation-universe --realized --also-version 2
```

No code change — the `--also-version` flag already handles any past
champion via `_reconstruct_champion_genome`, verified bit-exact in prior
runs. This was purely running the existing, already-tested diagnostic
against the one remaining real champion.

## Result

v2's held-only mean correlation is lower than universe-wide in **all four
windows**, same shape as v3 and v1:

| window  | v2 held-only | universe-wide | delta |
|---|---|---|---|
| fold 1  | +0.424 | +0.630 | −0.207 |
| fold 2  | +0.442 | +0.509 | −0.067 |
| fold 3  | +0.411 | +0.616 | −0.204 |
| holdout | +0.404 | +0.572 | −0.168 |

Cross-genome comparison (held-only mean correlation, this run vs. the prior
run's v3/v1 numbers):

| window  | v3 (live) | v2 | v1 (seed) |
|---|---|---|---|
| fold 1  | +0.523 | +0.424 | +0.443 |
| fold 2  | +0.470 | +0.442 | +0.409 |
| fold 3  | +0.427 | +0.411 | +0.407 |
| holdout | +0.437 | +0.404 | +0.452 |

All three real champions this account has ever had (v1 seed, v2, v3 live)
now show the identical qualitative pattern: the champion's own position
selection (max 6 slots out of 27 symbols, `correlation_penalty` at its
default `0.0` no-op in every case) lands on a *less* correlated subset than
the wider universe average, in every single fold and the sealed holdout,
despite the three genomes differing by many generations of unrelated
parametric tuning (entry/exit thresholds, sizing, stop-loss, regime gating —
none of it correlation-aware).

## Reading against item 3's open decision

This closes the specific gap the prior run named: "not just another read of
v3" is done — v2 is a genuinely different, independently-tuned genome (the
account's first self-promotion, found by blind search from the seed) and it
lands on the same conclusion. Four independent measurements now agree:
universe-wide structure (2026-08-18), and portfolio-realized structure for
v3, v1, and now v2 (2026-08-19 x2). None show a concentration problem for a
correlation-aware sizing rule to have caught.

**This is now the complete set of real champions this account has ever
had** — there is no fourth real genome to check until a new promotion
happens. The honest remaining caveat, unchanged from the prior run: all
three are real *accidental* champions found by blind search optimizing for
fitness, not a genome deliberately built or mutated to concentrate exposure
— that would need an adversarial-style check (e.g. hand-construct a genome
that ignores diversification, or search with a fitness term that rewards
concentration, and see if the held-set correlation picture changes), not
another read of an organically-found genome. Not attempted this run.

## Verification

- Purely additive/read-only: no code changed (`git status --short` empty
  after this run — the diagnostic already existed).
- `live_state.json` md5 identical before/after:
  `09c35b692da1d694c5a3cace5d488f40`.
- `constitution verified dfae6a697f51fb49` reported at the start of the
  command, unchanged.
- Full test suite still 104 passed (no new tests needed — no new code).
- Today's bar confirmed already handled before this run started; no `tick`
  invoked this cycle.

## Next

Item 3's drop-vs-build decision now has its strongest evidentiary base yet:
four independent measurements, three of them genuinely different genomes,
all pointing the same way. If this item is ever revisited to actually make
a change, the two live options are: (1) treat this as sufficient and drop
`correlation_penalty`, `correlation_lookback`, and `RiskJudge.
_correlation_scale` as dead weight (all still at their no-op defaults
today), or (2) run the adversarial check described above first — a genome
that actually tries to concentrate — before concluding the mechanism would
never have caught anything. No further "check another real champion" runs
are possible; that data source is now exhausted (n=3, all found).
