#!/usr/bin/env python3
"""Tiny pure-local fixtures for full-set shard aggregation invariants."""
from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import aggregate_full as agg


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def jsonl_write(path: Path, rows: list[dict]) -> None:
    path.write_text("".join(json.dumps(x, sort_keys=True, separators=(",", ":")) + "\n" for x in rows))


def make_expected():
    return {
        qid: {"question_id": qid, "category": "math" if qid < 3 else "physics",
              "expected_answer": "A", "prompt_sha256": f"p{qid}",
              "token_ids_sha256": f"t{qid}", "shots_used": 5, "preparation_status": "READY"}
        for qid in (1, 2, 3, 4)
    }


def response(qid: int, *, status="OK", answer="A", finish="stop", body=None):
    text = f"The answer is ({answer})" if answer else "unparseable"
    if body is None:
        body = json.dumps({"choices": [{"message": {"content": text}, "finish_reason": finish}]})
    return {"question_id": qid, "category": "math" if qid < 3 else "physics",
            "expected_answer": "A", "prompt_sha256": f"p{qid}", "token_ids_sha256": f"t{qid}",
            "shots_used": 5, "status": status, "http_status": 200 if status == "OK" else 503,
            "raw_response_body": body, "completion_text": text if status == "OK" else None,
            "predicted_answer": answer if status == "OK" else None,
            "finish_reason": finish if status == "OK" else None}


class AggregateTests(unittest.TestCase):
    def test_different_shard_counts_full_coverage_and_local_ratio(self):
        expected = make_expected()
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            ref_dirs = self._write_role(root, "ref", [([1, 2], [response(1), response(2)]),
                                                       ([3, 4], [response(3), response(4)])])
            cand_dirs = self._write_role(root, "cand", [([1, 2, 3, 4], [response(q) for q in (1, 2, 3, 4)])])
            ref = agg.aggregate_role(ref_dirs, expected, "corpus", "prep")
            cand = agg.aggregate_role(cand_dirs, expected, "corpus", "prep")
            self.assertEqual(ref["n"], 4)
            self.assertEqual(ref["correct"], 4)
            self.assertEqual(cand["accuracy"] / ref["accuracy"], 1.0)
            self.assertEqual(len(ref["source_runs"]), 2)
            self.assertTrue(agg.compare_roles(ref, cand)["local_engineering_gate_pass"])

    def test_errors_invalid_truncation_and_fixed_denominator(self):
        expected = make_expected()
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            rows = [response(1), response(2, answer=None),
                    response(3, status="ERROR", body='{"error":"fixture"}'),
                    response(4, finish="length")]
            dirs = self._write_role(root, "role", [(list(range(1, 5)), rows)])
            result = agg.aggregate_role(dirs, expected, "corpus", "prep")
            self.assertEqual(result["n"], 4)
            self.assertEqual(result["correct"], 2)
            self.assertEqual(result["service_errors"], 1)
            self.assertEqual(result["invalid_outputs"], 1)
            self.assertEqual(result["truncated_outputs"], 1)
            self.assertEqual(result["categories"]["math"]["n"], 2)

    def test_rejects_overlap_duplicate_missing_and_extra_shards(self):
        expected = make_expected()
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            overlap = self._write_role(root, "overlap", [([1, 2], [response(1), response(2)]),
                                                           ([2, 3, 4], [response(2), response(3), response(4)])])
            with self.assertRaisesRegex(ValueError, "overlapping source shards"):
                agg.aggregate_role(overlap, expected, "corpus", "prep")
            missing = self._write_role(root, "missing", [([1, 2, 3], [response(1), response(2), response(3)])])
            with self.assertRaisesRegex(ValueError, "missing="):
                agg.aggregate_role(missing, expected, "corpus", "prep")
            extra = self._write_role(root, "extra", [([1, 2, 3, 4, 9], [response(1), response(2), response(3), response(4), response(9)])])
            with self.assertRaisesRegex(ValueError, "outside compiled corpus"):
                agg.aggregate_role(extra, expected, "corpus", "prep")

    def test_rejects_prompt_label_protocol_or_terminal_state_mismatch(self):
        expected = make_expected()
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            bad = response(1); bad["prompt_sha256"] = "changed"
            dirs = self._write_role(root, "bad-prompt", [([1], [bad])])
            with self.assertRaisesRegex(ValueError, "prompt_sha256 differs"):
                agg.aggregate_role(dirs, expected, "corpus", "prep")
            dirs2 = self._write_role(root, "incomplete", [([1], [response(1)])], run_status="INCOMPLETE")
            with self.assertRaisesRegex(ValueError, "not COMPLETE"):
                agg.aggregate_role(dirs2, expected, "corpus", "prep")

    def test_prepared_manifest_sha_and_exact_full_count(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            rows = list(make_expected().values())
            # Add the chat request and READY fields expected in a compiled corpus.
            for row in rows:
                row.update({"messages": [{"role": "user", "content": "fixture"}]})
            corpus = root / "compiled.jsonl"
            jsonl_write(corpus, rows)
            prep = root / "prepare.json"
            prep.write_text(json.dumps({"status": "READY", "generation_blocked": False,
                                       "question_count": 4, "compiled_corpus_sha256": sha(corpus.read_bytes())}))
            by_id, corpus_hash, prep_hash = agg.validate_prepared(prep, corpus, expected_count=4)
            self.assertEqual(len(by_id), 4)
            self.assertEqual(corpus_hash, sha(corpus.read_bytes()))
            self.assertEqual(prep_hash, sha(prep.read_bytes()))
            with self.assertRaisesRegex(ValueError, "question_count"):
                agg.validate_prepared(prep, corpus, expected_count=5)
            corpus.write_text(corpus.read_text() + "{}\n")
            with self.assertRaisesRegex(ValueError, "SHA-256"):
                agg.validate_prepared(prep, corpus, expected_count=4)

    @staticmethod
    def _write_role(root: Path, role: str, shards, run_status="COMPLETE"):
        dirs = []
        for index, (ids, records) in enumerate(shards):
            d = root / f"{role}-{index}"; d.mkdir()
            run = {"status": run_status, "corpus_sha256": "corpus", "prepare_manifest_sha256": "prep",
                   "generation": agg.PINNED_GENERATION, "served_model": role,
                   "selected_question_ids": ids, "selected_count": len(ids)}
            (d / "run.json").write_text(json.dumps(run))
            jsonl_write(d / "responses.jsonl", records)
            dirs.append(d)
        return dirs


if __name__ == "__main__":
    unittest.main(verbosity=2)
