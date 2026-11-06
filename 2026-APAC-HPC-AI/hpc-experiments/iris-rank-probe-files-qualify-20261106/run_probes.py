#!/usr/bin/env python3
"""Four bounded MPI launcher probes with independent per-rank proof files."""
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import socket
import subprocess
import sys
import time

from read_rank_proofs import validate_proof_dir

ROOT = Path(__file__).resolve().parent
MODES = [
    ('M56-socket-core', 56, ['--map-by', 'socket', '--bind-to', 'core']),
    ('M48-default', 48, []),
    ('M48-default-repeat', 48, []),
    ('M56-socket-core-repeat', 56, ['--map-by', 'socket', '--bind-to', 'core']),
]
LAUNCH_CAP_SECONDS = 30
WRAPPER_DEADLINE_SECONDS = 240


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def main():
    if os.environ.get('SLURM_NTASKS') != '56' or os.environ.get('SLURM_CPUS_ON_NODE') != '56':
        raise RuntimeError('expected one exclusive 56-CPU Iris allocation')
    if os.environ.get('SLURM_JOB_NUM_NODES') != '1':
        raise RuntimeError('expected exactly one allocated node')
    if os.environ.get('SLURM_GPUS_ON_NODE', '0') not in ('0', ''):
        raise RuntimeError('unexpected allocated GPU')
    job_id = os.environ['SLURM_JOB_ID']
    run = ROOT / 'runs' / job_id
    run.mkdir(parents=True, exist_ok=False)
    start = time.monotonic()
    expected_end = start + WRAPPER_DEADLINE_SECONDS
    manifest = json.loads((ROOT / 'payload-sha256.json').read_text())['files']
    before = {name: sha256(ROOT / name) for name in manifest}
    if before != manifest:
        raise RuntimeError('payload source hashes failed before probes')
    mpirun = shutil.which('mpirun')
    if not mpirun:
        raise RuntimeError('mpirun not found in loaded module environment')
    version = subprocess.run([mpirun, '--version'], stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT, text=True, timeout=10, check=False)
    if version.returncode:
        raise RuntimeError('mpirun --version failed')
    launcher_path = str(Path(mpirun).resolve())
    launcher_binary_sha256 = sha256(launcher_path)
    metadata = {
        'job_id': job_id,
        'node': socket.gethostname(),
        'started_unix': time.time(),
        'mpirun_path': mpirun,
        'mpirun_resolved_path': launcher_path,
        'mpirun_binary_sha256': launcher_binary_sha256,
        'mpirun_version': version.stdout,
        'python_path': sys.executable,
        'python_version': platform.python_version(),
        'module_environment_log': str(run.parent / (job_id + '-module-environment.txt')),
        'wrapper_deadline_seconds': WRAPPER_DEADLINE_SECONDS,
        'launch_cap_seconds_each': LAUNCH_CAP_SECONDS,
        'mode_order': [mode for mode, _, _ in MODES],
        'source_hashes_before': before,
        'modes': [],
        'stdout_proof_parsing': False,
        'probe_phase': 'Pre-MPI_Init launcher process OS-affinity observation.',
        'solver_invoked': False,
    }
    (run / 'metadata-start.json').write_text(json.dumps(metadata, indent=2, sort_keys=True) + '\n')
    for mode, ranks, flags in MODES:
        if time.monotonic() + LAUNCH_CAP_SECONDS + (len(MODES) - len(metadata['modes']) - 1) * LAUNCH_CAP_SECONDS > expected_end:
            raise RuntimeError('insufficient time to finish all remaining launch probes')
        proof_dir = run / 'proofs' / mode
        proof_dir.mkdir(parents=True, exist_ok=False)
        launcher_log = run / (mode + '.launcher.stdout.log')
        launcher_err = run / (mode + '.launcher.stderr.log')
        command = [mpirun, '--report-bindings', '--display-map', *flags, '-np', str(ranks),
                   '--', sys.executable, str(ROOT / 'probe_writer.py'), '--proof-dir', str(proof_dir)]
        mode_start = time.monotonic()
        with launcher_log.open('w') as out, launcher_err.open('w') as err:
            result = subprocess.run(command, cwd=ROOT, stdout=out, stderr=err,
                                    timeout=LAUNCH_CAP_SECONDS, check=False)
        elapsed = time.monotonic() - mode_start
        if result.returncode:
            raise RuntimeError('%s launcher returned %d; stdout/stderr retained' % (mode, result.returncode))
        proof_summary = validate_proof_dir(proof_dir, ranks)
        (run / (mode + '.proof-validation.json')).write_text(
            json.dumps(proof_summary, indent=2, sort_keys=True) + '\n')
        metadata['modes'].append({
            'mode': mode,
            'ranks': ranks,
            'mpi_flags': flags,
            'command': command,
            'elapsed_seconds': elapsed,
            'returncode': result.returncode,
            'proof_directory': str(proof_dir),
            'proof_validation': str(run / (mode + '.proof-validation.json')),
            'stdout_log': str(launcher_log),
            'stderr_log': str(launcher_err),
        })
        (run / 'metadata-progress.json').write_text(json.dumps(metadata, indent=2, sort_keys=True) + '\n')
    after = {name: sha256(ROOT / name) for name in manifest}
    if after != before:
        raise RuntimeError('payload source hashes changed during diagnostic')
    metadata.update({
        'source_hashes_before': before,
        'source_hashes_after': after,
        'payload_sources_unchanged': True,
        'finished_unix': time.time(),
        'elapsed_seconds': time.monotonic() - start,
        'all_four_probes_passed': len(metadata['modes']) == 4,
    })
    (run / 'metadata.json').write_text(json.dumps(metadata, indent=2, sort_keys=True) + '\n')
    if len(metadata['modes']) != 4:
        raise RuntimeError('incomplete probe set')
    print('IRIS_RANK_PROBE_FILES_QUALIFICATION_PASS')


if __name__ == '__main__':
    main()
