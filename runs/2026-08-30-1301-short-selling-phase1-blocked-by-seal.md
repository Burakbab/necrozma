# Short selling Phase 1: implemented, reverted — blocked by the constitution seal

**3-hourly check, ~13:01 UTC.** Followed up on the 09:51 UTC design pass's
concretely-scoped Phase 1 (item 5 in AGENTS.md's "Next steps"): `PaperBroker`
gains `short()`/`cover()` alongside `buy()`/`sell()`, `mark()` gains borrow
accrual, proven correct with new unit tests calling the broker methods
directly. Built it. Then had to revert all of it — not because the code was
wrong, but because of something the design pass missed.

## What got built (and then reverted)

- `Position.qty` goes negative for a short (no new schema field): `is_open`
  became `abs(self.qty) > 1e-12`, a new `is_short` property.
- `PaperBroker.short()` mirrors `buy()` — `quote_amount` capped by `self.cash`
  as a no-leverage buying-power proxy, slippage works against the seller
  (`eff = price * (1 - slippage_bps/10_000)`, you receive less), fee taken
  from proceeds, cash credited `quote_amount - fee`.
- `PaperBroker.cover()` mirrors `sell()` — slippage works against the buyer
  on the way back in, `pnl = (avg_cost - eff) * qty - fee` (profit when the
  cover price is below the entry price).
- Cross-side guards: `short()` refuses if the symbol already has an open
  long; `buy()` refuses if it already has an open short. Neither side can be
  flipped in one call — cover/sell first.
- `mark()` gained a `_update_peak` helper so `peak_price` tracks the highest
  price seen for a long but the lowest for a short (the trailing-stop
  reference point flips direction), and accrues `borrow_bps_per_bar * abs(qty)
  * price / 10_000` against cash for every open short, every bar — the same
  kind of flat modelled constant `fee_bps`/`slippage_bps` already are, per
  the design pass's own argument.
- `to_state()`/`from_state()` gained `borrow_bps_per_bar`, defaulting to 0.0
  so a pre-Phase-1 saved state still loads.
- `tests/test_short_selling.py`: 16 new tests — short→cover profit/loss,
  partial cover, `equity()` correctly falling as price rises against a short,
  both cross-side guards, cash-capping, borrow accrual (present, absent,
  long-exempt), a circuit-breaker trip mid-short, peak-price direction, a
  state round trip, and a regression test proving `buy()`/`sell()`/`mark()`
  produce byte-identical numbers to before for a caller that never touches
  the new methods. All 16 passed on the first correct pass (one intermediate
  failure round was a stale-bundle red herring, see below).

## Why it's reverted instead of committed

Ran the full suite after wiring the change into `evotrader_bundle.py` via
`tools/edit_bundle_module.py sync` (the documented step for any real-file
edit, since the bundle — not the real files — is what every scheduled
command actually executes). 12 tests in `tests/test_run_from_files_matches_
bundle.py` failed, all with the same message:

```
CONSTITUTION MODIFIED: expected 8b74865634b1db07, found ...
A human must review and re-seal before any run.
```

Traced it: `constitution.checksum()` hashes exactly two things —
`constitution/__init__.py` and `core/portfolio.py` (`_PROTECTED` in that
module, or `EMBEDDED_SOURCES['core.portfolio']` when running from the
bundle). `core/portfolio.py`'s own docstring says it "lives under the
constitution *in spirit*" — that phrasing undersold it. It is not a spiritual
alignment, it is one of the two files literally inside the anti-tampering
seal `evotrader.manifest` protects. Any edit to it, synced into the bundle,
trips `CONSTITUTION MODIFIED` the next time anything calls
`constitution.verify()` — which every scheduled command does at startup.

AGENTS.md's own Run protocol section already has the rule for this exact
message: *"If a run reports CONSTITUTION MODIFIED, stop. Do not re-seal it.
Investigate and check AMENDMENTS.md first."* There is also no CLI path that
re-seals the manifest — `verify()` only ever writes it when the file is
*missing*, never to overwrite a mismatch. The only way past this is a human
directly reviewing the diff and hand-editing `evotrader.manifest` (or
deleting it and letting `verify()` re-create it, which is the same act of
trust, just via a different mechanic). A scheduled session doing that on its
own initiative is exactly the failure mode the seal exists to prevent — "a
self-modifying system whose reward function is inside its own mutable
surface will always find it cheaper to edit the scoreboard than to learn the
game," per that module's own docstring, and `core/portfolio.py` is the
scoreboard here just as much as `constitution/__init__.py` is.

So: reverted everything. `git checkout -- core/portfolio.py
evotrader_bundle.py`, deleted `tests/test_short_selling.py`. Confirmed
`evotrader.manifest` itself was never touched (`verify()` doesn't write on
mismatch, only compares) and `python3 -m pytest -q` is back to 243/243.
`md5sum live_state.json` unchanged throughout
(`81922c6011c986449f635dbf43553d0e`) — no tick or evolve ran this session.

One intermediate wrinkle worth naming so a future session doesn't re-lose
time on it: the first test run after adding `short()`/`cover()` failed with
`AttributeError: no attribute 'short'` even though the real file had it —
`tests/conftest.py` imports `evotrader_bundle` at collection time, which
installs a meta-path finder that serves `core.*` from the bundle's own
`_SRC`, not from disk. Tests only see a real-file edit after `sync`. Not a
new discovery (item 7's own "Where things live" table already says this
about the bundle being the live path), but easy to trip over mid-edit.

## What this changes for item 5

The 09:51 UTC design pass's phasing put both constitution questions (a
short-exposure cap; whether `MAX_DD_HARD_FAIL` needs a short-specific
instrument) in Phase 2, after Phase 1's broker mechanics were already
landed, on the reasoning that Phase 1 was "zero behavior change for every
existing caller" and therefore safe to ship without owner involvement. That
reasoning was right about behavior and wrong about mechanism: zero behavior
change for existing *callers* is not the same thing as zero change to the
*bytes* `constitution.checksum()` hashes, and it's the bytes that gate every
scheduled run. Phase 1 needs the human-reviewed `AMENDMENTS.md` row and
manifest re-seal *before* it can land at all, not after, and not deferred to
Phase 2. Recommend: next session on this item should not re-attempt the
implementation without that sign-off already in hand. The design itself
(signed-`qty` convention, the guard structure, the borrow-accrual placement
in `mark()`) held up under a real implementation attempt and is worth
reusing verbatim once a human has reviewed and re-sealed — this was wasted
session time on the shipping mechanics, not on the design.
