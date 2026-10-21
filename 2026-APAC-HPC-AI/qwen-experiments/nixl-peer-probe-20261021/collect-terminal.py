"""Seal only redacted probe run artifacts; never capture private peer exchange."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,importlib.util,json,re,shlex,subprocess,tarfile
O=Path(__file__).resolve().parent;receipt=json.loads((O/'pbs-receipt.json').read_text());job=receipt['job'];number=job.split('.')[0];root='/scratch/users/industry/ai-hpc/apacsc42/qwen-pbs-20261015/'+O.name;helper='/home/apacsc42/workspace/vpn-rootless/vpn.sh'
def remote(command,stream=None):return subprocess.run(['bash',helper,'ssh-batch','bash -lc '+shlex.quote(command)],stdout=stream if stream else subprocess.PIPE,stderr=subprocess.PIPE,timeout=120)
q=remote('qstat -xf '+job);assert q.returncode==0;account=q.stdout.decode();assert re.search(r'Job_Owner\s*=\s*apacsc42@',account);state=re.search(r'job_state\s*=\s*(\S+)',account)[1]
if state!='F':print('NOT_TERMINAL',job,state);raise SystemExit(0)
D=O/'collected'/job;assert not D.exists(),'Never overwrite sealed evidence';D.mkdir(parents=True);(D/'pbs-accounting.txt').write_text(account)
with (D/'raw-artifacts.tar.gz').open('wb') as stream:
 c=remote('cd '+root+' && files=(runs/'+job+'); for f in ./*.o'+number+' ./*.e'+number+'; do if [[ -f "$f" ]]; then files+=("$f"); fi; done; tar -czf - "${files[@]}"',stream)
assert c.returncode==0
with tarfile.open(D/'raw-artifacts.tar.gz') as t:
 members=t.getmembers();assert all(not Path(m.name).is_absolute() and '..' not in Path(m.name).parts and (m.isfile() or m.isdir()) for m in members);t.extractall(D,members=members,filter='data')
run=D/'runs'/job;r=subprocess.run(['sha256sum','--check','SHA256SUMS'],cwd=run/'submitted',capture_output=True,text=True);(D/'payload-checksums.txt').write_text(r.stdout+r.stderr);assert r.returncode==0
exit_status=int(re.search(r'Exit_status\s*=\s*(-?\d+)',account)[1]);rankpaths=[run/('rank'+str(rank)+'-result.json') for rank in range(2)];rows=[json.loads(p.read_text()) if p.exists() else None for p in rankpaths]
s=importlib.util.spec_from_file_location('probe',(run/'submitted/probe.py'));module=importlib.util.module_from_spec(s);s.loader.exec_module(module)
valid,reason=module.result_rows_valid(*rows) if all(rows) else (False,'Missing rank result(s)')
final=json.loads((run/'final.json').read_text()) if (run/'final.json').exists() else None
passed=exit_status==0 and valid and bool(final and final['status']=='pass')
h,m,seconds=map(int,re.search(r'resources_used.walltime\s*=\s*(\d+):(\d+):(\d+)',account).groups());wall=h*3600+m*60+seconds
seal={str(p.relative_to(D)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(D.rglob('*')) if p.is_file()};(D/'evidence-sha256.json').write_text(json.dumps(seal,indent=2)+'\n')
result=dict(job=job,collected_utc=datetime.now(timezone.utc).isoformat(),state='BASE_NIXL_VRAM_PASS' if passed else 'BASE_NIXL_VRAM_FAILED_REVIEW_REQUIRED',exit_status=exit_status,payload_and_raw_hashes_verified=True,semantic_replayed_without_raw_mutation=True,semantic_passed=passed,semantic_reason=reason,rank_results=rows,walltime_s=wall,estimated_allocated_charge_su=wall*2*128/3600,official_accuracy_verified=False,ranked_performance_measured=False,model_loaded=False,private_peer_exchange_collected=False,scope='Two selected H100s on actual recorded nodes; a base peer/VRAM pass does not validate SGLang hetero KV or EAGLE3 and may use a different pair from 223055',hardware_telemetry='No utilization/power/memory sampling; device identity and transfer/checksum evidence only')
(O/'collection.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='rank_results'},indent=2))
