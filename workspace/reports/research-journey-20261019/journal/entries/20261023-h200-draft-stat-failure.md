# A filesystem fingerprint is local; draft content needs a portable identity

23 October 2026. H200 25682 fails at 75 s before demonstrated model initialization because its g4 worker rejects the draft's stat tuple against another-node full report. The parent full byte/header/adapter check passed. No actual differing worker stat/hash was captured, so remote equality or corruption is not established. Zero actual output IDs are retained; EAGLE correctness and speedup are still unverified.

The repair preserves strict identity by full-hashing the draft separately in each worker, comparing portable bytes/SHA and publisher/config/header identities, and requiring all three role-local receipts. Local before/after stat checks remain valid for detecting changes during a read. Exact 1600-ID equality, native runtime, graph, geometry and semantic P/D gates stay unchanged. No original payload is modified. [Raw failure and supported next decision](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-review-25682-20261023/REVIEW.md).

For a presentation: “Device and inode identify a file in one filesystem view. To prove that workers on different nodes see the intended model, we compare the actual file bytes by hash. We still reject altered content.”
