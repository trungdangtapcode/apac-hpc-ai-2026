> Updated 24 October 13:00 UTC: root completed and reviewed the controller, bound the actual R3 artifacts and candidate review, and sealed the startup-only payload. The earlier incomplete/unbound preparation descriptions below are historical. See ROOT_REVIEW.json and PREPARATION_STATUS.md. A submitted receipt is still required before claiming this was queued; a completed independent review is required before claiming GPU readiness.

# D5 H200 decode-only readiness candidate

## Purpose and evidence boundary

This is a source-qualified, decode-only startup candidate for the ordinary Qwen3-235B-A22B-Instruct-2507 FP8 target model. It is separate from the EAGLE experiments. The candidate is not submitted and has no D5 runtime evidence. The only accepted prerequisite is the root-reported R3 native physical-replica primitive result; the actual receipt, result, and root review bytes still need to be bound in `ROOT_REFERENCE_BINDING.json` before the launch guard can pass.

The R3 primitive passed with EP5/oracle relative L2 0.0062373071, EP1/oracle 0.0059553883, EP5/EP1 relative L2 0.0023261150, and physical-map error 0.0, against limits 0.02 and 1e-7. That result covers its synthetic native primitive only. It does not establish SGLang dispatch or model loading.

## Proposed bounded configuration

One H200 node, five scheduler-assigned GPUs, at most 17 minutes. The pinned SGLang image is `/scratch/enroot-images/sglang-harbor.sqsh` (SHA-256 and byte count in `SOURCE_PROVENANCE.json`); the model is `/scratch/models/Qwen3-235B-A22B-Instruct-2507-FP8` (actual `config.json` SHA-256 `f056921e486d3e22aed125b5218b87146ea2ac838ccf1521dea5b08f809e8d59`). The controller must use Pyxis with `srun --gres=gpu:5`, mount the candidate and result directory, and provide a private per-job HOME. The worker preserves the scheduler-provided `CUDA_VISIBLE_DEVICES` and requires five visible H200 devices.

The launch contract is explicit BF16 model dtype, BF16 KV cache, TP5, DP5 with DP attention, EP5, MoE-DP1 (therefore MoE-TP1), two redundant physical expert slots, dynamic dispatch, no A2A backend, and the HPC-Ops MoE runner. HPC-Ops's pinned CLI help requires page size 64, so the candidate sets `--page-size 64`. The 128 logical experts plus two replicas produce 130 physical slots, or 26 slots per EP rank. NIXL decode mode is configured for startup readiness only. The decode graph maximum batch is 4; there is no prefill worker, no generation request, no PD correctness claim, and no performance claim.

Do not set an MNNVL fusion value. The selected DP-attention geometry resolves effective attention TP1, which excludes that FlashInfer fusion path; leave the pinned source's native default and record the resolved runtime backend. Do not replace another default based on assumptions.

## Source proof for the observer

The pinned `ModelRunner.initialize()` calls `maybe_init_expert_location_metadata()` before `load_model()`. `load_model()` assigns the loaded model before returning. The candidate's `observer/sitecustomize.py` wraps these methods after importing the pinned class and also observes `configure_kv_cache_dtype()`; it does not edit source files or model operations.

`ExpertLocationMetadata.physical_to_logical_map_cpu` supplies the CPU map. The trivial source map appends redundant IDs 128 and 129 as logical replicas of 0 and 1. `FusedMoE` has `w13_weight`, `w2_weight`, `w13_weight_scale_inv`, and `w2_weight_scale_inv`; its physical loader translates physical IDs to local slots before copying loaded checkpoint tensors. The observer captures map hash and tail on all five ranks, then hashes selected rows on global rank0 slots 0/1 and global rank4 slots 24/25. It hashes the two runtime FP8 weights, the two runtime scale parameters, and the prepared HPC-Ops scale tensors. It writes no tensor bytes. Equality of loaded tensor-row hashes is required to claim the duplicate checkpoint weights/scales were loaded consistently. The observer's summaries are not a substitute for serving outputs or numerical correctness.

The safetensors checkpoint stores BF16 inverse-scale values, but those are not the runtime parameter dtype. In pinned `layers/quantization/fp8.py`, `Fp8MoEMethod.create_fp8_moe_weight_()` allocates block scale parameters as FP32 when `weight_block_size` is set. Loading the checkpoint values copies them into those FP32 parameters. With explicit `moe_runner_backend=hpc_ops`, DeepGEMM is not selected; `requant_block_scale_ue8m0_for_deepgemm()` returns without modifying scales when `use_deepgemm_runner` is false. The HPC-Ops path then creates its consumed scale tensors using `.data.float()`. The observer therefore requires FP32 both for loaded scale parameters and consumed HPC-Ops scales. The quant source and its hash are in `SOURCE_PROVENANCE.json`.

