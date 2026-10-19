"""Append one reserved H100 collective trial after the verified active chain."""
from pathlib import Path
import datetime,fcntl,json,re,shlex,subprocess
R=Path(__file__).resolve().parents[1];O=Path(__file__).resolve().parent;P=R/'nscc-pbs';H='/home/apacsc42/workspace/vpn-rootless/vpn.sh';REMOTE='/scratch/users/industry/ai-hpc/apacsc42/qwen-pbs-20261015';receipt=O/'pbs-receipt.json'
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(p,d):
 t=p.with_suffix('.tmp');t.write_text(json.dumps(d,indent=2)+'\n');t.replace(p)
def remote(command,stdin=None):return subprocess.run(['bash',H,'ssh-batch','bash -lc '+shlex.quote(command)],stdin=stdin,capture_output=True,timeout=60)
assert not receipt.exists();p=json.loads((O/'pbs-pilot.json').read_text());assert json.loads((O/'pbs-validation.json').read_text())['passed'];name=p['id']
with (O/'pbs-bundles.tar.gz').open('rb') as stream:r=remote('cd '+REMOTE+' && test ! -e '+name+' && tar -xzf - && cd '+name+' && sha256sum --check SHA256SUMS',stream)
(O/'pbs-upload.txt').write_bytes(r.stdout);(O/'pbs-upload.stderr').write_bytes(r.stderr);assert r.returncode==0
with (P/'budget.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX);b=json.loads((P/'nscc-budget.json').read_text());assert not b.get('uncertain_pbs_jobs')
 r=remote('qstat -u apacsc42; qstat -xf 221590.pbs111 221645.pbs111 221646.pbs111; myprojects');(O/'pbs-pre-submit.txt').write_bytes(r.stdout);(O/'pbs-pre-submit.stderr').write_bytes(r.stderr);assert r.returncode==0;s=r.stdout.decode();active={x.group(1) for x in re.finditer(r'^\s*(\d+\.pbs\d+)\s+',s,re.M)};assert active=={'221645.pbs111','221646.pbs111'}
 blocks={m.group(1):m.group(2) for m in re.finditer(r'Job Id: (\d+\.pbs\d+)\n(.*?)(?=Job Id: |Project\s*:|\Z)',s,re.S)};assert 'afterany:221645.pbs111' in re.sub(r'\n\t','',blocks['221646.pbs111'])
 mm=re.search(r'\|\s*SU\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|',s);assert mm;grant,used,balance,doubt=map(float,mm.groups());assert abs(grant-used-balance-doubt)<.01
 block=blocks['221590.pbs111'];assert re.search(r'job_state\s*=\s*F\b',block) and re.search(r'Exit_status\s*=\s*0\b',block);wall=re.search(r'resources_used.walltime\s*=\s*(\S+)',block).group(1);h,m,sec=map(int,wall.split(':'));charge=16*128*(h+m/60+sec/3600);item=next(x for x in b['jobs'] if x['job_id']=='221590.pbs111');delta=used-b['ledger']['used_su'];included=item.get('included_in_ledger_used',False)
 assert abs(delta)<.01 or (not included and abs(delta-charge)<.01),('Unexplained ledger change',delta)
 included=included or abs(delta-charge)<.01;item.update(state='F',exit_status=0,observed_walltime=wall,included_in_ledger_used=included,accounting_pending=not included,last_checked_utc=now())
 for x in b['pending_reservations']:
  if x.get('job_id')=='221590.pbs111':x.update(state='RECONCILED_IN_LEDGER' if included else 'TERMINAL_PENDING_LEDGER_CONSERVATIVE_RESERVE',last_checked_utc=now())
 outstanding=sum(x['max_charge_su'] for x in b['pending_reservations'] if x['state'] not in {'RECONCILED_IN_LEDGER','CANCELLED','RELEASED'});assert used+outstanding+1536<=b['commissioning_cap_su'];assert grant-used-outstanding-1536>=b['retain_project_su'];assert len(active)+1<=3
 b['ledger'].update(as_of=re.search(r'balance as of (\S+)',s).group(1),grant_su=grant,used_su=used,balance_su=balance,in_doubt_su=doubt,queried_utc=now(),source=str(O/'pbs-pre-submit.txt'),freshness_note='Only terminal charges reflected in Used reconciled. Balance already excludes In Doubt prepayment.')
 z=dict(purpose=name,state='SUBMISSION_IN_PROGRESS',max_charge_su=1536,requested_gpus=16,requested_walltime='00:45:00',reserved_utc=now(),dependency_afterany='221646.pbs111');b['pending_reservations'].append(z);b.update(updated_utc=now(),active_pbs_jobs=sorted(active),campaign_headroom_after_reserved_su=b['commissioning_cap_su']-used-outstanding-1536,unallocated_commissioning_su=b['commissioning_cap_su']-used-outstanding-1536);save(P/'nscc-budget.json',b);record=dict(id=name,state='SUBMISSION_IN_PROGRESS',attempted_utc=now());save(receipt,record)
 try:r=remote('cd '+REMOTE+'/'+name+' && sha256sum --check SHA256SUMS >/dev/null && qsub -W depend=afterany:221646.pbs111 benchmark.pbs')
 except Exception:
  z['state']=record['state']='SUBMISSION_UNCERTAIN';b['uncertain_pbs_jobs'].append(name);save(P/'nscc-budget.json',b);save(receipt,record);raise
 (O/'pbs-submit.stdout').write_bytes(r.stdout);(O/'pbs-submit.stderr').write_bytes(r.stderr);ids=re.findall(r'^\s*(\d+\.pbs\d+)\s*$',r.stdout.decode(),re.M)
 if r.returncode or len(ids)!=1:
  z['state']=record['state']='SUBMISSION_UNCERTAIN';b['uncertain_pbs_jobs'].append(name);save(P/'nscc-budget.json',b);save(receipt,record);raise RuntimeError('Uncertain qsub; do not retry')
 job=ids[0];record.update(job=job,state='SUBMITTED',submitted_utc=now(),dependency_afterany='221646.pbs111');z.update(job_id=job,state='SUBMITTED_PENDING_ACCOUNTING',submitted_utc=now());save(receipt,record);b['jobs'].append(dict(job_id=job,bundle=name,state='SUBMITTED',requested_gpus=16,requested_walltime='00:45:00',max_charge_su=1536,included_in_ledger_used=False,accounting_pending=True,dependency_afterany='221646.pbs111',planned_ns=[54],submitted_utc=now()));b['active_pbs_jobs'].append(job);save(P/'nscc-budget.json',b)
 path=P/'continuous-plan.json';plan=json.loads(path.read_text());plan['pilots'].append(dict(id=name,bundle=p['bundle'],job_id=job,state='H',max_su=1536,minutes=45,ns=[54],dependency_afterany='221646.pbs111',uploaded=True,payload_sha256=p['payload_sha256'],accuracy_verified=False,diagnostic_profile=True,result_state='AWAITING_BENCHMARK'));plan.update(updated_utc=now(),next_bounded_step='Review N54 repeat/N56 plus Tree-prefill N54. Verify actual profile activation; no unchanged failures or automatic load increase.');save(path,plan)
 r=remote('qstat -u apacsc42; qstat -f '+job);(O/'pbs-post-submit.txt').write_bytes(r.stdout);(O/'pbs-post-submit.stderr').write_bytes(r.stderr);assert r.returncode==0 and 'afterany:221646.pbs111' in re.sub(r'\n\t','',r.stdout.decode());print(name,job,'serial dependency verified; internal headroom',b['campaign_headroom_after_reserved_su'],flush=True)
