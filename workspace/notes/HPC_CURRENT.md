# Current HPC/OpenFOAM handoff

Updated **02 November 2026, 10:48:56 Vietnam**. HPC fork `01a17c4b-65e6-75e0-be95-c5bea1b25502`; AI is separate. No background Codex or schedules. Prior detailed snapshots are [historical](history/HPC_CURRENT-before-xzy-native-20261102T034856Z.md).

## Reviewed outcomes

**Own zyx method job 2294640 completed 0:0**, all four 40-step/39-interval native arms and 222 transfer-file hashes pass. Scotch 22.358237138/31.443932712 versus zyx 27.821793339/31.476255063 s/step. Zyx pooled mean is **10.21498% slower**, adjacent +24.43644%/+0.10279%, control repeat drift +40.63690%. This does not support promotion. The prepared common-teammate-runtime transfer is **closed unsubmitted and unreserved**. Historical 21.2296 was a real full 150 result, but its advantage did not survive repetition. [Result](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-own-zyx40-20261102/completed-2294640/RESULTS.md).

**New xzy initialization job 2294642 completed 0:0 in 272 seconds**, iris001 / 56 CPUs. Independent replay passes 50 collected-file hashes, 41 canonical pins, 8 mesh members, source-preserving clone, all 3 mandatory native stages and 336 field seals. Its new 1040-file accepted manifest is e52d67b1a9a2bcad002fdbd17da982362a8d2e92e678cb81cb442b0601745987. [Initialization result](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-xzy-init-20261102/completed-2294642/RESULTS.md). This is not a solver measurement.

## Next native trial

The prepared **xzy versus Scotch BAAB** changes a previously solver-unmeasured hierarchy order, using default MPI/uncollated on both methods, same 56 ranks/build/original 65M problem/fixed work. It has a lower total interface/fanout proxy but worse busiest-rank surface than xyz/zyx; no proxy-based speedup is claimed. Real reviewed xzy manifest is installed; do not substitute old zyx. The four arms are xzy/Scotch/Scotch/xzy, 40 steps / 39 intervals each, 140 CPU-hour maximum. Root is completing financial/freeze/admission review; at this handoff it has no scheduler receipt or reservation. [Payload](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-xzy40-20261102/README.md).

## Accounting and access

Local Iris ledger: **750 consumed + 0 reserved**, internal stage 873; last 28-hour maximum retired once at actual 4.231111 CPU-hours, conservatively 5. To admit the next 140-hour maximum, only an internal stage adjustment of 17 to 890 is needed. This is agent stage planning, not an owner numeric Iris limit, billed SU or an NSCC/AI allocation transfer. Review fresh own queue and reservations under the existing lock; preserve any existing job and obtain a definite one-shot receipt. All 22 retained accepted owned Iris jobs are now terminal; pending new admission is a separate state. [Previous count audit](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-job-count-audit-20261102/README.md) is dated before this new job.

NSCC read-only transport **10:43:55 Vietnam** returned NAMESPACE_UNAVAILABLE; no SSH authentication attempt or fresh CPU credit/queue proof. No Gadi identity/project is supplied. Do not derive a Gadi forecast from Iris seconds. The best reviewed scored-platform reproduction remains NSCC 3.364622070 s/step, organizer recipe; no own stable scored-platform gain exists. Organizer/teammate recipes retain attribution. AI, submission materials, frozen past payloads and raw failures stay unchanged.

Review per-arm timing tails/drift, Cd repeats/differences, native warnings, maps, resource logs and missing hardware evidence; no trimming. Completed preparation requires actual solver comparison next, not more proxy-only work. Preserve reasoning and explicit safe captures, small commits and pushes. [Own research history](../reports/hpc-own-research-status-20261102/README.md).
