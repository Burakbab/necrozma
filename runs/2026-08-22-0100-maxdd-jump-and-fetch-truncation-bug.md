# A -46.5% baseline maxDD, and a real silent-truncation bug in the fetch path — 2026-08-22 01:00 UTC

## Scope

Started as the flagged Next-steps item 2 follow-up ("an honest design pass on
whether `MAX_DD_HARD_FAIL`'s margin is right given how many single-symbol
removals cross it" — open since the 2026-08-21 19:02/22:10 `universe-perturb`
runs). Turned into something more urgent once the very first command run this
session (`universe-perturb --drop ETHUSDT`) printed a champion-v3,
**unperturbed, 27-symbol, full-history baseline** of `-46.5%` maxDD, hard-fail
(`fitness = -inf`) — not the `-34.1%` every session this week, including the
one 2.5 hours earlier, had consistently reported for the exact same
computation. That gap (12.4pp, crossing `MAX_DD_HARD_FAIL`'s own 40% line) was
too large to build a design pass on top of without first finding out which
number is real.

## What was checked, in order

1. **Reproduced independently, 3 ways, all agreeing on -46.5%:**
   `universe-perturb` (with and without `--also-version 1`), the `drawdown`
   CLI, and a hand-rolled `nav_history` peak/trough trace all gave the same
   answer: peak $38,379 on 2024-12-08, trough $20,541 on 2025-06-22, "not
   recovered" through today (2026-08-22 NAV $32,306, still below that peak).

2. **Ruled out a live-tick/state problem.** `live_state.json`'s own genome
   (version 3) is what every one of these runs loaded — same account, no
   promotion, no edit. `summary`/`review-hard-calls` clean, today's bar
   (2026-08-22) already processed by the 00:20 UTC daily run before this
   session started, `tick` not run this session.

3. **Ruled out a fabricated/corrupted individual data point.** The scan that
   found the maxDD episode also turned up one alarming single-bar move worth
   naming explicitly: `TRXUSDT` 2024-12-02→12-03, `0.2072 → 0.4334` close
   (+67% in a day). Queried Binance's own public data mirror directly
   (`curl https://data-api.binance.vision/api/v3/klines?symbol=TRXUSDT...`,
   bypassing every line of this project's own fetch/cache code) and got back
   the identical numbers, with volume ~13x the days around it (4.73B vs
   ~0.3-1.4B) — a real, exchange-recorded move (plausibly the Nov/Dec 2024
   Trump-adjacent WLFI/Sun news cycle), not a decoded-wrong or duplicated
   candle.

4. **Corroborated with a genome-independent read.** `regime` (raw
   equal-weight buy-and-hold, no genome, no backtest) on this session's fetch:
   fold 3 (2024-11-27→2026-01-15) maxDD **-55.9%**, and — separately, and more
   currently relevant — the **sealed holdout itself** (2026-01-15→today,
   219 bars) shows **-40.3% maxDD, -22.6% return** on raw buy-and-hold. The
   holdout window being a genuinely bad stretch isn't new (the 2026-08-17
   `regime` run already flagged it as "the worst window of the four... not a
   lucky bull run" at a smaller magnitude); what's new is how much worse it's
   gotten in the days since, and that it's now large enough on its own to
   plausibly be moving the full-history number.

5. **Checked this session's own fetch for the exact failure mode that would
   explain the discrepancy — a partial/truncated historical fetch silently
   passing as "reached the end of history".** All 27 symbols: 1,461 daily
   bars each, 2022-08-23→2026-08-22, **zero missing calendar days** (checked
   via `pd.date_range` diff against each symbol's actual index). So *this*
   session's own data is clean by this test. That doesn't prove what produced
   the earlier `-34.1%` reads was corrupted — there's no way to inspect a
   past, ephemeral container's cache after the fact (`state/` is gitignored by
   design, a fresh empty cache every session) — but it does mean this
   session's own -46.5% number isn't explained by *this* class of bug, and it
   surfaced a real, previously-unguarded vulnerability worth closing either
   way.

## The bug, and the fix shipped

`core.market.fetch_klines`'s pagination loop treated any page under 1,000
rows as unconditional proof the requested range was exhausted:

```python
if len(batch) < 1000:
    break
```

A transient partial response from `data-api.binance.vision` mid-range looks
identical to a real end-of-history page under that check — the loop exits
early, `rows` silently ends up short, and nothing downstream (`load`,
`load_universe`, any backtest) had any way to notice. No exception, no log
line, no test would have caught it — this is exactly the "understates risk
with no error surfaced" failure mode that AGENTS.md's own culture (fail loud,
checksum the scoreboard) exists to prevent, just in a different corner of the
codebase than the constitution package.

Two changes, both in `core.market` (not checksummed — only
`constitution/__init__.py` and `core/portfolio.py` are):

1. **`fetch_klines`**: a short page that stops *before* the requested `end_ms`
   now gets up to 3 bounded retries (backing off 1.5s/3s/4.5s) before being
   accepted as real end-of-history. A genuine end-of-history page (or one
   that actually reaches `end_ms`) still exits on the first try, so this
   costs nothing in the common case.
2. **`find_gaps(df, interval)`** (new, pure): diffs a symbol's actual index
   against the full expected calendar grid between its first and last bar.
   Wired into `load_universe`, which now prints a loud `[market] WARNING`
   naming the symbol, bar count, and first few missing timestamps if any gap
   survives the retry — catching this class of bug regardless of cause
   (this fix, a future different bug, or a stale pre-fix `state/cache/*.pkl`
   from within the same long-running container).

Tested: `tests/test_market_gaps.py`, 5 new tests (contiguous/single-gap/
multi-day-gap/empty/hourly-step), full suite **184 passed, up from 179**.
Edited via `tools/edit_bundle_module.py extract/reinsert core.market`,
`verify` round-trip clean, `py_compile` clean. `evotrader.manifest` unchanged
(`0bf3a7d9411ee692d0a9f152a7533803` — `core.market` isn't part of the
checksummed set). `constitution verified 8b74865634b1db07` on every
invocation this session. `live_state.json` md5 unchanged throughout
(`3f71d6ab111ecd646eda9e0e595a9970` — differs from the prior session's
recorded hash only because `tick` ran once between sessions, at 00:20 UTC,
before this session started; unchanged *within* this session).
Manually exercised `find_gaps` against a synthetic gapped index outside the
test suite too, to confirm the detection logic end-to-end, not just via
mocked unit tests.

## What's still open, honestly

- **Root cause of the -34.1% vs -46.5% discrepancy is not proven, only
  narrowed.** This session's data passed the gap check; there's no way to
  retroactively audit whatever produced the earlier reads. The fix closes the
  most concrete failure mode found, but "some other session hit this exact
  bug, repeatedly, with the exact same resulting number, several times this
  week" is a real leap even if the mechanism fits. Flagging this as *likely*
  the explanation, not confirmed.
- **If -46.5% is the correct number**, the champion's own unperturbed
  full-history backtest currently hard-fails `MAX_DD_HARD_FAIL` — a
  materially different, more urgent situation than the "5.9pp margin, cliff
  nearby but not crossed" picture the last several days of `universe-perturb`/
  `margin-curve` entries describe. This does **not** halt live trading
  (`MAX_DD_HARD_FAIL` gates evolution/promotion decisions, not the daily
  tick's own trade execution — today's tick 8 ran and traded normally before
  this session started), but it means: **do not trust the -34.1%/5.9pp-margin
  framing from the last several `Current state` entries without re-checking
  it against a gap-verified fetch first.**
- The design pass this session set out to do (whether `MAX_DD_HARD_FAIL`'s
  40% threshold itself is right) is **not attempted this run** — building it
  on a number that may already be wrong would be worse than not building it.
  Next session with spare capacity: re-run `universe-perturb`'s full 27-symbol
  single-drop census fresh (now that `load_universe` will loudly flag any
  gap), and only then pick the design-pass thread back up if the finding
  survives.
- Push notification sent to the user this session, given the severity and
  the fact this directly touches whether the last several days' fold/margin/
  universe-perturb findings are trustworthy.

## Verification checklist

- `git status --short`: clean except the intended `evotrader_bundle.py`
  (`core.market` module) and this run note + new test file.
- Full suite 184 passed (up from 179), `tools/edit_bundle_module.py verify`
  clean, `py_compile` clean.
- `live_state.json` untouched this session (md5 constant across every
  command run: `3f71d6ab111ecd646eda9e0e595a9970`).
- `evotrader.manifest` unchanged (`0bf3a7d9411ee692d0a9f152a7533803`),
  `constitution verified 8b74865634b1db07` on every invocation, never
  "CONSTITUTION MODIFIED".
- Today's 2026-08-22 daily bar confirmed already processed by the 00:20 UTC
  run before this session started (`updated` timestamp
  `2026-08-22T00:21:18+00:00`); `tick` not run this session, no double-trade.
  `review-hard-calls`: 0 pending.
  No genome promotion, no README `## Status` change needed.
- Repo-state note: session started with local `main` detached from an
  unrelated pre-restart ref against a force-updated `origin/main` (the same
  recurring container-seed artifact prior sessions have logged) — reset to
  `origin/main` per the run protocol, no work lost.

## Next

1. Re-run the universe-perturb single-symbol census fresh under the fixed
   fetch path (gap-checked) before treating either the -34.1% or -46.5%
   reading as settled, and before resuming the `MAX_DD_HARD_FAIL` design pass.
2. If -46.5% (or something close to it) reproduces again under a verified
   gap-free fetch, that upgrades this from "worth a design pass" to "the
   champion may currently be failing its own risk gate for real" — worth its
   own urgent look, independent of the single-symbol-perturbation framing.
3. Keep an eye out for the `[market] WARNING` line in any future run's output
   — if it ever fires for real, that run's numbers should be treated as
   suspect until re-fetched clean.
