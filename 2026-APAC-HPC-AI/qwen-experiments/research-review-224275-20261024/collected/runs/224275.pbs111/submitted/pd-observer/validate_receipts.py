#!/usr/bin/env python3
"""Validate one complete 4-prefill + 8-decode TP metadata receipt set."""

import argparse
import json
import sys
from pathlib import Path


def validate(paths: list[Path]) -> dict:
    records = []
    for path in paths:
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError(f"cannot read metadata receipt {path}: {exc}") from exc
        if not isinstance(record, dict) or record.get("schema") != "eagle3-pd-metadata-v1":
            raise ValueError(f"invalid metadata receipt schema: {path}")
        records.append(record)

    by_role: dict[str, dict[int, dict]] = {"prefill-0": {}, "prefill-1": {}, "decode-0": {}}
    for record in records:
        role, rank = record.get("role"), record.get("tp_rank")
        if role not in by_role or isinstance(rank, bool) or not isinstance(rank, int):
            raise ValueError("invalid role or TP rank in receipt")
        if rank in by_role[role]:
            raise ValueError(f"duplicate receipt for {role} TP rank {rank}")
        by_role[role][rank] = record

    expected = {"prefill-0": set(range(4)), "prefill-1": set(range(4)), "decode-0": set(range(8))}
    for role, ranks in expected.items():
        if set(by_role[role]) != ranks:
            raise ValueError(f"incomplete {role} TP ranks: got {sorted(by_role[role])}, expected {sorted(ranks)}")

    canonical_names = None
    canonical_widths = None
    role_rows = {}
    for role, rank_records in by_role.items():
        role_names = None
        role_widths = None
        role_row_counts = set()
        for rank, record in sorted(rank_records.items()):
            rows = record.get("rows")
            if not isinstance(rows, list) or not rows:
                raise ValueError(f"{role} TP rank {rank} has no tensor rows")
            names = [row.get("name") for row in rows if isinstance(row, dict)]
            if len(names) != len(rows) or record.get("ordered_names") != names:
                raise ValueError(f"{role} TP rank {rank} has missing/contradictory ordered names")
            widths = []
            for row in rows:
                width = row.get("row_nbytes")
                item_len = row.get("item_len")
                shape = row.get("shape")
                row_count = row.get("row_count")
                if (isinstance(width, bool) or not isinstance(width, int) or width <= 0
                        or item_len != width or not isinstance(shape, list)
                        or not shape or shape[0] != row_count or row_count <= 0):
                    raise ValueError(f"{role} TP rank {rank} has invalid item width/count at {row.get('name')}")
                widths.append(width)
                role_row_counts.add(row_count)
            if not all(record.get(key) is True for key in (
                "original_ptrs_equal_tensor_data_ptrs",
                "original_lens_equal_tensor_nbytes",
                "original_item_lens_equal_tensor_row_nbytes",
            )):
                raise ValueError(f"{role} TP rank {rank} has contradictory source-list equality checks")
            if role_names is None:
                role_names, role_widths = names, widths
            elif names != role_names or widths != role_widths:
                raise ValueError(f"{role} TP ranks disagree on ordered names or measured item widths")
        if canonical_names is None:
            canonical_names, canonical_widths = role_names, role_widths
        elif role_names != canonical_names or role_widths != canonical_widths:
            raise ValueError("prefill and decode differ in ordered names or actual per-item widths")
        role_rows[role] = {"tensor_names": role_names, "item_width_bytes": role_widths,
                           "observed_row_counts": sorted(role_row_counts)}

    return {
        "schema": "eagle3-pd-metadata-validation-v1",
        "complete": True,
        "tp_geometry": {"prefill_workers": {"prefill-0": 4, "prefill-1": 4}, "decode_workers": {"decode-0": 8}},
        "receipt_count": len(records),
        "cross_role_names_and_widths_match": True,
        "role_rows": role_rows,
        "row_counts_may_differ_between_roles": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("receipts", nargs="+", type=Path,
                        help="16 metadata.json files or a pd-observer directory")
    args = parser.parse_args()
    try:
        paths = []
        for item in args.receipts:
            paths.extend(sorted(item.rglob("metadata.json")) if item.is_dir() else [item])
        if len(paths) != 16:
            raise ValueError(f"expected exactly 16 actual rank receipts before pair warmup, found {len(paths)}")
        print(json.dumps(validate(paths), indent=2, sort_keys=True))
    except ValueError as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
