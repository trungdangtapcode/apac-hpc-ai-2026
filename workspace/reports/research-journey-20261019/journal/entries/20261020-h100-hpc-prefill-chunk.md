# H100 HPC-Ops prefill chunk interaction: actual submissions

Updated 2026-10-20T09:30:58.728352+00:00. No new model score is available. The dense-kernel search is closed at native defaults: **132-SM DeepGEMM remains**, with no Triton or per-shape SM patch deployed. All negative/mixed cases are retained. [240-case native budget screen](../deepgemm-sm-screen-20261020/RESULTS.md), [160-case boundary screen](../deepgemm-sm80-20261020/RESULTS.md), [160-case TP4 prefill comparison](../fp8-prefill-tp4-20261020/RESULTS.md).

| Job | Status at query | Prefill | Decode | N | Allocation |
|---|---|---|---|---:|---|
|222281.pbs111|R|HPC-Ops, chunk 4096|HPC-Ops, unchanged|54|16 H100, <=45 min|
|222282.pbs111|H|HPC-Ops, chunk 8192|Identical|54|16 H100, <=45 min|

The second depends on **afterany:222281**, verified by the scheduler. No overlapping allocation. Both use the same uniform resource sampler, phase markers, full 60/120/30 protocol and 4000/200 workload, FP8 checkpoint/BF16 KV, topology and output checks. Candidate worker inverse-diffs exactly to control after reverting only prefill chunk 8192→4096. No official accuracy claim. [Receipts](pbs-receipts.json), [latest PBS](live-pbs.txt), [predeclared hypothesis/thresholds/source evidence](PLAN.md), [frozen validation](validation.json).

The older H100 chunk 8192 trial used **auto prefill**, applying HPC-Ops only to decode. The new HPC-Ops-prefill8192 interaction is distinct. Compare the fresh equally observed pair, not H200 or old unobserved peaks. A useful >=1% pair gain needs all local gates and later independent confirmation; failure/loss closes this exact setting without an unchanged retry or blind chunk/load growth.

## What to collect and inspect next

Use the existing full-model PBS collector only after each terminal state, write collect-JOBNUMBER.json into this directory, then run review-pbs.py. It checks sealed payload/protocol/SLA/error/short/12-long gates and compares actual resolved ServerArgs with observed 222049, allowing only random seeds plus candidate prefill 4096→8192. It explicitly requires HPC-Ops preflights, unchanged decode attention/MNNVL ranks, BF16 KV and inference-mode policy. It writes a paired comparison only if both full local reviews pass. This prepared reviewer has syntax/static validation only; no future result is implied.

Inspect uniform hardware/server samples and all 16 separate diagnostic rank traces as well. Use existing observability tools with new run IDs, phase manifests, actual UUID/role/host mapping, field-support and coverage checks. Do not apply a historical hardcoded inspector without adapting its job list. Cross-node clock skew remains uncalibrated; deduplicate node counters. Profiles occur after scoring, do not add their traffic to the benchmark or treat summed kernel durations as critical-path fractions. The official >=99%-reference full-set accuracy remains unverified.

## Credit and other queue

Pre-submit publication queried 2026-10-20T09:29:00.721061+00:00: Used **37439.430 SU**, Balance **26560.570 SU**, In Doubt **0.000 SU**. Last completed micro 222279 estimated 35.271111 SU is unposted, so retain its whole 170.666667 maximum in addition to the pair's 3072 maximum. Conservative outstanding bound **3242.666667 SU**, internal headroom **10317.903333 SU**, unchanged 51000 campaign cap/13000 buffer. [Reconciliation proof](prior-accounting.json), [pre-submit ledger](pbs-pre-submit.txt). Prepayment is not deducted twice. Future credit claims require a fresh query.

