# What we inspect beyond the contest score

## Honest coverage answer

We inspect more than goodput, TTFT and ITL, but have **not provided complete, uniform resource inspection for every historical job**. Frozen payload/runtime checks, request-level latency/error/output gates and costs are systematic in recent full-model reviews. Kernel profiles, CPU timelines and source-backed activation checks exist on selected diagnostic runs. Continuous GPU utilization/power/VRAM and uniformly aligned server queue/CPU/network telemetry are a gap in the six inspected H200 deployments. Retaining raw artifacts is not the same as having analysed every field.

This review adds an offline extended inspection for six already accepted H200 runs. It verifies 30 raw file hashes against terminal manifests and verifies the manifests against accepted reviews. It launches no GPU allocation or benchmark traffic and makes no new live scheduler or budget claim. [Program](inspect-run.py), [validation](inspection-validation.json).

## Coverage by evidence type

| Evidence | Existing practice and actual use | Remaining gap |
|---|---|---|
| Per-request outcomes | Raw durations, errors, input/output lengths, joint SLA and local output checks feed acceptance | Most user summaries emphasised means; tail and concurrency distributions should be explicit |
| Actual runtime | Frozen payload hashes, ServerArgs, KV dtype, runner/attention/MNNVL rank evidence | Activation checks must follow actual pinned implementation, as shown by the NCCL correction |
| GPU work | Selected sealed per-rank GPU traces; named MoE, attention and collective costs drove microbenchmarks | Kernel-time sums are not sampled utilization, occupancy, bandwidth or end-to-end bottleneck shares |
| Host and launch overhead | Selected CPU/CUDA timeline, scheduler annotations and kernel interval coverage motivated phase-mode tests | Not equivalent to continuous CPU utilisation or proof of CPU limitation |
| Server state | Existing logs contain batch size, running/waiting/inflight requests, KV token usage, allocation and warnings | Extended extraction was missing from the standard per-run report; sparse whole-run logs mix phases |
| GPU hardware | These six exports configure no telemetry endpoints; launchers contain no dedicated nvidia-smi sampler | Per-GPU utilization, sampled VRAM, power, temperature, clocks, throttling and links unavailable in this review |
| Cost and allocation | PBS walltime/SU bounds and published-charge reconciliation; scheduler exit vs cleanup distinguished | Accounting snapshots cannot replace phase-aligned hardware measurements |

Selected earlier examples: [H200 interaction profile](../research-followup-20261020-0028/H200_PROFILE.md), [H100 CPU/GPU timeline and hypothesis](../research-followup-20261019-1720/RESULTS.md), [NCCL interpretation correction](../status-review-20261019-1755/CORRECTION.md), [collective timing refinement](../research-followup-20261020-collective-graph/RESULTS.md).

## What the new inspection actually finds

| H200 job | TTFT mean, ms | TTFT p99, ms | ITL p99, ms |
|---|---:|---:|---:|
| [24733](runs/24733.md) | 872.182 | 3445.347 | 17.721 |
| [24736](runs/24736.md) | 801.591 | 3211.967 | 17.470 |
| [24737](runs/24737.md) | 881.274 | 3198.448 | 16.064 |
| [24738](runs/24738.md) | 947.652 | 3230.452 | 15.720 |
| [24819](runs/24819.md) | 880.109 | 3203.812 | 16.046 |
| [24912](runs/24912.md) | 822.292 | 3282.130 | 17.567 |

All six have TTFT p99 above 3000 ms, while the existing joint pass fractions remain above 90%. That is compatible with the scoring rule: p99 is a separate tail diagnostic, not an additional contest requirement. The new finding does not invalidate accepted local scores. For 24738, TTFT mean is 947.652 ms, p99 3230.452 ms and maximum 4514.917 ms; ITL p99 is 15.720 ms. The slower first-token tail deserves investigation even as decode improves.

For 24738, full-deployment sparse logs show decode running requests p50/p95/max 51/53/54 and zero sampled decode queue; prefill queue p95/max 2/24 on both workers. Logged decode KV token usage p95/max is 0.11. These values include warmup and output checks and are event-sampled, not scored-phase time averages. They motivate checking prefill/router/inflight timing rather than declaring the decode queue saturated. They **do not prove** the cause of the TTFT tail or that KV/VRAM capacity can be reduced safely. Reported allocated KV buffers and token occupancy are distinct from measured total VRAM. No CUDA-out-of-memory or CUDA-error phrase was found in the inspected worker/router logs; that narrow text result is not a complete hardware health assessment.

