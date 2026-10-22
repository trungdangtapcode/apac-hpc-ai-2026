#!/usr/bin/env python3
"""Derive an instrumented conn.py from the pinned native H200 NIXL source."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import sys

EXPECTED_SOURCE_SHA256 = "912b7edb95b03604354cc0137f111756ed5bb0eaa91345e713afa53b5bf5024f"
DEFAULT_SOURCE = Path(
    "/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-10/"
    "s37-h200-target-reference/nixl-conn.py"
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def derive(source_path: Path, output_dir: Path) -> dict:
    raw = source_path.read_bytes()
    source_hash = sha256(raw)
    if source_hash != EXPECTED_SOURCE_SHA256:
        raise SystemExit(f"source hash mismatch: expected {EXPECTED_SOURCE_SHA256}, got {source_hash}")
    text = raw.decode("utf-8")
    tree = ast.parse(text, filename=str(source_path))
    init_methods = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "NixlKVManager":
            init_methods = [
                item for item in node.body
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == "__init__"
            ]
            break
    if len(init_methods) != 1:
        raise SystemExit("expected exactly one NixlKVManager.__init__")
    calls = []
    for node in ast.walk(init_methods[0]):
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            call = node.value
            func = call.func
            if (
                isinstance(func, ast.Attribute)
                and func.attr == "register_buffer_to_engine"
                and isinstance(func.value, ast.Name)
                and func.value.id == "self"
                and not call.args and not call.keywords
            ):
                calls.append(node)
    if len(calls) != 1:
        raise SystemExit(f"expected one native registration call in __init__, found {len(calls)}")
    call_node = calls[0]
    lines = text.splitlines(keepends=True)
    start = sum(len(line) for line in lines[: call_node.lineno - 1]) + call_node.col_offset
    end = sum(len(line) for line in lines[: call_node.end_lineno - 1]) + call_node.end_col_offset
    original = text[start:end]
    if original != "self.register_buffer_to_engine()":
        raise SystemExit(f"registration expression differs from reviewed spelling: {original!r}")
    replacement = "_instrument_nixl_registration(self, self.register_buffer_to_engine)"
    derived = text[:start] + replacement + text[end:]
    marker = "from __future__ import annotations\n"
    if derived.count(marker) != 1:
        raise SystemExit("expected one future import marker")
    derived = derived.replace(
        marker,
        marker + "\nfrom sglang.srt.disaggregation.nixl.kv_geometry import (\n"
        "    instrument_registration as _instrument_nixl_registration,\n)\n",
        1,
    )
    ast.parse(derived, filename="nixl-conn-instrumented.py")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "nixl-conn-instrumented.py"
    metadata_path = output_dir / "DERIVATION.json"
    if output_path.exists() or metadata_path.exists():
        raise SystemExit("refusing to overwrite existing derivation outputs")
    out_bytes = derived.encode("utf-8")
    output_path.write_bytes(out_bytes)
    result = {
        "schema": "h200-kv-geometry-derivation-v1",
        "source_path": str(source_path),
        "source_sha256": source_hash,
        "expected_source_sha256": EXPECTED_SOURCE_SHA256,
        "derived_file": output_path.name,
        "derived_sha256": sha256(out_bytes),
        "helper_file": "kv_geometry.py",
        "native_registration_call": "self.register_buffer_to_engine()",
        "instrumented_expression": replacement,
        "other_native_source_changes": False,
    }
    metadata_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


if __name__ == "__main__":
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_SOURCE
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(__file__).resolve().parent
    print(json.dumps(derive(src, out), indent=2, sort_keys=True))
