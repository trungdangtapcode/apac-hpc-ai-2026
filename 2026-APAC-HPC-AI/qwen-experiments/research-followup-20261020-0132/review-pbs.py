"""Review newly recovered PBS measurements, frozen payloads and actual runtime."""
from pathlib import Path
import datetime,importlib.util,json,re
R=Path(__file__).resolve().parents[1];O=Path(__file__).resolve().parent;P=R/'nscc-pbs'
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
m=module('candidate',P/'review-candidate-sweep.py');core=module('core',R/'serving-tuning/review-n54.py')
base=P/'collected/220575.pbs111/20261016T054555388584Z';smoke=P/'collected/220562.pbs111/20261015T194718195272Z/runs/220562.pbs111/output-smoke.json'
snapshots={j:Path(json.loads((O/('collect-'+j+'.json')).read_text())['destination']) for j in ['222027','222028']}
reference=Path(json.loads((R/'research-followup-20261019-1200/collect-221827.json').read_text())['destination']);refjob='221827.pbs111';refseal=json.loads((reference/'evidence-sha256.json').read_text())
for number,name,n in [('222027','h100-hpc-n54-attention-control-55',54),('222028','h100-hpc-n54-decode-fa3-56',54)]:
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
   if number=='222028' and role=='decode-0':allowed|={'decode_attention_backend'}
   assert a['decode_attention_backend']==("'fa3'" if number=='222028' and role=='decode-0' else "'flashinfer'" if role=='decode-0' else 'None')
   assert not set(delta)-allowed,(role,delta)
   expected=False
   assert 'DYNAMIC_GRAD_MODE_PREFLIGHT_PASSED inference_mode='+str(expected) in text,(number,role,expected)
   assert a['moe_runner_backend']=="'hpc_ops'"
   if a['moe_runner_backend']=="'hpc_ops'":assert 'HPC_OPS_PREFLIGHT_PASSED' in text
   if role=='decode-0':
    assert sorted(set(map(int,re.findall(r'backend=mnnvl, rank=(\d+), world_size=8',text))))==list(range(8))
    if number=='222027':
     assert sorted(set(map(int,re.findall(r'TP(\d+) EP\d+\] Using hybrid attention backend.*decode_backend=flashinfer, prefill_backend=fa3',text))))==list(range(8))
    else:
     traces=json.loads((O/'candidate-fa3-kernels.json').read_text())
     assert sorted(x['rank'] for x in traces)==list(range(8))
     for row in traces:
      assert core.sha(Path(row['path']))==row['sha256']==seal[str(Path(row['path']).relative_to(snapshot))]
      assert any('flash::FlashAttnFwdSm90' in name for name,_ in row['attention_kernels'])
     assert a['attention_backend']=="'fa3'" and a['decode_attention_backend']=="'fa3'"

   proof[role]=delta
  long_data=json.loads((run/'long-context-check.json').read_text());cases=long_data['cases'];assert len(cases)==12
  for case in cases:
   assert 'error' not in case
   text=case['response']['choices'][0]['message']['content']
   assert text==case['text'] and text.strip(' \t\n\r\"\'`.')==case['expected']
  result=dict(job=job,state='LOCAL_PROTOCOL_SLA_OUTPUT_RUNTIME_PASS' if point['latency_error_gate_pass'] else 'LOCAL_PROTOCOL_OUTPUT_RUNTIME_PASS_SLA_FAIL',point=point,long=gates['long_diagnostic'],runtime_vs_221827=proof,snapshot=str(snapshot),accuracy_verified=False)
  (O/(job+'-gates.json')).write_text(json.dumps(gates,indent=2)+'\n')
 except Exception as exc:
  import traceback
  traceback.print_exc()
  result=dict(job=job,state='EVIDENCE_INVALID_OR_INCOMPLETE',reason=str(exc),accuracy_verified=False)
 (O/(job+'-review.json')).write_text(json.dumps(result,indent=2)+'\n');print(job,result['state'],result.get('point',{}),result.get('reason',''),flush=True)