### Error triage uncovered a profiler-control defect

For 24738, error-severity matches in worker/router tails are Slurm step cancellation/cleanup messages after scored work, consistent with the accepted terminal review. In 24819, the server additionally logs `/stop_profile` HTTP 500 with `RuntimeError: Profiling is not in progress. Call /start_profile first.` The profile-control artifact has three start JSON parsing errors and three stop HTTP errors. These are separate from the 425/425 successful diagnostic generation requests and the accepted benchmark score. All 16 rank traces are present and sealed, so recorded-kernel analysis remains possible; the instrumentation control flow must not be described as clean.

The profiler helper unconditionally decoded every successful response as JSON. A successful empty/plain-text start response therefore caused a false parser error. Prepared a narrowly derived [HTTP handling fix](../profile-http-fix-20261020/PLAN.md) for future bundles and validated it against real local HTTP empty/text/JSON/500 fixtures. Generation JSON validation and non-2xx failure handling remain strict. Frozen submitted scripts, old traces and queued jobs are unchanged. The fix is prepared, **not deployed or GPU-validated**. Any stop failure remains visible and must be assessed alongside actual traces; no blanket suppression of HTTP 500.

## Standard for the next completed-run review

Every completed-run review should state what was **collected**, what was **inspected**, the finding, its limitation and the next hypothesis. Missing evidence must say `not collected` or `not inspected`, not zero or healthy.

1. Keep full contest/output/runtime acceptance and resource-cost checks.
2. Show TTFT/ITL/e2e p50/p95/p99/max, errors and effective concurrency, alongside joint SLA and goodput.
3. Summarise role-specific batch/running/waiting/inflight/retraction and KV allocation/occupancy samples, clearly separating warmup, scored traffic, checks and diagnostics where timestamps permit. Never silently mix phases.
4. Triage warnings, tracebacks, OOM, transport/timeouts, retries and cleanup. Link exact raw files and line references; do not equate log severity counts to failed scored requests.
5. For future derived benchmark bundles, add bounded low-overhead per-node/per-GPU hardware samples and UTC/monotonic phase markers: utilization percent, VRAM MiB, memory activity, W, degrees C, MHz and available throttling/error indicators; CPU/RAM and network counters where supported. Map GPU UUIDs to roles. Unsupported fields remain N/A. Align phases before interpreting them. These collectors are **not yet implemented/deployed by this audit**.
6. Validate the installed SGLang metrics interface before enabling/scraping server counters. The inspected runtime logs have `enable_metrics=False`; a router Prometheus port alone is not proof that worker counters were captured. Keep telemetry settings identical between control/candidate and check monitoring overhead before comparing new scores with old ones.
7. Keep heavy per-rank CPU/GPU traces short and outside ranked scoring. Inspect overlap/gaps, kernels and communication with their limits; select a distinct hypothesis and a falsification criterion before spending credit.

Existing jobs retain their frozen payloads; no cancel/resubmit or automatic job series is authorised by this review. During subsequent authorised research, use these findings to improve the next derived bundles. No claim changes official accuracy, platform ranking, slides or background Codex policy.

## Metric definitions and primary sources

GPU utilization from nvidia-smi describes time with at least one kernel executing during its sample period; 100% does not prove peak FLOP/s or efficient service. Memory utilization describes memory activity, not occupied VRAM or a measured percentage of peak HBM bandwidth. Use sampled VRAM separately, and avoid predicting goodput from either number alone. [NVIDIA nvidia-smi reference](https://docs.nvidia.com/deploy/nvidia-smi/index.html), [NVIDIA query definitions](https://nvidia.custhelp.com/app/answers/detail/a_id/3751).

SGLang exposes service metrics when enabled; the exact installed source must determine available names and their meaning. [SGLang observability documentation](https://docs.sglang.ai/advanced_features/observability.html), [upstream metric collector](https://github.com/sgl-project/sglang/blob/main/python/sglang/srt/observability/metrics_collector.py). Upstream is not a claim that all those counters exist or were enabled in the pinned contest image.
