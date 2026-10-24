# Native FP8 KV attention passes on H200

Job **25796** completed **0:0 in 38 seconds** on one actual H200/SM90. The native script took 5.517 seconds including imports and setup; allocation wall time includes launcher/container overhead. All four TP4/TP8 local-head × scale1.0/0.5 cases return finite BF16 outputs with the specified shapes and NHD layout. Runtime FlashInfer **0.6.15.post1** decode/prefill/core source hashes match the extracted pinned-source contract.

The independent FP32 oracle reads the **same rounded FP8 values**. Maximum relative-L2 disagreement is **0.003159019**, or **0.315902%**, under the predeclared 2% gate. The three-query verification mask allows 3,998/3,999/4,000 keys. This supports native API/kernel compatibility for these synthetic cases.

Relative-L2 against the **original BF16 KV** is **3.741432%–3.913238%**. That is local tensor error including quantization, not a language-model accuracy loss and not an MMLU score. Halving the synthetic scales does not remove FP8 rounding error; no best real-model scale is inferred. Official ≥99% reference accuracy remains unverified.

First-call wall times and single warm-call CUDA-event times are retained with units in raw result.json. There is no BF16 kernel timing control, repeated statistical sample, batching, serving queue, P/D transfer, or ranked workload. Do not convert this pass into a speedup claim. Hardware evidence is GPU identity/UUID/SM capability; utilization, periodic VRAM, CPU/RSS and heavy profiling were not collected.

Next: preserve this pass and close unchanged primitive repeats. Review scale provenance and qualify the DP-attention/EP rank path before spending on a full model-level FP8 experiment. Existing BF16 serving remains the score incumbent.

For a presentation: “FP8 KV is no longer just a source-code possibility: the actual attention kernels pass a small independent numerical check on our H200. Model quality and end-to-end performance are separate questions that remain open.”
