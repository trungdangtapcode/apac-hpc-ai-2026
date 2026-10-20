# Native PDL on/off screen 222026

## Hypothesis and bounded submission

The serving source enables PDL for MNNVL fusion. This screen changes only that native launch flag, retaining AUTO strategy, 32 collectives per graph, BF16/TP8/hidden 4096, all numerical/input-integrity gates, two order-reversed rounds and rank-complete timing. One 8-H100/10-minute allocation, maximum 170.667 SU. Submission followed ledger reconciliation; maximum outstanding reservations retained terminal pilots whose charges were not yet published. No model or custom model patch is loaded.

All eight ranks pass the sealed-payload/completeness/local-numerical/trace checks: 192 points and 16 nonempty traces. These are worst-rank median **microseconds per collective**, not model tokens/s or an elapsed model critical-path partition.

| Tokens | Round | PDL on (us) | PDL off (us) | Off versus on |
|---|---:|---:|---:|---:|
| 32 | 0 | 6.986 | 9.749 | +39.54% |
| 32 | 1 | 7.337 | 8.484 | +15.63% |
| 48 | 0 | 7.827 | 9.501 | +21.38% |
| 48 | 1 | 8.078 | 10.367 | +28.34% |
| 54 | 0 | 7.983 | 9.811 | +22.90% |
| 54 | 1 | 8.535 | 10.100 | +18.35% |
| 64 | 0 | 8.825 | 10.709 | +21.35% |
| 64 | 1 | 9.031 | 10.670 | +18.15% |

## Assessment and next decision

PDL off is slower in both rounds at every measured shape. At 54 tokens the observed disadvantage is 22.90%/18.35%; at 64 it is 21.35%/18.15%. Timing/rank/order variation remains, and back-to-back collectives do not reproduce transformer overlap. Nevertheless, this screen provides no positive signal for a model-level PDL-off patch. Keep PDL enabled and close that tested option. Do not turn these percentages into an estimated model speedup.

The next distinct full-model experiment compares native decode attention backends after the MoE/load changes, with a fresh same-load control; it retains AUTO and PDL and does not combine unproved settings. See ../research-followup-20261020-decode-attention/PLAN.md. The one-shot and PDL screens avoided an unsupported full-model source patch; failures and losing measurements remain preserved.

The complete source, API hashes, submitted checksums, actual qsub receipt, per-rank samples and raw traces are retained. Reservations are planning bounds and release only against published ledger charges. No official accuracy, global optimum, slide, authentication or AI scheduling claim.
