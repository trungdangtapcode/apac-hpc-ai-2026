# Official ranking units: Goodput multiplied by 200

Recorded on 2026-10-20T12:46:40.317494+00:00. Source: the owner pasted a discussion in this chat attributed to Pengzhi Zhu replying to Hirotaka Tsuneki. No message URL or original calendar date was supplied; this is retained user-provided clarification, not an independently fetched chat transcript.

The reply explicitly selects **Goodput × 200**, reading Goodput from `profile_export_aiperf.json`. Goodput is measured in requests per second; multiplying by the fixed 200 output tokens per request converts it to good output tokens per second. Because every candidate is multiplied by the same positive constant, rankings are unchanged.

For example, 100 requests over a ten-second measurement with 90 qualifying requests gives 9 good requests/s and 1800 good output tokens/s. Actual AIPerf phase timing remains authoritative; do not substitute a nominal duration for the exported metric. A good request passes both TTFT and ITL conditions (3000 ms and 20 ms in the retained contest protocol). Errors remain failures in acceptance accounting. The minimum 90% passing-request gate is separate from maximising Goodput. Passing latency conditions is not a certification of answer correctness; the organiser model-quality gate remains separate.

Use the exported `goodput.avg` in the retained JSON schema and multiply by 200. Do not multiply it by the passing-request fraction again: Goodput already counts qualifying requests. Do not replace the stated official formula with raw output token throughput multiplied by the passing fraction; equality depends on matching token counts, request populations and time intervals, and the supplied clarification specifically instructs reading Goodput.

## Existing implementation check

The active retained `nscc-pbs/h100-prefill-rr-n54-control-70/summarize.py` reads `goodput.avg` and assigns `good_output_tokens_s = goodput * 200`. The stricter `serving-tuning/review-n54.py` also returns `good_tokens_s = values['goodput'] * 200` after validating the measured phase interval and request counts. Their formulas agree with this clarification; no scorer or frozen payload was changed. This is a targeted implementation check, not a new audit of every historical run.

The retained H200 result 3022.034919 good output tokens/s therefore corresponds to approximately 15.110175 good requests/s. This unit conversion adds no performance improvement and does not verify official full-set model accuracy.

## Workload and latency clarification supplied later in this chat

Recorded on 2026-10-20T12:48:56.069388+00:00. The owner supplied a second discussion attributed to Pengzhi Zhu. No original message URL or calendar date is supplied, so attribution is retained as user-provided evidence.

| Setting | Supplied organiser clarification | Practical meaning |
|---|---|---|
| Load generation | Closed-loop at team-decided concurrency N | Maintain up to N outstanding requests; as requests finish, issue replacements during the measurement window. N is selected by the team. |
| Request rate | No target request rate | Requests per second result from serving performance; they are not a fixed arrival-rate input. N is a count of requests in progress, not requests per second. |
| Input / output length | Fixed 4000 / 200, ratio 20:1 | Synthetic target lengths have zero spread, rather than merely averaging these values. Actual tokenisation/export lengths still need inspection. |
| Prefix reuse | Disabled for cold cache | Do not gain prefix reuse across requests from a previously cached shared prompt. This does not remove a request's own KV cache used to generate its continuation, nor instruct flushing all server caches before every request. |
| Workload random seed | 2026 | Fix the AIPerf synthetic workload generator. This is distinct from the serving engine's own random seed and does not make GPU timing deterministic. |
| Goodput conditions | time_to_first_token:3000 inter_token_latency:20 | A good request must meet both the 3000 ms first-token and 20 ms inter-token latency conditions. |
| Run eligibility | good_request_fraction >= 0.90 | At least 90% must qualify before the run is scored. Higher raw throughput alone does not bypass this gate. |
| Ranking units | Goodput × 200 | Use qualifying requests/s from the JSON, multiplied by fixed output length. |

The follow-up question mentioned end-to-end latency, but the supplied reply sets **ITL**, not an independent end-to-end latency threshold. Total request latency remains useful diagnostic evidence; do not substitute it for ITL or invent a separate official total-latency cutoff from this excerpt. The excerpt does not supply a benchmark duration or explicitly change the separate model-quality requirement.

A team can try different N values to find its best qualifying Goodput. Increasing N is useful only if the resulting run keeps the required passing fraction; do not compare an ineligible high-throughput run as a winner. For example, N = 54 means approximately 54 requests in progress once the closed loop is filled, not an arrival rate of 54 requests/s.

### Targeted comparison with our implementation

The current H100 chunk-pair benchmark script explicitly uses concurrency N, no request-rate argument, 4000/200 means with zero standard deviation, workload random seed 2026, first_turn_prefix cache busting and the exact two goodput thresholds. A sealed completed export for H100 222302 records concurrency phases, seed 2026, those zero-spread synthetic lengths, prefix cache-busting and matching thresholds. [Structured paths, hashes and fields](official-workload-check-20261020.json). The existing strict reviewer also checks these fields. The retained sampler's near-zero prefix-hit observations support the cold-prefix workload but do not prove literally zero cache hits for all tokens.

These checked artifacts match the supplied settings. This is not a fresh audit of every historical H100/H200 run, an official evaluation result or permission to edit frozen submitted bundles. No scorer, scheduler job, research budget, submission material or authentication state changed during this clarification.

## Direct public repository corroboration

The later [pinned upstream review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/upstream-review-20261020/REPORT.md) directly checks public Qwen rules at 3d050964d1008b97fb6d0d7ec5160087cd6883d9: the official command and addendum corroborate the supplied workload and Goodput × 200 explanations. The rules file is byte-unchanged from the earlier retained September revision. This is stronger direct source provenance, not a newly changed metric.
