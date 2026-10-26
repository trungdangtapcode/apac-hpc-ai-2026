#!/usr/bin/env python3
"""Replay job 25999546 from its archive and collection manifest only."""
from collections import Counter
from pathlib import Path, PurePosixPath
import hashlib
import json
import re
import tarfile

HERE = Path(__file__).resolve().parent
ARCHIVE = HERE / "raw-records.tar.gz"
MANIFEST = HERE / "collection.json"
BATCH_OUTPUT = HERE / "batch-output.txt"
BATCH_METADATA = HERE / "batch-output.metadata.json"
OUTPUT = HERE / "review.json"
BASE = "runs/25999546/"
RANKS = 512
ARMS = ("bare", "global", "command_specific")

manifest = json.loads(MANIFEST.read_text())
assert manifest["job_id"] == "25999546.pbs101"
archive_sha256 = hashlib.sha256(ARCHIVE.read_bytes()).hexdigest()
assert archive_sha256 == manifest["archive_sha256"], "archive digest mismatch"

# Hash every archive file against the collection manifest before analysis.
with tarfile.open(ARCHIVE, "r:gz") as tar:
    members = tar.getmembers()
    files = [m for m in members if m.isfile()]
    assert len(files) == len(manifest["files"]) == 4630
    assert sum(m.size for m in files) == sum(v["bytes"] for v in manifest["files"].values()) == 1995910
    names = [m.name for m in files]
    assert len(names) == len(set(names)), "duplicate archive file member"
    assert set(names) == set(manifest["files"]), "archive/manifest member set differs"
    for member in files:
        path = PurePosixPath(member.name)
        assert not path.is_absolute() and ".." not in path.parts
        assert member.isfile(), "non-regular archive member"
        data = tar.extractfile(member).read()
        expected = manifest["files"][member.name]
        assert len(data) == expected["bytes"], f"length mismatch: {member.name}"
        assert hashlib.sha256(data).hexdigest() == expected["sha256"], f"hash mismatch: {member.name}"
    raw = {m.name: tar.extractfile(m).read() for m in files}

def text(rel):
    return raw[BASE + rel].decode("utf-8")

def record(rel):
    return json.loads(text(rel))

def rank_records(rel, phase):
    prefix = BASE + rel + "/rank-"
    rows = []
    for name, data in raw.items():
        if name.startswith(prefix) and name.endswith(".json"):
            obj = json.loads(data)
            idx = int(name[len(prefix):-5])
            rows.append((idx, obj))
    assert len(rows) == RANKS, f"{rel}: expected {RANKS} rows, got {len(rows)}"
    assert sorted(i for i, _ in rows) == list(range(RANKS)), f"{rel}: rank filenames incomplete"
    for idx, row in rows:
        assert row["phase"] == phase, f"{rel}: phase mismatch at file rank {idx}"
    return {idx: row for idx, row in rows}

def host_counts(rows, rank_key):
    return dict(sorted(Counter(row["host"] for row in rows.values()).items()))

