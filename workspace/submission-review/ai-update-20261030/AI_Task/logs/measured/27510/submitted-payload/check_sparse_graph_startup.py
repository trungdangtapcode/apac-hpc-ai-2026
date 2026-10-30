#!/usr/bin/env python3
"""Fail-closed CPU-only validation for sparse decode graph startup evidence."""

from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path
import re
import sys

GRAPH_BUCKETS = (1, 2, 4, 8, 16, 32, 48, 50, 52, 54, 56, 64)
COMPILE_BUCKETS = (1, 2, 4, 8, 16, 32, 48, 50, 52, 54, 56)
HOT_BUCKETS = (50, 52, 54, 56)
EXPECTED_NATIVE_SHA256 = "77b1e38dba14788800b6b6351af1b5b8a80d9e42b91b57e9484ea4561d33a48c"


def _literal_keyword(call: ast.Call, key: str):
    for item in call.keywords:
        if item.arg == key:
            try:
                return ast.literal_eval(item.value)
            except (ValueError, TypeError):
                return None
    return None


def _parse_server_args(line: str):
    marker = "server_args="
    pos = line.find(marker)
    if pos < 0:
        raise ValueError("missing server_args marker")
    expr = line[pos + len(marker):].strip()
    node = ast.parse("_record = " + expr).body[0].value
    if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name) or node.func.id != "ServerArgs":
        raise ValueError("logged object is not a ServerArgs constructor repr")
    fields = {kw.arg: ast.literal_eval(kw.value) for kw in node.keywords
              if kw.arg and kw.arg != "cuda_graph_config" and _is_literal(kw.value)}
    cfg = next((kw.value for kw in node.keywords if kw.arg == "cuda_graph_config"), None)
    if not isinstance(cfg, ast.Call):
        raise ValueError("cuda_graph_config is not represented as a constructor call")
    decode = next((kw.value for kw in cfg.keywords if kw.arg == "decode"), None)
    if not isinstance(decode, ast.Call):
        raise ValueError("decode phase config is missing")
    phase = {kw.arg: ast.literal_eval(kw.value) for kw in decode.keywords
             if kw.arg and _is_literal(kw.value)}
    fields["decode_phase"] = phase
    return fields


def _is_literal(node):
    try:
        ast.literal_eval(node)
        return True
    except (ValueError, TypeError):
        return False


def check_runtime_log(path: Path, mode: str, config: dict) -> list[str]:
    errors = []
    text = path.read_text(errors="replace")
    if "SPARSE_GRAPH_SOURCE_VERIFIED" not in text:
        errors.append("decode worker did not attest the pinned sparse-graph source hashes")
    lines = [line for line in text.splitlines() if "server_args=ServerArgs(" in line]
    if len(lines) != 1:
        errors.append(f"expected one launcher ServerArgs record, found {len(lines)}")
        return errors
    try:
        fields = _parse_server_args(lines[0])
    except (SyntaxError, ValueError, TypeError) as exc:
        errors.append(f"effective ServerArgs record could not be parsed safely: {exc}")
        return errors
    expected_compile = mode == "compile"
    for key, expected in {
        "enable_torch_compile": expected_compile,
        "torch_compile_max_bs": 56,
        "tp_size": 8,
        "ep_size": 8,
        "dp_size": 1,
        "enable_dp_attention": False,
        "disable_attn_tp_gather": False,
        "enable_two_batch_overlap": False,
        "disable_cuda_graph_padding": False,
        "moe_a2a_backend": "none",
        "moe_dense_tp_size": None,
        "max_running_requests": 256,
    }.items():
        actual = fields.get(key)
        if key not in fields or actual != expected:
            errors.append(f"effective ServerArgs {key}={actual!r}, expected {expected!r}")
    phase = fields["decode_phase"]
    if phase.get("backend") != "full" or not isinstance(phase.get("bs"), list):
        errors.append("effective decode CUDA graph config was not parseable")
    else:
        graph_max = phase.get("max_bs")
        buckets = tuple(phase["bs"])
        if graph_max != max(GRAPH_BUCKETS):
            errors.append(f"effective graph max_bs={graph_max}, expected {max(GRAPH_BUCKETS)}")
        if buckets != GRAPH_BUCKETS:
            errors.append(f"effective graph buckets={buckets}, expected {GRAPH_BUCKETS}")
    if config.get("decode_cuda_graph_batch_sizes") != list(GRAPH_BUCKETS):
        errors.append("frozen config does not contain the exact sparse graph list")
    if config.get("decode_torch_compile_max_bs") != 56:
        errors.append("frozen config compile cap is not 56")
    if config.get("decode_enable_torch_compile") != (mode == "compile"):
        errors.append("frozen config compile toggle does not match the selected arm")
    return errors


