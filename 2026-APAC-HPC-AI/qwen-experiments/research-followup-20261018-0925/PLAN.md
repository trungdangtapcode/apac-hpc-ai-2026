# Result-driven followups — 18 October 2026, 09:28 UTC

## Standing instruction

The user explicitly requested: whenever a job completes, assess its result, revise the hypothesis and submit the next justified experiment. Do not wait for an entire batch when one completed job already resolves an independent hypothesis. Review actual runtime and output, not only scheduler completion. Close losing branches. Preserve queue positions and account for credit before submitting. This does not enable Codex autopilot or a replacement AI schedule.

## New completed evidence

Fresh H100 auto-decode control **221275.pbs111** finished in **14:25**, passed terminal seal, frozen payload, full protocol, runtime, short nonregression and all 12 long retrieval checks. Its concurrency 50 score is **2,248.459 good output tokens/s**, joint latency success **98.6496%**, mean first-token latency **455.280 ms**, mean inter-token latency **19.466 ms**.

The independent HPC-Ops decode repeat **221274** scores **2,304.083**, now **2.4739% above this new control**. The original matched pair was +2.7955%. The new control is only about 0.13% above the previous control 221262, so the directional HPC-Ops result survives the reversed candidate/control ordering. This supports further research around the replicated backend. It is not a confidence interval, guarantee for another load/GPU, or organiser accuracy certification. TTFT remains higher with HPC-Ops while ITL is lower. Keep all requests and both latency limits in acceptance decisions.

The N52 HPC-Ops job 221276 is still running. Its result is not needed to test an independent N50 prefill chunk change or to profile the replicated N50 backend. Do not claim any N52 gain before its full review.

## Submitted hypotheses

| Job | Hardware and configuration | Hypothesis and comparison |
|---|---|---|
| **221284.pbs111** | 16 H100, existing HPC-Ops decode, concurrency 50, chunk 4096; profile after scoring | After changing decode MoE implementation, the previous auto-runner profile may no longer identify the main cost. Obtain a fresh full score first, then 16-rank diagnostic at concurrency 48, four prefill and 32 decode capture steps. Compare score with 221263/221274 and kernel categories with 221262 only descriptively. |
| **221285.pbs111** | 16 H100, same HPC-Ops decode, concurrency 50; prefill chunk 8192 | Test whether a larger prefill scheduling chunk improves qualifying throughput or TTFT at the faster decode operating point. Only prefill chunk/derived graph geometry changes. Compare directly with 221284's score and prior HPC-Ops N50 repeats. H200's tiny chunk gain motivates a bounded test; it is not a predicted H100 gain. |
| **24544** | 16 H200, DeepGEMM prefill, chunk 8192, concurrency 58; decode unchanged | Two chunk 8192 N56 observations have small positive differences. Check one adjacent load point to see whether batching changes the useful concurrency region. Compare same-load historical chunk 4096 job 24352 and fresh N56 chunk 8192 repeat 24527. Load and chunk effects cannot both be isolated from one cross-load comparison. |

The PBS dependency links **221276 → 221284 → 221285** were verified in qstat. One running 16-GPU allocation at a time, at most three active PBS jobs. Each cap 45 minutes / 1,536 SU. Existing H200 jobs 24528/24529/24538 retain positions; new 24544 is the fourth active H200 job, under the five-job bound, each 17 minutes / 16 GPUs. No unvalidated HPC-Ops prefill/decode combination is introduced.

## Stopping and followup rules

Require sealed terminal exports, exact frozen file hashes, intended runtime and layout, native checkpoint/precision, unchanged 60/120/30 protocol, zero request errors/cancellations, joint latency success at least 90%, short output nonregression and 12/12 long retrieval checks. Keep failed runs as evidence; never count a deployment failure as a completed benchmark. Official full-set accuracy at 99% of the reference evaluation score remains unverified.

For 221284 require all 16 nonzero trace ranks and inspect diagnostic request success. Its profile must not overlap scoring. Use the corrected grouped-GEMM classifier and inspect actual HPC-Ops kernel names; the old name-based classifier alone cannot establish the new backend's MoE fraction. Kernel fractions are summed duration shares, not wall-time gains or a speedup prediction. Profile deferral/failure does not erase a valid score; do not silently relax output checks to obtain traces.

If 221285 loses, close the chunk 8192 branch on H100 rather than trying a larger chunk automatically. If it improves while passing all gates, replicate before promotion. If 24544 fails SLA or does not improve enough to justify higher latency, retain the existing N56 operating point; no automatic N60. Do not retry backend/output failures unchanged. Review 221276 before another H100 load increase.

## Accounting

The ledger as of 18 October 17:20:01 SGT shows Used **22,072.889 SU**, Balance **40,391.111 SU**, In Doubt **1,536 SU**. Job 221274's **492.658 SU** now reconciles in Used; its maximum reservation is released. Terminal 221275's walltime 14:25 implies **492.089 SU**, not yet reconciled, so retain its full 1,536 SU reservation. Existing running 221276 retains 1,536 SU.

New pair reserve: **3,072 SU maximum**. Total conservative outstanding reserve including terminal lag and 221276: **6,144 SU**. Planning headroom under the unchanged internal 51,000 SU cap: **22,783.111 SU**. The retained 13,000 SU buffer is an internal choice, not an organiser quota. The displayed balance already excludes In Doubt; do not deduct that prepayment twice.

No new Codex schedule, background AI process, slide/package promotion or organiser upload. The existing non-AI Slurm submission function ran once under its lock. Frozen syntax and payload checks: next-validation.json. Credit, accounting, dependency receipts and raw collected artifacts are retained beside this plan or linked from the budget/continuous plan.
