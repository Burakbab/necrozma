# Holdout-noise: third champion checked (v1)

3-hourly self-improvement check. `git status` clean at start, local `main`
had gone detached/stale (leftover pre-container-restart ref pointing at old
Aug 15-16 history two commits behind `origin/main`'s 50 newer commits) —
reset to `origin/main` per AGENTS.md's "origin/main is authoritative" rule,
no force-push, no local work lost (the two stale local-only commits were
already-superseded initial-import commits, not unpushed work). Today's
2026-08-20 bar confirmed already processed by the 00:20 UTC daily run
(`live_state.json updated` = `2026-08-20T00:21:36+00:00`, latest run note
`runs/2026-08-20-0020-daily-trading.md`) before this check started — no
`tick` run this session, no double-trade risk.

## What this run did

The 06:54 UTC run today shipped `holdout-noise` and measured champion v3's
sealed-holdout bootstrap sigma at ~24x `constitution.MULTIPLE_TESTING_SIGMA`,
then checked it against v2 (14.3x) via `--also-version 2` to rule out a
v3-specific artifact — but flagged `--also-version 1` as a cheap unrun
follow-up for a third data point. Ran it:

```
python3 evotrader_bundle.py holdout-noise --also-version 1
```

Result (n_boot=1000, block_size=10, seed=0):

| champion | real holdout fitness | boot_fitness_std | ratio vs 0.08 |
|---|---|---|---|
| v3 (live) | -0.965 | 1.906 | **23.83x** |
| v1 (reconstructed) | -1.909 | 1.512 | **18.90x** |
| v2 (recorded earlier) | — | — | **14.3x** |

All three real champions this account has ever had now show
`boot_fitness_std` in the 14-24x range against the constant
`required_margin()` assumes (1x) — none anywhere near 1x, and the range
across genomes (14.3-23.83x) is itself narrower than the gap from any of
them to the assumed constant. This closes the "is this v3-specific" question
as firmly as the fold-scheme/correlation-universe cross-champion checks
elsewhere in this file closed theirs: n=3, all consistent, no fourth real
champion exists to check until a new promotion happens.

## Verified safe

- `live_state.json` md5 identical before/after: `cca58deb976cef403c5010f2e2b9528b`
- `evotrader.manifest` md5 identical: `6a4434574ff424f74ff300ebdb50d194`
- `constitution verified dfae6a697f51fb49` unchanged
- `git status --short` empty (no code changed — existing CLI flag, no new code)
- `py_compile evotrader_bundle.py` clean
- purely read-only: one real backtest replay per genome over the sealed
  holdout window plus pure-numpy bootstrap resampling, no `evolve`, no
  `tick`, no state writes

## Next

The recalibration decision itself (bump `MULTIPLE_TESTING_SIGMA`, or add a
separate holdout-specific sigma constant) is still a constitution change —
checksummed, needs its own `AMENDMENTS.md` row — and per the 06:54 run's
note, reads best combined with the fold-scheme outlier-fold finding as one
regime-stratified/rolling fold-and-holdout redesign, not a number to bump in
isolation. No further cheap data points remain on "is the ~20x order of
magnitude real" — the honest next steps from here are either that
constitution-level redesign, or a much higher `--n-boot` convergence check
on one champion (marginal value, not attempted this run).
