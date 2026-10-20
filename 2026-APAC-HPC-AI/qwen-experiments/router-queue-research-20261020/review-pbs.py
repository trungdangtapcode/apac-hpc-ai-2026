"""Review newly recovered PBS measurements, frozen payloads and actual runtime."""
from pathlib import Path
import datetime,importlib.util,json,re
R=Path(__file__).resolve().parents[1];O=Path(__file__).resolve().parent;P=R/'nscc-pbs'
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
m=module('candidate',P/'review-candidate-sweep.py');core=module('core',R/'serving-tuning/review-n54.py')
base=P/'collected/220575.pbs111/20261016T054555388584Z';smoke=P/'collected/220562.pbs111/20261015T194718195272Z/runs/220562.pbs111/output-smoke.json'
receipts=json.loads((O/'pbs-receipts.json').read_text());pilots={p['id']:p for p in json.loads((O/'pilots.json').read_text())}
available=[r for r in receipts if (O/('collect-'+r['job'].split('.')[0]+'.json')).exists()]
assert available, 'No collected terminal run to review'
snapshots={r['job'].split('.')[0]:Path(json.loads((O/('collect-'+r['job'].split('.')[0]+'.json')).read_text())['destination']) for r in available}
reference=Path(json.loads((R/'h100-prefill-hpc-chunk-interaction-20261020/collect-222281.json').read_text())['destination']);refjob='222281.pbs111';refseal=json.loads((reference/'evidence-sha256.json').read_text())
for number,name,n in [(r['job'].split('.')[0],r['id'],54) for r in available]:
 job=number+'.pbs111';snapshot=snapshots[number];run=snapshot/'runs'/job
 try:
  gates=m.compare(snapshot,base,smoke,name);assert gates['terminal_seal_short_payload_pass'];assert gates['long_diagnostic']['state']=='PASSED'
  points=gates['candidate_review']['points'];assert len(points)==1 and points[0]['concurrency']==n
  point=points[0];assert point['protocol_pass'] and point['phase_complete']
  seal=json.loads((snapshot/'evidence-sha256.json').read_text());proof={}
  for role,tp,ep in [('prefill-0',4,1),('prefill-1',4,1),('decode-0',8,8)]:
   logs=list(run.glob('task-'+role+'-node*.log'));refs=list((reference/'runs'/refjob).glob('task-'+role+'-node*.log'));assert len(logs)==len(refs)==1
   f,rf=logs[0],refs[0];assert seal[str(f.relative_to(snapshot))]==core.sha(f);assert refseal[str(rf.relative_to(reference))]==core.sha(rf)
   a,b=core.server_args(f),core.server_args(rf);text=f.read_text();assert a['tp_size']==str(tp) and a['ep_size']==str(ep);assert 'KV Cache is allocated. dtype: torch.bfloat16' in text;assert a['speculative_algorithm']=='None'
   delta={k:[b.get(k),a.get(k)] for k in a.keys()|b.keys() if a.get(k)!=b.get(k)};allowed={'random_seed'}
   assert a['enable_metrics']=='True' and a['scheduler_recv_interval']=='1'
   if role.startswith('prefill'):assert a['chunked_prefill_size']=='4096'
   assert a['decode_attention_backend']==("'flashinfer'" if role=='decode-0' else 'None')
   assert not set(delta)-allowed,(role,delta)
   expected=False
   assert 'DYNAMIC_GRAD_MODE_PREFLIGHT_PASSED inference_mode='+str(expected) in text,(number,role,expected)
   assert a['moe_runner_backend']=="'hpc_ops'"
   if a['moe_runner_backend']=="'hpc_ops'":assert 'HPC_OPS_PREFLIGHT_PASSED' in text
   if role=='decode-0':
    assert sorted(set(map(int,re.findall(r'backend=mnnvl, rank=(\d+), world_size=8',text))))==list(range(8))
    assert sorted(set(map(int,re.findall(r'TP(\d+) EP\d+\] Using hybrid attention backend.*decode_backend=flashinfer, prefill_backend=fa3',text))))==list(range(8))

   proof[role]=delta
  routing=[]
  expected_policy=pilots[name]['prefill_policy']
  enum='RoundRobin' if expected_policy=='round_robin' else 'PowerOfTwo'
  for path in sorted(run.glob('task-aux*.log')):
   assert seal[str(path.relative_to(snapshot))]==core.sha(path)
   text=path.read_text()
   if 'Starting router on 0.0.0.0:8000' not in text:continue
   lines=[line for line in text.splitlines() if 'Starting router on 0.0.0.0:8000' in line]
   assert len(lines)==1 and 'prefill_policy: Some('+enum+')' in lines[0] and 'decode_policy: None' in lines[0]
   preflights=re.findall(r'ROUTER_POLICY_PREFLIGHT_PASSED (\{.*?\})',text)
   assert len(preflights)==1
   preflight=json.loads(preflights[0]);assert preflight['prefill_policy']==expected_policy and preflight['version']=='0.3.2' and enum in preflight['native_mapping']
   routing.append(dict(path=str(path),prefill_policy=expected_policy,native_preflight=preflight,main_router_initialization=lines[0],per_dispatch_decisions='NOT_COLLECTED'))
  assert len(routing)==1,'Require actual main-router native phase policy initialization'
  long_data=json.loads((run/'long-context-check.json').read_text());cases=long_data['cases'];assert len(cases)==12
  for case in cases:
   assert 'error' not in case
   text=case['response']['choices'][0]['message']['content']
   assert text==case['text'] and text.strip(' \t\n\r\"\'`.')==case['expected']
  result=dict(job=job,state='LOCAL_PROTOCOL_SLA_OUTPUT_RUNTIME_PASS' if point['latency_error_gate_pass'] else 'LOCAL_PROTOCOL_OUTPUT_RUNTIME_PASS_SLA_FAIL',point=point,long=gates['long_diagnostic'],runtime_vs_222281=proof,routing_initialization=routing,snapshot=str(snapshot),accuracy_verified=False)
  (O/(job+'-gates.json')).write_text(json.dumps(gates,indent=2)+'\n')
 except Exception as exc:
  import traceback
  traceback.print_exc()
  result=dict(job=job,state='EVIDENCE_INVALID_OR_INCOMPLETE',reason=str(exc),accuracy_verified=False)
 (O/(job+'-review.json')).write_text(json.dumps(result,indent=2)+'\n');print(job,result['state'],result.get('point',{}),result.get('reason',''),flush=True)

if all((O/(r['job']+'-review.json')).exists() for r in receipts):
 reviews={r['id']:json.loads((O/(r['job']+'-review.json')).read_text()) for r in receipts}
 ordered=[reviews[p['id']] for p in json.loads((O/'pilots.json').read_text())]
 if all(r['state']=='LOCAL_PROTOCOL_SLA_OUTPUT_RUNTIME_PASS' for r in ordered):
  control,candidate=[r['point'] for r in ordered]
  gain=100*(candidate['good_output_tokens_s']/control['good_output_tokens_s']-1)
  (O/'paired-comparison.json').write_text(json.dumps(dict(goodput_change_pct=gain,control=ordered[0]['job'],candidate=ordered[1]['job'],useful_single_pair=gain>=1,requires_independent_confirmation=True,accuracy_verified=False),indent=2)+'\n')
