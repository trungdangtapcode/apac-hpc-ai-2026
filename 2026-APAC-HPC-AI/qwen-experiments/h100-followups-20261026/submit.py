#!/usr/bin/env python3
"""Explicit two-job admission with CPU-before-AI locks and conservative SU maxima."""
from pathlib import Path
import contextlib,datetime,fcntl,hashlib,json,re,shlex,subprocess
S=Path(__file__).resolve().parent;Q=S.parent
VPN='/home/apacsc42/workspace/vpn-rootless/vpn.sh'
CPU=Q.parent/'hpc-experiments/tools/nscc-cpu-ssh.sh'
REMOTE='/scratch/users/industry/ai-hpc/apacsc42/qwen-pbs-20261015'
BUDGET=Q/'nscc-pbs/nscc-budget.json'
PLANS=[('h100-incumbent-n54-refresh-20261026',16,30),('eagle3-h100-equal-tp-observer-r2-20261026',8,20)]
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(p,d):
 t=p.with_suffix(p.suffix+'.tmp');t.write_text(json.dumps(d,indent=2)+'\n');t.replace(p)
def remote(cmd,data=None):
 return subprocess.run(['bash',VPN,'ssh-batch','bash -lc '+shlex.quote(cmd)],input=data,capture_output=True,timeout=150)
def checked(cmd,data=None):
 r=remote(cmd,data);assert r.returncode==0,(r.returncode,r.stderr.decode(errors='replace'));return r.stdout.decode()
def snapshot():
 code="""import json,subprocess
out={}
for key,argv in [('hostname',['hostname']),('ai_jobs',['qselect','-u','apacsc42','-P','59010042']),('credit',['myprojects'])]:
 r=subprocess.run(argv,capture_output=True,text=True,timeout=40)
 assert r.returncode==0,(key,r.returncode,r.stderr)
 text=r.stdout
 if key=='credit':
  lines=[];capture=False
  for line in text.splitlines():
   if 'Project 59010042 balance as of' in line:capture=True
   elif capture and ('Usage breakdown' in line or (line.startswith('Project ') and '59010042' not in line)):capture=False
   if capture:lines.append(line)
  text='\\n'.join(lines)
 out[key]=text
print(json.dumps(out))
"""
 d=json.loads(checked('python3 -c '+shlex.quote(code)));assert 'a2ap-login' in d['hostname']
 r=subprocess.run(['bash',str(CPU),"bash -lc 'hostname; qselect -u apacsc42'"],capture_output=True,text=True,timeout=150)
 assert r.returncode==0,'CPU queue not established; no admission'
 cpu=re.findall(r'^\d+\.pbs\d+\s*$',r.stdout,re.M);ai=d['ai_jobs'].split()
 assert len(cpu)==len(set(cpu)) and all(re.fullmatch(r'\d+\.pbs\d+',x) for x in ai)
 # Establish a real CPU login response, not an empty gateway output.
 assert 'login' in r.stdout.lower() and len(r.stdout.strip().splitlines())>=1
 d.update(cpu_queue=r.stdout,cpu_jobs=[x.strip() for x in cpu],ai_job_ids=ai,checked_utc=now())
 return d
receipt=S/'submission-receipts.json'
existing=json.loads(receipt.read_text()) if receipt.exists() else None
assert existing is None or (not existing['jobs'] and len(existing['uploads'])==2),'Existing qsub attempt: inspect rather than retry'
assert json.loads((S/'verification.json').read_text())['state']=='CPU_PREFLIGHT_PASS_NOT_GPU_ACCEPTANCE'
receipts=existing or {'created_utc':now(),'jobs':[],'uploads':[]};save(receipt,receipts)
for name,gpus,minutes in ([] if existing else PLANS):
 b=Q/name;subprocess.run(['sha256sum','-c','SHA256SUMS'],cwd=b,check=True,stdout=subprocess.DEVNULL)
 dest=REMOTE+'/'+name
 # Atomic directory creation rejects overwrite; uncertain upload is never blindly repeated.
 out=checked('test ! -e '+shlex.quote(dest)+' && mkdir '+shlex.quote(dest)+' && tar -xzf - -C '+shlex.quote(dest)+' && cd '+shlex.quote(dest)+' && sha256sum -c SHA256SUMS', (b/'payload.tar.gz').read_bytes())
 receipts['uploads'].append({'bundle':name,'remote':dest,'manifest_sha256':hashlib.sha256((b/'SHA256SUMS').read_bytes()).hexdigest(),'verified_files':len(out.splitlines()),'utc':now()});save(receipt,receipts)
