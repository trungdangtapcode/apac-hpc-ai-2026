# Full-corpus local quality shard generator

Creates eight paired reference/candidate shards from the pinned 12,032-question local MMLU-Pro corpus. The unchanged client rule is used exactly: enumerate prepared-corpus rows in file order and select row index modulo 8 equal to the shard index. Each shard contains 1,504 questions; reference and candidate use identical IDs.

Pilot evidence: candidate job 28368 scored 102/128; reference job 28371 scored 104/128; ratio 98.076923%, with no service errors. This is below the local 99% ratio gate on a small sample, so the complete fixed corpus is needed to assess whether it generalizes. The full test keeps the prepared prompt bytes, parser, greedy decoding and 2,048-token output cap and uses concurrency 64.

The generator verifies existing frozen pilot/reference payloads and the candidate source manifest. It asserts candidate worker, NIXL patch, config, environment and placement files remain byte-identical. Original pilot bundles and the accepted submission are untouched. It creates no frozen-full8 guard and submits no jobs; review and freeze the generated payload before explicit admission.

All 16 jobs have a maximum exposure of 72.533333 H200 GPU-hours at full 17-minute allocations and zero PBS SU. Prior roughly 3,000 output tokens/s is only a forecast for long CoT. Review one actual paired concurrency-64 shard for completion time, coverage, errors, timeouts, token totals and responses before admitting the other shards.

Aggregate correct counts over the full 12,032 denominator for each role, then divide candidate accuracy by reference accuracy. Never average shard ratios. A local >=99% ratio is not BTC certification.
