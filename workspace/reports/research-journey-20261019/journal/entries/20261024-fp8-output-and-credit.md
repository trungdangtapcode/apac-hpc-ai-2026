# Real FP8 kernels, real EAGLE outputs, and a revised H100 allowance

24 October 2026. The research question has progressed from “can this deployment start?” to “what evidence supports its numerical behavior?” The reproduced score remains 3044.400475 good output tokens/s on H200; none of today's diagnostics changes that score.

The FP8 KV primitive 25796 runs native FlashInfer on one actual H200, with no model weights. All four synthetic local-head/scale cases pass against FP32 attention reading the same rounded FP8 cache. Maximum relative-L2 error is 0.315902%. Comparing against the original BF16 cache gives 3.741432–3.913238% local tensor error; it is not a benchmark accuracy loss. This opens kernel compatibility, while model scale provenance, quality and serving performance remain separate questions.

The full EAGLE diagnostic 25797 reaches all 16 initialized model ranks, 32 geometry records and both semantic P/D paths. It collects 1600 actual token IDs. Arithmetic matches target; code/Unicode differ from target while repeating internally; long4000 also varies between repetitions. The original exact-token gate fails and remains failed. The official FAQ scores benchmark accuracy rather than token-by-token identity, so this local failure is not an official quality verdict. A matched deterministic target/reference and speculative pair is the next diagnostic hypothesis. The native flag changes collectives and may change attention; a different target reference is necessary. It is not a promised speedup.

H100 preflight 224275 fails on our CUDA API typo before model loading. The corrected 224276 passes its independent real four-rank metadata check; ten tensors have 96 rows each, including BF16 hidden states [96, 4096]. Cost estimates 9.386667 / 51.057778 SU remain separate from actual posted charges. R4 admission correctly stops before reserving a full job after the failed parent. Derived R5 **224277** is admitted afterok 224276, then moves to Q once the actual prerequisite succeeds. It will test 16-rank metadata, native sends, both P/D paths and 1600 IDs on H100; it has no score.

The owner explicitly frees the former 13000 SU buffer and asks to use remaining H100 credit before 30 October. The new AI cap is the actual 64000 SU grant with zero discretionary reserve, without changing CPU budgets, job caps or disabled automation. The account report has a later 15 November date; use the owner's earlier date for planning and preserve that provenance. Current grant minus retained used and pending maxima leaves 16201.322 SU at the recorded checkpoint.

The DP-attention/EP source lead is preserved separately: TP5/DP5 gives attention TP1, and 128 logical experts plus 2 physical replicas yields 130 slots divisible by EP5. This is only arithmetic/source feasibility. Exact expert mapping, rank communication, backend choices and NIXL routing remain runtime questions. A bounded synthetic HPC-Ops replica check is being prepared before a larger topology attempt.

For a presentation: “We now distinguish kernel compatibility, end-to-end integration, output stability, official benchmark accuracy and measured speed. A pass at one level does not prove the next. The retained failures tell us which controlled experiment to run next.”

Evidence: [FP8 kernel review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-review-25796-20261024/README.md), [EAGLE divergence review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-review-25797-20261024/README.md), [H100 prefill review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-review-224276-20261024/README.md), [credit decision](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h100-budget-owner-update-20261024/README.md), [new DP/EP source review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/dp-attention-ep-feasibility-20261024/README.md).

## Later admissions and accounting

Root submitted **25807**, the target-only deterministic reference. Its protocol now requires new-run target repeat stability and retains the historical 25585 token comparison as informational. This is a prospective new deployment control, not a retrospective pass for 25797. S45 cannot run until the actual S44 result and review are accepted and bound.

Root also submitted **224278.pbs111**, one H100 for at most ten minutes / maximum21.333333SU, afterany224277. It tests physical replica IDs and local expert partition math, without claiming a distributed collective. A new charge stopped the first admission before reservation or qsub; root reconciled the uniquely matching224275 charge of9.387SU, verified the existing remote payload hashes and safely resumed admission with no duplicate qsub.

At03:36UTC, used46528.065SU plus all retained maxima leaves16298.601667SU under the owner-approved grant. The published128SU prepayment is already excluded from balance; the conservative maximum for224276 remains until its actual51.057778SU estimate is uniquely posted.
