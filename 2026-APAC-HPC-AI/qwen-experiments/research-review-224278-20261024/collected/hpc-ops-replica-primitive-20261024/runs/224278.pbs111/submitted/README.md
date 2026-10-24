# Synthetic HPC-Ops redundant-expert primitive (2026-10-24)

## Purpose and boundary

This one-H100 diagnostic asks whether the pinned HPC-Ops `fuse_moe_blockwise` API can execute the exact global-physical-ID shape used by SGLang's FP8 MoE runner: 128 logical experts, 130 physical experts, five contiguous virtual EP partitions of 26 experts each, and physical slots 128/129 holding exact copies of logical experts 0/1. Deterministic top-k rows route through logical experts 0, 1, 127 and 64, with the two duplicate physical IDs used on alternating rows.

It calls the native installed HPC-Ops Python API on five local weight slices, one after another on the same GPU, passing each `rank_ep` and the global count 130. The outputs are added with a local PyTorch sum and compared with (a) an EP=1 native call on the 128 logical weights/IDs and (b) an independent FP32 Torch calculation using the same quantized FP8 weights and dequantized activation groups. Every relative-L2 value must be at most 2%; the physical-copy oracle must match the logical oracle within 1e-7.

The local source-shaped fixture has been run and passed. GPU execution is **prepared but not run**. This is not a multi-GPU collective or communication test. It cannot prove distributed EP, DP attention, NIXL, MNNVL, production routing/EPLB balance, checkpoint loader behavior, Qwen accuracy, or model-scale memory fit. Do not describe the local sum as an all-reduce.

## Exact pinned API and why this payload is viable

The retained SGLang wrapper calls `hpc.fuse_moe_blockwise(x_q, x_scale, w13_weight, w13_scale, w2_weight, w2_scale, topk_ids, topk_weights, moe_ep_rank, global_num_experts)` at `pinned-source/sgl-workspace/sglang/python/sglang/srt/layers/moe/moe_runner/hpc_ops.py:167-184`. The extracted HPC-Ops wheel wrapper has the same positional API at `hpc-package/usr/local/lib/python3.12/dist-packages/hpc/fuse_moe.py` (`fuse_moe_blockwise`), which forwards `rank_ep` and `num_expert_total` to the installed native op. The package metadata pins `hpc-ops 0.0.1.dev0+gab1a402`; the deployed image digest/NSCC asset path are in `SOURCE_PROVENANCE.json`.

The pinned SGLang CUDA test `pinned-source/sgl-workspace/sglang/test/registered/moe/test_hpc_ops_moe.py` demonstrates the same 128×128 block-FP8 weights, activation quantizer, scale padding, and native wrapper on SM90 with EP1. This diagnostic extends only the native argument geometry: for each virtual rank it supplies 26 local expert rows, the global physical top-k IDs, `rank_ep` 0 through 4 and total count 130. The CPU fixture verifies contiguous physical partitioning and the pinned trivial-map rule `append_trivial_expert_slots(...): new_slots % num_logical_experts` for the final IDs. No source evidence here proves that a live SGLang Qwen request takes this path correctly; that remains a separate full stack question.

## Payload geometry and fixed gates

- Hardware: exactly one assigned H100 (SM90), confirmed in process by CUDA device count, device name and compute capability.
- Weights: synthetic FP32 source tensors, seed 2026, block-quantized to E4M3 with 128×128 scale blocks, then exact FP8/scale copies for physical experts 128/129.
- Activations: 16 BF16 rows, hidden size 256; SGLang's pinned per-token group-128 FP8 activation quantizer is checked byte-for-byte against an independent PyTorch group quantizer. Pre-quantization and quantized extrema, scale range, dtypes and shapes are recorded.
- MoE geometry: intermediate size 128, top-k 4, no shared experts, gated SiLU, global physical count 130, virtual EP size 5. Every rank call is checked for output shape, finiteness and recorded rank participation.
- References: native EP1 on 128 logical experts and an FP32 Torch oracle over quantized weights/activations. Relative L2 is computed against the oracle for EP1, virtual EP5 and EP5-vs-EP1; every value must be ≤ 0.02. The physical-to-logical duplicate-copy oracle must be ≤ 1e-7.
- Runtime bounds: PBS walltime 10 minutes; external 480-second timeout around the container; Python 440-second internal deadline. No model is loaded and no service starts.

A blocker is a source-hash/package mismatch, missing HPC-Ops callable, anything other than one H100 SM90 visible device, a local partition shape failure, native kernel exception, non-finite output, activation quantizer mismatch, any threshold failure, or a runtime over bound. Failure JSON and stderr are retained. Do not alter IDs, scales, dimensions, reference math, tolerance or rank count after seeing a failure; prepare a separate corrected diagnostic with the observed issue first.

## Submission-state boundary

`benchmark.pbs` is the bounded job payload only. It contains no qsub/controller logic and was not submitted. It uses an ordinary non-login bash shell, initializes the module system only if PBS did not, explicitly loads `singularity/4.1.5`, requests one GPU for at most ten minutes, and passes PBS's single assigned `CUDA_VISIBLE_DEVICES` value through without inventing or widening the host mask. The job checks the established NSCC image path and byte count; it does not rehash the 26 GB image inside the allocation. The expected image SHA-256 is retained from `nscc-pbs/asset-contract.json`, and runtime SGLang source hashes plus the HPC-Ops package version are checked before the kernel calls. The compiled `_C.abi3.so` binary is trusted through the image/package provenance rather than copied or hashed by this payload. The job captures before/after `nvidia-smi` samples, stdout, stderr and JSON under `runs/$PBS_JOBID/`.

No queue, scheduler, budget ledger, reservation, model, persistent note, submission payload, Git archive or remote system was accessed or changed. The next action belongs to the root owner: review the exact staged paths, frozen job payload and current resource/admission state before any upload or submission.
