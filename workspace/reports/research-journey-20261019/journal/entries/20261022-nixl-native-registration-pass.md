# 22 October: native registration and host auxiliary transport pass

Recorded 2026-10-22T00:11:49.638230+00:00. [Prior hypothesis, control and fixture correction](20261021-nixl-native-registration-plan.md),
[actual receipt](20261021-nixl-native-registration-receipt.md).

**223132.pbs111 is F/exit0**,315 seconds /estimated22.4 SU. Actual native
190-entry VRAM and three-entry DRAM registration groups verify on both physical
ranks, nodes039/037. Three native KV writes and one host auxiliary write complete;
independent head and local replays verify all GPU/host bytes, sentinels, source
identities and reciprocal peer metadata hashes. All raw/submitted checksums pass.

[Full sealed review and precise limits](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nixl-native-registration-probe-20261021/REVIEW.md). No selected transport
error patterns occur in inspected joined PBS stdout. Automatic coarse GPU/CPU
accounting exists but is not matched telemetry or production health proof.
Private pointers and NIXL metadata bytes are excluded. Published charge not yet
uniquely posted: retain42.666667 SU maximum, internal headroom4575.472333 SU.

Assessment: base transport, tiny descriptor arithmetic, native tiny multi-region
registration and DRAM aux now pass these cheap gates. Full bootstrap, large KV
pools, actual TP collective and native EAGLE3 correctness remain unproven. Next
assess a fresh H200 target reference plus EAGLE3 correctness port to save H100 SU,
with actual native geometry receipts and independent semantic pair warmup gating.
Do not blindly repeat the unchanged full H100 failure or claim a serving gain.
Current full H200 N62 control25365 completed; matched N64 candidate25366 is running.
