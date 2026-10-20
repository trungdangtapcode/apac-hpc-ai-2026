# Native decode receive-poll interval, with measured observer overhead

## Hypothesis and prior evidence

H200's DeepGEMM prefill chunk8192 + HPC-Ops decode interaction now independently repeats at N60 (24738/24913: 2990.151/2989.175 good output tokens/s), with +5.295% versus fresh auto control 24912. Preserve N62 control/candidate positions. H100 decode FA3 is locally valid but loses 0.812% against fresh FlashInfer; keep FlashInfer. Prior phase-mode, one-shot and PDL-off overrides remain closed. The current queue is not a reason to repeat a losing option unchanged.

Selected CPU/CUDA traces show request/scheduler work and waits, but do not prove CPU limitation. The exact pinned disaggregated decode loop calls the request receiver on each iteration. Its native `SchedulerRecvSkipper` can avoid polling/pulling/broadcasting new requests on alternate decode iterations when `--scheduler-recv-interval 2` is set. Default interval 1 creates no skipper. Native DECODE weight is 1 and EXTEND/default weight 1000, so the interval-2 selection still receives immediately for extend-like mode; idle/decode polling can be delayed. All seven relevant source files have equal hashes in both runtime images; the extracted source and fixture checks are retained.

Hypothesis: reduce receive/broadcast overhead enough to improve serving goodput. Counterhypothesis: GPU work dominates, so the change is flat, or delayed admission worsens TTFT/goodput. This knob does not skip model tokens, remove synchronization safety barriers, change numerical kernels or add speculation. It is a different mechanism from continuous multi-token decode steps, grad mode or a collective protocol override.

## Matched six-run plan

| Platform | Observer off, interval 1 | Observer on, interval 1 | Observer on, interval 2 | Fixed load |
|---|---|---|---|---:|
| H200 | s19-hpc-n60-observer-off | s19-hpc-n60-observer-on | s19-hpc-n60-recv2 | 60 |
| H100 | h100-hpc-n54-observer-off-57 | h100-hpc-n54-observer-on-58 | h100-hpc-n54-recv2-59 | 54 |

Observer on means low-rate per-role GPU/node/server metrics plus worker `--enable-metrics`. The first pair estimates the combined observation cost; it is a single bounded overhead comparison, not an unchanged performance repeat for queue filling. Candidate versus the equally observed interval-1 control changes only the decode receive interval. Worker scripts inverse-diff to exactly the control. Common phase markers and the prepared post-score profiler HTTP parsing fix are present in all six. H200 uses its own DeepGEMM/HPC-Ops incumbent; H100 keeps both-phase HPC-Ops/chunk4096. Their scores are not pooled.

All retain checkpoint/native FP8 precision, BF16 KV, graph shape list, MNNVL AUTO+PDL, request-scoped NIXL, router placement/policy, streaming 4000/200, seed/dataset, full 60/120/30 protocol and short/12-long output checks. Native ServerArgs, backend/rank and patch hashes must match the intended configuration. The existing seven-case short-output nonregression baseline remains explicit; local tests are not organiser accuracy.

## Inspection and acceptance

Use complete raw protocol/SLA/error/output/runtime gates. Inspect latency p50/p95/p99/max and effective concurrency, per-role queue/batch/KV logs, sampler errors and raw hardware fields, plus separate CPU/GPU traces where collected. Align scored samples to exact phase manifest boundaries; verify GPU UUIDs/counts/role mapping and data coverage before reporting utilization. Missing data is not a healthy zero. Co-located node counters must not be summed twice. Kernel sums and sparse logs do not establish end-to-end bottleneck fractions.

The H200 post-score profile remains GPU-only; H100 retains its existing CPU+GPU activities. Both use the validated response fix: successful empty/text control responses are recorded; invalid generation JSON and HTTP 500 are not hidden. New profiles must be checked for actual traces and control status, not accepted merely because the helper exited zero.

Compare observer-on candidate to observer-on control; report observer-on/off delta separately. If observation causes material instability or makes cross-generation comparison unsafe, retain the raw evidence and design a lower-overhead followup rather than adjust reported scores. A useful gain requires an independent controlled repeat; a flat/losing result closes interval 2 at this setting, with no automatic interval 4, new load or combined knobs. Official full-set accuracy at 99% reference remains unverified.

## Resource and submission bounds

Three H100 16-GPU jobs, at most 45 minutes each, serial afterany chain: **4608 SU maximum reserve**, not expected charge. Pre-reservation ledger reconciles to Used 34972.443, Balance 29027.557, In Doubt zero, with 16027.557 SU internal headroom. Submissions must refresh real queues/credit, retain the 51000-SU cap and 13000-SU project buffer, and never exceed three active PBS jobs or one running allocation. Reserve before qsub; stop and retain reservations on uncertainty.

Three H200 16-GPU jobs, at most 17 minutes each. Preserve the existing 24914/24915 positions; query the actual queue and remain within five active jobs. Freeze payloads before submission and record every returned ID immediately. No job cancellation, existing-payload modification, authentication restart, background Codex or slide promotion is part of this plan. Initial preparation's H100-command mismatch was rejected before any submission and is retained under preparation-initial/.

Primary context: [SGLang server argument reference](https://docs.sglang.io/docs/advanced_features/server_arguments), [observability definitions and sampler validation](../resource-telemetry-20261020/README.md), [actual source evidence and reviewed results](../research-followup-20261020-0132/RESULTS.md). Runtime source, not a current documentation listing alone, determines whether this option executes in the disaggregated path.
