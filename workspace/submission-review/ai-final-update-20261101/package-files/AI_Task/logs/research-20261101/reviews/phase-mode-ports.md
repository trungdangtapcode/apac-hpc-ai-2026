# Phase-specific inference mode is compatible but gives no useful goodput gain

All three allocations completed 0:0 and independently passed their full local
raw protocol, source/runtime, physical KV, both semantic P/D paths and output
gates. All use 16 H200 on g1/g4 at N64, with the current DeepGEMM/chunk 8192
prefill and HPC-Ops/FlashInfer/MNNVL decode recipe. Provider choice is the only
intended intervention; source and context preflight code is identical.

| Job | Prefill provider | Decode provider | Good output tokens/s | Versus fresh explicit control |
|---|---|---|---:|---:|
| **27826** | no_grad | no_grad | **3039.167093** | Reference |
| 27828 | no_grad | inference_mode |3039.356215|+0.006223%|
| 27830 | inference_mode | no_grad |3043.141258|+0.130765%|

Both differences are below the prospective 1% useful-gain gate. The prefill-only
point is not a new best: the retained historical H200 repeat mean 3044.400475
remains a separate series, and larger individual observations also exist. A
fresh control is the denominator here, not a selected old peak or low repeat.

**Decision:** retain the current H200 recipe and native no_grad provider;
close these exact H200 phase arms without an unchanged repeat, combined-mode
sweep, default change or submission promotion. The full source-intervention
verification request is now measured: 27804/27806 chunk ports and 27828/27830
phase ports. 27826 is extra control and is not counted as another candidate.
These are four H100-derived settings tested on H200, not four H100 winners or
byte-identical H100 full deployment reproductions.

## Actual activation was checked, not inferred from timing

| Native role-level provider preflight | Control 27826 | Decode-only 27828 | Prefill-only 27830 |
|---|---|---|---|
| Prefill 0 | False | False | True |
| Prefill 1 | False | False | True |
| Decode 0 | False | True | False |

Each role verifies the exact common.py and scheduler.py hashes, native resolved
provider boolean, grad disabled inside DynamicGradMode, expected inference mode
inside context and restoration after exit. Exported flags precede server import
and are inherited by the unchanged server launch. The independent raw-log gate
rejects missing, duplicate or wrong phase receipts. Actual distributed graph,
KV/NIXL/cache/rank allocation, both semantic routes and output checks also pass.

The frozen worker audit differs only in phase flag values. Resolved ServerArgs
for all roles differ only in generated engine seeds. A ServerArgs dump alone
would not establish provider activation: the separate source/context receipts
are required. These receipts are role-launch preflights, not a steady-state
per-rank or kernel trace; preserve that limitation rather than overclaim it.

## Raw request and latency results

| Measure | 27826 control | 27828 decode mode | 27830 prefill mode |
|---|---:|---:|---:|
| Joint qualifying / all profiling requests |1873 /1899|1876 /1902|1876 /1902|
| Joint qualifying fraction, % |98.630858|98.633018|98.633018|
| TTFT mean / p95, ms |1123.231 /1391.127|1116.088 /1361.411|1118.628 /1289.030|
| Request-mean ITL mean / p95, ms |14.991 /15.163|15.004 /15.185|14.986 /15.141|
| TTFT / mean-request ITL breaches |26 /0|26 /0|26 /0|
| Scored errors / cancellations |0 /0|0 /0|0 /0|
| Small non-regression / retrieval |7/8 and 12/12|7/8 and 12/12|7/8 and 12/12|

The prefill-only run has a lower observed TTFT p95, by 102.097 ms, and shorter
sampled prefill queues; this single observation does not establish a robust
tail-latency gain or explain its cause. The TTFT breach count remains 26 in
every arm. Mean latency and goodput differences are small; do not describe a
0.130765% score difference as a material speedup.

Each raw full 60/120/30, requested 4000/200, seed 2026, cold-prefix client protocol
passes independently. Official good output tokens/s is exported Goodput (req/s)
times 200. At least 90% of all requests must jointly meet TTFT <= 3000 ms and their
mean ITL <= 20 ms; errors stay in the denominator. Local sanity/retrieval checks
do not certify the organiser's 99%-reference model quality. Full official
accuracy remains UNKNOWN, with no new quality claim.

## Resource and runtime inspection

| Profiling-request-start-envelope sample | Control | Decode mode | Prefill mode |
|---|---:|---:|---:|
| Decode running requests, mean / max |50.0833 /56|50.0417 /54|50.4583 /54|
| Decode queue max, requests |0|0|0|
| Prefill 0/1 mean queued requests |1.0000 /0.7500|1.4583 /1.0000|0.3333 /0.0833|
| Decode mean GPU activity, % |100|100|100|
| Decode mean VRAM, GiB/GPU |131.204|131.244|131.180|
| Decode mean KV token usage |0.1200|0.1192|0.1200|
| Server metric polls, successful / inspected |72 /72|72 /72|72 /72|
| Actual allocated GPU-hours |3.226667|3.271111|3.106667|

All three have 24 five-second samples per role covering 16 distinct GPU UUIDs.
Role logs have no selected transport/OOM markers or Python tracebacks and no
failed semantic setup responses. CPU busy estimates are approximately 12.5%
on g1 and 12.9% on g4; they are host averages, not scheduler-thread demand.
Power, temperature, clocks and GPU memory-activity distributions were collected,
inspected and retained with full p50/p95/p99/max request latency and role state.
GPU activity, sampled VRAM and KV token occupancy are different quantities and
do not identify a causal bottleneck. Missing per-thread/heavy kernel/Xid/
throttle-reason profiles and actual output token IDs remain uncollected, not
zero or healthy. Five-second sparse samples, uncalibrated host clocks and the
first-to-last request-start envelope exclude exact phase/drain coverage.

Actual occupancy is 9.604444 GPU-hours versus 13.600000 maximum; zero PBS SU.
The new control completes 12:06, decode-only 12:16 and prefill-only 11:39, all 0:0.
These are single sequential allocations, not a statistically powered repeated
experiment. Source H100 trials used both-HPC-Ops/chunk 4096/N54; the mode setting
alone was ported into the stronger current H200 base. Thus comparisons with
historical H100 scores are contextual, not pure GPU speed ratios.

All three terminal runs are sealed with raw requests, exports, synthetic inputs,
logs, telemetry, frozen payload and scheduler accounting. Git captures recovery
manifests; large external object bytes still require a separate off-host copy.
The fresh queue snapshot and exact comparisons are in comparison.json. No new
GPU job, H100 authentication/spending, HPC edit, schedules, background Codex,
published PowerPoint/ZIP change or organiser upload follows automatically.

Comparison, activation matrix and accounting (retained source: `comparison.json`),
control extended review (retained source: `result-27826.json`),
decode extended review (retained source: `result-27828.json`),
prefill extended review (retained source: `result-27830.json`),
four-port register (retained source: `distinct-port-register.json`).
