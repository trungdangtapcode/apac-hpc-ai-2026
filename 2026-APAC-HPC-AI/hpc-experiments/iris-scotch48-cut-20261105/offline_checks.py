#!/usr/bin/env python3
"""Offline payload integrity, syntax, and synthetic processor-set checks."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
PAYLOAD = ROOT / 'payload'
MANIFEST = json.loads((PAYLOAD / 'payload-sha256.json').read_text())['files']

def check(condition, label):
    print(('PASS ' if condition else 'FAIL ') + label)
    if not condition:
        raise SystemExit(1)

# Exact content list: all regular job/source/validator inputs; exclude the
# manifest itself and local-only runs placeholder to avoid self-reference.
expected = ['expected-mesh.json', 'job.sbatch', 'validate-cut.py', 'verify-payload.py']
expected += [p.relative_to(PAYLOAD).as_posix() for p in sorted((PAYLOAD / 'payload-case').rglob('*')) if p.is_file()]
expected = sorted(expected)
check(sorted(MANIFEST) == expected, 'manifest covers exact payload files')
for name, digest in MANIFEST.items():
    path = PAYLOAD / name
    check(path.is_file() and not path.is_symlink() and hashlib.sha256(path.read_bytes()).hexdigest() == digest,
          'sha256 ' + name)
verify = subprocess.run([sys.executable, str(PAYLOAD / 'verify-payload.py'), str(PAYLOAD)],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
check(verify.returncode == 0, 'pinned payload verifier')
syntax = subprocess.run([sys.executable, '-m', 'py_compile', str(PAYLOAD / 'validate-cut.py'),
                         str(PAYLOAD / 'verify-payload.py')], stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE, universal_newlines=True)
check(syntax.returncode == 0, 'Python syntax')
shell = subprocess.run(['bash', '-n', str(PAYLOAD / 'job.sbatch')], stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, universal_newlines=True)
check(shell.returncode == 0, 'Slurm shell syntax')

# Exercise exact processor set, native log counts, and restored-field checks
# with synthetic directories; no MPI/OpenFOAM command is invoked.
base_cells, remainder = divmod(65334765, 48)
for domain_count, should_pass in [(48, True), (47, False), (49, False)]:
    with tempfile.TemporaryDirectory(prefix='scotch48-cut-check-') as temp:
        case = Path(temp)
        (case / 'logFiles').mkdir()
        (case / 'system/include').mkdir(parents=True)
        (case / 'system/include/caseDefinition').write_text(
            'nCores              48;\ndecompositionMethod scotch;\n')
        lines = ['version=v2512 scalar=64']
        for i in range(48):
            cells = base_cells + (1 if i < remainder else 0)
            lines.append('Number of cells = ' + str(cells))
        lines.extend(['End'])
        (case / 'logFiles/decomposePar.log').write_text('\n'.join(lines) + '\n')
        for i in range(domain_count):
            processor = case / ('processor' + str(i))
            (processor / 'constant/polyMesh').mkdir(parents=True)
            (processor / 'constant/polyMesh/boundary').write_text('synthetic\n')
            (processor / '0').mkdir()
            for field in ['U', 'p', 'k', 'omega', 'nut', 'nuTilda']:
                (processor / '0' / field).write_text('synthetic\n')
        out = case / 'validation.json'
        run = subprocess.run([sys.executable, str(PAYLOAD / 'validate-cut.py'), '--case', str(case),
                              '--output', str(out)], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             universal_newlines=True)
        passed = run.returncode == 0
        check(passed == should_pass, 'synthetic processor count ' + str(domain_count))
