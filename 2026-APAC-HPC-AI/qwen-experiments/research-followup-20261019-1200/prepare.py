"""Freeze independent, source-gated trials; preserve ranked workload and decode."""
from pathlib import Path
import ast,datetime,hashlib,json,shutil,subprocess,tarfile
R=Path(__file__).resolve().parents[1];O=Path(__file__).resolve().parent
P=R/'nscc-pbs';D=R/'serving-tuning-10';pilots=[];proofs={}
assert json.loads((R/'status-review-20261019-1111/221645.pbs111-review.json').read_text())['state']=='LOCAL_PROTOCOL_SLA_OUTPUT_RUNTIME_PASS'
assert json.loads((R/'research-followup-20261019-0600/24724-review.json').read_text())['state']=='LOCAL_PROTOCOL_SLA_OUTPUT_PASS'
rows=[
 ('H100','h100-hpc-both-n54-repeat-39','221645.pbs111','h100-hpc-n54-control-profile-42','control',True),
 ('H100','h100-hpc-both-n54-repeat-39','221645.pbs111','h100-hpc-chunk6144-n54-43','chunk6144',False),
 ('H100','h100-hpc-both-n54-repeat-39','221645.pbs111','h100-hpc-prefill-simple-n54-44','simple',True),
 ('H200','s16-dg8192-hpc-decode-repeat-n58','24724','s17-dg8192-hpc-decode-profile-n58','winner_profile',True)]
purposes={
 'control':'Fresh N54 both-phase HPC-Ops control; score unchanged, then separately profile the actual N54 deployment at diagnostic N48.',
 'chunk6144':'At fixed N54, test prefill chunk 6144 with both-phase HPC-Ops. Prior H100 chunk 8192 loss used auto prefill, so this is a new runner/chunk interaction rather than an unchanged retry.',
 'simple':'At fixed N54 change only prefill NCCL all-reduce protocol to Simple; default algorithm selection and all decode settings remain unchanged. Actual kernel protocol/algorithm require separate trace proof.',
 'winner_profile':'Full N58 repeat and separate diagnostic profile of the highest observed H200 interaction: DeepGEMM prefill, chunk 8192 and HPC-Ops decode. Obtain actual winning-platform kernels instead of inferring from H100.'}
for platform,source,job,name,kind,profile in rows:
 parent=P if platform=='H100' else D;src=parent/source;dst=parent/name
 assert not dst.exists();shutil.copytree(src,dst)
 jobfile='benchmark.pbs' if platform=='H100' else 'job.sbatch';f=dst/jobfile
 s=f.read_text().replace(source,name);assert 'QWEN_DIAGNOSTIC_PROFILE=0' in s
 s=s.replace('QWEN_DIAGNOSTIC_PROFILE=0','QWEN_DIAGNOSTIC_PROFILE='+str(int(profile)));f.write_text(s)
 worker=(src/'worker.sh').read_text();changed_worker=worker;env={}
 if kind=='chunk6144':
  assert worker.count('--chunked-prefill-size 4096')==1;changed_worker=worker.replace('--chunked-prefill-size 4096','--chunked-prefill-size 6144',1)
  assert changed_worker.replace('--chunked-prefill-size 6144','--chunked-prefill-size 4096',1)==worker
 if kind=='simple':
  needle='if [[ $role == prefill ]]; then\n';extra='  export NCCL_PROTO=allreduce:Simple\n  echo "PREFILL_NCCL_PROTO=$NCCL_PROTO"\n'
  assert worker.count(needle)==1 and 'NCCL_ALGO=' not in worker
  changed_worker=worker.replace(needle,needle+extra,1);assert changed_worker.replace(extra,'',1)==worker
  env={'NCCL_PROTO':'allreduce:Simple'}
 (dst/'worker.sh').write_text(changed_worker)
 assert changed_worker.split('\nelse\n',1)[1]==worker.split('\nelse\n',1)[1]
 c=json.loads((src/'config.json').read_text());n=54 if platform=='H100' else 58
 c.update(experiment=name,source_experiment=source,source_job=job,replication_source_job=job,control_job=job,fresh_control_job=None,control_experiment='h100-hpc-n54-control-profile-42' if platform=='H100' else 's16-dg8192-control-n58',concurrency=[n],matched_concurrency=n,purpose=purposes[kind],accuracy_verified=False,diagnostic_profile=profile,changed_factor={'kind':kind},prefill_environment=env,profile_position='Separate post-score diagnostic; ranked protocol unchanged' if profile else 'Disabled')
 if kind=='chunk6144':
  c['prefill_chunk_size']=6144;c['prefill_extra_flags']=[str(6144) if x=='4096' else x for x in c['prefill_extra_flags']]
 (dst/'config.json').write_text(json.dumps(c,indent=2)+'\n')
 for f in dst.iterdir():
  if f.suffix=='.py':ast.parse(f.read_text())
  if f.suffix in {'.sh','.sbatch','.pbs'}:subprocess.run(['bash','-n',str(f)],check=True)
  if f.is_file() and f.name not in {jobfile,'worker.sh','config.json','SHA256SUMS'}:assert f.read_bytes()==(src/f.name).read_bytes(),f.name
 hashes={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(dst.iterdir()) if f.is_file() and f.name!='SHA256SUMS'}
 (dst/'SHA256SUMS').write_text(''.join(v+'  '+k+'\n' for k,v in hashes.items()))
 pilot=dict(platform=platform,id=name,bundle=str(dst),planned_ns=[n],state='PLANNED',purpose=purposes[kind],payload_sha256=hashes,replication_source_job=job,control_experiment=c['control_experiment'],diagnostic_profile=profile)
 if platform=='H100':pilot.update(minutes=45,max_su=1536)
 else:pilot.update(wave=10,measurements=[],missing_ns=[n],benchmark_complete=False,profile_complete=None,traces=[],attempts=[])
 pilots.append(pilot);proofs[name]=dict(decode_branch_byte_identical=True,all_unmodified_operational_files_byte_identical=True,profile_after_score=profile,worker_inverse_patch_pass=True)
with tarfile.open(O/'pbs-bundles.tar.gz','w:gz') as tar:
 for p in pilots:
  if p['platform']=='H100':tar.add(p['bundle'],arcname=p['id'])
(O/'pilots.json').write_text(json.dumps(pilots,indent=2)+'\n')
(O/'validation.json').write_text(json.dumps(dict(passed=True,checked_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),proofs=proofs,client_precision_transport_quality_byte_identical=True,ranked_workload_4000_200_and_60_120_30_unchanged=True,actual_gpu_activation_and_quality_require_new_evidence=True),indent=2)+'\n')
print('Four bounded source-gated trials frozen.')
