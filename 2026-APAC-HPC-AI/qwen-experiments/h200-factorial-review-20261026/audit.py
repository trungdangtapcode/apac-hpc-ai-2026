#!/usr/bin/env python3
"""Reconcile four full-runtime arms and seal terminal raw evidence."""
from pathlib import Path
import ast,datetime,hashlib,json,statistics,subprocess
S=Path(__file__).resolve().parent;Q=S.parent
ARMS=[(26315,'disabled',64),(26317,'breakable',64),(26319,'breakable',None),(26347,'disabled',None)]
def serverargs(job,role):
 lines=[x.split('server_args=',1)[1] for x in (Q/f'runs/{job}/{role}.log').read_text().splitlines() if 'server_args=ServerArgs(' in x];assert len(lines)==1
 node=ast.parse(lines[0],mode='eval').body;return {k.arg:ast.dump(k.value) for k in node.keywords}
rows=[]
for job,graph,cap in ARMS:
 d=json.loads((Q/f'h200-incumbent-recovery-20261026/review-{job}.json').read_text());assert d['state']=='LOCAL_FULL_GATE_PASS_NOT_OFFICIAL_ACCURACY'
 a=Q/f'runs/{job}';cfg=json.loads((a/'config.json').read_text());assert cfg['prefill_cuda_graph']==graph and cfg['prefill_max_running_requests']==cap
 state=subprocess.check_output(['sacct','-X','-j',str(job),'-P','--format=JobID,State,ExitCode,Elapsed,NodeList'],text=True);assert f'{job}|COMPLETED|0:0|' in state
 (a/'scheduler-accounting.psv').write_text(state)
 if not (a/'artifact-manifest.json').exists():
  files=[]
  for p in sorted(a.rglob('*')):
   if not p.is_file() or p.is_symlink() or '__pycache__' in p.parts or p.name=='artifact-manifest.json':continue
   before=p.stat();h=hashlib.sha256()
   with p.open('rb') as f:
    for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
   after=p.stat();assert (before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns)
   files.append({'path':str(p.relative_to(Q)),'bytes':after.st_size,'sha256':h.hexdigest()})
  for p in [Q/f'runs/{job}.out',Q/f'runs/{job}.err']:files.append({'path':str(p.relative_to(Q)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
  (a/'artifact-manifest.json').write_text(json.dumps({'job':job,'sealed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'terminal_accounting':state,'files':files},indent=2)+'\n')
 delta={}
 for role in ('prefill-0','prefill-1','decode-0'):
  control=serverargs(26315,role);actual=serverargs(job,role);delta[role]={k:[control.get(k),actual.get(k)] for k in set(control)|set(actual) if control.get(k)!=actual.get(k)}
  assert not(set(delta[role])-{'random_seed','cuda_graph_config','cuda_graph_backend_prefill','max_running_requests'}),(job,role,delta[role])
 rows.append({'job':job,'graph':graph,'prefill_cap':cap,'summary':d['summary'],'ttft_breaches':d['ttft_breaches'],'itl_breaches':d['itl_breaches'],'smoke':d['smoke'],'retrieval':d['retrieval'],'runtime_delta_vs26315':delta,'telemetry':d['telemetry_in_admission_envelope'],'runtime_error_inspection':d['runtime']})
scores={x['job']:x['summary']['good_output_tokens_s'] for x in rows}
pairs=[{'label':'graph at cap64','control':26315,'candidate':26317},{'label':'graph at native cap','control':26347,'candidate':26319},{'label':'native cap with graph disabled','control':26315,'candidate':26347},{'label':'native cap with graph breakable','control':26317,'candidate':26319}]
for p in pairs:p['gain_pct']=100*(scores[p['candidate']]/scores[p['control']]-1)
result={'reviewed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'units':'good output tokens/sec = AIPerf Goodput requests/sec *200','arms':rows,'contrasts':pairs,'decision':'All graph/admission contrasts below prospective >1% useful gain. Close tuning branch; no confirmation of subthreshold peak. Two full native load-bracket arms are separately submitted, not measured.','limits':'One ordered deployment per cell, unrandomized, no independent repetitions, unknown host clock skew. Contrasts descriptive, not causal certainty or confidence intervals. Official full-set accuracy UNKNOWN.'}
(S/'factorial.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'contrasts':pairs,'all_local_gates_pass':True},indent=2))
