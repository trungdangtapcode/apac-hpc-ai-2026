# Current HPC/OpenFOAM handoff

Updated **2 November 2026, 21:35:51 Vietnam**. HPC fork `01a17c4b-65e6-75e0-be95-c5bea1b25502`; AI is separate. No background Codex, schedules or automatic MFA loops. [Earlier detailed handoff](history/HPC_CURRENT-before-scotch-package-20261102.md) is historical.

## VPN request

Latest bounded retry **3 November 00:06:30–00:06:34 Vietnam** returned gateway Authentication failed; **00:07:58** path check remained NAMESPACE_UNAVAILABLE. No SSH authentication, phone-side DUO outcome or exact rejection cause established. No agent cache reset/deletion or automatic loop. [Safe record](nscc-vpn-retry-20261103.md).

## Reviewed xzy result and next actual job

**2294644 COMPLETED 0:0**, 6,261 seconds / 56 CPUs, all 222 transferred files and all four 52-step / 51-interval native/source/runtime gates pass. Xzy pooled **10.25252% slower**, adjacent +1.84160%/+19.78388%, control repeat -11.75533%. Candidate native sample recommendations 69/97 exceed 51. The earlier 40-step 0.71% signal is not reproduced. **Unchanged xzy branch closed**; no more horizon extensions to chase a favorable sign. [Full result](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-xzy52-reverse-20261102/completed-2294644/RESULTS.md). Collection initially failed in the delegated worker, but a bounded root retry succeeded; this was not authentication evidence.

**2294657 COMPLETED 0:0**, 278 seconds / 56 CPUs, terminal observed **3 November 00:05:39 Vietnam**. All 168 collected text artifacts and 112 boundary files replay correctly; native 65M mesh / 56 ranks and accepted control hashes pass. Synthetic 10:1 tree increased logical cross-package faces **37.7308%** and maximum fanout **+3**, so the predeclared graph gates rejected it. **No READY, initialization or solver measurement**. [Full negative result](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-scotch2x28-init-20261102/completed-2294657/RESULTS.md).

No demonstrated weight-order inversion was found in the pinned OpenFOAM wrapper; exact runtime library labeling remains untraced. A single targeted 100:1 falsification, with domains/physics/control and all graph gates unchanged, is being prepared. It is not submitted yet. Stop further weight-only tuning if it also rejects; do not promote proxy reductions as speedups.

## Budget and next decision

Ledger **944 consumed + 0 reserved**, existing agent-selected stage **1,009**. Last prep cost 4.324444 actual allocated CPU-hours, conservatively 5; original 28 maximum retired once. Another 28-hour preparation fits without stage increase. All 25 retained owned job IDs are terminal now; current queues must be refreshed before any admission. No billed SU or NSCC/AI transfer is claimed.

After terminal collection, inspect native graph gates/source/work, actual initialization/READY state, warnings/resources and missing telemetry; reconcile actual cost once. If promising and fully initialized, separately freeze a matched default-versus-tree solver trial within a reviewed bounded stage. If rejected, close unchanged hypothesis and choose the next distinct useful trial. No blind duplicates or unsupported success claims.

No Gadi identity/project supplied; NSCC access unverified after gateway failure. No own stable scored-platform gain is established. Best reviewed NSCC 3.364622070 s/step is an organizer-recipe reproduction; organizer 3.210832548 and teammate Gadi 2.079045460 are separate references. Iris seconds/percentages cannot forecast a Gadi win. AI payloads, queues, budget and submission materials remain unchanged. [Own research history](../reports/hpc-own-research-status-20261102/README.md).
