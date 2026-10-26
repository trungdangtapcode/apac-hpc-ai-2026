#!/usr/bin/env python3
"""CPU checks of observer transparency and fail-closed gates; no GPU claim."""
import hashlib,importlib.util,json,sys,tempfile,shutil
from pathlib import Path
S=Path(__file__).resolve().parent;Q=S.parent
b=Q/'eagle3-h100-equal-tp-observer-r2-20261026'
sys.path[:0]=[str(b),str(b/'pd-observer')]
def load(p,name):
 spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
obs=load(b/'pd-observer/observer.py','test_observer');events=[]
obs._bounded_transfer_record=lambda kind,peer,row:events.append((kind,peer,row))
handle=object();calls=[]
def native(self,*args,**kwargs):calls.append((self,args,kwargs));return handle
self=object();args=('peer',[1,2],['ptr'],[3,4,5],0,'notif','kind')
assert obs.wrap_transfer(native,'send_kvcache')(self,*args) is handle
assert calls==[(self,args,{})]
assert events[0][2]['source_page_count']==2 and events[0][2]['destination_page_count']==3
assert [e[2]['marker'] for e in events]==['start','returned_handle']
error=ValueError('synthetic observer test')
def fail(self,*args,**kwargs):raise error
try:obs.wrap_transfer(fail,'send_kvcache')(self,*args)
except ValueError as exc:assert exc is error
else:raise AssertionError('native exception swallowed')
assert events[-1][2]['marker']=='exception'
gate=load(b/'metadata-gate.py','test_gate')
raw=Q/'h100-recovered-runs-20261026/eagle3-h100-single-node-equal-tp-20261024/runs/224560.pbs111'
assert gate.validate_pre_warmup(raw)['state']=='PRE_WARMUP_METADATA_PASS'
parent='eagle3-h100-single-node-equal-tp-20261024'
try:gate.validate_post_semantic(raw,parent)
except ValueError as exc:assert 'send_kvcache' in str(exc)
else:raise AssertionError('missing actual KV evidence accepted')
# Synthetic events live only in a temporary fixture, never in retained GPU evidence.
with tempfile.TemporaryDirectory(prefix='apac-observer-synthetic-') as tmp:
 art=Path(tmp)/'fixture';shutil.copytree(raw,art)
 markers=[json.loads(x) for x in (art/'phase-markers.jsonl').read_text().splitlines()]
 start=next(x['utc_ns'] for x in markers if x['event']=='semantic_start')
 for rank in range(4):
  p=art/f'pd-observer/prefill-0/tp-{rank}/transfers.jsonl'
  with p.open('a') as f:
   for marker in ('start','returned_handle'):f.write(json.dumps({'kind':'send_kvcache','marker':marker,'tp_rank':rank,'time_unix_ns':start+1})+'\n')
 assert gate.validate_post_semantic(art,parent)['state']=='ONE_SEMANTIC_PD_RECEIPT_PASS'
 p=art/'pd-observer/prefill-0/tp-3/transfers.jsonl';original=p.read_text();p.write_text('\n'.join(x for x in original.splitlines() if json.loads(x)['kind']!='send_kvcache')+'\n')
 try:gate.validate_post_semantic(art,parent)
 except ValueError as exc:assert 'coverage' in str(exc)
 else:raise AssertionError('missing rank accepted')
 p.write_text(original+json.dumps({'kind':'send_kvcache','marker':'exception','tp_rank':3,'time_unix_ns':start+2})+'\n')
 try:gate.validate_post_semantic(art,parent)
 except ValueError as exc:assert 'exception' in str(exc)
 else:raise AssertionError('exception accepted')
parent=Q/'nscc-pbs/h100-cpu-envelope-legacy-n54-79';child=Q/'h100-incumbent-n54-refresh-20261026';identical=[]
for line in (parent/'SHA256SUMS').read_text().splitlines():
 digest,rel=line.split(None,1)
 if rel in {'config.json','benchmark.pbs','submit-pbs.py'}:continue
 assert hashlib.sha256((child/rel).read_bytes()).hexdigest()==digest;identical.append(rel)
result={'state':'CPU_PREFLIGHT_PASS_NOT_GPU_ACCEPTANCE','checks':['positional argument counts','native arguments/return identity','native exception identity','actual old metadata pass','old missing KV markers rejected','synthetic full rank coverage accepted','synthetic missing rank rejected','synthetic exception rejected'],'incumbent_identical_operational_files':identical,'actual_new_GPU_observation':'NOT_COLLECTED'}
(S/'verification.json').write_text(json.dumps(result,indent=2)+'\n');print(result['state'])
