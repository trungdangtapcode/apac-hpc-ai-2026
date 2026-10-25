# S62r4 job 26081: partial routes, bounded timeout, no benchmark

Reviewed 25 October 2026. Slurm records FAILED 1:0 after 8:59 on g1/g4, 16 H200 GPUs. Runtime and 32-record native KV gates passed. The 180-second semantic warmup ended with status 124 before AIPerf; there is no profile. Goodput, scored TTFT/ITL, SLA fraction, profiled errors/cancellations and output accuracy are NOT_MEASURED, not zero. Allocation is 2.3956 GPU-hours; no separate PBS SU.

Both prefill-1/decode-0 and prefill-1/decode-1 returned HTTP 200, nonempty assistant responses and 8 completion tokens. The independent audit rechecks raw response hashes, semantic body/usage, endpoint inventory and run binding. Both routes from prefill-0 are missing. Replaying the full semantic gate rejects exactly two missing receipts. Longer HTTP waiting was sufficient to recover two routes beyond 26076, but did not repair the full topology.

Health/worker readiness and KV buffer registration are necessary prerequisites; they do not certify end-to-end KV transfer. Prefill-0 remains alive and reports bootstrap requests, and shutdown records AbortReq KVTransferError after termination. These observations do not establish the initiating transport cause. Do not describe all NIXL communication as down because the two prefill-1 routes worked. Do not label this a model-quality failure or a throughput loss.

Startup/initialization telemetry covers 16 distinct GPU UUIDs, 99–100 samples per role. Successful server polls number 61/62/72/78 for decode-0/decode-1/prefill-0/prefill-1. This is startup coverage only; scored utilization/CPU/KV/tail measurements are unavailable. Hardware saturation and causal bottlenecks are not inferred. Full metrics were collected to raw logs but only coverage and available server health were inspected here; phase-specific utilization values were not analysed.

Decision: close further full-topology S62 retries as prospectively required after this bounded failure. Investigate existing failed-prefill-0 versus successful-prefill-1 transport/metadata evidence before proposing any separate scoped diagnostic. Keep useful research running through the distinct routing and fusion hypotheses rather than repeating the unchanged topology.

Five jobs were admitted earlier. After 26081 terminated, four remain queued: 26083 fresh round-robin control; 26085 power-of-two; 26089 prefill-only native QK/RoPE fusion; 26091 decode-only fusion. All three candidates have afterany:26083, with local acceptance still conditional on the actual control. At the 06:20 UTC snapshot another account holds g1/g4 via two one-node jobs; preserve queue positions. Team01 publicly has one pending job at that query. Public names/counts do not reveal its scores, optimization details or contest standing. No private team artifacts were read.

The H200 full-protocol frontier remains 3044.400475 good output tokens/s; official full-set accuracy is unknown. [Independent audit](inspection.json), [queue snapshot](queue-snapshot.json), raw artifacts and frozen submitted payload in runs/26081. Earlier five-active-job and partial-running snapshots remain historical evidence.

Source review: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-review-26081-20261025/REVIEW.md
