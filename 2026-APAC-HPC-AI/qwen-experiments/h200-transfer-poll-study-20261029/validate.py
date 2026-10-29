#!/usr/bin/env python3
"""Adversarial CPU fixtures for exact role-local polling readiness gates."""
from pathlib import Path
import importlib.util,json,re,subprocess,sys,tempfile
D=Path(__file__).resolve().parent;Q=D.parent
prep=json.loads((D/'preparation.json').read_text());results=[]
base={r:(Q/'runs/26949'/f'{r}.log').read_text() for r in ('prefill-0','prefill-1','decode-0')}
def replace_field(text,old,new):
 assert text.count(old)==1,(old,text.count(old));return text.replace(old,new)
for item in prep['bundles']:
 B=Q/item['bundle'];k=item['interval'];logs=dict(base)
 logs['decode-0']=replace_field(logs['decode-0'],'disaggregation_decode_polling_interval=1,',f'disaggregation_decode_polling_interval={k},')
 cases=[('intended_target_only_runtime',{},True)]
 for value in (k+1,k+2):cases.append((f'reject_wrong_decode_{value}',{'decode-0':replace_field(logs['decode-0'],f'disaggregation_decode_polling_interval={k},',f'disaggregation_decode_polling_interval={value},')},False))
 for role in ('prefill-0','prefill-1'):cases.append((f'reject_wrong_{role}',{role:replace_field(logs[role],'disaggregation_decode_polling_interval=1,','disaggregation_decode_polling_interval=2,')},False))
 cases.append(('reject_missing_decode_setting',{'decode-0':replace_field(logs['decode-0'],f'disaggregation_decode_polling_interval={k},','')},False))
 cases.append(('reject_nonliteral_decode_setting',{'decode-0':replace_field(logs['decode-0'],f'disaggregation_decode_polling_interval={k},','disaggregation_decode_polling_interval=unknown_value,')},False))
 graph='\n'.join(s for s in logs['decode-0'].splitlines() if not ('TP7 EP7]' in s and 'Capture target decode CUDA graph end.' in s));assert graph!=logs['decode-0']
 cases.append(('reject_missing_target_graph_rank7',{'decode-0':graph},False))
 nixl='\n'.join(s for s in logs['decode-0'].splitlines() if not ('TP7 EP7]' in s and 'NIXL KVManager initialized' in s));assert nixl!=logs['decode-0']
 cases.append(('reject_missing_NIXL_rank7',{'decode-0':nixl},False))
 with tempfile.TemporaryDirectory(prefix='ap42-poll-fixtures-') as tmp:
  a=Path(tmp)
  for name,changes,wanted in cases:
   for role,text in {**logs,**changes}.items():(a/f'{role}.log').write_text(text)
   run=subprocess.run([sys.executable,'-B',str(B/'check-fast-runtime.py'),str(a),'control','64'],text=True,capture_output=True)
   assert (run.returncode==0)==wanted,(k,name,run.stdout,run.stderr)
   if wanted:
    receipt=json.loads(run.stdout)
    assert receipt['roles']['decode-0']['decode_transfer_polling_interval']==k
    assert all(receipt['roles'][r]['decode_transfer_polling_interval']==1 for r in ('prefill-0','prefill-1'))
    spec=importlib.util.spec_from_file_location('poll_independent_gate',B/'check-performance.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    for role in logs:assert mod.read_server_args(a,role)['disaggregation_decode_polling_interval']==(k if role=='decode-0' else 1)
   results.append({'interval':k,'case':name,'expected_pass':wanted,'passed':True})
assert len(results)==27
(D/'validation.json').write_text(json.dumps({'state':'PASS_CPU_FIXTURES_ONLY','fixtures':results,'scope':'Real historical logs with explicitly synthetic argument alterations, plus missing actual startup markers; not candidate runtime or GPU evidence.'},indent=2)+'\n')
print('PASS: 27 role/argument/startup fixtures across all three intervals; no GPU evidence claimed.')
