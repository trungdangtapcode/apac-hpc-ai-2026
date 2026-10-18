# Best observed result for each serving metric

This report answers: **What is the best recorded value of each metric across the available experiment history?** Each row is an independent record. The table does not describe one configuration that achieves every record at once.

H200 and H100 results are listed separately. The table contains measurements from those systems, not estimated conversions between GPU types.

## Records and units

| Platform | Metric | Best observed value | Unit | Job ID | N |
|---|---|---:|---|---|---:|
| H200 | Good output throughput ↑ | 2786.696 | good tokens/s | 24544 | 58 |
| H200 | Mean TTFT ↓ | 328.900 | ms | 23773 | 53 |
| H200 | Mean ITL ↓ | 13.495 | ms/token interval | 22517 | 16 |
| H200 | Joint SLA pass rate ↑ | 100.000 | % | 22416 (2 tied observations) | 16 |
| H100 | Good output throughput ↑ | 2371.961 | good tokens/s | 221315.pbs111 | 50 |
| H100 | Mean TTFT ↓ | 303.288 | ms | 220720.pbs111 | 32 |
| H100 | Mean ITL ↓ | 17.138 | ms/token interval | 220909.pbs111 | 32 |
| H100 | Joint SLA pass rate ↑ | 100.000 | % | 220562.pbs111 (14 tied observations) | 32 |

**N means the number of concurrent requests**, not GPU count, batch size, prompt length or total requests in the dataset. For example, N56 means a closed-loop client targets 56 requests in flight and starts replacement requests as others finish. GPU allocation is a separate setting.

The arrows show the preferred direction: **↑ higher is better; ↓ lower is better**. Here, TTFT and ITL are averages across measured requests. They are not p95 or maximum latency.

## What each metric means

### Goodput: useful completed requests per second

Goodput counts only requests that meet **both** latency conditions. A failed request or a request that misses either condition contributes nothing to goodput.

- Native unit: **requests per second**, written `request/s` or `req/s`.
- This report uses **good output tokens per second**, written `good tokens/s`, because the workload asks for 200 output tokens per request.
- Conversion: `good output tokens/s = good requests/s × 200`.
- Direction: **higher is better**, subject to the SLA and output-quality requirements.

For example, 2,715.842 good tokens/s corresponds to about **13.579 qualifying requests/s**. It does not mean a single user receives 2,715 tokens each second. It is aggregate throughput across the service.

Use the goodput exported by AIPerf, multiplied by 200. Do not substitute `successful requests / 120` for the exported rate: the effective accounting duration and completion handling must follow the benchmark's implementation.

**Raw output throughput is different:** it can include tokens from requests that were too slow. More total tokens do not necessarily mean more good tokens.

### TTFT: time to first token

TTFT is how long a request waits, from the benchmark client's request start until the first generated token arrives. It reflects the user's initial wait, including the serving path observed by the client, such as queueing, prompt processing and transfer.

- Full name: **Time To First Token**.
- Unit: **milliseconds (`ms`)**. `1,000 ms = 1 second`.
- Direction: **lower is better**.
- Per-request limit used in these experiments: **TTFT ≤ 3,000 ms**, or **3 seconds**.

For example, a TTFT of 328.90 ms means the first token arrives after about **0.329 seconds on average**. This is not the time required to generate the entire answer.

### ITL: time between generated tokens

ITL describes the pace of the response after generation begins. The benchmark evaluates a request's mean interval between output tokens.

- Full name: **Inter-Token Latency**.
- Unit: **milliseconds per token interval**, conventionally reported as **`ms`** or **`ms/token`**.
- Direction: **lower is better**.
- Per-request limit used in these experiments: **mean ITL ≤ 20 ms**.

For intuition, ITL is approximately the elapsed time from first to last output token divided by the number of token intervals. With 200 output tokens there are approximately 199 intervals. Use AIPerf's exported value for scoring; streaming chunks and timestamps can make a hand calculation differ from the exported metric.

For example, 13.49 ms between tokens is roughly **74 tokens/s for one continuously generating request** (`1,000 / 13.49`). This is an intuitive conversion, not the service's aggregate goodput. At 20 ms per interval, generating the remaining 199 intervals takes about 3.98 seconds, in addition to the initial TTFT.

The table's mean ITL averages request measurements. A low mean does not prove that every request meets the 20 ms condition, or that every individual token gap is below 20 ms.

### Joint SLA pass rate: requests that satisfy both latency limits

The joint SLA pass rate measures the fraction of requests that succeed and meet **both** TTFT and mean ITL limits in the same request.

`SLA pass rate (%) = 100 × qualifying requests / all evaluated requests`

- Unit: **percent (`%`)**. The raw export may store a fraction: `1.0 = 100%`, and `0.988194 ≈ 98.8194%`.
- Direction: **higher is better**.
- Required threshold used here: **at least 90%**.
- Errors remain in the denominator and do not count as qualifying requests. The benchmark's cancellation and completion rules also apply; the historical record scan additionally excludes points reporting request errors or cancellations.

For example, if 1,000 requests are evaluated and 950 succeed within both limits, the pass rate is **95%**. A request with TTFT 2,000 ms but mean ITL 25 ms fails; so does one with TTFT 3,500 ms and mean ITL 15 ms.

Averages alone cannot establish this pass rate. The average TTFT and average ITL could both look acceptable while too many individual requests fail. A 100% pass rate is the maximum observed value, so multiple runs can tie. It does not guarantee that future requests will always pass.

