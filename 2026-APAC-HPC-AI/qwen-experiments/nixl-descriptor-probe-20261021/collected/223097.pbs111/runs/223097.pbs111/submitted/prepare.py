#!/usr/bin/env python3
"""Freeze a source-pinned descriptor fixture after bounded CPU validation."""
from pathlib import Path
from datetime import datetime, timezone
import ast
import hashlib
import json
import subprocess
import tarfile

O = Path(__file__).resolve().parent
assert not (O / 'SHA256SUMS').exists(), 'Never rewrite a frozen payload'
base = O.parent / 'nixl-peer-probe-20261021'
prior = json.loads((base / 'collection.json').read_text())
assert prior['state'] == 'BASE_NIXL_VRAM_PASS' and prior['semantic_passed']
prerequisite = {key: prior[key] for key in (
    'job', 'state', 'collected_utc', 'semantic_passed', 'semantic_reason',
    'walltime_s', 'estimated_allocated_charge_su', 'scope')}
prerequisite['source_collection_sha256'] = hashlib.sha256((base / 'collection.json').read_bytes()).hexdigest()
(O / 'prerequisite.json').write_text(json.dumps(prerequisite, indent=2) + '\n')
expected = {
    'nixl-conn.py': '912b7edb95b03604354cc0137f111756ed5bb0eaa91345e713afa53b5bf5024f',
    'source/common-conn.py': 'ba33d63c6920f87b55cf57f9224bb7d08af67e1476bd70b8e1a70067f33a29d7',
    'staging_buffer.py': '52693777d6ee25d1919555a5b910677ba58fa6c18e35782faa7a0470b43839ab',
    'source/nixl_api.py': '27c3ce3c4fe58480aa3bce5e5c158c7659821a3bf1e84680778645adfdaa1bea',
}
assert all(hashlib.sha256((O / name).read_bytes()).hexdigest() == value for name, value in expected.items())
for p in O.glob('*.py'):
    ast.parse(p.read_text(), filename=str(p))
for p in [*O.glob('*.sh'), O / 'component.pbs']:
    subprocess.run(['bash', '-n', str(p)], check=True)
commands = [('cpu-validation', ['python3', str(O / 'CPU-test.py')]),
            ('numpy-rehearsal', ['/tmp/apac-descriptor-cpu-venv/bin/python', str(O / 'numpy-rehearsal.py')])]
for label, command in commands:
    r = subprocess.run(command, capture_output=True, text=True, timeout=60)
    (O / (label + '.stdout')).write_text(r.stdout)
    (O / (label + '.stderr')).write_text(r.stderr)
    assert r.returncode == 0, (label, r.stderr)
functions = [n.name for n in ast.parse((O / 'CPU-test.py').read_text()).body
             if isinstance(n, ast.FunctionDef) and n.name.startswith('test_')]
validation = dict(passed=True, checked_utc=datetime.now(timezone.utc).isoformat(),
    cpu_test_functions=len(functions), cpu_test_names=functions,
    actual_numpy_native_method_rehearsal=True, source_hashes=expected,
    scope='Actual pinned Python descriptor methods and semantic failure fixtures; no GPU, native registration or network execution',
    requested_gpus=2, minutes=10, max_su=2*128*10/60, model_loaded=False,
    raw_peer_metadata_outside_artifact_tree=True, actual_transport_validated=False)
(O / 'validation.json').write_text(json.dumps(validation, indent=2) + '\n')
files = ['component.pbs', 'node-entry.sh', 'entry.sh', 'descriptor.py', 'base-peer.py',
    'CPU-test.py', 'numpy-rehearsal.py', 'prepare.py', 'nixl-conn.py', 'PLAN.md',
    'prerequisite.json', 'validation.json', 'cpu-validation.stdout', 'cpu-validation.stderr',
    'numpy-rehearsal.stdout', 'numpy-rehearsal.stderr', 'source/common-conn.py',
    'source/nixl_api.py', 'source/PROVENANCE.md', 'staging_buffer.py', 'submit-pbs.py',
    'collect-terminal.py', 'refresh-accounting.py']
(O / 'SHA256SUMS').write_text(''.join(hashlib.sha256((O / name).read_bytes()).hexdigest() + '  ' + name + '\n' for name in files))
with tarfile.open(O / 'payload.tar.gz', 'w:gz') as tar:
    for name in files + ['SHA256SUMS']:
        tar.add(O / name, arcname=O.name + '/' + name)
print('Frozen descriptor probe: 2 H100 / 2 nodes / max 10 minutes / max 42.666667 SU. Not submitted.')
