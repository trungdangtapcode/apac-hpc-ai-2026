#!/usr/bin/env python3
"""Replay retained integrity, native output, and placement checks for job 2295087."""
import hashlib
import importlib.util
import json
import statistics
import tarfile
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXPERIMENT = HERE.parent
ARCHIVE = HERE / "raw-evidence.tar.gz"
ARMS = ("A1-control48", "B1-candidate40", "B2-candidate40", "A2-control48")


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def load_json(path):
    return json.loads(path.read_text())


def cpu_masks(root, arm, expected):
    path = root / "runs/2295087/arms" / arm / "rank-proofs.json"
    d = load_json(path)
    assert d["passed"] and d["rank_count"] == expected
    assert d["rank_ids"] == list(range(expected))
    proofs = d["proofs"]
    assert len(proofs) == expected
    assert [p["rank"] for p in proofs] == list(range(expected))
    assert all(p["world_size"] == expected for p in proofs)
    assert all(len(p["affinity_cpu_ids"]) == 1 for p in proofs)
    masks = [tuple(p["affinity_cpu_ids"]) for p in proofs]
    assert len(set(masks)) == expected
    assert all(p["hostname"] == "iris001.hpcadvisorycouncil.com" for p in proofs)
    return masks


def telemetry_summary(root, arm):
    path = root / "runs/2295087/arms" / arm / "telemetry-samples.jsonl"
    rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    def med(group, key):
        vals = [float(row[group][key]) for row in rows if key in row.get(group, {})]
        return statistics.median(vals) if vals else None
    return {
        "samples_5s": len(rows),
        "median_cpuinfo_frequency_mhz": med("cpuinfo_frequency", "median_mhz"),
        "median_sample_min_cpu_frequency_mhz": med("cpuinfo_frequency", "minimum_mhz"),
        "median_memavailable_kb": med("meminfo_kb", "MemAvailable"),
        "median_active_anon_kb": med("meminfo_kb", "Active(anon)"),
        "scope": "Whole-node aggregate, not process attribution or causal bandwidth evidence.",
        "pressure_files": "not available in procfs",
    }


def main():
    collection = load_json(HERE / "collection.json")
    assert collection["job_id"] == "2295087"
    assert sha256(ARCHIVE) == collection["archive_sha256"]
    assert ARCHIVE.stat().st_size == collection["archive_bytes"]

    with tempfile.TemporaryDirectory(prefix="review-2295087-") as tmp:
        with tarfile.open(ARCHIVE, "r:gz") as tf:
            tf.extractall(tmp, filter="data")
        root = Path(tmp)
        entries = collection["files"]
        assert len(entries) == 452
        for rel, meta in entries.items():
            p = root / rel
            assert p.is_file() and p.stat().st_size == meta["bytes"]
            assert sha256(p) == meta["sha256"], rel

        frozen = {}
        for line in (EXPERIMENT / "payload-sha256.txt").read_text().splitlines():
            digest, rel = line.split(None, 1)
            frozen[rel] = digest
        assert len(frozen) == 101
        assert frozen == collection["frozen_runtime_hashes"]

        # Validate before and after payload checks plus accepted source checks.
        for rel in ("payload-before.status.json", "payload-after.status.json"):
            assert load_json(root / "runs/2295087" / rel)["returncode"] == 0
        for ranks in (40, 48):
            for phase in ("before", "after"):
                assert load_json(root / f"runs/2295087/accepted-source-{ranks}-{phase}.status.json")["returncode"] == 0
            assert load_json(root / f"runs/2295087/source-after-{ranks}.json")["passed"]
        final = load_json(root / "runs/2295087/comparison.json")
        assert final["passed"] and final["complete_four_arm_comparison"]
        runtime_before = load_json(root / "runs/2295087/runtime-before.json")
        runtime_after = load_json(root / "runs/2295087/runtime-after.json")
        assert runtime_before["libraries"] == runtime_after["libraries"]
        assert runtime_before["tools"] == runtime_after["tools"]

        spec = importlib.util.spec_from_file_location("native_output", EXPERIMENT / "native_output.py")
        native = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(native)
        means, interval_counts, force_rows = {}, {}, {}
        for arm in ARMS:
            ranks = 40 if "candidate40" in arm else 48
            _, timings, forces, _ = native.review_native_output(
                root / "runs/2295087/arms" / arm, expected_ranks=ranks
            )
            assert len(timings) == 39 and len(forces) == 40
            means[arm] = statistics.mean(timings)
            interval_counts[arm] = len(timings)
            force_rows[arm] = len(forces)

        ranks = {arm: cpu_masks(root, arm, 40 if "candidate40" in arm else 48) for arm in ARMS}
        assert ranks["B1-candidate40"] == ranks["B2-candidate40"]
        preflight = load_json(root / "runs/2295087/probes/balanced40-placement.json")
        assert preflight["passed"] and preflight["rank_counts_by_NUMA_node"] == {"node0": 20, "node1": 20}
        placement = {}
        for arm in ("B1-candidate40", "B2-candidate40"):
            d = load_json(root / "runs/2295087/arms" / arm / "placement-validation.json")
            assert d["passed"] and d["rank_counts_by_NUMA_node"] == {"node0": 20, "node1": 20}
            placement[arm] = d["rank_counts_by_NUMA_node"]

        candidate = (means["B1-candidate40"] + means["B2-candidate40"]) / 2
        control = (means["A1-control48"] + means["A2-control48"]) / 2
        comparison = (candidate / control - 1) * 100
        candidate_drift = (means["B2-candidate40"] / means["B1-candidate40"] - 1) * 100
        control_drift = (means["A2-control48"] / means["A1-control48"] - 1) * 100
        telemetry = {arm: telemetry_summary(root, arm) for arm in ARMS}
        result = {
            "job_id": "2295087",
            "overall_measurement_valid": True,
            "raw_archive_sha256_verified": True,
            "raw_collected_file_hashes_verified": len(entries),
            "frozen_payload_hashes_verified": len(frozen),
            "payload_before_after": "PASS",
            "accepted_source_before_after_40_and_48": "PASS",
            "source_after_40_and_48": "PASS",
            "runtime_library_and_tool_identity_before_after": "PASS",
            "native_output_api": {arm: "PASS" for arm in ARMS},
            "arms": {
                arm: {"ranks": 40 if "candidate40" in arm else 48,
                      "steps": 40, "intervals": interval_counts[arm],
                      "mean_seconds_per_step": means[arm], "force_rows": force_rows[arm]}
                for arm in ARMS
            },
            "balanced40_preflight_proof_by_numa_node": preflight["rank_counts_by_NUMA_node"],
            "balanced40_actual_proof_by_numa_node": placement,
            "candidate_exact_rank_to_CPU_masks_repeat_equal": True,
            "pooled_candidate_mean_seconds_per_step": candidate,
            "pooled_control_mean_seconds_per_step": control,
            "candidate_vs_control_percent_slower": comparison,
            "candidate_repeat_drift_percent_B1_to_B2": candidate_drift,
            "control_repeat_drift_percent_A1_to_A2": control_drift,
            "telemetry": telemetry,
            "interpretation": "Complete matched configuration comparison, but the large candidate repeat drift and identical rank-to-CPU masks with divergent timings make a causal NUMA claim unsupported. Candidate is slower pooled and is not a winner.",
        }
        (HERE / "REVIEW.json").write_text(json.dumps(result, indent=2) + "\n")
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