### Accuracy and output quality: a separate requirement

Latency SLA pass rate is **not answer accuracy**. The organisers' requirement to retain at least 99% of reference accuracy is a relative quality requirement, not a claim that the model answers 99% of questions correctly.

For illustration, if a reference score were 80%, retaining 99% of that score would mean 79.2%, under a simple relative-score rule. The official evaluation determines the actual scoring and aggregation.

The current short output checks and 12-case long diagnostics are research checks. They do **not** establish the organisers' full-set accuracy requirement. There is therefore **no verified official-accuracy winner** in this report.

## How to read the configuration labels

- **Job ID** identifies the scheduler allocation and its saved logs. H100 jobs use PBS IDs such as `221058.pbs111`; H200 jobs use Slurm IDs such as `24291`.
- **N** is concurrent client requests. Changing N changes workload pressure, so a latency record at N16 and a throughput record at N56 answer different questions.
- **TP** means tensor parallelism: GPUs cooperate to run a model worker by splitting tensor computations.
- **EP** means expert parallelism: MoE experts are distributed across GPUs in a worker.
- **Prefill** processes the input prompt. **Decode** generates subsequent output tokens.

The H200 highest observed goodput is job 24544: DeepGEMM prefill, auto decode, chunk 8192, concurrency 58, at 2,786.696 good tokens/s. It passes full local checks and is 2.5244% above historical same-load chunk 4096 control 24352. A new same-load control and independent repeat are submitted: the historical comparator alone cannot isolate batching from time/node drift.

The H100 highest observed goodput is job 221315.pbs111: HPC-Ops prefill and decode, chunk 4096, concurrency 50, at 2,371.961 good tokens/s. It passes full local checks and is 2.7277% above immediately preceding matched decode-only control 221314. Only the prefill runner changes. Mean TTFT improves, while mean ITL rises slightly. Independent repeat 221339 passes at 2371.341, +2.7009% versus the previous control; a fresh reversed-order control is running. Official full-set accuracy is unverified.

## Configuration and optimisation history of each record job

The cards include every tied SLA job, not only the example shown in the summary table. Configuration files describe intended settings; runtime fields below are separately extracted from saved role logs when available. An `auto` setting is a policy, not proof of one fixed kernel backend. Missing fields and old preparation metadata must not be silently treated as verified runtime.

All listed layouts allocate 16 GPUs across two nodes and use SGLang to serve Qwen3-235B-A22B-Instruct-2507-FP8. The scored client is AIPerf with the protocol above. FP8 here describes the supplied model checkpoint, not a new quantisation performed by these trials. Common intended settings include context length 8,192 and static memory fraction 0.9; `kv_dtype=auto` is the requested KV setting, and BF16 runtime claims require log/review evidence. A GPU memory fraction is not model accuracy or GPU utilisation.

**What the optimisations do:** chunked prefill divides prompt processing into bounded pieces; round-robin distributes prompts across prefill workers; CUDA graphs reduce repeated GPU launch overhead for supported shapes; DeepGEMM provides a selected MoE computation backend; FlashInfer supplies decode attention kernels; MNNVL selects an all-reduce fusion backend; NIXL transfers KV data between separate prefill and decode workers. The heterogeneous-TP descriptor patch repairs transfer compatibility and is not a demonstrated standalone throughput optimisation. Weight prefetch targets checkpoint loading before serving.

