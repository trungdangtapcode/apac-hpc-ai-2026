#!/usr/bin/env python3
"""Validate one actual TP4 prefill and one actual TP4 decode metadata set."""
import json
from pathlib import Path

EXPECTED = {"prefill-0": set(range(4)), "decode-0": set(range(4))}


def validate(paths: list[Path]) -> dict:
    by_role = {role: {} for role in EXPECTED}
    for path in paths:
        record = json.loads(path.read_text(encoding="utf-8"))
        if record.get("schema") != "eagle3-pd-metadata-v1":
            raise ValueError(f"invalid metadata schema: {path}")
        role, rank = record.get("role"), record.get("tp_rank")
        if role not in by_role or isinstance(rank, bool) or not isinstance(rank, int):
            raise ValueError(f"invalid role/rank in {path}")
        if rank in by_role[role]:
            raise ValueError(f"duplicate {role} TP rank {rank}")
        by_role[role][rank] = record
    for role, expected in EXPECTED.items():
        if set(by_role[role]) != expected:
            raise ValueError(f"{role} ranks {sorted(by_role[role])}, expected {sorted(expected)}")

    canonical_names = canonical_widths = None
    role_summary = {}
    for role, rank_records in by_role.items():
        role_names = role_widths = None
        row_counts = set()
        for rank, record in sorted(rank_records.items()):
            rows = record.get("rows")
            names = [row.get("name") for row in rows] if isinstance(rows, list) else []
            if not names or record.get("ordered_names") != names:
                raise ValueError(f"{role} rank {rank} has incomplete ordered names")
            widths = []
            for row in rows:
                width, item_len = row.get("row_nbytes"), row.get("item_len")
                shape, row_count = row.get("shape"), row.get("row_count")
                if (type(width) is not int or width <= 0 or item_len != width
                        or not isinstance(shape, list) or not shape or shape[0] != row_count
                        or type(row_count) is not int or row_count <= 0):
                    raise ValueError(f"{role} rank {rank} invalid width/count for {row.get('name')}")
                widths.append(width)
                row_counts.add(row_count)
            equality_fields = ("original_ptrs_equal_tensor_data_ptrs",
                               "original_lens_equal_tensor_nbytes",
                               "original_item_lens_equal_tensor_row_nbytes")
            if any(record.get(k) is not True for k in equality_fields):
                raise ValueError(f"{role} rank {rank} source-list equality check failed")
            if role_names is None:
                role_names, role_widths = names, widths
            elif (names, widths) != (role_names, role_widths):
                raise ValueError(f"{role} rank receipts disagree on names/widths")
        if canonical_names is None:
            canonical_names, canonical_widths = role_names, role_widths
        elif (role_names, role_widths) != (canonical_names, canonical_widths):
            raise ValueError("P4 and D4 actual item names or widths differ")
        role_summary[role] = {"tp_size": 4, "rank_ids": sorted(rank_records),
                              "tensor_names": role_names, "item_width_bytes": role_widths,
                              "observed_row_counts": sorted(row_counts)}
    return {"schema": "single-node-equal-tp-metadata-v1", "complete": True,
            "receipt_count": 8, "roles": role_summary,
            "cross_role_names_and_widths_match": True}


def main() -> int:
    import argparse, sys
    parser = argparse.ArgumentParser()
    parser.add_argument("receipts", type=Path)
    args = parser.parse_args()
    paths = sorted(args.receipts.rglob("metadata.json"))
    if len(paths) != 8:
        print(f"METADATA_GATE_FAILED: expected 8 rank receipts, found {len(paths)}", file=sys.stderr)
        return 1
    try:
        print(json.dumps(validate(paths), sort_keys=True, indent=2))
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"METADATA_GATE_FAILED: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
