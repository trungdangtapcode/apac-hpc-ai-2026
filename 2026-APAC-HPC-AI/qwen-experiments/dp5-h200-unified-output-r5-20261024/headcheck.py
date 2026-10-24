#!/usr/bin/env python3
"""Independent post-startup readiness gate over actual observer and health files."""

import argparse
import json
import sys
from pathlib import Path


EXPECTED_RANKS = set(range(5))
BF16 = {"bf16", "bfloat16", "torch.bfloat16"}


def read_events(observer_dir: Path) -> list[dict]:
    events = []
    for path in sorted(observer_dir.glob("observer-*.jsonl")):
        for line_no, line in enumerate(path.read_text().splitlines(), 1):
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid observer JSON {path.name}:{line_no}: {exc}") from exc
    if not events:
        raise ValueError("no observer JSONL records were produced")
    return events


def one_per_rank(events: list[dict], event_name: str) -> dict[int, dict]:
    rows = [item for item in events if item.get("event") == event_name]
    by_rank = {int(item["rank"]): item for item in rows if "rank" in item}
    if set(by_rank) != EXPECTED_RANKS or len(rows) != 5:
        raise ValueError(f"{event_name}: expected exactly one row for ranks 0..4; got {sorted(by_rank)} count={len(rows)}")
    return by_rank


