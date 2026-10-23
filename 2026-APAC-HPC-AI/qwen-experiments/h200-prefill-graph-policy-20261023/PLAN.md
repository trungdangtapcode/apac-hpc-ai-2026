# Measure the prefill graph policy before attributing an EAGLE speedup

## Question and prior evidence

The reproduced H200 target-only choice is N64, three full runs averaging 3044.400475 good output tokens/s. Full N68 adds only 0.083056% over its fresh control and is closed unchanged. EAGLE3 correctness job 25682 remains queued; no speculative speedup exists. Its prefill graph backend is uniformly disabled to avoid the earlier native draft/target initialization divergence. The ordinary target deployment uses the native automatic policy. Comparing these two deployments directly would mix speculative decoding with a graph-policy change.

This independent target-only pair asks how much the required prefill policy itself changes startup and short serving performance. It can run after 25682 regardless of that diagnostic's outcome. It neither bypasses the correctness-first EAGLE gate nor spends PBS credit while H100 access is unavailable.

## Controlled pair

Use two TP4/EP1 DeepGEMM prefill workers with chunk 8192 and one TP8/EP8 HPC-Ops decode worker, 16 H200 across two nodes. Keep the official FP8 target, explicit BF16 activations, BF16 KV confirmed on all ranks, FlashInfer decode attention, MNNVL, round-robin routing, the existing 912b7e heterogeneous-TP NIXL patch, native CPU binding, resource observation and client images common.

Both sides explicitly set max-running-requests 64 per prefill and 256 on decode. This prevents the old target's default 4096 capacity from becoming a hidden difference in a later speculative comparison. This pair does not assume the old limit caused a bottleneck or that the new limits have already initialized successfully. The explicit BF16 dtype and capacities are common conditions, so neither short result is a direct estimate of the original full incumbent's performance.

- Control s40: omit the prefill backend override. The pinned native CLI has no literal auto value. Actual ServerArgs must retain None and the native resolver must select breakable prefill graphs on prefill roles and disabled prefill graphs on the decode role.
- Candidate s41: explicitly set cuda-graph-backend-prefill disabled on every role. Actual prefill graph resolution must be disabled throughout.

The decoder's own CUDA graphs stay enabled with all batch sizes 1 through 64 on both sides. Require actual all-eight-rank decode capture completion, and all-four-rank prefill completion for each automatic prefill worker. An unexpected role resolution or incomplete capture fails for review. The capacity helper checks actual ServerArgs and later initialized scheduler receipts; an argument string alone cannot pass.

## Workload, semantic gates and observation

This is an unranked short screen: closed-loop N64, fixed synthetic 4000/200 input/output settings, seed 2026, cold-prefix cache busting, streaming chat, 20-second warmup, 40-second measurement and 30-second grace. Require exact normalized AIPerf input configuration, all raw profiling records, matching raw/exported joint SLA, fraction at least 0.90, and zero errors/cancellations. Keep every scored request in the denominator and use exported Goodput times 200 in good output tokens/s.

Before load, require both independently replayable P/D semantic warmup receipts, the explicit initialized capacity gate and per-rank BF16 KV records. After load, independently replay all eight short diagnostic responses against retained 25487 cases with no new failures, and all twelve long retrieval cases. The known reverse baseline failure stays recorded. Neither diagnostic establishes organiser accuracy, which remains unverified. Missing/deferred quality, missing exports, conflicting logs or failed stages reject the screen.

Both runs keep the same five-second role-specific CPU/GPU/server sampler and phase markers. Inspect startup, sampled allocated VRAM, actual KV pool and queues/running/inflight state when present, latency tails, raw errors and transport logs. No heavy profiler runs in this screen. Missing/misaligned data remains unknown; GPU activity, allocated memory, token occupancy and kernel time are different quantities. Save original failed outputs and provenance. Retain raw export and logs even when a gate fails.

## Resource, queue and stopping policy

Each allocation requests 16 H200 on two nodes with the actual 17-minute ceiling; no PBS SU. Shared absolute bounds are startup by T0+600, semantic warmup by T0+720, client/quality by T0+960 with a separate 240-second phase cap, head check by T0+980 with a separate 20-second cap, and bounded teardown/hard stop by T0+1020. Whole AIPerf invocation has a 135-second timeout; missing completion is a failure, not a score.

Preserve queued 25682. Submit s40 with afterany:25682 and s41 with afterok:s40, without modifying prior payloads or queue positions. Fresh own queue and partition checks must fit the five-job cap. The candidate remains dependent on a successful, fully gated control. If the control fails, review/cancel the held candidate rather than weaken gates or blindly rerun.

A valid short candidate gain of at least 1% only justifies a fresh full-duration matched pair and independent confirmation; it is not a ranked win. A smaller or negative result closes this standalone policy branch unchanged. If disabling graphs loses, retain the measured policy cost when later evaluating EAGLE3; do not interpret it as evidence that speculative decoding itself loses. If disabling graphs saves startup time, report allocated runtime separately from serving throughput. One fixed-order pair does not establish a reproducible gain.

## Preparation evidence

The source bundles s35 and accepted reference s38 are checksum-verified before derivation. The latter supplies bounded native Slurm launch, corrected role HOME creation, BF16-rank and semantic P/D proof. The former supplies the measured official client, quality checks, common workers and sampler. Source hashes and actual asset identities are retained. CPU fixtures cover ten initialized-capacity cases and two complete synthetic head-gate cases, each rejecting wrong durations, raw SLA contradictions, new output failures and missing graph capture. Synthetic fixtures are parser/gate tests, never new model measurements. Actual explicit 64/256 runtime, graph policy, memory headroom and performance await these jobs.
