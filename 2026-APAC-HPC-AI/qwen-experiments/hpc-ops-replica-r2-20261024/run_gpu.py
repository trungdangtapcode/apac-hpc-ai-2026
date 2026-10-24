#!/usr/bin/env python3
"""One-GPU synthetic HPC-Ops check for global IDs across virtual EP=5 shards."""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import inspect
import json
import os
from pathlib import Path
import signal
import sys
import time
import traceback

SEED = 2026
LOGICAL_EXPERTS = 128
PHYSICAL_EXPERTS = 130
EP_SIZE = 5
TOKENS = 16
TOPK = 4
HIDDEN = 256
INTERMEDIATE = 128
BLOCK = 128
FP8_MAX = 448.0

ROOT = Path(__file__).resolve().parent
PROVENANCE = json.loads((ROOT / "SOURCE_PROVENANCE.json").read_text())


class DeadlineExpired(TimeoutError):
    pass


def atomic_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    tmp.replace(path)


def relative_l2(actual, reference) -> float:
    denom = reference.float().norm().clamp_min(1e-12)
    return float((actual.float() - reference.float()).norm() / denom)


def fp8_byte_diagnostic(actual, reference) -> dict:
    import torch

    actual_bytes = actual.contiguous().view(torch.uint8).cpu().flatten().tolist()
    reference_bytes = reference.contiguous().view(torch.uint8).cpu().flatten().tolist()
    pairs: dict[str, int] = {}
    for got, expected in zip(actual_bytes, reference_bytes):
        if got != expected:
            key = f"0x{expected:02x}->0x{got:02x}"
            pairs[key] = pairs.get(key, 0) + 1
    count = sum(pairs.values())
    return {
        "mismatch_count": count,
        "element_count": len(actual_bytes),
        "mismatch_fraction": count / max(1, len(actual_bytes)),
        "byte_pairs": dict(sorted(pairs.items())),
    }


def source_aware_activation_diagnostic(torch, x, x_q, x_scale, direct_q, reciprocal_q) -> dict:
    groups = HIDDEN // BLOCK
    x32 = x.float().view(TOKENS, groups, BLOCK)
    scale = x_scale.float()
    qactual = x_q.float().view(TOKENS, groups, BLOCK)
    qinput = x32 / scale[:, :, None]
    dequant = qactual * scale[:, :, None]
    absolute_error = (dequant - x32).abs()

    # Positive finite E4M3FN values in ascending byte order, excluding NaN 0x7f.
    codes = torch.arange(127, device=x.device, dtype=torch.uint8)
    lattice = codes.view(torch.float8_e4m3fn).float()
    upper = torch.searchsorted(lattice, qinput.abs().contiguous()).clamp(1, len(lattice) - 1)
    lower_value = lattice[(upper - 1).reshape(-1)].view_as(qinput)
    upper_value = lattice[upper.reshape(-1)].view_as(qinput)
    local_gap = upper_value - lower_value
    fp32_allowance = 4.0 * torch.finfo(torch.float32).eps * torch.maximum(qinput.abs(), torch.ones_like(qinput))
    quant_error_bound = scale[:, :, None] * (0.5 * local_gap + fp32_allowance)
    bound_excess = absolute_error > quant_error_bound

    return {
        "input_shape": list(x.shape),
        "input_dtype": str(x.dtype),
        "activation_dtype": str(x_q.dtype),
        "scale_shape": list(x_scale.shape),
        "scale_dtype": str(x_scale.dtype),
        "activation_scales_finite_positive": bool(torch.isfinite(scale).all() and (scale > 0).all()),
        "activation_quantized_finite": bool(torch.isfinite(qactual).all()),
        "activation_scales_min": float(scale.min()),
        "activation_scales_max": float(scale.max()),
        "input_absmax": float(x32.abs().max()),
        "activation_fp8_min": float(qactual.min()),
        "activation_fp8_max": float(qactual.max()),
        "activation_values_at_fp8_limits": int(((qactual <= -FP8_MAX) | (qactual >= FP8_MAX)).sum()),
        "activation_fp8_absmax_within_cast_limit": bool(qactual.abs().max() <= FP8_MAX),
        "actual_vs_direct_division": fp8_byte_diagnostic(x_q, direct_q),
        "actual_vs_reciprocal_multiply": fp8_byte_diagnostic(x_q, reciprocal_q),
        "dequantized_vs_fp32_input": {
            "max_abs_error": float(absolute_error.max()),
            "rms_abs_error": float(absolute_error.square().mean().sqrt()),
            "relative_l2": relative_l2(dequant, x32),
            "rounding_bound_max_abs": float(quant_error_bound.max()),
            "rounding_bound_violations": int(bound_excess.sum()),
            "rounding_bound_elements": int(bound_excess.numel()),
            "rounding_bound": "half the larger adjacent positive E4M3FN spacing around the FP32 normalized input, scaled by the actual group scale, plus 4 FP32 epsilons in normalized space",
        },
    }


