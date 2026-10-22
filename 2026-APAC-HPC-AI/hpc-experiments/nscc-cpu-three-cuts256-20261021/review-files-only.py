"""Review collected native evidence without claiming terminal PBS accounting."""
from pathlib import Path
import datetime
import hashlib
import json
import re
import statistics


ROOT = Path(__file__).resolve().parent
EXPECTED_CELLS = 65_334_765
ROLES = ("hierarchical", "default_scotch", "node_scotch")
GRAPH_NAMES = {"hierarchical": "hierarchical", "default_scotch": "default_scotch", "node_scotch": "node_scotch"}


def read_json(path):
    return json.loads(path.read_text())


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(condition, message):
    if not condition:
        raise AssertionError(message)


submission = read_json(ROOT / "submission.json")
job = submission["stdout"].strip()
check(job and re.fullmatch(r"\d+\.pbs\w+", job), "invalid PBS job identity in submission receipt")
collection = ROOT / "collected-files-only" / job
check(collection.is_dir(), f"sealed collection is unavailable: {collection}")

# Verify every collected evidence member before interpreting any of it.
evidence_seal = read_json(collection / "evidence-sha256.json")
for relative, digest in evidence_seal.items():
    path = collection / relative
    check(path.is_file(), f"sealed evidence member missing: {relative}")
    check(sha256(path) == digest, f"evidence seal mismatch: {relative}")

check(submission["ncpus"] == 32 and submission["ngpus"] == 0 and
      submission["mesh_split_ranks"] == 256 and submission["cases"] == 3 and
      submission["maximum_SU"] == 24,
      "submission receipt does not describe the expected three-cut allocation")

# The complete deployed bundle, including all three role payloads and review tools,
# must match the pre-submission hash manifest.
payload_hashes = read_json(ROOT / "payload-sha256.json")
for relative, digest in payload_hashes.items():
    path = collection / relative
    check(path.is_file() and sha256(path) == digest, f"submitted payload mismatch: {relative}")

mesh = read_json(collection / "mesh-identity.json")
check(mesh["archive_md5"] == "50393a15d84f53255fda85ac702390e9", "official archive MD5 mismatch")
check(mesh["archive_sha256"] == "ef30fa8405dbaab77185ace2521b1bedc5650f245e40d7451259a5ac773a5376",
      "official archive SHA256 mismatch")
members = mesh["unpacked_members_match_archive"]
member_names = {Path(row["file"]).name for row in members}
check(len(members) >= 8 and {"points", "faces", "owner", "neighbour", "boundary"} <= member_names,
      "archive member identity is incomplete")
check(all(row.get("bytes", 0) > 0 and re.fullmatch(r"[0-9a-f]{64}", row.get("sha256", ""))
          for row in members), "archive member identity contains invalid size/hash data")

