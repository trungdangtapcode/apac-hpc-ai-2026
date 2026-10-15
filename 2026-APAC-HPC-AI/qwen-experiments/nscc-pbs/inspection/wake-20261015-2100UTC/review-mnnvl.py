import hashlib,json,re,subprocess,datetime,math
from pathlib import Path
ROOT=Path('/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments')
OUT=Path(__file__).resolve().parent
now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
def dump(name,obj):
 with (OUT/name).open('x') as f:json.dump(obj,f,indent=2,ensure_ascii=False);f.write('\n')
def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest()
def command(name,args):
 t=now();p=subprocess.run(args,text=True,capture_output=True,timeout=35)
 (OUT/(name+'.txt')).write_text(p.stdout);(OUT/(name+'.stderr')).write_text(p.stderr)
 return {'utc':t,'argv':args,'exit_code':p.returncode,'stdout':name+'.txt','stderr':name+'.stderr'}
checks=[command('slurm-own-queue',['squeue','-u','apacsc42','-o','%.18i %.40j %.10T %.12M %.20R']),command('slurm-accounting',['sacct','-j','23778,23839,23859,23904,23905,23906,23924','--format=JobID,State,ExitCode,Elapsed,Start,End','-X']),command('watcher-process',['ps','-p','3514431','-o','pid,etime,stat,comm']),command('nscc-pbs-credit',['/home/apacsc42/workspace/vpn-rootless/vpn.sh','ssh-batch','date -u; qstat -u apacsc42; myprojects'])]
dump('live-check.json',checks)
runs=[]
for job in ['23778','23839']:
 run=ROOT/'runs'/job
 d=json.loads((run/'confirm/n52/artifacts/profile_export_aiperf.json').read_text())
 phases=d['input_config']['phases'];assert [(p['duration'],p['concurrency']) for p in phases]==[(60,52),(120,52)]
 assert phases[0]['exclude_from_results'] and phases[1]['grace_period']==30
 assert d['error_summary']==[] and not d['was_cancelled']
 avg=lambda k:d[k]['avg']
 assert math.isclose(avg('good_request_fraction'),avg('good_request_count')/avg('request_count'))
 good=avg('goodput')*200
 stored=json.loads((run/'summary.json').read_text())[0]
 assert math.isclose(good,stored['good_output_tokens_s'])
 smoke=json.loads((run/'output-smoke.json').read_text());comparison=json.loads((run/'output-baseline-comparison.json').read_text())
 failed=[c['name'] for c in smoke['cases'] if not c['passed']]
 assert failed==['reverse'] and comparison['research_eligible'] and comparison['new_failed_cases']==[]
 log=(run/'decode-0.log').read_text()
 ranks=sorted({int(x) for x in re.findall(r'backend=mnnvl, rank=(\d+), world_size=8',log)})
 assert ranks==list(range(8))
 manifest=json.loads((run/'artifact-manifest.json').read_text())
 mismatches=[e['path'] for e in manifest['files'] if sha(ROOT/e['path'])!=e['sha256']]
 assert not mismatches
 runs.append({'job':job,'good_tokens_s':good,'sla':avg('good_request_fraction'),'good_requests':avg('good_request_count'),'requests':avg('request_count'),'itl_ms':avg('inter_token_latency'),'ttft_ms':avg('time_to_first_token'),'nominal_input_tokens':4000,'observed_input_tokens_mean':avg('input_sequence_length'),'observed_output_tokens':d['output_sequence_length'],'smoke_failed_cases':failed,'mnnvl_initialized_ranks':ranks,'manifest_files_verified':len(manifest['files']),'manifest_mismatches':mismatches})
a=json.loads((ROOT/'runs/23778/config.json').read_text());b=json.loads((ROOT/'runs/23839/config.json').read_text())
diff={k:[a.get(k),b.get(k)] for k in a.keys()|b.keys() if a.get(k)!=b.get(k)}
assert set(diff)=={'experiment','purpose'}
files=['worker.sh','benchmark.sh','topology-job.sh','output-smoke.py','nixl-conn.py','warm-topology.py','placement.tsv']
payload={f:sha(ROOT/'runs/23778/submitted'/f)==sha(ROOT/'runs/23839/submitted'/f) for f in files};assert all(payload.values())
mean=sum(r['good_tokens_s'] for r in runs)/2
controls={j:json.loads((ROOT/'runs'/j/'summary.json').read_text())[0] for j in ['23607','23773']}
gate=all(r['sla']>=.95 and r['itl_ms']<=19.3 and r['good_tokens_s']>=max(2400.1830549877477,controls['23607']['good_output_tokens_s'])*1.02 for r in runs)
assert gate
review={'reviewed_utc':now(),'scope':'Independent CPU evidence audit; no new GPU submission. Runtime initialization is not a new kernel profile; two runs do not estimate all-cluster variability. Organiser accuracy unverified.','runs':runs,'mean_good_tokens_s':mean,'repeat_change_percent':(runs[1]['good_tokens_s']/runs[0]['good_tokens_s']-1)*100,'mean_gain_percent_vs':{j:(mean/c['good_output_tokens_s']-1)*100 for j,c in controls.items()},'mean_ttft_delta_ms_vs_23607':sum(r['ttft_ms'] for r in runs)/2-controls['23607']['ttft_avg_ms'],'mean_itl_delta_ms_vs_23607':sum(r['itl_ms'] for r in runs)/2-controls['23607']['itl_avg_ms'],'config_differences':diff,'identical_submitted_payload':payload,'existing_n54_gate_passes':gate,'next_job':'23924','next_job_submitted_by':'existing watcher at2026-10-15T21:00:05.820399+00:00','no_new_pbs_auth_or_qsub':True}
dump('mnnvl-repeat-review.json',review)
print(json.dumps({k:v for k,v in review.items() if k not in ['runs','config_differences','identical_submitted_payload']},indent=2))
