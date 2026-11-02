# What our HPC research has actually established

**No configuration developed by this worker has demonstrated a stable improvement over our scored-platform baseline.** Our best reviewed NSCC result is **3.364622070 seconds per step**, job 25940700, four nodes / 512 ranks / 150 steps. It reproduces the organizer's default Scotch recipe. It must not be presented as a new optimization we invented.

The organizer's separate NSCC reference is 3.210832548 s/step. The teammate's supplied 2.079045460 s/step result is on Gadi, a different platform; its runtime recipe and measurement belong to that package. Our matched experiments can test their settings, but do not transfer authorship of those ideas to us.

## Own hypotheses and their outcomes

| Own experimental branch | Question and evidence | Current conclusion |
|---|---|---|
| NUMA-aware Scotch coefficients | On NSCC, the synthetic `(8 16)` grouping reduced the face-cut proxy, but native timing in 25907753 was **3.4416% slower** in its one-node pair. | No gain. Native files passed; final scheduler history and billing were unavailable. No four-node improvement is claimed. |
| Hierarchical axis ordering | Our `zyx` choice at `(7 4 2)` reached **21.229594 s/step**, but reached **26.610796 s/step** in the reverse full-length comparison. Each allocation's first arm won. | No stable order improvement demonstrated. Different allocations/order effects must not be hidden by selecting the best number. |
| Graph-driven CPU placement | We reduced the logical cross-NUMA face proxy for the zyx case from 129,700 to 90,953. Short ABBA looked 18.50% faster, but BAAB was **5.37% slower**, with severe drift/tails. | Close the unchanged timing claim. Better graph proxies are not measured hardware traffic or a solver speedup. |
| Native and post-MPI affinity qualification | Built and checked allocation, core-selection and source/field integrity mechanisms. | Diagnostic evidence, not a measured performance improvement or a reason to label the baseline optimized. |
| Hierarchical zyx versus default Scotch | Earlier Hxyz/Scotch job 2294047 timed out in Scotch; later successful full runs compared hierarchy orders, not these two methods. | A complete matched comparison remained missing. **Job 2294640 is now actually submitted to fill this gap.** |

The hierarchical method is standard OpenFOAM. The parameter choice, hypothesis and testing are ours; claiming a new algorithm would be inaccurate. Negative results and diagnostic work are retained as evidence, but they do not replace the missing performance improvement.

## Borrowed settings being evaluated

The supplied teammate recipe adds socket/core mapping and collated I/O. These flags are not our invention. The isolated I/O pair showed an apparent 6.07% gain that reversed to a 9.35% loss when order changed; it does not establish a stable gain. Actual launcher reports for the first organizer/teammate pair on Iris showed identical reported rank/core assignments. This qualified a separate mapping-only trial as an observed-placement duplicate, without proving all MPI semantics or Gadi behavior equivalent.

Job **2294637** is the owner's requested organizer-versus-teammate comparison on the same Iris setup. Its experimental design and evidence collection are our work; both input recipes remain attributed to their sources. At **2 November 07:16:45 Vietnam**, it was still running its final organizer arm, so there was no complete recipe winner.

## The next measurement of our own configuration

**Accepted job 2294640**, receipt 2026-11-02T00:15:46.990918Z / **2 November 07:15:46 Vietnam**. Slurm verified it pending with `afterany:2294637`, zero allocated CPUs, preserving one active allocation.

- Control: default Scotch.
- Our candidate: hierarchical `(7 4 2)`, `order zyx`.
- Common setup: one Iris node, 56 ranks, the same OpenFOAM v2512 double-precision build, default MPI, uncollated I/O, original 65M physical mesh and numerical settings.
- Order: control → candidate → candidate → control, 40 steps / 39 measured intervals each.

The two methods use their own accepted initialized partitions and fields; they cannot share identical partitioned data. Both source trees have 1,040-file manifests, with the same 41 canonical input pins and explicit allowed decomposition transforms. All sources, copies, initialized fields, native work/output and runtime identities are checked. Candidate input is the reviewed `initialized/order-zyx`, not the original xyz source.

Maximum request is 140 allocated CPU-hours / 2.5 hours, conditionally scheduled after the existing comparison. This is a bounded Iris planning allowance, not a claim about billed SU or a new NSCC grant. Full four-arm timing consistency, Cd/sanity, repeated controls, tails, warnings and resource evidence must be reviewed before reporting an improvement. Iris one-node evidence does not establish NSCC/Gadi four-node performance.

[Actual own-candidate job and scripts](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-own-zyx40-20261102/STATUS.md), [complete research journal](../research-journey-20261019/journal/README.md). Historical measurements retain their original limitations; new measurements must be compared with their own simultaneous controls rather than ranked by raw seconds across allocations.

The [Gadi transfer outlook](../../notes/gadi-transfer-outlook-20261102.md) distinguishes a plausible faster platform baseline from an unproven improvement over Gadi's own references. No Gadi result is claimed.
