#!/usr/bin/env python3
"""Fail-closed prefill readiness and geometry gate; no explicit user serving client."""

from __future__ import annotations

import json
import ast
import re
import sys
from pathlib import Path

from validate_prefill_geometry import validate as validate_geometry

DERIVED_NIXL_SHA256 = "45096e831735362c7de5b37b485d02f1f55fc291f3f3876115f6da37aefd63b8"
PINNED_DRAFT_SHA256 = "bf226a966868fe413a22e62e471aa1130bd94f17fd2c40d322b1c8b4def1ae86"
EXPECTED_RANKS = {"0", "1", "2", "3"}
TARGET_PATH = "/scratch/users/industry/ai-hpc/apacsc42/qwen-assets/Qwen3-235B-A22B-Instruct-2507-FP8"
DRAFT_PATH = "/scratch/users/industry/ai-hpc/apacsc42/qwen-assets/drafts/nebius-eagle3-qwen235b-ff0f0c09"


def server_config(text: str) -> dict:
    lines = [line.split("server_args=", 1)[1]
             for line in text.splitlines() if "server_args=ServerArgs(" in line]
    if len(lines) != 1:
        return {"passed": False, "reason": f"expected one ServerArgs line; found {len(lines)}"}
    try:
        node = ast.parse(lines[0], mode="eval").body
        if not isinstance(node, ast.Call):
            raise ValueError("ServerArgs record is not a call")
        values = {kw.arg: ast.literal_eval(kw.value) for kw in node.keywords
                  if kw.arg in {
                      "model_path", "tp_size", "dtype", "context_length", "chunked_prefill_size",
                      "moe_runner_backend", "speculative_algorithm", "speculative_draft_model_path",
                      "speculative_num_steps", "speculative_eagle_topk", "speculative_num_draft_tokens",
                      "speculative_draft_model_quantization", "disaggregation_mode",
                      "disaggregation_transfer_backend", "mem_fraction_static"}}
    except (SyntaxError, TypeError, ValueError) as exc:
        return {"passed": False, "reason": f"cannot parse resolved ServerArgs: {type(exc).__name__}: {exc}"}
    expected = {
        "model_path": TARGET_PATH, "tp_size": 4, "dtype": "bfloat16", "context_length": 8192,
        "chunked_prefill_size": 4096, "moe_runner_backend": "hpc_ops",
        "speculative_algorithm": "EAGLE3", "speculative_draft_model_path": DRAFT_PATH,
        "speculative_num_steps": 2, "speculative_eagle_topk": 1,
        "speculative_num_draft_tokens": 3, "speculative_draft_model_quantization": None,
        "disaggregation_mode": "prefill", "disaggregation_transfer_backend": "nixl",
        "mem_fraction_static": 0.9,
    }
    return {"passed": values == expected, "observed": values,
            "expected": expected,
            "note": "The original worker passes the explicit unquantized-draft option; the retained readiness ServerArgs resolves speculative_draft_model_quantization=None. Preserve this observed runtime representation and the pinned draft bytes; do not reinterpret the field as a dtype measurement."}


