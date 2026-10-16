from pathlib import Path
import subprocess,json,re,fcntl,datetime,shlex
P=Path('/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs');e=P/'inspection/chain-20261016-0551UTC';e.mkdir(exist_ok=True)
helper=['bash','/home/apacsc42/workspace/vpn-rootless/vpn.sh','ssh-batch']
def remote(cmd):return subprocess.run(helper+['bash -lc '+shlex.quote(cmd)],capture_output=True,text=True,timeout=45,check=True).stdout
now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
with (P/'budget.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX)
 snapshot=remote('date -Is; qstat -u apacsc42; myprojects');(e/'pre-submit-credit-and-queue.txt').write_text(snapshot)
 assert not re.search(r'^\d+\.pbs\d+\s',snapshot,re.M),'Own PBSjobs already active; reconcile first'
 numbers=re.search(r'\|\s*SU\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)',snapshot);assert numbers
 grant,used,balance,doubt=map(float,numbers.groups());assert doubt==0
 b=json.loads((P/'nscc-budget.json').read_text());plan=json.loads((P/'continuous-plan.json').read_text());names=['h100-mnnvl-04','h100-flashinfer-05','h100-loader-prefetch-06']
 assert not b['active_pbs_jobs'] and not b['pending_reservations']
 assert used+3*1536<=b['commissioning_cap_su'] and balance-3*1536>=b['retain_project_su']
 b.update(max_gpu_jobs_pending_or_running=3,max_gpu_jobs_running=1,updated_utc=now())
 b['queue_amendment']={'user_instruction':'rồi submit nhiều vào, tận dụng thời gian giúp tôi','at':now(),'max_pending_or_running_jobs':3,'max_running_jobs':1,'enforcement':'PBS afterany chain; each job16GPU, no simultaneous allocations','total_max_new_su':4608}
 b['ledger'].update(used_su=used,balance_su=balance,in_doubt_su=doubt,source=str(e/'pre-submit-credit-and-queue.txt'))
 plan.update(max_active_gpu_jobs=3,max_running_gpu_jobs=1,queue_policy='At most3pending/running PBS jobs, strict afterany dependency chain;16GPU maximum simultaneously. User requested multiple submissions16Oct05:49UTC.')
 reservations=[]
 for name in names:
  pilot=next(v for v in plan['pilots']+plan.get('startup_pilots',[]) if v['id']==name);assert pilot['state'] in ['PREPARED_NOT_SUBMITTED','PREPARED_LOCAL_NOT_UPLOADED_NOT_SUBMITTED'],(name,pilot['state'])
  subprocess.run(['sha256sum','--check','SHA256SUMS'],cwd=P/name,stdout=subprocess.DEVNULL,check=True)
  reservations.append({'purpose':name,'state':'RESERVED_BEFORE_QSUB','max_charge_su':1536,'requested_gpus':16,'requested_walltime':'00:45:00','reserved_utc':now()})
 b['pending_reservations']=reservations;b['unallocated_commissioning_su']=b['commissioning_cap_su']-used-4608
 def save():
  b['updated_utc']=now();(P/'nscc-budget.json').write_text(json.dumps(b,indent=2)+'\n');(P/'continuous-plan.json').write_text(json.dumps(plan,indent=2)+'\n')
 save();previous=None;ids=[]
 for name,reservation in zip(names,reservations):
  dependency=(' -W depend=afterany:'+previous) if previous else ''
  cmd=f'cd /scratch/users/industry/ai-hpc/apacsc42/qwen-pbs-20261015/{name} && sha256sum --check SHA256SUMS >/dev/null && qsub{dependency} benchmark.pbs'
  reservation['dependency_afterany']=previous;reservation['submission_command']=cmd;save()
  try:
   result=remote(cmd);(e/(name+'-qsub.txt')).write_text(result)
   job=result.strip();assert re.fullmatch(r'\d+\.pbs\d+',job),result
  except Exception as exc:
   reservation.update(state='SUBMISSION_UNCERTAIN',error=str(exc));save();raise
  reservation.update(job_id=job,state='SUBMITTED',submitted_utc=now());ids.append(job)
  b['jobs'].append({'job_id':job,'state':'SUBMITTED','requested_gpus':16,'requested_walltime':'00:45:00','max_charge_su':1536,'included_in_ledger_used':False,'reservation_recorded':True,'bundle':name,'dependency_afterany':previous,'planned_ns':[32,34,36,38,40,42]})
  b['active_pbs_jobs']=ids.copy()
  pilot=next(v for v in plan['pilots']+plan.get('startup_pilots',[]) if v['id']==name);pilot.update(state='SUBMITTED',job_id=job,dependency_afterany=previous,uploaded=True)
  previous=job;save();print(name,job,'afterany',reservation['dependency_afterany'],flush=True)
 plan.update(current_job=ids[0],chain_jobs=ids,access_status='Existing authenticated VPN/SSH worked. Three independent candidate trials queued sequentially; do not duplicate.')
 b['reconciliation_note']='Baseline220575 fullprotocol/shortnonregression PASS. Reserve4608SU for three independent45minute pilots queued with afterany dependencies; max16GPU at once. Terminal artifacts retained. No new authentication.'
 save();(e/'chain.json').write_text(json.dumps({'jobs':ids,'max_charge_su':4608,'max_concurrent_gpus':16,'baseline_review':str(P/'collected/220575.pbs111/20261016T054555388584Z/review.json')},indent=2)+'\n')
print(remote('qstat -u apacsc42'))