The actual target config and header-only FP8 inventory are retained in `ACTUAL_MODEL_CONFIG.json` and `SOURCE_PROVENANCE.json`. `asset_preflight.py` rechecks the exact config hash and reads only the first safetensors shard header; it does not read checkpoint tensor payloads.

The DP-attention helper in pinned `layers/dp_attention.py` computes `attn_tp_size = tp_size // dp_size // attn_cp_size`; with the candidate's actual arguments TP5/DP5/CP1, this is 1. The pinned Qwen3-MoE attention implementation checks query/KV head partitioning against this effective attention TP; the retained target config has 4 KV heads, which is divisible by 1. This resolves the geometry guard at source/config level only. `parallel_state.py` computes MoE-TP as TP/EP/MoE-DP, giving 5/5/1=1. The CPU fixture reproduces only the trivial map arithmetic; a future run must capture the actual SGLang metadata on each rank.

Pinned `server_args.py` declares native CLI fields for BF16 dtype, KV cache dtype, TP/DP/EP, MoE-DP, redundant expert count, dynamic dispatch, A2A backend, MoE runner, decode disaggregation, NIXL transfer and decode graph maximum batch. Its pinned help lists HPC-Ops for FP8 MoE on Hopper/SM90 and requires page size 64; `hpc_ops.py` requires FP8 weights, BF16 activations and 128×128 block scales. The actual config/header show E4M3 weights, BF16 inverse scales and 128×128 blocks. The candidate therefore sets page size 64 and leaves model/attention backend selection native except for the explicitly selected HPC-Ops MoE runner. A full architecture and kernel compatibility check still occurs only at runtime.

The pinned `max_running_requests` argument is optional. The inspected `server_args.py` and runtime-argument override source contain no DP-size divisibility validation for it; its retained `server_args.py` uses are memory-reservation sizing. This candidate omits the explicit max-running setting because it sends no requests. It keeps decode graph maximum batch 4 for startup initialization. This source review does not claim a serving concurrency limit.

The pinned image's Torch 2.11 stub declares `_CudaDeviceProperties.uuid`; `device_preflight.py` uses the scheduler-preserved CUDA mask with `torch.cuda.device_count()` and each assigned device's name, SM capability, UUID, and memory size. It requires exactly five visible H200/SM90 devices with unique UUIDs. The observer then checks its rank-local CUDA UUID set matches this inventory. Neither the worker nor readiness checker depends on `nvidia-smi` output or `rg` inside the container.

## Required future acceptance evidence

The actual R3 receipt, collected result, and terminal review paths and SHA-256 values are bound in `ROOT_REFERENCE_BINDING.json`; the terminal review status is PASS. This is a primitive prerequisite only. `prepare_check.py` still fails closed until root reviews the D5 candidate/controller and fills `ROOT_CANDIDATE_REVIEW_BINDING.json`. That candidate review gate is separate from the R3 result review and must pass before any model allocation.

For an authorized run, accept readiness only after `headcheck.py` passes. It requires rank records for all five processes, matching TP5/DP5, DP attention effective attention TP1, EP5/MoE-TP1, a 94-layer 130-to-128 map, 26 loaded slots, the expected FP8 weights, FP32 runtime scale parameters and FP32 HPC-Ops consumed scales. All ranks must have the same full map hash and a `[0,1]` map tail for every layer. Rank0 loaded tensor hashes at local slots 0/1 must equal rank4 slots 24/25 for both weights and both parameter scales and both consumed scales. Each rank must resolve BF16 model/KV dtypes and four KV heads. The independent gate also requires the exact model header preflight, a five-device H200/SM90 Python-CUDA inventory with five unique UUIDs, and successful native `/health`. It writes `readiness-gate.json` only after every check passes. Health alone is never a readiness pass.

This qualification sends no `/generate` or user-output request. Native health confirms only that the service reached its health state. It does not claim model quality, numerical correctness, PD connectivity, throughput, latency, or capacity.

## CPU-only checks

`python3 cpu_fixture.py` checks the worker argument contract, pure 130-slot map arithmetic, duplicate local slot locations, R3 bound artifact hashes, rejection of an unreviewed D5 candidate, and refusal to accept a health-only directory. It imports no SGLang modules and uses no CUDA, model payload, endpoint, or scheduler. These checks validate candidate structure only.

Current state and source evidence: `PREPARATION_STATUS.md` and `SOURCE_PROVENANCE.json`. The mutable candidate tree is not frozen provenance; regenerate `SHA256SUMS` after root review binds actual prerequisite artifacts. Do not submit directly from this source tree until root has reviewed the completed controller and payload.
