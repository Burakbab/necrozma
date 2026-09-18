# 3-hourly check: AGENTS.md rotation (2026-09-18 ~21:47-22:00 UTC)

No new daily bar to process this cycle — `live_state.json`'s `updated`
timestamp (`2026-09-18T19:09:44+00:00`) and `runs/2026-09-18-1912-evolve-batch-v3.md`
confirmed tick 35 was already handled at 00:20 UTC and the prior 3-hourly
slot's evolve batch had already run. No trading performed.

## What this cycle did instead

`AGENTS.md` had regrown to 253,326 bytes, within ~2.7KB of the 256KB
single-read limit that scheduled sessions' `Read` tool enforces, and
another evolve-batch entry (typically 2.5-3.5KB) would have pushed it
over. Rather than add one more entry and let a future session hit a
truncated read, used this slot to rotate the log now, following the exact
precedent of the 2026-09-04/09-10/09-15/09-16 rotations already documented
in the file:

- Moved the 2026-09-11 00:48 UTC through 2026-09-12 22:11 UTC slice of the
  "Current state" chronological log (lines 1906-2427, two full days of
  entries) verbatim, byte-for-byte, into a new file
  `AGENTS_ARCHIVE_2026-09-11_to_2026-09-12.md`, with a header matching the
  format of the existing `AGENTS_ARCHIVE_*.md` files.
- Verified the archived content is byte-identical to what was cut (`diff`
  against a pre-edit backup, clean).
- Verified the static sections below the chronological log ("Owner
  decisions pending" onward through "### The first promotion", "Measured",
  "Rules") are byte-identical before and after the edit (`diff`, clean) —
  the cut boundary was placed precisely so none of that material moved.
- Replaced the cut block in `AGENTS.md` with a new tombstone entry (same
  convention as the existing 2026-09-15/2026-09-16 tombstones), placed at
  the oldest position in the log, pointing to the new archive file and the
  existing archive chain.
- `AGENTS.md` is now 218,000 bytes (was 253,326), comfortable margin under
  the 256KB threshold again.

## Verification before commit

- `python3 -m pytest -q`: 422/422 passed (docs-only change, no regression
  expected or found).
- `git diff --stat` confirmed only `AGENTS.md` and the new archive file
  changed — `live_state.json`, `evotrader_bundle.py`, and
  `evotrader.manifest` untouched.
- No genome, broker, journal, or trading state affected. Genome still v3
  (1d) live, untouched.

## Why this instead of another evolve batch

Every recent 3-hourly slot for the past several days has used its
"nothing else queued" time on one more 15-generation `evolve` batch
against the live v3 champion, with no promotion. That's still the right
default when nothing else is actionable, but the AGENTS.md rotation was
concrete, overdue infrastructure maintenance flagged by the file's own
"if this file keeps growing at a similar rate, a future session should
archive again" note (written at the 2026-09-15 rotation) — doing it now
avoids a future session hitting the read-size limit mid-cycle.
