# First full-study paired shard: valid runtime and favorable point result

Reviewed 2026-11-03T01:34:00.954685+07:00, Vietnam time (UTC+7).

| Role | Job | Correct / questions | Accuracy | Invalid answers | Output at token cap | Service errors | Allocation |
|---|---|---|---|---|---|---|---|
| Stock native FP8 reference |28373|1200 /1504|79.787234%|13|187|0|620 seconds|
| Accepted candidate model-worker config |28375|1205 /1504|80.119681%|10|188|0|739 seconds|

Both jobs are COMPLETED 0:0. Raw API bodies were reparsed and verified against the exact frozen prepared questions, labels and shard membership. Paired concurrency 64 and generation 2048/greedy settings match. The local shard ratio 1205/1200=100.416667% exceeds 99%; this is only 1504/12032 questions and not a full-set or organiser pass. The earlier N16 pilot 102/104=98.076923% point failure remains preserved separately, not averaged into this N64 full study.

## Decision and limits

The purpose of this first pair was to qualify long-answer runtime, exact coverage and zero service errors. Both fit under 1020 seconds. This passes the admission gate for the remaining 14 fixed shards. Accuracy was not a selection or stopping gate. The whole 12032-question set must be evaluated unchanged, including unparsed and token-capped answers. The candidate gains five correct answers in this shard, but the deployments differ in layout, kernels and serving path; no single-optimisation causal benefit is established. The general capture helper prunes bytecode directories; the exact 16 checksum-required public runtime files are separately preserved in the verified recovery tar before further admission.

Actual full-pair cost is 6.04 H200 GPU-hours; pilots 4.213333, stage so far 10.253333; zero PBS SU. Serving workers are intentionally cancelled during cleanup; native top-level job completion and scored responses, not worker daemon cancellation flags, determine measurement validity.

Runtime evidence includes all worker/router logs, readiness and semantic receipts, frozen-input checks and raw responses. Candidate warmup had one transient 503 before both P/D routes passed; this is outside the fixed scored question set. All 1504 scored requests succeeded. Hardware GPU utilisation, power, memory-bandwidth and CPU sampling were not collected in this quality-only derivative; absent telemetry is not assumed healthy. Source configuration and runtime logs establish the invoked backends, not their isolated arithmetic contribution.

The finite Slurm callback can only admit the remaining fixed role/shard pairs within cap 5 and the declared 16-job /72.533334 GPU-hour maximum. It validates exact data and stops on service failure, deadline misses, malformed evidence or ambiguous submission. It is not Codex, a daemon, a recurring schedule, a new hypothesis selector, an authentication client or a Git mirror. Final aggregation is automatic once all 16 valid events exist; official certification still requires the organiser's own reference/harness.
