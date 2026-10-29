#!/usr/bin/env python3
"""Fail-closed pre-AIPerf gate for all-rank Qwen compile startup receipts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

EXPECTED_NATIVE_SHA256 = "77b1e38dba14788800b6b6351af1b5b8a80d9e42b91b57e9484ea4561d33a48c"
EXPECTED_WORLD = 8
REQUIRED_SHAPES = tuple(range(50, 55))


def check(receipts, expected_world=8, expected_job_id=None, expected_experiment_id=None, expected_role=None):
    errors, warnings = [], []
    if expected_world != EXPECTED_WORLD:
        errors.append(f"this candidate requires exactly {EXPECTED_WORLD} ranks")
    valid = []
    for path in sorted(Path(receipts).glob("rank-*-pid-*.json")):
        try:
            obj = json.loads(path.read_text())
        except Exception as exc:
            errors.append(f"{path.name}: invalid JSON ({exc})")
            continue
        if obj.get("schema") != "native-qwen-torch-compile-startup-observer-v1":
            errors.append(f"{path.name}: schema mismatch")
            continue
        if obj.get("native_source_sha256") != EXPECTED_NATIVE_SHA256 or obj.get("module_source_sha256") != EXPECTED_NATIVE_SHA256:
            errors.append(f"{path.name}: native pinned-source receipt mismatch")
            continue
        if obj.get("state") not in {"RUNNING", "COMPLETE"}:
            errors.append(f"{path.name}: receipt not live/complete ({obj.get('state')})")
            continue
        if expected_job_id is None or not obj.get("job_id") or obj.get("job_id") != str(expected_job_id):
            errors.append(f"{path.name}: stale/missing Slurm job ID")
            continue
        if expected_experiment_id is None or not obj.get("experiment_id") or obj.get("experiment_id") != expected_experiment_id:
            errors.append(f"{path.name}: stale/missing experiment ID")
            continue
        if expected_role is None or not obj.get("role") or obj.get("role") != expected_role:
            errors.append(f"{path.name}: missing/wrong role")
            continue
        if obj.get("distributed_initialized_at_hook") is not True:
            errors.append(f"{path.name}: distributed process group was not initialized at model hook")
            continue
        valid.append(obj)
    by_rank = {}
    for item in valid:
        rank = item.get("rank")
        if not isinstance(rank, int) or rank < 0:
            errors.append(f"pid {item.get('pid')}: rank unavailable at receipt time")
            continue
        by_rank.setdefault(rank, []).append(item)
    missing_ranks = sorted(set(range(expected_world)) - set(by_rank))
    if missing_ranks:
        errors.append(f"missing rank receipts: {missing_ranks}")
    unexpected = sorted(set(by_rank) - set(range(expected_world)))
    if unexpected:
        errors.append(f"unexpected rank ids: {unexpected}")
    for rank in range(expected_world):
        items = by_rank.get(rank, [])
        if not items:
            continue
        if any(item.get("world_size") != expected_world for item in items):
            errors.append(f"rank {rank}: world size receipt is not {expected_world}")
        if len(items) != 1:
            errors.append(f"rank {rank}: expected exactly one process receipt, found {len(items)}")
            continue
        shape_union = {}
        for key, value in items[0].get("shapes", {}).items():
            shape_union.setdefault(key, []).append(value)
        missing_shapes = []
        for shape in REQUIRED_SHAPES:
            entries = shape_union.get(str(shape), [])
            good = any(
                entry.get("compile_enabled_argument_seen") is True
                and entry.get("compiled_callable_materialized") is True
                and entry.get("callable_invocations", 0) > 0
                and entry.get("successful_cuda_graph_captures", 0) > 0
                for entry in entries
            )
            if not good:
                missing_shapes.append(shape)
        if missing_shapes:
            errors.append(f"rank {rank}: missing enabled/materialized/invoked/captured evidence for shapes {missing_shapes}")
        positive_fx = any(
            entry.get("fxgraph_cache_positive") is True
            for entries in shape_union.values() for entry in entries
        )
        positive_inductor = any(
            entry.get("inductor_cache_positive") is True or entry.get("generated_kernel_positive") is True
            for entries in shape_union.values() for entry in entries
        )
        positive_dynamo = any(
            entry.get("dynamo_unique_graphs_positive") is True
            for entries in shape_union.values() for entry in entries
        )
        if not (positive_fx and positive_inductor and positive_dynamo):
            errors.append(f"rank {rank}: compiler activity unproven; requires Dynamo graph + FX graph cache + Inductor cache/kernel delta")
        else:
            warnings.append(f"rank {rank}: compile activity proven from positive counters; shape-specific reuse is not proven for every shape")
    passed = not errors and len(by_rank) == expected_world
    return {"state": "PASS" if passed else "FAIL_CLOSED", "ready_for_aiperf": passed,
            "expected_world": expected_world, "required_shapes": list(REQUIRED_SHAPES),
            "expected_job_id": str(expected_job_id) if expected_job_id is not None else None,
            "expected_experiment_id": expected_experiment_id, "expected_role": expected_role,
            "receipt_count": len(valid), "rank_ids": sorted(by_rank), "warnings": warnings, "errors": errors}


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("receipt_dir", type=Path)
    parser.add_argument("--world-size", type=int, choices=[EXPECTED_WORLD], default=EXPECTED_WORLD)
    parser.add_argument("--job-id", required=True)
    parser.add_argument("--experiment-id", required=True)
    parser.add_argument("--role", required=True)
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args(argv)
    result = check(args.receipt_dir, args.world_size, args.job_id, args.experiment_id, args.role)
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(rendered)
    print(rendered, end="")
    return 0 if result["ready_for_aiperf"] else 2


if __name__ == "__main__":
    sys.exit(main())
