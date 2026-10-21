# Actual native draft construction and loading pass

222750.pbs111, reviewed 2026-10-21T04:54:38.656130+00:00: sealed terminal F / exit 0, **99 seconds**, estimated **3.520000 SU** before unique posted reconciliation. Submitted hashes and raw evidence seal pass. Earlier gateway/config/tensor gates repeat successfully.

The **actual unmodified native LlamaForCausalLMEagle3 class constructs** on one allocated H100 in BF16 with real native single-rank NCCL/TP/PP/attention context. Native loaders consume all **13 published floating tensors** exactly once, covering **10 non-shared parameters**. Every loaded parameter equals the exact checkpoint/reference tensor, including combined Q/K/V and gate/up ordering. The native hot-token map also matches exactly. No silent ignored float tensor or unexpected absent parameter is observed.

The sole unloaded parameter is **model.embed_tokens.weight** (151936 × 4096 BF16). This is intentionally shared from the real target by the full runtime; the draft checkpoint does not supply it. The gate does not substitute fabricated weights and executes **no forward** with the uninitialized embedding. All target weights are untouched. Peak allocation **2902492672 bytes** describes this construction/loader diagnostic, including its buffers; it is not incremental serving VRAM, KV occupancy or utilization. No scored latency, acceptance length, role queue/KV series or hardware time series exists in this job.

The native ServerArgs diagnostic emits a default maximum-running-requests reset to 48 for speculation. A future full integration must explicitly record the actual serving value; do not silently treat its capacity as the baseline 256. The single-rank diagnostic has CUDA graphs disabled and does not establish production graph compatibility, TP4/TP8 sharding, target embedding sharing/auxiliary layers, both-phase KV/state transfer, exact greedy output, useful acceptance, throughput or organiser accuracy.

Next use a bounded real **target-only PD baseline** to validate full output-token IDs and target-a/target-b stability through the actual /generate gateway on the retained topology. Then a separately frozen speculative deployment can compare exact IDs with that control. No full ranked speculative benchmark is justified before these correctness gates. Preserve full diagnostic/config/runtime/cost evidence and the official scoring command unchanged.

[Complete collection](collection.json), [sealed raw hashes](collected/222750.pbs111/evidence-sha256.json), [prospective gates](PLAN.md).
