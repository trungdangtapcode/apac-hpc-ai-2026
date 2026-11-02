"""Offline checks for the exact 2x28/100:1 treatment and unchanged canonical physics."""
from pathlib import Path
import shutil, tempfile
import init

E=Path(__file__).resolve().parent
assert init.DEADLINE_SECONDS == 1680
expected=init.expected_config('system/decomposeParDict')
assert expected.count(b'domains       (2 28);') == 1
assert b'domainWeights (1 0.01);' in expected
assert b'processorWeights' not in expected
with tempfile.TemporaryDirectory(prefix='iris-scotch2x28-w100-offline-') as td:
    base=Path(td)/'canonical'; candidate=Path(td)/'candidate'
    shutil.copytree(E/'payload-case',base)
    init.CASE_SRC=base
    shutil.copytree(base,candidate)
    (candidate/'Allrun').unlink()
    (candidate/'system/include/caseDefinition').write_bytes(init.expected_config('system/include/caseDefinition'))
    (candidate/'system/decomposeParDict').write_bytes(expected)
    assert init.check_case_inputs(base)['passed']
    assert init.check_case_inputs(candidate,candidate=True)['passed']
    config=candidate/'system/decomposeParDict'
    config.write_text(config.read_text().replace('domainWeights (1 0.01);','domainWeights (1 0.1);'))
    try: init.check_case_inputs(candidate,candidate=True)
    except AssertionError: pass
    else: raise AssertionError('prior 10:1 treatment accepted')
    config.write_bytes(expected)
    physics=candidate/'system/fvSolution'; physics.write_bytes(physics.read_bytes()+b'\n// altered-physics-fixture\n')
    try: init.check_case_inputs(candidate,candidate=True)
    except AssertionError: pass
    else: raise AssertionError('numerical input mutation accepted')
print('PASS: exact 2x28/100:1 treatment; reject prior 10:1 and physics/source drift')
