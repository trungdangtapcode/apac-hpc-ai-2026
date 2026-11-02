# Current HPC/OpenFOAM handoff

Updated **2 November 2026, 14:48:52 Vietnam**. HPC fork `01a17c4b-65e6-75e0-be95-c5bea1b25502`; AI is separate. No background Codex or schedules. Prior detailed snapshots are [historical](history/HPC_CURRENT-before-xzy-native-20261102T034856Z.md).

## Reviewed outcomes

**Own zyx method job 2294640 completed 0:0**, all four 40-step/39-interval native arms and 222 transfer-file hashes pass. Scotch 22.358237138/31.443932712 versus zyx 27.821793339/31.476255063 s/step. Zyx pooled mean is **10.21498% slower**, adjacent +24.43644%/+0.10279%, control repeat drift +40.63690%. This does not support promotion. The prepared common-teammate-runtime transfer is **closed unsubmitted and unreserved**. Historical 21.2296 was a real full 150 result, but its advantage did not survive repetition. [Result](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-own-zyx40-20261102/completed-2294640/RESULTS.md).

**New xzy initialization job 2294642 completed 0:0 in 272 seconds**, iris001 / 56 CPUs. Independent replay passes 50 collected-file hashes, 41 canonical pins, 8 mesh members, source-preserving clone, all 3 mandatory native stages and 336 field seals. Its new 1040-file accepted manifest is e52d67b1a9a2bcad002fdbd17da982362a8d2e92e678cb81cb442b0601745987. [Initialization result](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-xzy-init-20261102/completed-2294642/RESULTS.md). This is not a solver measurement.

## Latest reviewed native result

**2294643 COMPLETED 0:0**, iris001 / 56 CPUs, 5,847 seconds, observed **2 November 14:48:52 Vietnam**. All 222 transfer hashes and four 40-step / 39-interval native/source/runtime gates pass. Xzy B1/B2 **32.777265111 / 33.505903444 s/step**; Scotch A1/A2 **33.170890385 / 33.586073698**. Pooled xzy **0.70973% lower**, adjacent -1.18666%/-0.23870%, repeat drift +1.25165% S / +2.22300% X. This is a small favorable screen, not a stable win.

Xzy native sample recommendations 50/44 exceed 39 intervals; both warn the run is too short. Candidate tails are wider. Every arm trends from first-ten 35.4–36.5 to last-ten 31.1–32.4 s/step; cause unknown, no trimming. Same-method Cd repeats match; method-specific final Cd 0.43777827 xzy / 0.43695933 Scotch. Bounding-omega diagnostics and all warnings/logs retained, not hidden. Reported maps match; bandwidth/cycles/sustained clocks/helper-affinity/pages not collected. [Full review](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-xzy40-20261102/completed-2294643/RESULTS.md).

Next justified measurement is **reverse ABBA 52 steps / 51 intervals** per arm, same methods/sources/default MPI/uncollated and fixed numerical work. Native N=50 motivates the horizon, but does not prove 0.7%-effect significance or future sample adequacy. Preparing robust 3-hour / 168 CPU-hour bounds to avoid truncating a full arm. At this review no new scheduler receipt or reservation exists; fresh queue observed empty, admission remains a separate checkpoint. Preserve all completed evidence and obtain an actual new receipt before calling the confirmation submitted.

## Accounting and access

Local Iris ledger **841 consumed + 0 reserved**, internal stage 890. Current 5847-second job cost 90.953333 allocated CPU-hours, conservatively 91; original 140 maximum retired once. A robust 168-hour reverse request would require internal stage 1009 (increment 119), not yet changed or reserved. The owner numeric/site budget is distinct; no billed Iris SU or NSCC/AI transfer is implied. All 23 retained owned Iris job IDs are terminal now; actual next admission must recheck own queue and budget under the existing lock.

**Owner-requested VPN retry, 2 November 10:59:50 Vietnam:** exactly one attempt returned gateway Authentication failed; client exited 1. Fresh path probe **11:00:37 Vietnam** still returned NAMESPACE_UNAVAILABLE. No SSH authentication, DUO phone delivery/approval or exact failure cause was established. Private recovery state preserved, no repeated loop. [Safe attempt record](nscc-vpn-retry-20261102.md). No fresh CPU credit/queue proof. No Gadi identity/project is supplied. Do not derive a Gadi forecast from Iris seconds. The best reviewed scored-platform reproduction remains NSCC 3.364622070 s/step, organizer recipe; no own stable scored-platform gain exists. Organizer/teammate recipes retain attribution. AI, submission materials, frozen past payloads and raw failures stay unchanged.

Review per-arm timing tails/drift, Cd repeats/differences, native warnings, maps, resource logs and missing hardware evidence; no trimming. The previous native allocation is terminal; complete the next justified admission rather than treating a sampling-limited result as a global stop. Preserve reasoning and explicit safe captures, small commits and pushes. [Own research history](../reports/hpc-own-research-status-20261102/README.md).
