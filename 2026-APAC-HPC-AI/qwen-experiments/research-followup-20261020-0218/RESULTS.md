# H200 N62 review for the 20 October presentation

## Question and controlled change

The fresh auto-decode N62 control 24914 passed at 2890.878 good output tokens/s. Does the independently reproduced N60 interaction remain useful at N62? Previously submitted job 24915 preserves the selected layout, DeepGEMM prefill/chunk8192, native FP8 checkpoint, BF16 KV, FA3 prefill attention, FlashInfer decode attention, NIXL and full benchmark protocol; decode MoE uses HPC-Ops instead of auto. The presentation request prompted this terminal review, not another GPU submission.

## Observation and acceptance

Job 24915 completed with Slurm exit 0:0 in 10:48. Exit status alone is insufficient. The sealed payload/runtime, 60-second warmup, 120-second scored duration and 30-second grace, 4000/200 workload, raw request errors and output checks were reviewed separately. The retained review marks LOCAL_PROTOCOL_SLA_OUTPUT_PASS; all 12 long-context checks pass and the eight-case short check introduces no newly failed case versus its independent baseline. These checks are not organiser accuracy verification.

| Metric | Value | Unit |
|---|---:|---|
| Good output throughput | 3022.034919 | good output tokens/s |
| Joint latency pass fraction | 98.726115 | percent |
| Mean TTFT | 1022.927941 | ms |
| Mean request ITL | 14.971161 | ms |
| Scored requests / qualifying | 1884 / 1860 | requests |
| TTFT breaches / ITL breaches | 24 / 0 | requests |
| Request errors / cancellations | 0 / 0 | requests |

The observed gain over fresh auto N62 is 4.536934%. This is the highest individual reviewed H200 result, but N62 has only one treatment observation. N60 remains independently reproduced at 2990.151 and 2989.175. Do not substitute the N60 repeat for an N62 repeat. The tokenizer reports 199–200 output tokens (mean 199.998408); request settings remain min_tokens=max_tokens=200 and ignore_eos=true. Preserve that counting detail rather than claiming every reported length is exactly 200.

## Collected and inspected beyond the score

[Extended inspection](inspection/24915.md) reconstructs raw request tails and sparse full-deployment role logs. TTFT p99 is 3466.927 ms, with a 4505.927-ms maximum; ITL p99 is 15.692 ms. Effective concurrency has p50/p95/max 62. Both prefill roles have a logged queue maximum of 25; decode running requests peak at 56 and logged KV token occupancy at 0.12. These log observations include warmup, checks and diagnostic phases, so they are not scored-phase time-weighted bottleneck measurements.

The separate N48 diagnostic after scoring has 425/425 successful requests and 16 sealed, rank-checked traces. [Profile analysis](h200-n62-profile.json) identifies named decode HPC group GEMM, MNNVL collectives and FlashInfer paged attention at 21.390%, 23.529% and 15.137% of summed recorded kernel duration. Prefill DeepGEMM named sums are 35.032% and 35.568%. These quantities are sums across recorded rank events, not elapsed critical-path fractions, GPU utilization or predicted speedups. Historical HTTP response parsing/stop limitations are retained in the raw controls; later response-parser fixes do not retroactively repair this run.

Dedicated continuous hardware telemetry is not available in this run: GPU activity, sampled VRAM, HBM bandwidth, power, clocks, temperatures, CPU/RAM and network rates remain unmeasured here. AIPerf lists no successful telemetry endpoint. No PBS credit is charged for this Slurm review; offline inspection creates no new GPU reservation. Resource observers are deployed in later distinct jobs, whose coverage and overhead still require review.

## Assessment and next decision

The controlled N62 result supports the phase-specific kernel interaction beyond N60. It does not establish an optimal global load, a causal device bottleneck or official full-set quality. Present N62 as a single observation, retain N60 as the replicated result, and confirm N62 independently during future authorised research. Review already submitted off/on/receive-interval pilots before promoting the polling change; no automatic load increase or job-script promotion is warranted by this slide update.

At the actual 02:17 UTC scheduler read, H200 24926/24927/24928 were pending for resources; PBS 222048 and 222049 had completed while 222050 was running. PBS outputs and charges were not collected or reviewed in this presentation pass. This dated state is not a live queue claim.
