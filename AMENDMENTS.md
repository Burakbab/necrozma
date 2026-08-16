# Constitution amendment log

The constitution is locked against the Researcher, not against the owner. Every
change to it is recorded here so that "we loosened a gate" can never happen
quietly.

This file is **append-only in spirit**: rows are added, never edited or removed.
If you are a scheduled run and you amend the constitution, you add a row here in
the same commit — no exceptions.

| date | change | why |
|---|---|---|
| 2026-08-15 | Circuit breaker became a 20-bar cooldown + forced flatten, instead of latching permanently | The latching version turned 62% of a backtest into a flat line, so fitness was measuring how fast the system died rather than how well it traded. |
| 2026-08-15 | Multiple-testing margin: linear `0.02k` → `σ·sqrt(2 ln k)` with σ=0.08 | The linear form put the bar at 0.46 for a 24-candidate generation, which is arithmetically unreachable on a Sortino-scaled metric — a mis-specification, not a safety property. sqrt-log is the standard correction for the expected maximum of k noisy estimates. The cross-fold consistency penalty and sealed holdout were left untouched. |
| 2026-08-15 | Added `ranking_fitness()` with a finite floor | `fitness()` returns −∞ on a hard gate failure, which is the right verdict but leaves search with no gradient when every candidate fails. Ranking uses a floor; **acceptance still uses the real `fitness()`**, so a floored score can never buy a promotion. |
| 2026-08-15 | `accepts()` now applies the multiple-testing margin to the **selection metric** (fold-aggregate fitness), and separately requires no regression on merged fitness | The margin was landing on the merged fold stats, which rank nothing, while the fold-aggregate that actually selects the winner had no correction at all — backwards on both counts. Selection bias enters wherever you mine for a maximum, so that is where the correction belongs. A new gate was added at the same time (merged fitness may not regress), so this is stricter in one direction and correctly targeted in the other. |
| 2026-08-16 | The sealed-holdout gate now requires the same multiple-testing margin as the selection metric, applied to a **cumulative** draw count that is never reset by a promotion (`holdout_accepts()`) | The holdout gate was a bare `challenger >= champion` while the fold-aggregate got the full `sigma*sqrt(2 ln k)` correction. So the metric being mined was protected and the metric meant to *catch* mining was not: a noise-equal challenger passed the final honest test about half the time. Worse, the holdout is the newest 15% of a history that grows one bar a day, so it is substantially the same bars on every run, and the per-champion counter reset to one after each promotion — the exact pattern by which a validation set is slowly mined while appearing to be passed cleanly. The margin is explicitly a floor, not a calibration: a single holdout window is noisier than a fold-aggregate, and candidates arrive pre-selected by folds that correlate with it, so the honest bar is higher still. Sanity check on the only promotion this system has made: v1->v2 improved holdout fitness by 0.181 against a 14-draw margin of 0.184, so under this rule it would not have been promoted. |

A note on the second row, because it is the dangerous kind of change: lowering a
bar because your system can't clear it is exactly the failure this design exists
to prevent. The defence is that the replacement is the textbook correction rather
than a tuned-down number, the two independent gates were not touched, and the
change is written down here where it can be argued with.
