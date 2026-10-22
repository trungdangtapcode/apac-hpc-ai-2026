"""Retain wrapper timing and a live resource snapshot before history expires."""
from pathlib import Path
import datetime
import json
import os
import shutil
import subprocess
import sys
import time

mode, run_name = sys.argv[1], sys.argv[2]
run = Path(run_name)
record_path = run / "batch-lifecycle.json"
if mode == "start":
    record = {
        "job": os.environ["PBS_JOBID"],
        "utc_start": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "start_monotonic": time.monotonic(),
        "requested_ncpus": 128,
        "requested_walltime_seconds": 1740,
        "maximum_SU": 128 * 1740 / 3600,
        "scope": "Wrapper time is not scheduler terminal accounting.",
    }
else:
    record = json.loads(record_path.read_text())
    record.update({
        "utc_end": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "wrapper_exit_status": int(sys.argv[3]),
        "observed_wrapper_elapsed_seconds": time.monotonic() - record["start_monotonic"],
    })
    record["estimated_wrapper_core_hour_SU"] = record["observed_wrapper_elapsed_seconds"] * 128 / 3600
    qstat = shutil.which("qstat")
    if qstat:
        try:
            result = subprocess.run([qstat, "-f", "-F", "json", os.environ["PBS_JOBID"]],
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    universal_newlines=True, timeout=12)
            if result.returncode == 0:
                job = json.loads(result.stdout)["Jobs"][os.environ["PBS_JOBID"]]
                record["pre_exit_live_snapshot"] = {
                    key: job[key] for key in ("job_state", "resources_used", "exec_host") if key in job
                }
            else:
                record["resource_snapshot"] = "Not collected: live query failed"
        except Exception:
            record["resource_snapshot"] = "Not collected: live query unavailable"
    else:
        record["resource_snapshot"] = "Not collected: qstat absent from compute PATH"
    record["limits"] = (
        "Wrapper status/timing excludes scheduler prologue and cleanup and does not prove final PBS exit or billed SU. "
        "A live resource snapshot is not terminal accounting."
    )
record_path.write_text(json.dumps(record, indent=2) + "\n")
