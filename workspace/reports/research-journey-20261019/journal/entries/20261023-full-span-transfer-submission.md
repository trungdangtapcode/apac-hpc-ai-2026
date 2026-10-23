# Production-span pilot 224116 submitted

23 October 2026, 13:08 UTC. [Prior hypothesis and preparation correction](20261023-full-span-transfer-preparation.md).

The frozen no-model two-H100 pilot is now submitted as **224116.pbs111** and immediately running on a2ap-dgx036 and a2ap-dgx037. It reproduces 190 full-sized KV spans per GPU and ten pinned auxiliary spans, exercises native request-scoped transfer, and requires 380 distinct page hashes, a GPU scan of untouched destination bytes and independent source preservation. Source-only pattern initialization is frozen before submission. No completion or performance claim exists yet.

Fresh selected queue and credit passed under the AI budget lock. Reserve at most 42.666667 SU for two H100 GPUs over ten minutes; headroom after reservation is 4507.703333 SU. Used remains 46449.630 SU before posting. Existing access worked without new DUO authentication. Preserve H200 25682 unchanged and review terminal transfer/runtime/resource evidence before deciding whether this justifies a full serving repair. A pilot pass alone cannot prove model outputs or speedup.

[Actual receipt, scheduler record and frozen identity](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nixl-production-span-probe-20261023/RESULTS.md).
