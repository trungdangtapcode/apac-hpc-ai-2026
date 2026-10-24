#!/usr/bin/env python3
"""Strict actual four-rank H100 prefill readiness and metadata-observer gate."""

from __future__ import annotations

import ast
import hashlib
import json
import re
import sys
from pathlib import Path


UTILS_SHA256 = "db1b6285e08a6949632d9347f546e1cb290359ca4ad077a1a204af19547caf82"
NIXL_SHA256 = "912b7edb95b03604354cc0137f111756ed5bb0eaa91345e713afa53b5bf5024f"
DRAFT_SHA256 = "bf226a966868fe413a22e62e471aa1130bd94f17fd2c40d322b1c8b4def1ae86"
TARGET = "/scratch/users/industry/ai-hpc/apacsc42/qwen-assets/Qwen3-235B-A22B-Instruct-2507-FP8"
DRAFT = "/scratch/users/industry/ai-hpc/apacsc42/qwen-assets/drafts/nebius-eagle3-qwen235b-ff0f0c09"
EXPECTED_RANKS = {0, 1, 2, 3}


def parse_server_args(text: str) -> dict:
    lines = [line.split("server_args=ServerArgs(", 1)[1]
             for line in text.splitlines() if "server_args=ServerArgs(" in line]
    if len(lines) != 1:
        return {"passed": False, "reason": f"expected one ServerArgs line, got {len(lines)}"}
    try:
        node = ast.parse("ServerArgs(" + lines[0], mode="eval").body
        if not isinstance(node, ast.Call):
            raise ValueError("ServerArgs line is not a call")
        keys = {"model_path", "tp_size", "dtype", "context_length", "chunked_prefill_size",
                "moe_runner_backend", "speculative_algorithm", "speculative_draft_model_path",
                "speculative_num_steps", "speculative_eagle_topk", "speculative_num_draft_tokens",
                "speculative_draft_model_quantization", "disaggregation_mode",
                "disaggregation_transfer_backend", "mem_fraction_static"}
        observed = {kw.arg: ast.literal_eval(kw.value) for kw in node.keywords if kw.arg in keys}
    except (SyntaxError, TypeError, ValueError) as exc:
        return {"passed": False, "reason": f"cannot parse resolved args: {type(exc).__name__}"}
    expected = {"model_path": TARGET, "tp_size": 4, "dtype": "bfloat16", "context_length": 8192,
                "chunked_prefill_size": 4096, "moe_runner_backend": "hpc_ops",
                "speculative_algorithm": "EAGLE3", "speculative_draft_model_path": DRAFT,
                "speculative_num_steps": 2, "speculative_eagle_topk": 1,
                "speculative_num_draft_tokens": 3, "speculative_draft_model_quantization": None,
                "disaggregation_mode": "prefill", "disaggregation_transfer_backend": "nixl",
                "mem_fraction_static": 0.9}
    return {"passed": observed == expected, "observed": observed, "expected": expected}


