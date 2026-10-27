# Iris full150 pair 2294234: actual fallback measurement admitted

Recorded 2026-10-27T17:33:06.657738+00:00. The owner explicitly directed using Iris instead of waiting for NSCC DUO. The [actual accepted job and live state](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-order56-full150-20261027/STATUS.md) replace preparation-only status for this Iris branch. NSCC native-wave remains unsubmitted.

**Question and hypothesis.** Previous 30-step pairs favored zyx by 26.94% and 21.42%, and a single 50-step extension averaged 21.1120 s/step. Do the same native initialized decompositions preserve that direction through 150 full steps on the same Iris allocation? Those short observations do not predict a full-run gain.

**Exact change and control.** One exclusive 56-CPU node, zyx first and xyz second, each 150 steps/149 timings, factors (7 4 2), native v2512 GCC 11/HPCX 2.50, FP64, no injection. Each case is a new verified copy of its corresponding READY source; all numerical work, function objects, initialization provenance and fixed iterations remain. Only run endTime becomes 150; original startFrom remains and all processor numeric times must be zero.

**Review.** Root ran source/physics-edit and timing/error/iteration negative checks, six admission checks, and replayed the new parser against the actual retained 150-step Iris H result 2294047. The remote one-shot driver was exercised using mock scheduler commands before actual use; missing os import and experiment-local hash handling were fixed. The 49-file kit is sealed and unchanged. Offline or test-only success was never reported as a real job.

**Actual admission.** One definite receipt: 2294234,confirmed 2026-10-28T00:28:44.398145+07:00. Live Slurm snapshot 17:29:25 UTC reports RUNNING on iris024, 56 CPUs, 3-hour limit. First source-hash phase passed in 31.46 s, then zyx clone started. These are startup observations, not solver means. Full output, terminal status and matched interpretation remain pending.

**Cost and scope.** The prior 224-hour envelope was agent-defined and exhausted for meaningful solver work. The latest direct owner instruction justified one bounded new 168-hour maximum allocation. Root transparently extended the same ledger to 392 CPU-hours; 219 consumed plus 168 reserved = 387. Existing history and retired maxima remain. SU rate and posted charge are unknown. NSCC credit and AI work are unchanged.

**Next decision.** Inspect partial results without accepting an incomplete pair. After completion, collect/replay both 150-step arms and tails/forces/source/runtime/resource evidence, record numerical limits and native sample warnings, then retire only the known actual allocation maximum. Any winning Iris setting remains a hypothesis to transfer to NSCC; raw Iris seconds are not compared with NSCC 3.3646. No background agent or schedule was enabled.
