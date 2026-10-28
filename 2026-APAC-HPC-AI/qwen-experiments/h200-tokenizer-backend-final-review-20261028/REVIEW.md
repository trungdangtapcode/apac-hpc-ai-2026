# H200 tokenizer and prefill backend final review

Reviewed 29 October 2026, Vietnam time (UTC+7); scheduler run dates use their retained timezone. This review covers completed H200 jobs 26951, 26953 and 27077 against fresh matched control 26949. It reuses the existing full-load reviewer at `h200-full-load-review-20261026/review-full.py`. The per-job machine-readable reports remain beside that reviewer as `review-26951.json`, `review-26953.json` and `review-27077.json`; the existing `review-26949.json` was preserved.

## Results

| Job | Configuration | Good output tokens/s | Change vs 26949 | Mean / p95 TTFT (ms) | Mean / p95 ITL (ms) | Joint SLA |
|---|---|---:|---:|---:|---:|---:|
|26949|Fresh tokenizer-off control|3034.761|—|1128 / 1423|14.979 / 15.147|98.628%|
|26951|Prefill dynamic tokenizer, 200 microsecond batch wait|3040.592|+0.192%|1117 / 1349|14.998 / 15.155|98.632%|
|26953|Prefill dynamic tokenizer, 2 millisecond batch wait|3042.964|+0.270%|1118 / 1309|14.993 / 15.160|98.632%|
|27077|Prefill FlashInfer attention, page size 1|2841.004|-6.385%|1480 / 1886|14.499 / 14.659|98.323%|

Good output tokens/s is AIPerf Goodput requests/s multiplied by the fixed 200 output tokens per request. The two tokenizer settings are less than 1% above their matched control. Both are below the earlier native-runtime observation 26766 (3045.502 tokens/s) by 0.161% and 0.083%, respectively. These are single-run observations and do not establish a tokenizer-caused gain or a new best.

FlashInfer had lower mean and p95 ITL, alongside a 6.385% throughput reduction and worse mean and p95 TTFT relative to 26949. This is a measured tradeoff in one run, not an overall improvement. It does not justify claiming a causal new best or changing the default on this evidence.

## Gate and evidence review

All three completed jobs passed the unchanged full local performance gate. For each, the review verified terminal Slurm state `COMPLETED 0:0`, no live allocation, frozen payload checksum, raw fixed-workload denominator, actual runtime arguments, native KV geometry, both semantic routes, and local smoke/retrieval outputs. Each had zero profiling errors and cancellations, smoke 7/8 with no regression, and retrieval 12/12. The exact N64, 4000-input/200-output workload, seed 2026, 60/120/30 second phases and joint request SLA remained in force. The complete evidence and gate outputs are in the per-job JSON reports.

TTFT breaches over 3000 ms were 26 for each tokenizer run and 30 for FlashInfer; ITL breaches over 20 ms were zero. All runs remained above the unchanged 90% joint request threshold. This is a local performance pass only: official full-set accuracy remains UNKNOWN, and no official score or quality claim follows.

The reviewer inspected all three role logs for selected NIXL/transport errors and tracebacks; none were found. It retained role-local queue, running-request and KV-token gauges; sampled GPU activity and VRAM; host CPU and memory observations; and server HTTP/error polls. The full evidence is embedded in `comparison.json` and in each per-job reviewer output. Sampling is every five seconds within the first-to-last profiling request-start envelope, excludes warmup and final drain, and has uncalibrated cross-host clock skew. GPU activity is not FLOPS, VRAM is not KV occupancy, and these observations do not identify a causal bottleneck. Request identifiers are not retained generated model token IDs.

The earlier failed exact-reference comparison remains a quality limitation; this performance review does not resolve it. The prior 26766 comparison is a contextual native-runtime reference, not the matched control. No run was changed or promoted based on this review. Close both unchanged tokenizer arms below the predeclared useful-gain threshold and retain FA3 prefill for the incumbent. FlashInfer page1 remains a measured compatibility/control point for a possible future coupled page/backend test; its throughput loss must be recovered before any gain could be claimed.

## Preservation

`seal.py` verifies terminal accounting and SHA-256 manifests for listed files in raw run directories 26949, 26951, 26953 and 27077, including each job's `.out` and `.err` scheduler streams. Existing manifests and immutable submitted payloads are preserved; missing terminal accounting/manifests are added without editing payload contents. The script rechecks hashes after sealing.

Exact safe capture paths for this review are:

- `qwen-experiments/h200-tokenizer-backend-final-review-20261028/REVIEW.md`
- `qwen-experiments/h200-tokenizer-backend-final-review-20261028/comparison.json`
- `qwen-experiments/h200-tokenizer-backend-final-review-20261028/seal.py`
- `qwen-experiments/h200-full-load-review-20261026/review-26951.json`
- `qwen-experiments/h200-full-load-review-20261026/review-26953.json`
- `qwen-experiments/h200-full-load-review-20261026/review-27077.json`
- `qwen-experiments/runs/26949/` and `qwen-experiments/runs/26949.out`, `qwen-experiments/runs/26949.err`
- `qwen-experiments/runs/26951/` and `qwen-experiments/runs/26951.out`, `qwen-experiments/runs/26951.err`
- `qwen-experiments/runs/26953/` and `qwen-experiments/runs/26953.out`, `qwen-experiments/runs/26953.err`
- `qwen-experiments/runs/27077/` and `qwen-experiments/runs/27077.out`, `qwen-experiments/runs/27077.err`

`comparison.json` records the full exact list of raw run directories and scheduler streams. No shared notes, run ledger, submissions, other track files, commits or new jobs were changed as part of this bounded review.
