# What this quality test can establish

The local test asks whether the serving implementation preserves answer accuracy relative to a stock deployment of the same official FP8 checkpoint. It does not ask whether 99% of all questions are answered correctly. Both deployments answer exactly the same questions with the same prompt, greedy generation, output allowance and scoring rules.

For example, if the reference answers 10,000 questions correctly, the candidate needs at least 9,900 correct on the same complete test set. With equal denominators, candidate accuracy / reference accuracy is simply candidate correct / reference correct. Compare total counts across all shards; do not average shard percentages or omit failed requests.

## What has actually happened

The initial 128-question pilot gave reference 104 and candidate 102 correct. The ratio 102/104=98.076923%, below99%. This is a measured local pilot failure, not evidence that the complete set necessarily fails. The pilot used concurrency 16 and a small category-balanced sample. It is preserved separately and is not mixed into the full-set denominator.

The fixed complete study uses all 12,032 MMLU-Pro test questions and concurrency 64 for both deployments. The eight paired shards each contain 1,504 unique question IDs, fixed before generation. A question belongs to exactly one shard per deployment. Both roles are measured on the same 16-H200 two-node system. The reference is native stock FP8 TP8/EP8, one colocated replica per node; the candidate is the accepted two TP4 prefill workers plus TP8/EP8 decode deployment with its existing runtime optimisations. Therefore this tests the combined serving configuration, not an isolated kernel or transport change.

The first pair only establishes whether a 1,504-question long-answer shard fits within the 17-minute allocation, completes without service errors and retains auditable raw responses. A losing accuracy result is not a reason to skip later shards. Invalid infrastructure or incomplete coverage stops dispatch; it is not a valid quality measurement. A local accuracy failure is still an important completed measurement.

## Why unchanged weights do not prove a pass

Different tensor and expert layouts, arithmetic kernels, reduction orders, batch shapes and runtime paths can change numerical results even when the stored weights are identical. Greedy decoding then follows a different continuation when logits are close. This is a possible mechanism, not an identified cause of our pilot differences. The pilot compared several implementation differences together, so it cannot attribute a change to one optimisation.

The 2,048-token generation cap is fixed for both deployments using the pinned source evaluator recipe. Some answers reach that cap; they stay in the denominator. The pinned parser can recover a final standalone choice letter, and invalid unparsed answers count as wrong rather than random guesses. These local protocol choices are disclosed; they are not silently claimed to match an unpublished organiser harness or the model-card score.

## How a final result will be read

A valid complete result requires exact 12,032-question coverage for each role, no duplicated questions, unchanged prompts and scoring, replayed raw HTTP bodies and zero service errors. The local ratio gate is candidate_correct/reference_correct>=0.99. This is a point comparison on the fixed benchmark, not a confidence guarantee about every workload. A local full-set pass supports the submission; official Q1 acceptance still belongs to the organiser, whose exact full-set harness and numerical reference are not public in the reviewed repository.

No AIPerf throughput score is used as accuracy evidence. The accepted 3,051.518173 good output tokens/s result 28197 measures service latency/throughput, not correct answers. Likewise, tokens/s recorded during these long-answer quality runs are diagnostic throughput, not the ranked 4,000-input/200-output performance score.
