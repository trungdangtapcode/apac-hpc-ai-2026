from pathlib import Path
import json,shutil,subprocess,hashlib,ast,tarfile
R=Path.cwd();D=R/'serving-tuning-10';P=R/'nscc-pbs';O=R/'research-followup-20261018-1323';validation={};pilots=[]
specs=[(D,'s11-dg-chunk8192-n58','s12-dg-chunk8192-repeat-n58',58,'24544'),(D,'s12-dg-fresh-control-n56','s12-dg-fresh-control-n58',58,'24526'),(P,'h100-hpc-both-31','h100-hpc-both-repeat-33',50,'221315.pbs111'),(P,'h100-hpc-fresh-control-30','h100-hpc-decode-control-34',50,'221314.pbs111'),(P,'h100-hpc-both-31','h100-hpc-both-n52-35',52,'221315.pbs111')]
for parent,source,name,n,job in specs:
 src=parent/source;dst=parent/name;assert not dst.exists();shutil.copytree(src,dst);f=dst/('job.sbatch' if parent==D else 'benchmark.pbs');s=f.read_text().replace(source,name)
 if n==58:s=s.replace('QWEN_TUNE_NS=56','QWEN_TUNE_NS=58')
 if n==52:s=s.replace('QWEN_TUNE_NS="50"','QWEN_TUNE_NS="52"')
 f.write_text(s);c=json.loads((dst/'config.json').read_text());c.update(experiment=name,source_experiment=source,source_job=job,concurrency=[n],matched_concurrency=n,accuracy_verified=False,diagnostic_profile=False)
 c['purpose']={'s12-dg-chunk8192-repeat-n58':'Repeat provisional N58 chunk8192 peak against a new same-load chunk4096 control; do not rely only on historical comparator','s12-dg-fresh-control-n58':'Fresh DeepGEMM chunk4096 N58 control to isolate chunk effect at the new operating point','h100-hpc-both-repeat-33':'Independent N50 HPC-Ops prefill gain repetition; decode already replicated, compare new decode-only control','h100-hpc-decode-control-34':'Fresh N50 HPC-Ops decode control with auto prefill, reverse candidate/control ordering','h100-hpc-both-n52-35':'One bounded N52 operating-point trial after HPC-Ops prefill plus decode passes N50; no automatic higher load'}[name]
 (dst/'config.json').write_text(json.dumps(c,indent=2)+'\n')
 for f in dst.iterdir():
  if f.suffix=='.py':ast.parse(f.read_text())
  if f.suffix in ['.sh','.pbs','.sbatch']:subprocess.run(['bash','-n',str(f)],check=True)
 for filename in ['worker.sh','benchmark.sh','profile-serving.py','topology-job.sh','nixl-conn.py','output-smoke.py','long-context-check.py']:assert (src/filename).read_bytes()==(dst/filename).read_bytes()
 h={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(dst.iterdir()) if f.is_file() and f.name!='SHA256SUMS'};(dst/'SHA256SUMS').write_text(''.join(v+'  '+k+'\n' for k,v in h.items()));validation[name]=h
 if parent==D:pilots.append(dict(id=name,bundle=str(dst),planned_ns=[58],state='PLANNED',wave=10,purpose=c['purpose'],diagnostic_profile=False,expected_profile_ranks={},payload_sha256=h,measurements=[],missing_ns=[58],benchmark_complete=False,profile_complete=None,traces=[],attempts=[],replication_source_job=job))
(O/'slurm-pilots.json').write_text(json.dumps(pilots,indent=2)+'\n');(O/'next-validation.json').write_text(json.dumps(dict(passed=True,payloads=validation),indent=2)+'\n')
with tarfile.open(O/'next-pbs.tar.gz','w:gz') as t:
 for name in ['h100-hpc-both-repeat-33','h100-hpc-decode-control-34','h100-hpc-both-n52-35']:t.add(P/name,arcname=name)
print('Five bounded followups frozen')
