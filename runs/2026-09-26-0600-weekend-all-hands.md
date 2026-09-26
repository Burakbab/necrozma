# Weekend all-hands, 2026-09-26 (~06:00-07:20 UTC)

Two pieces of work this session: a new read-only diagnostic for item 5
(short selling), and one larger real `evolve` batch against the live v3
champion using the extra time budget a weekend slot gets over a 3-hourly
check.

## 1. `short-headroom`: is there real upside on the table from shorting?

### Why this, not something else

Reviewed `AGENTS.md`'s "Owner decisions pending" and "Next steps" before
starting. Items 6 (equities/FX data source) and 13 (`HOLDOUT_SIGMA`
calibration) are both explicit owner-only calls the file says not to
re-litigate with more diagnostics. Items 2/3/3a/8/9/10/11/12 are closed or
resolved. Item 7 (bundle unflatten) is feature-complete and explicitly
optional/last. That leaves item 5 (short selling) as the one open item with
real, un-owner-gated engineering room left: Phase 1 broker mechanics
(`PaperBroker.short()`/`.cover()`) shipped 2026-09-08, the sign-landmine
audit and cover-intent wiring are done as of 2026-09-14, and what remains —
"whether/how the Researcher should be allowed to propose short
positions" — is explicitly flagged as unscoped and owner-gated.

Before spending a session designing that wiring (which touches
`RiskJudge.rule`'s sizing loop and `SuperiorJudge.review`'s cap-check, both
of which currently have no "open a short" path at all — only "buy",
"sell", and "cover" are handled), the more useful question to answer first,
and the one this repo's own culture already prefers (see item 3's
correlation-penalty saga: measure before building, five separate real and
adversarial checks before touching a single gene), is: is there real
theoretical edge here at all, or would a short-opening signal be chasing
something that isn't there?

### What was built

`loop.engine.benchmark_sell_short(replay, symbols, start, end, cash,
fee_bps, slippage_bps, borrow_bps_per_bar, bars_per_year)` — a sibling to
the existing `benchmark_buy_hold`. Where `benchmark_buy_hold` computes an
equal-weight long's NAV path with zero costs (raw price math, no broker),
this function opens an equal-weight short of the same basket using the
*real* `PaperBroker.short()`/`.mark()`/`.cover()` mechanics: real
`fee_bps`/`slippage_bps` (pulled from the genome's own `broker` config, not
invented), real per-bar borrow accrual (`borrow_bps_per_bar`, a modelled
constant in the same family as fee/slippage — explicitly *not* a measured
real crypto borrow rate, since nothing in this repo has ever measured one),
and the same entry/exit fill-price convention `benchmark_buy_hold` uses.
The circuit breaker is effectively disabled (`dd_halt=10.0`) since a static,
unmanaged short has no exit discipline of its own for a breaker to protect —
the point is to see the raw, un-stopped path.

One correctness subtlety worth recording: at zero cost this function's
`total_return` is exactly the negative of the *true* fill-to-fill long
return (`-(replay.close_at(s, end-1) / replay.next_open(s, start) - 1)`,
equal-weight averaged) — but it is *not* bit-identical to
`-benchmark_buy_hold(...)['total_return']`, because `benchmark_buy_hold`
values its own starting position at the close of the first tradeable bar
rather than at the fill price used to size it, a pre-existing one-bar
reference-point quirk in that already-relied-upon function. The gap is
bounded by one bar's own intrabar move and negligible over the many-bar
fold/holdout windows this is meant to run against; it only showed up
clearly while testing against a short, sharp synthetic price path. The
first version of this diagnostic's docstring and test suite claimed an
exact bit-for-bit mirror against `benchmark_buy_hold`'s own output, and the
first test run caught the discrepancy immediately (three failing
assertions, ~3-4% relative error on a 30-bar synthetic series) — fixed by
deriving the correct oracle by hand (worked through the linear equity
identity `equity(price) = cash_start + notional*(1 - price/entry)` for a
fully-invested short) and rewriting both the docstring and the tests
against that, rather than against `benchmark_buy_hold`'s own number.

