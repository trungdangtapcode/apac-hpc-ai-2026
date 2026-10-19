"""Reserve and submit one source-supported attention trial; never retry uncertain qsub."""
from pathlib import Path
import datetime,fcntl,itertools,json,re,shlex,subprocess
R=Path(__file__).resolve().parents[1];P=R/'nscc-pbs';O=Path(__file__).resolve().parent;H='/home/apacsc42/workspace/vpn-rootless/vpn.sh';REMOTE='/scratch/users/industry/ai-hpc/apacsc42/qwen-pbs-20261015';receipts_path=O/'pbs-receipts.json'
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(p,d):
 t=p.with_suffix('.tmp');t.write_text(json.dumps(d,indent=2)+'\n');t.replace(p)
def remote(cmd,stdin=None):return subprocess.run(['bash',H,'ssh-batch','bash -lc '+shlex.quote(cmd)],stdin=stdin,capture_output=True,timeout=60)
assert not receipts_path.exists(),'Existing receipts: do not rerun'
pilots=[p for p in json.loads((O/'pilots.json').read_text()) if p['platform']=='H100'];assert len(pilots)==1
assert json.loads((O/'validation.json').read_text())['passed']
assert json.loads((R/'research-followup-20261019-1200/221827.pbs111-review.json').read_text())['state']=='LOCAL_PROTOCOL_SLA_OUTPUT_RUNTIME_PASS'
# Unique directories prevent overwriting an uploaded or previously submitted bundle.
names=[p['id'] for p in pilots];checks=' && '.join('test ! -e '+shlex.quote(name) for name in names)
with (O/'pbs-bundles.tar.gz').open('rb') as handle:
 result=remote('cd '+REMOTE+' && '+checks+' && tar -xzf - && for name in '+' '.join(names)+'; do (cd "$name" && sha256sum --check SHA256SUMS) || exit; done',handle)