if existing:
 for upload in receipts['uploads']:
  out=checked('cd '+shlex.quote(upload['remote'])+' && sha256sum -c SHA256SUMS')
  assert len(out.splitlines())==upload['verified_files']
 receipts['resumed_before_any_qsub_utc']=now();save(receipt,receipts)
last=None
for name,gpus,minutes in PLANS:
 with contextlib.ExitStack() as stack:
  for p in [Q.parent/'hpc-experiments/nscc-cpu-timing-probe-20261021/cpu-budget.lock',Q/'nscc-pbs/budget.lock']:
   f=stack.enter_context(p.open('a'));fcntl.flock(f,fcntl.LOCK_EX)
  snap=snapshot();save(S/('pre-admission-'+name+'.json'),snap)
  assert len(snap['cpu_jobs'])+len(snap['ai_job_ids'])+1<=3,'Combined PBS cap full'
  assert not snap['ai_job_ids'] or (last and set(snap['ai_job_ids'])<={last}),'Unserialized existing AI allocation'
  nums=re.search(r'\| SU\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)',snap['credit']);assert nums,'No selected credit row'
  grant,used,balance,doubt=map(float,nums.groups());budget=json.loads(BUDGET.read_text())
  assert grant==64000 and budget['commissioning_cap_su']==64000 and not budget.get('uncertain_pbs_jobs')
  outstanding=sum(float(x['max_charge_su']) for x in budget['pending_reservations'] if x['state']!='RECONCILED_IN_LEDGER')
  charge=gpus*128*minutes/60;headroom=min(balance,grant-used-doubt)-outstanding
  assert headroom>=charge,(headroom,charge)
  reserve={'purpose':name,'state':'SUBMISSION_IN_PROGRESS','max_charge_su':charge,'requested_gpus':gpus,'requested_walltime':f'00:{minutes:02d}:00','reserved_utc':now(),'dependency_afterany':last}
  budget['pending_reservations'].append(reserve)
  budget['ledger'].update(grant_su=grant,used_su=used,balance_su=balance,in_doubt_su=doubt,queried_utc=snap['checked_utc'],source=str(S/('pre-admission-'+name+'.json')),freshness_note='Fresh before admission; old unreconciled maximum reservations retained.')
  budget['updated_utc']=now();budget['campaign_headroom_after_reserved_su']=headroom-charge;budget['unallocated_commissioning_su']=headroom-charge;save(BUDGET,budget)
  cmd='cd '+shlex.quote(REMOTE+'/'+name)+' && qsub '+('-W depend=afterany:'+last+' ' if last else '')+'benchmark.pbs'
  entry={'bundle':name,'command':cmd,'max_charge_su':charge,'attempt_utc':now(),'state':'SUBMISSION_IN_PROGRESS'};receipts['jobs'].append(entry);save(receipt,receipts)
  try:r=remote(cmd)
  except BaseException:
   reserve['state']='SUBMISSION_UNCERTAIN';save(BUDGET,budget);raise
  entry.update(returncode=r.returncode,stdout=r.stdout.decode(),stderr=r.stderr.decode(),returned_utc=now());save(receipt,receipts)
  match=re.fullmatch(r'\s*(\d+\.pbs\d+)\s*',entry['stdout'])
  if r.returncode!=0 or not match:
   reserve['state']='SUBMISSION_UNCERTAIN';entry['state']='SUBMISSION_UNCERTAIN';save(BUDGET,budget);save(receipt,receipts);raise RuntimeError('Submission outcome not confirmed; preserve reservation and inspect')
  job=match[1];reserve.update(state='SUBMITTED_PENDING_ACCOUNTING',job_id=job,submitted_utc=now());entry.update(state='SUBMITTED',job_id=job,dependency_afterany=last)
  budget['jobs'].append({'job_id':job,'bundle':name,'state':'SUBMITTED','requested_gpus':gpus,'requested_walltime':reserve['requested_walltime'],'max_charge_su':charge,'accounting_pending':True,'included_in_ledger_used':False,'submitted_utc':now(),'dependency_afterany':last})
  budget['active_pbs_jobs']=snap['ai_job_ids']+[job];budget['active_pbs_jobs_verified']=budget['active_pbs_jobs'];budget['next_baseline_reserved']=True
  save(BUDGET,budget);save(receipt,receipts);last=job
  print('Submitted',job,name,'max SU',charge,flush=True)
receipts['post_submit']=snapshot();save(receipt,receipts)
print('Both jobs submitted; no automatic resubmission or schedule installed.')
