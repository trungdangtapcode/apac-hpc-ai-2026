"""Collect the completed NSCC affinity trace using native tar and retain replayable raw evidence."""
from pathlib import Path
import datetime, hashlib, io, json, shlex, subprocess, tarfile

HERE = Path(__file__).resolve().parent
OUT = HERE / "completed-26004608"
ROOT = json.loads((HERE / "deployment.json").read_text())["root"]
JOB = "26004608"
REMOTE_RUN = f"runs/{JOB}"
BATCH = f"cpu-affinity-strace.o{JOB}"
HELPER = HERE.parent / "tools/nscc-cpu-ssh.sh"
assert not (OUT / "raw-records.tar.gz").exists(), "Preserve original collection; inspect before repeating"
OUT.mkdir(exist_ok=True)

qstat = subprocess.run(["bash", str(HELPER), f"qstat -fx -F json {JOB}.pbs101"], capture_output=True, text=True, timeout=30)
(OUT / "fresh-qstat.stdout.json").write_text(qstat.stdout)
(OUT / "fresh-qstat.stderr.txt").write_text(qstat.stderr)
(OUT / "fresh-qstat.exit-code.txt").write_text(str(qstat.returncode) + "\n")
saved = json.loads((HERE / "live-status-1632.json").read_text())
assert saved["job"]["job_state"] == "F" and saved["job"]["Exit_status"] == 0
terminal_source = "fresh-qstat" if qstat.returncode == 0 else "live-status-1632.json (dated 2026-10-26T16:31:10.939654+00:00); fresh qstat failed and PBS history is no longer available"

remote = (f"cd {shlex.quote(ROOT)} && "
          f"tar --exclude={shlex.quote('runs/'+JOB+'/mpi-init-probe')} "
          f"--exclude={shlex.quote('runs/'+JOB+'/runtime-environment-whitelist.txt')} "
          f"-czf - {shlex.quote(REMOTE_RUN)} {shlex.quote(BATCH)}")
p = subprocess.run(["bash", str(HELPER), remote], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=180)
(OUT / "native-tar.stderr.txt").write_bytes(p.stderr)
assert p.returncode == 0, f"native tar failed rc={p.returncode}: {p.stderr[-2000:]!r}"
archive_path = OUT / "raw-records.tar.gz"
archive_path.write_bytes(p.stdout)
manifest = {}
with tarfile.open(fileobj=io.BytesIO(p.stdout), mode="r:gz") as archive:
    for member in archive.getmembers():
        parts = Path(member.name).parts
        assert ".." not in parts and not member.name.startswith("/")
        if member.isdir():
            continue
        assert member.isfile() and member.size < 2_000_000, (member.name, member.size)
        assert not member.name.endswith("/mpi-init-probe")
        assert not member.name.endswith("/runtime-environment-whitelist.txt")
        raw = archive.extractfile(member).read()
        manifest[member.name] = {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
assert any(k.endswith("/arms/untraced_control/native/pre/rank-0000.json") for k in manifest)
assert any(k.endswith("/arms/rank0_straced/native/pre/rank-0000.json") for k in manifest)

terminal = saved["job"]
if qstat.returncode == 0:
    try:
        terminal = json.loads(qstat.stdout)["Jobs"][JOB + ".pbs101"]
    except Exception:
        terminal_source = "live-status-1632.json (fresh qstat returned zero but response was not parseable)"
        terminal = saved["job"]
keep = ["job_state", "Exit_status", "Resource_List", "resources_used", "project", "queue", "stime", "obittime", "comment", "exec_host", "Output_Path"]
terminal = {k: v for k, v in terminal.items() if k in keep}
doc = {
    "collected_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "job_id": JOB + ".pbs101", "remote_root": ROOT,
    "terminal_evidence_source": terminal_source,
    "fresh_qstat": {"exit_code": qstat.returncode, "stdout_file": "fresh-qstat.stdout.json", "stderr_file": "fresh-qstat.stderr.txt"},
    "terminal": terminal,
    "archive": "raw-records.tar.gz", "archive_sha256": hashlib.sha256(archive_path.read_bytes()).hexdigest(),
    "files": manifest,
    "scope": "Native tar of this job's runs/26004608 records plus its explicitly selected PBS batch stdout; mpi-init-probe executable and runtime-environment-whitelist.txt excluded before transfer. Full archive and per-member byte-count/SHA-256 inventory retained; members are replayed directly from the archive."
}
(OUT / "collection.json").write_text(json.dumps(doc, indent=2) + "\n")
print(json.dumps({"files": len(manifest), "archive_bytes": archive_path.stat().st_size, "fresh_qstat_rc": qstat.returncode, "terminal_source": terminal_source, "terminal": terminal}, indent=2))
