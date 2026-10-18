# Research review and next trials — 18 October 2026

This is a research snapshot, not an organiser submission or official accuracy certificate. All prior queued jobs finished. Frozen JSON reviews and original artifacts are retained beside this report or linked from each review.

## What improved?

The highest observed H200 result is **2,722.281 good output tokens/s**, from job **24425** at concurrency 56 with DeepGEMM prefill and an 8,192-token prefill chunk. It passes the full benchmark protocol, joint latency requirement, frozen payload and runtime checks, short-output nonregression, and all 12 long-context retrieval checks. The improvement over the independent 4,096-token control 24327 is only **0.2022%**. This is a provisional peak, not a confirmed improvement. Job 24429 provides a third 4,096-token control at **2,715.549 good tokens/s**.

Good output tokens/s means the exported rate of requests meeting both latency limits, multiplied by 200 output tokens. Larger is better. The joint requirement is first-token latency at most 3,000 ms and per-request mean inter-token latency at most 20 ms, for at least 90% of all requests, including errors in the denominator. The table reports mean latencies; means alone do not prove the joint requirement.

| H200 job | Change, concurrency 56 unless stated | Good tokens/s | Joint SLA success | Mean TTFT (ms) | Mean ITL (ms) | Decision |
|---|---|---:|---:|---:|---:|---|
| 24376 | Auto MoE, prefill graphs off | 2,530.832 | 98.435% | 1,079.94 | 16.071 | 5.22% below auto graph-on control; close branch |
| 24425 | DeepGEMM, chunk 8192, graphs on | 2,722.281 | 98.940% | 755.646 | 16.396 | Repeat against fresh control |
| 24426 | DeepGEMM, prefill graphs off | 1,590.313 | 72.721% | 1,998.40 | 15.089 | Reject: joint SLA fails |
| 24428 | DeepGEMM, chunk 4096, concurrency 54 | 2,693.158 | 98.927% | 661.670 | 16.348 | Below concurrency 56; no unchanged repeat |
| 24429 | DeepGEMM, chunk 4096, then separate profile | 2,715.549 | 98.820% | 741.425 | 16.489 | Third stable control |

All rows except 24426 pass the joint latency gate. A finished allocation is not automatically an accepted measurement. Official full-set accuracy at 99% of the reference evaluation score remains unverified for every research configuration.

## H100: prefetch saves startup time, but has no confirmed throughput gain

| H100 job | Change at concurrency 50 | Good tokens/s | Joint SLA success | Mean TTFT (ms) | Mean ITL (ms) |
|---|---|---:|---:|---:|---:|
| 221181 | Prefill graphs off | 2,211.107 | 98.414% | 563.493 | 19.243 |
| 221194 | Prefetch repeat | 2,225.562 | 98.355% | 505.395 | 19.362 |
| 221195 | Immediately following no-prefetch control | 2,238.778 | 98.643% | 486.558 | 19.400 |

All three pass local protocol, payload, runtime, latency and output checks. Graph-off loses 0.91% against fresh 221151; close this branch. The prefetch repeat loses about 0.59% against the new paired control, reversing the original small gain. The historical highest H100 observation remains **2,241.336 good tokens/s** in 221153; it is not proof of a repeatable prefetch throughput advantage.

The reversed-order repeat again shows shorter startup: 221194 walltime 12:55 with prefill loading around 150–151 seconds, versus control 221195 walltime 25:05 with loading around 898–900 seconds. Earlier prefetch/control walltimes were 15:45 / 24:51. Graph capture duration stays around 112–117 seconds. This supports using prefetch as a startup-cost candidate for the next matched pair. Cache, node and ordering effects remain confounded; these observations are not a causal estimate of guaranteed savings.

## Profile correction

The old classifier missed renamed grouped DeepGEMM kernels. Its approximately 0.8% prefill MoE fraction in 24429 is an **undercount**, not evidence that MoE computation disappeared. The corrected classifier uses the exact image's DeepGEMM enum: grouped types 1 and 2, explicit MoE kernels, and DeepGEMM pre/post reorder kernels; normal GEMM type 0 is excluded.

Applying the same corrected classifier to both raw captures gives prefill MoE-associated shares of **42.84% / 42.77%** in 24263 and **34.81% / 34.83%** in 24429. New prefill collective shares are about **24.22% / 24.13%**. Decode shares remain around 27.88% MoE and 23.91% collectives. These are fractions of summed GPU kernel durations, not wall time, causal gains, or guaranteed speedup opportunities. Capture concurrency and step counts match, but batches and shapes need not.

