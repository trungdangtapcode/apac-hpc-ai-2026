# Best observed result for each serving metric

This report answers: **What is the best recorded value of each metric across the available experiment history?** Each row is an independent record. The table does not describe one configuration that achieves every record at once.

H200 and H100 results are listed separately. The table contains measurements from those systems, not estimated conversions between GPU types.

## Records and units

{{RECORD_TABLE}}

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

{{JOB_DETAILS}}

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
