"""Directional native solver screen with interleaved versus inherited preparation copies."""
from pathlib import Path
import datetime
import hashlib
import json
import math
import os
import re
import socket
import shutil
import statistics
import subprocess
import sys
import time

import helpers as h
from native_checks import field_snapshot
from native_output import review_native_output
from sampler import (preflight as sampler_preflight, start_sampler, stop_sampler,
                     wait_for_first_sample, run_with_sampler, validate_sample_file)
from qualification_utils import (parse_numactl_show, parse_hardware_nodes,
    policy_signature, process_masks, validate_manifest_paths)

KIT = Path(__file__).resolve().parent
SOURCES = {
    'scotch': Path('/global/exafs/users/rdmaworkshop30/apac2026/tripleu-iris-scotch56-20261025T063431Z/artifacts/ready-N56-scotch'),
}
MANIFESTS = {'scotch': KIT / 'accepted-source-manifest.json'}
SUPPLEMENTARY = KIT / 'supplementary-source-manifest.json'
LAUNCH = ['mpirun', '-np', '56', '--report-bindings', '--display-map']
ARMS = ['A1-inherited-prep', 'B1-interleaved-prep', 'B2-interleaved-prep', 'A2-inherited-prep']
TREATMENTS = {'A1-inherited-prep':'inherited','B1-interleaved-prep':'interleave-all',
              'B2-interleaved-prep':'interleave-all','A2-inherited-prep':'inherited'}
SOLVER_CAP=1500
COPY_CAP=50
POLICY_CAP=10
PREP_CAP=COPY_CAP+POLICY_CAP
FINALIZE_RESERVE=180
INTERNAL_SECONDS=6800

def solver_launch(label):
    return LAUNCH + ['--', 'simpleFoam', '-parallel']


def preparation_launch(label,worker,numactl):
    if TREATMENTS[label]=='inherited':
        return list(worker)
    return [numactl,'--interleave=all',*worker]


def complete_sequence_seconds(arms_left,include_current_prep=True):
    if include_current_prep:
        return arms_left*(SOLVER_CAP+PREP_CAP)+FINALIZE_RESERVE
    return SOLVER_CAP+(arms_left-1)*(SOLVER_CAP+PREP_CAP)+FINALIZE_RESERVE


def require_complete_sequence_window(seconds_left,arms_left,include_current_prep=True):
    required=complete_sequence_seconds(arms_left,include_current_prep)
    if seconds_left < required:
        raise RuntimeError(f'need {required}s for {arms_left} full arms and finalization; have {seconds_left}s')


