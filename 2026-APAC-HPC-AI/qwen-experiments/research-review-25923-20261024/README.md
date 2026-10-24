# Review of failed D5 R2 H200 startup job 25923

Job 25923 failed with exit code 1:0 after 128 seconds. The five-GPU device preflight and all five rank-local expert metadata observations passed. Each rank reported TP5/DP5, attention TP1, EP5/MoE TP1, 130 physical experts, 26 local expert slots, and the same valid 94x130 physical-to-logical map with replica tail [0,1].

Initialization then failed at ParallelLMHead: the checkpoint vocabulary size is 151,936, which is not divisible by TP5. DP attention reduced attention TP to one, but enable-dp-lm-head remained false, so the vocabulary-parallel LM head still used TP5. This occurred before model loading completed. No loaded expert weights or hashes, health response, request, quality result, PD result, or performance score were produced.

The 13 pinned Python source digests match the retained image extraction. The model tensor header preflight read only 352,848 bytes of header metadata; no tensor payload was read. Observer records are initialization metadata, not hardware telemetry. GPU utilization, memory, power, temperature, and server metrics were not collected.

The scheduler accounting and exact evidence limits are in [REVIEW.json](REVIEW.json). The read-only accounting query is retained in [SACCT.txt](SACCT.txt). Selected raw evidence hashes are in [EVIDENCE-SHA256SUMS](EVIDENCE-SHA256SUMS). Raw run artifacts and the submitted payload remain unchanged.
