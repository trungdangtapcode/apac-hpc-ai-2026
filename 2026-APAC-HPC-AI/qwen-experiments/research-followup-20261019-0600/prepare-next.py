"""Prepare a fresh matched control, interaction repeat and one load step."""
from pathlib import Path
import ast,datetime,hashlib,json,shutil,subprocess
R=Path(__file__).resolve().parents[1];O=Path(__file__).resolve().parent;D=R/'serving-tuning-10';pilots=[];payloads={}
assert json.loads((O/'24724-review.json').read_text())['state']=='LOCAL_PROTOCOL_SLA_OUTPUT_PASS'
for source,job,name,n,kind in [('s14-dg8192-control-n58','24721','s16-dg8192-control-n58',58,'control'),('s14-dg8192-hpc-decode-n58','24724','s16-dg8192-hpc-decode-repeat-n58',58,'repeat'),('s14-dg8192-hpc-decode-n58','24724','s16-dg8192-hpc-decode-n60',60,'load')]:
 src=D/source;dst=D/name;assert not dst.exists();shutil.copytree(src,dst)
 f=dst/'job.sbatch';s=f.read_text().replace(source,name);assert 'QWEN_TUNE_NS=58' in s;s=s.replace('QWEN_TUNE_NS=58','QWEN_TUNE_NS='+str(n));f.write_text(s)
 purpose={'control':'Fresh N58 auto-decode control for the observed chunk8192 plus HPC-Ops decode interaction; no kernel or workload change.','repeat':'Independent N58 repeat of2938.628 good tokens/s from24724; compare fresh auto-decode control at identical load and chunk.','load':'One N60 operating-point trial from passing N58 HPC-Ops decode plus DeepGEMM chunk8192; compare N58 interaction repeat for load, pending auto-decode N60 repeat24732 for runner.'}[kind]
 purpose=purpose.replace('chunk8192','chunk 8192').replace('of2938','of 2938').replace('from24724','from 24724').replace('repeat24732','repeat 24732')
 c=json.loads((dst/'config.json').read_text());c.update(experiment=name,source_experiment=source,source_job=job,replication_source_job=job,control_job=job,fresh_control_job=None,control_experiment='s16-dg8192-control-n58' if kind=='repeat' else 's16-dg8192-hpc-decode-repeat-n58',concurrency=[n],matched_concurrency=n,purpose=purpose,accuracy_verified=False,diagnostic_profile=False,changed_factor={'kind':kind,'concurrency':n});(dst/'config.json').write_text(json.dumps(c,indent=2)+'\n')
 for f in dst.iterdir():
  if f.suffix=='.py':ast.parse(f.read_text())
  if f.suffix in {'.sh','.sbatch'}:subprocess.run(['bash','-n',str(f)],check=True)
  if f.is_file() and f.name not in {'job.sbatch','config.json','SHA256SUMS'}:assert f.read_bytes()==(src/f.name).read_bytes(),f.name
 h={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(dst.iterdir()) if f.is_file() and f.name!='SHA256SUMS'};(dst/'SHA256SUMS').write_text(''.join(v+'  '+k+'\n' for k,v in h.items()));payloads[name]=h
 pilots.append(dict(platform='H200',id=name,bundle=str(dst),planned_ns=[n],state='PLANNED',purpose=purpose,payload_sha256=h,replication_source_job=job,wave=10,diagnostic_profile=False,measurements=[],missing_ns=[n],benchmark_complete=False,profile_complete=None,traces=[],attempts=[]))
(O/'pilots.json').write_text(json.dumps(pilots,indent=2)+'\n');(O/'validation.json').write_text(json.dumps(dict(passed=True,checked_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),payloads=payloads,client_worker_precision_quality_transport_byte_identical_to_each_declared_source=True,new_gpu_gates_required=True),indent=2)+'\n');print('Three source-gated H200 bundles frozen')
