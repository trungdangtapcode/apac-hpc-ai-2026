"""Reject a broken common setup before the dependent candidate loads weights.

This is a coarse bootstrap guard, not the complete sealed local run review.
"""
import json
from pathlib import Path
import sys


def check(run, reference):
    points = json.loads((run / 'summary.json').read_text())
    point, = [p for p in points if p['phase'] == 'confirm' and p['concurrency'] == 54]
    assert point['sla_pass'] and point['good_request_fraction'] >= .90
    assert point['requests'] > 0 and point['errors'] == point['cancelled_requests'] == 0
    for role, count, cpus in [('prefill-0', 4, 32), ('prefill-1', 4, 32), ('decode-0', 8, 64)]:
        receipt = json.loads((run / f'cpu-envelope/{role}.json').read_text())
        assert receipt['mode'] == 'legacy' and receipt['role'] == role
        assert receipt['cpu_budget'] == receipt['physical_cores_selected'] == cpus
        assert len(set(receipt['selected_cuda_gpu_uuids'])) == count
        assert receipt['applied_cpu_ids'] == receipt['legacy_cpu_ids']
        assert len(receipt['balanced_cpu_ids']) == cpus
    short = json.loads((run / 'output-smoke.json').read_text())
    assert short['total'] == len(short['cases']) == 8
    ref = {case['name']: case for case in reference['cases']}
    assert set(ref) == {case['name'] for case in short['cases']}
    for case in short['cases']:
        assert case['prompt'] == ref[case['name']]['prompt']
        assert case['expected'] == ref[case['name']]['expected']
        assert 'error' not in case
        assert case['response']['choices'][0]['message']['content'] == case['text']
        assert case['passed'] or not ref[case['name']]['passed'], 'New failed short diagnostic'
    long = json.loads((run / 'long-context-check.json').read_text())
    assert long['passed'] == long['total'] == len(long['cases']) == 12 and not long['errors']
    for case in long['cases']:
        assert 'error' not in case and case['response']['choices'][0]['message']['content'] == case['text']
        assert case['text'].strip(' \t\n\r\"\'`.') == case['expected']
    return dict(control_job=run.name, bootstrap_guard_passed=True,
                full_sealed_review_still_required=True)


if __name__ == '__main__':
    run = Path(sys.argv[1])
    assert run.name.endswith('.pbs111') and run.name.split('.')[0].isdigit()
    reference = json.loads(Path(__file__).with_name('reference-output-smoke.json').read_text())
    print('CPU_ENVELOPE_CONTROL_BOOTSTRAP_PASS', json.dumps(check(run, reference)), flush=True)
