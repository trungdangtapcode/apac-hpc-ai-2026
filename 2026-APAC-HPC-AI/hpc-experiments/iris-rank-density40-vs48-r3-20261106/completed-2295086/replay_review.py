#!/usr/bin/env python3
"""Replay the retained local review checks for Iris job 2295086."""
import hashlib
import importlib.util
import json
import re
import statistics
import tarfile
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve().parent
EXPERIMENT = HERE.parent
ARCHIVE = HERE / "raw-evidence.tar.gz"


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def check_rank_proofs(root, arm, expected):
    d = root / "runs/2295086/arms" / arm / "rank-probe-proofs"
    proofs = [json.loads(p.read_text()) for p in sorted(d.glob("rank-*.json"))]
    assert len(proofs) == expected
    assert sorted(p["rank"] for p in proofs) == list(range(expected))
    assert all(p["world_size"] == expected for p in proofs)
    assert len({tuple(p["affinity_cpu_ids"]) for p in proofs}) == expected
    assert all(len(p["affinity_cpu_ids"]) == 1 for p in proofs)
    return proofs


def main():
    collection = json.loads((HERE / "collection.json").read_text())
    assert sha256(ARCHIVE) == collection["archive_sha256"]
    assert ARCHIVE.stat().st_size == collection["archive_bytes"]

    with tempfile.TemporaryDirectory(prefix="review-2295086-") as tmp:
        with tarfile.open(ARCHIVE, "r:gz") as tf:
            tf.extractall(tmp, filter="data")
        root = Path(tmp)
        entries = collection["files"]
        assert len(entries) == 207
        for rel, meta in entries.items():
            p = root / rel
            assert p.is_file() and p.stat().st_size == meta["bytes"]
            assert sha256(p) == meta["sha256"], rel

        frozen = {}
        for line in (EXPERIMENT / "payload-sha256.txt").read_text().splitlines():
            digest, rel = line.split(None, 1)
            frozen[rel] = digest
        assert len(frozen) == 100
        assert frozen == collection["frozen_runtime_hashes"]

        for ranks in (40, 48):
            status = json.loads((root / f"runs/2295086/accepted-source-{ranks}-before.status.json").read_text())
            assert status["returncode"] == 0

        spec = importlib.util.spec_from_file_location("native_output", EXPERIMENT / "native_output.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _, a1_times, _, _ = module.review_native_output(
            root / "runs/2295086/arms/A1-control48", expected_ranks=48
        )

        a1 = check_rank_proofs(root, "A1-control48", 48)
        b1 = check_rank_proofs(root, "B1-candidate40", 40)
        numa0 = set(range(0, 56, 2))
        numa1 = set(range(1, 56, 2))

        def numa_counts(proofs):
            cpus = {cpu for proof in proofs for cpu in proof["affinity_cpu_ids"]}
            return len(cpus & numa0), len(cpus & numa1)

        a_counts, b_counts = numa_counts(a1), numa_counts(b1)
        assert a_counts == (28, 20)
        assert b_counts == (28, 12)

        b_log = (root / "runs/2295086/arms/B1-candidate40/simpleFoam.log").read_text(errors="replace")
        b_steps = [int(x) for x in re.findall(r"^Time = (\d+)\s*$", b_log, re.M)]
        b_times = [float(x) for x in re.findall(
            r"^Wall-clock time elapsed during the current time step = ([\deE.+-]+)", b_log, re.M
        )]
        assert b_steps == list(range(1, 37))
        assert len(b_times) == 34
        assert not re.search(r"^End\s*$", b_log, re.M)
        a1_rc = json.loads((root / "runs/2295086/arms/A1-control48/return-code.json").read_text())
        b1_rc = json.loads((root / "runs/2295086/arms/B1-candidate40/return-code.json").read_text())
        assert a1_rc["returncode"] == 0
        assert b1_rc["returncode"] == 124

        result = {
            "job_id": "2295086",
            "raw_archive_sha256_verified": True,
            "raw_collected_file_hashes_verified": len(entries),
            "frozen_payload_hashes_verified": len(frozen),
            "accepted_source_checks_before_each_decomposition": "PASS",
            "A1_native_output_api": "PASS",
            "A1_rank_count": 48,
            "A1_complete_steps": 40,
            "A1_measured_intervals": len(a1_times),
            "A1_mean_seconds_per_step": statistics.mean(a1_times),
            "A1_recorded_rank_cpus_by_numa": {"node0": a_counts[0], "node1": a_counts[1]},
            "B1_rank_count": 40,
            "B1_started_steps": [min(b_steps), max(b_steps)],
            "B1_recorded_intervals": len(b_times),
            "B1_diagnostic_mean_seconds_per_interval": statistics.mean(b_times),
            "B1_recorded_rank_cpus_by_numa": {"node0": b_counts[0], "node1": b_counts[1]},
            "B1_native_output_api": "NOT_APPLICABLE_INCOMPLETE",
            "A1_native_return": a1_rc["returncode"],
            "B1_native_return": b1_rc["returncode"],
            "overall_measurement_valid": False,
            "interpretation": "The rank masks establish pre-MPI launcher affinity only, not causal solver placement.",
        }
        (HERE / "REVIEW.json").write_text(json.dumps(result, indent=2) + "\n")
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