H200 24990/24928/24962/24964/24965 are all Priority-pending, exactly five active jobs; no cancellation or sixth job. [Actual queue](live-slurm.txt). Serving bests are unchanged: H200 3022.034919 and H100 2433.019859 good output tokens/s, with platform/replication/official-quality limits in CURRENT. No package, authentication or background Codex change. Git source/evidence captures are explicit; external large artifacts still need separate off-host copy.

## Completed control review — 2026-10-20T09:54:34.952862+00:00

Control **222281** passes full local protocol/runtime/output/SLA gates: **2401.577649 good output tokens/s**, 1482/1509 joint requests (**98.210736%**), zero request errors/cancellations, twelve long-context checks passed. TTFT mean 741.246 ms, p99 **3452.047 ms**, maximum 4586.645 ms; ITL mean 18.180 ms, p99 **19.072 ms**, maximum 21.014 ms. There are 21 TTFT breaches and 6 ITL breaches with no overlap. TTFT p99 exceeding 3000 ms is compatible with the contest's per-request joint 90% pass rule; it is a separate diagnostic, not an extra gate. [Strict result](222281.pbs111-review.json), [tail/log/profile inspection](222281.pbs111-inspection.json).

This is +0.262% over earlier observed 222049 (2395.311), a descriptive control repeat, not a new optimisation. The old unobserved 2433.020 peak differs in observer settings. Compare chunk 8192 only against this equally observed fresh control after its own full review; at the latest query 222282 is still running. No candidate score is claimed.

### What was collected and inspected

- Frozen payload, terminal seal, exact role ServerArgs, BF16 KV, HPC-Ops/attention/MNNVL rank proof and short/long outputs all checked. All 16 sealed post-score CPU/GPU traces contain actual kernels; separate diagnostic requests/control responses inspected. Profile starts return 200, but all three stop calls return 500 after bounded captures. ASGI stack traces point to stop_profile_async after scoring, not ranked generation. Do not label the logs error-free. [Flagged transport/runtime lines](222281-transport-log-review.json).
- Hardware/server samples verify 16 distinct GPU UUIDs and 24/25/25 scored samples for prefill 0/prefill 1/decode. Mean GPU activity 91.42%/85.21%/99.125%; mean power 646.85/609.58/410.11 W; sampled VRAM 76710/76706/78000 MiB. These are sample-weighted activity/memory quantities, not FLOPS/bandwidth efficiency or a causal bottleneck. [Verified resource coverage](222281-resources.json).
- New offline phase-bounded server-value reader retains complete metric labels. Decode running-request median 47, p95 50, max 51; sampled queue 0 and KV token-usage mean 0.2332. Prefill queue mean 0.333/0.92, maxima 3/17 across 24/25 five-second samples; their running-request means 1.208/1.56. Whole-deployment sparse logs have different distributions because they mix startup, warmup and diagnostics. Inflight was **NOT COLLECTED** by the current whitelist. Clock skew is uncalibrated, short spikes may be missed and node counters must be deduplicated. [Gauge values and missing-field limits](222281.pbs111-server-state.json).

### Assessment and next decision

Preserve the accepted fresh control and its tail/resource evidence now, rather than wait for the whole pair. Candidate 222282 must finish and pass independently. Prefill samples show some worker imbalance/queue excursions; cache hit is near zero, but these observations do not prove routing is the bottleneck. While the chunk candidate runs, inspect exact native queue-aware router policy support and earlier policy trials before planning another distinct candidate. Do not repeat closed kernels, infer health from missing inflight data or change frozen jobs.

Allocated walltime 14:11 estimates **484.124444 SU**, not yet posted in the retained 09:49 publication. Prior micro 35.271 SU does reconcile; publication Used **37474.701**, Balance **24989.299**, In Doubt **1536** SU. Keep completed-control max 1536 plus running-candidate max 1536, **3072 SU** bound, internal headroom **10453.299 SU** under unchanged 51000 cap/13000 buffer. Prepaid In Doubt is already withheld from Balance; no double deduction. H200 five jobs remain Priority-pending. No official quality claim or submission package change.

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
