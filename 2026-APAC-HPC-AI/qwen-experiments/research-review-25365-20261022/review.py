"""Seal and validate a fresh full observed load point against its control."""
from pathlib import Path
from datetime import datetime,timezone
import collections,csv,hashlib,importlib.util,json,re,subprocess
O=Path(__file__).resolve().parent;R=O.parent;job='25365';n=62;source_job='24964';source_n=60;run=R/'runs'/job
assert job not in subprocess.check_output(['squeue','-h','-u','apacsc42','-o','%i'],text=True).split(),'Wait until allocation cleanup leaves queue'
s=importlib.util.spec_from_file_location('wave',R/'serving-tuning-10/review-wave10.py');w=importlib.util.module_from_spec(s);s.loader.exec_module(w)
raw=subprocess.check_output(['sacct','-X','-j',job,'-P','--format=JobID,State%30,ExitCode,Elapsed,Start,End'],text=True);(O/'accounting.psv').write_text(raw);status=list(csv.DictReader(raw.splitlines(),delimiter='|'))[0];assert status['State']=='COMPLETED' and status['ExitCode']=='0:0'
seal=run/'artifact-manifest.json'
if not seal.exists():
 files=[p for p in run.rglob('*') if p.is_file() and p.name not in {'summary.json','artifact-manifest.json'} and '__pycache__' not in p.parts]+[p for p in [R/'runs'/f'{job}.out',R/'runs'/f'{job}.err'] if p.is_file()]
 seal.write_text(json.dumps(dict(job=job,sealed_utc=datetime.now(timezone.utc).isoformat(),status_at_seal=status,scope='Terminal run evidence inventoried after all allocation cleanup; summary excluded',files=[dict(path=str(p.relative_to(R)),bytes=p.stat().st_size,sha256=w.core.sha(p)) for p in sorted(files)]),indent=2)+'\n')
point=w.core.point(R,job,n);source=w.core.point(R,source_job,source_n);long=w.long_check(run)
assert point['metrics']['sla_pass'] and long['state']=='PASSED';assert point['normalized_protocol']==source['normalized_protocol']
unchanged=[]
for name in point['payload_files']:
 if name in ['config.json','job.sbatch']:continue
 assert (run/'submitted'/name).read_bytes()==(R/'runs'/source_job/'submitted'/name).read_bytes(),name;unchanged.append(name)
deltas={}
for role,args in point['server_args'].items():
 before=source['server_args'][role];delta={k:[before.get(k),args.get(k)] for k in args.keys()|before.keys() if args.get(k)!=before.get(k)};assert not set(delta)-{'random_seed'},(role,delta);deltas[role]=delta
counts=collections.Counter();good=ttft_bad=itl_bad=0
for line in (run/f'confirm/n{n}/artifacts/profile_export.jsonl').read_text().splitlines():
 row=json.loads(line)
 if row['metadata']['phase_kind']!='profiling':continue
 m=row['metrics'];a=m['time_to_first_token']['value'];b=m['inter_token_latency']['value'];passed=a<=3000 and b<=20;assert m['good_request_count']['value']==int(passed);good+=passed;ttft_bad+=a>3000;itl_bad+=b>20;counts[m['output_sequence_length']['value']]+=1
summary=next(r for r in json.loads((run/'summary.json').read_text()) if r['concurrency']==n and r['phase']=='confirm')
roles={}
for role in ['prefill-0','prefill-1','decode-0']:
 t=(run/(role+'.log')).read_text();assert 'KV Cache is allocated. dtype: torch.bfloat16' in t;assert not any(x in t for x in ['NIXL_ERR_','CUDA out of memory'])
 roles[role]=dict(nixl_or_oom_errors=0,traceback_count=t.count('Traceback (most recent call last)'),scope='Score errors independently checked; diagnostic tracebacks require profile-control review')
result=dict(job=job,reviewed_utc=datetime.now(timezone.utc).isoformat(),state='LOCAL_PROTOCOL_SLA_OUTPUT_PASS',point=point,summary=summary,source_job=source_job,source_point=source,full_scored_protocol_equal=True,unchanged_execution_files=unchanged,runtime_delta=deltas,long_context=long,independent_threshold_classification=dict(good=good,total=sum(counts.values()),ttft_breaches=ttft_bad,itl_breaches=itl_bad,exported_length_histogram=dict(counts),note='Nominal requested output is200; exported lengths can vary byone; actual generated IDs not retained'),runtime_log_review=roles,quality_status='Official >=99% reference accuracy remains unverified; local smoke/retrieval only',observability=dict(resource_monitor_enabled=True,phase_markers_collected=(run/'phase-markers.jsonl').exists(),hardware_resource_samples_collected=(run/'resource-telemetry').exists(),inspection_state='COLLECTED; raw protocol/role errors inspected; phase-aligned telemetry and diagnostic profile controls reviewed separately'),source_delta_goodput_percent=(summary['good_output_tokens_s']/source['metrics']['good_tokens_s']-1)*100,next_decision='Fresh matched observed full N64 candidate25366 is in flight; compare against this full N62 control before any promotion')
(O/'REVIEW.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(job=job,state=result['state'],summary=summary,raw_counts=result['independent_threshold_classification'],long=long['state']),indent=2))
