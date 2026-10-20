# H100 prefill chunk interaction: retain 4096

Reviewed 2026-10-20T10:06:31.204284+00:00. Both jobs pass all local protocol, SLA, runtime, sealed payload and short/12-long output gates. **Chunk 8192 provides no useful gain in this pair**: good output throughput is **0.7814% lower**, first-token mean increases **75.665 ms**, and its modest ITL mean improvement does not compensate. Retain HPC-Ops prefill chunk 4096, with no unchanged 8192 retry or load growth. This is one pair; it does not prove a universal loss at every load/platform. Official full-set reference accuracy remains unverified.

| Metric | 222281: chunk 4096 control | 222282: chunk 8192 candidate |
|---|---:|---:|
| Good output throughput, good tokens/s |2401.577649|2382.811874|
| Joint qualifying/total requests |1482/1509|1471/1499|
| Joint SLA success, % |98.210736|98.132088|
| TTFT mean / p99, ms |741.246 /3452.047|816.911 /3795.440|
| ITL mean / p99, ms |18.180 /19.072|17.950 /19.138|
| Raw TTFT / ITL breaches |21 /6|24 /4|
| Request errors/cancellations |0 /0|0 /0|
| Long-context diagnostic checks |12/12|12/12|
| Allocation walltime |14:11|12:50|
| Allocated-walltime charge, SU |484.124444|438.044444|

TTFT is time to first token; ITL is the mean interval between output tokens within a request. The contest checks each request against 3000/20 ms and requires at least 90% joint success; p99 is an additional tail diagnostic, not a new contest gate. Good output tokens/s counts only jointly qualifying requests and uses the prescribed 200 output tokens per request. Errors remain in the denominator. The historical unobserved 2433.020 H100 peak is not a matched control for this observed pair.

## What was really changed

Only the worker's explicit prefill chunk flag changes 4096→8192; inverse-diff and all common execution payload hashes pass. The resolved native runtime also **automatically expands prefill breakable-graph max_bs/buckets** with that chunk setting. Earlier statements implying every prefill graph field was identical are historical and incomplete. Complete decode graph settings, prefill backend/compiler, worker topology, precision, MoE runners and other arguments remain identical apart from random seeds. The treatment is the deployed chunk-setting effect including its native graph consequence, not batching with graph range held fixed.

The initial reviewer stopped on this dependent cuda_graph_config delta. The correction executes the exact pinned bucket generator and validates only the derived max/buckets, rejecting five unrelated decoder/backend/compiler/bucket mutations. No blanket exemption or frozen job modification. [Correction and source](GRAPH_CORRECTION.md), [strict fixture test](derived-graph-validation.json), [original rejection](222282-original-rejection.json), [accepted pair](paired-comparison.json).

## Inspection beyond score

Both jobs have 16 disjoint GPU UUIDs with 24–25 five-second samples per role inside the scored phase, complete role/rank runtime proofs, and 16 sealed post-score CPU/GPU traces. Diagnostic requests succeed 354/354 and 371/371. Starts return 200; all three stop_profile calls return 500 after auto-bounded captures in each deployment. Preserve those known diagnostic errors; do not call logs error-free or mix profile traffic into the score. Kernel-time sums and sampled activity are not wall-time bottleneck shares or FLOPS/bandwidth efficiency.

| Role | Control GPU activity, % | Candidate GPU activity, % | Control VRAM, MiB | Candidate VRAM, MiB |
|---|---:|---:|---:|---:|
| Prefill 0 |91.42|88.30|76710|77766|
| Prefill 1 |85.21|83.89|76706|77766|
| Decode |99.125|100.0|78000|77964.32|

The larger chunk uses about 1 GiB more sampled prefill VRAM. Phase-bounded server gauges show no sampled decode queue; decode KV token usage mean 0.2332/0.2288 differs from allocated VRAM. Prefill running-request means change 1.208/1.56→1.40/1.32; sampled queue maxima 3/17→15/5. Worker imbalance and intermittent queues motivate investigating routing but **do not prove a causal bottleneck**. Current whitelist does not collect inflight state: record NOT_COLLECTED, not zero. Cross-host clock skew is uncalibrated, short stalls may be missed, metric labels stay separate and node counters are deduplicated. Per-job inspections/server-state/resources JSONs retain every field and explicit limits.

## Assessment and next experiment

Close this non-improving chunk interaction; keep the accepted fresh 4096 control. A distinct native prefill routing comparison is justified by the sampled queue excursions and near-zero cache hit, with no prediction of a speedup. The pinned 0.3.2 parser/Rust enum support power_of_two, which chooses between workers using native load rather than fixed alternation. Reject unsupported shortest_queue and do not borrow newer experimental-router semantics. Prepare an equally observed fresh round_robin/power_of_two pair at fixed chunk 4096/N54, unchanged model/protocol/output gates. Actual native policy activation and full run acceptance must be verified; useful >=1% gains need independent confirmation.

All pair charges reconcile against the published ledger: Used **38396.869 SU**, Balance **25603.131 SU**, no In Doubt or outstanding local maxima. Internal headroom **12603.131 SU** under unchanged 51000 campaign cap/13000 buffer, before any new reservation. [Accounting evidence](pair-accounting.json). Own PBS queue is empty at this review; five H200 jobs remain Priority-pending. No official package, authentication or background AI change.