New CLI command `evotrader_bundle.py short-headroom [--interval X]
[--borrow-bps-per-bar Y]` (default borrow 3.0 bps/bar, an explicit modelling
assumption) reports `benchmark_buy_hold` next to two `benchmark_sell_short`
runs (0bp borrow, and the modelled borrow rate) over the champion's own
`regime`-style fold/holdout windows, plus a "captured" column: how much of
the zero-cost theoretical short edge (`-buy&hold return`, meaningful only
when buy&hold itself lost) survives real costs.

8 new tests, `tests/test_short_headroom_benchmark.py`: zero-cost mirror
property (declining and rising price paths), short profits in a decline,
short loses in a rally, costs/borrow only ever reduce the return (never
improve it), multi-symbol equal-weight averaging, and the two early-return
contracts (`{}` for no usable symbols / too-short window) `benchmark_buy_hold`
already has. Full suite 426 → 434 passed.

Mechanical note: this repo's test suite runs entirely against the code
embedded in `evotrader_bundle.py`'s `_SRC` dict (`tests/conftest.py` imports
`evotrader_bundle` at collection time, which installs a meta-path finder
that intercepts every `from loop.engine import ...`-style import), *not*
directly against the real `loop/engine.py` file on disk, even though the
import syntax looks identical. Editing `loop/engine.py` alone left the
tests silently importing the stale pre-edit bundle version and failing with
a confusing `ImportError: cannot import name 'benchmark_sell_short'` even
though a bare `python3 -c "import loop.engine"` in a fresh interpreter
worked fine. `tools/edit_bundle_module.py sync` (real files → bundle,
already documented in `AGENTS.md` item 7) is the fix, and is now run
immediately after any real-file edit in this style of session, before the
first test run rather than after a confusing failure.

### First result

```
SHORT-THE-INDEX HEADROOM BY FOLD/HOLDOUT -- equal-weight, static, unmanaged
  window       bars   buy&hold  short 0bp  short+borrow   captured
  fold 1        353    +84.6%    -85.3%       -99.4% n/a (bull)
  fold 2        414   +121.1%   -136.9%      -157.9% n/a (bull)
  fold 3        414    -39.1%    +36.9%       +26.8%       +69%
  holdout       219    +57.1%    -61.1%       -67.9% n/a (bull)
```

Three of the champion's four real windows are strong bull markets. A naked,
always-on, equal-weight short of the same 27-symbol universe would have
lost -85% to -158% in each of them (a loss exceeding 100% of starting
capital is real and expected here — no leverage was used, but a short's
downside is unbounded on the upside, unlike a long's bounded-at-zero
downside). Only fold 3, the one genuine bear window, is where shorting
would have helped: buy&hold lost -39.1%, and a realistically-costed short
captured +69% of that theoretical edge (+26.8% real return).

### Reading, and what this does/doesn't decide

This rules out the simplest version of "just add a short" — a permanent,
regime-blind short overlay would be actively dangerous three years out of
four on this universe's real history. It does *not* rule out shorting
altogether: the one bear window shows genuine, cost-surviving edge. What it
argues for, if this is ever built, is a **regime-conditional** entry
signal (something that only opens a short when a `bear`/`crisis`-style
condition holds, mirroring how `RiskJudge.rule`'s own `regime_scale` gene
already gates *long* entries by regime) rather than a standing position —
sharpening the still-open Phase 2 design question rather than answering it.

Nothing here is a proposal, gene, or code path a real search can reach:
no genome field changed, no `RiskJudge`/`SuperiorJudge` code path for
opening a short exists yet, no mutation range was added, and
`live_state.json` was untouched throughout. The two owner-gated
constitution questions the 2026-08-30 design pass raised (a short-exposure
cap; whether `MAX_DD_HARD_FAIL` needs a short-specific instrument given a
short's unbounded downside — now underlined by this session's -157.9%
worst case) still need a human decision before any real wiring, whatever
this measurement found.

