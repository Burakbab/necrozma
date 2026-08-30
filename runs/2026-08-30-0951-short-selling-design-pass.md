# Short selling: design pass (no code shipped this session)

**3-hourly check, ~09:51 UTC.** Item 5 in AGENTS.md's "Next steps"
("Short selling with modelled borrow cost — currently long-only, which is
why a bear market can only be survived, not traded") has had zero history
since the file was created — every other open item has multiple prior
sessions' worth of measurement or code behind it, this one has none. Rather
than opening a diagnostic or writing code straight into the paper broker
(the file that "lives under the constitution in spirit" per its own
docstring), this session did a design pass: read the real long-only
assumptions end to end and wrote down what a real implementation needs,
mirroring the discipline this project already uses for other structural
questions (the fitness-vs-excess-return write-up, the dd-corrected maxDD
gate fix, the `HOLDOUT_SIGMA` recalibration) — measure/argue in writing
before code touches money-tracking or promotion logic.

**No code changed this cycle.** `md5sum live_state.json` unchanged,
`python3 -m pytest -q` 243/243 confirmed at session start, no genome or
constitution touched.

## Where "long-only" actually lives

Grepping instead of assuming turned up five separate places that each
independently encode "no shorting," not one central switch:

1. **`core/portfolio.py`'s `PaperBroker`** — the docstring says it outright
   ("Long-only for v0.1 (shorting comes later, with borrow costs
   modelled)"). Mechanically: `buy()` only ever grows `Position.qty` from a
   non-negative floor, `sell()` only ever shrinks an existing `qty > 0`
   position and refuses to act if none is open (`if not pos or not
   pos.is_open: return None`) — there is no path that creates a liability.
   `equity()` sums `qty * price` per symbol, which is correct for a long
   (`qty >= 0`) but would need materially different accounting for a short:
   a naive "let `qty` go negative" trick does make `equity()`'s sum point
   the right direction (a negative `qty * price` term reduces equity as
   price rises, which is correct for a short), but `avg_cost` bookkeeping,
   the `pnl = (eff - pos.avg_cost) * qty - fee` formula, and the "open
   more" vs "close" branch logic in `buy`/`sell` all implicitly assume
   `qty` moves in one direction per position — none of this is a
   free reinterpretation, it is a real rewrite of both methods plus new
   `short()`/`cover()` counterparts, done carefully enough that the
   existing long-only call sites (which will still be the only call sites
   for a long time — see rollout below) produce byte-identical output.

2. **`core/types.py`'s `Intent`/`Order`** — `side` is a bare string,
   `"buy" | "sell" | "hold"` on `Intent`, `"buy" | "sell"` on `Order`.
   `"sell"` means exactly one thing everywhere it's read: *close an
   existing long*. There is no way to express "open a short" in the
   current vocabulary without adding a real third value (or a
   `"buy"`/`"sell"`/`"short"`/`"cover"` four-way split) and updating every
   consumer.

3. **`agents/consults.py`** — grepped all three consults
   (`ContrarianConsult`, `MomentumConsult`, the third moderate/aggressive
   pair): every single `Intent(...)` construction in the file uses either
   `"buy"` or `"sell"`, and every `"sell"` is gated on `b.open_positions.get(sym, 0.0) > 0`-shaped
   logic upstream — none of them ever proposes opening a new short. Adding
   short-side proposals means adding a fourth kind of trading idea to
   every consult individually (what does "momentum wants to short a
   downtrend" even look like for `MomentumConsult`, distinct from what
   it already says for exits?), not just relabeling `"sell"`.

4. **`agents/judges.py`'s `RiskJudge.rule`** — buys and sells are
   partitioned by `it.side == "buy"` into two dicts and handled by two
   completely different code paths (exits are unconditional-if-above-
   threshold; entries are scored, sorted, and capped against
   `max_position_pct`/`cash_floor_pct`/`max_positions`). A short entry
   needs its own version of the entry path (sizing against a *short*
   exposure cap, not a long one) and its own exit path (`cover`, distinct
   from `sell`) — this is real new logic in the busiest judge in the
   system, not a relabeling.

5. **The risk gates themselves assume bounded downside.** A long position's
   worst case is losing the capital already committed to it — `equity()`
   can't go below the value of cash plus zero. A short position's
   worst case is unbounded (price can rise past any ceiling), which
   `mark()`'s circuit breaker (a *drawdown-from-peak* percentage check)
   doesn't obviously handle correctly if a single short blows through
   more than the position's own allocated capital before the next bar's
   `mark()` call re-evaluates it — the existing gate was never designed
   against that failure mode because it was structurally impossible
   before now.

## What real borrow-cost modelling needs

The project's stated no-credentials design (`## No credentials, anywhere`
in AGENTS.md — prices come from Binance's public, keyless market-data
endpoint) has no equivalent public, keyless *lending-rate* feed. This
isn't a blocker — `fee_bps`/`slippage_bps` are already flat, hand-set
constants rather than fetched live data (`PaperBroker.__init__`'s
defaults, 10/5 bps), so a modelled constant borrow rate is the same *kind*
of approximation the broker already makes for costs, not a new category.
Concretely: a `short_borrow_bps_per_bar` gene (natural home: the `broker`
gene group alongside `fee_bps`/`slippage_bps` in `core/genome.py`'s
`_DEFAULTS`), accrued against `cash` for every open short position inside
`PaperBroker.mark()` the same way `bars_held` already increments there.
Worth being explicit in whatever ships this that the rate is an assumed
constant, not observed — the same honesty this file already insists on
for buy-and-hold comparisons and holdout noise.