def inspect(root: Path, health_status: str, readiness_loop_passed: bool,
            experiment_id: str, job_id: str, context_path: Path) -> dict:
    text = (root / "prefill.log").read_text(errors="replace")
    context = json.loads(context_path.read_text(encoding="utf-8"))
    context_ok = (context.get("experiment_id") == experiment_id
                  and context.get("pbs_job_id") == job_id
                  and isinstance(context.get("t0_epoch_seconds"), int)
                  and context.get("startup_deadline_epoch_seconds") == context.get("t0_epoch_seconds", -1) + 1100
                  and context.get("semantic_check_deadline_epoch_seconds") == context.get("t0_epoch_seconds", -1) + 1140
                  and context.get("cleanup_deadline_epoch_seconds") == context.get("t0_epoch_seconds", -1) + 1170)
    rank_records = re.findall(r"TP(\d+)\].*KV Cache is allocated\. dtype: ([^, ]+)", text)
    kv_dtypes = {rank: [] for rank in EXPECTED_RANKS}
    for rank, dtype in rank_records:
        if rank in kv_dtypes:
            kv_dtypes[rank].append(dtype)

    disabled_ranks = re.findall(
        r"TP(\d+)\].*Disable prefill CUDA graph.*resolved prefill\.backend='disabled'", text)
    nixl_ranks = re.findall(r"TP(\d+)\] NIXL KVManager initialized with backend: UCX", text)
    graph_capture = re.findall(r"Capture (?:target|draft) prefill CUDA graph begin", text)
    fatal_lines = [line for line in text.splitlines()
                   if re.search(r"Traceback|RuntimeError:|OutOfMemoryError:|Mismatched Tensor|NIXL_ERR_", line)]
    runtime_config = server_config(text)

    proof = {
        "experiment_context_verified": context_ok,
        "http_health_status": str(health_status),
        "readiness_loop_passed": bool(readiness_loop_passed),
        "server_ready_log": "The server is fired up and ready to roll!" in text,
        "native_graph_source_verified": "NATIVE_GRAPH_SOURCE_VERIFIED" in text,
        "runtime_h100_verified": "H100_RUNTIME_VERIFIED" in text,
        "draft_sha256_verified": f"PINNED_DRAFT_VERIFIED {PINNED_DRAFT_SHA256}" in text,
        "derived_nixl_source_verified": f"NIXL_PATCH_VERIFIED {DERIVED_NIXL_SHA256}" in text,
        "hpc_ops_preflight_passed": "HPC_OPS_PREFLIGHT_PASSED" in text,
        "resolved_server_config": runtime_config,
        "kv_cache_dtype_counts_by_rank": {rank: kv_dtypes[rank] for rank in sorted(kv_dtypes)},
        "disabled_prefill_graph_messages_by_rank": {
            rank: disabled_ranks.count(rank) for rank in sorted(EXPECTED_RANKS)},
        "nixl_initialization_count_by_rank": {
            rank: nixl_ranks.count(rank) for rank in sorted(EXPECTED_RANKS)},
        "unexpected_rank_labels": sorted((set(rank for rank, _ in rank_records)
                                            | set(disabled_ranks) | set(nixl_ranks)) - EXPECTED_RANKS),
        "prefill_graph_capture_started": bool(graph_capture),
        "fatal_runtime_lines": fatal_lines[:12],
    }

    geometry = None
    geometry_error = None
    try:
        geometry = validate_geometry(root / "kv-geometry", experiment_id)
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        geometry_error = f"{type(exc).__name__}: {exc}"

    kv_pass = (set(kv_dtypes) == EXPECTED_RANKS and
               all(kv_dtypes[rank] == ["torch.bfloat16", "torch.bfloat16"]
                   for rank in EXPECTED_RANKS) and len(rank_records) == 8)
    disabled_pass = (set(disabled_ranks) == EXPECTED_RANKS and
                      all(disabled_ranks.count(rank) == 2 for rank in EXPECTED_RANKS) and
                      len(disabled_ranks) == 8)
    nixl_pass = (set(nixl_ranks) == EXPECTED_RANKS and
                 all(nixl_ranks.count(rank) == 1 for rank in EXPECTED_RANKS) and
                 len(nixl_ranks) == 4)
    passed = all((
        str(health_status) == "200",
        bool(readiness_loop_passed), context_ok,
        proof["server_ready_log"], proof["native_graph_source_verified"],
        proof["runtime_h100_verified"], proof["draft_sha256_verified"],
        proof["derived_nixl_source_verified"], kv_pass, disabled_pass, nixl_pass,
        proof["hpc_ops_preflight_passed"], runtime_config["passed"],
        not proof["unexpected_rank_labels"], not proof["prefill_graph_capture_started"],
        not fatal_lines, geometry is not None,
    ))
    return {"passed": passed, "experiment_id": experiment_id,
            "proof": proof, "geometry_validation": geometry,
            "geometry_error": geometry_error,
            "pbs_job_id": job_id,
            "scope": "One native TP4 EAGLE3 prefill readiness and full-size KV registration geometry only; no explicit user-serving client or generation workload, decoder, router, PD equivalence, score, or official accuracy claim. The native /health path may internally execute a token-level check."}


def main():
    root = Path(sys.argv[1])
    status_file = root / "health-status.txt"
    status = status_file.read_text().strip() if status_file.exists() else "MISSING"
    if len(sys.argv) != 6:
        raise SystemExit("usage: check_probe.py ART READY EXPERIMENT_ID PBS_JOB_ID CONTEXT_JSON")
    readiness_loop_passed = sys.argv[2] == "1"
    experiment_id, job_id, context_path = sys.argv[3], sys.argv[4], Path(sys.argv[5])
    result = inspect(root, status, readiness_loop_passed, experiment_id, job_id, context_path)
    # Both records are created exclusively so a repeated invocation cannot replace evidence.
    with (root / "geometry-validation.json").open("x", encoding="utf-8") as f:
        json.dump(result["geometry_validation"] or {"passed": False, "error": result["geometry_error"]}, f, indent=2)
        f.write("\n")
    with (root / "probe-result.json").open("x", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
        f.write("\n")
    sys.exit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
