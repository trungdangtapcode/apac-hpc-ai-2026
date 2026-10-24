# D5 unified output qualification R5 (H100)

R5 is a source-backed correction to R4 startup. R4 job 25936 enabled DP attention with global prefill chunk 8192. The pinned server source floor-divided that value by DP size 5, resolving 1638 tokens per rank, then rejected it because 1638 is not divisible by page size 64. This happened before model loading; no model response or quality result exists. See `R4_FAILURE_CONTEXT.json` and its immutable run-log references.

R5 sets `--chunked-prefill-size 10240`. The pinned argument-resolution code divides it by five, yielding 2048 per-rank tokens, which is divisible by page size 64. `prefill_chunk_preflight.py` checks the relevant pinned source constraints and both numerical cases on CPU before the server starts. The observer writes the actual resolved chunk, and the readiness gate requires 2048 on each of the five ranks.

All reviewed R4 runtime and independent raw output gates are retained: unified disaggregation mode, TP5/DP5/EP5 and DP LM head, loaded expert/map/hash checks, BF16 KV, health, metrics, 900-second server/container bounds, 5-second telemetry, eight smoke cases with the known 7/8 floor, and twelve retrieval cases. The output screen requires no request errors, no known smoke regressions, at least 7/8 smoke, and 12/12 retrieval. It remains separate from startup readiness; official quality is UNKNOWN and there is no scored-load or throughput claim.

R5 is not root-reviewed. `prepare_check.py` fails closed until that review is bound. H100 additionally requires an actual root-bound afterok dependency on the current eight-node probe; its placeholder currently prevents execution. No job is submitted by this bundle preparation.

## Root admission review

The actual global chunk is now **10,240 tokens**, divided by five DP ranks to **2,048 tokens per rank**, exactly divisible by page size 64. The old 8,192-token default became 1,638 per rank and failed before model loading. The CPU preflight rejects that original case and requires the corrected flag; actual runtime evidence must still prove 2,048 on every rank.

H100 uses the actual PBS working directory. Its `afterany:224560.pbs111` dependency preserves one active AI allocation; it is scheduling order only. The separate EAGLE transport probe need not pass for this unified-model hypothesis to run. Actual R3 qualification remains the portable, hash-bound prerequisite.

**Platform-specific correction:** actual H100 R4 job 224559 failed at the initial `cd` into a nonexistent local checkout path, before any model or argument validation. H200 R4 job 25936 reached the page-alignment assertion. R5 fixes the H100 working directory and proactively applies the source-proven chunk alignment on both platforms; it does not invent an observed H100 page failure.
