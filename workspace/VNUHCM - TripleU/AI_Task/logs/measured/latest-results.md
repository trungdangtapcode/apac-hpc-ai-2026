# Current AI results and recommended submission

Updated 2026-10-30T13:03:03.333733+07:00, Vietnam time (UTC+7).

**Submit the replicated native N64 target-only setting.** The highest complete local full pass is 3048.446289 good output tokens/s, but its +0.240921% matched cache difference is too small to establish a useful improvement. The three-run historical N64 mean is 3044.400475; later native control 26766 reproduces that level at 3045.501509. These are distinct measurement series.

| Evidence class | Job / setting | Good output tokens/s | Interpretation |
|---|---|---:|---|
| Reproduced operating choice | 25366 / 25373 / 25487, N64 | 3044.400475 mean | Three historical full deployments |
| Separate native full control | 26766, N64 | 3045.501509 | Full local pass; no causal launcher-gain claim |
| Fresh native cache control | 27376, N64 | 3041.119598 | Comparator for the cache candidate |
| Highest complete full local pass | 27378, prefill ChunkCache | 3048.446289 | +0.240921% versus 27376; no promotion |
| Recovered portable raw observation | 27145, N64 | 3055.330517 | Original job FAILED after client; not a whole-job pass |
| Separate H100 retained peak | 222048, N54 | 2433.019859 | Different hardware and configuration; do not pool |

AIPerf Goodput is measured in qualifying requests per second. Multiply its exported value by the fixed 200 output tokens to obtain good output tokens/s. For 27378 this is 15.242231445 requests/s × 200. Do not replace exported Goodput with total token throughput or divide successful counts by an assumed 120-second wall window.

## Highest complete run: exact configuration and metrics

Job 27378 completed 0:0 in 11:41 on g1/g4 with 16 H200. It uses two TP4/EP1 prefill roles on one node and one TP8/EP8 decode on the other. Prefill DeepGEMM, chunk 8192, FA3 attention and breakable graphs are retained. The single treatment disables prefill radix prefix caching and selects ChunkCache; physical active-request BF16 KV remains enabled. Decode stays HPC-Ops, FlashInfer attention, MNNVL collectives, full graph buckets 1–64, cap 256 and transfer polling interval 1. Model weights remain the official Qwen3-235B-A22B-Instruct-2507 FP8 target, with BF16 activation/KV. No EAGLE, dynamic tokenization or torch.compile.

| Metric | Unit | Control 27376 | Candidate 27378 |
|---|---|---:|---:|
| Good output throughput | qualifying output tokens/s | 3041.119598 | 3048.446289 |
| Joint latency success | good requests / all requests | 1874 / 1900 | 1879 / 1905 |
| Good fraction | % | 98.631579 | 98.635171 |
| Mean / p95 TTFT | ms | 1119.985 / 1332.727 | 1102.185 / 1380.071 |
| Mean / p95 request-mean ITL | ms | 14.991 / 15.166 | 15.028 / 15.226 |
| TTFT / ITL violations | requests | 26 / 0 | 26 / 0 |
| Errors / cancellations | requests | 0 / 0 | 0 / 0 |
| Local smoke / retrieval | passed cases | 7/8; no new regression / 12/12 | 7/8; no new regression / 12/12 |

TTFT means waiting time to the first token. Request-mean ITL means the average time between generated tokens within one request; the table reports the average and p95 across those request-level values. Every good request must jointly satisfy TTFT ≤3000 ms and request-mean ITL ≤20 ms. At least 90% of all requests, including errors in the denominator, must pass. Mean latency alone cannot certify this condition.

Candidate p95 TTFT and mean ITL are slightly worse despite the small goodput increase. One run per arm and different generated engine seeds do not establish a causal gain. Workload seed 2026 remains fixed. Actual all-rank cache classes, source bindings, physical KV, both semantic routes and frozen raw/output gates pass.

## Later branches and decisions

