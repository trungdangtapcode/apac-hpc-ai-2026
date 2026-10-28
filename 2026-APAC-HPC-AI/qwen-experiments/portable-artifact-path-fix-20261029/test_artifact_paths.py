#!/usr/bin/env python3
"""Targeted regression checks for portable AIPerf artifact layout handling."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from artifact_paths import resolve_artifacts


class ArtifactPathTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    @staticmethod
    def pair(directory):
        directory.mkdir(parents=True, exist_ok=True)
        (directory / 'profile_export_aiperf.json').write_text('{}')
        (directory / 'profile_export.jsonl').write_text('')

    def test_legacy_flat_pair(self):
        root = self.base / 'flat'; self.pair(root)
        a, b = resolve_artifacts(root)
        self.assertEqual(a.parent, root); self.assertEqual(b.parent, root)

    def test_nested_pair(self):
        root = self.base / 'nested'; self.pair(root / 'qwen-openai-chat-concurrency64')
        a, b = resolve_artifacts(root)
        self.assertEqual(a.parent.name, 'qwen-openai-chat-concurrency64')
        self.assertEqual(b.parent, a.parent)

    def test_ambiguous_pairs_rejected(self):
        root = self.base / 'ambiguous'; self.pair(root); self.pair(root / 'namespace')
        with self.assertRaisesRegex(ValueError, 'Ambiguous'):
            resolve_artifacts(root)

    def test_incomplete_pair_rejected(self):
        root = self.base / 'incomplete'; root.mkdir(); (root / 'profile_export_aiperf.json').write_text('{}')
        with self.assertRaisesRegex(ValueError, 'Incomplete'):
            resolve_artifacts(root)

    def test_missing_pair_rejected(self):
        root = self.base / 'missing'; root.mkdir()
        with self.assertRaisesRegex(ValueError, 'No complete'):
            resolve_artifacts(root)

    def test_symlink_escape_rejected(self):
        root = self.base / 'escape'; root.mkdir()
        outside = self.base / 'outside'; self.pair(outside)
        (root / 'namespace').symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'Symlink namespace'):
            resolve_artifacts(root)

    def test_injected_bad_request_fails_score_gate(self):
        root = self.base / 'bad-run'; art = root / 'official' / 'n64' / 'artifacts'
        self.pair(art / 'nested')
        export = {
            'request_count': {'avg': 1}, 'good_request_count': {'avg': 0},
            'good_request_fraction': {'avg': 0.0}, 'goodput': {'avg': 2.0},
            'was_cancelled': False, 'error_summary': None,
        }
        (art / 'nested' / 'profile_export_aiperf.json').write_text(json.dumps(export))
        row = {'metadata': {'phase_kind': 'profiling'}, 'metrics': {
            'time_to_first_token': {'value': 3100}, 'inter_token_latency': {'value': 10}}}
        (art / 'nested' / 'profile_export.jsonl').write_text(json.dumps(row) + '\n')
        (root / 'official' / 'n64' / 'client.log').write_text(
            'Phase profiling (profiling) complete | completed=1, cancelled=0, errors=0\n')
        result = subprocess.run([sys.executable, str(HERE / 'score-gate.py'), str(root), '64'],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn('Joint SLA below 90%', result.stdout)

    def test_summarize_reads_nested_and_legacy(self):
        root = self.base / 'summary-run'
        for phase, nested in (('legacy', False), ('official', True)):
            art = root / phase / 'n64' / 'artifacts'
            target = art / 'child' if nested else art
            self.pair(target)
            export = {
                'goodput': {'avg': 15}, 'good_request_fraction': {'avg': .95},
                'request_count': {'avg': 10}, 'error_request_count': {'avg': 0},
                'output_token_throughput': {'avg': 3000},
                'time_to_first_token': {'avg': 100, 'p95': 200},
                'inter_token_latency': {'avg': 10, 'p95': 15},
            }
            (target / 'profile_export_aiperf.json').write_text(json.dumps(export))
            (art.parent / 'client.log').write_text('Phase profiling (profiling) complete | completed=10, cancelled=0, errors=0\n')
        result = subprocess.run([sys.executable, str(HERE / 'summarize.py'), str(root)],
                                capture_output=True, text=True, check=True)
        rows = json.loads(result.stdout)
        self.assertEqual(len(rows), 2)
        self.assertEqual({r['phase'] for r in rows}, {'legacy', 'official'})
        self.assertTrue(all(r['good_output_tokens_s'] == 3000 for r in rows))
        self.assertTrue(all(r['cancelled_requests'] == 0 for r in rows))


if __name__ == '__main__':
    unittest.main(verbosity=2)
