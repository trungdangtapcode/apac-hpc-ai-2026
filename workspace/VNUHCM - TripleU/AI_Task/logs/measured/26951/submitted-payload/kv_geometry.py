#!/usr/bin/env python3
"""Bounded, redacted NIXL KV registration geometry receipts."""

from __future__ import annotations

import json
import numbers
import os
import re
import tempfile
import uuid
from pathlib import Path

MAX_REGIONS = 8192
MAX_NESTED_REGIONS = 8192
MAX_RECEIPT_BYTES = 1024 * 1024
MAX_INT = (1 << 63) - 1
_ROLE_NAME = re.compile(r"^(?:prefill|decode)-[0-9]{1,3}$")
_EXPERIMENT = re.compile(r"^[A-Za-z0-9_.-]{1,128}$")


def _int(value, field, *, minimum=0):
    if isinstance(value, bool):
        raise ValueError(f"{field} must be an integer")
    if not isinstance(value, numbers.Integral):
        raise ValueError(f"{field} must be an integer")
    try:
        parsed = int(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"{field} must be an integer") from exc
    if parsed != value or parsed < minimum or parsed > MAX_INT:
        raise ValueError(f"{field} is out of range")
    return parsed


def _flat_ints(value, field, *, positive=False):
    if value is None or isinstance(value, (str, bytes, bytearray)):
        raise ValueError(f"{field} must be a finite sequence")
    try:
        values = list(value)
    except TypeError as exc:
        raise ValueError(f"{field} must be a finite sequence") from exc
    if len(values) > MAX_REGIONS:
        raise ValueError(f"{field} exceeds the region limit")
    minimum = 1 if positive else 0
    return [_int(item, f"{field}[{index}]", minimum=minimum) for index, item in enumerate(values)]


def _optional_positive(obj, name):
    value = getattr(obj, name, None)
    if value is None:
        return "not_collected"
    return _int(value, name, minimum=1)


def _nested_ints(value, field):
    if value is None:
        return []
    if isinstance(value, (str, bytes, bytearray)):
        raise ValueError(f"{field} must be a nested sequence")
    try:
        rows = list(value)
    except TypeError as exc:
        raise ValueError(f"{field} must be a nested sequence") from exc
    if len(rows) > MAX_REGIONS:
        raise ValueError(f"{field} exceeds the component limit")
    result = []
    total = 0
    for index, row in enumerate(rows):
        parsed = _flat_ints(row, f"{field}[{index}]")
        total += len(parsed)
        if total > MAX_NESTED_REGIONS:
            raise ValueError(f"{field} exceeds the nested region limit")
        result.append(parsed)
    return result


def _sequence(value, field):
    if value is None or isinstance(value, (str, bytes, bytearray)):
        raise ValueError(f"{field} must be a finite sequence")
    try:
        result = list(value)
    except TypeError as exc:
        raise ValueError(f"{field} must be a finite sequence") from exc
    if len(result) > MAX_REGIONS:
        raise ValueError(f"{field} exceeds the region limit")
    return result


