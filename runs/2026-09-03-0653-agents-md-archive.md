# 3-hourly check: archive AGENTS.md's oldest history

2026-09-03 ~06:47-06:53 UTC

## Context

Daily bar already handled at 00:20 UTC (tick 20, held, no trade) — `live_state.json`'s
`updated` timestamp (2026-09-03T00:22:19Z) matches `runs/2026-09-03-0020-daily-trading.md`,
so no tick this cycle.

Every numbered "Next steps" item in `AGENTS.md` is currently blocked on something outside
a routine session's authority: item 2 (4h-bar shadow evolution) has three consecutive
sessions recommending the "accept vs. redirect" call be made explicitly by the next
session/owner rather than running a sixth search seed — deciding to move toward a real
promotion attempt is a high-blast-radius call this session isn't going to make
unilaterally, and "redirect" doesn't point anywhere actionable either (item 4 has zero
pending hard calls to review — checked via `review-hard-calls`; item 5 is blocked on a
human sign-off + constitution re-seal; item 6 is blocked on a human picking a real data
source). So this cycle didn't touch item 2, and instead found and fixed an unrelated
operational problem.

## What was found

Tried to `Read` `AGENTS.md` at the start of this session per the run protocol and the
tool call failed outright: the file had grown to ~510KB / 7486 lines, over the Read
tool's 256KB single-call limit. Had to fall back to `grep`+offset reads to get through
the Run protocol and Next steps sections. This wasn't previously flagged anywhere in the
file itself, and at the file's current growth rate (multiple dated entries added per
3-hourly cycle) it was only going to get worse for every future session.

## What was done

Split `AGENTS.md`'s "Current state" dated-entry log (the file's only genuinely
chronological, ever-growing section) at a clean bullet boundary: kept the newest ~5 days
(2026-08-29 ~22:50 UTC onward) plus the full "Next steps" list, promotion-history
narratives, "Measured", and "Rules" sections in place; moved everything older
(2026-08-15 through 2026-08-29 ~19:12 UTC, ~4300 lines) verbatim into a new file,
`AGENTS_ARCHIVE_2026-08-15_to_2026-08-29.md`, with a short header explaining what it is
and pointing back at `AGENTS.md`.

Verified before committing:
- `diff` of (kept head + moved block + kept tail) against the original `AGENTS.md` was
  byte-identical — confirms the split lost or altered nothing, only relocated text.
- New `AGENTS.md` is 232,811 bytes (~227KB), safely under the 256KB Read limit again; the
  archive file is 291,419 bytes, holding everything that was removed plus its own header.
- Left a pointer entry in `AGENTS.md`'s Current state (top of the archived boundary)
  naming the archive file and the exact cutoff, and noting a future session should
  archive again if growth continues at this pace.
- Full test suite: 338/338 (unchanged from baseline). `tools/edit_bundle_module.py sync
  --check`: clean, no drift. `live_state.json` untouched (this is a docs-only change —
  only `AGENTS.md` was modified and one new file added; no code, no protected file, no
  constitution-checksummed file touched). `evotrader_bundle.py summary` runs clean.

## Not done / next steps

This is a one-time archival pass, not a permanent fix — `AGENTS.md`'s "Current state"
log and the "Next steps" list's own per-item chronological pointer histories (item 2's
alone is ~1100 lines) will keep growing. A future session should archive again once the
file approaches the 256KB limit — same mechanical, diff-verified split, no rewording.

Item 2's accept-vs-redirect decision (see `AGENTS.md` Next steps item 2) is still open
and still explicitly the next session/owner's call, not decided or touched this cycle.
