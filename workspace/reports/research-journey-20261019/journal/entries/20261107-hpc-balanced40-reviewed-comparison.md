# Full balanced 40 comparison: slower pooled, unstable repeated timings

7 November 2026, Vietnam (UTC+7). Iris job **2295087 COMPLETED 0:0** in 5,430 seconds /56 allocated CPUs /iris001. Root and independent terminal replay pass all 452 transferred hashes, 101 frozen payload hashes, 216 actual rank records, source/payload/runtime before/after, exact field seals, four native 40-step/39-interval/40-force outputs and same-partition force repeats. Final comparison.json is the completed result; partial-results.json is intentionally the earlier progress snapshot, not the final completion authority. This is a research microbenchmark, not an official contest score.

| Configuration | First arm (s/step) | Second arm (s/step) | Pooled mean (s/step) |
|---|---:|---:|---:|
| Default 48 control | 27.549682806 | 31.794129632 | 29.671906219 |
| Balanced 40 socket/core | 40.020672136 | 22.901997128 | 31.461334632 |

Balanced 40 is **6.030716% slower** pooled. Its candidate repeats change **−42.774581%**, while control repeats drift +15.406518%. Both candidate rank-to-CPU maps are exactly identical and show 20/20 before MPI_Init. Same-partition force coefficients have zero maximum difference. Thus the observed timing change cannot be explained merely by a different recorded launcher map or changed native iteration work. It does not identify the cause: pages, solver-helper affinity and per-process bandwidth were not measured. Whole-node telemetry exists (230/329/193/263 samples); PSI unavailable. Sampled frequency summaries and available-memory aggregates do not establish task-specific clocks or a NUMA bottleneck.

The earlier question was whether correcting default 40's 28/12 imbalance could beat default 48 after default 40's censored ~50s/step result. Here partition count and placement differ together; this is a complete whole-configuration comparison, not a causal proof of either factor. The 22.901997 single arm is not a stable best-known configuration and does not beat the separate historical ~22-second observations. Close unchanged balanced 40 as a promotion candidate. Preserve this negative result and its full raw artifacts.

Next distinct measurement: keep the same initialized N48 source, all numerical work, uncollated I/O and horizon fixed; compare default 48 mapping against socket/core 24/24. Earlier hybrid 48 changed mapping plus collated I/O, so that did not isolate mapping. Use opposite placement order BAAB and inspect all repeats. The current result supports asking that question, not claiming that the next candidate will win. Optional hardware explanations must not replace a measured matched comparison.

Actual allocated cost **84.466667 CPU-hours**, conservatively 85. Its 168 maximum was retired exactly once: **1,767 consumed /zero reserved /internal stage 1,850**, site SU unknown. One-own Iris cap is free after the terminal check. No NSCC/AI changes. Owner's latest no-status-only-commit rule is respected: this is the first substantive reviewed completed result since that rule. One result-backed capture may preserve this configuration, its failed parent evidence, final review and connected reasoning. Future status/admission work remains local until its own reviewed result or explicit commit instruction. No background schedules or MFA action.

[Complete raw review](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-balanced 40-vs48-20261107/completed-2295087/RESULTS.md). [Root replay](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-balanced 40-vs48-20261107/completed-2295087/ROOT_REPLAY.json).