arm_results = {}
all_host_layouts = []
for arm in ARMS:
    py = rank_records(f"arms/{arm}/python", "python_entry")
    pre = rank_records(f"arms/{arm}/native/pre", "before_mpi_init_thread")
    post = rank_records(f"arms/{arm}/native", "after_mpi_init_thread")

    assert all(r["affinity_status"] == 0 and r["affinity_error"] is None for r in py.values())
    assert all(r["affinity_status"] == 0 and r["errno"] == 0 for r in pre.values())
    assert all(r["affinity_status"] == 0 and r["errno"] == 0 for r in post.values())
    assert all(len(r["cpus"]) == 1 for r in py.values())
    assert all(len(r["cpus"]) == 1 for r in pre.values())
    assert all(len(r["cpus"]) == 256 and r["cpus"] == list(range(256)) for r in post.values())

    # PMI identity links the Python entry records to the native pre-init records.
    py_by_pmi = {r["pmi_rank"]: r for r in py.values()}
    pre_by_pmi = {r["pmi_rank"]: r for r in pre.values()}
    assert len(py_by_pmi) == len(pre_by_pmi) == RANKS
    assert set(py_by_pmi) == set(pre_by_pmi) == set(range(RANKS))
    for pmi in range(RANKS):
        a, b = py_by_pmi[pmi], pre_by_pmi[pmi]
        assert a["host"] == b["host"] and a["cpus"] == b["cpus"], f"{arm}: Python/pre mismatch at PMI rank {pmi}"

    # Before MPI_Init_thread, the probe's rank field is the PMI rank. After init,
    # MPI world rank is available; PMI rank provides the per-process crosswalk.
    assert all(r["rank"] == r["pmi_rank"] for r in pre.values())
    assert sorted(r["rank"] for r in post.values()) == list(range(RANKS))
    post_by_pmi = {r["pmi_rank"]: r for r in post.values()}
    assert len(post_by_pmi) == RANKS and set(post_by_pmi) == set(range(RANKS))
    world_by_pmi = {pmi: row["rank"] for pmi, row in post_by_pmi.items()}
    assert len(set(world_by_pmi.values())) == RANKS
    for pmi in range(RANKS):
        assert pre_by_pmi[pmi]["host"] == post_by_pmi[pmi]["host"], f"{arm}: host changed for PMI rank {pmi}"

    py_hosts = host_counts(py, "pmi_rank")
    pre_hosts = host_counts(pre, "rank")
    post_hosts = host_counts(post, "rank")
    assert len(py_hosts) == len(pre_hosts) == len(post_hosts) == 4
    assert set(py_hosts.values()) == set(pre_hosts.values()) == set(post_hosts.values()) == {128}
    unique_py_cpu_per_host = {}
    unique_pre_cpu_per_host = {}
    for host in py_hosts:
        unique_py_cpu_per_host[host] = len({r["cpus"][0] for r in py.values() if r["host"] == host})
        unique_pre_cpu_per_host[host] = len({r["cpus"][0] for r in pre.values() if r["host"] == host})
    assert set(unique_py_cpu_per_host.values()) == set(unique_pre_cpu_per_host.values()) == {128}

    arm_results[arm] = {
        "python_records": RANKS,
        "native_pre_records": RANKS,
        "native_post_records": RANKS,
        "pmi_rank_range_unique": [0, RANKS - 1],
        "native_world_rank_range_unique": [0, RANKS - 1],
        "native_post_world_ranks_unique": True,
        "native_post_pmi_ranks_unique": True,
        "native_pre_rank_field_equals_pmi_rank": True,
        "world_rank_to_pmi_rank_crosswalk_after_init": "Complete one-to-one mapping; linked to pre-init records by PMI rank.",
        "world_rank_pmi_nonidentity_pairs": sum(world != pmi for pmi, world in world_by_pmi.items()),
        "python_native_pre_post_host_match_by_pmi": True,
        "python_to_native_pre_cpu_match_by_pmi": True,
        "host_record_counts_each_phase": py_hosts,
        "unique_logical_cpu_ids_per_host_python": unique_py_cpu_per_host,
        "unique_logical_cpu_ids_per_host_native_pre": unique_pre_cpu_per_host,
        "python_and_native_pre_mask_widths": [1],
        "native_post_mask_widths": [256],
        "affinity_status_zero_all_rows": True,
        "native_errno_zero_all_rows": True,
    }
    all_host_layouts.append(py_hosts)

# Six MPI probe invocations: Python and native probe for each launcher-option arm.
returns = [json.loads(line) for line in text("command-return-codes.jsonl").splitlines()]
assert all(x["return_code"] == 0 for x in returns)
return_map = {x["command"]: x["return_code"] for x in returns}
probe_commands = [f"{arm}_{kind}_capture" if kind == "python" else f"{arm}_mpi_init_probe"
                  for arm in ARMS for kind in ("python", "native")]
assert len(probe_commands) == 6
# Phase names in this run use *_capture for Python and *_mpi_init_probe for native.
for arm in ARMS:
    assert return_map[f"{arm}_python_capture"] == 0
    assert return_map[f"{arm}_mpi_init_probe"] == 0

