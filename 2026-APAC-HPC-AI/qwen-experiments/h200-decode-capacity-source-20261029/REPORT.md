# Decode request-cap source review

**Date:** 2026-10-29 (UTC)
**Scope:** Read-only review of the pinned SGLang runtime and the N=64 Qwen H200 control. No GPU job was run and no scheduler or budget state was changed.

## Decision

`decode_max_running_requests=64` is technically compatible with the scored N=64 steady workload, provided the candidate's final TP0 scheduler value is verified as 64 and its graph batches remain captured through 64. SGLang gives the decode worker a running-request pool of this size and allocates disaggregation preallocation slots separately. The benchmark uses at most 64 closed-loop clients; semantic warmup is completed before the scored phase. Leave the prefill limit unchanged.

This is a weak performance hypothesis, not a likely score improvement. Existing H200 evidence has low decode token-pool usage (about 0.12) and no sustained decode queue, so the 256 cap is not shown to be the bottleneck. Lowering it mainly trims fixed request metadata and caps admission. Recommend at most one bounded 64-cap trial against a matched 256 control; do not spend a second 128-cap run unless the 64 run changes runtime behavior or a concrete allocation/admission issue appears. Keep the result explicitly exploratory and do not promote it without repeatable goodput gain and the normal SLA gate.

## Runtime behavior from the pinned source

- `--max-running-requests` is described as the maximum running requests (`server_args.py`). For the decode memory calculation, the explicit cap is clamped by token capacity; the finalized value is used to build the request pool (`kv_cache_configurator.py`). The final TP0 scheduler startup line is the runtime acceptance check, not just the requested command-line value.
- The decode pool constructor receives `size=max_num_reqs` and separately receives `pre_alloc_size`. Its row count is `size + pre_alloc_size + 1` (`kv_cache_configurator.py`, `decode.py`). The decode pool's source comment states the invariant: running requests are bounded by `size`; preallocated and in-transfer requests use the separate `pre_alloc_size` headroom. Thus a cap of 64 does not consume the transfer reserve.
- In the submitted 27270 launch, only the decode worker receives `--max-running-requests 256`; prefill workers do not receive this override. The `prefill_max_running_requests` setting is null. A candidate should change only the decode setting.
- Decode CUDA graph batches are captured through 64 in the existing config. A cap of 64 therefore does not require adding/removing graph shapes, but candidate startup logs must verify this remains true.
- At context length 8192, reducing the request-pool base from 256 to 64 removes at most `192 * 8192 * 4 = 6,291,456` bytes (6 MiB) of int32 request-to-token rows per decode rank, before separate preallocation rows. The metadata buffer is also sized from the pool. This is small relative to the H200 memory footprint. The pinned activation-reserve formula floors at 2048 tokens; with no speculative draft multiplier, the 256 and 64 settings both hit that floor, so this change should not free decode activation reserve in this run.

## Matched control and limits

Run 27270 is the relevant H200 TP8 decode baseline: N=64, decode cap 256, prefill cap unset, and 3039.053 good output tokens/s with 0.9853 good-request fraction. Its runtime reported `max_running_requests=256`. The broader run review records decode token usage around 0.12 and typical observed active decode concurrency around 50–54, with no sustained queue. A 64 cap has room for the measured steady active count and the full official concurrency, but it leaves no extra *running* slots beyond N=64; disaggregation transfer/preallocation slots remain separate.

This is source feasibility, not proof of performance. It does not show that reducing the pool improves GPU kernels, memory bandwidth, latency, or goodput. The run's 5-second metric sampling cannot rule out brief queueing between samples. Verify final TP0 `max_running_requests=64`, unchanged graph capture through batch 64, and no queue/error/SLA regression in a candidate before interpreting any score.

## Selected provenance

The six copied Python files are byte-for-byte extracts from `/scratch/enroot-images/sglang-harbor.sqsh` (SHA-256 `b74ae77446bfedd6c5d72820b45be255cc513cf7c7c039d1bf63679c8178bfe5`). Their image paths and individual hashes are in `evidence/SOURCE_MANIFEST.json`. No full container, weights, user home, or runtime credentials are included.
