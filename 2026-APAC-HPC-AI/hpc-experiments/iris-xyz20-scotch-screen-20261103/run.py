"""Matched standard Scotch versus hierarchical xyz screen on Iris."""
from pathlib import Path
import datetime
import hashlib
import json
import os
import re
import socket
import shutil
import statistics
import subprocess
import time

import helpers as h
from native_checks import field_snapshot
from native_output import review_native_output
from sampler import (preflight as sampler_preflight, start_sampler, stop_sampler,
                     wait_for_first_sample, run_with_sampler, validate_sample_file)

KIT = Path(__file__).resolve().parent
SOURCES = {
    'scotch': Path('/global/exafs/users/rdmaworkshop30/apac2026/tripleu-iris-scotch56-20261025T063431Z/artifacts/ready-N56-scotch'),
    'xyz': Path('/global/exafs/users/rdmaworkshop30/apac2026/tripleu-iris-order-init-20261026T133526Z/initialized/order-xyz'),
}
MANIFESTS = {'scotch': KIT / 'accepted-source-manifest.json', 'xyz': KIT / 'accepted-xyz-source-manifest.json'}
LAUNCH = ['mpirun', '-np', '56', '--report-bindings', '--display-map']
ARMS = ['S1-scotch', 'X1-hierarchical-xyz', 'X2-hierarchical-xyz', 'S2-scotch']

def solver_launch(label):
    return LAUNCH + ['--', 'simpleFoam', '-parallel']


