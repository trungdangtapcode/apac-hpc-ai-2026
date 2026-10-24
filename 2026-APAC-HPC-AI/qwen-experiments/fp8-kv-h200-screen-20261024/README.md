# H200 BF16 versus FP8 KV screen (2026-10-24)

## Question and prior evidence

Does storing the target model's K/V cache as E4M3 reduce decode memory traffic enough to improve the existing H200 N64 workload, with the same FlashInfer decode attention path and the same rest of S41?

This is a bandwidth hypothesis. The task does not establish a KV-capacity bottleneck, and this plan makes no memory-bandwidth claim. At N64 with 4,000-token prompts, the theoretical resident KV amount is large enough to motivate a short screen, while kernel/runtime behavior, active sequence lengths, cache reads, and memory bandwidth remain unmeasured.

The prior native H200 FP8-KV primitive 25796 passed four synthetic FlashInfer cases; its maximum same-rounded-cache relative L2 error was 0.315902%. That supports primitive kernel compatibility only. It does not validate Qwen model quality, the serving path's scale values, NIXL transfer, or performance. The full source preflight is retained at [`fp8-kv-source-preflight-20261023/REPORT.md`](../fp8-kv-source-preflight-20261023/REPORT.md).

## Actual checkpoint scale metadata

A CPU metadata-only scan of `/scratch/models/Qwen3-235B-A22B-Instruct-2507-FP8` read `config.json` and `model.safetensors.index.json`, but did not open a tensor weight shard. The config identifies Qwen3-MoE, 94 layers, four KV heads and head dimension 128. Its FP8 weight quantization config has no `kv_cache_quant_algo`. The 73,417-entry checkpoint index has zero `k_scale` or `v_scale` keys. The pinned SGLang source says `auto` selects model dtype unless `kv_cache_quant_algo` explicitly declares FP8; the explicit `fp8_e4m3` path selects `torch.float8_e4m3fn`. The source also documents that FP8 buffers use `torch.uint8` storage because float8 `index_put` is unsupported.

The CLI source warns that absent `--quantization-param-path` makes KV scale factors default to 1.0 and may cause accuracy issues. This pair therefore records the uncalibrated default-scale status. The FP8 candidate is an **exploratory unranked screen**. Quality is unknown regardless of the short local checks; no 99% official accuracy claim or promotion follows from this pair.

The actual CPU preflight output, file hashes and exact pinned source provenance are retained in `checkpoint-kv-scale-preflight.json`, `SOURCE_PROVENANCE.json`, and the source-preflight manifest. Each job reruns the metadata scan before worker startup and writes a per-job copy. If model geometry or the index's scale keys change, the job stops for review.

## Matched design

The canonical control and candidate are prepared under:

- [`serving-tuning-10/s47-h200-bf16-kv-control`](../serving-tuning-10/s47-h200-bf16-kv-control)
- [`serving-tuning-10/s48-h200-fp8-kv-screen`](../serving-tuning-10/s48-h200-fp8-kv-screen)

Both derive from frozen S41 `s41-h200-graph-disabled-cap64-screen`. Each job uses two H200 nodes and 16 GPUs for at most 17 minutes. The topology remains two target prefill workers on node 0 (TP4 each), one target decode worker on node 1 (TP8/EP8), round-robin P/D routing, and the pinned NIXL `912b7...` descriptor patch. Both retain model-weight dtype explicitly as BF16, uniform disabled prefill graphs, graph-captured decode sizes 1–64, P/D request caps 64/256, prefill DeepGEMM with chunk size 8192, decode FlashInfer attention, HPC-Ops MoE and MNNVL all-reduce.

Only the KV-cache dtype differs operationally. S47 leaves the SGLang setting at `auto`; the expected model config path resolves that to `torch.bfloat16`. S48 sets `--kv-cache-dtype fp8_e4m3` in the single shared worker argument path, so both prefill and decode roles receive it. Its expected logical allocation dtype is `torch.float8_e4m3fn`; pinned pool code stores that cache in `torch.uint8` buffers.

