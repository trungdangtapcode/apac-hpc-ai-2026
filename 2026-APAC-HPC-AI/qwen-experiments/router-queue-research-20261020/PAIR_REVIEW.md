# Native prefill routing: completed comparison

Both 222302 (round-robin control) and 222303 (power-of-two candidate) finish exit 0 and pass the full local protocol, runtime/source/payload, joint latency/error and output gates. This is one equally observed N54 pair on H100, with both-phase HPC-Ops and prefill chunk 4096. Official full-set accuracy is still unverified.

| Metric | 222302 round-robin | 222303 power-of-two |
|---|---:|---:|
| Good output tokens/s | 2396.201520 | 2279.626751 |
| Joint good / requests | 1480 / 1507 | 1410 / 1432 |
| Joint SLA, % | 98.2084 | 98.4637 |
| Mean TTFT, ms | 749.170 | 1065.117 |
| TTFT p99, ms | 3457.303 | 3522.852 |
| Mean ITL, ms | 18.183 | 17.768 |
| ITL p99, ms | 19.201 | 18.760 |
| Raw TTFT / ITL breaches, requests | 21 / 6 | 22 / 0 |
| Errors / cancelled, requests | 0 / 0 | 0 / 0 |
| Long-context output checks | 12 / 12 | 12 / 12 |
| Allocated walltime | 14:44 | 11:56 |
| Estimated charge, SU | 502.897778 | 407.324444 |

Power-of-two loses **4.865% goodput**. Its mean ITL improves 0.415 ms, but mean TTFT rises 315.947 ms; a larger passing-request percentage does not mean more useful requests per second. Retain round-robin, close this exact default policy trial and do not repeat it unchanged. This is not a universal ranking of routing algorithms. H100 peak 2433.019859 and H200 peak 3022.034919 remain separate and unchanged.

## What was inspected

All scored request records, output checks, exact three worker ServerArgs, native main-router startup and common hash/enum preflight were inspected. All sixteen sealed CPU/GPU diagnostic traces per run are present; separate post-score requests succeed 372/372 and 352/352. Start-profile calls return 200, and all three stop-profile calls return 500 after bounded captures in both jobs, matching the previously recorded post-score stop-profile limitation. Do not describe these logs as error-free.

The candidate startup uses `PowerOfTwo { load_check_interval_secs: 5 }`, not a unit-like Debug enum. [Preserved reviewer correction](ROUTER_REVIEW_CORRECTION.md) explains the exact acceptance and corrects the earlier separate 30-second monitoring interpretation. Main port 8000 explicitly configures the phase override; default cache-aware registry labels and worker-local load_balance_method warnings describe other paths. Per-dispatch decision counters were not collected, so configuration proof cannot attribute individual assignments.

Five-second scored hardware/server sampling verifies sixteen disjoint GPU UUIDs and 24–25 samples per role per run. Mean prefill-0/prefill-1/decode GPU activity is 87.94/91.27/96.575% for control and 85.46/89.92/98.425% for candidate. Mean decode running requests decrease 45.88 to 42.16; decode sampled queue stays zero. Mean prefill queues increase from 0.60/0.417 to 2.08/3.125 requests, with observed maxima 8/2 versus 17/9. Mean decode KV token occupancy is 0.2248/0.2264 and is distinct from sampled VRAM (78000/77808 MiB). Near-zero prefix hit remains. These associations support rejecting this policy at this setting; they do not establish a causal bottleneck or dispatch bias.

Resource records also retain role VRAM, memory activity, power, temperature, clocks and deduplicated node CPU/memory/interface counters. Their five-second cadence aliases short events; cross-host clock skew is uncalibrated. Inflight is NOT_COLLECTED, no missing metric means zero, GPU activity is not FLOPS/bandwidth efficiency, and summed post-score kernel time is not scored wall time. Whole-run batch log distributions mix phases; scored state comes from the phase-bounded sampler.

## Decision and next hypothesis

The prior larger-chunk 8192 trial lost 0.7814%; this routing trial loses 4.865%. Keep the accepted 4096/round-robin implementation. A bounded metadata scan found no retained H100 worker with chunk 2048; the old H200 23905 chunk2048 at a different implementation/load/hardware does not settle the both-HPC-Ops H100 interaction. A smaller prefill chunk might reduce individual prefill scheduling intervals and tails, but repeats transformer passes and may lose efficiency. Inspect the exact pinned defaults/derived graph range and prepare a fresh controlled 4096/2048 pair only after explicit validation and budget checks. No model-quality or precision relaxation, no blind load growth.

Both charges sum to 910.222222 SU and reconcile to the published 910.222 SU delta within rounding. Fresh Used 39307.091 SU, Balance 24692.909 SU, In Doubt 0, internal headroom 11692.909 SU under the unchanged 51000 cap/13000 buffer. [Accounting](pair-accounting.json), [published source](pbs-final-credit.txt).

## Reproduction and evidence

Read [PLAN.md](PLAN.md), definite [receipts](pbs-receipts.json), per-job `*-review.json`, `*-inspection.json`, `*-server-state.json`, `*-resources.json`, and collection pointers. The collected terminal snapshots preserve raw exports, frozen submitted payloads, profiles and evidence SHA-256 seals. The original reviewer rejection is retained. Git contains safe manifests and inline evidence; large external objects still need a separate off-host copy.

## Additional inspected node and transport evidence

Node-wide mean CPU busy percentages are 7.157/7.181 for control decode/prefill hosts and 7.069/7.236 for candidate. These are host aggregates, not per-worker thread saturation. Sampled available host memory remains about 1.96–2.00 billion KiB. Kernel-bypass RDMA traffic is not measured by IP interface byte counters, so zero sampled IB interface counters do not prove zero NIXL traffic. No whole-worker-log NIXL error-pattern or OOM match was found in this bounded scan; all three observed ASGI stacks per job occur in stop_profile_async after scoring. Worker-local load_balance_method warnings remain preserved and are not evidence that the main router override was ignored. Structured substring counts are in each `*-transport-log-review.json` and are not a universal log-health certificate.
