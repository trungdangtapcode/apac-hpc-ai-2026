#!/usr/bin/env python3
"""Verify the actual delivery ZIP and permission-independent PBS launchers."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import tempfile
import zipfile

W = Path('/home/apacsc42/workspace')
O = W / 'submission-review/hpc-update-20261023'


def main():
    report = json.loads((O / 'publication-validation.json').read_text())
    payload = W / 'VNUHCM - TripleU.zip'
    assert hashlib.sha256(payload.read_bytes()).hexdigest() == report['zip_sha256']
    launches = []
    with zipfile.ZipFile(payload) as z, tempfile.TemporaryDirectory(prefix='hpc-extracted-check-') as td:
        assert z.testzip() is None
        assert {n.split('/')[1] for n in z.namelist() if n.count('/') >= 2} == {'Presentation', 'AI_Task', 'HPC_Task'}
        prefix = 'VNUHCM - TripleU/HPC_Task/job_scripts/'
        bundle = Path(td) / 'team folder with spaces' / 'job_scripts'
        bundle.mkdir(parents=True)
        for name in z.namelist():
            if name.startswith(prefix) and not name.endswith('/'):
                relative = Path(name[len(prefix):])
                assert not relative.is_absolute() and '..' not in relative.parts
                target = bundle / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(z.read(name))
                target.chmod(0o644)  # Deliberately simulate lost executable bits.
        subprocess.run(['python3', str(bundle / 'verify-inputs.py'), '--mode', 'bundle'],
                       check=True, stdout=subprocess.DEVNULL)
        for path in bundle.glob('*.pbs'):
            subprocess.run(['bash', '-n', str(path)], check=True)
        # Substitute only the driver in an isolated disposable copy to test the
        # real extracted entry points without allocating or running solver work.
        (bundle / 'run-openfoam.pbs').write_text(
            'python3 - <<\'PY\'\nimport json,os\n'
            'print(json.dumps({k:os.environ[k] for k in '
            '["HPC_NODES","HPC_STEPS","HPC_VARIANT","PBS_O_WORKDIR"]}))\nPY\n')
        (bundle / 'run-openfoam.pbs').chmod(0o644)
        for name, nodes, steps in [('submit-best.pbs', '4', '150'),
                                   ('scaling-1node.pbs', '1', '40'),
                                   ('scaling-2node.pbs', '2', '80')]:
            env = {**os.environ, 'PBS_O_WORKDIR': str(bundle)}
            output = subprocess.check_output(['bash', str(bundle / name)], cwd='/', env=env, text=True)
            observed = json.loads(output)
            assert observed['HPC_NODES'] == nodes and observed['HPC_STEPS'] == steps
            assert observed['PBS_O_WORKDIR'] == str(bundle)
            launches.append(dict(entry=name, nodes=int(nodes), steps=int(steps),
                                 driver_mode='0644', passed=True))
    subprocess.run(['sha256sum', '-c', 'SHA256SUMS'],
                   cwd=W / 'VNUHCM - TripleU/AI_Task/logs', check=True,
                   stdout=subprocess.DEVNULL)
    result = dict(passed=True, zip_sha256=report['zip_sha256'],
                  zip_crc_and_global_checksums=True,
                  extracted_original_bundle_seal_passed=True,
                  extracted_pbs_syntax_passed=True,
                  spaced_path_nonexecutable_driver_launches=launches,
                  limits='Launcher harness only; no PBS submission, mesh/core probe or compute replay performed.')
    (O / 'delivery-validation.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
