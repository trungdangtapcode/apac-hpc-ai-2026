#!/usr/bin/env python3
"""One-GPU FlashInfer FP8 KV compatibility primitive; no model or SGLang server."""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import math
import os
import platform
import subprocess
import sys
import time
import traceback
from pathlib import Path


SEED = 2026
CONTEXT = 4000
VERIFY_TOKENS = 3
HEAD_DIM = 128
REL_L2_TOLERANCE = 0.02
GEOMETRIES = (
    {"tp": 4, "q_heads": 16, "kv_heads": 1},
    {"tp": 8, "q_heads": 8, "kv_heads": 1},
    {"tp": 1, "q_heads": 64, "kv_heads": 4},
)
SCALE_CASES = (
    {"name": "unit", "k_scale": 1.0, "v_scale": 1.0},
    {"name": "half", "k_scale": 0.5, "v_scale": 0.5},
)


def lower_right_mask(qo_len: int, kv_len: int) -> list[list[bool]]:
    """Allowed-key mask: the query block is aligned to the end of the KV span."""
    if qo_len < 1 or kv_len < qo_len:
        raise ValueError("require 1 <= qo_len <= kv_len")
    first_query_position = kv_len - qo_len
    return [
        [key_pos <= first_query_position + query_pos for key_pos in range(kv_len)]
        for query_pos in range(qo_len)
    ]


def validate_geometry(q_heads: int, kv_heads: int, head_dim: int) -> None:
    if q_heads <= 0 or kv_heads <= 0 or q_heads % kv_heads:
        raise ValueError("FlashInfer GQA requires positive q_heads divisible by kv_heads")
    if head_dim != HEAD_DIM:
        raise ValueError(f"this primitive pins head_dim={HEAD_DIM}")


def scalar_attention_reference(q, k_stored, v_stored, k_scale, v_scale):
    """Tiny standard-library oracle used by CPU validation, with GQA and lower-right mask."""
    qo_len = len(q)
    q_heads = len(q[0])
    kv_len = len(k_stored)
    kv_heads = len(k_stored[0])
    dim = len(q[0][0])
    # This scalar helper intentionally permits tiny dimensions for CPU tests.
    # The native experiment separately enforces HEAD_DIM through
    # validate_geometry() before constructing its GPU tensors.
    if q_heads <= 0 or kv_heads <= 0 or q_heads % kv_heads:
        raise ValueError("scalar oracle requires positive q_heads divisible by kv_heads")
    if dim <= 0 or any(len(head) != dim for row in q for head in row):
        raise ValueError("scalar oracle requires a consistent non-empty query head dimension")
    if any(len(head) != dim for row in k_stored for head in row):
        raise ValueError("scalar oracle requires key head dimensions to match queries")
    if any(len(head) != dim for row in v_stored for head in row):
        raise ValueError("scalar oracle requires value head dimensions to match queries")
    mask = lower_right_mask(qo_len, kv_len)
    group_size = q_heads // kv_heads
    output = []
    for qi in range(qo_len):
        query_outputs = []
        for qh in range(q_heads):
            kh = qh // group_size
            logits = []
            for ki in range(kv_len):
                if not mask[qi][ki]:
                    logits.append(float("-inf"))
                    continue
                dot = sum(float(q[qi][qh][d]) * float(k_stored[ki][kh][d]) * k_scale for d in range(dim))
                logits.append(dot / math.sqrt(dim))
            top = max(logits)
            weights = [0.0 if value == float("-inf") else math.exp(value - top) for value in logits]
            total = sum(weights)
            query_outputs.append([
                sum(weights[ki] * float(v_stored[ki][kh][d]) * v_scale for ki in range(kv_len)) / total
                for d in range(dim)
            ])
        output.append(query_outputs)
    return output


def runtime_gpu_metadata(torch):
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is unavailable; native primitive cannot pass")
    if torch.cuda.device_count() != 1:
        raise RuntimeError(f"expected exactly one visible GPU, found {torch.cuda.device_count()}")
    device = torch.cuda.current_device()
    props = torch.cuda.get_device_properties(device)
    name = str(props.name)
    capability = tuple(torch.cuda.get_device_capability(device))
    # CUDA properties identify the assigned logical device. nvidia-smi may
    # enumerate all physical GPUs even when CUDA_VISIBLE_DEVICES selects one.
    uuid = str(getattr(props, "uuid", "") or "")
    try:
        query = subprocess.run(
            ["nvidia-smi", *(["--id=" + uuid] if uuid else []),
             "--query-gpu=uuid,name", "--format=csv,noheader"],
            check=True,
            capture_output=True,
            text=True,
            timeout=10,
        )
        rows = [line.strip() for line in query.stdout.splitlines() if line.strip()]
        if len(rows) == 1:
            uuid = rows[0].split(",", 1)[0].strip()
    except (OSError, subprocess.SubprocessError):
        pass
    if "H200" not in name.upper() or capability != (9, 0) or not uuid:
        raise RuntimeError(
            f"required one H200 (SM90) with a recorded UUID; got name={name!r}, "
            f"capability={capability}, uuid_present={bool(uuid)}"
        )
    return {
        "gpu_name": name,
        "gpu_uuid": uuid,
        "compute_capability": list(capability),
        "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES", "<unset>"),
        "device_index": device,
    }


