# Full native-runtime load bracket after graph/admission review

Question: can a small change in client concurrency improve goodput under the recovered full breakable/native runtime? Actual full N64 control 26319 passes at 2827.996286 good tokens/s, 98.424311% joint SLA, zero errors/cancellations and 28 TTFT breaches. The four-arm graph/admission study found graph gains 0.79–0.91%, below the prospective >1% gate, and negligible admission gains. Close that tuning treatment without a confirmation selected from a subthreshold peak.

The previous N66–N70 losing sweep used a short graph-disabled/cap 64 runtime. It cannot settle the different full breakable/native workload. These two bounded arms change only closed-loop client load and corresponding worker count; keep all model/server/precision/transport/runtime/output gates and full 60/120/30/fixed 4000:200/seed 2026/cold-prefix settings. Runtime Python gates and worker script are byte-identical to control 26319. Dense decode captures remain 1..64; client N66 need not mean 66 simultaneous decoder requests.

| New job | Treatment | Receipt |
|---|---|---|
|26436|N62, lower load|Submitted, PENDING Resources|
|26438|N66, higher load|Submitted, afterany 26436|

Each requests 16 H200/two nodes/at most 17 minutes; no PBS SU. Fresh Slurm admission lock and cap 5 checked, sbatch test-only passed and exact receipts retained. A submission is not a result. Require independently replayed configured-N workload/raw denominator,>=90% joint SLA, zero errors/cancellations, smoke>=7/8 without regression and retrieval 12/12. Inspect role queue/running/KV, tails, hardware/CPU and transport evidence. Only >1% useful valid gain versus contemporary N64 justifies proposing independent confirmation. No widening or unchanged retry without these observations. Official full-set 99%-reference accuracy remains UNKNOWN. No submission/slides or HPC payload change; no background schedule.

[Plans and actual receipts](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-full-load-followups-20261026/submission-receipts.json). Frozen parents and failed earlier load runs are retained.
