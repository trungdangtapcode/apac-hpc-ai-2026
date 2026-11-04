#!/usr/bin/env python3
"""Run the same 56-rank probe under inherited and launcher interleave policy."""
import hashlib
import json
import os
import pathlib
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parent
RUNS = ROOT / "runs"
RANKS = 56
CAP_SECONDS = 100


def digest_payload():
    entries = []
    for line in (ROOT / "payload-sha256.txt").read_text().splitlines():
        digest, rel = line.split(None, 1)
        path = ROOT / rel.strip().lstrip("*")
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        entries.append({"path": rel.strip(), "expected": digest, "actual": actual,
                        "matches": actual == digest})
    return entries


def execute(arm, interleave):
    out = RUNS / arm
    out.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, RANK_PROBE_ARM=arm, RANK_PROBE_ROOT=str(RUNS))
    launch = ["mpirun", "-np", str(RANKS), "--report-bindings", "--display-map", "--"]
    if interleave:
        launch = ["numactl", "--interleave=all"] + launch
    launch += [sys.executable, str(ROOT / "rank_probe.py")]
    command = ["timeout", "--signal=TERM", "--kill-after=5s", str(CAP_SECONDS)] + launch
    start = time.time()
    with (out / "stdout-stderr.log").open("w") as log:
        proc = subprocess.run(command, cwd=str(ROOT), env=env, stdout=log,
                              stderr=subprocess.STDOUT)
    files = sorted(out.glob("rank-*.json"))
    ranks = []
    for path in files:
        try:
            ranks.append(json.loads(path.read_text()))
        except Exception as exc:
            raise RuntimeError("invalid rank record %s: %s" % (path, exc))
    observed = sorted(item["mpi_rank"] for item in ranks)
    if proc.returncode != 0:
        raise RuntimeError("%s launch failed with status %d" % (arm, proc.returncode))
    if observed != list(range(RANKS)):
        raise RuntimeError("%s expected ranks 0..55, observed %r" % (arm, observed))
    if any(item["arm"] != arm or not item["numactl_show"] for item in ranks):
        raise RuntimeError("%s has missing/mismatched actual policy records" % arm)
    if any(not item["mapping"]["numa_node_pages"] for item in ranks):
        raise RuntimeError("%s has no NUMA node placement pages for a rank" % arm)
    summary = {"arm": arm, "command": command, "exit_status": proc.returncode,
               "elapsed_seconds": round(time.time() - start, 3),
               "rank_file_count": len(files), "ranks": observed,
               "all_exact_mapping_accounting": all(
                   item["mapping"]["exact_mapping_accounting"] for item in ranks)}
    (out / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")


def main():
    RUNS.mkdir(exist_ok=True)
    pre = digest_payload()
    if not pre or any(not item["matches"] for item in pre):
        raise RuntimeError("frozen payload hash check failed before launches")
    execute("inherited", False)
    execute("interleave", True)
    post = digest_payload()
    if pre != post or any(not item["matches"] for item in post):
        raise RuntimeError("frozen payload changed during diagnostic")
    (RUNS / "payload-hash-check.json").write_text(json.dumps(
        {"before": pre, "after": post, "unchanged": pre == post},
        indent=2, sort_keys=True) + "\n")
    print("RANK_POLICY_DIAGNOSTIC_OK: 56 ranks per arm; hashes unchanged")


if __name__ == "__main__":
    main()
