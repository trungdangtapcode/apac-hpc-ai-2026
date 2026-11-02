#!/usr/bin/env python3
"""Finite Slurm-job completion callback for the already declared 16 quality shards.

This process handles one completed driver's exit only. It never runs a model,
starts a watcher, retries a job, or cancels queued work.
"""
from __future__ import annotations

import argparse
import fcntl
import getpass
import hashlib
import json
import os
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

TASK_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PREPARED = TASK_ROOT / "prepared-4k"
DEFAULT_LEDGER = TASK_ROOT / "admission-full8" / "ledger.json"
DEFAULT_MEMBERSHIP = TASK_ROOT / "full-tools" / "full_shard_membership.json"
DEFAULT_ADMIT = TASK_ROOT / "admit_full.py"
EXPECTED_SHARD_ROWS = 1504
SHARD_COUNT = 8
ROLE_NAMES = ("reference", "candidate")


class ValidationFailure(RuntimeError):
    pass


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValidationFailure(f"required artifact missing: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValidationFailure(f"invalid JSON artifact: {path}") from exc


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    try:
        f = path.open(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValidationFailure(f"required artifact missing: {path}") from exc
    rows = []
    with f:
        for n, line in enumerate(f, 1):
            if line.strip():
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError as exc:
                    raise ValidationFailure(f"invalid JSONL in {path}:{n}") from exc
    return rows


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + f".{os.getpid()}.tmp")
    with temp.open("x", encoding="utf-8") as f:
        json.dump(value, f, ensure_ascii=False, sort_keys=True, indent=2)
        f.write("\n")
        f.flush()
        os.fsync(f.fileno())
    os.replace(temp, path)


def append_or_compare_event(path: Path, event: dict[str, Any]) -> dict[str, Any]:
    """Write exactly once; repeated invocation cannot replace evidence."""
    if path.exists():
        old = read_json(path)
        for key in ("job_id", "role", "shard_index", "driver_rc"):
            if old.get(key) != event.get(key):
                raise ValidationFailure(f"event already exists with conflicting {key}: {path}")
        return old
    atomic_json(path, event)
    return event


def evaluation_dir(task_root: Path, role: str, shard: int, job: int) -> Path:
    if role == "reference":
        return task_root / "jobs" / f"full-ref-{shard:02d}of08" / "runs" / str(job) / "reference" / "evaluation"
    return task_root / "jobs" / f"full-cand-{shard:02d}of08" / "AI_Task" / "logs" / "full-shards" / str(job) / "evaluation"


def load_pinned_parser(task_root: Path):
    import importlib.util
    parser_path = task_root / "client" / "aggregate_full.py"
    spec = importlib.util.spec_from_file_location("quality_aggregate_for_finite_event", parser_path)
    if spec is None or spec.loader is None:
        raise ValidationFailure(f"cannot load pinned response parser: {parser_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.parse_pinned


def validate_response_records(records: list[dict[str, Any]],
                              compiled: dict[int, dict[str, Any]],
                              expected_ids: list[int], parse) -> dict[str, Any]:
    """Validate one finite shard against explicit frozen membership and corpus rows."""
    response_ids = [int(r["question_id"]) for r in records]
    if (len(records) != len(expected_ids) or len(set(response_ids)) != len(expected_ids)
            or set(response_ids) != set(expected_ids)):
        raise ValidationFailure("response file does not contain one record for every frozen selected ID")
    errors = invalid = truncated = correct = 0
    for row in records:
        qid = int(row["question_id"])
        source = compiled.get(qid)
        if source is None:
            raise ValidationFailure(f"response includes ID outside prepared corpus: {qid}")
        for field in ("prompt_sha256", "token_ids_sha256", "shots_used", "expected_answer", "category"):
            if row.get(field) != source.get(field):
                raise ValidationFailure(f"question {qid}: response {field} differs from compiled corpus")
        try:
            body = json.loads(row.get("raw_response_body") or "")
        except (json.JSONDecodeError, TypeError):
            body = None
        choices = body.get("choices") if isinstance(body, dict) else None
        choice = choices[0] if isinstance(choices, list) and choices and isinstance(choices[0], dict) else None
        message = choice.get("message") if choice else None
        completion = message.get("content") if isinstance(message, dict) else None
        finish_reason = choice.get("finish_reason") if choice else None
        if (row.get("status") != "OK" or row.get("http_status") != 200
                or not isinstance(completion, str)):
            errors += 1
            continue
        parsed = parse(completion)
        if (row.get("completion_text") != completion or row.get("predicted_answer") != parsed
                or row.get("finish_reason") != finish_reason):
            raise ValidationFailure(f"question {qid}: stored parsing fields disagree with raw response body")
        if parsed is None:
            invalid += 1
        elif parsed == source["expected_answer"]:
            correct += 1
        if finish_reason in ("length", "max_tokens"):
            truncated += 1
    if errors:
        raise ValidationFailure(f"raw responses contain {errors} HTTP/client errors")
    return {"correct": correct, "accuracy": correct / len(expected_ids),
            "service_errors": errors, "invalid_outputs": invalid,
            "truncated_outputs": truncated}


def validate_artifacts(task_root: Path, role: str, shard: int, job: int,
                       ledger_entry: dict[str, Any], prepare_path: Path,
                       corpus_path: Path, membership_path: Path,
                       expected_count: int = EXPECTED_SHARD_ROWS) -> dict[str, Any]:
    evaluation = evaluation_dir(task_root, role, shard, job)
    run_path = evaluation / "run.json"
    summary_path = evaluation / "summary.json"
    response_path = evaluation / "responses.jsonl"
    shard_root = task_root / "jobs" / (f"full-ref-{shard:02d}of08" if role == "reference"
                                        else f"full-cand-{shard:02d}of08")
    plan_path = shard_root / "FULL_SHARD.json"
    plan = read_json(plan_path)
    if (plan.get("role") != role or plan.get("shard_index") != shard
            or plan.get("shard_count") != SHARD_COUNT or plan.get("rows") != expected_count
            or plan.get("concurrency") != 64 or plan.get("temperature") != 0.0
            or plan.get("max_output_tokens") != 2048):
        raise ValidationFailure("frozen FULL_SHARD plan differs from callback role/shard/workload")
    run = read_json(run_path)
    summary = read_json(summary_path)
    prepare = read_json(prepare_path)
    membership = read_json(membership_path)
    if prepare.get("status") != "READY" or prepare.get("generation_blocked"):
        raise ValidationFailure("prepared manifest is not READY")
    corpus_sha = sha_file(corpus_path)
    prepare_sha = sha_file(prepare_path)
    if prepare.get("compiled_corpus_sha256") != corpus_sha:
        raise ValidationFailure("prepared manifest does not bind the exact compiled corpus SHA-256")
    if int(prepare.get("question_count", -1)) != 12032:
        raise ValidationFailure("prepared corpus does not declare exactly 12,032 questions")
    if membership.get("corpus_sha256") != corpus_sha or int(membership.get("prepared_rows", -1)) != 12032:
        raise ValidationFailure("frozen shard-membership manifest differs from prepared corpus")
    shard_key = f"{shard:02d}of08"
    role_table = membership.get("roles", {}).get(role, {})
    membership_row = role_table.get(shard_key)
    if not isinstance(membership_row, dict):
        raise ValidationFailure(f"frozen membership has no {role} shard {shard_key}")
    expected_ids = [int(q) for q in membership_row.get("question_ids", [])]
    if len(expected_ids) != expected_count or len(set(expected_ids)) != expected_count:
        raise ValidationFailure(f"frozen shard membership is not exactly {expected_count} unique IDs")
    if run.get("status") != "COMPLETE" or summary.get("status") != "COMPLETE":
        raise ValidationFailure("client run/summary is not COMPLETE")
    if run.get("prepare_manifest_sha256") != prepare_sha or run.get("corpus_sha256") != corpus_sha:
        raise ValidationFailure("client run has different prepared-manifest or corpus hash")
    if run.get("concurrency") != 64:
        raise ValidationFailure(f"client concurrency is not 64: {run.get('concurrency')}")
    if run.get("generation") != {"temperature": 0.0, "top_p": 1.0,
                                  "max_tokens": 2048, "stop": ["Question:"], "stream": False}:
        raise ValidationFailure("client generation protocol differs from frozen full-shard recipe")
    if run.get("selected_count") != expected_count or run.get("selected_question_ids") != expected_ids:
        raise ValidationFailure("client selected IDs/count differ from frozen membership list/order")
    if summary.get("denominator") != expected_count or not summary.get("coverage_complete"):
        raise ValidationFailure("client summary denominator or coverage is incomplete")
    if summary.get("service_errors_in_denominator") != 0 or summary.get("not_started_deadline_records") != 0:
        raise ValidationFailure("client summary has service errors or deadline-not-started requests")
    if summary.get("missing_ids") or summary.get("duplicate_ids") or summary.get("extra_ids"):
        raise ValidationFailure("client summary reports missing, duplicate, or extra IDs")

    # Exact response provenance against the prepared rows, parsing raw response
    # JSON again rather than trusting stored predictions or aggregate counters.
    compiled_rows = read_jsonl(corpus_path)
    compiled = {int(r["question_id"]): r for r in compiled_rows}
    if len(compiled) != 12032:
        raise ValidationFailure("compiled corpus IDs are not unique/full")
    records = read_jsonl(response_path)
    parse = load_pinned_parser(task_root)
    stats = validate_response_records(records, compiled, expected_ids, parse)
    errors = stats["service_errors"]
    invalid = stats["invalid_outputs"]
    truncated = stats["truncated_outputs"]
    correct = stats["correct"]
    accuracy = stats["accuracy"]
    if summary.get("correct") != correct or summary.get("accuracy") != accuracy:
        raise ValidationFailure("client summary correctness/accuracy differs from raw-response recomputation")
    if summary.get("local_quality_gate_zero_service_errors") is not True:
        raise ValidationFailure("client local zero-service-error gate is not true")

    validity_path = evaluation.parent / "measurement-validity.json"
    validity = read_json(validity_path)
    response_hash = sha_file(response_path)
    if validity.get("passed") is not True or validity.get("question_count") != expected_count:
        raise ValidationFailure("measurement-validity.json did not pass for exact shard size")
    if validity.get("raw_responses_sha256") != response_hash or validity.get("correct") != correct:
        raise ValidationFailure("measurement-validity receipt does not match raw responses/recomputed score")
    if validity.get("accuracy") != accuracy:
        raise ValidationFailure("measurement-validity accuracy differs from raw-response recomputation")

    return {
        "status": "VALID", "job_id": int(job), "role": role,
        "shard_index": shard, "shard_count": SHARD_COUNT,
        "question_count": expected_count, "correct": correct, "accuracy": accuracy,
        "service_errors": errors, "invalid_outputs": invalid, "truncated_outputs": truncated,
        "concurrency": 64, "generation": run["generation"],
        "corpus_sha256": corpus_sha, "prepare_manifest_sha256": prepare_sha,
        "membership_manifest_sha256": sha_file(membership_path),
        "evaluation_dir": str(evaluation.resolve()),
        "source_ids": expected_ids,
        "source_files": {
            "frozen_shard_plan": {"path": str(plan_path.resolve()), "sha256": sha_file(plan_path)},
            "run_json": {"path": str(run_path.resolve()), "sha256": sha_file(run_path)},
            "summary_json": {"path": str(summary_path.resolve()), "sha256": sha_file(summary_path)},
            "responses_jsonl": {"path": str(response_path.resolve()), "sha256": response_hash},
            "measurement_validity": {"path": str(validity_path.resolve()), "sha256": sha_file(validity_path)},
        },
    }


def query_squeue() -> tuple[bool, int | None, str]:
    """Return count of all this user's active/pending Slurm rows; unknown is not zero."""
    try:
        proc = subprocess.run(["squeue", "-u", getpass.getuser(), "-h", "-o", "%i|%T|%j|%R"],
                              text=True, capture_output=True, timeout=20)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return False, None, f"{type(exc).__name__}: {exc}"
    if proc.returncode != 0:
        return False, None, (proc.stderr or proc.stdout)[-2000:]
    rows = [x for x in proc.stdout.splitlines() if x.strip()]
    return True, len(rows), proc.stdout


def dispatch_fill(admit_script: Path) -> dict[str, Any]:
    argv = [sys.executable, str(admit_script), "--wave", "fill", "--chain"]
    proc = None
    try:
        proc = subprocess.Popen(argv, cwd=str(admit_script.parent), text=True,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                start_new_session=True)
        stdout, stderr = proc.communicate(timeout=180)
        return {"argv": argv, "returncode": proc.returncode,
                "stdout": stdout[-10000:], "stderr": stderr[-10000:],
                "timed_out": False, "ambiguous_submission_possible": False}
    except subprocess.TimeoutExpired as exc:
        # The admission script may already have handed a job to Slurm before
        # hanging or losing the receipt. Kill its whole local process group,
        # but never claim this undid any sbatch that Slurm already accepted.
        kill_error = None
        if proc is not None:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            except OSError as kill_exc:
                kill_error = f"{type(kill_exc).__name__}: {kill_exc}"
        try:
            stdout, stderr = proc.communicate(timeout=10) if proc is not None else ("", "")
        except subprocess.TimeoutExpired:
            stdout = exc.output or ""
            stderr = exc.stderr or ""
        if isinstance(stdout, bytes): stdout = stdout.decode("utf-8", errors="replace")
        if isinstance(stderr, bytes): stderr = stderr.decode("utf-8", errors="replace")
        return {"argv": argv, "returncode": None, "timed_out": True,
                "process_group_kill_error": kill_error,
                "ambiguous_submission_possible": True,
                "manual_reconciliation_required": True,
                "error": "admission command timed out; sbatch may already have been accepted before its receipt was returned; STOP and reconcile scheduler/ledger before any retry",
                "stdout": str(stdout)[-10000:], "stderr": str(stderr)[-10000:]}
    except OSError as exc:
        return {"argv": argv, "returncode": None, "timed_out": False,
                "ambiguous_submission_possible": False,
                "error": f"{type(exc).__name__}: {exc}"}


def persist_unhandled_stop(task_root: Path, *, job: int, role: str, shard: int,
                           driver_rc: int, exception: Exception,
                           lock_wait_seconds: float = 10.0) -> dict[str, Any]:
    """Fail closed for exceptions escaping handle_event; never replace first STOP."""
    workflow = task_root.resolve() / "workflow"
    workflow.mkdir(parents=True, exist_ok=True)
    lock_path = workflow / ".finite-event.lock"
    stop_path = workflow / "STOP.json"
    incident_dir = workflow / "unhandled-events"
    incident_dir.mkdir(exist_ok=True)
    incident_path = incident_dir / f"job{job}-{role}-{shard:02d}.json"
    incident = {"status": "UNHANDLED_CALLBACK_EXCEPTION", "created_utc": now(),
                "job_id": int(job), "role": role, "shard_index": int(shard),
                "driver_rc": int(driver_rc), "exception_type": type(exception).__name__,
                "exception": str(exception)[:3000],
                "action": "STOP dispatch; do not retry or cancel any job automatically."}
    acquired = False
    deadline = time.monotonic() + lock_wait_seconds
    with lock_path.open("a") as lock:
        while not acquired:
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                acquired = True
            except BlockingIOError:
                if time.monotonic() >= deadline:
                    raise TimeoutError("timed out waiting for workflow lock; could not persist fail-closed STOP")
                time.sleep(0.1)
        stop_created = False
        if not stop_path.exists():
            atomic_json(stop_path, {"status": "STOPPED", "created_utc": now(),
                                    "reason": "unhandled finite callback exception",
                                    "job_id": int(job), "role": role, "shard_index": int(shard),
                                    "driver_rc": int(driver_rc),
                                    "exception_type": type(exception).__name__,
                                    "exception": str(exception)[:3000],
                                    "policy": "Fail closed. No automatic retry, cancellation, or further dispatch."})
            stop_created = True
        # Keep later incidents without mutating an existing STOP or event.
        incident_written = False
        if not incident_path.exists():
            atomic_json(incident_path, incident)
            incident_written = True
        atomic_json(workflow / "STATE.json", {"status": "STOPPED", "updated_utc": now(),
                                                "reason": "unhandled finite callback exception",
                                                "job_id": int(job), "role": role,
                                                "shard_index": int(shard), "driver_rc": int(driver_rc),
                                                "exception_type": type(exception).__name__,
                                                "exception": str(exception)[:3000],
                                                "stop_created": stop_created,
                                                "incident_path": str(incident_path.resolve()),
                                                "incident_written": incident_written})
        return {"stop_path": str(stop_path), "stop_created": stop_created,
                "incident_path": str(incident_path), "incident_written": incident_written}


def _write_stop(workflow: Path, reason: str, event_path: Path,
                details: dict[str, Any] | None = None) -> None:
    stop_path = workflow / "STOP.json"
    if not stop_path.exists():
        atomic_json(stop_path, {"status": "STOPPED", "created_utc": now(),
                                "reason": reason, "event_path": str(event_path.resolve()),
                                "details": details or {},
                                "policy": "No retry, replacement job, cancellation, or further dispatch."})


def _valid_events(workflow: Path) -> dict[str, dict[str, Any]]:
    found: dict[str, dict[str, Any]] = {}
    for path in sorted((workflow / "events").glob("*.json")):
        ev = read_json(path)
        if ev.get("status") != "VALID":
            continue
        key = f"{ev.get('role')}-{int(ev.get('shard_index', -1)):02d}"
        if key in found:
            raise ValidationFailure(f"duplicate valid workflow event key {key}")
        found[key] = ev
    return found


def _finish_if_complete(task_root: Path, workflow: Path, prepare_path: Path,
                        corpus_path: Path,
                        aggregate_runner: Callable[[list[Path], list[Path], Path], dict[str, Any]] | None = None) -> dict[str, Any] | None:
    events = _valid_events(workflow)
    expected_keys = {f"{role}-{i:02d}" for role in ROLE_NAMES for i in range(SHARD_COUNT)}
    if set(events) != expected_keys:
        return None
    reference = [Path(events[f"reference-{i:02d}"]["evaluation_dir"]) for i in range(SHARD_COUNT)]
    candidate = [Path(events[f"candidate-{i:02d}"]["evaluation_dir"]) for i in range(SHARD_COUNT)]
    output = workflow / "FULL_COMPARISON.json"
    if output.exists():
        result = read_json(output)
        expected_ref = [str(x.resolve()) for x in reference]
        expected_cand = [str(x.resolve()) for x in candidate]
        if result.get("prepared_manifest", {}).get("sha256") != sha_file(prepare_path):
            raise ValidationFailure("existing full comparison belongs to a different prepared manifest")
        if result.get("prepared_manifest", {}).get("compiled_corpus_sha256") != sha_file(corpus_path):
            raise ValidationFailure("existing full comparison belongs to a different compiled corpus")
        actual_ref = [x.get("run_dir") for x in result.get("reference", {}).get("source_runs", [])]
        actual_cand = [x.get("run_dir") for x in result.get("candidate", {}).get("source_runs", [])]
        if actual_ref != expected_ref or actual_cand != expected_cand:
            raise ValidationFailure("existing full comparison source shards differ from workflow events")
        if result.get("status") not in ("LOCAL_FULLSET_GATE_PASS", "LOCAL_FULLSET_GATE_FAIL"):
            raise ValidationFailure("existing full comparison has unexpected status")
        atomic_json(workflow / "STATE.json", {"status": "COMPLETED", "completed_utc": now(),
                                                "event_count": 16, "comparison_path": str(output.resolve()),
                                                "comparison_sha256": sha_file(output),
                                                "comparison_status": result.get("status"),
                                                "interpretation": "Workflow completed; local quality gate status is retained, not recast as infrastructure failure."})
        return result
    if aggregate_runner is None:
        script = task_root / "client" / "aggregate_full.py"
        argv = [sys.executable, str(script), "--prepare-manifest", str(prepare_path),
                "--compiled-corpus", str(corpus_path), "--reference-runs",
                *[str(x) for x in reference], "--candidate-runs",
                *[str(x) for x in candidate], "--out", str(output)]
        p = subprocess.run(argv, cwd=str(task_root), text=True, capture_output=True, timeout=900)
        result = {"argv": argv, "returncode": p.returncode,
                  "stdout": p.stdout[-12000:], "stderr": p.stderr[-12000:]}
        if p.returncode not in (0, 4) or not output.is_file():
            raise ValidationFailure(f"full aggregate command failed unexpectedly: rc={p.returncode}; {p.stderr[-1500:]}")
        report = read_json(output)
        if report.get("status") not in ("LOCAL_FULLSET_GATE_PASS", "LOCAL_FULLSET_GATE_FAIL"):
            raise ValidationFailure("aggregate output has unexpected local-gate status")
        result["report_status"] = report["status"]
    else:
        result = aggregate_runner(reference, candidate, output)
        # Test-only runners may materialize a small report at the same path.
        if not output.exists():
            atomic_json(output, result)
    state = {"status": "COMPLETED", "completed_utc": now(),
             "event_count": 16, "comparison_path": str(output.resolve()),
             "comparison_sha256": sha_file(output),
             "comparison_status": result.get("report_status", result.get("status")),
             "interpretation": "Workflow completed. Local quality pass/fail is retained as a measurement, not an infrastructure failure or BTC certification."}
    atomic_json(workflow / "STATE.json", state)
    return result


def handle_event(task_root: Path, *, job: int, role: str, shard: int, driver_rc: int,
                 prepare_path: Path | None = None, corpus_path: Path | None = None,
                 ledger_path: Path | None = None, membership_path: Path | None = None,
                 expected_count: int = EXPECTED_SHARD_ROWS, no_dispatch: bool = False,
                 dispatch_existing: bool = False,
                 queue_query: Callable[[], tuple[bool, int | None, str]] | None = None,
                 admit: Callable[[Path], dict[str, Any]] | None = None,
                 aggregate_runner: Callable[[list[Path], list[Path], Path], dict[str, Any]] | None = None) -> dict[str, Any]:
    if role not in ROLE_NAMES or not 0 <= shard < SHARD_COUNT:
        raise ValidationFailure("role/shard is outside the frozen 2 x 8 design")
    task_root = task_root.resolve()
    prepare_path = prepare_path or DEFAULT_PREPARED / "prepare-manifest.json"
    corpus_path = corpus_path or DEFAULT_PREPARED / "compiled-corpus.jsonl"
    ledger_path = ledger_path or DEFAULT_LEDGER
    membership_path = membership_path or DEFAULT_MEMBERSHIP
    workflow = task_root / "workflow"
    event_dir = workflow / "events"
    event_dir.mkdir(parents=True, exist_ok=True)
    event_path = event_dir / f"{role}-{shard:02d}-job{int(job)}.json"
    lock_path = workflow / ".finite-event.lock"
    with lock_path.open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if event_path.exists():
            existing = read_json(event_path)
            if (existing.get("job_id"), existing.get("role"), existing.get("shard_index"), existing.get("driver_rc")) != (int(job), role, shard, int(driver_rc)):
                raise ValidationFailure("callback identity differs from already recorded immutable event")
            if not dispatch_existing:
                return {"state": "ALREADY_RECORDED", "event_path": str(event_path), "status": existing.get("status")}
            event = existing
        else:
            ledger = read_json(ledger_path)
            key = f"{role}-{shard:02d}"
            ledger_record = ledger.get("jobs", {}).get(key)
            if not isinstance(ledger_record, dict) or int(ledger_record.get("job", -1)) != int(job):
                raise ValidationFailure(f"job {job} does not match ledger key {key}")
            if (ledger_record.get("role") != role or int(ledger_record.get("shard_index", -1)) != shard
                    or int(ledger_record.get("shard_count", -1)) != SHARD_COUNT
                    or int(ledger_record.get("questions", -1)) != expected_count
                    or int(ledger_record.get("concurrency", -1)) != 64):
                raise ValidationFailure(f"ledger plan for {key} differs from the frozen shard recipe")
            event = {"created_utc": now(), "job_id": int(job), "role": role,
                     "shard_index": shard, "shard_count": SHARD_COUNT,
                     "driver_rc": int(driver_rc),
                     "callback_execution": "inside driver completion callback; Slurm terminal state is not asserted",
                     "source_ledger_key": key,
                     "source_ledger_sha256": sha_file(ledger_path),
                     "source_evaluation_dir": str(evaluation_dir(task_root, role, shard, int(job)).resolve())}
            stop_path = workflow / "STOP.json"
            if stop_path.exists():
                event.update({"status": "SKIPPED_EXISTING_STOP", "stop_sha256": sha_file(stop_path)})
            elif int(driver_rc) != 0:
                event.update({"status": "INVALID", "validation_error": f"driver exit status {driver_rc}"})
            else:
                try:
                    event.update(validate_artifacts(task_root, role, shard, int(job), ledger_record,
                                                    prepare_path, corpus_path, membership_path,
                                                    expected_count=expected_count))
                except Exception as exc:
                    event.update({"status": "INVALID", "validation_error": f"{type(exc).__name__}: {exc}"})
            event = append_or_compare_event(event_path, event)
            if event.get("status") == "INVALID":
                _write_stop(workflow, event["validation_error"], event_path,
                            {"role": role, "shard_index": shard, "job_id": job,
                             "driver_rc": driver_rc})
                atomic_json(workflow / "STATE.json", {"status": "STOPPED", "updated_utc": now(),
                                                        "reason": event["validation_error"],
                                                        "event_path": str(event_path.resolve())})
                return {"state": "STOPPED", "event_path": str(event_path), "reason": event["validation_error"]}
            if event.get("status") == "SKIPPED_EXISTING_STOP":
                return {"state": "STOPPED", "event_path": str(event_path), "reason": "STOP.json already exists"}

        if (workflow / "STOP.json").exists():
            return {"state": "STOPPED", "event_path": str(event_path), "reason": "STOP.json already exists"}
        if event.get("status") != "VALID":
            _write_stop(workflow, f"non-valid callback event status {event.get('status')}", event_path)
            return {"state": "STOPPED", "event_path": str(event_path), "reason": "event not valid"}

        try:
            completed = _finish_if_complete(task_root, workflow, prepare_path, corpus_path,
                                            aggregate_runner=aggregate_runner)
        except Exception as exc:
            reason = f"full-set aggregation failed: {type(exc).__name__}: {exc}"
            _write_stop(workflow, reason, event_path)
            atomic_json(workflow / "STATE.json", {"status": "STOPPED", "updated_utc": now(),
                                                    "reason": reason, "event_path": str(event_path.resolve())})
            return {"state": "STOPPED", "event_path": str(event_path), "reason": reason}
        if completed is not None:
            return {"state": "COMPLETED", "comparison": str((workflow / "FULL_COMPARISON.json").resolve()),
                    "comparison_status": completed.get("report_status", completed.get("status"))}

        if no_dispatch:
            atomic_json(workflow / "STATE.json", {"status": "RECORDED_NO_DISPATCH", "updated_utc": now(),
                                                    "event_path": str(event_path.resolve()),
                                                    "valid_event_count": len(_valid_events(workflow))})
            return {"state": "RECORDED_NO_DISPATCH", "event_path": str(event_path)}

        first_pair_path = task_root / "reviews" / "first-full-pair-qualification.json"
        if not first_pair_path.is_file():
            return {"state": "DEFERRED_FIRST_PAIR_REVIEW", "event_path": str(event_path),
                    "reason": "waiting for reviewed first-full-pair qualification"}
        first_pair = read_json(first_pair_path)
        if first_pair.get("passed") is not True:
            reason = "first full pair qualification was not passed"
            _write_stop(workflow, reason, event_path, {"review_path": str(first_pair_path.resolve()),
                                                       "review": first_pair})
            atomic_json(workflow / "STATE.json", {"status": "STOPPED", "updated_utc": now(), "reason": reason})
            return {"state": "STOPPED", "event_path": str(event_path), "reason": reason}
        ledger = read_json(ledger_path)
        if queue_query is None:
            queue_query = query_squeue
        queue_ok, count, queue_detail = queue_query()
        if not queue_ok or count is None:
            state = {"status": "DEFERRED_QUEUE_UNKNOWN", "updated_utc": now(),
                     "event_path": str(event_path.resolve()), "queue_detail": queue_detail,
                     "policy": "Unknown queue state is never treated as empty; no dispatch."}
            atomic_json(workflow / "STATE.json", state)
            return {"state": "DEFERRED_QUEUE_UNKNOWN", "event_path": str(event_path), "queue_detail": queue_detail}
        if count >= int(ledger.get("own_active_pending_cap", 5)):
            atomic_json(workflow / "STATE.json", {"status": "DEFERRED_CAP", "updated_utc": now(),
                                                    "active_pending_count": count,
                                                    "cap": ledger.get("own_active_pending_cap", 5),
                                                    "event_path": str(event_path.resolve())})
            return {"state": "DEFERRED_CAP", "active_pending_count": count}
        if admit is None:
            admit = dispatch_fill
        result = admit(task_root / "admit_full.py")
        if result.get("returncode") not in (0,):
            reason = "bounded admit_full fill command failed or was ambiguous; no automatic retry"
            _write_stop(workflow, reason, event_path, {"admission": result, "active_pending_count": count})
            atomic_json(workflow / "STATE.json", {"status": "STOPPED", "updated_utc": now(),
                                                    "reason": reason, "admission": result})
            return {"state": "STOPPED", "reason": reason, "admission": result}
        atomic_json(workflow / "STATE.json", {"status": "FILL_ADMITTED", "updated_utc": now(),
                                                "event_path": str(event_path.resolve()),
                                                "active_pending_before_admit": count,
                                                "admission": result})
        return {"state": "FILL_ADMITTED", "active_pending_before_admit": count,
                "admission_returncode": result.get("returncode")}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--job", required=True, type=int)
    p.add_argument("--role", required=True, choices=ROLE_NAMES)
    p.add_argument("--shard", required=True, type=int, help="zero-based frozen shard index 0..7")
    p.add_argument("--driver-rc", required=True, type=int, help="exit status of the completed model/evaluation driver")
    p.add_argument("--no-dispatch", action="store_true", help="record/validate only; never call the admission script")
    p.add_argument("--dispatch-existing", action="store_true", help="explicitly resume a previously recorded valid callback after review")
    p.add_argument("--task-root", default=str(TASK_ROOT))
    p.add_argument("--prepare-manifest", default=str(DEFAULT_PREPARED / "prepare-manifest.json"))
    p.add_argument("--compiled-corpus", default=str(DEFAULT_PREPARED / "compiled-corpus.jsonl"))
    p.add_argument("--ledger", default=str(DEFAULT_LEDGER))
    p.add_argument("--membership", default=str(DEFAULT_MEMBERSHIP))
    a = p.parse_args()
    try:
        result = handle_event(Path(a.task_root), job=a.job, role=a.role, shard=a.shard,
                              driver_rc=a.driver_rc, prepare_path=Path(a.prepare_manifest),
                              corpus_path=Path(a.compiled_corpus), ledger_path=Path(a.ledger),
                              membership_path=Path(a.membership), no_dispatch=a.no_dispatch,
                              dispatch_existing=a.dispatch_existing)
        print(json.dumps(result, indent=2))
        return 0 if result["state"] not in ("STOPPED",) else 2
    except Exception as exc:
        identity = {"job": getattr(a, "job", -1), "role": getattr(a, "role", "unknown"),
                    "shard": getattr(a, "shard", -1), "driver_rc": getattr(a, "driver_rc", -1)}
        try:
            saved = persist_unhandled_stop(Path(getattr(a, "task_root", TASK_ROOT)),
                                           job=identity["job"], role=identity["role"],
                                           shard=identity["shard"], driver_rc=identity["driver_rc"],
                                           exception=exc)
            print(f"FAIL-CLOSED: callback exception recorded; no further dispatch: {json.dumps(saved)}",
                  file=sys.stderr)
        except Exception as persist_exc:
            # Do not retry failed writes. Report that the guard itself could not
            # persist so the owner can inspect manually; never continue dispatch.
            print("FAIL-CLOSED PERSISTENCE FAILURE: "
                  f"callback job={identity['job']} role={identity['role']} shard={identity['shard']} "
                  f"error={type(exc).__name__}: {exc}; persistence_error={type(persist_exc).__name__}: {persist_exc}; "
                  "no admission retry was attempted.", file=sys.stderr)
        print(f"ERROR: {type(exc).__name__}: {exc}; callback identity={identity}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
