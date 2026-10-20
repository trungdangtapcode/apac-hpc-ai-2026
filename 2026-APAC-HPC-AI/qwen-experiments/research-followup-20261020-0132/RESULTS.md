# Repeat confirmation and decode-attention review — 20 October 2026

## H200 N60 treatment independently repeats

Job **24913** passes the complete local sealed-payload, raw protocol, joint SLA, runtime and short/12-long output checks: **2989.174711 good output tokens/s**, joint SLA fraction **0.988178399**, mean TTFT **947.627300 ms**, mean ITL **14.934353 ms**. It differs by only −0.033% from 24738 = 2990.150791. Against the fresh same-load auto control 24912 = 2838.852531, the new treatment is **+5.295%**. The DeepGEMM prefill chunk8192 + HPC-Ops decode interaction is now repeated at both N58 and N60. This is locally reproducible serving evidence, not proof of official accuracy or a global optimum.

[Full acceptance](24913-review.json), [extended latency/log inspection](inspection/24913.md). Sparse log/queue/KV samples mix phases; no sampled GPU utilization or VRAM is retroactively claimed. At 01:32 UTC H200 24914 was running and 24915 Resources-pending. Preserve both positions and compare their matched N62 results before increasing load.

## H100 FA3 trades faster first token for slower decode and lower goodput

| Job | Decode attention | Good output tokens/s | Joint SLA fraction | Mean TTFT ms | Mean ITL ms |
|---|---|---:|---:|---:|---:|
| 222027 | Fresh FlashInfer control | 2420.945479 | 0.985497693 | 713.198502 | 18.214406 |
| 222028 | FA3 candidate | 2401.283565 | 0.985372340 | 594.276232 | 18.987684 |

Both pass all local protocol, frozen payload, runtime and output checks. FA3 is approximately **−0.812%** in goodput; mean TTFT falls 118.922 ms, while mean ITL rises 0.773 ms. Keep FlashInfer for this tested H100 N54 deployment and close this tested candidate without an unchanged repeat. The lower TTFT is retained as a tradeoff rather than advertised as a new throughput improvement. The highest H100 individual observation remains 221590 = 2430.891; no cross-platform score pooling.

The first review erroneously required a hybrid-backend log line even when both attention phases resolve to FA3. That is a reviewer assumption, not a failed deployment. Corrected the gate using resolved arguments and sealed per-rank decode traces: all eight decode ranks execute `flash::FlashAttnFwdSm90` kernels. MNNVL activation, HPC-Ops preflights and unchanged default grad mode are verified independently. [Corrected reviewer](review-pbs.py), [FA3 rank evidence](candidate-fa3-kernels.json). A kernel name alone is not the proof: payload, runtime arguments, actual traces and output gates agree.

The phase-specific inference-mode, forced one-shot and PDL-off branches stay closed. Do not blindly retry the earlier losing single-request prefill cap. A new native scheduler receive-poll interval hypothesis is justified by the actual pinned disaggregated receiver source and prior CPU/CUDA observations; it still requires a matched control and cannot be declared CPU limited from kernel gaps.

## Credit reconciliation

Published at **20 October 09:20:07 SGT**: Used **34972.443 SU**, Balance **29027.557 SU**, In Doubt zero. Four completed micro/model charges match the **937.244-SU** delta, releasing all corresponding maximum reserves. Headroom before new submissions is **16027.557 SU** under the unchanged 51000-SU internal cap and 13000-SU project buffer. [Exact walltime charges](reconciliation.json). These are actual allocated-wall estimates reconciled to publication, not maximum reservations. PBS queue was empty at 01:32 UTC; existing VPN/SSH was reused without authentication.

## Next decision

Prepare bounded matched runs on both clusters: an observer-off baseline, observer-on control and observer-on decode scheduler receive interval 2 candidate. Keep N60 on H200 and N54 on H100; do not change checkpoint precision, transport, request/output work or numerical kernels. The observer-off/on pair measures instrumentation overhead. Add bounded low-rate hardware/server samples and phase markers, deploy the prepared profile response fix only through new derived bundles, and preserve old payloads. Rank candidate against its fresh equally instrumented control; repeat a useful improvement and retain all latency/error/output/runtime gates. Heavy traces stay after scoring. No official accuracy or promotion claim.