| Trial | Jobs | Result | Decision |
|---|---|---|---|
| Prefill dynamic tokenizer | 26951 / 26953 vs 26949 | +0.192% / +0.270% | Below useful-gain gate; retain default |
| Prefill FlashInfer, page 1 | 27077 vs 26949 | −6.385% | Lower throughput; retain FA3 |
| Shallow EAGLE decode | 27238 vs 26949 | 2971.628430 tokens/s; −2.080318% | Close unchanged treatment |
| Transfer polling 1 / 2 / 4 | 27270 / 27272 / 27274 | 3039.053 / 3028.280 / 3016.700 tokens/s | Keep interval 1 |
| Decode request cap 64 | 27365 vs 27270 | 3046.890454 tokens/s; +0.257879% | No promotion |
| Full model decode compile | 27383 | FAILED before AIPerf: native RoPE rejects fused KV argument | No score; unchanged compile blocked |
| C++ radix CPU prerequisite | 27506 | Completed 0:0, 95 s; JIT 26.605 s; CPU fixtures pass | No Qwen integration or serving-speed claim |

Sparse compile-off graph trial **27510 completed 0:0 in 13:15** and independently passes the full local gate at **3029.861122 good output tokens/s**, −0.370208% versus earlier control 27376. It has 1870/1896 good requests (98.628692%), zero errors/cancellations, smoke 7/8 without regression and retrieval 12/12. Twelve graph buckets reduce native logged capture memory from 1.15 to 0.36 GB per rank, but capture time changes only from 101.46–101.49 to 95.98–96.05 seconds. TTFT mean/p95 is 1102.404/1240.481 ms, request-mean ITL 15.136/15.324 ms. Keep dense graphs. This single observation has generated-seed, different-time and candidate startup-observer limitations. No further job is submitted by this delivery update.

## Portable replay and quality limits

Portable 27136 and 27145 completed both semantic P/D routes and the official GPU client, then ended FAILED in result-reader namespace/alias handling. Fixed readers passed actual compute-only job 27152 against both retained real datasets. The package includes those corrections. This does not rewrite original failed states or constitute a whole-allocation repeat after the repair.

The official full-set model-quality gate (at least 99% of the organiser's unchanged FP8 reference) remains UNKNOWN. Local smoke and retrieval do not certify it. No official ranking or global optimum is claimed.

All full runs above use closed-loop N64, requested 4000 input / 200 output tokens, seed 2026, cold prefixes, 60 s warmup / 120 s profiling / 30 s grace. Client-retokenized lengths can differ from requested counts; actual generated token IDs are not retained. Keep the official fixed ×200 multiplier and original gates.

Raw profiling JSONL, exports, configuration, submitted payloads, runtime/semantic evidence and selected role telemetry are provided in the new job directories and research reports. Large generated inputs.json, model weights and disposable caches are omitted. Historical raw originals remain in the research archive. Sparse five-second request-start-envelope telemetry does not prove a causal bottleneck; final drain, calibrated clocks, heavy kernel profiles, hot CPU threads and Xid/throttle reasons were not collected as a complete series.


## Final H200 verification — 31 October 2026

# Final H200 verification evidence — 31 October 2026


| Job | Change | N | Good output tokens/s | Control interpretation |
|---:|---|---:|---:|---|
| 27777 | Fresh H200 incumbent control; DeepGEMM prefill chunk 8192, FlashInfer attention | 64 | 3038.022907 | 98.6301% joint pass |
| 27779 | FA3 decode alternative against job 27777 | 64 | 2999.245473 | 98.5075% joint pass |
| 27781 | H100-derived HPC-Ops prefill and decode, chunk 4096, N54 load point | 54 | 2738.940099 | 98.9443% joint pass |
| 27783 | Same transferred recipe at N64; matched-load comparison against 27777 | 64 | 2721.815800 | 98.3692% joint pass |
| 27804 | HPC-Ops prefill chunk 6144; runner and chunk branch versus incumbent | 64 | 2821.884862 | 98.3108% joint pass |
| 27806 | HPC-Ops prefill chunk 8192; same-chunk runner comparison versus 27777 | 64 | 2900.606831 | 98.3516% joint pass |
| 27826 | Explicit no_grad control for phase-mode ports | 64 | 3039.167093 | 98.6309% joint pass |
| 27828 | Decode-only inference_mode port versus 27826 | 64 | 3039.356215 | 98.6330% joint pass |
| 27830 | Prefill-only inference_mode port versus 27826 | 64 | 3043.141258 | 98.6330% joint pass |

The native H200 recipe remains the selected operating choice. Full official quality remains unknown. See `research-20261101/README.md` and its three reviews for controls, raw files, limitations and diagnostic coverage.
