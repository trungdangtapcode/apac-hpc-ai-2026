#!/usr/bin/env python3
"""Replay source-backed geometry metadata from the failed H100 validator probe."""
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PAYLOAD = ROOT / "payload"
EVIDENCE = Path("/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-review-223788-20261023")
RECEIPTS = EVIDENCE / "geometry-source-records.json"
EXPECTED_RECEIPTS_SHA256 = "19beb2149fd9fe9cf2e4aff2636dc47cad68a920f77a5ffa1cf4843acddefdd2"
EXPECTED_COLLECTION_SHA256 = "372ff2c7935de2bd7f6813c3cb3adb1273013c53ba2e42422bb2cfdd9661edfe"
EXPECTED_COUNT = 8


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def replay():
    if sha256(RECEIPTS) != EXPECTED_RECEIPTS_SHA256:
        raise ValueError("geometry-source-records manifest digest mismatch")
    collection_manifest = EVIDENCE / "collected" / "evidence-sha256.json"
    if sha256(collection_manifest) != EXPECTED_COLLECTION_SHA256:
        raise ValueError("collected evidence hash manifest digest mismatch")
    spec = importlib.util.spec_from_file_location("candidate_geometry_validator", PAYLOAD / "validate_kv_geometry.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    records = json.loads(RECEIPTS.read_text())
    if not isinstance(records, list) or len(records) != EXPECTED_COUNT:
        raise ValueError("expected exactly eight source geometry receipts")
    experiment = "ap42-e3-h100-geometry-223788.pbs111-ff7fef9bdf124ffa8d1eec392ac1d78e"
    roles = {"prefill-0": 4}
    paired = {}
    for entry in records:
        path = Path(entry["path"])
        if sha256(path) != entry["sha256"]:
            raise ValueError(f"source receipt hash mismatch: {path.name}")
        record = json.loads(path.read_text())
        key, phase, validated = module._validate_record(record, path, experiment, roles)
        if len(validated["kv_regions"]) != 190:
            raise ValueError("source receipt does not contain exactly 190 KV regions")
        if validated["kv_layer_ids"] != []:
            raise ValueError("source receipt did not preserve observed empty layer IDs")
        phases = paired.setdefault(key, {})
        if phase in phases:
            raise ValueError(f"duplicate source receipt phase: {key} {phase}")
        phases[phase] = validated
    if len(paired) != 4 or any(set(phases) != {"before", "after"} for phases in paired.values()):
        raise ValueError("source evidence must cover before/after receipts for all four ranks")
    for key, phases in paired.items():
        before = {k: v for k, v in phases["before"].items() if k not in {"phase", "registration_returned"}}
        after = {k: v for k, v in phases["after"].items() if k not in {"phase", "registration_returned"}}
        if before != after:
            raise ValueError(f"source geometry changed across registration: {key}")
    return {"state": "PASS", "receipt_count": len(records), "rank_count": len(paired),
            "regions_per_rank": 190, "observed_layer_ids": [],
            "semantic_layer_order": "unproven", "transfer_claim": False}


if __name__ == "__main__":
    print(json.dumps(replay(), sort_keys=True))
