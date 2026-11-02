"""Offline checks for exact candidate coefficients and frozen numerical inputs."""
from pathlib import Path
import shutil, tempfile
import init

E=Path(__file__).resolve().parent
assert init.DEADLINE_SECONDS == 1680
assert init.expected_config('system/decomposeParDict').count(b'domains       (2 28);') == 1
assert b'domainWeights (1 0.1);' in init.expected_config('system/decomposeParDict')
assert b'processorWeights' not in init.expected_config('system/decomposeParDict')
with tempfile.TemporaryDirectory(prefix='iris-scotch2x28-offline-') as td:
    base=Path(td)/'canonical'; candidate=Path(td)/'candidate'
    shutil.copytree(E/'payload-case',base)
    base.mkdir(exist_ok=True)
    init.CASE_SRC=base
    shutil.copytree(base,candidate)
    (candidate/'Allrun').unlink()
    (candidate/'system/include/caseDefinition').write_bytes(init.expected_config('system/include/caseDefinition'))
    (candidate/'system/decomposeParDict').write_bytes(init.expected_config('system/decomposeParDict'))
    assert init.check_case_inputs(base)['passed']
    assert init.check_case_inputs(candidate,candidate=True)['passed']
    config=candidate/'system/decomposeParDict'; text=config.read_text().replace('domainWeights (1 0.1);','domainWeights (1 0.01);'); config.write_text(text)
    try: init.check_case_inputs(candidate,candidate=True)
    except AssertionError: pass
    else: raise AssertionError('wrong Scotch weight accepted')
    config.write_bytes(init.expected_config('system/decomposeParDict'))
    physics=candidate/'system/fvSolution'; physics.write_bytes(physics.read_bytes()+b'\n// altered-physics-fixture\n')
    try: init.check_case_inputs(candidate,candidate=True)
    except AssertionError: pass
    else: raise AssertionError('numerical input mutation accepted')
print('PASS: exact 2x28/10:1 Scotch config, no processorWeights, and physics/source drift rejection')
