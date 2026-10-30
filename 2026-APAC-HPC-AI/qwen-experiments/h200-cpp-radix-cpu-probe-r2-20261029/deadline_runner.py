#!/usr/bin/env python3
"""Run the CPU fixture under an absolute deadline and reap its full process group."""
from __future__ import annotations
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

result_path = Path(os.environ["APAC_CPP_RADIX_RESULT"])
receipt_path = result_path.with_name("deadline-supervisor.json")
deadline = int(os.environ["APAC_CPP_RADIX_PROCESS_DEADLINE_EPOCH"])
probe = sys.argv[1] if len(sys.argv) == 2 else "/work/probe.py"
receipt = {"state": "RUNNING", "absolute_deadline_epoch": deadline,
           "probe_path": probe, "term_grace_seconds": 15}

def save_receipt() -> None:
    tmp = receipt_path.with_suffix(".tmp")
    tmp.write_text(json.dumps(receipt, indent=2) + "\n")
    tmp.replace(receipt_path)

def fail_result(reason: str) -> None:
    try:
        value = json.loads(result_path.read_text()) if result_path.is_file() else {}
        if not isinstance(value, dict):
            value = {"previous_result_type": type(value).__name__}
    except Exception as exc:
        value = {"result_read_error": repr(exc)}
    value.update(state="FAIL_PROCESS_DEADLINE", deadline_failure=reason,
                 process_deadline_epoch=deadline)
    tmp = result_path.with_suffix(".deadline.tmp")
    tmp.write_text(json.dumps(value, indent=2) + "\n")
    tmp.replace(result_path)

remaining = deadline - int(time.time())
if remaining <= 0:
    receipt.update(state="FAIL_NO_TIME_REMAINING", exit_code=124,
                   finished_epoch=int(time.time()))
    save_receipt()
    fail_result("absolute deadline elapsed before fixture launch")
    raise SystemExit(124)

proc = subprocess.Popen([sys.executable, "-B", probe], start_new_session=True)
receipt.update(state="RUNNING_FIXTURE", child_pid=proc.pid,
               child_start_epoch=int(time.time()), remaining_seconds=remaining)
save_receipt()
try:
    code = proc.wait(timeout=remaining)
    receipt.update(state="CHILD_EXITED", child_exit_code=code,
                   child_end_epoch=int(time.time()))
    save_receipt()
    raise SystemExit(code)
except subprocess.TimeoutExpired:
    receipt.update(state="DEADLINE_TERM_SENT", term_epoch=int(time.time()))
    save_receipt()
    try:
        os.killpg(proc.pid, signal.SIGTERM)
    except ProcessLookupError:
        pass
    try:
        proc.wait(timeout=15)
        receipt.update(state="CHILD_REAPED_AFTER_TERM", child_exit_code=proc.returncode)
    except subprocess.TimeoutExpired:
        receipt.update(state="DEADLINE_KILL_SENT", kill_epoch=int(time.time()))
        save_receipt()
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        proc.wait()
        receipt.update(state="CHILD_REAPED_AFTER_KILL", child_exit_code=proc.returncode)
    receipt.update(finished_epoch=int(time.time()))
    save_receipt()
    fail_result("CPU fixture exceeded absolute batch-start + 300-second deadline")
    raise SystemExit(124)
