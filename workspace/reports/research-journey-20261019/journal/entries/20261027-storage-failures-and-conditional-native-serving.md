# Runtime storage becomes the current prerequisite

Question: after actual smaller-chunk losses, can the larger-batch/HPC-Ops interaction be measured reliably? The first candidate/control never reached model startup because g4 default Enroot storage was full. Allocated disk inspection found no stale own rootfs to remove and ample node-local NVMe. An exported data-path variable passed the standalone Enroot fixture but was filtered by Pyxis in actual jobs; this corrects the initial deployment claim.

Now probe 26538 tests the real image and CUDA using unprivileged direct Enroot under Slurm. Conditional control 26545 and candidate 26547 are queued and require its actual successful receipt. Their original worker/model/source/quality/raw-score gates remain. Nothing has measured a gain yet.

[Complete controlled change, exact receipts, source references and limits](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/native-enroot-serving-20261027/REVIEW.md). [Original failed fix and correction](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/enroot-local-repair-20261027/RESULTS.md).

No privileged plugin setting or another user's files were changed. The direct runtime is experimental until actual GPU, namespace/mount, native source/runtime, semantic and output checks pass. No automatic retry or unreviewed score promotion.
