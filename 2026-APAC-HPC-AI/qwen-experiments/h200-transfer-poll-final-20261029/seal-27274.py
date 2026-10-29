#!/usr/bin/env python3
"""Seal completed job 27274's raw evidence without changing its frozen payload."""
from pathlib import Path
import datetime, hashlib, json, subprocess

Q = Path(__file__).resolve().parents[1]
job = 27274
run = Q / f"runs/{job}"
account_path = run / "scheduler-accounting.psv"
manifest_path = run / "artifact-manifest.json"
if account_path.exists() or manifest_path.exists():
    raise SystemExit("Refusing to overwrite existing terminal accounting or artifact manifest")
account = subprocess.check_output([
    "sacct", "-X", "-j", str(job), "-P",
    "--format=JobID,State,ExitCode,Elapsed,ElapsedRaw,NodeList,AllocTRES,ReqTRES"
], text=True)
rows = [line.split("|") for line in account.strip().splitlines()]
assert len(rows) >= 2 and rows[0][0] == "JobID"
job_rows = [dict(zip(rows[0], row)) for row in rows[1:] if row[0] == str(job)]
assert len(job_rows) == 1
assert job_rows[0]["State"] == "COMPLETED" and job_rows[0]["ExitCode"] == "0:0"
queue = subprocess.check_output(["squeue", "-h", "-u", "apacsc42", "-o", "%i"], text=True).split()
assert str(job) not in queue, "Job still appears in the user queue"
assert (Q / f"runs/{job}.out").is_file() and (Q / f"runs/{job}.err").is_file()

# Retain the exact accounting response as a distinct raw terminal receipt.
account_path.write_text(account)
files = []
paths = sorted(run.rglob("*")) + [Q / f"runs/{job}.out", Q / f"runs/{job}.err"]
for path in paths:
    if not path.is_file() or path.is_symlink() or "__pycache__" in path.parts or path == manifest_path:
        continue
    before = path.stat()
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    after = path.stat()
    assert (before.st_size, before.st_mtime_ns) == (after.st_size, after.st_mtime_ns), path
    files.append({"path": str(path.relative_to(Q)), "bytes": after.st_size, "sha256": digest.hexdigest()})

manifest = {
    "job": job,
    "sealed_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "terminal_accounting": account,
    "manifest_scope": "All regular raw run files and the original Slurm stdout/stderr; symlinks and Python cache files excluded. Frozen submitted payload is included and was not modified.",
    "files": files,
}
manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
for item in files:
    path = Q / item["path"]
    assert path.stat().st_size == item["bytes"]
    assert hashlib.sha256(path.read_bytes()).hexdigest() == item["sha256"], path
print(json.dumps({"job": job, "state": job_rows[0]["State"], "files_sealed": len(files), "accounting": str(account_path), "manifest": str(manifest_path)}, indent=2))
