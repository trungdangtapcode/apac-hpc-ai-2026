#!/usr/bin/env python3
"""Fail-closed source, rank, semantic warmup, and native-call evidence checks."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

# These two helpers are shipped under pd-observer/ with the observer payload,
# not beside this gate script. Add that exact bundle-owned directory before
# importing them so pre-warmup cannot fail with an unrelated ModuleNotFoundError.
OBSERVER_DIR = Path(__file__).resolve().parent / "pd-observer"
sys.path.insert(0, str(OBSERVER_DIR))
from validate_receipts import validate
import warmup_semantic


ROLES = ("prefill-0", "prefill-1", "decode-0")
MODULE_HASHES = {
    "utils": "db1b6285e08a6949632d9347f546e1cb290359ca4ad077a1a204af19547caf82",
    "conn": "912b7edb95b03604354cc0137f111756ed5bb0eaa91345e713afa53b5bf5024f",
}
METHODS = ("send_kvcache_slice", "send_aux")


def verify_source_reports(root: Path) -> dict:
    out = {}
    for role in ROLES:
        for short, expected_hash in MODULE_HASHES.items():
            path = root / "source-modules" / role / f"{short}.json"
            record = json.loads(path.read_text(encoding="utf-8"))
            expected_module = ("sglang.srt.disaggregation.utils" if short == "utils"
                               else "sglang.srt.disaggregation.nixl.conn")
            if (record.get("schema") != "eagle3-pd-source-module-v1"
                    or record.get("role") != role
                    or record.get("module") != expected_module
                    or record.get("sha256") != expected_hash):
                raise ValueError(f"source module report mismatch: {path}")
            out[f"{role}/{short}"] = record["sha256"]
    return out


def verify_transfer_observations(root: Path) -> dict:
    result = {}
    for role in ("prefill-0", "prefill-1"):
        events = []
        for path in sorted((root / role).glob("tp-*/transfers.jsonl")):
            for line in path.read_text(encoding="utf-8").splitlines():
                event = json.loads(line)
                if event.get("role") != role or event.get("schema") != "eagle3-pd-transfer-v1":
                    raise ValueError(f"invalid transfer event in {path}")
                events.append(event)
        for kind in METHODS:
            markers = [event.get("marker") for event in events if event.get("kind") == kind]
            if "start" not in markers or not any(m in {"returned_handle", "exception"} for m in markers):
                raise ValueError(f"missing invoked/outcome observation for {role} {kind}")
            result[f"{role}/{kind}"] = {
                "start_markers": markers.count("start"),
                "returned_handle_markers": markers.count("returned_handle"),
                "exception_markers": markers.count("exception"),
                "return_is_not_completion": True,
            }
    return result


def verify_semantic_receipts(art: Path, experiment_id: str) -> dict:
    endpoints = art / "endpoints.tsv"
    inv_hash, pairs, rows = warmup_semantic.inventory(endpoints)
    if set(rows) != set(ROLES) or len(pairs) != 2:
        raise ValueError("semantic endpoint inventory differs from the expected two-P/one-D topology")
    run_token = hashlib.sha256(experiment_id.encode()).hexdigest()[:32]
    checked = warmup_semantic.check(art / "pair-warmup-receipts", endpoints, run_token)
    if checked.get("pair_count") != 2 or checked.get("inventory_sha256") != inv_hash:
        raise ValueError("semantic warmup receipts do not independently validate both P/D paths")
    return checked


def run(art: Path, stage: str, experiment_id: str | None = None) -> dict:
    observer_root = art / "pd-observer"
    receipt_paths = sorted(observer_root.glob("*/tp-*/metadata.json"))
    if len(receipt_paths) != 16:
        raise ValueError(f"expected 16 metadata receipts before any pair warmup; found {len(receipt_paths)}")
    ranks = validate(receipt_paths)
    sources = verify_source_reports(observer_root)
    result = {"stage": stage, "rank_layout": ranks, "source_module_sha256": sources}
    if stage == "after-warmup":
        if not experiment_id:
            raise ValueError("after-warmup stage requires QWEN_EXPERIMENT_ID")
        result["semantic_receipts"] = verify_semantic_receipts(art, experiment_id)
        result["native_transfer_observations"] = verify_transfer_observations(observer_root)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", choices=("pre-warmup", "after-warmup"))
    parser.add_argument("artifact", type=Path)
    parser.add_argument("--experiment-id")
    args = parser.parse_args()
    try:
        print(json.dumps(run(args.artifact, args.stage, args.experiment_id), sort_keys=True, indent=2))
    except Exception as exc:
        print(f"OBSERVER_GATE_FAILED: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