phases = [line.split("\t") for line in text("phases.tsv").splitlines()]
assert phases and all(len(row) == 3 for row in phases)
phase_names = {row[2] for row in phases}
for arm in ARMS:
    assert f"{arm}_python_capture" in phase_names
    assert f"{arm}_mpi_init_probe" in phase_names

# Verify source checks were clean and identical before/after, including pinned files.
before = text("payload-sha256-before.txt")
after = text("payload-sha256-after.txt")
pinned_before = text("pinned-source-before.txt")
pinned_after = text("pinned-source-after.txt")
assert before == after
assert pinned_before == pinned_after
assert all(line.endswith(": OK") for line in pinned_before.splitlines())
assert len(pinned_before.splitlines()) == 3

# PBS node file and retained terminal metadata.
node_hosts = text("pbs-nodefile.txt").splitlines()
assert len(node_hosts) == RANKS
node_counts = dict(sorted(Counter(node_hosts).items()))
assert len(node_counts) == 4 and set(node_counts.values()) == {128}
terminal = manifest["terminal"]
assert terminal["job_state"] == "F" and terminal["Exit_status"] == 0
assert str(terminal["project"]) == "59000042"
resources_used = terminal["resources_used"]
resource_list = terminal["Resource_List"]
wall = resources_used["walltime"]
wall_s = int(wall.split(":")[0]) * 3600 + int(wall.split(":")[1]) * 60 + int(wall.split(":")[2])
assert wall_s == 13
cores = int(resources_used["ncpus"])
charge_rate = float(resource_list["am_job_cache"] and json.loads(resource_list["am_job_cache"])["job.queue_charge_rate"])
estimated_su = cores * wall_s / 3600 * charge_rate

# The separately retained exact batch stdout is hash/length sealed and reports all arms.
batch_metadata = json.loads(BATCH_METADATA.read_text())
batch_bytes = BATCH_OUTPUT.read_bytes()
assert len(batch_bytes) == batch_metadata["bytes"]
assert hashlib.sha256(batch_bytes).hexdigest() == batch_metadata["sha256"]
batch_summary_rows = [json.loads(line.split("MPI_SUMMARY_JSON ", 1)[1]) for line in batch_bytes.decode().splitlines() if line.startswith("MPI_SUMMARY_JSON ")]
assert len(batch_summary_rows) == 3
assert all(x == {"world_size": 512, "ranks_with_capture_or_identity_errors": 0} for x in batch_summary_rows)
assert batch_bytes.decode().splitlines()[-1] == "COLLECTION_FINISHED"

# Per-run wall-clock timings and return codes for the six probe commands.
probe_timings = {}
for arm in ARMS:
    for kind, label in (("python", f"{arm}_python"), ("native", f"{arm}_native")):
        data = text(f"logs/{label}.time.txt")
        match = re.search(r"Elapsed \(wall clock\) time .*?: ([0-9:]+(?:\.[0-9]+)?)", data)
        assert match, f"missing resource timing for {label}"
        parts = match.group(1).split(":")
        seconds = sum(float(part) * 60 ** i for i, part in enumerate(reversed(parts)))
        assert "Exit status: 0" in data
        probe_timings[label] = seconds

