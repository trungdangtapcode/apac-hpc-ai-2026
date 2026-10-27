#!/usr/bin/env python3
"""Offline financial, queue, sealing, and one-shot admission checks."""
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import admission as a


REPORT = '''
Project 59000042 balance
| Unit   | Grant | Used | Balance | In Doubt |
| SU     | 30000.000 | 222.154 | 29777.846 | 0.000 |
Project 59000042 SU Usage breakdown
| Unit | Usage | SU Rate | SU Used |
| CPU Hour | 222.154 | 1 | 222.154 |
'''


def ledger():
    return {'schema': 2, 'project': '59000042', 'baseline_wave_planning_ceiling_SU': 29777.846,
            'published_snapshot': {'used_SU': 222.154}, 'consumed_ceiling_SU': 2254,
            'outstanding_reserved_max_SU': 2603.2, 'reserved_max_SU': 4857.2,
            'planning_committed_SU': 4857.2,
            'jobs': [{'id': '26019383.pbs101', 'state': 'SUBMITTED', 'maximum_SU': 85.3333333333}]}


def completed(value: str, returncode: int = 0) -> subprocess.CompletedProcess:
    return subprocess.CompletedProcess([], returncode, value.encode(), b'')


def fake_qstat(jobs: dict) -> str:
    return json.dumps({'Jobs': jobs})


def job(job_id: str, state: str, owner: str = 'apacsc42@cpu') -> dict:
    return {'Job_Owner': owner, 'job_state': state,
            'Variable_List': {'SECRET_TOKEN': 'must_not_be_saved'}}


