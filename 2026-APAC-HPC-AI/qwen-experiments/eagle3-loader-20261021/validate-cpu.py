"""Adversarial isolation checks that require no CUDA or serving imports."""
from pathlib import Path
import ast, hashlib, json, subprocess
from gpu_identity import canonical_uuid, require_same_device
O = Path(__file__).resolve().parent
u = '01234567-89ab-cdef-0123-456789abcdef'
assert require_same_device('GPU-' + u, u.upper()) == u
assert require_same_device('GPU-' + u, 'GPU-' + u) == u
rejected = 0
for value in ['', '0', u[:8], 'GPU-' + u[:8], 'MIG-' + u,
              ' GPU-' + u, 'GPU-' + u + ',GPU-' + u, u.replace('-', ''), None, b'uuid']:
    try:
        canonical_uuid(value)
    except ValueError:
        rejected += 1
    else:
        raise AssertionError('Malformed identity accepted')
try:
    require_same_device('GPU-' + u, '11234567-89ab-cdef-0123-456789abcdef')
except ValueError:
    rejected += 1
else:
    raise AssertionError('Different GPU accepted')
for p in O.glob('*.py'):
    ast.parse(p.read_text(), filename=str(p))
for name in ['component.pbs', 'component-entry.sh']:
    subprocess.run(['bash', '-n', str(O / name)], check=True)
previous = O.parent / 'eagle3-component-homefix-20261021'
assert (O/'gateway-echo.py').read_bytes() == (previous/'gateway-echo.py').read_bytes()
loader = ast.parse((O/'loader.py').read_text())
init_call = next(n for n in ast.walk(loader) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'init_distributed_environment')
assert next(k.value.value for k in init_call.keywords if k.arg == 'timeout') == 30
source = (O/'source/sgl-workspace/sglang/python/sglang/srt/distributed/parallel_state.py').read_text()
assert 'assert isinstance(timeout, (int))' in source
assert '$src' not in (O/'component-entry.sh').read_text()
report = dict(passed=True, malformed_or_mismatched_uuid_rejections=rejected,
              scope='Strict full-UUID rejection, loader syntax, native timeout signature and frozen payload; model load remains unverified',
              derived_from_job='222749.pbs111', max_su=128*4/60,
              target_inference=False, official_client_changed=False)
(O/'validation.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report))