inputs = read_json(ROOT / "payload" / "case-inputs.json")
graphs = read_json(collection / "interface-summary.json")
partitions = {}
for role in ROLES:
    spec = inputs[role]
    artifact = collection / "artifacts" / role
    ready = read_json(artifact / "CUT_READY.json")
    check(ready["ranks"] == 256 and ready["total_cells"] == EXPECTED_CELLS,
          f"{role}: CUT_READY identity/cell total mismatch")
    check(ready["method"] == spec["method"], f"{role}: method mismatch")
    check(ready.get("hierarchical_factors") == spec["hierarchical_factors"] and
          ready.get("domains") == spec["domains"], f"{role}: CUT_READY decomposition identity mismatch")
    check("restored initial fields" in ready.get("scope", ""),
          f"{role}: CUT_READY does not attest restored initial fields")

    log = (artifact / "logFiles" / "decomposePar.log").read_text()
    check(re.search(r"^End\s*$", log, re.M) and "FOAM FATAL" not in log,
          f"{role}: native decomposePar did not end cleanly")
    check("OPENFOAM=2512" in log and "scalar=64" in log,
          f"{role}: native OpenFOAM version/precision evidence missing")
    check(f"{spec['method']} [256]" in log, f"{role}: native method/rank log mismatch")

    cells = [int(value) for value in re.findall(r"^    Number of cells\s*=\s*(\d+)", log, re.M)]
    faces = [int(value) for value in re.findall(r"^    Number of processor faces\s*=\s*(\d+)", log, re.M)]
    patches = [int(value) for value in re.findall(r"^    Number of processor patches\s*=\s*(\d+)", log, re.M)]
    check(len(cells) == len(faces) == len(patches) == 256 and sum(cells) == EXPECTED_CELLS,
          f"{role}: native log does not contain 256 complete partition records")
    # The collector intentionally excludes processor* trees. Their complete rank
    # and restored-field checks are evidenced by the sealed native CUT_READY file,
    # emitted only after the frozen check-cut.py passed on the allocated compute.
    for relative, expected in spec["sha256"].items():
        # Inputs are copied into the artifact by the native job; their source bytes
        # must remain identical to the sealed payload's case inputs.
        src = artifact / relative
        payload_path = ROOT / "payload" / "cases" / role / relative
        check(payload_path.is_file() and sha256(payload_path) == expected,
              f"{role}: submitted case source hash mismatch: {relative}")
        check(src.is_file() and sha256(src) == expected,
              f"{role}: collected source/system differs from submitted bytes: {relative}")

    restore_log = (artifact / "logFiles" / "restore0Dir.log").read_text()
    check("Restore 0/" in restore_log, f"{role}: restore0Dir completion marker missing")

    graph = read_json(collection / f"graph-{GRAPH_NAMES[role]}.json")
    summary = graphs[role]
    check(graph["ranks"] == summary["ranks"] == 256, f"{role}: graph rank identity mismatch")
    expected_boundaries = {
        f"processor{rank}/constant/polyMesh/boundary" for rank in range(256)
    }
    check(set(graph["boundary_sha256"]) == expected_boundaries and
          all(re.fullmatch(r"[0-9a-f]{64}", value)
              for value in graph["boundary_sha256"].values()),
          f"{role}: incomplete or malformed sealed boundary graph")
    edge_pairs = [(edge["a"], edge["b"]) for edge in graph["edges"]]
    check(all(isinstance(a, int) and isinstance(b, int) and 0 <= a < b < 256
              for a, b in edge_pairs), f"{role}: invalid graph edge endpoints")
    check(len(edge_pairs) == len(set(edge_pairs)), f"{role}: duplicate undirected graph edge")
    check(all(isinstance(edge["faces"], int) and edge["faces"] > 0
              for edge in graph["edges"]), f"{role}: invalid graph edge face count")
    check(sum(edge["faces"] for edge in graph["edges"]) == summary["unique_interface_faces"],
          f"{role}: graph edge face total differs from summary")
    check(sum(edge["faces"] for edge in graph["edges"] if edge["cross_group"]) ==
          summary["unique_cross_group_interface_faces"], f"{role}: cross-group graph total mismatch")
    check(all(edge["cross_group"] == (edge["a"] // 128 != edge["b"] // 128)
              for edge in graph["edges"]), f"{role}: graph grouping mismatch")
    check(summary["unique_interface_faces"] == sum(faces) // 2 and
          summary["max_rank_interface_faces"] == max(faces) and
          summary["max_rank_processor_patches"] == max(patches),
          f"{role}: graph totals do not match native decomposePar logs")
    partitions[role] = {
        "min_cells": min(cells), "max_cells": max(cells),
        "mean_cells": statistics.mean(cells),
        "max_cell_excess_fraction": max(cells) / statistics.mean(cells) - 1,
        "native_total_cells": sum(cells),
        "unique_interface_faces": summary["unique_interface_faces"],
        "unique_cross_group_interface_faces": summary["unique_cross_group_interface_faces"],
        "max_rank_interface_faces": summary["max_rank_interface_faces"],
        "max_rank_processor_patches": summary["max_rank_processor_patches"],
    }

# Check the native job-level pass marker and role-specific check-cut markers.
stdout_candidates = sorted(collection.glob("tu-cpu-cuts256.o*"))
check(stdout_candidates, "native PBS stdout evidence missing")
native_stdout = "\n".join(path.read_text(errors="replace") for path in stdout_candidates)
check("CPU_THREE_CUTS256_PASS" in native_stdout, "native three-cut pass marker missing")
for role in ROLES:
    check(f"{role}" in native_stdout, f"native stdout does not identify role {role}")

output = {
    "reviewed_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "job": job,
    "state": "NATIVE_THREE_CUTS_EVIDENCE_PASS_SCHEDULER_HISTORY_UNAVAILABLE",
    "archive": {"md5": mesh["archive_md5"], "sha256": mesh["archive_sha256"], "member_count": len(members)},
    "partition_stats": partitions,
    "graph_summary": graphs,
    "node_aware_tradeoffs_advisory": {
        "cross_group_faces_vs_default_fraction": (
            partitions["node_scotch"]["unique_cross_group_interface_faces"] /
            partitions["default_scotch"]["unique_cross_group_interface_faces"] - 1
        ),
        "total_interface_faces_vs_default_fraction": (
            partitions["node_scotch"]["unique_interface_faces"] /
            partitions["default_scotch"]["unique_interface_faces"] - 1
        ),
        "max_cell_excess_fraction": partitions["node_scotch"]["max_cell_excess_fraction"],
        "interpretation": "Descriptive partition-graph tradeoffs only; synthetic 10:1 weighting is not a performance model.",
    },
    "maximum_reserved_SU": 24,
    "actual_walltime": "unavailable: terminal PBS accounting was not retained",
    "actual_posted_cost": "unknown",
    "limits": [
        "These are native partition and field-restore checks; no candidate initialization or solve was run.",
        "This evidence review does not establish terminal PBS state, batch exit status, or allocation resource usage; scheduler history is unavailable.",
        "No exact batch elapsed time or posted SU cost is reported. The 24 SU value is the submitted maximum reservation only.",
        "The 10:1 graph weight is synthetic. Rank groups imply physical nodes only when placement is independently verified.",
        "Graph faces do not measure traffic, MPI wait, page residency, critical path, speedup, counters, bandwidth, or power.",
        "Processor field and mesh trees were not downloaded; their checks are represented by the sealed native check-cut.py result and CUT_READY/job pass markers.",
        "Reciprocity was asserted by the frozen native graph collector; unique undirected edge output cannot independently prove the discarded reciprocal records.",
    ],
}
(ROOT / "review-files-only.json").write_text(json.dumps(output, indent=2) + "\n")
print(json.dumps(output, indent=2))
