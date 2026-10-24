"""Upload and submit one frozen full-H100 correctness candidate after observer qualification under the AI lock."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,fcntl,hashlib,json,re,shlex,subprocess
O=Path(__file__).resolve().parent;P=O.parent/'nscc-pbs'
REMOTE='/scratch/users/industry/ai-hpc/apacsc42/qwen-pbs-20261015/'+O.name
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--control-socket',required=True);args=parser.parse_args()
SSH=['ssh','-F','/dev/null','-S',args.control_socket,'-o','ControlMaster=no','-o','BatchMode=yes','-o','ConnectTimeout=5','apacsc42@aspire2p.nscc.sg']
def remote(command,source=None):return subprocess.run(SSH+['bash -lc '+shlex.quote(command)],stdin=source,capture_output=True,timeout=90)
def now():return datetime.now(timezone.utc).isoformat()
def save(path,data):
 temp=path.with_suffix('.tmp');temp.write_text(json.dumps(data,indent=2)+'\n');temp.replace(path)
receipt=O/'pbs-receipt.json';assert not receipt.exists(),'Never retry an existing or uncertain qsub attempt'
assert json.loads((O/'ROOT_REVIEW.json').read_text())['ready_for_bounded_probe']
subprocess.run(['sha256sum','--check','SHA256SUMS'],cwd=O,check=True,capture_output=True)
subprocess.run(['ssh','-F','/dev/null','-S',args.control_socket,'-O','check','apacsc42@aspire2p.nscc.sg'],check=True,capture_output=True,timeout=10)
with (O/'payload.tar.gz').open('rb') as source:
 result=remote('test ! -e '+shlex.quote(REMOTE)+' && mkdir '+shlex.quote(REMOTE)+' && tar -xzf - -C '+shlex.quote(REMOTE)+' && cd '+shlex.quote(REMOTE)+' && sha256sum --check SHA256SUMS && python3 -c '+shlex.quote("from pathlib import Path; import json; p=Path('/scratch/users/industry/ai-hpc/apacsc42/qwen-assets/sglang-harbor.sqsh'); assert p.is_file() and p.stat().st_size==26476240896; print(json.dumps({'serving_image_size_checked':True,'large_image_not_freshly_rehashed':True,'models_loaded':False}))"),source)
(O/'upload.stdout').write_bytes(result.stdout);(O/'upload.stderr').write_bytes(result.stderr);assert result.returncode==0,'Inspect failed upload/preflight; no reservation or qsub was attempted'
with (O.parent.parent/'hpc-experiments/nscc-cpu-timing-probe-20261021/cpu-budget.lock').open('a') as shared_lock, (P/'budget.lock').open('a') as lock:
 fcntl.flock(shared_lock,fcntl.LOCK_EX)
 cpu=subprocess.run(['bash',str(O.parent.parent/'hpc-experiments/tools/nscc-cpu-ssh.sh'),"bash -lc 'qselect -u apacsc42'"],capture_output=True,text=True,timeout=30,check=True)
 (O/'cpu-pre-submit.txt').write_text(cpu.stdout)
 cpu_jobs=[x for x in cpu.stdout.splitlines() if x.strip()]
 assert len(cpu_jobs)+1<=3,'Combined PBS cap; preserve CPU queue'
 fcntl.flock(lock,fcntl.LOCK_EX);b=json.loads((P/'nscc-budget.json').read_text());assert b['project']=='59010042' and b['commissioning_cap_su']==64000 and b['retain_project_su']==0 and not b['uncertain_pbs_jobs']
 code='''import subprocess,json
rows=[]
for argv in [['qselect','-u','apacsc42','-P','59010042'],['myprojects']]:
 r=subprocess.run(argv,capture_output=True,text=True);text=r.stdout
 if argv==['myprojects']:
  lines=[];selected=False
  for line in text.splitlines():
   if 'Project 59010042 balance as of' in line:selected=True
   elif selected and ('Usage breakdown' in line or (line.startswith('Project ') and '59010042' not in line)):selected=False
   if selected:lines.append(line)
  text='\\n'.join(lines)+'\\n'
 rows.append(dict(argv=argv,returncode=r.returncode,stdout=text,stderr=r.stderr))
print(json.dumps(rows))
'''
 result=remote('python3 -c '+shlex.quote(code));(O/'pre-submit.stdout').write_bytes(result.stdout);(O/'pre-submit.stderr').write_bytes(result.stderr);assert result.returncode==0
 rows=json.loads(result.stdout);assert all(x['returncode']==0 for x in rows)
 ai_jobs=rows[0]['stdout'].split();assert not ai_jobs,'Unexpected AI queue; review before admission'
 assert len(cpu_jobs)+len(ai_jobs)+1<=3,'Combined PBS cap'

 text=re.sub(r'(?<![\d.])-0\.000(?=\s*\|)','0.000',rows[1]['stdout']);match=re.search(r'\|\s*SU\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)',text);assert match
 grant,used,balance,doubt=map(float,match.groups());assert abs(grant-used-balance-doubt)<.01
 assert used>=b['ledger']['used_su'] and grant==64000, 'Unexpected grant/accounting regression'
 # Preserve all outstanding maxima even if a new charge has posted; no double subtraction is released without reconciliation.
 b['ledger']['used_su']=used
 excluded={'RECONCILED_IN_LEDGER','CANCELLED','RELEASED'};pending=[x for x in b['pending_reservations'] if x['state'] not in excluded];assert not any(x['purpose']==O.name for x in pending)
 outstanding=sum(x['max_charge_su'] for x in pending);maximum=5*128*17/60
 assert used+outstanding+maximum<=b['commissioning_cap_su'] and grant-used-outstanding-maximum>=b['retain_project_su']
 row=dict(purpose=O.name,state='SUBMISSION_IN_PROGRESS',max_charge_su=maximum,requested_gpus=5,requested_walltime='00:17:00',reserved_utc=now())
 b['pending_reservations'].append(row);b['ledger'].update(balance_su=balance,in_doubt_su=doubt,queried_utc=now(),source=str(O/'pre-submit.stdout'),as_of=re.search(r'balance as of (\S+)',text).group(1))
 b.update(updated_utc=now(),campaign_headroom_after_reserved_su=b['commissioning_cap_su']-used-outstanding-maximum,unallocated_commissioning_su=b['commissioning_cap_su']-used-outstanding-maximum)
 record=dict(state='SUBMISSION_IN_PROGRESS',attempted_utc=now(),bundle=O.name,kind='qwen_unified_five_rank_local_output_qualification',requested_gpus=5,minutes=17,max_su=maximum,explicit_generation_client=True,full_pd=False,scored_benchmark=False,root_manifest_sha256=hashlib.sha256((O/'SHA256SUMS').read_bytes()).hexdigest())
 save(receipt,record);save(P/'nscc-budget.json',b)
 try:result=remote('cd '+shlex.quote(REMOTE)+' && sha256sum --check SHA256SUMS >/dev/null && qsub benchmark.pbs')
 except Exception:
  record['state']=row['state']='SUBMISSION_UNCERTAIN';b['uncertain_pbs_jobs'].append(O.name);save(receipt,record);save(P/'nscc-budget.json',b);raise
 (O/'submit.stdout').write_bytes(result.stdout);(O/'submit.stderr').write_bytes(result.stderr);ids=re.findall(r'^\s*(\d+\.pbs\d+)\s*$',result.stdout.decode(),re.M)
 if result.returncode or len(ids)!=1:
  record['state']=row['state']='SUBMISSION_UNCERTAIN';b['uncertain_pbs_jobs'].append(O.name);save(receipt,record);save(P/'nscc-budget.json',b);raise RuntimeError('Uncertain submission: inspect scheduler; never retry blindly')
 job=ids[0];record.update(job=job,state='SUBMITTED',submitted_utc=now());row.update(job_id=job,state='SUBMITTED_PENDING_ACCOUNTING',submitted_utc=record['submitted_utc'])
 b['jobs'].append(dict(job_id=job,bundle=O.name,kind=record['kind'],state='SUBMITTED',requested_gpus=5,requested_walltime='00:17:00',max_charge_su=maximum,included_in_ledger_used=False,accounting_pending=True,submitted_utc=record['submitted_utc']))
 b['active_pbs_jobs']=sorted(set(ai_jobs+[job]));save(receipt,record);save(P/'nscc-budget.json',b)
 result=remote('qstat -f '+shlex.quote(job));(O/'post-submit.stdout').write_bytes(result.stdout);(O/'post-submit.stderr').write_bytes(result.stderr)
 print(job,'five H100 / at most 17 minutes / maximum',maximum,'SU / remaining internal headroom',b['campaign_headroom_after_reserved_su'])