def validate_receipts(art: Path) -> dict:
    root = art / "pd-observer"
    files = sorted(root.rglob("metadata.json"))
    if len(files) != 4:
        raise ValueError(f"expected exactly four actual metadata receipts; found {len(files)}")
    records = {}
    for path in files:
        if path.is_symlink() or path.stat().st_size <= 0 or path.stat().st_size > 1024 * 1024:
            raise ValueError(f"invalid metadata receipt file: {path}")
        row = json.loads(path.read_text(encoding="utf-8"))
        allowed = {"schema", "role", "role_kind", "tp_rank", "rank_source", "ordered_names",
                   "tensor_count", "total_row_count", "ptr_list_count", "lens_list_count",
                   "item_lens_list_count", "total_bytes", "original_ptrs_equal_tensor_data_ptrs",
                   "original_lens_equal_tensor_nbytes", "original_item_lens_equal_tensor_row_nbytes",
                   "rows", "recorded_unix_ns"}
        if set(row) - allowed:
            raise ValueError(f"unexpected metadata receipt fields (possible raw data): {path}")
        rank = row.get("tp_rank")
        if row.get("schema") != "eagle3-pd-metadata-v1" or row.get("role") != "prefill-0":
            raise ValueError(f"wrong prefill metadata identity: {path}")
        if type(rank) is not int or rank not in EXPECTED_RANKS or rank in records:
            raise ValueError(f"invalid or duplicate prefill TP rank: {path}")
        if row.get("rank_source") != "initialized sglang.srt.distributed.get_tp_group().rank":
            raise ValueError("metadata TP rank is not the initialized SGLang TP-group rank")
        names, rows = row.get("ordered_names"), row.get("rows")
        if not isinstance(rows, list) or not rows or names != [r.get("name") for r in rows]:
            raise ValueError(f"missing or contradictory ordered tensor names: {path}")
        if row.get("tensor_count") != len(rows) or row.get("ptr_list_count") != len(rows) \
                or row.get("lens_list_count") != len(rows) or row.get("item_lens_list_count") != len(rows):
            raise ValueError(f"metadata list/tensor counts differ: {path}")
        if not all(row.get(k) is True for k in (
                "original_ptrs_equal_tensor_data_ptrs", "original_lens_equal_tensor_nbytes",
                "original_item_lens_equal_tensor_row_nbytes")):
            raise ValueError(f"original metadata lists do not match the actual tensors: {path}")
        for tensor in rows:
            if not isinstance(tensor.get("name"), str) or not tensor["name"]:
                raise ValueError(f"invalid metadata tensor name at rank {rank}")
            shape, strides = tensor.get("shape"), tensor.get("strides")
            width, item_len, count = tensor.get("row_nbytes"), tensor.get("item_len"), tensor.get("row_count")
            nbytes, dtype = tensor.get("nbytes"), tensor.get("dtype")
            if (not isinstance(shape, list) or not shape or not isinstance(strides, list)
                    or len(shape) != len(strides) or any(type(x) is not int or x < 0 for x in shape)
                    or any(type(x) is not int or x < 0 for x in strides)
                    or type(width) is not int or width <= 0
                    or item_len != width or type(count) is not int or count <= 0 or shape[0] != count):
                raise ValueError(f"invalid measured tensor row schema at rank {rank}")
            if type(nbytes) is not int or nbytes <= 0 or not isinstance(dtype, str) or not dtype:
                raise ValueError(f"invalid tensor byte count/dtype at rank {rank}")
        if row.get("total_bytes") != sum(t["nbytes"] for t in rows):
            raise ValueError(f"metadata total byte count differs from tensor rows: {path}")
        if row.get("total_row_count") != sum(t["row_count"] for t in rows):
            raise ValueError(f"metadata total row count differs from tensor rows: {path}")
        records[rank] = row
    if set(records) != EXPECTED_RANKS:
        raise ValueError(f"incomplete prefill rank set: {sorted(records)}")
    names = [records[0]["ordered_names"]]
    widths = [[(r["name"], r["row_nbytes"], r["dtype"]) for r in records[0]["rows"]]]
    for rank in sorted(EXPECTED_RANKS - {0}):
        if records[rank]["ordered_names"] != names[0]:
            raise ValueError(f"prefill TP rank {rank} ordered names differ")
        actual = [(r["name"], r["row_nbytes"], r["dtype"]) for r in records[rank]["rows"]]
        if actual != widths[0]:
            raise ValueError(f"prefill TP rank {rank} measured widths/dtypes differ")
    reports = sorted((root / "source-modules" / "prefill-0").glob("*.json"))
    if {p.name for p in reports} != {"utils.json", "conn.json"}:
        raise ValueError("expected exactly the actual utils and patched NIXL source reports")
    module_hashes = {"utils": UTILS_SHA256, "conn": NIXL_SHA256}
    for path in reports:
        item = json.loads(path.read_text(encoding="utf-8"))
        short = path.stem
        module = ("sglang.srt.disaggregation.utils" if short == "utils"
                  else "sglang.srt.disaggregation.nixl.conn")
        if (item.get("schema") != "eagle3-pd-source-module-v1"
                or item.get("role") != "prefill-0" or item.get("module") != module
                or item.get("sha256") != module_hashes[short]):
            raise ValueError(f"actual source module hash mismatch: {path}")
    return {"passed": True, "role": "prefill-0", "tp_size": 4,
            "receipt_count": len(records), "rank_set": sorted(records),
            "ordered_names": names[0], "measured_widths_and_dtypes": widths[0],
            "observed_row_counts_by_rank": {str(rank): [r["row_count"] for r in records[rank]["rows"]]
                                             for rank in sorted(records)},
            "source_module_sha256": module_hashes,
            "cross_rank_names_widths_dtypes_match": True}


