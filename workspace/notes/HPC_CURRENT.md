# Current HPC/OpenFOAM handoff

Updated **3 November 2026, 02:06:44 Vietnam**. HPC fork `01a17c4b-65e6-75e0-be95-c5bea1b25502`; AI is separate. No background Codex, schedules or automatic MFA loops. [Earlier detailed handoff](history/HPC_CURRENT-before-scotch-package-20261102.md) is historical.

## VPN request

Latest bounded retry **3 November 00:06:30–00:06:34 Vietnam** returned gateway Authentication failed; **00:07:58** path check remained NAMESPACE_UNAVAILABLE. No SSH authentication, phone-side DUO outcome or exact rejection cause established. No agent cache reset/deletion or automatic loop. [Safe record](nscc-vpn-retry-20261103.md).

## Reviewed xzy result and next actual job

**2294644 COMPLETED 0:0**, 6,261 seconds / 56 CPUs, all 222 transferred files and all four 52-step / 51-interval native/source/runtime gates pass. Xzy pooled **10.25252% slower**, adjacent +1.84160%/+19.78388%, control repeat -11.75533%. Candidate native sample recommendations 69/97 exceed 51. The earlier 40-step 0.71% signal is not reproduced. **Unchanged xzy branch closed**; no more horizon extensions to chase a favorable sign. [Full result](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-xzy52-reverse-20261102/completed-2294644/RESULTS.md). Collection initially failed in the delegated worker, but a bounded root retry succeeded; this was not authentication evidence.

**2294657 COMPLETED 0:0**, 278 seconds / 56 CPUs, terminal observed **3 November 00:05:39 Vietnam**. All 168 collected text artifacts and 112 boundary files replay correctly; native 65M mesh / 56 ranks and accepted control hashes pass. Synthetic 10:1 tree increased logical cross-package faces **37.7308%** and maximum fanout **+3**, so the predeclared graph gates rejected it. **No READY, initialization or solver measurement**. [Full negative result](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-scotch2x28-init-20261102/completed-2294657/RESULTS.md).

**2294670 COMPLETED 0:0**, 280 seconds / 56 CPUs; terminal reviewed **3 November 01:44:26 Vietnam**. All 168 retained artifacts and native graph/source/cut gates replay. 100:1 reduced cross-group faces **5.07289%**, but maximum neighbor patches **20→24** fails the unchanged +2 limit. Four gates pass; no initialization, READY or solver result. **Weight-only tuning for this topology is closed.** [Full result](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-scotch2x28-w100-init-20261103/completed-2294670/RESULTS.md).

The first two status calls timed out because a completed job absent from live squeue caused check_output to raise before JSON emission. A corrected query reached Iris and read sacct plus terminal files. These timeouts do not establish authentication failure. No cancellation or resubmission occurred.

**New actual job 2294671 accepted 03 November 2026 02:05:12 Vietnam.** One Iris node / 56 CPUs / maximum 60 minutes. Native Scotch/xyz/xyz/Scotch, 20 steps per arm, with equal five-second whole-node memory/paging/NUMA/CPU sampling after compute-side preflight. RUNNING on iris001 at 02:05:38 Vietnam; source checks passed and the first clone was being verified at 02:06:44. The sampler compute preflight passed five reads at 1.74–2.11 ms each. Diagnostic only; 19 intervals do not confirm a gain. [Receipt and status](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-xyz20-scotch-screen-20261103/STATUS.md). [Evidence-driven next hypotheses](/home/apacsc42/workspace/reports/hpc-next-directions-20261103/README.md).

## Budget and next decision

Ledger **949 consumed + 56 reserved = 1,005 committed**, existing agent-selected stage **1,009**. Last prep cost 4.355556 actual allocated CPU-hours, conservatively 5; original 28 maximum retired once. All 26 previous owned jobs are terminal; the new diagnostic is accepted. Preserve its queue position and refresh actual scheduler state before further admission. No billed SU or NSCC/AI transfer is claimed.

After terminal collection, inspect native graph gates/source/work, actual initialization/READY state, warnings/resources and missing telemetry; reconcile actual cost once. If promising and fully initialized, separately freeze a matched default-versus-tree solver trial within a reviewed bounded stage. If rejected, close unchanged hypothesis and choose the next distinct useful trial. No blind duplicates or unsupported success claims.

No Gadi identity/project supplied; NSCC access unverified after gateway failure. No own stable scored-platform gain is established. Best reviewed NSCC 3.364622070 s/step is an organizer-recipe reproduction; organizer 3.210832548 and teammate Gadi 2.079045460 are separate references. Iris seconds/percentages cannot forecast a Gadi win. AI payloads, queues, budget and submission materials remain unchanged. [Own research history](../reports/hpc-own-research-status-20261102/README.md).