def check_receipts(receipt_dir: Path, mode: str, job_id: str, experiment_id: str, role: str):
    errors, warnings = [], []
    files = sorted(receipt_dir.glob("rank-*-pid-*.json"))
    by_rank = {}
    if not files:
        errors.append("no rank receipts")
    for path in files:
        try:
            obj = json.loads(path.read_text())
        except Exception as exc:
            errors.append(f"{path.name}: invalid JSON ({exc})")
            continue
        if obj.get("schema") != "native-qwen-torch-compile-startup-observer-v1":
            errors.append(f"{path.name}: observer schema mismatch")
            continue
        if obj.get("native_source_sha256") != EXPECTED_NATIVE_SHA256 or obj.get("module_source_sha256") != EXPECTED_NATIVE_SHA256:
            errors.append(f"{path.name}: native pinned source hash mismatch")
            continue
        if obj.get("state") not in {"RUNNING", "COMPLETE"}:
            errors.append(f"{path.name}: receipt is not current/live ({obj.get('state')})")
        if str(obj.get("job_id")) != str(job_id):
            errors.append(f"{path.name}: stale or incorrect job ID")
        if obj.get("experiment_id") != experiment_id:
            errors.append(f"{path.name}: stale or incorrect experiment ID")
        if obj.get("role") != role:
            errors.append(f"{path.name}: role mismatch")
        if obj.get("distributed_initialized_at_hook") is not True or obj.get("world_size") != 8:
            errors.append(f"{path.name}: distributed world-size-8 hook not proven")
        if not isinstance(obj.get("observer_disabled_unix"), (int, float)):
            errors.append(f"{path.name}: startup observer was not disabled after graph capture")
        if not set(GRAPH_BUCKETS).issubset(set(obj.get("observer_disabled_after_capture_shapes", []))):
            errors.append(f"{path.name}: observer disabled before all sparse graph captures")
        if obj.get("state") not in {"RUNNING", "COMPLETE"}:
            continue
        rank = obj.get("rank")
        if not isinstance(rank, int) or not 0 <= rank < 8:
            errors.append(f"{path.name}: rank outside 0..7")
            continue
        recorded_path = obj.get("receipt_path")
        if not recorded_path or Path(recorded_path).resolve() != path.resolve():
            errors.append(f"{path.name}: receipt path is not current payload path")
        if not isinstance(obj.get("updated_unix"), (int, float)) or obj["updated_unix"] <= 0:
            errors.append(f"{path.name}: missing live update timestamp")
        by_rank.setdefault(rank, []).append(obj)

    if sorted(by_rank) != list(range(8)):
        errors.append(f"expected exactly ranks 0..7, found {sorted(by_rank)}")
    for rank, rows in sorted(by_rank.items()):
        if len(rows) != 1:
            errors.append(f"rank {rank}: expected one current receipt, found {len(rows)}")
            continue
        shapes = rows[0].get("shapes", {})
        for shape in GRAPH_BUCKETS:
            entry = shapes.get(str(shape))
            if not entry or entry.get("successful_cuda_graph_captures", 0) < 1:
                errors.append(f"rank {rank}: missing real CUDA graph capture for bucket {shape}")
                continue
            expected_enabled = mode == "compile" and shape in COMPILE_BUCKETS
            if entry.get("compile_enabled_argument_seen") is not expected_enabled:
                errors.append(f"rank {rank}: compile flag for bucket {shape} is not {expected_enabled}")
            if expected_enabled:
                if entry.get("compiled_callable_materialized") is not True or entry.get("callable_invocations", 0) < 1:
                    errors.append(f"rank {rank}: compiled callable/call not proven for bucket {shape}")
        for shape in HOT_BUCKETS:
            entry = shapes.get(str(shape), {})
            if entry.get("successful_cuda_graph_captures", 0) < 1:
                errors.append(f"rank {rank}: hot bucket {shape} did not capture")
        if mode == "compile":
            positive_dynamo = any(e.get("dynamo_unique_graphs_positive") is True for e in shapes.values())
            positive_fx = any(e.get("fxgraph_cache_positive") is True for e in shapes.values())
            positive_inductor = any(
                e.get("inductor_cache_positive") is True or e.get("generated_kernel_positive") is True
                for e in shapes.values()
            )
            if not (positive_dynamo and positive_fx and positive_inductor):
                errors.append(f"rank {rank}: Dynamo, FX-cache and Inductor/kernel activity not all proven")
        else:
            warnings.append(f"rank {rank}: compile is intentionally disabled; sparse CUDA-graph captures are required")

    return {
        "state": "PASS" if not errors else "FAIL_CLOSED",
        "ready_for_aiperf": not errors,
        "mode": mode,
        "expected_world": 8,
        "job_id": str(job_id),
        "experiment_id": experiment_id,
        "role": role,
        "graph_buckets": list(GRAPH_BUCKETS),
        "compile_buckets": list(COMPILE_BUCKETS) if mode == "compile" else [],
        "hot_buckets": list(HOT_BUCKETS),
        "rank_ids": sorted(by_rank),
        "warnings": warnings,
        "errors": errors,
    }


def check(receipt_dir: Path, server_log: Path, mode: str, config_path: Path,
          job_id: str, experiment_id: str, role: str):
    config = json.loads(config_path.read_text())
    result = check_receipts(receipt_dir, mode, job_id, experiment_id, role)
    result["errors"].extend(check_runtime_log(server_log, mode, config))
    if result["errors"]:
        result["state"] = "FAIL_CLOSED"
        result["ready_for_aiperf"] = False
    return result


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("control", "compile"))
    parser.add_argument("receipt_dir", type=Path)
    parser.add_argument("server_log", type=Path)
    parser.add_argument("config", type=Path)
    parser.add_argument("--job-id", required=True)
    parser.add_argument("--experiment-id", required=True)
    parser.add_argument("--role", default="decode-0")
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args(argv)
    result = check(args.receipt_dir, args.server_log, args.mode, args.config,
                   args.job_id, args.experiment_id, args.role)
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(rendered)
    print(rendered, end="")
    return 0 if result["ready_for_aiperf"] else 2


if __name__ == "__main__":
    sys.exit(main())
