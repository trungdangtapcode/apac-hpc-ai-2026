# Continue research when a tested branch loses

The user explicitly repeated that active research must continue: inspect outcomes, form the next justified hypothesis and submit it when queue/budget allow. The earlier interpretation that losing N56 and Tree meant leaving all H100 work stopped was wrong. Closing one branch is not a global stop. This instruction applies during authorised interactive work; it does not enable background Codex, schedules or automatic chat notifications.

## Why these tests

The retained H100 profile shows prefill Ring LL all-reduce kernels consuming 22.784% and 24.007% of summed kernel durations. Forced Tree actually executed and lost 10.65% against fresh N54, so it remains closed. Test the **protocol** rather than retrying Tree: change only prefill `NCCL_PROTO=allreduce:Simple`, leave algorithm selection automatic and retain the decode worker exactly. Separate GPU traces must establish actual protocol and algorithm. A change in the automatic algorithm would make this a protocol-selection interaction, not an isolated protocol-only causal result.

NVIDIA NCCL 2.28 documentation lists Simple among the supported protocols and supports per-collective selections since 2.24. It generally discourages overrides, so this is a bounded diagnostic hypothesis rather than a permanent recommended setting or a promised gain. We did not force LL128 on unverified hardware support. Tested runtime is NCCL 2.28.9; the reference below is the 2.28-series manual. Source accessed 19 October 2026: [official NCCL_PROTO reference](https://docs.nvidia.com/deeplearning/nccl/archives/nccl_2283/user-guide/docs/env.html#nccl-proto).

The other new hypothesis tests **chunk 6144 with HPC-Ops prefill** at N54. Earlier H100 chunk 8192 lost with auto prefill; that does not measure the new runner/chunk interaction. A 6144-token processing budget may change prompt batching and GEMM shapes. This is not an increased prompt length or a load increase. Compare with a newly deployed N54 control, preserving both-phase HPC-Ops and every other setting. If the result loses or fails quality, close that tested branch and choose another evidence-backed direction rather than retrying unchanged.

## Actual batch

Submit three serial PBS trials, at most one running 16-GPU allocation: fresh both-HPC-Ops N54 control plus post-score diagnostic profile; chunk6144 N54; and prefill Simple N54 plus post-score profile. Reserve at most 4608 SU in the existing 51000-SU operating bound and 13000-SU buffer. Keep original fixed 4000/200 workload, 60/120/30 protocol, raw request/error/SLA checks, BF16 KV and output checks. New results remain unaccepted until actual runtime, sealed payload, short nonregression and all 12 long checks pass. Organiser accuracy remains unverified.

Use the free fifth H200 queue slot for a full N58 interaction repeat with a separate post-score profile of the actual best-observed H200 deployment. Its measured source took 9:54; the existing 17-minute bound remains. Obtain actual winning-platform traces instead of transferring H100 kernel fractions. Preserve the four older H200 queue positions. The profile is not ranked traffic.

## Decision rule

Review jobs independently as they complete. Promote only a reproduced gain with a matched control and quality evidence. Retain all losing and failed outcomes. When feasible queue capacity remains, research and submit the next distinct test within the existing bounds; do not require another user reminder merely because a different branch lost. Do not submit jobs just to inflate the experiment count. No new load increase, model precision change, official submission promotion, slides or AI schedules in this batch.
