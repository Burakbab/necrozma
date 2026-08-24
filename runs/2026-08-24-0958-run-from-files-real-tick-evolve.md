# Item 7's actual cutover: real (saving) `tick`/`evolve` in run_from_files.py — 2026-08-24 ~09:46 UTC

3-hourly self-improvement check. `git pull` fast-forwarded 18 commits to
`786b30a` (the 09:00 UTC daily discussion). `pip3 install -r requirements.txt`
(bare cloud sandbox). Today's bar (2026-08-23) already processed by the 00:20
UTC daily run — `live_state.json` `updated` timestamp and
`runs/2026-08-24-0020-daily-trading.md` both confirm it — so no `tick` was run
against the real state this session.

## What changed

`run_from_files.py` gains real `tick` and `evolve` commands — the same
bodies as `evotrader_bundle.py`'s own `tick`/`evolve`, transcribed verbatim,
including the genuine `acct.save(state_path)` calls. This is the piece both
the 06:56 UTC `evolve-dry-run` entry and the 09:00 UTC daily discussion
named as the natural next checkpoint for item 7 ("unflatten
`evotrader_bundle.py` into real files"), now that both state-mutating
commands had tested dry-run twins.

The 09:00 UTC daily discussion explicitly checked whether this needed the
owner's attention before proceeding and concluded it didn't: "an
engineering/testing milestone, not a real-money or risk-appetite call — the
existing safety discipline... already covers it." That's the basis for
proceeding without pausing for sign-off this session.

`tick` supports `--force` (unlike `tick-dry-run`, which deliberately omits
it — see that command's own docstring) because this command is meant to be
a genuine drop-in replacement for the bundle's own `tick`, not a narrower
safety-scoped variant. `evolve` keeps the same test-only `--seed N` escape
hatch `evolve-dry-run` already had (the bundle's own `evolve` always passes
`seed=None`).

## Verification

Four new tests in `tests/test_run_from_files_matches_bundle.py`:

- `test_tick_matches_bundle_on_untraded_bar` — the strongest parity check in
  the file: runs the bundle's real `tick` and this file's real `tick`
  against two byte-identical copies of the same synthetic scratch starting
  state (the existing `synthetic_universe` fixture, forced onto the
  non-skip branch), and asserts the resulting state files match once
  wall-clock timestamps are normalized out.
- `test_tick_skips_already_traded_bar_without_saving` — confirms the real
  `tick`'s skip branch never calls `acct.save()`, same invariant
  `tick-dry-run`'s test already covers for the dry-run twin.
- `test_evolve_saves_and_matches_its_own_dry_run_decision` — runs
  `evolve-dry-run` and `evolve` with the same `--seed` against
  byte-identical starting state (the `synthetic_universe_4y` fixture) and
  asserts they reach the same decision (held vs. promoted), the only
  difference being that `evolve` actually persists it. Can't do a direct
  subprocess-vs-bundle comparison here the way `tick` does, because the
  bundle's own `evolve` has no `--seed` flag.
- `test_evolve_rejects_unsupported_flags_the_same_as_evolve_dry_run` —
  generation-count argv parsing sanity check (2 generations → 2 lineage
  entries appended).

Also had to fix `test_run_from_files_rejects_unsupported_command`, which
previously used `tick` as its example of an unsupported command — no longer
true, switched to `anatomy` (still genuinely unwired).

**A real bug caught in the first draft of `test_tick_matches_bundle_on_untraded_bar`
itself, not in the code under test**: an initial byte-for-byte comparison of
the two resulting state files failed, because `core.live._now()` stamps
`updated`, `genome.created`, and `journal[].ts` with real wall-clock time at
save/construction time — the bundle subprocess and the real-files subprocess
run a few seconds apart, so those fields predictably differ even when every
decision made was identical. Fixed by writing a small `_normalize_timestamps`
helper that recursively blanks any ISO-8601-shaped string before comparing,
rather than weakening the test to skip real content — the normalized
comparison still fails on any genuine decision difference.

Full suite: 231 passed (was 227 before this session; +4 new tests, 0 broken).
`tools/edit_bundle_module.py sync --check`: clean, no `_SRC` module touched
(`run_from_files.py` is plain CLI-script code, same as every prior addition
to this file). `py_compile` clean on both changed files. Manifest verify:
`constitution verified 8b74865634b1db07`, unchanged. Real `live_state.json`
md5 unchanged throughout — confirmed by `git status --short` showing no diff
on that file, and by re-running `run_from_files.py tick-dry-run` against the
real state afterward: still correctly reports today's bar (2026-08-23,
tick 10) already traded. `evotrader_bundle.py summary`/`review-hard-calls`
both still clean (0 hard-call reviews pending).

## What this does NOT do

No scheduled run has been pointed at `run_from_files.py` instead of the
bundle. `evotrader_bundle.py` remains what every scheduled `tick`/`evolve`/
`summary` command actually runs, byte-identical before and after this
session's changes. That stays true until a separate, deliberate decision
says otherwise.

Item 7 is now feature-complete relative to the bundle's own state-mutating
commands: both `tick` and `evolve` exist in both dry-run and real form
against the real files, and both are proven — not just asserted — to behave
identically to the bundle. What remains, if anyone ever wants it, is purely
the scheduling decision itself (switch some/all scheduled commands to
`run_from_files.py`, all at once or incrementally, keep the bundle as a
fallback or retire it) — a migration-policy question, not an engineering
task. Flagging this explicitly in AGENTS.md's "Next steps" so the next
session doesn't default to treating it as unfinished engineering work.

No push notification — infrastructure work verified safe by the test suite
and manual checks above; zero effect on live trading, since the file that
actually executes on a schedule (`evotrader_bundle.py`) is untouched.
