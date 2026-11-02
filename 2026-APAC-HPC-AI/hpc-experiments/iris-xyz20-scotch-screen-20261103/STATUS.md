# Instrumented xyz versus Scotch diagnostic accepted

**Job 2294671 accepted 03 November 2026 02:05:12 Vietnam.** Iris, one node, 56 CPUs, zero GPUs, maximum 60 minutes / 56 allocated CPU-hours. Native S/X/X/S sequence, 20 steps / 19 intervals each. Frozen runtime includes equal five-second node sampling with compute-side cost/availability checks and explicit missing-data handling. No measured improvement or official scaling result exists yet.

The question, prior 12-arm drift evidence, exact source lineage, controlled change, sampling limitations and next rank-density/locality hypotheses are preserved in README.md and workspace/reports/hpc-next-directions-20261103/README.md. A short diagnostic can inform the next test; it cannot establish a stable gain. Sources are the independent accepted 1,040-file Scotch and xyz trees, the latter pinned to job 2294262. Original physics, fixed iterations, initialization, fields, native output and runtime gates remain required.

The root verified and committed all 62 frozen payload files before deployment. The deployment reply timed out, but exact-root reconciliation rehashed all 62 files and both manifests, confirming no remote submission intent. Three preflight attempts then timed out without local durable intent, reservation or sbatch. Their exact transport cause remains undetermined; it is not established as authentication failure. A structured standalone read showed both named-user and numeric-user queues empty. The retained admission wrapper repeated both reads under the ordinary budget lock, asserted agreement, and then used the unchanged durable intent/reservation plus one-sbatch transaction. Receipt stdout is 2294671. No cancellation or duplicate scheduler submission occurred.

Consumed 949 plus reserved 56 = **1,005 allocated CPU-hours**, inside the unchanged internal stage 1,009. This is local planning, not billed SU. The first marker means submitted; consult post-submit-status.json for a dated scheduler observation. Source, sampling and native outputs need review after terminal completion; no automatic Codex wake-up was enabled.

## Observed execution

RUNNING on iris001 at 3 November 2026, 02:05:38 Vietnam. At 02:06:44, source preflight completed and the first Scotch clone was being verified. All five sampling reads passed the 50-ms cost gate (1.74–2.11 ms); sampler enabled. This is measured collection duration, not a measured solver perturbation bound. The first solver result is still pending.
