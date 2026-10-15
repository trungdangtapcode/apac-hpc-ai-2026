# Keep research moving while GPU queue time dominates

**Completed 2026-10-15:** control23607 measured2400.02 good tokens/s and98.93%
SLA, then collected all16 profile traces. FP8 KV23608 measured254.47 with10.75%
SLA; DeepGEMM23609 measured2021.39 with84.71% SLA. Both backend points have
zero errors/cancellations but fail the90% SLA requirement; their dependent jobs
were skipped. N54 measured2358.64, and the subsequent N53 midpoint reached
2433.41 with98.88% SLA. Repeat23773 is pending. The profile now informs
[the three submitted kernel experiments in wave7](../serving-tuning-07/PLAN.md).
The plan below records the rationale and policy at submission time.

The user explicitly requested continuous research, decisions and submission of
the next justified jobs, because GPU queue waits are long. Independent trials
are submitted immediately after CPU validation, sharing a maximum of four
queued/running account jobs. Dependent trials still require their preceding
evidence; no result or accuracy approval is inferred from elapsed time.

## Current evidence

Round-robin N52 measured 2402.64 and 2397.72 good tokens/s with approximately
98.93% SLA and zero benchmark errors/cancellations. N50 measured 2350.25,
99.04% SLA. The N54 job 23583 is already queued and is retained.
Round-robin mean ITL at N52 is approximately 19.46–19.57ms, close to the20ms gate.

The first DeepGEMM and FP8-KV pilots were measured with cache-aware routing,
before round-robin improved admission and increased sustained decode load.
Their scores do not establish their effect on the current fuller decode batch.
The retained profiler traces also describe the old cache-aware N48 diagnostic,
not the current round-robin N52 point. Summed decode kernel time there included
approximately28.1% MoE and20.7% collective kernels; these are not wall-time fractions.

## Initial independent submissions

| Job | Experiment | Single change / purpose |
|---|---|---|
| 23607 | Round-robin N52 control + profile | Full official measurement first, then separate N52 traffic and sixteen-rank GPU traces |
| 23608 | Round-robin N52 FP8 KV | E4M3 KV on both roles, retaining the dense decode graph list and original runner |
| 23609 | Round-robin N52 DeepGEMM | Decode MoE runner only; same BF16 KV, router and dense graph list |

All three frozen bundles passed actual-image CLI, shell and checksum validation.
Official benchmark/client, model, layout, router, graph list and transport patch
are retained. The profile helper runs at52 requests after the ranked measurement;
its traffic and GPU traces do not affect that score. A complete profile requires
4+4+8 nonempty rank traces from one deployment. Partial traces from separate
attempts are not combined into a completed profile. Budget-only profiling retries
retain N52 rather than silently reverting to the historical N48 profile.

## Automatic decisions after measurements

Each backend is assessed independently, without waiting for the other candidate
once its own matched control and result exist:

1. Require a full N52 benchmark with no errors/cancellations, SLA≥90% and output
   research eligibility on the same attempt.
2. If the backend improves goodput by at least2% over **both** the two-run
   original round-robin reference and the fresh control, submit an independent
   N52 repeat immediately when a queue slot opens.
3. After the repeat reproduces that improvement, require SLA≥95% and mean
   ITL≤19.3ms before submitting N54 on that backend.
4. Otherwise record the decision and skip that dependent job. A failed deploy
   is not a measured latency boundary or a successful experiment.

At most three initial jobs plus one repeat and one N54 test per promising
backend: seven deployments in this bounded wave, apart from recorded budget
retries. All share the queue cap with the older N54/midpoint/winner-replay jobs.

FP8 KV remains experimental: default scales and eight hand-written questions
cannot establish the organiser99% full-set accuracy gate. Weights remain the
official FP8 checkpoint, no format below FP8 is introduced, and no submission
promotion happens automatically. The known reverse-string failure remains wrong.

## Research prepared while these jobs wait

Use the new traces to decide whether the next intervention should target MoE,
attention or collectives. Inspect the exact image before selecting a new backend.
For example, its FP8 MoE source includes a CUTLASS path gated on block quantization
and SM90 support, which is a more relevant compatibility candidate for H200 than
blindly selecting Blackwell-oriented FlashInfer/TRT-LLM configurations. This is
a CPU/source observation, not a GPU-validated new configuration or a speedup claim.
No CUTLASS job has been submitted by this plan yet.

Primary references:
[SGLang MoE backends](https://docs.sglang.io/docs/advanced_features/expert_parallelism),
[FP8 KV formats, scaling and attention support](https://docs.sglang.io/docs/advanced_features/quantized_kv_cache).
Actual inspected source versions take precedence over newer documentation.

- [Prepared jobs and states](prepared-pilots.json)
- [Automatic follow-up policy](followup-plan.json)
- [Payload/CLI validation](cpu-validation.json)
- [Queue and profile validation](controller-validation.json)
- [Follow-up decision validation](followup-validation.json)
- [Live measurements](../SERVING_TUNING_RESULTS.md)
