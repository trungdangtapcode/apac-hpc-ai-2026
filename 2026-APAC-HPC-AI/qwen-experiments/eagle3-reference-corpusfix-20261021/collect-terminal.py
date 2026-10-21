"""Seal the owned real target-only token gate; no scored acceptance inferred."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shlex
import subprocess
import tarfile

O=Path(__file__).resolve().parent
receipt=json.loads((O/'pbs-receipt.json').read_text())
job=receipt['job'];number=job.split('.')[0]
root='/scratch/users/industry/ai-hpc/apacsc42/qwen-pbs-20261015'
helper='/home/apacsc42/workspace/vpn-rootless/vpn.sh'

def remote(command, stream=None):
    return subprocess.run(['bash',helper,'ssh-batch','bash -lc '+shlex.quote(command)],
                          stdout=stream if stream else subprocess.PIPE,
                          stderr=subprocess.PIPE,timeout=120)

query=remote('qstat -xf '+job);assert query.returncode==0
account=query.stdout.decode();assert re.search(r'Job_Owner\s*=\s*apacsc42@',account)
state=re.search(r'job_state\s*=\s*(\S+)',account)[1]
if state!='F':
    print('NOT_TERMINAL',job,state);raise SystemExit(0)
D=O/'collected'/job
assert not D.exists(), 'Do not overwrite sealed evidence'
D.mkdir(parents=True);(D/'pbs-accounting.txt').write_text(account)
with (D/'raw-artifacts.tar.gz').open('wb') as stream:
    command='cd '+root+' && files=(runs/'+job+'); for f in '+O.name+'/*.o'+number+' '+O.name+'/*.e'+number+'; do if [[ -f "$f" ]]; then files+=("$f"); fi; done; tar -czf - "${files[@]}"'
    copy=remote(command,stream)
assert copy.returncode==0
with tarfile.open(D/'raw-artifacts.tar.gz') as archive:
    members=archive.getmembers()
    assert all(not Path(m.name).is_absolute() and '..' not in Path(m.name).parts and (m.isfile() or m.isdir()) for m in members)
    archive.extractall(D,members=members,filter='data')
run=D/'runs'/job
check=subprocess.run(['sha256sum','--check','SHA256SUMS'],cwd=run/'submitted',capture_output=True,text=True)
(D/'payload-checksums.txt').write_text(check.stdout+check.stderr);assert check.returncode==0
seal={str(p.relative_to(D)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(D.rglob('*')) if p.is_file()}
(D/'evidence-sha256.json').write_text(json.dumps(seal,indent=2)+'\n')
exit_status=int(re.search(r'Exit_status\s*=\s*(-?\d+)',account)[1])
path=run/'token-control.json';token=json.loads(path.read_text()) if path.exists() else None
passed=exit_status==0 and bool(token and token.get('passed'))
result=dict(job=job,collected_utc=datetime.now(timezone.utc).isoformat(),terminal=True,
            exit_status=exit_status,payload_hashes_passed=True,destination=str(D),
            token_reference_passed=passed,token_control=token,
            state='TOKEN_REFERENCE_PASS_AWAITING_RUNTIME_REVIEW' if passed else 'TOKEN_REFERENCE_FAILED_REVIEW_REQUIRED',
            scope='Real target-only PD ID completeness and repeat stability; inspect runtime/resource/transport evidence separately',
            speculative_inference_tested=False,ranked_performance_measured=False,organiser_accuracy_verified=False)
(O/'collection.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='token_control'},indent=2))
