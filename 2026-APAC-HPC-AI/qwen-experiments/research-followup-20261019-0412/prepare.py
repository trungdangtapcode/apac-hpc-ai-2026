"""Freeze single-factor H200 followups and two bounded H100 load trials."""
from pathlib import Path
import ast,hashlib,json,shutil,subprocess,tarfile,datetime
R=Path(__file__).resolve().parents[1];O=Path(__file__).resolve().parent;D=R/'serving-tuning-10';P=R/'nscc-pbs';specs=[];validation={}
def freeze(dst,src,unchanged):
 for f in dst.iterdir():
  if f.suffix=='.py':ast.parse(f.read_text())
  if f.suffix in {'.sh','.sbatch','.pbs'}:subprocess.run(['bash','-n',str(f)],check=True)
 for filename in unchanged:assert (src/filename).read_bytes()==(dst/filename).read_bytes(),filename
 h={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(dst.iterdir()) if f.is_file() and f.name!='SHA256SUMS'}
 (dst/'SHA256SUMS').write_text(''.join(v+'  '+k+'\n' for k,v in h.items()));validation[dst.name]=h;return h
source='s13-dg-chunk8192-n58-bounded';src=D/source
for name,n,chunk,decode,kind in [('s14-dg8192-control-n58',58,8192,'auto','control'),('s14-dg8192-n60',60,8192,'auto','load'),('s14-dg12288-n58',58,12288,'auto','chunk'),('s14-dg8192-hpc-decode-n58',58,8192,'hpc_ops','decode')]:
 dst=D/name;assert not dst.exists();shutil.copytree(src,dst)
 f=dst/'job.sbatch';s=f.read_text().replace(source,name).replace('QWEN_TUNE_NS=58','QWEN_TUNE_NS='+str(n));f.write_text(s)
 if kind=='chunk':
  f=dst/'worker.sh';s=f.read_text();assert s.count('--chunked-prefill-size 8192')==1;f.write_text(s.replace('--chunked-prefill-size 8192','--chunked-prefill-size 12288'))
 if kind=='decode':
  f=dst/'worker.sh';s=f.read_text();probe=(D/'s13-hpc-decode-n58/worker.sh').read_text().split('else\n',1)[1].split('  extra=',1)[0];assert 'HPCCHECK' in probe;s=s.replace('else\n  extra=','else\n'+probe+'  extra=');assert s.count('--decode-attention-backend flashinfer)')==1;s=s.replace('--decode-attention-backend flashinfer)','--decode-attention-backend flashinfer --moe-runner-backend hpc_ops)');f.write_text(s)
 c=json.loads((dst/'config.json').read_text());purpose={'control':'Fresh repeated best observed H200 operating point, matched control for three single-factor trials; retain whole-client 360 s containment.','load':'Single N60 trial justified by independently repeated N58 chunk8192 latency headroom; compare fresh N58 control, no automatic N62.','chunk':'At N58 test whether 12288-token prefill capacity improves over 8192 by accommodating more prompt tokens per batch; larger workspace/graph cost may lose, no automatic larger chunk.','decode':'Test HPC-Ops decode interaction with repeated DeepGEMM chunk8192 at N58; decoded-token latency improved at chunk4096 but aggregate gain was small, so retain same-load chunk8192 control.'}[kind]
 c.update(experiment=name,source_experiment=source,source_job='24647',replication_source_job='24647',control_job='24647',fresh_control_job=None,control_experiment='s14-dg8192-control-n58',concurrency=[n],matched_concurrency=n,prefill_chunk_size=chunk,accuracy_verified=False,diagnostic_profile=False,purpose=purpose,changed_factor={'kind':kind,'concurrency':n,'chunk':chunk,'decode_runner':decode},retry_interpretation='Controlled followup after a completed passing measurement, not an automatic retry. Any whole-client timeout is a failed attempt; no unchanged retry.',manual_bounded_retry_limit=0)
 c['prefill_extra_flags'][1]=str(chunk)
 if kind=='decode':c['decode_extra_flags']+=['--moe-runner-backend','hpc_ops']
 (dst/'config.json').write_text(json.dumps(c,indent=2)+'\n')
 same=['benchmark.sh','topology-job.sh','profile-serving.py','output-smoke.py','long-context-check.py','nixl-conn.py','placement.tsv']
 if kind in {'control','load'}:same.append('worker.sh')
 h=freeze(dst,src,same);specs.append(dict(platform='H200',id=name,bundle=str(dst),planned_ns=[n],state='PLANNED',wave=10,purpose=purpose,kind=kind,payload_sha256=h,diagnostic_profile=False,measurements=[],missing_ns=[n],benchmark_complete=False,profile_complete=None,traces=[],attempts=[],replication_source_job='24647'))
source='h100-hpc-both-n52-35';src=P/source
for name,n in [('h100-hpc-both-n52-repeat-37',52),('h100-hpc-both-n54-38',54)]:
 dst=P/name;assert not dst.exists();shutil.copytree(src,dst);f=dst/'benchmark.pbs';s=f.read_text().replace(source,name).replace('QWEN_TUNE_NS="52"','QWEN_TUNE_NS="'+str(n)+'"');f.write_text(s)
 c=json.loads((dst/'config.json').read_text());purpose='Independent N52 repeat of 2398.728 good tokens/s with identical serving/client/quality payloads' if n==52 else 'One N54 trial after N52 passes 98.73% joint SLA, 602 ms TTFT and 18.21 ms ITL; retain both-phase HPC-Ops and chunk4096, no automatic N56'
 c.update(experiment=name,source_experiment=source,source_job='221341.pbs111',replication_source_job='221341.pbs111',control_job='221341.pbs111',fresh_control_job=None,control_experiment='h100-hpc-both-n52-repeat-37',concurrency=[n],matched_concurrency=n,purpose=purpose,accuracy_verified=False,benchmark_runtime_validation='PENDING_NEW_ALLOCATION');(dst/'config.json').write_text(json.dumps(c,indent=2)+'\n')
 h=freeze(dst,src,[f.name for f in src.iterdir() if f.is_file() and f.name not in {'benchmark.pbs','config.json','SHA256SUMS'}]);specs.append(dict(platform='H100',id=name,bundle=str(dst),planned_ns=[n],minutes=45,max_su=1536,state='PLANNED',purpose=purpose,payload_sha256=h))
with tarfile.open(O/'pbs-bundles.tar.gz','w:gz') as tar:
 for item in specs:
  if item['platform']=='H100':tar.add(item['bundle'],arcname=item['id'])
(O/'pilots.json').write_text(json.dumps(specs,indent=2)+'\n');(O/'validation.json').write_text(json.dumps(dict(passed=True,checked_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),unchanged_client_protocol_quality_precision_transport=True,payloads=validation,caveat='Syntax and frozen payload checks do not prove new GPU shapes/backends work; full terminal GPU checks required.'),indent=2)+'\n');print('Frozen',len(specs),'trials; not submitted')
