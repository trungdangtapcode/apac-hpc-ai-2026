#!/usr/bin/env python3
"""CPU tests for portable worker draft identity and all-role gating."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("draft_fingerprint", HERE / "draft-fingerprint.py")
fingerprint = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fingerprint)
spec2 = importlib.util.spec_from_file_location("headcheck_worker_drafts", HERE / "headcheck-worker-drafts.py")
headcheck = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(headcheck)

QWEN = Path("/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments")
PARENT_REPORT = QWEN / "runs/25682/draft-full-verification.json"
ACTUAL_DRAFT = QWEN / "hf-cache/drafts/nebius-eagle3-qwen235b-ff0f0c09"
ORIGINAL_VERIFIER = QWEN / "runs/25682/submitted-payload/verify-draft.py"


def valid_report():
    report = json.loads(PARENT_REPORT.read_text())
    # This simulates another node/mount: stat identity is intentionally unrelated.
    for i, row in enumerate(report["files"]):
        row["fingerprint"] = {key: (9000 + i * 100 + n) for n, key in enumerate(fingerprint.FINGERPRINT_FIELDS)}
        row["fingerprint"]["st_size"] = row["bytes"]
    return report


class FakeVerifier:
    def __init__(self, report):
        self.report = report

    def verify(self, draft):
        return copy.deepcopy(self.report)


class PortableIdentityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.parent = self.root / "parent.json"
        self.parent.write_bytes(PARENT_REPORT.read_bytes())
        self.draft = self.root / "draft"
        self.draft.mkdir()
        self.now = 1_800_000_000

    def tearDown(self):
        self.temp.cleanup()

    def call_run(self, role, verifier=None, parent=None):
        return fingerprint.run(self.draft, parent or self.parent, role=role,
                               artifact_root=self.root / "artifacts",
                               job_start_epoch=self.now - 1,
                               verifier=verifier or FakeVerifier(valid_report()), now=lambda: self.now)

    def test_same_content_with_different_parent_stat_is_accepted(self):
        self.call_run("prefill-0")
        receipt = json.loads((self.root / "artifacts/draft-worker-verifications/prefill-0.json").read_text())
        self.assertEqual(receipt["state"], "PASS")
        self.assertNotEqual(receipt["observed_local_fingerprints"]["model.safetensors"],
                            json.loads(self.parent.read_text())["files"][0]["fingerprint"])

    def test_hash_size_and_revision_mismatch_are_rejected(self):
        for mutate in (
            lambda report: report["files"][0].update(sha256="0" * 64),
            lambda report: report["files"][0].update(bytes=report["files"][0]["bytes"] - 1),
            lambda report: report.update(revision="0" * 40),
        ):
            report = valid_report()
            mutate(report)
            with self.subTest(report=report.get("revision")):
                with self.assertRaises(ValueError):
                    self.call_run("prefill-0", FakeVerifier(report))

    def test_unknown_or_missing_role_is_rejected(self):
        with self.assertRaises(ValueError):
            self.call_run("prefill0")
        for role in fingerprint.ROLES:
            if role != "decode-0":
                self.call_run(role)
        with self.assertRaises(FileNotFoundError):
            headcheck.check(self.root / "artifacts", self.parent)

    def test_headcheck_requires_three_exact_role_receipts(self):
        for role in fingerprint.ROLES:
            self.call_run(role)
        result = headcheck.check(self.root / "artifacts", self.parent)
        self.assertEqual(result["state"], "PASS")
        path = self.root / "artifacts/draft-worker-verifications/decode-0.json"
        path.unlink()
        with self.assertRaises(FileNotFoundError):
            headcheck.check(self.root / "artifacts", self.parent)

    def test_headcheck_rejects_role_parent_and_pass_mismatches(self):
        for role in fingerprint.ROLES:
            self.call_run(role)
        path = self.root / "artifacts/draft-worker-verifications/prefill-1.json"
        original = json.loads(path.read_text())
        for key, value in (("role", "decode-0"),
                           ("parent_report_sha256", "0" * 64),
                           ("verification_state", "FAIL")):
            changed = dict(original)
            changed[key] = value
            path.write_text(json.dumps(changed))
            with self.subTest(field=key), self.assertRaises(ValueError):
                headcheck.check(self.root / "artifacts", self.parent)
        path.write_text(json.dumps(original))

    def test_full_original_verifier_runs_on_actual_staged_draft(self):
        self.assertTrue(ACTUAL_DRAFT.joinpath("model.safetensors").is_file())
        receipt = fingerprint.run(ACTUAL_DRAFT, PARENT_REPORT, role="decode-0",
                                  artifact_root=self.root / "artifacts",
                                  job_start_epoch=self.now - 1, verifier_path=ORIGINAL_VERIFIER,
                                  now=lambda: self.now)
        self.assertEqual(receipt["state"], "PASS")
        self.assertEqual(receipt["portable_identity"]["files"]["model.safetensors"]["bytes"], 1145943008)
        self.assertEqual(receipt["portable_identity"]["files"]["model.safetensors"]["sha256"], fingerprint.WEIGHT_SHA256)


if __name__ == "__main__":
    unittest.main(verbosity=2)
