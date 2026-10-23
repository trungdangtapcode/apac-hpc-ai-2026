# Full production-span bytes pass while PBS exits unsuccessfully

23 October 2026. [Prior hypothesis and actual submission](20261023-full-span-transfer-submission.md).

224116.pbs111 is terminal F / exit 1 after 229 s, estimated 16.284444 SU. Retain this failed job status. Its independently replayed native data receipts pass: each of two H100 GPUs registers 190×76,132,096-byte KV spans; 380 selected region/page payloads (97,280 bytes) are correct, all 14,465,000,960 untouched destination bytes are GPU-scanned, the sender remains intact, and ten whole auxiliary spans (933,888 bytes) match. Rank semantic work finishes by T0+100.161 s, component marker by T0+130.146 s. The per-rank process RSS and CUDA allocator samples are inspected. PBS utilization counters conflict with allocation and duration, so no zero-usage or healthy-hardware conclusion is justified.

A task log reports exit 1 although the outer launcher records zero; final cleanup and semantic markers exist. Stageout_status is 1. These observations do not establish the exact failing layer. Next isolate container, node cleanup and parent exits with durable receipts before a full-model repair. This is technical progress beyond small buffers, not a new serving score or EAGLE correctness result. Official accuracy remains unverified and H200 25682 is still pending.

The charge is not yet posted; keep maximum 42.666667 SU reserved and internal headroom 4507.703333 SU. [Complete question, controls, observations, inspection gaps, interpretation and next decision](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-review-224116-20261023/REVIEW.md).

For a presentation: “We have now proved that selected KV pages can move correctly across two GPUs at production-sized memory registrations. The scheduler still reports a failed process, so we preserve the successful data evidence separately and investigate the exit path before claiming the whole integration works.”
