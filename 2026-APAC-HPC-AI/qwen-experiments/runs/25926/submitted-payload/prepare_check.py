#!/usr/bin/env python3
"""Fail-closed source, asset, and prerequisite-reference checks for D5."""

import hashlib
import json
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_root_binding() -> list[str]:
    binding = json.loads((HERE / "ROOT_REFERENCE_BINDING.json").read_text())
    problems = []
    artifacts = {}
    if binding.get("state") != "ROOT_REVIEWED_ACCEPTED":
        problems.append("root R3 reference binding is not accepted")
    for field in ("actual_receipt_sha256", "actual_result_sha256", "root_review_sha256"):
        if not isinstance(binding.get(field), str) or len(binding[field]) != 64:
            problems.append(f"missing valid {field}")
    for path_field, hash_field in (
        ("actual_receipt_path", "actual_receipt_sha256"),
        ("actual_result_path", "actual_result_sha256"),
        ("root_review_path", "root_review_sha256"),
    ):
        value = binding.get(path_field)
        if not isinstance(value, str) or not value:
            problems.append(f"missing {path_field}")
            continue
        artifact = Path(value)
        if not artifact.is_absolute():
            artifact = HERE.parent.parent / artifact
        if not artifact.is_file():
            problems.append(f"bound artifact does not exist: {path_field}")
        elif isinstance(binding.get(hash_field), str) and sha(artifact) != binding[hash_field]:
            problems.append(f"bound artifact hash mismatch: {path_field}")
        else:
            artifacts[path_field] = artifact
    if binding["native_ep5_oracle_relative_l2"] > binding["acceptance_limits"]["native_relative_l2_max"]:
        problems.append("R3 native EP5 oracle error exceeds accepted threshold")
    if binding["physical_map_oracle_error"] > binding["acceptance_limits"]["physical_map_error_max"]:
        problems.append("R3 physical-map error exceeds accepted threshold")
    try:
        receipt = json.loads(artifacts["actual_receipt_path"].read_text())
        result = json.loads(artifacts["actual_result_path"].read_text())
        review = json.loads(artifacts["root_review_path"].read_text())
        if receipt.get("job") != binding["actual_run_identity"].rsplit(" ", 1)[-1]:
            problems.append("bound R3 receipt job identity mismatch")
        if review.get("status") != "PASS" or review.get("job_id") != receipt.get("job"):
            problems.append("bound R3 terminal review does not pass for the receipt job")
        actual_metrics = result.get("outputs", {})
        pairs = (
            ("native_ep5_oracle_relative_l2", "ep5_vs_oracle_relative_l2"),
            ("native_ep1_oracle_relative_l2", "ep1_vs_oracle_relative_l2"),
            ("native_ep5_ep1_relative_l2", "ep5_vs_ep1_relative_l2"),
            ("physical_map_oracle_error", "physical_map_oracle_relative_l2"),
        )
        for binding_name, result_name in pairs:
            if result_name not in actual_metrics or abs(binding[binding_name] - actual_metrics[result_name]) > 1e-9:
                problems.append(f"bound R3 metric does not match actual result: {binding_name}")
    except (KeyError, TypeError, ValueError, json.JSONDecodeError, OSError) as exc:
        problems.append(f"bound R3 artifacts could not be cross-checked: {exc}")
    return problems


def check_candidate_review_binding() -> list[str]:
    binding = json.loads((HERE / "ROOT_CANDIDATE_REVIEW_BINDING.json").read_text())
    problems = []
    if binding.get("state") != "ROOT_REVIEWED_READY" or binding.get("review_status") != "PASS":
        problems.append("D5 candidate/controller root review is not accepted")
    review_path = binding.get("review_path")
    review_hash = binding.get("review_sha256")
    if not isinstance(review_path, str) or not review_path:
        problems.append("missing D5 candidate review path")
    elif not isinstance(review_hash, str) or len(review_hash) != 64:
        problems.append("missing valid D5 candidate review SHA-256")
    else:
        artifact = Path(review_path)
        if not artifact.is_absolute():
            artifact = HERE.parent.parent / artifact
        if not artifact.is_file():
            problems.append("D5 candidate root review artifact does not exist")
        elif sha(artifact) != review_hash:
            problems.append("D5 candidate root review artifact hash mismatch")
    return problems


def main() -> int:
    problems = check_root_binding() + check_candidate_review_binding()
    cfg = HERE / "model-config.json"
    expected = json.loads((HERE / "ACTUAL_MODEL_CONFIG.json").read_text())
    if not cfg.is_file() or sha(cfg) != expected["sha256"]:
        problems.append("retained model config SHA-256 mismatch")
    if not (HERE / "observer" / "sitecustomize.py").is_file():
        problems.append("observer hook is missing")
    for required_file in ("device_preflight.py", "headcheck.py", "ROOT_CANDIDATE_REVIEW_BINDING.json"):
        if not (HERE / required_file).is_file():
            problems.append(f"required readiness gate is missing: {required_file}")
    if problems:
        print("D5_PREPARE_CHECK=FAIL_CLOSED")
        for problem in problems:
            print(f"- {problem}")
        return 2
    print("D5_PREPARE_CHECK=PASS")
    print("R3 artifacts, D5 root review, actual config hash, and readiness hooks are verified.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