def tensor_reference(torch, q, k_stored, v_stored, q_len, k_scale, v_scale):
    """FP32 PyTorch attention on the same rounded FP8 cache values as the kernel."""
    q32 = q.to(torch.float32)
    if q.ndim == 2:
        q32 = q32.unsqueeze(0)
    k32 = k_stored.to(torch.float32) * float(k_scale)
    v32 = v_stored.to(torch.float32) * float(v_scale)
    q_heads = q32.shape[1]
    kv_heads = k32.shape[1]
    group_size = q_heads // kv_heads
    if q_heads % kv_heads:
        raise ValueError("q_heads must be divisible by kv_heads")
    head_map = torch.arange(q_heads, device=q.device) // group_size
    keys = k32.index_select(1, head_map).permute(1, 0, 2)
    values = v32.index_select(1, head_map).permute(1, 0, 2)
    logits = torch.einsum("thd,hkd->thk", q32, keys) / math.sqrt(q32.shape[-1])
    allowed = torch.tensor(lower_right_mask(q_len, k32.shape[0]), device=q.device, dtype=torch.bool)
    logits = logits.masked_fill(~allowed[:, None, :], float("-inf"))
    probs = torch.softmax(logits, dim=-1)
    return torch.einsum("thk,hkd->thd", probs, values)


def relative_l2(torch, actual, reference) -> float:
    actual32 = actual.to(torch.float32)
    reference32 = reference.to(torch.float32)
    numerator = torch.linalg.vector_norm(actual32 - reference32)
    denominator = torch.linalg.vector_norm(reference32).clamp_min(torch.finfo(torch.float32).tiny)
    return float((numerator / denominator).item())


def _flashinfer_version(flashinfer):
    return str(getattr(flashinfer, "__version__", "unknown"))