def inspect(art: Path, ready: bool, experiment_id: str, job_id: str, context_path: Path) -> dict:
    text = (art / "prefill.log").read_text(encoding="utf-8", errors="replace")
    context = json.loads(context_path.read_text(encoding="utf-8"))
    context_ok = (context.get("experiment_id") == experiment_id and context.get("pbs_job_id") == job_id
                  and type(context.get("t0_epoch_seconds")) is int
                  and context.get("startup_deadline_epoch_seconds") == context["t0_epoch_seconds"] + 720
                  and context.get("check_deadline_epoch_seconds") == context["t0_epoch_seconds"] + 780
                  and context.get("cleanup_deadline_epoch_seconds") == context["t0_epoch_seconds"] + 840)
    rank_dtypes = {str(i): [] for i in EXPECTED_RANKS}
    kv_records = re.findall(r"TP(\d+)\].*KV Cache is allocated\. dtype: ([^, ]+)", text)
    for rank, dtype in kv_records:
        if rank in rank_dtypes:
            rank_dtypes[rank].append(dtype)
    graph_disabled = re.findall(r"TP(\d+)\].*Disable prefill CUDA graph.*resolved prefill\.backend='disabled'", text)
    nixl_init = re.findall(r"TP(\d+)\] NIXL KVManager initialized with backend: UCX", text)
    graph_captures = re.findall(r"Capture (?:target|draft) prefill CUDA graph begin", text)
    fatal = [line for line in text.splitlines()
             if re.search(r"Traceback|RuntimeError:|OutOfMemoryError:|NIXL_ERR_", line)]
    args = parse_server_args(text)
    receipts = None
    receipt_error = None
    try:
        receipts = validate_receipts(art)
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        receipt_error = f"{type(exc).__name__}: {exc}"
    status_path = art / "health-status.txt"
    health = status_path.read_text().strip() if status_path.exists() else "MISSING"
    proof = {
        "experiment_context_verified": context_ok,
        "http_health_status": health,
        "server_ready_log": "The server is fired up and ready to roll!" in text,
        "h100_runtime_verified": "H100_RUNTIME_VERIFIED" in text,
        "native_graph_source_verified": "NATIVE_GRAPH_SOURCE_VERIFIED" in text,
        "pinned_draft_sha256_verified": f"PINNED_DRAFT_VERIFIED {DRAFT_SHA256}" in text,
        "nixl_source_sha256_verified": f"NIXL_PATCH_VERIFIED {NIXL_SHA256}" in text,
        "hpc_ops_preflight_passed": "HPC_OPS_PREFLIGHT_PASSED" in text,
        "resolved_prefill_server_config": args,
        "bf16_kv_allocations_by_rank": rank_dtypes,
        "prefill_graph_disabled_messages_by_rank": {r: graph_disabled.count(r) for r in sorted(rank_dtypes)},
        "nixl_initialization_count_by_rank": {r: nixl_init.count(r) for r in sorted(rank_dtypes)},
        "unexpected_rank_labels": sorted((set(rank for rank, _ in kv_records) | set(graph_disabled) | set(nixl_init)) - set(rank_dtypes)),
        "prefill_graph_capture_started": bool(graph_captures),
        "fatal_runtime_lines": fatal[:12],
        "metadata_observer": receipts,
        "metadata_observer_error": receipt_error,
    }
    passed = all((context_ok, ready, health == "200", proof["server_ready_log"],
        proof["h100_runtime_verified"], proof["native_graph_source_verified"],
        proof["pinned_draft_sha256_verified"], proof["nixl_source_sha256_verified"],
        proof["hpc_ops_preflight_passed"], args["passed"], not fatal,
        not proof["unexpected_rank_labels"], not proof["prefill_graph_capture_started"],
        all(rank_dtypes[r] == ["torch.bfloat16", "torch.bfloat16"] for r in rank_dtypes),
        len(kv_records) == 8,
        all(proof["prefill_graph_disabled_messages_by_rank"][r] == 2 for r in rank_dtypes),
        len(graph_disabled) == 8,
        all(proof["nixl_initialization_count_by_rank"][r] == 1 for r in rank_dtypes),
        len(nixl_init) == 4, receipts is not None))
    return {"schema": "h100-observer-prefill-preflight-v1", "passed": passed,
            "experiment_id": experiment_id, "pbs_job_id": job_id,
            "proof": proof,
            "scope": "One actual TP4 H100 EAGLE3 prefill readiness and four actual MetadataBuffers receipts only; no decoder, P/D transport, output client, correctness equivalence, or performance score."}


def main() -> int:
    if len(sys.argv) != 6:
        raise SystemExit("usage: check_prefill_observer.py ART READY EXPERIMENT_ID PBS_JOB_ID CONTEXT_JSON")
    art = Path(sys.argv[1])
    result = inspect(art, sys.argv[2] == "1", sys.argv[3], sys.argv[4], Path(sys.argv[5]))
    with (art / "prefill-observer-preflight.json").open("x", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
        f.write("\n")
    print(json.dumps({"passed": result["passed"], "receipt_count": (result["proof"]["metadata_observer"] or {}).get("receipt_count"),
                      "health": result["proof"]["http_health_status"]}, sort_keys=True))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
