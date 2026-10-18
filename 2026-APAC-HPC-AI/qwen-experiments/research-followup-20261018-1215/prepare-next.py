from pathlib import Path
import json,shutil,subprocess,hashlib,ast,tarfile
R=Path.cwd();D=R/'serving-tuning-10';P=R/'nscc-pbs';O=R/'research-followup-20261018-1215';validation={};pilots=[]
specs=[(D,'s11-dg-chunk6144-n56','s12-dg-chunk6144-repeat-n56','repeat'),(D,'s11-hpc-prefill-n56','s12-hpc-prefill-repeat-n56','repeat'),(D,'s11-dg-control-n56','s12-dg-fresh-control-n56','control'),(P,'h100-hpc-repeat-25','h100-hpc-fresh-control-30','control'),(P,'h100-hpc-repeat-25','h100-hpc-both-31','both'),(P,'h100-hpc-n52-27','h100-hpc-n52-repeat-32','repeat')]
for parent,source,name,kind in specs:
 src=parent/source;dst=parent/name;assert not dst.exists();shutil.copytree(src,dst);f=dst/('job.sbatch' if parent==D else 'benchmark.pbs');f.write_text(f.read_text().replace(source,name));c=json.loads((dst/'config.json').read_text());c.update(experiment=name,source_experiment=source,diagnostic_profile=False,accuracy_verified=False)
 purpose={'s12-dg-chunk6144-repeat-n56':'Independent repetition of provisional 0.78 percent prefill chunk6144 gain; compare new chunk4096 control','s12-hpc-prefill-repeat-n56':'Independent repetition of provisional 0.61 percent HPC-Ops prefill gain; compare new DeepGEMM control','s12-dg-fresh-control-n56':'Fresh confirmed DeepGEMM chunk4096 N56 control to detect drift before interpreting sub-percent gains','h100-hpc-fresh-control-30':'Fresh replicated HPC-Ops decode N50 control for a prefill-only HPC-Ops change','h100-hpc-both-31':'Test HPC-Ops prefill in addition to replicated HPC-Ops decode; isolate prefill runner at N50','h100-hpc-n52-repeat-32':'Repeat provisional N52 operating point; compare adjacent fresh N50 score and latency before more load'}[name];c['purpose']=purpose;c['matched_concurrency']=c['concurrency'][0]
 sourcejob={'s12-dg-chunk6144-repeat-n56':'24528','s12-hpc-prefill-repeat-n56':'24529','s12-dg-fresh-control-n56':'24526','h100-hpc-fresh-control-30':'221284.pbs111','h100-hpc-both-31':'221284.pbs111','h100-hpc-n52-repeat-32':'221276.pbs111'}[name];c['source_job']=sourcejob
 if kind=='both':
  f=dst/'worker.sh';s=f.read_text();assert 'extra=(--chunked-prefill-size 4096 --weight-loader-prefetch-checkpoints)' in s;s=s.replace('extra=(--chunked-prefill-size 4096 --weight-loader-prefetch-checkpoints)','extra=(--chunked-prefill-size 4096 --weight-loader-prefetch-checkpoints --moe-runner-backend hpc_ops)');preflight=s.split('else\n',1)[1].split('  extra=',1)[0];assert 'HPCCHECK' in preflight;s=s.replace('if [[ $role == prefill ]]; then\n','if [[ $role == prefill ]]; then\n'+preflight);f.write_text(s);c['prefill_extra_flags']+=['--moe-runner-backend','hpc_ops']
 (dst/'config.json').write_text(json.dumps(c,indent=2)+'\n')
 for f in dst.iterdir():
  if f.suffix=='.py':ast.parse(f.read_text())
  if f.suffix in ['.sh','.pbs','.sbatch']:subprocess.run(['bash','-n',str(f)],check=True)
 for filename in ['benchmark.sh','profile-serving.py','topology-job.sh','nixl-conn.py','output-smoke.py','long-context-check.py']:assert (src/filename).read_bytes()==(dst/filename).read_bytes()
 h={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(dst.iterdir()) if f.is_file() and f.name!='SHA256SUMS'};(dst/'SHA256SUMS').write_text(''.join(v+'  '+k+'\n' for k,v in h.items()));validation[name]=h
 if parent==D:pilots.append(dict(id=name,bundle=str(dst),planned_ns=[56],state='PLANNED',wave=10,purpose=purpose,diagnostic_profile=False,expected_profile_ranks={},payload_sha256=h,measurements=[],missing_ns=[56],benchmark_complete=False,profile_complete=None,traces=[],attempts=[],replication_source_job=sourcejob))
(O/'slurm-pilots.json').write_text(json.dumps(pilots,indent=2)+'\n');(O/'next-validation.json').write_text(json.dumps(dict(passed=True,payloads=validation),indent=2)+'\n')
with tarfile.open(O/'next-pbs.tar.gz','w:gz') as t:
 for name in ['h100-hpc-fresh-control-30','h100-hpc-both-31','h100-hpc-n52-repeat-32']:t.add(P/name,arcname=name)
print('Six reviewed-source bundles frozen, not yet armed')
