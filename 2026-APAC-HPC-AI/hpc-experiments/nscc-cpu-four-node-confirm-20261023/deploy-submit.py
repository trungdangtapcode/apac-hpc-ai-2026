"""Stage a reviewed CPU payload, or submit it once with a durable reservation."""
from pathlib import Path
import argparse
import datetime
import fcntl
import hashlib
import io
import json
import math
import os
import re
import shlex
import subprocess
import tarfile

EXPERIMENT = Path(__file__).resolve().parent
RESEARCH = EXPERIMENT.parent
ACCOUNT_ROOT = RESEARCH.parents[1]
SSH = str(RESEARCH / "tools/nscc-cpu-ssh.sh")
BUDGET_DIR = RESEARCH / "nscc-cpu-timing-probe-20261021"
MAXIMUM = 512 * 2400 / 3600


def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def save(path, value, exclusive=False):
    with path.open("x" if exclusive else "w") as stream:
        stream.write(json.dumps(value, indent=2) + "\n")
        stream.flush()
        os.fsync(stream.fileno())


def save_budget(value):
    path = BUDGET_DIR / "cpu-budget.json"
    temporary = path.with_name(".cpu-budget-next.json")
    save(temporary, value)
    os.replace(temporary, path)
    descriptor = os.open(str(BUDGET_DIR), os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def cpu(command):
    return subprocess.run([SSH, "bash -lc " + shlex.quote(command)],
                          capture_output=True, text=True, timeout=60, check=True)


def hashes():
    expected = json.loads((EXPERIMENT / "payload-sha256.json").read_text())["files"]
    actual = {str(p.relative_to(EXPERIMENT)): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in (EXPERIMENT / "payload").rglob("*") if p.is_file()}
    assert actual == expected and len(actual) == 54, "Frozen payload mismatch"
    assert all(not (EXPERIMENT / name).is_symlink() for name in expected)
    return expected


def deploy(expected):
    target = EXPERIMENT / "deployment.json"
    assert not target.exists(), "Preserve the existing deployed root"
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    remote = "/scratch/users/industry/ai-hpc/apacsc42/apac2026/tripleu-four-node-confirm-" + stamp
    payload = io.BytesIO()
    with tarfile.open(fileobj=payload, mode="w:gz") as archive:
        for name in [*expected, "payload-sha256.json"]:
            archive.add(str(EXPERIMENT / name), arcname=name, recursive=False)
    code = '''import sys,io,tarfile,hashlib,json
from pathlib import Path
r=Path(ROOT);r.mkdir(exist_ok=False)
with tarfile.open(fileobj=io.BytesIO(sys.stdin.buffer.read()),mode='r:gz') as t:
 for m in t.getmembers():
  assert m.isfile() and not m.name.startswith('/') and '..' not in Path(m.name).parts
  p=r/m.name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(t.extractfile(m).read())
expected=json.loads((r/'payload-sha256.json').read_text())['files']
assert all(hashlib.sha256((r/n).read_bytes()).hexdigest()==h for n,h in expected.items())
print(json.dumps({'root':str(r),'sha256':expected}))
'''.replace("ROOT", repr(remote))
    result = subprocess.run([SSH, "python3 -c " + shlex.quote(code)], input=payload.getvalue(),
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=120, check=True)
    record = json.loads(result.stdout)
    assert record["root"] == remote and record["sha256"] == expected
    record.update(utc=utc(), state="DEPLOYED_NOT_SUBMITTED")
    save(target, record, exclusive=True)
    print(remote)


def submit(expected):
    intent_path = EXPERIMENT / "submission-intent.json"
    assert not intent_path.exists(), "Prior intent exists; query PBS, never blindly retry"
    deployed = json.loads((EXPERIMENT / "deployment.json").read_text())
    assert deployed["sha256"] == expected
    remote = deployed["root"]
    assert remote.startswith("/scratch/users/industry/ai-hpc/apacsc42/apac2026/tripleu-four-node-confirm-")
    # This is bounded text hashing only. Mesh and numerical checks run on compute.
    check = cpu("python3 " + shlex.quote(remote + "/payload/verify-inputs.py") +
                " --root " + shlex.quote(remote) + " --mode bundle")
    assert json.loads(check.stdout)["bundle"]["passed"]
    with (BUDGET_DIR / "cpu-budget.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        assert not intent_path.exists()
        queue = cpu("qstat -u apacsc42").stdout
        assert not re.search(r"^\d+\S*\s+apacsc42\b", queue, re.M), "Preserve new shared CPU jobs; no overlap"
        ai = subprocess.run(["bash", str(ACCOUNT_ROOT / "workspace/vpn-rootless/vpn.sh"),
                             "ssh-batch", "bash -lc 'qstat -u apacsc42'"],
                            capture_output=True, text=True, timeout=30, check=True)
        count = len(re.findall(r"^\d+\S*\s+apacsc42\b", ai.stdout, re.M))
        assert count + 1 <= 3
        report = cpu("myprojects -p 59000042").stdout
        line = [s for s in report.splitlines() if s.startswith("| SU")]
        assert len(line) == 1
        grant, used, balance, indoubt = map(float, [x.strip() for x in line[0].split("|")[2:-1]])
        rate = [s for s in report.splitlines() if s.startswith("| CPU Hour")]
        assert grant == 30000 and balance >= MAXIMUM and indoubt == 0
        assert len(rate) == 1 and float(rate[0].split("|")[3].strip()) == 1
        b = json.loads((BUDGET_DIR / "cpu-budget.json").read_text())
        assert b["project"] == "59000042" and b["schema"] == 2
        fresh_consumed = max(b["consumed_ceiling_SU"], math.ceil(used - b["published_snapshot"]["used_SU"] + 1))
        if fresh_consumed != b["consumed_ceiling_SU"]:
            b["consumed_ceiling_SU"] = fresh_consumed
            b["planning_committed_SU"] = b["reserved_max_SU"] = fresh_consumed + b["outstanding_reserved_max_SU"]
            save_budget(b)
        assert b["planning_committed_SU"] + MAXIMUM <= b["baseline_wave_planning_ceiling_SU"]
        checks = dict(utc=utc(), CPU_queue=queue, AI_queue_read_only=ai.stdout,
                      combined_jobs_before=count, project_report=report,
                      consumed_ceiling_SU=fresh_consumed, outstanding_max_SU=b["outstanding_reserved_max_SU"],
                      new_maximum_SU=MAXIMUM, ceiling_SU=b["baseline_wave_planning_ceiling_SU"],
                      retained_shared_max_SU=b.get("shared_cost_observations", {}).get("retained_uncertain_max_SU"),
                      dependency=None, reason="Independent S128 replication with complete frozen-source and return/field proof")
        save(EXPERIMENT / "pre-submit-checks.json", checks)
        intent = dict(utc=utc(), root=remote, project="59000042", maximum_SU=MAXIMUM,
                      payload_sha256=expected, state="INTENT_RESERVED_DO_NOT_RETRY_BLINDLY")
        save(intent_path, intent, exclusive=True)
        b["outstanding_reserved_max_SU"] += MAXIMUM
        b["reserved_max_SU"] = b["planning_committed_SU"] = fresh_consumed + b["outstanding_reserved_max_SU"]
        entry = dict(id=None, root=remote, maximum_SU=MAXIMUM, state="SUBMISSION_INTENT",
                     branch="four_node_default_scotch_S128_confirmation", observed_utc=utc())
        b["jobs"].append(entry)
        save_budget(b)
        try:
            result = cpu("cd " + shlex.quote(remote) + " && qsub payload/pair.pbs")
            receipt = dict(utc=utc(), root=remote, stdout=result.stdout, stderr=result.stderr,
                           returncode=result.returncode, project="59000042", maximum_SU=MAXIMUM,
                           ncpus=512, mpi_ranks=512, nodes=4, maximum_seconds=2400, ngpus=0)
            save(EXPERIMENT / "submission.json", receipt, exclusive=True)
            job = result.stdout.strip()
            assert re.fullmatch(r"\d+\.pbs\d+", job), "Ambiguous submission response"
        except Exception as exc:
            save(EXPERIMENT / "submission-uncertain.json", dict(utc=utc(), root=remote,
                 reason=str(exc), instruction="Retain full reservation; inspect PBS and never resubmit blindly"))
            raise
        entry.update(id=job, state="SUBMITTED", observed_utc=utc())
        b["updated_utc"] = utc()
        save_budget(b)
        print(job)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--deploy-only", action="store_true")
    mode.add_argument("--submit", action="store_true")
    args = parser.parse_args()
    expected = hashes()
    if args.deploy_only:
        deploy(expected)
    else:
        submit(expected)
