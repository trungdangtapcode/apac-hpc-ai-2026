# Graph32 collective screen 222023

## Question, submission and checks

The one-collective-per-graph screen included too much host launch cadence to support an isolated timing claim. This new frozen pilot captures 32 collectives per graph and times 10 replays. One 8-H100/10-minute allocation was submitted as 222023.pbs111, maximum 170.667 additional SU. With first-pilot billing still unpublished, total maximum reserve remained 341.333 SU and internal headroom 16643.664 SU at submission. Both source and actual graph operations/units are retained.

All eight ranks pass local payload, completeness, numerical/input-integrity and trace checks: 288 points and 24 nonempty traces. The full model is never loaded. Every row below is worst-rank median **microseconds per collective**, computed from graph time divided by 32. These values cannot be directly compared with the first screen's single-call graph times as if its host gaps had disappeared causally from a model.

| Tokens | Order-reversed round | AUTO (us/collective) | One-shot | Two-shot |
|---|---:|---:|---:|---:|
| 32 | 0 | 7.040 | 12.025 | 6.969 |
| 32 | 1 | 7.702 | 11.239 | 7.393 |
| 48 | 0 | 8.168 | 14.155 | 9.199 |
| 48 | 1 | 7.842 | 13.870 | 7.915 |
| 54 | 0 | 9.091 | 15.561 | 9.424 |
| 54 | 1 | 8.838 | 15.408 | 8.809 |
| 64 | 0 | 8.717 | 17.959 | 9.136 |
| 64 | 1 | 9.511 | 17.258 | 8.896 |

## Assessment and next decision

Forced one-shot is slower in both rounds at every 32–64 shape. At 54 it loses 71.16%/74.34% versus AUTO; at 64 it loses 106.03%/81.45%. Same-algorithm controls retain some variation, so do not claim a precise universal percentage. The broad relevant-shape disadvantage is enough to reject this proposed model patch. Keep AUTO and close forced-one-shot tuning for this tested setting. No full 235B re-deployment is funded on this branch.

Next distinct cheap hypothesis: PDL on/off while retaining AUTO strategy. The exact serving source enables PDL, and the native API supports disabling it. Screen the flag in the same graph32 microbenchmark before considering a source-level model candidate/control. This neither reopens the losing strategy nor claims a model speedup. Full official accuracy remains unverified.

Definite scheduler receipts, raw per-rank samples, shaped reference checks, complete traces and source hashes are retained. Reservations release only after terminal charges reconcile with published Used. No slides, authentication, scheduler automation or background Codex changes.
