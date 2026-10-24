#!/usr/bin/env python3
"""Admit one reviewed S61 validator-repair retry under the existing Slurm safety cap."""
from datetime import datetime, timezone
from pathlib import Path
import fcntl
import hashlib
import json
import re
import subprocess
import sys

R = Path(__file__).resolve().parents[1]
O = Path(__file__).resolve().parent
B = R / "serving-tuning-10/s61-h200-eagle3-decode-only-kvfix"
RECEIPT = O / "slurm-receipt.json"
CONTROL = R / "runs/25988/matched-control-verification.json"
EXPECTED_CONTROL_SHA = "cd91b8b2b05006ed43d48d8b31a24e1df6887041e2f06c7e24b4cde2e66b0a38"

def run(args, **kwargs):
    return subprocess.check_output(args, text=True, **kwargs)

def main():
    assert not RECEIPT.exists(), "Existing or uncertain receipt requires inspection; do not retry blindly"
    manifest_sha = hashlib.sha256((B / "SHA256SUMS").read_bytes()).hexdigest()
    subprocess.run(["sha256sum", "--check", "SHA256SUMS"], cwd=B, check=True, stdout=subprocess.DEVNULL)
    subprocess.run([sys.executable, "-B", str(B / "preflight-assets.py")], check=True, stdout=subprocess.DEVNULL)
    subprocess.run([sys.executable, "-B", str(B / "check-client-image.py")], check=True, stdout=subprocess.DEVNULL)

    geometry = json.loads((O / "validator-replay-25988.json").read_text())
    assert geometry["passed"] is True and geometry["receipt_count"] == 32
    terminal = run(["sacct", "-X", "-j", "25988", "-P", "--format=JobID,State,ExitCode,Elapsed"])
    assert "25988|FAILED|1:0|00:06:15" in terminal

    control = json.loads(CONTROL.read_text())
    assert control["state"] == "PASS_ACTUAL_S59_CONTROL_RUNTIME_REVIEW"
    assert control["job_id"] == "25947"
    assert control["source_manifest_sha256"] == EXPECTED_CONTROL_SHA
    replay = control["independent_raw_protocol_replay"]
    assert replay["state"] == "PASS_UNRANKED_PERFORMANCE_PROTOCOL"
    assert replay["good_request_fraction"] >= 0.90 and replay["errors"] == replay["cancelled"] == 0

    queue = run(["squeue", "-h", "-u", "apacsc42", "-o", "%i|%T|%j"])
    partition = run(["scontrol", "show", "partition", "hpcai", "-o"])
    assert len(queue.splitlines()) < 5, "Five-job Slurm cap would be exceeded"
    assert "State=UP" in partition and ("MaxTime=00:17:00" in partition or "MaxTime=UNLIMITED" in partition)
    dry = subprocess.run(["sbatch", "--test-only", str(B / "job.sbatch")], cwd=R, capture_output=True, text=True, check=True)
    test = (dry.stdout + dry.stderr).strip()
    match = re.search(r"\bJob\s+(\d+)\s+to start at\b", test)
    assert match, f"Slurm test-only admission did not return its expected placement report: {test}"

    review = {
        "state": "ROOT_REVIEWED_READY",
        "reviewed_utc": datetime.now(timezone.utc).isoformat(),
        "hypothesis": "Decode-only EAGLE3 preserves decode ITL gains while avoiding unnecessary speculative state on prefill and recovering TTFT; this retry changes only the role-aware KV validator after job 25988 failed before scoring.",
        "validator_replay": "PASS_ALL_32_RAW_RECEIPTS: prefill 188 target regions/rank, decode 188 target + 2 EAGLE3 draft regions/rank",
        "bundle": str(B),
        "bundle_manifest_sha256": manifest_sha,
        "control_job": "25947",
        "control_state": "COMPLETED 0:0 with independent raw protocol pass",
        "gpus": 16,
        "nodes": 2,
        "time_limit": "17 minutes",
        "protocol": "N64; 4000/200; seed 2026; 20/40/30 seconds",
        "quality": "UNKNOWN_NOT_EVALUATED",
        "ranked": False,
        "queue_before_submit": queue.splitlines(),
        "partition": partition.strip(),
        "test_only_result": test,
        "test_only_virtual_job_id": match.group(1),
        "required_gates": ["role-specific native args", "BF16 KV and NIXL rank records", "both P/D semantic paths", "zero request errors/cancellations", "joint success >= 0.90", "smoke >= 7/8 without regression", "retrieval 12/12"],
        "source_limit": "This short feasibility screen is not directly rankable against the full 60/120/30-second 3044.400475-token/s incumbent."
    }
    (O / "ROOT_REVIEW.json").write_text(json.dumps(review, indent=2) + "\n")

    row = {
        "state": "SUBMISSION_IN_PROGRESS",
        "attempted_utc": datetime.now(timezone.utc).isoformat(),
        "bundle": str(B),
        "bundle_manifest_sha256": manifest_sha,
        "control_job": "25947",
        "gpus": 16,
        "nodes": 2,
        "time_limit_minutes": 17,
        "pbs_su_reserved": 0,
        "ranked": False,
        "quality": "UNKNOWN_NOT_EVALUATED",
        "sbatch_argv": ["sbatch", "--parsable", str(B / "job.sbatch")]
    }
    RECEIPT.write_text(json.dumps(row, indent=2) + "\n")
    try:
        raw = subprocess.run(["sbatch", "--parsable", str(B / "job.sbatch")], cwd=R, capture_output=True, text=True, timeout=30)
    except BaseException:
        row["state"] = "SUBMISSION_UNCERTAIN"
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n")
        raise
    (O / "submit.stdout").write_text(raw.stdout)
    (O / "submit.stderr").write_text(raw.stderr)
    job = raw.stdout.strip().split(";")[0]
    if raw.returncode or not job.isdigit():
        row["state"] = "SUBMISSION_UNCERTAIN"
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n")
        raise RuntimeError("Inspect Slurm before any retry")
    row.update(state="SUBMITTED", job=job, submitted_utc=datetime.now(timezone.utc).isoformat())
    RECEIPT.write_text(json.dumps(row, indent=2) + "\n")
    detail = run(["scontrol", "show", "job", job, "-o"])
    (O / "post-submit.txt").write_text(detail)
    assert "TimeLimit=00:17:00" in detail
    queue_after = run(["squeue", "-h", "-j", job, "-o", "%i|%T|%j|%R"])
    (O / "post-submit-queue.txt").write_text(queue_after)
    print(f"Submitted S61 role-aware KV validator retry as Slurm job {job}; 16 H200, 17-minute cap.")

if __name__ == "__main__":
    lock = R / "serving-tuning/watcher.lock"
    with lock.open("a") as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)
        main()
