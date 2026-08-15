# Run notes

One file per scheduled run: `YYYY-MM-DD-HHMM-<slug>.md`, UTC.

**Always create a NEW file. Never append to a shared one** — several routines run
concurrently and appending clobbers whichever run committed last.

Keep these **technical**: NAV, the decision and its reasoning, what changed, what
was tried and rejected, what the next run should pick up. This directory is
public — no personal content, no email addresses, no private correspondence.

The authoritative ledger is `live_state.json`, not these notes. These exist so a
future run can read *why* something happened, which the JSON doesn't record.
