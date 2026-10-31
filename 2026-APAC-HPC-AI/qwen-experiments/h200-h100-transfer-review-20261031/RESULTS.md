# H200 verification: three reviewed runs, one candidate still running

Checked 31 October 2026, Vietnam time (UTC+7). This is the owner-requested
four-job verification wave; all measurements below use **16 H200 on g1/g4**.
H100 findings selected the questions, but no H100-to-H200 multiplier is used.

| Job | Serving choice | Client concurrency | Good output tokens/s | Joint SLA pass | State |
|---|---|---:|---:|---:|---|
| 27777 | Current H200 recipe, FlashInfer decode | 64 | **3038.022907** | 1872/1898, 98.630137% | Reviewed local pass |
| 27779 | Same recipe, FA3 decode | 64 | 2999.245473 | 1848/1876, 98.507463% | Reviewed local pass; loses 1.276404% |
| 27781 | H100 recipe: HPC-Ops both phases, chunk 4096 | 54 | 2738.940099 | 1687/1705, 98.944282% | Reviewed local pass |
| 27783 | Same H100 recipe | 64 | Not yet measured/reviewed | Unknown | Running in the dated snapshot |

The current H200 recipe means two TP4/EP1 prefill workers with DeepGEMM/chunk 8192
and one TP8/EP8 decoder with HPC-Ops, MNNVL and round-robin prefill routing.
The transferred H100 recipe changes prefill to HPC-Ops/chunk 4096. Both recipes
retain FA3 prefill attention, FlashInfer decode except in 27779, the same pinned
image and FP8 target, BF16 KV, native Enroot, NIXL patch, caches, polling and
dense decode graphs 1..64. N54 is client concurrency, not a graph-capacity cap.

## FA3 shortens first-token wait but loses serving goodput

| Latency measure, ms | FlashInfer 27777 | FA3 27779 |
|---|---:|---:|
| TTFT mean / p95 | 1120.236 / 1396.041 | 1062.811 / 1287.101 |
| Request-mean ITL mean / p95 | 15.007 / 15.349 | 15.534 / 15.756 |
| Mean end-to-end request latency | 4106.549 | 4154.070 |
| Requests exceeding TTFT / ITL thresholds | 26 / 0 | 28 / 0 |

FA3 improves mean TTFT by 57.425 ms, but increases mean request ITL by 0.527 ms and
mean end-to-end latency by 47.522 ms. For a 200-token response, slower decode can
outweigh a shorter first-token wait. The measured goodput drops 1.276404%.
This is consistent with the earlier H100 tradeoff, not proof of a universal
backend ranking. Runtime argument comparison permits only the intended decode
attention change plus generated engine seeds; both prefills are unchanged apart
from seeds. Actual FA3 decode settings, full graph/rank KV, source/runtime and
both semantic P/D paths pass. No new kernel trace was collected, so the exact
kernel-level cause is not established.

**Decision:** retain FlashInfer decode and close this exact H200 FA3 candidate
without a losing repeat or default/submission promotion. The prospective gain
gate was greater than 1%; a 1.28% loss does not qualify for confirmation.

## The H100 recipe needs its same-load H200 comparison

27781 is a real full N54 measurement: TTFT mean/p95 896.156/1106.815 ms,
request-mean ITL 14.868/15.042 ms and mean end-to-end latency 3854.914 ms. It has
18 TTFT breaches, zero ITL breaches and zero scored errors/cancellations. Its
lower client concurrency also lowers the sampled decode running-request mean
to 42.4583, versus 50.0 in 27777; this is an observation, not isolated proof of
the prefill runner's effect.

Do not describe its score difference from 27777 as a one-factor recipe loss:
both load and prefill settings differ. Await 27783 at N64 to compare recipes
against 27777, and compare 27781/27783 for load sensitivity with the same recipe.
Even the N64 recipe comparison changes both runner and chunk size, so it cannot
attribute an effect to either alone. Historical H100 scores remain contextual,
not a pure hardware-speed calibration under identical native launch conditions.

## Inspection, cost and limitations

Both new terminal jobs complete 0:0: 27779 in 12:15, 27781 in 11:04. All original
raw workload, physical KV/cache/source/runtime, semantic and output gates replay
successfully. Both retain smoke 7/8 without regression and retrieval 12/12.
Official full-set accuracy remains UNKNOWN; these checks do not certify 99% of
the organiser's reference. Good output tokens/s equals exported AIPerf Goodput
requests/s times 200, with all requests in the denominator and the unchanged
TTFT <= 3000 ms / mean-request ITL <= 20 ms joint fraction >= 0.90 gate.

| Inspected sample, profiling-request-start envelope | 27779 FA3, N64 | 27781 H100 recipe, N54 |
|---|---:|---:|
| Decode GPU activity mean, % | 100.000 | 95.859 |
| Decode sampled VRAM mean, GiB/GPU | 130.321 | 130.734 |
| Decode running requests, mean / max | 52.1304 / 55 | 42.4583 / 47 |
| Decode sampled queue max | 0 | 0 |
| Decode KV token usage mean | 0.1200 | 0.0954 |
| Prefill sampled queue maxima, worker 0 / worker 1 | 20 / 18 | 3 / 21 |
| Server metric polls, successful / inspected | 71 / 71 | 72 / 72 |
| Actual allocated GPU-hours | 3.266667 | 2.951111 |

There are no selected transport/OOM error markers or Python tracebacks in any
of the three serving-role logs for these two jobs, and their semantic retry
failure files are empty. The earlier control had two pre-score setup 503 retries;
that separate fact remains preserved. Five-second role/host samples include
power, temperature, clocks, GPU memory activity and CPU estimates; distributions
were inspected and retained in the result-27779.json and result-27781.json files. The N54 decode
activity average includes boundary samples and does not establish recoverable
idle time. GPU activity, sampled VRAM and KV token usage are different metrics.
No heavy kernel profile, per-thread demand, Xid/throttle reasons or actual
generated token IDs were collected. Host clocks are uncalibrated and final-drain
coverage is excluded by the first-to-last request-start envelope.

These are single runs; unmeasured host/cache state and generated engine seeds
limit causal or statistical claims. No winner is promoted. Keep the admitted
27783 position; no duplicate fifth job or broad research restart is justified
by these results. H100/PBS spending, authentication, HPC payloads, presentation
and submission materials remain untouched.

Each reviewed raw run is sealed with its frozen payload, requests, exports,
synthetic inputs, telemetry and terminal scheduler proof. Git preservation
includes recovery manifests; large external objects are not uploaded by Git.

Evidence: [27779 extended review](result-27779.json),
[27781 extended review](result-27781.json),
[27777 control](../h200-h100-attention-transfer-20261031/CONTROL_RESULTS-27777.md),
[source recipe and admission](../h200-h100-incumbent-transfer-20261031/PLAN.md).
