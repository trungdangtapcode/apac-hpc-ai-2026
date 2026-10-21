"""Execute the pinned native capacity branch and adversarial log-gate fixtures."""
import ast
import contextlib
import copy
import hashlib
import importlib.util
import json
import logging
from pathlib import Path
import tempfile
from types import SimpleNamespace

O = Path(__file__).resolve().parent
R = O.parent
source = R / 'eagle3-preflight-20261020/source/pilot-interfaces/sgl-workspace/sglang/python/sglang/srt/arg_groups/speculative_hook.py'
tree = ast.parse(source.read_text())
function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == '_handle_eagle_family')
condition = next(n for n in function.body if isinstance(n, ast.If) and ast.unparse(n.test) == 'server_args.max_running_requests is None')
code = compile(ast.Module(body=[copy.deepcopy(condition)], type_ignores=[]), str(source), 'exec')
logger = logging.getLogger('native-capacity-branch');logger.addHandler(logging.NullHandler())
branch_cases = []
for requested, expected in [(None, 48), (64, 64), (256, 256), (4096, 4096)]:
    args = SimpleNamespace(max_running_requests=requested)
    exec(code, dict(server_args=args, logger=logger))
    assert args.max_running_requests == expected
    branch_cases.append(dict(requested=requested, resolved=args.max_running_requests))
spec = importlib.util.spec_from_file_location('capacity', O / 'audit-capacity.py')
m = importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
fixture_cases = []
with tempfile.TemporaryDirectory(prefix='eagle-capacity-') as tmp:
    root = Path(tmp)
    def write(mode, changed=None):
        for p in root.iterdir():p.unlink()
        for role, (tp, ep, capacity) in m.ROLES.items():
            fields = dict(max_running_requests=capacity, tp_size=tp, ep_size=ep,
                          dtype='bfloat16', mem_fraction_static=.9, chunked_prefill_size=4096,
                          speculative_algorithm='EAGLE3' if mode == 'candidate' else None)
            if changed and changed[0] == role:fields.update(changed[1])
            text = 'server_args=ServerArgs(' + ', '.join(k+'='+repr(v) for k,v in fields.items()) + ')\n' + 'max_total_num_tokens=100000, max_running_requests=' + str(capacity) + ', context_len=8192\n'
            (root / ('task-'+role+'-node.fixture.log')).write_text(text)
    for mode in ['control', 'candidate']:
        write(mode);assert m.audit(root,mode)['passed'];fixture_cases.append(mode+'_explicit_capacity_pass')
    for case, change in [('native_spec_default', ('prefill-0',dict(max_running_requests=48))),
                         ('target_default', ('prefill-1',dict(max_running_requests=4096))),
                         ('changed_tp', ('decode-0',dict(tp_size=4))),
                         ('auto_dtype', ('prefill-0',dict(dtype='auto'))),
                         ('spec_disabled', ('decode-0',dict(speculative_algorithm=None)))]:
        write('candidate',change);assert not m.audit(root,'candidate')['passed'];fixture_cases.append(case+'_rejected')
    write('candidate');next(root.glob('*prefill-0*')).unlink()
    assert not m.audit(root,'candidate')['passed'];fixture_cases.append('missing_role_rejected')
    write('candidate');original=next(root.glob('*decode-0*'))
    (root/'decode-0.log').write_text(original.read_text().replace('max_running_requests=256','max_running_requests=64'))
    assert not m.audit(root,'candidate')['passed'];fixture_cases.append('conflicting_logs_rejected')
    write('candidate')
    p = next(root.glob('*prefill-0*'))
    p.write_text(p.read_text().split('max_total_num_tokens=')[0])
    assert not m.audit(root,'candidate')['passed'];fixture_cases.append('missing_final_scheduler_rejected')
    write('candidate')
    p = next(root.glob('*decode-0*'))
    p.write_text(p.read_text().replace('max_total_num_tokens=100000, max_running_requests=256', 'max_total_num_tokens=100000, max_running_requests=128'))
    assert not m.audit(root,'candidate')['passed'];fixture_cases.append('different_final_scheduler_rejected')
# Parse sealed real historical logs: establish what resolved, not what flags suggested.
historical = {}
for job,relative in [('222761','eagle3-reference-corpusfix-20261021'),('222763','eagle3-pd-candidate-20261021')]:
    root = R/relative/'collected'/(job+'.pbs111')/'runs'/(job+'.pbs111')
    observed={}
    for role in m.ROLES:
        for path in sorted(root.glob('task-'+role+'-*.log')):
            with path.open(errors='replace') as stream:
                for line in stream:
                    if 'server_args=ServerArgs(' in line:observed[role]=m.parse(line);break
    assert set(observed)==set(m.ROLES)
    assert observed['decode-0']['max_running_requests']==256
    assert all(observed[x]['max_running_requests']==(None if job=='222761' else 48) for x in ['prefill-0','prefill-1'])
    final = {}
    for role in m.ROLES:
        values = set()
        for path in root.glob('task-'+role+'-*.log'):
            for line in path.open(errors='replace'):
                if 'max_total_num_tokens=' in line and 'server_args=ServerArgs(' not in line:
                    match = __import__('re').search(r'(?<![\w.])max_running_requests=(\d+)(?=[,\s])',line)
                    if match:values.add(int(match[1]))
        final[role] = sorted(values)
    if job=='222761':assert final=={'prefill-0':[4096],'prefill-1':[4096],'decode-0':[256]}
    else:assert all(not v for v in final.values())
    historical[job]=dict(server_args=observed,final_scheduler=final)
result=dict(passed=True, native_source=str(source), native_source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
            native_function=function.name, native_branch_line=condition.lineno, native_branch_cases=branch_cases,
            adversarial_fixture_cases=fixture_cases, historical_resolved_values=historical,
            scope='Isolated exact native AST branch plus synthetic log fixtures and sealed historical log parsing; no full ServerArgs initialization, model loading or GPU execution')
(O/'validation.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(passed=True,native_cases=len(branch_cases),log_gate_cases=len(fixture_cases),historical_jobs=list(historical))))
