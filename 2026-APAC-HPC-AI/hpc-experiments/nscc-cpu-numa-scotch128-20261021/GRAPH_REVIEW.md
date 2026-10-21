# Actual partition graphs validate the NUMA screen

Read-only metadata collection retained 256 small ASCII processor-boundary files from the accepted initialized hierarchical and default Scotch trees. No field arrays or binary mesh were copied. Local bounded analysis checked every reciprocal neighbor edge, retained SHA256 for each boundary file and reproduced both native decomposePar totals exactly. See boundary-metadata.tar.gz, collection provenance and graph-parser-validation.json. This validates the real parser before a paid candidate prep allocation.

| Unique interface faces | Hierarchical | Default Scotch |
|---|---:|---:|
| All neighbor edges | 2,109,346 | 1,549,377 |
| Across logical rank groups of 16 | 1,203,493 | 371,658 |
| Within a group | 905,853 | 1,177,719 |
| Maximum processor faces | 131,252 | 42,141 |
| Maximum processor neighbors | 16 | 35 |

The separate current allocation's atomic diagnostic rank map matches these logical groups to eight NUMA CPU sets. These are interface face counts, not actual communication volume, wait time, memory traffic or page locality. A later allocation must recheck placement. Default Scotch already reduces cross-group faces; this may leave less benefit for an explicit tree. That is a reason to use an inexpensive graph screen before spending on another solver.

Decision: retain the native (8 16) tree hypothesis with synthetic weights 10:1, compare all graph quantities and cell imbalance, and only promote a non-dominated result. The active H→S pair is still running; its final result and locked budget reconciliation gate any new submission. No allocation or budget increase is performed by this analysis. No numerical score is claimed.
