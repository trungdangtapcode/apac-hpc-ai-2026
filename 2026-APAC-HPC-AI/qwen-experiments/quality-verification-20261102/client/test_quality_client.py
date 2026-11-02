#!/usr/bin/env python3
"""Network-local fixture tests; no model, GPU, credential, or external service."""
from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
import threading
import time
import unittest
from collections import Counter, UserDict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import quality_client as qc


def digest(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


class FixtureHandler(BaseHTTPRequestHandler):
    lock = threading.Lock()
    seen = Counter()
    active = 0
    max_active = 0

    def do_POST(self):
        n = int(self.headers.get("Content-Length", "0"))
        body = json.loads(self.rfile.read(n))
        prompt = body["messages"][0]["content"]
        qid = int(prompt.split("qid=")[1].split()[0])
        with self.lock:
            type(self).seen[qid] += 1
            type(self).active += 1
            type(self).max_active = max(type(self).max_active, type(self).active)
        time.sleep(0.06)
        if qid == 3:
            payload = json.dumps({"error": {"message": "fixture failure"}}).encode()
            self.send_response(503)
        else:
            payload = json.dumps({"id": f"req-{qid}", "choices": [{"message": {"content": "Reasoning. The answer is (A)"}, "finish_reason": "stop"}], "usage": {"prompt_tokens": 9, "completion_tokens": 4, "total_tokens": 13}}).encode()
            self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)
        with self.lock:
            type(self).active -= 1

    def log_message(self, *_):
        pass


