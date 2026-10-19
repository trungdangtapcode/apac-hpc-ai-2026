"""Review newly recovered PBS measurements, frozen payloads and actual runtime."""
from pathlib import Path
import ast,copy,datetime,importlib.util,json,re
R=Path(__file__).resolve().parents[1];O=Path(__file__).resolve().parent;P=R/'nscc-pbs'
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
m=module('candidate',P/'review-candidate-sweep.py');core=module('core',R/'serving-tuning/review-n54.py')

# Reproduce derived graph buckets from the exact inspected runtime source.
args_source=O/'runtime-attention-source/sgl-workspace/sglang/python/sglang/srt/server_args.py'
args_hashes=json.loads((O/'runtime-attention-source-sha256.json').read_text())
assert core.sha(args_source)==args_hashes[str(args_source.relative_to(O))]
source_ast=ast.parse(args_source.read_text())
fn=copy.deepcopy(next(x for x in ast.walk(source_ast) if isinstance(x,ast.FunctionDef) and x.name=='_generate_prefill_cuda_graph_batch_sizes'))
fn.decorator_list=[];namespace={};exec(compile(ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[])),str(args_source),'exec'),namespace)
def graph_without_derived_prefill(value,chunk):
 node=ast.parse(value,mode='eval');assert isinstance(node.body,ast.Call) and isinstance(node.body.func,ast.Name) and node.body.func.id=='CudaGraphConfig'
 fields={x.arg:x for x in node.body.keywords};prefill=fields['prefill'].value
 assert isinstance(prefill,ast.Call) and isinstance(prefill.func,ast.Name) and prefill.func.id=='PhaseConfig'
 pf={x.arg:x for x in prefill.keywords}
 assert ast.literal_eval(pf['max_bs'].value)==chunk
 assert ast.literal_eval(pf['bs'].value)==namespace['_generate_prefill_cuda_graph_batch_sizes'](None,chunk)
 prefill.keywords=[x for x in prefill.keywords if x.arg not in {'max_bs','bs'}]
 return ast.dump(node,include_attributes=False)
base=P/'collected/220575.pbs111/20261016T054555388584Z';smoke=P/'collected/220562.pbs111/20261015T194718195272Z/runs/220562.pbs111/output-smoke.json'
receipts=json.loads((O/'pbs-receipts.json').read_text())
specs=[(x['job'].split('.')[0],x['id'],54) for x in receipts]
snapshots={j:Path(json.loads((O/('collect-'+j+'.json')).read_text())['destination']) for j,_,_ in specs if (O/('collect-'+j+'.json')).exists()}
reference=Path(json.loads((R/'status-review-20261019-1111/collect-221645.json').read_text())['destination']);refjob='221645.pbs111';refseal=json.loads((reference/'evidence-sha256.json').read_text())
for number,name,n in specs:
 if number not in snapshots:
  print(number,'NOT_COLLECTED: inspect scheduler before collecting',flush=True);continue
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
   if name=='h100-hpc-chunk6144-n54-43' and role.startswith('prefill'):
    allowed.add('chunked_prefill_size');assert delta.get('chunked_prefill_size')==['4096','6144'],delta
    assert graph_without_derived_prefill(b['cuda_graph_config'],4096)==graph_without_derived_prefill(a['cuda_graph_config'],6144)
    allowed.add('cuda_graph_config')
   if name=='h100-hpc-prefill-simple-n54-44':
    if role.startswith('prefill'):assert 'PREFILL_NCCL_PROTO=allreduce:Simple' in text
    else:assert 'PREFILL_NCCL_PROTO=' not in text
   assert not set(delta)-allowed,(role,delta)
   assert a['moe_runner_backend']=="'hpc_ops'"
   if a['moe_runner_backend']=="'hpc_ops'":assert 'HPC_OPS_PREFLIGHT_PASSED' in text
   if role=='decode-0':
    for pattern in [r'backend=mnnvl, rank=(\d+), world_size=8',r'TP(\d+) EP\d+\] Using hybrid attention backend.*decode_backend=flashinfer, prefill_backend=fa3']:assert sorted(set(map(int,re.findall(pattern,text))))==list(range(8))
   proof[role]=delta
  long_data=json.loads((run/'long-context-check.json').read_text());cases=long_data['cases'];assert len(cases)==12
  for case in cases:
   assert 'error' not in case
   text=case['response']['choices'][0]['message']['content']
   assert text==case['text'] and text.strip(' \t\n\r\"\'`.')==case['expected']
  result=dict(job=job,state='LOCAL_PROTOCOL_SLA_OUTPUT_RUNTIME_PASS' if point['latency_error_gate_pass'] else 'LOCAL_PROTOCOL_OUTPUT_RUNTIME_PASS_SLA_FAIL',point=point,long=gates['long_diagnostic'],runtime_vs_221645=proof,snapshot=str(snapshot),accuracy_verified=False)
  (O/(job+'-gates.json')).write_text(json.dumps(gates,indent=2)+'\n')
 except Exception as exc:result=dict(job=job,state='EVIDENCE_INVALID_OR_INCOMPLETE',reason=str(exc),accuracy_verified=False)
 (O/(job+'-review.json')).write_text(json.dumps(result,indent=2)+'\n');print(job,result['state'],result.get('point',{}),result.get('reason',''),flush=True)
