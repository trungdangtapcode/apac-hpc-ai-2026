# Extended artifact inspection: H200 job 24915

Generated offline from sealed raw artifacts. This supplements the accepted protocol/output review; it does not replace it or rerun the benchmark.

## Client distribution

| Metric | Unit | Mean | p50 | p95 | p99 | Maximum |
|---|---|---:|---:|---:|---:|---:|
| time_to_first_token | ms | 1022.9279 | 942.9952 | 1243.2609 | 3466.9272 | 4505.9272 |
| inter_token_latency | ms | 14.9712 | 15.0036 | 15.1629 | 15.6921 | 17.0262 |
| request_latency | ms | 4002.1638 | 3931.964 | 4194.3905 | 6400.8622 | 7508.6886 |
| effective_concurrency | requests | 61.2551 | 62.0 | 62.0 | 62.0 | 62.0 |

## Full-deployment server log samples

These include warmup, scored traffic, output checks and any separate diagnostic. They are event samples, not time-weighted scored-phase means.

| Role | Batch lines | Running requests p50 / p95 / max | Queue p50 / p95 / max | Logged KV token usage p50 / p95 / max |
|---|---:|---|---|---|
| prefill-0 | 886 | 0.0 / 0.0 / 0.0 | 0.0 / 2.0 / 25.0 | 0.02 / 0.02 / 0.02 |
| prefill-1 | 895 | 0.0 / 0.0 / 0.0 | 0.0 / 2.0 / 25.0 | 0.02 / 0.02 / 0.02 |
| decode-0 | 347 | 50.0 / 54.0 / 56.0 | 0.0 / 0.0 / 0.0 | 0.12 / 0.12 / 0.12 |
| router | 0 | N/A / N/A / N/A | N/A / N/A / N/A | N/A / N/A / N/A |

## Collection gaps and interpretation

AIPerf telemetry endpoints configured: `[]`; successful: `[]`.

GPU utilization, HBM activity, sampled VRAM, power, clocks, temperature, CPU/RAM and link throughput are **not available as dedicated continuous hardware measurements in this inspection**. Missing is not zero. A separate profile can still describe recorded kernel execution; it does not reconstruct missing hardware samples.

KV allocation records and warning/error mention counts are in the adjacent JSON. A nonzero queue or token-usage peak somewhere in the whole deployment is not proof of the scored benchmark bottleneck.

## Limits

- Role log statistics cover the entire deployment, including warmup, output checks and any separate profile.
- Batch log samples are sparse and event-weighted, not uniform time samples or proven scored-phase statistics.
- Token usage is logged KV token occupancy, not GPU utilization, allocated VRAM or HBM bandwidth.
- KV allocation sizes are reported by the server; they are not sampled total or peak VRAM.
- No timestamp conversion or cross-rank alignment is assumed for the naive client/server wall clocks.
- Warning/error matches require triage and are not counts of failed scored requests.
- Uncollected GPU/CPU/network telemetry cannot be reconstructed from goodput or kernel duration sums.
