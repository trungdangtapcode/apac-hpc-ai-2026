#!/usr/bin/env python3
"""Require three role-local full-verification receipts with one parent identity."""
import hashlib
import json
from pathlib import Path
import sys

from importlib.machinery import SourceFileLoader

_helper = SourceFileLoader("draft_fingerprint", str(Path(__file__).resolve().with_name("draft-fingerprint.py"))).load_module()
ROLES = _helper.ROLES


def check(artifact_root, parent_report_path):
    artifact_root = Path(artifact_root)
    parent_bytes = Path(parent_report_path).read_bytes()
    parent = json.loads(parent_bytes)
    expected_identity = _helper.portable_identity(parent)
    expected_parent_sha = hashlib.sha256(parent_bytes).hexdigest()
    root = artifact_root / "draft-worker-verifications"
    found = {}
    for role in ("decode-0",):
        path = root / (role + ".json")
        receipt = json.loads(path.read_text())
        if receipt.get("role") != role:
            raise ValueError("worker receipt role does not match filename: " + role)
        if receipt.get("state") != "PASS" or receipt.get("verification_state") != "PASS":
            raise ValueError("worker full-verification receipt is not PASS: " + role)
        if receipt.get("parent_report_sha256") != expected_parent_sha:
            raise ValueError("worker receipt parent report SHA-256 mismatch: " + role)
        if receipt.get("portable_identity") != expected_identity:
            raise ValueError("worker portable identity differs from parent full report: " + role)
        if not receipt.get("node_hostname"):
            raise ValueError("worker receipt lacks node hostname: " + role)
        fingerprints = receipt.get("observed_local_fingerprints", {})
        if set(fingerprints) != set(_helper.FILES):
            raise ValueError("worker receipt lacks all local fingerprints: " + role)
        for name, fingerprint in fingerprints.items():
            if set(fingerprint) != set(_helper.FINGERPRINT_FIELDS):
                raise ValueError("worker local fingerprint fields incomplete: " + role + "/" + name)
            if any(type(fingerprint[key]) is not int or fingerprint[key] < 0 for key in _helper.FINGERPRINT_FIELDS):
                raise ValueError("worker local fingerprint values malformed: " + role + "/" + name)
            if fingerprint["st_size"] != expected_identity["files"][name]["bytes"]:
                raise ValueError("worker local fingerprint size contradicts portable bytes: " + role + "/" + name)
        if receipt.get("weight_sha256_matches_publisher_lfs") is not True:
            raise ValueError("worker publisher LFS hash gate did not pass: " + role)
        if receipt.get("all_tensor_header_entries_match_retained_inventory") is not True:
            raise ValueError("worker tensor header gate did not pass: " + role)
        if receipt.get("tensor_count") != 15 or receipt.get("tensor_dtype_counts") != {"BF16": 13, "I32": 2}:
            raise ValueError("worker tensor inventory flags mismatch: " + role)
        if receipt.get("gpu_used") is not False or receipt.get("native_model_loaded") is not False:
            raise ValueError("worker receipt exceeds its CPU-only verification scope: " + role)
        found[role] = receipt
    if {p.name for p in root.glob("*.json")} != {"decode-0.json"}:
        raise ValueError("worker receipt directory contains missing or unexpected role JSON files")
    return {"state": "PASS", "parent_report_sha256": expected_parent_sha,
            "portable_identity": expected_identity,
            "roles": {role: {"state": found[role]["state"], "node_hostname": found[role]["node_hostname"]} for role in ("decode-0",)}}


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 2:
        raise SystemExit("usage: headcheck-worker-drafts.py ARTDIR FULLREPORT")
    print(json.dumps(check(argv[0], argv[1]), sort_keys=True))


if __name__ == "__main__":
    main()
