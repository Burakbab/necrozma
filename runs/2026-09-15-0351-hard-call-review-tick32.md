# 3-hourly check — 2026-09-15 ~03:46-03:51 UTC — tick 32's hard-call reviewed

## Daily bar

Already handled. `live_state.json` `updated: 2026-09-15T00:23:11+00:00` before
this cycle's edit, tick 32 (bar 2026-09-14) traded DOTUSDT at 00:20 UTC (see
`runs/2026-09-15-0020-daily-trading.md`) and left a pending hard-call flag —
confirmed via `review-hard-calls` before touching anything. No new bar to
trade this cycle.

## What this cycle did: reviewed tick 32's flagged hard call

`review-hard-calls` flagged tick 32 as a lone-voice DOTUSDT buy (agreement
0.33, 0.90 conviction, 14.3% of equity, the only order the bar produced) —
the second live tick ever to trip `flag_hard_call` (first was tick 16,
2026-08-30).

Reconstructed `RiskJudge.rule`'s scoring arithmetic by hand against champion
v3's real evolved `risk_judge` genes (`base_size_pct` 0.2392,
`lone_voice_scale` 1.4791, `two_agree_bonus` 1.2, `max_position_pct` 0.25,
`cash_floor_pct` 0.3503) and matched it to the actual order to the cent,
same method as the tick 16 review:

- 13 buy candidates were proposed that bar. DOTUSDT was lone-voice (only
  `consult_moderate`, share 0.33, conv 0.904, score
  0.904 × 1.4791 = **1.337**).
- **UNIUSDT actually scored higher** (0.95 × 1.4791 = 1.405, the bar's
  single highest score) but was already held at 25.92% of equity
  (3096.17 / 11942.93 NAV) — over `max_position_pct` (25%), room −0.9% —
  correctly vetoed "no room: size cap" *before* DOTUSDT was even reached in
  score order. Not a ranking bug: the sort put UNIUSDT first, its own
  position cap is what excluded it.
- DOTUSDT was next-highest among candidates with actual room. Its target
  hit the 25% position cap, and `cash_avail`
  (equity × (`cash_pct` 0.4936 − `cash_floor_pct` 0.3503) = $1711.92) was
  the binding constraint — recomputed `full_amount` came to **$1711.9210**,
  an exact match (to the cent) of the real order's $1711.92.
- That consumed 100% of the bar's remaining deployable cash, leaving $0.00
  for anyone else — which is why every other candidate that bar, including
  ICPUSDT (score 1.319, higher than DOT's among the rest), LTCUSDT,
  ATOMUSDT, BNBUSDT, AVAXUSDT, NEARUSDT, FILUSDT, INJUSDT, XLMUSDT, ETHUSDT
  and TRXUSDT, was vetoed `"no room: size cap or cash floor"` — cash-starved,
  not a processing-order artifact.
- The underlying signal was an ordinary confirmed-trend read (ma-spread
  +20.8%, slope +3.61%, rsi 61 in-band), not an outlier bet.

**Verdict: `approve`** — recorded via `evotrader_bundle.py review-hard-calls
--tick 32 --verdict approve --notes '...'` (full notes text in
`live_state.json`'s `hard_call_reviews`). Same shape as tick 16: the evolved
genome's own risk logic (`lone_voice_scale` > `two_agree_bonus`, a scarce
cash floor) operated exactly as designed once the top-scored candidate
(UNIUSDT) was excluded by its own already-near-cap position size. Nothing to
correct. `review-hard-calls` now reports 0 pending, 2 reviewed.

## Verified safe

- `review-hard-calls` re-run after recording confirms 0 pending.
- `git diff --stat`: only `live_state.json` (11 insertions: `updated`
  timestamp + one new `hard_call_reviews` entry) and `index.html`
  (dashboard rebuild) — `genome`/`broker`/`journal` byte-identical, no other
  top-level key touched.
- `python3 -m pytest -q`: 415/415, run before and after — clean, no flake.
- `python3 tools/edit_bundle_module.py verify`: round-trip verified, bundle
  unchanged.
- Dashboard rebuilt against the updated state.

Genome still v3 (1d) live, unchanged throughout.
