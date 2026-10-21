# Native component gate passes: 222749.pbs111

Reviewed 2026-10-21T04:49:30.595962+00:00. Sealed terminal F / exit 0, **78 seconds**, estimated **2.773333 SU** before unique posted reconciliation. Submitted checksums and raw evidence seal pass. This is a component result, not serving performance.

The native /generate gateway again preserves synthetic request IDs and logprob response IDs. Scheduler and nvidia-smi return the same GPU-prefixed UUID; Torch returns that exact full UUID without GPU-. Canonical complete UUID equality passes, with one visible NVIDIA H100 80GB HBM3 / SM90. This new evidence establishes the representation mismatch that the preceding failed log alone could not establish.

Native source hashes match. Actual ModelConfig and registry resolve **sglang.srt.models.llama_eagle3.LlamaForCausalLMEagle3**, BF16, no quantization. The full pinned 1145943008-byte draft digest matches. All **13 BF16 tensors** are finite on the allocated GPU; both int32 mapping tensors have expected shapes. Native d2t + arange yields **64000 unique target IDs**, range **0–151645**, within the 151936 target vocabulary. t2d ranges 0–1 and the inspected loader ignores it; no inverse-index assumption is made.

Peak tensor-validation allocation is **1835008000 bytes** (not model VRAM usage, occupancy or utilization). No hardware time series, server batch/queue/KV metrics, token latency or scored workload was collected because there is no running model. Container extraction fallback remains visible. No draft class was instantiated, no weights loaded into model parameters, no official target loaded, no PD state transfer or forward pass occurred. Synthetic IDs do not prove real response ID completeness, exact greedy equality or organiser accuracy.

Next prepare one bounded allocated **real native draft construction and parameter coverage** gate. Require every published floating tensor to be consumed by native loaders and every non-shared model parameter to match the exact expected values, including combined Q/K/V and gate/up ordering. Explicitly leave the target-shared embedding unvalidated until real target integration; do not run inference with it. Real TP4/TP8, feature layers, PD transfer, attention verification/graphs, full ID completeness and greedy correctness remain later gates. No full speculative benchmark is justified yet.

[Sealed evidence](collection.json), [per-file hashes](collected/222749.pbs111/evidence-sha256.json), [pinned payload](SHA256SUMS).
