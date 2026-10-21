# Submit a cheaper native TP4 prefill graph probe — 21 October 2026

**Question and prior evidence.** Collected 222780 proves the BF16 repair gets
decode graphs/readiness past RMSNorm, but both prefills split at the automatic
4-GiB memory guard. Three ranks skip; rank 3 enters draft graph capture and
never finishes. The observed stall is not yet a proven blocked collective.
A full unchanged retry would cost up to 1024 SU without a new intervention.

**Hypothesis and exact change.** Uniformly disable prefill graphs with the
native --cuda-graph-backend-prefill disabled flag, retaining the published FP8
target, BF16/unquant EAGLE3 draft, TP4/EP1, chunk 4096/HPC-Ops and NIXL patch.
The eager model path preserves its work; do not force below-threshold capture
or change weights, experts, layers or target verification. First use one
prefill on 4 H100, not another complete 16-GPU PD deployment.

**Source proof and validation.** Bounded extraction reads just cuda_graph_setup.py
from the recorded image with one CPU worker. The host unsquashfs lacks -cat;
that first syntax attempt failed and the subsequent single-file -d extraction
succeeded. The actual native AST functions reproduce the three-rank skip/
one-rank capture decision at observed memory values. Explicit-disabled paths
return the target eager runner and no draft graph. Four threshold cases, both
early returns and three adversarial semantic fixtures pass on CPU; actual
GPU initialization and full tensor behavior remain untested at submission.
The compute entry point verifies the native source hash and four Hopper GPUs.

**Submission and cost.** Definite 223005.pbs111, immediate Q, requests one node,
4 H100/56 CPU cores/940 GB RAM/20 minutes; ceiling 170.666667 SU. Empty own PBS
queue, no dependency or overlap, frozen checksummed payload uploaded once.
Fresh queue/myprojects/known accounting ran under budget.lock. Used 45575.959,
Balance 18424.041, In Doubt 0 SU. A unique 950.506-SU delta reconciles 222769/222780;
retain only the new maximum, leaving 5253.374333 SU inside the 51000 cap and
13000 buffer. No double-counting In Doubt or inferred prepaid refund.

**Assessment and next decision.** This is a readiness diagnostic with no
serving request, decoder, router, AIPerf, throughput or output-equivalence
result. Independent result validation requires HTTP readiness, native ready
log, target/draft graph-disable messages, all four NIXL ranks and no prefill
capture start or matched fatal patterns. On terminal completion inspect these
and actual UUID/memory/CPU/resource evidence. Missing/uninspected data stays
unknown. Only useful successful readiness permits a separate full-PD repair
and actual-ID comparison; that still precedes any matched throughput screen.
Failure requires new evidence or closure, not an unchanged repeat.

**Preservation.** Preparation was captured/pushed as ba31b6d before qsub.
The receipt, budget change and this interpretation form a separate small
checkpoint. [Frozen plan and results](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/eagle3-prefill-graph-gate-20261021/RESULTS.md).
The accepted N62 package remains unchanged because no new serving result has
passed. Keep VPN/SSH alive, existing five H200 positions and autopilot disabled.
