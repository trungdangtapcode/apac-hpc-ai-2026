#!/usr/bin/env python3
"""CPU-only AST, source-hash and S107/S108 preparation checks."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
STUDY = Path(__file__).resolve().parent
CONTROL = ROOT / "serving-tuning-11/s107-h200-sparse-graph-control"
BLOCKED = ROOT / "serving-tuning-11/s108-h200-sparse-graph-compile"
GRAPH = [1, 2, 4, 8, 16, 32, 48, 50, 52, 54, 56, 64]
COMPILE = GRAPH[:-1]
HOT = [50, 52, 54, 56]


def _function(tree, name):
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return node
    raise AssertionError(f"missing function {name}")


def _source(path):
    return path.read_text()


def _sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_source():
    manifest = json.loads((STUDY / "SOURCE_MANIFEST.json").read_text())
    for item in manifest["files"]:
        path = STUDY / item["path"]
        assert _sha(path) == item["sha256"], f"source hash mismatch: {item['path']}"
        ast.parse(_source(path), filename=str(path))

    base = STUDY / "evidence/sglang/srt/model_executor/runner/base_cuda_graph_runner.py"
    base_tree = ast.parse(_source(base))
    capture = ast.unparse(_function(base_tree, "get_batch_sizes_to_capture"))
    pad = ast.unparse(_function(base_tree, "_pad_to_bucket"))
    assert "server_args.torch_compile_max_bs" in capture and "if get_flags().capture.enable_torch_compile" in capture
    assert "bisect.bisect_left" in pad

    args = STUDY / "evidence/sglang/srt/server_args.py"
    args_tree = ast.parse(_source(args))
    parser = ast.unparse(_function(args_tree, "_parse_cuda_graph_config"))
    compat = ast.unparse(_function(args_tree, "_handle_cuda_graph_config"))
    assert 'self.cuda_graph_bs_decode' in parser and any(isinstance(n, ast.Constant) and n.value == 'bs' for n in ast.walk(_function(args_tree, '_parse_cuda_graph_config')))
    assert "self._parse_cuda_graph_config()" in compat
    server_source = _source(args)
    assert "decode_cuda_graph_config.max_bs = max(decode_cuda_graph_config.bs)" in server_source
    assert "if self.device != \"cpu\":" in server_source

    common = STUDY / "evidence/sglang/srt/utils/common.py"
    common_tree = ast.parse(_source(common))
    align = ast.unparse(_function(common_tree, "get_cuda_graph_batch_size_alignment"))
    require_buf = ast.unparse(_function(common_tree, "require_gathered_buffer"))
    require_attn = ast.unparse(_function(common_tree, "require_attn_tp_gather"))
    assert "alignment = 1" in align and "require_gathered_buffer" in align
    assert "require_mlp_tp_gather" in require_buf and "require_attn_tp_gather" in require_buf
    assert "get_moe_a2a_backend().is_none()" in require_attn and "moe_dense_tp_size is not None" in require_attn

    sizes = GRAPH
    assert len(sizes) == 12 and len(set(sizes)) == 12 and sizes == sorted(sizes)
    assert all(x > 0 for x in sizes) and sizes[-1] == 64
    assert 51 not in sizes and 53 not in sizes and set(HOT).issubset(sizes)
    compiled = [x for x in sizes if x <= 56]
    assert compiled == COMPILE and len(compiled) == 11
    mapping = {x: next(b for b in sizes if b >= x) for x in (49, 50, 51, 52, 53, 54, 55, 56, 57, 64)}
    assert mapping == {49: 50, 50: 50, 51: 52, 52: 52, 53: 54, 54: 54, 55: 56, 56: 56, 57: 64, 64: 64}
    return {"source_files_hash_verified": len(manifest["files"]), "graph_buckets": sizes,
            "compile_buckets_source_eligibility_only": compiled,
            "raw_to_bucket": mapping, "hot_buckets": HOT}


def check_arm_state():
    a = json.loads((CONTROL / "config.json").read_text())
    b = json.loads((BLOCKED / "config.json").read_text())
    assert a["decode_cuda_graph_batch_sizes"] == GRAPH
    assert b["decode_cuda_graph_batch_sizes"] == GRAPH
    assert a["decode_torch_compile_max_bs"] == b["decode_torch_compile_max_bs"] == 56
    assert a["decode_enable_torch_compile"] is False
    assert b["decode_enable_torch_compile"] is True
    assert a["expected_capture_buckets"] == b["expected_capture_buckets"] == GRAPH
    assert a["expected_compile_buckets"] == []
    assert b["expected_compile_buckets"] == COMPILE
    differences = {k for k in set(a) | set(b) if a.get(k) != b.get(k)}
    permitted = {"arm", "experiment", "label", "study_arm", "decode_enable_torch_compile",
                 "expected_compile_buckets", "expected_hot_compile_buckets", "admission_state",
                 "source_compatibility_status", "blocked_by_job"}
    assert differences <= permitted, f"unexpected arm differences: {sorted(differences - permitted)}"
    assert a["admission_state"] == "PREPARED_FOR_ROOT_REVIEW_NOT_SUBMITTED"
    assert b["admission_state"] == "BLOCKED_SOURCE_INCOMPATIBILITY"
    assert not (BLOCKED / "job.sbatch").exists()
    assert not (BLOCKED / "topology-job.sh").exists()
    assert not (BLOCKED / "worker.sh").exists()
    assert (CONTROL / "job.sbatch").exists()
    assert _sha(CONTROL / "compile-hooks/observer_module.py") == _sha(BLOCKED / "compile-hooks/observer_module.py")
    assert _sha(CONTROL / "check_sparse_graph_startup.py") == _sha(STUDY / "check_sparse_graph_startup.py")
    assert "check_sparse_graph_startup.py" in _source(CONTROL / "topology-job.sh")
    assert ' control "$ART/compile-receipts"' in _source(CONTROL / "topology-job.sh")
    return {"config_differences": sorted(differences), "S107_runnable_for_review": True,
            "S108_submission_entrypoint": False}


def main():
    result = {"source": check_source(), "arms": check_arm_state()}
    cp = subprocess.run([sys.executable, "-B", str(STUDY / "test_sparse_graph_startup.py")],
                        cwd=STUDY, text=True, capture_output=True, check=True)
    result["receipt_fixtures"] = json.loads(cp.stdout)
    result["runtime_imports"] = []
    result["gpu_used"] = False
    result["state"] = "CPU_PREPARATION_CHECKS_PASS"
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
