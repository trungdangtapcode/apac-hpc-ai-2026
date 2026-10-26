# Four full H200 graph/admission arms: useful controls, no material gain

The question was whether prefill CUDA graph and admission drift explained the newer lower measurements. Four ordered deployments used the same modern full N64 protocol: 60 s warmup, 120 s measurement, 30 s grace, fixed 4000/200 tokens, seed 2026 and cold prefixes. All pass independently replayed raw workload, SLA/error denominator, actual runtime/graph/source/geometry, two semantic routes, smoke 7/8 without regression and retrieval 12/12. Official full-set 99%-reference accuracy remains unknown.

| Job | Prefill graph | Admission cap | Good tokens/s | Joint SLA | Mean / p95 TTFT (ms) | Mean / p95 request ITL (ms) |
|---|---|---|---:|---:|---:|---:|
|26315|Disabled|64|2807.325653|98.248588%|1515.92 / 2203.19|14.534 / 15.008|
|26317|Breakable|64|2829.604300|98.426966%|1460.60 / 2228.77|14.674 / 15.414|
|26319|Breakable|Native|2827.996286|98.424311%|1471.40 / 2222.67|14.659 / 15.287|
|26347|Disabled|Native|2802.498990|98.247598%|1523.32 / 2219.74|14.526 / 14.994|

Every score equals raw AIPerf Goodput in requests/s multiplied by 200. Every profiling request is retained; all arms have zero request errors/cancellations. The graph contrast is +0.793590% at cap 64 and +0.909806% at native admission. Removing the cap changes score by -0.171931% with graphs disabled and -0.056828% with graphs enabled. None clears the prospective >1% useful-gain gate. Close the graph/admission tuning branch; no confirmation of a subthreshold favorable peak. Breakable/native remains available as the recovered full-runtime control, not a newly proven winner.

This is one unrandomized deployment per cell. Internal server seeds differ, host skew is uncalibrated and run order can confound comparisons. Actual ServerArgs differ only in internal seed and declared graph/admission fields; the graph backend appears in both cuda_graph_config and cuda_graph_backend_prefill. We verified both representations rather than silently ignoring other runtime drift. No significance, confidence interval or complete causal explanation is claimed. The historical 3.044k cluster has not been reproduced today.

## Observability and limits

Each independent review retains raw TTFT/ITL breaches, role-local queue/running/token gauges, first-to-last profiling-request-start envelope CPU/GPU samples and selected transport/traceback scans. The JSON has the per-role evidence and counts for every arm. Missing sampling is not zero utilization. Decode is near continuous sampled activity, but that is not FLOPS or proof of a specific bottleneck. Prefill queues are asymmetric in some snapshots; this is not by itself a routing diagnosis. Allocated VRAM is distinct from token occupancy. Heavy profiles were disabled for these modern arms; there is no hidden heavy-profile score intervention. Host memory unit keys are corrected to GiB; original raw KiB bytes are unchanged.

Jobs 26317, 26319 and 26347 completed 0:0 after 10:08, 11:12 and 10:07 respectively. Their allocated costs are approximately 2.7022, 2.9867 and 2.6978 GPU-hours, with no PBS SU. Full terminal raw artifacts are sealed with SHA256 manifests. Large retained objects may live in the sibling external artifact store; GitHub push does not upload that store.

## Next decision

New jobs 26436 (N62) and 26438 (N66) now bracket the full native N64 runtime, changing only client load and worker count. Earlier losing N66–N70 short graph-disabled/cap64 runs remain retained; the new protocol is explicitly different. Review these two actual outcomes before widening or confirming. Keep quality, response, runtime, fixed-workload, raw denominator and prospective >1% useful-gain gates. No package or slide promotion follows from these controls.

Separately, component 26337 passes small NIXL writes and destination integrity on all 16 H200s. It does not prove SGLang model bootstrap, production KV layout or a serving score. [Component review](../research-review-26337-20261026/REVIEW.md). Do not relaunch the old failed full topology merely because the component passes.

Evidence: [reproducible audit](audit.py), [all metrics, contrasts, actual runtime differences and resource observations](factorial.json), the independent per-job review JSON in h200-incumbent-recovery-20261026, and sealed runs/26317, runs/26319 and runs/26347. No HPC queues/payloads/budget, submission or background schedule changed.
