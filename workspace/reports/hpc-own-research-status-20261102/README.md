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

[Actual own-candidate job and scripts](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-own-zyx 40-20261102/STATUS.md), [complete research journal](../research-journey-20261019/journal/README.md). Historical measurements retain their original limitations; new measurements must be compared with their own simultaneous controls rather than ranked by raw seconds across allocations.

The [Gadi transfer outlook](../../notes/gadi-transfer-outlook-20261102.md) distinguishes a plausible faster platform baseline from an unproven improvement over Gadi's own references. No Gadi result is claimed.


## Same-Iris comparison reviewed

Job 2294637 completed 0:0. Organizer A1/A2 means 25.581958377 / 30.164981109 s/step; teammate B1/B2 22.396949743 / 27.093606214. Teammate's pooled mean is 11.2228% lower, with both adjacent comparisons favorable, but repeats drift 17.9–21.0% and organizer sampling recommendations exceed the 39 intervals. This is a qualified short-runtime signal for the supplied recipe, not our own winning configuration. All Cd trajectories match; all four reported rank/core maps match. Our separate hierarchical job 2294640 is now actually running and has no result yet. See the [full review](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-recipes40-20261101/completed-2294637/RESULTS.md). Iris is a platform; cross-platform seconds do not establish a three-way recipe ranking.


## Did any Iris run finish below 22 seconds per step?

**Yes.** Completed full-size native runs include the following measured means. These are historical per-arm observations, not a new simultaneous ranking.

| Job | Configuration / arm | Mean s/step | Completed work |
|---|---|---:|---|
| 2294234 | Hierarchical `(7 4 2)`, `zyx`, first arm | 21.229593669 | 150 steps / 149 intervals |
| 2294262 | Hierarchical `(7 4 2)`, `xyz`, first arm | 21.823903674 | 150 steps / 149 intervals |
| 2294635 | Scotch, socket/core MPI, uncollated, second arm | 21.431810307 | 40 steps / 39 intervals |
| 2293754 | Initial hierarchical `(7 4 2)` practice on the full-size case | 21.965353836 | 40 steps / 39 intervals |

The 21.2296 result is real, completed and retained. What is unproven is a stable configuration advantage: the same zyx choice reached 26.6108 in the reversed full-length job, while xyz also changed from 26.9538 to 21.8239. Both first arms won, confounding node/order effects with configuration. Saying no stable improvement must never be shortened to saying that no sub-22 native run exists. The latest teammate/organizer job's 22.397–30.165 means do not erase these older results or provide matched controls for them.

Sources: [2294234 replay](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-order56-full150-20261027/completed-2294234/REVIEW.json), [2294262 reversal](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-order56-full150-reverse-20261028/completed-2294262/REVIEW.json), [2294635 replay](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-collated40-reverse-20261101/completed-2294635/REVIEW.json), [2293754 replay](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-65m-20261021/solver-review.json).


## Own method trial completed: promotion rejected

Job 2294640 completed 0:0 with all four native/source/runtime checks. Scotch 22.358237138/31.443932712 versus zyx 27.821793339/31.476255063 s/step. Zyx pooled +10.21498%, adjacent +24.43644%/+0.10279%, control repeat drift +40.63690%. There is no favorable signal to promote, and no Gadi forecast. The conditional teammate-runtime payload is closed unsubmitted. [Full replay and inspection](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-own-zyx 40-20261102/completed-2294640/RESULTS.md). The old 21.2296 result remains valid as an observation, not a stable optimization claim.


## Actual next native measurement

After rejecting zyx promotion, xzy initialization 2294642 completed 0:0 in 272 seconds with all source/native gates. New actual solver job **2294643** was accepted **2 November 2026, 10:50:30 Vietnam**, and observed RUNNING at 10:51:22 Vietnam on iris001 / 56 CPUs, in source preflight. It compares xzy/Scotch/Scotch/xzy with default MPI/uncollated and fixed 40-step work, using the true new 1040-file accepted source. Structural tradeoffs motivate testing, not a gain claim. Full 140-hour maximum is reserved under a transparently bounded internal stage 890 (750 consumed); no site SU balance or Gadi estimate is asserted. [Actual receipt and limits](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-xzy40-20261102/STATUS.md).

At **2 November 10:54:27 Vietnam**, both source gates passed and the actual xzy solver was at step 3/40 in running 2294643. No completed arm mean or improvement is established yet.
