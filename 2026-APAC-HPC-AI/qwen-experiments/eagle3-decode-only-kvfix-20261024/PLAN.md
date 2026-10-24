# S61 retry: role-aware KV geometry validator

## Evidence and hypothesis

S61 job 25988 used two target-only TP4 prefill workers and one EAGLE3 TP8 decode worker. All workers reached health 200; draft identity and runtime checks passed. It failed before semantic P/D warmup and before AIPerf because the geometry checker incorrectly required 190 KV regions on each prefill rank. The 32 raw receipts show 188 regions on each prefill rank and 190 on each draft-enabled decode rank. The corrected validator passes all 32 receipts.

This retry changes no serving parameter. It tests the same decode-only EAGLE3 feasibility hypothesis with only the role-aware validator repaired. Match the S59 target-only control 25947, with N64, 4,000/200 tokens, seed 2026, cold prefix cache and 20/40/30-second protocol.

## Frozen gates

Require checksum and asset preflight, root-bound control review, decode draft identity, all three server health gates, target-only prefill arguments, decode-only EAGLE3 args, rank-level BF16 KV/NIXL geometry, both semantic P/D paths, zero AIPerf errors/cancellations, at least 90% joint SLA success, smoke at least 7/8 without a new regression, and retrieval 12/12. Any startup/semantic failure is a failed run, never a score. A score from this short screen remains unranked and cannot replace the 60/120/30 full-protocol H200 frontier. Official accuracy remains UNKNOWN.

## Cost and admission

Reservation: 16 H200 GPUs across two nodes, maximum 17 minutes. H200 Slurm use does not consume PBS SU. Before submit, query actual queue and partition under `serving-tuning/watcher.lock`, check the five-job user cap and preserve the root review and definite scheduler receipt.

## Provenance

The new bundle is derived from the exact submitted S61 payload, with its SHA-256 manifest retained as `PARENT_SHA256SUMS`. The checker replay evidence is `validator-replay-25988.json`. Job 25988 raw evidence remains immutable under `runs/25988/`; it is a failed validation run and has no performance metrics.