Both reuse the same client image, deterministic seed 2026, fixed 4,000 input and 200 output tokens, 12,800-entry no-reuse cache-busted synthetic corpus, and 20-second warmup / 40-second measurement / 30-second grace protocol. They retain the eight-case output smoke and 12-case long retrieval diagnostic after the ranked measurement interval. No strict token-for-token comparison is added: the contest permits FP8 KV, and that would be inappropriate for this exploratory precision comparison.

## Runtime and quality gates

The bundle retains S41's source, asset, NIXL, two-path semantic warmup, client/runtime, telemetry, capacity, short-output and long-output checks. Additional fail-closed CPU log parsing requires each role to show the resolved `ServerArgs` KV setting and BF16 model dtype. It also requires actual `KV Cache is allocated` log lines for the expected TP ranks and checks their logical dtype: BF16 for S47; E4M3 FP8 for S48. Missing allocation evidence or a dtype mismatch fails the job. The check records `torch.uint8` as source-derived physical storage for FP8; allocation logs expose logical dtype, not that internal buffer dtype.

The same checker records the absent quantization parameter path, absent checkpoint K/V scale keys and source-defined 1.0 default. Per-layer backend scale values are not emitted by the inspected source, so the record says that directly instead of claiming a runtime readback. Resolved decode attention must remain FlashInfer, and the existing server log gate must confirm capacities, graph policy and role backends.

For both jobs require zero benchmark request errors and cancellations, SLA good-request fraction at least 0.90, no regression against the frozen 7/8 output-smoke vector (and at least 7/8), both P/D semantic warmup paths, complete telemetry/protocol records, and all 12/12 long retrieval checks. These local checks are screening conditions, not formal accuracy measurement. Neither a fast score nor 7/8 + 12/12 establishes the official 99% reference threshold.

Use an `afterok` dependency for S48 on a reviewed passing S47 control receipt, so the candidate is only compared when its control is valid. The root owner handles current queue review, immutable freeze, receipts and any submission decision. These draft payloads do not submit themselves.

## Expected traffic and decision gates

For this model and TP8 decode, four global KV heads give one KV head per rank. At head dimension 128 and 94 layers, theoretical K+V cache bytes per token per decode rank are:

- BF16: `94 layers × 2 (K,V) × 1 local KV head × 128 × 2 bytes = 48,128 bytes/token`.
- FP8: `94 × 2 × 1 × 128 × 1 byte = 24,064 bytes/token`.

If all 64 requests simultaneously reach 4,000 cached tokens, the corresponding theoretical cache amounts are 12,320,768,000 bytes (12.32 GB, 11.47 GiB) versus 6,160,384,000 bytes (6.16 GB, 5.74 GiB) per rank. This arithmetic motivates the experiment; it is not measured traffic, bandwidth, a capacity diagnosis, or a speedup prediction. It ignores varying live sequence lengths and runtime/cache-layout effects.

The candidate's observed goodput must exceed the matched S47 control by more than 1% to justify considering a full matched confirmation. That decision also requires all local runtime and output gates above. At or below the threshold, or if any gate fails, close this unchanged FP8-KV performance branch and retain the result. Even above 1%, keep the screen unranked and accuracy unknown; do not promote it until separate scale/quality work establishes the official requirement.

## CPU-only evidence and limits

`cpu-fixtures.py` tests source hashes, actual worker argument construction, S41 protocol identity, BF16 graph/capacity parsing, and positive/negative synthetic log fixtures for missing or wrong KV allocation proof. The fixture also deliberately removes `--dtype bfloat16` and asserts that the validator rejects the S44-style omission. These synthetic fixtures test parser behavior only; they are not H200 logs, server starts, KV allocations, NIXL transfers or performance evidence.

No GPU, scheduler queue, budget, submission, or Git operation was used to prepare this pair. Both canonical bundles remain draft and unsubmitted.

## Root conditional submission contract

S47 is submitted as25863 afterany25862. S48 may reserve its position with **afterok:25863**; before starting any model worker it independently replays the actual control raw runtime/protocol/SLA/response gates using the frozen S47 checker and verifies the control source manifest. Thus a missing or failed control cannot launch the candidate. This prospective programmatic gate supersedes the draft wording that waited for a manual post-run review before queueing; no completed control result is claimed in advance. FP8 scale calibration and official accuracy remain unverified.
