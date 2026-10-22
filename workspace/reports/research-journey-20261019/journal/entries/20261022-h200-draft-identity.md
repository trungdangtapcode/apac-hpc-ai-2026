# 22 October: fresh draft identity before native H200 speculative integration

**Question and prior evidence.** Full N64 independently repeats near 3044.28 good output tokens/s. The full N64/N68 pair 25487/25488 and exact-reference diagnostic 25495 are pending at this checkpoint. Speculative decoding is a distinct possible source of improvement, but the earlier full H100 attempt failed on transport. Header/alias checks alone did not establish current H200 draft bytes.

**Change and control.** A new CPU-only verifier streams the actual local 1,145,943,008-byte draft, checks its full pinned publisher SHA256 and all retained tensor-header entries, and checks the draft-only native architecture adapter. The official target and all frozen jobs are unchanged. No allocation or additional PBS reservation was made.

**Observations.** Full digest PASS; all 15 entries match, with 13 BF16 and two I32 tensors. Stable device/inode/size/mtime/ctime across reads; about 2.162368 seconds in this cached read. This is not startup time, native loading, transport or output-equivalence evidence. [Byte record and full interpretation](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/eagle3-h200-candidate-assets-20261022/REVIEW.md).

**Assessment and next decision.** The actual staged draft is intact. Keep EAGLE3 conditional on terminal semantic acceptance of the fresh H200 reference, then derive from native Slurm with explicit BF16/unquantized draft, uniformly eager prefill, actual redacted KV geometry, independent warmup receipts and all 1600 exact output IDs. No EAGLE3 speedup or official accuracy is claimed. The old port plan's size-only snapshot is historical; fresh full model/image and draft audits supersede that narrow uncertainty.

**Preservation.** Capture this verifier, safe manifests, review and routing notes as a small separate checkpoint. Never capture draft/model/image bytes, private cache state or authentication material.