## Further completed control and extended inspection

H200 **24914**, the fresh auto-decode N62 control, passes complete local gates at **2890.877695 good output tokens/s**, joint fraction **0.986747653**, mean TTFT **877.242592 ms**, mean ITL **16.601046 ms**. It closely repeats older auto N62 24733 = 2890.551. The HPC-Ops N62 treatment **24915** remains pending at the latest queue check, so do not attribute a new N62 treatment gain. [Review](24914-review.json), [extended inspection](inspection/24914.md).

H100 raw scored request inspection confirms **222027: 1517 requests, 1495 joint-good; 222028: 1504 requests, 1482 joint-good**. Each has exactly **22 TTFT breaches**, zero mean-request ITL breaches above 20 ms and zero request errors/cancellations. TTFT p99 is **3454.130/3472.798 ms**; ITL p99 **19.036/19.648 ms**. The candidate's lower mean TTFT did not remove its slow first-token tail, and slower ITL reduced serving goodput even while remaining within the ITL limit. The SLA applies to each request's mean ITL, not every individual token gap.

All **16 sealed traces per job** were inspected with CPU/CUDA/annotation data. Separate N48 diagnostic traffic succeeded **352/352** for control and **373/373** for FA3. Decode recorded-kernel interval coverage is **95.49–95.62% / 95.85–95.93%** across ranks. CPU annotations include batch-result processing, scheduler.run_batch and Gloo operations; candidate rank 0 also records scheduler.recv_requests. Durations nest and overlap GPU work. These observations do **not** demonstrate substantial CPU starvation, and uncovered recorded-kernel intervals are not automatically recoverable serving time. The receive-poll candidate therefore tests a bounded supported overhead mechanism rather than an asserted large bottleneck.

Both old profile controllers retain the diagnosed start JSON parse/stop HTTP errors; all trace/request evidence is preserved. The newly submitted derived bundles deploy the tested parser correction without hiding HTTP failures. [Executable inspection](inspect-pbs.py), [control details](222027.pbs111-inspection.json), [candidate details](222028.pbs111-inspection.json), [new actual submissions](../research-followup-20261020-recv2/RESULTS.md). No sampled GPU utilization/power/VRAM is invented for these old runs.

## FA3 scope clarification — 20 October 2026

The user asked whether FA3 is bad or merely unsuitable for this case. The measured negative is limited to **changing decode attention to FA3 on the tested H100 both-HPC-Ops, N54 deployment and pinned runtime**. FA3 executed on all eight decode ranks and passed the local protocol/output checks. This is not incompatibility, an accuracy failure, a global backend ranking or a claim about H200. Prefill attention remains FA3 in the deployed incumbents; rejecting this decode candidate does not remove it from prefill.

Mean end-to-end request latency is **4337.852772 ms** for FlashInfer control 222027 and **4372.812795 ms** for FA3 222028, an increase of **34.960023 ms**. The 118.922270-ms reduction in mean TTFT is outweighed by about 199 inter-token intervals with a 0.773278-ms higher mean ITL (approximately 153.882 ms extra). This explains the direction of the observed tradeoff for 200-token replies; it is not an exact goodput prediction or a causal kernel attribution. End-to-end TTFT includes scheduling/queueing/transport effects and does not prove a faster prefill kernel, since prefill settings were held fixed.

The goodput observation is −0.812% in one matched pair. It is insufficient to establish a universally slower algorithm or a statistically stable effect across deployments. There is currently no measured throughput improvement justifying priority for an unchanged repeat under the credit budget. Keep FlashInfer decode for this setting; reconsider FA3 when a distinct hardware/load/layout/runtime change or direct diagnostic evidence creates a new hypothesis. The exact kernel-level cause of this difference is not established by these aggregate numbers.

[Primary SGLang guidance](https://docs.sglang.io/docs/advanced_features/attention_backend), checked 20 October 2026, explicitly makes backend choice depend on model, hardware and use case and supports different prefill/decode backends. The retained actual workload and runtime evidence decide this particular comparison; current documentation is not proof that every installed backend supports every configuration.
