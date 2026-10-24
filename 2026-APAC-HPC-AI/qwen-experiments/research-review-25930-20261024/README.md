# Job 25930: incomplete target-only control run

Job **25930** ran for **528 seconds** and ended `FAILED (1:0)`. The deterministic BF16 runtime check, 188-region prefill KV geometry check, and two prefill-to-decode semantic warmups passed. AIPerf also completed the requested N=64 profiling interval and retained raw request records. The benchmark then failed because `benchmark.sh` looked for `summarize.py` inside the run output directory (`ART`) even though the helper was present in the submitted bundle. The empty summary caused the head check to fail, and the smoke and retrieval checks never ran.

The raw export contains 367 profiling requests, with zero recorded request errors/cancellations, but also reports zero good requests and zero goodput under the configured latency thresholds. Its throughput and latency aggregates are retained as partial profiler evidence only. They do not form a valid completed control score. Job 25935, the dependent candidate, was cancelled while pending, so there is no matched comparison or qualified speedup. Model quality remains unevaluated.

Raw run artifacts were not changed. See `REVIEW.json` and `accounting.psv` for details and source hashes.
