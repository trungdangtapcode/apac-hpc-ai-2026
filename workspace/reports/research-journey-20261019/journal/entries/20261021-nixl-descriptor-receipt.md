# 21 October: submit the bounded actual KV descriptor gate

Recorded 2026-10-21T19:54:53.334131+00:00. Prior question, exact controls, CPU failures/corrections and
scope are in the [prospective milestone](20261021-nixl-descriptor-plan.md).

The frozen 24-write source-pinned descriptor probe is submitted once as
**223097.pbs111**, at 2026-10-21T19:54:05.187642+00:00, maximum two H100 GPUs / two nodes /
ten minutes / 42.666667 SU. The immediate actual scheduler shows RUNNING on
035/039. These are different from the earlier failed full-model pair 019/031.

The fresh locked own-GPU queue was empty and published Used remains 46367.710 SU
before submission. Reservation leaves **4589.623333 SU** under the fixed internal
cap, preserving the 13000-SU project reserve. No CPU project query or ledger
change, uncertain retry or full model load was performed. The same-job final
checker must validate real rank receipts; remote shell status alone is insufficient.

[Actual receipt and raw scheduler](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nixl-descriptor-probe-20261021/RESULTS.md),
[immutable payload](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nixl-descriptor-probe-20261021/SHA256SUMS). No outcome yet. Review native descriptors,
destination bytes, source/peer identities, error logs and accounting when terminal;
then decide whether actual native KV geometry and semantic warmup gates justify
a bounded full-PD integration attempt. Short H200 screen 25339 remains queued
alongside the four existing positions; its result is also pending.
