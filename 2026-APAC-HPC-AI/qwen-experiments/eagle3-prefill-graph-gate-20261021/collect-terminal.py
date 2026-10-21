"""Seal the owned isolated prefill readiness probe, never infer PD equivalence."""
from pathlib import Path
import datetime,hashlib,json,re,shlex,subprocess,tarfile
O=Path(__file__).resolve().parent;job=json.loads((O/'pbs-receipt.json').read_text())['job'];number=job.split('.')[0]
root='/scratch/users/industry/ai-hpc/apacsc42/qwen-pbs-20261015/'+O.name
helper='/home/apacsc42/workspace/vpn-rootless/vpn.sh'
def remote(cmd,stream=None):
 return subprocess.run(['bash',helper,'ssh-batch','bash -lc '+shlex.quote(cmd)],stdout=stream if stream else subprocess.PIPE,stderr=subprocess.PIPE,timeout=120)
r=remote('qstat -xf '+job);assert r.returncode==0
text=r.stdout.decode();assert re.search(r'Job_Owner\s*=\s*apacsc42@',text)
state=re.search(r'job_state\s*=\s*(\S+)',text)[1]
if state!='F':print('NOT_TERMINAL',job,state);raise SystemExit(0)
D=O/'collected'/job;assert not D.exists(),'Preserve sealed evidence';D.mkdir(parents=True)
(D/'pbs-accounting.txt').write_text(text)
with (D/'raw-artifacts.tar.gz').open('wb') as stream:
 r=remote('cd '+shlex.quote(root)+' && files=(runs/'+job+'); for f in *.o'+number+' *.e'+number+'; do if [[ -f "$f" ]]; then files+=("$f"); fi; done; tar -czf - "${files[@]}"',stream)
assert r.returncode==0
with tarfile.open(D/'raw-artifacts.tar.gz') as archive:
 members=archive.getmembers();assert all(not Path(m.name).is_absolute() and '..' not in Path(m.name).parts and (m.isfile() or m.isdir()) for m in members)
 archive.extractall(D,members=members,filter='data')
run=D/'runs'/job;S=run/'submitted';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(S/'SHA256SUMS')==sha(O/'SHA256SUMS')
expected={line.split('  ',1)[1]:line.split('  ',1)[0] for line in (S/'SHA256SUMS').read_text().splitlines()}
names=['worker.sh','capture-worker-locality.py','resource-sampler.py','verify-draft.py','asset-contract.json','nixl-conn.py','expected-source.json','target-staging-record.json','entry.sh','component.pbs','check-probe.py','SHA256SUMS']
assert {p.name for p in S.iterdir()}==set(names)
for name in names:
 assert (S/name).is_file()
 if name!='SHA256SUMS':assert sha(S/name)==expected[name]
seal={str(p.relative_to(D)):sha(p) for p in D.rglob('*') if p.is_file()};(D/'evidence-sha256.json').write_text(json.dumps(seal,indent=2)+'\n')
exit_status=int(re.search(r'Exit_status\s*=\s*(-?\d+)',text)[1]);result=json.loads((run/'probe-result.json').read_text()) if (run/'probe-result.json').is_file() else None
out=dict(job=job,collected_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),terminal=True,exit_status=exit_status,payload_subset_hashes_passed=True,copied_payload_files=len(names),probe_result=result,semantic_pass=exit_status==0 and bool(result and result.get('passed')),runtime_review_complete=False,pd_output_equivalence=False,ranked_performance_measured=False,official_accuracy_verified=False)
(O/'collection.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
