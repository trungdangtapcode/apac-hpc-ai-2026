# Correct the interpretation of startup-inclusive GPU averages

Original allocation-wide H100 resource means include startup and teardown. A separate request-admission-envelope audit finds decode activity 99.990%, prefill 91.542% / 91.427%, with 24 sparse samples per role and 72 successful server polls. Throughput and raw data are unchanged.

[Readable analysis, units, limitations and reproducible evidence](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h100-score-window-225227-20261026/REVIEW.md).

Activity is not FLOPS; VRAM is not token occupancy, and a low average CPU busy fraction does not establish that every relevant serving thread has capacity. These values do not prove EAGLE will win or establish a causal bottleneck. No new SU spent.
