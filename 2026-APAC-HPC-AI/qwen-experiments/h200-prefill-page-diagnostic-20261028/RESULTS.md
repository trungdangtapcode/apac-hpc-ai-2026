# Constructed FlashInfer prefill diagnostic — job 27141

Reviewed 29 October 2026, Vietnam time (UTC+7). Job 27141 completed successfully; stdout records native-container command status 0, and the result JSON reports `DIAGNOSTIC_COMPLETE_NO_PASS_CLAIM`. The scheduler wall time reported for this one-H200 allocation was 1 minute 36 seconds. Raw artifacts and their seal manifest are retained under [`raw/27141`](raw/27141); the machine-readable review is [`review-27141.json`](review-27141.json).

## Question and method

This follow-up to the constructed KV page primitive asked whether native FlashInfer causal prefill executes at the constructed Qwen attention geometry for ragged KV and paged KV with page sizes 1 and 16. It used one H200, seed 2026, BF16 query/key/value tensors, native BF16 NHD `MHATokenToKVPool` writes, one constructed layer, head dimension 128 and a single KV head. TP4 geometry used 16 query heads; TP8 used 8. All 42 planned cases were attempted: 14 ragged cases and 28 paged cases across lengths 15, 16, 17, 31, 32, 33 and 4000.

For length 4000, native attention used all 4000 KV tokens but queried and compared only the final eight query positions, 3992–3999, against the matching causal suffix reference. The FP32 reference had TF32 disabled. The two original diagnostic limits remained flags only: relative L2 at most 0.01 and maximum absolute error at most 0.005. Completion did not imply a correctness pass.

The selected runtime backend was **FA3 for all 42 cases**. All cases produced finite BF16 output with the expected shape. Both native page pools were written and checked exactly before the paged cases; ragged cases use the same raw K/V tensors. There were zero execution-error cases. The result records the installed pool, FlashInfer prefill and SGLang backend source hashes, model config hash, GPU model/UUID, shapes, cache strides and page descriptors. Source hashes are in [`review-27141.json`](review-27141.json).

## Findings

All 42 relative-L2 values passed the original 0.01 flag. Values ranged from 0.00169224 to 0.00226000. The maximum-absolute 0.005 flag failed in 36 cases: all six short lengths for each TP hypothesis in the ragged path (12 cases) and for both page sizes in the paged path (24 cases). TP4's largest short-case absolute error was 0.00775242; TP8's was 0.00853753. Every length-4000 sampled-tail case passed both original flags; its maximum absolute error ranged from 0.00039546 to 0.00042147.

All 14 matched page-16/page-1 pairs had relative L2 difference exactly zero, covering both TP geometries and all seven lengths. This is evidence that page size did not change these constructed FA3 paged-prefill outputs. It does not explain the short-sequence absolute-reference discrepancy: the same strict absolute failures occur at both page sizes and in ragged prefill.

## Limits and next decision

This is constructed single-layer attention evidence only. It does not exercise model weights, the real full-model D-role head/layer registration, P/D transfer, end-to-end serving, acceptance gates, or performance. The 4000-token reference covers only the final eight query rows, not all output rows. No hardware time series, kernel profile, cost trace, or causal attribution of the short-sequence absolute errors was collected. The FP32-oracle threshold failure remains unresolved; do not call this a correctness pass or use it to widen any production page-size exception. Preserve the page-size equality as useful narrow evidence, and keep actual role registration, transfer, and prefill compatibility as separate prerequisites for any larger page-size serving trial.

Stdout confirms container creation, successful command return and cleanup. Stderr contains container extraction chatter and a third-party `torchao` Python `SyntaxWarning`; the diagnostic itself completed with exit status 0. The per-case source-bound measurements and frozen raw artifacts are authoritative; this summary is not a model-serving result.

The one-GPU scheduler elapsed 96 seconds corresponds to 0.026667 allocated GPU-hour under the 0.1 GPU-hour reservation; this arithmetic is not a site SU charge. The internal FlashInfer kernel label FA3 here is distinct from the outer SGLang attention-backend label FlashInfer in job 27077. Do not treat those two labels as separate evidence of entirely different GPU kernels.
