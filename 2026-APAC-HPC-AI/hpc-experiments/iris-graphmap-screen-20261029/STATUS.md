# Actual non-scored graph-placement screen

Slurm accepted **2294366** at **2026-10-29T03:04:59.323155+07:00 (Vietnam, UTC+7)**. A definite receipt, frozen 57-file payload and full maximum reservation are retained. Current state and runtime gates are recorded separately in `post-submit-status.json`. Submission alone is not a completed performance measurement.

The job requests one exclusive Iris node, 56 CPU ranks, zero GPUs and at most 50 minutes. It compares the identity rankfile with a graph-derived rankfile in **A–B–B–A** order. Each arm performs **14 solver steps and retains all 13 native timings**. This is a non-scored screening experiment, not the prescribed full 150-step result or an NSCC target hit.

The graph hypothesis reduces unique cross-NUMA logical interface faces from 129,700 to 90,953 at the same 28/28 rank counts and the same group cell loads. This is a proxy, not a speed prediction. Each rank keeps its zyx mesh partition, initialized fields, fixed iterations and physics. Both treatments use the same native Open MPI rankfile mechanism; only physical rank placement differs.

Before any solver launch, the job must verify the accepted 1,040-file source inventory and graph boundary hashes, then compile and run native MPI qualification to prove identity equals the actual default CPU map and candidate equals its requested permutation. Global logical Open MPI core slots are validated against actual OS CPU masks; they are not assumed to be the same identifiers. Every fresh arm is copied and byte-checked independently. Time-zero fields, native output rows, command exits and runtime/source stability gates remain required.

An initial 18-step draft was revised before submission after retained logs projected about 649 seconds for 18 steps versus 524 seconds for 14. The actual solver cap is 650 seconds per arm, with a shared 2,850-second deadline, protected planning windows and a 2,970-second outer timeout. Insufficient remaining time stops the experiment rather than reducing work during a run. A partial or failed arm is not a valid full screen.

## Accounting and evidence

The maximum reservation is **46.666667 allocated CPU-hours**, within the existing Iris envelope: consumed 457 plus reserved 46.666667 equals 503.666667 under ceiling 505. Headroom after reservation is 1.333333 CPU-hours; no ceiling increase or transfer from NSCC/AI occurred. The site SU rate and balance remain unknown.

Remote root: `/global/exafs/users/rdmaworkshop30/apac2026/tripleu-iris-gmap14-20261028T200415Z`. Kit: `root/kit`; run evidence and isolated cases: `root/kit/runs/2294366`; scheduler logs: `root/kit/runs/2294366.out/.err`. The compiled qualification binary and large processor trees are not Git payloads; source, build hashes and selected text evidence are retained through collection.

Root independently reran the offline positive and negative rank/source/field/parser fixtures and replayed a real retained native 14-step prefix without dropping slow intervals. Actual rankfile behavior, all four arms and terminal status still require cluster review. One short balanced cycle cannot establish robust tuning, output equivalence or a hardware cause. Frequency, memory bandwidth, NUMA page residency and solver helper-thread placement are not collected by this kit.

NSCC remains separate: its best reviewed full observation is 3.364622070 seconds per step, and the prepared native Scotch/xyz/zyx comparison is still unsubmitted because verified access is unavailable. This Iris screen cannot beat that target by cross-machine substitution.
