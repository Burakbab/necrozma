# 3-hourly check, 2026-08-29 ~03:56 UTC — `--champion-only` span sweep, and a trend the earlier framing missed

## What this is

The 00:56 UTC entry today shipped `history-perturb --champion-only` and ran it
once (10 as-of points, 21 days apart, ~189 days of span), flagging as an
explicit next step: "run with a longer span / different `--as-of-step-days`
to see if the spread grows, shrinks, or plateaus with more history." This
session did that — no code changes, just more runs of the existing tool plus
analysis of the combined output.

## What was run

Three `--champion-only` sweeps against live champion v3, same genome, same
tool, increasing span:

| N  | step (days) | span (days) | finite/N | range              | std   | std / HOLDOUT_SIGMA (2.0) |
|----|-------------|-------------|----------|--------------------|-------|---------------------------|
| 10 | 21          | 189         | 7/10     | [-0.824, 1.167]    | 0.613 | 0.31x (00:56 UTC entry)   |
| 20 | 14          | 266         | 16/20    | [-0.408, 2.228]    | 0.830 | 0.41x                     |
| 30 | 14          | 406         | 24/30    | [-0.408, 2.352]    | 0.832 | 0.42x                     |

`live_state.json`/`evotrader.manifest` md5 unchanged across all three runs
(`bf360fc7f86f6bae2bc46bb6f6dc6026` / `0bf3a7d9411ee692d0a9f152a7533803`,
matching the 00:56 UTC entry) — read-only, as documented for this command.

**Finding 1: the std genuinely plateaus, and the 189-day run underestimated it.**
0.613 -> 0.830 -> 0.832 going from 189 to 266 to 406 days of span. The jump
from 10 to 20 points is real (the 189-day window was simply too short a look
to have sampled the full spread), but 20 -> 30 points (266 -> 406 days) moved
the std by <0.3%, i.e. essentially nothing. Best current estimate of the
as-of-drift std is **~0.83**, not the 00:56 UTC entry's 0.613 — still
comfortably under `HOLDOUT_SIGMA` (0.42x) but a real ~35% upward revision,
worth carrying forward if anyone acts on the still-open combine-with-
`holdout-noise` question.

**Finding 2, more important: this isn't symmetric noise around a fixed mean —
it's a trend with calendar recency.** Pearson correlation between as-of index
(0 = today, higher = further back) and finite fitness on the 30-point run:
**r = 0.686**. Splitting at the midpoint:

- idx 0-14 (as-of dates 2026-02-14 through today, holdout windows ending
  recently): n=11 finite, mean **0.464**, std 0.613
- idx 15-29 (as-of dates 2025-07-19 through 2026-01-31, older holdout
  windows): n=13 finite, mean **1.829**, std 0.326

The older half isn't just less noisy, it's systematically *better* by more
than a full point of fitness, and its own internal spread (0.326) is much
tighter than the recent half's (0.613) — most of the total spread is coming
from the boundary between two different regimes, not from uniform noise
across the whole range.

**What this does and doesn't establish.** Checked one candidate mechanism —
whether the elevated older-window scores are explained by the sealed holdout
slice pulling in the known fold-2 melt-up episode (2024-03-31 to 2024-08-05,
flagged by `drawdown`/`fold-dd-blindspot` as a permanent +200%+ outlier) —
and it does **not** hold up on inspection: the elevation already shows up at
as-of index 14 (holdout window 2024-11-06 to 2026-02-14), which starts three
months *after* that episode's own recovery date (2024-11-10 per the
`fold-dd-blindspot` entry), so the melt-up itself falls outside that
window entirely. Ruled out, not confirmed — the actual driver of the
recent/older split is still unidentified. Not chased further this session;
flagging the ruled-out mechanism so the next person doesn't re-check it.

## Why this matters for the open `HOLDOUT_SIGMA` question

The 00:56 UTC entry's still-open question was whether to combine this
noise source with `holdout-noise`'s block-bootstrap resampling std (~2.04)
"in quadrature" on the assumption both are independent, mean-zero noise
around the champion's true score. Finding 2 undercuts that framing directly:
if roughly half of this spread is a level shift between two calendar regimes
rather than draws from one noise distribution, then (a) a single empirical
std number here is summarizing a mixture, not a clean noise estimate, and
(b) "combine in quadrature" is the wrong operation regardless of the exact
number — that formula assumes independent zero-mean perturbations, which a
trend is not. This doesn't change the actual `HOLDOUT_SIGMA` value (still not
touched, still a constitution-amendment-level decision, still out of scope
for this session) but it does mean whoever next picks up that question should
treat the 0.83 std figure as a description of this specific mixed sample, not
as an input ready to plug into a quadrature-sum formula.

## Next steps

- The recent/older split's actual driver is still open — ruled out the fold-2
  melt-up specifically, nothing else checked. A next session could look at
  which regime each half's holdout window actually sits in (reuse `regime
  --interval 1d` scoped to these specific windows, or just eyeball the raw
  bar count / return columns already printed) before spending more effort on
  the `HOLDOUT_SIGMA` combination question — a trend needs a different
  statistical treatment than noise, and knowing *what* is driving it would
  clarify which treatment is right.
- `--also-version N` against v1/v2 (not run this session) would show whether
  this recent/older split is champion-specific or a property of the sealed
  holdout's calendar structure itself, the same way the correlation-penalty
  investigation eventually checked "genuinely different genome" before
  drawing a general conclusion.
