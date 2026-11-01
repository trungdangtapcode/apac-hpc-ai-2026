# Larger chunks help HPC-Ops prefill, but DeepGEMM remains the H200 choice

Jobs **27804** and **27806** both completed and independently passed their full
local raw workload, source/runtime, physical KV, two semantic P/D paths and
output checks. All comparisons below use **16 H200 on g1/g4 at N64**. These are
two additional distinct ports; the remaining two slots requested by the owner
have not been filled with qualified configurations.

| Job | Prefill MoE runner | Prefill chunk, tokens | Good output tokens/s | Versus H200 incumbent |
|---|---|---:|---:|---:|
| 27777, prior control | DeepGEMM | 8192 | **3038.022907** | Reference |
| 27783, prior H100-recipe port | HPC-Ops | 4096 | 2721.815800 | -10.408319% |
| **27804** | HPC-Ops | **6144** | **2821.884862** | **-7.114431%** |
| **27806** | HPC-Ops | **8192** | **2900.606831** | **-4.523207%** |

Decode remains HPC-Ops, FlashInfer attention and MNNVL, with two TP4/EP1
prefills, one TP8/EP8 decoder and round-robin routing. All retain FA3 prefill
attention, the pinned FP8 target and image, BF16 KV, native Enroot, NIXL, cache
policy, polling 1, decode cap 256 and dense decode graphs 1..64.

## What this resolves

The preceding 27783 versus 27777 comparison changed both prefill runner and
chunk size. That comparison alone could not isolate their contributions.
Holding HPC-Ops fixed, chunk 6144 improves goodput 3.676555% and chunk 8192 improves 6.568815% over 4096; they recover part of its performance gap.
At 8192 on both sides, 27806 still loses to DeepGEMM 27777. The exact native
argument audit permits only the intended runner and generated-seed differences,
plus the automatically resolved speculative-runner fallback field; speculation
remains disabled and no draft is loaded. All prefill and decode graph settings
are identical in this same-chunk runner comparison.

The within-HPC chunk comparisons include native dependent prefill graph
maximum/buckets. The strict runtime reviewer verifies actual 6144/8192 prefill
capture ranges, all ranks, source/module receipts and both semantic paths.
Do not describe this as a batching-only experiment with graph sizes held fixed.

**Decision:** retain DeepGEMM prefill/chunk 8192 and the current decode deployment.
The new runs improve a losing branch, not the incumbent. Do not promote an
HPC-Ops prefill default, buy unchanged repeats or assume still larger chunks
must continue improving. A useful gain over the incumbent would need a fresh
independent matched confirmation; none is established here.

## Latency, request validity and diagnostics

| Measure | 27783 HPC 4096 | 27804 HPC 6144 | 27806 HPC 8192 |
|---|---:|---:|---:|
| TTFT mean / p95, ms |1591.493 /2017.559|1462.905 /1792.998|1368.992 /1561.224|
| Request-mean ITL mean / p95, ms |14.872 /15.033|14.734 /14.857|14.648 /14.803|
| Joint qualifying requests / total |1689 /1717|1746 /1776|1790 /1820|
| Joint qualifying fraction, % |98.369249|98.310811|98.351648|
| TTFT / mean-request ITL breaches |28 /0|30 /0|30 /0|
| Scored errors / cancellations |0 /0|0 /0|0 /0|
| Small output non-regression / retrieval |7/8 and 12/12|7/8 and 12/12|7/8 and 12/12|

The fixed full 60/120/30, requested 4000/200, seed 2026 and cold-prefix protocol
passes against actual client exports. Good output tokens/s equals exported
AIPerf Goodput (req/s) times 200. The joint >= 90% gate uses TTFT <= 3000 ms and each
request's mean ITL <= 20 ms with all requests in the denominator. Official full-set
accuracy remains UNKNOWN; small checks are not 99%-reference certification.

Five-second samples in the first-to-last profiling-request-start envelope show
the following associated changes; they are not direct per-request time measures.

| Sampled state | HPC 4096 | HPC 6144 | HPC 8192 |
|---|---:|---:|---:|
| Prefill 0/1 mean running requests |2.0000 /1.9583|2.5000 /2.7500|3.0000 /3.0000|
| Prefill 0/1 mean queued requests |7.3750 /4.4583|5.0000 /2.4167|2.1667 /1.0000|
| Decode mean running requests |44.1667|46.5417|48.5833|
| Decode mean GPU activity, % |100|100|100|
| Decode sampled VRAM mean, GiB/GPU |130.631|130.811|131.090|

Larger chunks coincide with more active prefill requests, shorter sampled
prefill queues, lower first-token latency and more running decode requests.
This supports the chunk/serving interaction hypothesis. It does not establish
which compute, communication or waiting component accounts for the change;
no direct time decomposition or new heavy kernel profile was collected.
At 8192, HPC-Ops has lower mean ITL than DeepGEMM control but a longer TTFT, so
neither metric alone determines the ranking.

Each new run has 24 samples per role covering 16 distinct GPU UUIDs, 72 successful
server metric polls, no selected transport/OOM markers or Python tracebacks in
the three role logs, and no failed semantic setup responses. CPU, GPU memory
activity, power, temperature and clocks were inspected; complete distributions,+p50/p95/p99/max raw request latency and sampled server states are preserved in
the per-job JSONs. GPU activity, sampled VRAM and KV token usage are different
quantities. Sparse sampling and uncalibrated host clocks exclude exact phase/
drain coverage. Per-thread demand, Xid/throttle reasons and authoritative
generated token IDs remain uncollected; no causal kernel claim is made.

## Cost, preservation and current scope

27804 completed 0:0 in11:15, 27806 completed 0:0 in 11:29. Their actual occupancy
is 6.062222 GPU-hours combined, versus 9.066667 maximum; zero PBS SU. Old controls
are from the same day, not interleaved concurrently; node/cache state and
generated engine seeds remain limitations. One observation per setting does
not establish statistical significance or a universal backend ranking.

The source H100 6144/8192 variants were near-flat/losing on that platform, not
H100 winners. These new H200 measurements test their missing current-native
runner/load interaction. They do not create two more fictional high-performing
H100 recipes. The request for four distinct additional ports is still only
partly fulfilled: two were admitted and reviewed, two qualified slots remain
unfilled. No blind replacements are submitted merely to reach four.

Raw requests, exports, synthetic inputs, frozen payloads, role logs, telemetry
and scheduler accounting are sealed. Git retains recovery manifests; external
large objects require a separate off-host copy. No H100 authentication/spending,
HPC change, schedules, background Codex, published PPTX/ZIP change or organiser
upload is implied by this review. Fresh queue and exact percentages/costs are
in the comparison JSON.

Exact comparison and argument audit (retained source: `comparison.json`),
27804 extended review (retained source: `result-27804.json`),
27806 extended review (retained source: `result-27806.json`),
source plan and H100 evidence (retained source: `PLAN.md`).
