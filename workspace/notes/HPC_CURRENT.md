# Current HPC/OpenFOAM handoff

Updated **2 November 2026, 10:54:27 Vietnam**. HPC fork `01a17c4b-65e6-75e0-be95-c5bea1b25502`; AI is separate. No background Codex or schedules. Prior detailed snapshots are [historical](history/HPC_CURRENT-before-xzy-native-20261102T034856Z.md).

## Reviewed outcomes

**Own zyx method job 2294640 completed 0:0**, all four 40-step/39-interval native arms and 222 transfer-file hashes pass. Scotch 22.358237138/31.443932712 versus zyx 27.821793339/31.476255063 s/step. Zyx pooled mean is **10.21498% slower**, adjacent +24.43644%/+0.10279%, control repeat drift +40.63690%. This does not support promotion. The prepared common-teammate-runtime transfer is **closed unsubmitted and unreserved**. Historical 21.2296 was a real full 150 result, but its advantage did not survive repetition. [Result](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-own-zyx40-20261102/completed-2294640/RESULTS.md).

**New xzy initialization job 2294642 completed 0:0 in 272 seconds**, iris001 / 56 CPUs. Independent replay passes 50 collected-file hashes, 41 canonical pins, 8 mesh members, source-preserving clone, all 3 mandatory native stages and 336 field seals. Its new 1040-file accepted manifest is e52d67b1a9a2bcad002fdbd17da982362a8d2e92e678cb81cb442b0601745987. [Initialization result](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-xzy-init-20261102/completed-2294642/RESULTS.md). This is not a solver measurement.

## Actual current native trial

**2294643 RUNNING** on iris001, 56 CPUs, observed **2 November 10:54:27 Vietnam**, elapsed 236 seconds. Actual receipt **10:50:30 Vietnam**. Both accepted source gates and the B1 copy check pass; native xzy solver started at **10:52:24 Vietnam** and reached **step 3/40**. No fatal marker in stdout; full stderr/native/output review and all final means remain pending. Frozen 58-file root `/global/exafs/users/rdmaworkshop30/apac2026/tripleu-iris-xzy40-20261102T034956Z`; evidence root/kit/runs/2294643.

**xzy / Scotch / Scotch / xzy**, 40 steps / 39 intervals each, common default MPI/uncollated, same build/original 65M problem/fixed work, accepted method-specific partitions/fields. New xzy 1040-file manifest is installed from independently reviewed 2294642, never old zyx. Lower total interface/fanout proxy competes with worse busiest-rank surface; no speedup is claimed. [Actual status and receipt](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-xzy40-20261102/STATUS.md).

## Accounting and access

Local Iris ledger: **750 consumed + 140 reserved = 890 CPU-hours**, agent-selected internal stage 890. Reviewed init 2294642 cost 4.231111 allocated CPU-hours, conservatively 5, original 28 maximum retired once. Root documented a bounded 17-hour internal-stage extension from 873 to 890 for only this new 140-hour request. This is not an owner numeric Iris cap, billed SU or an NSCC/AI grant transfer. Fresh queue and financial checks passed under the lock before one definite sbatch. One owned allocation runs; preserve it and its maximum. There are now 23 unique accepted owned Iris job IDs: 21 completed, one prior failed/censored, one running. The earlier 21-job audit remains dated evidence, not a current count.

NSCC read-only transport **10:43:55 Vietnam** returned NAMESPACE_UNAVAILABLE; no SSH authentication attempt or fresh CPU credit/queue proof. No Gadi identity/project is supplied. Do not derive a Gadi forecast from Iris seconds. The best reviewed scored-platform reproduction remains NSCC 3.364622070 s/step, organizer recipe; no own stable scored-platform gain exists. Organizer/teammate recipes retain attribution. AI, submission materials, frozen past payloads and raw failures stay unchanged.

Review per-arm timing tails/drift, Cd repeats/differences, native warnings, maps, resource logs and missing hardware evidence; no trimming. The prepared case is now in an actual native solver allocation; no extra admission while it occupies the own slot. Preserve reasoning and explicit safe captures, small commits and pushes. [Own research history](../reports/hpc-own-research-status-20261102/README.md).
