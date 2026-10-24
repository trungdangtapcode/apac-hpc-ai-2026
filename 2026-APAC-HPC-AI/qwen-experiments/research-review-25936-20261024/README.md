# Job 25936: DP chunk alignment rejected before model load

Job **25936** ended `FAILED (1:0)` after **82 seconds**. Five assigned H200 devices, pinned runtime source preflight, and header-only FP8 model metadata checks passed. SGLang then adjusted the configured global chunked-prefill size 8192 across DP size 5 to 1638 tokens per rank. That value leaves remainder 38 modulo the configured 64-token page size, so server-argument validation raised `chunked_prefill_size must be divisible by page_size`.

The server did not load the model or reach health, rank metadata, or output checks. No correctness, quality, or performance result exists. R5's explicit 10240 global chunk size is a source-prepared follow-up hypothesis (2048 per rank, divisible by 64), not a result from this job.

The run artifacts were read only. Telemetry has six sparse pre-model-startup samples across five GPUs; the server metrics endpoint returned `URLError` for all six. These samples are not evidence of a healthy serving state or a causal hardware diagnosis. See `REVIEW.json`, `SOURCE_PROOF.json`, and `accounting.psv`.
