# A separate geometry constraint: vocabulary partitioning

H200 25923 and H100 224553 both reached actual five-rank initialization and failed while constructing the Qwen LM head: `151936 is not divisible by 5`. The five-rank expert metadata observer had already run; model weights and health did not qualify. This disproves the earlier source-only implication that attention TP1 and 130 expert slots were sufficient for complete startup. They address two partitions; the output vocabulary has a third constraint.

Pinned Qwen source passes `get_parallel().enable_dp_lm_head` to `ParallelLMHead(use_attn_tp_group=...)`. The native flag is declared in server_args and requires DP attention. Selecting it partitions the LM head over attention TP1, retaining all vocabulary rows without a custom padding or model patch. New derived R3 bundles require the actual flag on every rank and keep every loaded-weight/health check. They are prospective until actual GPU execution.
