# 23 October: real H200 reference failed before the token client started

**Question and prior evidence.** Review terminal exact-reference job 25495 before any EAGLE3 successor. It was intended to retain 1600 actual generated IDs, not a ranked score.

**Observations.** Top-level Slurm FAILED/1:0 after 406 seconds. Original frozen/submitted payload and all raw artifacts now have verified terminal hashes. Actual native workers/router reached readiness, BF16 KV logs cover 4+4+8 ranks, and both independent semantic P/D receipts replay successfully. Pyxis then refused the token-client container because its advertised role HOME directory had never been created. No token client ran, no result file or diagnostic output IDs exist; the head correctly rejected the missing result.

**Correction.** Earlier CPU launcher mocks did not validate container mount source directories and therefore missed this real bug. Their failure-propagation coverage was valid but did not establish Pyxis launch readiness. [Full diagnosis and preserved evidence](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-review-25495-20261023/REVIEW.md).

**Next decision.** Freeze a separate reference repair creating token-client HOME before launch, with a real-shell mount-prerequisite regression rejecting the old source and reaching the fake client with the fix. Preserve all target/transport/protocol/client/deadline settings and original failed bytes. One justified repair allocation may follow within the five-job H200 cap; EAGLE3 remains conditional on actual 1600-ID reference acceptance. No new job, score or PBS SU is created by this review.
