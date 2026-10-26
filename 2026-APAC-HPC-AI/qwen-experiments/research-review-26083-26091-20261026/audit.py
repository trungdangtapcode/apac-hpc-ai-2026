#!/usr/bin/env python3
"""Independent review of routing/fusion screens and retained legacy runtime drift."""
from pathlib import Path
import ast,datetime,importlib.util,json,subprocess,sys
Q=Path(__file__).resolve().parents[1];OUT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('prior',Q/'research-review-26064-26068-20261025/audit-results.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
records=[]
for job in (26083,26085,26089,26091):
 a=Q/'runs'/str(job);b=a/'submitted-payload'
 result=m.audit(job);result['slurm_accounting']=subprocess.check_output(['sacct','-X','-j',str(job),'--format=JobID,State,ExitCode,Elapsed,NodeList','-n'],text=True)
 result['slurm_state']='FAILED' if job==26085 else 'COMPLETED'
 result['state']='RAW_PROFILE_VALID_SLA_GATE_FAILED' if job==26085 else 'LOCAL_SHORT_GATE_PASS'
 # Run the actual frozen head checker; do not turn a failing SLA into PASS.
 replay=subprocess.run([sys.executable,'-B',str(b/'check-performance.py'),str(a)],capture_output=True,text=True)
 result['actual_checker_replay']={'returncode':replay.returncode,'stdout':replay.stdout,'stderr':replay.stderr}
 assert (replay.returncode==0)==(job!=26085)
 # Prior audit's boundary is the outer client window (warmup+profiling+grace), not just profiling.
 result['telemetry']['limits']='Five-second samples bounded by outer benchmark_start/end, INCLUDING WARMUP, profiling and grace. Not exact profiling-only evidence. Role gauges are rank-local, host CPU counted once. No causal bottleneck proof; absent data is not zero.'
 result['telemetry']['window']='OUTER_CLIENT_ENVELOPE_NOT_PROFILING_ONLY'
 result['telemetry']['warmup_seconds']=20
 result['transport_log_scan']={}
 for role in ('prefill-0','prefill-1','decode-0'):
  lines=(a/f'{role}.log').read_text(errors='replace').splitlines()
  matches=[l[:500] for l in lines if any(s in l for s in ('Traceback (most recent call last)','KVTransferError','NIXL transport error','CUDA out of memory','Unexpected transfer worker error'))]
  result['transport_log_scan'][role]={'selected_matches':len(matches),'lines':matches[:8],'scope':'Bounded selected-pattern scan; not universal health proof.'}
 records.append(result)
control=records[0]['summary']['good_output_tokens_s']
for r in records:r['delta_good_tokens_vs_fresh_control_pct']=100*(r['summary']['good_output_tokens_s']/control-1)

def args(job,role):
 line=next(l.split('server_args=',1)[1] for l in (Q/f'runs/{job}/{role}.log').read_text().splitlines() if 'server_args=ServerArgs(' in l)
 node=ast.parse(line,mode='eval').body
 return {k.arg:k.value for k in node.keywords}
changes={}
for role in ('prefill-0','prefill-1','decode-0'):
 old,new=args(25487,role),args(26083,role);delta={}
 for key in set(old)|set(new):
  if ast.dump(old.get(key,ast.Constant(None)))==ast.dump(new.get(key,ast.Constant(None))):continue
  if key=='cuda_graph_config':
   def graph(n):return {k.arg:{a.arg:ast.literal_eval(a.value) for a in k.value.keywords if a.arg=='backend'} for k in n.keywords}
   delta[key]={'legacy':graph(old[key]),'modern':graph(new[key])}
  else:delta[key]={'legacy':ast.unparse(old[key]),'modern':ast.unparse(new[key])}
 changes[role]=delta
report={'reviewed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'jobs':records,'runtime_difference_25487_vs_26083':changes,'correction':'Protocol duration is NOT the only difference. Legacy prefill uses breakable CUDA graphs and max_running_requests=None; modern prefill explicitly disables those graphs and caps64. Model dtype is auto vs explicit bfloat16 but actual old KV allocations were BF16. Random server seeds differ; client seed2026 is fixed. Short-vs-full score gap cannot be causally attributed without controlled full comparisons.','decisions':{'routing':'Close H200 default power_of_two; SLA fails and goodput lower.','fusion':'Close prefill-only/decode-only arms; +0.48%/+0.27% below prospective3% gate. No unchanged full confirmation.','next':'Investigate incumbent preservation and prefill graph/admission drift using controlled full protocol. Retain3044.400475 historical mean; no newly measured frontier.','official_accuracy':'UNKNOWN'}}
(OUT/'inspection.json').write_text(json.dumps(report,indent=2)+'\n')
for r in records:print(r['job_id'],round(r['summary']['good_output_tokens_s'],3),round(r['delta_good_tokens_vs_fresh_control_pct'],3),r['scoreable_local_screen'])
print(json.dumps(changes,indent=2))
