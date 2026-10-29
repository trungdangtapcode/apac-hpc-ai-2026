#!/usr/bin/env python3
"""Adversarial real-log fixtures for requested and final cap validation."""
from pathlib import Path
import json,re,subprocess,sys,tempfile
D=Path(__file__).resolve().parent;Q=D.parent;B=Q/'serving-tuning-11/s102-h200-decode-cap64'
base={r:(Q/'runs/27270'/f'{r}.log').read_text() for r in ('prefill-0','prefill-1','decode-0')}
assert base['decode-0'].count('max_running_requests=256,')==2
base['decode-0']=base['decode-0'].replace('max_running_requests=256,','max_running_requests=64,')
def sub(text,old,new):
 assert old in text;return text.replace(old,new)
cases=[('intended_cap64',{},True),('reject_stale_cap256',{'decode-0':sub(base['decode-0'],'max_running_requests=64,','max_running_requests=256,')},False),('reject_wrong_cap128',{'decode-0':sub(base['decode-0'],'max_running_requests=64,','max_running_requests=128,')},False)]
final=next(x for x in base['decode-0'].splitlines() if 'TP0 EP0] max_total_num_tokens=' in x)
cases += [('reject_wrong_final_scheduler',{'decode-0':sub(base['decode-0'],final,final.replace('max_running_requests=64,','max_running_requests=128,'))},False),('reject_missing_final_scheduler',{'decode-0':sub(base['decode-0'],final,'')},False),('reject_prefill_cap_change',{'prefill-0':sub(base['prefill-0'],'max_running_requests=None,','max_running_requests=64,')},False),('reject_wrong_polling',{'decode-0':sub(base['decode-0'],'disaggregation_decode_polling_interval=1,','disaggregation_decode_polling_interval=2,')},False)]
for marker,label in [('Capture target decode CUDA graph end.','reject_missing_graph_rank7'),('NIXL KVManager initialized','reject_missing_NIXL_rank7')]:
 altered='\n'.join(x for x in base['decode-0'].splitlines() if not ('TP7 EP7]' in x and marker in x));assert altered!=base['decode-0'];cases.append((label,{'decode-0':altered},False))
results=[]
with tempfile.TemporaryDirectory(prefix='ap42-cap64-fixture-') as t:
 a=Path(t)
 for name,changes,wanted in cases:
  for role,text in {**base,**changes}.items():(a/f'{role}.log').write_text(text)
  p=subprocess.run([sys.executable,'-B',str(B/'check-fast-runtime.py'),str(a),'control','64'],text=True,capture_output=True)
  assert (p.returncode==0)==wanted,(name,p.stdout,p.stderr)
  results.append({'case':name,'expected_pass':wanted,'passed':True})
assert len(results)==9
(D/'validation.json').write_text(json.dumps({'state':'PASS_CPU_RUNTIME_FIXTURES_ONLY','fixtures':results,'scope':'Historical logs with declared synthetic changes; no candidate GPU evidence.'},indent=2)+'\n')
print('PASS9 meaningful runtime/startup fixtures; not GPU proof.')
