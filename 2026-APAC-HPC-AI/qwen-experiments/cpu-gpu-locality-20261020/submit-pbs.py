"""Reserve and submit one static probe after the current model candidate."""
from pathlib import Path
import datetime,fcntl,itertools,json,re,shlex,subprocess,tarfile
R=Path(__file__).resolve().parents[1];O=Path(__file__).resolve().parent;P=R/'nscc-pbs';REMOTE='/scratch/users/industry/ai-hpc/apacsc42/qwen-pbs-20261015';HELPER='/home/apacsc42/workspace/vpn-rootless/vpn.sh';receipt=O/'pbs-receipt.json'
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(path,value):path.write_text(json.dumps(value,indent=2)+'\n')
def remote(cmd,stdin=None):return subprocess.run(['bash',HELPER,'ssh-batch','bash -lc '+shlex.quote(cmd)],stdin=stdin,capture_output=True,timeout=60)
assert not receipt.exists(),'Never retry an existing or uncertain submission'
assert json.loads((O/'validation.json').read_text())['passed']
assert json.loads((R/'startup-prefetch-20261020/222407.pbs111-review.json').read_text())['state']=='LOCAL_PROTOCOL_SLA_OUTPUT_RUNTIME_PASS'
with tarfile.open(O/'payload.tar.gz','w:gz') as t:
 for name in ['collect-topology.py','topology.pbs','SHA256SUMS']:t.add(O/name,arcname=O.name+'/'+name)
