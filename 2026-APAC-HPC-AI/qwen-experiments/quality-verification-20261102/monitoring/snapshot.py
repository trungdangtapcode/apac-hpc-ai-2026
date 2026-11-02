#!/usr/bin/env python3
"""Take one read-only scheduler/evaluation snapshot; never dispatch or retry jobs."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import getpass
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return json.loads(path.read_text()) if path.is_file() else None


def command(argv):
    try:
        p = subprocess.run(argv, capture_output=True, text=True, timeout=20)
        return dict(argv=argv, returncode=p.returncode, stdout=p.stdout, stderr=p.stderr)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return dict(argv=argv, returncode=None, error=str(exc))


def take_snapshot():
    stamp = datetime.now(timezone.utc).isoformat()
    ledger = read(ROOT / "admission-full8/ledger.json")
    jobs = ledger["jobs"]
    queue = command(["squeue", "-u", getpass.getuser(), "-h", "-o", "%i|%T|%M|%R|%N"])
    account = command(["sacct", "-X", "-n", "-P", "-j",
                       ",".join(str(x["job"]) for x in jobs.values()),
                       "--format=JobIDRaw,State,ExitCode,ElapsedRaw,Start,End,AllocTRES,NodeList"])
    live = {}
    if queue["returncode"] == 0:
        for line in queue["stdout"].splitlines():
            fields = line.split("|", 4)
            if len(fields) == 5:
                live[fields[0]] = dict(state=fields[1], elapsed=fields[2], reason=fields[3], nodes=fields[4])
    terminal = {}
    if account["returncode"] == 0:
        for line in account["stdout"].splitlines():
            fields = line.strip().split("|")
            if len(fields) >= 8 and fields[0].isdigit():
                terminal[fields[0]] = dict(state=fields[1], exit_code=fields[2],
                                          elapsed_seconds=int(fields[3]), start=fields[4],
                                          end=fields[5], allocated_tres=fields[6], nodes=fields[7])
    rows = []
    for shard in range(8):
        for role in ("reference", "candidate"):
            key = f"{role}-{shard:02d}"
            entry = jobs.get(key)
            row = dict(role=role, shard_index=shard, planned_questions=1504,
                       job_id=entry["job"] if entry else None)
            if entry is None:
                row.update(state="NOT_SUBMITTED", lifecycle="FROZEN_NOT_SUBMITTED")
                rows.append(row)
                continue
            job = str(entry["job"])
            accounting = terminal.get(job)
            row["queue"] = live.get(job)
            row["accounting"] = accounting
            row["state"] = live.get(job, {}).get("state", (accounting or {}).get("state", "UNKNOWN"))
            evaluation = (ROOT / "jobs" / f"full-ref-{shard:02d}of08" / "runs" / job / "reference/evaluation"
                          if role == "reference" else ROOT / "jobs" / f"full-cand-{shard:02d}of08"
                          / "AI_Task/logs/full-shards" / job / "evaluation")
            run, summary = read(evaluation / "run.json"), read(evaluation / "summary.json")
            event = read(ROOT / "workflow/events" / f"{role}-{shard:02d}-job{job}.json")
            row["evaluation_dir"] = str(evaluation)
            row["client_progress"] = ({k: run.get(k) for k in
                                       ("status", "completed_records", "selected_count", "progress_correct")}
                                      if run else None)
            row["client_summary"] = ({k: summary.get(k) for k in
                                      ("status", "denominator", "correct", "accuracy", "service_errors_in_denominator")}
                                     if summary else None)
            row["callback_status"] = event.get("status") if event else None
            valid = bool(accounting and accounting["state"] == "COMPLETED"
                         and accounting["exit_code"] == "0:0" and event and event.get("status") == "VALID")
            row["completed_with_validated_callback"] = valid
            row["human_reviewed_in_ledger"] = entry.get("state") == "REVIEWED_COMPLETE"
            if valid:
                row["validated_correct"] = event["correct"]
                row["validated_questions"] = event["question_count"]
            rows.append(row)
    common = [k for k in range(8) if all(any(r["role"] == role and r["shard_index"] == k
              and r.get("completed_with_validated_callback") for r in rows) for role in ("reference", "candidate"))]
    counts = {role: sum(r["validated_correct"] for r in rows if r["role"] == role
                       and r["shard_index"] in common) for role in ("reference", "candidate")}
    n = len(common) * 1504
    return dict(created_utc=stamp, scope="Dated read-only monitoring; existing callback validation is reported, not rerun.",
                planned_full_questions_per_role=12032, planned_jobs=16, admitted_jobs=len(jobs),
                queue_available=queue["returncode"] == 0,
                own_active_pending_count=len(live) if queue["returncode"] == 0 else None,
                rows=rows, common_completed_shards=common, paired_questions=n,
                paired_correct_counts=counts,
                paired_point_ratio=counts["candidate"] / counts["reference"] if counts["reference"] else None,
                paired_ratio_scope="Only common completed shards; not a full-set result unless all 12032 questions are covered.",
                last_callback_state=read(ROOT / "workflow/STATE.json"),
                stop=read(ROOT / "workflow/STOP.json"),
                full_comparison_exists=(ROOT / "workflow/FULL_COMPARISON.json").is_file(),
                scheduler_commands=dict(queue=queue, accounting=account))


def render(snapshot):
    text = ["# Local quality measurement: dated monitoring snapshot", "",
            f"Observed UTC: {snapshot['created_utc']}. Add seven hours for Vietnam time.", "",
            f"Admitted: **{snapshot['admitted_jobs']}/16**. Common completed coverage: "
            f"**{snapshot['paired_questions']}/12032 questions per role**.", "",
            "The callback state records its last invocation; it is not a substitute for live scheduler state.", "",
            "| Role | Shard (zero-based) | Job | Scheduler state | Client responses | Callback |",
            "|---|---:|---:|---|---:|---|"]
    for row in snapshot["rows"]:
        progress = row.get("client_progress") or {}
        count = progress.get("completed_records", "—")
        text.append(f"|{row['role']}|{row['shard_index']}|{row['job_id'] or '—'}|{row['state']}|{count}|{row.get('callback_status') or '—'}|")
    text += ["", f"Common completed correct counts: {snapshot['paired_correct_counts']}.",
             f"Paired point ratio: {snapshot['paired_point_ratio']}; scope: {snapshot['paired_ratio_scope']}", "",
             f"Queue query available: {snapshot['queue_available']}. Unknown queue state is never reported as empty.",
             f"STOP marker present: {snapshot['stop'] is not None}. Full aggregate exists: {snapshot['full_comparison_exists']}.", "",
             "A validated callback does not replace the technical review of logs, diagnostics and limitations. "
             "This local benchmark does not certify the organiser's unpublished quality evaluation.", ""]
    return "\n".join(text)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", required=True, type=Path, help="New directory; snapshots never overwrite old evidence")
    args = parser.parse_args()
    snapshot = take_snapshot()
    args.out_dir.mkdir(parents=True, exist_ok=False)
    (args.out_dir / "snapshot.json").write_text(json.dumps(snapshot, indent=2) + "\n")
    (args.out_dir / "SNAPSHOT.md").write_text(render(snapshot))
    print(json.dumps({k: snapshot[k] for k in ("created_utc", "admitted_jobs", "own_active_pending_count",
                     "paired_questions", "paired_point_ratio", "full_comparison_exists")}))
