# Native Scotch 100:1 tree rejected; weight-only branch closed

Job **2294670 completed 0:0** on iris001 in **280 seconds**, 56 CPUs, zero GPUs. Reviewed terminal observation: **3 November 2026, 01:44:26 Vietnam**. This was decomposition and graph screening; no solver benchmark, initialization or READY tree was produced.

| Graph quantity | Default Scotch | Synthetic 100:1 tree | Change |
|---|---:|---:|---:|
| Logical cross-package faces | 86,913 | 82,504 | **−5.07289%** |
| All processor interfaces | 1,035,208 | 1,063,767 | +2.75877% |
| Worst-rank interface faces | 68,534 | 74,424 | +8.59427% |
| Maximum neighbor patches | 20 | 24 | **+4; fails maximum +2** |

Four of five predeclared graph gates pass, including the targeted cross-group reduction. The fanout gate fails, so the frozen job correctly stopped before mandatory initialization. The stronger weight did change the partition and reduced the target proxy, unlike the prior 10:1 result. This is useful mechanistic evidence, **not a solver speedup**. More neighbor patches can add communication overhead, but no message costs, traffic or slowdown were measured here. The triage gate is a research screening rule, not a contest correctness rule. Preserve its decision and do not relax it after seeing this result. Further weight-only tuning for this topology is closed.

All 168 retained artifacts pass transfer hashes. Offline replay reproduces both 56-rank reciprocal boundary graphs, native face totals, 65,334,765 cells, all 56 accepted control boundary hashes, exact permitted system transforms and the rejection. Eight canonical mesh members and 336 restored field-presence checks passed on compute; binary processor fields/mesh were not retained, so full offline field-byte recovery is not claimed. Native OpenFOAM v2512/double precision and zero status gates pass. No renumberMesh, potentialFoam or applyBoundaryLayer logs or READY exist.

Collected hardware/resource evidence is limited to lscpu, GNU time stage resources and scheduler accounting (TotalCPU 04:35.691; MaxRSS field empty). This CPU time is not utilization for a solver; no solver ran. Hardware bandwidth, cycles, actual library architecture labeling and runtime communication costs were not collected. Synthetic costs and rank//28 face counts remain proxies.

Allocated cost: **56 × 280 / 3600 = 4.355556 CPU-hours**, conservatively 5. Retired its 28-hour maximum once under the budget lock. Planning ledger **949 consumed + 0 reserved**, existing internal stage 1,009. No billed SU, NSCC or AI transfer.

## Corrected status-query interpretation

The first two owner-requested status attempts reached Iris but timed out waiting for a JSON frame. A corrected read-only query exposed `squeue -j 2294670` returning 1 with `Invalid job id specified`, while sacct retained COMPLETED 0:0 and the native terminal files existed. The earlier query used check_output, so this exception prevented JSON emission. Thus these timeouts are not evidence of VPN, Iris authentication or scheduler outage. Retain command return codes and stderr; use accounting for completed jobs removed from the live queue. No job was resubmitted or cancelled.

## Next distinct hypothesis

Compare the already initialized hierarchical `(7 4 2), order xyz` tree directly with accepted default Scotch, common native runtime and unchanged numerical work. Prior sub-22-second xyz observations compared other candidates or were order-confounded, not a matched win against Scotch. A bounded 20-step four-arm ABBA screen fits the current stage, but 19 intervals are far below a historical xyz recommendation of 361; it cannot certify a final speedup or support promotion. Prepare it as a large-effect directional screen with all tails and native checks, not a substitute for a qualified full evaluation. No new submission is claimed by this result.
