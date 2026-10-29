# Shallow EAGLE3 full N64 result: close the unchanged arm

Reviewed 29 October 2026, Vietnam time (UTC+7). Actual job **27238** completed **0:0 in 13 minutes 12 seconds on g1/g4**, using 16 H200. This is our measured candidate, not the organiser reference. All frozen payload checks and the exact independent submitted performance checker pass. Official model accuracy remains UNKNOWN.

## Question and controlled change

The older decode-only two-step/three-token short trial 25998 lost 4.74%, with low draft acceptance. Could a one-step/two-token draft avoid wasted work? New S98 changes only decode speculation relative to full native target-only 26949. Target-only P4+P4, D8/TP8/EP8, DeepGEMM prefill chunk 8192/breakable graphs, HPC-Ops/FlashInfer/MNNVL decode, FP8 target/BF16 activation and KV/page1, tokenizer batching off, N64 cold fixed 4000/200 seed 2026 and full 60/120/30 remain fixed. EAGLE3 uses top-k 1, unquantized draft, one step and two draft tokens. See PLAN.md, frozen SHA256SUMS and the definite submission receipt.

Actual prerequisite 27153 proves native argument resolution only; the full 27238 logs now separately prove actual model startup. Before startup the candidate independently replays the exact completed 26949 raw gate. Source analysis correctly requires all eight target verification graph captures and TP0 draft extend, and skips the unused intermediate draft-decode graph for steps=1. All-rank BF16 target/draft allocation, draft load/backend and MNNVL records pass. The unchanged same-architecture KV gate observes 188 prefill and 190 decode regions in 32 receipts across 16 ranks. Both actual semantic P/D routes pass. Explicit layer identity and decode head counts remain uncollected under the exact existing page1 exception; no exception was widened.

## Full performance result

| Metric | Target-only control 26949 | Shallow candidate 27238 |
|---|---:|---:|
| Good output throughput, tokens/s | 3034.761104 | 2971.628430 |
| Joint latency SLA, percent of all requests | 98.627968 | 98.595354 |
| Total / good requests | 1895 / 1869 | 1851 / 1825 |
| Mean / p95 TTFT, ms | 1128.133 / 1423.391 | 1056.422 / 1386.492 |
| Mean / p95 request-mean ITL, ms | 14.979 / 15.147 | 15.776 / 17.084 |
| Errors / cancellations | 0 / 0 | 0 / 0 |
| TTFT / ITL breaches | 26 / 0 | 26 / 0 |
| Local smoke / retrieval | 7/8 / 12/12 | 7/8 / 12/12 |

The candidate is **2.080318% slower** in good throughput. TTFT improves slightly but ITL worsens; the joint contest metric does not improve. No new best, package promotion or official accuracy pass is claimed. Known strict token-ID comparison failures 25797/25862 remain retained.

## Inspection beyond the score

All 72 sampled role-server polls return HTTP200. No selected transport errors or Python tracebacks appear in the three worker logs. Within the first-to-last profiling-request start envelope, 24 decode samples show mean 52.25 running requests, zero sampled decode queue and 0.12 KV token usage. Decode GPU activity averages 93.76%, versus 100% in the control; sampled VRAM is 131.875 GiB per decode GPU. Both prefill roles have occasional queue spikes to 22. These are sparse five-second observations, not a kernel bottleneck attribution. Host clocks are uncalibrated and request-start envelopes exclude final drain.

Among all 196 decode log entries with at least 48 running requests, the unweighted mean displayed acceptance length is 1.2464 (range 1.19–1.30), and mean displayed acceptance rate is 0.2464. This filter includes warmup and profiling, is not token weighted, and is not an exact phase-aligned acceptance estimate. It supports the low-acceptance hypothesis, but it does not isolate draft kernel overhead. Heavy kernel profiles and exact generated token IDs were not collected.

Actual allocation occupancy is 3.52 GPU-hours, separate from the maximum 4.533334 GPU-hour reservation. No PBS SU was used. This is allocation arithmetic, not a metered site charge.

## Decision and preservation

Close this unchanged one-step/two-token arm under the predeclared >1% useful gain rule. Do not repeat it or sweep larger depths without new evidence. Separate source investigation has closed the continuous-decode-step knob for this pinned image: the complete Python package declares it but has no consumer. A distinct transfer/admission investigation may proceed; an optional source investigation is not a ready benchmark.

Raw AIPerf exports, per-request records, logs, telemetry, output checks, actual frozen payload and terminal accounting are sealed in runs/27238/artifact-manifest.json. comparison.json and ../h200-full-load-review-20261026/review-27238.json retain machine-readable review. Source hashes and all failed prior branches remain. The Git archive preserves safe code and recovery manifests; large object bytes require separate off-host copying.
