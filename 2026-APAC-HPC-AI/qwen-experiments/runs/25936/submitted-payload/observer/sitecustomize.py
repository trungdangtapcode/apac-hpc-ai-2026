"""Read-only ModelRunner observer for bounded D5 startup qualification.

Pinned-source basis: ModelRunner.initialize calls expert metadata init before
load_model; load_model returns after assigning self.model; KV dtype resolution
is exposed by configure_kv_cache_dtype. No source or model math is changed.
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path


def _write(record: dict) -> None:
    out = Path(os.environ["D5_OBSERVER_DIR"])
    out.mkdir(parents=True, exist_ok=True)
    record.update(pid=os.getpid(), timestamp_unix=time.time())
    with (out / f"observer-{os.getpid()}.jsonl").open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(record, sort_keys=True) + "\n")


def _rank_world(torch, fallback_rank: int, fallback_world: int) -> tuple[int, int]:
    dist = torch.distributed
    if dist.is_available() and dist.is_initialized():
        return dist.get_rank(), dist.get_world_size()
    return fallback_rank, fallback_world


def _hash_row(torch, tensor, slot: int) -> dict:
    # SHA only; never retain or write tensor payloads. uint8 view supports FP8
    # weights and FP32 runtime scale tensors without dtype conversion.
    row = tensor.detach().select(0, slot).contiguous()
    payload = row.view(torch.uint8).cpu().numpy().tobytes()
    return {
        "sha256": hashlib.sha256(payload).hexdigest(),
        "shape": list(row.shape),
        "dtype": str(row.dtype),
        "bytes_hashed": len(payload),
    }


def _capture_metadata(runner) -> None:
    import torch
    from sglang.srt.eplb.expert_location import get_global_expert_location_metadata
    from sglang.srt.layers.dp_attention import compute_dp_attention_world_info
    from sglang.srt.model_executor.model_runner import get_parallel

    args = runner.server_args
    parallel = get_parallel()
    rank, world_size = _rank_world(torch, parallel.tp_rank, parallel.tp_size)
    meta = get_global_expert_location_metadata()
    if meta is None:
        raise RuntimeError("D5 observer: expert location metadata is absent")

    p2l = meta.physical_to_logical_map_cpu.detach().to("cpu", dtype=torch.int64).contiguous()
    _, effective_attn_tp, dp_rank, effective_dp_size = compute_dp_attention_world_info(
        args.enable_dp_attention,
        parallel.tp_rank,
        parallel.tp_size,
        args.dp_size,
        args.attn_cp_size,
    )
    resolved_contract = (
        world_size == 5
        and parallel.tp_size == 5
        and effective_dp_size == 5
        and effective_attn_tp == 1
        and parallel.moe_ep_rank == rank
        and parallel.moe_ep_size == 5
        and parallel.moe_tp_size == 1
        and parallel.enable_dp_lm_head
        and args.moe_dp_size == 1
        and args.ep_num_redundant_experts == 2
        and args.ep_dispatch_algorithm == "dynamic"
        and args.moe_a2a_backend == "none"
        and args.moe_runner_backend == "hpc_ops"
        and args.disaggregation_mode == "null"
        and args.cuda_graph_backend_prefill == "disabled"
        and args.cuda_graph_max_bs_decode == 4
    )
    if not resolved_contract:
        raise RuntimeError("D5 observer: resolved parallel/MoE contract mismatch")
    if tuple(p2l.shape) != (94, 130) or meta.num_logical_experts != 128 or meta.num_local_physical_experts != 26:
        raise RuntimeError("D5 observer: actual expert metadata differs from 94x130 / 128 / 26")
    if not bool(torch.all(p2l[:, -2] == 0).item() and torch.all(p2l[:, -1] == 1).item()):
        raise RuntimeError("D5 observer: actual redundant expert map tail is not [0, 1]")
    model_dtype = str(runner.model_config.dtype).lower().replace("torch.", "")
    if model_dtype not in ("bfloat16", "bf16"):
        raise RuntimeError(f"D5 observer: target model dtype resolved to {model_dtype}")

    gpu_id = int(getattr(runner, "gpu_id", 0))
    props = torch.cuda.get_device_properties(gpu_id)
    record = {
        "event": "expert_metadata_after_init",
        "rank": rank,
        "world_size": world_size,
        "tp_rank": parallel.tp_rank,
        "dp_rank": dp_rank,
        "moe_ep_rank": parallel.moe_ep_rank,
        "tp_size": parallel.tp_size,
        "dp_size": effective_dp_size,
        "moe_ep_size": parallel.moe_ep_size,
        "moe_tp_size": parallel.moe_tp_size,
        "enable_dp_attention": args.enable_dp_attention,
        "enable_dp_lm_head": bool(parallel.enable_dp_lm_head),
        "attn_tp_size": effective_attn_tp,
        "physical_to_logical_shape": list(p2l.shape),
        "physical_to_logical_sha256": hashlib.sha256(p2l.numpy().tobytes()).hexdigest(),
        "physical_to_logical_tail": p2l[:, -2:].tolist(),
        "physical_to_logical_replicas_valid": True,
        "logical_experts": meta.num_logical_experts,
        "physical_experts": meta.num_physical_experts,
        "local_physical_experts": meta.num_local_physical_experts,
        "device_name": str(props.name),
        "compute_capability": [int(props.major), int(props.minor)],
        "device_uuid": str(getattr(props, "uuid", "")),
        "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
        "model_dtype": model_dtype,
        "moe_runner_backend": str(args.moe_runner_backend),
        "disaggregation_mode": str(args.disaggregation_mode),
        "disaggregation_transfer_backend": str(args.disaggregation_transfer_backend),
        "cuda_graph_backend_prefill": str(args.cuda_graph_backend_prefill),
        "cuda_graph_max_bs_decode": args.cuda_graph_max_bs_decode,
    }
    _write(record)


def _capture_loaded_weights(runner) -> None:
    import torch

    rank, world_size = _rank_world(
        torch,
        int(os.environ.get("RANK", "0")),
        int(os.environ.get("WORLD_SIZE", "1")),
    )
    if world_size != 5:
        raise RuntimeError(f"D5 observer expected world size 5, got {world_size}")

    model = runner.model
    candidates = []
    for module_name, module in model.named_modules():
        if all(hasattr(module, name) for name in ("w13_weight", "w2_weight")):
            layer_id = getattr(module, "layer_id", None)
            candidates.append((layer_id if layer_id is not None else 10**9, module_name, module))
    if not candidates:
        raise RuntimeError("D5 observer: no loaded FusedMoE expert tensors found")
    _, module_name, experts = min(candidates, key=lambda item: (item[0], item[1]))
    tensors = {}
    for name in ("w13_weight", "w2_weight", "w13_weight_scale_inv", "w2_weight_scale_inv"):
        tensor = getattr(experts, name, None)
        if tensor is None:
            raise RuntimeError(f"D5 observer: missing loaded expert parameter {name}")
        tensors[name] = tensor
    if int(tensors["w13_weight"].shape[0]) != 26 or int(tensors["w2_weight"].shape[0]) != 26:
        raise RuntimeError("D5 observer: expected 26 local loaded expert rows in both weights")

    expected_weight_shapes = {"w13_weight": [3072, 4096], "w2_weight": [1536, 4096]}
    for name, dims in expected_weight_shapes.items():
        if tensors[name].dtype != torch.float8_e4m3fn:
            raise RuntimeError(f"D5 observer: {name} is not runtime FP8 E4M3")
        if tensors[name].ndim != 3 or sorted(tensors[name].shape[-2:]) != sorted(dims):
            raise RuntimeError(f"D5 observer: {name} shape differs from target FP8 geometry")

    # Source proof: Fp8MoEMethod.create_fp8_moe_weight_ initializes serialized
    # block scales as FP32. BF16 checkpoint scale_inv tensors are copied into
    # those FP32 Parameters. With explicit hpc_ops, DeepGEMM requantization is
    # a no-op; _prepare_hpc_ops_weights creates consumed FP32 .float() copies.
    expected_scales = {
        "w13_weight_scale_inv": [24, 32],
        "w2_weight_scale_inv": [12, 32],
    }
    for name, dims in expected_scales.items():
        tensor = tensors[name]
        if tensor.dtype != torch.float32:
            raise RuntimeError(f"D5 observer: {name} runtime scale parameter is not FP32")
        if tensor.ndim != 3 or tensor.shape[0] != 26 or sorted(tensor.shape[-2:]) != sorted(dims):
            raise RuntimeError(f"D5 observer: {name} runtime scale shape differs from 128x128 blocks")

    consumed = {
        "hpc_ops_w13_weight_scale": getattr(experts, "hpc_ops_w13_weight_scale", None),
        "hpc_ops_w2_weight_scale": getattr(experts, "hpc_ops_w2_weight_scale", None),
    }
    for name, dims in (("hpc_ops_w13_weight_scale", [24, 32]), ("hpc_ops_w2_weight_scale", [12, 32])):
        tensor = consumed[name]
        if tensor is None or tensor.dtype != torch.float32:
            raise RuntimeError(f"D5 observer: consumed {name} is absent or not FP32")
        if tensor.ndim != 3 or tensor.shape[0] != 26 or sorted(tensor.shape[-2:]) != sorted(dims):
            raise RuntimeError(f"D5 observer: consumed {name} shape differs from 128x128 blocks")
    tensors.update(consumed)

    quant = experts.quant_method
    metadata = {
        name: {"shape": list(tensor.shape), "dtype": str(tensor.dtype)}
        for name, tensor in tensors.items()
    }
    common = {
        "module_name": module_name,
        "layer_id": getattr(experts, "layer_id", None),
        "rank": rank,
        "world_size": world_size,
        "local_experts": 26,
        "moe_runner_backend": str(runner.server_args.moe_runner_backend),
        "quant_method": type(quant).__name__,
        "block_quant": bool(getattr(quant, "block_quant", False)),
        "weight_block_size": list(getattr(quant, "weight_block_size", []) or []),
        "parameter_metadata": metadata,
    }
    _write({"event": "loaded_first_moe_expert_parameter_metadata", **common})

    if rank not in (0, 4):
        return
    slots = [0, 1] if rank == 0 else [24, 25]
    hashes = {
        name: {str(slot): _hash_row(torch, tensor, slot) for slot in slots}
        for name, tensor in tensors.items()
    }
    _write({
        "event": "loaded_first_moe_expert_weight_hashes",
        **common,
        "selected_local_slots": slots,
        "selected_slot_hashes": hashes,
        "hash_payload_bytes": sum(
            entry["bytes_hashed"] for by_slot in hashes.values() for entry in by_slot.values()
        ),
    })


def _capture_kv_config(runner) -> None:
    import torch

    rank, world_size = _rank_world(
        torch,
        int(os.environ.get("RANK", "0")),
        int(os.environ.get("WORLD_SIZE", "1")),
    )
    hf_config = getattr(runner.model_config, "hf_config", None)
    resolved_dtype = str(runner.kv_cache_dtype_str).lower().replace("torch.", "")
    kv_heads = getattr(hf_config, "num_key_value_heads", None)
    if world_size != 5 or resolved_dtype not in ("bfloat16", "bf16") or kv_heads != 4:
        raise RuntimeError("D5 observer: resolved KV runtime dtype/head count/world size mismatch")
    _write({
        "event": "resolved_kv_cache_config",
        "rank": rank,
        "world_size": world_size,
        "kv_cache_dtype_str": str(runner.kv_cache_dtype_str),
        "num_key_value_heads": kv_heads,
        "server_args_kv_cache_dtype": str(runner.server_args.kv_cache_dtype),
    })


def _install() -> None:
    from sglang.srt.model_executor.model_runner import ModelRunner

    if getattr(ModelRunner, "_d5_observer_installed", False):
        return
    original_metadata = ModelRunner.maybe_init_expert_location_metadata
    original_load = ModelRunner.load_model
    original_kv_config = ModelRunner.configure_kv_cache_dtype

    def metadata_wrapper(self, *args, **kwargs):
        result = original_metadata(self, *args, **kwargs)
        if os.environ.get("D5_OBSERVER_DIR") and not self.is_draft_worker:
            _capture_metadata(self)
        return result

    def load_wrapper(self, *args, **kwargs):
        result = original_load(self, *args, **kwargs)
        if os.environ.get("D5_OBSERVER_DIR") and not self.is_draft_worker:
            _capture_loaded_weights(self)
        return result

    def kv_config_wrapper(self, *args, **kwargs):
        result = original_kv_config(self, *args, **kwargs)
        if os.environ.get("D5_OBSERVER_DIR") and not self.is_draft_worker:
            _capture_kv_config(self)
        return result

    ModelRunner.maybe_init_expert_location_metadata = metadata_wrapper
    ModelRunner.load_model = load_wrapper
    ModelRunner.configure_kv_cache_dtype = kv_config_wrapper
    ModelRunner._d5_observer_installed = True


if os.environ.get("D5_OBSERVER_DIR"):
    _install()
