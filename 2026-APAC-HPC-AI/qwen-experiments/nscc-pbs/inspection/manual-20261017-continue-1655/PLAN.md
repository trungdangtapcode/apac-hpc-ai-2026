# Follow-up experiments after the new controls

Updated 17 October 2026, 16:58 UTC. These are local research results, not organiser scores.

## Results reviewed in this turn

| Platform | Job | Load | Good tokens/s | Mean TTFT (ms) | Mean ITL (ms) | Joint SLA (%) |
|---|---|---:|---:|---:|---:|---:|
| H200 | 24320 | 56 | 2670.321 | 851.827 | 16.267 | 98.8002 |
| H100 | 221151 | 50 | 2231.429 | 495.915 | 19.386 | 98.4286 |

Both controls passed full protocol, frozen payload, runtime, short-output and 12-case long review. H100 221151 exceeds the previous peak by about 0.072%, while retaining the same configuration. This is an observation of repeat variability, not a new algorithmic gain. H200 24320 confirms the prior control range.

## H100: repair readiness, not benchmark thresholds

Job 221152 failed with exit status 1 and no benchmark export. It consumed 20:13 allocation walltime. The scheduler output reports a worker health readiness timeout at the global 1,200-second deadline. Prefill logs reached engine startup and local disaggregation warmup near that deadline; representative timing was 912.66 seconds loading weights plus 161.62 seconds of prefill CUDA graphs. No backend incompatibility traceback was found. These logs do not prove scored requests would pass.

Retry **221177.pbs111** retains all model, topology, backend, client, quality and benchmark settings. The only execution change is the worker readiness deadline, from 1,200 to 1,800 seconds. The overall allocation stays capped at 45 minutes; the client deadline still follows the allocation. It runs after prefetch job 221153 via a verified afterany dependency. There is no automatic retry loop. If it still cannot start within that bound, retain the failed artifacts and reassess startup before spending another allocation.

Fresh project ledger: grant 64,000 SU, used 17,075.200 SU, balance 46,924.800 SU, In Doubt 0, as of 18 October 00:40:02 SGT. Terminal jobs 221151 (24:51) and 221152 (20:13) account for the 1,538.275 SU ledger increase within 0.01 SU. Their reservations are reconciled. Prefetch 221153 and retry 221177 each reserve 1,536 SU maximum: 3,072 SU total. Headroom within the existing 51,000 SU planning limit is 30,852.800 SU after reservations. The 13,000 SU buffer and 51,000 SU limit remain internal planning choices, not BTC quotas.

## H200: bounded load test for the new prefill backend

Job **24352** tests prefill-only DeepGEMM at **N58**. The existing combo plateaued at N56–58, but DeepGEMM at N56 improved TTFT and goodput versus control 24263. A new prefill implementation may move that load frontier, so this is a justified new-backend load test rather than a blind increase of the old configuration. The only execution change from 24291 is client concurrency 56 to 58. Keep the 17-minute, 16-GPU bound and all runtime/output gates.

Compare against the same-load historical combo 24236, explicitly acknowledging time drift, and against the pending independent DeepGEMM N56 repeat 24327. The full normalized client protocol must match the N58 reference. A higher-load gain needs repeat evidence before selection; a failed SLA or worse useful throughput closes this load branch. Do not extend to N60 automatically.

Still pending: 24321 (TP8/EP2 prefill), 24322 (prefill weight prefetch) and 24327 (DeepGEMM N56 independent confirmation). Source-bound reviewers are prepared for TP8/EP2, the DeepGEMM repeat and N58. Existing completed reviews passed regression checks; pending jobs correctly return a waiting status.

## Scope and records

Preserve collected raw artifacts and all negative results. The old slide deck update remains a dated research snapshot; no official-script promotion is implied by a new control peak. No Codex autopilot, cron or background AI session is enabled. Existing non-AI Slurm watcher remains active.
