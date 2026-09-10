# 3-hourly check, 2026-09-10 ~18:47-19:00 UTC — archived item 2's resolved history

## Context

Repo pull hit the shallow-clone/force-push detached-HEAD situation again;
resolved with `git checkout main && git reset --hard origin/main` after
confirming detached HEAD already matched `origin/main`'s tip (nothing local
lost). `pip3 install -r requirements.txt -q` needed one retry (a
`files.pythonhosted.org` read timeout on the first attempt, clean on retry).

Attempting to `Read` `AGENTS.md` in full failed outright:

```
File content (257.9KB) exceeds maximum allowed size (256KB).
```

Checked the daily-trading state first per protocol: `live_state.json`'s
`updated` was `2026-09-10T16:17:08+00:00` (tick 27, already handled at 00:20
UTC, several evolve batches run since) — no new bar to process, no `tick`
run this cycle. `review-hard-calls` confirmed 0 pending.

## What was done

`AGENTS.md`'s own 2026-09-04 archival entry predicted this: "if this file
keeps growing at a similar rate, a future session should archive again." It
did — 264KB now vs. 242KB then — but not for the reason that entry expected
(the chronological "Current state" log growing ~15-20KB/day). Measuring by
byte range instead of guessing: lines 387-1851 (the actual reverse-
chronological "Current state" log since the last rotation) were only ~102KB.
The real growth was inside the static Next-steps roadmap, specifically item
2's inline "Pointer" sub-history — 1126 lines / ~76KB of dated shadow-4h-x6
evolution evidence-gathering entries, none of which had ever rotated because
the file's own rule says the Next-steps section is "never part of either
rotation." That rule stopped fitting once item 2 was actually decided by the
owner on 2026-09-08 (parked, redirect effort — see "Owner decisions
pending") — the detailed pointer trail was closed research sitting inline in
an active-roadmap section.

Moved that 1126-line body verbatim (same text, same order, nothing reworded
or dropped) into new `AGENTS_ARCHIVE_item2_4h-bar-shadow-evolution.md`, with
a short header explaining what it is and why it's there. Replaced it in
`AGENTS.md` with a ~15-line "RESOLVED" summary that states the bottom line
(the `consv1 + trailing_stop + ramp` stack's one real fold-clear is
boundary-fragile and traceable to a deterministic Researcher candidate, not
independent search evidence) and points to both the archive and "Owner
decisions pending" for the decision itself.

Checked whether any other Next-steps item had regrown similarly before
stopping: item 7 (unflatten `evotrader_bundle.py`) is ~14KB of history,
item 9 (background-runner story) is ~5KB — neither close to item 2's former
76KB, so this was the one clear outlier, not evidence the whole section
needs the same treatment yet.

## Verification

- `AGENTS.md`: 264,093 bytes → 189,121 bytes (well under the 256KB limit,
  with room to grow for a while at the ~15-20KB/day chronological-log rate).
- `git status`/`git diff --stat`: only `AGENTS.md` modified plus the new
  archive file — no code, no protected file, `live_state.json` untouched.
- `python3 -m pytest -q`: 390/390 (baseline — no code changed this session).
- `python3 evotrader_bundle.py summary`: constitution verified
  `726dfa4bac85891a` (unchanged), genome version 3 (unchanged).
- Re-read the spliced region of `AGENTS.md` around item 2/item 3 to confirm
  the markdown structure is intact (numbered list still reads 1, 2, 3, ...
  correctly, no stray fragments).

## Next steps (unchanged by this session)

- Item 4 (LLM-backed consults): still blocked on a real hard call ever
  flagging live (`review-hard-calls` reports 0 pending, 1 reviewed so far).
- Item 6 (equities/FX): still needs a human to pick a data source — not this
  session's call.
- No other unstarted/unblocked roadmap item found this cycle; the standing
  `evolve` batch against live v3 remains the default filler when nothing else
  is actionable, same as the last several dozen 3-hourly sessions.
