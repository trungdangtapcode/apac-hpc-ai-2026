#!/usr/bin/env python3
"""Offline structural checks; never launches a scheduler or MPI job."""
import ast
import hashlib
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent
required = ["rank_probe.py", "run.py", "job.sbatch", "README.md"]
for name in required:
    path = ROOT / name
    assert path.is_file() and path.stat().st_size > 0, "missing " + name
for name in ("rank_probe.py", "run.py"):
    ast.parse((ROOT / name).read_text(), filename=name)

job = (ROOT / "job.sbatch").read_text()
for directive in ("--partition=iris", "--qos=low", "--exclusive", "--mem=0",
                  "--gpus=0", "--nodes=1", "--ntasks=56", "--time=00:05:00"):
    assert directive in job, "missing resource bound " + directive
assert "module load gcc/11" in job and "module load hpcx/2.50" in job
assert "OpenFOAM-v2512/etc/bashrc" in job
assert "timeout --signal=TERM --kill-after=5s 240s" in job

probe = (ROOT / "rank_probe.py").read_text()
for token in ("OMPI_COMM_WORLD_RANK", "numactl", "--show", "sched_getaffinity",
              "MAP_PRIVATE", "MAP_ANONYMOUS", "range(0, BYTES, page_size)",
              "/proc/self/numa_maps", "os.replace"):
    assert token in probe, "missing probe feature " + token
driver = (ROOT / "run.py").read_text()
assert "CAP_SECONDS = 100" in driver and "RANKS = 56" in driver
assert 'execute("inherited", False)' in driver and 'execute("interleave", True)' in driver
assert "--interleave=all" in driver

# Freeze only the four runnable/description files. The manifest excludes itself.
manifest = ROOT / "payload-sha256.txt"
with manifest.open("w") as stream:
    for name in sorted(required):
        digest = hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
        stream.write("%s  %s\n" % (digest, name))
lines = manifest.read_text().splitlines()
assert len(lines) == len(required)
for line in lines:
    digest, name = line.split(None, 1)
    assert re.fullmatch(r"[0-9a-f]{64}", digest)
    assert hashlib.sha256((ROOT / name.strip()).read_bytes()).hexdigest() == digest
print("OFFLINE_CHECKS_OK: four frozen files, 56 ranks x two arms, 100-second arm caps, 5-minute job")
