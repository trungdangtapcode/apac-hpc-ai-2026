# Same-source N48 mapping result: a fast arm is not a stable win

7 November 2026, Vietnam (UTC+7). **2295090 COMPLETED 0:0**, 4,525 seconds /56 allocated CPUs /iris001. Root and independent replay pass all 469 transferred hashes, 57 frozen payload hashes, 240 actual rank records across five sets, accepted source/runtime/payload before/after, initial field seals, four native forty-step/39-interval outputs and strict within/across-mapping force checks. Same-source paired force differences are at most 1.63203e-14; within-mode repeats are identical. Final comparison.json is authoritative; partial-results.json is the earlier progress snapshot. This is a bounded microbenchmark, not an official contest score.

| Arm | Configuration | Mean solver time (s/step) |
|---|---|---:|
| B1 | 48 ranks, contiguous 24/24 socket/core | 32.001684128 |
| A1 | Same source, default mapping | 24.663577539 |
| A2 | Same source, default mapping | 24.200998556 |
| B2 | 48 ranks, contiguous 24/24 socket/core | 21.085907685 |

Candidate mean **26.543795906 s/step**, default **24.432288048 s/step**: candidate **8.642285% slower**. The fast 21.085908 arm is a real full 40-step measurement, numerically below the retained historical approximately 22.35-second observation, but it is not a repeatable configuration improvement or a cross-allocation matched gain. Both candidate arms have identical recorded rank-to-CPU maps yet very different time. Preserve both, not only the minimum. Do not promote unchanged contiguous 24/24 mapping.

The task source, decomposition, numerical work, runtime and I/O were common, so this comparison isolates the requested mapping policy at the configuration level. The timing cause remains unobserved: pre-MPI launcher affinity does not prove post-MPI solver-helper affinity or memory residency. Available node-wide frequency/memory counters are not process-attributed; PSI was unavailable. Review includes telemetry coverage and raw logs; no causal bandwidth or clock claim follows.

## Next distinct hypothesis, with an earlier assumption corrected

Actual proof records show candidate rank 0..23 on one NUMA node and 24..47 on the other. I initially considered PPR with fill ranking, but this would reproduce that contiguous map; no such duplicate was submitted. OpenMPI's official 5.0.10 guide separates mapping, ranking and binding and distinguishes fill from span. The new candidate explicitly requests `--map-by ppr:24:package --rank-by span --bind-to core`: consecutive rank IDs should alternate nodes while using the same first 24 cores per NUMA node. This changes rank-to-core association without changing the N48 decomposition, core count or numerical work. It is a hypothesis, not a prediction of a win.

A new actual pre-solver gate must verify 24/24, strict alternation and exact core membership from observed sysfs topology. Root offline tests reject the actual prior contiguous proof records, so the next trial cannot silently repeat the old map. Offline preparation CLI, source/clone/field/inode and native interfaces pass. An initially missing import in the new offline test was corrected before the passing review; no failed test or local fixture is labeled as MPI qualification. This new candidate is not yet a performance result.

Keep the same four forty-step/39-interval BAAB trial against default 48. If this final rank-order factor loses or large repeated-state drift persists, stop blind placement variants and move to separately qualified process-level memory-residency diagnostics before more timed sweeps. Optional diagnostics must not block an independent ready native test.

Actual allocation cost **70.388889 CPU-hours**, conservatively 71; retire 140 maximum once: **1,838 consumed /zero reserved /stage 1,907**. Billed site SU unknown. Next 140 maximum would need only a bounded internal stage 1,978 (+71); that is not an owner allowance or site SU. CPU/AI budgets remain separate. This completed result permits one coherent result-backed capture; next preparation/admission remains local. No background Codex/MFA actions.

Primary reference: [OpenMPI 5.0.10 mapping/ranking guide](https://docs.open-mpi.org/en/v5.0.10/man-openmpi/man1/mpirun.1.html#mapping-ranking-and-binding-oh-my). Actual collected rank records take precedence over assumptions about defaults; the future runtime probe must validate the requested layout before solver work.
