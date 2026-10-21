# Native TP4 prefill graph-disable probe submitted

Definite job **223005.pbs111**, submitted 2026-10-21T10:07:05.118514+00:00,
was Q in the server's immediate post-submit response. It requests one node,
4 H100, 56 CPU cores, 940 GB RAM and at most 20 minutes: maximum 170.666667 SU
at the retained 128 SU/GPU-hour accounting rate. The own PBS queue was empty;
there is no dependency, overlapping owned allocation or uncertain retry.
This is single-prefill initialization, not the 16-GPU scored deployment.

The exact native source functions pass four memory-threshold cases and both
explicit-disabled early returns on CPU. Three independent semantic artifact
fixtures pass. The submitted worker keeps the full 222780 BF16/unquant draft,
FP8 target, chunk 4096/HPC-Ops and unchanged NIXL patch; the only new server flag
is --cuda-graph-backend-prefill disabled. The role runs alone as TP4/EP1.
No serving requests, decoder, router, AIPerf or score is produced. The source
hash is checked inside the actual image before initialization.

Require terminal sealing and actual HTTP/native readiness, disabled graph
messages, all four NIXL ranks and no capture-begin/fatal failure. Inspect GPU
UUID mapping, memory/resource series and runtime traces separately. A passing
probe still does not prove real PD transfer, greedy token equality or accuracy.
No full-PD candidate or throughput screen has been submitted here.

The locked fresh ledger is Used 45575.959 / Balance 18424.041 / In Doubt 0 SU.
A unique 950.506-SU published delta reconciles 222769 and 222780, releasing only
their posted maxima. Reserving the new 170.666667 SU leaves 5253.374333 SU
internal headroom under the unchanged 51000 cap and 13000 project buffer.
Balance already excludes In Doubt; no double subtraction. These are dated
pre-submit ledger values, not a post-submit live balance or final probe charge.
[Reconciliation](reconciliation.json), [receipt](pbs-receipt.json),
[post-submit state](post-submit.txt), [frozen plan](PLAN.md).

The prior full repair's rank-divergent prefill graph decisions are observed,
but a specific blocked collective is still a hypothesis. This bounded probe
cost ceiling is one sixth of another 30-minute, 16-GPU, 1024-SU repair. Accepted
H200/H100 peaks, official accuracy gap and the current N62 submission remain.