class ClientTests(unittest.TestCase):
    def test_tokenizer_list_and_documented_single_item_mapping(self):
        class FakeTokenizer:
            def __init__(self, result): self.result, self.kwargs = result, None
            def apply_chat_template(self, messages, **kwargs):
                self.kwargs = kwargs
                self.messages = messages
                return self.result

        direct = FakeTokenizer([3, 8, 13])
        self.assertEqual(qc.tokenize(direct, "p"), [3, 8, 13])
        self.assertIs(direct.kwargs["return_dict"], False)
        self.assertTrue(direct.kwargs["tokenize"])
        mapped = FakeTokenizer(UserDict({"input_ids": [[21, 34]], "attention_mask": [[1, 1]]}))
        self.assertEqual(qc.tokenize(mapped, "p"), [21, 34])

    def test_tokenizer_refuses_missing_or_ambiguous_batch_mapping(self):
        class FakeTokenizer:
            def __init__(self, result): self.result = result
            def apply_chat_template(self, *_args, **_kwargs): return self.result

        with self.assertRaisesRegex(ValueError, "no input_ids"):
            qc.tokenize(FakeTokenizer(UserDict({"attention_mask": [[1]]})), "p")
        with self.assertRaisesRegex(ValueError, "batch of 2"):
            qc.tokenize(FakeTokenizer(UserDict({"input_ids": [[1, 2], [3, 4]]})), "p")

    def test_pinned_parser_order_and_invalid_wrong(self):
        self.assertEqual(qc.official_parse("A then the answer is (C)"), ("C", "answer_is"))
        self.assertEqual(qc.official_parse("Answer: B"), ("B", "answer_colon"))
        self.assertEqual(qc.official_parse("I choose D"), ("D", "final_standalone_letter"))
        self.assertEqual(qc.official_parse("No parseable option"), (None, "invalid_unparsed"))
        self.assertIsNone(qc.strict_parse("Answer: B"))
        self.assertEqual(qc.strict_parse("Done. The answer is (J)."), "J")

    def test_fixed_denominator_counts_missing_and_service_error_wrong(self):
        rows = [
            {"question_id": 1, "category": "math", "status": "OK", "predicted_answer": "A", "expected_answer": "A"},
            {"question_id": 2, "category": "math", "status": "OK", "predicted_answer": None, "expected_answer": "B"},
            {"question_id": 3, "category": "math", "status": "ERROR", "predicted_answer": None, "expected_answer": "A"},
        ]
        s = qc.summarize_records(rows, [1, 2, 3, 4])
        self.assertEqual((s["denominator"], s["correct"], s["accuracy"]), (4, 1, 0.25))
        self.assertEqual(s["service_errors_in_denominator"], 2)
        self.assertEqual(s["missing_ids"], [4])
        self.assertFalse(s["coverage_complete"])

    def test_concurrent_http_raw_response_and_no_retry(self):
        FixtureHandler.seen = Counter(); FixtureHandler.active = 0; FixtureHandler.max_active = 0
        server = ThreadingHTTPServer(("127.0.0.1", 0), FixtureHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
        try:
            with tempfile.TemporaryDirectory() as tmp_s:
                tmp = Path(tmp_s)
                corpus = tmp / "corpus.jsonl"
                rows = []
                for qid in range(1, 5):
                    prompt = f"fixture qid={qid}"
                    rows.append({"question_id": qid, "category": "math", "expected_answer": "A",
                                 "prompt": prompt, "messages": [{"role": "user", "content": prompt}],
                                 "prompt_sha256": digest(prompt), "token_ids_sha256": digest("tokens"),
                                 "shots_used": 5, "preparation_status": "READY"})
                qc.write_jsonl(corpus, rows)
                prep = tmp / "prepare-manifest.json"
                qc.atomic_json(prep, {"status": "READY", "generation_blocked": False,
                                      "compiled_corpus_sha256": qc.file_sha(corpus), "question_count": 4})
                a = argparse.Namespace(corpus=str(corpus), prepare_manifest=str(prep), base_url=f"http://127.0.0.1:{server.server_port}/v1",
                                       model="qwen-fixture", out=str(tmp / "run"), concurrency=3, timeout=2,
                                       deadline_epoch=None, deadline_margin=0, ids_file=None, shard_count=0, shard_index=0, api_key_env=None)
                rc = qc.cmd_run(a)
                run = json.loads((tmp / "run" / "run.json").read_text())
                out = qc.read_jsonl(tmp / "run" / "responses.jsonl")
                self.assertEqual(rc, 0)  # all four fixed-denominator slots have terminal records
                self.assertEqual(run["status"], "COMPLETE")
                self.assertEqual(len(out), 4)
                self.assertEqual(sum(r["status"] == "ERROR" for r in out), 1)
                self.assertEqual(next(r for r in out if r["question_id"] == 1)["raw_response_body"] is not None, True)
                self.assertEqual(FixtureHandler.seen, Counter({1: 1, 2: 1, 3: 1, 4: 1}))
                self.assertGreater(FixtureHandler.max_active, 1)
                summary = json.loads((tmp / "run" / "summary.json").read_text())
                self.assertEqual(summary["denominator"], 4)
                self.assertEqual(summary["service_errors_in_denominator"], 1)
        finally:
            server.shutdown(); server.server_close(); thread.join(timeout=2)

    def test_deadline_writes_not_started_fixed_slots_without_http(self):
        with tempfile.TemporaryDirectory() as tmp_s:
            tmp = Path(tmp_s)
            prompt = "deadline fixture"
            corpus = tmp / "c.jsonl"
            qc.write_jsonl(corpus, [{"question_id": 1, "category": "math", "expected_answer": "A", "messages": [{"role": "user", "content": prompt}], "prompt_sha256": digest(prompt), "token_ids_sha256": digest("t"), "shots_used": 0, "preparation_status": "READY"}])
            prep = tmp / "p.json"
            qc.atomic_json(prep, {"status": "READY", "compiled_corpus_sha256": qc.file_sha(corpus), "question_count": 1})
            a = argparse.Namespace(corpus=str(corpus), prepare_manifest=str(prep), base_url="http://127.0.0.1:1/v1", model="qwen", out=str(tmp / "r"), concurrency=1, timeout=120, deadline_epoch=time.time() + 1, deadline_margin=120, ids_file=None, shard_count=0, shard_index=0, api_key_env=None)
            self.assertEqual(qc.cmd_run(a), 3)
            rec = qc.read_jsonl(tmp / "r" / "responses.jsonl")[0]
            self.assertEqual(rec["status"], "NOT_STARTED_DEADLINE")
            self.assertEqual(json.loads((tmp / "r" / "run.json").read_text())["status"], "INCOMPLETE")
            self.assertEqual(json.loads((tmp / "r" / "summary.json").read_text())["service_errors_in_denominator"], 1)

    def test_compare_ratio_and_exact_coverage_gate(self):
        with tempfile.TemporaryDirectory() as tmp_s:
            tmp = Path(tmp_s)
            ids = [1, 2, 3, 4]
            common = {"status": "COMPLETE", "corpus_sha256": "same", "prepare_manifest_sha256": "prep",
                      "selected_question_ids": ids, "selected_count": 4,
                      "generation": {"temperature": 0, "top_p": 1, "max_tokens": 2048, "stop": ["Question:"], "stream": False}}
            for name, wrong in (("ref", set()), ("cand-pass", set()), ("cand-fail", {4})):
                d = tmp / name; d.mkdir()
                qc.atomic_json(d / "run.json", common)
                records = []
                for qid in ids:
                    pred = "B" if qid in wrong else "A"
                    records.append({"question_id": qid, "category": "math", "status": "OK", "expected_answer": "A", "predicted_answer": pred})
                qc.write_jsonl(d / "responses.jsonl", records)
            def compare(r, c):
                return qc.cmd_compare(argparse.Namespace(reference=str(tmp / r), candidate=str(tmp / c), out=None))
            self.assertEqual(compare("ref", "cand-pass"), 0)
            self.assertEqual(compare("ref", "cand-fail"), 4)


if __name__ == "__main__":
    unittest.main(verbosity=2)
