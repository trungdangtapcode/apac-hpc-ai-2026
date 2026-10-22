"""Deploy the frozen H/S256 pair and submit it once under the CPU budget lock."""
from pathlib import Path
import datetime
import fcntl
import hashlib
import io
import json
import re
import shlex
import subprocess
import tarfile


ROOT_HOME = Path("/home/apacsc42")
RESEARCH = ROOT_HOME / "2026-APAC-HPC-AI/hpc-experiments"
EXPERIMENT = Path(__file__).resolve().parent
PAYLOAD = EXPERIMENT / "payload"
SSH_HELPER = str(RESEARCH / "tools/nscc-cpu-ssh.sh")
PREPARATION_REVIEW = RESEARCH / "nscc-cpu-three-cuts256-20261021/review.json"
CPU_LOCK = RESEARCH / "nscc-cpu-timing-probe-20261021/cpu-budget.lock"
BUDGET_PATH = RESEARCH / "nscc-cpu-timing-probe-20261021/cpu-budget.json"
MAXIMUM_SU = 256 * 40 / 60
DEPENDENCY = "25907772.pbs101"


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def save(name, value):
    (EXPERIMENT / name).write_text(json.dumps(value, indent=2) + "\n")


def cpu(command):
    return subprocess.run(
        [SSH_HELPER, "bash -lc " + shlex.quote(command)],
        capture_output=True,
        text=True,
        timeout=120,
        check=True,
    )


assert not (EXPERIMENT / "submission-intent.json").exists(), \
    "Submission already attempted; inspect scheduler state instead of retrying"
if not PREPARATION_REVIEW.is_file():
    PREPARATION_REVIEW = RESEARCH / "nscc-cpu-three-cuts256-20261021/review-files-only.json"
assert PREPARATION_REVIEW.is_file(), "Reviewed native preparation evidence is missing"
preparation = json.loads(PREPARATION_REVIEW.read_text())
assert preparation.get("state") in {"NATIVE_THREE_CUTS_PREPARATION_PASS", "NATIVE_THREE_CUTS_EVIDENCE_PASS_SCHEDULER_HISTORY_UNAVAILABLE"}, preparation.get("state")
assert preparation.get("job") == DEPENDENCY, preparation.get("job")

expected_hashes = json.loads((EXPERIMENT / "payload-sha256.json").read_text())
actual_hashes = {
    name: hashlib.sha256((PAYLOAD / name).read_bytes()).hexdigest()
    for name in expected_hashes
}
assert actual_hashes == expected_hashes, "Frozen payload hash mismatch"

stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
remote_root = f"/scratch/users/industry/ai-hpc/apacsc42/apac2026/tripleu-method-pair256-{stamp}"
expected_document = json.dumps(expected_hashes, indent=2).encode()
archive_buffer = io.BytesIO()
with tarfile.open(fileobj=archive_buffer, mode="w:gz") as archive:
    for relative in expected_hashes:
        archive.add(str(PAYLOAD / relative), arcname=relative, recursive=False)
    member = tarfile.TarInfo("__deployment_expected_sha256.json")
    member.size = len(expected_document)
    archive.addfile(member, io.BytesIO(expected_document))

# Stream the archive as SSH stdin so a large payload never enters one argv item.
remote_code = """import io,tarfile,hashlib,json,sys
from pathlib import Path
root=Path(ROOT);root.mkdir(exist_ok=False)
with tarfile.open(fileobj=io.BytesIO(sys.stdin.buffer.read()),mode='r:gz') as archive:
 for member in archive.getmembers():
  assert member.isfile() and not member.name.startswith('/') and '..' not in Path(member.name).parts
  target=root/member.name;target.parent.mkdir(parents=True,exist_ok=True)
  target.write_bytes(archive.extractfile(member).read())
hashes=json.loads((root/'__deployment_expected_sha256.json').read_text())
for name,digest in hashes.items():assert hashlib.sha256((root/name).read_bytes()).hexdigest()==digest,name
print(json.dumps(dict(root=str(root),sha256=hashes)))
""".replace("ROOT", repr(remote_root))
deployment_process = subprocess.run(
    [SSH_HELPER, "python3 -c " + shlex.quote(remote_code)],
    input=archive_buffer.getvalue(),
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    timeout=120,
    check=True,
)
deployment = json.loads(deployment_process.stdout.decode())
assert deployment["root"] == remote_root
assert deployment["sha256"] == expected_hashes
save("deployment.json", deployment)

