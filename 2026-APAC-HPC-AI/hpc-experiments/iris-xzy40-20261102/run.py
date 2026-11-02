"""Native BAAB comparison of the screened xzy cut against default Scotch."""
from pathlib import Path
import hashlib
import json
import math
import os
import re
import socket
import shutil
import statistics
import subprocess
import time

import helpers as h
from case_checks import source_check
from native_checks import field_snapshot
from native_output import review_native_output

KIT = Path(__file__).resolve().parent
SOURCES = {
    'scotch': Path('/global/exafs/users/rdmaworkshop30/apac2026/tripleu-iris-scotch56-20261025T063431Z/artifacts/ready-N56-scotch'),
    'xzy': Path('/global/exafs/users/rdmaworkshop30/apac2026/tripleu-iris-xzy-init-20261102T033918Z/initialized/order-xzy'),
}
MANIFESTS = {'scotch': KIT / 'accepted-source-manifest.json', 'xzy': KIT / 'accepted-xzy-source-manifest.json'}
LAUNCH = ['mpirun', '-np', '56', '--report-bindings', '--display-map']
ARMS = ['B1-our-xzy', 'A1-scotch', 'A2-scotch', 'B2-our-xzy']


def method_key(label):
    mapping = {'B1-our-xzy': 'xzy', 'B2-our-xzy': 'xzy',
               'A1-scotch': 'scotch', 'A2-scotch': 'scotch'}
    if label not in mapping:
        raise ValueError(f'unknown arm label: {label}')
    return mapping[label]


def solver_launch(label):
    method_key(label)
    return LAUNCH + ['--', 'simpleFoam', '-parallel']


def nearest_rank(values, quantile):
    ordered = sorted(values)
    return ordered[math.ceil(quantile * len(ordered)) - 1]


def comparison_metrics(results):
    means = {row['arm']: row['mean_s_step'] for row in results}
    assert set(means) == set(ARMS)
    return {
        'xzy_vs_scotch_percent': 100 * ((means['B1-our-xzy'] + means['B2-our-xzy']) /
                                         (means['A1-scotch'] + means['A2-scotch']) - 1),
        'first_adjacent_B1_xzy_vs_A1_scotch_percent': 100 * (means['B1-our-xzy'] / means['A1-scotch'] - 1),
        'reverse_adjacent_B2_xzy_vs_A2_scotch_percent': 100 * (means['B2-our-xzy'] / means['A2-scotch'] - 1),
        'control_repeat_A2_vs_A1_percent': 100 * (means['A2-scotch'] / means['A1-scotch'] - 1),
        'candidate_repeat_B2_vs_B1_percent': 100 * (means['B2-our-xzy'] / means['B1-our-xzy'] - 1),
    }


