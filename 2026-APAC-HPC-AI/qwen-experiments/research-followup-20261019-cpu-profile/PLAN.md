# Identify host and GPU costs before further tuning

Three matched N54 observations around 2414 good tokens/s give no useful signal from larger prefill chunks or the scoped communication setting. Existing diagnostic traces requested GPU activities only: their summed kernel-duration percentages cannot identify host dispatch, launch gaps or an end-to-end critical path.

Prepare a repeat of the accepted both-HPC-Ops N54 baseline, keeping every worker, ranked client, precision, transfer and output-check file unchanged. Enable a separate bounded post-score profile and request CPU plus GPU activities, preserving 4 prefill and 32 decode steps, no stacks, no shapes and the same N48 diagnostic traffic. The exact retained ProfileReq schema lists CPU and GPU as supported activity choices. Runtime support, successful control calls, complete rank traces, CPU events and GPU kernels still need actual evidence.

This is an information-gathering experiment, not a predicted speedup. The baseline repeat must satisfy the usual full local gates before its number is accepted. Profile timing is perturbed by instrumentation, is not ranked traffic, and cannot automatically be mapped to the scored N54 interval or blamed on the scheduler. Use actual event correlations and gaps to choose a bounded next change to decode, MoE, communication or host dispatch.

Submit when a PBS slot is free, after live credit and the current serial tail are checked. Maximum request remains 16 GPUs / 45 minutes, reserve 1536 SU under the existing cap. If a preceding terminal charge has not reached Used, retain its conservative maximum reservation. Do not exceed three active jobs or one running 16-GPU allocation. No automatic schedule or background Codex.