Jump to a job: [H200 24544](#h200-job-24544) · [H200 23773](#h200-job-23773) · [H200 22517](#h200-job-22517) · [H200 22416](#h200-job-22416) · [H200 22532](#h200-job-22532) · [H100 221315.pbs111](#h100-job-221315pbs111) · [H100 220720.pbs111](#h100-job-220720pbs111) · [H100 220909.pbs111](#h100-job-220909pbs111) · [H100 220562.pbs111](#h100-job-220562pbs111) · [H100 220575.pbs111](#h100-job-220575pbs111) · [H100 220721.pbs111](#h100-job-220721pbs111) · [H100 220722.pbs111](#h100-job-220722pbs111) · [H100 220908.pbs111](#h100-job-220908pbs111)

### H200 job 24544

**Record held:** goodput at N58.

**Layout:** 8 GPUs for prefill: 2 worker(s), each TP4/EP1. 8 GPUs for decode: 1 worker(s), each TP8/EP8.

**Experiment:** `s11-dg-chunk8192-n58`. Scheduler: Slurm.

| Recorded point | Good tokens/s | Mean TTFT (ms) | Mean ITL (ms) | Joint SLA (%) |
|---|---:|---:|---:|---:|
| N58 (confirm) | 2786.696 | 774.057 | 16.515 | 98.8493 |

**Configured additions:**

- Prefill: `--chunked-prefill-size 8192 --moe-runner-backend deep_gemm`.
- Decode: `--flashinfer-allreduce-fusion-backend mnnvl --decode-attention-backend flashinfer`.
- Router: `--prefill-policy round_robin`.
- KV transfer: `nixl`; descriptor patch: `hetero-tp-request-descriptors-v1`.

**Submitted worker additions:** these preserve inherited launch settings that may be absent from the config metadata.

```text
--chunked-prefill-size 8192 --moe-runner-backend deep_gemm
```

```text
--cuda-graph-max-bs-decode 64 --cuda-graph-bs-decode 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59 60 61 62 63 64 --flashinfer-allreduce-fusion-backend mnnvl --decode-attention-backend flashinfer
```

**Available runtime fields** (one representative log per role; this extraction is not an all-rank audit):

| Setting | Prefill worker 0 | Decode worker 0 |
|---|---|---|
| `attention_backend` | 'fa3' | 'fa3' |
| `chunked_prefill_size` | 8192 | 8192 |
| `decode_attention_backend` | None | 'flashinfer' |
| `ep_size` | 1 | 8 |
| `flashinfer_allreduce_fusion_backend` | 'auto' | 'mnnvl' |
| `kv_cache_dtype` | 'auto' | 'auto' |
| `moe_runner_backend` | 'deep_gemm' | 'auto' |
| `tp_size` | 4 | 8 |

**How this result was obtained and what it proves:** DeepGEMM prefill, auto decode, chunk 8192, concurrency 58 reaches 2,786.696 good tokens/s. All local checks pass. It is 2.5244% above historical same-load chunk 4096 control 24352; a new N58 control 24589 and independent repeat 24588 are submitted. One historical comparison cannot isolate chunk gain from node/time drift. Official full-set accuracy is unverified.

**Evidence:** [saved configuration](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/runs/24544/config.json); [run artifacts](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/runs/24544); [AIPerf export for the first listed point](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/runs/24544/confirm/n58/artifacts/profile_export_aiperf.json) ; [submitted worker script](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/runs/24544/submitted/worker.sh).

### H200 job 23773

**Record held:** mean TTFT at N53.

**Layout:** 8 GPUs for prefill: 2 worker(s), each TP4/EP1. 8 GPUs for decode: 1 worker(s), each TP8/EP8.

**Experiment:** `s5-rr-best-repeat`. Scheduler: Slurm.

| Recorded point | Good tokens/s | Mean TTFT (ms) | Mean ITL (ms) | Joint SLA (%) |
|---|---:|---:|---:|---:|
| N53 (confirm) | 2438.470 | 328.900 | 19.673 | 98.8816 |

**Configured additions:**

- Prefill: `--chunked-prefill-size 4096`.
- Decode: `--cuda-graph-max-bs-decode 64 --cuda-graph-bs-decode 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59 60 61 62 63 64`.
- Router: `--prefill-policy round_robin`.
- KV transfer: `nixl`; descriptor patch: `hetero-tp-request-descriptors-v1`.

**Submitted worker additions:** these preserve inherited launch settings that may be absent from the config metadata.

```text
--chunked-prefill-size 4096
```

```text
--cuda-graph-max-bs-decode 64 --cuda-graph-bs-decode 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59 60 61 62 63 64
```

**Available runtime fields** (one representative log per role; this extraction is not an all-rank audit):

| Setting | Prefill worker 0 | Decode worker 0 |
|---|---|---|
| `attention_backend` | 'fa3' | 'fa3' |
| `chunked_prefill_size` | 4096 | 8192 |
| `decode_attention_backend` | None | None |
| `ep_size` | 1 | 8 |
| `flashinfer_allreduce_fusion_backend` | 'auto' | 'auto' |
| `kv_cache_dtype` | 'auto' | 'auto' |
| `moe_runner_backend` | 'auto' | 'auto' |
| `tp_size` | 4 | 8 |

**How this result was obtained and what it proves:** This was an independent repeat of the earlier round-robin serving configuration at N53. It used 4,096-token prefill chunks and dense decode CUDA graph sizes 1–64. Round-robin sends prompts across the two prefill workers; CUDA graphs aim to reduce launch overhead. Runtime logs show FA3 attention and auto MoE/all-reduce settings, rather than the later MNNVL plus FlashInfer decode combination. The minimum recorded TTFT is an observation of this complete setup; this report does not isolate how much each optimisation contributed.

**Evidence:** [saved configuration](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/runs/23773/config.json); [run artifacts](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/runs/23773); [AIPerf export for the first listed point](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/runs/23773/confirm/n53/artifacts/profile_export_aiperf.json) ; [submitted worker script](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/runs/23773/submitted/worker.sh).

### H200 job 22517

**Record held:** mean ITL at N16.

**Layout:** 4 GPUs for prefill: 2 worker(s), each TP2/EP1. 12 GPUs for decode: 3 worker(s), each TP4/EP4.

**Experiment:** `P4-TP2_D12-TP4-EP4`. Scheduler: Slurm.

| Recorded point | Good tokens/s | Mean TTFT (ms) | Mean ITL (ms) | Joint SLA (%) |
|---|---:|---:|---:|---:|
| N16 (confirm) | 837.154 | 1035.407 | 13.495 | 98.6667 |

**Configured additions:**

- Prefill: No additional prefill flags recorded in config.json; inspect runtime below..
- Decode: No additional decode flags recorded in config.json; inspect runtime below..
- Router: No additional router flags recorded in config.json..
- KV transfer: `nixl`; descriptor patch: `hetero-tp-request-descriptors-v1`.

**Available runtime fields** (one representative log per role; this extraction is not an all-rank audit):

| Setting | Prefill worker 0 | Decode worker 0 |
|---|---|---|
| `attention_backend` | 'fa3' | 'fa3' |
| `chunked_prefill_size` | 8192 | 8192 |
| `decode_attention_backend` | None | None |
| `ep_size` | 1 | 4 |
| `flashinfer_allreduce_fusion_backend` | 'auto' | 'auto' |
| `kv_cache_dtype` | 'auto' | 'auto' |
| `moe_runner_backend` | 'auto' | 'auto' |
| `tp_size` | 2 | 4 |

**How this result was obtained and what it proves:** This early topology trial allocated more GPUs to decode: three independent TP4/EP4 decode workers, with only two TP2 prefill workers. At N16, relatively few requests compete for those workers. That is a plausible explanation for the low ITL, but it is not an isolated causal test. This run did not use the later explicit DeepGEMM, MNNVL, FlashInfer decode or 4,096-token prefill tuning. Its latency record does not make it the best aggregate-throughput configuration.

**Evidence:** [saved configuration](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/runs/22517/config.json); [run artifacts](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/runs/22517); [AIPerf export for the first listed point](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/runs/22517/confirm/n16/artifacts/profile_export_aiperf.json) ; [submitted worker script](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/runs/22517/submitted/worker.sh).

### H200 job 22416

**Record held:** joint SLA at N16.

**Layout:** 12 GPUs for prefill: 3 worker(s), each TP4/EP1. 4 GPUs for decode: 1 worker(s), each TP4/EP4.

**Experiment:** `P12-TP4_D4-TP4-EP4`. Scheduler: Slurm.

| Recorded point | Good tokens/s | Mean TTFT (ms) | Mean ITL (ms) | Joint SLA (%) |
|---|---:|---:|---:|---:|
| N16 (confirm) | 828.111 | 437.820 | 16.981 | 100.0000 |

**Configured additions:**

- Prefill: No additional prefill flags recorded in config.json; inspect runtime below..
- Decode: No additional decode flags recorded in config.json; inspect runtime below..
- Router: No additional router flags recorded in config.json..
- KV transfer: `nixl`; descriptor patch: `not selected`.

**Available runtime fields** (one representative log per role; this extraction is not an all-rank audit):

| Setting | Prefill worker 0 | Decode worker 0 |
|---|---|---|
| `attention_backend` | 'fa3' | 'fa3' |
| `chunked_prefill_size` | 8192 | 8192 |
| `decode_attention_backend` | None | None |
| `ep_size` | 1 | 4 |
| `flashinfer_allreduce_fusion_backend` | 'auto' | 'auto' |
| `kv_cache_dtype` | 'auto' | 'auto' |
| `moe_runner_backend` | 'auto' | 'auto' |
| `tp_size` | 4 | 4 |

**How this result was obtained and what it proves:** This topology allocated 12 GPUs to three TP4 prefill workers and four GPUs to one TP4/EP4 decode worker. N16 is a light load compared with the current goodput frontier. Every evaluated request in the selected full run met both latency limits. This demonstrates a 100% observed pass rate at that load, not a uniquely superior backend or capacity limit.

**Evidence:** [saved configuration](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/runs/22416/config.json); [run artifacts](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/runs/22416); [AIPerf export for the first listed point](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/runs/22416/confirm/n16/artifacts/profile_export_aiperf.json) ; [submitted worker script](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/runs/22416/submitted/worker.sh).

### H200 job 22532

**Record held:** joint SLA at N16.

**Layout:** 12 GPUs for prefill: 6 worker(s), each TP2/EP1. 4 GPUs for decode: 1 worker(s), each TP4/EP4.

**Experiment:** `P12-TP2_D4-TP4-EP4`. Scheduler: Slurm.

| Recorded point | Good tokens/s | Mean TTFT (ms) | Mean ITL (ms) | Joint SLA (%) |
|---|---:|---:|---:|---:|
| N16 (confirm) | 776.248 | 708.656 | 16.887 | 100.0000 |

**Configured additions:**

- Prefill: No additional prefill flags recorded in config.json; inspect runtime below..
- Decode: No additional decode flags recorded in config.json; inspect runtime below..
- Router: No additional router flags recorded in config.json..
- KV transfer: `nixl`; descriptor patch: `hetero-tp-request-descriptors-v1`.

**Available runtime fields** (one representative log per role; this extraction is not an all-rank audit):

| Setting | Prefill worker 0 | Decode worker 0 |
|---|---|---|
| `attention_backend` | 'fa3' | 'fa3' |
| `chunked_prefill_size` | 8192 | 8192 |
| `decode_attention_backend` | None | None |
| `ep_size` | 1 | 4 |
| `flashinfer_allreduce_fusion_backend` | 'auto' | 'auto' |
| `kv_cache_dtype` | 'auto' | 'auto' |
| `moe_runner_backend` | 'auto' | 'auto' |
| `tp_size` | 2 | 4 |

**How this result was obtained and what it proves:** This tied SLA record used six TP2 prefill workers on 12 GPUs and one TP4/EP4 decode worker on four GPUs, at N16. It is a different topology from job 22416 even though both achieved 100% SLA. The observation does not establish which topology is better at higher concurrency.

**Evidence:** [saved configuration](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/runs/22532/config.json); [run artifacts](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/runs/22532); [AIPerf export for the first listed point](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/runs/22532/confirm/n16/artifacts/profile_export_aiperf.json) ; [submitted worker script](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/runs/22532/submitted/worker.sh).

### H100 job 221315.pbs111

**Record held:** goodput at N50.

**Layout:** 8 GPUs for prefill: 2 worker(s), each TP4/EP1. 8 GPUs for decode: 1 worker(s), each TP8/EP8.

**Experiment:** `h100-hpc-both-31`. Scheduler: PBS.

| Recorded point | Good tokens/s | Mean TTFT (ms) | Mean ITL (ms) | Joint SLA (%) |
|---|---:|---:|---:|---:|
| N50 (confirm) | 2371.961 | 486.401 | 18.221 | 98.7838 |

**Configured additions:**

- Prefill: `--chunked-prefill-size 4096 --weight-loader-prefetch-checkpoints --moe-runner-backend hpc_ops`.
- Decode: `--flashinfer-allreduce-fusion-backend mnnvl --decode-attention-backend flashinfer --moe-runner-backend hpc_ops`.
- Router: `--prefill-policy round_robin`.
- KV transfer: `nixl`; descriptor patch: `hetero-tp-request-descriptors-v1`.

**Submitted worker additions:** these preserve inherited launch settings that may be absent from the config metadata.

```text
--chunked-prefill-size 4096 --weight-loader-prefetch-checkpoints --moe-runner-backend hpc_ops
```

```text
--cuda-graph-max-bs-decode 64 --cuda-graph-bs-decode 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59 60 61 62 63 64 --flashinfer-allreduce-fusion-backend mnnvl --decode-attention-backend flashinfer --moe-runner-backend hpc_ops
```

**Runtime extraction:** representative role logs do not contain parseable ServerArgs here. Review task-side logs and the linked review before treating requested flags as verified activation.

**How this result was obtained and what it proves:** HPC-Ops prefill+decode at concurrency 50 reaches 2,371.961 good tokens/s, +2.7277% versus immediately preceding decode-only HPC-Ops control 221314 at 2,308.979. Only the prefill MoE runner changes. Mean TTFT falls 669.245 to 486.401 ms; mean ITL rises 17.831 to 18.221 ms. Full local payload, protocol, runtime and output gates pass. Independent repeat and fresh reversed-order control are submitted; official full-set accuracy is unverified.

**Evidence:** [saved configuration](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/collected/221315.pbs111/20261018T132318646525Z/runs/221315.pbs111/config.json); [run artifacts](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/collected/221315.pbs111/20261018T132318646525Z/runs/221315.pbs111); [AIPerf export for the first listed point](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/collected/221315.pbs111/20261018T132318646525Z/runs/221315.pbs111/confirm/n50/artifacts/profile_export_aiperf.json) ; [submitted worker script](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/collected/221315.pbs111/20261018T132318646525Z/runs/221315.pbs111/submitted/worker.sh).

### H100 job 220720.pbs111

**Record held:** mean TTFT, joint SLA at N32; joint SLA at N34; joint SLA at N36.

**Layout:** 8 GPUs for prefill: 2 worker(s), each TP4/EP1. 8 GPUs for decode: 1 worker(s), each TP8/EP8.

**Experiment:** `h100-mnnvl-04`. Scheduler: PBS.

| Recorded point | Good tokens/s | Mean TTFT (ms) | Mean ITL (ms) | Joint SLA (%) |
|---|---:|---:|---:|---:|
| N32 (confirm) | 1692.166 | 303.288 | 17.247 | 100.0000 |
| N34 (confirm) | 1754.073 | 355.723 | 17.465 | 100.0000 |
| N36 (confirm) | 1787.737 | 348.287 | 18.249 | 100.0000 |

**Configured additions:**

- Prefill: `--chunked-prefill-size 4096`.
- Decode: `--flashinfer-allreduce-fusion-backend mnnvl`.
- Router: `--prefill-policy round_robin`.
- KV transfer: `nixl`; descriptor patch: `hetero-tp-request-descriptors-v1`.

**Submitted worker additions:** these preserve inherited launch settings that may be absent from the config metadata.

```text
--chunked-prefill-size 4096
```

```text
--cuda-graph-max-bs-decode 64 --cuda-graph-bs-decode 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59 60 61 62 63 64 --flashinfer-allreduce-fusion-backend mnnvl
```

**Runtime extraction:** representative role logs do not contain parseable ServerArgs here. Review task-side logs and the linked review before treating requested flags as verified activation.

**How this result was obtained and what it proves:** This first H100 MNNVL trial added the decode all-reduce fusion backend mnnvl to the earlier round-robin/chunk4096/dense-graph baseline. Its N32 export contains the historical TTFT minimum. However, role logs were empty, so runtime activation was not fully proved for this allocation. Do not attribute the 303.288 ms TTFT causally to MNNVL or present it as a fully validated deployment. Later jobs repeated the setting with improved logging.

**Evidence:** [saved configuration](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/collected/220720.pbs111/20261016T132540573992Z/runs/220720.pbs111/config.json); [run artifacts](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/collected/220720.pbs111/20261016T132540573992Z/runs/220720.pbs111); [AIPerf export for the first listed point](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/collected/220720.pbs111/20261016T132540573992Z/runs/220720.pbs111/confirm/n32/artifacts/profile_export_aiperf.json) ; [submitted worker script](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/collected/220720.pbs111/20261016T132540573992Z/runs/220720.pbs111/submitted/worker.sh).

### H100 job 220909.pbs111

**Record held:** mean ITL, joint SLA at N32; joint SLA at N34.

**Layout:** 8 GPUs for prefill: 2 worker(s), each TP4/EP1. 8 GPUs for decode: 1 worker(s), each TP8/EP8.

**Experiment:** `h100-mnnvl-repeat-08`. Scheduler: PBS.

| Recorded point | Good tokens/s | Mean TTFT (ms) | Mean ITL (ms) | Joint SLA (%) |
|---|---:|---:|---:|---:|
| N32 (confirm) | 1680.796 | 350.838 | 17.138 | 100.0000 |
| N34 (confirm) | 1758.237 | 332.219 | 17.537 | 100.0000 |

**Configured additions:**

- Prefill: `--chunked-prefill-size 4096`.
- Decode: `--flashinfer-allreduce-fusion-backend mnnvl`.
- Router: `--prefill-policy round_robin`.
- KV transfer: `nixl`; descriptor patch: `hetero-tp-request-descriptors-v1`.

**Submitted worker additions:** these preserve inherited launch settings that may be absent from the config metadata.

```text
--chunked-prefill-size 4096
```

```text
--cuda-graph-max-bs-decode 64 --cuda-graph-bs-decode 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59 60 61 62 63 64 --flashinfer-allreduce-fusion-backend mnnvl
```

**Runtime extraction:** representative role logs do not contain parseable ServerArgs here. Review task-side logs and the linked review before treating requested flags as verified activation.

**How this result was obtained and what it proves:** This was the MNNVL repeat with compute-task logging, paired with fresh control 220908. The reviewed goodput improvement was about 7.52% at N32 and 8.24% at N34 versus that control. Runtime proof was recovered from task-side logs. The job also holds the observed H100 mean ITL record at N32. The matched comparison supports a throughput benefit in those tests; it does not separately establish that MNNVL caused the minimum ITL.

**Evidence:** [saved configuration](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/collected/220909.pbs111/20261017T005441565035Z/runs/220909.pbs111/config.json); [run artifacts](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/collected/220909.pbs111/20261017T005441565035Z/runs/220909.pbs111); [AIPerf export for the first listed point](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/collected/220909.pbs111/20261017T005441565035Z/runs/220909.pbs111/confirm/n32/artifacts/profile_export_aiperf.json) ; [submitted worker script](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/collected/220909.pbs111/20261017T005441565035Z/runs/220909.pbs111/submitted/worker.sh).

### H100 job 220562.pbs111

**Record held:** joint SLA at N32.

**Layout:** 8 GPUs for prefill: 2 worker(s), each TP4/EP1. 8 GPUs for decode: 1 worker(s), each TP8/EP8.

**Experiment:** `nscc-pbs-baseline-n32-readiness-02`. Scheduler: PBS.

| Recorded point | Good tokens/s | Mean TTFT (ms) | Mean ITL (ms) | Joint SLA (%) |
|---|---:|---:|---:|---:|
| N32 (confirm) | 1565.161 | 346.633 | 18.572 | 100.0000 |

**Configured additions:**

- Prefill: `--chunked-prefill-size 4096`.
- Decode: `--cuda-graph-max-bs-decode 64 --cuda-graph-bs-decode 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59 60 61 62 63 64`.
- Router: `--prefill-policy round_robin`.
- KV transfer: `nixl`; descriptor patch: `hetero-tp-request-descriptors-v1`.

**Submitted worker additions:** these preserve inherited launch settings that may be absent from the config metadata.

```text
--chunked-prefill-size 4096
```

```text
--cuda-graph-max-bs-decode 64 --cuda-graph-bs-decode 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59 60 61 62 63 64
```

**Runtime extraction:** representative role logs do not contain parseable ServerArgs here. Review task-side logs and the linked review before treating requested flags as verified activation.

**How this result was obtained and what it proves:** This early full H100 baseline used the transferred round-robin/chunk4096/dense-graph configuration at N32. Longer readiness allowances addressed slow checkpoint loading; they are startup reliability settings, not inference throughput optimisations. The 100% observed SLA rate at N32 is a low-load baseline result. Old metadata saying a benchmark was not yet run is preparation history, not the terminal result.

**Evidence:** [saved configuration](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/collected/220562.pbs111/20261015T194640353769Z/runs/220562.pbs111/config.json); [run artifacts](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/collected/220562.pbs111/20261015T194640353769Z/runs/220562.pbs111); [AIPerf export for the first listed point](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/collected/220562.pbs111/20261015T194640353769Z/runs/220562.pbs111/confirm/n32/artifacts/profile_export_aiperf.json) ; [submitted worker script](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/collected/220562.pbs111/20261015T194640353769Z/runs/220562.pbs111/submitted/worker.sh).

### H100 job 220575.pbs111

**Record held:** joint SLA at N32; joint SLA at N34.

**Layout:** 8 GPUs for prefill: 2 worker(s), each TP4/EP1. 8 GPUs for decode: 1 worker(s), each TP8/EP8.

**Experiment:** `nscc-load-sweep-03`. Scheduler: PBS.

| Recorded point | Good tokens/s | Mean TTFT (ms) | Mean ITL (ms) | Joint SLA (%) |
|---|---:|---:|---:|---:|
| N32 (confirm) | 1570.212 | 321.759 | 18.633 | 100.0000 |
| N34 (confirm) | 1625.595 | 331.753 | 19.090 | 100.0000 |

**Configured additions:**

- Prefill: `--chunked-prefill-size 4096`.
- Decode: `--cuda-graph-max-bs-decode 64 --cuda-graph-bs-decode 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59 60 61 62 63 64`.
- Router: `--prefill-policy round_robin`.
- KV transfer: `nixl`; descriptor patch: `hetero-tp-request-descriptors-v1`.

**Submitted worker additions:** these preserve inherited launch settings that may be absent from the config metadata.

```text
--chunked-prefill-size 4096
```

```text
--cuda-graph-max-bs-decode 64 --cuda-graph-bs-decode 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59 60 61 62 63 64
```

**Runtime extraction:** representative role logs do not contain parseable ServerArgs here. Review task-side logs and the linked review before treating requested flags as verified activation.

**How this result was obtained and what it proves:** This H100 baseline established full-protocol performance before MNNVL tuning, including N32 and N34 observations with 100% joint SLA. It retains the earlier round-robin, chunk4096 and dense-graph setup. Its role here is a baseline and an SLA tie, not the final throughput winner.

**Evidence:** [saved configuration](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/collected/220575.pbs111/20261016T054555388584Z/runs/220575.pbs111/config.json); [run artifacts](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/collected/220575.pbs111/20261016T054555388584Z/runs/220575.pbs111); [AIPerf export for the first listed point](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/collected/220575.pbs111/20261016T054555388584Z/runs/220575.pbs111/confirm/n32/artifacts/profile_export_aiperf.json) ; [submitted worker script](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/collected/220575.pbs111/20261016T054555388584Z/runs/220575.pbs111/submitted/worker.sh).

### H100 job 220721.pbs111

**Record held:** joint SLA at N32; joint SLA at N34.

**Layout:** 8 GPUs for prefill: 2 worker(s), each TP4/EP1. 8 GPUs for decode: 1 worker(s), each TP8/EP8.

**Experiment:** `h100-flashinfer-05`. Scheduler: PBS.

| Recorded point | Good tokens/s | Mean TTFT (ms) | Mean ITL (ms) | Joint SLA (%) |
|---|---:|---:|---:|---:|
| N32 (confirm) | 1542.053 | 333.854 | 18.939 | 100.0000 |
| N34 (confirm) | 1602.838 | 312.350 | 19.482 | 100.0000 |

**Configured additions:**

- Prefill: `--chunked-prefill-size 4096`.
- Decode: `--decode-attention-backend flashinfer`.
- Router: `--prefill-policy round_robin`.
- KV transfer: `nixl`; descriptor patch: `hetero-tp-request-descriptors-v1`.

**Submitted worker additions:** these preserve inherited launch settings that may be absent from the config metadata.

```text
--chunked-prefill-size 4096
```

```text
--cuda-graph-max-bs-decode 64 --cuda-graph-bs-decode 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59 60 61 62 63 64 --decode-attention-backend flashinfer
```

**Runtime extraction:** representative role logs do not contain parseable ServerArgs here. Review task-side logs and the linked review before treating requested flags as verified activation.

**How this result was obtained and what it proves:** This standalone H100 attention trial selected FlashInfer for decode without the later explicit MNNVL combination. It achieved 100% SLA at the listed lower loads, but historical matched throughput was about 1–2% below the baseline. A 100% pass-rate tie therefore does not imply that this optimisation improved goodput.

**Evidence:** [saved configuration](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/collected/220721.pbs111/20261016T132615690894Z/runs/220721.pbs111/config.json); [run artifacts](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/collected/220721.pbs111/20261016T132615690894Z/runs/220721.pbs111); [AIPerf export for the first listed point](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/collected/220721.pbs111/20261016T132615690894Z/runs/220721.pbs111/confirm/n32/artifacts/profile_export_aiperf.json) ; [submitted worker script](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/collected/220721.pbs111/20261016T132615690894Z/runs/220721.pbs111/submitted/worker.sh).

### H100 job 220722.pbs111

**Record held:** joint SLA at N32; joint SLA at N34.

**Layout:** 8 GPUs for prefill: 2 worker(s), each TP4/EP1. 8 GPUs for decode: 1 worker(s), each TP8/EP8.

**Experiment:** `h100-loader-prefetch-06`. Scheduler: PBS.

| Recorded point | Good tokens/s | Mean TTFT (ms) | Mean ITL (ms) | Joint SLA (%) |
|---|---:|---:|---:|---:|
| N32 (confirm) | 1565.656 | 348.003 | 18.572 | 100.0000 |
| N34 (confirm) | 1622.773 | 342.228 | 19.086 | 100.0000 |

**Configured additions:**

- Prefill: `--chunked-prefill-size 4096 --weight-loader-prefetch-checkpoints`.
- Decode: `--cuda-graph-max-bs-decode 64 --cuda-graph-bs-decode 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59 60 61 62 63 64`.
- Router: `--prefill-policy round_robin`.
- KV transfer: `nixl`; descriptor patch: `hetero-tp-request-descriptors-v1`.

**Submitted worker additions:** these preserve inherited launch settings that may be absent from the config metadata.

```text
--chunked-prefill-size 4096 --weight-loader-prefetch-checkpoints
```

```text
--cuda-graph-max-bs-decode 64 --cuda-graph-bs-decode 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59 60 61 62 63 64
```

**Runtime extraction:** representative role logs do not contain parseable ServerArgs here. Review task-side logs and the linked review before treating requested flags as verified activation.

**How this result was obtained and what it proves:** This H100 trial added checkpoint weight prefetch to reduce loading time. Prefetch is a startup and allocation-cost hypothesis, not inherently a faster per-token inference method. The historical short allocation is confounded by load, node and cache differences, and old role logs were incomplete; no causal loading speedup is established. It ties on SLA at the listed lower loads.

**Evidence:** [saved configuration](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/collected/220722.pbs111/20261016T145617950924Z/runs/220722.pbs111/config.json); [run artifacts](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/collected/220722.pbs111/20261016T145617950924Z/runs/220722.pbs111); [AIPerf export for the first listed point](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/collected/220722.pbs111/20261016T145617950924Z/runs/220722.pbs111/confirm/n32/artifacts/profile_export_aiperf.json) ; [submitted worker script](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/collected/220722.pbs111/20261016T145617950924Z/runs/220722.pbs111/submitted/worker.sh).

### H100 job 220908.pbs111

**Record held:** joint SLA at N32; joint SLA at N34.

**Layout:** 8 GPUs for prefill: 2 worker(s), each TP4/EP1. 8 GPUs for decode: 1 worker(s), each TP8/EP8.

**Experiment:** `h100-control-07`. Scheduler: PBS.

| Recorded point | Good tokens/s | Mean TTFT (ms) | Mean ITL (ms) | Joint SLA (%) |
|---|---:|---:|---:|---:|
| N32 (confirm) | 1563.237 | 321.242 | 18.671 | 100.0000 |
| N34 (confirm) | 1624.351 | 331.682 | 19.088 | 100.0000 |

**Configured additions:**

- Prefill: `--chunked-prefill-size 4096`.
- Decode: No additional decode flags recorded in config.json; inspect runtime below..
- Router: `--prefill-policy round_robin`.
- KV transfer: `nixl`; descriptor patch: `hetero-tp-request-descriptors-v1`.

**Submitted worker additions:** these preserve inherited launch settings that may be absent from the config metadata.

```text
--chunked-prefill-size 4096
```

```text
--cuda-graph-max-bs-decode 64 --cuda-graph-bs-decode 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59 60 61 62 63 64
```

**Runtime extraction:** representative role logs do not contain parseable ServerArgs here. Review task-side logs and the linked review before treating requested flags as verified activation.

**How this result was obtained and what it proves:** This fresh H100 control used the same task-side logging as MNNVL candidate 220909. It retained round-robin prefill, chunk4096 and dense decode graphs without explicitly selecting MNNVL. It supplies a fairer same-load reference and ties at 100% SLA at N32 and N34. Logging is an evidence fix, not a model optimisation.

**Evidence:** [saved configuration](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/collected/220908.pbs111/20261017T005441200160Z/runs/220908.pbs111/config.json); [run artifacts](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/collected/220908.pbs111/20261017T005441200160Z/runs/220908.pbs111); [AIPerf export for the first listed point](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/collected/220908.pbs111/20261017T005441200160Z/runs/220908.pbs111/confirm/n32/artifacts/profile_export_aiperf.json) ; [submitted worker script](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/collected/220908.pbs111/20261017T005441200160Z/runs/220908.pbs111/submitted/worker.sh).

### Matched comparisons and review sources

- [DeepGEMM 24291 runtime, quality and control comparison](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-10/prefill-pilot-reviews/24291-v2.json)
- [H100 221058 sealed sweep review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/inspection/manual-20261017-0858/review-221058.pbs111.json)
- [H100 220909 versus 220908 matched review and runtime proof](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/inspection/manual-20261017/pair-review.json)

Some inherited metadata names earlier controls or an old concurrency. The per-point AIPerf export and terminal reviews determine the measured load and comparison; an old config comment is not a new measurement.

## Scope and evidence limits

The scan ranks available historical points with:

- A configured **60-second warmup**, **120-second measurement**, and **30-second grace period** for outstanding requests. Grace is not an extra steady-state measurement window.
- **4,000 input tokens** and **200 requested output tokens**.
- A reported joint SLA pass and zero reported request errors or cancellations.

Short exploratory sweeps are excluded. These are **observed historical records**, not a new runtime and quality audit of every old allocation. The scan checks the saved protocol configuration and reported metrics; it does not independently revalidate every raw request or terminal seal. It cannot establish repeatability or statistical significance by choosing a minimum or maximum.

Important qualifications:

- **H100 TTFT, job 220720:** 303.288 ms is present in the metric export, but the historical review found empty role logs, leaving intended runtime incompletely verified. Treat this as an observed metric record, not a fully validated deployment winner.
- **H100 ITL, job 220909:** later task-side logs provide runtime proof.
- **H200 goodput, job 24544:** full local checks pass; compare the submitted independent N58 repeat and fresh same-load control before treating the 2.5244% historical comparison as a confirmed chunk gain.
- **H100 goodput, job 221315:** full local checks pass; the original 2.7277% prefill HPC-Ops gain is followed by independent repeat 221339 at 2371.341 (+2.7009% versus the previous control). The fresh decode-only control is running.
- **SLA ties:** all tied observations are stored in `records.json`. The table shows one example job and the number of tied observations, not a uniquely best configuration.
- **Snapshot:** this report reflects the saved artifacts scanned when `build.py` runs. It is not live scheduler status.

Low concurrency often improves latency while reducing service throughput. Select a serving configuration by **maximising goodput while meeting latency and quality requirements**; choosing only the smallest TTFT or ITL can select a much less productive service.

## Sources and reproduction

- [Machine-readable records, all ties and raw export paths](records.json).
- [Report generator and selection rules](build.py).
- [Configuration and runtime data for all record jobs](job-details.json).
- [Job detail renderer](run_details.py).
- [Detailed metric explanations used by the generator](REPORT.template.md).
- [Current candidate comparison](../metric-comparison-20261017/REPORT.md).
- [Cross-platform comparison and its limits](../cross-platform-20261017/REPORT.md).

Run `python3 build.py` from this directory to rescan the available results and regenerate the record table. The generator retains these explanations. Raw experiment artifacts are not modified.
