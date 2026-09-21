# First real hard-call review — 2026-09-21 00:51 UTC

## Summary

- No live trading this cycle: tick 38 already handled at the dedicated
  00:20 UTC daily slot (`live_state.json`'s `updated` timestamp
  `2026-09-21T00:22:31+00:00` and `runs/2026-09-21-0020-daily-trading.md`).
  `38 % 7 = 3`, so no `evolve` batch fired as part of that tick either.
- `python3 evotrader_bundle.py review-hard-calls` (no args) showed
  **1 bar pending review** — tick 38's lone-voice ICPUSDT buy (agreement
  0.33, 0.86 conviction, 21.8% of equity). This is the first real live tick
  ever flagged `is_hard_call: true` since the `review-hard-calls`
  infrastructure shipped 2026-08-17 — AGENTS.md's item 4 has been waiting
  for exactly this since then.
- Reconstructed `RiskJudge.rule`'s scoring by hand against v3's evolved
  genes (`base_size_pct` 0.2392, `lone_voice_scale` 1.4791,
  `two_agree_bonus` 1.2, `max_position_pct` 0.25, `cash_floor_pct` 0.3503).
  14 buy candidates proposed that bar. ICPUSDT (lone-voice, share 1/3,
  conv 0.858, score `0.858*1.4791=1.2691`) was genuinely the top-scored
  candidate — higher than every two-consult-agreement symbol (e.g.
  NEARUSDT 0.8697, UNIUSDT 0.8416) and higher than the next lone-voice
  candidate, FETUSDT (conv 0.812, score 1.2010).
  `cash_avail = equity*(cash_pct 0.568134 - cash_floor_pct 0.3503) =
  $3012.9506894161623` to the digit; ICPUSDT's target hit the 25%
  position cap first, so `full_amount = min(0.25*equity, cash_avail) =
  cash_avail` exactly, matching the real order's $3012.95 to the cent and
  leaving $0.00 deployable — which is why every other candidate that bar,
  including higher-conviction FETUSDT, was correctly vetoed "no room:
  size cap or cash floor". Cash-floor exhaustion by the single
  highest-scored order, not a processing-order bug.
- One nuance flagged as an observation, not a defect: consult_moderate's
  rationale was "confirmed trend: ma-spread +11.4%, slope +0.34%, rsi 59
  in band" — the slope (+0.34%) is nearly flat, far weaker than every
  other candidate's slope that bar (range +1.55% to +17.18%).
  `consult_moderate.min_slope` is 0 (any nonnegative slope qualifies), so
  this is a legitimate signal by the evolved gene's own threshold, just
  weaker on the momentum axis than its lone-voice score alone suggests.
- Recorded verdict via `--tick 38 --verdict approve --notes '...'` (full
  arithmetic reconstruction in the note). Confirmed
  `review-hard-calls` now reports 0 pending, 3 reviewed (ticks 16, 32, 38).

## Verification

- `python3 -m pytest -q` → 426/426 passed after recording the verdict.
- Top-level key diff of `live_state.json` before/after: only `updated` and
  `hard_call_reviews` changed; `genome`, `broker`, `journal`,
  `researcher_memory`, `lineage`, `ticks`, `started` byte-identical.
- Dashboard rebuilt via `EVO_STATE="$(pwd)/live_state.json" python3
  evotrader_dashboard.py` — wrote `index.html` (19.4 KB), no errors.
- Genome unchanged at v3 (1d) live; no promotion this cycle, so no
  README.md `## Status` update needed.

## Repo state at run start

Container started with `main` checked out but 33 commits behind
`origin/main` (not detached HEAD this time). `git pull origin main`
fast-forwarded cleanly from `aaee4c8` to `da56a57` — nothing local to
lose, nothing discarded.