Verified before commit: `python3 -m pytest -q` 434/434; `tools/
edit_bundle_module.py sync --check` and `verify` both clean;
`evotrader.manifest` unchanged (`726dfa4bac85891a`) — `core/portfolio.py`,
the one file this session came closest to (short/cover mechanics live
there), was read but never edited; only `loop/engine.py` (a new function,
additive) and `evotrader_bundle.py`'s own CLI dispatch section (not part of
`_SRC`, no sync needed for that half) changed. `live_state.json` untouched.
Committed and pushed (`a1d1fda`) before starting the `evolve` batch below.

## 2. One real 30-generation `evolve` batch against live v3

With the diagnostic shipped and nothing else queued (`review-hard-calls` 0
pending, items 6/13 still owner decisions, `AGENTS.md` comfortably under
its 256KB single-read threshold), used the rest of this session's larger
time budget for one real `evolve` batch — bigger than a weekday 3-hourly
check's usual 15 generations, on the theory that a weekend slot should go
deep (one larger, more thoroughly verified batch) rather than wide (several
separate small ones).

Ran via `tools/background_runner.py` (`start` + a separately-backgrounded
`wait`, per the repo's own standing rule against pairing a tool's own
`run_in_background` with a shell `&`), exit code 0, no truncation, ~30
minutes for 30 generations.

**No promotion.** Champion's fold-aggregate fitness held flat at 1.751
across all 30 generations (959 trades, 38% win rate, 1% stops, 4 halts,
unchanged throughout). Cumulative candidates tried against v3 rose
33963 → 34379 (`researcher_memory.tested`), stagnation/boldness counter
2449 → 2479. Best-of-generation fold-fitness ranged 1.511-2.265 — several
generations' best candidate genuinely beat the champion's own *raw* fold
fitness (1.751), which is enough to trigger a holdout check
(`holdout-pressure`'s cumulative draw count advanced 648 → 651 over this
batch, three new draws), but none came remotely close to clearing the much
higher multiple-testing-adjusted promotion margin (still ~7.2x the best
individual real edge measured so far, per item 13's already-tracked,
still-not-a-scheduled-session's-call question). This is the same pattern
every 3-hourly `evolve` batch this week has logged; running one bigger
batch instead of two 15-generation ones didn't change the qualitative
picture, which is itself a small data point supporting item 13's own
framing: the bottleneck is the ever-rising cumulative margin, not the
volume of search per session.

Verified before commit: `python3 -m pytest -q` 434/434 both immediately
after the diagnostic commit (baseline) and again after `evolve`; top-level
key diff of `live_state.json` (checked directly in Python against `git
show HEAD:live_state.json`, not eyeballed) showed only
`updated`/`researcher_memory`/`lineage` changed — genome, broker, journal,
and `hard_call_reviews` byte-identical; `lineage` length unchanged at 202
(bounded ring buffer, no new promotion attempt recorded);
`tools/edit_bundle_module.py verify`/`sync --check` both clean (nothing
touched here needed a bundle resync — no module source changed in this
half); `holdout-pressure` re-checked, read-only, no state change beyond the
draw count above; `review-hard-calls` still 0 pending, 4 reviewed; dashboard
rebuilt with `EVO_STATE` set (`index.html` now shows 34379 challenger ideas
tried). Genome still v3 (1d) live, untouched throughout both pieces of this
session.

## Housekeeping

`AGENTS.md`'s "Current state" and item 5 sections updated in the same
commits as each piece of work. File size after both edits: ~230KB, still
comfortably under the 256KB single-read threshold — no archival needed
this cycle. No constitution amendment, no genome promotion, so no
`AMENDMENTS.md` row and no `README.md` `## Status` update were needed.
