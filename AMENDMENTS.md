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

A note on the second row, because it is the dangerous kind of change: lowering a
bar because your system can't clear it is exactly the failure this design exists
to prevent. The defence is that the replacement is the textbook correction rather
than a tuned-down number, the two independent gates were not touched, and the
change is written down here where it can be argued with.