def main():
    assert os.environ['SLURM_NTASKS'] == '56'
    assert os.environ['SLURM_JOB_NUM_NODES'] == '1'
    h.DEADLINE = time.monotonic() + INTERNAL_SECONDS
    h.RUN = KIT / 'runs' / os.environ['SLURM_JOB_ID']
    h.RUN.mkdir(parents=True, exist_ok=False)
    run = h.RUN
    h.bounded('payload-before', ['sha256sum', '-c', KIT/'payload-sha256.txt'], KIT, 10)
    h.save(run / 'intent.json', {'steps_each': 40, 'intervals_each': 39,
           'arm_order': ARMS, 'ranks': 56, 'nodes': 1,
           'commands_by_arm': {label: solver_launch(label) for label in ARMS}, 'scored_result': False,
           'preparation_treatment_by_arm':TREATMENTS,'request_maximum_cpu_hours':112,
           'internal_deadline_seconds':INTERNAL_SECONDS,'solver_cap_seconds_each':SOLVER_CAP,
           'prep_cap_seconds_each':PREP_CAP,
           'scope': 'Same accepted Scotch source, initialized fields, native launcher, solver, physics, 40-step directional confirmation and sampler. Only copy/hash child policy differs; the launcher parent policy is unchanged; per-rank policy is not measured. Not a scored result.'})
    free = shutil.disk_usage(KIT).free
    h.save(run / 'space-preflight.json', {'filesystem_free_bytes': free, 'required_free_bytes': 64 * 1024**3, 'scope': 'Filesystem space only; not user quota or reservation.'})
    assert free >= 64 * 1024**3, 'Less than 64 GiB free for four isolated cases'
    src=SOURCES['scotch']; frozen=MANIFESTS['scotch']
    masks=process_masks(); assert len(masks['allowed_cpu_ids'])>=56 and set(masks['allowed_memory_node_ids'])>={0,1},masks
    numactl=shutil.which('numactl'); assert numactl
    hw=h.bounded('numa-hardware',[numactl,'--hardware'],KIT,10)
    topology=parse_hardware_nodes(Path(run/'numa-hardware.log').read_text())
    assert hw['returncode']==0 and topology=={'count':2,'node_ids':[0,1]},topology
    inherited_result=h.bounded('inherited-policy',[numactl,'--show'],KIT,10)
    inherited=parse_numactl_show(Path(run/'inherited-policy.log').read_text())
    assert inherited_result['returncode']==0 and inherited['policy']!='unknown',inherited
    inter_result=h.bounded('interleave-policy',['numactl','--interleave=all',sys.executable,'-c',
        'import subprocess,sys;p=subprocess.run(["numactl","--show"],text=True,capture_output=True);print(p.stdout);sys.exit(p.returncode)'],KIT,10)
    inter=parse_numactl_show(Path(run/'interleave-policy.log').read_text())
    assert inter_result['returncode']==0 and inter['policy']=='interleave' and set(inter['interleave_nodes'])>={0,1},inter
    assert policy_signature(inter)!=policy_signature(inherited),'copy treatment has same effective policy as solver default'
    h.save(run/'process-masks.json',masks);h.save(run/'inherited-policy.json',inherited);h.save(run/'interleave-policy.json',inter)
    h.bounded('accepted-source-before',['python3',KIT/'source_checks.py',src,frozen,SUPPLEMENTARY,run/'source-before.json'],KIT,100)
    h.bounded('official-inputs-before',['python3',KIT/'verify-inputs.py','--source',src,
        '--method','scotch','--pins',KIT/'source-pins.json','--case',KIT/'payload-case',
        '--observations',KIT/'source-observations.json'],KIT,60)
    assert os.environ.get('WM_PROJECT_VERSION')=='v2512',os.environ.get('WM_PROJECT_VERSION')
    assert os.environ.get('WM_PRECISION_OPTION')=='DP',os.environ.get('WM_PRECISION_OPTION')
    source_fields=field_snapshot(src);h.save(run/'source-fields.json',source_fields)
    before = h.runtime_snapshot('runtime-before')
    telemetry_preflight = sampler_preflight(reads=5, max_read_ms=50.0)
    h.save(run / 'sampler-preflight.json', telemetry_preflight)
    require_complete_sequence_window(h.remaining(),len(ARMS))
    results = []
    for index, label in enumerate(ARMS):
        arms_left=len(ARMS)-index
        require_complete_sequence_window(h.remaining(),arms_left)
        treatment=TREATMENTS[label]
        h.save(run / (label + '-source-selection.json'), {'method_key':'scotch','source':str(src),
            'core_manifest_sha256':hashlib.sha256(frozen.read_bytes()).hexdigest(),
            'supplementary_manifest_sha256':hashlib.sha256(SUPPLEMENTARY.read_bytes()).hexdigest(),
            'copy_policy_treatment':treatment,'launcher_parent_policy':'same inherited policy as preflight; per-rank policy not measured'})
        dest = run / 'arms' / label
        dest.parent.mkdir(exist_ok=True)
        assert not dest.exists()
        copy_worker=['python3',KIT/'copy_phase.py','--source',src,'--destination',dest,
            '--manifest',frozen,'--supplementary',SUPPLEMENTARY,'--expected-policy',run/'inherited-policy.json',
            '--numactl',numactl,'--treatment',treatment,'--result',run/(label+'-copy-result.json')]
        copy_command=preparation_launch(label,copy_worker,numactl)
        h.bounded(label+'-preparation-copy-hash',copy_command,KIT,COPY_CAP)
        prep=json.loads((run/(label+'-copy-result.json')).read_text())
        assert prep['passed'] and prep['treatment']==treatment and prep['no_source_inode_reuse']
        assert field_snapshot(dest)==source_fields
        ctrl = dest / 'system/controlDict'
        original = ctrl.read_text()
        changed, count = re.subn(r'(?m)^endTime[ \t]+[^;\n]+;[^\n]*$', 'endTime 40;', original)
        assert count == 1
        ctrl.write_text(changed)
        assert (dest / 'system/fvSolution').read_bytes() == (dest / 'system/fvSolution.fixedIter').read_bytes()
        h.save(dest / 'control-change.json', {'only_control_edit': 'endTime=40',
               'source_control_sha256': hashlib.sha256(original.encode()).hexdigest(),
               'run_control_sha256': hashlib.sha256(ctrl.read_bytes()).hexdigest()})
        require_complete_sequence_window(h.remaining(),arms_left,include_current_prep=False)
        solver_policy_result=h.bounded(label+'-solver-policy',['numactl','--show'],KIT,POLICY_CAP)
        solver_policy=parse_numactl_show(Path(run/(label+'-solver-policy.log')).read_text())
        assert solver_policy_result['returncode']==0 and policy_signature(solver_policy)==policy_signature(inherited), \
            'Solver policy differs from the frozen inherited policy'
        h.save(dest/'solver-memory-policy.json',solver_policy)
        require_complete_sequence_window(h.remaining(),arms_left,include_current_prep=False)
        cap=SOLVER_CAP
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
        assert field_snapshot(dest) == source_fields, 'Initialized fields changed'
        h.save(dest / 'postsolve-fields.json', field_snapshot(dest))
        log, timings, cd, counts = review_native_output(dest)
        assert not re.search(r'FOAM FATAL|MPI_ABORT|died from signal|core dumped', (dest / 'solver.stderr').read_text(), re.I)
        handler = 'uncollated'
        assert re.search(r'^I/O\s*:\s*' + handler + r'\b', log, re.M), ('Wrong actual file handler', label, handler)
        row = {'arm': label,'preparation_policy':treatment,'launcher_parent_policy_signature':policy_signature(solver_policy),
               'copy_seconds':prep['copy_seconds'],'copy_hash_seconds':prep['destination_hash_verify_seconds'],
               'preparation_numa_snapshots':prep['numa_snapshots'],
               'steps': 40, 'intervals': 39, 'mean_s_step': statistics.mean(timings),
               'median_s_step': statistics.median(timings), 'maximum_s_step': max(timings),
               'timings_seconds': timings, 'Cd_by_step': cd, 'fixed_iterations': counts,
               'solver_elapsed_seconds': elapsed}
        results.append(row)
        h.save(run / 'partial-results.json', {'arms': results, 'scored_result': False})
        h.phase(label, 'reviewed', {'mean_s_step': row['mean_s_step']})
    after = h.runtime_snapshot('runtime-after')
    assert h.runtime_identity_equal(before, after)
    h.bounded('accepted-source-after',['python3',KIT/'source_checks.py',src,frozen,SUPPLEMENTARY,run/'source-after.json'],KIT,100)
    # Identical source and native work must retain the same force trajectory.
    control_cd = results[0]['Cd_by_step']
    for arm in results[1:]:
        assert len(arm['Cd_by_step']) == len(control_cd)
        for observed, reference in zip(arm['Cd_by_step'], control_cd):
            assert len(observed) == len(reference)
            assert all(math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-10)
                       for a, b in zip(observed, reference)), 'Cross-arm force trajectory changed'
    h.bounded('payload-after', ['sha256sum', '-c', KIT/'payload-sha256.txt'], KIT, 10)
    inherited_mean=statistics.mean(x['mean_s_step'] for x in results if TREATMENTS[x['arm']]=='inherited')
    interleaved_mean=statistics.mean(x['mean_s_step'] for x in results if TREATMENTS[x['arm']]=='interleave-all')
    h.save(run / 'comparison.json', {'passed': True, 'scored_result': False, 'arms': results,
           'inherited_preparation_mean_s_step':inherited_mean,'interleaved_preparation_mean_s_step':interleaved_mean,
           'interleaved_preparation_vs_inherited_percent': 100 * (interleaved_mean / inherited_mean - 1),
           'adjacent_B1_vs_A1_percent':100*(next(x['mean_s_step'] for x in results if x['arm']=='B1-interleaved-prep')/next(x['mean_s_step'] for x in results if x['arm']=='A1-inherited-prep')-1),
           'adjacent_B2_vs_A2_percent':100*(next(x['mean_s_step'] for x in results if x['arm']=='B2-interleaved-prep')/next(x['mean_s_step'] for x in results if x['arm']=='A2-inherited-prep')-1),
           'node_sampler_preflight': telemetry_preflight,
           'node_sampler_arm_statuses': {label: json.loads((run / 'arms' / label / 'telemetry-status.json').read_text()) for label in ARMS},
           'hostname': socket.getfqdn(), 'runtime_identity_stable': True,
           'limits': ['One ABBA allocation balances linear drift but not nonlinear drift; this 40-step confirmation is not a full-run result or promotion.',
                      'Only the copy/hash child receives the interleave policy; the launcher parent is checked before every arm; per-rank policy is not measured.',
                      'Whole-node NUMA counters and cached file pages are not process-attributed; no causal placement or performance explanation follows from them.',
                      'Not a Gadi or NSCC result. No hardware bandwidth or solver helper-affinity data.',
                      'Five-second aggregate procfs sampling is diagnostic only; sample collection duration is not a causal or true solver-interference estimate.']})
    print('IRIS_PREPARATION_NUMA_REPEAT40_ABBA_CONFIRMATION_PASS')


if __name__ == '__main__':
    main()
