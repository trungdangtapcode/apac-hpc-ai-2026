# Full-set Qwen answer-quality result

Reviewed **2026-11-03T11:25:47.125335+07:00, Vietnam time (UTC+7)**. **PASS for our predeclared local MMLU-Pro comparison.** All sixteen quality allocations are `COMPLETED 0:0`; the complete 12,032-question test split was evaluated once by each deployment. The finite workflow completed at **04:19:08 on 3 November 2026, Vietnam time**. The fresh queue check at 11:22 Vietnam time was empty because this fixed study had finished.

## The exact answer

| Measurement | Stock FP8 reference | Optimised candidate |
|---|---:|---:|
| Same test questions | 12,032 | 12,032 |
| Correct answers | **9,460** | **9,452** |
| Accuracy | **78.623670%** | **78.557181%** |
| Service errors | 0 | 0 |
| Invalid parsed answers, retained as wrong | 101 | 101 |
| Answers reaching the 2,048-token generation limit, retained | 1,484 | 1,468 |

**Accuracy retention = (9452 / 12032) / (9460 / 12032) = 9452 / 9460 = 99.915433% ≥ 99%.**

This is retention of the reference score. It does **not** mean the model answers 99.915433% of questions correctly. The actual candidate accuracy is 78.557181%. It is 8 correct answers below the reference, or **0.066489 percentage points lower accuracy**. With this measured reference, at least 9,366 correct answers were required to pass the declared point threshold; the candidate has 86 more than that integer minimum.

The denominator is our stock deployment of the official FP8 checkpoint, measured on the same questions. It is not an unpublished numeric score supplied by the organisers. The precise claim is **“full local MMLU-Pro accuracy-retention check passed”**, not “BTC has certified a pass.” No organiser quality certificate or private-harness result has been received.

## Why this comparison answers the engineering question

The question was whether our complete serving implementation changes answer quality materially, despite retaining the official checkpoint. We compared a stock colocated deployment against the accepted serving configuration from job 28197, using the same **16 H200 GPUs on g1/g4**, pinned dataset, prepared prompt text and chat template, adaptive demonstration count, generation settings and answer parser. This is entirely an H200-to-H200 comparison; no H100 extrapolation enters it.

The stock reference has two colocated TP8/EP8 replicas. The candidate has two TP4/EP1 prefill workers on the first node and TP8/EP8 decode on the second, with its retained backend and NIXL optimisations. Both use the official `Qwen3-235B-A22B-Instruct-2507-FP8` checkpoint. The deployments are compared as a whole; this experiment does not isolate the effect of any individual kernel or patch.

The full study uses N64 closed-loop quality requests, greedy decoding and up to 2,048 answer tokens. It is separate from the 4,000/200-token performance benchmark. Both roles receive exactly the same 12,032 question IDs, once each, in eight fixed shards. No retry replaces an incorrect answer, no losing shard is omitted, and the final score uses total correct counts rather than averaging shard ratios.

[The detailed method](METHODOLOGY.md) explains the sources, prompt-fitting process, controls, parser, errors, failed attempts and exact pinned identities.

## What each pair measured

Each row contains 1,504 identical questions per role. Shard indexes are zero-based.

| Shard | Reference job | Candidate job | Reference correct | Candidate correct | Difference | Retention |
|---:|---:|---:|---:|---:|---:|---:|
| 0 | 28373 | 28375 | 1200 | 1205 | +5 | 100.416667% |
| 1 | 28382 | 28384 | 1206 | 1204 | -2 | 99.834163% |
| 2 | 28386 | 28388 | 1166 | 1167 | +1 | 100.085763% |
| 3 | 28390 | 28392 | 1175 | 1166 | -9 | 99.234043% |
| 4 | 28394 | 28396 | 1211 | 1203 | -8 | 99.339389% |
| 5 | 28398 | 28400 | 1149 | 1153 | +4 | 100.348129% |
| 6 | 28402 | 28404 | 1156 | 1169 | +13 | 101.124567% |
| 7 | 28406 | 28408 | 1197 | 1185 | -12 | 98.997494% |

There are gains and losses across shards. The earlier partial result of 100.124688% on the first 3,008 questions was a valid dated snapshot, not the final result. The separate N16 128-question pilot failed its point gate at 102/104 = 98.076923%; that result and the original FP8 reference startup failure remain preserved. Pilot responses were not mixed into this N64 full-set result.

