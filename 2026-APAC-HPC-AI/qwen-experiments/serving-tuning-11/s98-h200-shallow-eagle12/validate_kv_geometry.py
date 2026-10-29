#!/usr/bin/env python3
"""Fail-closed completeness and whitelist check for prospective rank receipts."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

MAX_FILES = 32
MAX_TOTAL_BYTES = 32 * 1024 * 1024
KEYS = {
    "schema", "role_name", "experiment_id", "engine_rank", "pp_rank", "gpu_rank",
    "tp_size", "page_size_tokens", "kv_head_num", "total_kv_head_num", "kv_layer_ids",
    "kv_regions", "aux_region_lengths_bytes", "state_region_lengths_bytes", "dtype",
    "tensor_strides", "phase", "registration_returned",
}
REGION_KEYS = {
    "index", "region_bytes", "item_bytes", "page_stride_bytes", "memory_kind",
    "page_count", "token_stride_bytes",
}
ROLE_RE = re.compile(r"^(?:prefill|decode)-[0-9]{1,3}$")
EXPERIMENT_RE = re.compile(r"^[A-Za-z0-9_.-]{1,128}$")
# A source-backed exception for Qwen's pinned full MHA layout. Its native
# CommonKVManager computes layer addressing from the KV pointer array and PP
# offset; kv_layer_ids may therefore be observed as [] without an ID sequence.
# This does not establish semantic layer order. All other empty/missing forms fail.
IMPLICIT_MHA_PREFILL_REGIONS = 188
IMPLICIT_MHA_DECODE_REGIONS = 188
EAGLE3_DRAFT_KV_REGIONS = 2
IMPLICIT_MHA_HEADS = 1
IMPLICIT_MHA_TOTAL_HEADS = 4
IMPLICIT_MHA_PAGE_TOKENS = 1
# decode.py assigns these fields after constructing the KV manager on this pinned
# path. Preserve the observed not_collected values; permit them only for the
# reviewed H200 D-role geometry. Its observed region count follows the explicit
# decode-draft setting below.
UNKNOWN_D_HEADS_ROLE = "decode-0"
UNKNOWN_D_HEADS_TP = 8
UNKNOWN_D_HEADS_PP = 0
UNKNOWN_D_HEADS_PAGE_TOKENS = 1
UNKNOWN_D_HEADS_ITEM_BYTES = 256
UNKNOWN_D_HEADS_TOKEN_STRIDE_BYTES = 256


def _integer(value, field, *, minimum=0, maximum=(1 << 63) - 1):
    if type(value) is not int or value < minimum or value > maximum:
        raise ValueError(f"invalid integer field {field}")
    return value


def _integer_list(value, field, *, minimum=0):
    if not isinstance(value, list) or len(value) > 8192:
        raise ValueError(f"invalid or oversized array field {field}")
    return [_integer(item, f"{field}[{index}]", minimum=minimum)
            for index, item in enumerate(value)]


def _validate_record(record, path, experiment_id, expected_roles, decode_draft):
    if not isinstance(record, dict) or set(record) != KEYS:
        raise ValueError(f"receipt has missing or unapproved fields: {path.name}")
    if record["schema"] != "h200-kv-registration-geometry-v1":
        raise ValueError(f"unknown receipt schema: {path.name}")
    role = record["role_name"]
    if not isinstance(role, str) or not ROLE_RE.fullmatch(role) or role not in expected_roles:
        raise ValueError(f"unexpected or malformed role: {path.name}")
    experiment = record["experiment_id"]
    if not isinstance(experiment, str) or not EXPERIMENT_RE.fullmatch(experiment):
        raise ValueError(f"malformed experiment identity: {path.name}")
    if experiment != experiment_id:
        raise ValueError(f"experiment identity mismatch: {path.name}")

    tp = expected_roles[role]
    if _integer(record["tp_size"], "tp_size", minimum=1) != tp:
        raise ValueError(f"TP size mismatch for {role}")
    engine = _integer(record["engine_rank"], "engine_rank")
    if engine >= tp:
        raise ValueError(f"engine rank out of range for {role}")
    pp = _integer(record["pp_rank"], "pp_rank")
    if pp != 0:
        raise ValueError(f"unexpected pipeline rank for {role}")
    gpu = _integer(record["gpu_rank"], "gpu_rank")
    if gpu >= tp:
        raise ValueError(f"GPU rank out of range for {role}")
    page_size = _integer(record["page_size_tokens"], "page_size_tokens", minimum=1)

    head_values = (record["kv_head_num"], record["total_kv_head_num"])
    unknown_d_heads = head_values == ("not_collected", "not_collected")
    if "not_collected" in head_values and not unknown_d_heads:
        raise ValueError("head fields must be jointly observed or jointly not_collected")
    if unknown_d_heads and not (
        role == UNKNOWN_D_HEADS_ROLE
        and pp == UNKNOWN_D_HEADS_PP
        and tp == UNKNOWN_D_HEADS_TP
        and page_size == UNKNOWN_D_HEADS_PAGE_TOKENS
    ):
        raise ValueError("uncollected head fields are permitted only for the pinned D-role registration path")
    for field in ("kv_head_num", "total_kv_head_num"):
        value = record[field]
        if value != "not_collected":
            _integer(value, field, minimum=1)
    layers = record["kv_layer_ids"]
    if not isinstance(layers, list):
        raise ValueError("KV layer IDs must be an observed list, including the pinned empty-list form")
    layer_ids = _integer_list(layers, "kv_layer_ids")
    observed_empty_layer_ids = not layer_ids
    if observed_empty_layer_ids and not (
        (record["kv_head_num"] == IMPLICIT_MHA_HEADS
         and record["total_kv_head_num"] == IMPLICIT_MHA_TOTAL_HEADS
         and page_size == IMPLICIT_MHA_PAGE_TOKENS)
        or unknown_d_heads
    ):
        raise ValueError("empty KV layer IDs are permitted only for the pinned Qwen MHA signature or exact D-role unknown-head exception")

    regions = record["kv_regions"]
    if not isinstance(regions, list) or not regions or len(regions) > 8192:
        raise ValueError(f"full-model geometry requires a nonempty bounded KV region list: {path.name}")
    expected_decode_regions = IMPLICIT_MHA_DECODE_REGIONS + (
        EAGLE3_DRAFT_KV_REGIONS if decode_draft else 0
    )
    if observed_empty_layer_ids:
        if role.startswith("prefill-"):
            expected_region_count = IMPLICIT_MHA_PREFILL_REGIONS
        else:
            expected_region_count = expected_decode_regions
        if len(regions) != expected_region_count:
            raise ValueError(
                f"empty KV layer IDs require {expected_region_count} pinned MHA KV regions "
                f"for role={role} decode_draft={decode_draft}"
            )
    if unknown_d_heads and len(regions) != expected_decode_regions:
        raise ValueError(f"uncollected D-role heads require {expected_decode_regions} pinned KV regions")
    for index, region in enumerate(regions):
        if not isinstance(region, dict) or set(region) != REGION_KEYS:
            raise ValueError(f"invalid KV region fields for {role} rank {engine}")
        if _integer(region["index"], "region.index") != index:
            raise ValueError(f"noncanonical KV region index for {role} rank {engine}")
        region_bytes = _integer(region["region_bytes"], "region.region_bytes", minimum=1)
        item_bytes = _integer(region["item_bytes"], "region.item_bytes", minimum=1)
        if region_bytes < item_bytes:
            raise ValueError(f"region is shorter than one item for {role} rank {engine}")
        if _integer(region["page_stride_bytes"], "region.page_stride_bytes", minimum=1) != item_bytes:
            raise ValueError(f"page stride does not match item size for {role} rank {engine}")
        if unknown_d_heads and (
            region["memory_kind"] != "VRAM"
            or item_bytes != UNKNOWN_D_HEADS_ITEM_BYTES
            or region["page_stride_bytes"] != UNKNOWN_D_HEADS_ITEM_BYTES
            or region["token_stride_bytes"] != UNKNOWN_D_HEADS_TOKEN_STRIDE_BYTES
        ):
            raise ValueError("uncollected D-role heads require 190 VRAM regions with 256-byte item/page/token strides")
        if not isinstance(region["memory_kind"], str) or region["memory_kind"] not in {"VRAM", "DRAM"}:
            raise ValueError(f"invalid memory kind for {role} rank {engine}")
        expected_pages = region_bytes // item_bytes if region_bytes % item_bytes == 0 else "not_collected"
        expected_token_stride = item_bytes // page_size if item_bytes % page_size == 0 else "not_collected"
        if type(expected_pages) is int:
            actual_pages = _integer(region["page_count"], "region.page_count", minimum=1)
        elif type(region["page_count"]) is str:
            actual_pages = region["page_count"]
        else:
            raise ValueError(f"invalid page count type for {role} rank {engine}")
        if actual_pages != expected_pages:
            raise ValueError(f"incorrect page count or divisibility marker for {role} rank {engine}")
        if type(expected_token_stride) is int:
            actual_token_stride = _integer(region["token_stride_bytes"], "region.token_stride_bytes", minimum=1)
        elif type(region["token_stride_bytes"]) is str:
            actual_token_stride = region["token_stride_bytes"]
        else:
            raise ValueError(f"invalid token stride type for {role} rank {engine}")
        if actual_token_stride != expected_token_stride:
            raise ValueError(f"incorrect token stride or divisibility marker for {role} rank {engine}")

    _integer_list(record["aux_region_lengths_bytes"], "aux_region_lengths_bytes")
    state = record["state_region_lengths_bytes"]
    if not isinstance(state, list) or len(state) > 8192:
        raise ValueError("invalid or oversized state component array")
    state_count = 0
    for component, row in enumerate(state):
        lengths = _integer_list(row, f"state_region_lengths_bytes[{component}]")
        state_count += len(lengths)
        if state_count > 8192:
            raise ValueError("state region lengths exceed the total region limit")

    if record["dtype"] != "not_collected" or record["tensor_strides"] != "not_collected":
        raise ValueError("dtype and tensor strides must remain explicitly not_collected")
    key = (role, engine, pp)
    phase = record["phase"]
    if phase not in {"before", "after"}:
        raise ValueError(f"invalid phase for {key}")
    returned = record["registration_returned"]
    if (phase == "before" and returned is not None) or (phase == "after" and returned is not True):
        raise ValueError(f"registration did not pass for {key} phase {phase}")
    return key, phase, record


def validate(directory: Path, expected_roles: dict[str, int], experiment_id: str, decode_draft: bool) -> dict:
    if expected_roles != {"prefill-0": 4, "prefill-1": 4, "decode-0": 8}:
        raise ValueError("expected role inventory must match the reviewed TP4/TP4/TP8 topology")
    if not isinstance(experiment_id, str) or not EXPERIMENT_RE.fullmatch(experiment_id):
        raise ValueError("expected experiment identity is malformed")
    files = sorted(directory.glob("*.json"))
    if len(files) != MAX_FILES:
        raise ValueError(f"expected {MAX_FILES} rank receipts, found {len(files)}")
    total_bytes = 0
    grouped = {}
    for path in files:
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"receipt is not a regular file: {path.name}")
        size = path.stat().st_size
        if size <= 0 or size > 1024 * 1024:
            raise ValueError(f"receipt exceeds the per-file byte limit: {path.name}")
        total_bytes += size
        if total_bytes > MAX_TOTAL_BYTES:
            raise ValueError("receipt set exceeds total byte limit")
        record = json.loads(path.read_text())
        key, phase, record = _validate_record(record, path, experiment_id, expected_roles, decode_draft)
        if key not in grouped:
            grouped[key] = {}
        if phase in grouped[key]:
            raise ValueError(f"duplicate or invalid phase for {key}")
        grouped[key][phase] = record

    expected_keys = {
        (role, rank, 0)
        for role, tp in expected_roles.items()
        for rank in range(tp)
    }
    if set(grouped) != expected_keys:
        missing = sorted(expected_keys - set(grouped))
        extra = sorted(set(grouped) - expected_keys)
        raise ValueError(f"rank inventory mismatch; missing={missing}, extra={extra}")
    for key, phases in grouped.items():
        if set(phases) != {"before", "after"}:
            raise ValueError(f"incomplete before/after receipt pair for {key}")
        before = {k: v for k, v in phases["before"].items() if k not in {"phase", "registration_returned"}}
        after = {k: v for k, v in phases["after"].items() if k not in {"phase", "registration_returned"}}
        if before != after:
            raise ValueError(f"geometry changed across native registration for {key}")
    return {
        "schema": "h200-kv-geometry-validation-v1",
        "experiment_id": experiment_id,
        "rank_count": len(expected_keys),
        "receipt_count": len(files),
        "receipt_bytes": total_bytes,
        "layer_identity": "observed_empty; explicit IDs not collected; semantic layer order unproven",
        "observed_prefill_mha_signature": {
            "role_scope": ["prefill-0", "prefill-1"],
            "kv_regions_per_rank": IMPLICIT_MHA_PREFILL_REGIONS,
            "kv_head_num": IMPLICIT_MHA_HEADS,
            "total_kv_head_num": IMPLICIT_MHA_TOTAL_HEADS,
            "page_size_tokens": IMPLICIT_MHA_PAGE_TOKENS,
        },
        "unknown_d_heads_exception": {
            "role": UNKNOWN_D_HEADS_ROLE,
            "engine_ranks": "0-7; each remains individually receipt-gated",
            "tp_size": UNKNOWN_D_HEADS_TP,
            "pp_rank": UNKNOWN_D_HEADS_PP,
            "page_size_tokens": UNKNOWN_D_HEADS_PAGE_TOKENS,
            "kv_regions": IMPLICIT_MHA_DECODE_REGIONS + (EAGLE3_DRAFT_KV_REGIONS if decode_draft else 0),
            "memory_kind": "VRAM",
            "item_page_token_stride_bytes": UNKNOWN_D_HEADS_ITEM_BYTES,
            "observed_heads": "not_collected; not inferred or fabricated",
        },
        "decode_draft_regions": {
            "enabled": decode_draft,
            "target_model_regions_per_rank": IMPLICIT_MHA_DECODE_REGIONS,
            "additional_draft_regions_per_rank": EAGLE3_DRAFT_KV_REGIONS if decode_draft else 0,
            "observed_regions_per_rank": IMPLICIT_MHA_DECODE_REGIONS + (EAGLE3_DRAFT_KV_REGIONS if decode_draft else 0),
        },
        "passed": True,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("receipt_dir", type=Path)
    parser.add_argument("--experiment-id", required=True)
    parser.add_argument("--expected-role", action="append", default=[], metavar="NAME=TP")
    parser.add_argument("--decode-draft", choices=("0", "1"), required=True)
    args = parser.parse_args()
    roles = {}
    for value in args.expected_role:
        name, separator, size = value.partition("=")
        if not separator or name in roles or not size.isdecimal():
            parser.error(f"invalid --expected-role {value!r}")
        roles[name] = int(size)
    print(json.dumps(validate(args.receipt_dir, roles, args.experiment_id, args.decode_draft == "1"), sort_keys=True))


if __name__ == "__main__":
    main()
