# H200 graph-policy pair submitted

At 23 October 2026 14:54:36 UTC, the frozen pair was accepted by Slurm:

| Job | Policy | Dependency | Requested allocation |
|---|---|---|---|
|25712|Native automatic prefill policy; no backend override|afterany:25682|16 H200, two nodes, at most 17 minutes|
|25713|Explicit prefill backend disabled throughout|afterok:25712|16 H200, two nodes, at most 17 minutes|

Both runs keep two TP4 DeepGEMM/chunk8192 prefills, one TP8/EP8 HPC-Ops decoder, explicit BF16 activations, target BF16 KV, FP8 weights, prefill 64/decode 256 request caps, decoder graphs 1–64, native NIXL and common observation. Only the user-selected prefill graph policy differs between the two conditions. Native automatic policy resolves differently by role; see the source-backed plan. The source variables in the old full incumbent differ in common dtype/capacity declarations, so compare these short runs only with each other.

These are **unranked short screens**, 20/40/30 seconds at closed-loop N64 with fixed 4000/200, seed 2026 and cold prefixes. No new score, model result or runtime capacity has been observed yet. Before load require initialized capacity, all-rank KV/graph and both semantic P/D receipts; the final head gate independently checks workload, all raw SLA records, zero errors/cancel and short/long response semantics. Official accuracy remains unverified.

Existing 25682 is unchanged. The control follows its terminal status and the treatment follows only a passing control. Current own jobs total three at submission, within the five-job cap. No PBS SU or H100 reservation was added; Slurm allocations still consume real GPU time. The per-job maximum is 4.533333 GPU-hours and the combined allocation ceiling 9.066667 GPU-hours; actual runtime will be measured after completion.

The full source/CPU/asset milestone was pushed as 7a6d936c before sbatch. [Definite receipts](slurm-receipt.json), [queue snapshot](post-submit-queue.txt), [exact plan and stopping rules](PLAN.md), [root validation](root-final-validation.json). Queue snapshots are dated, not live status.
