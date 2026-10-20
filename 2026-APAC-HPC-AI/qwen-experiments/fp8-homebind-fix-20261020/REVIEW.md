# H200 TP8 dense screen reviewed

25020 completes exit 0 in 3 min 41 s on g4. The /work bind fixes actual Pyxis execution; all 256 full cases, ten unranked provider-preflight cases, eight distinct GPU UUIDs, numerical/input/source/config guards, nine finite positive samples per case and four nonempty native GPU traces pass. The prior 24990 path failure remains preserved.

Keep DeepGEMM for these TP8 decode projections. At M54, QKV DeepGEMM median 7.9295 us versus Triton 16.6580 us; O projection 5.6029 us versus 6.9759 us. Triton loses every rank/shape/M. FlashInfer gains 5.26% paired median only at QKV M16 with 5/8 improving ranks, loses at QKV M31 and both O shapes; native M>=32 falls back to DeepGEMM. No consistent useful provider signal warrants a full 235B model change or an unchanged repeat. This is a synthetic kernel test, not a new serving score or official accuracy check.

Inspect collect-25020.json,25020-review.json and the sealed collected/25020 raw payload/numerical/timing/cache/GPU-before-after and profiler artifacts. Full CPU/node/network telemetry and a serving queue/KV trace were not collected by this isolated harness; do not infer them as healthy or zero. Kernel time sums are not model wall time. Allocated cost is 8 GPUs × 221 s; this Firmus test is not charged to the NSCC SU ledger. The four H200 model jobs remain pending at the fresh query.
