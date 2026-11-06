# Single-pass preparation retry actually accepted

6 November 2026, Vietnam (UTC+7). Iris accepted **2295086** at 2026-11-06T23:37:40.384266+07:00. At 23:38:19 Vietnam it is RUNNING on iris001, elapsed 39 seconds /56 allocated CPUs /zero GPUs. Payload-before passes; N40 accepted-source validation returns zero after 31.456132 seconds, and N48 source preflight has started. No solver arm at this snapshot; no completed native or timing result.

The prior 2295000 source repair passed both real source gates but A1 preparation timed out at 180 seconds before solver. Its exact internal timeout substage was unobserved because stdout was empty. Root preserves that failed job, 53 raw evidence hashes, 100 frozen hashes and invalid-measurement status. Actual 4.713333 allocated CPU-hours was conservatively charged 5 and the 140 maximum retired once. This is not evidence that 40 ranks lose.

R3 changes only **prepare_arm.py and source_checks.py** among 100 operational files. Static review found redundant complete core hash passes on source and clone. The derived bundle reuses the exact complete-tree helper from actually successful six-arm 2294997: compute core inventory once and compare every core hash to its frozen manifest, then validate all paths, links, directory inventory and supplementary hashes with core_already_verified only at that proven callsite. Each clone still has its own complete core SHA validation. Original source before/after, exact initialized field seals, no source inode reuse, pinned physics, strict rank files, native work/runtime and repeat-force gates remain. Nothing is changed in submitted old payloads or original accepted source trees.

New preparation logs flush timestamps for cloning, core verification, complete-tree verification, fields/inodes and rank proof stages. Root executes the actual preparation CLI end-to-end on a realistic 40-domain fixture with a clearly synthetic offline launcher, verifies clone/endTime/field/inode/proof interfaces and rejection of a changed core field. It does not claim that fixture qualifies real MPI or predicts native speed. The previously actually qualified writer/reader bytes remain identical. A test-fixture mutation-ordering failure was fixed before the final passing review; no failed test is called a pass.

The native hypothesis and controls remain **48/40/40/48**, forty steps/39 intervals per arm, same iris001, default MPI placement, uncollated I/O, v2512 DP and fixed iteration original 65M-cell physics. Solver caps 1,800 seconds and prep 180 seconds remain; max2.5h/56CPUs/zero GPUs reserves140 allocatedCPU-hours. Fresh queue was empty at locked preflight and again before sbatch. The bounded internal stage extends 1,769→1,774 (+5) with 1,634 consumed +140 reserved. Billed site SU unknown; NSCC/AI separate; no owner numeric budget is increased. Preserve active job, full maximum and one-own cap. No schedule, background Codex or MFA action is enabled.

This is an actual new admission and repaired preparation implementation, not a valid completed performance comparison. Preparation elapsed time is not solver s/step. All repeated/native/source/runtime/force gates and terminal review must pass before assessing a gain, exposing order/timing drift and every arm. Historical approximately 22-second observations remain unpassed.

[Receipt](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-rank-density40-vs48-r3-20261106/submission-receipt.json). [Live evidence](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-rank-density40-vs48-r3-20261106/post-submit-status.json). [Exact verification provenance](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-rank-density40-vs48-r3-20261106/ROOT_INDEPENDENT_REVIEW.json).


## Actual preparation and native launch verified

At 23:40:09 Vietnam on 6 November 2026, 2295086 is RUNNING on iris001, elapsed 150 seconds. Both source preflights return zero (N40 31.456132s, N48 31.656919s). Actual A1-control48 preparation returnszero in 46.772873 seconds under the unchanged 180-second cap. Flushed stages show clone 10.753142s, core hashes verified 37.766027s, complete-tree check 37.861341s, fields/inodes 46.404758s and rank files 46.686025s (cumulative from preparation start). All 48 exact rank files and binding reports pass. Actual native mpirun/simpleFoam 48 command starts at 23:39:45.638928 Vietnam with telemetry sampling. At the snapshot no Time step line is present yet, so this proves native process launch, not completion of any measured interval or performance gain. Batch stderr empty. Preserve full 140 reservation and one-own cap.

Compared with old 180-second timeout, the preparation now succeeds; the old internal timeout substage remains unobserved and these are not matched solver performance measurements. No ranked score or historical approximately 22-second improvement is claimed.


## Actual solver stepping verified

At 23:41:23 Vietnam on 6 November 2026, 2295086 is RUNNING on iris001, elapsed 223 seconds. A1-control48 native log has started step 3 of 40; batch stderr empty. Preparation passed in 46.772873 seconds. This proves the actual solver progresses after the repaired preparation; no arm has completed and no stable seconds-per-step result or historical record is claimed. Source/control/native payload stays frozen; full 140 CPU-hour maximum remains reserved and one-own cap occupied.
