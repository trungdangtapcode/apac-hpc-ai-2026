# 25 October: submit corrected two-replica TP4 topology as 26057

**Hypothesis and control.** S62r2 keeps the target-only topology experiment unchanged: two TP4 prefill workers and two TP4/EP4 decode replicas on 16 H200 GPUs, compared with target-only TP8/EP8 control 25947. Request shape, seed, runtime, model, N64, protocol and 3% advancement gate remain fixed.

**Correction from first admission.** Original job 26055 was cancelled at zero elapsed before node allocation after review found only two warmup threads and a 120-second deadline for four P/D paths. Historical 22219 needed up to 150.55 seconds for the same four paths. S62r2 starts all four route checks concurrently and allows 180 seconds, with fixed downstream deadlines. This is an orchestration/readiness change only; the model hypothesis and scoring workload remain the same.

**Admission.** Job **26057** was submitted at 2026-10-25 03:08:26 UTC to `hpcai`, requesting two nodes, 16 H200 GPUs and a maximum 17 minutes. The fresh pre-submit query found no apacsc42 job, while both nodes g1 and g4 were allocated to another user's job 26015. Immediate state was `PENDING (Resources)`, zero elapsed and no node. The scheduler's test-only estimate was 03:19:32 UTC; it is not a start guarantee. This Slurm job uses no PBS SU.

**Expected measurement and gates.** This is one unranked short N64 screen. All four workers, 32 before/after KV receipts, NIXL/runtime checks, all four semantic P/D routes, raw AIPerf denominator, >=90% joint latency success, 7/8 smoke, 12/12 retrieval and zero request errors/cancellations must pass. A longer confirmation requires >=2,840.08 good output tokens/s (3% over control 25947). No result exists while pending.

**Preservation.** Frozen payload: [`s62r2-h200-two-decode-tp4`](../../../../2026-APAC-HPC-AI/qwen-experiments/serving-tuning-11/s62r2-h200-two-decode-tp4/). Separate scheduler receipt: [`SUBMISSION-26057.md`](../../../../2026-APAC-HPC-AI/qwen-experiments/serving-tuning-11/SUBMISSION-26057.md). Original cancelled job 26055 is recorded separately and remains a non-benchmark attempt.