def main():
    assert os.environ['SLURM_NTASKS'] == '56'
    assert os.environ['SLURM_JOB_NUM_NODES'] == '1'
    h.DEADLINE = time.monotonic() + 3510
    h.RUN = KIT / 'runs' / os.environ['SLURM_JOB_ID']
    h.RUN.mkdir(parents=True, exist_ok=False)
    run = h.RUN
    h.save(run / 'intent.json', {'steps_each': 20, 'intervals_each': 19,
           'arm_order': ARMS, 'ranks': 56, 'nodes': 1,
           'commands_by_arm': {label: solver_launch(label) for label in ARMS}, 'scored_result': False,
           'request_maximum_cpu_hours': 56, 'internal_deadline_seconds': 3510,
           'scope': 'Same original mesh/physics and runtime; standard Scotch versus hierarchical(7 4 2),orderxyz. Method-specific accepted initialization, not identical partitioned fields. Basic runtime comparison on Iris, not a scored or cross-platform result.'})
    free = shutil.disk_usage(KIT).free
    h.save(run / 'space-preflight.json', {'filesystem_free_bytes': free, 'required_free_bytes': 64 * 1024**3, 'scope': 'Filesystem space only; not user quota or reservation.'})
    assert free >= 64 * 1024**3, 'Less than 64 GiB free for four isolated cases'
    h.bounded('payload-before', ['sha256sum', '-c', 'payload-sha256.txt'], KIT, 30)
    source_fields = {}
    for key, src in SOURCES.items():
        assert (src / 'READY').is_file()
        h.bounded(key + '-accepted-source-before', ['python3', KIT / 'seal_tree.py', 'compare', src,
                   MANIFESTS[key], run / (key + '-source-before.json')], KIT, 120)
        if key == 'scotch':
            command = ['python3', KIT / 'verify-inputs.py', '--source', src,
                       '--method', 'scotch', '--pins', KIT / 'source-pins.json', '--case', KIT / 'payload-case',
                       '--observations', KIT / 'source-observations.json']
        else:
            command = ['python3', '-c', 'import sys,json;from pathlib import Path;from case_checks import source_check;print(json.dumps(source_check(Path(sys.argv[1]), "xyz")))', src]
        h.bounded(key + '-official-inputs-before', command, KIT, 60)
        source_fields[key] = field_snapshot(src)
        h.save(run / (key + '-source-fields.json'), source_fields[key])
    before = h.runtime_snapshot('runtime-before')
    telemetry_preflight = sampler_preflight(reads=5, max_read_ms=50.0)
    h.save(run / 'sampler-preflight.json', telemetry_preflight)
    results = []
    for index, label in enumerate(ARMS):
        assert h.remaining() >= ((len(ARMS) - index) * 810 + 120), 'Insufficient full-arm planning window'
        key = 'xyz' if label.startswith('X') else 'scotch'
        src = SOURCES[key]
        frozen = MANIFESTS[key]
        h.save(run / (label + '-source-selection.json'), {'method_key': key, 'source': str(src), 'manifest_sha256': hashlib.sha256(frozen.read_bytes()).hexdigest()})
        dest = run / 'arms' / label
        dest.parent.mkdir(exist_ok=True)
        assert not dest.exists()
        h.bounded(label + '-copy', ['python3', '-c',
                   'import shutil,sys;shutil.copytree(sys.argv[1],sys.argv[2],symlinks=True)', src, dest], KIT, 180)
        h.bounded(label + '-copy-check', ['python3', KIT / 'seal_tree.py', 'verify-copy', src, dest,
                   frozen, run / (label + '-copy.json')], KIT, 120)
        assert field_snapshot(dest) == source_fields[key]
        ctrl = dest / 'system/controlDict'
        original = ctrl.read_text()
        changed, count = re.subn(r'(?m)^endTime[ \t]+[^;\n]+;[^\n]*$', 'endTime 20;', original)
        assert count == 1
        ctrl.write_text(changed)
        assert (dest / 'system/fvSolution').read_bytes() == (dest / 'system/fvSolution.fixedIter').read_bytes()
        h.save(dest / 'control-change.json', {'only_control_edit': 'endTime=20',
               'source_control_sha256': hashlib.sha256(original.encode()).hexdigest(),
               'run_control_sha256': hashlib.sha256(ctrl.read_bytes()).hexdigest()})
        cap = min(720, h.remaining() - ((len(ARMS) - index - 1) * 810 + 120))
        assert cap >= 720, 'No full directional-screen solver window'
        command = solver_launch(label)
        h.save(dest / 'command.json', {'command': command, 'cap_seconds': cap})
        h.node_snapshot('solver-before', dest)
        telemetry_path = dest / 'telemetry-samples.jsonl'
        telemetry_stderr = dest / 'telemetry-stderr.log'
        sampler_process = None
        sampler_stop_state = None
        telemetry_status = {'state': 'disabled_by_preflight', 'preflight_reason': telemetry_preflight.get('reason')}
        if telemetry_preflight.get('enabled'):
            try:
                sampler_process = start_sampler(telemetry_path, interval=5.0, stderr_path=telemetry_stderr)
                ready = wait_for_first_sample(sampler_process, telemetry_path, timeout_seconds=1.0)
                if ready.get('available'):
                    telemetry_status = {'state': 'sampling', 'interval_seconds': 5.0, 'first_sample_seen': True}
                else:
                    telemetry_status = {'state': 'unavailable', 'reason': ready.get('reason')}
                    sampler_stop_state = stop_sampler(sampler_process)
                    sampler_process = None
                    telemetry_status['stop'] = sampler_stop_state
            except Exception as exc:
                telemetry_status = {'state': 'unavailable', 'reason': type(exc).__name__}
                if sampler_process is not None:
                    sampler_stop_state = stop_sampler(sampler_process)
                    telemetry_status['stop'] = sampler_stop_state
                    sampler_process = None
        start = time.monotonic()
        h.phase(label, 'solver-start', {'command': command, 'cap_seconds': cap,
                 'node_sampler_state': telemetry_status['state'], 'node_sampler_interval_seconds': 5.0})
        try:
            with (dest / 'simpleFoam.log').open('w') as out, (dest / 'solver.stderr').open('w') as err:
                p, sampler_stop_state = run_with_sampler(sampler_process,
                        ['/usr/bin/time', '-v', '-o', str(dest / 'resource-time.log'),
                        'timeout', '--signal=TERM', '--kill-after=15s', str(cap) + 's', *command],
                        cwd=dest, stdout=out, stderr=err, timeout=cap + 25)
                sampler_process = None
        finally:
            stop_state = (stop_sampler(sampler_process) if sampler_process is not None else
                          sampler_stop_state or telemetry_status.get('stop', {'process_was_started': False}))
            sample_check = validate_sample_file(telemetry_path)
            telemetry_status.update({'stop': stop_state,
                                     'sample_count': sample_check['sample_count'],
                                     'sample_bytes': sample_check['bytes'],
                                     'sample_file_present': sample_check['present'],
                                     'scope': 'Whole-node aggregate procfs samples; collection_ms is not a measured interference estimate.'})
            h.save(dest / 'telemetry-status.json', telemetry_status)
        elapsed = time.monotonic() - start
        h.save(dest / 'return-code.json', {'returncode': p.returncode, 'elapsed_seconds': elapsed})
        h.phase(label, 'solver-exit', {'returncode': p.returncode, 'elapsed_seconds': elapsed})
        assert p.returncode == 0
        h.node_snapshot('solver-after', dest)
        assert field_snapshot(dest) == source_fields[key], 'Initialized fields changed'
        h.save(dest / 'postsolve-fields.json', field_snapshot(dest))
        log, timings, cd, counts = review_native_output(dest)
        assert not re.search(r'FOAM FATAL|MPI_ABORT|died from signal|core dumped', (dest / 'solver.stderr').read_text(), re.I)
        handler = 'uncollated'
        assert re.search(r'^I/O\s*:\s*' + handler + r'\b', log, re.M), ('Wrong actual file handler', label, handler)
        row = {'arm': label, 'steps': 20, 'intervals': 19, 'mean_s_step': statistics.mean(timings),
               'median_s_step': statistics.median(timings), 'maximum_s_step': max(timings),
               'timings_seconds': timings, 'Cd_by_step': cd, 'fixed_iterations': counts,
               'solver_elapsed_seconds': elapsed}
        results.append(row)
        h.save(run / 'partial-results.json', {'arms': results, 'scored_result': False})
        h.phase(label, 'reviewed', {'mean_s_step': row['mean_s_step']})
    after = h.runtime_snapshot('runtime-after')
    assert h.runtime_identity_equal(before, after)
    for key, src in SOURCES.items():
        h.bounded(key + '-source-after', ['python3', KIT / 'seal_tree.py', 'compare', src,
                   MANIFESTS[key], run / (key + '-source-after.json')], KIT, 120)
    h.bounded('payload-after', ['sha256sum', '-c', 'payload-sha256.txt'], KIT, 30)
    h.save(run / 'comparison.json', {'passed': True, 'scored_result': False, 'arms': results,
           'hierarchical_xyz_vs_scotch_percent': 100 * ((results[1]['mean_s_step'] + results[2]['mean_s_step']) / (results[0]['mean_s_step'] + results[3]['mean_s_step']) - 1),
           'node_sampler_preflight': telemetry_preflight,
           'node_sampler_arm_statuses': {label: json.loads((run / 'arms' / label / 'telemetry-status.json').read_text()) for label in ARMS},
           'first_adjacent_X1_vs_S1_percent': 100 * (results[1]['mean_s_step'] / results[0]['mean_s_step'] - 1),
           'hostname': socket.getfqdn(), 'runtime_identity_stable': True,
           'limits': ['One ABBA allocation balances linear drift but not nonlinear drift; independent confirmation remains required.',
                      'Not a Gadi or NSCC result. No hardware bandwidth or solver helper-affinity data.',
                      'Launcher binding reports are not actual solver helper-thread affinity or NUMA page residency.',
                      'Five-second aggregate procfs sampling is diagnostic only; sample collection duration is not a causal or true solver-interference estimate.']})
    print('IRIS_XYZ20_DIRECTIONAL_ABBA_SCREEN_PASS')


if __name__ == '__main__':
    main()
