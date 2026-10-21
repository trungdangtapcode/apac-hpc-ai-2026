"""Seal only the completed owned EAGLE3 component gate; never infer model correctness."""
from pathlib import Path
import datetime,hashlib,json,re,shlex,subprocess,tarfile
O=Path(__file__).resolve().parent;rec=json.loads((O/'pbs-receipt.json').read_text());job=rec['job'];number=job.split('.')[0];helper='/home/apacsc42/workspace/vpn-rootless/vpn.sh';remote_root='/scratch/users/industry/ai-hpc/apacsc42/qwen-pbs-20261015/'+O.name

def remote(cmd,stream=None):
 return subprocess.run(['bash',helper,'ssh-batch','bash -lc '+shlex.quote(cmd)],stdout=stream if stream else subprocess.PIPE,stderr=subprocess.PIPE,timeout=120)

z=remote('qstat -xf '+job);assert z.returncode==0;account=z.stdout.decode();state=re.search(r'job_state\s*=\s*(\S+)',account)[1]
assert re.search(r'Job_Owner\s*=\s*apacsc42@',account)
if state!='F':print('NOT_TERMINAL',job,state);raise SystemExit(0)
D=O/'collected'/job;assert not D.exists(),'Existing sealed capture; do not overwrite';D.mkdir(parents=True);(D/'pbs-accounting.txt').write_text(account)
with (D/'raw-artifacts.tar.gz').open('wb') as out:
 z=remote('cd '+remote_root+' && files=(runs/'+job+'); for f in *.o'+number+' *.e'+number+'; do if [[ -f "$f" ]]; then files+=("$f"); fi; done; tar -czf - "${files[@]}"',out)
assert z.returncode==0
with tarfile.open(D/'raw-artifacts.tar.gz') as archive:
 members=archive.getmembers()
 assert all(not Path(m.name).is_absolute() and '..' not in Path(m.name).parts and (m.isfile() or m.isdir()) for m in members)
 archive.extractall(D,members=members,filter='data')
run=D/'runs'/job;z=subprocess.run(['sha256sum','--check','SHA256SUMS'],cwd=run/'submitted',capture_output=True,text=True);(D/'payload-checksums.txt').write_text(z.stdout+z.stderr);assert z.returncode==0
seal={str(p.relative_to(D)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(D.rglob('*')) if p.is_file()};(D/'evidence-sha256.json').write_text(json.dumps(seal,indent=2)+'\n')
exit_status=int(re.search(r'Exit_status\s*=\s*(-?\d+)',account)[1]);report=dict(job=job,terminal=True,exit_status=exit_status,destination=str(D),payload_hashes_passed=True,model_loaded=False,performance_measured=False)
gateway=run/'gateway/gateway-echo.json';component=run/'component.json'
report.update(scope='Native gateway with synthetic workers plus draft metadata/tensor checks; no target inference or PD transfer',gateway=json.loads(gateway.read_text()) if gateway.exists() else None,component=json.loads(component.read_text()) if component.exists() else None)
if exit_status==0:
 assert report['gateway']['passed'] and report['component']['passed']
 report['state']='COMPONENT_PASS_FULL_INTEGRATION_UNVERIFIED'
else:report['state']='COMPONENT_FAILED_REVIEW_REQUIRED'
(O/'collection.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
