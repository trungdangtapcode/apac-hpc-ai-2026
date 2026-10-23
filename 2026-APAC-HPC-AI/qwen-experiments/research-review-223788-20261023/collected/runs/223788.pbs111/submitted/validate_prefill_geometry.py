#!/usr/bin/env python3
"""Validate an exact native TP4 prefill NIXL geometry receipt inventory."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from geometry_value_validator import _validate_record, MAX_TOTAL_BYTES

MAX_RECEIPT_BYTES = 1024 * 1024

EXPECTED_ROLES = {"prefill-0": 4}
EXPECTED_RECEIPTS = 8


def validate(directory: Path, experiment_id: str) -> dict:
    if directory.is_symlink() or not directory.is_dir():
        raise ValueError("geometry receipt path must be a real directory")
    children = sorted(directory.iterdir())
    if len(children) != EXPECTED_RECEIPTS:
        raise ValueError(f"expected exactly {EXPECTED_RECEIPTS} receipt files, found {len(children)}")
    if any(path.is_symlink() or not path.is_file() or path.suffix != ".json" for path in children):
        raise ValueError("receipt directory contains a symlink, non-file, or unexpected extra")

    grouped = {}
    total_bytes = 0
    receipts = []
    for path in children:
        size = path.stat().st_size
        if size <= 0 or size > MAX_RECEIPT_BYTES:
            raise ValueError(f"receipt is empty or exceeds the per-file limit: {path.name}")
        total_bytes += size
        if total_bytes > MAX_TOTAL_BYTES:
            raise ValueError("receipt set exceeds the shared total byte limit")
        record = json.loads(path.read_text(encoding="utf-8"))
        key, phase, record = _validate_record(record, path, experiment_id, EXPECTED_ROLES)
        if key in grouped and phase in grouped[key]:
            raise ValueError(f"duplicate receipt phase for {key}: {phase}")
        grouped.setdefault(key, {})[phase] = record
        receipts.append({"name": path.name, "bytes": size,
                         "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                         "role": key[0], "engine_rank": key[1], "pp_rank": key[2],
                         "phase": phase})

    expected = {("prefill-0", rank, 0) for rank in range(4)}
    if set(grouped) != expected:
        missing = sorted(expected - set(grouped))
        extra = sorted(set(grouped) - expected)
        raise ValueError(f"rank inventory mismatch; missing={missing}, extra={extra}")
    for key in sorted(expected):
        phases = grouped[key]
        if set(phases) != {"before", "after"}:
            raise ValueError(f"incomplete before/after pair for {key}")
        before = {k: v for k, v in phases["before"].items()
                  if k not in {"phase", "registration_returned"}}
        after = {k: v for k, v in phases["after"].items()
                 if k not in {"phase", "registration_returned"}}
        if before != after:
            raise ValueError(f"geometry changed across native registration for {key}")

    return {"schema": "h100-prefill-geometry-validation-v1",
            "experiment_id": experiment_id, "role_inventory": EXPECTED_ROLES,
            "rank_count": len(expected), "receipt_count": len(receipts),
            "receipt_bytes": total_bytes, "receipts": receipts, "passed": True}


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("receipt_dir", type=Path)
    parser.add_argument("--experiment-id", required=True)
    args = parser.parse_args()
    print(json.dumps(validate(args.receipt_dir, args.experiment_id), sort_keys=True))
