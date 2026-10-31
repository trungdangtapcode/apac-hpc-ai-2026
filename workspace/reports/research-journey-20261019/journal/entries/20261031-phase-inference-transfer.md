# Complete the distinct-port selection with two phase-mode interventions

Question: can the remaining two requested H100-derived configurations be tested
on H200 without padding the count with controls or repeated loads? H100 221924
was a real decode-only inference-mode trial at 2430.657 good tokens/s, +0.2596%
versus 221923 control 2424.365; H100 221966 prefill-only was 2424.089 (-0.0114%).
These do not establish useful H100 wins. The earlier exclusion was too strong
when applied across different hardware/load/serving contexts. Keep H100 branches
closed, but qualify one explicit current-H200 transfer for each distinct setting.

Hypothesis: the native DynamicGradMode inference-mode provider may alter tensor
bookkeeping costs differently at H200 N64. Actual CPU limitation or speedup is
not assumed. Pinned common.py and scheduler.py support the environment selector
and decorators. Export mode before server import, check exact source hashes,
native boolean/context behavior and restoration, then preserve all existing
runtime/KV/graph/semantic/output/full-workload gates. No mode or precision change
is inferred from ServerArgs alone; require raw per-role provider preflight.

S117 ports decode-only and S118 prefill-only into the current H200 DeepGEMM/
chunk 8192/N64 recipe, not the full H100 both-HPC-Ops/chunk 4096/N54 deployment.
S116 is a necessary fresh explicit no_grad control with the same preflight code;
old 27777 did not record explicit mode activation. Workers differ only in phase
environment flags. The native preflight runs in a launch subprocess with exported
environment inherited by the server; it is not an all-rank kernel-mode trace.
Actual distributed startup, graph/KV and output checks remain mandatory.

Twenty-one CPU synthetic receipt/backend/graph rejection fixtures pass. Host
Torch is absent; no real native context or GPU proof is claimed from these tests.
Three full 16 H200/two-node/17 minute allocations, maximum 13.6 GPU-hours combined,
zero PBS SU, cap five, no old-payload mutation. Compare both candidates with
fresh S116 only after it passes; useful gain > 1% needs independent confirmation.
No combined-mode sweep or unchanged losing repeat. Official quality UNKNOWN.

Existing chunk ports 27804/27806 plus the two phase ports would cover four source
intervention configurations. The added control is not an extra candidate.
Preparation is not admission; actual IDs/reservations follow separately. No H100
authentication/spending, HPC, background Codex or published package changes.

[Plan and source evidence](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-phase-inference-transfer-20261031/PLAN.md).
