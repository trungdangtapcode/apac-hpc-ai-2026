# Current candidate comparison by metric

Scope: recent reviewed H200 prefill candidates at concurrency 56, plus the held-out combo control at concurrency 50; and the latest fully reviewed H100 combo sweep (job 221058). This is a comparison of current candidates, not an exhaustive all-history latency record. Concurrency differs where stated, so lower latency does not establish a better backend.

Good tokens/s and joint SLA pass percentage should increase. Mean time to first token (TTFT) and mean inter-token latency (ITL) should decrease. SLA is measured per request with errors in the denominator; passing average latency alone is insufficient.

| Platform | Job | Concurrent requests | Good tokens/s | Mean TTFT (ms) | Mean ITL (ms) | Joint SLA pass (%) |
|---|---|---:|---:|---:|---:|---:|
| H200 | 24291 | 56 | 2715.842 | 749.053 | 16.446 | 98.8194 |
| H200 | 24263 | 56 | 2667.465 | 856.622 | 16.257 | 98.7995 |
| H200 | 24281 | 56 | 2621.292 | 936.611 | 16.190 | 98.7805 |
| H200 | 24272 | 50 | 2601.629 | 505.178 | 16.367 | 99.1326 |
| H100 | 221058.pbs111 | 48 | 2197.808 | 393.890 | 19.410 | 98.7627 |
| H100 | 221058.pbs111 | 50 | 2229.827 | 508.568 | 19.358 | 98.5684 |
| H100 | 221058.pbs111 | 52 | 2215.673 | 700.291 | 19.230 | 97.7857 |

At the same H200 concurrency 56, prefill DeepGEMM wins observed goodput, TTFT and joint SLA fraction among these three runs. Limiting prefill batching to one request wins mean ITL but loses goodput and worsens TTFT. The DeepGEMM gain needs independent replication (job 24327 is pending); small SLA differences are descriptive, not statistically established superiority.

For the latest H100 sweep, concurrency 50 wins goodput; concurrency 48 wins TTFT and SLA fraction; concurrency 52 wins mean ITL. Changing concurrency is changing workload pressure, not demonstrating a backend speedup. Goodput is the optimisation objective subject to the latency and quality constraints.

No new organiser accuracy result is available. Short output non-regression and 12-case long diagnostics do not establish 99% of the official reference accuracy. Cross-platform metrics remain separate; no H100-to-H200 conversion is applied.
