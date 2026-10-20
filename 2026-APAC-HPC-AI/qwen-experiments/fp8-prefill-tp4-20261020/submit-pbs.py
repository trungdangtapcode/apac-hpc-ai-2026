"""Submit exactly one bounded native FP8 kernel screen after fresh accounting gates."""
from pathlib import Path
import datetime,fcntl,itertools,json,re,shlex,subprocess
R=Path(__file__).resolve().parents[1];O=Path(__file__).resolve().parent;P=R/'nscc-pbs';REMOTE='/scratch/users/industry/ai-hpc/apacsc42/qwen-pbs-20261015';HELPER='/home/apacsc42/workspace/vpn-rootless/vpn.sh';receipt=O/'pbs-receipts.json'
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(p,d):
 t=p.with_suffix('.tmp');t.write_text(json.dumps(d,indent=2)+'\n');t.replace(p)
def remote(cmd,stdin=None):return subprocess.run(['bash',HELPER,'ssh-batch','bash -lc '+shlex.quote(cmd)],stdin=stdin,capture_output=True,timeout=60)
assert not receipt.exists(),'Never repeat an existing or uncertain qsub'
assert json.loads((O/'validation.json').read_text())['passed']
assert json.loads((R/'fp8-privatehome-20261020/222242.pbs111-review.json').read_text())['state']=='ISOLATED_KERNEL_NUMERICAL_TIMING_PASS'
for j in ['222178','222179']:assert json.loads((R/'research-followup-20261020-0647'/(j+'.pbs111-review.json')).read_text())['state']=='LOCAL_PROTOCOL_SLA_OUTPUT_RUNTIME_PASS'
pilot=json.loads((O/'pilot.json').read_text());name=pilot['id'];reserve=8*128*10/60;assert pilot['requested_gpus']==8 and pilot['minutes']==10 and abs(pilot['max_su']-reserve)<1e-8
with (O/'pbs-bundles.tar.gz').open('rb') as f:z=remote('cd '+REMOTE+' && test ! -e '+shlex.quote(name)+' && tar -xzf - && cd '+shlex.quote(name)+' && sha256sum --check SHA256SUMS',f)
(O/'pbs-upload.txt').write_bytes(z.stdout);(O/'pbs-upload.stderr').write_bytes(z.stderr);assert z.returncode==0
with (P/'budget.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX);path=P/'nscc-budget.json';b=json.loads(path.read_text());assert not b['uncertain_pbs_jobs']
 z=remote('qstat -u apacsc42; qstat -xf 222232.pbs111 222242.pbs111; myprojects');(O/'pbs-pre-submit.txt').write_bytes(z.stdout);(O/'pbs-pre-submit.stderr').write_bytes(z.stderr);assert z.returncode==0;s=z.stdout.decode();assert not re.findall(r'^\s*\d+\.pbs\d+\s+',s,re.M),'Own queue is no longer empty'
 m=re.search(r'\|\s*SU\s*\|\s*(-?[\d.]+)\s*\|\s*(-?[\d.]+)\s*\|\s*(-?[\d.]+)\s*\|\s*(-?[\d.]+)\s*\|',s);assert m;grant,used,balance,doubt=map(float,m.groups());assert abs(grant-used-balance-doubt)<.01
 blocks={}
 for block in re.split(r'(?=Job Id:)',s):
  hit=re.search(r'Job Id:\s*(\d+\.pbs\d+)',block)
  if hit:blocks[hit.group(1)]=re.sub(r'\n\t','',block)
 failed=[]
 for job_id in ['222232.pbs111','222242.pbs111']:
  block=blocks[job_id]
  assert re.search(r'job_state\s*=\s*F\b',block) and re.search(r'Exit_status\s*=\s*'+('0' if job_id=='222242.pbs111' else '1')+r'\b',block)
  assert re.search(r'Job_Owner\s*=\s*apacsc42@',block)
  wall=re.search(r'resources_used.walltime\s*=\s*(\S+)',block).group(1)
  hours,minutes,seconds=map(int,wall.split(':'));charge=8*128*(hours+minutes/60+seconds/3600)
  prior=next(v for v in b['jobs'] if v['job_id']==job_id)
  failed.append(dict(job_id=job_id,walltime=wall,charge_su=charge,already_included=prior.get('included_in_ledger_used',False)))
 delta=used-b['ledger']['used_su'];unposted=[x for x in failed if not x['already_included']]
 matches=[subset for n in range(len(unposted)+1) for subset in itertools.combinations(unposted,n) if abs(sum(x['charge_su'] for x in subset)-delta)<.01]
 assert len(matches)==1,('Unexplained or ambiguous ledger delta',delta,failed)
 reconciled={x['job_id'] for x in matches[0]}
 for x in failed:
  included=x['already_included'] or x['job_id'] in reconciled
  prior=next(v for v in b['jobs'] if v['job_id']==x['job_id'])
  prior.update(state='F',exit_status=0 if x['job_id']=='222242.pbs111' else 1,observed_walltime=x['walltime'],estimated_charge_su_from_allocated_walltime=x['charge_su'],included_in_ledger_used=included,accounting_pending=not included,last_checked_utc=now())
  for q in b['pending_reservations']:
   if q.get('job_id')==x['job_id']:q.update(state='RECONCILED_IN_LEDGER' if included else 'TERMINAL_PENDING_LEDGER_CONSERVATIVE_RESERVE',last_checked_utc=now())
  x['final_charge_reconciled']=included
 save(O/'failed-accounting.json',dict(jobs=failed,published_delta_su=delta,rule='Only the unique matching subset is reconciled; retain all other maximum reservations.'))
 outstanding=sum(q['max_charge_su'] for q in b['pending_reservations'] if q['state'] not in {'RECONCILED_IN_LEDGER','CANCELLED','RELEASED'})
 assert outstanding<=2*170.666667+.01
 assert used+outstanding+reserve<=b['commissioning_cap_su'] and grant-used-outstanding-reserve>=b['retain_project_su']
 b['ledger'].update(as_of=re.search(r'balance as of (\S+)',s).group(1),grant_su=grant,used_su=used,balance_su=balance,in_doubt_su=doubt,queried_utc=now(),source=str(O/'pbs-pre-submit.txt'),freshness_note='Failed micro charges matched as a unique subset; unposted maxima retained conservatively.')
 q=dict(purpose=name,state='RESERVED_NOT_SUBMITTED',max_charge_su=reserve,requested_gpus=8,requested_walltime='00:10:00',reserved_utc=now());b['pending_reservations'].append(q);b.update(active_pbs_jobs=[],updated_utc=now(),campaign_headroom_after_reserved_su=b['commissioning_cap_su']-used-outstanding-reserve,unallocated_commissioning_su=b['commissioning_cap_su']-used-outstanding-reserve);save(path,b)
 record=dict(id=name,state='SUBMISSION_IN_PROGRESS',attempted_utc=now());q['state']='SUBMISSION_IN_PROGRESS';save(receipt,[record]);save(path,b)
 try:z=remote('cd '+REMOTE+'/'+name+' && sha256sum --check SHA256SUMS >/dev/null && qsub benchmark.pbs')
 except Exception:
  q['state']=record['state']='SUBMISSION_UNCERTAIN';b['uncertain_pbs_jobs'].append(name);save(receipt,[record]);save(path,b);raise
 (O/'pbs-submit.stdout').write_bytes(z.stdout);(O/'pbs-submit.stderr').write_bytes(z.stderr);ids=re.findall(r'^\s*(\d+\.pbs\d+)\s*$',z.stdout.decode(),re.M)
 if z.returncode or len(ids)!=1:
  q['state']=record['state']='SUBMISSION_UNCERTAIN';b['uncertain_pbs_jobs'].append(name);save(receipt,[record]);save(path,b);raise RuntimeError('Uncertain qsub; no retry')
 job=ids[0];record.update(job=job,state='SUBMITTED',submitted_utc=now());q.update(job_id=job,state='SUBMITTED_PENDING_ACCOUNTING',submitted_utc=now());save(receipt,[record]);b['jobs'].append(dict(job_id=job,bundle=name,state='SUBMITTED',requested_gpus=8,requested_walltime='00:10:00',max_charge_su=reserve,included_in_ledger_used=False,accounting_pending=True,kind='isolated_microbenchmark',model_loaded=False,submitted_utc=now()));b['active_pbs_jobs']=[job];save(path,b)
 p=P/'continuous-plan.json';d=json.loads(p.read_text());assert not any(v['id']==name for v in d['pilots']);d['pilots'].append(dict(id=name,bundle=pilot['bundle'],job_id=job,state='Q',kind='isolated_microbenchmark',requested_gpus=8,max_su=reserve,minutes=10,ns=[],uploaded=True,payload_sha256=pilot['payload_sha256'],model_loaded=False,result_state='AWAITING_MICROBENCH_NOT_MODEL_SCORE',accuracy_verified=False));d.update(updated_utc=now(),next_bounded_step='Review all eight ranks, exact source guard, numerical/input checks, representative shapes, graph timing and actual kernels before any full-model pair.');save(p,d)
 z=remote('qstat -u apacsc42; qstat -f '+job);(O/'pbs-post-submit.txt').write_bytes(z.stdout);(O/'pbs-post-submit.stderr').write_bytes(z.stderr);assert z.returncode==0 and 'select = 1:ngpus=8:mpiprocs=1' in z.stdout.decode();print(job,'reserved_su',reserve,'headroom_su',b['campaign_headroom_after_reserved_su'],flush=True)
