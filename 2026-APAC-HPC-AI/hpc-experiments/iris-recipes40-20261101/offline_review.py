"""Exercise recipe and dependent-admission gates without contacting Slurm."""
from pathlib import Path
import ast
import copy
import importlib.util
import json
import subprocess
import tempfile

import admit

E = Path(__file__).resolve().parent


def rejects(call):
    try:
        call()
    except (AssertionError, ValueError, KeyError):
        return
    raise AssertionError('Invalid fixture was accepted')


def budget():
    return {'cluster': 'Iris', 'account': 'rdmaworkshop',
            'branch_planning_ceiling_allocated_CPU_hours': 770,
            'consumed_planning_allowance_allocated_CPU_hours': 560,
            'reserved_maximum_allocated_CPU_hours': 70,
            'jobs': [{'job_id': '2294635', 'maximum_allocated_CPU_hours': 70,
                      'reservation_retired': False}]}


def submission_fixture(uncertain=False):
    """Fake every remote call and redirect every writable path to a temporary tree."""
    saved = {name: getattr(admit, name) for name in ['E', 'C', 'reviewed', 'run_json']}
    try:
        with tempfile.TemporaryDirectory(prefix='iris-recipe-admission-fixture-') as directory:
            top = Path(directory)
            admit.E = top / 'experiment'
            admit.C = top / 'ledger'
            admit.E.mkdir()
            admit.C.mkdir()
            files = {'run.py': 'fixture-only-not-a-real-hash'}
            remote = '/global/exafs/users/rdmaworkshop30/apac2026/tripleu-iris-recipes40-20261101T000000Z'
            (admit.E / 'deployment.json').write_text(json.dumps({'root': remote, 'payload_sha256': files}))
            (admit.C / 'budget.json').write_text(json.dumps(budget()))
            predecessor = top / 'iris-collated40-reverse-20261101'
            predecessor.mkdir()
            (predecessor / 'submission-receipt.json').write_text(json.dumps({
                'job_id': '2294635', 'returncode': 0,
                'root': '/global/exafs/users/rdmaworkshop30/apac2026/tripleu-iris-io40r-fixture'}))
            admit.reviewed = lambda: files
            calls = []

            def fake_remote(body, timeout):
                calls.append(body)
                if len(calls) == 1:
                    return {'queue': '2294635|tu-iris-io40r|RUNNING\n', 'utc': 'fixture'}
                # The only submission call must occur after durable local intent/reservation.
                assert (admit.E / 'submission-intent.json').exists()
                live = json.loads((admit.C / 'budget.json').read_text())
                assert live['reserved_maximum_allocated_CPU_hours'] == 210
                assert live['jobs'][-1]['dependency'] == {'type': 'afterany', 'job_id': '2294635'}
                assert "'--dependency=afterany:'+PREDECESSOR_ID" in body
                assert body.count("['sbatch'") == 1
                if uncertain:
                    return {'returncode': 0, 'stdout': '', 'root': remote}
                return {'returncode': 0, 'job_id': '999900', 'stdout': '999900\n', 'root': remote}

            admit.run_json = fake_remote
            if uncertain:
                rejects(lambda: admit.submit(files))
                assert (admit.E / 'submission-uncertain.json').exists()
            else:
                assert admit.submit(files)['job_id'] == '999900'
            before_retry = len(calls)
            rejects(lambda: admit.submit(files))
            assert len(calls) == before_retry == 2
            assert json.loads((admit.C / 'budget.json').read_text())['reserved_maximum_allocated_CPU_hours'] == 210
    finally:
        for name, value in saved.items():
            setattr(admit, name, value)


def main():
    for path in E.glob('*.py'):
        compile(path.read_text(), str(path), 'exec')
    subprocess.run(['bash', '-n', str(E / 'job.sbatch')], check=True)
    spec = importlib.util.spec_from_file_location('recipe_runner_fixture', E / 'run.py')
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    assert runner.ARMS == ['A1-organizer', 'B1-teammate', 'B2-teammate', 'A2-organizer']
    base = ['mpirun', '-np', '56', '--report-bindings', '--display-map']
    assert runner.solver_launch('A1-organizer') == base + ['--', 'simpleFoam', '-parallel']
    assert runner.solver_launch('B1-teammate') == base + ['--map-by', 'socket', '--bind-to', 'core',
                                                       '--', 'simpleFoam', '-parallel', '-fileHandler', 'collated']
    tree = ast.parse((E / 'run.py').read_text())
    expr = next(v for node in ast.walk(tree) if isinstance(node, ast.Dict)
                for k, v in zip(node.keys, node.values)
                if isinstance(k, ast.Constant) and k.value == 'teammate_vs_organizer_percent')
    result = eval(compile(ast.Expression(expr), '<ratio-fixture>', 'eval'),
                  {'results': [{'mean_s_step': value} for value in [14, 10, 12, 16]]})
    assert abs(result - 100 * (22 / 30 - 1)) < 1e-12
    assert admit.financial(budget())['new_maximum_CPU_hours'] == 140
    b = budget(); b['branch_planning_ceiling_allocated_CPU_hours'] = 630
    rejects(lambda: admit.financial(b))
    b = budget(); b['reserved_maximum_allocated_CPU_hours'] = 69
    rejects(lambda: admit.financial(b))
    b = budget(); b['jobs'][0]['job_id'] = 'unowned'
    rejects(lambda: admit.financial(b))
    assert admit.queue_allowed('')
    assert admit.queue_allowed('2294635|tu-iris-io40r|RUNNING\n')
    rejects(lambda: admit.queue_allowed('2294000|tu-unknown|PENDING\n'))
    rejects(lambda: admit.queue_allowed('2294635|tu-iris-io40r|RUNNING\n2294000|tu-other|PENDING\n'))
    submission_fixture()
    submission_fixture(uncertain=True)
    report = {'passed': True, 'scope': 'Offline only. No real queue, budget or remote root was changed.',
              'checks': ['Python and bash syntax', 'Exact ABBA recipe commands and pooled ratio',
                         '770-hour stage accepts max; old630 rejects', 'Reserved counter must equal outstanding row maxima',
                         'Reject unknown own jobs or extra successors', 'Exact predecessor dependency in sbatch',
                         'Durable intent and210-hour combined reservation before sole mocked submission',
                         'Successful and uncertain mocked submission both block replay; uncertain maximum retained']}
    (E / 'offline-review.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
