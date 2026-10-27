#!/usr/bin/env python3
"""Verify prepared chunk bundles and CPU-only checker fixtures."""

from __future__ import annotations

import hashlib
import ast
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "serving-tuning-11/s72-h200-full-pgraph-breakable-capnative"
OUT = ROOT / "serving-tuning-11"
RUN = ROOT / "runs/26319"
ARMS = {"s78-h200-full-chunk12288": 12288}
ALLOWED_CHANGED = {
    "config.json", "worker.sh", "check-fast-runtime.py", "job.sbatch",
    "README.md", "PLAN.md", "DERIVATION.json", "SHA256SUMS",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_checker(bundle: Path, logs: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", "-B", str(bundle / "check-fast-runtime.py"), str(logs), "control"],
        cwd=bundle, text=True, capture_output=True,
    )


def verify_arm(name: str, chunk: int) -> dict:
    bundle = OUT / name
    subprocess.run(["sha256sum", "--check", "SHA256SUMS"], cwd=bundle, check=True, stdout=subprocess.DEVNULL)
    cfg = json.loads((bundle / "config.json").read_text())
    assert cfg["prefill_chunked_prefill_size"] == chunk
    assert cfg["concurrency"] == 64 and cfg["gpus"] == 16 and cfg["walltime_minutes"] == 17
    assert cfg["prefill_cuda_graph"] == "breakable" and cfg["prefill_max_running_requests"] is None
    assert cfg["official_score_claim"] is False and cfg["quality"] == "UNKNOWN_NOT_EVALUATED"
    worker = (bundle / "worker.sh").read_text()
    assert worker.count(f"--chunked-prefill-size {chunk}") == 1
    assert "--chunked-prefill-size 8192" not in worker
    checker = (bundle / "check-fast-runtime.py").read_text()
    assert "chunked_prefill_size=cfg['prefill_chunked_prefill_size']" in checker
    assert "Capture target prefill CUDA graph begin" in checker and "Capture target prefill CUDA graph end" in checker
    assert "chunked_prefill_size=8192" not in checker
    job = (bundle / "job.sbatch").read_text()
    assert f"QWEN_BUNDLE=/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/serving-tuning-11/{name}" in job

    # Files outside the explicitly derived identities are byte-for-byte copied from frozen S72.
    changed = []
    for parent_file in SOURCE.iterdir():
        if parent_file.is_file() and parent_file.name not in ALLOWED_CHANGED:
            target_file = bundle / parent_file.name
            if not target_file.exists() or sha256(parent_file) != sha256(target_file):
                changed.append(parent_file.name)
    assert not changed, f"{name}: unexpected payload source changes: {changed}"

    subprocess.run(["bash", "-n", "job.sbatch", "worker.sh", "topology-job.sh", "benchmark.sh"], cwd=bundle, check=True)
    ast.parse((bundle / "check-fast-runtime.py").read_text(), filename="check-fast-runtime.py")

    # Existing S72 logs must be rejected because they report chunk 8192.
    rejected = run_checker(bundle, RUN)
    assert rejected.returncode != 0 and f"chunked_prefill_size=8192, expected {chunk}" in rejected.stderr

    # Synthetic parser-only fixture: change only the logged ServerArgs literal.
    with tempfile.TemporaryDirectory(prefix=f"{name}-fixture-") as tmp:
        fixture = Path(tmp)
        for role in ("prefill-0", "prefill-1", "decode-0"):
            shutil.copyfile(RUN / f"{role}.log", fixture / f"{role}.log")
        for role in ("prefill-0", "prefill-1"):
            path = fixture / f"{role}.log"
            text = path.read_text(errors="replace")
            old = "chunked_prefill_size=8192"
            records=[line for line in text.splitlines() if "server_args=ServerArgs(" in line]
            assert len(records)==1 and old in records[0]
            updated=records[0].replace(old, f"chunked_prefill_size={chunk}")
            path.write_text(text.replace(records[0],updated,1))
        accepted = run_checker(bundle, fixture)
        assert accepted.returncode == 0, accepted.stderr[-2000:]
        parsed = json.loads(accepted.stdout)
        assert parsed["state"] == "PASS_FAST_RUNTIME"
    return {
        "bundle": f"serving-tuning-11/{name}",
        "chunk": chunk,
        "checksum": "PASS",
        "only_allowed_payload_differences": "PASS",
        "shell_and_python_syntax": "PASS",
        "actual_26319_logs_rejected_for_8192_mismatch": "PASS",
        "synthetic_chunk_parser_fixture": "PASS_PARSER_ONLY_NOT_GPU_EVIDENCE",
        "graph_capture_gate": "present_and_exercised_on_synthetic_parent_logs_only",
    }


def main() -> None:
    results = [verify_arm(name, chunk) for name, chunk in ARMS.items()]
    verification = {
        "state": "CPU_PREPARATION_PASS_NOT_GPU_ACCEPTANCE",
        "parent_control_job": 26319,
        "source_bundle": "serving-tuning-11/s72-h200-full-pgraph-breakable-capnative",
        "arms": results,
        "limitations": [
            "Synthetic fixtures alter only the chunk-size literal in copied ServerArgs logs; they are not evidence that either chunk runs or captures graphs on H200.",
            "No new GPU submission or result is represented.",
            "Official full-set accuracy remains unknown and unverified.",
        ],
    }
    output = Path(__file__).resolve().parent / "verification.json"
    output.write_text(json.dumps(verification, indent=2, sort_keys=True) + "\n")
    print(json.dumps(verification, indent=2))


if __name__ == "__main__":
    main()
