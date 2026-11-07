# Explicit interleaved N48 placement admitted and actually qualified

7 November 2026, 14:09:57 Vietnam (UTC+7): **2295091 RUNNING on iris001**, elapsed 68 seconds, 56 allocated CPUs and zero GPUs. Source 48 preflight and payload hashes pass. Before any solver, an actual forty-eight-rank probe validates 24/24 placement, strictly alternating NUMA assignment for consecutive rank IDs, and exactly CPU IDs 0–47. First candidate clone preparation has started; no solver arm or performance result at this snapshot. Batch stderr empty. The exact qualification is launcher affinity before MPI_Init, not solver-helper binding or page residency.

## Evidence and new hypothesis

Parent 2295090 is a reviewed complete but negative result: contiguous 24/24 pooled 26.543795906 versus default 24.432288048 s/step (+8.642285% slower), including one full 40-step arm 21.085907685 and another 32.001684128. Exact rank maps and force trajectories repeat, so do not promote the minimum as a stable configuration win. Real source/work checks pass; the cause of timing drift remains unknown.

The current candidate keeps the same N48 source and original numerical work but explicitly uses `--map-by ppr:24:package --rank-by span --bind-to core`. It uses the same first 24 cores per NUMA node as the preceding contiguous 24/24 candidate, changing rank-to-core association. The reference in this trial remains practical default 48 (previously observed 28/20), so the measured comparison is requested placement policy as a whole, not an isolated causal effect of ranking or NUMA balance. Four 40-step/39-interval BAAB arms, uncollated I/O, runtime, DP/fixed iterations and all force/source/field/inode/native gates remain.

I initially considered PPR with fill ranking; actual previous records show it would be a duplicate. That alternative was never submitted. Official OpenMPI 5.0.10 documentation distinguishes mapping, ranking and binding and explains span; actual rank records take precedence over assumed defaults. Root offline tests reject the real prior contiguous proof records, accept alternating fixtures, and exercise the complete source/clone/preparation APIs with a clearly synthetic launcher. The separate real probe above proves this job's actual nonduplicate layout. A missing test import was corrected before passing review, with no cluster action from the failed test.

If this final rank-order trial loses or strong repeated-state drift remains, close blind placement sweeps and qualify targeted process-level memory-residency diagnostics outside scoring rather than recycling unchanged configurations. No prospective speed gain is claimed.

## Resources, provenance and backup scope

57 operational files frozen, one exclusive iris001 node /56 CPUs /zero GPUs /maximum 2.5h, reserve 140 allocated CPU-hours. Actual source before/after, every clone SHA/field/inode check, strict rank files and within/across-mapping force tolerance remain unchanged. The initial conservative window 8400 seconds fits internal 8800/wrapper 8940/wall 9000. Fresh queues were empty at locked admission and sbatch. Ledger **1,838 consumed +140 reserved /stage 1,978**, bounded internal extension +71; not owner allowance or known site-billed SU. Parent 70.388889 CPU-hours was conservatively charged 71 and its 140 maximum retired once. Preserve this allocation, maximum and one-own cap; no concurrent own submission.

Completed 2295090 result, raw evidence and reasoning were captured/pushed once as 3f60a169. New 2295091 code/receipt, current budget and local notes remain uncaptured/uncommitted until a substantive reviewed result or explicit commit request. No status-only commit. Existing history, AI/NSCC work, schedules and MFA unchanged.

The first sandboxed status check exited before the Iris prompt; an escalation request was interrupted by the permission change. A retry under current full access succeeded. This does not establish a VPN, credential or cluster outage; no authentication material was recorded and no MFA attempt was made. Session metadata verifies this HPC fork 01a1b4ac is a child of 01a1b1b3, separate from AI.

Reference: [OpenMPI 5.0.10 mapping/ranking guide](https://docs.open-mpi.org/en/v5.0.10/man-openmpi/man1/mpirun.1.html#mapping-ranking-and-binding-oh-my). [Actual receipt](submission-receipt.json). [Actual CPU/rank layout](post-submit-status.json).

[Source directory](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-interleaved48-20261107).