def validate(out: Path) -> dict:
    for filename in ("health-status.txt", "devices.json", "model-header-preflight.json"):
        path = out / filename
        if not path.is_file() or not path.stat().st_size:
            raise ValueError(f"required readiness evidence is missing or empty: {filename}")
    if not (out / "health.json").is_file() or "HEALTH_HTTP=200" not in (out / "health-status.txt").read_text().splitlines():
        raise ValueError("native health HTTP 200 receipt missing (the response body may be empty)")
    devices = json.loads((out / "devices.json").read_text())
    if devices.get("status") != "PASS_ASSIGNED_CUDA_DEVICES" or devices.get("torch_cuda_device_count") != 5:
        raise ValueError("assigned-device preflight did not pass for five CUDA devices")
    if len({item.get("uuid") for item in devices.get("devices", [])}) != 5:
        raise ValueError("assigned-device preflight did not retain five unique UUIDs")
    header = json.loads((out / "model-header-preflight.json").read_text())
    if header.get("status") != "PASS_HEADER_ONLY" or header.get("tensor_payload_read") is not False:
        raise ValueError("model header-only preflight did not pass")

    events = read_events(out / "observer")
    metadata = one_per_rank(events, "expert_metadata_after_init")
    loaded = one_per_rank(events, "loaded_first_moe_expert_parameter_metadata")
    kv = one_per_rank(events, "resolved_kv_cache_config")
    for rank, row in metadata.items():
        required = {
            "tp_size": 5,
            "dp_size": 5,
            "enable_dp_attention": True,
            "enable_dp_lm_head": True,
            "attn_tp_size": 1,
            "moe_ep_size": 5,
            "moe_tp_size": 1,
            "logical_experts": 128,
            "physical_experts": 130,
            "local_physical_experts": 26,
            "physical_to_logical_shape": [94, 130],
            "physical_to_logical_replicas_valid": True,
            "disaggregation_mode": "null",
            "cuda_graph_backend_prefill": "disabled",
            "cuda_graph_max_bs_decode": 4,
            "chunked_prefill_size": 2048,
        }
        if any(row.get(key) != value for key, value in required.items()):
            raise ValueError(f"rank {rank}: actual resolved geometry/map metadata mismatch")
        if row.get("tp_rank") != rank or row.get("moe_ep_rank") != rank:
            raise ValueError(f"rank {rank}: actual TP/EP rank identity mismatch")
        if "H200" not in str(row.get("device_name")) or row.get("compute_capability") != [9, 0]:
            raise ValueError(f"rank {rank}: actual runner device is not H200/SM90")
    map_hashes = {row.get("physical_to_logical_sha256") for row in metadata.values()}
    if len(map_hashes) != 1 or None in map_hashes:
        raise ValueError("actual expert map hash differs across ranks or is absent")
    if any(row.get("physical_to_logical_tail") != [[0, 1]] * 94 for row in metadata.values()):
        raise ValueError("actual expert map does not show replica tail [0,1] for each layer")
    observer_uuids = {row.get("device_uuid") for row in metadata.values()}
    assigned_uuids = {item.get("uuid") for item in devices.get("devices", [])}
    if len(observer_uuids) != 5 or observer_uuids != assigned_uuids:
        raise ValueError("rank-local device UUIDs do not match the five assigned CUDA devices")

    expected_shapes = {
        "w13_weight": (26, "torch.float8_e4m3fn", [3072, 4096]),
        "w2_weight": (26, "torch.float8_e4m3fn", [1536, 4096]),
        "w13_weight_scale_inv": (26, "torch.float32", [24, 32]),
        "w2_weight_scale_inv": (26, "torch.float32", [12, 32]),
        "hpc_ops_w13_weight_scale": (26, "torch.float32", [24, 32]),
        "hpc_ops_w2_weight_scale": (26, "torch.float32", [12, 32]),
    }
    for rank, row in loaded.items():
        if row.get("world_size") != 5 or row.get("local_experts") != 26:
            raise ValueError(f"rank {rank}: loaded expert count/world size mismatch")
        if row.get("moe_runner_backend") != "hpc_ops" or row.get("quant_method") != "Fp8MoEMethod":
            raise ValueError(f"rank {rank}: resolved MoE runner/quant method mismatch")
        if row.get("block_quant") is not True or row.get("weight_block_size") != [128, 128]:
            raise ValueError(f"rank {rank}: loaded quantization is not block FP8 128x128")
        for name, (first, dtype, dims) in expected_shapes.items():
            record = row["parameter_metadata"].get(name)
            if not record or record.get("dtype") != dtype:
                raise ValueError(f"rank {rank}: {name} runtime dtype does not match {dtype}")
            shape = record.get("shape", [])
            if len(shape) != 3 or shape[0] != first or sorted(shape[-2:]) != sorted(dims):
                raise ValueError(f"rank {rank}: {name} actual shape does not match expected expert/block geometry")

    for rank, row in kv.items():
        if row.get("world_size") != 5 or row.get("num_key_value_heads") != 4:
            raise ValueError(f"rank {rank}: actual KV head count/world size mismatch")
        dtype = str(row.get("kv_cache_dtype_str", "")).lower().replace("torch.", "")
        if dtype not in BF16:
            raise ValueError(f"rank {rank}: actual resolved KV cache dtype is {dtype}")

    hashes = {item.get("rank"): item for item in events if item.get("event") == "loaded_first_moe_expert_weight_hashes"}
    if set(hashes) != {0, 4} or len(hashes) != 2:
        raise ValueError("loaded duplicate-weight hash evidence is missing for rank0/rank4")
    left = hashes[0].get("selected_slot_hashes", {})
    right = hashes[4].get("selected_slot_hashes", {})
    pairs = [("0", "24"), ("1", "25")]
    for tensor_name in expected_shapes:
        if tensor_name not in left or tensor_name not in right:
            raise ValueError(f"loaded hash missing for {tensor_name}")
        for rank0_slot, rank4_slot in pairs:
            lh = left[tensor_name].get(rank0_slot, {}).get("sha256")
            rh = right[tensor_name].get(rank4_slot, {}).get("sha256")
            if not lh or lh != rh:
                raise ValueError(f"replica loaded bytes differ for {tensor_name} local slots {rank0_slot}/{rank4_slot}")

    return {
        "state": "D5_STARTUP_READINESS_PASS",
        "claim_scope": "startup geometry, loaded replica byte identity, runtime dtype, and native health only",
        "ranks_verified": sorted(EXPECTED_RANKS),
        "expert_map_sha256": next(iter(map_hashes)),
        "replica_slot_pairs_verified": [[0, 24], [1, 25]],
        "quant_scale_runtime_dtype": "float32",
        "kv_cache_dtype": "bfloat16",
        "kv_heads": 4,
        "generation_requests_before_readiness_gate": False,
        "performance_or_model_quality_claim": False,
        "resolved_disaggregation_mode": "null",
        "resolved_chunked_prefill_size_per_dp_rank": 2048,
        "generation_requests_before_readiness_gate": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    try:
        result = validate(args.out)
    except Exception as exc:
        print(json.dumps({"state": "D5_STARTUP_READINESS_FAIL", "reason": str(exc)}, sort_keys=True))
        return 2
    print(json.dumps(result, sort_keys=True))
    (args.out / "readiness-gate.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
