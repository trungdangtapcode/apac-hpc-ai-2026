# Test the chunk/decode interaction and prefill communication

The user requested further optimisation on 19 October 2026. Review the two completed single-factor H200 trials before generating followups. Job 24723 (chunk 12288) loses 2.3789% versus control 24721; close that branch without retry. Job 24724 (DeepGEMM prefill chunk 8192 plus HPC-Ops decode at N58) passes all local gates and scores 2938.628 good tokens/s, +5.6907% versus same-load 24721 at 2780.403. This is a useful single observation, not a reproduced gain.

## H200 batch

Submit three exact source-derived bundles: 24736 fresh auto-decode N58 control, 24737 independent HPC-Ops-decode N58 repeat, and 24738 with the same interaction at N60. For the N60 interaction, compare both the N58 interaction repeat (load effect) and pending auto-decode N60 repeat 24732 (runner effect). Existing auto-decode N60/N62 jobs 24732/24733 retain their positions. Total own H200 active allocations must remain at most five, each 16 GPUs / 17 minutes. Do not automatically increase load or retry failures.

Every non-identifying operational file is byte-identical to the declared accepted source. The existing whole-client 360-second guard is unchanged across candidate and control. The benchmark, precision, output checks, transport and workload are unchanged. Worker runtime and frozen hashes remain mandatory acceptance evidence. The observed interaction does not establish that independent optimisations add linearly.

## One H100 prefill communication trial

Existing PBS N54 repeat 221645 and N56 trial 221646 remain queued in their verified serial chain. The prefill Tree trial is appended after 221646, so only one 16-GPU allocation runs at a time. Its maximum additional reservation is 1536 SU (16 GPUs / 45 minutes), within the existing 51000-SU operating bound and 13000-SU buffer. Keep ledger-lag reserves until actual Used reconciles; never deduct In Doubt twice.

Sealed both-phase H100 profile 221346 has 16 nonzero-rank traces and 376 successful diagnostic requests. Its two prefill workers show named NCCL Ring BF16 all-reduce kernels at 22.784% and 24.007% of summed kernel durations. These are not elapsed bottleneck shares or a speedup prediction. Actual H100 prefill logs report NCCL 2.28.9. The exact retained container header also identifies 2.28.9, and SGLang source calls ncclGetVersion and ncclAllReduce. Source dispatch can select custom paths, so an environment value alone does not prove algorithm activation.

NVIDIA's NCCL 2.28 environment reference documents per-collective selection since 2.24, with Tree among accepted algorithms. The default is automatic selection. Constraining an algorithm can fail or reduce performance; this trial needs evidence, not a presumption that Tree is better. Source: [NVIDIA NCCL_ALGO documentation](https://docs.nvidia.com/deeplearning/nccl/archives/nccl_2283/user-guide/docs/env.html#nccl-algo), accessed 19 October 2026. The documentation page is for the 2.28 series; the tested runtime is specifically 2.28.9.

At fixed N54, retain both-phase HPC-Ops and prefill chunk 4096. Export only `NCCL_ALGO=allreduce:Tree` inside the prefill branch of worker.sh; print that public setting. Decode's worker branch and environment are unchanged. Enable the existing separate post-score N48 profile without modifying its traffic or the ranked benchmark. Compare with queued N54 default-algorithm repeat 221645, plus source 221590. Require the new profile to show actual Tree kernels on every prefill rank and unchanged decode backends. Log selection without execution evidence is not activation proof. Changing reduction order may affect numerics, so short/long output checks and eventual organiser accuracy still apply. Reject backend/output failures without an unchanged retry.

The local source probe first used an unsupported `unsquashfs -cat` option; this was a tool error, not evidence of missing files. A sparse extraction then refused an existing empty destination. Both attempts are preserved and corrected by successful extraction into engine-source-v2; its files and hashes are retained. No GPU allocation was used for source inspection.

## Acceptance and stopping rules

A terminal allocation must also pass complete 60/120/30 protocol, all raw request/error/cancellation and joint TTFT ≤ 3000 ms / request-mean ITL ≤ 20 ms checks, at least 90% joint success, frozen payloads, intended runtime/rank coverage, short-output nonregression and all 12 long retrieval checks. Keep every failed attempt. Organiser full-set accuracy at 99% of the reference is still unverified. Repeat useful gains before promotion. No slides, official package, HPC task or organiser upload changes; no background Codex or new schedule.
