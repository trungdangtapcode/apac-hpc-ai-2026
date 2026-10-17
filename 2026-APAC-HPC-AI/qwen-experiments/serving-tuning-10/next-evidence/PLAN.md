# Two prefill experiments on H200

**Goal:** improve throughput while preserving output quality and latency requirements. Jobs **24281** and **24282** have been submitted. Their results have not yet been reviewed, so neither configuration is an established improvement.

## Why investigate prompt processing?

The model serves a request in two stages:

- **Prefill** reads the prompt and prepares the state needed to generate an answer.
- **Decode** generates the answer one token at a time.

Previous measurements of the MNNVL + FlashInfer configuration show:

| Concurrent requests | Time to first token (TTFT) | Average time between tokens (ITL) |
|---:|---:|---:|
| 52 | About 634 ms | About 16.23 ms |
| 56 | About 850 ms | About 16.27 ms |
| 58 | About 991 ms | About 16.27 ms |

As load increases, **the first token takes longer to arrive, while token generation speed barely changes**. This makes prefill scheduling and parallelism worth testing.

This is a hypothesis, not a bottleneck diagnosis. TTFT also includes queuing, routing, state transfer, and delivery of the first decode token.

## Job 24281: one request per prefill batch

**Current configuration:** a prefill worker can combine multiple requests in a batch.

**Change:** limit each prefill batch to one request. Keep two prefill workers, each using four GPUs.

**Question:** does completing requests individually reduce first-token latency?

**Possible downside:** smaller batches may use the GPUs less efficiently and reduce overall throughput. Reject the change if the latency improvement does not compensate for lost goodput.

An earlier trial, job 23324, tested this batch limit with an older configuration and showed only about 0.34% improvement in one run. That trial used different routing and preceded the current decode optimizations. It does not establish whether the limit helps when combined with round-robin routing, MNNVL, and FlashInfer.

## Job 24282: one eight-GPU prefill worker

| Component | Current configuration | Job 24282 |
|---|---|---|
| Prompt processing | Two workers, four GPUs each | One worker using all eight GPUs |
| Answer generation | One worker using eight GPUs | Unchanged |
| Total allocation | 16 H200 GPUs | 16 H200 GPUs |

**Question:** does assigning more GPUs to each prompt reduce first-token latency?

**Possible downside:** removing a prefill replica reduces request-level parallelism, while a larger tensor-parallel group adds communication. Individual prompts might finish faster without improving overall throughput.

This changes the prefill parallelism and replication plan. It is not yet a validated optimization.

## How the comparison stays fair

Both experiments retain:

- **56 concurrent requests**, the same official FP8 model, and the same benchmark workload.
- **16 H200 GPUs**, with a maximum allocation of 17 minutes per job.
- The same decode configuration: TP8, EP8, MNNVL, and FlashInfer.
- The same protocol: 60 seconds of warmup, 120 seconds of measurement, and a 30-second grace period.
- The same short-output checks and 12 long-context retrieval checks.

Compare against the original N56 configuration, which measured approximately **2,670 good output tokens per second** across two runs. Job **24263** also measures the unchanged configuration before starting its profiler, providing a fresh control.

**Good output tokens per second** counts only requests that meet the latency requirements. Lower TTFT alone is not enough if goodput falls.

## Acceptance and rejection rules

1. Confirm that the job ran the intended configuration and produced a complete benchmark. A startup failure is not a completed measurement.
2. Require at least 90% of requests to satisfy both latency limits, with no request errors or cancellations.
3. Require no new short-output failures relative to the baseline, and all 12 long-context checks to pass.
4. Compare goodput, TTFT, and ITL against all relevant control runs. Preserve negative results.
5. If a configuration shows a useful improvement, plan an independent repeat before selecting it as the winner.

These output checks **do not establish compliance with the organisers' 99% reference-accuracy requirement**.

## References and evidence

- [DistServe](https://arxiv.org/abs/2401.09670v3) studies phase-specific resource allocation and parallelism. It motivates these experiments but does not predict a speedup for this model.
- [SGLang tuning guidance](https://docs.sglang.io/docs/advanced_features/hyperparameter_tuning) describes batching tradeoffs. Advice for offline throughput must not be applied blindly to a latency-constrained benchmark.
- [Prefill log observations](prefill-observations.json) show more multi-request prefill steps at higher loads. These logs mix startup, warmup, measurement, and later checks; the counts are descriptive rather than isolated causal evidence.
- [Pre-submission validation](pilot-validation.json) records changed files, shell syntax checks, and the 16-GPU placement check. It does not prove successful GPU execution.

For runtime review, job 24282 has **one prefill worker and one prefill-to-decode path**. Its reviewer must expect that layout rather than reuse a checker that requires two prefill workers.
