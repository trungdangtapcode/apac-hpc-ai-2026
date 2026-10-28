# Portable reader correction, 29 October 2026 Vietnam time

Actual GPU job27136 initialized all workers and both semantic P/D routes, then completed the official N64 AIPerf command. It ended1:0 because local readers assumed exports directly under artifacts/. AIPerf0.12 placed them in artifacts/qwen-openai-chat-concurrency64/.

The corrected readers accept exactly one complete pair at the artifact root or one immediate child and reject ambiguity, missing/incomplete pairs and symlink namespaces. Phase exports are excluded. The official command, model/worker flags, score formula and SLA limits remain unchanged. Eight regression tests and the repaired gate on retained raw data pass.

Recovered performance:3050.225487 good output tokens/s,1880 of1906 good requests (98.635887%), zero errors/cancellations. TTFT mean/p95=1102.185717/1297.447714ms; request-mean ITL mean/p95=15.011058/15.165369ms. This is an individual protocol observation after postprocessing repair, not a validated new optimization or a successful original scheduler job. Original failure and raw evidence are preserved. No hardware sampler or separate smoke/retrieval suite ran here; official full-set accuracy remains UNKNOWN.

The patched postprocessors were validated on real retained raw data. A subsequent end-to-end GPU replay remains separate until its receipt and review. Historical delivery checks describe the earlier package; this correction has its own targeted validation.
