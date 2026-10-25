# Job 25998: decode-only EAGLE3 passes the short SLA but loses to target-only

Review date: 2026-10-25 UTC

## Question and prior evidence

The all-worker EAGLE3 candidate (25948) lost good output throughput and failed the 90% joint-latency gate. The hypothesis for 25998 was that keeping EAGLE3 only on decode would retain its lower inter-token latency while avoiding draft verification work on the prefill workers. Job 25988 did not reach AIPerf because a validator incorrectly required 190 KV regions on every role. The immutable retry fixed the check by distinguishing 188 target-model regions from two decode-side draft registrations.

## Change and control

Both jobs used two target-only TP4 prefill workers, a TP8/EP8 decode worker, SGLang, NIXL, the same FP8 Qwen checkpoint, H200 hardware, N64, 4,000 input tokens, 200 output tokens, seed 2026, cold prefix cache and the short 20-second warmup / 40-second measurement / 30-second grace protocol. Control 25947 used target-only decoding; candidate 25998 added EAGLE3 to decode only. Both used 16 H200 GPUs. This is an unranked screen, not the organiser's full scoring protocol.

## Result

Job 25998 completed successfully (Slurm `COMPLETED 0:0`, 9:44 allocation). It served 601 profiled requests with zero errors and cancellations. Goodput was 13.133553 requests/s; multiplied by 200 output tokens, good output throughput was **2,626.71 tokens/s**. The joint fraction satisfying TTFT <= 3,000 ms and mean ITL <= 20 ms was **94.84%**, above the short-screen gate. Raw output throughput was 2,769.57 tokens/s. Mean TTFT was 1,182.33 ms (p95 2,812.08 ms); mean ITL was 16.428 ms (p95 17.778 ms). The per-request recount found 30 TTFT failures and one ITL failure, with no request violating both.

Matched target-only control 25947 produced **2,757.36 good output tokens/s**, 95.24% joint success, mean TTFT 1,311.60 ms, mean ITL 14.833 ms, 630 requests and zero errors/cancellations. Thus the candidate was **4.74% lower** in good output throughput and 0.40 percentage points lower in joint success. Mean TTFT improved 9.86%, but mean ITL regressed 10.76%; ITL p95 rose 16.17%. This trade-off does not support promoting EAGLE3.

The candidate's decode logs reported draft acceptance around 0.12–0.15 (approximately 1.24–1.29 accepted tokens per verification sequence in the measured region). Low acceptance is consistent with speculative work failing to repay its overhead; this is evidence for a hypothesis, not a measured causal decomposition. The unchanged EAGLE3 branch is closed for this pinned draft/runtime combination. Do not repeat the same setup without a changed acceptance mechanism or materially new runtime.

## Broader inspection and limits

The 83-second AIPerf window had 18 five-second hardware samples per role. During that window, the eight decode GPUs averaged 68.6% sampled GPU-active time (median 94%, maximum 99%), 136.1 GiB allocated memory (maximum 136.9 GiB), and 407.9 W average sampled power (maximum 519 W). The two prefill groups averaged 61.6% and 57.1% sampled GPU-active time, about 131.7 GiB allocated memory, and 464 W / 460 W sampled power. Shared-node CPU busy estimates were 14.2% on g1 and 13.5% on g4. These five-second samples are not FLOP utilization, do not establish a causal bottleneck, and shared CPU/network counters cannot be assigned to one worker. The interface byte deltas and samples do not establish network saturation.

During the scoring window, sampler HTTP polls returned 200 for all captured samples. AIPerf's own embedded server telemetry endpoints were not configured, so its `telemetry_data` section is empty; separately sampled SGLang metrics were collected. At one captured decode instant, the TP0 series reported 28 running requests, queue 0 and token usage 0.05. Prefill series at the final sample reported zero running/queued requests, as expected after their prompt work. These are instantaneous, rank-local samples, not integrated occupancy. KV allocation bytes and token occupancy are different measurements.

Runtime evidence passed: all three workers became healthy, two P/D semantic warmups passed, all 32 role/rank KV receipts passed the corrected 188-target/190-draft geometry gate, and the draft fingerprint check passed. The local output smoke was 7/8 and retrieval was 12/12; the same reverse-string smoke case also failed on target-only control 25947, so it is not a candidate-only regression. Official model-quality accuracy remains **unknown**; this performance screen is not ranked and is not directly comparable to the 60/120/30-second H200 incumbent of 3,044.40 good output tokens/s.

The model logs include an HTTP/2 preface warning on prefill at 05:56 and 05:57 local time, outside the AIPerf interval; the routers subsequently warmed both P/D paths and the scored request profile has zero errors. Treat those startup warnings as observed but not shown to cause a scored failure. Slurm's enclosing job completed; child `srun` serving steps were cancelled during the batch script's expected teardown, not by the scheduler during the scored window.

## Next decision

Retain the 3,044.40 full-protocol result as the measured H200 frontier. Close the unchanged decode-only EAGLE3 branch. The next distinct bounded hypothesis is to compare a modern-runtime `P8-TP4 / D8-2x(TP4, EP4)` target-only layout against the current `P8-TP4 / D8-TP8-EP8` control. The older topology job 22219 reached 1,666.01 good tokens/s at N40 under an earlier runtime and short protocol; it motivates a fresh confirmation but is not a current comparison. Any new runner must support four endpoints, validate all four worker/rank KV receipts, warm all four P/D pairs, preserve a 16-GPU placement, and use an explicit accepted topology. Do not submit the old script unchanged. Compare under the same short protocol first; require >=90% joint success and zero errors/cancellations, and only advance to full protocol if it beats the matched control by a predeclared margin.

## Raw evidence

- [Slurm output](../runs/25998.out)
- [AIPerf profile and raw request rows](../runs/25998/screen/n64/artifacts/)
- [Independent head check](../runs/25998/head-performance-check.json)
- [Runtime and geometry receipts](../runs/25998/runtime-readiness.json), [KV geometry](../runs/25998/kv-geometry-validation.json), [semantic P/D warmup](../runs/25998/pair-warmup.log)
- [Output smoke](../runs/25998/output-smoke.json), [retrieval check](../runs/25998/long-context-check.json)
- [Per-role GPU, CPU, network and server-metric samples](../runs/25998/resource-telemetry/)
- [Frozen submitted payload](../runs/25998/submitted-payload/)

