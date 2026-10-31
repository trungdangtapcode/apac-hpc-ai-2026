# Recover chunk performance, then isolate the remaining runner gap

Question: did the earlier H100-recipe port lose on H200 because the prefill
runner and chunk were changed together? Prior current-native H200 27783 used
HPC-Ops/chunk 4096 at N64 and scored 2721.815800 good tokens/s with large prefill
queues. Prior same-day 27777 used DeepGEMM/chunk 8192 and scored 3038.022907. The
H100 6144/8192 variants were valid near-flat/losing measurements; they were not
advertised as H100 winners. Different hardware/load/runner interaction justified
two new ports, rather than unchanged repeats of the old source-platform loss.

27804 chunk 6144 and 27806 chunk 8192 now complete 0:0, independently passing all
raw fixed-workload/source/runtime/physical KV/two-semantic-route/output gates.
Both retain 16 H200/g1/g4/N64, both-phase HPC-Ops, FA3 prefill, FlashInfer/MNNVL
decode, topology, precision, cache, polling and dense decode graphs 1..64. Their
strict raw runtime gate checks actual chunk-derived prefill capture maximum and
buckets on all relevant roles. Full 60/120/30, requested 4000/200, seed 2026 and
all-request joint SLA thresholds remain unchanged.

| Job / chunk | Good tokens/s | Versus HPC 4096 | Versus H200 incumbent |
|---|---:|---:|---:|
| 27804 /6144 |2821.884862|+3.676555%|-7.114431%|
| 27806 /8192 |2900.606831|+6.568815%|-4.523207%|

The hypothesis is partially supported: larger chunks recover performance while
holding the HPC-Ops runner fixed, including native graph consequences. Prefill
mean running requests increase from 2.0000/1.9583 to 3.0000/3.0000, sampled queue
means drop 7.3750/4.4583 to 2.1667/1.0000 and decode running mean grows 44.1667 to
48.5833 between 4096 and 8192. Mean/p95 TTFT 1591.493/2017.559 falls to 1368.992/
1561.224 ms; request-mean ITL 14.872 falls to 14.648 ms. These are associated serving
observations, not direct per-request queue/compute/transport decomposition.

The 8192 comparison now holds chunk and all graph settings fixed between 27806
and 27777. The argument audit permits only prefill runner, its inactive
speculative-runner fallback field and generated seeds; decode is unchanged
apart from seed, no draft is loaded. The measured HPC-Ops port still loses
4.523207%. This supports retaining DeepGEMM for the current deployment, not a
universal kernel-speed ranking. There is one run per candidate, same-day old
controls, and unmeasured host/cache state. No winning repeat or promotion.

27804 has 1746/1776 good (98.310811%), 27806 has 1790/1820 good (98.351648%); both 30 TTFT/
0 ITL breaches, zero scored errors/cancellations, smoke 7/8 non-regression and
retrieval 12/12. Official full-set quality remains UNKNOWN. Role logs show no
selected transport/OOM markers or Python tracebacks; no failed semantic setup
responses. Each has 72 successful metric polls and 24 samples per role over 16 GPU
UUIDs. Decode sampled activity 100% in both; VRAM 130.811/131.090 GiB per GPU.
GPU activity, VRAM and token occupancy differ; sampled CPU/power/clocks/thermal
values and full raw p50/p95/p99/max are retained. Heavy/per-thread/Xid/throttle
profiles and actual token IDs remain uncollected; host clocks uncalibrated.

Actual occupancy 27804=3.000000 GPU-hours, 27806=3.062222 GPU-hours, total 6.062222
versus maximum 9.066667, zero PBS SU. All terminal raw inputs/requests/exports,
frozen payloads, telemetry and scheduler evidence are sealed. Git capture has
recovery manifests; external large objects require separate off-host copying.

Decision: keep the current H200 incumbent and close this unchanged chunk arm;
no blind larger-chunk extension or repeat. Own queue is empty in the dated
comparison audit. The owner's distinct-four request is not fully satisfied:
two additional qualified configurations were admitted/reviewed; two slots remain
unfilled. Do not inflate this count using controls, repeats or load points.
No H100 authentication/spending, HPC, automation or published PPTX/ZIP change.

[Complete result and comparison audit](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-hpc-chunk-transfer-20261031/RESULTS.md).
