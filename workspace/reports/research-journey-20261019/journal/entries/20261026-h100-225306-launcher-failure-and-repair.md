# Repair a launcher error without blaming EAGLE performance

225306 F/127 after 6:41 passed actual source/device/metadata and one semantic response, then external timeout failed to find a binary named srun. The PBS compatibility layer implements it as a Bash function. Root added this incorrect wrapper after the preparation handoff; CPU syntax/JSON tests did not catch the cluster boundary. No AIPerf ran and no throughput was measured.

The new R2 derivative runs timed Bash, explicitly sources the unchanged shim and forwards arguments to its function. A regression with actual shim in isolated PATH reproduces old exit127 and corrected exit0, verifying node/GPU/CPU/command argv. Worker, model, weights, source, precision, observer, fixed N24 workload and output gates remain byte-identical. Preserve the original failed payload and charge; no retroactive pass.

[Actual raw failure and inspection](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h100-review-225306-20261026/REVIEW.md). [Reproducible R2 derivation and actual shim regression](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h100-equal-tp-bench-repair-20261026/regression.json). R2 is prepared, not a submitted or measured result. Fresh combined queue admission is required; CPU read channel currently times out while AI SSH works. No VPN restart, frozen-payload edit, HPC queue/budget action or background schedule.
