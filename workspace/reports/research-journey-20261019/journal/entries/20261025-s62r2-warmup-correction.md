# 25 October: correct S62 route warmup before GPU allocation

**Question and prior evidence.** The first S62 submission (26055) was pending without a node. Review found its inherited warmup cap was 120 seconds and its four required P/D routes used only two worker threads. Historical job 22219 tested the same two-prefill/two-decode topology: all four semantic routes passed, but the last took 150.55 seconds. Modern S59 control 25947 had only two P/D routes and warmed both in 104 seconds, which did not justify a 120-second limit for four routes.

**Correction.** Job 26055 was cancelled at 03:06 UTC while still `PENDING (Resources)`: no node assigned, elapsed zero, no GPU allocation. Its frozen payload and cancellation receipt remain preserved. The new immutable revision [S62r2](../../../../2026-APAC-HPC-AI/qwen-experiments/serving-tuning-11/s62r2-h200-two-decode-tp4/) keeps the topology and scoring settings unchanged, launches all four route checks concurrently, and allows a bounded 180-second warmup. Startup is bounded at 640 seconds; the N64 workload and downstream deadlines remain fixed. This changes orchestration readiness, not model configuration or the performance hypothesis.

**Evidence and limits.** Old job 22219 proves that four endpoints and all four semantic paths can work with the earlier router/runtime; it does not validate S62r2's modern worker image, KV receipts, runtime gates or throughput. The new bundle's shell/Python syntax and all payload hashes passed local checks. Hardware-dependent runtime behavior remains unverified until job start. It is not a measurement.

**Next decision.** Refresh Slurm queue/nodes before submitting one S62r2 job, 16 H200 GPUs for no more than 17 minutes. Keep pending/cancelled attempts separate from benchmark results. Use the existing gate and require at least 2,840.08 good output tokens/s with all SLA/output checks passing before any longer confirmation.

**Preservation.** Original bundle and no-allocation receipt: [`s62-h200-two-decode-tp4`](../../../../2026-APAC-HPC-AI/qwen-experiments/serving-tuning-11/s62-h200-two-decode-tp4/), [`SUBMISSION-26055.md`](../../../../2026-APAC-HPC-AI/qwen-experiments/serving-tuning-11/SUBMISSION-26055.md). Corrected revision is a separate frozen payload.