def run_case(torch, flashinfer, geom, scale_case, base_q, base_k, base_v):
    q_heads = geom["q_heads"]
    kv_heads = geom["kv_heads"]
    k_scale = float(scale_case["k_scale"])
    v_scale = float(scale_case["v_scale"])
    q = base_q.to(torch.bfloat16)
    k_stored = (base_k.to(torch.float32) / k_scale).to(torch.float8_e4m3fn)
    v_stored = (base_v.to(torch.float32) / v_scale).to(torch.float8_e4m3fn)
    if not torch.isfinite(k_stored.to(torch.float32)).all() or not torch.isfinite(v_stored.to(torch.float32)).all():
        raise RuntimeError("FP8 cache quantization produced non-finite stored values")
    mask = torch.tensor(lower_right_mask(VERIFY_TOKENS, CONTEXT), device=q.device, dtype=torch.bool)
    sm_scale = 1.0 / math.sqrt(HEAD_DIM)

    # Warm the same CUDA FP32 oracle before timing; it is independent of FlashInfer.
    rounded_reference = tensor_reference(torch, q[-VERIFY_TOKENS:], k_stored, v_stored,
                                         VERIFY_TOKENS, k_scale, v_scale)
    bf16_reference = tensor_reference(torch, q[-VERIFY_TOKENS:], base_k, base_v,
                                      VERIFY_TOKENS, 1.0, 1.0)
    torch.cuda.synchronize()

    decode_q = q[-1].contiguous()
    decode_ref = tensor_reference(torch, decode_q, k_stored, v_stored, 1, k_scale, v_scale)[0]
    decode_bf16_ref = tensor_reference(torch, decode_q, base_k, base_v, 1, 1.0, 1.0)[0]
    torch.cuda.synchronize()

    decode_start = time.perf_counter()
    decode_out = flashinfer.single_decode_with_kv_cache(
        decode_q,
        k_stored.contiguous(),
        v_stored.contiguous(),
        kv_layout="NHD",
        use_tensor_cores=True,
        k_scale=k_scale,
        v_scale=v_scale,
        sm_scale=sm_scale,
    )
    torch.cuda.synchronize()
    decode_first_wall_s = time.perf_counter() - decode_start
    decode_event_start = torch.cuda.Event(enable_timing=True)
    decode_event_end = torch.cuda.Event(enable_timing=True)
    decode_event_start.record()
    decode_out = flashinfer.single_decode_with_kv_cache(
        decode_q,
        k_stored.contiguous(),
        v_stored.contiguous(),
        kv_layout="NHD",
        use_tensor_cores=True,
        k_scale=k_scale,
        v_scale=v_scale,
        sm_scale=sm_scale,
    )
    decode_event_end.record()
    decode_event_end.synchronize()
    decode_warm_cuda_ms = float(decode_event_start.elapsed_time(decode_event_end))

    prefill_q = q[-VERIFY_TOKENS:].contiguous()
    prefill_start = time.perf_counter()
    prefill_out = flashinfer.single_prefill_with_kv_cache(
        prefill_q,
        k_stored.contiguous(),
        v_stored.contiguous(),
        o_dtype=torch.bfloat16,
        custom_mask=mask,
        causal=False,
        kv_layout="NHD",
        sm_scale=sm_scale,
        backend="auto",
        k_scale=k_scale,
        v_scale=v_scale,
    )
    torch.cuda.synchronize()
    prefill_first_wall_s = time.perf_counter() - prefill_start
    prefill_event_start = torch.cuda.Event(enable_timing=True)
    prefill_event_end = torch.cuda.Event(enable_timing=True)
    prefill_event_start.record()
    prefill_out = flashinfer.single_prefill_with_kv_cache(
        prefill_q,
        k_stored.contiguous(),
        v_stored.contiguous(),
        o_dtype=torch.bfloat16,
        custom_mask=mask,
        causal=False,
        kv_layout="NHD",
        sm_scale=sm_scale,
        backend="auto",
        k_scale=k_scale,
        v_scale=v_scale,
    )
    prefill_event_end.record()
    prefill_event_end.synchronize()
    prefill_warm_cuda_ms = float(prefill_event_start.elapsed_time(prefill_event_end))

    torch.cuda.synchronize()
    checks = {
        "decode_output_shape": list(decode_out.shape),
        "decode_output_dtype": str(decode_out.dtype),
        "prefill_output_shape": list(prefill_out.shape),
        "prefill_output_dtype": str(prefill_out.dtype),
        "fp8_cache_dtype": str(k_stored.dtype),
        "fp8_cache_layout": "NHD",
        "k_shape": list(k_stored.shape),
        "v_shape": list(v_stored.shape),
        "k_stride": list(k_stored.stride()),
        "v_stride": list(v_stored.stride()),
        "stored_k_finite_fraction": float(torch.isfinite(k_stored.to(torch.float32)).float().mean().item()),
        "stored_v_finite_fraction": float(torch.isfinite(v_stored.to(torch.float32)).float().mean().item()),
        "decode_rel_l2_vs_same_rounded_fp8": relative_l2(torch, decode_out, decode_ref),
        "prefill_rel_l2_vs_same_rounded_fp8": relative_l2(torch, prefill_out, rounded_reference),
        "decode_rel_l2_vs_original_bf16_kv": relative_l2(torch, decode_out, decode_bf16_ref),
        "prefill_rel_l2_vs_original_bf16_kv": relative_l2(torch, prefill_out, bf16_reference),
        "decode_first_call_wall_s_compile_included": decode_first_wall_s,
        "decode_warm_call_cuda_ms": decode_warm_cuda_ms,
        "prefill_first_call_wall_s_compile_included": prefill_first_wall_s,
        "prefill_warm_call_cuda_ms": prefill_warm_cuda_ms,
    }
    if checks["decode_output_shape"] != [q_heads, HEAD_DIM]:
        raise RuntimeError(f"decode shape mismatch: {checks['decode_output_shape']}")
    if checks["prefill_output_shape"] != [VERIFY_TOKENS, q_heads, HEAD_DIM]:
        raise RuntimeError(f"prefill shape mismatch: {checks['prefill_output_shape']}")
    if checks["decode_output_dtype"] != "torch.bfloat16" or checks["prefill_output_dtype"] != "torch.bfloat16":
        raise RuntimeError("kernel output dtype was not BF16")
    if checks["decode_rel_l2_vs_same_rounded_fp8"] > REL_L2_TOLERANCE:
        raise RuntimeError("decode relative-L2 exceeded the predeclared 2% tolerance")
    if checks["prefill_rel_l2_vs_same_rounded_fp8"] > REL_L2_TOLERANCE:
        raise RuntimeError("prefill relative-L2 exceeded the predeclared 2% tolerance")
    if not all(math.isfinite(checks[k]) for k in (
        "decode_rel_l2_vs_same_rounded_fp8", "prefill_rel_l2_vs_same_rounded_fp8",
        "decode_rel_l2_vs_original_bf16_kv", "prefill_rel_l2_vs_original_bf16_kv",
        "decode_first_call_wall_s_compile_included", "decode_warm_call_cuda_ms",
        "prefill_first_call_wall_s_compile_included", "prefill_warm_call_cuda_ms",
    )):
        raise RuntimeError("non-finite metric in primitive result")
    return checks


