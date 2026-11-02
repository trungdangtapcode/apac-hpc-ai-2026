# Current HPC/OpenFOAM handoff

Updated **2 November 2026, 15:07:02 Vietnam**. HPC fork `01a17c4b-65e6-75e0-be95-c5bea1b25502`; AI is separate. No background Codex or schedules. Prior detailed snapshots are [historical](history/HPC_CURRENT-before-xzy-native-20261102T034856Z.md).

## Reviewed outcomes

**Own zyx method job 2294640 completed 0:0**, all four 40-step/39-interval native arms and 222 transfer-file hashes pass. Scotch 22.358237138/31.443932712 versus zyx 27.821793339/31.476255063 s/step. Zyx pooled mean is **10.21498% slower**, adjacent +24.43644%/+0.10279%, control repeat drift +40.63690%. This does not support promotion. The prepared common-teammate-runtime transfer is **closed unsubmitted and unreserved**. Historical 21.2296 was a real full 150 result, but its advantage did not survive repetition. [Result](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-own-zyx40-20261102/completed-2294640/RESULTS.md).

**New xzy initialization job 2294642 completed 0:0 in 272 seconds**, iris001 / 56 CPUs. Independent replay passes 50 collected-file hashes, 41 canonical pins, 8 mesh members, source-preserving clone, all 3 mandatory native stages and 336 field seals. Its new 1040-file accepted manifest is e52d67b1a9a2bcad002fdbd17da982362a8d2e92e678cb81cb442b0601745987. [Initialization result](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-xzy-init-20261102/completed-2294642/RESULTS.md). This is not a solver measurement.

## Latest reviewed native result

**2294643 COMPLETED 0:0**, iris001 / 56 CPUs, 5,847 seconds, observed **2 November 14:48:52 Vietnam**. All 222 transfer hashes and four 40-step / 39-interval native/source/runtime gates pass. Xzy B1/B2 **32.777265111 / 33.505903444 s/step**; Scotch A1/A2 **33.170890385 / 33.586073698**. Pooled xzy **0.70973% lower**, adjacent -1.18666%/-0.23870%, repeat drift +1.25165% S / +2.22300% X. This is a small favorable screen, not a stable win.

Xzy native sample recommendations 50/44 exceed 39 intervals; both warn the run is too short. Candidate tails are wider. Every arm trends from first-ten 35.4–36.5 to last-ten 31.1–32.4 s/step; cause unknown, no trimming. Same-method Cd repeats match; method-specific final Cd 0.43777827 xzy / 0.43695933 Scotch. Bounding-omega diagnostics and all warnings/logs retained, not hidden. Reported maps match; bandwidth/cycles/sustained clocks/helper-affinity/pages not collected. [Full review](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-xzy40-20261102/completed-2294643/RESULTS.md).

**Actual confirmation job 2294644 RUNNING** on iris001 / 56 CPUs, observed **2 November 15:07:02 Vietnam**, elapsed 242 seconds. Definite receipt **15:03:00 Vietnam**. Both accepted source gates passed and the actual first Scotch solver reached **step 3/52**. No completed arm mean or final win exists yet. Frozen 58-file root `/global/exafs/users/rdmaworkshop30/apac2026/tripleu-iris-xzy52-reverse-20261102T080210Z`.

Reverse **Scotch / xzy / xzy / Scotch**, 52 steps / 51 intervals each, same accepted sources, physical problem, fixed iterations and default MPI/uncollated. Prior native N=50 motivates a longer horizon but does not establish significance for a 0.7% effect or guarantee future adequacy. Hard maximum 3 hours / 168 CPU-hours. Protected full-arm and initial-source time checks pass local fixtures; no truncation or trimming. [Actual status and receipt](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-xzy52-reverse-20261102/STATUS.md).

## Accounting and access

Local Iris ledger **841 consumed + 168 reserved = 1,009 CPU-hours**, agent-selected internal stage 1,009. Prior 2294643 cost 90.953333 allocated CPU-hours, conservatively 91; original 140 maximum retired once. A bounded 119-hour stage extension from 890 covers only this new 168-hour maximum, not an owner numeric/site quota, billed SU or NSCC/AI transfer. One owned allocation is now running; preserve it and its maximum. There are 24 retained unique accepted owned Iris job IDs: 22 completed, one prior failed/censored, one running. No further admission while this owned allocation occupies the slot.

**Owner-requested VPN retry, 2 November 10:59:50 Vietnam:** exactly one attempt returned gateway Authentication failed; client exited 1. Fresh path probe **11:00:37 Vietnam** still returned NAMESPACE_UNAVAILABLE. No SSH authentication, DUO phone delivery/approval or exact failure cause was established. Private recovery state preserved, no repeated loop. [Safe attempt record](nscc-vpn-retry-20261102.md). No fresh CPU credit/queue proof. No Gadi identity/project is supplied. Do not derive a Gadi forecast from Iris seconds. The best reviewed scored-platform reproduction remains NSCC 3.364622070 s/step, organizer recipe; no own stable scored-platform gain exists. Organizer/teammate recipes retain attribution. AI, submission materials, frozen past payloads and raw failures stay unchanged.

Review per-arm timing tails/drift, Cd repeats/differences, native warnings, maps, resource logs and missing hardware evidence; no trimming. The required longer confirmation is now actually running; review it and its warnings rather than extrapolate the short-run sign. Preserve reasoning and explicit safe captures, small commits and pushes. [Own research history](../reports/hpc-own-research-status-20261102/README.md).


Read-only NSCC transport at **2 November 14:48:46 Vietnam** still returned NAMESPACE_UNAVAILABLE. No fresh VPN login or DUO attempt was made by this status checkpoint; the earlier 10:59 gateway failure remains historical authentication evidence.


## New VPN attempt and dated Iris terminal observation — 2 November evening

Owner explicitly requested another VPN login. At **21:06:46 Vietnam**, one bounded attempt returned gateway Authentication failed; **21:08:07** transport probe remains NAMESPACE_UNAVAILABLE. No SSH authentication or phone-side DUO outcome was observed. Private recovery state preserved. [Safe record](nscc-vpn-retry-20261102.md#new-explicitly-requested-attempt--2106-vietnam). No automatic MFA loop or AI changes.

At **21:05:43 Vietnam**, actual Iris accounting showed **2294644 COMPLETED 0:0 in 6,261 seconds / 56 CPUs** and all four 52-step arms End. Runtime summaries alone are not independent terminal replay. Collection currently encounters interactive-bridge framing/timeout failures; do not call that authentication failure or assume an empty current queue. Raw result collection/review remains pending. Keep the original maximum until separately recorded accounting reconciliation; no fresh Iris submission/queue or NSCC credit is claimed here.
