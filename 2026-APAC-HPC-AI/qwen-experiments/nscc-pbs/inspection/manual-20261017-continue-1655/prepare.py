"""Prepare one startup repair on H100 and a bounded H200 load hypothesis."""
from pathlib import Path
import json,hashlib,shutil,subprocess,datetime,tarfile
R=Path.cwd();O=R/'nscc-pbs/inspection/manual-20261017-continue-1655'
def clone(src,name,kind):
 dst=src.parent/name;assert not dst.exists();shutil.copytree(src,dst)
 f=dst/('benchmark.pbs' if kind=='pbs' else 'job.sbatch');s=f.read_text().replace(src.name,name)
 if kind=='slurm':
  assert 'QWEN_TUNE_NS=56' in s;s=s.replace('QWEN_TUNE_NS=56','QWEN_TUNE_NS=58')
 f.write_text(s)
 f=dst/'config.json';c=json.loads(f.read_text());c.update(experiment=name,source_job='221152.pbs111' if kind=='pbs' else '24291')
 if kind=='pbs':
  f2=dst/'topology-job.sh';s=f2.read_text();assert s.count('deadline=${2:-1200}')==1;f2.write_text(s.replace('deadline=${2:-1200}','deadline=${2:-1800}'));c.update(worker_readiness_deadline_s=1800,purpose='Retry failed 221152 with only worker readiness extended; full benchmark unchanged',retry_of='221152.pbs111',retry_reason='Global 1200s readiness expired near completed prefill startup; load_weight=912.66s and prefill graphs=161.62s. No benchmark was recorded.')
 else:c.update(concurrency=[58],matched_concurrency=58,purpose='Bounded DeepGEMM prefill load test at N58 after N56 gain; compare old combo N58 and pending N56 repeat, no automatic promotion')
 f.write_text(json.dumps(c,indent=2)+'\n')
 allowed={'benchmark.pbs','job.sbatch','config.json','SHA256SUMS'}|({'topology-job.sh'} if kind=='pbs' else set())
 for f in src.iterdir():
  if f.is_file() and f.name not in allowed:assert f.read_bytes()==(dst/f.name).read_bytes(),f.name
 for f in list(dst.glob('*.sh'))+[dst/('benchmark.pbs' if kind=='pbs' else 'job.sbatch')]:subprocess.run(['bash','-n',str(f)],check=True)
 hashes={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(dst.iterdir()) if f.is_file() and f.name!='SHA256SUMS'};(dst/'SHA256SUMS').write_text(''.join(v+'  '+k+'\n' for k,v in hashes.items()));return dst,hashes
pbs,hp=clone(R/'nscc-pbs/h100-prefill-deepgemm-17','h100-prefill-deepgemm-retry-19','pbs')
slurm,hs=clone(R/'serving-tuning-10/s10-prefill-deepgemm-n56','s10-prefill-deepgemm-n58','slurm')
(O/'validation.json').write_text(json.dumps(dict(created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),pbs={pbs.name:hp},slurm={slurm.name:hs}),indent=2)+'\n')
with tarfile.open(O/'h100-retry.tar.gz','w:gz') as t:t.add(pbs,arcname=pbs.name)
# Existing non-AI watcher owns Slurm submissions and obeys its queue cap.
q=subprocess.check_output(['squeue','-h','-u','apacsc42','-o','%i'],text=True);assert len(q.splitlines())+1<=5
f=R/'serving-tuning-10/prepared-pilots.json';p=json.loads(f.read_text());p['pilots'].append(dict(id=slurm.name,bundle=str(slurm),planned_ns=[58],state='PLANNED',wave=10,purpose='New prefill backend may move capacity frontier: one N58 test, not a blind N60 increase. Existing combo N58 plateaued; independent DeepGEMM N56 confirmation remains required.',diagnostic_profile=False,expected_profile_ranks={},payload_sha256=hs,measurements=[],missing_ns=[58],benchmark_complete=False,profile_complete=None,traces=[],attempts=[],replication_source_job='24291'));p['updated_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();tmp=f.with_suffix('.n58.tmp');tmp.write_text(json.dumps(p,indent=2)+'\n');tmp.replace(f)
print('Prepared H100 readiness-only repair and armed H200 DeepGEMM N58')
