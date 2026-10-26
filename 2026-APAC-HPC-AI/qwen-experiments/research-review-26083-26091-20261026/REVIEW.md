# H200 routing/fusion results and incumbent configuration correction

Reviewed 26 October 2026. Full raw workload/denominator/output checks and the actual frozen head checkers were replayed. All runs use 16 H200 GPUs, N64, 4000/200 tokens, client seed 2026 and the short 20/40/30-second protocol. Official accuracy is unknown.

| Job | Good output tokens/s | Joint SLA | Delta vs fresh control | Mean / p95 TTFT, ms | Mean / p95 ITL, ms |
|---|---:|---:|---:|---:|---:|
| 26083 | 2558.14 | 94.63% | +0.000% | 1661.00 / 3024.68 | 14.411 / 14.959 |
| 26085 | 2337.35 | 89.12% | -8.631% | 1873.11 / 3431.21 | 14.243 / 15.177 |
| 26089 | 2570.51 | 94.63% | +0.484% | 1635.44 / 3078.96 | 14.413 / 14.935 |
| 26091 | 2565.12 | 94.59% | +0.273% | 1594.20 / 3050.15 | 14.727 / 15.268 |

26083 is fresh round-robin control. Power-of-two 26085 is FAILED 1:0 and genuinely misses the 90% SLA floor (62 TTFT breaches of 570, no ITL breach); its post-run failure is not a checker bug. Fusion prefill 26089 and decode 26091 are COMPLETED 0:0 and pass local runtime/geometry/semantic/output gates, but improve only 0.484%/0.273%, below the predeclared 3% threshold. Close all three exact intervention branches without unchanged full confirmation. Every profile has zero errors/cancellations, smoke 7/8 and retrieval 12/12.

Beyond score: outer-client telemetry covers sixteen disjoint GPU UUIDs, 18–19 samples per role and startup-selected transport scans. Mean sampled active-time is 69.93/66.07/63.45/69.97% and VRAM 129.55–129.69 GiB/GPU. These windows INCLUDE warmup, profiling and grace; the prior reusable audit incorrectly described its outer benchmark_start/end boundary as scoring-only. This report explicitly corrects that scope. Role queues/KV/host CPU/memory details are retained in inspection.json; they cannot establish causality or represent merged rank totals. Selected transport error patterns have zero matches, not a universal clean-log certificate. No heavy kernel profile was collected in these arms.

## Why the old configuration reached 3k

Retained full N64 jobs 25366/25373/25487 scored 3044.49/3044.07/3044.64 good output tokens/s (mean 3044.400475) at 60/120/30, not 20/40/30. But duration is NOT the only difference. Direct AST comparison of actual ServerArgs from 25487 and 26083 proves both old prefill workers used breakable CUDA graphs with max_running_requests=None; modern controls explicitly disable prefill graphs and set 64. Server dtype is auto versus explicit bfloat16; old actual KV allocations are BF16. Client seed 2026 remains fixed while internal random server seeds differ. The native transport wrapper also gained geometry instrumentation. Configuration and harness differences prevent attributing the gap to duration, warmup or graphs alone.

The earlier chat explanation that emphasized only protocol duration was incomplete and is corrected here. Do not call the accepted 3k architecture a dead end, and do not claim the graph difference caused the full gap. Reproduce the frozen legacy operational payload and compare full-protocol modern arms with graphs disabled/enabled and native versus 64 admission to isolate these questions. This is regression diagnosis and incumbent preservation, not promotion of losing fusion/router screens.

Raw logs, frozen payloads, per-request rows and resource sampling are retained under runs/26083,26085,26089,26091. Exact comparisons, independent audits and acceptance failures are in inspection.json. S68 separate component diagnostic has definite submission 26308; no result is claimed. It cannot produce an inference score.
