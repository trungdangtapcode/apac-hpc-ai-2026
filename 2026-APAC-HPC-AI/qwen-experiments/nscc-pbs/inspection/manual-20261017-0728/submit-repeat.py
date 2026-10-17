from pathlib import Path
import json,subprocess,shlex,re,fcntl,datetime
P=Path('/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs');O=P/'inspection/manual-20261017-0728';HELP='/home/apacsc42/workspace/vpn-rootless/vpn.sh';name='h100-combo-load-repeat-15'
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def remote(cmd):return subprocess.run(['bash',HELP,'ssh-batch','bash -lc '+shlex.quote(cmd)],capture_output=True,text=True,timeout=60)
def save(b):
 p=P/'nscc-budget.json';t=p.with_suffix('.pending.tmp');t.write_text(json.dumps(b,indent=2)+'\n');t.replace(p)
with (P/'budget.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX);b=json.loads((P/'nscc-budget.json').read_text());assert not b.get('uncertain_pbs_jobs')
 q=remote('qstat -u apacsc42; qstat -xf 221051.pbs111; qstat -xf 221052.pbs111; myprojects');(O/'repeat-pre-submit.txt').write_text(q.stdout);(O/'repeat-pre-submit.stderr').write_text(q.stderr);assert q.returncode==0
 assert len(set(re.findall(r'^\s*(\d+\.pbs\d+)\s+apacsc42',q.stdout,re.M)))<3
 blocks=re.split(r'Job Id: ',q.stdout);mid=next(x for x in blocks if x.startswith('221051.pbs111'));parent=next(x for x in blocks if x.startswith('221052.pbs111'))
 assert re.search(r'job_state\s*=\s*F\b',mid) and re.search(r'Exit_status\s*=\s*0\b',mid) and '00:25:45' in mid
 assert re.search(r'job_state\s*=\s*(R|Q|H|F)\b',parent)
 m=re.search(r'\|\s*SU\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|',q.stdout);assert m
 grant,used,balance,doubt=map(float,m.groups());delta=used-12487.681;charge=(25*60+45)/3600*16*128
 assert abs(delta)<.002 or abs(delta-charge)<.002,'Additional ledger charges need reconciliation'
 accounted=abs(delta-charge)<.002;unposted=0 if accounted else 878.934
 newreserve=1365.334;remaining=16384-used-unposted-1536-newreserve
 assert remaining>=0 and balance-unposted-1536-newreserve>=13000
 for j in b['jobs']:
  if j['job_id']=='221051.pbs111':j.update(state='F',exit_status=0,observed_walltime='00:25:45',included_in_ledger_used=accounted,accounting_pending=not accounted,estimated_charge_su_from_allocated_walltime=878.934,last_checked_utc=now())
 for x in b['pending_reservations']:
  if x.get('job_id')=='221051.pbs111':x.update(state='RECONCILED_IN_LEDGER' if accounted else 'TERMINAL_CHARGE_PENDING',conservative_outstanding_su=unposted,terminal_accounting_verified_utc=now())
 b['ledger'].update(used_su=used,balance_su=balance,in_doubt_su=doubt,queried_utc=now(),source=str(O/'repeat-pre-submit.txt'))
 reservation=dict(purpose=name,state='RESERVED_NOT_SUBMITTED',max_charge_su=newreserve,requested_gpus=16,requested_walltime='00:40:00',reserved_utc=now(),dependency_afterany='221052.pbs111');b['pending_reservations'].append(reservation);b.update(updated_utc=now(),campaign_headroom_after_reserved_su=remaining,unallocated_commissioning_su=remaining);save(b)
 cmd='cd /scratch/users/industry/ai-hpc/apacsc42/qwen-pbs-20261015/'+name+' && sha256sum --check SHA256SUMS >/dev/null && qsub -W depend=afterany:221052.pbs111 benchmark.pbs'
 reservation.update(state='SUBMISSION_IN_PROGRESS',submission_command=cmd);save(b)
 try:r=remote(cmd)
 except Exception:
  reservation['state']='SUBMISSION_UNCERTAIN';b['uncertain_pbs_jobs'].append(name);save(b);raise
 (O/'repeat-submit.stdout').write_text(r.stdout);(O/'repeat-submit.stderr').write_text(r.stderr);ids=re.findall(r'^\s*(\d+\.pbs\d+)\s*$',r.stdout,re.M)
 if r.returncode or len(ids)!=1:
  reservation['state']='SUBMISSION_UNCERTAIN';b['uncertain_pbs_jobs'].append(name);save(b);raise RuntimeError('Submission uncertain,no retry')
 job=ids[0];reservation.update(state='SUBMITTED_PENDING_ACCOUNTING',job_id=job,submitted_utc=now());b['jobs'].append(dict(job_id=job,state='SUBMITTED',requested_gpus=16,requested_walltime='00:40:00',max_charge_su=newreserve,included_in_ledger_used=False,reservation_recorded=True,bundle=name,dependency_afterany='221052.pbs111',planned_ns=[48,50,52],accounting_pending=True,submitted_utc=now()));b['active_pbs_jobs']=['221052.pbs111',job];save(b)
 r=remote('qstat -u apacsc42; qstat -f '+job);(O/'repeat-post-submit.txt').write_text(r.stdout);assert r.returncode==0 and 'afterany:221052.pbs111' in re.sub(r'\n\t','',r.stdout)
 b.update(active_pbs_jobs_verified=True,updated_utc=now());save(b);print('Submitted',job,'verified afterany221052; conservativecampaignheadroom',remaining)