## Constitution-level questions this would force

Per this file's own standing rule, any change to promotion/risk gates
needs an `AMENDMENTS.md` row, argued in writing, same as `HOLDOUT_SIGMA`
and the dd-corrected maxDD fix were. Short selling raises at least two
gate questions that don't have obvious defaults:

- **A net-exposure or max-short-exposure cap**, analogous to
  `max_position_pct`/`cash_floor_pct` but for the short side, sized
  against the unbounded-loss concern above rather than reusing the long
  caps as-is.
- **Whether `MAX_DD_HARD_FAIL`'s existing definition (peak-to-trough on
  NAV) is still the right instrument**, or whether a short-specific
  hard stop (e.g., a single position's own loss ratio, independent of
  portfolio NAV) needs to exist alongside it — the -46.5%/-34.1%
  fold-merged-vs-continuous blind spot fixed 2026-08-22 was already a
  hard lesson in this gate seeing less than the real risk; shorting is
  exactly the kind of change that could reopen a new version of the same
  blind spot if not designed against deliberately.

Neither of these has a default answer in this write-up — they're the
actual design questions a real proposal would need to resolve, not
rhetorical.

## Recommended phasing (not started this session)

Mirrors the pattern this project already uses for every big structural
addition (`bar_interval`: additive gene, zero behavior change, verified
identical, *then* a shadow evolution to see if it's worth using;
hard-call flagging: infra shipped ahead of its first real case). The
scoping choice below deliberately does **not** split "broker mechanics"
into its own dead-code phase the way `bar_interval` did — a `short()`/
`cover()` pair on `PaperBroker` with genuinely nothing that ever calls
them would be exactly the kind of half-finished, speculative plumbing
this project's own code style avoids building ahead of need. Instead:

- **Phase 1 (one scoped, testable slice):** `PaperBroker` gains
  `short()`/`cover()` alongside `buy()`/`sell()`, `mark()` gains borrow
  accrual, `Position` gains whatever the accounting actually needs
  (either a `side` field or a signed-`qty` convention — the write-up
  above found genuine tradeoffs between these, not yet decided). Proven
  correct with new unit tests that call the broker methods *directly*
  (short → mark → cover round trips, borrow accrual over N bars, a
  circuit-breaker trip mid-short) — the same "prove the mechanism in
  isolation" approach `tools/edit_bundle_module.py` and `tick-dry-run`
  both used before anything upstream could reach the new code. Genuinely
  useful on its own (a tested, correct short-accounting primitive) rather
  than inert scaffolding, and still zero behavior change for every
  existing caller.
- **Phase 2 (wiring):** a real `allow_short` boolean gene (default
  `False`, same "opt-in, zero behavior change until flipped" convention
  as `bar_interval`), a fourth `Intent`/`Order` side vocabulary, and the
  two constitution questions above resolved and given `AMENDMENTS.md`
  rows *before* any genome can search into short territory even in
  shadow.
- **Phase 3:** shadow evolution with `allow_short=True` from a fresh or
  scaled seed, same never-touches-`live_state.json` discipline as every
  4h-bar shadow run — a real live cutover stays the owner's call, same
  gate this file already applies to 4h cadence and to real-money
  promotion.

**Recommendation: Phase 1 is a reasonable scope for a future 3-hourly or
weekend session to actually build**, now that it's scoped concretely
instead of being a one-line bullet. Not started here — this session's
output is the design, not the code, on the judgment that broker
correctness deserves the same measure-before-code discipline this project
already applies to constitution and promotion-gate changes, and that a
single 3-hour slot doing both design *and* a correct, fully-tested
rewrite of the money-tracking core was more than this slot should attempt
at once.
