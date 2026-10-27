# Smaller full-workload prefill chunks lose; 4096 fails the real SLA

| Job | Chunk | Good output tokens/s | Joint SLA | Mean / p95 TTFT (ms) | Mean / p95 request ITL (ms) | Status |
|---|---:|---:|---:|---:|---:|---|
|26319 reference|8192|2827.996286|98.424311%|1471.40 / 2222.67|14.659 / 15.287|Earlier full local pass|
|26473|6144|2661.889812|97.874852%|1712.41 / 2918.49|14.591 / 15.264|Full local pass, slower|
|26475|4096|1437.120127 diagnostic only|57.151899%|2083.93 / 3922.50|14.462 / 15.072|Real SLA failure; not score eligible|

The 6144 arm passes raw fixed N64/4000:200/seed2026/cold-prefix/full60:120:30, actual runtime/source/graph/KV/semantic and local smoke7/8 without regression/retrieval12/12. It is a lower observation, not an improvement. The comparison with the earlier reference is descriptive because deployments were not simultaneous and cluster variability is retained.

26475 is FAILED1:0 for the correct reason: the full request denominator contains1580 profiling requests and only903 meet both latency limits. There are677 TTFT breaches and zero ITL breaches. No scored errors/cancellations were reported. Raw input schema, counts and good fraction were independently replayed; smoke7/8 and retrieval12/12 still pass separately. The strict submitted gate remains failed. The raw Goodput*200 value is diagnostic only and must not be presented as an accepted contest score. No gate was weakened to accept this observation. Official full-set accuracy remains UNKNOWN.

The audit retains role queues/running/token gauges, sparse request-admission-envelope CPU/GPU/VRAM observations, actual runtime readiness and selected transport/traceback/ENOSPC scans. No hardware utilization is invented for missing samples. GPU activity is not FLOPS; VRAM is not KV token occupancy; host memory unit keys are GiB. Sparse five-second samples and uncalibrated host skew limit inference. TTFT degrades much more than ITL, consistent with a worse prefill/queue tradeoff; this does not prove a unique bottleneck. Later container extraction failures on the full g4 data volume occurred before model startup in different jobs and do not retroactively establish the cause of these scored measurements.

Close the smaller-chunk branch without repetition or promotion. New26521/26524 attempted a declared larger-batch/HPC-Ops interaction and fresh8192 control, but both failed before model startup due to Enroot ENOSPC. Those are infrastructure failures, not chunk scores. Read-only26526 confirmed local NVMe capacity and empty own stale roots. New26531/26533 use the same per-job node-local rootfs policy for the control/candidate; actual new benchmark acceptance remains unknown. No deleting other users' data, frozen-payload edit or automatic retry.

Evidence: audit.py, review-26475.json, independent full pass in h200-full-load-review-20261026/review-26473.json, raw sealed runs26473/26475 and the separate disk-audit/repair receipts. Preserve the original failures and raw data.
