"""Synthetic CPU fixtures for diagnostic integrity; no model calls."""
import copy
import importlib.util
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
spec = importlib.util.spec_from_file_location('wave10', ROOT / 'serving-tuning-10/review-wave10.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
cases = []
for i in range(12):
    value = str(73160429 + i * 137)
    cases.append(dict(name=f'retrieval-{i}', expected=value, prompt=f'archive_key_{i}',
                      input_tokens=3801, response={'choices': [{'message': {'content': value}}]},
                      text=value, passed=True))
good = dict(total=12, passed=12, errors=0, cases=cases)
checks = []


def fixture(name, data=None, marker=None):
    run = OUT / ('synthetic-long-' + name)
    run.mkdir()
    if data is not None:
        (run / 'long-context-check.json').write_text(json.dumps(data) + '\n')
    if marker:
        (run / marker).touch()
    files = [{'path': str(p.relative_to(ROOT)), 'bytes': p.stat().st_size,
              'sha256': m.core.sha(p)} for p in run.iterdir()]
    (run / 'artifact-manifest.json').write_text(json.dumps({'files': files}) + '\n')
    return run


assert m.long_check(fixture('pass', good))['state'] == 'PASSED'
checks.append('12 sealed raw responses pass')
bad = copy.deepcopy(good)
bad['cases'][3].update(text='wrong', response={'choices': [{'message': {'content': 'wrong'}}]}, passed=False)
bad['passed'] = 11
assert m.long_check(fixture('failure', bad))['state'] == 'FAILED'
checks.append('wrong raw answer remains failure')
for name, marker, state in [('missing', None, 'MISSING'),
                            ('deferred', 'long-context-check-deferred.txt', 'DEFERRED'),
                            ('timeout', 'long-context-check-failed.txt', 'FAILED')]:
    assert m.long_check(fixture(name, marker=marker))['state'] == state
    checks.append(name + ' never passes')
assert m.long_check(fixture('contradictory-marker', good, 'long-context-check-failed.txt'))['state'] == 'FAILED'
checks.append('failure marker blocks otherwise passing summary')
bad['passed'] = 12
try:
    m.long_check(fixture('false-summary', bad))
    raise AssertionError('accepted false summary')
except ValueError:
    checks.append('reject false pass summary')
run = fixture('tampered', good)
(run / 'long-context-check.json').write_text('{}\n')
try:
    m.long_check(run)
    raise AssertionError('accepted altered seal')
except ValueError:
    checks.append('reject tampered sealed evidence')
(OUT / 'long-review-validation.json').write_text(json.dumps({
    'passed': len(checks), 'checks': checks,
    'scope': 'Synthetic CPU fixtures only; no SGLang, model or GPU'}, indent=2) + '\n')
print(json.dumps({'passed': len(checks)}))