class AdmissionTests(unittest.TestCase):
    def test_project_parser_reads_the_cpu_hour_rate_column(self):
        parsed = a.parse_project_report(REPORT)
        self.assertEqual(parsed['rate_SU_per_CPU_hour'], 1)
        self.assertEqual(parsed['in_doubt_SU'], 0)
        with self.assertRaisesRegex(ValueError, 'header'):
            a.parse_project_report(REPORT.replace('Project 59000042 balance', 'Project 59010042 balance'))

    def test_negative_zero_is_accepted_but_nonfinite_is_rejected(self):
        text = REPORT.replace('0.000 |\nProject', '-0.000 |\nProject')
        self.assertEqual(a.parse_project_report(text)['in_doubt_SU'], -0.0)
        with self.assertRaises(ValueError):
            a.parse_project_report(REPORT.replace('222.154 | 29777', 'nan | 29777'))

    def test_budget_gate_respects_ceiling_and_live_balance_minus_indoubt(self):
        parsed = a.parse_project_report(REPORT)
        result = a.financial_admission(ledger(), parsed)
        self.assertEqual(result['request_maximum_SU'], 768)
        self.assertEqual(result['outstanding_reserved_max_SU'], 2603.2)
        self.assertEqual(result['live_required_for_existing_plus_request_SU'], 3371.2)
        with self.assertRaisesRegex(ValueError, 'in-doubt'):
            a.financial_admission(ledger(), {**parsed, 'balance_SU': 3372, 'in_doubt_SU': 1})
        tight = ledger()
        tight['baseline_wave_planning_ceiling_SU'] = 5000
        with self.assertRaisesRegex(ValueError, 'ceiling'):
            a.financial_admission(tight, parsed)

    def test_ledger_unknown_maximum_is_a_hard_stop(self):
        bad = ledger()
        bad['jobs'].append({'id': 'unknown'})
        with self.assertRaisesRegex(ValueError, 'unknown maximum'):
            a.financial_admission(bad, a.parse_project_report(REPORT))

    def test_qstat_redacts_environment_and_counts_held_jobs(self):
        parsed = a.parse_qstat_json(fake_qstat({'1.pbs101': job('1.pbs101', 'H'),
                                                '2.pbs101': job('2.pbs101', 'Q', 'someone@cpu')}))
        self.assertEqual(parsed, [{'id': '1.pbs101', 'state': 'H'}])
        self.assertNotIn('Variable_List', repr(parsed))
        with self.assertRaisesRegex(ValueError, 'CPU PBS queue'):
            a.enforce_queue_caps(parsed, [])
        with self.assertRaisesRegex(ValueError, 'combined'):
            a.enforce_queue_caps([], [{'id': 'a.pbs101', 'state': 'Q'},
                                     {'id': 'b.pbs101', 'state': 'H'},
                                     {'id': 'c.pbs101', 'state': 'R'}])
        with self.assertRaisesRegex(ValueError, 'missing Job_Owner'):
            a.parse_qstat_json(fake_qstat({'3.pbs101': {'job_state': 'Q'}}))

    def test_defaults_and_unique_pbs_are_the_sibling_native_wave(self):
        self.assertEqual(a.EXPERIMENT, a.CAMPAIGN / 'native-wave')
        self.assertEqual(a.RESEARCH, a.CAMPAIGN.parent)
        actual = a.payload_hashes(a.EXPERIMENT)
        self.assertIn('payload/native-wave.pbs', actual)
        self.assertEqual(a.pbs_script(actual, a.EXPERIMENT), 'payload/native-wave.pbs')

    def test_manifest_and_root_review_must_match_exact_payload(self):
        with tempfile.TemporaryDirectory() as tmp:
            exp = Path(tmp)
            (exp / 'payload').mkdir()
            (exp / 'payload' / 'native-triple.pbs').write_text('# frozen')
            hashes = a.payload_hashes(exp)
            (exp / 'payload-sha256.json').write_text(json.dumps({'files': hashes}))
            (exp / 'ROOT_REVIEW.json').write_text(json.dumps({'passed': True, 'payload_sha256': hashes}))
            self.assertEqual(a.reviewed_hashes(exp), hashes)
            (exp / 'payload' / 'native-triple.pbs').write_text('# altered')
            with self.assertRaisesRegex(ValueError, 'differs'):
                a.reviewed_hashes(exp)

    def _submit_fixture(self, tmp: Path):
        exp = tmp / 'campaign' / 'native-wave'
        (exp / 'payload').mkdir(parents=True)
        (exp / 'payload' / 'native-wave.pbs').write_text('''#!/bin/bash
#PBS -P 59000042
#PBS -l select=4:ncpus=128:mpiprocs=128:mem=440gb:ngpus=0
#PBS -l place=scatter:excl
#PBS -l walltime=01:30:00
''')
        hashes = a.payload_hashes(exp)
        pbs_name = a.pbs_script(hashes, exp)
        (exp / 'payload-sha256.json').write_text(json.dumps({'files': hashes}))
        (exp / 'ROOT_REVIEW.json').write_text(json.dumps({'passed': True, 'payload_sha256': hashes}))
        root = a.REMOTE_PREFIX + '20261027T110000Z'
        (exp / 'deployment.json').write_text(json.dumps({'root': root, 'files': hashes, 'pbs_script': pbs_name,
                                                         'state': 'DEPLOYED_NOT_SUBMITTED'}))
        ledger_path = tmp / 'cpu-budget.json'
        ledger_path.write_text(json.dumps(ledger()))
        cpu_lock = tmp / 'cpu.lock'
        ai_lock = tmp / 'ai.lock'
        return exp, hashes, root, ledger_path, cpu_lock, ai_lock

    def test_submit_writes_intent_and_reservation_before_one_qsub(self):
        with tempfile.TemporaryDirectory() as tmpname:
            tmp = Path(tmpname)
            exp, hashes, root, budget, cpu_lock, ai_lock = self._submit_fixture(tmp)
            cpu_q = lambda cmd: completed(fake_qstat({})) if 'qstat' in cmd else completed(REPORT)
            ai_q = lambda cmd: completed(fake_qstat({}))
            seen = []
            def qsub(command):
                self.assertIn(root, command)
                self.assertIn('payload/native-wave.pbs', command)
                intent = json.loads((exp / 'submission-intent.json').read_text())
                saved = json.loads(budget.read_text())
                self.assertEqual(intent['state'], 'RESERVED_DO_NOT_RETRY_BLINDLY')
                self.assertAlmostEqual(saved['outstanding_reserved_max_SU'], 2603.2 + 768)
                seen.append(command)
                return completed('12345.pbs101\n')
            with patch.multiple(a, EXPERIMENT=exp, ROOT_REVIEW=exp / 'ROOT_REVIEW.json',
                                MANIFEST=exp / 'payload-sha256.json', DEPLOYMENT=exp / 'deployment.json',
                                PRECHECK=exp / 'pre-submit-checks.json', INTENT=exp / 'submission-intent.json',
                                RECEIPT=exp / 'submission.json', UNCERTAIN=exp / 'submission-uncertain.json'), \
                 patch.object(a, '_remote_hash_verify', return_value=json.dumps({'files': hashes, 'root': root}, sort_keys=True)):
                job_id = a.submit(cpu_query=cpu_q, ai_query=ai_q, ledger_path=budget,
                                  cpu_lock_path=cpu_lock, ai_lock_path=ai_lock, qsub=qsub)
                self.assertEqual(job_id, '12345.pbs101')
                self.assertEqual(len(seen), 1)
                self.assertEqual(json.loads((exp / 'submission-intent.json').read_text())['state'], 'SUBMITTED')
                self.assertEqual(json.loads((exp / 'submission.json').read_text())['job_id'], job_id)

    def test_ambiguous_qsub_preserves_reservation_and_blocks_replay(self):
        with tempfile.TemporaryDirectory() as tmpname:
            tmp = Path(tmpname)
            exp, hashes, root, budget, cpu_lock, ai_lock = self._submit_fixture(tmp)
            cpu_q = lambda cmd: completed(fake_qstat({})) if 'qstat' in cmd else completed(REPORT)
            ai_q = lambda cmd: completed(fake_qstat({}))
            def ambiguous(_): return completed('submitted?')
            globals_patch = dict(EXPERIMENT=exp, ROOT_REVIEW=exp / 'ROOT_REVIEW.json',
                                 MANIFEST=exp / 'payload-sha256.json', DEPLOYMENT=exp / 'deployment.json',
                                 PRECHECK=exp / 'pre-submit-checks.json', INTENT=exp / 'submission-intent.json',
                                 RECEIPT=exp / 'submission.json', UNCERTAIN=exp / 'submission-uncertain.json')
            with patch.multiple(a, **globals_patch), \
                 patch.object(a, '_remote_hash_verify', return_value=json.dumps({'files': hashes, 'root': root}, sort_keys=True)):
                with self.assertRaisesRegex(RuntimeError, 'ambiguous'):
                    a.submit(cpu_query=cpu_q, ai_query=ai_q, ledger_path=budget,
                             cpu_lock_path=cpu_lock, ai_lock_path=ai_lock, qsub=ambiguous)
                self.assertTrue((exp / 'submission-uncertain.json').exists())
                self.assertAlmostEqual(json.loads(budget.read_text())['outstanding_reserved_max_SU'], 2603.2 + 768)
                with self.assertRaisesRegex(FileExistsError, 'never retry'):
                    a.submit(cpu_query=cpu_q, ai_query=ai_q, ledger_path=budget,
                             cpu_lock_path=cpu_lock, ai_lock_path=ai_lock, qsub=ambiguous)


if __name__ == '__main__':
    unittest.main(verbosity=2)