with (O/'payload.tar.gz').open('rb') as f:z=remote('cd '+REMOTE+' && test ! -e '+O.name+' && tar -xzf - && cd '+O.name+' && sha256sum --check SHA256SUMS',f)
(O/'upload.txt').write_bytes(z.stdout);(O/'upload.stderr').write_bytes(z.stderr);assert z.returncode==0,'No qsub after failed upload'
with (P/'budget.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX);b=json.loads((P/'nscc-budget.json').read_text());assert not b['uncertain_pbs_jobs']
 z=remote('qstat -u apacsc42; qstat -xf 222407.pbs111 222408.pbs111; myprojects');(O/'pre-submit.txt').write_bytes(z.stdout);(O/'pre-submit.stderr').write_bytes(z.stderr);assert z.returncode==0;s=z.stdout.decode();active=re.findall(r'^\s*(\d+\.pbs\d+)\s+',s,re.M);assert len(active)+1<=3
 m=re.search(r'\|\s*SU\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)',s);assert m;grant,used,balance,doubt=map(float,m.groups());assert abs(grant-used-balance-doubt)<.01
 terminal={};states={}
 for block in s.split('Job Id: ')[1:]:
  job=block.splitlines()[0].strip();state=re.search(r'^\s*job_state\s*=\s*(\S+)',block,re.M);assert state;states[job]=state[1]
  if state[1]=='F':
   h,m,sec=map(int,re.search(r'resources_used.walltime\s*=\s*(\d+):(\d+):(\d+)',block).groups());terminal[job]=(h*3600+m*60+sec)*16*128/3600
 unposted=[j['job_id'] for j in b['jobs'] if j.get('job_id') in terminal and not j.get('included_in_ledger_used')];delta=used-b['ledger']['used_su'];matches=[subset for n in range(len(unposted)+1) for subset in itertools.combinations(unposted,n) if abs(sum(terminal[j] for j in subset)-delta)<.002];assert len(matches)==1,('Unexplained published delta',delta,terminal)
 reconciled=set(matches[0]);save(O/'reconciliation.json',dict(published_delta_su=delta,terminal_estimates_su=terminal,reconciled_jobs=sorted(reconciled),scope='Allocated cost accounting only, not candidate quality/performance acceptance'))
 for j in b['jobs']:
  job=j.get('job_id')
  if job in states:j.update(state=states[job],last_checked_utc=now())
  if job in terminal:j['estimated_charge_su']=terminal[job]
  if job in reconciled:j.update(included_in_ledger_used=True,accounting_pending=False)
 for j in b['pending_reservations']:
  if j.get('job_id') in reconciled:j.update(state='RECONCILED_IN_LEDGER',reconciliation_source=str(O/'pre-submit.txt'),last_checked_utc=now())
 outstanding=sum(j['max_charge_su'] for j in b['pending_reservations'] if j['state'] not in {'RECONCILED_IN_LEDGER','CANCELLED','RELEASED'});reserve=6.4;assert used+outstanding+reserve<=b['commissioning_cap_su'];assert grant-used-outstanding-reserve>=b['retain_project_su']
 b['ledger'].update(used_su=used,balance_su=balance,in_doubt_su=doubt,as_of=re.search('balance as of (\\S+)',s).group(1),queried_utc=now(),source=str(O/'pre-submit.txt'),freshness_note='Fresh project ledger; any posted prefetch charge reconciled exactly before small static probe. Outstanding maxima retained; Balance already excludes In Doubt.')
 res=dict(purpose=O.name,state='RESERVED_NOT_SUBMITTED',max_charge_su=reserve,requested_gpus=1,requested_walltime='00:03:00',reserved_utc=now());b['pending_reservations'].append(res);b.update(active_pbs_jobs=active,updated_utc=now(),unallocated_commissioning_su=b['commissioning_cap_su']-used-outstanding-reserve,campaign_headroom_after_reserved_su=b['commissioning_cap_su']-used-outstanding-reserve);save(P/'nscc-budget.json',b)
 rec=dict(state='SUBMISSION_IN_PROGRESS',attempted_utc=now(),bundle=O.name,kind='static_hardware_diagnostic',model_loaded=False,max_su=reserve,dependency_afterany='222408.pbs111');save(receipt,rec);res['state']='SUBMISSION_IN_PROGRESS';save(P/'nscc-budget.json',b)
 try:z=remote('cd '+REMOTE+'/'+O.name+' && sha256sum --check SHA256SUMS >/dev/null && qsub -W depend=afterany:222408.pbs111 topology.pbs')
 except Exception:rec['state']=res['state']='SUBMISSION_UNCERTAIN';b['uncertain_pbs_jobs'].append(O.name);save(receipt,rec);save(P/'nscc-budget.json',b);raise
 (O/'submit.stdout').write_bytes(z.stdout);(O/'submit.stderr').write_bytes(z.stderr);ids=re.findall(r'^\s*(\d+\.pbs\d+)\s*$',z.stdout.decode(),re.M)
 if z.returncode or len(ids)!=1:rec['state']=res['state']='SUBMISSION_UNCERTAIN';b['uncertain_pbs_jobs'].append(O.name);save(receipt,rec);save(P/'nscc-budget.json',b);raise RuntimeError('Uncertain qsub; never retry')
 job=ids[0];rec.update(state='SUBMITTED',job=job,submitted_utc=now());save(receipt,rec);res.update(state='SUBMITTED_PENDING_ACCOUNTING',job_id=job,submitted_utc=rec['submitted_utc']);b['jobs'].append(dict(job_id=job,bundle=O.name,kind='static_hardware_diagnostic',state='SUBMITTED',requested_gpus=1,requested_walltime='00:03:00',max_charge_su=reserve,included_in_ledger_used=False,accounting_pending=True,dependency_afterany='222408.pbs111',submitted_utc=rec['submitted_utc']));b['active_pbs_jobs'].append(job);b['reconciliation_note']='Static locality probe max6.4SU after current model candidate; existing unposted/running reservations retained. No full-model affinity change.';save(P/'nscc-budget.json',b)
 p=P/'continuous-plan.json';d=json.loads(p.read_text());assert not any(x['id']==O.name for x in d['pilots']);d['pilots'].append(dict(id=O.name,job_id=job,state='H',kind='static_hardware_diagnostic',model_loaded=False,minutes=3,max_su=6.4,requested_gpus=1,dependency_afterany='222408.pbs111',result_state='AWAITING_STATIC_TOPOLOGY'));d['updated_utc']=now;save(p,d)
 z=remote('qstat -f '+job);(O/'post-submit.txt').write_bytes(z.stdout);(O/'post-submit.stderr').write_bytes(z.stderr);assert z.returncode==0 and 'afterany:222408.pbs111' in z.stdout.decode();print(job,'max6.4SU, headroom',b['campaign_headroom_after_reserved_su'])
