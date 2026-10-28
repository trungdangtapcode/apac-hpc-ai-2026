# H200 S97 prefill MNNVL result

Date: 28 October 2026. Job 27138 completed successfully (`COMPLETED 0:0`) in 11:38 on H200 nodes g1 and g4. It used the full N64 4000-input/200-output workload, seed 2026, and 60/120/30 second warmup/measure/drain protocol. The matched fresh control is job 26949.

## Performance and gates

| Job | Prefill collective | Good output tokens/s | Joint SLA | Mean / p95 TTFT (ms) | Mean / p95 ITL (ms) |
|---|---|---:|---:|---:|---:|
|26949 matched control|trtllm (actual startup logs)|3034.761104|98.627968%|1128.133 / 1423.391|14.979 / 15.147|
|27138 candidate|MNNVL (actual rank startup logs)|3038.093484|98.526316%|1117.599 / 1340.118|14.994 / 15.161|

The candidate is +0.109807% versus control, below the predeclared >1% useful-gain threshold. Close this unchanged prefill-collective branch; the single run does not support promotion or a causal speedup claim.

The full local gate passed: 1,900 requests, zero errors/cancellations, 7/8 smoke checks with no regression, 12/12 retrieval checks, and two semantic P/D route checks. There were 28 TTFT breaches above 3000 ms and zero ITL breaches above 20 ms; 98.526316% of requests met the joint SLA, above the unchanged 90% gate. Official full-set accuracy remains UNKNOWN.

## Runtime, geometry and output evidence

The frozen candidate requests `prefill_allreduce_fusion_backend=mnnvl`. In actual startup logs, each of prefill-0 and prefill-1 reports FlashInfer AllReduce Fusion initialized with backend `mnnvl`, world size 4, max token count 2048 and hidden dimension 4096 for ranks 0, 1, 2 and 3. Each role's log has two initialization batches, and all eight rank/batch combinations report MNNVL. The matched control's corresponding startup logs resolve to `trtllm` on all four ranks of both prefill roles. Attention remained FA3. Decode stayed on FlashInfer with full CUDA graphs for batch sizes 1–64; prefill retained breakable graphs and chunk size 8192. P8-TP4 / D8-TP8-EP8, model/runtime/image, NIXL hashes and workload inputs match the control.

The native runtime readiness review passed across two four-rank prefill workers and the eight-rank decode worker. Actual role logs contain no selected NIXL/transport errors or tracebacks. The KV geometry validator passed 32 per-rank receipts across 16 ranks: for prefill it observed 188 BF16 one-token KV regions per rank, with four total KV heads across TP4. Explicit semantic layer identity was not collected, so layer order is unproven; decoder D-head counts remain unknown rather than inferred.

Raw output is retained under `runs/27138/confirm/n64/artifacts/`. AIPerf reports 15.190467 good requests/s, which multiplied by the fixed 200 output tokens yields 3038.093484 good output tokens/s. The exact latency and denominator data are in `review-27138.json` and `comparison.json`.

Telemetry includes 24 five-second samples per host and role in the profiling request-start envelope: mean sampled all-role GPU activity 97.734%, sampled VRAM 131.008 GiB, host estimated CPU busy 12.57% (g1) and 13.26% (g4), and role-local queue/running/KV-token gauges. The decode queue mean/max was 0/0 and running requests averaged 49.7083; prefill-0 queue mean/max was 0.3333/2 and running mean 2.9583; prefill-1 queue mean/max was 0.2083/1 and running mean 2.6667. These are sparse sampled observations, not exact phase clocks, omit warmup/final drain, and have uncalibrated host clock skew. GPU activity is not FLOPS, VRAM is not KV occupancy, and these aggregates do not prove a cause for the small throughput difference.

## Frozen evidence and seal

All entries in `runs/27138/submitted-payload/SHA256SUMS` verify unchanged. The immutable payload checksum file SHA-256 is `160e18472a004d52a92f033c6d6ac1653ba8a6fa2c9db03dc3d509aa57c59a41`; the run config SHA-256 is `3f3875fb9d09aa93d2b481455e8d0b1ce1d14cad459f577faec85cfde4659308`. Terminal scheduler accounting and a verified SHA-256 artifact manifest now cover the raw run directory plus `runs/27138.out` and `runs/27138.err`. The frozen submitted payload was not edited.

Evidence files in this review directory:

- `RESULTS.md`
- `comparison.json`
- `review-27138.json`

The raw capture paths are `qwen-experiments/runs/27138/`, `qwen-experiments/runs/27138.out`, and `qwen-experiments/runs/27138.err`, including the added `scheduler-accounting.psv` and `artifact-manifest.json`. No run ledger, shared notes, submission, other track files, source files, or jobs were changed.
