"""Native ABBA placement experiment; four 40-step Scotch arms on Iris."""
from pathlib import Path
import datetime
import hashlib
import json
import os
import re
import socket
import statistics
import subprocess
import time

import helpers as h
from native_checks import field_snapshot
from native_output import review_native_output

KIT = Path(__file__).resolve().parent
SOURCE = Path('/global/exafs/users/rdmaworkshop30/apac2026/tripleu-iris-scotch56-20261025T063431Z/artifacts/ready-N56-scotch')
LAUNCH = ['mpirun', '-np', '56', '--report-bindings', '--display-map']
ARMS = ['A1-default', 'B1-socket', 'B2-socket', 'A2-default']

def solver_launch(label):
    flags = ['--map-by', 'socket', '--bind-to', 'core'] if label.startswith('B') else []
    return LAUNCH + flags + ['--', 'simpleFoam', '-parallel']


def main():
    assert os.environ['SLURM_NTASKS'] == '56'
    assert os.environ['SLURM_JOB_NUM_NODES'] == '1'
    h.DEADLINE = time.monotonic() + 8850
    h.RUN = KIT / 'runs' / os.environ['SLURM_JOB_ID']
    h.RUN.mkdir(parents=True, exist_ok=False)
    run = h.RUN
    h.save(run / 'intent.json', {'steps_each': 40, 'intervals_each': 39,
           'arm_order': ARMS, 'ranks': 56, 'nodes': 1,
           'commands_by_arm': {label: solver_launch(label) for label in ARMS}, 'scored_result': False,
           'request_maximum_cpu_hours': 140, 'internal_deadline_seconds': 8850,
           'scope': 'Only MPI mapping/binding differs; common uncollated I/O and binding reports. ABBA practice-cluster trial, no Gadi/NSCC result.'})
    h.bounded('payload-before', ['sha256sum', '-c', 'payload-sha256.txt'], KIT, 30)
    h.bounded('accepted-source-before', ['python3', KIT / 'seal_tree.py', 'compare', SOURCE,
               KIT / 'accepted-source-manifest.json', run / 'source-before.json'], KIT, 120)
    h.bounded('official-inputs-before', ['python3', KIT / 'verify-inputs.py', '--source', SOURCE,
               '--method', 'scotch', '--pins', KIT / 'source-pins.json', '--case', KIT / 'payload-case',
               '--observations', KIT / 'source-observations.json'], KIT, 60)
    source_fields = field_snapshot(SOURCE)
    h.save(run / 'source-fields.json', source_fields)
    before = h.runtime_snapshot('runtime-before')
    results = []
    for index, label in enumerate(ARMS):
        assert h.remaining() >= ((len(ARMS) - index) * 2100 + 120), 'Insufficient full-arm planning window'
        dest = run / 'arms' / label
        dest.parent.mkdir(exist_ok=True)
        assert not dest.exists()
        h.bounded(label + '-copy', ['python3', '-c',
                   'import shutil,sys;shutil.copytree(sys.argv[1],sys.argv[2],symlinks=True)', SOURCE, dest], KIT, 180)
        h.bounded(label + '-copy-check', ['python3', KIT / 'seal_tree.py', 'verify-copy', SOURCE, dest,
                   KIT / 'accepted-source-manifest.json', run / (label + '-copy.json')], KIT, 120)
        assert field_snapshot(dest) == source_fields
        ctrl = dest / 'system/controlDict'
        original = ctrl.read_text()
        changed, count = re.subn(r'(?m)^endTime[ \t]+[^;\n]+;[^\n]*$', 'endTime 40;', original)
        assert count == 1
        ctrl.write_text(changed)
        assert (dest / 'system/fvSolution').read_bytes() == (dest / 'system/fvSolution.fixedIter').read_bytes()
        h.save(dest / 'control-change.json', {'only_control_edit': 'endTime=40',
               'source_control_sha256': hashlib.sha256(original.encode()).hexdigest(),
               'run_control_sha256': hashlib.sha256(ctrl.read_bytes()).hexdigest()})
        cap = min(1800, h.remaining() - ((len(ARMS) - index - 1) * 2100 + 120))
        assert cap >= 1800, 'No truncated full-arm solver window'
        command = solver_launch(label)
        h.save(dest / 'command.json', {'command': command, 'cap_seconds': cap})
        h.node_snapshot('solver-before', dest)
        start = time.monotonic()
        h.phase(label, 'solver-start', {'command': command, 'cap_seconds': cap})
        with (dest / 'simpleFoam.log').open('w') as out, (dest / 'solver.stderr').open('w') as err:
            p = subprocess.run(['/usr/bin/time', '-v', '-o', str(dest / 'resource-time.log'),
                    'timeout', '--signal=TERM', '--kill-after=15s', str(cap) + 's', *command],
                    cwd=dest, stdout=out, stderr=err, timeout=cap + 25)
        elapsed = time.monotonic() - start
        h.save(dest / 'return-code.json', {'returncode': p.returncode, 'elapsed_seconds': elapsed})
        h.phase(label, 'solver-exit', {'returncode': p.returncode, 'elapsed_seconds': elapsed})
        assert p.returncode == 0
        h.node_snapshot('solver-after', dest)
        assert field_snapshot(dest) == source_fields, 'Initialized fields changed'
        h.save(dest / 'postsolve-fields.json', field_snapshot(dest))
        log, timings, cd, counts = review_native_output(dest)
        assert not re.search(r'FOAM FATAL|MPI_ABORT|died from signal|core dumped', (dest / 'solver.stderr').read_text(), re.I)
        assert re.search(r'^I/O\s*:\s*uncollated', log, re.M), 'Every arm must use the same uncollated handler'
        row = {'arm': label, 'steps': 40, 'intervals': 39, 'mean_s_step': statistics.mean(timings),
               'median_s_step': statistics.median(timings), 'maximum_s_step': max(timings),
               'timings_seconds': timings, 'Cd_by_step': cd, 'fixed_iterations': counts,
               'solver_elapsed_seconds': elapsed}
        results.append(row)
        h.save(run / 'partial-results.json', {'arms': results, 'scored_result': False})
        h.phase(label, 'reviewed', {'mean_s_step': row['mean_s_step']})
    after = h.runtime_snapshot('runtime-after')
    assert h.runtime_identity_equal(before, after)
    h.bounded('source-after', ['python3', KIT / 'seal_tree.py', 'compare', SOURCE,
               KIT / 'accepted-source-manifest.json', run / 'source-after.json'], KIT, 120)
    h.bounded('payload-after', ['sha256sum', '-c', 'payload-sha256.txt'], KIT, 30)
    h.save(run / 'comparison.json', {'passed': True, 'scored_result': False, 'arms': results,
           'socket_vs_default_percent': 100 * ((results[1]['mean_s_step'] + results[2]['mean_s_step']) / (results[0]['mean_s_step'] + results[3]['mean_s_step']) - 1),
           'first_adjacent_B1_vs_A1_percent': 100 * (results[1]['mean_s_step'] / results[0]['mean_s_step'] - 1),
           'hostname': socket.getfqdn(), 'runtime_identity_stable': True,
           'limits': ['One ABBA allocation balances linear drift but not nonlinear drift; independent confirmation remains required.',
                      'Not a Gadi or NSCC result. No hardware bandwidth or solver helper-affinity data.',
                      'Launcher binding reports are not actual solver helper-thread affinity or NUMA page residency.']})
    print('IRIS_PLACEMENT40_ABBA_PASS')


if __name__ == '__main__':
    main()