All 16 rank traces contain kernels; the separate diagnostic recorded 421 successful requests out of 421. It ran after scoring, at concurrency 48, with four prefill and 32 decode capture steps. The original summaries are preserved. See [corrected analysis](profile-comparison.json) and [reproducible classifier](review-profile.py).

## New trials and stopping rules

All trials retain two nodes, 16 GPUs, the complete native FP8 checkpoint, BF16 key/value cache, the existing heterogeneous-TP NIXL patch, round-robin prefill routing and full 60-second warmup / 120-second scoring / 30-second grace protocol. Keep every request. Preserve output checks and frozen hashes.

| Platform | Job | Trial | Purpose |
|---|---|---|---|
| H200 | 24526 | DeepGEMM prefill, chunk 4096, concurrency 56 | Fresh control |
| H200 | 24527 | DeepGEMM prefill, chunk 8192, concurrency 56 | Independently repeat provisional 0.20% gain |
| H200 | 24528 | DeepGEMM prefill, chunk 6144, concurrency 56 | Test intermediate batch geometry without changing load/backend |
| H200 | 24529 | HPC-Ops prefill, chunk 4096, concurrency 56 | Test alternative grouped FP8 MoE implementation; decode unchanged |
| H100 | 221262.pbs111 | Existing prefetch configuration, concurrency 50, then separate profile | Fresh score control and diagnosis; no claim of prefetch inference gain |
| H100 | 221263.pbs111 | Same prefetch configuration, HPC-Ops decode only | Isolate decode implementation; depends afterany on 221262 |

HPC-Ops is installed in the frozen image. The exact staged source supports Hopper, blockwise FP8, BF16 inputs, SiLU, 128-aligned dimensions and the selected expert-parallel partition through global expert IDs. It is primarily tuned for H20, so a gain on H100/H200 is uncertain. The model has hidden size 4096, MoE intermediate size 1536, 128 experts and top-8 routing. Selected prefill partitions have intermediate width 384 and decode partitions 1536. Both are compatible with the documented alignment. This is source compatibility, not successful GPU execution. Each changed role checks Hopper capability and the installed FP8 entry point before model loading. Actual runtime, output and latency gates remain mandatory; no unchanged retry on a backend or quality failure.

H200 HPC-Ops is compared with the fresh DeepGEMM control for practical ranking and historical auto-runner control 24320 for context. H100's comparison is the freshly scored prefetch control. Do not transfer measured gains between GPU types. A tiny or contradictory result needs replication before promotion. Close losing branches rather than increasing concurrency automatically.

For the new PBS bundles only, the diagnostic tokenizer now reads the model path from the saved configuration instead of the old Slurm-only hardcoded path. Both bundles receive the same diagnostic script. Scoring and quality scripts are byte-identical to their source. The 48-request diagnostic is separate from scoring and may be explicitly deferred if allocation time is insufficient.

## Cost and scheduler receipts

At 08:09 UTC, all four H200 receipts were verified pending for Resources. The PBS afterany link was verified from qstat. H200 cap: 17 minutes per 16-GPU allocation; four active jobs, under the existing five-job bound. PBS cap: 45 minutes per allocation, two active jobs, one 16-GPU allocation at a time.

The previous three PBS jobs charged **2,173.156 SU**, fully reconciled against the latest ledger increment. The ledger reports Used **20,655.218 SU**, Balance **43,344.782 SU**, In Doubt **0**, as of 18 October 15:40:01 SGT. The two new jobs reserve at most **3,072 SU**. Headroom under the unchanged internal 51,000 SU planning limit is **27,272.782 SU** after reservations. The 13,000 SU buffer is our planning choice, not an organiser quota. Do not deduct a reported prepayment twice.

No Codex autopilot or replacement schedule was enabled. The previous non-AI watcher exited after its prior wave finished. Its existing submission function was invoked once under its lock to submit and persist the four H200 receipts; it is not currently a running background process. No slides, official scripts or organiser upload were changed.

Evidence: next-validation.json, prepared-pilots.json, serving-tuning/registry.json, pbs-pre-submit.txt, pbs-submitted-queue.txt, and nscc-budget.json. Preserve all raw artifacts and rejected results.

At 08:13 UTC, a fresh scheduler check shows PBS 221262 running and 221263 held for its dependency. All four H200 jobs remain pending Resources. This is a dated scheduler observation, not a promise of persistent monitoring.
