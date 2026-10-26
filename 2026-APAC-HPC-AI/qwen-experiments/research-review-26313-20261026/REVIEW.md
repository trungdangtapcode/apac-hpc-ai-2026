# Legacy N64 full replay: valid local result, lower than the old cluster

Reviewed 26 October 2026. Job 26313 (S69) is terminal COMPLETED 0:0 after 11:12 on g1/g4. Independent review verifies the frozen submitted hash list, all 15 operational files byte-identical to 25487, actual native ServerArgs equal except internal random seeds, complete prefill/decode CUDA graph captures and both P/D warmup paths. The exact raw AIPerf input remains N64, 4000/200, client seed 2026, full 60/120/30 and the retained cold-prefix recipe. Raw evidence is sealed in runs/26313/artifact-manifest.json.

| Metric | Result |
|---|---:|
| Good output throughput | 2830.923547 tokens/s |
| AIPerf Goodput | 14.154617736 requests/s |
| Joint latency success | 98.427850% |
| Profiling requests | 1781 |
| Profiling errors/cancellations | 0/0 |
| Mean/p95 TTFT | 1456.226/2193.477 ms |
| Mean/p95 request ITL | 14.685/15.407 ms |
| Raw TTFT/ITL breaches | 28/0 requests |
| Output sanity/retrieval | 7/8 and 12/12 |

The independent raw denominator and response checks pass; there is no new quality certification. Official full-set 99%-reference accuracy remains UNKNOWN. The eight small sanity requests and twelve retrievals cannot replace that evaluation. Allocation corresponds to 2.9867 GPU-hours, no separate PBS SU; startup/runtime/profile time is separate from scored throughput.

## Reproduction assessment

The retained 25366/25373/25487 scores are 3044.489701/3044.074628/3044.637094, averaging 3044.400475. New 26313 is -7.012% below that frozen historical mean, despite actual runtime parity. The descriptive mean of all four repeats is 2991.031243; keep the lower observation rather than selecting only favorable runs. Today we reproduced the deployment and local protocol, not the old 3.044k rate. The prior three-run result remains historical evidence; it is not a guarantee of current service throughput or proof of a global optimum.

The earlier modern short control 26083 used different duration, disabled prefill graphs and cap 64. That runtime drift is real, but the new legacy replay shows it cannot be assumed to explain every gap. Pending full modern 26315/26317/26319 remain necessary to isolate graph and admission. Do not use the invalid inference that graph must cause the full difference, and do not call the architecture exhausted from one lower replay.

## Beyond the score

First-to-last profiling-request-start envelope contains 24 five-second hardware samples per role and sixteen distinct GPU UUIDs. Both old 25487 and new 26313 decode samples average 100% active-time, 1980 MHz SM and 3201 MHz memory clock. New prefill means 1856.09/1932.03 MHz versus old 1918.91/1911.25 MHz; power/temperature differ by role. These sparse associations do not identify a cause for the 7.01% score drop. Power-limit/throttle-reason counters, calibrated host clocks and per-dispatch traces were not collected. GPU active-time is not FLOPS; VRAM is not KV occupancy. Exact resource values/units/window limits are in resource-comparison.json; request-admission envelope excludes warmup/final drain but is not an exact phase clock.

The full review retains role-local queue/KV gauges and deduplicated host CPU/memory estimates. Selected transport error scans are retained separately from traceback counts; post-score profiling has 423 diagnostic requests and all three stop calls return HTTP 500, matching the known diagnostic limitation. Those failures occur after scoring and are not profiled serving errors. Trace files are preserved/sealed; their full kernel contents were not inspected in this review. Do not describe the whole run as error-free.

## Decision

Keep the old operational configuration available. Accept 26313 only as a valid local full observation; no new-best promotion or unchanged repeat. Preserve queued full control 26315, graph arm 26317 and admission arm 26319, plus corrected no-model component 26337. Their actual results determine the next distinct hypothesis. The queue remains occupied, so there is no justification for blindly adding another copy to replace a finished slot.

Sources: [independent full audit](../h200-incumbent-recovery-20261026/review-26313.json), [repeat series](repeat-series.json), [resource comparison](resource-comparison.json), [fresh queue](post-review-queue.json), raw runs/26313 with original payloads and separate post-score traces. No submission slides, HPC payload, PBS budget, credentials or background schedules changed.
