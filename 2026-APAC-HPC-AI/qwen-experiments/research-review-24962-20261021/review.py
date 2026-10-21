"""Seal/replay the independent H200 N62 repeat and compare exact source execution."""
from pathlib import Path
from datetime import datetime,timezone
import csv,hashlib,importlib.util,json,re,subprocess
O=Path(__file__).resolve().parent;R=O.parent;job='24962';run=R/'runs'/job
s=importlib.util.spec_from_file_location('wave',R/'serving-tuning-10/review-wave10.py');w=importlib.util.module_from_spec(s);s.loader.exec_module(w)
raw=subprocess.check_output(['sacct','-X','-j',job,'-P','--format=JobID,State%30,ExitCode,Elapsed,Start,End'],text=True);(O/'accounting.psv').write_text(raw);status=list(csv.DictReader(raw.splitlines(),delimiter='|'))[0];assert status['State']=='COMPLETED' and status['ExitCode']=='0:0'
seal=run/'artifact-manifest.json'
if not seal.exists():
 files=[p for p in run.rglob('*') if p.is_file() and p.name not in {'summary.json','artifact-manifest.json'}]+[p for p in [R/'runs'/f'{job}.out',R/'runs'/f'{job}.err'] if p.is_file()]
 seal.write_text(json.dumps(dict(job=job,sealed_utc=datetime.now(timezone.utc).isoformat(),status_at_seal=status,scope='Existing terminal artifacts inventoried after completion, summary excluded; not a submission-time seal',files=[dict(path=str(p.relative_to(R)),bytes=p.stat().st_size,sha256=w.core.sha(p)) for p in sorted(files)]),indent=2)+'\n')
point=w.core.point(R,job,62);source=w.core.point(R,'24915',62);long=w.long_check(run);assert point['metrics']['sla_pass'] and source['metrics']['sla_pass'] and long['state']=='PASSED'
assert point['normalized_protocol']==source['normalized_protocol']
unchanged=[]
for name in point['payload_files']:
 if name in ['config.json','job.sbatch']:continue
 assert (run/'submitted'/name).read_bytes()==(R/'runs/24915/submitted'/name).read_bytes(),name
 unchanged.append(name)
deltas={}
for role,args in point['server_args'].items():
 before=source['server_args'][role];delta={k:[before.get(k),args.get(k)] for k in args.keys()|before.keys() if args.get(k)!=before.get(k)};assert not set(delta)-{'random_seed'},(role,delta);deltas[role]=delta
 metrics_flag=args.get('enable_metrics');assert metrics_flag=='False',(role,metrics_flag)
log=(run/'decode-0.log').read_text();assert sorted({int(i) for i in re.findall(r'backend=mnnvl, rank=(\d+), world_size=8',log)})==list(range(8))
summary=json.loads((run/'summary.json').read_text())[0];reference=json.loads((R/'runs/24915/summary.json').read_text())[0]
runtime_errors={}
for role in ['prefill-0','prefill-1','decode-0']:
 t=(run/(role+'.log')).read_text();assert 'KV Cache is allocated. dtype: torch.bfloat16' in t
 assert not any(s in t for s in ['NIXL_ERR_','CUDA out of memory'])
 lines=t.splitlines();traces=[i for i,x in enumerate(lines) if 'Traceback (most recent call last)' in x]
 for i in traces:
  assert 'POST /stop_profile HTTP/1.1' in '\n'.join(lines[max(0,i-4):i])
  assert 'RuntimeError: Profiling is not in progress. Call /start_profile first.' in '\n'.join(lines[i:i+100])
 runtime_errors[role]=dict(post_score_stop_profile_tracebacks=len(traces),scope='Separate diagnostic stop returns500/not-in-progress; preserved and not treated as a measured request failure')
profile=run/'diagnostic-profile';tracefiles=list(profile.rglob('*.json.gz')) if profile.exists() else []
result=dict(job=job,reviewed_utc=datetime.now(timezone.utc).isoformat(),state='LOCAL_PROTOCOL_SLA_OUTPUT_PASS',point=point,source_job='24915',source_point=source,full_scored_protocol_equal=True,unchanged_execution_files=unchanged,runtime_delta=deltas,long_context=long,runtime_error_inspection=runtime_errors,summary=summary,source_summary=reference,repeat_delta_goodput_percent=(summary['good_output_tokens_s']/reference['good_output_tokens_s']-1)*100,n62_mean_good_output_tokens_s=(summary['good_output_tokens_s']+reference['good_output_tokens_s'])/2,quality_status='Official >=99% reference accuracy remains unverified; local short and retrieval diagnostics only',observability=dict(resource_monitor_enabled=False,phase_markers_collected=(run/'phase-markers.jsonl').exists(),hardware_resource_samples_collected=(run/'resource-telemetry').exists(),post_score_gpu_trace_count=len(tracefiles),scope='Frozen independent repeat preserves observer-off source; post-score profiles are not scored utilization or CPU demand'),assessment='Independent N62 serving result reproduces within0.04%; slight new individual maximum is run-to-run variation, not a new configuration gain',next_hypothesis='Bounded matched-observer N62->N64 load frontier, within dense64 graph maximum; require full local gates and retain repeats before any promotion')
(O/'REVIEW.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:result[k] for k in ['job','state','repeat_delta_goodput_percent','n62_mean_good_output_tokens_s','observability']},indent=2))
