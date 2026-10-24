# S61: H200 EAGLE3 on decode workers only

## Evidence and question

The matched short-screen control and all-workers EAGLE3 candidate completed AIPerf profiling under the same N64 4,000/200 workload. The candidate lowered mean request ITL from 14.833 ms to 7.820 ms and raised raw output throughput from 2,895.18 to 2,926.13 tokens/s, but mean TTFT rose from 1,311.60 ms to 2,631.95 ms. Its joint request fraction fell from 95.24% to 83.49%, so it cannot meet the 90% score gate. The 3,044.400475 full-protocol frontier remains unchanged.

The earlier full N64 target-only logs configure no speculative algorithm on either prefill worker or on decode. S60 enabled EAGLE3 on all three workers. This is the next factor to isolate.

## Hypothesis

EAGLE3 draft execution is useful on decode but unnecessary on prefill. Keeping both prefill workers target-only may reduce prefill-side state and recover TTFT while preserving decode-side speculative ITL gains.

## Controlled configuration

- Platform: two H200 nodes, 16 GPUs total.
- Topology: two TP4 prefill workers and one TP8/EP8 decode worker.
- Fixed workload: N64, 4,000 input tokens, 200 output tokens, cold prefix cache, seed 2026.
- Short feasibility screen: 20-second warmup, 40-second measure, 30-second grace.
- Common runtime: FP8 target weights, BF16 target KV, FlashInfer sampling, HPC-Ops decode, MNNVL decode fusion, dense decode graphs 1–64, prefill graphs disabled, NIXL.
- One factor versus the actual target-only control: EAGLE3 with two steps, top-k 1 and three draft tokens on decode-0 only. Prefill-0 and prefill-1 must resolve all speculative arguments to null and allocate only the target BF16 KV pool.
- Matched control: reviewed actual S59 job 25947. Its source manifest, 0:0 terminal state and independent raw protocol replay are bound in the candidate bundle.

## Admission and stop gates

The frozen candidate bundle and a checksum-bound root review are required before admission. The candidate must pass all rank-level KV/NIXL checks, one decode-host draft fingerprint, native startup/graph checks, both P/D semantic paths, zero errors/cancellations, at least 90% joint latency success, the existing 7/8 smoke floor without a new regression, and 12/12 retrieval. Failure of the 90% short-screen floor ends the EAGLE3 branch; no full-length confirmation follows.

This is unranked feasibility evidence. It does not test MMLU-Pro/GPQA or certify the official ≥99% reference-accuracy gate. No speedup is established from a single screen.

## Source checks

The bundle is derived from the frozen S60 payload, records the parent manifest, and has its own SHA-256 manifest. CPU-only checks verify shell and Python syntax, all bundle hashes, the decode-only role condition, the root-reviewed S59 schema binding, and the target-only prefill geometry expectation. Actual resolved server arguments and runtime gates remain the job's responsibility.

## Result status

Submitted as Slurm job **25988** on 24 October 2026 at 20:04:27 UTC, 16 H200 GPUs across two nodes, 17-minute maximum, no dependency. Initial queue state: PENDING (Resources). Test-only ID 25987 is virtual and was never submitted. Preserve the actual scheduler receipt at [slurm-receipt.json](slurm-receipt.json) and pre-admission review at [ROOT_REVIEW.json](ROOT_REVIEW.json). Full prior-pair reasoning is in the [paired review](../research-review-25947-25948-20261024/REVIEW.md).
