# 20 October 2026: inspect beyond the ranked score

## Question and evidence

The user asked whether each run is inspected for utilization, resource usage, logs and insights instead of only the contest metrics. The honest answer is partial: recent acceptance reviews inspect raw requests, errors, output, protocol/runtime and costs, and selected diagnostics already drove hypotheses from GPU kernels and CPU/CUDA timelines. Continuous hardware telemetry and a uniform per-run resource narrative were missing. Retained artifacts are not proof that every field was analysed.

## Change and observations

Added an offline sealed-artifact inspector and six extended H200 reports for 24733/24736/24737/24738/24819/24912. Thirty raw hashes match accepted terminal manifests. Reports include latency/concurrency distributions, role batch/queue/KV samples, issue counts and explicit missing-data fields. No GPU work or benchmark traffic was launched; this is not a fresh scheduler or credit snapshot.

All six TTFT p99 values exceed 3000 ms, despite locally passing the required joint fraction. For the new individual peak 24738, mean TTFT is 947.652 ms, p99 3230.452 ms, ITL p99 15.720 ms. Whole-deployment sparse logs show prefill queue peaks 24 and no sampled decode queue, with decode running requests p50/p95/max 51/53/54 and KV token occupancy p95/max 0.11. The samples mix phases and do not establish what caused the slow first-token tail. AIPerf has no configured telemetry endpoints in these six runs; missing GPU utilization, sampled VRAM, power and link data remain unknown, not zero.

## Error triage, correction and fix

24819 additionally exposes an instrumentation defect: all three start-profile endpoints logged HTTP 200, but the helper tried decoding their non-JSON responses as JSON and recorded parse errors. Stop calls later returned HTTP 500 with `Profiling is not in progress`. Sixteen sealed rank traces and 425/425 successful diagnostic generation requests remain available, separately from the accepted score. The controller flow was not clean; do not infer that all errors were worker cleanup or silently discard the stop failures.

Prepared a derived profile HTTP fix for future bundles: record successful empty/text control responses without requiring JSON, keep generation JSON and HTTP failure handling strict. Six local HTTP fixture checks pass. It is not deployed or GPU-validated; frozen queued/running payloads and historical evidence stay unchanged. This fixes the false start parsing, not an asserted root cause of every stop failure.

## Assessment and next decision

Prioritise explaining the first-token tail and phase-specific queue/inflight behaviour using aligned measurements. Do not equate logged token occupancy with VRAM, GPU activity with peak efficiency, or summed kernels with wall-time shares. Add a collected/inspected/finding/limit/next-decision section to every completed-run review; explicitly mark unavailable evidence. Future derived control/candidate bundles should use matched bounded hardware/server telemetry and phase markers after interface and overhead validation. These collectors were not implemented or deployed in this audit. Keep expensive traces outside ranked scoring and preserve all failures.

[Extended report, coverage matrix, six results and primary references](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/observability-review-20261020/REPORT.md). [Prepared profiler fix and local checks](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/profile-http-fix-20261020/PLAN.md).
