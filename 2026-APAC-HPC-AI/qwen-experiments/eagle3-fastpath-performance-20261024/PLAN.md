# Fast-default EAGLE3 performance exploration

## Research question

Can EAGLE3 improve measured N=64 serving throughput under the fast H200 defaults while retaining the existing strict SLA and readiness gates? This is an unranked performance-only comparison. It does not resolve the known exact-token discrepancies or establish official model quality.

## Prior evidence

- Control job 25930 ran with deterministic inference enabled. Its N=64 raw profile recorded 0 good requests and 0 goodput under TTFT <= 3000 ms and ITL <= 20 ms. The profile's mean ITL was 29.145 ms. Its summary helper path failed after the raw profile, so smoke/retrieval did not run and the run is not a valid completed control score. The deterministic runtime disabled the FlashInfer MNNVL fusion path; that is a plausible performance-mode concern, not proof of the cause of the observed SLA failure. Review: `research-review-25930-20261024`.
- Fast-default target-only job 25863 used `enable_deterministic_inference=False`, FlashInfer sampling, custom all-reduce enabled by native default, prefill fusion `auto`, decode fusion `mnnvl`, P workers capped at 64, and D cap 256. Its completed short screen passed existing gates: 636 requests, 0 errors/cancellations, good-request fraction 0.952830, goodput 13.980732 requests/s, and 2796.146 good output tokens/s (`200 * goodput`). It also passed 7/8 smoke and 12/12 retrieval checks. This is historical feasibility evidence, not a matched new-run result or a causal speedup.
- Fast-default EAGLE3 job 25797 passed all-rank BF16 runtime, 190-region geometry, and two semantic P/D paths. Its strict 1,600-ID comparison failed; this remains a known quality limitation, not an official quality verdict. Its historical prefill cap was 48, so its runtime replay is not proof of the new P64 cap.
- Exact 1,600-ID comparison for candidate job 25862 also failed. No exact-ID comparison is run in this performance protocol.

## Controlled pair

S59 is target-only. S60 adds EAGLE3 (two steps, top-k 1, three draft tokens) and is independently gated against the reviewed actual S59 control before model startup. Both share the same NIXL transport, model, source wrapper, topology, P8-TP4 two-worker layout, P max-running-requests 64 per worker, D8-TP8-EP8 with request cap 256, BF16 runtime/KV allocations, chunked prefill 8192, disabled prefill CUDA graphs, and full decode graphs for batch sizes 1 through 64. Resolved fast defaults must show deterministic mode false, FlashInfer sampling, custom all-reduce disable false, decode MNNVL fusion, and prefill fusion `auto`. S60's root-supplied S59 binding is fail-closed and must be filled only from a reviewed successful actual S59 run.

The measured protocol is one N=64 AIPerf point: 20-second warmup, 40-second measurement, 30-second grace, fixed 4000 input / 200 output tokens, seed 2026. SLA remains a strict 90% good-request fraction; errors and cancellations must be zero. Keep the 7/8 smoke floor with no known regression and all 12 retrieval checks. Neither arm runs the known failed exact-ID diagnostic.

## Decision and limits

The deterministic-mode branch is stopped because 25930 produced zero goodput and would predictably block the same screen. This is a controlled change to fast defaults, not a relaxed SLA. Candidate 25797's exact-token failure remains preserved. Any measured throughput comparison is exploratory and quality remains UNKNOWN; do not promote an EAGLE speedup unless the quality issue is separately resolved. No score, quality verdict, GPU job, or submission is created by this source-preparation work.

## Source and CPU evidence

Runnable bundles: `serving-tuning-10/s59-h200-fast-default-control` and `serving-tuning-10/s60-h200-fast-default-eagle3`. CPU fixture replay uses retained actual runs 25863 and 25797. The 25797 replay explicitly passes its historical P48 cap as a fixture override; it does not simulate or claim new P64 GPU evidence.
