#!/usr/bin/env python3
"""CPU-only source and arithmetic fixtures; does not emulate CUDA/HPC-Ops."""
from __future__ import annotations

import hashlib
import json
import math
import re
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "pinned-source/tencent-hpc-ops"
PROVENANCE = json.loads((ROOT / "HPC_OPS_SOURCE_PROVENANCE.json").read_text())


def bf16_rne(value: float) -> float:
    """Round one finite FP32 scalar to BF16 using round-to-nearest-even."""
    bits = struct.unpack("<I", struct.pack("<f", value))[0]
    rounded = (bits + 0x7FFF + ((bits >> 16) & 1)) & 0xFFFF0000
    return struct.unpack("<f", struct.pack("<I", rounded))[0]


def e4m3fn_codebook() -> list[tuple[float, int]]:
    values: list[tuple[float, int]] = []
    for code in range(0x7F):  # 0x7f is NaN; 0x7e is finite 448.
        exponent, mantissa = (code >> 3) & 0xF, code & 0x7
        value = mantissa * (2.0**-9) if exponent == 0 else (1.0 + mantissa / 8.0) * (2.0 ** (exponent - 7))
        values.append((value, code))
    return values


E4M3_POSITIVE = e4m3fn_codebook()


def e4m3fn_rne(value: float) -> float:
    if not math.isfinite(value) or abs(value) > 448.0:
        raise ValueError("fixture expects finite, nonsaturating E4M3 input")
    sign = -1.0 if value < 0 else 1.0
    magnitude = abs(value)
    quantized, _ = min(E4M3_POSITIVE, key=lambda item: (abs(item[0] - magnitude), item[1] & 1))
    return sign * quantized


def check_sources() -> None:
    assert PROVENANCE["commit"] == "ab1a402724635507037426068f6cddc3d30dc0a8"
    for rel, expected in PROVENANCE["selected_source_sha256"].items():
        assert hashlib.sha256((SOURCE / rel).read_bytes()).hexdigest() == expected, rel
    entry = (SOURCE / "src/fuse_moe/entry.cc").read_text()
    fused = (SOURCE / "src/fuse_moe/fuse_moe.cu").read_text()
    activation = (SOURCE / "src/activation/activation.cu").read_text()
    reduce = (SOURCE / "src/fuse_moe/reduce.cu").read_text()
    assert 'options.dtype(torch::kBFloat16)' in entry
    assert "gate_up_output_ptr, gate_up_input_ptr" in fused
    assert "act_mul_and_blockwise_quant_async(" in fused
    assert "out[i] = silu(gate[i]) * up[i]" in activation
    assert "float scale = max / 448.0f;" in activation
    assert "float inv_scale = 1.0f / (scale + 1e-8f);" in activation
    assert "to<__nv_fp8x4_e4m3>(out)" in activation
    assert "auto y_bf16 = to<T>(y_fp32);" in reduce
    runner = (ROOT / "run_gpu.py").read_text()
    assert "gate_up_fp32.to(torch.bfloat16)" in runner
    assert "activated.abs().amax(dim=-1, keepdim=True) / FP8_MAX" in runner
    assert "1.0 / (activation_scale + 1.0e-8)" in runner
    assert "to(torch.float8_e4m3fn)" in runner
    assert "contribution_fp32.to(torch.bfloat16)" in runner
    assert "if max(oracle_error, candidate_error, baseline_pair_error) > 0.02:" in runner
    assert "if physical_oracle_error > 1e-7:" in runner


def check_toy_pipeline() -> None:
    # Verify the documented cast/scale sequence on a tiny, deterministic CPU row.
    gate = [bf16_rne(-1.0), bf16_rne(0.5), bf16_rne(1.0), bf16_rne(2.0)]
    up = [bf16_rne(0.5), bf16_rne(-1.0), bf16_rne(2.0), bf16_rne(0.25)]
    activated = [(g / (1.0 + math.exp(-g))) * u for g, u in zip(gate, up)]
    scale = max(abs(x) for x in activated) / 448.0
    inv_scale = 1.0 / (scale + 1.0e-8)
    normalized = [x * inv_scale for x in activated]
    quantized = [e4m3fn_rne(x) for x in normalized]
    dequantized = [x * scale for x in quantized]
    assert all(math.isfinite(x) for x in dequantized)
    assert max(abs(x) for x in quantized) <= 448.0
    assert len(quantized) == 4
    assert bf16_rne(1.00390625) == 1.0  # exact halfway case rounds to even.
    assert e4m3fn_rne(1.0) == 1.0 and e4m3fn_rne(-1.0) == -1.0


if __name__ == "__main__":
    check_sources()
    check_toy_pipeline()
    print("PASS: source hashes, source-derived stages, 2% / 1e-7 gates, and toy CPU cast/quantization properties")
    print("LIMIT: no PyTorch, CUDA, Triton, HPC-Ops extension, or H100 behavior was exercised")
