# Review of H200 BF16 KV control job 25863

This review covers the completed S47 BF16 KV control, job 25863. The frozen head checker was replayed and passed: 636 requests completed with zero errors or cancellations, good-request fraction 95.28%, and good output throughput 2796.15 tokens/s. This is an unranked 20/40/30 screen, so it is not directly comparable to a full N64 result near 3k tokens/s and does not establish a causal performance effect.

The runtime logs and all 16 allocation records confirm `kv_cache_dtype=auto` resolved to actual `torch.bfloat16` allocations across both prefill workers and decode. The stored `physical_store_dtype` description in the generated `kv-runtime-*.json` and head report is wrong: the frozen checker emits a uint8 description unconditionally. For this BF16 control, physical cache storage follows BF16; uint8 applies to FP8-backed cache buffers. The underlying raw role logs and logical dtype evidence remain valid. Frozen artifacts are preserved unchanged; the correction is recorded here.

The smoke vector passed 7/8 cases with the same known reverse-ASCII case as the frozen reference, with no new regressions. Long-context diagnostics passed 12/12, but this is not a formal accuracy test. Quality remains unknown and no official >=99% claim is supported. Resource sampling captured five-second GPU snapshots and cumulative host counters; server metrics were available only in a subset of samples. Missing values are not interpreted as zero or healthy, and the sampling does not prove a bottleneck. Full observations, caveats, exact metric values and next decision are in [REVIEW.json](REVIEW.json).

S48 job 25864 remains pending afterok 25863. This review makes no claim about its result.

Raw run artifacts remain at `/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/runs/25863`; no raw artifacts or submitted payload files were modified. Selected raw-file SHA256 references are in [RAW-SHA256SUMS](RAW-SHA256SUMS).
