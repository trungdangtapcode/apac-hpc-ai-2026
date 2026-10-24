# H200 prefill CUDA graph policy pair review

Reviewed 2026-10-23 UTC from completed raw runs 25712 and 25713. Both were short, unranked, target-only screens at concurrency 64. The pair isolates the prefill graph policy in the serving payload: default policy (`auto`) in 25712 versus explicit native `--cuda-graph-backend-prefill disabled` in 25713. These are not EAGLE results or full-run contest scores.

## Result

| Job | Prefill policy | Good output tokens/s | Effective concurrency avg | SLA-good requests | Errors / cancelled | TTFT p95 / p99 / max (ms) | Request-mean ITL p95 / p99 / max (ms) |
|---|---|---:|---:|---:|---:|---:|---:|
| 25712 | auto | 2826.265 | 61.872 | 612 / 638 (95.925%) | 0 / 0 | 2698.721 / 4244.425 / 4757.992 | 15.288 / 15.792 / 16.747 |
| 25713 | disabled | 2809.862 | 61.859 | 608 / 636 (95.597%) | 0 / 0 | 2761.643 / 4356.172 / 4879.316 | 15.134 / 15.338 / 15.525 |

Good output tokens/s is `AIPerf goodput.avg` in requests/s multiplied by the fixed 200 output tokens/request. The observed auto-minus-disabled difference is +16.403 tokens/s, or **+0.584%**. The plan's prospective practical-gain threshold is 1%, so this one pair does not clear it. All SLA failures were TTFT-only: 26 for auto and 28 for disabled; neither run had an ITL breach or a request classified bad on both measures. The client-reported mean TTFT/ITL were 1229.983/14.924 ms for auto and 1247.407/14.883 ms for disabled.

This is screening evidence from one 40-second scored profile per policy. The small throughput difference is below the predeclared gate and is not a validated policy improvement.

## Execution and matched treatment

Both top-level Slurm allocations completed with `COMPLETED 0:0` on two nodes with 16 GPUs, serially on 23 October UTC. Job 25712 ran 7:56 (16:05:20–16:13:16); job 25713 ran 7:18 (16:13:24–16:20:42). From allocation start, all workers were ready at 323.6 s and 291.9 s; all pairs were warm at 360.4 s and 326.9 s. Scored profile phases lasted 43.308 s and 43.277 s. The retained [terminal sacct snapshot](sacct-terminal.txt) also shows the long-lived nested serving `srun` steps cancelled at allocation teardown; the separate warmup/client steps and scored request phases completed. That teardown status is not a scored request cancellation.

Both frozen `submitted-payload/check-screen.py` copies and both `submitted-payload/audit-capacity.py` copies were rerun directly against their corresponding raw directories; all four commands passed. The frozen SHA256SUMS in each submitted payload also verified. The capacity checks found:

| Role | TP / EP | `ServerArgs` and initialized scheduler limit | Dtype / backend / chunk | Initialized prefill graph policy |
|---|---|---|---|---|
| prefill-0 and prefill-1 | 4 / 1 | 64 / 64 each | bfloat16 / DeepGEMM / 8192 | auto: breakable; disabled: disabled |
| decode-0 | 8 / 8 | 256 / 256 | bfloat16 / HPC-Ops / 8192 | auto: role default disabled; disabled: disabled |

For auto, both prefill roles logged default `cuda_graph_backend_prefill=None` and resolved `breakable`; decode logged the same unset flag and resolved prefill graph `disabled` under its decode-disaggregation role. The disabled treatment logged the explicit backend on all roles. The separate screen check found target prefill graph captures on all four TP ranks of both prefill servers only in auto; it found dense decode graph configuration and capture for batch sizes 1–64 on all eight decode ranks in both jobs. No speculative algorithm or draft model was active.

The normalized submitted AIPerf input configs both match their frozen expected config and each other. The actual 227,995,065-byte `inputs.json` files also have identical SHA-256 `51c49804d6bbb941ff87546b78d123c0a3670d08ee9add2ffcf557a4c528a5c1`. The client image hashes match. Across submitted payloads, runtime-serving files match except the planned disabled backend flag in `worker.sh`; `topology-job.sh` passes the policy to the audit. Remaining file differences are the policy/name/path fields in config and Slurm metadata, derived provenance, and checksums. Resolved fields checked by the capacity gate match between jobs after removing the prefill policy; all three per-role ServerArgs random seeds differ between allocations and are recorded in [REVIEW.json](REVIEW.json).

