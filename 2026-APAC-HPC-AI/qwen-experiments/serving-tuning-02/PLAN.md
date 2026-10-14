# Qwen improvement wave 2 — standalone N52 and backend pilots

The previous wave finished eight jobs and twelve full measurements. Its highest
single point was job 23114: chunk 4096, N52, 2140.10 good tokens/s and 98.81% SLA.
That point followed an N48 benchmark in the same deployment. The original N52
control also varied from 2096.88 to 1986.39 across deployments. This wave measures
N52 directly after deployment to check reproducibility and isolate improvements.

## Initial standalone results

| Job | Candidate | Good tokens/s | SLA | Versus standalone control |
|---|---|---:|---:|---:|
| 23128 | Control, original chunk 8192 | 1977.08 | 97.14% | — |
| 23129 | Chunk 4096 | 2033.03 | 97.39% | +2.83% |
| 23130 | Chunk 4096 + dense decode graphs | 2078.96 | 97.43% | +5.15% |
| 23131 | Chunk 16384 | 1741.20 | 90.92% | −11.93% |

All four full N52 measurements completed with zero benchmark errors/cancellations.
Each output smoke suite scored 7/8, failing only the reverse-string case.
The combined chunk/graph configuration is the best standalone candidate, pending
an independent repeat. The earlier 2140.10 peak is not used as its expected score.

Each job uses the same sixteen H200 GPUs, TP4 prefill → TP8/EP8 decode, official
FP8 checkpoint, request-scoped NIXL patch and unchanged 60/120/30 client protocol.
There is exactly one ranked N52 benchmark per deployment. Eight hand-written
output sanity requests run afterwards, with full responses saved separately.
Those sanity cases do not establish the organiser's 99% accuracy gate.

## Output anomaly investigation

The standalone control 23128 measured 1977.08 good tokens/s, 97.14% SLA and no
benchmark errors, but passed only seven of eight output sanity cases. The failed
reverse-string answer contains extra text; it remains a failure. Job **23146**
runs three unmodified monolithic deployments (two TP4/EP1, one TP8/EP8), without
NIXL transfer. It records 132 requests: the unchanged short cases repeated
sequentially and concurrently, plus long-context retrieval cases. This diagnostic
does not enter the performance ranking or satisfy the organiser accuracy gate.
Job 23146 completed: 120/132 answers pass, with no transport error. All twelve
reverse-string attempts fail on the unmodified monolithic deployments too;
the other cases, including all 36 long-context retrieval requests, pass.
The failure is therefore not exclusive to NIXL. Numerical and batching
differences mean this is not proof of patched-model correctness.

[Diagnostic status and raw-response links](OUTPUT_DIAGNOSTIC.md).
The controller counts this independent job towards the four-job account limit.

## Continuation submitted on 14 October

| Job | Experiment |
|---|---|
| 23264 | Matched DeepGEMM control |
| 23265 | FP8 KV pilot |
| 23266 | Independent repeat of chunk 4096 + dense decode graphs (23130) |
| 23267 | Independent repeat of chunk 4096 (23129) |

DeepEP awaits the measured DeepGEMM control and its output research eligibility.
[Standalone assessment](STANDALONE_ASSESSMENT.md) explains why the earlier
2140.10 peak is not treated as a stable score.

## Prepared pilots with automatic submission gates

| Candidate | Matched control | Change |
|---|---|---|
| s2-deepgemm-control-n52 | 23129 / chunk 4096 | DeepGEMM runner, coarse decode graph cap 64 |
| s2-deepep-ll-n52 | New DeepGEMM control | DeepEP low-latency dispatch/combine with explicit FP8 dispatch; same TP8/EP8 and BF16 KV |
| s2-fp8-kv-n52 | 23129 / chunk 4096 | FP8 E4M3 KV on both prefill and decode |

At most four jobs are pending/running for the account. A pilot is submitted only
after its matched control has a passing full N52 run and complete output evidence
on the same attempt. Initially, the 8/8 requirement skipped the pilots and repeats.
After independent baseline job 23146, the research gate allows either 8/8 or the
unchanged eight cases with no request errors and no newly failed case versus
that baseline. The only permitted known baseline failure is the reverse-string
case, verified in twelve baseline attempts; new failures block follow-ups.
The candidate's recorded score remains 7/8 and organiser accuracy stays unverified.
This change permits experiments, not submission promotion. The previous decisions
are archived in `backend-pilots.before-baseline-gate-2026-10-14.json`.

DeepEP therefore has a measured matching compute backend
instead of conflating runner and communication changes. Its graph cap 64 is
shared with the new DeepGEMM control and fits the N52 workload. Expert count,
expert selection and the sixteen-GPU P/D layout are retained.

The actual staged image contains DeepEP 1.2.1 and its CUDA 13/NVSHMEM binary.
The Qwen3 model uses scattered MoE inputs when an all-to-all backend is selected,
without requiring a new attention-DP layout for this pilot. The DeepGEMM
low-latency adapter expects FP8 activations/scales, so dispatch dtype is explicitly
FP8; INT8/FP4 is not selected. Library/source inspection is not GPU validation.

The actual FA3 attention code supports explicit FP8 KV for head dimension 128.
The checkpoint index has no KV scale tensors, so output quality needs evaluation;
unit/default scales are not a proof of acceptable accuracy. The NIXL patch was
checked against the original transfer geometry in 720 FP8-head-byte cases and
720 BF16-head-byte cases, without modifying the previous proof or GPU run data.
GPU transport, actual runtime dtype and output quality still require the pilots.

## Repeats and results

After the four initial standalone jobs finish, the controller selects the best
two passing candidates eligible under the research output gate and submits independent
N52 repeats. Only those four BF16 scheduling configurations are eligible for
this selection; an FP8/DeepEP benchmark is not promoted from speed alone.
The scope is bounded: four initial jobs, up to three guarded backend pilots,
and up to two repeats, plus explicitly tracked time-budget retries.

The controller records failed or skipped pilots as such. No export or a
cancelled/incomplete benchmark never counts as a completed measurement.
It propagates a failed control to dependent pilots rather than waiting forever.
It does not change the submitted scripts or slides automatically.

- [Live results](../SERVING_TUNING_RESULTS.md)
- [All job registry](../serving-tuning/registry.json)
- [Prepared backend plan](backend-pilots.json)
- [Initial payload validation](cpu-validation.json)
- [Controller validation](controller-validation.json)
- [FP8 geometry proof](geometry-headbytes-128.json)
- [Inspected source provenance](inspection/manifest.json)

References: [SGLang expert parallelism](https://docs.sglang.io/docs/advanced_features/expert_parallelism),
[quantized KV cache](https://docs.sglang.io/docs/advanced_features/quantized_kv_cache),
[PD serving](https://docs.sglang.io/docs/advanced_features/pd_disaggregation).
Compatibility decisions use the code extracted from the actual staged image.
