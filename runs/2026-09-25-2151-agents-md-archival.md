# 3-hourly check: AGENTS.md archival rotation — 2026-09-25 ~21:47-21:52 UTC

## Context

No live trading this cycle. Tick 42 was already handled at the dedicated
00:20 UTC daily slot, and the prior 3-hourly check's own evolve batch
already ran at ~18:47-19:19 UTC (confirmed via `live_state.json`'s `updated`
timestamp at session start, `2026-09-25T19:13:50+00:00`, matching
`runs/2026-09-25-1919-evolve-batch-v3.md`; the intervening 20:30 UTC daily
evaluation, `runs/2026-09-25-2030-daily-evaluation.md`, was read-only and
didn't touch state). `review-hard-calls` confirmed 0 pending (4 reviewed,
unchanged). Items 6 and 13 under "Owner decisions pending" remain genuine
owner calls, not actionable by a scheduled session.

## What was done

`AGENTS.md` had regrown to 257,797 bytes — within ~4.3KB of the
262,144-byte (256KB) single-read limit, tighter than any recent cycle
(most prior cycles had 6KB+ of margin at the point they chose to keep
running an evolve batch instead). Rather than run another 15-generation
batch on top and risk crossing the limit before the next cycle, used this
slot for the overdue archival rotation.

Moved the oldest slice of the "Current state" chronological log — every
entry from `Run 2026-09-19 (3-hourly check, ~00:46-01:20 UTC)` through
`Run 2026-09-20 (3-hourly check, ~21:46-22:16 UTC)` — verbatim to a new
`AGENTS_ARCHIVE_2026-09-19_to_2026-09-20.md`. `AGENTS.md` now keeps
everything from `Run 2026-09-21 (3-hourly check, ~00:46-00:55 UTC)`
onward, plus the full "Owner decisions pending", promotion-history,
"Measured", and "Rules" sections (never part of any rotation).

## Verification

- Extracted the exact line range (`sed -n '1770,2369p' AGENTS.md`) and
  confirmed the boundary lines by hand (blank line immediately before/after
  the slice, matching the established newest-first entry-boundary pattern
  used by every prior rotation).
- Appended the extracted slice to the new archive file (after a header
  matching the convention of the seven prior `AGENTS_ARCHIVE_*.md` files)
  and diffed the archive file's tail against the original extraction —
  byte-for-byte identical.
- Independently re-verified in Python: read `git show HEAD:AGENTS.md` (the
  pre-rotation committed version) and asserted the archived body is a
  verbatim substring of it. Confirmed.
- Byte arithmetic checked out: 257,797 (original) − 41,906 (archived body)
  + the new pointer entry ≈ 217,188 (new file size, confirmed by `wc -c`).
- `git diff --stat` against `live_state.json`, `evotrader.manifest`,
  `core/`, `agents/`, `loop/`, `constitution/`, `evotrader_bundle.py` —
  empty. Only `AGENTS.md` and the new archive file changed.
- `python3 -m pytest -q` — 426/426 passed (163.54s), matching baseline;
  text-only change, no regression expected or found.

## Outcome

`AGENTS.md` is now 217,188 bytes, well clear of the 256KB threshold.
No code, genome, or `live_state.json` changed. Genome still v3 (1d) live,
untouched.
