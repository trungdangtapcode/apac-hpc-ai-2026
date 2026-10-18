from pathlib import Path
import shutil,json,hashlib,subprocess,tarfile,ast
R=Path.cwd();P=R/'nscc-pbs';D=R/'serving-tuning-10';O=R/'research-followup-20261018-0925';payloads={};slurm=[]
for parent,source,name,kind in [(P,'h100-hpc-repeat-25','h100-hpc-profile-28','profile'),(P,'h100-hpc-repeat-25','h100-hpc-chunk8192-29','chunk'),(D,'s11-dg-chunk8192-repeat-n56','s11-dg-chunk8192-n58','load')]:
 src=parent/source;dst=parent/name;assert not dst.exists();shutil.copytree(src,dst);job=dst/('benchmark.pbs' if parent==P else 'job.sbatch');s=job.read_text().replace(source,name)
 if kind=='profile':s=s.replace('QWEN_DIAGNOSTIC_PROFILE=0','QWEN_DIAGNOSTIC_PROFILE=1')
 if kind=='load':s=s.replace('QWEN_TUNE_NS=56','QWEN_TUNE_NS=58')
 job.write_text(s);c=json.loads((dst/'config.json').read_text());c.update(experiment=name,source_experiment=source,source_job='24527' if kind=='load' else '221274.pbs111',diagnostic_profile=kind=='profile',accuracy_verified=False,concurrency=[58] if kind=='load' else [50],matched_concurrency=58 if kind=='load' else 50)
 c['purpose']={'profile':'Score replicated HPC-Ops decode N50 then profile separately; identify next bottleneck before choosing more kernels','chunk':'Test larger prefill chunk with replicated HPC-Ops decode at N50; isolate prefill batching, not a transferred H200 speed estimate','load':'One bounded N58 chunk8192 trial after two positive N56 chunk observations; compare historical N58 chunk4096 and fresh N56 chunk8192'}[kind]
 if kind=='chunk':
  f=dst/'worker.sh';s=f.read_text();assert '--chunked-prefill-size 4096' in s;s=s.replace('--chunked-prefill-size 4096','--chunked-prefill-size 8192');f.write_text(s);c['prefill_chunk_size']=8192;c['prefill_extra_flags'][1]='8192'
 if kind=='profile':c.update(diagnostic_concurrency=48,diagnostic_prefill_steps=4,diagnostic_decode_steps=32)
 (dst/'config.json').write_text(json.dumps(c,indent=2)+'\n')
 for f in dst.iterdir():
  if f.suffix=='.py':ast.parse(f.read_text())
  if f.suffix in ['.sh','.sbatch','.pbs']:subprocess.run(['bash','-n',str(f)],check=True)
 for file in ['benchmark.sh','profile-serving.py','topology-job.sh','output-smoke.py','long-context-check.py','nixl-conn.py']:assert (src/file).read_bytes()==(dst/file).read_bytes()
 h={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(dst.iterdir()) if f.is_file() and f.name!='SHA256SUMS'};(dst/'SHA256SUMS').write_text(''.join(v+'  '+k+'\n' for k,v in h.items()));payloads[name]=h
 if parent==D:slurm.append(dict(id=name,bundle=str(dst),planned_ns=[58],state='PLANNED',wave=10,purpose=c['purpose'],diagnostic_profile=False,expected_profile_ranks={},payload_sha256=h,measurements=[],missing_ns=[58],benchmark_complete=False,profile_complete=None,traces=[],attempts=[],replication_source_job='24527'))
with tarfile.open(O/'next-pbs.tar.gz','w:gz') as t:
 for name in ['h100-hpc-profile-28','h100-hpc-chunk8192-29']:t.add(P/name,arcname=name)
(O/'next-validation.json').write_text(json.dumps(dict(passed=True,payloads=payloads),indent=2)+'\n');(O/'slurm-pilot.json').write_text(json.dumps(slurm[0],indent=2)+'\n');print('Prepared, not yet armed: H100 profile/chunk pair and H200 chunk8192 N58')
