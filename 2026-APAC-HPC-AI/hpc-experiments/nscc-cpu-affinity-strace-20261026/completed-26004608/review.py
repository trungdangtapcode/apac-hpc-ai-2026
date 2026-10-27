"""Replay job 26004608 from the retained native archive and manifest."""
from collections import Counter, defaultdict
from pathlib import Path, PurePosixPath
import hashlib
import json
import re
import tarfile

HERE = Path(__file__).resolve().parent
ARCHIVE = HERE / "raw-records.tar.gz"
COLLECTION = json.loads((HERE / "collection.json").read_text())
OUTPUT = HERE / "review.json"
BASE = "runs/26004608/"
RANKS = 512
ARMS = ("untraced_control", "rank0_straced")

assert COLLECTION["job_id"] == "26004608.pbs101"
archive_hash = hashlib.sha256(ARCHIVE.read_bytes()).hexdigest()
assert archive_hash == COLLECTION["archive_sha256"]

raw = {}
with tarfile.open(ARCHIVE, "r:gz") as tar:
    files = [m for m in tar.getmembers() if m.isfile()]
    assert len(files) == len(COLLECTION["files"]) == 3102
    assert sum(m.size for m in files) == sum(v["bytes"] for v in COLLECTION["files"].values()) == 1442271
    assert len({m.name for m in files}) == len(files)
    assert {m.name for m in files} == set(COLLECTION["files"])
    for member in files:
        path = PurePosixPath(member.name)
        assert not path.is_absolute() and ".." not in path.parts
        data = tar.extractfile(member).read()
        info = COLLECTION["files"][member.name]
        assert len(data) == info["bytes"]
        assert hashlib.sha256(data).hexdigest() == info["sha256"]
        raw[member.name] = data
assert all("/mpi-init-probe" not in name for name in raw)
assert all(not name.endswith("runtime-environment-whitelist.txt") for name in raw)

def text(rel):
    return raw[BASE + rel].decode("utf-8")

def records(rel):
    prefix = BASE + rel + "/rank-"
    found = {}
    for name, data in raw.items():
        if name.startswith(prefix) and name.endswith(".json"):
            idx = int(name[len(prefix):-5])
            assert idx not in found
            found[idx] = json.loads(data)
    assert sorted(found) == list(range(RANKS)), f"{rel}: rank files incomplete"
    return found

def mask_summary(rows):
    by_host = defaultdict(Counter)
    for row in rows.values():
        by_host[row["host"]][tuple(row["cpus"])] += 1
    result = {}
    for host, counts in sorted(by_host.items()):
        result[host] = {
            "record_count": sum(counts.values()),
                        "unique_masks": len(counts),
        }
        widths = Counter()
        for mask, n in counts.items():
            widths[len(mask)] += n
        result[host]["mask_width_counts"] = {str(k): v for k, v in sorted(widths.items())}
        # Keep only compact examples; complete bitmaps remain in the raw archive.
        result[host]["mask_examples"] = [
            {"width": len(mask), "first_cpu": mask[0] if mask else None,
             "last_cpu": mask[-1] if mask else None, "records": n}
            for mask, n in counts.most_common(3)
        ]
    return result

