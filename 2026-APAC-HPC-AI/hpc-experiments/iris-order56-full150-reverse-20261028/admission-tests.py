#!/usr/bin/env python3
"""Offline checks for Iris admission finance, queue and idempotency guards."""
import json
from pathlib import Path
import tempfile
import unittest

import deploy_submit as d


def budget():
    return {'cluster': 'Iris', 'account': 'rdmaworkshop',
            'branch_planning_ceiling_allocated_CPU_hours': 505,
            'consumed_planning_allowance_allocated_CPU_hours': 337,
            'reserved_maximum_allocated_CPU_hours': 0,
            'jobs': [{'state': 'COMPLETED_0_0_REVIEW_PASS',
                      'maximum_allocated_CPU_hours': 24.266667}]}


VALID_SBATCH = '''#!/bin/bash
#SBATCH -J tu-iris-orderfull150
#SBATCH -p iris
#SBATCH -A rdmaworkshop
#SBATCH --qos=low
#SBATCH --exclusive
#SBATCH --mem=0
#SBATCH -N 1
#SBATCH -n 56
#SBATCH -t 03:00:00
#SBATCH --gres=gpu:0
#SBATCH -o runs/%j.out
'''


class IrisAdmissionTests(unittest.TestCase):
    def test_request_and_existing_authorized_budget_fit_exactly_within_ceiling(self):
        self.assertEqual(d.max_cpu_hours(), 168)
        checked = d.financial_check(budget())
        self.assertEqual(checked['committed_after_allocated_CPU_hours'], 505)
        self.assertEqual(checked['authorized_ceiling_allocated_CPU_hours'], 505)

    def test_over_ceiling_wrong_account_and_nonfinite_are_blocked(self):
        over = budget()
        over['reserved_maximum_allocated_CPU_hours'] = 6
        with self.assertRaisesRegex(ValueError, 'ceiling'):
            d.financial_check(over)
        wrong = budget()
        wrong['account'] = 'other'
        with self.assertRaisesRegex(ValueError, 'account'):
            d.financial_check(wrong)
        invalid = budget()
        invalid['consumed_planning_allowance_allocated_CPU_hours'] = float('nan')
        with self.assertRaisesRegex(ValueError, 'invalid'):
            d.financial_check(invalid)

    def test_unresolved_ledger_intent_blocks_second_job(self):
        data = budget()
        data['jobs'].append({'state': 'RESERVED_SUBMISSION_UNCERTAIN',
                             'maximum_allocated_CPU_hours': 168})
        with self.assertRaisesRegex(ValueError, 'unresolved'):
            d.require_no_active_local_jobs(data)

    def test_fresh_queue_guard_matches_only_owned_job_prefix(self):
        d.require_no_own_jobs('2295000|other-user-job|RUNNING\n')
        with self.assertRaisesRegex(ValueError, 'own-job cap'):
            d.require_no_own_jobs('2295000|tu-iris-other|PENDING\n')

    def test_existing_local_intent_or_receipt_blocks_retry(self):
        with tempfile.TemporaryDirectory() as tmp:
            experiment = Path(tmp)
            d.require_no_local_attempt(experiment)
            for name in ('submission-intent.json', 'submission-receipt.json',
                         'submission-uncertain.json'):
                (experiment / name).write_text('{}')
                with self.assertRaisesRegex(FileExistsError, 'never retry'):
                    d.require_no_local_attempt(experiment)
                (experiment / name).unlink()

    def test_sbatch_request_has_correct_lowqos_fullpair_bounds(self):
        with tempfile.TemporaryDirectory() as tmp:
            experiment = Path(tmp)
            (experiment / 'job.sbatch').write_text(VALID_SBATCH)
            files = {'job.sbatch': 'frozen-hash'}
            self.assertEqual(d.validate_sbatch(files, experiment), 'job.sbatch')
            (experiment / 'job.sbatch').write_text(VALID_SBATCH.replace('03:00:00', '02:00:00'))
            with self.assertRaisesRegex(ValueError, '3 hours'):
                d.validate_sbatch(files, experiment)


if __name__ == '__main__':
    unittest.main(verbosity=2)
