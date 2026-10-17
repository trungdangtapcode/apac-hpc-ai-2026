# Parallel experiments on H100 and H200

The user authorised continued submissions on both servers after clarification that the previous 16,384 SU campaign cap was an assistant planning choice, not the competition quota. H100 has 48,463.075 SU remaining in the last project ledger. Reserve at most 4,608 SU for this batch and retain a conservative 13,000 SU project buffer. H200 has no credit constraint reported by the user; the scheduler still limits active jobs.

| Platform | Job | Experiment | Maximum allocation |
|---|---|---|---|
| H100 | 221151 | Fresh combo control, concurrency 50 | 16 GPUs, 45 minutes |
| H100 | 221152 | DeepGEMM for prefill only, concurrency 50 | 16 GPUs, 45 minutes |
| H100 | 221153 | Weight prefetch for prefill only, concurrency 50 | 16 GPUs, 45 minutes |
| H200 | 24320 | Fresh combo control, concurrency 56 | 16 GPUs, 17 minutes |
| H200 | 24321 | One TP8/EP2 prefill worker, concurrency 56 | 16 GPUs, 17 minutes |
| H200 | 24322 | Weight prefetch for prefill only, concurrency 56 | 16 GPUs, 17 minutes |

H100 jobs form a verified afterany chain: 221151 → 221152 → 221153. The first job waits for resources; the other two have dependency holds. These holds are expected. H200 jobs are submitted by the existing non-AI watcher, with at most five active jobs.

## Questions and controls

DeepGEMM changes only the prefill MoE runner. Decode retains MNNVL and FlashInfer. H200 profile traces motivated the hypothesis; they do not prove a wall-time bottleneck or an H100 gain. Job 24291 has now passed full protocol, runtime, SLA, short output and 12 long checks: 2,715.842 good tokens/s, SLA 98.8194%, or +1.8136% versus control 24263. An independent H200 repeat is armed to confirm the gain against the new control. This does not verify the organisers' full accuracy requirement.

Weight prefetch targets startup time and allocated GPU cost. It need not improve benchmark throughput. Compare weight loading timestamps and allocation walltime with the new controls. Node storage, file cache and sequential ordering remain confounders; one observation is not causal proof of faster loading.

The TP8/EP2 prefill trial repairs the failed TP8/EP1 geometry in job 24282. The model has MoE intermediate size 1,536. MoE tensor parallelism is TP / EP / DP: TP8/EP1 gives 192 elements per partition, incompatible with the FP8 block size 128. TP8/EP2 gives 384, divisible by 128. This changes the prefill parallel layout without changing the checkpoint or precision. GPU startup and output quality still need validation. Treat it as a combined layout change, not an isolated TP speedup.

## Evidence and stopping rules

Keep the full 60-second warmup, 120-second measurement, 30-second grace, 4,000 input tokens and 200 output tokens. Preserve FP8 model weights, BF16 KV cache and the output checks. Require sealed raw evidence, intended runtime settings, no request errors or cancellations, and quality checks before accepting results. Useful gains need independent confirmation before selection.

Do not repeat the single-request prefill branch: job 24281 lost 1.73% goodput. Do not blindly increase concurrency beyond the observed plateau. Preserve all failed attempts. No Codex autopilot or new background AI session is enabled.

Independent H200 DeepGEMM confirmation is now submitted as job 24327 (pending for resources at 14:18 UTC). Four new H200 jobs and three new H100 jobs have confirmed scheduler IDs.
