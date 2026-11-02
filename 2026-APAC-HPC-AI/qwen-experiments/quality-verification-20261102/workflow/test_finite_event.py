#!/usr/bin/env python3
"""Finite workflow fixtures; no Slurm, model endpoint, GPU, or admission call."""
from __future__ import annotations

import json
import signal
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path
from io import StringIO
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import finite_event as fe


def make_response(qid: int, expected: dict, answer="A", status="OK"):
    text = f"The answer is ({answer})"
    return {"question_id": qid, "category": expected["category"],
            "expected_answer": expected["expected_answer"],
            "prompt_sha256": expected["prompt_sha256"],
            "token_ids_sha256": expected["token_ids_sha256"],
            "shots_used": expected["shots_used"], "status": status,
            "http_status": 200 if status == "OK" else 503,
            "raw_response_body": json.dumps({"choices": [{"message": {"content": text}, "finish_reason": "stop"}]}),
            "completion_text": text, "predicted_answer": answer,
            "finish_reason": "stop"}


class FiniteEventTests(unittest.TestCase):
    def setUp(self):
        self.expected = {
            10: {"category": "math", "expected_answer": "A", "prompt_sha256": "p10", "token_ids_sha256": "t10", "shots_used": 5},
            20: {"category": "physics", "expected_answer": "B", "prompt_sha256": "p20", "token_ids_sha256": "t20", "shots_used": 4},
        }

    def test_recomputes_raw_outputs_against_frozen_expected_ids(self):
        rows = [make_response(q, v, answer=v["expected_answer"]) for q, v in self.expected.items()]
        stats = fe.validate_response_records(rows, self.expected, [10, 20], fe.load_pinned_parser(fe.TASK_ROOT))
        self.assertEqual(stats, {"correct": 2, "accuracy": 1.0, "service_errors": 0,
                                 "invalid_outputs": 0, "truncated_outputs": 0})

    def test_rejects_missing_extra_duplicate_ids_and_prompt_mismatch(self):
        parse = fe.load_pinned_parser(fe.TASK_ROOT)
        rows = [make_response(q, v) for q, v in self.expected.items()]
        with self.assertRaisesRegex(fe.ValidationFailure, "one record"):
            fe.validate_response_records(rows[:1], self.expected, [10, 20], parse)
        with self.assertRaisesRegex(fe.ValidationFailure, "one record"):
            fe.validate_response_records(rows + [rows[0]], self.expected, [10, 20], parse)
        wrong = [dict(x) for x in rows]; wrong[0]["prompt_sha256"] = "tampered"
        with self.assertRaisesRegex(fe.ValidationFailure, "prompt_sha256"):
            fe.validate_response_records(wrong, self.expected, [10, 20], parse)

    def test_service_error_is_invalid_for_dispatch(self):
        parse = fe.load_pinned_parser(fe.TASK_ROOT)
        rows = [make_response(q, v) for q, v in self.expected.items()]
        rows[0]["status"] = "ERROR"; rows[0]["http_status"] = 503
        with self.assertRaisesRegex(fe.ValidationFailure, "HTTP/client errors"):
            fe.validate_response_records(rows, self.expected, [10, 20], parse)

    def test_nonzero_driver_writes_stop_and_never_dispatches(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); (root / "admission-full8").mkdir()
            ledger = root / "admission-full8" / "ledger.json"
            ledger.write_text(json.dumps({"jobs": {"reference-00": {"job": 7001, "role": "reference", "shard_index": 0, "shard_count": 8, "questions": 2, "concurrency": 64}}}))
            result = fe.handle_event(root, job=7001, role="reference", shard=0, driver_rc=9,
                                     ledger_path=ledger, expected_count=2, no_dispatch=True)
            self.assertEqual(result["state"], "STOPPED")
            event = json.loads((root / "workflow/events/reference-00-job7001.json").read_text())
            self.assertEqual(event["status"], "INVALID")
            self.assertTrue((root / "workflow/STOP.json").exists())

    def test_existing_stop_prevents_dispatch_even_on_repeat(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); workflow = root / "workflow"; workflow.mkdir()
            (workflow / "STOP.json").write_text(json.dumps({"status": "STOPPED"}))
            (workflow / "events").mkdir()
            event = {"status": "VALID", "job_id": 7002, "role": "candidate", "shard_index": 0,
                     "driver_rc": 0, "evaluation_dir": "/fixture"}
            (workflow / "events/candidate-00-job7002.json").write_text(json.dumps(event))
            calls = []
            result = fe.handle_event(root, job=7002, role="candidate", shard=0, driver_rc=0,
                                     expected_count=2, dispatch_existing=True,
                                     queue_query=lambda: calls.append("queue") or (True, 0, ""),
                                     admit=lambda p: calls.append("admit") or {"returncode": 0})
            self.assertEqual(result["state"], "STOPPED")
            self.assertEqual(calls, [])

    def test_five_queue_jobs_defer_without_admission(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); workflow = root / "workflow"; (workflow / "events").mkdir(parents=True)
            (root / "reviews").mkdir()
            (root / "reviews/first-full-pair-qualification.json").write_text(json.dumps({"passed": True}))
            ledger_path = root / "admission-full8/ledger.json"; ledger_path.parent.mkdir()
            ledger_path.write_text(json.dumps({"jobs": {}, "first_pair_qualified": True, "own_active_pending_cap": 5}))
            event = {"status": "VALID", "job_id": 7003, "role": "reference", "shard_index": 1,
                     "driver_rc": 0, "evaluation_dir": "/fixture"}
            (workflow / "events/reference-01-job7003.json").write_text(json.dumps(event))
            calls = []
            result = fe.handle_event(root, job=7003, role="reference", shard=1, driver_rc=0,
                                     ledger_path=ledger_path, expected_count=2, dispatch_existing=True,
                                     queue_query=lambda: (True, 5, "five rows"),
                                     admit=lambda p: calls.append(p) or {"returncode": 0})
            self.assertEqual(result["state"], "DEFERRED_CAP")
            self.assertEqual(calls, [])

    def test_admission_timeout_kills_process_group_and_preserves_ambiguity(self):
        class HungAdmission:
            pid = 4567
            returncode = None
            def __init__(self): self.timeouts = []
            # Model an admission parent that exited while a child still holds
            # the pipes open; timeout cleanup must kill the whole PGID anyway.
            def poll(self): return 0
            def communicate(self, timeout):
                self.timeouts.append(timeout)
                if len(self.timeouts) == 1:
                    raise subprocess.TimeoutExpired("admit_full.py", timeout, output="job may be accepted")
                self.returncode = -signal.SIGKILL
                return ("partial sbatch output", "killed after timeout")

        proc = HungAdmission()
        with mock.patch.object(fe.subprocess, "Popen", return_value=proc) as popen, \
                mock.patch.object(fe.os, "killpg") as killpg:
            result = fe.dispatch_fill(Path("/fixture/admit_full.py"))
        popen.assert_called_once()
        self.assertIs(popen.call_args.kwargs["start_new_session"], True)
        self.assertEqual(proc.timeouts, [180, 10])
        killpg.assert_called_once_with(proc.pid, signal.SIGKILL)
        self.assertTrue(result["timed_out"])
        self.assertTrue(result["ambiguous_submission_possible"])
        self.assertTrue(result["manual_reconciliation_required"])
        self.assertIn("may already have been accepted", result["error"])

    def test_ambiguous_admission_result_writes_stop_and_never_retries(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); workflow = root / "workflow"; (workflow / "events").mkdir(parents=True)
            (root / "reviews").mkdir()
            (root / "reviews/first-full-pair-qualification.json").write_text(json.dumps({"passed": True}))
            ledger_path = root / "admission-full8/ledger.json"; ledger_path.parent.mkdir()
            ledger_path.write_text(json.dumps({"jobs": {}, "first_pair_qualified": True, "own_active_pending_cap": 5}))
            event = {"status": "VALID", "job_id": 7004, "role": "reference", "shard_index": 1,
                     "driver_rc": 0, "evaluation_dir": "/fixture"}
            (workflow / "events/reference-01-job7004.json").write_text(json.dumps(event))
            calls = []
            result = fe.handle_event(root, job=7004, role="reference", shard=1, driver_rc=0,
                                     ledger_path=ledger_path, expected_count=2, dispatch_existing=True,
                                     queue_query=lambda: (True, 1, "one row"),
                                     admit=lambda p: calls.append(p) or {"returncode": None,
                                         "ambiguous_submission_possible": True,
                                         "manual_reconciliation_required": True,
                                         "error": "sbatch may have been accepted"})
            self.assertEqual(result["state"], "STOPPED")
            self.assertEqual(len(calls), 1)
            stop = json.loads((workflow / "STOP.json").read_text())
            self.assertIn("no automatic retry", stop["reason"])
            self.assertTrue(stop["details"]["admission"]["ambiguous_submission_possible"])

    def test_main_persists_fail_closed_stop_for_malformed_ledger(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            ledger = root / "ledger.json"; ledger.write_text("{malformed")
            argv = ["finite_event.py", "--job", "7101", "--role", "reference", "--shard", "0",
                    "--driver-rc", "0", "--task-root", str(root), "--ledger", str(ledger)]
            stderr = StringIO()
            with mock.patch.object(sys, "argv", argv), mock.patch.object(fe, "dispatch_fill") as dispatch, \
                    redirect_stderr(stderr):
                rc = fe.main()
            self.assertEqual(rc, 2)
            dispatch.assert_not_called()
            stop = json.loads((root / "workflow/STOP.json").read_text())
            self.assertEqual((stop["job_id"], stop["role"], stop["shard_index"]), (7101, "reference", 0))
            self.assertEqual(stop["exception_type"], "ValidationFailure")
            self.assertIn("invalid JSON", stop["exception"])
            state = json.loads((root / "workflow/STATE.json").read_text())
            self.assertEqual(state["status"], "STOPPED")

    def test_main_persists_unexpected_noninteger_id_validation_exception(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            argv = ["finite_event.py", "--job", "7102", "--role", "candidate", "--shard", "3",
                    "--driver-rc", "0", "--task-root", str(root)]
            stderr = StringIO()
            with mock.patch.object(sys, "argv", argv), \
                    mock.patch.object(fe, "handle_event", side_effect=ValueError("non-integer question ID")), \
                    mock.patch.object(fe, "dispatch_fill") as dispatch, redirect_stderr(stderr):
                rc = fe.main()
            self.assertEqual(rc, 2)
            dispatch.assert_not_called()
            stop = json.loads((root / "workflow/STOP.json").read_text())
            self.assertEqual((stop["job_id"], stop["role"], stop["shard_index"]), (7102, "candidate", 3))
            self.assertEqual(stop["exception"], "non-integer question ID")

    def test_all_sixteen_events_runs_aggregator_and_local_fail_is_completed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); workflow = root / "workflow"; events = workflow / "events"; events.mkdir(parents=True)
            for role in fe.ROLE_NAMES:
                for shard in range(fe.SHARD_COUNT):
                    key = f"{role}-{shard:02d}"
                    (events / f"{key}-job{8000+shard}.json").write_text(json.dumps({
                        "status": "VALID", "job_id": 8000 + shard, "role": role,
                        "shard_index": shard, "driver_rc": 0,
                        "evaluation_dir": f"/fixture/{role}/{shard}"}))
            called = []
            def fake_aggregate(refs, cands, out):
                called.append((len(refs), len(cands)))
                return {"status": "LOCAL_FULLSET_GATE_FAIL", "reason": "quality ratio below 0.99"}
            result = fe._finish_if_complete(root, workflow, root / "prepare.json", root / "corpus.jsonl",
                                            aggregate_runner=fake_aggregate)
            state = json.loads((workflow / "STATE.json").read_text())
            self.assertEqual(result["status"], "LOCAL_FULLSET_GATE_FAIL")
            self.assertEqual(called, [(8, 8)])
            self.assertEqual(state["status"], "COMPLETED")
            self.assertFalse((workflow / "STOP.json").exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
