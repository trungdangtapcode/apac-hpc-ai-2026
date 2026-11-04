# Cold-prefill cache candidate

> Source-linked retrospective. Original measurements remain attributed to their platform, load and trial.

## Research question

Does a cold-prefill cache intervention raise H200 goodput enough to offset its latency-tail behavior?

## Why investigate this?

The cold-prefix workload offers little benefit from reusable prefix lookup. The team tested whether removing radix-tree bookkeeping on prefill could improve useful throughput. This changes the cache implementation used by prefill; it does not remove the KV state needed for active requests.

## What changed?

| Aspect | Before / control | After / tested setting |
|---|---|---|
| Prefill cache implementation | disable_radix_cache=false; Python RadixCache on both prefill roles. | disable_radix_cache=true; ChunkCache on both prefill roles. |
| Decode cache and workload | Decode ChunkCache; cold-prefix workload, seed 2026. | Unchanged; active-request KV storage remains enabled. |

## What was measured?

| Evidence | Recorded result |
|---|---|
| Candidate peak | 3,048.446289 good output tokens/s; +0.240921% versus control. |
| Tail behavior | p95 TTFT worsened. |

## What did we learn?

- The small score difference was below the 1% promotion threshold.
- A worsened p95 TTFT weakens the case despite a higher peak.

## Decision

Do not promote; keep the existing recipe.

## Limits and remaining questions

- The result applies to this specific cache design and cold workload.
- No claim about warm-cache workloads or other cache strategies.

## Sources

- [ai-final-report-20261030/REPORT.md](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/workspace/reports/ai-final-report-20261030/REPORT.md)
- [h200-cold-prefill-cache-study-20261029/RESULTS.md](https://github.com/trungdangtapcode/apac-hpc-ai-2026/blob/main/2026-APAC-HPC-AI/qwen-experiments/h200-cold-prefill-cache-study-20261029/RESULTS.md)