## What the result proves, and what remains uncertain

The paired outcomes are **9,018 both correct**, **2,138 both wrong**, **434 candidate-only correct**, and **442 reference-only correct**. Therefore “eight fewer correct answers” is a net difference across **876 questions with different correctness outcomes**. It does not mean the two services produce identical answers except for eight questions. Even both-correct responses can have different wording or reasoning.

The aggregate gate passes. Category outcomes are not uniform: computer science retains 338/345 = **97.971014%**, and philosophy 383/387 = **98.966408%**. No per-category 99% gate was predeclared, so these are retained limitations, not silently excluded categories. [All fourteen category counts and paired outcomes](../../../2026-APAC-HPC-AI/qwen-experiments/quality-verification-20261102/reviews/final-independent-20261103/INDEPENDENT_REVIEW.md) are available for questions from judges.

This is one complete pass per deployment, partitioned for allocation limits. The independent replay recomputes the saved answers; it is not a second GPU repetition. The result does not establish statistical equivalence across future workloads, unchanged outputs, a particular numerical cause, or preservation on GPQA/other unseen benchmarks. Differences in layout, kernels and batching can affect decoding, but this study does not isolate that mechanism.

## How we checked the evidence

- An independent replay of all raw API bodies reproduced 9,460 and 9,452 correct answers with the frozen scorer, exact common coverage and zero service errors. Recorded run and response hashes match the original complete aggregate.
- Native Slurm accounting independently confirms all sixteen allocations `COMPLETED 0:0`; callback completion is not used as a substitute for terminal scheduler state.
- The original **310 frozen payload files** and **27 additional guarded files** still match their recorded hashes and byte lengths.
- All **24,064 reported API prompt lengths** match CPU preparation, with none missing. This verifies lengths, not server-side input token IDs, which were not collected.
- Invalid and length-capped outputs remain in the denominator. No physical GPU utilisation/power/bandwidth or CPU telemetry was collected for these quality runs; request-time and runtime-log inspection cannot substitute for it.

[Original full comparison](../../../2026-APAC-HPC-AI/qwen-experiments/quality-verification-20261102/workflow/FULL_COMPARISON.json), [independent replay](../../../2026-APAC-HPC-AI/qwen-experiments/quality-verification-20261102/reviews/final-independent-20261103/INDEPENDENT_REVIEW.md), [native accounting](../../../2026-APAC-HPC-AI/qwen-experiments/quality-verification-20261102/reviews/full-terminal-accounting-20261103/ACCOUNTING.json), and [full prompt-length check](../../../2026-APAC-HPC-AI/qwen-experiments/quality-verification-20261102/reviews/API_PROMPT_LENGTH_CHECK_FULL_24064.json) retain the actual evidence.

[Review of the final eleven runs](../../../2026-APAC-HPC-AI/qwen-experiments/quality-verification-20261102/reviews/final-diagnostics-20261103/FINAL_DIAGNOSTICS.md) retains per-run invalid outputs, length caps, non-stream latency tails, usage, selected logs and missing-telemetry limits.

## Decision and cost

Retain the candidate: the declared aggregate local accuracy-retention threshold is met. The bounded quality study is complete, so no replacement or extra GPU run is needed merely to refill the queue. Broad performance research remains stopped. This review does not change HPC materials or the published submission ZIP/slides.

Actual allocation cost is **47.32 H200 GPU-hours** for the sixteen full-study jobs, below the reserved maximum 72.533333 GPU-hours. The earlier pilot attempts consumed 4.213333 GPU-hours; total study allocation cost is **51.533333 H200 GPU-hours**. These are allocated GPU-hours, not active compute time, money, or PBS SU. PBS SU used: **0**.

## A short answer for the presentation

> We tested our optimised service against a stock deployment of the same official FP8 checkpoint on the same 16 H200 GPUs. On all 12,032 MMLU-Pro questions, the stock deployment answered 9,460 correctly and our service 9,452. That retains 99.9154% of the reference accuracy, passing our local 99% threshold. We replayed every saved answer and kept all errors, invalid outputs and losing shards. This is our measured regression check; the organisers' own quality evaluation remains a separate decision.

For preservation and exact recovery coverage, read [Materials and recovery](MATERIALS.md). Git commits preserve sources and manifests; the linked private evidence release separately preserves large response objects.
