# 3-hourly check, 2026-08-29 06:59 UTC — `promotion-excess-check`

## What this session did

Today's daily bar was already processed before this session started
(`runs/2026-08-29-0020-daily-trading.md`, `live_state.json.updated` =
2026-08-29T00:21Z) — no `tick`/`evolve` call, per protocol.

Picked up the sharpest thing the 06:00 UTC weekend all-hands entry flagged
but explicitly did not attempt: since sealed-holdout fitness (which gates
every real promotion) is dominated by a challenger's own market-beta-driven
absolute return rather than its skill relative to buy-and-hold, does an
excess-return-based selection criterion ever actually disagree with what a
real historical promotion picked? That question had never been checked
against this account's own two real promotions (v1→v2, v2→v3) — it was
raised as a design question, not a measurement gap, but the measurement
itself is a same-day-sized diagnostic in the codebase's own established
style (`succession-audit`, `fold-scheme --also-version`), not the "dedicated
design pass" the weekend entry deferred.

## New command: `promotion-excess-check`

For each real accepted promotion in `acct.lineage`, reconstructs both the
champion and the challenger genome (`_reconstruct_champion_genome`) and
replays both on identical footing against today's data
(`Evaluator.evaluate` for fold-aggregate, `Evaluator.holdout_check` for the
sealed holdout), comparing four things pairwise: fold-aggregate raw fitness,
fold-aggregate excess return, sealed-holdout raw fitness, sealed-holdout
excess return. Reports which side (champion/challenger) each of the four
prefers and flags any case where raw fitness and excess return disagree.
Where the real promotion's own recorded `champion_edge`/`edge`/`holdout_edge`
exist in `live_state.json` (only the v2→v3 promotion — the schema didn't
track `edge` yet at v1→v2), prints those actual promotion-time numbers too,
clearly separated as a cross-check on a different, smaller, sliding window —
not conflated with the same-basis replay.

Composes only already-tested `_reconstruct_champion_genome`/
`Evaluator.evaluate`/`Evaluator.holdout_check` — same precedent as
`succession-audit`/`fold-scheme`/`holdout-pressure`. No new pure function,
no constitution or `live_state.json` change, no `run_from_files.py` addition
(item 7 is closed per the 2026-08-24 09:46 UTC entry; not reopened here).

## Result: no disagreement found, on either real promotion

```
== promotion v1 -> v2 ==
  fold-aggregate fitness:  champion -2.804  challenger -2.617  -> challenger wins
  fold-aggregate excess return:      champion -107.7%  challenger -94.5%  -> challenger wins
  sealed-holdout fitness:  champion -0.404  challenger -0.317  -> challenger wins
  sealed-holdout excess return:      champion +12.3%   challenger +13.2%  -> challenger wins
  agree

== promotion v2 -> v3 ==
  fold-aggregate fitness:  champion -2.617  challenger -1.695  -> challenger wins
  fold-aggregate excess return:      champion -94.5%   challenger -28.6%  -> challenger wins
  sealed-holdout fitness:  champion -0.317  challenger +0.525  -> challenger wins
  sealed-holdout excess return:      champion +13.2%   challenger +23.4%  -> challenger wins
  agree
  (cross-check, actual promotion-time recorded values: champion fold-agg
   excess -35.1%, challenger fold-agg excess +6.8%, challenger holdout
   excess +21.7%, beat_benchmark=True — same direction as the replay above)
```

Both real promotions this account has ever made would also have been picked
by an excess-return criterion, on this same-basis-against-today's-data
replay. This is evidence, not proof the two criteria are equivalent in
general — two data points, both from a long-only, net-long-biased lineage
where a genuinely better policy and a higher market-beta absolute return
are not (yet) known to pull apart in either observed transition. It answers
the concrete question the weekend entry left open ("has this ever actually
been checked against a real promotion") without touching the larger,
deferred question (whether the selection *metric itself* should be
redefined around excess return) — that stays exactly where the weekend
entry left it, an owner-level design decision.

## Verified safe

- `md5sum live_state.json evotrader.manifest` unchanged before/after:
  `bf360fc7f86f6bae2bc46bb6f6dc6026` / `0bf3a7d9411ee692d0a9f152a7533803`.
- `python3 -m pytest -q` — 240/240 passed (no new tests needed — pure CLI
  composition of already-tested functions, same precedent as every other
  diagnostic added this way in this file).
- `tools/edit_bundle_module.py sync --check` — clean (the new code lives in
  `evotrader_bundle.py`'s own CLI dispatch, not in any `_SRC` package
  module, so this doesn't touch the bundle/real-files sync surface at all —
  confirmed by re-running `sync --check` after the edit).
- `python3 -m py_compile evotrader_bundle.py` — clean.
- `constitution verified 8b74865634b1db07` unchanged.
- No genome promotion, no `AMENDMENTS.md` row needed (no constitution value
  touched), no README `## Status` change needed.
- `git status --short` was clean before this session started; only
  `evotrader_bundle.py` changed.

## Next steps

- The larger question this measures but does not settle — whether
  fold/holdout selection should be redefined around excess return instead
  of raw Sortino `fitness()` — is unchanged: still flagged in "Current
  state" (2026-08-29 weekend entry) as needing its own dedicated design
  pass, not moved forward by this diagnostic beyond giving it one more real
  data point.
- If a third real promotion is ever made, `promotion-excess-check` will
  pick it up automatically (it iterates `acct.lineage`, no version numbers
  hardcoded) — worth re-running then to see if two-for-two agreement holds.
- The still-open v3 demotion/rollback design question (2026-08-22) is
  unchanged by this session and not restated further here, per the same
  no-noise judgment the 2026-08-28/29 daily discussions already applied.
