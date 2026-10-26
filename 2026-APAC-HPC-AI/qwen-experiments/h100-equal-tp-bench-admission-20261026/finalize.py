#!/usr/bin/env python3
"""Root final review: enforce scoring stage timeout and seal the derived bundle."""
from pathlib import Path
import ast,copy,datetime,hashlib,json,subprocess,tarfile
S=Path(__file__).resolve().parent;Q=S.parent;B=Q/'eagle3-h100-equal-tp-bench-n24-20261026';P=Q/'eagle3-h100-equal-tp-observer-r2-20261026'
p=B/'topology-job.sh';s=p.read_text();old='AIPERF=/scratch/users/industry/ai-hpc/apacsc42/qwen-assets/aiperf.sqsh\nsrun --overlap';new='AIPERF=/scratch/users/industry/ai-hpc/apacsc42/qwen-assets/aiperf.sqsh\ntimeout --signal=TERM --kill-after=5s "${score_remaining}s" srun --overlap';assert old in s;s=s.replace(old,new);p.write_text(s)
for name in ['worker.sh','placement.tsv','nixl-conn.py','pd-observer/observer.py','pd-observer/sitecustomize.py','metadata-gate.py','prerequisite-check.py','whole-node-preflight.py']:
 if not (P/name).exists():continue
 assert (P/name).read_bytes()==(B/name).read_bytes(),name
cfg=json.loads((B/'config.json').read_text());assert cfg['allocation']['gpus']==8 and cfg['allocation']['wall_seconds']==1800 and cfg['allocation']['max_su']==512
raw=Q/'h100-review-225227-225228-20261026/curated-r2/h100-incumbent-n54-refresh-20261026/runs/225227.pbs111/confirm/n54/artifacts/profile_export_aiperf.json'
expected=copy.deepcopy(json.loads(raw.read_text())['input_config']);expected['endpoint']['urls']=['DYNAMIC_ALLOCATED_ROUTER'];expected['artifacts']['dir']='DYNAMIC_ARTIFACT_DIRECTORY'
for phase in expected['phases']:
 if 'concurrency' in phase:phase['concurrency']=24
expected['runtime']['workers']=24
assert expected==json.loads((B/'expected-input-config.json').read_text()),'Unexpected fixed-workload/schema drift'
for p in B.rglob('*.py'):ast.parse(p.read_text())
for p in list(B.glob('*.sh'))+list(B.glob('*.pbs')):subprocess.run(['bash','-n',str(p)],check=True)
subprocess.run(['python3','-B',str(Q/'h100-equal-tp-bench-prep-20261026/verify.py')],check=True)
(B/'ROOT_FINALIZATION.json').write_text(json.dumps({'reviewed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'root_delta':'Bound outer scoring srun by actual score_remaining, so connection warmup and container startup cannot bypass scoring deadline.','unchanged_serving_arithmetic':True,'fixed_workload_schema_matches_fresh_N54_except_client_N_workers':True,'parent_job':'225228.pbs111','actual_new_GPU_result':'NOT_COLLECTED'},indent=2)+'\n')
files=sorted(p for p in B.rglob('*') if p.is_file() and p.name not in {'SHA256SUMS','payload.tar.gz'} and '__pycache__' not in p.parts)
(B/'SHA256SUMS').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+str(p.relative_to(B))+'\n' for p in files))
with tarfile.open(B/'payload.tar.gz','w:gz') as tar:
 for p in files+[B/'SHA256SUMS']:tar.add(p,arcname=str(p.relative_to(B)),recursive=False)
subprocess.run(['sha256sum','-c','SHA256SUMS'],cwd=B,check=True,stdout=subprocess.DEVNULL)
proof={'state':'ROOT_REVIEWED_READY_FOR_BOUNDED_GPU_BENCHMARK','manifest_sha256':hashlib.sha256((B/'SHA256SUMS').read_bytes()).hexdigest(),'payload_sha256':hashlib.sha256((B/'payload.tar.gz').read_bytes()).hexdigest(),'gpus':8,'minutes':30,'max_su':512,'limits':'CPU fixtures/source parity do not prove GPU benchmark throughput or official accuracy. Fresh locked admission still required.'}
(S/'ROOT-REVIEW.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof))