## Output and runtime observations

Each short output smoke checked 8 cases: 7 pass and `reverse` fails in both runs and in both frozen references, with no new regression. The long-context diagnostic passed 12/12 cases for each run. Local diagnostics do not verify the official contest accuracy threshold. Output lengths were 636×200 tokens for disabled; auto produced 636×200 plus one 199-token and one 201-token response. The score calculation remains based on the planned fixed 200-token factor.

Per-role GPU and host sampling was aligned to each scoring phase at five-second intervals. GPU queries reported `ok`; each scoring window had 9 sampler snapshots, except disabled `prefill-1` with 8. Values below summarize individual GPU samples, not sums across ranks:

| Role | Policy | GPU activity p50 / max (%) | Sampled maximum VRAM used (MiB/GPU) | Sampled maximum power (W/GPU) |
|---|---|---:|---:|---:|
| prefill-0 | auto | 96 / 99 | 133,344 | 691.0 |
| prefill-1 | auto | 97 / 99 | 133,346 | 696.1 |
| decode-0 | auto | 100 / 100 | 134,424 | 486.5 |
| prefill-0 | disabled | 97 / 100 | 132,156 | 694.0 |
| prefill-1 | disabled | 97 / 100 | 132,156 | 693.5 |
| decode-0 | disabled | 100 / 100 | 134,356 | 483.1 |

The sampler also retained host CPU jiffies, memory, and network counters; this review does not turn those cumulative/shared counters into CPU utilization or per-role network throughput. Server `/metrics` scrapes returned HTTP 200 for all scoring-window samples; startup samples include `URLError` before the endpoints were available. Scored server gauges and role batch logs show decode running requests peaking at 53/55 in five-second server metric samples (56/55 in scheduler batch logs), with zero decode queue. Prefill server metric samples saw at most 20/18 queued requests for auto and 6/3 for disabled, with at most 3 running and at most 0.02 token-usage fraction. The more frequent scheduler batch logs recorded prefill queue peaks of 24/24 for auto and 22/22 for disabled, inflight requests up to 5, and pending tokens up to 99,217/91,019 respectively. The sampled `sglang:num_used_tokens` gauge peaked at 27,543/28,372 on the auto prefill roles and 27,172/27,522 on disabled; decode peaked at 260,870/261,114. These role-side gauges, GPU activity, sampled VRAM used, and token-usage fraction are distinct measurements and are not interchangeable. The gauges/log snapshots are sparse and do not establish continuous saturation or a cause for the score difference.

## Limits and next decision

The short runs have no profiler kernel traces. The scored per-request export retains latency and output length, not generated token IDs; correctness evidence comes from the separate smoke and long-context probes. Server metrics and scheduler logs are sampled; per-role sampler outputs are phase-aligned but do not prove a causal bottleneck. Allocation order was auto then disabled, and server random seeds differ. These facts matter because the observed gain is smaller than 1%. Keep it as a completed matched policy screen, not as evidence for a durable throughput advantage. No ranked/full-speed score, official accuracy result, or EAGLE speedup is claimed.

## Reproduction and provenance

From this directory, run `./reproduce.sh`. It reruns the exact submitted checks and builds [REVIEW.json](REVIEW.json) plus [SOURCE-MANIFEST.json](SOURCE-MANIFEST.json) from the fixed raw paths. The source manifest hashes the raw logs, profiling artifacts, input corpus, submitted gate scripts, configs, and sampler records without copying them. Verify this review bundle with `sha256sum -c SHA256SUMS`.

## Prospective candidate decision

The candidate is **disabled prefill graphs (25713)**, and the control is **automatic native resolution (25712)**. Compute the predeclared direction as `(candidate / control - 1) × 100`: **-0.580368%**. The disabled candidate loses in this short pair and misses the +1% promotion gate. Close the standalone disabled-policy performance branch unchanged. This does not globally stop research, and it does not compare EAGLE against target-only inference. The inverse percentage elsewhere in the report describes auto relative to disabled; it is not the candidate's gain. `DECISION.json` retains the numbers and limits.
