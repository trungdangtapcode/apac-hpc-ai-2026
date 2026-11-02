# Independent review: H200 acceptance replay 28197

**Review verdict: PASS for local deployment acceptance and performance gates.** This is one successful replay of the qualified R2 portable Basic AI entry on the official cluster. It is not an official quality result, an official contest score, or evidence that an optimization improved performance.

## What ran

Slurm records job **28197** as `COMPLETED 0:0`, with 16 GPUs on two nodes, from **2026-11-02 01:06:04 to 01:16:15 UTC** (611 seconds). The scheduler queue no longer contains this job. The allocation used 16 H200 GPUs; elapsed allocation time is about **2.716 H200 GPU-hours**. No project SU figure is inferred from that GPU-hour calculation.

The measured entry was **P8-TP4_D8-TP8-EP8** at closed-loop concurrency **N=64**: two TP4 prefill workers, one TP8/EP8 decode worker, SGLang disaggregated prefill/decode over NIXL. Runtime logs show the submitted NIXL patch hash on all three worker processes; decode logs show the H200 HPC-Ops preflight and MNNVL all-reduce setup across eight ranks. The configured backends were DeepGEMM for prefill, HPC-Ops for decode MoE, FlashInfer for decode attention, and MNNVL for decode all-reduce.

The saved AIPerf input configuration records a synthetic, cold-prefix workload with seed 2026, nominal 4,000 input tokens and 200 output tokens, streaming chat requests, and SLA thresholds TTFT 3,000 ms / mean ITL 20 ms. The run used a 60-second warmup and a 120-second scored window with a 30-second completion grace period. The AIPerf manifest records 949 completed warmup requests and 1,907 completed scored requests; the scored phase took 123.28 seconds including completion grace.

Both P/D semantic warmup pairs passed (prefill-0/decode-0 and prefill-1/decode-0). I independently reran the included receipt validator; it exited successfully and checked two pairs against the saved endpoint inventory. The gateway model-list artifact contains the expected `qwen` model.

## Scored result, independently cross-checked

The raw request JSONL contains **1,907 profiling rows**. Applying the saved score-gate rule directly to those rows gives **1,881 good requests (98.6366%)**, **26 SLA misses**, **zero request errors**, and **zero cancellations**. All 26 misses exceeded the TTFT threshold; none exceeded the ITL threshold. This clears the local requirement that at least 90% of requests meet both latency limits.

| Metric | Result |
|---|---:|
| Goodput | 15.2575909 requests/s |
| Good output-token throughput (Goodput × fixed 200) | **3,051.5182 tokens/s** |
| Good-request fraction | **98.6366%** (1,881 / 1,907) |
| TTFT mean / p95 | 1,100.32 / 1,286.00 ms |
| Mean ITL / p95 ITL | 15.010 / 15.186 ms |
| Scored errors / cancellations | 0 / 0 |
| Raw output-token throughput (different metric) | 3,093.6895 tokens/s |

The 3,051.52 figure is the correct local contest-style score calculation for this run: exported Goodput times 200. Do not substitute raw output-token throughput. Client-exported output sequence lengths ranged from 199 to 201; the export reports zero OSL mismatches. Authoritative generated token IDs were not retained, so these counts do not establish a physical truncation or its cause. The score still uses the fixed 200 multiplier.

## Startup, runtime observations, and cleanup

The two pair-router logs each contain four early “No prefill workers available” messages. The bounded warm-topology retry then produced successful semantic completions on both paths before AIPerf began. These startup retries are separate from the 1,907 scored requests; the scored export and request log report no errors.

During the scored window, 191 decode-batch log snapshots show about 50 active requests on average (range 2–56), zero queued requests in the sampled lines, no retracted requests, and roughly 0.12 reported token-usage fraction on average. These are runtime scheduler snapshots, not GPU utilization measurements and not a causal bottleneck diagnosis. AIPerf's telemetry export has no configured or successful telemetry endpoints, despite telemetry being enabled in its input configuration. GPU utilization, sampled VRAM, power/temperature, CPU, network bandwidth, and per-phase hardware telemetry therefore remain **not collected** for this run. Do not describe the hardware as idle or healthy based on the missing telemetry.

The top-level batch and external Slurm records completed successfully. Nested serving processes and their launcher steps ended as `CANCELLED by` the batch job's EXIT cleanup after benchmark completion; that is expected teardown, not cancellation of scored requests. The profiling phase manifest and client log both show all 1,907 requests completed, with zero cancelled or errored.

## Promotion decision and limits

**Promote 28197 as the accepted, reproducible local deployment entry** for packaging and presentation, subject to the team's existing publication review. The frozen-payload manifest has 26/26 files matching their recorded SHA-256 hashes, and the benchmark-time submitted copies of the config, launcher, worker, semantic gate, score gate, and NIXL code are byte-identical to the frozen R2 entry selected for publication.

Keep the claim narrow:

- This is a successful full N64 performance-gate replay of the repaired portable entry, not a newly matched optimization comparison. The 3,051.52 result is an observation, not a gain attributable to the readiness patch.
- It verifies local request latency/goodput gates, semantic startup on both P/D paths, artifact completeness, and clean job completion.
- It does **not** verify the separate organiser-run model-quality requirement (at least 99% of reference quality). The local gate explicitly records `official_accuracy_verified: false`; the quality score remains unknown, not passed or failed.
- The readiness-only change addressed the earlier pre-benchmark model-registration race. The early pair-router retries still appear, but both semantic checks passed; retain them as startup observations.
- No official leaderboard result or organiser evaluation is available in this evidence bundle.

## Evidence paths

All paths below are relative to this study folder:

- `delivery/VNUHCM - TripleU/AI_Task/logs/reruns/28197/summary.json`
- `delivery/VNUHCM - TripleU/AI_Task/logs/reruns/28197/performance-gate.json`
- `delivery/VNUHCM - TripleU/AI_Task/logs/reruns/28197/official/n64/artifacts/qwen-openai-chat-concurrency64/profile_export_aiperf.json`
- `delivery/VNUHCM - TripleU/AI_Task/logs/reruns/28197/official/n64/artifacts/qwen-openai-chat-concurrency64/profile_export.jsonl`
- `delivery/VNUHCM - TripleU/AI_Task/logs/reruns/28197/official/n64/artifacts/qwen-openai-chat-concurrency64/phase_manifest.json`
- `delivery/VNUHCM - TripleU/AI_Task/logs/reruns/28197/pair-warmup-validation.json` and `pair-warmup-receipts/`
- `delivery/VNUHCM - TripleU/AI_Task/logs/reruns/28197/{prefill-0.log,prefill-1.log,decode-0.log,router.log}`
- `FROZEN_PAYLOAD.json`, `delivery/VNUHCM - TripleU/AI_Task/logs/reruns/28197/submitted/SHA256SUMS`, and Slurm accounting for job 28197
