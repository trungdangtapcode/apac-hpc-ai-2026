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