def snapshot(manager):
    """Return only the reviewed geometry whitelist; never serialize pointers."""
    args = manager.kv_args
    server_args = manager.server_args
    role_name = os.environ.get("QWEN_ROLE_NAME", "")
    experiment = os.environ.get("QWEN_EXPERIMENT_ID", "")
    if not _ROLE_NAME.fullmatch(role_name):
        raise ValueError("QWEN_ROLE_NAME is missing or invalid")
    if not _EXPERIMENT.fullmatch(experiment):
        raise ValueError("QWEN_EXPERIMENT_ID is missing or invalid")

    engine_rank = _int(getattr(args, "engine_rank", None), "engine_rank")
    pp_rank = _int(getattr(args, "pp_rank", None), "pp_rank")
    gpu_rank = _int(getattr(args, "gpu_id", None), "gpu_id")
    tp_size = _int(getattr(server_args, "tp_size", None), "tp_size", minimum=1)
    page_size = _int(getattr(args, "page_size", None), "page_size", minimum=1)

    ptrs = _sequence(getattr(args, "kv_data_ptrs", None), "kv_data_ptrs")
    lengths = _flat_ints(getattr(args, "kv_data_lens", None), "kv_data_lens", positive=True)
    item_lengths = _flat_ints(getattr(args, "kv_item_lens", None), "kv_item_lens", positive=True)
    mem_kinds = _sequence(getattr(args, "kv_data_mem_kinds", None), "kv_data_mem_kinds")
    if not (len(ptrs) == len(lengths) == len(item_lengths) == len(mem_kinds)):
        raise ValueError("KV pointer, region-length, item-length and memory-kind counts differ")
    kinds = []
    for index, kind in enumerate(mem_kinds):
        if not isinstance(kind, str) or kind not in {"VRAM", "DRAM"}:
            raise ValueError(f"kv_data_mem_kinds[{index}] is invalid")
        kinds.append(kind)

    kv_layer_ids_value = getattr(args, "kv_layer_ids", None)
    kv_layer_ids = (
        "not_collected"
        if kv_layer_ids_value is None
        else _flat_ints(kv_layer_ids_value, "kv_layer_ids")
    )
    regions = []
    for index, (region_bytes, item_bytes, kind) in enumerate(zip(lengths, item_lengths, kinds)):
        if region_bytes < item_bytes:
            raise ValueError(f"KV region {index} is shorter than one item")
        page_count = region_bytes // item_bytes if region_bytes % item_bytes == 0 else "not_collected"
        token_stride = item_bytes // page_size if item_bytes % page_size == 0 else "not_collected"
        regions.append({
            "index": index,
            "region_bytes": region_bytes,
            "item_bytes": item_bytes,
            "page_stride_bytes": item_bytes,
            "memory_kind": kind,
            "page_count": page_count,
            "token_stride_bytes": token_stride,
        })

    aux_ptrs = _sequence(getattr(args, "aux_data_ptrs", None), "aux_data_ptrs")
    aux_lengths = _flat_ints(getattr(args, "aux_data_lens", None), "aux_data_lens")
    if len(aux_ptrs) != len(aux_lengths):
        raise ValueError("auxiliary pointer and length counts differ")

    state_ptrs = _nested_ints(getattr(args, "state_data_ptrs", None), "state_data_ptrs")
    state_lengths = _nested_ints(getattr(args, "state_data_lens", None), "state_data_lens")
    if len(state_ptrs) != len(state_lengths) or any(
        len(pointer_row) != len(length_row)
        for pointer_row, length_row in zip(state_ptrs, state_lengths)
    ):
        raise ValueError("state pointer and length shapes differ")

    return {
        "schema": "h200-kv-registration-geometry-v1",
        "role_name": role_name,
        "experiment_id": experiment,
        "engine_rank": engine_rank,
        "pp_rank": pp_rank,
        "gpu_rank": gpu_rank,
        "tp_size": tp_size,
        "page_size_tokens": page_size,
        "kv_head_num": _optional_positive(args, "kv_head_num"),
        "total_kv_head_num": _optional_positive(args, "total_kv_head_num"),
        "kv_layer_ids": kv_layer_ids,
        "kv_regions": regions,
        "aux_region_lengths_bytes": aux_lengths,
        "state_region_lengths_bytes": state_lengths,
        "dtype": "not_collected",
        "tensor_strides": "not_collected",
    }


def _write_receipt(manager, phase, registration_returned):
    record = snapshot(manager)
    record["phase"] = phase
    record["registration_returned"] = registration_returned
    encoded = (json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    if len(encoded) > MAX_RECEIPT_BYTES:
        raise ValueError("geometry receipt exceeds the byte limit")
    artifact_root = os.environ.get("QWEN_ARTDIR", "")
    if not artifact_root:
        raise ValueError("QWEN_ARTDIR is missing")
    artifact_dir = Path(artifact_root)
    out_dir = artifact_dir / "kv-geometry"
    out_dir.mkdir(parents=True, exist_ok=True)
    unique = uuid.uuid4().hex
    stem = (
        f"{record['experiment_id']}-{record['role_name']}-"
        f"e{record['engine_rank']}-pp{record['pp_rank']}-gpu{record['gpu_rank']}-"
        f"{phase}-{unique}"
    )
    target = out_dir / f"{stem}.json"
    fd, temporary = tempfile.mkstemp(prefix=".geometry-", dir=out_dir)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())
        # Hard-link publication is atomic and refuses to replace an existing name.
        os.link(temporary, target)
        directory_fd = os.open(out_dir, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
    return target


def instrument_registration(manager, register):
    """Bracket exactly one native registration call without changing its result."""
    _write_receipt(manager, "before", None)
    try:
        result = register()
    except BaseException:
        try:
            _write_receipt(manager, "after", False)
        except BaseException:
            # Preserve the native registration exception; the missing after receipt
            # causes the separate diagnostic completeness gate to fail closed.
            pass
        raise
    _write_receipt(manager, "after", True)
    return result
