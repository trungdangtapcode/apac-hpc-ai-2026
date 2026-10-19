# Next research directions, prepared while allocations wait

## First available PBS slot: dense prefill attention

A standby trial h100-hpc-prefill-flashinfer-n54-45 is frozen locally, not uploaded, submitted or budget-reserved. Check the new control result and live queue/credit before submission. Preserve at most three active PBS jobs and one running 16-GPU allocation. A free slot should trigger review and justified continuation during active authorised work; do not wait for another reminder.

Exact source extracted from the retained SGLang image confirms the phase-specific attention override and the registered dense FlashInfer backend. In the inspected implementation its internal prefill backend starts at fa2, so a different kernel path is plausible; it is not proven faster than FA3. The old both-HPC-Ops profile puts one FlashAttention kernel near 7.2% of prefill summed kernel duration, giving a smaller target than MoE or communication. That is why protocol and chunk experiments were submitted first. These percentages are not wall-time speed predictions.

The standby changes only prefill attention, retains chunk4096 and both-phase HPC-Ops, and compares fresh N54 default-FA3 control 221827. Decode is byte-identical. Require resolved runtime and actual dense kernel evidence, all ranked workload/SLA/output checks and eventual official accuracy. No sparse attention, prompt pruning, shorter outputs or lower precision is allowed.

Primary context: [SGLang attention-backend guide](https://github.com/sgl-project/sglang/blob/main/docs/docs/advanced_features/attention_backend.mdx), accessed 19 October 2026. Current upstream documentation is only context; the extracted runtime source and its hashes establish support in our actual image. See runtime-attention-source/ and runtime-attention-source-sha256.json.

## Further communication work: establish support first

The failure of forced Tree does not exhaust communication tuning. NVLink SHARP could be another direction, but it requires actual platform/runtime support and allocation of NVLS resources. NCCL 2.28 documents automatic detection by default; forcing enable can make initialization fail. Do not submit a full-model NVLS sweep based only on the Hopper GPU label. First inspect support with a bounded communicator probe using the same runtime, then choose a matched full trial only if warranted. No NVLS job is submitted or reserved in this batch.

Source: [NVIDIA NCCL 2.28 NVLS reference](https://docs.nvidia.com/deeplearning/nccl/archives/nccl_2283/user-guide/docs/env.html#nccl-nvls-enable). The 2.28-series reference is distinct from our specifically recorded 2.28.9 runtime. No benefit is inferred from summed kernel shares.

## Accuracy: separate the published rule from missing details

The local task addendum Q1/Q4 requires full-set accuracy at 99% of the organisers' unmodified FP8 reference. It does not specify a frozen task list, evaluation harness version, prompt templates, decoding settings or published reference scores. Model-card benchmarks are examples, not enough to reconstruct that unpublished official check. This checkout also lacks the referenced reference-scripts directory. Preserve that finding rather than inventing an official harness.

A local evaluation can still compare candidate and retained FP8 baseline on declared public tasks, but it must be labelled local supporting evidence, not an official pass. Our short/12-long retrieval checks remain regression diagnostics only. No GPU time is committed to a guessed full official evaluation in this batch. Resolve published harness/reference information before claiming contest accuracy.
