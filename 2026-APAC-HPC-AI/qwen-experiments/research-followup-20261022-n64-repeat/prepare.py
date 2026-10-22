"""Freeze one independent N64 deployment after its full source passes review."""
from pathlib import Path
from datetime import datetime,timezone
import ast,hashlib,json,shutil,subprocess
O=Path(__file__).resolve().parent;R=O.parent
C=R/'serving-tuning-10/s30-h200-observed-n64-full-candidate'
bid='s34-h200-observed-n64-full-repeat'; B=R/'serving-tuning-10'/bid
review=json.loads((R/'research-review-25366-20261022/REVIEW.json').read_text())
assert review['job']=='25366' and review['state']=='LOCAL_PROTOCOL_SLA_OUTPUT_PASS'
assert review['full_scored_protocol_equal'] and review['source_delta_goodput_percent']>=1
assert review['summary']['concurrency']==64 and review['summary']['sla_pass']
assert review['summary']['errors']==review['summary']['cancelled_requests']==0
assert review['point']['short_output_comparison']['research_eligible']
assert not review['point']['short_output_comparison']['new_failed_cases']
assert review['long_context']['state']=='PASSED'
assert not B.exists(),'Never overwrite a frozen bundle'
for path,key in [(R/'serving-tuning/registry.json','entries'),(R/'serving-tuning-10/prepared-pilots.json','pilots')]:
 assert not any(e['id']==bid for e in json.loads(path.read_text())[key]),'Candidate already registered'
subprocess.run(['sha256sum','--check','SHA256SUMS'],cwd=C,check=True,capture_output=True)
files=[line.split('  ',1)[1] for line in (C/'SHA256SUMS').read_text().splitlines()]
B.mkdir()
for name in files:shutil.copyfile(C/name,B/name)
p=B/'job.sbatch'; t=p.read_text(); assert t.count(C.name)==2 and 'export QWEN_TUNE_NS=64' in t
assert '#SBATCH -t 00:17:00' in t and '#SBATCH -N 2' in t and '#SBATCH --gres=gpu:8' in t
p.write_text(t.replace(C.name,bid))
c=json.loads((B/'config.json').read_text()); c.update(experiment=bid,source_experiment=C.name,source_job='25366',purpose='Independent full observed N64 replication after accepted gain',changed_factor={'independent_deployment_repeat':True},performance_comparison='Independent N64 replication of 25366; fresh equally observed N62 control25365 retained',replication_source_job='25366')
(B/'config.json').write_text(json.dumps(c,indent=2)+'\n')
assert 'run_benchmark "$N" confirm 60 120' in (B/'benchmark.sh').read_text()
for name in files:
 if name not in ['job.sbatch','config.json']:assert (B/name).read_bytes()==(C/name).read_bytes(),name
for p in B.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
for p in list(B.glob('*.sh'))+[B/'job.sbatch']:subprocess.run(['bash','-n',str(p)],check=True)
hashes={name:hashlib.sha256((B/name).read_bytes()).hexdigest() for name in files}
(B/'SHA256SUMS').write_text(''.join(hashes[name]+'  '+name+'\n' for name in files))
subprocess.run(['sha256sum','--check','SHA256SUMS'],cwd=B,check=True,capture_output=True)
pilot=dict(platform='H200',id=bid,bundle=str(B),planned_ns=[64],state='PREPARED_NOT_SUBMITTED',minutes=17,gpus=16,max_su=None,pbs_su_reserved=0,payload_sha256=hashes)
(O/'pilots.json').write_text(json.dumps([pilot],indent=2)+'\n')
(O/'validation.json').write_text(json.dumps(dict(passed=True,checked_utc=datetime.now(timezone.utc).isoformat(),source_job='25366',source_review_passed=True,all_operational_files_byte_identical=True,source_files=len(files),protocol='N64; 60 warmup /120 measured /30 grace',minutes=17,gpus=16,pbs_su_reserved=0),indent=2)+'\n')
print('Frozen independent full observed N64 repeat; operational bytes unchanged')
