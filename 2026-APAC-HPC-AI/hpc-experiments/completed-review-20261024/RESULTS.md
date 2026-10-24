# Completed four-node and MPI preflight review

## Question and prior evidence

This review checks whether the default-Scotch four-node, 512-rank, 150-step replication is internally reproducible and whether the two dependent MPI reorder probes passed. The prior native candidate, job 25921488, averaged **3.677906731 s/step** over 149 samples, with median **3.298741570 s**, p95 **3.795740112 s**, and a **35.883552358 s** maximum at Time 119. Its source/submission and terminal PBS evidence had limitations documented in the 23 October review. The replication (25940700) was designed as a separate allocation, not a paired timing test.

## Evidence and replay

The script [review.py](review.py) verifies all **126** files listed by the frozen collection manifest, imports and reruns the existing native solver validator against the collected solver log, solverInfo, wall-clock function output, and force coefficients, then checks the replay against both saved validator outputs. It also compares the complete pre-solver and post-solver zero-time field seals, source-manifest checks, initialization stage logs, the four-rank probe validator, and the 512-rank failure records. Run it from any directory with `python3 review.py`.

The 25940700 replay passes: 150 ordered solver steps, 149 positive timed samples for Times 2–150, fixed iteration counts, four hosts with 128 ranks each, 150 finite force rows, and exact native-log/time-function agreement. The pre-solver and post-solver seals match across **3,072 files** and 512 processor directories. The payload source manifest is unchanged before and after. All recorded shell-stage return codes are zero; decomposition and the three initialization stage logs have `End` markers and no fatal markers. The startup-only rank probe records 512 ranks on four hosts, 128 per host, and validates 512 unique physical cores. This does not establish solver-time affinity or memory page placement.

The per-command `/usr/bin/time` records report 419.14 seconds wall for serial `decomposePar` and 549.16 seconds wall for `simpleFoam`, within a 1,133.66-second wrapper interval. The decomposition record reports 312.96 user and 69.79 system seconds. The MPI launcher resource records are not complete per-rank or allocation-wide CPU telemetry; these totals do not identify a bottleneck or explain solver timing.

There are nonfatal warnings in the run: decomposition reports reading `constant/README.md` as a dictionary, and `renumberMesh`, `potentialFoam`, and `applyBoundaryLayer` report the `FI_VERBS_PREFER_XRC` / `FI_OFI_RXM_USE_SRX=0` conflict and say XRC is disabled. The same SRX-off setting was intentional for comparison with the retained shared runs. These warnings are preserved as environment evidence; the logs do not show them as fatal stage failures.

The 4-rank preflight (25943865) produced a successful on-allocation validator record with the exact order `[0, 2, 1, 3]`; candidate MPI world ranks occupy the expected identity slots on four distinct physical cores on one host. The offline validator CLI also passes against its collected probe output, but it reads this machine's `/sys`; the captured compute-node `mapping-validation.json` is the authoritative physical placement evidence. This validates the small method-3 reorder path on that allocation only.

## Native timing comparison

| Native run | Mean (s/step) | Median (s) | p95 (s) | Maximum (s, time) | Recommended samples | Short-sample warning |
|---|---:|---:|---:|---:|---:|---|
| 25921488, prior Scotch candidate | 3.677906731 | 3.298741570 | 3.795740112 | 35.883552358 (119) | 5,491 | Yes |
| 25940700, independent Scotch repeat | 3.364622070 | 3.282042638 | 3.936922984 | 5.900973952 (101) | 101 | No |

The repeat mean is **0.313284661 s/step (8.52%) lower** and the median is **0.016698932 s (0.51%) lower**. Its p95 is **0.141182872 s (3.72%) higher**, while its maximum is much lower because the prior run's single 35.88-second step did not recur. The repeat's five slowest samples are Times 101 (5.901 s), 143 (5.519 s), 122 (4.606 s), 141 (4.444 s), and 117 (4.369 s). All samples remain included in the mean; no trimming is applied.

This is evidence that the prior extreme maximum was not repeated in this allocation and that the repeat's central timing was lower, while its 95th-percentile tail was slightly higher. It is not evidence of a code-level speedup or a cause: these are two separate allocations, their timing series are serially correlated, and the native recommended sample counts differ sharply (101 versus 5,491). The native recommendation is a time-series diagnostic, not an independent confidence interval. No hardware bottleneck or scheduler effect can be inferred from these comparisons alone.

## 512-rank placement preflight failure

The 512-rank preflight (25947168) completed payload hashing, nodefile validation, module/compiler/launcher checks, probe compilation and MPICH library gates. It failed during the **identity** MPI probe with return code 255; the candidate MPI launch and mapping validator were never reached. The stderr contains 512 generic messages saying the process could not prove single-CPU package/core/NUMA topology, and stdout contains no completed mapping records. The probe emits that same message for a combined condition: affinity must contain exactly one CPU, and package, core, and NUMA metadata must all be readable. The retained output does not distinguish which component failed on which rank, so the root cause remains unknown. Do not treat this as evidence that the proposed assignment itself is invalid or that a particular NUMA topology was observed.

For the next offline preparation, add categorized per-rank probe diagnostics (affinity mask cardinality and each sysfs read/result separately) and a small non-solver diagnostic that verifies those interfaces on the allocated node before scaling to all ranks. Keep the failure artifacts. Any later mapping attempt must rerender against fresh actual identity slots and separately version the balanced whole-group assignment; the 512-rank probe that failed used the earlier refined assignment.

## Scheduler and cost limits; next decision

The whitelisted terminal PBS records in `collected/collection.json` verify all three jobs finished on CPU project 59000042: 25940700 Exit 0 / 18:57 wall, 25943865 Exit 0 / 7 seconds, and 25947168 Exit 1 / 9 seconds. PBS `stime` strings are site times; UTC phase logs are separately labeled. These are retained scheduler resources and outcomes, not individual posted billing. Wrapper lifecycle is supplementary.

The separate locked [reconciliation](budget-reconciliation.json) verifies rate 1 and retains full-node conservative treatment for the four-core probe: 161.706667 + 0.248889 + 1.28 = 163.235556 SU of terminal allowance, rounded up to 164 SU. Only these three known maxima (373.333333 SU) were retired. All other uncertain reservations and shared maxima remain unchanged, including deliberate possible double counting. Planning commitment is 4,688.2 / 5,000 SU before any new submission; 311.8 SU remains. This is conservative research planning, not a claim about exact charges.

The four-node native replication is a valid repeat observation and can close that repeatability question at its stated limits. The 512-rank topology failure blocks interpretation of a large candidate mapping. Preserve all three outcomes, including the failed preflight; diagnose the combined topology gate before any future candidate qualification. A solver A/B remains a distinct, separately reviewed experiment and cannot be derived from the 4-rank pass or graph face proxies.
