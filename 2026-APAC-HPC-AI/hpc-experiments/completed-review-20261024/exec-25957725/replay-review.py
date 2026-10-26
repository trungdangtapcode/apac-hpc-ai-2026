#!/usr/bin/env python3
"""Replay a bounded review of retained job 25957725 artifacts; no remote access."""
from collections import Counter
from datetime import datetime
from pathlib import Path
import hashlib
import json
import re

HERE = Path(__file__).resolve().parent
COLLECTED = HERE / "collected"
RUN = COLLECTED / "25957725/runs/25957725"
OUT = HERE / "review.json"

def read_json(path):
    return json.loads(path.read_text())

def utc(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))

manifest = read_json(COLLECTED / "collection.json")
file_check = {}
for rel, meta in manifest["files"].items():
    path = COLLECTED / rel
    if not path.is_file():
        file_check[rel] = {"present": False}
        continue
    data = path.read_bytes()
    file_check[rel] = {
        "present": True,
        "bytes_match": len(data) == meta["bytes"],
        "sha256_match": hashlib.sha256(data).hexdigest() == meta["sha256"],
    }

stderr = (RUN / "logs/mpi_identity.stderr.txt").read_text()
prefix = "APAC_AFFINITY_EXEC_JSON "
records = [json.loads(line.split(prefix, 1)[1]) for line in stderr.splitlines() if prefix in line]
success = [r for r in records if r.get("success") is True]
rejected = [r for r in records if r.get("success") is not True]
pmi_success = sorted({int(r["pmi_rank"]) for r in success})
pmi_rejected = sorted({int(r["pmi_rank"]) for r in rejected})
assert len(success) == len(pmi_success) == 128 and pmi_success == list(range(128))
assert len(rejected) == len(pmi_rejected) == 17
errors = Counter(r.get("error", "<missing>") for r in rejected)
assert errors == {"launcher_mask_not_single_cpu": 17}

phase_rows = []
for line in (RUN / "phases.tsv").read_text().splitlines():
    stamp, event, name = line.split("\t", 2)
    phase_rows.append({"utc": stamp, "event": event, "phase": name})
starts = [x for x in phase_rows if x["phase"] == "mpi_identity" and x["event"] == "start"]
ends = [x for x in phase_rows if x["phase"] == "mpi_identity" and x["event"].startswith("exit=")]
assert len(starts) == len(ends) == 1
phase_seconds = (utc(ends[0]["utc"]) - utc(starts[0]["utc"])).total_seconds()
resource = (RUN / "logs/mpi_identity.resource.txt").read_text()
elapsed = re.search(r"Elapsed \(wall clock\) time .*?: ([0-9:.]+)", resource).group(1)
mm, ss = elapsed.split(":")[-2:]
resource_seconds = int(mm) * 60 + float(ss)
assert "Exit status: 143" in resource
codes = read_json(RUN / "command-return-codes.json")
rcs = {x["stage"]: x["return_code"] for x in codes}
assert rcs.get("mpi_identity") == 143 and all(v == 0 for k, v in rcs.items() if k != "mpi_identity")

stderr_rank = re.search(r"rank (\d+) exited with code (\d+)", stderr)
assert stderr_rank is not None
lifecycle = read_json(RUN / "batch-lifecycle.json")
submission = read_json(HERE.parents[1] / "nscc-cpu-mpi-exec-affinity-20261024/submission.json")
submitted_status = read_json(HERE.parents[1] / "nscc-cpu-mpi-exec-affinity-20261024/post-submit-status.json")

out = {
    "review_scope": "Local retained artifacts only; no scheduler access or submission.",
    "job": "25957725.pbs101",
    "artifacts": {
        "manifest_entries": len(manifest["files"]),
        "manifest_present_files": sum(x["present"] for x in file_check.values()),
        "manifest_files_all_hash_and_size_match": all(x.get("present") and x.get("bytes_match") and x.get("sha256_match") for x in file_check.values()),
        "terminal_metadata": manifest.get("terminal"),
        "scheduler_query": manifest.get("scheduler_query"),
    },
    "preexec_observations": {
        "successful_capture_and_exec_records": len(success),
        "successful_pmi_ranks": [min(pmi_success), max(pmi_success)],
        "preexec_mask_rejections": len(rejected),
        "rejection_reason_counts": dict(errors),
        "rejected_pmi_ranks": pmi_rejected,
        "ranks_without_retained_wrapper_record": 512 - len(records),
        "pals_reported_rank_exit": {"rank": int(stderr_rank.group(1)), "code": int(stderr_rank.group(2))},
        "mpi_probe_stdout_bytes": (RUN / "logs/mpi_identity.stdout.txt").stat().st_size,
        "mpi_initialization_or_topology_records": 0,
        "interpretation": "Rejections happened in the pre-exec wrapper. They do not prove MPI_Init was reached or that MPI_Init is the sole cause; later ranks and cancellation mechanism are not fully observed.",
    },
    "exit_and_timing": {
        "mpi_identity_return_code": rcs["mpi_identity"],
        "other_recorded_stage_return_codes": sorted(set(v for k, v in rcs.items() if k != "mpi_identity")),
        "phase_elapsed_seconds_rounded": round(phase_seconds, 3),
        "resource_elapsed_seconds": resource_seconds,
        "configured_command_timeout_seconds": 184,
        "wrapper_elapsed_seconds": lifecycle.get("wrapper_elapsed_seconds"),
        "wrapper_exit_status": lifecycle.get("wrapper_exit_status"),
        "post_run_source_hash_status": lifecycle.get("post_run_source_hash_status"),
        "timeout_interpretation": "Return code 143 is SIGTERM-style status, but observed MPI command runtime was about 4.25 s versus a 184 s timeout; it does not establish timeout expiry.",
    },
    "metadata_inconsistencies": {
        "frozen_script_vs_lifecycle_internal_deadline_seconds": {"script": 255, "lifecycle": lifecycle.get("internal_deadline_seconds")},
        "frozen_pbs_walltime_seconds_vs_lifecycle_requested_walltime_seconds": {"script": 300, "lifecycle": lifecycle.get("requested_walltime_seconds")},
        "frozen_pbs_max_su_vs_lifecycle_max_requested_su": {"script_request": "4 nodes x 300 seconds", "lifecycle": lifecycle.get("maximum_requested_SU")},
        "submission_record_maximum_su": submission.get("maximum_SU"),
        "post_submit_scheduler_snapshot": submitted_status.get("status"),
        "scheduler_terminal_result": "Unknown; retained qstat returned Unknown Job Id and collection terminal map is empty.",
        "accounting_or_actual_charged_su": "Not collected; do not infer from wrapper return status or reservation estimates.",
    },
    "phase_start_utc": starts[0]["utc"],
    "phase_exit_utc": ends[0]["utc"],
}
OUT.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
print(json.dumps({"output": str(OUT), "preexec_success": len(success), "preexec_rejections": len(rejected), "unobserved_ranks": 512-len(records), "rc": rcs["mpi_identity"], "resource_seconds": resource_seconds, "manifest_hashes_match": out["artifacts"]["manifest_files_all_hash_and_size_match"]}, indent=2))
