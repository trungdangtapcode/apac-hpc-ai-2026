# Prefill C++ radix-cache study

**Current status: S106 is prepared and blocked on actual CPU job 27387. No full-model job is submitted.** The source review found an experimental SGLang `RadixCacheCpp` branch. Unlike a prebuilt library, it JIT-compiles a C++ extension at first import. A two-CPU, zero-GPU probe tests the cold build and small deterministic tree invariants before a 16-GPU allocation is considered.

## Evidence and candidate

The measured comparator is completed H200 job **27376**, using Python `RadixCache` on both TP4 prefill roles and `ChunkCache` on the TP8 decode role. Its locally reviewed score is **3041.119598 good output tokens/s**, from 1874/1900 good requests (98.631579%) with no errors or cancellations. It is one fresh control observation, not an established optimum.

The single S106 treatment enables `SGLANG_EXPERIMENTAL_CPP_RADIX_TREE=1` for both prefill roles while retaining radix cache (`disable_radix_cache=False`). It expects `RadixCacheCpp` on all eight prefill ranks and keeps decode entirely unchanged. Model/weights, topology, FP8, BF16 KV, CUDA graphs, MoE backends, decode cap/polling, workload and gates derive from the exact job 27376 submitted payload. The cold C++ build must fit the existing 600-second shared model-startup deadline.

## Fail-closed sequence

1. Wait for actual job 27387 to reach `COMPLETED 0:0` and preserve its final `probe.json`.
2. Review the CPU probe's `PASS_CPU_FIXTURES_ONLY` state, page-1 and metadata-only page-16 fixtures, cleanup, binary/toolchain record, and source hashes.
3. Root reviews and admits the prepared S106 payload. Its pre-model guard independently checks the actual CPU job accounting/result and exact C++ hashes.
4. S106 starts the model only after that guard. It requires source-pin checks before SGLang import/JIT, actual per-rank P C++ selection and classes, unchanged decode cache/flags, physical KV, semantic P/D tests, and pre-performance output smoke. Any failure prevents the N64 client from starting.
5. If all startup gates pass, run the existing N64 local AIPerf protocol in the same allocation and independently review raw output, tails, server/runtime evidence, and cleanup.

The full candidate payload is [s106-h200-prefill-cpp-cache](../serving-tuning-11/s106-h200-prefill-cpp-cache/README.md). Its 16-H200 reservation is 17 minutes maximum (4.533334 GPU-hours); no PBS SU. The CPU probe is a prerequisite only and claims no serving gain. The S106 package remains `PREPARED_BLOCKED_ON_ACTUAL_27387`, not ready to submit, until the prerequisite is complete and root has reviewed it. No official accuracy claim is made.

## Offline admission and payload validation

[`validate.py`](validate.py) exercises the staged pre-model admission guard and the exact S106 runtime-log validator using standard-library-only fixtures. It includes wrong job/state/accounting receipts, malformed or incomplete probe output, cleanup/deadline failures, source/hash/page-scope mutations, comparator drift, missing or duplicated P-rank C++ selection, incorrect per-rank cache classes, decode/cache flag regressions, and source-guard marker mutations. It also executes the actual embedded worker `PATCHCHECK` against temporary synthetic source trees: the P-role case passes, a changed pinned C++ file is rejected, and a leaked C++ flag on decode is rejected. No Torch, model, CUDA, network, or scheduler runtime is imported; synthetic fixtures do not count as job 27387 evidence.

A config comparison against the frozen 27376 payload found no unrelated serving-setting changes. The functional treatment is only enabling the C++ radix implementation on P. `MAX_JOBS=2` and the role-private `TORCH_EXTENSIONS_DIR` bound and isolate cold JIT compilation; decode explicitly unsets these variables. They are startup/build controls, not an additional serving optimization claim. The P/D service flags, weights, topology, precision, workload and gates remain controlled. [Fixture outcomes](VALIDATION.json) record all 33 offline cases. Offline mutation fixtures pass, but the candidate remains blocked until the actual prerequisite and root review.