def main():
    assert os.environ['SLURM_NTASKS'] == '56'
    assert os.environ['SLURM_JOB_NUM_NODES'] == '1'
    assert all(path.is_file() for path in MANIFESTS.values()), 'Root must install reviewed XZY manifest before deployment'
    h.DEADLINE = time.monotonic() + 8850
    h.RUN = KIT / 'runs' / os.environ['SLURM_JOB_ID']
    h.RUN.mkdir(parents=True, exist_ok=False)
    run = h.RUN
    h.save(run / 'intent.json', {
        'steps_each': 40, 'intervals_each': 39, 'arm_order': ARMS,
        'ranks': 56, 'nodes': 1, 'commands_by_arm': {label: solver_launch(label) for label in ARMS},
        'scored_result': False, 'request_maximum_cpu_hours': 140,
        'internal_deadline_seconds': 8850,
        'scope': 'Default Scotch versus standard hierarchical(7 4 2),order xzy on Iris; BAAB; common default MPI and uncollated I/O; method-specific accepted initialization.',
        'hypothesis': 'XZY has fewer total interface faces and fewer maximum neighbor patches than the screened xyz/zyx cuts, but a larger worst-rank interface count; measure the solver rather than infer a speedup from the proxy.'})
    free = shutil.disk_usage(KIT).free
    h.save(run / 'space-preflight.json', {'filesystem_free_bytes': free, 'required_free_bytes': 64 * 1024**3,
           'scope': 'Filesystem space only; not user quota or reservation.'})
    assert free >= 64 * 1024**3, 'Less than 64 GiB free for four isolated cases'
    h.bounded('payload-before', ['sha256sum', '-c', 'payload-sha256.txt'], KIT, 30)

    source_fields = {}
    for key, source in SOURCES.items():
        assert (source / 'READY').is_file() and not source.is_symlink()
        manifest = MANIFESTS[key]
        h.bounded(key + '-accepted-source-before', ['python3', KIT / 'seal_tree.py', 'compare', source,
                   manifest, run / (key + '-source-before.json')], KIT, 120)
        if key == 'scotch':
            command = ['python3', KIT / 'verify-inputs.py', '--source', source, '--method', 'scotch',
                       '--pins', KIT / 'source-pins.json', '--case', KIT / 'payload-case',
                       '--observations', KIT / 'source-observations.json']
        else:
            command = ['python3', '-c', 'import sys,json;from pathlib import Path;from case_checks import source_check;print(json.dumps(source_check(Path(sys.argv[1]), "xzy")))', source]
        h.bounded(key + '-official-inputs-before', command, KIT, 60)
        source_fields[key] = field_snapshot(source)
        h.save(run / (key + '-source-fields.json'), source_fields[key])

    runtime_before = h.runtime_snapshot('runtime-before')
    rows = []
    for index, label in enumerate(ARMS):
        assert h.remaining() >= ((len(ARMS) - index) * 2100 + 120), 'Insufficient full-arm planning window'
        key = method_key(label)
        source = SOURCES[key]
        manifest = MANIFESTS[key]
        h.save(run / (label + '-source-selection.json'), {
            'method_key': key, 'source': str(source), 'manifest_sha256': hashlib.sha256(manifest.read_bytes()).hexdigest()})
        dest = run / 'arms' / label
        dest.parent.mkdir(exist_ok=True)
        assert not dest.exists()
        h.bounded(label + '-copy', ['python3', '-c',
                   'import shutil,sys;shutil.copytree(sys.argv[1],sys.argv[2],symlinks=True)', source, dest], KIT, 180)
        h.bounded(label + '-copy-check', ['python3', KIT / 'seal_tree.py', 'verify-copy', source, dest,
                   manifest, run / (label + '-copy.json')], KIT, 120)
        assert field_snapshot(dest) == source_fields[key]
        control = dest / 'system/controlDict'
        original = control.read_text()
        changed, count = re.subn(r'(?m)^endTime[ \t]+[^;\n]+;[^\n]*$', 'endTime 40;', original)
        assert count == 1
        control.write_text(changed)
        assert (dest / 'system/fvSolution').read_bytes() == (dest / 'system/fvSolution.fixedIter').read_bytes()
        h.save(dest / 'control-change.json', {'only_control_edit': 'endTime=40',
               'source_control_sha256': hashlib.sha256(original.encode()).hexdigest(),
               'run_control_sha256': hashlib.sha256(control.read_bytes()).hexdigest()})
        cap = min(1800, h.remaining() - ((len(ARMS) - index - 1) * 2100 + 120))
        assert cap >= 1800, 'No truncated full-arm solver window'
        command = solver_launch(label)
        h.save(dest / 'command.json', {'command': command, 'cap_seconds': cap, 'file_handler': 'uncollated'})
        h.node_snapshot('solver-before', dest)
        start = time.monotonic()
        h.phase(label, 'solver-start', {'command': command, 'cap_seconds': cap})
        with (dest / 'simpleFoam.log').open('w') as stdout, (dest / 'solver.stderr').open('w') as stderr:
            proc = subprocess.run(['/usr/bin/time', '-v', '-o', str(dest / 'resource-time.log'),
                    'timeout', '--signal=TERM', '--kill-after=15s', str(cap) + 's', *command],
                    cwd=dest, stdout=stdout, stderr=stderr, timeout=cap + 25)
        elapsed = time.monotonic() - start
        h.save(dest / 'return-code.json', {'returncode': proc.returncode, 'elapsed_seconds': elapsed})
        h.phase(label, 'solver-exit', {'returncode': proc.returncode, 'elapsed_seconds': elapsed})
        assert proc.returncode == 0
        h.node_snapshot('solver-after', dest)
        assert field_snapshot(dest) == source_fields[key], 'Initialized fields changed'
        h.save(dest / 'postsolve-fields.json', field_snapshot(dest))
        log, timings, cd, counts = review_native_output(dest)
        assert not re.search(r'FOAM FATAL|MPI_ABORT|died from signal|core dumped',
                             (dest / 'solver.stderr').read_text(), re.I)
        assert re.search(r'^I/O\s*:\s*uncollated\b', log, re.M), ('Wrong actual file handler', label)
        rows.append({'arm': label, 'method_key': key, 'steps': 40, 'intervals': 39,
            'mean_s_step': statistics.mean(timings), 'median_s_step': statistics.median(timings),
            'p95_s_step_nearest_rank': nearest_rank(timings, 0.95),
            'p99_s_step_nearest_rank': nearest_rank(timings, 0.99), 'max_s_step': max(timings),
            'timings_seconds': timings, 'Cd_by_step': cd, 'fixed_iterations': counts,
            'solver_elapsed_seconds': elapsed})
        h.save(run / 'partial-results.json', {'arms': rows, 'scored_result': False})
        h.phase(label, 'reviewed', {'mean_s_step': rows[-1]['mean_s_step'], 'p95_s_step': rows[-1]['p95_s_step_nearest_rank']})

    runtime_after = h.runtime_snapshot('runtime-after')
    assert h.runtime_identity_equal(runtime_before, runtime_after)
    for key, source in SOURCES.items():
        h.bounded(key + '-source-after', ['python3', KIT / 'seal_tree.py', 'compare', source,
                   MANIFESTS[key], run / (key + '-source-after.json')], KIT, 120)
    h.bounded('payload-after', ['sha256sum', '-c', 'payload-sha256.txt'], KIT, 30)

    by_label = {row['arm']: row for row in rows}
    cd_by_method = {}
    cd_series = {label: {int(row[0]): row[1] for row in by_label[label]['Cd_by_step']} for label in ARMS}
    for key, labels in [('scotch', ['A1-scotch', 'A2-scotch']), ('xzy', ['B1-our-xzy', 'B2-our-xzy'])]:
        repeat_deltas = [abs(cd_series[labels[0]][step] - cd_series[labels[1]][step]) for step in range(1, 41)]
        cd_by_method[key] = {'labels': labels,
            'mean_absolute_repeat_delta_Cd': statistics.mean(repeat_deltas),
            'maximum_absolute_repeat_delta_Cd': max(repeat_deltas),
            'final_Cd_by_arm': {label: cd_series[label][40] for label in labels}}
    stepwise_xzy = [(cd_series['B1-our-xzy'][step] + cd_series['B2-our-xzy'][step]) / 2 for step in range(1, 41)]
    stepwise_scotch = [(cd_series['A1-scotch'][step] + cd_series['A2-scotch'][step]) / 2 for step in range(1, 41)]
    between = [abs(a - b) for a, b in zip(stepwise_xzy, stepwise_scotch)]
    summary = {'passed': True, 'scored_result': False, 'arms': rows,
        **comparison_metrics(rows), 'Cd_repeat_diagnostics_by_method': cd_by_method,
        'method_mean_Cd_trajectory': {'mean_absolute_stepwise_delta': statistics.mean(between),
                                      'maximum_absolute_stepwise_delta': max(between),
                                      'final_mean_Cd_xzy': stepwise_xzy[-1],
                                      'final_mean_Cd_scotch': stepwise_scotch[-1]},
        'hostname': socket.getfqdn(), 'runtime_identity_stable': True,
        'file_handler_by_arm': {label: 'uncollated' for label in ARMS},
        'limits': ['One native BAAB allocation on Iris only; symmetric method placement reduces linear position bias but not nonlinear time drift.',
                   'Structural interface counts are not solver speed predictions. A higher worst-rank surface may offset lower total interfaces.',
                   'Not a Gadi/NSCC result. No hardware bandwidth, actual solver helper affinity or NUMA page residency was collected.']}
    h.save(run / 'comparison.json', summary)
    print('IRIS_XZY40_BAAB_PASS')


if __name__ == '__main__':
    main()