def quantize_blockwise(weight, block: int = BLOCK):
    # Mirrors the pinned SGLang block layout: scale=[E,N/128,K/128].
    e, n, k = weight.shape
    assert n % block == 0 and k % block == 0
    viewed = weight.contiguous().view(e, n // block, block, k // block, block)
    amax = viewed.abs().amax(dim=(2, 4), keepdim=True).clamp(min=1e-6)
    scale = amax / FP8_MAX
    quantized = (viewed / scale).clamp(-FP8_MAX, FP8_MAX).view(e, n, k).to(
        __import__("torch").float8_e4m3fn
    )
    scale = scale.squeeze(-1).squeeze(2)
    return quantized, scale


def pad_scale(scale, align: int = 4):
    import torch

    k = scale.shape[-1]
    padded_k = (k + align - 1) // align * align
    if k == padded_k:
        return scale.contiguous()
    padded = scale.new_zeros((*scale.shape[:-1], padded_k))
    padded[..., :k].copy_(scale)
    return padded


def dequant_weight(weight_q, scale):
    e, n, k = weight_q.shape
    blocks_n = n // BLOCK
    blocks_k = k // BLOCK
    return (
        weight_q.float()
        .view(e, blocks_n, BLOCK, blocks_k, BLOCK)
        .mul(scale[:, :, None, :, None])
        .view(e, n, k)
    )


def build_ids(torch):
    logits = torch.full((TOKENS, LOGICAL_EXPERTS), -100.0, device="cuda")
    for row in range(TOKENS):
        logits[row, 0] = 6.0 + 0.002 * row
        logits[row, 1] = 5.0
        logits[row, 127] = 4.0
        logits[row, 64] = 3.0
    values, logical_ids = torch.topk(logits, TOPK, dim=-1)
    topk_weights = values.softmax(dim=-1).float()
    physical_ids = logical_ids.clone()
    for row in range(TOKENS):
        for col in range(TOPK):
            expert = int(logical_ids[row, col])
            if expert == 0 and row % 2:
                physical_ids[row, col] = 128
            elif expert == 1 and row % 2 == 0:
                physical_ids[row, col] = 129
    return logits, logical_ids.to(torch.int32), physical_ids.to(torch.int32), topk_weights


def torch_oracle(torch, x_dequant, w13_dequant, w2_dequant, logical_ids, weights, physical_map):
    import torch.nn.functional as F

    out = torch.zeros((x_dequant.shape[0], HIDDEN), dtype=torch.float32, device=x_dequant.device)
    for row in range(x_dequant.shape[0]):
        for col in range(logical_ids.shape[1]):
            expert_id = int(logical_ids[row, col])
            logical = physical_map[expert_id] if physical_map is not None else expert_id
            gate_up = F.linear(x_dequant[row : row + 1], w13_dequant[logical])
            gate, up = gate_up.chunk(2, dim=-1)
            activated = F.silu(gate) * up
            contribution = F.linear(activated, w2_dequant[logical])
            out[row] += contribution[0] * weights[row, col]
    return out


def run(out_path: Path) -> dict:
    import torch
    import hpc
    from sglang.kernels.ops.quantization.fp8_kernel import sglang_per_token_group_quant_fp8
    from sglang.srt.layers.moe.moe_runner.hpc_ops import pad_hpc_ops_block_scale

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA unavailable")
    if torch.cuda.device_count() != 1:
        raise RuntimeError(f"Expected exactly one PBS-assigned visible GPU, got {torch.cuda.device_count()}")
    name = torch.cuda.get_device_name(0)
    capability = torch.cuda.get_device_capability(0)
    if "H100" not in name or capability != (9, 0):
        raise RuntimeError(f"Expected H100 SM90; got name={name!r} capability={capability}")
    if not hasattr(hpc, "fuse_moe_blockwise"):
        raise RuntimeError("Pinned HPC-Ops package lacks hpc.fuse_moe_blockwise")
    expected_api_prefix = (
        "x", "x_scale", "gate_up_weight", "gate_up_weight_scale",
        "down_weight", "down_weight_scale", "topk_ids", "topk_scale",
        "rank_ep", "num_expert_total",
    )
    actual_api = tuple(inspect.signature(hpc.fuse_moe_blockwise).parameters)
    if actual_api[: len(expected_api_prefix)] != expected_api_prefix:
        raise RuntimeError(
            f"Pinned HPC-Ops callable signature mismatch: expected prefix "
            f"{expected_api_prefix}, got {actual_api}"
        )
    package_version = importlib.metadata.version("hpc-ops")
    if package_version != PROVENANCE["hpc_ops_distribution"].removeprefix("hpc-ops "):
        raise RuntimeError(
            f"HPC-Ops build mismatch: expected {PROVENANCE['hpc_ops_distribution']}, got {package_version}"
        )

    runtime_hashes = {}
    for source_path, expected_hash in PROVENANCE["runtime_file_sha256"].items():
        path = Path(source_path)
        actual_hash = hashlib.sha256(path.read_bytes()).hexdigest()
        runtime_hashes[source_path] = actual_hash
        if actual_hash != expected_hash:
            raise RuntimeError(
                f"pinned runtime source mismatch for {source_path}: "
                f"expected {expected_hash}, got {actual_hash}"
            )

    torch.manual_seed(SEED)
    torch.cuda.manual_seed_all(SEED)
    device = torch.device("cuda:0")
    result = {
        "status": "RUNNING",
        "scope": "One-GPU synthetic MoE math only. The five virtual ranks run sequentially on this one H100; no process group, all-reduce, or inter-GPU routing is tested.",
        "started_unix": time.time(),
        "seed": SEED,
        "device": {"name": name, "capability": list(capability), "uuid": str(getattr(torch.cuda.get_device_properties(0), "uuid", "unavailable")), "visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES")},
        "software": {"torch": torch.__version__, "hpc_ops": package_version, "hpc_module": str(Path(hpc.__file__).resolve()), "hpc_fuse_moe_blockwise_signature": str(inspect.signature(hpc.fuse_moe_blockwise)), "native_extension_path": str(Path(hpc.__file__).resolve().parent / "_C.abi3.so"), "native_extension_bytes": (Path(hpc.__file__).resolve().parent / "_C.abi3.so").stat().st_size, "source_image_nscc_path": os.environ.get("QWEN_IMAGE_PATH"), "verified_runtime_source_sha256": runtime_hashes},
        "geometry": {"logical_experts": LOGICAL_EXPERTS, "physical_experts": PHYSICAL_EXPERTS, "ep_size": EP_SIZE, "physical_experts_per_virtual_rank": PHYSICAL_EXPERTS // EP_SIZE, "tokens": TOKENS, "topk": TOPK, "hidden_size": HIDDEN, "intermediate_size": INTERMEDIATE, "block_shape": [BLOCK, BLOCK]},
        "checks": {},
    }
    atomic_json(out_path, result)

    # Fixed synthetic Qwen-like routed block: no model or checkpoint is opened.
    x = torch.randn((TOKENS, HIDDEN), dtype=torch.bfloat16, device=device).contiguous()
    w13_fp32 = torch.randn((LOGICAL_EXPERTS, 2 * INTERMEDIATE, HIDDEN), dtype=torch.float32, device=device) * 0.02
    w2_fp32 = torch.randn((LOGICAL_EXPERTS, HIDDEN, INTERMEDIATE), dtype=torch.float32, device=device) * 0.02
    w13_logical, w13_scale_logical = quantize_blockwise(w13_fp32)
    w2_logical, w2_scale_logical = quantize_blockwise(w2_fp32)

    # Physical slots 128 and 129 carry exact copies of logical experts 0 and 1.
    w13_physical = torch.cat([w13_logical, w13_logical[:2]], dim=0).contiguous()
    w2_physical = torch.cat([w2_logical, w2_logical[:2]], dim=0).contiguous()
    w13_scale_physical = torch.cat([w13_scale_logical, w13_scale_logical[:2]], dim=0).contiguous()
    w2_scale_physical = torch.cat([w2_scale_logical, w2_scale_logical[:2]], dim=0).contiguous()
    physical_to_logical = list(range(LOGICAL_EXPERTS)) + [0, 1]
    assert w13_physical.shape[0] == PHYSICAL_EXPERTS and w2_physical.shape[0] == PHYSICAL_EXPERTS
    assert torch.equal(w13_physical[128].view(torch.uint8), w13_physical[0].view(torch.uint8)) and torch.equal(w13_physical[129].view(torch.uint8), w13_physical[1].view(torch.uint8))
    assert torch.equal(w2_physical[128].view(torch.uint8), w2_physical[0].view(torch.uint8)) and torch.equal(w2_physical[129].view(torch.uint8), w2_physical[1].view(torch.uint8))

    # SGLang's actual activation quantizer is used by the runner wrapper.
    x_q, x_scale = sglang_per_token_group_quant_fp8(x, BLOCK)
    groups = HIDDEN // BLOCK
    x_fp32_groups = x.float().view(TOKENS, groups, BLOCK)
    manual_scale = x_fp32_groups.abs().amax(dim=-1).clamp(min=1e-10) / FP8_MAX
    direct_division_q = (x_fp32_groups / manual_scale[:, :, None]).clamp(-FP8_MAX, FP8_MAX).to(torch.float8_e4m3fn).view(TOKENS, HIDDEN)
    reciprocal_multiply_q = (x_fp32_groups * (1.0 / manual_scale[:, :, None])).clamp(-FP8_MAX, FP8_MAX).to(torch.float8_e4m3fn).view(TOKENS, HIDDEN)
    if x_q.shape != x.shape or x_q.dtype != torch.float8_e4m3fn:
        raise RuntimeError(f"pinned activation quantizer returned unexpected shape/dtype: {tuple(x_q.shape)} {x_q.dtype}")
    if x_scale.shape != manual_scale.shape:
        raise RuntimeError(f"activation scale shape mismatch: helper={tuple(x_scale.shape)} manual={tuple(manual_scale.shape)}")
    torch.testing.assert_close(x_scale.float(), manual_scale, rtol=2e-5, atol=1e-7)
    activation_diagnostic = source_aware_activation_diagnostic(torch, x, x_q, x_scale, direct_division_q, reciprocal_multiply_q)
    result["activation_quantization_diagnostic"] = activation_diagnostic
    atomic_json(out_path, result)
    if (not activation_diagnostic["activation_scales_finite_positive"]
            or not activation_diagnostic["activation_quantized_finite"]
            or not activation_diagnostic["activation_fp8_absmax_within_cast_limit"]):
        raise RuntimeError("pinned activation quantizer returned non-finite values, invalid scales, or out-of-range FP8 values; diagnostic was persisted")
    if activation_diagnostic["dequantized_vs_fp32_input"]["rounding_bound_violations"]:
        raise RuntimeError("pinned activation quantization exceeded the source-aware E4M3 rounding bound; diagnostic was persisted")
    x_dequant = (x_q.float().view(TOKENS, groups, BLOCK) * x_scale.float()[:, :, None]).view(TOKENS, HIDDEN)

    logits, logical_ids, physical_ids, topk_weights = build_ids(torch)
    selected_ids = physical_ids.flatten().tolist()
    if not {128, 129, 127}.issubset(set(selected_ids)) or not {0, 1}.issubset(set(selected_ids)):
        raise RuntimeError("deterministic router fixture did not exercise base and replica IDs")
    if any(len(set(row)) != TOPK for row in physical_ids.tolist()):
        raise RuntimeError("a route row selected more than one physical copy of the same logical expert")
    if any(physical_to_logical[e] != int(l) for row_p, row_l in zip(physical_ids.tolist(), logical_ids.tolist()) for e, l in zip(row_p, row_l)):
        raise RuntimeError("physical ID fixture disagrees with the physical-to-logical map")

    w13_physical_scales_padded = pad_hpc_ops_block_scale(w13_scale_physical)
    w2_physical_scales_padded = pad_hpc_ops_block_scale(w2_scale_physical)
    w13_logical_scales_padded = pad_hpc_ops_block_scale(w13_scale_logical)
    w2_logical_scales_padded = pad_hpc_ops_block_scale(w2_scale_logical)
    if w13_physical_scales_padded.shape[-1] % 4 or w2_physical_scales_padded.shape[-1] % 4:
        raise RuntimeError("HPC-Ops block scale K dimension is not padded to four")

    torch.cuda.synchronize()
    candidate_started = time.monotonic()
    rank_outputs = []
    rank_output_dtypes = []
    rank_nonzero = []
    for rank in range(EP_SIZE):
        start = rank * (PHYSICAL_EXPERTS // EP_SIZE)
        end = start + (PHYSICAL_EXPERTS // EP_SIZE)
        # This is the installed native API's intended single-rank contribution:
        # local weights, global physical top-k IDs, virtual EP rank, global E.
        out = hpc.fuse_moe_blockwise(
            x_q,
            x_scale,
            w13_physical[start:end].contiguous(),
            w13_physical_scales_padded[start:end].contiguous(),
            w2_physical[start:end].contiguous(),
            w2_physical_scales_padded[start:end].contiguous(),
            physical_ids,
            topk_weights,
            rank,
            PHYSICAL_EXPERTS,
        )
        if out.shape != (TOKENS, HIDDEN) or out.dtype != torch.bfloat16:
            raise RuntimeError(f"rank {rank} returned shape {tuple(out.shape)}")
        if not torch.isfinite(out.float()).all():
            raise RuntimeError(f"rank {rank} returned non-finite output")
        rank_output_dtypes.append(str(out.dtype))
        rank_nonzero.append(bool(torch.count_nonzero(out).item()))
        rank_outputs.append(out.float())
    torch.cuda.synchronize()
    candidate = torch.stack(rank_outputs).sum(dim=0)
    candidate_seconds = time.monotonic() - candidate_started

    # Native EP=1 baseline takes the logical 128-expert weights and IDs.
    baseline_started = time.monotonic()
    baseline = hpc.fuse_moe_blockwise(
        x_q,
        x_scale,
        w13_logical.contiguous(),
        w13_logical_scales_padded.contiguous(),
        w2_logical.contiguous(),
        w2_logical_scales_padded.contiguous(),
        logical_ids,
        topk_weights,
        0,
        LOGICAL_EXPERTS,
    )
    torch.cuda.synchronize()
    baseline_seconds = time.monotonic() - baseline_started
    if baseline.shape != (TOKENS, HIDDEN) or baseline.dtype != torch.bfloat16 or not torch.isfinite(baseline.float()).all():
        raise RuntimeError("native EP1 baseline shape/dtype/finite gate failed")

    w13_logical_dequant = dequant_weight(w13_logical, w13_scale_logical)
    w2_logical_dequant = dequant_weight(w2_logical, w2_scale_logical)
    oracle = torch_oracle(torch, x_dequant, w13_logical_dequant, w2_logical_dequant, logical_ids, topk_weights, None)
    oracle_error = relative_l2(baseline, oracle)
    candidate_error = relative_l2(candidate, oracle)
    baseline_pair_error = relative_l2(candidate, baseline)
    result["outputs_partial"] = {"ep5_vs_oracle_relative_l2": candidate_error, "ep1_vs_oracle_relative_l2": oracle_error, "ep5_vs_ep1_relative_l2": baseline_pair_error}
    atomic_json(out_path, result)
    if max(oracle_error, candidate_error, baseline_pair_error) > 0.02:
        raise RuntimeError(f"relative-L2 gate failed: baseline/oracle={oracle_error:.6g}, EP5/oracle={candidate_error:.6g}, EP5/EP1={baseline_pair_error:.6g}; threshold=0.02; partial metrics persisted")

    # Check the duplicate physical slots against the independent logical oracle by
    # translating physical IDs back to logical IDs for the same selected routes.
    physical_oracle = torch_oracle(torch, x_dequant, w13_logical_dequant, w2_logical_dequant, physical_ids, topk_weights, physical_to_logical)
    physical_oracle_error = relative_l2(physical_oracle, oracle)
    result["outputs_partial"]["physical_map_oracle_relative_l2"] = physical_oracle_error
    atomic_json(out_path, result)
    if physical_oracle_error > 1e-7:
        raise RuntimeError(f"physical duplicate-weight oracle mismatch: relative-L2={physical_oracle_error:.6g}; partial metrics persisted")

    activation_q = x_q.float()
    result.update({
        "status": "PASS",
        "finished_unix": time.time(),
        "elapsed_seconds": time.monotonic() - _started,
        "native_candidate_seconds": candidate_seconds,
        "native_ep1_seconds": baseline_seconds,
        "quantization": {
            "activation_quantizer": "pinned sglang_per_token_group_quant_fp8(x, 128); byte differences versus direct division and source-shaped reciprocal multiplication are retained as diagnostics, while actual SGLang activations feed both native calls and the FP32 oracle",
            "activation_input_dtype": str(x.dtype),
            "activation_quantized_dtype": str(x_q.dtype),
            "activation_quantized_shape": list(x_q.shape),
            "activation_scale_dtype": str(x_scale.dtype),
            "activation_scale_shape": list(x_scale.shape),
            "activation_input_absmax": float(x.float().abs().max()),
            "activation_scale_min": float(x_scale.float().min()),
            "activation_scale_max": float(x_scale.float().max()),
            "activation_fp8_min": float(activation_q.min()),
            "activation_fp8_max": float(activation_q.max()),
            "activation_values_at_fp8_limits": int(((activation_q <= -FP8_MAX) | (activation_q >= FP8_MAX)).sum()),
            "w13_fp8_shape_physical": list(w13_physical.shape),
            "w13_scale_shape_physical_before_padding": list(w13_scale_physical.shape),
            "w13_scale_shape_physical_after_padding": list(w13_physical_scales_padded.shape),
            "w2_fp8_shape_physical": list(w2_physical.shape),
            "w2_scale_shape_physical_before_padding": list(w2_scale_physical.shape),
            "w2_scale_shape_physical_after_padding": list(w2_physical_scales_padded.shape),
            "weight_scale_convention": "Pinned SGLang test helper quantizes weight as w / (amax/448) and passes returned amax/448 to hpc.fuse_moe_blockwise; local argument names in hpc_ops.py include scale_inv but source test follows this exact convention.",
        },
        "route": {
            "logical_topk_ids": logical_ids.tolist(),
            "global_physical_topk_ids": physical_ids.tolist(),
            "topk_weights": topk_weights.tolist(),
            "physical_to_logical_tail": physical_to_logical[-4:],
            "rank_nonzero_output": rank_nonzero,
        },
        "outputs": {
            "native_candidate_dtype_per_rank": rank_output_dtypes,
            "native_baseline_dtype": str(baseline.dtype),
            "oracle_dtype": str(oracle.dtype),
            "candidate_shape": list(candidate.shape),
            "baseline_shape": list(baseline.shape),
            "oracle_shape": list(oracle.shape),
            "ep5_vs_oracle_relative_l2": candidate_error,
            "ep1_vs_oracle_relative_l2": oracle_error,
            "ep5_vs_ep1_relative_l2": baseline_pair_error,
            "physical_map_oracle_relative_l2": physical_oracle_error,
            "gate": "PASS; each measured relative L2 <= 0.02, physical-copy oracle <= 1e-7",
        },
        "limitations": [
            "Five virtual EP ranks execute serially on one H100; summing outputs with a local torch operation is not a communication or collective test.",
            "Synthetic 256-hidden by 128-intermediate weights do not prove Qwen checkpoint quantization metadata, loader behavior, model accuracy, or model-scale memory fit.",
            "The fixed deterministic route exercises global physical IDs and copied slots; it does not establish production request routing, EPLB load balance, DP-attention, NIXL, or MNNVL behavior.",
        ],
    })
    atomic_json(out_path, result)
    return result


_started = time.monotonic()

def _alarm(_signum, _frame):
    raise DeadlineExpired("internal execution deadline reached")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    signal.signal(signal.SIGALRM, _alarm)
    signal.alarm(440)
    try:
        result = run(args.out)
        print(json.dumps(result, indent=2, sort_keys=True), flush=True)
        return 0
    except BaseException as exc:
        try:
            failed = json.loads(args.out.read_text())
        except (OSError, json.JSONDecodeError):
            failed = {}
        failed.update({
            "status": "BLOCKED" if isinstance(exc, DeadlineExpired) else "ERROR",
            "scope": "One-GPU synthetic MoE math only; no distributed all-reduce is claimed.",
            "elapsed_seconds": time.monotonic() - _started,
            "error_type": type(exc).__name__,
            "error": str(exc),
            "traceback": traceback.format_exc(),
        })
        atomic_json(args.out, failed)
        print(json.dumps(failed, indent=2, sort_keys=True), file=sys.stderr, flush=True)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
