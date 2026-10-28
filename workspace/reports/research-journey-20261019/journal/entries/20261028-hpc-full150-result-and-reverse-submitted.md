# Full-length Iris order result and reversed confirmation

Recorded 28 October 2026, Vietnam time (UTC+7). HPC session only; AI work is unchanged.

## Question and prior evidence

Does hierarchical zyx remain faster than xyz for the complete 150-step workload? Earlier 30-step pairs favored zyx in both serial orders, and its 50-step extension was stable. These screens did not establish full-length or independent-allocation repeatability.

## Measurement and interpretation

Iris job **2294234**, node iris024, completed with exit 0:0 in 7,585 seconds. Both arms used 56 CPU ranks, factors (7 4 2), FP64, native OpenFOAM v2512 and fixed iterations. Execution order was zyx then xyz. Both completed 150 steps with 149 retained timing samples; local replay reproduced every timing and all 150 Cd rows per arm. Frozen payload, source/copy/initialized-field seals and runtime library identities passed. All recorded phase commands returned zero.

| Metric | zyx | xyz |
|---|---:|---:|
| Mean seconds per step | 21.229594 | 26.953799 |
| P95 seconds per step | 21.395847 | 31.569807 |
| Maximum seconds per step | 21.480447 | 32.410898 |
| Final total Cd | 0.282424 | 0.287070 |

The mean timing reduction is **21.2371%** in this one matched Iris allocation. This supports the direction of earlier screens. It is not an NSCC improvement, an organizer reference or a contest score. Final Cd differs by **1.6185% relative to xyz**; preserve this difference instead of claiming equivalent output. Both native structural/output gates pass, but no universal Basic-task numerical tolerance is inferred from the Bonus rule.

## Inspection beyond mean time

Retained and inspected: native step and timer tables, finite force rows, fixed iteration counts, source/copy/field seals, executable and shared-library hashes, command exits, GNU time counters and terminal Slurm accounting. There are 129 retained selected files with verified transfer hashes. zyx solver elapsed 3,223.76 seconds; xyz 4,075.94 seconds. GNU time reports high CPU use for both, but this does not establish a bandwidth or NUMA bottleneck. Whole-node procfs snapshots were collected; solver-specific memory bandwidth, per-rank frequency and per-process NUMA maps were not collected. Step samples are correlated and do not substitute for allocation-level repeats.

The native sample recommendation was zero for zyx and 51 for xyz, each below the 149 retained samples. It is a within-run statistic, not evidence of zero uncertainty.

## Next hypothesis and actual execution

Reverse the full-length serial order in a fresh allocation: **xyz first, then zyx**, with otherwise matched physics and output gates. If the direction persists, ordering alone becomes a weaker explanation; node differences and numerical trajectory differences still require qualification.

Slurm accepted **2294262** at **2026-10-28T15:40:09.431273+07:00**. The 49-file derived kit is frozen and independently reviewed; this is submitted work, not merely a plan. It requests one exclusive Iris node, 56 ranks, zero GPUs and at most three hours. Actual state is dated in the bundle's post-submit status. Parent kit remains unchanged.

## Cost and access decision

Job 2294234 consumed 117.988889 allocated CPU-hours by elapsed-time arithmetic; the local conservative allowance is 118. Retired its original 168 maximum once, leaving total consumption 337 and reserve 0. Under the latest instruction to continue authorized research, the agent documented one bounded new 168-hour maximum. Its internal ceiling rises from 392 to 505, adding 113 after using 55 released headroom. The owner did not specify this numeric ceiling. It is a planning allowance, not billed SU or an unknown site balance. No NSCC/AI credits are transferred.

NSCC CPU SSH reuse immediately reported no live VPN session. No repeated DUO attempt was made; usable Iris research continued. NSCC old jobs remain unknown and the prepared native transfer bundle remains unsubmitted.

## Evidence

- [Full parent review](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-order56-full150-20261027/completed-2294234/RESULTS.md)
- [Actual reverse submission](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-order56-full150-reverse-20261028/STATUS.md)
- [Budget authority](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-order56-full150-reverse-20261028/budget-authorisation.json)

No submission deck or other worker payload was changed. Large processor meshes and binary fields remain on the cluster; selected text evidence and reconstruction provenance are retained locally and captured explicitly into the research archive.
