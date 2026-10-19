"""Prepare a baseline repeat with CPU plus GPU post-score diagnostic traces."""
from pathlib import Path
import ast,hashlib,json,shutil,subprocess
R=Path(__file__).resolve().parents[1];O=Path(__file__).resolve().parent;P=R/'nscc-pbs';source='h100-hpc-both-n54-repeat-39';name='h100-hpc-n54-cpu-gpu-profile-48';src=P/source;dst=P/name
assert not dst.exists();assert json.loads((R/'research-followup-20261019-1200/221827.pbs111-review.json').read_text())['state']=='LOCAL_PROTOCOL_SLA_OUTPUT_RUNTIME_PASS'
shutil.copytree(src,dst)
f=dst/'benchmark.pbs';f.write_text(f.read_text().replace(source,name).replace('QWEN_DIAGNOSTIC_PROFILE=0','QWEN_DIAGNOSTIC_PROFILE=1'))
f=dst/'profile-serving.py';s=f.read_text();before="'activities': ['GPU']";after="'activities': ['CPU', 'GPU']";assert s.count(before)==1;s=s.replace(before,after,1)
s=s.replace('Collect bounded GPU traces','Collect bounded CPU and GPU traces',1)
assert s.replace(after,before,1).replace('Collect bounded CPU and GPU traces','Collect bounded GPU traces',1)==(src/'profile-serving.py').read_text()
s=s.replace("'kind': 'diagnostic-only', 'concurrency': 48", "'kind': 'diagnostic-only', 'activities': ['CPU', 'GPU'], 'concurrency': 48",1);f.write_text(s)
c=json.loads((src/'config.json').read_text());c.update(experiment=name,source_experiment=source,source_job='221827.pbs111',replication_source_job='221827.pbs111',control_job='221827.pbs111',diagnostic_profile=True,accuracy_verified=False,profile_activities=['CPU','GPU'],purpose='Repeat the accepted N54 baseline, then capture bounded CPU and GPU activities to investigate host-launch gaps and phase costs absent from GPU-only traces. No candidate speedup claimed from instrumentation.',changed_factor={'kind':'post_score_profile_activities_only'},profile_position='After full unchanged scored benchmark; separate diagnostic N48 with 4 prefill / 32 decode steps');(dst/'config.json').write_text(json.dumps(c,indent=2)+'\n')
for f in dst.iterdir():
 if f.suffix=='.py':ast.parse(f.read_text())
 if f.suffix in {'.sh','.pbs'}:subprocess.run(['bash','-n',str(f)],check=True)
 if f.is_file() and f.name not in {'benchmark.pbs','profile-serving.py','config.json','SHA256SUMS'}:assert f.read_bytes()==(src/f.name).read_bytes()
h={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(dst.iterdir()) if f.is_file() and f.name!='SHA256SUMS'};(dst/'SHA256SUMS').write_text(''.join(v+'  '+k+'\n' for k,v in h.items()))
(O/'pilot.json').write_text(json.dumps(dict(platform='H100',id=name,bundle=str(dst),planned_ns=[54],minutes=45,max_su=1536,state='PREPARED_NOT_SUBMITTED',purpose=c['purpose'],replication_source_job='221827.pbs111',diagnostic_profile=True,payload_sha256=h,budget_reserved=False),indent=2)+'\n')
(O/'validation.json').write_text(json.dumps(dict(passed=True,ranked_benchmark_worker_precision_transport_quality_byte_identical=True,post_score_activities_only=True,profile_activity_schema_source='research-followup-20261019-1418/runtime-profiler-source/sgl-workspace/sglang/python/sglang/srt/managers/io_struct.py'),indent=2)+'\n')
print('CPU + GPU post-score diagnostic standby frozen, not submitted.')
