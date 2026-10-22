# Independent full H200 N64 replication

Full candidate 25366 scored 3044.489701 good output tokens/s with 98.633018% joint SLA and zero errors, 1.082867% above equally observed N62 control 25365. The earlier short screen 25339 also favored N64. One independent full deployment is required to assess repeatability before replacing the submission primary.

Derive `s34-h200-observed-n64-full-repeat` directly from the sealed N64 candidate `s30-h200-observed-n64-full-candidate`. Keep all operational files byte-identical. Only job identity and configuration provenance change. Preserve N64, 60-second warmup, 120-second measurement, 30-second grace, cold-prefix 4000/200 workload, seed 2026, FP8 target/BF16 KV, TP4 DeepGEMM/chunk8192 prefills, TP8/EP8 HPC-Ops decode, native graph batches 1–64, transport, router and resource observer.

Request 16 H200 GPUs across two nodes for at most 17 minutes; no PBS SU. Submit once after manifest verification, source review, partition and five-job cap checks. No dependency on the separate N64/N68 screen is required because this job is an independent deployment. Preserve queue positions.

Require full protocol/runtime checks, zero request errors and cancellations, joint SLA fraction at least 0.90, no new local output regression, and long-context checks. Compare the two full N64 runs and the matched full N62 control. Report individual values and variation; do not infer a statistical confidence interval from two runs or change the official score denominator. Official >=99% reference accuracy remains unverified. If N64 fails to reproduce, retain both runs and investigate rather than promote it.
