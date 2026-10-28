#!/usr/bin/env python3
"""Offline static source check for the pinned image API evidence."""
import hashlib
import ast
import sys
from pathlib import Path

EXPECTED = {
    "flashinfer_backend.py": "3cb0b4d5c4d3e8e94724d07c91130ab69d85e73c84cefaf3f69a5ad7813f5c7e",
    "prefill.py": "7f4926dcf1610dfd058716e9ba3d8b08f15268e607ea1e28bef7d28b8b2f889e",
}


def main() -> int:
    if len(sys.argv) != 4:
        print("usage: validate_sources.py FLASHINFER_BACKEND_PY PREFILL_PY PREFILL_DIAGNOSTIC_PY", file=sys.stderr)
        return 2
    backend_path, prefill_path, diagnostic_path = map(Path, sys.argv[1:])
    for path, key in ((backend_path, "flashinfer_backend.py"), (prefill_path, "prefill.py")):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != EXPECTED[key]:
            raise SystemExit(f"FAIL {key}: expected {EXPECTED[key]}, got {digest}")

    backend = backend_path.read_text()
    prefill = prefill_path.read_text()
    requirements = (
        (backend, "BatchPrefillWithPagedKVCacheWrapper", "SGLang paged wrapper import"),
        (backend, "BatchPrefillWithRaggedKVCacheWrapper", "SGLang ragged wrapper import"),
        (backend, "causal=causal", "SGLang causal forwarding"),
        (prefill, "class BatchPrefillWithPagedKVCacheWrapper", "native paged wrapper"),
        (prefill, "class BatchPrefillWithRaggedKVCacheWrapper", "native ragged wrapper"),
        (prefill, "def plan(", "native prefill planning API"),
        (prefill, "def run(", "native prefill execution API"),
    )
    for source, needle, description in requirements:
        if needle not in source:
            raise SystemExit(f"FAIL missing source evidence: {description}")
    native_tree = ast.parse(prefill)
    class_methods = {}
    for node in ast.walk(native_tree):
        if isinstance(node, ast.ClassDef) and node.name in {
            "BatchPrefillWithPagedKVCacheWrapper", "BatchPrefillWithRaggedKVCacheWrapper"
        }:
            class_methods[node.name] = {n.name: n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    expected_params = {
        "BatchPrefillWithPagedKVCacheWrapper": {"__init__": {"float_workspace_buffer", "kv_layout"}, "plan": {"qo_indptr", "paged_kv_indptr", "paged_kv_indices", "paged_kv_last_page_len", "head_dim_qk", "page_size", "causal", "q_data_type", "kv_data_type"}, "run": {"q", "paged_kv_cache"}},
        "BatchPrefillWithRaggedKVCacheWrapper": {"__init__": {"float_workspace_buffer", "kv_layout"}, "plan": {"qo_indptr", "kv_indptr", "head_dim_qk", "causal", "q_data_type", "kv_data_type"}, "run": {"q", "k", "v"}},
    }
    if set(class_methods) != set(expected_params):
        raise SystemExit("FAIL native wrapper classes absent")
    for cls, methods in expected_params.items():
        for method, needed in methods.items():
            node = class_methods[cls].get(method)
            args = set() if node is None else {a.arg for a in node.args.args}
            if not needed <= args:
                raise SystemExit(f"FAIL {cls}.{method} signature missing {sorted(needed - args)}")

    diagnostic = ast.parse(diagnostic_path.read_text())
    calls = [n for n in ast.walk(diagnostic) if isinstance(n, ast.Call)]
    plans = [n for n in calls if isinstance(n.func, ast.Attribute) and n.func.attr == "plan"]
    runs = [n for n in calls if isinstance(n.func, ast.Attribute) and n.func.attr == "run"]
    if len(plans) != 2 or len(runs) != 2:
        raise SystemExit("FAIL diagnostic must bind exactly one plan/run for each prefill wrapper path")
    if sorted(len(n.args) for n in plans) != [5, 8] or sorted(len(n.args) for n in runs) != [2, 3]:
        raise SystemExit("FAIL diagnostic positional API bindings do not match native paged/ragged signatures")
    for call in plans:
        keywords = {k.arg for k in call.keywords}
        if not {"causal", "sm_scale", "q_data_type", "kv_data_type"} <= keywords:
            raise SystemExit("FAIL plan call lacks causal/scale/dtype bindings")
    print("PASS pinned source hashes, wrapper AST signatures, and paged/ragged diagnostic API bindings")
    print("NOT a CUDA runtime validation, scheduler submission, or correctness pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
