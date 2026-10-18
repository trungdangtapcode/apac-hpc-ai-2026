# Progress explained — 18 October 2026, 13:37 UTC

The observed performance is improving, but confirmed effects and provisional peaks are different evidence levels.

| Change | Observed improvement | Evidence level |
|---|---|---|
| H100 decode MoE runner: auto to HPC-Ops, concurrency 50 | About 2.47–2.80% over matched auto-runner controls | Independent repeat and fresh reversed-order control support the direction |
| H100 prefill MoE runner: auto to HPC-Ops, retaining HPC-Ops decode, concurrency 50 | 2.7277%; 2308.979 to 2371.961 good tokens/s | One matched observation; independent repeat currently running |
| H200 prefill chunk: 4096 to 8192, concurrency 58 | 2.5244%; historical control 2718.080 to 2786.696 | Passing local evidence, but needs new same-load control and repeat to separate time/node drift |

HPC-Ops changes the implementation of the mixture-of-experts computation. Chunk size changes how prefill tokens are divided into scheduled work. Concurrency changes the number of outstanding benchmark requests. These gains do not come from dropping model weights, experts, output tokens or requests, nor from loosening latency limits. They retain the native FP8 checkpoint, BF16 key/value cache and full protocol. Local output checks pass; organiser full-set reference-score accuracy remains unverified.

The latest observation is not a new completed measurement. At 13:36:55 UTC, H100 repeat 221339 is running (elapsed about 10 minutes); 221340 and 221341 are held in the verified dependency chain. H200 jobs 24573, 24574, 24575, 24588 and 24589 remain pending Priority. Both queues are at the current campaign caps, so no extra job is submitted. Preserve their positions.

A higher best observation is not proof that every change helps. H100 chunk8192 previously lost 2.4813% and was closed. Repeats and fresh controls may reduce or reverse provisional gains. Do not add percentages from different loads or convert these backend gains between H100 and H200.

Full hypotheses, metrics, source evidence, budget and stopping rules: ../research-followup-20261018-1323/RESULTS.md. No slide/package or scheduler-policy change. Codex autopilot remains off.
