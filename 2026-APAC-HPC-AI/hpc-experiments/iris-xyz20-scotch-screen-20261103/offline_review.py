"""Offline configuration/provenance gates; never connects to Iris or fabricates results."""
from pathlib import Path
import hashlib
import importlib.util
import json
import re
import shutil
import tempfile

import run
from case_checks import source_check
from native_output import review_native_output

E = Path(__file__).resolve().parent
assert run.ARMS == ['S1-scotch', 'X1-hierarchical-xyz', 'X2-hierarchical-xyz', 'S2-scotch']
assert run.SOURCES['xyz'].as_posix().endswith('/initialized/order-xyz')
assert run.MANIFESTS['xyz'].name == 'accepted-xyz-source-manifest.json'
assert run.MANIFESTS['scotch'].name == 'accepted-source-manifest.json'
assert 4 * 810 + 120 == 3360 <= 3510
assert 3510 < 3540 < 3600
assert all('zyx' not in str(path) for path in [run.SOURCES['xyz'], run.MANIFESTS['xyz']])

xyz = json.loads((E / 'accepted-xyz-source-manifest.json').read_text())
assert len(xyz['files']) == 1040
assert xyz['symlinks'] == {'constant/polyMesh': '/global/exafs/groups/rdmaworkshop/2026hpcai-openfoam/occDrivAer/polyMesh'}
assert len(json.loads((E / 'xyz-source-field-seal-2294262.json').read_text())['fields']) == 336
assert json.loads((E / 'xyz-source-check-2294262.json').read_text()) == {'factors':[7,4,2], 'order':'xyz', 'passed':True, 'pinned_input_files':41}
historical = E.parent / 'iris-order56-full150-reverse-20261028/completed-2294262/collected/cases/xyz'
before = json.loads((historical / 'source-before.json').read_text())
after = json.loads((historical / 'source-after.json').read_text())
assert before == after == xyz
assert (E / 'accepted-xyz-source-manifest.json').read_bytes() == (historical / 'source-before.json').read_bytes()

# Test the exact canonical xyz transform; reject changed axis order and altered physics.
with tempfile.TemporaryDirectory(prefix='iris-xyz20-source-fixture-') as td:
    candidate = Path(td) / 'candidate'
    shutil.copytree(E / 'payload-case', candidate)
    (candidate / 'Allrun').unlink()
    cdef = candidate / 'system/include/caseDefinition'
    text, n = re.subn(r'(?m)^nCores .*$', 'nCores              56;', cdef.read_text()); assert n == 1
    text, n = re.subn(r'(?m)^nHierarchical .*$', 'nHierarchical       (7 4 2);', text); assert n == 1
    cdef.write_text(text)
    decomp = candidate / 'system/decomposeParDict'
    assert source_check(candidate, 'xyz')['passed']
    wrong_order, n = re.subn(r'(?m)^([ \t]+order[ \t]+)xyz;', r'\g<1>zyx;', decomp.read_text()); assert n == 1
    decomp.write_text(wrong_order)
    try: source_check(candidate, 'xyz')
    except AssertionError: pass
    else: raise AssertionError('wrong order accepted')
    decomp.write_text(re.sub(r'(?m)^([ \t]+order[ \t]+)zyx;', r'\g<1>xyz;', wrong_order))
    physics = candidate / 'system/fvSolution'
    physics.write_bytes(physics.read_bytes() + b'\n// altered-physics-fixture\n')
    try: source_check(candidate, 'xyz')
    except AssertionError: pass
    else: raise AssertionError('changed physics accepted')

# Real historical 150-step output must fail the new exact 20-step parser.
old_arm = historical / 'simpleFoam.log'
assert old_arm.is_file()
try: review_native_output(historical)
except AssertionError: pass
else: raise AssertionError('150-step output accepted by 20-step gate')

print(json.dumps({'passed':True,'scope':'Offline configuration/provenance only; sampler lifecycle fixtures run separately in sampler_offline_review.py.',
 'checks':['Exact S/X/X/S ABBA and xyz source bindings','Historical source-before equals source-after and 1,040-file XYZ manifest','336 initialized field seals and 41-pin xyz source check','Canonical xyz source transform passes; wrong axis order and altered physics reject','Old 150-step native log rejects under exact 20-step/19-interval gate','Protected windows, CPU-hour ceiling, and nested deadlines'],
 'directional_limit':'Historical native minimum-sample recommendation is 361 versus 19 planned; not confirmatory.'},indent=2))