(O/'pbs-upload.txt').write_bytes(result.stdout);(O/'pbs-upload.stderr').write_bytes(result.stderr);assert result.returncode==0,'Upload failed; do not submit'
with (P/'budget.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX);b=json.loads((P/'nscc-budget.json').read_text());assert not b.get('uncertain_pbs_jobs')
 result=remote('qstat -u apacsc42; qstat -xf 221589.pbs111 221590.pbs111; myprojects');(O/'pbs-pre-submit.txt').write_bytes(result.stdout);(O/'pbs-pre-submit.stderr').write_bytes(result.stderr);assert result.returncode==0;s=result.stdout.decode();active={m.group(1) for m in re.finditer(r'^\s*(\d+\.pbs\d+)\s+',s,re.M)};assert not active,'Queue changed; re-plan serialisation'
 mm=re.search(r'\|\s*SU\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|',s);assert mm;grant,used,balance,doubt=map(float,mm.groups());assert abs(grant-used-balance-doubt)<.01
 blocks={m.group(1):m.group(2) for m in re.finditer(r'Job Id: (\d+\.pbs\d+)\n(.*?)(?=Job Id: |Project\s*:|\Z)',s,re.S)}
 terminal=[]
 for job in ['221589.pbs111','221590.pbs111']:
  row=next(x for x in b['jobs'] if x['job_id']==job);block=blocks[job];assert re.search(r'job_state\s*=\s*F\b',block);assert re.search(r'Exit_status\s*=\s*0\b',block)
  wall=re.search(r'resources_used.walltime\s*=\s*(\S+)',block).group(1);h,m,sec=map(int,wall.split(':'));charge=16*128*(h+m/60+sec/3600);terminal.append((job,wall,charge,row.get('included_in_ledger_used',False)))
 unknown=[x for x in terminal if not x[3]];delta=used-b['ledger']['used_su'];possibilities=[list(seq) for size in range(len(unknown)+1) for seq in itertools.combinations(unknown,size)];matched=next((seq for seq in possibilities if abs(sum(x[2] for x in seq)-delta)<.01),None);assert matched is not None,('Unexplained ledger delta',delta);included_ids={x[0] for x in matched}
 for job,wall,charge,wasincluded in terminal:
  included=wasincluded or job in included_ids
  row=next(x for x in b['jobs'] if x['job_id']==job);row.update(state='F',exit_status=0,observed_walltime=wall,estimated_charge_su_from_allocated_walltime=charge,included_in_ledger_used=included,accounting_pending=not included,last_checked_utc=now())
  for reservation in b['pending_reservations']:
   if reservation.get('job_id')==job:reservation.update(state='RECONCILED_IN_LEDGER' if included else 'TERMINAL_PENDING_LEDGER_CONSERVATIVE_RESERVE',last_checked_utc=now(),reconciliation_source=str(O/'pbs-pre-submit.txt'))
 outstanding=sum(x['max_charge_su'] for x in b['pending_reservations'] if x['state'] not in {'RECONCILED_IN_LEDGER','CANCELLED','RELEASED'});newreserve=sum(p['max_su'] for p in pilots);assert newreserve==1536
 assert used+outstanding+newreserve<=b['commissioning_cap_su'];assert grant-used-outstanding-newreserve>=b['retain_project_su']
 b['ledger'].update(grant_su=grant,used_su=used,balance_su=balance,in_doubt_su=doubt,queried_utc=now(),source=str(O/'pbs-pre-submit.txt'),as_of=re.search(r'balance as of (\S+)',s).group(1))
 reservations=[]
 for p in pilots:
  item=dict(purpose=p['id'],state='RESERVED_NOT_SUBMITTED',max_charge_su=p['max_su'],requested_gpus=16,requested_walltime='00:45:00',reserved_utc=now());reservations.append(item);b['pending_reservations'].append(item)
 b.update(active_pbs_jobs=[],updated_utc=now(),campaign_headroom_after_reserved_su=b['commissioning_cap_su']-used-outstanding-newreserve,unallocated_commissioning_su=b['commissioning_cap_su']-used-outstanding-newreserve,reconciliation_note='Reconcile terminal charges only when reflected in Used; retain any ledger-lag maximum reserve. Reserve one fixed-N54 dense prefill-attention trial, at most 1536 SU. No budget increase.')
 save(P/'nscc-budget.json',b);receipts=[];previous=None
 for p,z in zip(pilots,reservations):
  name=p['id'];z.update(state='SUBMISSION_IN_PROGRESS',dependency_afterany=previous);save(P/'nscc-budget.json',b);record=dict(id=name,state='SUBMISSION_IN_PROGRESS',attempted_utc=now());receipts.append(record);save(receipts_path,receipts)
  try:result=remote('cd '+REMOTE+'/'+name+' && sha256sum --check SHA256SUMS >/dev/null && qsub '+('-W depend=afterany:'+previous+' ' if previous else '')+'benchmark.pbs')
  except Exception:
   z['state']=record['state']='SUBMISSION_UNCERTAIN';b['uncertain_pbs_jobs'].append(name);save(P/'nscc-budget.json',b);save(receipts_path,receipts);raise
  (O/(name+'-submit.stdout')).write_bytes(result.stdout);(O/(name+'-submit.stderr')).write_bytes(result.stderr);ids=re.findall(r'^\s*(\d+\.pbs\d+)\s*$',result.stdout.decode(),re.M)
  if result.returncode or len(ids)!=1:
   z['state']=record['state']='SUBMISSION_UNCERTAIN';b['uncertain_pbs_jobs'].append(name);save(P/'nscc-budget.json',b);save(receipts_path,receipts);raise RuntimeError('Uncertain qsub; keep reserve, do not retry')
  job=ids[0];z.update(state='SUBMITTED_PENDING_ACCOUNTING',job_id=job,submitted_utc=now());record.update(state='SUBMITTED',job=job,submitted_utc=now(),dependency_afterany=previous);save(receipts_path,receipts)
  b['jobs'].append(dict(job_id=job,bundle=name,state='SUBMITTED',requested_gpus=16,requested_walltime='00:45:00',max_charge_su=p['max_su'],included_in_ledger_used=False,accounting_pending=True,dependency_afterany=previous,planned_ns=p['planned_ns'],submitted_utc=now()));b['active_pbs_jobs'].append(job);save(P/'nscc-budget.json',b)
  path=P/'continuous-plan.json';plan=json.loads(path.read_text());plan['pilots'].append(dict(id=name,bundle=p['bundle'],job_id=job,state='H' if previous else 'Q',max_su=p['max_su'],minutes=45,ns=p['planned_ns'],dependency_afterany=previous,uploaded=True,payload_sha256=p['payload_sha256'],accuracy_verified=False,result_state='AWAITING_BENCHMARK'));plan.update(updated_utc=now(),next_bounded_step='Review each completed fixed-N54 trial as it finishes; prepare and submit the next justified distinct hypothesis during the active user-authorised research session. Losing branches do not stop all research. Keep budget and queue caps; do not repeat unchanged losses.');save(path,plan);print(name,job,flush=True);previous=job
 result=remote('qstat -u apacsc42; qstat -f '+' '.join(x['job'] for x in receipts));(O/'pbs-post-submit.txt').write_bytes(result.stdout);(O/'pbs-post-submit.stderr').write_bytes(result.stderr);assert result.returncode==0;unfold=re.sub(r'\n\t','',result.stdout.decode());assert all('afterany:'+receipts[i]['job'] in unfold for i in range(len(receipts)-1))
 print('Serial dependency verified; reserved 1536 SU; internal headroom',b['campaign_headroom_after_reserved_su'],flush=True)
