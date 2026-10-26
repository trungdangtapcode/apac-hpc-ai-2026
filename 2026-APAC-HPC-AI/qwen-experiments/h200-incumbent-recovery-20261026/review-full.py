#!/usr/bin/env python3
"""Offline recovery audit; requires terminal job, raw fixed workload and output evidence."""
from pathlib import Path
import ast,datetime,hashlib,importlib.util,json,re,subprocess,sys
S=Path(__file__).resolve().parent;Q=S.parent

def module(path,name):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def resolved(job,role):
 text=(Q/f'runs/{job}/{role}.log').read_text(errors='replace');rows=[line.split('server_args=',1)[1] for line in text.splitlines() if 'server_args=ServerArgs(' in line];assert len(rows)==1
 node=ast.parse(rows[0],mode='eval').body;assert isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id=='ServerArgs'
 return {k.arg:ast.dump(k.value,include_attributes=False) for k in node.keywords},text

def gate_module():
 p=Q/'serving-tuning-11/s70-h200-full-pgraph-disabled-cap64/performance_gates.py';source=p.read_text()
 # Audit accepts either documented legacy [64] or modern64; does not alter submitted gate.
 old="assert json.loads((art/'config.json').read_text())['concurrency']==n, 'bundle concurrency differs from expected workload'"
 new="assert json.loads((art/'config.json').read_text())['concurrency'] in (n,[n]), 'bundle concurrency differs from expected workload'"
 assert old in source;source=source.replace(old,new)
 source=source.replace("phase=json.loads((art/'config.json').read_text())['benchmark_phase']","cfg=json.loads((art/'config.json').read_text()); phase=cfg.get('benchmark_phase',cfg.get('phase'))")
 result={'__name__':'offline_full_gate','__file__':str(p)};exec(compile(source,str(p),'exec'),result);return result

def review(job):
 a=Q/'runs'/str(job)
 state=subprocess.check_output(['sacct','-X','-j',str(job),'-P','--format=JobID,State,ExitCode,Elapsed,NodeList'],text=True)
 raw=[line.split('|') for line in state.splitlines()];status=[dict(zip(raw[0],row)) for row in raw[1:] if row[0]==str(job)];assert len(status)==1
 assert status[0]['State']=='COMPLETED' and status[0]['ExitCode']=='0:0','Not terminal successful; preserve failure independently instead'
 live=subprocess.check_output(['squeue','-h','-u','apacsc42','-o','%i'],text=True).split();assert str(job) not in live,'Allocation cleanup still live'
 legacy=(a/'submitted').is_dir();b=a/('submitted' if legacy else 'submitted-payload');cfg=json.loads((a/'config.json').read_text());assert cfg==json.loads((b/'config.json').read_text())
 subprocess.run(['sha256sum','-c','SHA256SUMS'],cwd=b,stdout=subprocess.DEVNULL,check=True)
 gates=gate_module();expected=json.loads((Q/'serving-tuning-11/s70-h200-full-pgraph-disabled-cap64/expected-input-config.json').read_text());profile=gates['check_aiperf'](a,expected)
 smoke=gates['check_smoke'](a,Q/'serving-tuning-11/s65-h200-router-rr-control/reference-output-smoke.json');retrieval=gates['check_retrieval'](a)
 runtime={}
 for role in ('prefill-0','prefill-1','decode-0'):
  actual,text=resolved(job,role)
  selected=[line[:500] for line in text.splitlines() if any(x in line for x in ('KVTransferError','NIXL transport error','CUDA out of memory','Unexpected transfer worker error'))]
  runtime[role]={'selected_transport_error_lines':selected,'traceback_count':text.count('Traceback (most recent call last)'),'traceback_scope':'Legacy post-score profile-stop HTTP500 is separate; inspect timing, never call blanket error-free.'}
  if legacy:
   previous,_=resolved(25487,role);delta={k:[previous.get(k),actual.get(k)] for k in set(previous)|set(actual) if previous.get(k)!=actual.get(k)};runtime[role]['delta_vs_legacy_25487']=delta
   assert not (set(delta)-{'random_seed'}),(role,delta)
  else:
   replay=subprocess.run([sys.executable,'-B',str(b/'check-performance.py'),str(a)],capture_output=True,text=True);assert replay.returncode==0,replay.stdout+replay.stderr
 if legacy:
  parent=Q/'runs/25487/submitted'
  identical=[]
  for p in parent.iterdir():
   if p.is_file() and p.name not in ('config.json','job.sbatch','SHA256SUMS'):
    assert p.read_bytes()==(b/p.name).read_bytes(),p.name;identical.append(p.name)
  warm=(a/'pair-warmup.log').read_text();assert 'ALL 2 P/D paths initialized' in warm
 else:identical=None
 export=json.loads((a/'confirm/n64/artifacts/profile_export_aiperf.json').read_text());raw_requests=[]
 for line in (a/'confirm/n64/artifacts/profile_export.jsonl').open():
  r=json.loads(line)
  if r['metadata']['benchmark_phase']=='profiling':raw_requests.append(r)
 ttft_bad=sum(r['metrics']['time_to_first_token']['value']>3000 for r in raw_requests);itl_bad=sum(r['metrics']['inter_token_latency']['value']>20 for r in raw_requests)
 prior=module(Q/'research-review-26064-26068-20261025/audit-results.py','telemetry_helper')
 lo=min(r['metadata']['request_start_ns'] for r in raw_requests);hi=max(r['metadata']['request_start_ns'] for r in raw_requests)
 telemetry=prior.telemetry(a,lo,hi);telemetry['limits']='Inside first-to-last profiling-request START envelope; excludes warmup/final drain but is not exact phase-clock coverage. Five-second sparse samples, rank-local gauges, uncalibrated host skew. Not FLOPS or causal proof.'
 result={'reviewed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'job':job,'state':'LOCAL_FULL_GATE_PASS_NOT_OFFICIAL_ACCURACY','scheduler':status[0],'legacy':legacy,'raw_fixed_workload':profile,'smoke':smoke,'retrieval':retrieval,'runtime':runtime,'legacy_operational_files_identical':identical,'ttft_breaches':ttft_bad,'itl_breaches':itl_bad,'summary':next(r for r in json.loads((a/'summary.json').read_text()) if r['phase']=='confirm' and r['concurrency']==64),'telemetry_in_admission_envelope':telemetry,'official_accuracy':'UNKNOWN','new_best_or_promotion':False,'limits':'Terminal gate review is one run. No automatic score promotion or causal attribution. Request IDs not retained as actual generated model token IDs.'}
 return result

if __name__=='__main__':
 job=int(sys.argv[1]);result=review(job);target=S/f'review-{job}.json';assert not target.exists(),'Preserve prior review; choose separate revised report if needed';target.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'job':job,'state':result['state'],'good_output_tokens_s':result['raw_fixed_workload']['good_output_tokens_per_second'],'review':str(target)}))
