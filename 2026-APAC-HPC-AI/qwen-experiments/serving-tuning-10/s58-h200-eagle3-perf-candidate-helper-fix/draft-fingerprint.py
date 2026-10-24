#!/usr/bin/env python3
"""Fully verify a worker's staged draft and record portable identity evidence."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import signal
import socket
import sys
import tempfile
import time

REVISION = "ff0f0c0999f6c86b21dfd2f5803eebc4ac712224"
WEIGHT_SHA256 = "bf226a966868fe413a22e62e471aa1130bd94f17fd2c40d322b1c8b4def1ae86"
WEIGHT_BYTES = 1145943008
CONFIG_SHA256 = "fc9573a970a1afd1c78ca29df2837f0d3f9f577721590a2fa132b87f759c9433"
FILES = ("model.safetensors", "config.json", "publisher-config.json")
ROLES = ("prefill-0", "prefill-1", "decode-0")
FINGERPRINT_FIELDS = ("st_dev", "st_ino", "st_size", "st_mtime_ns", "st_ctime_ns")
VERIFIER_PATH = Path(__file__).resolve().with_name("verify-draft.py")


def portable_identity(report):
    if report.get("state") != "PASS" or report.get("revision") != REVISION:
        raise ValueError("full draft report is not PASS for the pinned revision")
    if report.get("repository") != "nebius/EAGLE3-Qwen3-235B-A22B-Instruct-2507":
        raise ValueError("full draft report repository mismatch")
    rows = {Path(row["path"]).name: row for row in report.get("files", [])}
    if set(rows) != set(FILES) or len(report.get("files", [])) != len(FILES):
        raise ValueError("full draft report must contain exactly the three pinned files")
    expected = {
        "model.safetensors": (WEIGHT_BYTES, WEIGHT_SHA256),
        "config.json": (474, CONFIG_SHA256),
        "publisher-config.json": (505, "1ec83be9e2876dcf7fd85f5a19528ddb49095b15cc7d83970e3d66b0746e4ab4"),
    }
    result = {}
    for name in FILES:
        row = rows[name]
        identity = {"bytes": row.get("bytes"), "sha256": row.get("sha256")}
        if identity != {"bytes": expected[name][0], "sha256": expected[name][1]}:
            raise ValueError("full draft report has a pinned byte length or SHA-256 mismatch: " + name)
        result[name] = identity
    return {"repository": report["repository"], "revision": report["revision"], "files": result}


def load_verifier(path):
    spec = importlib.util.spec_from_file_location("pinned_draft_verifier", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load sibling verify-draft.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def atomic_exclusive_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix="." + path.name + ".", suffix=".tmp", dir=path.parent)
    temp = Path(temp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(value, stream, sort_keys=True, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        # link() publishes atomically and fails if another worker already owns this role.
        os.link(temp, path)
        temp.unlink()
        dfd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(dfd)
        finally:
            os.close(dfd)
    except Exception:
        try:
            temp.unlink()
        except FileNotFoundError:
            pass
        raise


def run(draft, parent_report_path, *, role=None, artifact_root=None,
        job_start_epoch=None, verifier_path=None, verifier=None, now=None):
    role = role if role is not None else os.environ.get("QWEN_ROLE_NAME", "")
    artifact_root_value = artifact_root if artifact_root is not None else os.environ.get("QWEN_ARTDIR")
    if not artifact_root_value:
        raise ValueError("QWEN_ARTDIR is required")
    artifact_root = Path(artifact_root_value)
    if role not in ROLES:
        raise ValueError("QWEN_ROLE_NAME must be one of: " + ", ".join(ROLES))
    start_value = job_start_epoch if job_start_epoch is not None else os.environ.get("QWEN_JOB_START_EPOCH")
    if start_value is None:
        raise ValueError("QWEN_JOB_START_EPOCH is required")
    deadline = float(start_value) + 600.0
    clock = time.time if now is None else now
    if clock() >= deadline:
        raise TimeoutError("draft verification startup deadline has already expired")

    parent_bytes = Path(parent_report_path).read_bytes()
    parent = json.loads(parent_bytes)
    parent_identity = portable_identity(parent)
    parent_sha = hashlib.sha256(parent_bytes).hexdigest()

    if verifier is None:
        verifier = load_verifier(verifier_path or VERIFIER_PATH)
    remaining = deadline - clock()
    if remaining <= 0:
        raise TimeoutError("draft verification startup deadline has already expired")
    previous_handler = signal.getsignal(signal.SIGALRM)
    previous_timer = signal.getitimer(signal.ITIMER_REAL)

    def deadline_alarm(_signum, _frame):
        raise TimeoutError("full worker draft verification exceeded startup deadline")

    signal.signal(signal.SIGALRM, deadline_alarm)
    signal.setitimer(signal.ITIMER_REAL, remaining)
    try:
        local = verifier.verify(Path(draft))
    finally:
        signal.setitimer(signal.ITIMER_REAL, *previous_timer)
        signal.signal(signal.SIGALRM, previous_handler)
    if clock() >= deadline:
        raise TimeoutError("full worker draft verification exceeded startup deadline")
    local_identity = portable_identity(local)
    if local_identity != parent_identity:
        raise ValueError("worker full-verification portable identity differs from parent report")
    local_rows = {Path(row["path"]).name: row for row in local["files"]}
    fingerprints = {}
    for name in FILES:
        fingerprint = local_rows[name].get("fingerprint")
        if not isinstance(fingerprint, dict) or set(fingerprint) != set(FINGERPRINT_FIELDS):
            raise ValueError("worker verifier omitted local fingerprint fields: " + name)
        if any(type(fingerprint[key]) is not int or fingerprint[key] < 0 for key in FINGERPRINT_FIELDS):
            raise ValueError("worker local fingerprint fields are not nonnegative integers: " + name)
        if fingerprint["st_size"] != local_identity["files"][name]["bytes"]:
            raise ValueError("worker local fingerprint size contradicts verified byte length: " + name)
        fingerprints[name] = {key: fingerprint[key] for key in FINGERPRINT_FIELDS}

    receipt = {
        "state": "PASS",
        "verification_state": "PASS",
        "role": role,
        "node_hostname": socket.gethostname(),
        "repository": local_identity["repository"],
        "revision": local_identity["revision"],
        "parent_report_sha256": parent_sha,
        "portable_identity": local_identity,
        "observed_local_fingerprints": fingerprints,
        "weight_sha256_matches_publisher_lfs": local.get("weight_sha256_matches_publisher_lfs") is True,
        "all_tensor_header_entries_match_retained_inventory": local.get("all_tensor_header_entries_match_retained_inventory") is True,
        "tensor_count": local.get("tensor_count"),
        "tensor_dtype_counts": local.get("tensor_dtype_counts"),
        "gpu_used": local.get("gpu_used") is True,
        "native_model_loaded": local.get("native_model_loaded") is True,
        "official_accuracy_verified": local.get("official_accuracy_verified") is True,
        "local_full_verification_elapsed_s": local.get("elapsed_s"),
        "scope": "Full local byte hash, safetensors header, and adapter verification; no native model load or official accuracy claim.",
    }
    if (receipt["weight_sha256_matches_publisher_lfs"] is not True or
            receipt["all_tensor_header_entries_match_retained_inventory"] is not True or
            receipt["tensor_count"] != 15 or receipt["gpu_used"] or receipt["native_model_loaded"]):
        raise ValueError("worker verifier did not return the expected full CPU-only verification flags")
    destination = artifact_root / "draft-worker-verifications" / (role + ".json")
    atomic_exclusive_json(destination, receipt)
    return receipt


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 2:
        raise SystemExit("usage: draft-fingerprint.py DRAFT FULLREPORT")
    receipt = run(argv[0], argv[1])
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
