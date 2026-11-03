#!/usr/bin/env python3
"""Replay local hashes and NUMA-policy qualification evidence for job 2294675."""
from __future__ import annotations

import datetime
import hashlib
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXPERIMENT = HERE.parent
COLLECTED = HERE / "collected"
RUN = COLLECTED / "runs" / "2294675"
COLLECTION = json.loads((HERE / "collection.json").read_text())
APPROVED_SYMLINKS = {
    "constant/polyMesh": "/global/exafs/groups/rdmaworkshop/2026hpcai-openfoam/occDrivAer/polyMesh"
}
ARM_ORDER = ["A1-inherited", "B1-interleave-all", "B2-interleave-all", "A2-inherited"]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(2 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def node_values(snapshot: dict) -> dict:
    result = {}
    for node_id, row in snapshot["nodes"].items():
        assert row["available"] is True
        result[node_id] = {
            "FilePages_kB": row["meminfo"]["FilePages"]["value"],
            "interleave_hit": row["numastat"]["interleave_hit"],
        }
    return result


def main() -> dict:
    assert COLLECTION["job_id"] == "2294675"
    assert "2294675|COMPLETED|0:0|216|56|iris001" in COLLECTION["accounting"]
    assert len(COLLECTION["files"]) == 10

    verified = []
    for relative, expected in COLLECTION["files"].items():
        data = (COLLECTED / relative).read_bytes()
        assert len(data) == expected["bytes"], f"size mismatch: {relative}"
        assert sha256_bytes(data) == expected["sha256"], f"SHA-256 mismatch: {relative}"
        verified.append(relative)

    archive = HERE / "raw.tar.gz"
    assert sha256_file(archive) == COLLECTION["archive_sha256"]

    frozen_matches = []
    assert len(COLLECTION["frozen_hashes"]) == 7
    for relative, expected_hash in COLLECTION["frozen_hashes"].items():
        path = EXPERIMENT / relative
        assert path.is_file(), f"frozen file missing: {relative}"
        assert sha256_file(path) == expected_hash, f"frozen hash mismatch: {relative}"
        frozen_matches.append(relative)

    source_before = json.loads((RUN / "source-before-inventory.json").read_text())
    source_after = json.loads((RUN / "source-after-inventory.json").read_text())
    accepted_main = json.loads((EXPERIMENT / "accepted-source-manifest.json").read_text())
    accepted_supp = json.loads((EXPERIMENT / "supplementary-source-manifest.json").read_text())
    assert source_before == source_after == accepted_main
    assert len(source_before["files"]) == 1040
    assert source_before["symlinks"] == APPROVED_SYMLINKS
    assert len(accepted_supp["files"]) == 13

    qualification = json.loads((RUN / "qualification.json").read_text())
    assert qualification["state"] == "completed"
    assert qualification["scored_result"] is False
    assert qualification["source_after_matches"] is True
    assert qualification["source_file_count"] == 1040
    assert qualification["supplementary_file_count"] == 13
    assert qualification["topology"] == {"count": 2, "node_ids": [0, 1]}
    assert qualification["arms_order"] == ARM_ORDER
    assert qualification["source_manifest_sha256"] == COLLECTION["frozen_hashes"]["accepted-source-manifest.json"]
    assert qualification["supplementary_manifest_sha256"] == COLLECTION["frozen_hashes"]["supplementary-source-manifest.json"]
    assert qualification["inherited_policy"]["policy"] == "default"
    assert qualification["inherited_policy"]["membind_nodes"] == [0, 1]
    assert qualification["interleave_child_policy"]["policy"] == "interleave"
    assert qualification["interleave_child_policy"]["interleave_nodes"] == [0, 1]
    assert qualification["process_masks"]["Cpus_allowed_list"] == "0-55"
    assert qualification["process_masks"]["Mems_allowed_list"] == "0-1"

    arm_results = []
    for arm_name in ARM_ORDER:
        result = json.loads((RUN / f"{arm_name}.json").read_text())
        assert result["passed"] is True
        assert result["regular_files"] == 1040
        assert result["supplementary_files_verified"] == 13
        assert result["no_source_inode_reuse"] is True
        assert result["symlinks"] == APPROVED_SYMLINKS
        expected_policy = "interleave" if arm_name.startswith("B") else "default"
        expected_nodes = [0, 1] if arm_name.startswith("B") else []
        policy = result["effective_memory_policy"]
        assert policy["policy"] == expected_policy
        assert policy["interleave_nodes"] == expected_nodes
        assert policy["membind_nodes"] == [0, 1]
        assert result["manifest_sha256"] == qualification["source_inventory_sha256"]
        assert set(result["numa_snapshots"]) == {"before_copy", "after_copy_before_hash", "after_hash"}

        snapshots = result["numa_snapshots"]
        before = node_values(snapshots["before_copy"])
        after_copy = node_values(snapshots["after_copy_before_hash"])
        after_hash = node_values(snapshots["after_hash"])
        deltas = {}
        for node_id in ("0", "1"):
            b = before[node_id]
            c = after_copy[node_id]
            h = after_hash[node_id]
            copy_file_delta = c["FilePages_kB"] - b["FilePages_kB"]
            hash_file_delta = h["FilePages_kB"] - b["FilePages_kB"]
            copy_interleave_delta = c["interleave_hit"] - b["interleave_hit"]
            hash_interleave_delta = h["interleave_hit"] - c["interleave_hit"]
            assert copy_file_delta >= 0 and hash_file_delta >= copy_file_delta
            assert copy_interleave_delta >= 0 and hash_interleave_delta >= 0
            deltas[node_id] = {
                "FilePages_delta_after_copy_GiB": copy_file_delta / (1024 ** 2),
                "FilePages_delta_after_hash_GiB": hash_file_delta / (1024 ** 2),
                "interleave_hit_delta_during_copy": copy_interleave_delta,
                "interleave_hit_delta_during_hash": hash_interleave_delta,
            }

        copy_s = float(result["copy_seconds"])
        hash_s = float(result["destination_hash_verify_seconds"])
        assert math.isfinite(copy_s) and copy_s > 0
        assert math.isfinite(hash_s) and hash_s > 0
        arm_results.append({
            "arm": arm_name,
            "policy": expected_policy,
            "interleave_nodes": expected_nodes,
            "clone_passed": result["passed"],
            "copied_regular_files": result["regular_files"],
            "supplementary_regular_files_verified": result["supplementary_files_verified"],
            "approved_symlink": result["symlinks"],
            "no_source_inode_reuse": result["no_source_inode_reuse"],
            "copy_seconds": copy_s,
            "hash_verify_seconds": hash_s,
            "whole_node_deltas_by_numa_node": deltas,
        })

    qualification_arms = qualification["arms"]
    assert [row["name"] for row in qualification_arms] == ARM_ORDER
    assert all(row["returncode"] == 0 for row in qualification_arms)

    # The qualification process itself is intentionally copy/hash-only.
    assert all("simpleFoam" not in json.dumps(row) for row in qualification_arms)
    total_cpu_hours = 216 * 56 / 3600
    result = {
        "reviewed_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "job_id": "2294675",
        "scheduler": {"state": "COMPLETED", "exit_code": "0:0", "elapsed_seconds": 216,
                      "allocated_cpus": 56, "node": "iris001"},
        "all_collected_file_hashes_verified": True,
        "collected_file_count": len(verified),
        "raw_archive_hash_verified": True,
        "frozen_runtime_and_source_manifest_hashes_verified": len(frozen_matches),
        "source_inventory": {
            "before_after_identical": True,
            "accepted_manifest_matches_before_and_after": True,
            "main_regular_files": 1040,
            "supplementary_regular_files_verified_per_arm": 13,
            "total_regular_source_inputs": 1053,
            "approved_symlink_count": 1,
            "approved_symlinks": APPROVED_SYMLINKS,
            "source_after_matches_gate": True,
        },
        "order": ARM_ORDER,
        "arms": arm_results,
        "qualification": {
            "passed": True,
            "state": qualification["state"],
            "preparation_only": True,
            "actual_inherited_policy": qualification["inherited_policy"],
            "actual_interleave_child_policy": qualification["interleave_child_policy"],
            "four_actual_copy_hash_arms_succeeded": True,
            "no_solver_run": True,
        },
        "cost": {"allocation_wall_seconds": 216, "allocated_cpus": 56,
                 "allocated_cpu_hours_arithmetic": total_cpu_hours,
                 "is_billed_site_SU": False},
        "missing_or_uncollected": [
            "No solver timing or performance result; this job runs only preparation copy and checksum phases.",
            "No per-process or per-file page residency; FilePages and numastat counters are whole-node cumulative values.",
            "No memory-bandwidth or hardware-cycle measurements.",
            "No causal attribution of cache/page placement to the copied files; unrelated node activity is not excluded.",
        ],
        "interpretation": "The child memory-policy treatment was actually qualified and the node-level FilePages/interleave_hit response was consistent across repeats. This does not prove placement of the specific files or predict solver performance.",
    }
    (HERE / "REVIEW.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({
        "job_id": result["job_id"],
        "verified_collected_files": result["collected_file_count"],
        "verified_frozen_hashes": result["frozen_runtime_and_source_manifest_hashes_verified"],
        "source_after_matches": result["source_inventory"]["source_after_matches_gate"],
        "arms_passed": [row["arm"] for row in arm_results if row["clone_passed"]],
        "allocated_cpu_hours_arithmetic": total_cpu_hours,
    }, indent=2))
    return result


if __name__ == "__main__":
    main()