result = {
    "job": "25999546.pbs101",
    "review_scope": "Local replay using collection.json and raw-records.tar.gz plus the separately retained exact PBS stdout and its digest metadata; no scheduler or remote access.",
    "collection_integrity": {
        "archive_sha256_matches_manifest": True,
        "archive_sha256": archive_sha256,
        "archive_bytes": ARCHIVE.stat().st_size,
        "manifest_file_count": len(manifest["files"]),
        "manifest_total_file_bytes": sum(v["bytes"] for v in manifest["files"].values()),
        "all_member_lengths_and_sha256_verified": True,
        "archive_directory_entries": len(members) - len(files),
    },
    "arms": arm_results,
    "launcher_option_placement_result": "Bare, deprecated global, and command-specific arms all had singleton masks at Python entry and native pre-MPI_Init_thread; each native post-init mask covered CPUs 0-255. This run found no difference among the three option placements.",
    "pbs_stdout_crosscheck": {
        "metadata_path": BATCH_METADATA.name,
        "stdout_path": BATCH_OUTPUT.name,
        "sha256_and_bytes_match_metadata": hashlib.sha256(BATCH_OUTPUT.read_bytes()).hexdigest() == json.loads(BATCH_METADATA.read_text())["sha256"] and BATCH_OUTPUT.stat().st_size == json.loads(BATCH_METADATA.read_text())["bytes"],
        "bytes": BATCH_OUTPUT.stat().st_size,
        "sha256": hashlib.sha256(BATCH_OUTPUT.read_bytes()).hexdigest(),
        "summary_count": sum(1 for line in BATCH_OUTPUT.read_text().splitlines() if line.startswith("MPI_SUMMARY_JSON ")),
        "summaries": [json.loads(line.split("MPI_SUMMARY_JSON ", 1)[1]) for line in BATCH_OUTPUT.read_text().splitlines() if line.startswith("MPI_SUMMARY_JSON ")],
        "collection_finished_marker": BATCH_OUTPUT.read_text().splitlines()[-1] == "COLLECTION_FINISHED",
    },
    "command_results": {
        "all_recorded_commands_return_code_zero": True,
        "recorded_command_count": len(returns),
        "six_launcher_probe_commands_return_code_zero": True,
        "six_probe_elapsed_seconds": probe_timings,
    },
    "source_integrity": {
        "payload_hash_before_equals_after": True,
        "three_pinned_source_files_verified_before_and_after": True,
        "pinned_verification_records": pinned_before.splitlines(),
    },
    "nodefile": {
        "slots": len(node_hosts),
        "host_counts": node_counts,
        "matches_each_arm_host_counts": True,
    },
    "scheduler": {
        "state": terminal["job_state"],
        "exit_status": terminal["Exit_status"],
        "project": terminal["project"],
        "resources_used": resources_used,
        "requested_resources": {k: v for k, v in resource_list.items() if k in ("select", "walltime", "ncpus", "mpiprocs", "ngpus", "mem", "nodect", "place", "queue_charge_rate")},
        "estimated_su_from_512_cores_x_13_seconds_at_rate_1": round(512 * 13 / 3600, 9),
        "estimated_su_from_terminal_metadata": round(estimated_su, 9),
        "posted_charge": "Not present in this collection; estimate is not posted accounting.",
        "resource_list_full": resource_list,
    },
    "collection_limits": {
        "scope_from_collection": manifest["scope"],
        "included_files": "Text diagnostics and per-rank records only.",
        "not_collected": ["runtime environment snapshot", "compiled native executable", "system-call trace", "physical-core topology"],
        "collection_timeout_correction": "The earlier Python per-file pack attempt timed out without retaining an archive. The retained collection used native tar; the compressed archive digest and every member hash/length were verified here.",
        "inference_limits": [
            "Affinity results establish process masks, not physical-core uniqueness; no core topology was collected.",
            "This method-0 order-control run does not prove all method-3 behavior or identify the cause of the earlier method-3 pre-exec failure.",
            "The observed post-init expansion does not prove MPI_Init_thread is the sole cause; no system-call caller trace was collected.",
            "This is a short diagnostic, not an OpenFOAM performance or solver result.",
        ],
    },
    "decision": {
        "launcher_option_placement_branch": "Close this unchanged branch: the three option placements produced the same clean pre-init masks and the same 256-CPU post-init masks in this run.",
        "next_hypothesis": "Use a bounded one-rank strace observer matched to the same launcher and probe sequence to identify which process or library changes affinity around initialization.",
    },
}
OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
print(json.dumps({
    "output": str(OUTPUT),
    "files_verified": result["collection_integrity"]["manifest_file_count"],
    "bytes_verified": result["collection_integrity"]["manifest_total_file_bytes"],
    "arms": {a: {"python_pre": arm_results[a]["python_records"], "native_pre": arm_results[a]["native_pre_records"], "native_post": arm_results[a]["native_post_records"], "post_width": arm_results[a]["native_post_mask_widths"]} for a in ARMS},
    "terminal": [terminal["job_state"], terminal["Exit_status"], wall_s],
    "estimated_su": round(estimated_su, 9),
}, indent=2))
