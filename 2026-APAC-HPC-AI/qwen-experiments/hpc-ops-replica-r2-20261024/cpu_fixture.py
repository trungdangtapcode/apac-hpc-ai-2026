#!/usr/bin/env python3
"""CPU-only provenance and diagnostic-bookkeeping fixture; no GPU emulation."""
from collections import Counter
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PINNED = ROOT / "pinned-source/sgl-workspace/sglang/python/sglang/kernels/ops/quantization/fp8_kernel.py"
RUNTIME = json.loads((ROOT / "SOURCE_PROVENANCE.json").read_text())


def byte_pair_counts(actual: bytes, reference: bytes) -> dict:
    assert len(actual) == len(reference)
    pairs = Counter((expected, got) for got, expected in zip(actual, reference) if got != expected)
    count = sum(pairs.values())
    return {
        "mismatch_count": count,
        "element_count": len(actual),
        "mismatch_fraction": count / max(1, len(actual)),
        "byte_pairs": {f"0x{a:02x}->0x{b:02x}": n for (a, b), n in sorted(pairs.items())},
    }


def main() -> None:
    source = PINNED.read_text()
    runner = (ROOT / "run_gpu.py").read_text()
    assert hashlib.sha256(PINNED.read_bytes()).hexdigest() == RUNTIME["runtime_file_sha256"]["/sgl-workspace/sglang/python/sglang/kernels/ops/quantization/fp8_kernel.py"]
    assert "y_s = _absmax / bit8_max" in source
    assert "y_s_inv = 1.0 / y_s" in source
    assert "y * y_s_inv" in source
    assert ".to(y_q_ptr.dtype.element_ty)" in source
    assert 'expected_api_prefix = (' in runner
    assert '"rank_ep", "num_expert_total"' in runner
    assert 'failed = json.loads(args.out.read_text())' in runner
    assert 'actual_vs_direct_division' in runner and 'actual_vs_reciprocal_multiply' in runner
    assert 'rounding_bound_violations' in runner
    assert 'x_dequant = (x_q.float()' in runner
    assert 'atomic_json(out_path, result)' in runner

    # This checks count/fraction/format bookkeeping only; the bytes are toy inputs.
    diagnostic = byte_pair_counts(bytes([0x20, 0x31, 0x44, 0x50]), bytes([0x20, 0x30, 0x45, 0x50]))
    assert diagnostic == {
        "mismatch_count": 2,
        "element_count": 4,
        "mismatch_fraction": 0.5,
        "byte_pairs": {"0x30->0x31": 1, "0x45->0x44": 1},
    }
    assert byte_pair_counts(b"", b"")["mismatch_fraction"] == 0.0
    try:
        byte_pair_counts(b"a", b"")
    except AssertionError:
        pass
    else:
        raise AssertionError("mismatched diagnostic lengths must fail")

    result = {
        "status": "PASS",
        "scope": "CPU provenance and byte-pair bookkeeping fixture only; no Triton, CUDA, FP8 hardware, HPC-Ops, or GPU rounding is emulated.",
        "pinned_quantizer_sha256": hashlib.sha256(PINNED.read_bytes()).hexdigest(),
        "toy_byte_pair_diagnostic": diagnostic,
        "source_expression_checked": "scale=max(abs(x),eps)/448; normalized=x*(1/scale); clamp; cast to output FP8 dtype",
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
