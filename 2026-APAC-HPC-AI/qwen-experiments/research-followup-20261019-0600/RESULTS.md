# H200 chunk/decode interaction and prefill communication trial

Checked on 19 October 2026. The user requested further optimisation. [PLAN.md](PLAN.md) records hypotheses, controls, cost and stopping rules. Raw snapshots and post-completion hashes are retained; scheduler states below are dated checks.

## New completed H200 measurements

| Job | Configuration at concurrency 58 | Good tokens/s | Joint SLA (%) | Mean TTFT (ms) | Mean ITL (ms) |
|---|---|---:|---:|---:|---:|
|24721|Fresh DeepGEMM prefill chunk 8192, auto decode control|2780.403|98.7889|784.526|16.498|
|24723|DeepGEMM prefill chunk 12288, auto decode|2714.261|98.4724|922.231|16.258|
|24724|DeepGEMM prefill chunk 8192, HPC-Ops decode|2938.628|98.9065|871.991|14.998|

**24724 is the new highest locally accepted H200 observation: 2938.628 good tokens/s, +5.6907% versus the fresh same-N58 control 24721.** This isolates the decode runner at the chunk-8192 prefill setting. The earlier chunk-4096 runner comparison gained only about 0.21% at N58, so do not assume a runner effect independent of chunk/batching. This useful interaction requires an independent repeat and fresh matched control, now submitted. It is not a reproduced gain or a statistical confidence claim. It also changes more than load compared with the previous N60 auto-decode peak 2839.532, so do not use that cross-load comparison to isolate the backend gain.

**24723 loses 2.3789%** versus same-N58 chunk-8192 control. Mean TTFT worsens even though mean ITL is slightly lower. Close the chunk-12288 branch without an unchanged retry or automatically increasing chunk again. Retain the full passing-but-slower measurement as evidence.

Both completed candidates pass successful terminal accounting, exact planned submitted hashes, complete unchanged raw 60-second warmup / 120-second scoring / 30-second grace, no request errors/cancellations, joint latency gate, short-output nonregression and all 12 long retrieval checks. Their resolved runtime differences are restricted to the intended prefill chunk/graph geometry or decode main/inherited speculative MoE runner, apart from random seeds. Speculative decoding remains disabled, BF16 KV retained, all decode NIXL/MNNVL/attention ranks present, and HPC-Ops preflight passes. The whole-client guard did not fire. Full organiser accuracy at 99% of the reference score remains unverified.

Good tokens/s means qualifying requests per second multiplied by the prescribed 200 output tokens. Each request must satisfy TTFT ≤ 3000 ms and mean ITL ≤ 20 ms; at least 90% of all requests must pass jointly. The table reports means in milliseconds, which do not replace the per-request joint gate.

## New H200 jobs and matched comparisons

| Job | Purpose | Comparison |
|---|---|---|
|24736|Fresh chunk-8192 auto-decode N58 control|Match 24737 at identical load and prefill setting|
|24737|Independent chunk-8192 HPC-Ops-decode N58 repeat|Repeat 24724 and compare fresh 24736|
|24738|Same HPC-Ops-decode interaction at N60|Compare 24737 for load and pending auto-decode N60 repeat 24732 for runner|

All three request 16 GPUs / 17 minutes. Operational worker/client/quality/precision/transport payloads are byte-identical to their declared sources. Existing 24732 auto-decode N60 repeat and 24733 N62 keep their positions. At the latest check 24732 is running; the other four are pending Resources. At most five own H200 jobs are active. No automatic next load step or unchanged failure retry.

## H100: one source-checked communication hypothesis

The existing both-phase HPC-Ops N54 repeat 221645 and N56 trial 221646 remain queued in sequence. Added **221669.pbs111**, fixed N54 with prefill-only `NCCL_ALGO=allreduce:Tree`, after 221646. Decode worker code/environment remains unchanged. It enables the existing separate post-score diagnostic profile, not modified ranked benchmark traffic. Verify actual Tree execution on every prefill rank before claiming activation; a printed environment setting alone is insufficient.

Actual H100 prefill logs from sealed job 221346 and new H200 logs report **NCCL 2.28.9**. Sparse inspection of the tested image retains the matching header, PyNccl version query, NCCL all-reduce call and SGLang dispatch code with hashes under engine-source-v2/. SGLang can choose custom collective paths, which is another reason to verify the trace. The H100 profile shows one Ring all-reduce kernel at 22.784%/24.007% of summed prefill kernel durations; these are not elapsed critical-path shares or predicted speedup.

NVIDIA documents per-collective algorithm selection from 2.24, Tree support and automatic default selection. Restricting algorithms can fail or be slower. [NVIDIA NCCL 2.28 environment reference](https://docs.nvidia.com/deeplearning/nccl/archives/nccl_2283/user-guide/docs/env.html#nccl-algo), accessed 19 October 2026. The fixed-N54 trial compares with queued default-algorithm repeat 221645 and source 221590. Output checks remain mandatory because a different floating-point reduction order can change numerics. A useful outcome needs later confirmation; no new performance result is inferred from the documentation or CPU inspection.

The first source probe used unsupported `unsquashfs -cat`; the next sparse extraction refused an existing empty destination. These were local tooling failures, not missing runtime files. Successful corrected extraction uses a new destination, with original output/errors and hashes preserved. No GPU was allocated for inspection.

## Budget and current limits

The newly queried ledger as of 19 October 13:40:01 SGT reports **Used 27975.680 SU, Balance 36024.320 SU, In Doubt 0 SU**. The additional 398.222 SU reconciles terminal 221590 (16 GPUs,11:40 walltime at 128 SU/GPU-hour) within rounding. Its old conservative reservation is now released only because that charge appears in Used.

The new communication job reserves at most 1536 SU. All three outstanding PBS jobs reserve at most**4608 SU total**, each 16 GPUs / 45 minutes in verified `221645→221646→221669` order. Conservative internal operating headroom is **18416.320 SU**, under unchanged 51000 SU bound and 13000 SU buffer. These are planning limits, not organiser quotas or expected expenditure; no budget increase. Do not subtract In Doubt twice from reported Balance. New PBS jobs have no score yet.

No new VPN authentication, background AI, schedule, slide, official submission package, HPC task or organiser upload. The latest H100 accepted peak remains 221590 N54 at 2430.891 good tokens/s until new jobs finish and pass full review. Safe work is captured into the existing private Git archive; external artifact bytes remain local and require their separate off-host copy.
