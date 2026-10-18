from pathlib import Path
import json,shutil,subprocess,hashlib,ast,tarfile,datetime,importlib.util
R=Path.cwd();D=R/'serving-tuning-10';P=R/'nscc-pbs';O=R/'research-followup-20261018-0900';validation={};pilots=[]
for parent,source,name,n in [(P,'h100-hpc-decode-24','h100-hpc-repeat-25',50),(P,'h100-prefetch-profile-23','h100-hpc-control-26',50),(P,'h100-hpc-decode-24','h100-hpc-n52-27',52),(D,'s11-dg-control-n56','s11-hpc-decode-n56',56)]:
 src=parent/source;dst=parent/name;assert not dst.exists();shutil.copytree(src,dst);f=dst/('benchmark.pbs' if parent==P else 'job.sbatch');s=f.read_text().replace(source,name).replace('QWEN_DIAGNOSTIC_PROFILE=1','QWEN_DIAGNOSTIC_PROFILE=0')
 if n==52:assert 'QWEN_TUNE_NS="50"' in s;s=s.replace('QWEN_TUNE_NS="50"','QWEN_TUNE_NS="52"')
 f.write_text(s);c=json.loads((dst/'config.json').read_text());c.update(experiment=name,source_experiment=source,source_job='221263.pbs111' if parent==P and 'hpc-decode' in source else '221262.pbs111' if parent==P else '24526',concurrency=[n],matched_concurrency=n,diagnostic_profile=False,accuracy_verified=False)
 c['purpose']='Independent HPC-Ops decode replication at N50' if name.endswith('25') else 'Fresh auto decode control for HPC-Ops confirmation; prefetch retained, profile disabled after scoring' if name.endswith('26') else 'Bounded N52 load trial after validated N50 HPC-Ops; do not automatically increase further' if name.endswith('27') else 'H200 decode-only HPC-Ops trial motivated by measured H100 gain; retain confirmed DeepGEMM prefill and compare fresh24526'
 if parent==D:
  f=dst/'worker.sh';s=f.read_text();source_hpc=(P/'h100-hpc-decode-24/worker.sh').read_text();preflight=source_hpc.split("else\n",1)[1].split('  extra=',1)[0];assert 'HPCCHECK' in preflight
  s=s.replace('else\n  extra=','else\n'+preflight+'  extra=');s=s.replace('--decode-attention-backend flashinfer)','--decode-attention-backend flashinfer --moe-runner-backend hpc_ops)');f.write_text(s);c['decode_extra_flags']+=['--moe-runner-backend','hpc_ops']
 (dst/'config.json').write_text(json.dumps(c,indent=2)+'\n')
 for f in dst.iterdir():
  if f.suffix=='.py':ast.parse(f.read_text(),str(f))
  if f.suffix in ['.sh','.pbs','.sbatch']:subprocess.run(['bash','-n',str(f)],check=True)
 for filename in ['benchmark.sh','topology-job.sh','output-smoke.py','long-context-check.py','nixl-conn.py']:assert (src/filename).read_bytes()==(dst/filename).read_bytes(),filename
 hashes={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(dst.iterdir()) if f.is_file() and f.name!='SHA256SUMS'};(dst/'SHA256SUMS').write_text(''.join(v+'  '+k+'\n' for k,v in hashes.items()));validation[name]=hashes
 if parent==D:pilots.append(dict(id=name,bundle=str(dst),planned_ns=[56],state='PLANNED',wave=10,purpose=c['purpose'],diagnostic_profile=False,expected_profile_ranks={},payload_sha256=hashes,measurements=[],missing_ns=[56],benchmark_complete=False,profile_complete=None,traces=[],attempts=[],replication_source_job='24526'))
active=subprocess.check_output(['squeue','-h','-u','apacsc42','-o','%i'],text=True);assert len(active.splitlines())+len(pilots)<=5
f=D/'prepared-pilots.json';p=json.loads(f.read_text());assert not any(x['id']==pilots[0]['id'] for x in p['pilots']);p['pilots'].extend(pilots);t=f.with_suffix('.followup.tmp');t.write_text(json.dumps(p,indent=2)+'\n');t.replace(f)
with tarfile.open(O/'next-pbs.tar.gz','w:gz') as t:
 for name in ['h100-hpc-repeat-25','h100-hpc-control-26','h100-hpc-n52-27']:t.add(P/name,arcname=name)
(O/'next-validation.json').write_text(json.dumps(dict(payloads=validation,passed=True,unchanged_scoring_quality=True),indent=2)+'\n');print('H200 decode trial armed; three PBS followups frozen')
