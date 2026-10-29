# Prefill prefix cache under the fixed cold workload

Reviewed 29 October 2026, Vietnam time (UTC+7). This is source feasibility, not measured improvement. Root completed an interrupted child source review so it would not block ready work.

Actual control 27270 uses RadixCache on all four ranks of each prefill, with disable_radix_cache=False. Decode already resolves disable_radix_cache=True and uses ChunkCache on all eight ranks. No session, streaming, hierarchical or hybrid SWA/SSM cache is active.

The pinned kv_cache_builder forwards the flag into its build context. registry.py lines 84-88 select ChunkCache when chunked prefill is enabled and radix is disabled. ChunkCache.match_prefix returns no shared prefix; insert is a no-op. Unfinished chunks retain their own KV indices, and finished requests free their allocation. The physical KV pool and active request KV remain. The unrelated prefill_only_disable_kv_cache flag stays false.

Disaggregation lifecycle is explicit: prefill.py lines 867-875 retains waiting/transferring requests and calls release_kv_cache after successful transfer. mem_cache/common.py lines 148-153 delegates final release to the cache. This supports the proposed lifecycle but does not certify actual new NIXL/semantic/output behavior. Fresh physical KV receipts and both semantic routes remain required.

Hypothesis: cold prefixes provide little reusable prompt work, while the prefix tree still performs lookup/insertion/eviction. Removing that bookkeeping may help TTFT or useful throughput. Removing small formatting-prefix matches may cost extra work, and the host-wide CPU samples do not isolate a bottleneck. Upside is uncertain.

One full candidate changes both prefills to --disable-radix-cache. Require actual resolved flags and all-rank native classes: candidate ChunkCache on all roles; fresh control RadixCache on both prefills and unchanged ChunkCache on decode. Preserve decode cap256/polling1, native model and precision, topology, graph sets, requested N64 cold4000/200 seed2026/full60/120/30 and all original output gates. Official accuracy remains unknown.

A fresh control is warranted after intervening cluster activity. Require a complete valid >1% useful gain with acceptable tails before independent confirmation, otherwise close unchanged. Each arm is 16 H200/two nodes/17 minutes maximum, no PBS SU, own cap5. No weights, native model math, NIXL descriptor exceptions, HPC payload, submission or authentication changes. SOURCE_MANIFEST.json records exact image paths and hashes.
