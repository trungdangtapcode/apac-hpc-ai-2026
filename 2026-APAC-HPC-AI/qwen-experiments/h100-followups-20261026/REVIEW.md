# H100 followups admitted on 26 October

Two justified allocations are submitted, not measured results. Restored H100 access allowed recovery of earlier terminal evidence. The full incumbent needs a fresh observation after the outage; the equal-TP EAGLE branch needs its observer corrected before any performance interpretation.

| Job | Question and control | Allocation bound | Actual receipt |
|---|---|---|---|
| 225227.pbs111 | Reproduce accepted 222551 full N54 with unchanged operational files; distinguish current performance from a historical peak | 16 H100, two nodes, 30 minutes; 1024 SU | Q, aiq2; waiting for memory resources |
| 225228.pbs111 | Does native equal-TP send_kvcache return on all four sender ranks while the independent semantic response passes? | 8 H100, one node, 20 minutes; 341.333333 SU | H, afterany 225227 |

The earlier 224560 semantic response is independently valid, but old native KV invocation evidence is missing: the observer only wrapped the heterogeneous method. CPU preflight checks native argument/return/exception transparency and destination-index accounting; actual old evidence is rejected by the corrected gate. Temporary synthetic fixtures test full-rank acceptance, missing-rank rejection and exception rejection. These fixtures were never written into GPU raw evidence. New GPU acceptance is unknown.

The first admission attempt uploaded both bundles and verified their manifests, then stopped before any reservation or qsub because the separate CPU SSH channel was not authenticated. One echo-disabled authentication restored that read-only channel without restarting the VPN. Its fresh own queue was empty. The resumed operation verified existing remote manifests and checked selected AI credit and both queues under CPU-before-AI locks. It did not repeat an uncertain qsub. The final combined snapshot contains two AI jobs and no CPU job; one running AI is enforced by afterany. No HPC payload or budget was changed.

Selected project credit is 16447.331 SU. All 2634.666667 SU older unreconciled maximum reservations remain. New maxima total 1365.333333 SU, leaving a conservative 12447.331 SU planning headroom. This is not a statement that those maxima have actually been charged. The 30 October owner deadline and actual grant remain in force.

Inspect terminal raw outputs, errors, tails, source/runtime identity, role queues/KV, resource samples and cost before accepting or following up. A lower incumbent observation must be preserved. The observer probe is neither a ranked benchmark nor full official accuracy. If it fails, inspect its distinct cause rather than retry unchanged. No scheduled Codex or automatic retry was created. Frozen payloads and original failures remain unchanged.

Evidence: submission-receipts.json, pre-admission snapshots, post-submit-selected-qstat.json, verification.json, each frozen bundle's PLAN.md and SHA256SUMS. Private authentication/session state is excluded.