arm_results = {}
for arm in ARMS:
    entry = records(f"arms/{arm}/entry")
    pre = records(f"arms/{arm}/native/pre")
    post = records(f"arms/{arm}/native")
    assert {row["arm"] for row in entry.values()} == ({"control"} if arm == "untraced_control" else {"rank0-straced"})
    assert all(row["pmi_rank"] == idx for idx, row in entry.items())
    assert all(row["pmi_rank"] == idx and row["rank"] == idx
               for idx, row in pre.items())
    assert all(row["phase"] == "before_mpi_init_thread" for row in pre.values())
    assert all(row["phase"] == "after_mpi_init_thread" for row in post.values())
    assert all(row["affinity_status"] == 0 and row["errno"] == 0
               for row in list(pre.values()) + list(post.values()))
    assert all(len(row["cpus"]) > 0 and row["cpus"] == sorted(set(row["cpus"]))
               for row in list(pre.values()) + list(post.values()))
    assert all(row["rank"] in range(RANKS) and row["pmi_rank"] in range(RANKS)
               for row in post.values())
    post_by_pmi = {row["pmi_rank"]: row for row in post.values()}
    assert len(post_by_pmi) == RANKS and set(post_by_pmi) == set(range(RANKS))
    assert sorted(row["rank"] for row in post.values()) == list(range(RANKS))
    assert all(pre[pmi]["host"] == post_by_pmi[pmi]["host"] for pmi in range(RANKS))
    host_counts = Counter(row["host"] for row in post.values())
    assert len(host_counts) == 4 and set(host_counts.values()) == {128}
    expected_post = list(range(256))
    assert all(row["cpus"] == expected_post for row in post.values())
    entry_modes = Counter(row["mode"] for row in entry.values())
    assert entry_modes == ({"native": 512} if arm == "untraced_control"
                           else {"native": 511, "strace": 1})
    world_pmi = {pmi: post_by_pmi[pmi]["rank"] for pmi in range(RANKS)}
    arm_results[arm] = {
        "entry_records": RANKS,
        "entry_modes": dict(entry_modes),
        "native_pre_records": RANKS,
        "native_post_records": RANKS,
        "entry_and_pre_pmi_rank_coverage": [0, RANKS - 1],
        "post_world_rank_coverage_unique": True,
        "post_pmi_rank_coverage_unique": True,
        "world_rank_to_pmi_rank_nonidentity_pairs": sum(a != b for a, b in world_pmi.items()),
        "pre_affinity_errors": sum(row["affinity_status"] != 0 for row in pre.values()),
        "post_affinity_errors": sum(row["affinity_status"] != 0 for row in post.values()),
        "post_mask_all_ranks_cpus_0_through_255": True,
        "pre_masks_by_host": mask_summary(pre),
        "post_masks_by_host": mask_summary(post),
    }

# Confirm the two arms used the same MPI world-rank/PMI crosswalk.
maps = []
for arm in ARMS:
    post = records(f"arms/{arm}/native")
    maps.append({row["pmi_rank"]: row["rank"] for row in post.values()})
assert maps[0] == maps[1]

returns = [json.loads(line) for line in text("command-return-codes.jsonl").splitlines()]
return_map = {row["command"]: row["return_code"] for row in returns}
assert len(return_map) == len(returns)
assert all(return_map.get(name) == 0 for name in (
    "payload_hash_before", "module_reset", "module_load_openfoam_2512",
    "lookup_cc", "lookup_mpiexec", "lookup_strace", "lookup_ldd",
    "strace_version", "strace_help", "strace_stack_trace_option",
    "cc_version", "mpiexec_version", "compile_native_probe", "probe_ldd",
    "pstream_library_lookup", "pstream_ldd", "untraced_control_native",
    "rank0_straced_native", "payload_hash_after"))
assert text("payload-sha256-before.txt") == text("payload-sha256-after.txt")
assert all(line.endswith(": OK") for line in text("payload-sha256-before.txt").splitlines())
worker = json.loads(text("worker-status.json"))
assert worker["worker_return_code"] == worker["post_hash_return_code"] == 0
assert all("MPI_SUMMARY_JSON {\"world_size\":512,\"ranks_with_capture_or_identity_errors\":0}"
           in text(f"logs/{arm}.stdout.txt") for arm in ARMS)

trace = text("arms/rank0_straced/entry/rank-0000-affinity.strace").splitlines()
calls = []
for index, line in enumerate(trace):
    if "sched_getaffinity(" in line or "sched_setaffinity(" in line:
        stack = []
        cursor = index + 1
        while cursor < len(trace) and trace[cursor].startswith(" > "):
            stack.append(trace[cursor][3:])
            cursor += 1
        calls.append({"syscall": "sched_getaffinity" if "sched_getaffinity(" in line else "sched_setaffinity",
                      "line": line, "stack": stack})
