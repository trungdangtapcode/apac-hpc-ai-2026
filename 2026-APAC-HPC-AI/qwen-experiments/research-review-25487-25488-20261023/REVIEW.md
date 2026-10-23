# Full H200 N64/N68 pair review

This offline review inspects jobs 25487 (N64 control) and 25488 (N68 candidate), then compares the pair with the accepted full N64 source 25366. It reuses the validated metric reader from `serving-tuning/review-n54.py`, the long-diagnostic validator from `serving-tuning-10/review-wave10.py`, and phase-aligned telemetry parsers from `research-review-25373-20261022/observability.py`.

## Scored comparison

| Job | Client concurrency | Good output tokens/s | Joint SLA | Requests | Errors / cancelled | TTFT mean / p95 / p99 / max (ms) | Request-mean ITL mean / p95 / p99 / max (ms) |
|---|---:|---:|---:|---:|---:|---:|---:|
| 25487 | 64 | 3044.637 | 98.632299% | 1901 | 0 / 0 | 1113.6 / 1419.0 / 3474.5 / 4757.0 | 14.993 / 15.160 / 15.620 / 16.744 |
| 25488 | 68 | 3047.166 | 98.430141% | 1911 | 0 / 0 | 1347.1 / 1686.7 / 3723.7 / 5012.1 | 14.996 / 15.140 / 15.601 / 16.330 |

N68 changed good output throughput by **+0.083%** over the fresh full N64 control. Both meet the local 90% joint TTFT/ITL threshold and have zero scored errors or cancellations. The gain is below the predeclared 1% replication gate, so stop the unchanged N68 branch.

The raw joint classification counts each profiling request once, including bad requests. The local good fraction is not the separate contest accuracy gate.

## Request tails and output lengths

Job 25487: TTFT breaches >3,000 ms = 26; request-mean ITL breaches >20 ms = 0. Joint good / TTFT-only / ITL-only / both-bad = 1875 / 26 / 0 / 0. Exported output lengths: `{199: 3, 200: 1898}`; requested length remained nominally 200.
Job 25488: TTFT breaches >3,000 ms = 30; request-mean ITL breaches >20 ms = 0. Joint good / TTFT-only / ITL-only / both-bad = 1881 / 30 / 0 / 0. Exported output lengths: `{199: 7, 200: 1904}`; requested length remained nominally 200.

Actual generated token IDs were not retained in these performance runs, so exported lengths remain diagnostic evidence rather than a byte-level output archive.

## Protocol and payload control

Job 25487: normalized official closed-loop 4,000/200 protocol and 60 s warm-up / 120 s measurement / 30 s grace match source 25366; the 15 non-config operational payload files are byte-identical. Resolved SGLang arguments differ from 25366 only in the randomized seed. Output smoke eligibility: True; new failed cases: []. Long retrieval: PASSED (12/12).
Job 25488: normalized official closed-loop 4,000/200 protocol and 60 s warm-up / 120 s measurement / 30 s grace match source 25366; the 15 non-config operational payload files are byte-identical. Resolved SGLang arguments differ from 25366 only in the randomized seed. Output smoke eligibility: True; new failed cases: []. Long retrieval: PASSED (12/12).

Across 25487 vs 25488, `config.json` differs only in concurrency (64 → 68) and the descriptive experiment name. The 15 non-config execution payload files are byte-identical; resolved service arguments differ from source 25366 only in randomized seeds.

## Queue, runtime, and cleanup

Both top-level allocations and batch steps ended COMPLETED/0:0 after the scripts logged MEASUREMENTS_COMPLETE. The retained topology-job.sh installs an EXIT trap that sends kill to its background worker/router srun PIDs and waits; sacct shows those long-lived nested steps 25487.0-.3 and 25488.0-.3 cancelled at allocation teardown, while the AIPerf step .5 completed 0:0 and pair-warmup step .4 completed 0:0. The scored phase manifests report was_cancelled=false and zero request errors/cancellations. The separate post-score profiler stop returned HTTP 500 and is recorded as a diagnostic failure.
The diagnostic profiler starts returned HTTP 200 but all stop calls returned HTTP 500. Its trace files were inventoried, not analyzed. This failure is not scored request failure.
CUDA graph decode sizes are configured from 1 through 64. Per-role SGLang running/queued request gauges and sampled GPU activity, VRAM, and power are retained in `REVIEW.json`; series are not summed across TP ranks. Client concurrency is not itself the measured batch size. Sparse observer readings cannot prove saturation or identify cause.

## Decision and limits

Keep N64 as the measured incumbent. Close N68 at this load: +0.083% is too small to justify another full replication under the plan's 1% gate. The scoring pair is valid local serving evidence; it does not verify the organizer's ≥99% reference accuracy, and no H100/H200 cross-hardware conversion is inferred.

Reproduce from this directory with `python3 review.py`. It seals raw run files once if manifests are absent and writes only this review directory plus `runs/25487/artifact-manifest.json` and `runs/25488/artifact-manifest.json`.
