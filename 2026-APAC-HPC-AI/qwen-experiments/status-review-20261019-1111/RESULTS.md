# Reviewed H100 outcomes and H200 queue — 19 October 2026

Scheduler evidence checked at 11:11 UTC; review completed at 2026-10-19T11:15:15.315162+00:00. All measurements remain platform-specific. This status review submitted no new allocation and did not authenticate or restart the VPN.

## Current answer

H200 jobs **24733, 24736, 24737 and 24738 are still pending for Priority**. The two hpcai nodes are allocated. The highest accepted H200 observation remains **24724 = 2938.628 good tokens/s**; its own interaction repeat 24737 has not run at this check. Do not cancel or resubmit these jobs solely to refresh their positions.

The three H100 jobs have finished, and all three pass full local protocol, request/error/SLA, frozen payload, resolved runtime, short-output and 12-case long-output checks. Their performance conclusions differ:

| Job | Trial | Good tokens/s | Joint success (%) | Mean TTFT (ms) | Mean ITL (ms) | Change vs fresh N54 |
|---|---|---:|---:|---:|---:|---:|
| 221645 | N54 default-collective independent repeat | 2418.588 | 98.6139 | 711.780 | 18.255 | +0.0000% |
| 221646 | N56 load trial | 2407.364 | 98.4169 | 886.297 | 18.201 | -0.4641% |
| 221669 | N54 forced prefill Tree | 2160.946 | 98.1022 | 1380.699 | 17.260 | -10.6525% |

The N54 repeat is -0.5061% from the earlier 221590 observation of 2430.891. N54 is independently remeasured near its earlier result, but this pair alone does not prove a statistically significant gain over N52. N56 produces no observed improvement versus the fresh N54 repeat; do not automatically proceed to N58. The highest individual H100 observation remains 221590, not a new record in this batch.

Forced Tree is **-10.6525% worse** than the fresh same-N54 default-collective control. It passes the acceptance checks but loses performance: close this branch, retain default selection and preserve the result. Mean TTFT increases substantially while mean ITL improves; one favourable metric does not make the overall configuration faster.

Good tokens/s means requests meeting both TTFT ≤3000 ms and per-request mean ITL ≤20 ms per second, multiplied by 200. Joint success includes request failures in its denominator and must reach at least 90%. All reported latency values are in milliseconds. Official accuracy at 99% of the organiser reference remains unverified.

## The Tree hypothesis really executed

The separately scored N54 benchmark is distinct from the subsequent N48 diagnostic profile. The latter contains **16 sealed, nonempty rank traces and 355/355 successful diagnostic requests**. All eight prefill ranks show actual Tree all-reduce kernels; no Ring all-reduce kernel appears in those prefill traces. The decoded runtime keeps MNNVL and FlashInfer on all eight ranks. This is execution evidence rather than inference from an environment variable.

The N48 profile is diagnostic, not ranked traffic and not a causal decomposition of the N54 result. Kernel-duration shares sum event durations across ranks; they are not critical-path wall-time fractions. This outcome rejects forcing prefill Tree for this tested deployment; it does not prove every communication optimisation is exhausted.

## Credit and next decision

The ledger at 19/10/2026-19:00:02 SGT reports **34608.356 SU remaining**, Used 29391.644, In Doubt 0.000. The three completed jobs consumed approximately **1415.964 SU**, matching the Used delta within rounding; their former 4608-SU maximum reservations are released only after this reconciliation. No own PBS jobs remain active. Outstanding maximum reserves: 0.000 SU. Internal headroom under the unchanged 51000-SU operating bound is **21608.356 SU**, with the 13000-SU buffer retained. Reported balance is a dated published snapshot.

Keep the four H200 queue positions and review them when they run. On H100, stop this load-growth branch and forced Tree. A further GPU trial needs a distinct, evidence-backed hypothesis and matched control rather than a larger concurrency or unchanged rerun. Prioritise the pending H200 interaction confirmation and organiser accuracy; use the retained profile to prepare a targeted next experiment. This status check adds no new job, budget increase, slide change, official package promotion or AI schedule.

## Retained evidence

- [H200 queue](slurm-queue.txt) and [terminal accounting](slurm-accounting.txt).
- [PBS terminal accounting and project ledger](pbs-queue-accounting.txt).
- [N54 review](221645.pbs111-review.json), [N56 review](221646.pbs111-review.json), [Tree review](221669.pbs111-review.json).
- [Actual Tree rank analysis](h100-prefill-tree-profile.json) and [named kernel summary](profile-summary.txt).
- The collection receipts identify the immutable source snapshots: [221645](collect-221645.json), [221646](collect-221646.json), [221669](collect-221669.json).
- [Prior hypothesis and acceptance rules](../research-followup-20261019-0600/PLAN.md).