assert len(calls) == 3
assert [c["syscall"] for c in calls].count("sched_getaffinity") == 3
assert not any(c["syscall"] == "sched_setaffinity" for c in calls)
mpi_call = next(c for c in calls if any("_cray_ofi_get_my_rank_numa_node" in f for f in c["stack"]))
assert any("MPIDI_CRAY_ofi_nic_assign_policy" in f for f in mpi_call["stack"])
assert any("MPIDI_OFI_mpi_init_hook" in f for f in mpi_call["stack"])

pstream_path = text("logs/pstream-path.txt").strip()
pstream_ldd = text("logs/pstream-ldd.txt")
assert "OpenFOAM-v2512" in pstream_path and "lib/cray-mpich/libPstream.so" in pstream_path
assert "libmpi_gnu_91.so.12" in pstream_ldd and "/opt/cray/pe/mpich/8.1.15" in pstream_ldd
probe_ldd = text("logs/probe-ldd.txt")
assert "libmpi_gnu_91.so.12" in probe_ldd
assert "strace -- version 5.18" in text("logs/strace-version.txt")
assert "stack-trace=libdw" in text("logs/strace-version.txt")

job = COLLECTION["terminal"]
assert job["job_state"] == "F" and job["Exit_status"] == 0
assert job["project"] == "59000042" and job["resources_used"]["ncpus"] == 512
assert job["resources_used"]["ngpus"] == 0
assert job["resources_used"]["walltime"] == "00:00:11"
batch_member = "cpu-affinity-strace.o26004608"
assert batch_member in raw

result = {
    "passed": True,
    "job_id": "26004608.pbs101",
    "terminal_evidence_source": COLLECTION["terminal_evidence_source"],
    "collection_archive_sha256_verified": archive_hash,
    "archive_file_count": len(raw),
    "archive_uncompressed_bytes": sum(v["bytes"] for v in COLLECTION["files"].values()),
    "batch_stdout_member": batch_member,
    "terminal": {key: job[key] for key in ("job_state", "Exit_status", "project", "queue", "stime", "obittime", "exec_host", "resources_used", "Resource_List")},
    "all_command_return_codes_zero": True,
    "before_after_payload_hashes_equal_and_checks_clean": True,
    "worker_status": worker,
    "arms": arm_results,
    "rank_crosswalk_same_across_arms": True,
    "trace": {
        "trace_file": "runs/26004608/arms/rank0_straced/entry/rank-0000-affinity.strace",
        "traced_rank": 0,
        "syscalls": calls,
        "sched_getaffinity_count": 3,
        "sched_setaffinity_count": 0,
        "mpi_getaffinity_query_caller": "_cray_ofi_get_my_rank_numa_node, via MPIDI_CRAY_ofi_nic_assign_policy and MPIDI_OFI_mpi_init_hook in Cray MPICH 8.1.15",
        "setter_identified": False,
    },
    "native_pstream": {"path": pstream_path, "cray_mpich_library_seen": True},
    "interpretation_limits": [
        "The trace establishes the caller of one sched_getaffinity query, not the caller or mechanism that changed the process affinity mask.",
        "Only rank zero and its traced process descendants were observed; no sched_setaffinity call appears in that trace.",
        "The control pre-init masks differ on one host from the traced arm and from the other three control hosts; this four-node allocation observation is unexplained.",
        "Logical CPU IDs were recorded; physical-core topology and rank-to-core uniqueness were not collected.",
        "This diagnostic has no solver, scored workload, per-phase hardware telemetry, or performance conclusion."
    ],
}
OUTPUT.write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({"passed": True, "file_count": len(raw), "trace_calls": len(calls),
                  "arm_results": {arm: {k: v for k, v in data.items() if k not in ("pre_masks_by_host", "post_masks_by_host")}
                                  for arm, data in arm_results.items()},
                  "mpi_getaffinity_query_caller": result["trace"]["mpi_getaffinity_query_caller"]}, indent=2))