def run(args) -> dict:
    import torch
    import flashinfer

    expected = json.loads(Path(__file__).with_name("source-contract.json").read_text())
    source_hashes = {}
    for name, digest in expected.items():
        module = importlib.import_module(name)
        actual = hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest()
        if actual != digest:
            raise RuntimeError(f"pinned FlashInfer source mismatch: {name}")
        source_hashes[name] = actual
    gpu = runtime_gpu_metadata(torch)
    if not hasattr(torch, "float8_e4m3fn"):
        raise RuntimeError("PyTorch does not expose float8_e4m3fn")
    if torch.cuda.get_device_capability() != (9, 0):
        raise RuntimeError("H200 Hopper SM90 required")

    torch.manual_seed(SEED)
    torch.cuda.manual_seed_all(SEED)
    device = torch.device("cuda", torch.cuda.current_device())
    results = []
    selected_geometries = GEOMETRIES if args.include_tp1 else GEOMETRIES[:2]
    for geom in selected_geometries:
        validate_geometry(geom["q_heads"], geom["kv_heads"], HEAD_DIM)
        q = torch.randn((CONTEXT, geom["q_heads"], HEAD_DIM), device=device, dtype=torch.bfloat16)
        k = torch.randn((CONTEXT, geom["kv_heads"], HEAD_DIM), device=device, dtype=torch.bfloat16)
        v = torch.randn((CONTEXT, geom["kv_heads"], HEAD_DIM), device=device, dtype=torch.bfloat16)
        for scale_case in SCALE_CASES:
            case_start = time.perf_counter()
            checks = run_case(torch, flashinfer, geom, scale_case, q, k, v)
            results.append({
                "tp": geom["tp"],
                "q_heads": geom["q_heads"],
                "kv_heads": geom["kv_heads"],
                "head_dim": HEAD_DIM,
                "context_tokens": CONTEXT,
                "verify_query_tokens": VERIFY_TOKENS,
                "scale_case": scale_case["name"],
                "k_scale": scale_case["k_scale"],
                "v_scale": scale_case["v_scale"],
                "checks": checks,
                "case_wall_s": time.perf_counter() - case_start,
            })
            print(json.dumps({"event": "case_complete", "case": results[-1]}, sort_keys=True), flush=True)
    return {
        "status": "passed",
        "claim_scope": "one-H200 native FlashInfer primitive only; no model, quality, throughput, SLO, or contest accuracy result",
        "seed": SEED,
        "gpu": gpu,
        "python": sys.version,
        "platform": platform.platform(),
        "torch_version": str(torch.__version__),
        "torch_cuda_version": str(torch.version.cuda),
        "flashinfer_version": _flashinfer_version(flashinfer),
        "flashinfer_runtime_source_sha256": source_hashes,
        "kernel_dtype": "torch.float8_e4m3fn",
        "query_dtype": "torch.bfloat16",
        "kv_layout": "NHD",
        "lower_right_causal_mask": "allowed key index <= context - verify_query_tokens + query_index",
        "acceptance": {"same_rounded_fp8_relative_l2_max": REL_L2_TOLERANCE, "finite": True, "shapes_and_dtypes": True},
        "cases": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--include-tp1", action="store_true", help="also exercise local Q/KV heads 64/4")
    args = parser.parse_args()
    started = time.perf_counter()
    try:
        result = run(args)
    except BaseException as exc:
        result = {
            "status": "failed",
            "claim_scope": "one-H200 native FlashInfer primitive only",
            "seed": SEED,
            "exception_type": type(exc).__name__,
            "exception": str(exc),
            "traceback": traceback.format_exc(),
        }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        print(json.dumps({"event": "primitive_failed", "result": result}, sort_keys=True), file=sys.stderr, flush=True)
        return 1
    result["total_wall_s"] = time.perf_counter() - started
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
