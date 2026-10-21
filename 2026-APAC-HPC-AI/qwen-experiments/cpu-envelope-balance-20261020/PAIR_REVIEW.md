# Balanced CPU envelopes work as intended but do not deliver a useful gain

The H100 control **222551** and candidate **222552** both pass the sealed local protocol, SLA, runtime and output-comparison gates. The candidate produces **2414.502691 good output tokens/s** versus **2407.544052**, a **0.289035%** increase. This misses the prospective **1%** useful-gain gate. **Close this exact CPU-envelope policy without an unchanged repeat or default promotion.** The retained H100 individual peak remains 2433.019859 from 222048; that historical unobserved point is not the matched control.

## Question and exact change

The preceding actual locality capture showed native SGLang GPU schedulers already on local NUMA CPUs, but an ordinal outer wrapper left NUMA 1 groups sharing only eight CPU IDs. The hypothesis was that balancing the same 32/32/64 per-task CPU budget would improve serving by reducing host scheduling imbalance. Both jobs retain N54, two TP4/EP1 prefills, TP8/EP8 decode, the official FP8 target, BF16 KV, both-phase HPC-Ops, chunk 4096, FA3 prefill/FlashInfer decode, MNNVL, round-robin, receive interval one, the official scored client and common diagnostics. The prelaunch UUID-aware helper is identical; only the selected envelope mode differs. Frozen submitted payloads remain unchanged.

## Complete serving and tail review

| Quantity | Legacy 222551 | Balanced 222552 |
|---|---:|---:|
| Good output tokens/s | 2407.544052 | 2414.502691 |
| Joint qualifying requests / total | 1488 / 1513 | 1490 / 1516 |
| Joint qualifying fraction | 98.347654% | 98.284960% |
| Mean TTFT, ms | 732.101787 | 708.229503 |
| TTFT p99, ms | 3443.675812 | 3457.002692 |
| Mean request ITL, ms | 18.192860 | 18.249500 |
| ITL p99, ms | 19.115946 | 19.208171 |
| TTFT / ITL breaches | 20 / 5 | 22 / 4 |
| Request errors or cancellations | 0 | 0 |
| Long-context diagnostic | 12 / 12 | 12 / 12 |
| Separate diagnostic requests | 356 / 356 | 380 / 380 |
| Separate sealed rank traces | 16 | 16 |
| Allocated walltime, s | 828 | 821 |
| Estimated allocated charge, SU | 471.040000 | 467.057778 |

The full 60/120/30 protocol and raw exported Goodput × 200 were verified. Seven of eight hand-written short checks pass in each job; the same retained baseline short mismatch remains, with no new mismatch. This local output-comparison gate is not a claim of perfect answers or the organiser's full-set accuracy. Each long response was checked against its expected value. No overlapping TTFT/ITL breach or request error is hidden by the means. Slightly better mean TTFT accompanies worse ITL and p99 TTFT; the score change is not a substantial end-to-end gain. [Per-job reviews and pair summary](paired-serving-comparison.json), [review output](review.stdout), [raw tail/profile inspection](inspection.stdout).

## The intended CPU intervention actually reached the GPU workers

[Sealed envelope and scheduler review](envelope-review.json) verifies 4/4/8 distinct CUDA UUIDs, all 16 GPU scheduler processes per job, equal physical-core counts, allowed-allocation membership and every captured GPU scheduler thread mask. Both deployments use the same physical nodes, a2ap-dgx014 and a2ap-dgx030. Order and unmeasured host/cache state remain limitations.

| GPU group | Legacy scheduler mask | Balanced scheduler mask |
|---|---|---|
| Prefill 0, NUMA 0 | 0–31 | 0–31 |
| Prefill 1, NUMA 1 | 56–63 | 56–87 |
| Decode, NUMA 0 | 0–55 | 0–31 |
| Decode, NUMA 1 | 56–63 | 56–87 |

All captured GPU scheduler threads are local and match the expected envelope intersection. Some non-GPU parent threads retain the full allocation mask; they are explicitly recorded separately, not declared within the task envelope. This confirms a real intervention, so the flat serving outcome cannot be dismissed as a missing configuration change. Scored per-thread demand and host-memory placement were not collected. It does not prove that CPU contention never occurs or that another affinity policy cannot help.

## Resources, queues, runtime and profiler limits

Scored hardware samples cover 16 nonoverlapping GPU UUIDs in each job: 25 decode, 24 prefill 0 and 25 prefill 1 samples. Sampled decode GPU activity averages 99.97% / 100%; the prefill averages are about 92.20% / 87.60% and 92.47% / 88.41%. These are sampled activity percentages, not measured compute efficiency or evidence of a particular causal bottleneck. Per-role VRAM, power/clocks, node CPU/memory/network counters and native source/runtime/transport logs are retained and inspected in the resource JSON and run reviews.

Interior scored gauges show decode queue zero in both runs and mean decode running requests 45.8 / 45.64. Decode KV token occupancy averages 0.2336 / 0.2300; it is not VRAM utilization. Prefill 1 sampled queue peaks at 7 / 21, so the balanced envelope does not eliminate prefill tail bursts. Inflight remains uncollected, five-second samples miss short events, clocks are not independently calibrated, and the diagnostic profile uses its own N48 traffic after scoring. All rank traces contain kernels. Native stop-profile HTTP 500 remains on all three roles in both jobs; do not call the complete job error-free merely because scored request errors are zero.

## Cost and next decision

A fresh locked ledger at 2026-10-21T03:21:52 UTC uniquely reconciles **938.098 SU** posted cost. Used is **43571.410 SU**, Balance **20428.590 SU**, In Doubt **0 SU**, no outstanding maxima, and internal headroom **7428.590 SU** under the unchanged 51000 cap / 13000 buffer. [Accounting source and proof](reconciliation-terminal.json). Balance already excludes In Doubt; no double subtraction or budget increase.

Do not buy a repeat for this sub-threshold result, widen CPU budgets, or transfer it numerically to H200. Preserve all five pending H200 positions. The next independent branch is a bounded EAGLE3 component/correctness preflight: first validate actual image interfaces and gateway token-ID forwarding, draft class/parameter loading and token-map values with minimal allocated resources. Only then consider full target/PD integration and exact greedy equality. High decode activity does not promise that speculation wins at N54; a valid short load screen must justify any later full scoring pair. No new GPU job is implied by this completed-run report. Official model accuracy remains unverified.
