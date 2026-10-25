#!/usr/bin/env python3
"""CPU regressions against retained real profiles; not new GPU measurements."""
from pathlib import Path
import ast, importlib.util, json, subprocess, sys
ROOT=Path(__file__).resolve().parents[1]
names=['s64-h200-prefill-power-of-two','s65-h200-router-rr-control','s62r4-h200-two-decode-tp4']
records=[]
for name in names:
    b=ROOT/'serving-tuning-11'/name
    subprocess.run(['sha256sum','-c','SHA256SUMS'],cwd=b,check=True,stdout=subprocess.DEVNULL)
    for p in b.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
    for p in b.glob('*.sh'):subprocess.run(['bash','-n',str(p)],check=True)
    subprocess.run(['bash','-n',str(b/'job.sbatch')],check=True)
    record={'bundle':name,'checksums':True,'python_syntax':True,'shell_syntax':True,'profiles':[]}
    spec=importlib.util.spec_from_file_location('gates',b/'performance_gates.py');g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
    for job in (25947,26065,26066,26067,26068):
        art=ROOT/'runs'/str(job)
        expected=json.loads((art/'submitted-payload/expected-input-config.json').read_text())
        try:
            r=g.check_aiperf(art,expected)
            assert job!=26068, 'N72 real SLA failure must be rejected'
            record['profiles'].append({'job':job,'accepted':True,'good_output_tokens_s':r['good_output_tokens_per_second']})
        except AssertionError as e:
            if job!=26068:raise
            assert 'SLA floor' in str(e),str(e)
            record['profiles'].append({'job':job,'accepted':False,'reason':str(e),'expected_rejection':'real N72 SLA failure'})
    try:
        g.check_aiperf(ROOT/'runs/26065',json.loads((b/'expected-input-config.json').read_text()))
    except AssertionError as e:
        assert 'bundle concurrency' in str(e)
        record['wrong_expected_N_rejected']=str(e)
    else:raise AssertionError('N66 data accepted as N64')
    records.append(record)
# Pin what both routing bundles should actually launch, and the precise enum representation.
for name,policy in zip(names[:2],('power_of_two','round_robin')):
    b=ROOT/'serving-tuning-11'/name
    assert json.loads((b/'config.json').read_text())['prefill_policy']==policy
    assert f'export QWEN_PREFILL_POLICY={policy}\n' in (b/'job.sbatch').read_text()
    assert '--prefill-policy "$PREFILL_POLICY"' in (b/'topology-job.sh').read_text()
    assert 'Some(PowerOfTwo { load_check_interval_secs: 5 })' in (b/'check-performance.py').read_text()
# Check real native round-robin startup with the exact inserted policy block.
p=ROOT/'serving-tuning-11'/names[1]/'check-performance.py'
source=p.read_text(); block=source[source.index('    policy_log='):source.index('    context=json.loads')]
exec('def replay_router(art,cfg):\n'+block,globals())
import re
replay_router(ROOT/'runs/25947',{'prefill_policy':'round_robin'})
try:replay_router(ROOT/'runs/25947',{'prefill_policy':'power_of_two'})
except AssertionError:pass
else:raise AssertionError('Wrong actual router policy accepted')
s=ROOT/'serving-tuning-11'/names[2]/'warm-topology.py'
tree=ast.parse(s.read_text())
urlopen_calls=[n for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='urlopen']
assert len(urlopen_calls)==2
assert 'timeout=max(0.1, deadline-time.time())' in s.read_text()
assert 'min(30' not in s.read_text()
report={'state':'PASS_CPU_REGRESSION_ONLY','records':records,'actual_router_round_robin_verified':25947,'wrong_actual_router_policy_rejected':True,'timeout_contract':'request uses remaining shared180s deadline; outer180s cap remains','limits':'No newly executed worker, PD route, GPU kernel, accuracy or performance result.'}
Path(__file__).with_name('verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