with CPU_LOCK.open("a") as lock:
    fcntl.flock(lock, fcntl.LOCK_EX)
    cpu_queue = cpu("qstat -u apacsc42")
    cpu_jobs = re.findall(r"^(\d+\.\S+)\s+apacsc42\s", cpu_queue.stdout, re.M)
    assert set(cpu_jobs).issubset({"25907753.pbs101", DEPENDENCY}), \
        f"Unexpected own CPU jobs; preserve queue: {cpu_jobs}"

    assert not cpu_jobs, "An immediate new CPU allocation requires the own CPU queue to be empty"
    parent_process = subprocess.run([SSH_HELPER, "bash -lc " + shlex.quote("qstat -xf -F json " + DEPENDENCY)], capture_output=True, text=True, timeout=30)
    if parent_process.returncode == 0:
        parent = json.loads(parent_process.stdout)["Jobs"][DEPENDENCY]
        assert str(parent["project"]) == "59000042" and parent["job_state"] == "F" and parent["Exit_status"] == 0
        parent_state = "F"
        dependency_satisfied = True
        dependency_history_unavailable = False
    else:
        assert "Unknown Job Id" in parent_process.stderr, parent_process.stderr
        assert preparation["state"] == "NATIVE_THREE_CUTS_EVIDENCE_PASS_SCHEDULER_HISTORY_UNAVAILABLE"
        parent_state = "HISTORY_UNAVAILABLE"
        dependency_satisfied = False
        dependency_history_unavailable = True
    # Fresh runtime input/rank checks and complete initialization validate the prepared data;
    # missing historical PBS status is never fabricated or released from the cost ledger.
    afterok_dependency = None
    ai_queue = subprocess.run(
        ["bash", str(ROOT_HOME / "workspace/vpn-rootless/vpn.sh"), "ssh-batch",
         "bash -lc 'qstat -u apacsc42'"],
        capture_output=True,
        text=True,
        timeout=45,
        check=True,
    )
    ai_jobs = [line for line in ai_queue.stdout.splitlines()
               if re.search(r"^\d+\S*\s+apacsc42\s", line)]
    assert len(ai_jobs) + len(cpu_jobs) + 1 <= 3, "Combined own PBS cap would be exceeded"

    project_report = cpu("myprojects -p 59000042")
    assert "59000042" in project_report.stdout
    su_lines = [line for line in project_report.stdout.splitlines() if line.startswith("| SU")]
    assert len(su_lines) == 1
    project_values = [float(value.strip()) for value in su_lines[0].split("|")[2:-1]]
    assert project_values[2] > MAXIMUM_SU, "Fresh CPU project balance is insufficient"

    budget = json.loads(BUDGET_PATH.read_text())
    assert budget["schema"] == 2 and budget["project"] == "59000042"
    ceiling = float(budget["baseline_wave_planning_ceiling_SU"])
    assert float(budget["consumed_ceiling_SU"]) + float(budget["outstanding_reserved_max_SU"]) + MAXIMUM_SU <= ceiling

    checks = {
        "utc": now(),
        "cpu_queue": cpu_queue.stdout,
        "ai_queue_readonly": ai_queue.stdout,
        "cpu_project": project_report.stdout,
        "combined_jobs_before": len(ai_jobs) + len(cpu_jobs),
        "dependency_afterok": afterok_dependency,
        "dependency_job": DEPENDENCY,
        "dependency_already_satisfied": dependency_satisfied,
        "dependency_scheduler_state": parent_state,
        "dependency_history_unavailable": dependency_history_unavailable,
        "preparation_review": str(PREPARATION_REVIEW),
        "preparation_review_state": preparation["state"],
        "budget_schema": budget["schema"],
        "cumulative_ceiling_SU": ceiling,
        "consumed_ceiling_SU": budget["consumed_ceiling_SU"],
        "outstanding_reserved_max_SU": budget["outstanding_reserved_max_SU"],
        "new_maximum_SU": MAXIMUM_SU,
    }
    save("pre-submit-checks.json", checks)

    intent = {
        "utc": now(),
        "root": remote_root,
        "project": "59000042",
        "maximum_SU": MAXIMUM_SU,
        "dependency_afterok": DEPENDENCY,
        "payload_sha256": expected_hashes,
        "state": "SUBMISSION_ATTEMPT_MUST_NOT_RETRY_BLINDLY",
    }
    save("submission-intent.json", intent)
    budget["outstanding_reserved_max_SU"] += MAXIMUM_SU
    budget["reserved_max_SU"] = budget["planning_committed_SU"] = (
        budget["consumed_ceiling_SU"] + budget["outstanding_reserved_max_SU"]
    )
    budget["jobs"].append({
        "id": None,
        "state": "SUBMISSION_INTENT",
        "root": remote_root,
        "maximum_SU": MAXIMUM_SU,
        "branch": "N256_two_node_hierarchical_vs_default_scotch_pair",
        "dependency_afterok": DEPENDENCY,
    })
    BUDGET_PATH.write_text(json.dumps(budget, indent=2) + "\n")

    try:
        qsub_command = f"cd {shlex.quote(remote_root)} && qsub"
        if afterok_dependency:
            qsub_command += f" -W depend=afterok:{afterok_dependency}"
        qsub_command += " pair.pbs"
        receipt = cpu(qsub_command)
    except Exception as error:
        save("submission-uncertain.json", {
            "utc": now(),
            "root": remote_root,
            "reason": str(error),
            "stdout": getattr(error, "stdout", None),
            "stderr": getattr(error, "stderr", None),
            "instruction": "Keep the reservation, query PBS, and never resubmit blindly",
        })
        raise

    submission = {
        "utc": now(),
        "root": remote_root,
        "returncode": receipt.returncode,
        "stdout": receipt.stdout,
        "stderr": receipt.stderr,
        "project": "59000042",
        "maximum_SU": MAXIMUM_SU,
        "ncpus": 256,
        "mpi_ranks": 256,
        "nodes": 2,
        "maximum_seconds": 2400,
        "dependency_afterok": afterok_dependency,
        "dependency_job": DEPENDENCY,
        "dependency_already_satisfied": dependency_satisfied,
        "ngpus": 0,
    }
    save("submission.json", submission)
    submitted_job = receipt.stdout.strip()
    assert re.fullmatch(r"\d+\.pbs\d+", submitted_job), submitted_job
    budget["jobs"][-1].update(id=submitted_job, state="SUBMITTED", observed_utc=now())
    BUDGET_PATH.write_text(json.dumps(budget, indent=2) + "\n")
    print(submitted_job)
