# S56 EAGLE3 candidate for unranked performance exploration

This prospective source bundle derives from S49 while retaining its EAGLE3 steps 2/top-k 1/three draft tokens/FlashInfer settings, CPU draft-byte and worker identity checks, deterministic BF16 target/draft runtime, all-rank NIXL checks, native 190-region candidate geometry, and both P/D semantic warmups. It shares identical worker and topology files with S55; `QWEN_HAS_DRAFT=1` adds only the candidate's EAGLE3 flags.

Actual job 25862's independent review remains bound in the parent plan and source provenance: runtime, native geometry, P/D semantic checks, and candidate repeat stability passed, while the strict exact-reference stage failed for all 1,600 IDs. That failure is unchanged and is not treated as an official quality verdict. The performance protocol does not invoke the exact-ID checker.

The post-readiness workload is the same single N=64 AIPerf point, 7/8 smoke floor, and 12 retrieval requests used by S55. An independent head checker validates raw input settings, SLA request counts, errors/cancellations, smoke/retrieval output, runtime, geometry, draft identity, and semantic receipts. The batch file enforces an absolute 1,020-second stop and verifies the pinned model/image and client image identities.

This is unranked feasibility evidence only. Quality is UNKNOWN; no official accuracy or speedup claim is made. Root review and root-owned submission handling are still required. No GPU, queue, or endpoint action occurred during preparation.
