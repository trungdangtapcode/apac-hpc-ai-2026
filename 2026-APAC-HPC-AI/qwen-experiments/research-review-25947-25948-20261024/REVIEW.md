# H200 fast-default control and EAGLE3 performance screen

Review date: 24 October 2026. These are short, unranked feasibility runs, not official contest scores.

## Question and prior evidence

The reproduced H200 frontier remains 3,044.400475 good output tokens/s from full N64 runs 25366, 25373 and 25487. The strict EAGLE3 exact-token diagnostic has failed in earlier runs, while official full-set accuracy remains unknown. This pair asks whether EAGLE3 can improve service throughput under the official latency limits after restoring native fast defaults.

## Change and control

Both jobs used 16 H200 GPUs across two nodes, topology P8-TP4 / D8-TP8-EP8, BF16 KV, the same target FP8 model, N64, 4,000 input / 200 output tokens, seed 2026, cold prefix cache, 20-second warmup, 40-second measurement and 30-second grace. Both used FlashInfer sampling and native fast defaults. The candidate added EAGLE3 with two steps, top-k 1 and three draft tokens on all three workers.

Control job 25947 used target-only decoding. Candidate job 25948 used the same layout and workload with the draft model enabled. Their short protocol matches each other. It is not directly comparable to the 60/120/30-second full-protocol frontier.

## Results

| Measure | Control 25947 | EAGLE3 25948 |
|---|---:|---:|
| AIPerf requests | 630 | 642 |
| Request throughput | 14.4761 req/s | 14.6307 req/s |
| Raw output throughput | 2,895.18 tokens/s | 2,926.13 tokens/s |
| Goodput | 13.7868 req/s | 12.2150 req/s |
| Good output throughput (Goodput × 200) | 2,757.36 tokens/s | 2,443.00 tokens/s |
| Requests meeting both limits | 95.2381% | 83.4891% |
| Mean TTFT | 1,311.60 ms | 2,631.95 ms |
| P95 TTFT | 2,767.61 ms | 3,321.06 ms |
| Mean request ITL | 14.8330 ms | 7.8204 ms |
| P95 request ITL | 15.3033 ms | 8.6631 ms |
| Request errors / cancellations | 0 / 0 | 0 / 0 |
| Output sanity | 7/8 | 7/8 |
| Long-context retrieval | 12/12 | 12/12 |

The candidate increased raw output throughput by about 1.07% and nearly halved mean ITL, but its joint SLA fraction fell below the mandatory 90% gate. Its good output throughput was about 11.40% below the paired control. The 3,044.400475 full-protocol frontier is unchanged.

Recounting every retained profiling row shows the failure is entirely TTFT: the control has 30/630 TTFT breaches and zero ITL breaches; the candidate has 106/642 TTFT breaches and zero ITL breaches. Thus 600/630 control requests and 536/642 candidate requests meet both limits. The candidate's first-token tail, not its inter-token spacing, is the measured SLA problem.

The candidate decode log reported mean speculative accept length near 2.0 and accept rate near 0.5 during sampled batches. These runtime counters are descriptive, not a causal latency attribution. Five-second GPU sampling showed similar sampled role utilization and memory use between the pair; these aggregates do not isolate the TTFT cause.

## Terminal state and evidence validity

Job 25947 completed with exit 0. Independent replay of its raw AIPerf export passed the short protocol and confirmed the reported control metrics.

Job 25948 was marked FAILED with exit 1 after the scored AIPerf request run completed with zero request errors or cancellations. The post-run checker expected control fields named PASS_ACTUAL_S59_CONTROL and control_job, while the actual root review correctly emitted PASS_ACTUAL_S59_CONTROL_RUNTIME_REVIEW and job_id. A temporary, read-only replay translating those two schema fields advanced the checker to the substantive result: it rejected the candidate because its good-request fraction was 83.49%, below 90%. No frozen payload or retained raw run was changed.

Thus, the scheduler terminal state reflects a checker schema mismatch, while the underlying candidate is independently disqualified by the measured SLA. The run is not a winning or scoreable configuration. Its separate smoke and retrieval checks passed; these do not override the SLA failure or establish official quality.

## Assessment and next decision

Close the unchanged all-workers EAGLE3 configuration. EAGLE3 reduced ITL but sharply worsened TTFT on this short N64 screen. The measured N64 serving baseline confirms that prefill workers were target-only, while S60 enabled draft settings on prefill and decode workers. A new decode-only EAGLE3 candidate is justified: preserve the same N64 workload and control binding, keep both prefill workers target-only, and enable the draft model only on decode. Require actual role arguments, KV geometry, both P/D semantic paths, no errors, at least 90% joint SLA and the existing output-check floors before considering any longer full run.

Neither this screen nor the local sanity checks measure the official accuracy requirement. Keep the full-set ≥99% reference-accuracy status UNKNOWN.

## Evidence

- Control logs, AIPerf raw exports, summaries and resource telemetry: runs/25947.
- Candidate logs, raw exports, summaries, runtime counters and resource telemetry: runs/25948.
- Frozen source bundles: serving-tuning-10/s59-h200-fast-default-control and serving-tuning-10/s60-h200-fast-default-eagle3.
- Scheduler accounting: 25947 COMPLETED 0:0; 25948 FAILED 1:0, both on 16 H200 GPUs.
- Candidate checker mismatch is retained in runs/25948/head-performance-check.json and matched-control-verification.json.
