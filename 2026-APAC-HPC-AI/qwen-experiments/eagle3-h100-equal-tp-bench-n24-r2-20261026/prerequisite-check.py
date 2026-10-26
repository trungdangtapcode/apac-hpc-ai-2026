#!/usr/bin/env python3
"""Validate and materialize the portable accepted 224276 parent receipt."""
import argparse
import hashlib
import json
from pathlib import Path

EXPECTED_SHA256 = "9b06239b1e70d460b99623bdeea8cce0f5376025954772270cbbebd3bf3032a8"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    receipt_path = args.bundle / "prerequisites/224276/accepted-parent-observer.json"
    receipt_bytes = receipt_path.read_bytes()
    actual = hashlib.sha256(receipt_bytes).hexdigest()
    recorded = (args.bundle / "prerequisites/224276/accepted-parent-observer.sha256").read_text().strip()
    if actual != EXPECTED_SHA256 or recorded != actual:
        raise SystemExit("FATAL: portable accepted parent receipt hash mismatch")
    receipt = json.loads(receipt_bytes)
    if receipt.get("schema") != "h100-observer-prefill-preflight-v1" or receipt.get("passed") is not True:
        raise SystemExit("FATAL: parent receipt is not an accepted prefill readiness pass")
    if receipt.get("pbs_job_id") != "224276.pbs111":
        raise SystemExit("FATAL: parent receipt job ID does not match 224276.pbs111")
    proof = receipt.get("proof", {})
    metadata = proof.get("metadata_observer", {})
    observed = proof.get("resolved_prefill_server_config", {}).get("observed", {})
    required = {
        "experiment_context_verified": True,
        "http_health_status": "200",
        "server_ready_log": True,
        "h100_runtime_verified": True,
        "native_graph_source_verified": True,
        "pinned_draft_sha256_verified": True,
        "nixl_source_sha256_verified": True,
        "hpc_ops_preflight_passed": True,
    }
    if any(proof.get(key) != value for key, value in required.items()):
        raise SystemExit("FATAL: accepted 224276 proof is missing a required source/runtime gate")
    expected_config = {
        "dtype": "bfloat16", "tp_size": 4, "speculative_algorithm": "EAGLE3",
        "speculative_num_steps": 2, "speculative_eagle_topk": 1,
        "speculative_num_draft_tokens": 3, "disaggregation_mode": "prefill",
        "disaggregation_transfer_backend": "nixl",
    }
    if any(observed.get(key) != value for key, value in expected_config.items()):
        raise SystemExit("FATAL: accepted parent runtime configuration differs from this candidate's prerequisite contract")
    if metadata.get("passed") is not True or metadata.get("tp_size") != 4 or metadata.get("receipt_count") != 4:
        raise SystemExit("FATAL: accepted parent metadata observer gate is incomplete")
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "accepted-parent-observer.json").write_bytes(receipt_bytes)
    (args.out / "accepted-parent-observer.sha256").write_text(actual + "\n")
    print("ACCEPTED_PARENT_224276_PORTABLE_RECEIPT_VERIFIED", actual)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
